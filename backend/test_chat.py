import asyncio
import logging
from app.config.settings import settings
from app.services.lemma_service import LemmaService

logging.basicConfig(level=logging.DEBUG)

async def main():
    print("Testing LemmaService chat")
    svc = LemmaService(settings)
    try:
        result = await svc.chat("hello")
        print(f"Chat Result: {result}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(main())
