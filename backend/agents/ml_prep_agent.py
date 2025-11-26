"""
ML Preparation Agent

Prepares datasets for machine learning by:
- Encoding categorical variables
- Scaling numerical features
- Splitting into train/test sets
- Validating ML-readiness
- Providing ML recommendations
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import logging
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder, OneHotEncoder
from sklearn.model_selection import train_test_split
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class MLPrepAgent(BaseAgent):
    """Agent for preparing datasets for machine learning"""
    
    def __init__(self, openai_client):
        super().__init__("ML Preparation Agent", openai_client)
        
    def _create_system_prompt(self) -> str:
        return """You are an expert ML engineer preparing datasets for machine learning.

Your task is to analyze the dataset and target variable, then provide:
1. Problem type detection (classification or regression)
2. Recommendations for ML algorithms
3. Warnings about potential issues
4. Best practices for this specific dataset

Return your response as JSON with this structure:
{
    "problem_type": "classification" or "regression",
    "recommended_algorithms": ["algorithm1", "algorithm2", ...],
    "warnings": ["warning1", "warning2", ...],
    "best_practices": ["practice1", "practice2", ...]
}"""

    def _format_user_prompt(self, **context) -> str:
        df = context.get("dataframe")
        target_col = context.get("target_column")
        
        target_info = self._analyze_target(df[target_col])
        feature_info = self._analyze_features(df.drop(columns=[target_col]))
        
        return f"""Dataset Information:
- Total samples: {len(df)}
- Total features: {len(df.columns) - 1}
- Target column: {target_col}

Target Variable Analysis:
- Data type: {target_info['dtype']}
- Unique values: {target_info['unique_count']}
- Sample values: {target_info['sample_values']}
- Null count: {target_info['null_count']}
- Distribution: {target_info['distribution']}

Feature Summary:
- Numerical features: {feature_info['numerical_count']}
- Categorical features: {feature_info['categorical_count']}
- High cardinality features: {feature_info['high_cardinality']}
- Features with missing values: {feature_info['missing_features']}

