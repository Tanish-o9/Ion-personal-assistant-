"""
Phase 76: JARVIS Developer SDK Exceptions
"""

class JarvisSDKError(Exception):
    """Base exception for all JARVIS SDK errors."""
    def __init__(self, message: str, status_code: int = 400, details: str = ""):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details

class AuthenticationError(JarvisSDKError):
    def __init__(self, message: str = "Authentication failed: Invalid API key or credentials.", details: str = ""):
        super().__init__(message, status_code=401, details=details)

class AuthorizationError(JarvisSDKError):
    def __init__(self, message: str = "Authorization failed: Required scope missing.", details: str = ""):
        super().__init__(message, status_code=403, details=details)

class ValidationError(JarvisSDKError):
    def __init__(self, message: str = "Validation failed: Invalid request payload.", details: str = ""):
        super().__init__(message, status_code=422, details=details)

class RateLimitError(JarvisSDKError):
    def __init__(self, message: str = "Rate limit exceeded: Please wait before retrying.", details: str = ""):
        super().__init__(message, status_code=429, details=details)

class TimeoutError(JarvisSDKError):
    def __init__(self, message: str = "Request timed out.", details: str = ""):
        super().__init__(message, status_code=408, details=details)

class ServerError(JarvisSDKError):
    def __init__(self, message: str = "Internal server error.", details: str = ""):
        super().__init__(message, status_code=500, details=details)

class CapabilityError(JarvisSDKError):
    def __init__(self, message: str = "Capability execution error.", details: str = ""):
        super().__init__(message, status_code=400, details=details)

class ApprovalRequiredError(JarvisSDKError):
    def __init__(self, message: str = "Action requires Human-in-the-Loop approval.", approval_id: str = "", details: str = ""):
        super().__init__(message, status_code=202, details=details)
        self.approval_id = approval_id
