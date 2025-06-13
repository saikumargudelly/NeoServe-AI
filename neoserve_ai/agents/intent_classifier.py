from typing import Dict, Any, List, Optional
import logging
from .base_agent import BaseAgent
from ..utils.vertex_ai_logger import vertex_ai_logger
from neoserve_ai.agents.google_imports import aiplatform, vertexai

class IntentClassifierAgent(BaseAgent):
    """
    Agent responsible for classifying user intents and routing them to the appropriate handler.
    Uses Google's Vertex AI for intent classification.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Intent Classifier Agent.
        
        Args:
            config: Configuration dictionary containing:
                - project_id: Google Cloud project ID
                - location: Google Cloud region
                - endpoint_id: Vertex AI endpoint ID for the classification model
        """
        super().__init__("intent_classifier", config)
        self.endpoint = None
        self.possible_intents = [
            "billing",
            "technical_support",
            "product_information",
            "account_management",
            "order_status",
            "refund_request",
            "general_inquiry"
        ]
    
    def initialize_agent(self) -> None:
        """Initialize the Vertex AI endpoint for intent classification."""
        try:
            project_id = self.config.get("project_id")
            location = self.config.get("location", "us-central1")
            endpoint_id = self.config.get("endpoint_id")
            
            if not all([project_id, endpoint_id]):
                self.logger.warning(
                    "Missing required configuration for Vertex AI. Using mock classification."
                )
                return
            
            # Log initialization attempt
            vertex_ai_logger.logger.info(
                f"Initializing Vertex AI endpoint - Project: {project_id}, "
                f"Location: {location}, Endpoint: {endpoint_id}"
            )
            
            # Initialize Vertex AI
            vertexai.init(project=project_id, location=location)
            self.endpoint = aiplatform.Endpoint(endpoint_id)
            
            # Verify endpoint access
            self.logger.info(f"Vertex AI endpoint initialized: {self.endpoint.resource_name}")
            vertex_ai_logger.logger.info(
                f"Successfully connected to Vertex AI endpoint: {endpoint_id}"
            )
            
        except Exception as e:
            error_msg = f"Error initializing Vertex AI endpoint: {str(e)}"
            self.logger.error(error_msg)
            vertex_ai_logger.logger.error(
                "Failed to initialize Vertex AI endpoint",
                extra={"error": str(e), "error_type": type(e).__name__}
            )
            self.endpoint = None
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the user query to determine the intent.
        
        Args:
            input_data: Dictionary containing:
                - message: User's message text
                - user_id: Optional user ID for personalization
                - session_id: Optional session ID for conversation tracking
                
        Returns:
            Dictionary containing:
                - intent: Predicted intent
                - confidence: Confidence score (0-1)
                - entities: Extracted entities (if any)
        """
        message = input_data.get("message", "").strip()
        if not message:
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "entities": {}
            }
        
        # If Vertex AI endpoint is not available, use a simple rule-based classifier
        if self.endpoint is None:
            return self._rule_based_classification(message)
        
        # Otherwise, use the Vertex AI endpoint for classification
        return await self._vertex_ai_classification(message)
    
    async def _vertex_ai_classification(self, message: str) -> Dict[str, Any]:
        """Classify intent using Vertex AI endpoint."""
        try:
            # Log the prediction request
            vertex_ai_logger.log_model_call(
                model_name="intent_classifier",
                prompt=message,
                parameters={"method": "predict"},
                metadata={
                    "endpoint": self.endpoint.resource_name,
                    "message_length": len(message)
                }
            )
            
            # Prepare the instance for prediction
            instance = {
                "content": message,
                "mime_type": "text/plain"
            }
            
            # Make the prediction
            prediction = await self.endpoint.predict(instances=[instance])
            
            # Process the prediction result
            if prediction.predictions and len(prediction.predictions) > 0:
                result = prediction.predictions[0]
                response = {
                    "intent": result.get("intent", "unknown"),
                    "confidence": result.get("confidence", 0.0),
                    "entities": result.get("entities", {})
                }
                
                # Log successful prediction
                vertex_ai_logger.log_model_call(
                    model_name="intent_classifier",
                    prompt=message,
                    parameters={"method": "predict"},
                    response=response,
                    metadata={
                        "endpoint": self.endpoint.resource_name,
                        "prediction_type": type(prediction).__name__
                    }
                )
                
                return response
                
            # If no predictions, log and fall back to rule-based
            vertex_ai_logger.logger.warning(
                "No predictions returned from Vertex AI endpoint",
                extra={"message": message[:100]}
            )
            return self._rule_based_classification(message)
            
        except Exception as e:
            error_msg = f"Error in Vertex AI classification: {str(e)}"
            self.logger.error(error_msg)
            
            # Log the error with additional context
            vertex_ai_logger.log_model_call(
                model_name="intent_classifier",
                prompt=message,
                parameters={"method": "predict"},
                error=e,
                metadata={
                    "endpoint": self.endpoint.resource_name if self.endpoint else None,
                    "error_type": type(e).__name__
                }
            )
            
            # Fall back to rule-based classification
            return self._rule_based_classification(message)
        
    def _rule_based_classification(self, message: str) -> Dict[str, Any]:
        """
        Simple rule-based intent classification as a fallback.
        This is a basic implementation that can be enhanced with more sophisticated rules.
        """
        # Log fallback to rule-based classification
        vertex_ai_logger.logger.info(
            "Using rule-based classification fallback",
            extra={"message_preview": (message[:100] + '...') if len(message) > 100 else message}
        )
        
        message_lower = message.lower()
        
        # Define keyword patterns for each intent
        intent_keywords = {
            "billing": ["bill", "invoice", "payment", "charge", "refund", "pricing"],
            "technical_support": ["help", "support", "issue", "problem", "not working", "error"],
            "product_information": ["feature", "how to", "what is", "can i", "does it", "product"],
            "account_management": ["account", "login", "sign up", "password", "profile"],
            "order_status": ["order", "track", "delivery", "shipping", "when will"],
            "refund_request": ["refund", "return", "cancel", "money back"],
            "general_inquiry": ["hello", "hi", "hey", "thank", "thanks", "bye"]
        }
        
        # Check for matching intents
        matched_intents = []
        for intent, keywords in intent_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                matched_intents.append(intent)
        
        # Determine the most specific intent or default to general inquiry
        if not matched_intents:
            intent = "general_inquiry"
            confidence = 0.3
        else:
            # If multiple intents matched, pick the most specific one (first in the list)
            intent = matched_intents[0]
            confidence = min(0.9, 0.3 + (len(matched_intents) * 0.1))
        
        # Log the matched intent
        vertex_ai_logger.logger.info(
            f"Rule-based classification matched intent '{intent}'",
            extra={
                "matched_intents": matched_intents,
                "confidence": confidence,
                "intent": intent
            }
        )
        
        return {
            "intent": intent,
            "confidence": confidence,
            "entities": {}
        }
    
    def get_possible_intents(self) -> List[str]:
        """Return the list of possible intents this classifier can detect."""
        return self.possible_intents
