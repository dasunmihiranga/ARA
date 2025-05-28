from typing import Dict, List
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
MODELS_DIR = DATA_DIR / "models"
CACHE_DIR = DATA_DIR / "cache"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
KNOWLEDGE_GRAPHS_DIR = DATA_DIR / "knowledge_graphs"

# File extensions
SUPPORTED_DOCUMENT_EXTENSIONS = [".pdf", ".doc", ".docx", ".txt", ".md", ".html", ".htm"]
SUPPORTED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
SUPPORTED_VIDEO_EXTENSIONS = [".mp4", ".avi", ".mov", ".wmv"]
SUPPORTED_AUDIO_EXTENSIONS = [".mp3", ".wav", ".ogg", ".flac"]

# Search settings
DEFAULT_SEARCH_ENGINES = ["duckduckgo", "searx"]
MAX_SEARCH_RESULTS = 100
SEARCH_TIMEOUT = 30  # seconds
SEARCH_RETRY_ATTEMPTS = 3
SEARCH_RETRY_DELAY = 1  # seconds

# Content extraction settings
MAX_CONTENT_LENGTH = 1000000  # characters
MIN_CONTENT_LENGTH = 100  # characters
EXTRACTION_TIMEOUT = 60  # seconds
CLEAN_HTML = True
REMOVE_ADS = True
REMOVE_NAVIGATION = True

# Analysis settings
DEFAULT_SUMMARY_LENGTH = 200  # words
MAX_SUMMARY_LENGTH = 1000  # words
MIN_CONFIDENCE_THRESHOLD = 0.7
SENTIMENT_THRESHOLDS = {
    "positive": 0.3,
    "negative": -0.3,
    "neutral": (-0.3, 0.3)
}

# LLM settings
DEFAULT_MODEL = "llama2"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2000
DEFAULT_TOP_P = 0.9
DEFAULT_FREQUENCY_PENALTY = 0.0
DEFAULT_PRESENCE_PENALTY = 0.0

# Cache settings
CACHE_TTL = 3600  # seconds
MAX_CACHE_SIZE = 1000  # items
CACHE_CLEANUP_INTERVAL = 300  # seconds

# API settings
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
RATE_LIMIT_CALLS = 100
RATE_LIMIT_PERIOD = 60  # seconds

# Authentication settings
TOKEN_EXPIRY = 3600  # seconds
REFRESH_TOKEN_EXPIRY = 604800  # seconds (7 days)
MIN_PASSWORD_LENGTH = 8
PASSWORD_REQUIREMENTS = {
    "uppercase": True,
    "lowercase": True,
    "numbers": True,
    "special_chars": True
}

# Error messages
ERROR_MESSAGES = {
    "invalid_input": "Invalid input provided",
    "not_found": "Resource not found",
    "unauthorized": "Unauthorized access",
    "forbidden": "Access forbidden",
    "rate_limited": "Rate limit exceeded",
    "server_error": "Internal server error",
    "validation_error": "Validation error",
    "timeout": "Request timed out",
    "connection_error": "Connection error"
}

# Logging settings
LOG_LEVELS = {
    "debug": 10,
    "info": 20,
    "warning": 30,
    "error": 40,
    "critical": 50
}
DEFAULT_LOG_LEVEL = "info"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Export settings
SUPPORTED_EXPORT_FORMATS = ["pdf", "html", "markdown", "json", "yaml"]
DEFAULT_EXPORT_FORMAT = "pdf"
MAX_EXPORT_SIZE = 10485760  # 10MB

# Session settings
SESSION_TIMEOUT = 1800  # seconds (30 minutes)
MAX_SESSIONS_PER_USER = 5
SESSION_CLEANUP_INTERVAL = 300  # seconds

# Validation patterns
PATTERNS = {
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "url": r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$",
    "date": r"^\d{4}-\d{2}-\d{2}$",
    "time": r"^\d{2}:\d{2}:\d{2}$",
    "datetime": r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
    "phone": r"^\+?1?\d{9,15}$",
    "username": r"^[a-zA-Z0-9_-]{3,16}$",
    "password": r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
}

# HTTP status codes
HTTP_STATUS = {
    "OK": 200,
    "CREATED": 201,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "METHOD_NOT_ALLOWED": 405,
    "RATE_LIMITED": 429,
    "INTERNAL_ERROR": 500,
    "SERVICE_UNAVAILABLE": 503
}

# MIME types
MIME_TYPES = {
    "pdf": "application/pdf",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "txt": "text/plain",
    "md": "text/markdown",
    "html": "text/html",
    "json": "application/json",
    "yaml": "application/x-yaml",
    "jpg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "mp4": "video/mp4"
} 