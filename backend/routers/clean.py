from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging
from models.schemas import CleaningResponse, CleaningRequest
from utils.file_handler import file_handler
from services.openai_manager import openai_manager
from agents.cleaning_agent import CleaningAgent

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=CleaningResponse)
async def clean_dataset(
    request: CleaningRequest,
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Auto-clean the dataset using AI.
    Handles missing values, duplicates, and inconsistencies.
    """
    if not session_id:
        session_id = request.session_id
        
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
        
    try:
        # Load the dataset
        # Always start from original for a fresh clean, or load 'cleaned.csv' if we want to iterate?
        # For now, let's load original to ensure reproducible clean from base
        try:
            df = file_handler.load_dataframe(session_id, "original.csv")
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Dataset not found")
            
        # Get OpenAI client
        client = openai_manager.get_client(session_id)
        
        # Initialize Agent
        agent = CleaningAgent(client)
        
        # Get dimensions before cleaning
        rows_before, cols_before = df.shape
        
        # Execute cleaning
        result = agent.execute_cleaning(df)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Cleaning failed: {result.get('error')}")
            
        cleaned_df = result["cleaned_df"]
        rows_after, cols_after = cleaned_df.shape
        
        # Save cleaned dataset
        file_handler.save_dataframe(cleaned_df, session_id, "cleaned.csv")
        
        # Get preview of cleaned data
        preview = file_handler.get_preview(cleaned_df)
        
        return CleaningResponse(
            session_id=session_id,
            status="success",
            cleaning_steps=result["steps"],
            applied_changes=result["code"],
            rows_before=rows_before,
            rows_after=rows_after,
            columns_before=cols_before,
            columns_after=cols_after,
            preview=preview,
            summary=result["summary"]
        )
        
    except Exception as e:
        logger.error(f"Cleaning endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
