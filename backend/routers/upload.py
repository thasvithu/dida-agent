from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from typing import Optional
import uuid
import logging
from models.schemas import UploadResponse, PasteDataRequest, FileFormat
from utils.file_handler import file_handler

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/file", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Upload a CSV, Excel, or TSV file.
    Returns preview of the first 20 rows and basic metadata.
    """
    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
        
    try:
        # Detect file format
        file_format = file_handler.detect_format(file.filename)
        
        # Save the uploaded file
        file_path = await file_handler.save_upload(file, session_id)
        
        # Parse the file
        df = file_handler.parse_file(file_path, file_format)
        
        # Get preview and basic info
        preview = file_handler.get_preview(df, n_rows=20)
        info = file_handler.get_basic_info(df)
        
        # Save the original DataFrame
        file_handler.save_dataframe(df, session_id, "original.csv")
        
        logger.info(f"File uploaded successfully: {file.filename} (session: {session_id})")
        
        return UploadResponse(
            session_id=session_id,
            filename=file.filename,
            format=file_format,
            rows=info["rows"],
            columns=info["columns"],
            preview=preview,
            column_names=info["column_names"],
            message="File uploaded and parsed successfully"
        )
        
    except ValueError as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process file")


@router.post("/paste", response_model=UploadResponse)
async def upload_pasted_data(
    request: PasteDataRequest,
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Upload data pasted as text.
    Supports CSV and TSV formats.
    """
    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
        
    try:
        # Parse pasted data
        df = file_handler.parse_pasted_data(
            request.data,
            delimiter=request.delimiter,
            has_header=request.has_header
        )
        
        # Get preview and basic info
        preview = file_handler.get_preview(df, n_rows=20)
        info = file_handler.get_basic_info(df)
        
        # Save the DataFrame
        file_handler.save_dataframe(df, session_id, "original.csv")
        
        logger.info(f"Pasted data uploaded successfully (session: {session_id})")
        
        return UploadResponse(
            session_id=session_id,
            filename="pasted_data.csv",
            format=FileFormat.PASTE,
            rows=info["rows"],
            columns=info["columns"],
            preview=preview,
            column_names=info["column_names"],
            message="Pasted data parsed successfully"
        )
        
    except ValueError as e:
        logger.error(f"Paste upload error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected paste upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process pasted data")
