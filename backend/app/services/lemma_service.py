import os
import json
import logging
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional

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
    Service Layer responsible for interacting with the Lemma CLI.
    Runs the customer support workflow via subprocess command execution.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        logger.info("Initializing Lemma Service CLI wrapper.")

    async def health_check(self) -> bool:
        """
        Validates connectivity and authentication against the Lemma API
        by executing a simple version/doctor/auth check command.
        """
        try:
            logger.info("Conducting Lemma Gateway CLI health check.")
            cmd = ["lemma", "version"]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
            if result.returncode == 0:
                logger.info("Lemma Gateway health check succeeded.")
                return True
            logger.error(f"Lemma CLI version check failed with return code {result.returncode}: {result.stderr}")
            return False
        except Exception as exc:
            logger.error(f"Health validation encountered error: {str(exc)}")
            return False

    async def chat(self, message: str) -> Dict[str, Any]:
        """
        Interacts with the customer support workflow:
        1. Writes message to a temporary JSON file.
        2. Executes the workflow run CLI command.
        3. Parses the output JSON.
        4. Extracts and returns the reply content.
        """
        logger.info("Initiating customer support workflow run via Lemma CLI.")
        temp_file_path = None

        try:
            # 1. Create a temporary JSON file containing: {"message": "<user_message>"}
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
                json.dump({"message": message}, f)
                temp_file_path = f.name
            logger.debug(f"Created temporary input file: {temp_file_path}")

            # 2. Build the command list
            cmd = ["lemma"]
            
            # Pass configurations if they are provided in Settings (non-empty)
            if self.settings.LEMMA_API_KEY:
                cmd.extend(["--token", self.settings.LEMMA_API_KEY])
            
            # Only specify custom server URL if it is not the default cloud endpoint
            if self.settings.LEMMA_API_URL and self.settings.LEMMA_API_URL != "https://api.lemma.work":
                cmd.extend(["--server", self.settings.LEMMA_API_URL])
                
            if self.settings.LEMMA_POD_ID:
                cmd.extend(["--pod", self.settings.LEMMA_POD_ID])

            cmd.extend([
                "workflow", 
                "run", 
                self.settings.LEMMA_WORKFLOW_NAME, 
                "-f", 
                temp_file_path, 
                "--json"
            ])

            # Safely mask the token in logs
            masked_cmd = []
            for c in cmd:
                if self.settings.LEMMA_API_KEY and c == self.settings.LEMMA_API_KEY:
                    masked_cmd.append("********")
                else:
                    masked_cmd.append(c)
            logger.info(f"Executing command: {' '.join(masked_cmd)}")

            # 3. Execute subprocess run in a threadpool to prevent blocking the async loop
            from fastapi.concurrency import run_in_threadpool
            
            result = await run_in_threadpool(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )

            # 4. Check for command failure
            if result.returncode != 0:
                err_msg = result.stderr.strip() or result.stdout.strip() or f"Exit code {result.returncode}"
                # Map specific errors if possible
                if "Unauthorized" in err_msg or "401" in err_msg:
                    raise LemmaGatewayAuthError(f"Lemma CLI authentication failed: {err_msg}")
                elif "Not Found" in err_msg or "404" in err_msg:
                    raise LemmaGatewayNotFoundError(f"Lemma CLI workflow or pod resource not found: {err_msg}")
                else:
                    raise LemmaGatewayError(f"Lemma CLI execution failed: {err_msg}")

            # 5. Parse JSON output
            try:
                run_data = json.loads(result.stdout)
            except json.JSONDecodeError as exc:
                logger.error(f"Failed to parse JSON output from Lemma CLI: {result.stdout}")
                raise LemmaGatewayError(f"Failed to parse JSON output from Lemma CLI: {str(exc)}") from exc

            # Validate run-level failure status
            if run_data.get("status") in ["FAILED", "CANCELLED"] or run_data.get("error"):
                error_detail = run_data.get("error") or "Workflow run failed or was cancelled."
                logger.error(f"Workflow execution failed: {error_detail}")
                raise LemmaGatewayError(f"Workflow execution failed: {error_detail}")

            # 6. Extract the assistant response from the workflow execution
            response_text = None
            
            # Path A: Check step history
            step_history = run_data.get("step_history") or []
            for step in step_history:
                if step.get("node_id") == "customer_support" and step.get("output_data"):
                    data = step["output_data"]
                    if isinstance(data, dict):
                        response_text = data.get("answer") or data.get("text") or data.get("response") or data.get("output")
                    elif isinstance(data, str):
                        response_text = data
                    if response_text:
                        break

            # Path B: Check execution context
            if not response_text:
                ctx = run_data.get("execution_context") or {}
                for node_id, data in ctx.items():
                    if node_id == "customer_support" and data:
                        if isinstance(data, dict):
                            response_text = data.get("answer") or data.get("text") or data.get("response") or data.get("output")
                        elif isinstance(data, str):
                            response_text = data
                        if response_text:
                            break

            # Path C: Fallback search of any key in execution context
            if not response_text:
                ctx = run_data.get("execution_context") or {}
                for node_id, data in ctx.items():
                    if isinstance(data, dict):
                        response_text = data.get("answer") or data.get("text") or data.get("response") or data.get("output")
                        if response_text:
                            break

            if not response_text:
                logger.error("Failed to extract assistant response from CLI run output.")
                raise LemmaGatewayError("Response text could not be extracted from the workflow execution context.")

            logger.info("Successfully fetched response from Lemma Workflow.")

            # 7. Return structured format
            return {
                "success": True,
                "response": response_text,
                "source": "lemma-cli",
                "timestamp": datetime.utcnow(),
                "metadata": {}
            }

        finally:
            # 8. Delete temporary JSON file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logger.debug(f"Deleted temporary input file: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {temp_file_path}: {e}")

    def close(self) -> None:
        """Gracefully release resources (no-op for CLI wrapper)."""
        pass
