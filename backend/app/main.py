import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from .api.routes import router as api_router
from .config.settings import settings
from .utils.logger import LoggingMiddleware

# Define root logger levels
logger = logging.getLogger("main")  # reload trigger

# Initialize FastAPI application with custom documentation settings
app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI API Gateway connecting the front-end application to Lemma AI Workflows.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.DEBUG
)

# 1. Enable logging middleware
app.add_middleware(LoggingMiddleware)

# 2. Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Register routing components
app.include_router(api_router)


# 4. Centralized exception handling
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles and standardizes validation errors (422) for client consumption."""
    logger.error(f"Validation failure for path {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": "Validation Error",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unhandled internal application errors (500)."""
    logger.error(f"Global unhandled error for path {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred while processing your request."
        }
    )


@app.on_event("startup")
async def startup_event():
    """Triggers logging and initialization checks during gateway bootup."""
    logger.info(f"Initializing {settings.APP_NAME} in {'DEBUG' if settings.DEBUG else 'PRODUCTION'} mode.")
    logger.info("FastAPI service successfully started.")


@app.get("/", tags=["General"])
async def root():
    """Simple root welcome endpoint displaying gateway metadata."""
    return {
        "app": settings.APP_NAME,
        "status": "operational",
        "documentation_docs": "/docs",
        "documentation_redoc": "/redoc"
    }
