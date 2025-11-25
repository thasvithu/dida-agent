from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from agents.base_agent import BaseAgent
import logging
import io
import contextlib

logger = logging.getLogger(__name__)

class FeatureAgent(BaseAgent):
    """
    Agent for feature engineering.
    Suggests and creates new features from existing data.
    """
    
    def __init__(self, client, model: str = "gpt-4-turbo-preview"):
        super().__init__(
            name="Feature Engineering Agent",
            client=client,
            model=model,
            temperature=0.2
        )
        
    def _create_system_prompt(self) -> str:
        return """You are an expert machine learning engineer specialized in feature engineering.
Your task is to create new, predictive features from a dataset to improve model performance.

You have access to a pandas DataFrame named `df`.
You should consider:
1. Date/Time extraction (year, month, day, dayofweek)
2. Text processing (length, word count, sentiment if applicable)
3. Numerical interactions (ratios, sums, differences)
4. Categorical encoding (if specifically useful, but prefer creating semantic features)
5. Binning/Discretization

Response Format:
Return a JSON object with:
- "new_features": List of strings describing the new features (e.g., "Created 'age_group' from 'age'")
- "code": The Python code to execute. It MUST modify `df` in place or assign back to `df`.
- "summary": A brief summary of the feature engineering process.

Example:
{
    "new_features": ["Extracted 'title' from 'name'", "Created 'family_size' from 'sibsp' + 'parch'"],
    "code": "df['title'] = df['name'].str.extract(' ([A-Za-z]+)\\\\.', expand=False)\ndf['family_size'] = df['sibsp'] + df['parch'] + 1",
    "summary": "Created title and family size features."
}
"""

    def _format_user_prompt(self, **kwargs) -> str:
        df = kwargs.get("dataframe")
        instructions = kwargs.get("instructions", "")
        
        # Create context
        columns = df.columns.tolist()
        dtypes = df.dtypes.to_dict()
        sample = df.head(3).to_string()
        
        context = f"""
Dataset Info:
- Columns: {columns}
- Data Types: {dtypes}
- Sample Data:
{sample}

User Instructions (if any): {instructions}

Please generate useful features for this dataset.
"""
        return context

    def _process_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Process the feature engineering request"""
        response = self.chat_completion(
            messages,
            response_format={"type": "json_object"}
        )
        return self.parse_json_response(response)

    def execute_feature_engineering(self, df: pd.DataFrame, instructions: str = "") -> Dict[str, Any]:
        """
        Execute generated feature engineering code.
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
            # Generate plan and code
            messages = [
                {"role": "system", "content": self._create_system_prompt()},
                {"role": "user", "content": self._format_user_prompt(dataframe=df, instructions=instructions)}
            ]
            
            ai_response = self._process_request(messages)
            
            code = ai_response.get("code", "")
            new_features = ai_response.get("new_features", [])
            summary = ai_response.get("summary", "")
            
            # Execute code
            with contextlib.redirect_stdout(output_buffer):
                exec(code, {}, local_env)
                
            engineered_df = local_env.get("df")
            
            return {
                "success": True,
                "engineered_df": engineered_df,
                "code": code,
                "new_features": new_features,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Feature engineering error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
