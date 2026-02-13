import httpx
import logging
from typing import Optional, List, Dict
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

OLLAMA_API_URL = settings.ollama_api_url


async def generate_with_ollama(prompt: str, model: str = "olmo:1b") -> Optional[str]:
    """Generate response using OLMo-1B via Ollama"""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": 256
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_API_URL}/api/generate",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
    except Exception as e:
        logger.error(f"Ollama error: {e}", exc_info=True)
        return None


async def chat_with_ollama(messages: List[Dict[str, str]], model: str = "olmo:1b") -> Optional[str]:
    """Chat using OLMo-1B via Ollama"""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_API_URL}/api/chat",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "").strip()
    except Exception as e:
        logger.error(f"Ollama chat error: {e}", exc_info=True)
        return None
