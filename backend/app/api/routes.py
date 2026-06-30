import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from ..models.chat import ChatRequest, ChatResponse
from ..config.settings import settings
from ..services.lemma_service import (
    LemmaService,
    LemmaGatewayAuthError,
    LemmaGatewayNotFoundError,
    LemmaGatewayTimeoutError,
    LemmaGatewayConnectionError,
    LemmaGatewayError
)

# Set up logging for API routes
logger = logging.getLogger("api_routes")
router = APIRouter()


# Dependency injection provider for LemmaService
def get_lemma_service() -> LemmaService:
    """Provides a thread-safe singleton-like instance of LemmaService."""
    return LemmaService(settings)


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Returns the gateway health status."
)
async def health_check():
    """Simple status check to confirm gateway service is running."""
    return {"status": "healthy"}


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat Gateway",
    description="Routes client chat messages to the Lemma Workflow and returns AI Support agent responses."
)
@router.post("/chat/", response_model=ChatResponse, include_in_schema=False)
async def chat_gateway(
    request: ChatRequest,
    lemma_service: LemmaService = Depends(get_lemma_service)
):
    """
    Receives user messages, forwards them to the Lemma workflow layer,
    polls until execution is complete, and serves the structured answer.
    """
    # Clean and validate input message
    message = request.message.strip()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request message cannot be empty or consist solely of whitespace."
        )

    try:
        logger.info(f"Forwarding chat query: '{message[:40]}...' to Lemma Service.")
        result = await lemma_service.chat(message)
        
        return ChatResponse(
            success=result["success"],
            response=result["response"],
            source=result["source"],
            timestamp=result["timestamp"],
            metadata=result.get("metadata")
        )

    except LemmaGatewayAuthError as exc:
        logger.error(f"Authentication failure at gateway: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Gateway authentication failed against backend support servers."
        )
    except LemmaGatewayNotFoundError as exc:
        logger.error(f"Target resource missing: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested customer support workflow or pod could not be found."
        )
    except LemmaGatewayTimeoutError as exc:
        logger.error(f"Gateway request timeout: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Connection timed out while waiting for customer support agent to compile a response."
        )
    except (LemmaGatewayConnectionError, LemmaGatewayError) as exc:
        logger.error(f"Gateway network transport error: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="API Gateway encountered an error communicating with upstream support systems."
        )
    except Exception as exc:
        logger.error(f"Unexpected exception caught in chat route handler: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred inside the gateway."
        )
