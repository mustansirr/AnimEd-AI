from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain_core.tools import tool
import asyncio
import time
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class RateLimitedChatGroq(ChatGroq):
    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        try:
            return await super()._agenerate(messages, stop, run_manager, **kwargs)
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                logger.warning("Groq rate limit hit, switching to fallback model...")
                await asyncio.sleep(5)
            raise e
    
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        try:
            return super()._generate(messages, stop, run_manager, **kwargs)
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                logger.warning("Groq rate limit hit, switching to fallback model...")
                time.sleep(5)
            raise e

print("Subclassing works")
