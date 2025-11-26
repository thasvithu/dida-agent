"""
ML Preparation Router

Handles ML preparation requests for encoding, scaling, and train/test split.
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging

from models.schemas import MLPrepRequest, MLPrepResponse
from services.openai_manager import openai_manager
from utils.file_handler import file_handler
from agents.ml_prep_agent import MLPrepAgent

router = APIRouter(prefix="/api/ml-prep", tags=["ml-prep"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=MLPrepResponse)
async def prepare_for_ml(
    request: MLPrepRequest,
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Prepare dataset for machine learning
    
    - Encodes categorical variables
    - Scales numerical features
    - Splits into train/test sets
    - Provides ML recommendations
    """
    try:
        session_id = request.session_id or x_session_id
        
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID required")
        
        # Get OpenAI client
        client = openai_manager.get_client(session_id)
        if not client:
            raise HTTPException(status_code=400, detail="No OpenAI API key available. Please provide one.")
        
        # Load the most processed dataset available
        df = None
        dataset_source = None
        
        for filename in ["engineered.csv", "cleaned.csv", "original.csv"]:
            try:
                df = file_handler.load_dataframe(session_id, filename)
                dataset_source = filename
                logger.info(f"Loaded dataset from {filename}")
                break
            except FileNotFoundError:
                continue
        
        if df is None:
            raise HTTPException(status_code=404, detail="No dataset found. Please upload a file first.")
        
        # Initialize Agent
        agent = MLPrepAgent(client)
        
        # Prepare for ML
        result = agent.prepare_for_ml(
            df=df,
            target_column=request.target_column,
            test_size=request.test_size,
            random_state=request.random_state,
            scaling_strategy=request.scaling_strategy,
            encoding_strategy=request.encoding_strategy
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"ML preparation failed: {result.get('error')}")
        
        # Save the splits
        file_handler.save_dataframe(result["X_train"], session_id, "X_train.csv")
        file_handler.save_dataframe(result["X_test"], session_id, "X_test.csv")
        file_handler.save_dataframe(result["y_train"], session_id, "y_train.csv")
        file_handler.save_dataframe(result["y_test"], session_id, "y_test.csv")
        
        # Create download URLs
        download_urls = {
            "X_train": f"/api/export/download/{session_id}/X_train.csv",
            "X_test": f"/api/export/download/{session_id}/X_test.csv",
            "y_train": f"/api/export/download/{session_id}/y_train.csv",
            "y_test": f"/api/export/download/{session_id}/y_test.csv"
        }
        
        logger.info(f"ML preparation completed for session: {session_id}")
        
        return MLPrepResponse(
            session_id=session_id,
            status="success",
            problem_type=result["problem_type"],
            train_samples=len(result["X_train"]),
            test_samples=len(result["X_test"]),
            num_features=len(result["X_train"].columns),
            encoded_columns=result["encoded_columns"],
            scaled_columns=result["scaled_columns"],
            target_encoded=result["target_encoded"],
            class_distribution=result.get("class_distribution"),
            recommended_algorithms=result["recommended_algorithms"],
            warnings=result["warnings"],
            best_practices=result["best_practices"],
            download_urls=download_urls
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ML prep endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
