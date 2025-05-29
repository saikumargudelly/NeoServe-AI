from typing import Dict, Any, List, Optional
import logging
from .base_agent import BaseAgent
from google.cloud import aiplatform

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
            
            # Initialize the Vertex AI endpoint
            aiplatform.init(project=project_id, location=location)
            self.endpoint = aiplatform.Endpoint(endpoint_id)
            self.logger.info("Initialized Vertex AI endpoint for intent classification")
            
        except Exception as e:
            self.logger.error(f"Error initializing Vertex AI endpoint: {str(e)}")
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
            # Prepare the instance for prediction
            instance = {
                "content": message,
                "mime_type": "text/plain"
            }
            
            # Make the prediction
            prediction = await self.endpoint.predict(instances=[instance])
            
            # Process the prediction result
            # Note: Adjust this based on your model's output format
            if prediction.predictions and len(prediction.predictions) > 0:
                result = prediction.predictions[0]
                return {
                    "intent": result.get("intent", "unknown"),
                    "confidence": result.get("confidence", 0.0),
                    "entities": result.get("entities", {})
                }
                
        except Exception as e:
            self.logger.error(f"Error in Vertex AI classification: {str(e)}")
        
        # Fall back to rule-based classification if there's an error
        return self._rule_based_classification(message)
    
    def _rule_based_classification(self, message: str) -> Dict[str, Any]:
        """
        Simple rule-based intent classification as a fallback.
        This is a basic implementation that can be enhanced with more sophisticated rules.
        """
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
        
        return {
            "intent": intent,
            "confidence": confidence,
            "entities": {}
        }
    
    def get_possible_intents(self) -> List[str]:
        """Return the list of possible intents this classifier can detect."""
        return self.possible_intents
