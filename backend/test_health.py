import asyncio
import logging
from app.config.settings import settings
from app.services.lemma_service import LemmaService

logging.basicConfig(level=logging.DEBUG)

async def main():
    print("Testing LemmaService health_check")
    svc = LemmaService(settings)
    result = await svc.health_check()
    print(f"Health Check Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
