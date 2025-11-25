from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from agents.base_agent import BaseAgent
from models.schemas import CleaningResponse
import logging
import io
import contextlib

logger = logging.getLogger(__name__)

class CleaningAgent(BaseAgent):
    """
    Agent for cleaning datasets.
    Detects issues and generates code to fix them.
    """
    
    def __init__(self, client, model: str = "gpt-4-turbo-preview"):
        super().__init__(
            name="Cleaning Agent",
            client=client,
            model=model,
            temperature=0.1
        )
        
    def _create_system_prompt(self) -> str:
        return """You are an expert data scientist specialized in data cleaning.
Your task is to analyze a dataset, identify quality issues, and write Python code to clean it.

You have access to a pandas DataFrame named `df`.
You must perform the following cleaning steps if applicable:
1. Handle missing values (impute or drop)
2. Remove duplicate rows
3. Fix inconsistent data types
4. Handle outliers
5. Standardize text data (trim whitespace, lower/title case)

Response Format:
Return a JSON object with:
- "steps": List of strings describing what you did (e.g., "Imputed missing values in 'age' with median")
- "code": The Python code to execute. It MUST modify `df` in place or assign back to `df`.
- "summary": A brief summary of the cleaning process.

Example:
{
    "steps": ["Removed 5 duplicate rows", "Filled missing 'age' with median (28.0)"],
    "code": "df.drop_duplicates(inplace=True)\ndf['age'].fillna(df['age'].median(), inplace=True)",
    "summary": "Cleaned duplicates and missing values."
}
"""

    def _format_user_prompt(self, **kwargs) -> str:
        df = kwargs.get("dataframe")
        analysis = kwargs.get("analysis", {})
        
        # Create context
        columns = df.columns.tolist()
        dtypes = df.dtypes.to_dict()
        missing = df.isnull().sum().to_dict()
        duplicates = df.duplicated().sum()
        
        context = f"""
Dataset Info:
- Columns: {columns}
- Data Types: {dtypes}
- Missing Values: {missing}
- Duplicate Rows: {duplicates}

Previous Analysis (if any):
{analysis}

Please clean this dataset. Focus on handling missing values, duplicates, and obvious type mismatches.
"""
        return context

    def _process_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Process the cleaning request"""
        response = self.chat_completion(
            messages,
            response_format={"type": "json_object"}
        )
        return self.parse_json_response(response)

    def execute_cleaning(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute generated cleaning code.
        Returns cleaned dataframe and metadata.
        """
        # Create a local environment
        local_env = {
            "df": df.copy(),
            "pd": pd,
            "np": np
        }
        
        # Capture stdout
        output_buffer = io.StringIO()
        
        try:
            # Generate cleaning plan and code
            messages = [
                {"role": "system", "content": self._create_system_prompt()},
                {"role": "user", "content": self._format_user_prompt(dataframe=df)}
            ]
            
            ai_response = self._process_request(messages)
            
            code = ai_response.get("code", "")
            steps = ai_response.get("steps", [])
            summary = ai_response.get("summary", "")
            
            # Execute code
            with contextlib.redirect_stdout(output_buffer):
                exec(code, {}, local_env)
                
            cleaned_df = local_env.get("df")
            
            return {
                "success": True,
                "cleaned_df": cleaned_df,
                "code": code,
                "steps": steps,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Cleaning error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
