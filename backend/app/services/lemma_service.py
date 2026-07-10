import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi.concurrency import run_in_threadpool

from lemma_sdk import Lemma
from lemma_sdk.errors import (
    LemmaError,
    LemmaAPIError,
    LemmaAuthError,
    LemmaNotFoundError,
    LemmaTimeoutError,
    LemmaConnectionError
)

from ..config.settings import Settings

logger = logging.getLogger("lemma_integration")

# Custom Exceptions for clean routing error mapping
class LemmaGatewayError(Exception):
    """Base exception class for API gateway failures."""
    pass

class LemmaGatewayAuthError(LemmaGatewayError):
    """Exception raised when Lemma API token is expired or unauthorized."""
    pass

class LemmaGatewayNotFoundError(LemmaGatewayError):
    """Exception raised when the pod or workflow resource is not found."""
    pass

class LemmaGatewayTimeoutError(LemmaGatewayError):
    """Exception raised on network timeouts or polling timeouts."""
    pass

class LemmaGatewayConnectionError(LemmaGatewayError):
    """Exception raised on transport network layer failures."""
    pass


class LemmaService:
    """
    Service Layer responsible for interacting with the Lemma SDK.
    Runs the customer support workflow via python SDK library calls.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        logger.info("Initializing Lemma SDK client.")

        # Build SDK client kwargs — omit token to let SDK use CLI session auth
        client_kwargs = {
            "base_url": settings.LEMMA_API_URL,
            "pod_id": settings.LEMMA_POD_ID,
        }
        if settings.LEMMA_API_KEY:
            client_kwargs["token"] = settings.LEMMA_API_KEY
            logger.info("Using explicit LEMMA_API_KEY for authentication.")
        else:
            logger.info("No LEMMA_API_KEY set — using Lemma CLI session auth.")

        self.client = Lemma(**client_kwargs)
        self.pod = self.client.pod(settings.LEMMA_POD_ID)

    async def health_check(self) -> bool:
        """
        Validates connectivity and authentication against the Lemma API
        by executing a workflows list call on the target pod.
        """
        try:
            logger.info("Conducting Lemma Gateway SDK health check.")
            await run_in_threadpool(self.pod.workflows.list)
            logger.info("Lemma Gateway health check succeeded.")
            return True
        except Exception as exc:
            logger.error(f"Health validation encountered error: {str(exc)}")
            return False

    async def chat(self, message: str) -> Dict[str, Any]:
        """
        Interacts with the customer support workflow:
        1. Creates a workflow run.
        2. Submits the message to the intake form node.
        3. Polls until completion.
        4. Extracts and returns the reply content.
        """
        logger.info("Initiating customer support workflow run via Lemma SDK.")
        try:
            # 1. Create the workflow run
            run = await run_in_threadpool(
                self.pod.workflows.run,
                self.settings.LEMMA_WORKFLOW_NAME
            )
            # 2. Submit the form to the intake node
            if run.active_wait and run.active_wait.node_id == "intake":
                run = await run_in_threadpool(
                    self.pod.workflows.submit_form,
                    run.id,
                    node_id="intake",
                    inputs={"message": message}
                )
            
            # 3. Poll until completed or failed
            attempts = 0
            # Wait up to 60 seconds (60 * 1 second)
            while run.status not in ["COMPLETED", "FAILED", "CANCELLED"] and attempts < 60:
                await asyncio.sleep(1.0)
                run = await run_in_threadpool(
                    self.pod.workflows.run_get,
                    run.id
                )
                attempts += 1
            
            # 4. Handle failed/cancelled status or timeout
            status = str(run.status)
            if "COMPLETED" not in status:
                err_msg = run.error or f"Workflow execution failed or timed out with status {run.status}"
                raise LemmaGatewayError(err_msg)
            
            # 5. Extract assistant response from run data
            response_text = None
            
            # Path A: Check step history
            step_history = run.step_history or []
            for step in step_history:
                if getattr(step, "node_id", None) == "customer_support" and getattr(step, "output_data", None):
                    data = step.output_data
                    if isinstance(data, dict):
                        response_text = data.get("answer") or data.get("text") or data.get("response") or data.get("output")
                    elif isinstance(data, str):
                        response_text = data
                    if response_text:
                        break

            # Path B: Check execution context
            if not response_text and run.execution_context:
                ctx = getattr(run.execution_context, "additional_properties", {}) or {}
                for node_id, data in ctx.items():
                    if node_id == "customer_support" and data:
                        if isinstance(data, dict):
                            response_text = data.get("answer") or data.get("text") or data.get("response") or data.get("output")
                        elif isinstance(data, str):
                            response_text = data
                        if response_text:
                            break

            # Path C: Fallback search of any key in execution context
            if not response_text and run.execution_context:
                ctx = getattr(run.execution_context, "additional_properties", {}) or {}
                for node_id, data in ctx.items():
                    if isinstance(data, dict):
                        response_text = data.get("answer") or data.get("text") or data.get("response") or data.get("output")
                        if response_text:
                            break

            if not response_text:
                logger.error("Failed to extract assistant response from SDK run output.")
                raise LemmaGatewayError("Response text could not be extracted from the workflow execution context.")

            logger.info("Successfully fetched response from Lemma Workflow.")

            # 6. Return structured format
            return {
                "success": True,
                "response": response_text,
                "source": "lemma-sdk",
                "timestamp": datetime.utcnow(),
                "metadata": {}
            }

        except LemmaAuthError as exc:
            logger.error(f"Lemma SDK authentication failed: {exc}")
            raise LemmaGatewayAuthError(str(exc)) from exc
        except LemmaNotFoundError as exc:
            logger.error(f"Lemma SDK workflow or pod resource not found: {exc}")
            raise LemmaGatewayNotFoundError(str(exc)) from exc
        except LemmaTimeoutError as exc:
            logger.error(f"Lemma SDK operation timed out: {exc}")
            raise LemmaGatewayTimeoutError(str(exc)) from exc
        except LemmaConnectionError as exc:
            logger.error(f"Lemma SDK connection failure: {exc}")
            raise LemmaGatewayConnectionError(str(exc)) from exc
        except LemmaAPIError as exc:
            logger.error(f"Lemma SDK API error: {exc}")
            raise LemmaGatewayError(str(exc)) from exc
        except LemmaError as exc:
            logger.error(f"Lemma SDK base error: {exc}")
            raise LemmaGatewayError(str(exc)) from exc
        except Exception as exc:
            logger.error(f"Unexpected error in LemmaService SDK implementation: {exc}", exc_info=True)
            raise LemmaGatewayError(str(exc)) from exc

    def close(self) -> None:
        """Gracefully release client resources."""
        if hasattr(self, "client") and self.client:
            try:
                self.client.close()
            except Exception as e:
                logger.warning(f"Error closing Lemma SDK client: {e}")