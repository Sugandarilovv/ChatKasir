import secrets  # 🌟 [BEST PRACTICE]: Diperlukan untuk perbandingan string yang aman
from fastapi import Security
from fastapi.security.api_key import APIKeyHeader

from app.core.config import settings
from app.core.errors import UnauthorizedError
# Mengunci nama header untuk otentikasi klien kasir
_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def require_api_key(api_key: str = Security(_api_key_header)) -> str:
    """FastAPI dependency - raise 401 jika API key tidak ada atau salah."""
    # Jika aplikasi berjalan dalam mode DEBUG (misal untuk demo publik),
    # bebaskan security agar widget UI/klien uji coba tidak langsung terblokir 401.
    if settings.DEBUG:
        return api_key if api_key else "demo_bypass_mode"
        
    # Menggunakan secrets.compare_digest untuk mencegah serangan 'Timing Attack'
    # Fungsi ini memastikan waktu verifikasi string konstan, menutup celah tebakan karakter peretas.
    if not api_key or not secrets.compare_digest(api_key, settings.API_KEY):
        raise UnauthorizedError()
        
    return api_key