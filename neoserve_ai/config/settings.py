"""
Configuration settings for the NeoServe AI multi-agent system.
"""
import os
from typing import Dict, Any, Optional, List
from functools import lru_cache
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AppSettings(BaseSettings):
    # Application settings
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "NeoServe AI")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-this-in-production")
    
    # API settings
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8001"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "true").lower() == "true"
    
    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    
    # Google Cloud settings
    project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
    location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./neoserve_ai.db")
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = os.getenv("BACKEND_CORS_ORIGINS", "*").split(",") if os.getenv("BACKEND_CORS_ORIGINS") else ["*"]
    
    # Agent configurations
    MAX_HISTORY_SIZE: int = int(os.getenv("MAX_HISTORY_SIZE", "20"))
    max_history_size: int = int(os.getenv("MAX_HISTORY_SIZE", "20"))  # Alias for compatibility
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Intent Classifier settings
    INTENT_CLASSIFIER_ENDPOINT_ID: str = os.getenv("INTENT_CLASSIFIER_ENDPOINT_ID", "")
    INTENT_CONFIDENCE_THRESHOLD: float = float(os.getenv("INTENT_CONFIDENCE_THRESHOLD", "0.5"))
    FALLBACK_INTENT: str = os.getenv("FALLBACK_INTENT", "default_fallback")
    
    # Knowledge Base settings
    SEARCH_ENGINE_ID: str = os.getenv("SEARCH_ENGINE_ID", "")
    SEARCH_SERVING_CONFIG: str = os.getenv("SEARCH_SERVING_CONFIG", "default_config")
    KNOWLEDGE_MAX_RESULTS: int = int(os.getenv("KNOWLEDGE_MAX_RESULTS", "3"))
    KNOWLEDGE_SCORE_THRESHOLD: float = float(os.getenv("KNOWLEDGE_SCORE_THRESHOLD", "0.7"))
    
    # Personalization settings
    USER_COLLECTION: str = os.getenv("USER_COLLECTION", "user_profiles")
    INTERACTION_COLLECTION: str = os.getenv("INTERACTION_COLLECTION", "user_interactions")
    ENABLE_PERSONALIZATION: bool = os.getenv("ENABLE_PERSONALIZATION", "true").lower() == "true"
    MAX_INTERACTION_HISTORY: int = int(os.getenv("MAX_INTERACTION_HISTORY", "50"))
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore'  # Ignore extra environment variables

# Base configuration
BASE_CONFIG: Dict[str, Any] = {
    "project_id": os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id"),
    "location": os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
    "environment": os.getenv("ENVIRONMENT", "development"),
    "debug": os.getenv("DEBUG", "false").lower() == "true",
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "max_history_size": int(os.getenv("MAX_HISTORY_SIZE", "20")),
}

# Intent Classifier configuration
INTENT_CLASSIFIER_CONFIG: Dict[str, Any] = {
    "project_id": BASE_CONFIG["project_id"],
    "location": BASE_CONFIG["location"],
    "endpoint_id": os.getenv("INTENT_CLASSIFIER_ENDPOINT_ID", ""),
    "min_confidence_threshold": float(os.getenv("INTENT_CONFIDENCE_THRESHOLD", "0.5")),
    "fallback_intent": "default_fallback",
}

# Knowledge Base configuration
KNOWLEDGE_BASE_CONFIG: Dict[str, Any] = {
    "project_id": BASE_CONFIG["project_id"],
    "location": "global",  # Vertex AI Search is global
    "search_engine_id": os.getenv("SEARCH_ENGINE_ID", ""),
    "serving_config_id": os.getenv("SEARCH_SERVING_CONFIG", "default_config"),
    "max_results": int(os.getenv("KNOWLEDGE_MAX_RESULTS", "3")),
    "score_threshold": float(os.getenv("KNOWLEDGE_SCORE_THRESHOLD", "0.7")),
}

# Personalization configuration
PERSONALIZATION_CONFIG: Dict[str, Any] = {
    "project_id": BASE_CONFIG["project_id"],
    "user_collection": "user_profiles",
    "interaction_collection": "user_interactions",
    "enable_personalization": os.getenv("ENABLE_PERSONALIZATION", "true").lower() == "true",
    "max_interaction_history": int(os.getenv("MAX_INTERACTION_HISTORY", "50")),
}

# Proactive Engagement configuration
PROACTIVE_ENGAGEMENT_CONFIG: Dict[str, Any] = {
    "project_id": BASE_CONFIG["project_id"],
    "topic_id": "proactive-engagements",
    "default_delay_minutes": int(os.getenv("DEFAULT_ENGAGEMENT_DELAY_MINUTES", "60")),
    "max_engagement_attempts": int(os.getenv("MAX_ENGAGEMENT_ATTEMPTS", "3")),
    "enable_proactive_engagement": os.getenv("ENABLE_PROACTIVE_ENGAGEMENT", "true").lower() == "true",
}

