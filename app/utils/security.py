from fastapi import Header, HTTPException, status
from ..config import settings

def require_auth(x_api_key: str | None = Header(default=None)):
    if settings.APP_SECRET and x_api_key != settings.APP_SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing X-API-Key")
