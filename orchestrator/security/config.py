import os
from typing import List

# Centralized security settings loaded from environment variables with safe defaults
ALLOWED_ORIGINS: List[str] = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173").split(",")
    if origin.strip()
]

# Rate Limits (requests per minute)
RATE_LIMIT_LOGIN: int = int(os.getenv("RATE_LIMIT_LOGIN", "10"))
RATE_LIMIT_CHAT: int = int(os.getenv("RATE_LIMIT_CHAT", "30"))
RATE_LIMIT_UPLOAD: int = int(os.getenv("RATE_LIMIT_UPLOAD", "15"))

# Resource Bounds
MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
MAX_REQUEST_BODY_BYTES: int = MAX_UPLOAD_SIZE_MB * 1024 * 1024
MAX_WS_MESSAGE_SIZE_BYTES: int = int(os.getenv("MAX_WS_MESSAGE_SIZE_BYTES", "10485760")) # 10MB
MAX_CONCURRENT_JOBS_PER_USER: int = int(os.getenv("MAX_CONCURRENT_JOBS", "3"))
MAX_WS_CONNECTIONS_PER_USER: int = int(os.getenv("MAX_WS_CONNECTIONS", "5"))

ALLOWED_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "text/plain",
    "text/markdown",
}

ALLOWED_FILE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".txt", ".md"}
