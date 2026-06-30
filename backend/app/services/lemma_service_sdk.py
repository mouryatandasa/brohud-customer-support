import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

from fastapi.concurrency import run_in_threadpool

from lemma_sdk import Lemma
from lemma_sdk.errors import LemmaAPIError, LemmaError

from ..config.settings import Settings

logger = logging.getLogger("lemma_integration")
class LemmaGatewayError(Exception):
    pass


class LemmaGatewayAuthError(LemmaGatewayError):
    pass


class LemmaGatewayNotFoundError(LemmaGatewayError):
    pass


class LemmaGatewayTimeoutError(LemmaGatewayError):
    pass


class LemmaGatewayConnectionError(LemmaGatewayError):
    pass
class LemmaService:

    def __init__(self, settings: Settings):
        self.settings = settings

        logger.info("Initializing Lemma SDK client.")

        self.client = Lemma(
            token=settings.LEMMA_API_KEY,
            base_url=settings.LEMMA_API_URL
        )

        self.pod = self.client.pod(settings.LEMMA_POD_ID)