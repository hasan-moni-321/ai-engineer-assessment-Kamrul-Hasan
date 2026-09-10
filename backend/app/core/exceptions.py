class AppError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ConfigurationError(AppError):
    status_code = 500
    code = "configuration_error"


class UpstreamServiceError(AppError):
    status_code = 503
    code = "upstream_service_error"


class RetrievalError(AppError):
    status_code = 503
    code = "retrieval_error"


class NoGroundedContextError(AppError):
    status_code = 422
    code = "insufficient_context"