Please analyze this dataset and provide ML preparation recommendations."""

    def _process_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Process the ML prep request"""
        response = self.chat_completion(
            messages,
            response_format={"type": "json_object"}
        )
        return self.parse_json_response(response)

    def _analyze_target(self, target_series: pd.Series) -> Dict[str, Any]:
        """Analyze target variable"""
        unique_count = target_series.nunique()
        
        # Get distribution
        if unique_count <= 20:
            distribution = target_series.value_counts().head(10).to_dict()
        else:
            distribution = {
                "mean": float(target_series.mean()) if pd.api.types.is_numeric_dtype(target_series) else None,
                "std": float(target_series.std()) if pd.api.types.is_numeric_dtype(target_series) else None,
                "min": float(target_series.min()) if pd.api.types.is_numeric_dtype(target_series) else None,
                "max": float(target_series.max()) if pd.api.types.is_numeric_dtype(target_series) else None
            }
        
        return {
            "dtype": str(target_series.dtype),
            "unique_count": unique_count,
            "sample_values": target_series.dropna().head(5).tolist(),
            "null_count": int(target_series.isna().sum()),
            "distribution": distribution
        }

    def _analyze_features(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze feature characteristics"""
        numerical_cols = features_df.select_dtypes(include=[np.number]).columns
        categorical_cols = features_df.select_dtypes(exclude=[np.number]).columns
        
        high_cardinality = [
            col for col in categorical_cols 
            if features_df[col].nunique() > 50
        ]
        
        missing_features = [
            col for col in features_df.columns 
            if features_df[col].isna().sum() > 0
        ]
        
        return {
            "numerical_count": len(numerical_cols),
            "categorical_count": len(categorical_cols),
            "high_cardinality": high_cardinality,
            "missing_features": missing_features
        }

    def _detect_problem_type(self, target_series: pd.Series) -> str:
        """Detect if problem is classification or regression"""
        unique_count = target_series.nunique()
        
        # If numeric and many unique values, likely regression
        if pd.api.types.is_numeric_dtype(target_series):
            if unique_count > 20:
                return "regression"
            else:
                return "classification"
        else:
            # Non-numeric is classification
            return "classification"

    def _encode_categorical(
        self, 
        df: pd.DataFrame, 
        strategy: str = "auto"
    ) -> Tuple[pd.DataFrame, List[str]]:
        """Encode categorical variables"""
        categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
        encoded_cols = []
        
        if not categorical_cols:
            return df, encoded_cols
        
        df_encoded = df.copy()
        
        for col in categorical_cols:
            unique_count = df[col].nunique()
            
            # Decide encoding strategy
            if strategy == "auto":
                # Use label encoding for high cardinality, one-hot for low
                use_onehot = unique_count <= 10
            elif strategy == "onehot":
                use_onehot = True
            else:  # label
                use_onehot = False
            
            if use_onehot and unique_count <= 10:
                # One-hot encoding
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
                df_encoded = pd.concat([df_encoded.drop(columns=[col]), dummies], axis=1)
                encoded_cols.extend(dummies.columns.tolist())
            else:
                # Label encoding
                le = LabelEncoder()
                df_encoded[col] = le.fit_transform(df[col].astype(str))
                encoded_cols.append(col)
        
        return df_encoded, encoded_cols

    def _scale_numerical(
        self, 
        df: pd.DataFrame, 
        strategy: str = "standard"
    ) -> Tuple[pd.DataFrame, List[str]]:
        """Scale numerical features"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numerical_cols:
            return df, []
        
        df_scaled = df.copy()
        
        # Choose scaler
        if strategy == "standard":
            scaler = StandardScaler()
        elif strategy == "minmax":
            scaler = MinMaxScaler()
        elif strategy == "robust":
            scaler = RobustScaler()
        else:
            scaler = StandardScaler()
        
        # Scale
        df_scaled[numerical_cols] = scaler.fit_transform(df[numerical_cols])
        
        return df_scaled, numerical_cols

    def prepare_for_ml(
        self,
        df: pd.DataFrame,
        target_column: str,
        test_size: float = 0.2,
        random_state: int = 42,
        scaling_strategy: str = "standard",
        encoding_strategy: str = "auto"
    ) -> Dict[str, Any]:
        """
        Prepare dataset for machine learning
        
        Returns:
            Dictionary with train/test splits, metadata, and recommendations
        """
        try:
            # Validate target column
            if target_column not in df.columns:
                raise ValueError(f"Target column '{target_column}' not found in dataset")
            
            # Detect problem type
            problem_type = self._detect_problem_type(df[target_column])
            logger.info(f"Detected problem type: {problem_type}")
            
            # Separate features and target
            X = df.drop(columns=[target_column])
            y = df[target_column]
            
            # Encode categorical variables in features
            X_encoded, encoded_cols = self._encode_categorical(X, encoding_strategy)
            
            # Encode target if classification
            target_encoded = False
            if problem_type == "classification" and not pd.api.types.is_numeric_dtype(y):
                le = LabelEncoder()
                y = pd.Series(le.fit_transform(y.astype(str)), name=target_column)
                target_encoded = True
            
            # Scale numerical features
            X_scaled, scaled_cols = self._scale_numerical(X_encoded, scaling_strategy)
            
            # Train/test split
            stratify = y if problem_type == "classification" else None
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, 
                test_size=test_size, 
                random_state=random_state,
                stratify=stratify
            )
            
            # Get AI recommendations
            messages = [
                {"role": "system", "content": self._create_system_prompt()},
                {"role": "user", "content": self._format_user_prompt(
                    dataframe=df, 
                    target_column=target_column
                )}
            ]
            
            ai_response = self._process_request(messages)
            
            # Calculate class distribution for classification
            class_distribution = None
            if problem_type == "classification":
                # Convert keys to strings for JSON serialization
                class_distribution = {str(k): int(v) for k, v in y_train.value_counts().to_dict().items()}
            
            # Check for class imbalance
            warnings = ai_response.get("warnings", [])
            if problem_type == "classification" and class_distribution:
                max_class = max(class_distribution.values())
                min_class = min(class_distribution.values())
                if max_class / min_class > 3:
                    warnings.append(f"Class imbalance detected: ratio {max_class/min_class:.1f}:1. Consider using SMOTE or class weights.")
            
            return {
                "success": True,
                "X_train": X_train,
                "X_test": X_test,
                "y_train": y_train,
                "y_test": y_test,
                "problem_type": problem_type,
                "encoded_columns": encoded_cols,
                "scaled_columns": scaled_cols,
                "target_encoded": target_encoded,
                "class_distribution": class_distribution,
                "recommended_algorithms": ai_response.get("recommended_algorithms", []),
                "warnings": warnings,
                "best_practices": ai_response.get("best_practices", [])
            }
            
        except Exception as e:
            logger.error(f"ML preparation error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
