from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable overrides."""
    
    APP_NAME: str = "AI Medical Assistant - Agentic AI Healthcare Chatbot"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # LLM Settings (OpenAI-compatible)
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # PDF Processing Limits
    MAX_PDF_SIZE_MB: int = 5
    MAX_EXTRACTED_CHARS: int = 25000
    
    # Standard Persistent Safety Disclaimer
    PERSISTENT_SAFETY_DISCLAIMER: str = (
        "Educational demo only. Not medical advice. For urgent or severe symptoms, "
        "contact local emergency services or a qualified healthcare professional."
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def is_local_demo_mode(self) -> bool:
        """Returns True if no OpenAI API key is supplied."""
        return not bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY.strip())


settings = Settings()
