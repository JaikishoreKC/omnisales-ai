import httpx
import logging
from typing import Optional, Callable
from app.config import get_settings
from groq import Groq

logger = logging.getLogger(__name__)
settings = get_settings()

GROQ_API_KEY = settings.groq_api_key
GROQ_MODEL = "llama3-8b-8192"
OLLAMA_API_URL = settings.ollama_url or settings.ollama_api_url
OLLAMA_MODEL = "qwen2.5:3b"


async def generate_response(prompt: str) -> Optional[str]:
    """
    Generate AI response using Groq (primary) or Ollama (fallback)
    
    Args:
        prompt: The prompt to send to AI
        
    Returns:
        Generated text response or None if failed
    """
    providers = _get_providers()

    for provider in providers:
        try:
            response = await provider(prompt)
            if response:
                return response
        except Exception as exc:
            logger.error(f"AI provider error: {exc}", exc_info=True)
            continue

    return "I'm sorry, I couldn't process your request at the moment. Please try again."


def _get_providers() -> list[Callable[[str], Optional[str]]]:
    providers = []

    if GROQ_API_KEY:
        providers.append(_call_groq)

    if OLLAMA_API_URL:
        providers.append(_call_ollama)

    return providers


async def _call_groq(prompt: str) -> Optional[str]:
    """Call Groq API (primary cloud provider)."""
    try:
        client = Groq(api_key=GROQ_API_KEY, timeout=60.0)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        if response and response.choices:
            return response.choices[0].message.content
        return None
    except Exception as e:
        logger.error(f"Groq API error: {e}", exc_info=True)
        return None


async def _call_ollama(prompt: str) -> Optional[str]:
    """Call Ollama API (free local AI)"""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:  # 3 minutes for local AI
            response = await client.post(
                f"{OLLAMA_API_URL}/api/generate",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            if "response" in data:
                return data["response"]
            return None
            
    except httpx.ConnectError:
        logger.error(
            f"Ollama connection failed. Is Ollama running?\n"
            f"Install: https://ollama.ai/download\n"
            f"Download model: ollama pull {OLLAMA_MODEL}\n"
            f"Verify: ollama list"
        )
        return None
    except httpx.ReadTimeout:
        logger.error(
            f"Ollama timeout after 180 seconds. This can happen with:\n"
            f"- Large prompts\n"
            f"- Slow hardware\n"
            f"Try a faster model: ollama pull llama3.2:1b"
        )
        return None
    except Exception as e:
        logger.error(f"Ollama API error: {e}", exc_info=True)
        return None
