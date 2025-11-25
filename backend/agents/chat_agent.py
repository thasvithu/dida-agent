from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from agents.base_agent import BaseAgent
from models.schemas import ChatResponse, ChatMessage
import logging
import io
import contextlib
import matplotlib.pyplot as plt
import base64

logger = logging.getLogger(__name__)


class ChatAgent(BaseAgent):
    """
    Agent for chatting with data.
    Translates natural language queries into pandas code and executes it.
    """
    
    def __init__(self, client, model: str = "gpt-4-turbo-preview"):
        super().__init__(
            name="Chat Agent",
            client=client,
            model=model,
            temperature=0.1  # Low temperature for precise code generation
        )
        
    def _create_system_prompt(self) -> str:
        return """You are an expert data scientist and Python programmer.
Your task is to answer user questions about a dataset by writing and executing Python code using pandas.

You have access to a pandas DataFrame named `df`.
You can use libraries: pandas (pd), numpy (np), matplotlib.pyplot (plt).

When asked a question:
1. Analyze what the user wants (statistics, visualization, or data transformation).
2. Write Python code to achieve this.
3. The code must assign the result to a variable named `result`.
4. If a plot is requested, create it using matplotlib/seaborn but do not show it; just create the figure.

Response Format:
Return a JSON object with:
- "thought": Your reasoning about what to do
- "code": The Python code to execute
- "response_text": A natural language response to show the user (explaining what you did)
- "requires_plot": Boolean, true if a plot is generated

Example:
User: "What is the average age?"
Response:
{
    "thought": "Calculate mean of age column",
    "code": "result = df['age'].mean()",
    "response_text": "I calculated the average age.",
    "requires_plot": false
}
"""

    def _format_user_prompt(self, **kwargs) -> str:
        df = kwargs.get("dataframe")
        message = kwargs.get("message")
        history = kwargs.get("history", [])
        
        # Create context from dataframe
        columns = df.columns.tolist()
        dtypes = df.dtypes.to_dict()
        sample = df.head(3).to_string()
        
        context = f"""
Dataset Info:
- Columns: {columns}
- Data Types: {dtypes}
- Sample Data:
{sample}

Chat History:
{history[-5:] if history else "No previous history"}

User Question: {message}
"""
        return context

    def execute_code(self, code: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute generated Python code safely.
        Returns result and any plot data.
        """
        # Create a local environment with df and libraries
        local_env = {
            "df": df,
            "pd": pd,
            "np": np,
            "plt": plt,
            "result": None
        }
        
        # Capture stdout
        output_buffer = io.StringIO()
        
        try:
            # Execute code
            with contextlib.redirect_stdout(output_buffer):
                exec(code, {}, local_env)
                
            result = local_env.get("result")
            output = output_buffer.getvalue()
            
            # Handle plots if any
            plot_data = None
            if plt.get_fignums():
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png', bbox_inches='tight')
                img_buffer.seek(0)
                plot_data = base64.b64encode(img_buffer.read()).decode('utf-8')
                plt.close('all')
                
            return {
                "success": True,
                "result": result,
                "output": output,
                "plot": plot_data
            }
            
        except Exception as e:
            logger.error(f"Code execution error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _process_request(self, messages: List[Dict[str, str]], **kwargs) -> ChatResponse:
        df = kwargs.get("dataframe")
        session_id = kwargs.get("session_id")
        
        # Get AI response with code
        response = self.chat_completion(
            messages,
            response_format={"type": "json_object"}
        )
        
        ai_response = self.parse_json_response(response)
        
        code = ai_response.get("code", "")
        response_text = ai_response.get("response_text", "")
        
        # Execute code
        exec_result = self.execute_code(code, df)
        
        data_result = None
        visualization = None
        
        if exec_result["success"]:
            result_val = exec_result["result"]
            
            # Format result for frontend
            if isinstance(result_val, pd.DataFrame):
                # Replace NaN/Inf with None for JSON serialization
                result_val = result_val.replace([np.inf, -np.inf], np.nan)
                # Handle NaN values explicitly
                records = result_val.head(20).to_dict('records')
                for record in records:
                    for key, value in record.items():
                        if pd.isna(value):
                            record[key] = None
                data_result = records
            elif isinstance(result_val, pd.Series):
                result_val = result_val.replace([np.inf, -np.inf], np.nan)
                # Convert series to list of dicts
                data_result = [{"index": k, "value": None if pd.isna(v) else v} for k, v in result_val.head(20).items()]
            elif result_val is not None:
                # Scalar value
                if pd.isna(result_val):
                    result_val = None
                elif isinstance(result_val, (np.integer, np.floating)):
                    result_val = result_val.item()
                
                # Append scalar result to response text
                response_text += f"\n\nResult: {result_val}"
                
            # Handle visualization
            if exec_result["plot"]:
                visualization = {
                    "type": "image",
                    "data": exec_result["plot"]
                }
        else:
            response_text += f"\n\n(Error executing code: {exec_result['error']})"
            
        return ChatResponse(
            session_id=session_id,
            response=response_text,
            visualization=visualization,
            data_result=data_result,
            code_executed=code
        )

    def execute(self, dataframe: pd.DataFrame, message: str, history: List[ChatMessage], session_id: str) -> ChatResponse:
        """Execute chat request"""
        system_prompt = self._create_system_prompt()
        user_prompt = self._format_user_prompt(
            dataframe=dataframe,
            message=message,
            history=history
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._process_request(
            messages,
            dataframe=dataframe,
            session_id=session_id
        )
