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
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates PDF and HTML reports from agent output"""
    
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

    def create_html(self, content: Dict[str, Any], df: pd.DataFrame, session_id: str) -> str:
        """
        Create HTML report and return file path.
        """
        session_dir = os.path.join(self.upload_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        file_path = os.path.join(session_dir, "report.html")
        
        # Generate plots as base64 images
        plot_images = []
        for section in content.get("sections", []):
            if section.get("plot_code"):
                img_buffer = self._execute_plot(section["plot_code"], df)
                if img_buffer:
                    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
                    plot_images.append(img_base64)
                else:
                    plot_images.append(None)
            else:
                plot_images.append(None)
        
        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content.get("title", "Data Analysis Report")}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 50px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
            border-bottom: 4px solid #667eea;
            padding-bottom: 15px;
        }}
        .meta {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #764ba2;
            font-size: 1.8em;
            margin-top: 40px;
            margin-bottom: 15px;
            border-left: 5px solid #764ba2;
            padding-left: 15px;
        }}
        .summary {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin: 20px 0;
            font-size: 1.1em;
        }}
        .insights {{
            background: #fff3cd;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }}
        .insights ul {{
            list-style: none;
            padding-left: 0;
        }}
        .insights li {{
            padding: 10px 0;
            padding-left: 30px;
            position: relative;
        }}
        .insights li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #ffc107;
            font-weight: bold;
            font-size: 1.2em;
        }}
        .section {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        .section h3 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        .plot {{
            margin: 20px 0;
            text-align: center;
        }}
        .plot img {{
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #e9ecef;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{content.get("title", "Data Analysis Report")}</h1>
        <div class="meta">
            Generated by DIDA on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
        </div>
        
        <h2>Executive Summary</h2>
        <div class="summary">
            {content.get("summary", "No summary available.")}
        </div>
        
        {f'''<h2>Key Insights</h2>
        <div class="insights">
            <ul>
                {"".join([f"<li>{insight}</li>" for insight in content.get("insights", [])])}
            </ul>
        </div>''' if content.get("insights") else ""}
        
        <h2>Detailed Analysis</h2>
"""
        
        # Add sections
        for i, section in enumerate(content.get("sections", [])):
            html += f"""
        <div class="section">
            <h3>{section.get("title", f"Section {i+1}")}</h3>
            <p>{section.get("content", "")}</p>
"""
            if plot_images[i]:
                html += f"""
            <div class="plot">
                <img src="data:image/png;base64,{plot_images[i]}" alt="{section.get('title', 'Plot')}">
            </div>
"""
            html += """
        </div>
"""
        
        html += """
        <div class="footer">
            <p><strong>DIDA</strong> - Domain-Aware Intelligent Data Scientist Agent</p>
            <p>Powered by OpenAI GPT-4</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html)
            
        logger.info(f"HTML report generated: {file_path}")
        return file_path
