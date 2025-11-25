from typing import List, Dict, Any
import pandas as pd
import numpy as np
from agents.base_agent import BaseAgent
from models.schemas import AnalysisResponse, ColumnInfo, DataType
import logging

logger = logging.getLogger(__name__)


class SchemaAnalyzerAgent(BaseAgent):
    """
    Analyzes dataset schema to understand structure, data types,
    and potential issues. Uses AI to infer semantic meaning of columns.
    """
    
    def __init__(self, client, model: str = "gpt-4-turbo-preview"):
        super().__init__(
            name="Schema Analyzer",
            client=client,
            model=model,
            temperature=0.3  # Lower temperature for more consistent analysis
        )
        
    def _create_system_prompt(self) -> str:
        return """You are an expert data scientist specializing in dataset analysis and schema understanding.
Your task is to analyze datasets and provide insights about:
- Column meanings and semantic interpretation
- Data quality issues
- Potential primary keys
- Suggested target variables for ML
- Domain-specific insights
- Data validation concerns

Provide detailed, actionable insights that help users understand their data better."""

    def _analyze_column_basic(self, df: pd.DataFrame, col: str) -> Dict[str, Any]:
        """Perform basic statistical analysis on a column"""
        series = df[col]
        
        # Detect data type
        if pd.api.types.is_numeric_dtype(series):
            data_type = DataType.NUMERIC
        elif pd.api.types.is_datetime64_any_dtype(series):
            data_type = DataType.DATETIME
        elif pd.api.types.is_bool_dtype(series):
            data_type = DataType.BOOLEAN
        elif pd.api.types.is_categorical_dtype(series) or series.nunique() / len(series) < 0.05:
            data_type = DataType.CATEGORICAL
        elif pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
            # Check if it's text or categorical
            if series.nunique() / len(series) < 0.5:
                data_type = DataType.CATEGORICAL
            else:
                data_type = DataType.TEXT
        else:
            data_type = DataType.UNKNOWN
            
        # Get sample values (non-null)
        sample_values = series.dropna().head(5).tolist()
        
        # Calculate statistics
        null_count = series.isna().sum()
        null_percentage = (null_count / len(series)) * 100
        unique_count = series.nunique()
        
        # Check if could be primary key
        is_primary_key = (
            unique_count == len(series) and
            null_count == 0 and
            len(series) > 0
        )
        
        return {
            "name": col,
            "data_type": data_type,
            "null_count": int(null_count),
            "null_percentage": round(null_percentage, 2),
            "unique_count": int(unique_count),
            "sample_values": sample_values,
            "is_primary_key": is_primary_key,
            "total_rows": len(series)
        }
        
    def _format_user_prompt(self, **kwargs) -> str:
        """Format prompt with dataset information"""
        df = kwargs.get("dataframe")
        column_stats = kwargs.get("column_stats", [])
        
        # Create a summary of the dataset
        summary = f"""Dataset Overview:
- Total Rows: {len(df)}
- Total Columns: {len(df.columns)}

Column Details:
"""
        for stat in column_stats:
            summary += f"\n{stat['name']}:"
            summary += f"\n  - Type: {stat['data_type']}"
            summary += f"\n  - Null: {stat['null_count']} ({stat['null_percentage']}%)"
            summary += f"\n  - Unique: {stat['unique_count']}"
            summary += f"\n  - Samples: {stat['sample_values'][:3]}"
            if stat['is_primary_key']:
                summary += f"\n  - Potential Primary Key: Yes"
                
        prompt = f"""{summary}

Please analyze this dataset and provide:

1. **Semantic Meaning**: For each column, infer what it represents (e.g., "customer_id" = unique customer identifier, "age" = person's age in years)

2. **Data Quality Issues**: Identify potential problems:
   - High null percentages
   - Suspicious values
   - Inconsistent data types
   - Potential duplicates

3. **Suggested Target Variable**: If this looks like an ML dataset, which column would likely be the target/label?

4. **Domain Insights**: What domain/industry does this data likely come from? What business questions could it answer?

5. **Questions for User**: What clarifications would help understand this data better?

6. **Overall Quality Score**: Rate the dataset quality from 0-100.

Respond in JSON format:
{{
    "column_insights": [
        {{
            "column": "column_name",
            "meaning": "inferred meaning",
            "issues": ["issue1", "issue2"],
            "suggested_action": "recommendation"
        }}
    ],
    "suggested_target": "column_name or null",
    "domain_insights": ["insight1", "insight2"],
    "warnings": ["warning1", "warning2"],
    "questions": ["question1", "question2"],
    "quality_score": 85
}}"""
        
        return prompt
        
    def _process_request(self, messages: List[Dict[str, str]], **kwargs) -> AnalysisResponse:
        """Process analysis request"""
        df = kwargs.get("dataframe")
        
        # Get AI insights
        response = self.chat_completion(
            messages,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        ai_insights = self.parse_json_response(response)
        
        # Combine basic stats with AI insights
        column_stats = kwargs.get("column_stats", [])
        columns_info = []
        
        for stat in column_stats:
            # Find AI insight for this column
            ai_insight = next(
                (ci for ci in ai_insights.get("column_insights", []) if ci["column"] == stat["name"]),
                {}
            )
            
            columns_info.append(ColumnInfo(
                name=stat["name"],
                data_type=stat["data_type"],
                inferred_meaning=ai_insight.get("meaning", "Unknown"),
                null_count=stat["null_count"],
                null_percentage=stat["null_percentage"],
                unique_count=stat["unique_count"],
                sample_values=stat["sample_values"],
                suggested_action=ai_insight.get("suggested_action"),
                is_primary_key=stat["is_primary_key"],
                detected_issues=ai_insight.get("issues", [])
            ))
            
        return AnalysisResponse(
            session_id=kwargs.get("session_id", ""),
            columns=columns_info,
            suggested_target=ai_insights.get("suggested_target"),
            domain_insights=ai_insights.get("domain_insights", []),
            warnings=ai_insights.get("warnings", []),
            questions_for_user=ai_insights.get("questions", []),
            overall_quality_score=ai_insights.get("quality_score", 50.0)
        )
        
    def execute(self, dataframe: pd.DataFrame, session_id: str = "") -> AnalysisResponse:
        """Execute schema analysis"""
        logger.info(f"Analyzing schema for dataset: {dataframe.shape}")
        
        # Perform basic analysis on each column
        column_stats = [
            self._analyze_column_basic(dataframe, col)
            for col in dataframe.columns
        ]
        
        # Get AI insights
        system_prompt = self._create_system_prompt()
        user_prompt = self._format_user_prompt(
            dataframe=dataframe,
            column_stats=column_stats
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._process_request(
            messages,
            dataframe=dataframe,
            column_stats=column_stats,
            session_id=session_id
        )
