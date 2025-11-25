from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import FileResponse
from typing import Optional
import logging
import os
from utils.file_handler import file_handler

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/download/{session_id}/{filename}")
async def download_file(session_id: str, filename: str):
    """
    Download a file from the session directory.
    """
    try:
        file_path = os.path.join(file_handler.upload_dir, session_id, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
            
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
