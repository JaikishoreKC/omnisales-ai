import httpx
import logging
from typing import Optional
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

OPENROUTER_API_KEY = settings.openrouter_api_key
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OLLAMA_API_URL = settings.ollama_api_url
DEFAULT_MODEL = "openai/gpt-4o-mini"
OLLAMA_MODEL = "qwen2.5:3b"


async def generate_response(prompt: str, model: str = DEFAULT_MODEL) -> Optional[str]:
    """
    Generate AI response using OpenRouter (if key provided) or Ollama (free local AI)
    
    Args:
        prompt: The prompt to send to AI
        model: Model to use (for OpenRouter only)
        
    Returns:
        Generated text response or None if failed
    """
    # Try OpenRouter first if API key is provided
    if OPENROUTER_API_KEY:
        return await _call_openrouter(prompt, model)
    
    # Fall back to Ollama (free local AI)
    return await _call_ollama(prompt)


async def _call_openrouter(prompt: str, model: str) -> Optional[str]:
    """Call OpenRouter API (paid service with better models)"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
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
