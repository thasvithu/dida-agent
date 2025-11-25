from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging
from models.schemas import FeatureEngineeringResponse, FeatureEngineeringRequest
from utils.file_handler import file_handler
from services.openai_manager import openai_manager
from agents.feature_agent import FeatureAgent

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=FeatureEngineeringResponse)
async def generate_features(
    request: FeatureEngineeringRequest,
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Auto-generate new features using AI.
    """
    if not session_id:
        session_id = request.session_id
        
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
        
    try:
        # Load the dataset
        # Prefer cleaned data, fall back to original
        try:
            df = file_handler.load_dataframe(session_id, "cleaned.csv")
        except FileNotFoundError:
            try:
                df = file_handler.load_dataframe(session_id, "original.csv")
            except FileNotFoundError:
                raise HTTPException(status_code=404, detail="Dataset not found")
            
        # Get OpenAI client
        client = openai_manager.get_client(session_id)
        
        # Initialize Agent
        agent = FeatureAgent(client)
        
        # Execute feature engineering
        result = agent.execute_feature_engineering(df, request.instructions or "")
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Feature engineering failed: {result.get('error')}")
            
        engineered_df = result["engineered_df"]
        
        # Save engineered dataset
        file_handler.save_dataframe(engineered_df, session_id, "engineered.csv")
        
        # Get preview
        preview = file_handler.get_preview(engineered_df)
        
        return FeatureEngineeringResponse(
            session_id=session_id,
            status="success",
            new_features=result["new_features"],
            code_generated=result["code"],
            preview=preview,
            summary=result["summary"]
        )
        
    except Exception as e:
        logger.error(f"Feature engineering endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
