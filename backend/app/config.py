from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    mongo_uri: str
    db_name: str = "omnisales"
    openrouter_api_key: str = ""
    secret_key: str = ""
    frontend_url: str = "http://localhost:5173"
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()
