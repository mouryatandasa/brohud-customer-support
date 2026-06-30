from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    FastAPI gateway configurations loaded from environment variables or .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    LEMMA_API_URL: str = Field(default="https://api.lemma.work", description="Lemma Cloud API Endpoint")
    LEMMA_API_KEY: str = Field(..., description="API key to authenticate against Lemma API")
    LEMMA_POD_ID: str = Field(..., description="Target Lemma pod ID containing agent resources")
    LEMMA_WORKFLOW_NAME: str = Field(default="customer-support-workflow", description="Workflow name to run support queries")
    
    APP_NAME: str = Field(default="Brohud AI Support Gateway", description="FastAPI Gateway App Name")
    DEBUG: bool = Field(default=True, description="Enable development debug features")
    HOST: str = Field(default="0.0.0.0", description="IP Host binding address")
    PORT: int = Field(default=8000, description="IP port binding address")

# Global settings instance
settings = Settings()
