import logging
from enum import IntEnum

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Inisialisasi Logger produksi untuk mencetak error ke konsol Docker/Hugging Face
logger = logging.getLogger("uvicorn.error")

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

    # 1. Handler untuk Eksepsi Kustom internal ChatKasir
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

    # 2. Overriding error validasi internal FastAPI/Pydantic
    # Agar jika payload Pydantic gagal (salah type data), format response tetap seragam sesuai kontrak API
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Ambil detail pesan error pertama yang dideteksi oleh Pydantic
        errors = exc.errors()
        msg = errors[0]["msg"] if errors else "Validation error"
        loc = " -> ".join(str(x) for x in errors[0]["loc"]) if errors else ""
        full_message = f"{msg} ({loc})" if loc else msg
        
        return JSONResponse(
            status_code=422,
            content={
                "error": True,
                "error_code": int(ErrorCode.INVALID_INPUT),
                "message": f"Input validation failed: {full_message}",
            },
        )

    # 3. Handler untuk Error Global Sistem/Bahasa Python (Sangat Aman)
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # Wajib mencetak stack trace asli ke log konsol kontainer Docker
        # Tanpa baris ini, Anda tidak akan bisa melakukan debugging di Hugging Face jika server crash
        logger.error(f"Unhandled Exception occurred: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "error_code": int(ErrorCode.UNKNOWN),
                "message": "An unexpected server error occurred.",
            },
        )