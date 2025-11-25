from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class ReportingAgent(BaseAgent):
    """
    Agent for generating data analysis reports.
    Produces structure, insights, and visualization code.
    """
    
    def __init__(self, client, model: str = "gpt-4-turbo-preview"):
        super().__init__(
            name="Reporting Agent",
            client=client,
            model=model,
            temperature=0.3
        )
        
    def _create_system_prompt(self) -> str:
        return """You are an expert data analyst.
Your task is to generate a comprehensive analysis report for a dataset.

You have access to a pandas DataFrame named `df`.
You should provide:
1. An executive summary
2. Key insights (correlations, trends, outliers)
3. 3-5 relevant visualizations (matplotlib/seaborn code)

Response Format:
Return a JSON object with:
- "title": Report title
- "summary": Executive summary paragraph
- "insights": List of strings (key findings)
- "sections": List of objects, each with:
    - "title": Section title
    - "content": Textual explanation
    - "plot_code": Python code to generate a plot (optional). The code must create a figure using `plt.figure()` or `sns.plot()` but NOT `plt.show()`.

Example:
{
    "title": "Titanic Survival Analysis",
    "summary": "Analysis of survival rates...",
    "insights": ["Females had higher survival rate", "Class 1 passengers survived more"],
    "sections": [
        {
            "title": "Survival by Gender",
            "content": "Females were much more likely to survive...",
            "plot_code": "plt.figure(figsize=(10,6))\nsns.barplot(x='Sex', y='Survived', data=df)"
        }
    ]
}
"""

    def _format_user_prompt(self, **kwargs) -> str:
        df = kwargs.get("dataframe")
        
        # Create context
        columns = df.columns.tolist()
        dtypes = df.dtypes.to_dict()
        description = df.describe().to_string()
        
        context = f"""
Dataset Info:
- Columns: {columns}
- Data Types: {dtypes}
- Statistical Summary:
{description}

Please generate a comprehensive analysis report.
"""
        return context

    def _process_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Process the reporting request"""
        response = self.chat_completion(
            messages,
            response_format={"type": "json_object"}
        )
        return self.parse_json_response(response)

    def generate_report_content(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate report structure and content.
        """
        try:
            messages = [
                {"role": "system", "content": self._create_system_prompt()},
                {"role": "user", "content": self._format_user_prompt(dataframe=df)}
            ]
            
            return self._process_request(messages)
            
        except Exception as e:
            logger.error(f"Report generation error: {str(e)}")
            return {
                "title": "Error Generating Report",
                "summary": f"Failed to generate report: {str(e)}",
                "insights": [],
                "sections": []
            }
