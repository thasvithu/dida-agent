import os
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from typing import Dict, Any, List
import logging
import contextlib

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates PDF reports from agent output"""
    
    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        ))
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=12
        ))
        
    def _execute_plot(self, code: str, df: pd.DataFrame) -> io.BytesIO:
        """Execute plot code and return image buffer"""
        local_env = {"df": df, "plt": plt, "sns": sns, "pd": pd, "np": np}
        
        img_buffer = io.BytesIO()
        
        try:
            plt.clf()  # Clear existing plots
            exec(code, {}, local_env)
            plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
            img_buffer.seek(0)
            plt.close('all')
            return img_buffer
        except Exception as e:
            logger.error(f"Plot generation error: {str(e)}")
            return None

    def create_pdf(self, content: Dict[str, Any], df: pd.DataFrame, session_id: str) -> str:
        """
        Create PDF report and return file path.
        """
        session_dir = os.path.join(self.upload_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        file_path = os.path.join(session_dir, "report.pdf")
        
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph(content.get("title", "Data Analysis Report"), self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Summary
        story.append(Paragraph("Executive Summary", self.styles['CustomHeading']))
        story.append(Paragraph(content.get("summary", ""), self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Insights
        if content.get("insights"):
            story.append(Paragraph("Key Insights", self.styles['CustomHeading']))
            for insight in content["insights"]:
                story.append(Paragraph(f"• {insight}", self.styles['Normal']))
            story.append(Spacer(1, 20))
            
        # Sections
        for section in content.get("sections", []):
            story.append(Paragraph(section.get("title", ""), self.styles['CustomHeading']))
            story.append(Paragraph(section.get("content", ""), self.styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Plot
            if section.get("plot_code"):
                img_buffer = self._execute_plot(section["plot_code"], df)
                if img_buffer:
                    img = Image(img_buffer, width=400, height=300)
                    story.append(img)
                    story.append(Spacer(1, 12))
                    
        doc.build(story)
        logger.info(f"PDF report generated: {file_path}")
        return file_path
