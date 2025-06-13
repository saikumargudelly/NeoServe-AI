from typing import Dict, Any, List, Optional
import logging
from .base_agent import BaseAgent
# Use our custom import wrapper for better error handling
from .google_imports import SEARCH_SERVICE_CLIENT

class KnowledgeBaseAgent(BaseAgent):
    """
    Agent responsible for answering questions using a knowledge base.
    Integrates with Vertex AI Search (Discovery Engine) for document retrieval.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Knowledge Base Agent.
        
        Args:
            config: Configuration dictionary containing:
                - project_id: Google Cloud project ID
                - location: Google Cloud region
                - search_engine_id: Vertex AI Search engine ID
                - serving_config_id: Serving configuration ID (defaults to 'default_config')
        """
        super().__init__("knowledge_base_agent", config)
        self.client = None
        self.search_engine = None
        self.serving_config = None
    
    def initialize_agent(self) -> None:
        """Initialize the Vertex AI Search client and configuration."""
        try:
            project_id = self.config.get("project_id")
            location = self.config.get("location", "global")
            search_engine_id = self.config.get("search_engine_id")
            
            if not all([project_id, search_engine_id]):
                self.logger.warning(
                    "Missing required configuration for Vertex AI Search. "
                    "Knowledge base functionality will be limited."
                )
                return
            
            # Initialize the Discovery Engine client using our imported client class
            if SEARCH_SERVICE_CLIENT is None:
                raise ImportError("Failed to import SearchServiceClient. Check logs for details.")
            self.client = SEARCH_SERVICE_CLIENT()
            
            # Construct the serving config name
            serving_config = self.config.get("serving_config_id", "default_config")
            self.serving_config = self.client.serving_config_path(
                project=project_id,
                location=location,
                data_store=search_engine_id,
                serving_config=serving_config
            )
            
            self.logger.info("Initialized Knowledge Base Agent with Vertex AI Search")
            
        except Exception as e:
            self.logger.error(f"Error initializing Knowledge Base Agent: {str(e)}")
            self.client = None
            self.serving_config = None
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user query against the knowledge base.
        
        Args:
            input_data: Dictionary containing:
                - message: User's question
                - user_id: Optional user ID for personalization
                - session_id: Optional session ID for conversation tracking
                - filters: Optional filters to apply to the search
                
        Returns:
            Dictionary containing:
                - answer: The answer from the knowledge base
                - confidence: Confidence score (0-1)
                - sources: List of source documents used for the answer
        """
        query = input_data.get("message", "").strip()
        if not query:
            return {
                "answer": "I didn't receive a question to look up. How can I help you?",
                "confidence": 0.0,
                "sources": []
            }
        
        # If Vertex AI Search is not available, return a generic response
        if self.client is None or self.serving_config is None:
            return self._fallback_response(query)
        
        try:
            # Prepare the search request
            request = {
                "serving_config": self.serving_config,
                "query": query,
                "page_size": 3,  # Limit to top 3 results
                "query_expansion_spec": {
                    "condition": "AUTO"  # Enable query expansion
                },
                "spell_correction_spec": {
                    "mode": "AUTO"  # Enable spell correction
                },
                "content_search_spec": {
                    "summary_spec": {
                        "summary_result_count": 1,
                        "include_citations": True
                    }
                }
            }
            
            # Add filters if provided
            if "filters" in input_data and isinstance(input_data["filters"], dict):
                request["filter"] = self._build_filter_expression(input_data["filters"])
            
            # Execute the search
            response = await self.client.search(request)
            
            # Process the response
            if not response.results:
                return {
                    "answer": "I couldn't find any relevant information in our knowledge base.",
                    "confidence": 0.0,
                    "sources": []
                }
            
            # Extract the summary if available
            if hasattr(response, 'summary') and response.summary.summary_text:
                answer = response.summary.summary_text
                confidence = 0.9  # High confidence for summarized answers
            else:
                # Fall back to the first result's content
                first_result = response.results[0]
                answer = getattr(first_result.document.derived_struct_data, "snippet", "")
                confidence = 0.7  # Slightly lower confidence for direct snippets
            
            # Extract sources
            sources = []
            for result in response.results[:3]:  # Limit to top 3 sources
                doc = result.document
                source = {
                    "title": getattr(doc.derived_struct_data, "title", ""),
                    "link": getattr(doc.derived_struct_data, "link", ""),
                    "snippet": getattr(doc.derived_struct_data, "snippet", "")
                }
                sources.append(source)
            
            return {
                "answer": answer,
                "confidence": confidence,
                "sources": sources
            }
            
        except Exception as e:
            self.logger.error(f"Error querying knowledge base: {str(e)}")
            return self._fallback_response(query)
    
    def _build_filter_expression(self, filters: Dict[str, Any]) -> str:
        """
        Build a filter expression for the search query.
        
        Args:
            filters: Dictionary of filter conditions
            
        Returns:
            String representation of the filter expression
        """
        filter_parts = []
        for field, value in filters.items():
            if isinstance(value, (str, int, float, bool)):
                filter_parts.append(f'{field} = "{value}"')
            elif isinstance(value, list):
                if value:  # Only add non-empty lists
                    quoted_values = [f'"{v}"' for v in value]
                    filter_parts.append(f'{field} IN({", ".join(quoted_values)})')
        
        return " AND ".join(filter_parts) if filter_parts else ""
    
    def _fallback_response(self, query: str) -> Dict[str, Any]:
        """
        Generate a fallback response when the knowledge base is not available.
        
        Args:
            query: The user's query
            
        Returns:
            Dictionary with a fallback response
        """
        # Simple keyword matching for common questions
        query_lower = query.lower()
        
        responses = [
            (["how to", "how do i"], "Please check our help center at https://support.example.com for detailed instructions."),
            (["contact", "support", "help"], "You can reach our support team at support@example.com or call us at 1-800-EXAMPLE."),
            (["pricing", "cost", "how much"], "For the most up-to-date pricing information, please visit our pricing page at https://example.com/pricing."),
            (["refund", "return", "cancel"], "For refund and return requests, please contact our support team with your order number.")
        ]
        
        for keywords, response in responses:
            if any(keyword in query_lower for keyword in keywords):
                return {
                    "answer": response,
                    "confidence": 0.6,
                    "sources": []
                }
        
        # Default response if no keywords match
        return {
            "answer": "I'm having trouble accessing the knowledge base. "
                     "Please try again later or contact support for assistance.",
            "confidence": 0.3,
            "sources": []
        }