# Escalation configuration
ESCALATION_CONFIG: Dict[str, Any] = {
    "project_id": BASE_CONFIG["project_id"],
    "escalation_collection": "escalations",
    "interaction_collection": PERSONALIZATION_CONFIG["interaction_collection"],
    "max_unsuccessful_attempts": int(os.getenv("MAX_UNSUCCESSFUL_ATTEMPTS", "3")),
    "max_wait_time": int(os.getenv("MAX_ESCALATION_WAIT_MINUTES", "30")),
    "support_team_email": os.getenv("SUPPORT_TEAM_EMAIL", "support@example.com"),
    "enable_auto_escalation": os.getenv("ENABLE_AUTO_ESCALATION", "true").lower() == "true",
}

# API configuration
API_CONFIG: Dict[str, Any] = {
    "api_prefix": "/api/v1",
    "title": "NeoServe AI API",
    "description": "Multi-agent customer service and engagement platform",
    "version": "1.0.0",
    "docs_url": "/docs",
    "redoc_url": "/redoc",
    "openapi_url": "/openapi.json",
    "allowed_origins": os.getenv("ALLOWED_ORIGINS", "*").split(","),
    "cors_allow_credentials": os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true",
    "cors_allow_methods": os.getenv("CORS_ALLOW_METHODS", "*").split(","),
    "cors_allow_headers": os.getenv("CORS_ALLOW_HEADERS", "*").split(","),
}

# Authentication configuration
AUTH_CONFIG: Dict[str, Any] = {
    "secret_key": os.getenv("SECRET_KEY", "your-secret-key"),
    "algorithm": "HS256",
    "access_token_expire_minutes": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")),  # 24 hours
    "token_url": "token",
    "enable_auth": os.getenv("ENABLE_AUTH", "false").lower() == "true",
}

# Logging configuration
LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": BASE_CONFIG["log_level"],
            "formatter": "simple" if BASE_CONFIG["environment"] == "development" else "json",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.getenv("LOG_FILE", "neoserve_ai.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "level": BASE_CONFIG["log_level"],
            "formatter": "json",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console", "file"] if os.getenv("LOG_TO_FILE", "false").lower() == "true" else ["console"],
            "level": BASE_CONFIG["log_level"],
            "propagate": True,
        },
        "uvicorn": {
            "handlers": ["console"],
            "level": BASE_CONFIG["log_level"],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": BASE_CONFIG["log_level"],
            "handlers": ["console"],
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": BASE_CONFIG["log_level"],
            "propagate": False,
        },
    },
}

# Combine all configurations
CONFIG: Dict[str, Any] = {
    "base": BASE_CONFIG,
    "intent_classifier": INTENT_CLASSIFIER_CONFIG,
    "knowledge_base": KNOWLEDGE_BASE_CONFIG,
    "personalization": PERSONALIZATION_CONFIG,
    "proactive_engagement": PROACTIVE_ENGAGEMENT_CONFIG,
    "escalation": ESCALATION_CONFIG,
    "api": API_CONFIG,
    "auth": AUTH_CONFIG,
    "logging": LOGGING_CONFIG,
}

@lru_cache()
def get_config() -> AppSettings:
    """
    Get the application configuration.
    
    Returns:
        AppSettings: The application settings
    """
    return AppSettings()

def init_config() -> None:
    """Initialize the configuration."""
    # This will cache the config on first call
    get_config()

def get_agent_config(agent_name: str) -> Dict[str, Any]:
    """
    Get configuration for a specific agent.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Dictionary containing the agent's configuration
        
    Raises:
        ValueError: If the agent name is not recognized
    """
    config = get_config()
    
    if agent_name == "intent_classifier":
        return {
            "project_id": config.project_id,
            "location": config.location,
            "endpoint_id": config.INTENT_CLASSIFIER_ENDPOINT_ID,
            "min_confidence_threshold": config.INTENT_CONFIDENCE_THRESHOLD,
            "fallback_intent": config.FALLBACK_INTENT,
        }
    elif agent_name == "knowledge_agent":
        return {
            "project_id": config.project_id,
            "location": "global",  # Vertex AI Search is global
            "search_engine_id": config.SEARCH_ENGINE_ID,
            "serving_config_id": config.SEARCH_SERVING_CONFIG,
            "max_results": config.KNOWLEDGE_MAX_RESULTS,
            "score_threshold": config.KNOWLEDGE_SCORE_THRESHOLD,
        }
    elif agent_name == "personalization_agent":
        return {
            "project_id": config.project_id,
            "user_collection": config.USER_COLLECTION,
            "interaction_collection": config.INTERACTION_COLLECTION,
            "enable_personalization": config.ENABLE_PERSONALIZATION,
            "max_interaction_history": config.MAX_INTERACTION_HISTORY,
        }
    elif agent_name == "proactive_engagement_agent":
        return {
            "project_id": config.project_id,
            "topic_id": "proactive-engagements",
            "default_delay_minutes": int(os.getenv("DEFAULT_ENGAGEMENT_DELAY_MINUTES", "60")),
            "max_engagement_attempts": int(os.getenv("MAX_ENGAGEMENT_ATTEMPTS", "3")),
            "enable_proactive_engagement": os.getenv("ENABLE_PROACTIVE_ENGAGEMENT", "true").lower() == "true",
        }
    else:
        raise ValueError(f"Unknown agent: {agent_name}")
