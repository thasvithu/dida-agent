from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging
from models.schemas import AnalysisResponse
from utils.file_handler import file_handler
from services.openai_manager import openai_manager
from agents.schema_analyzer import SchemaAnalyzerAgent

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=AnalysisResponse)
async def analyze_dataset(
    session_id: str = Header(..., alias="X-Session-ID")
):
    """
    Analyze the uploaded dataset using Schema Analyzer and Domain Knowledge agents.
    Returns insights about columns, data types, potential issues, and suggestions.
    """
    try:
        # Load the original dataset
        df = file_handler.load_dataframe(session_id, "original.csv")
        
        # Get OpenAI client for this session
        client = openai_manager.get_client(session_id)
        
        # Create and execute Schema Analyzer agent
        schema_agent = SchemaAnalyzerAgent(client)
        analysis_result = schema_agent.execute(dataframe=df)
        
        logger.info(f"Analysis completed for session: {session_id}")
        
        return analysis_result
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset not found. Please upload a file first.")
    except ValueError as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze dataset")
