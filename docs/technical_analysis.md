# Brohud AI Customer Support: Technical Architecture Analysis

This document provides a comprehensive technical and architectural breakdown of the **Brohud AI Customer Support** application. It details the project's purpose, backend architecture, integration with the Lemma AI platform, custom tool definitions, schemas, and includes the codebase's main files.

---

## 1. Project Overview

### Purpose
**Brohud AI Customer Support** is an intelligent assistant platform designed for **Brohud**, an online streetwear fashion brand. It functions as a conversational customer service representative capable of answering static and dynamic requests about the brand.

### Problem Solved
1. **Customer Service Overhead**: Automates responses to repetitive queries (sizing, shipping, returns).
2. **Real-time Order Information**: Provides status updates on orders without manual human intervention.
3. **Product Concierge**: Suggests products from the catalog matching a specific budget and category.
4. **Issue Escalation**: Automatically collects required information (customer name, issue details) and registers support tickets for human assistance when complex situations arise.

---

## 2. Platform Contributions & Components

The application is split into three main logical tiers:

```
                           +----------------------+
                           |   React/Vite Client  | (TSX, TanStack Router)
                           +----------------------+
                                      |
                                      | HTTP POST (/chat)
                                      v
                           +----------------------+
                           |  FastAPI API Gateway | (Python, Uvicorn)
                           +----------------------+
                                      |
                                      | Lemma SDK (HTTP/JSON Polling)
                                      v
                           +----------------------+
                           |   Lemma Cloud Pod    | (AI Agent, Workflows,
                           |                      |  Knowledge, Tables)
                           +----------------------+
```

1. **React Frontend**: A premium, responsive interface optimized for chat interactions. It communicates with the FastAPI gateway to send messages and render structured agent answers.
2. **FastAPI Gateway**: Acts as the middleware. It handles incoming requests, triggers the Lemma workflow, polls for execution completion, maps exceptions, and formats responses.
3. **Lemma Cloud Platform**: Orchestrates the AI Agent (`customer-support`), stores static business policy documents in `/knowledge` for RAG, executes custom Python tools for order tracking and recommendations, and manages data.

---

## 3. Technology Stack

### Backend
- **Programming Language**: Python 3.10+
- **Web Framework**: FastAPI (v0.100+)
- **ASGI Server**: Uvicorn
- **Settings & Validation**: Pydantic v2 & Pydantic Settings
- **AI SDK**: `lemma-sdk` (>=0.5.3)

### Frontend
- **Framework & Routing**: React 19, TypeScript, Vite, TanStack Router, TanStack Start, React Query
- **Styling**: Tailwind CSS v4, Radix UI primitives, Lucide React icons
- **State & Alerts**: Sonner (toasts), React state hooks

### AI & Knowledge Layer
- **Orchestrator**: Lemma Cloud Platform
- **RAG & Docs**: Markdown-based policy sheets (`shipping_policy.md`, etc.)
- **Execution Engine**: Lemma Workflows

---

## 4. Backend Architecture

The backend gateway is built using clean separation of concerns:

