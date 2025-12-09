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
    Generate a comprehensive PDF and/or HTML report.
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
        
        # Generate reports based on requested format
        generator = ReportGenerator(file_handler.upload_dir)
        report_url = None
        
        if request.format in ["pdf", "both"]:
            pdf_path = generator.create_pdf(content, df, session_id)
            report_url = f"/api/export/download/{session_id}/report.pdf"
            
        if request.format in ["html", "both"]:
            html_path = generator.create_html(content, df, session_id)
            if not report_url:
                report_url = f"/api/export/download/{session_id}/report.html"
        
        logger.info(f"Report generation completed for session: {session_id}")
        
        return ReportResponse(
            session_id=session_id,
            status="success",
            report_url=report_url,
            summary=content.get("summary", ""),
            insights=content.get("insights", [])
        )
        
    except Exception as e:
        logger.error(f"Report generation endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
