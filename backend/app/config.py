from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    mongo_uri: str
    db_name: str = "omnisales"
    openrouter_api_key: str = ""
    groq_api_key: str = ""
    secret_key: str = ""
    api_secret_key: str = ""  # API key for authentication
    frontend_url: str = "http://localhost:5173"
    environment: str = "development"
    
    # WhatsApp Business API
    whatsapp_api_token: str = ""
    whatsapp_phone_id: str = ""
    whatsapp_verify_token: str = ""
    
    # SuperU Voice API
    superu_api_key: str = ""
    superu_from_number: str = ""
    superu_webhook_url: str = ""
    
    # Ollama (OLMo-1B)
    ollama_api_url: str = "http://localhost:11434"
    ollama_url: str = ""  # Optional alias for OLLAMA_URL env var
    
    # POS System
    pos_api_url: str = ""
    pos_api_key: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()
