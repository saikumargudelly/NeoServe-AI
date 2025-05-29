from typing import Dict, Any, Optional, List, Callable, Awaitable
import asyncio
import logging
from datetime import datetime
from .intent_classifier import IntentClassifierAgent
from .knowledge_agent import KnowledgeBaseAgent
from .personalization_agent import PersonalizationAgent
from .proactive_engagement_agent import ProactiveEngagementAgent
from .escalation_agent import EscalationAgent
from .base_agent import BaseAgent

class AgentOrchestrator:
    """
    Orchestrates the flow between different agents in the NeoServe AI system.
    Manages the conversation flow, agent selection, and response generation.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the AgentOrchestrator with configuration.
        
        Args:
            config: Configuration dictionary containing settings for all agents
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.agents = {}
        self.conversation_history = {}
        self.max_history_size = config.get("max_history_size", 20)
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize all agents and required resources."""
        if self.initialized:
            return
            
        try:
            # Initialize all agents
            self.agents["intent_classifier"] = IntentClassifierAgent(
                config=self.config.get("intent_classifier", {})
            )
            
            self.agents["knowledge_base"] = KnowledgeBaseAgent(
                config=self.config.get("knowledge_base", {})
            )
            
            self.agents["personalization"] = PersonalizationAgent(
                config=self.config.get("personalization", {})
            )
            
            self.agents["proactive_engagement"] = ProactiveEngagementAgent(
                config=self.config.get("proactive_engagement", {})
            )
            
            self.agents["escalation"] = EscalationAgent(
                config=self.config.get("escalation", {})
            )
            
            # Initialize all agents
            for name, agent in self.agents.items():
                if isinstance(agent, BaseAgent):
                    agent.initialize_agent()
            
            self.initialized = True
            self.logger.info("AgentOrchestrator initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing AgentOrchestrator: {str(e)}")
            self.initialized = False
    
    async def process_message(
        self,
        user_id: str,
        session_id: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process an incoming message through the agent pipeline.
        
        Args:
            user_id: Unique identifier for the user
            session_id: Unique identifier for the conversation session
            message: The user's message
            metadata: Additional metadata for context
            
        Returns:
            Dictionary containing the agent's response and metadata
        """
        if not self.initialized:
            await self.initialize()
            if not self.initialized:
                return self._create_error_response(
                    "System initialization failed. Please try again later.",
                    "system_error"
                )
        
        try:
            # Initialize conversation history if needed
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
            
            # Add user message to history
            self._add_to_history(session_id, "user", message, metadata)
            
            # Check for escalation first
            escalation_result = await self._check_escalation(user_id, session_id, message)
            if escalation_result["needs_escalation"]:
                return await self._handle_escalation(
                    user_id=user_id,
                    session_id=session_id,
                    message=message,
                    escalation_result=escalation_result,
                    metadata=metadata
                )
            
            # Classify intent
            intent_result = await self.agents["intent_classifier"].process({"message": message})
            
            # Route based on intent
            if intent_result["intent"] in ["billing", "product_information", "general_inquiry"]:
                response = await self._handle_knowledge_based_query(
                    user_id=user_id,
                    session_id=session_id,
                    message=message,
                    intent=intent_result["intent"],
                    confidence=intent_result["confidence"],
                    metadata=metadata
                )
            else:
                # Default response for other intents
                response = {
                    "response": "I'll help you with that. Let me check the best way to assist you.",
                    "intent": intent_result["intent"],
                    "confidence": intent_result["confidence"],
                    "source": "orchestrator"
                }
            
            # Personalize the response
            personalized_response = await self._personalize_response(
                user_id=user_id,
                session_id=session_id,
                response=response,
                metadata=metadata
            )
            
            # Add assistant response to history
            self._add_to_history(
                session_id,
                "assistant",
                personalized_response.get("response", ""),
                {"intent": personalized_response.get("intent")}
            )
            
            # Check for proactive engagement opportunities
            await self._check_proactive_engagement(
                user_id=user_id,
                session_id=session_id,
                message=message,
                intent=intent_result["intent"],
                metadata=metadata
            )
            
            return personalized_response
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return self._create_error_response(
                "I'm sorry, I encountered an error processing your request. "
                "Our team has been notified.",
                "processing_error"
            )
    
    async def _check_escalation(
        self,
        user_id: str,
        session_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Check if the conversation needs to be escalated.
        
        Args:
            user_id: The user ID
            session_id: The session ID
            message: The user's message
            
        Returns:
            Dictionary with escalation decision
        """
        escalation_result = await self.agents["escalation"].process({
            "user_id": user_id,
            "session_id": session_id,
            "message": message,
            "history": self.conversation_history.get(session_id, [])[-5:],  # Last 5 messages
            "metadata": {
                "timestamp": datetime.utcnow().isoformat()
            }
        })
        
        return escalation_result
    
    async def _handle_escalation(
        self,
        user_id: str,
        session_id: str,
        message: str,
        escalation_result: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle an escalation scenario.
        
        Args:
            user_id: The user ID
            session_id: The session ID
            message: The user's message
            escalation_result: Result from the escalation check
            metadata: Additional metadata
            
        Returns:
            Response to the user about the escalation
        """
        reason = escalation_result.get("reason", "unknown reason")
        priority = escalation_result.get("priority", "medium")
        
        # Log the escalation
        self.logger.info(
            f"Escalating conversation for user {user_id}, session {session_id}. "
            f"Reason: {reason}, Priority: {priority}"
        )
        
        # Get a human-readable response based on escalation reason
        response_text = self._get_escalation_response(reason, priority)
        
        # Add the escalation to the conversation history
        self._add_to_history(
            session_id,
            "system",
            f"[ESCALATION] {reason} (Priority: {priority})",
            {"type": "escalation", "priority": priority}
        )
        
        return {
            "response": response_text,
            "intent": "escalation",
            "confidence": 1.0,
            "escalation": {
                "escalated": True,
                "reason": reason,
                "priority": priority,
                "timestamp": datetime.utcnow().isoformat()
            },
            "source": "escalation_agent"
        }
    
    async def _handle_knowledge_based_query(
        self,
        user_id: str,
        session_id: str,
        message: str,
        intent: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle a query that can be answered by the knowledge base.
        
        Args:
            user_id: The user ID
            session_id: The session ID
            message: The user's message
            intent: The detected intent
            confidence: Confidence score of the intent
            metadata: Additional metadata
            
        Returns:
            Response from the knowledge base
        """
        # Query the knowledge base
        kb_response = await self.agents["knowledge_base"].process({
            "message": message,
            "user_id": user_id,
            "session_id": session_id,
            "intent": intent,
            "confidence": confidence,
            "metadata": metadata or {}
        })
        
        return {
            "response": kb_response.get("answer", "I couldn't find any information on that topic."),
            "intent": intent,
            "confidence": confidence,
            "sources": kb_response.get("sources", []),
            "source": "knowledge_base"
        }
    
    async def _personalize_response(
        self,
        user_id: str,
        session_id: str,
        response: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Personalize a response using the personalization agent.
        
        Args:
            user_id: The user ID
            session_id: The session ID
            response: The response to personalize
            metadata: Additional metadata
            
        Returns:
            Personalized response
        """
        personalized = await self.agents["personalization"].process({
            "user_id": user_id,
            "session_id": session_id,
            "message": response.get("response", ""),
            "intent": response.get("intent"),
            "metadata": metadata or {}
        })
        
        # Merge the personalized message with the original response
        response["response"] = personalized.get("personalized_message", response.get("response", ""))
        response["personalization_applied"] = True
        
        return response
    
    async def _check_proactive_engagement(
        self,
        user_id: str,
        session_id: str,
        message: str,
        intent: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Check if there are opportunities for proactive engagement.
        
        Args:
            user_id: The user ID
            session_id: The session ID
            message: The user's message
            intent: The detected intent
            metadata: Additional metadata
        """
        try:
            # Check conditions for proactive engagement
            engagement_opportunity = await self._identify_engagement_opportunity(
                user_id=user_id,
                session_id=session_id,
                message=message,
                intent=intent,
                metadata=metadata
            )
            
            if engagement_opportunity["should_engage"]:
                await self.agents["proactive_engagement"].process({
                    "user_id": user_id,
                    "engagement_type": engagement_opportunity["type"],
                    "message": engagement_opportunity.get("message"),
                    "metadata": {
                        "trigger_intent": intent,
                        "user_message": message,
                        "session_id": session_id,
                        **engagement_opportunity.get("metadata", {})
                    },
                    "trigger_time": engagement_opportunity.get("trigger_time")
                })
                
                # Log the proactive engagement
                self.logger.info(
                    f"Scheduled proactive engagement for user {user_id}. "
                    f"Type: {engagement_opportunity['type']}"
                )
                
        except Exception as e:
            self.logger.error(f"Error in proactive engagement check: {str(e)}", exc_info=True)
    
    async def _identify_engagement_opportunity(
        self,
        user_id: str,
        session_id: str,
        message: str,
        intent: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Identify opportunities for proactive engagement.
        
        Args:
            user_id: The user ID
            session_id: The session ID
            message: The user's message
            intent: The detected intent
            metadata: Additional metadata
            
        Returns:
            Dictionary with engagement opportunity details
        """
        # This is a simplified implementation. In a real system, you would have more sophisticated logic.
        engagement_opportunity = {
            "should_engage": False,
            "type": None,
            "message": None,
            "metadata": {}
        }
        
        # Check for specific intents that might trigger engagement
        if intent == "product_information":
            # If user is asking about a product, consider sending a follow-up
            engagement_opportunity.update({
                "should_engage": True,
                "type": "follow_up",
                "trigger_time": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
                "metadata": {
                    "follow_up_type": "product_interest",
                    "trigger_intent": intent
                },
                "message": (
                    "Hi! I noticed you were interested in our products. "
                    "Do you have any questions I can help with?"
                )
            })
        
        # Add more engagement rules as needed
        
        return engagement_opportunity
    
    def _add_to_history(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            session_id: The session ID
            role: The role of the message sender ('user', 'assistant', 'system')
            content: The message content
            metadata: Additional metadata
        """
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        self.conversation_history[session_id].append(message)
        
        # Limit history size
        if len(self.conversation_history[session_id]) > self.max_history_size:
            self.conversation_history[session_id] = self.conversation_history[session_id][-self.max_history_size:]
    
    def _get_conversation_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get the conversation history for a session.
        
        Args:
            session_id: The session ID
            limit: Maximum number of messages to return
            
        Returns:
            List of message dictionaries
        """
        history = self.conversation_history.get(session_id, [])
        return history[-limit:] if limit else history
    
    def _create_error_response(
        self,
        message: str,
        error_type: str = "unknown_error"
    ) -> Dict[str, Any]:
        """
        Create a standardized error response.
        
        Args:
            message: Error message to display to the user
            error_type: Type of error for internal tracking
            
        Returns:
            Error response dictionary
        """
        return {
            "response": message,
            "intent": "error",
            "confidence": 1.0,
            "error": {
                "type": error_type,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            },
            "source": "orchestrator"
        }
    
    def _get_escalation_response(
        self,
        reason: str,
        priority: str = "medium"
    ) -> str:
        """
        Get a user-friendly message about the escalation.
        
        Args:
            reason: The reason for escalation
            priority: The priority level of the escalation
            
        Returns:
            User-friendly message
        """
        priority_messages = {
            "high": "high priority",
            "critical": "top priority",
            "medium": "priority",
            "low": "standard priority"
        }
        
        priority_text = priority_messages.get(priority.lower(), "")
        
        return (
            "I've escalated your request to our support team with {priority_text}. "
            "Someone will get back to you as soon as possible. "
            "In the meantime, is there anything else I can help you with?"
        ).format(priority_text=priority_text)
