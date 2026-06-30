import logging
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging format and level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# Standard Logger instances for routing and services
gateway_logger = logging.getLogger("gateway")
lemma_logger = logging.getLogger("lemma_integration")
error_logger = logging.getLogger("errors")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that captures all incoming requests, computes response times,
    and logs them via Python's standard logging library.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        
        # Log request ingestion
        gateway_logger.info(
            f"Incoming Request - Method: {request.method} | Path: {request.url.path} | "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            response = await call_next(request)
            process_time = (time.perf_counter() - start_time) * 1000
            
            # Log successful processing with duration
            gateway_logger.info(
                f"Response Sent - Path: {request.url.path} | "
                f"Status Code: {response.status_code} | Duration: {process_time:.2f}ms"
            )
            return response
            
        except Exception as exc:
            process_time = (time.perf_counter() - start_time) * 1000
            error_logger.exception(
                f"Request Failed - Path: {request.url.path} | Error: {str(exc)} | "
                f"Duration: {process_time:.2f}ms"
            )
            raise exc
