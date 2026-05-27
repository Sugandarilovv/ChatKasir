from enum import IntEnum

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# ── Error Codes ───────────────────────────────────────────────────────────────

class ErrorCode(IntEnum):
    UNKNOWN           = 1000
    INVALID_INPUT     = 1001
    MODEL_NOT_LOADED  = 1002
    INFERENCE_FAILED  = 1003
    UNAUTHORIZED      = 4010
    NOT_FOUND         = 4040


# ── Custom Exceptions ─────────────────────────────────────────────────────────

class AI2BaseException(Exception):
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN,
        status_code: int = 500,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(message)


class InvalidInputError(AI2BaseException):
    def __init__(self, message: str = "Invalid input data"):
        super().__init__(message, ErrorCode.INVALID_INPUT, 422)


class ModelNotLoadedError(AI2BaseException):
    def __init__(self, message: str = "Model is not loaded"):
        super().__init__(message, ErrorCode.MODEL_NOT_LOADED, 503)


class InferenceFailedError(AI2BaseException):
    def __init__(self, message: str = "Inference failed"):
        super().__init__(message, ErrorCode.INFERENCE_FAILED, 500)


class UnauthorizedError(AI2BaseException):
    def __init__(self, message: str = "Unauthorized - invalid or missing API key"):
        super().__init__(message, ErrorCode.UNAUTHORIZED, 401)


# ── Handler Registration ──────────────────────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(AI2BaseException)
    async def ai2_exception_handler(request: Request, exc: AI2BaseException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "error_code": int(exc.error_code),
                "message": exc.message,
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "error_code": int(ErrorCode.UNKNOWN),
                "message": "An unexpected error occurred.",
            },
        )
