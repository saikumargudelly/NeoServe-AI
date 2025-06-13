"""
Logging utility for Vertex AI operations.
Provides detailed logging for model interactions and API calls.
"""
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

class VertexAILogger:
    """Enhanced logger for Vertex AI operations."""
    
    def __init__(self, name: str = "vertex_ai"):
        """Initialize the logger.
        
        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Add console handler if not already configured
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def log_model_call(
        self,
        model_name: str,
        prompt: str,
        parameters: Dict[str, Any],
        response: Any = None,
        error: Optional[Exception] = None,
        **kwargs
    ) -> None:
        """Log a model API call with details.
        
        Args:
            model_name: Name of the model being called
            prompt: Input prompt to the model
            parameters: Generation parameters
            response: Model response (if successful)
            error: Exception (if any)
            **kwargs: Additional metadata
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "model": model_name,
            "prompt": prompt,
            "parameters": parameters,
            **kwargs
        }
        
        if error:
            log_data.update({
                "status": "error",
                "error": str(error),
                "error_type": error.__class__.__name__
            })
            self.logger.error(json.dumps(log_data, default=str))
        else:
            log_data.update({
                "status": "success",
                "response_length": len(str(response)) if response else 0,
                "response_type": type(response).__name__
            })
            self.logger.info(json.dumps(log_data, default=str))
    
    def log_prediction(
        self,
        endpoint: str,
        instances: list,
        parameters: Dict[str, Any],
        response: Any = None,
        error: Optional[Exception] = None,
        **kwargs
    ) -> None:
        """Log a prediction API call with details.
        
        Args:
            endpoint: Prediction endpoint
            instances: Input instances for prediction
            parameters: Prediction parameters
            response: Prediction response (if successful)
            error: Exception (if any)
            **kwargs: Additional metadata
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": endpoint,
            "instance_count": len(instances),
            "parameters": parameters,
            **kwargs
        }
        
        if error:
            log_data.update({
                "status": "error",
                "error": str(error),
                "error_type": error.__class__.__name__
            })
            self.logger.error(json.dumps(log_data, default=str))
        else:
            log_data.update({
                "status": "success",
                "response_type": type(response).__name__
            })
            self.logger.info(json.dumps(log_data, default=str))

# Create a default logger instance
vertex_ai_logger = VertexAILogger()
