"""Authentication module for API."""

from fastapi import HTTPException, Header, status
import os


def verify_api_key(x_api_key: str = Header(None, alias="X-API-Key")) -> str:
    """
    Verify API key from request header.
    
    Args:
        x_api_key: API key from X-API-Key header
        
    Returns:
        The valid API key
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="X-API-Key header is required"
        )
    
    valid_keys = os.getenv("API_KEYS", "test-key-123").split(",")
    valid_keys = [key.strip() for key in valid_keys]  # Strip whitespace
    
    if x_api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    
    return x_api_key
