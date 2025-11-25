from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum


# ==================== Enums ====================

class DataType(str, Enum):
    """Column data types"""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    TEXT = "text"
    BOOLEAN = "boolean"
    UNKNOWN = "unknown"


class FileFormat(str, Enum):
    """Supported file formats"""
    CSV = "csv"
    EXCEL = "excel"
    TSV = "tsv"
    PASTE = "paste"
    SQL = "sql"


class CleaningAction(str, Enum):
    """Cleaning actions"""
    DROP_COLUMN = "drop_column"
    DROP_ROWS = "drop_rows"
    IMPUTE_MEAN = "impute_mean"
    IMPUTE_MEDIAN = "impute_median"
    IMPUTE_MODE = "impute_mode"
    IMPUTE_FORWARD_FILL = "impute_forward_fill"
    IMPUTE_BACKWARD_FILL = "impute_backward_fill"
    REMOVE_OUTLIERS = "remove_outliers"
    CAP_OUTLIERS = "cap_outliers"
    FIX_DATA_TYPE = "fix_data_type"
    STANDARDIZE = "standardize"
    NORMALIZE = "normalize"


# ==================== Upload Schemas ====================

class UploadResponse(BaseModel):
    """Response from file upload"""
    session_id: str
    filename: str
    format: FileFormat
    rows: int
    columns: int
    preview: List[Dict[str, Any]]
    column_names: List[str]
    message: str


class PasteDataRequest(BaseModel):
    """Request for pasting data"""
    data: str
    delimiter: str = ","
    has_header: bool = True


# ==================== Analysis Schemas ====================

class ColumnInfo(BaseModel):
    """Information about a single column"""
    name: str
    data_type: DataType
    inferred_meaning: str
    null_count: int
    null_percentage: float
    unique_count: int
    sample_values: List[Any]
    suggested_action: Optional[str] = None
    is_primary_key: bool = False
    detected_issues: List[str] = []


class AnalysisResponse(BaseModel):
    """Response from dataset analysis"""
    session_id: str
    columns: List[ColumnInfo]
    suggested_target: Optional[str] = None
    domain_insights: List[str]
    warnings: List[str]
    questions_for_user: List[str]
    overall_quality_score: float = Field(ge=0, le=100)


# ==================== Cleaning Schemas ====================

class CleaningDecision(BaseModel):
    """A single cleaning decision"""
    column: str
    action: CleaningAction
    reason: str
    parameters: Dict[str, Any] = {}
    affected_rows: int = 0


class CleaningRequest(BaseModel):
    """Request for cleaning"""
    session_id: str
    user_preferences: Optional[Dict[str, Any]] = {}
    domain_rules: Optional[Dict[str, Any]] = {}


class CleaningResponse(BaseModel):
    """Response from cleaning"""
    session_id: str
    decisions: Optional[List[CleaningDecision]] = None
    cleaning_steps: List[str] = []
    applied_changes: str = ""
    rows_before: int
    rows_after: int
    columns_before: int
    columns_after: int
    summary: str
    preview: List[Dict[str, Any]]


# ==================== Feature Engineering Schemas ====================

class FeatureInfo(BaseModel):
    """Information about an engineered feature"""
    name: str
    source_columns: List[str]
    transformation: str
    reason: str
    importance_score: Optional[float] = None


class FeatureEngineeringRequest(BaseModel):
    """Request for feature engineering"""
    session_id: str
    target_column: Optional[str] = None
    auto_engineer: bool = True
    instructions: Optional[str] = None
    custom_features: Optional[List[Dict[str, Any]]] = []


class FeatureEngineeringResponse(BaseModel):
    """Response from feature engineering"""
    session_id: str
    status: str
    new_features: List[str]
    code_generated: str
    preview: List[Dict[str, Any]]
    summary: str
    feature_importance: Optional[Dict[str, float]] = None
    correlation_matrix: Optional[Dict[str, Any]] = None


# ==================== Report Schemas ====================

class ReportRequest(BaseModel):
    """Request for report generation"""
    session_id: str
    include_visualizations: bool = True
    format: Literal["pdf", "html", "both"] = "both"


class ReportResponse(BaseModel):
    """Response from report generation"""
    session_id: str
    status: str
    report_url: Optional[str] = None
    summary: str
    insights: List[str] = []
    generated_at: datetime = Field(default_factory=datetime.now)


# ==================== Chat Schemas ====================

class ChatMessage(BaseModel):
    """A chat message"""
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    visualization: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Request for chat"""
    session_id: str
    message: str
    history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    """Response from chat"""
    session_id: str
    response: str
    visualization: Optional[Dict[str, Any]] = None
    data_result: Optional[List[Dict[str, Any]]] = None
    code_executed: Optional[str] = None


# ==================== Export Schemas ====================

class ExportRequest(BaseModel):
    """Request for export"""
    session_id: str
    formats: List[Literal["csv", "excel", "python", "notebook", "json"]]
    include_original: bool = False


class ExportResponse(BaseModel):
    """Response from export"""
    session_id: str
    files: Dict[str, str]  # format -> download_url
    summary: str


# ==================== Auth Schemas ====================

class SetAPIKeyRequest(BaseModel):
    """Request to set OpenAI API key"""
    api_key: str
    
    @validator('api_key')
    def validate_api_key(cls, v):
        if not v.startswith('sk-'):
            raise ValueError('Invalid OpenAI API key format')
        return v


class ValidateAPIKeyResponse(BaseModel):
    """Response from API key validation"""
    valid: bool
    message: str
    model: Optional[str] = None


# ==================== Error Schemas ====================

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    session_id: Optional[str] = None
