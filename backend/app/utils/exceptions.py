class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationError(AppException):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, status_code=401)


class PermissionDeniedError(AppException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, status_code=403)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class InvalidFileError(AppException):
    def __init__(self, message: str = "Invalid file"):
        super().__init__(message, status_code=400)


class AnalysisError(AppException):
    def __init__(self, message: str = "Analysis failed"):
        super().__init__(message, status_code=422)
