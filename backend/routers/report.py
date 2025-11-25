from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import FileResponse
from typing import Optional
import logging
import os
from models.schemas import ReportResponse, ReportRequest
from utils.file_handler import file_handler
from utils.report_generator import ReportGenerator
from services.openai_manager import openai_manager
from agents.reporting_agent import ReportingAgent

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Generate a comprehensive PDF report.
    """
    if not session_id:
        session_id = request.session_id
        
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
        
    try:
        # Load dataset (prefer engineered -> cleaned -> original)
        df = None
        for filename in ["engineered.csv", "cleaned.csv", "original.csv"]:
            try:
                df = file_handler.load_dataframe(session_id, filename)
                break
            except FileNotFoundError:
                continue
                
        if df is None:
            raise HTTPException(status_code=404, detail="Dataset not found")
            
        # Get OpenAI client
        client = openai_manager.get_client(session_id)
        
        # Initialize Agent
        agent = ReportingAgent(client)
        
        # Generate Content
        content = agent.generate_report_content(df)
        
        # Generate PDF
        generator = ReportGenerator(file_handler.upload_dir)
        pdf_path = generator.create_pdf(content, df, session_id)
        
        # Return response with download URL (relative path)
        # In a real app, we'd return a URL to a static file server or a download endpoint
        # For now, we'll return the relative path which the frontend can use to request the file
        
        return ReportResponse(
            session_id=session_id,
            status="success",
            report_url=f"/api/export/download/{session_id}/report.pdf",
            summary=content.get("summary", ""),
            insights=content.get("insights", [])
        )
        
    except Exception as e:
        logger.error(f"Report generation endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
