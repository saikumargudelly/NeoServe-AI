from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
from .base_agent import BaseAgent
# Use our custom import wrapper for better error handling
from .google_imports import FIRESTORE_CLIENT, FieldFilter

class EscalationAgent(BaseAgent):
    """
    Agent responsible for detecting when a conversation should be escalated to a human agent.
    Tracks conversation history and applies escalation rules to determine when human intervention is needed.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Escalation Agent.
        
        Args:
            config: Configuration dictionary containing:
                - project_id: Google Cloud project ID
                - escalation_collection: Firestore collection for escalation records (default: 'escalations')
                - interaction_collection: Firestore collection for interaction history (default: 'interactions')
                - max_unsuccessful_attempts: Number of failed resolutions before escalation (default: 3)
                - max_wait_time: Maximum wait time before escalation (minutes, default: 30)
        """
        super().__init__("escalation_agent", config)
        self.db = None
        self.escalation_collection = None
        self.interaction_collection = None
        self.max_attempts = 3
        self.max_wait_minutes = 30
        self.escalation_rules = []
    
    def initialize_agent(self) -> None:
        """Initialize the Firestore client and load escalation rules."""
        try:
            project_id = self.config.get("project_id")
            if not project_id:
                self.logger.warning(
                    "Missing project_id in configuration. "
                    "Escalation features will be limited."
                )
                return
            
            # Initialize Firestore client using our import wrapper
            if FIRESTORE_CLIENT is None:
                raise ValueError("Firestore client is not available. Check your Google Cloud setup and credentials.")
            self.db = FIRESTORE_CLIENT(project=project_id)
            
            # Set collection names with defaults
            self.escalation_collection = self.config.get("escalation_collection", "escalations")
            self.interaction_collection = self.config.get("interaction_collection", "interactions")
            
            # Load configuration
            self.max_attempts = self.config.get("max_unsuccessful_attempts", 3)
            self.max_wait_minutes = self.config.get("max_wait_time", 30)
            
            # Initialize default escalation rules
            self._initialize_default_rules()
            
            self.logger.info("Initialized Escalation Agent with Firestore")
            
        except Exception as e:
            self.logger.error(f"Error initializing Escalation Agent: {str(e)}")
            self.db = None
    
    def _initialize_default_rules(self) -> None:
        """Initialize default escalation rules if none are provided in config."""
        self.escalation_rules = self.config.get("escalation_rules", [
            {
                "name": "multiple_unsuccessful_attempts",
                "condition": self._check_multiple_attempts,
                "priority": "medium"
            },
            {
                "name": "high_priority_keywords",
                "condition": self._check_high_priority_keywords,
                "priority": "high"
            },
            {
                "name": "sentiment_escalation",
                "condition": self._check_negative_sentiment,
                "priority": "medium"
            },
            {
                "name": "explicit_escalation",
                "condition": self._check_explicit_escalation_request,
                "priority": "high"
            }
        ])
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a conversation turn and determine if escalation is needed.
        
        Args:
            input_data: Dictionary containing:
                - user_id: The user ID
                - message: The user's message
                - session_id: The conversation session ID
                - intent: The detected intent (optional)
                - confidence: The confidence score of the intent (optional)
                - metadata: Additional metadata (optional)
                
        Returns:
            Dictionary containing:
                - needs_escalation: Boolean indicating if escalation is needed
                - reason: Reason for escalation (if applicable)
                - priority: Escalation priority (low, medium, high, critical)
                - suggested_agent: Suggested agent type for handling the escalation
        """
        if not self.db:
            return {
                "needs_escalation": False,
                "reason": "Escalation service not available",
                "priority": "none",
                "suggested_agent": None
            }
        
        try:
            user_id = input_data.get("user_id")
            session_id = input_data.get("session_id")
            
            if not user_id or not session_id:
                return {
                    "needs_escalation": False,
                    "reason": "Missing required fields: user_id and session_id are required",
                    "priority": "none",
                    "suggested_agent": None
                }
            
            # Get conversation history
            conversation_history = await self._get_conversation_history(user_id, session_id)
            
            # Check escalation rules
            escalation_result = await self._check_escalation_rules(input_data, conversation_history)
            
            # If escalation is needed, create an escalation record
            if escalation_result["needs_escalation"]:
                await self._create_escalation_record(
                    user_id=user_id,
                    session_id=session_id,
                    reason=escalation_result["reason"],
                    priority=escalation_result["priority"],
                    suggested_agent=escalation_result["suggested_agent"],
                    conversation_history=conversation_history
                )
            
            return escalation_result
            
        except Exception as e:
            self.logger.error(f"Error in escalation processing: {str(e)}")
            return {
                "needs_escalation": True,
                "reason": f"Error in escalation processing: {str(e)}",
                "priority": "high",
                "suggested_agent": "technical_support"
            }
    
    async def _check_escalation_rules(
        self,
        current_input: Dict[str, Any],
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check all escalation rules to determine if escalation is needed.
        
        Args:
            current_input: Current user input
            conversation_history: List of previous conversation turns
            
        Returns:
            Dictionary with escalation decision and details
        """
        escalation_result = {
            "needs_escalation": False,
            "reason": None,
            "priority": "low",
            "suggested_agent": None
        }
        
        # Check each rule until we find one that triggers escalation
        for rule in self.escalation_rules:
            try:
                rule_result = await rule["condition"](current_input, conversation_history)
                if rule_result["needs_escalation"]:
                    escalation_result.update({
                        "needs_escalation": True,
                        "reason": rule_result.get("reason", f"Triggered by rule: {rule['name']}"),
                        "priority": rule_result.get("priority", rule.get("priority", "medium")),
                        "suggested_agent": rule_result.get("suggested_agent")
                    })
                    break
            except Exception as e:
                self.logger.error(f"Error evaluating escalation rule {rule.get('name')}: {str(e)}")
        
        return escalation_result
    
    async def _check_multiple_attempts(
        self,
        current_input: Dict[str, Any],
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check if the user has made multiple unsuccessful attempts.
        
        Args:
            current_input: Current user input
            conversation_history: List of previous conversation turns
            
        Returns:
            Dictionary with escalation decision
        """
        # Count unsuccessful bot responses in the conversation
        unsuccessful_attempts = sum(
            1 for turn in conversation_history[-self.max_attempts:]
            if turn.get("role") == "assistant" and turn.get("unsuccessful", False)
        )
        
        if unsuccessful_attempts >= self.max_attempts - 1:  # -1 because we're checking before adding current turn
            return {
                "needs_escalation": True,
                "reason": f"User has had {unsuccessful_attempts + 1} unsuccessful attempts",
                "priority": "medium",
                "suggested_agent": "customer_service"
            }
        
        return {"needs_escalation": False}
    
    async def _check_high_priority_keywords(
        self,
        current_input: Dict[str, Any],
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check for high-priority keywords that require immediate escalation.
        
        Args:
            current_input: Current user input
            conversation_history: List of previous conversation turns
            
        Returns:
            Dictionary with escalation decision
        """
        high_priority_phrases = [
            "speak to a human",
            "talk to a person",
            "let me talk to a manager",
            "this is urgent",
            "I need help now",
            "emergency",
            "critical issue",
            "not working at all",
            "cancel my account",
            "I want to cancel"
        ]
        
        message = current_input.get("message", "").lower()
        
        for phrase in high_priority_phrases:
            if phrase in message:
                return {
                    "needs_escalation": True,
                    "reason": f"High-priority phrase detected: {phrase}",
                    "priority": "high",
                    "suggested_agent": "senior_support"
                }
        
        return {"needs_escalation": False}
    
    async def _check_negative_sentiment(
        self,
        current_input: Dict[str, Any],
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check for negative sentiment that might indicate frustration.
        
        Args:
            current_input: Current user input
            conversation_history: List of previous conversation turns
            
        Returns:
            Dictionary with escalation decision
        """
        # This is a simplified implementation. In production, you would use a sentiment analysis API.
        negative_words = [
            "angry", "frustrated", "disappointed", "terrible", "awful",
            "horrible", "worst", "hate", "useless", "waste"
        ]
        
        message = current_input.get("message", "").lower()
        
        # Check for negative words and exclamation marks as a simple proxy for sentiment
        negative_word_count = sum(1 for word in negative_words if word in message)
        exclamation_count = message.count("!")
        
        if negative_word_count > 1 or (negative_word_count > 0 and exclamation_count > 1):
            return {
                "needs_escalation": True,
                "reason": "Negative sentiment detected",
                "priority": "high",
                "suggested_agent": "customer_relations"
            }
        
        return {"needs_escalation": False}
    
    async def _check_explicit_escalation_request(
        self,
        current_input: Dict[str, Any],
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check if the user has explicitly requested escalation.
        
        Args:
            current_input: Current user input
            conversation_history: List of previous conversation turns
            
        Returns:
            Dictionary with escalation decision
        """
        message = current_input.get("message", "").lower()
        
        explicit_requests = [
            "speak to a human",
            "talk to a real person",
            "connect me with an agent",
            "let me talk to someone",
            "transfer me to a person"
        ]
        
        if any(req in message for req in explicit_requests):
            return {
                "needs_escalation": True,
                "reason": "User explicitly requested human assistance",
                "priority": "high",
                "suggested_agent": "customer_service"
            }
        
        return {"needs_escalation": False}
    
    async def _get_conversation_history(
        self,
        user_id: str,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the conversation history for a user session.
        
        Args:
            user_id: The user ID
            session_id: The conversation session ID
            limit: Maximum number of turns to retrieve
            
        Returns:
            List of conversation turns
        """
        try:
            # Query the interaction history for this user and session
            query = (
                self.db.collection(self.interaction_collection)
                .where(filter=FieldFilter("user_id", "==", user_id))
                .where(filter=FieldFilter("session_id", "==", session_id))
                .order_by("timestamp", direction="DESCENDING")
                .limit(limit)
            )
            
            docs = await query.get()
            
            # Convert to list of dictionaries and reverse to maintain chronological order
            history = [doc.to_dict() for doc in docs]
            return history[::-1]  # Reverse to get oldest first
            
        except Exception as e:
            self.logger.error(f"Error fetching conversation history: {str(e)}")
            return []
    
    async def _create_escalation_record(
        self,
        user_id: str,
        session_id: str,
        reason: str,
        priority: str = "medium",
        suggested_agent: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Create a new escalation record in Firestore.
        
        Args:
            user_id: The user ID
            session_id: The conversation session ID
            reason: Reason for escalation
            priority: Escalation priority (low, medium, high, critical)
            suggested_agent: Suggested agent type for handling the escalation
            conversation_history: The conversation history leading to escalation
        """
        try:
            escalation_data = {
                "user_id": user_id,
                "session_id": session_id,
                "status": "pending",
                "reason": reason,
                "priority": priority,
                "suggested_agent": suggested_agent,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "assigned_agent": None,
                "resolved_at": None,
                "resolution_notes": None,
                "conversation_snapshot": conversation_history or []
            }
            
            # Add the escalation record to Firestore
            doc_ref = self.db.collection(self.escalation_collection).document()
            await doc_ref.set(escalation_data)
            
            self.logger.info(f"Created escalation record for user {user_id}, session {session_id}")
            
        except Exception as e:
            self.logger.error(f"Error creating escalation record: {str(e)}")
    
    async def get_active_escalations(
        self,
        status: str = "pending",
        priority: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve active escalations matching the given criteria.
        
        Args:
            status: Status filter (default: 'pending')
            priority: Optional priority filter (low, medium, high, critical)
            limit: Maximum number of escalations to return (default: 50)
            
        Returns:
            List of escalation records
        """
        if not self.db:
            return []
            
        try:
            query = self.db.collection(self.escalation_collection)
            
            # Apply filters
            query = query.where("status", "==", status)
            
            if priority:
                query = query.where("priority", "==", priority)
            
            # Order by creation time (oldest first)
            query = query.order_by("created_at", direction="ASCENDING").limit(limit)
            
            # Execute query
            docs = await query.get()
            
            # Convert to list of dictionaries
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
            
        except Exception as e:
            self.logger.error(f"Error retrieving active escalations: {str(e)}")
            return []
    
    async def update_escalation_status(
        self,
        escalation_id: str,
        status: str,
        assigned_agent: Optional[str] = None,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """
        Update the status of an escalation.
        
        Args:
            escalation_id: The ID of the escalation to update
            status: New status (e.g., 'in_progress', 'resolved', 'cancelled')
            assigned_agent: ID of the agent assigned to the escalation
            resolution_notes: Notes about the resolution
            
        Returns:
            True if the update was successful, False otherwise
        """
        if not self.db:
            return False
            
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if assigned_agent:
                update_data["assigned_agent"] = assigned_agent
            
            if status == "resolved":
                update_data["resolved_at"] = datetime.utcnow()
                if resolution_notes:
                    update_data["resolution_notes"] = resolution_notes
            
            doc_ref = self.db.collection(self.escalation_collection).document(escalation_id)
            await doc_ref.update(update_data)
            
            self.logger.info(f"Updated escalation {escalation_id} to status: {status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating escalation status: {str(e)}")
            return False