- [main.py](file:///c:/Users/mourya/brohud-ai-support/backend/app/main.py): Sets up the FastAPI app, CORS, error handlers, and initiates the routing tree.
- [routes.py](file:///c:/Users/mourya/brohud-ai-support/backend/app/api/routes.py): Defines the REST endpoints and handles HTTP status mappings for service errors.
- [settings.py](file:///c:/Users/mourya/brohud-ai-support/backend/app/config/settings.py): Validates configurations loaded from environment variables using Pydantic.
- [lemma_service.py](file:///c:/Users/mourya/brohud-ai-support/backend/app/services/lemma_service.py): Wraps the Lemma SDK client, controls runs, handles form submissions, polls workflow states, and extracts LLM answers.
- [logger.py](file:///c:/Users/mourya/brohud-ai-support/backend/app/utils/logger.py): Custom logging middleware that measures and logs the latency of incoming requests.

### Authentication
- The FastAPI gateway uses a pre-configured `LEMMA_API_KEY` to authenticate against the Lemma Cloud API.
- Customer-facing authentication is planned as a future improvement.

### Error Handling
The gateway translates standard Lemma SDK errors into client-facing HTTP exceptions:
- `LemmaAuthError` -> `401 Unauthorized`
- `LemmaNotFoundError` -> `404 Not Found`
- `LemmaTimeoutError` -> `504 Gateway Timeout`
- `LemmaConnectionError` / `LemmaAPIError` -> `502 Bad Gateway`
- Unhandled general exceptions -> `500 Internal Server Error`

---

## 5. Lemma Integration

The application integrates with the Lemma cloud service through the official Python SDK client.

### Request-Response Flow

```
  React Frontend             FastAPI Gateway              Lemma Cloud
        |                           |                          |
        |--- POST /chat ----------->|                          |
        |    {message}              |                          |
        |                           |--- pod.workflows.run()-->|
        |                           |    (Create Run)          |
        |                           |<-- Returns Run ID -------|
        |                           |                          |
        |                           |--- submit_form() ------->|
        |                           |    (Submit message to    |
        |                           |     intake node)         |
        |                           |<-- Returns Run Status ---|
        |                           |                          |
        |                           |=== POLL STATUS loop =====| (Up to 60s)
        |                           |--- run_get() ----------->|
        |                           |<-- Returns Status -------|
        |                           |==========================|
        |                           |                          |
        |                           |--- Extract output -------| (Checks step history
        |                           |    data for answer)      |  & execution context)
        |                           |                          |
        |<-- Returns ChatResponse --|                          |
        |    {success, response}    |                          |
```

---

## 6. AI Features

The Lemma Pod implements several modern agentic patterns:

### 1. Prompt Engineering
The system prompt is defined in [instruction.md](file:///c:/Users/mourya/brohud-ai-support/backend/brohud-ai-support/agents/customer-support/instruction.md). It outlines:
- **Tone & Style**: Friendly, professional, concise, using formatting lists where appropriate.
- **Intent Parsing**: Determines whether a request is informational, requires tool execution, or needs escalation.
- **Strict Boundaries**: Safety guidelines prevent inventing company policies, promising refunds, or guessing dates.

### 2. Retrieval-Augmented Generation (RAG)
The agent has read access to the `/knowledge` directory, which hosts several Markdown reference sheets:
- `shipping_policy.md`
- `refund_policy.md`
- `return_policy.md`
- `faq.md`
- `size_guide.md`
- `product_catalog.md`

### 3. Function Calling (Tools)
The agent executes three python-based custom tools when the customer request demands a business action:
- **`track_order`**: Inspects a dictionary of mock order statuses (`BH1001`, `BH1002`, `BH1003`).
- **`recommend_products`**: Evaluates category and budget inputs to recommend items from the catalog.
- **`create_support_ticket`**: Instantiates a support ticket ID `SUP1001` and guides the user to human help.

---

## 7. Database Configuration

The Lemma pod supports schema-driven tables. The workspace contains a table definition:
- [items.json](file:///c:/Users/mourya/brohud-ai-support/backend/brohud-ai-support/functions/tables/items/items.json): Declares a pod-level shared data table named `items` with columns `title` (text) and `status` (enum: open, in_progress, done).

---

## 8. APIs (Gateway REST Endpoints)

### `GET /health`
- **Purpose**: Verifies gateway operational status.
- **Response**:
  ```json
  {"status": "healthy"}
  ```

### `POST /chat`
- **Purpose**: Submits queries to the AI Customer Support Agent.
- **Request Body**:
  ```json
  {
    "message": "Recommend a hoodie under ₹2000"
  }
  ```
- **Response Body**:
  ```json
  {
    "success": true,
    "response": "Based on your category (hoodie) and budget (₹2000), I recommend the Oversized Hoodie in Black for ₹1999.",
    "source": "lemma-sdk",
    "timestamp": "2026-07-02T05:00:00Z",
    "metadata": {}
  }
  ```

---

## 9. Deployment Strategy

- **Frontend**: Scaled on Vercel utilizing TanStack Start Nitro routing.
- **Backend API Gateway**: Hosted on Render using Uvicorn.
- **AI Core**: Maintained in a dedicated Lemma Cloud Pod, providing elastic orchestration.

---

## 10. Code Reference

Here are the complete implementations of the key gateway and pod files.

### A. FastAPI Entrypoint: `main.py`
[main.py](file:///c:/Users/mourya/brohud-ai-support/backend/app/main.py)
```python
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from .api.routes import router as api_router
from .config.settings import settings
from .utils.logger import LoggingMiddleware

logger = logging.getLogger("main")

app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI API Gateway connecting the front-end application to Lemma AI Workflows.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.DEBUG
)

# Enable logging middleware
app.add_middleware(LoggingMiddleware)

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routing components
app.include_router(api_router)

# Centralized exception handling
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
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
    logger.info(f"Initializing {settings.APP_NAME} in {'DEBUG' if settings.DEBUG else 'PRODUCTION'} mode.")
    logger.info("FastAPI service successfully started.")

@app.get("/", tags=["General"])
async def root():
    return {
        "app": settings.APP_NAME,
        "status": "operational",
        "documentation_docs": "/docs",
        "documentation_redoc": "/redoc"
    }
```

---

### B. Gateway Routes: `routes.py`
[routes.py](file:///c:/Users/mourya/brohud-ai-support/backend/app/api/routes.py)
```python
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

logger = logging.getLogger("api_routes")
router = APIRouter()

def get_lemma_service() -> LemmaService:
    return LemmaService(settings)

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check"
)
async def health_check():
    return {"status": "healthy"}

@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat Gateway"
)
@router.post("/chat/", response_model=ChatResponse, include_in_schema=False)
async def chat_gateway(
    request: ChatRequest,
    lemma_service: LemmaService = Depends(get_lemma_service)
):
    message = request.message.strip()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request message cannot be empty."
        )

    try:
        logger.info(f"Forwarding chat query to Lemma Service.")
        result = await lemma_service.chat(message)
        
        return ChatResponse(
            success=result["success"],
            response=result["response"],
            source=result["source"],
            timestamp=result["timestamp"],
            metadata=result.get("metadata")
        )

    except LemmaGatewayAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Gateway authentication failed against backend support servers."
        )
    except LemmaGatewayNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested customer support workflow or pod could not be found."
        )
    except LemmaGatewayTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Connection timed out while waiting for customer support agent to compile a response."
        )
    except (LemmaGatewayConnectionError, LemmaGatewayError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="API Gateway encountered an error communicating with upstream support systems."
        )
```

---

### C. SDK Integrator Service: `lemma_service.py`
[lemma_service.py](file:///c:/Users/mourya/brohud-ai-support/backend/app/services/lemma_service.py)
```python
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

class LemmaGatewayError(Exception): pass
class LemmaGatewayAuthError(LemmaGatewayError): pass
class LemmaGatewayNotFoundError(LemmaGatewayError): pass
class LemmaGatewayTimeoutError(LemmaGatewayError): pass
class LemmaGatewayConnectionError(LemmaGatewayError): pass

class LemmaService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = Lemma(
            token=settings.LEMMA_API_KEY,
            base_url=settings.LEMMA_API_URL
        )
        self.pod = self.client.pod(settings.LEMMA_POD_ID)

    async def chat(self, message: str) -> Dict[str, Any]:
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
            
            # 3. Poll until completed or failed (60s maximum)
            attempts = 0
            while run.status not in ["COMPLETED", "FAILED", "CANCELLED"] and attempts < 60:
                await asyncio.sleep(1.0)
                run = await run_in_threadpool(
                    self.pod.workflows.run_get,
                    run.id
                )
                attempts += 1
            
            if "COMPLETED" not in str(run.status):
                err_msg = run.error or f"Workflow execution failed with status {run.status}"
                raise LemmaGatewayError(err_msg)
            
            # 4. Extract response
            response_text = None
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

            if not response_text:
                raise LemmaGatewayError("Response text could not be extracted from the workflow execution.")

            return {
                "success": True,
                "response": response_text,
                "source": "lemma-sdk",
                "timestamp": datetime.utcnow(),
                "metadata": {}
            }

        except LemmaAuthError as exc:
            raise LemmaGatewayAuthError(str(exc)) from exc
        except LemmaNotFoundError as exc:
            raise LemmaGatewayNotFoundError(str(exc)) from exc
        except LemmaTimeoutError as exc:
            raise LemmaGatewayTimeoutError(str(exc)) from exc
        except LemmaConnectionError as exc:
            raise LemmaGatewayConnectionError(str(exc)) from exc
        except Exception as exc:
            raise LemmaGatewayError(str(exc)) from exc
```

---

### D. Settings Configuration: `settings.py`
[settings.py](file:///c:/Users/mourya/brohud-ai-support/backend/app/config/settings.py)
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    LEMMA_API_URL: str = Field(default="https://api.lemma.work", description="Lemma Cloud API Endpoint")
    LEMMA_API_KEY: str = Field(..., description="API key to authenticate against Lemma API")
    LEMMA_POD_ID: str = Field(..., description="Target Lemma pod ID containing agent resources")
    LEMMA_AGENT_NAME: str = Field(default="customer-support-workflow", description="Target Lemma agent/workflow base name")

    @property
    def LEMMA_WORKFLOW_NAME(self) -> str:
        if self.LEMMA_AGENT_NAME.endswith("-workflow"):
            return self.LEMMA_AGENT_NAME
        return f"{self.LEMMA_AGENT_NAME}-workflow"
    
    APP_NAME: str = Field(default="Brohud AI Support Gateway", description="FastAPI Gateway App Name")
    DEBUG: bool = Field(default=True, description="Enable development debug features")
    HOST: str = Field(default="0.0.0.0", description="IP Host binding address")
    PORT: int = Field(default=8000, description="IP port binding address")

settings = Settings()
```

---

### E. Custom Logging Middleware: `logger.py`
[logger.py](file:///c:/Users/mourya/brohud-ai-support/backend/app/utils/logger.py)
```python
import logging
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

gateway_logger = logging.getLogger("gateway")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        
        gateway_logger.info(
            f"Incoming Request - Method: {request.method} | Path: {request.url.path} | Client: {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            response = await call_next(request)
            process_time = (time.perf_counter() - start_time) * 1000
            gateway_logger.info(
                f"Response Sent - Path: {request.url.path} | Status Code: {response.status_code} | Duration: {process_time:.2f}ms"
            )
            return response
        except Exception as exc:
            process_time = (time.perf_counter() - start_time) * 1000
            logging.getLogger("errors").exception(
                f"Request Failed - Path: {request.url.path} | Error: {str(exc)} | Duration: {process_time:.2f}ms"
            )
            raise exc
```

---

### F. Lemma Agent Definition: `customer-support.json`
[customer-support.json](file:///c:/Users/mourya/brohud-ai-support/backend/brohud-ai-support/agents/customer-support/customer-support.json)
```json
{
  "name": "customer-support",
  "description": "AI customer support agent for Brohud that assists customers with product information, shipping, returns, refunds, sizing, and general support queries.",
  "instruction": {
    "$file": "instruction.md"
  },
  "toolsets": [
    "POD"
  ],
  "visibility": "POD",
  "permissions": {
    "grants": [
      {
        "resource_type": "folder",
        "resource_name": "/knowledge",
        "permission_ids": [
          "folder.read"
        ]
      }
    ]
  }
}
```

---

### G. Lemma Workflow Definition: `customer-support-workflow.json`
[customer-support-workflow.json](file:///c:/Users/mourya/brohud-ai-support/backend/brohud-ai-support/workflows/customer-support-workflow/customer-support-workflow.json)
```json
{
  "name": "customer-support-workflow",
  "description": "Orchestrates customer support requests for Brohud.",
  "start": {
    "type": "MANUAL"
  },
  "nodes": [
    {
      "id": "intake",
      "type": "FORM",
      "label": "Customer Input",
      "config": {
        "input_schema": {
          "type": "object",
          "properties": {
            "message": {
              "type": "string"
            }
          },
          "required": [
            "message"
          ]
        }
      }
    },
    {
      "id": "customer_support",
      "type": "AGENT",
      "label": "Customer Support Agent",
      "config": {
        "agent_name": "customer-support",
        "input_mapping": {
          "message": {
            "type": "expression",
            "value": "intake.message"
          }
        }
      }
    },
    {
      "id": "end",
      "type": "END",
      "label": "Response Sent"
    }
  ],
  "edges": [
    {
      "id": "edge1",
      "source": "intake",
      "target": "customer_support"
    },
    {
      "id": "edge2",
      "source": "customer_support",
      "target": "end"
    }
  ],
  "visibility": "POD"
}
```
