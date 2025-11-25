from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging
from models.schemas import ChatRequest, ChatResponse
from utils.file_handler import file_handler
from services.openai_manager import openai_manager
from agents.chat_agent import ChatAgent

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat_with_data(
    request: ChatRequest,
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Chat with the dataset using natural language.
    Executes queries and generates visualizations.
    """
    if not session_id:
        # Try to get session_id from request body if not in header
        session_id = request.session_id
        
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
        
    try:
        # Load the dataset
        # Try to load cleaned version first, then original
        try:
            df = file_handler.load_dataframe(session_id, "cleaned.csv")
        except FileNotFoundError:
            df = file_handler.load_dataframe(session_id, "original.csv")
            
        # Get OpenAI client
        client = openai_manager.get_client(session_id)
        
        # Create and execute Chat Agent
        chat_agent = ChatAgent(client)
        
        response = chat_agent.execute(
            dataframe=df,
            message=request.message,
            history=request.history,
            session_id=session_id
        )
        
        logger.info(f"Chat request processed for session: {session_id}")
        return response
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset not found. Please upload a file first.")
    except ValueError as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat request: {str(e)}")
