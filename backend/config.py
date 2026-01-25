"""
Configuration for the Recommendation Engine
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    API_TITLE: str = "X Recommendation Engine API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database Configuration (currently in-memory, can be extended)
    DATABASE_URL: Optional[str] = None
    USE_VECTOR_DB: bool = False

    # Vector Database (Pinecone/Weaviate)
    VECTOR_DB_TYPE: str = "pinecone"  # "pinecone" or "weaviate"
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_INDEX_NAME: str = "tweets"
    WEAVIATE_URL: Optional[str] = None

    # LLM Configuration (for synthetic data generation and explanations)
    LLM_PROVIDER: str = "openai"  # "openai" or "anthropic"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-3.5-turbo"

    # Ranking Configuration
    RECENCY_DECAY_HOURS: float = 24.0
    MAX_LIKES_NORMALIZATION: int = 10000
    MAX_RETWEETS_NORMALIZATION: int = 2000
    MAX_REPLIES_NORMALIZATION: int = 500
    MAX_BOOKMARKS_NORMALIZATION: int = 1000

    # Diversity Filtering
    MAX_TWEETS_PER_AUTHOR: int = 3
    MAX_TWEETS_PER_TOPIC: int = 5

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
