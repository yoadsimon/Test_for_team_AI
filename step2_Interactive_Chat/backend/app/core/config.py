from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore"  # Ignore extra fields in environment variables
    )
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Video Highlights Chat API"
    
    # CORS Settings
    CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React frontend
        "http://localhost:8000",  # Backend
    ]
    
    # Database Settings
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    # Model Settings
    EMBEDDING_MODEL: str = "all-mpnet-base-v2"  # 768-dimensional model
    SIMILARITY_THRESHOLD: float = 0.3  # Minimum similarity score for matching highlights
    
    # API Keys
    GOOGLE_API_KEY: str = ""
    
    @property
    def DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings() 