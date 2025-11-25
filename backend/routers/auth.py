from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging
from models.schemas import SetAPIKeyRequest, ValidateAPIKeyResponse
from services.openai_manager import openai_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/set-key", response_model=ValidateAPIKeyResponse)
async def set_api_key(
    request: SetAPIKeyRequest,
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Set and validate user's OpenAI API key for their session.
    The key is stored in memory only and not persisted.
    """
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required in header")
        
    # Validate the API key
    is_valid, message, model = await openai_manager.validate_api_key(request.api_key)
    
    if not is_valid:
        logger.warning(f"Invalid API key attempt for session: {session_id}")
        return ValidateAPIKeyResponse(
            valid=False,
            message=message,
            model=None
        )
        
    # Store the key for this session
    openai_manager.set_session_key(session_id, request.api_key)
    
    logger.info(f"API key validated and stored for session: {session_id}")
    return ValidateAPIKeyResponse(
        valid=True,
        message="API key validated and stored successfully",
        model=model
    )


@router.delete("/remove-key")
async def remove_api_key(
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """Remove user's API key from session"""
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required in header")
        
    openai_manager.remove_session_key(session_id)
    
    return {"message": "API key removed from session"}


@router.get("/key-status")
async def check_key_status(
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """Check if a valid API key is available for the session"""
    if not session_id:
        return {
            "has_session_key": False,
            "has_system_key": openai_manager.system_api_key is not None
        }
        
    has_session_key = openai_manager.get_session_key(session_id) is not None
    
    return {
        "has_session_key": has_session_key,
        "has_system_key": openai_manager.system_api_key is not None
    }
