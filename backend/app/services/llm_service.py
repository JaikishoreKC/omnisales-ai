import httpx
import logging
from typing import Optional, Callable
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

OPENROUTER_API_KEY = settings.openrouter_api_key
OPENROUTER_MODEL = settings.openrouter_model
OPENROUTER_BASE_URL = settings.openrouter_base_url.rstrip("/")
OLLAMA_API_URL = settings.ollama_url or settings.ollama_api_url
OLLAMA_MODEL = "qwen2.5:3b"


async def generate_response(prompt: str) -> Optional[str]:
    """
    Generate AI response using OpenRouter (primary) or Ollama (fallback)
    
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

    if OPENROUTER_API_KEY:
        providers.append(_call_openrouter)

    if OLLAMA_API_URL:
        providers.append(_call_ollama)

    return providers


async def _call_openrouter(prompt: str) -> Optional[str]:
    """Call OpenRouter API (primary cloud provider)."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content")
        return None
    except Exception as e:
        logger.error(f"OpenRouter API error: {e}", exc_info=True)
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
