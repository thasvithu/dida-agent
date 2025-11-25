import os
import pandas as pd
import polars as pl
from typing import Tuple, Optional, List, Dict, Any
from fastapi import UploadFile
import io
import logging
from models.schemas import FileFormat

logger = logging.getLogger(__name__)


class FileHandler:
    """Handles file uploads, parsing, and validation"""
    
    def __init__(self, upload_dir: str = "./uploads", max_size_mb: int = 100):
        self.upload_dir = upload_dir
        self.max_size_bytes = max_size_mb * 1024 * 1024
        os.makedirs(upload_dir, exist_ok=True)
        
    async def save_upload(self, file: UploadFile, session_id: str) -> str:
        """Save uploaded file and return path"""
        # Validate file size
        contents = await file.read()
        if len(contents) > self.max_size_bytes:
            raise ValueError(f"File too large. Maximum size: {self.max_size_bytes / (1024*1024)}MB")
            
        # Create session directory
        session_dir = os.path.join(self.upload_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(session_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(contents)
            
        logger.info(f"File saved: {file_path} ({len(contents)} bytes)")
        return file_path
        
    def detect_format(self, filename: str) -> FileFormat:
        """Detect file format from extension"""
        ext = filename.lower().split('.')[-1]
        if ext == 'csv':
            return FileFormat.CSV
        elif ext in ['xlsx', 'xls']:
            return FileFormat.EXCEL
        elif ext == 'tsv':
            return FileFormat.TSV
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
    def parse_file(self, file_path: str, file_format: Optional[FileFormat] = None) -> pd.DataFrame:
        """Parse file into pandas DataFrame"""
        if file_format is None:
            file_format = self.detect_format(file_path)
            
        try:
            if file_format == FileFormat.CSV:
                df = pd.read_csv(file_path)
            elif file_format == FileFormat.TSV:
                df = pd.read_csv(file_path, sep='\t')
            elif file_format == FileFormat.EXCEL:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported format: {file_format}")
                
            logger.info(f"Parsed file: {file_path} -> {df.shape[0]} rows, {df.shape[1]} columns")
            return df
            
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {str(e)}")
            raise ValueError(f"Failed to parse file: {str(e)}")
            
    def parse_pasted_data(self, data: str, delimiter: str = ",", has_header: bool = True) -> pd.DataFrame:
        """Parse pasted data into DataFrame"""
        try:
            df = pd.read_csv(
                io.StringIO(data),
                sep=delimiter,
                header=0 if has_header else None
            )
            logger.info(f"Parsed pasted data: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
        except Exception as e:
            logger.error(f"Error parsing pasted data: {str(e)}")
            raise ValueError(f"Failed to parse pasted data: {str(e)}")
            
    def get_preview(self, df: pd.DataFrame, n_rows: int = 20) -> List[Dict[str, Any]]:
        """Get preview of first n rows as list of dicts"""
        import numpy as np
        
        preview_df = df.head(n_rows).copy()
        
        # Replace infinity values with None
        preview_df = preview_df.replace([np.inf, -np.inf], np.nan)
        
        # Convert to dict and replace NaN with None
        records = preview_df.to_dict('records')
        
        # Replace NaN values with None in the records
        for record in records:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
        
        return records
        
    def get_basic_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic information about the DataFrame"""
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024 * 1024)
        }
        
    def save_dataframe(self, df: pd.DataFrame, session_id: str, filename: str) -> str:
        """Save DataFrame to session directory"""
        session_dir = os.path.join(self.upload_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        file_path = os.path.join(session_dir, filename)
        
        # Determine format from extension
        ext = filename.lower().split('.')[-1]
        if ext == 'csv':
            df.to_csv(file_path, index=False)
        elif ext in ['xlsx', 'xls']:
            df.to_excel(file_path, index=False)
        else:
            raise ValueError(f"Unsupported save format: {ext}")
            
        logger.info(f"DataFrame saved: {file_path}")
        return file_path
        
    def load_dataframe(self, session_id: str, filename: str) -> pd.DataFrame:
        """Load DataFrame from session directory"""
        file_path = os.path.join(self.upload_dir, session_id, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {filename}")
            
        return self.parse_file(file_path)


# Global instance
file_handler = FileHandler(
    upload_dir=os.getenv("UPLOAD_DIR", "./uploads"),
    max_size_mb=int(os.getenv("MAX_UPLOAD_SIZE", 104857600)) // (1024 * 1024)
)
