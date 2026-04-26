from fastapi import Security
from fastapi.security.api_key import APIKeyHeader

from app.core.config import settings
from app.core.errors import UnauthorizedError

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(api_key: str = Security(_api_key_header)) -> str:
    """FastAPI dependency — raise 401 jika API key tidak ada atau salah."""
    if not api_key or api_key != settings.API_KEY:
        raise UnauthorizedError()
    return api_key
