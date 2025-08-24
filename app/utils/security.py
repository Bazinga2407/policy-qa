import os
from fastapi import HTTPException, Header
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

def require_auth(x_api_key: Optional[str] = Header(None)):
    """
    Validate API key from X-API-Key header against APP_SECRET from .env
    """
    expected_key = os.getenv("APP_SECRET")
    
    if not expected_key:
        raise HTTPException(status_code=500, detail="APP_SECRET not configured")
    
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")
    
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")
    
    return True