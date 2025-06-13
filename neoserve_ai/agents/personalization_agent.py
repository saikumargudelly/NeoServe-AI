from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
from .base_agent import BaseAgent
# Use our custom import wrapper for better error handling
from .google_imports import FIRESTORE_CLIENT, FieldFilter

class PersonalizationAgent(BaseAgent):
    """
    Agent responsible for personalizing responses based on user data.
    Integrates with Firestore for user profiles and interaction history.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Personalization Agent.
        
        Args:
            config: Configuration dictionary containing:
                - project_id: Google Cloud project ID
                - user_collection: Name of the Firestore collection for user profiles (default: 'users')
                - interaction_collection: Name of the Firestore collection for interaction history (default: 'interactions')
        """
        super().__init__("personalization_agent", config)
        self.db = None
        self.user_collection = None
        self.interaction_collection = None
    
    def initialize_agent(self) -> None:
        """Initialize the Firestore client and collections."""
        try:
            if FIRESTORE_CLIENT is None:
                raise ImportError("Firestore client is not available. Check logs for import errors.")
                
            # Initialize Firestore client
            self.db = FIRESTORE_CLIENT(project=self.config.get("project_id"))
            
            # Set collection names with defaults
            self.user_collection = self.config.get("user_collection", "users")
            self.interaction_collection = self.config.get("interaction_collection", "interactions")
            
            self.logger.info("Initialized Personalization Agent with Firestore")
            
        except Exception as e:
            self.logger.error(f"Error initializing Personalization Agent: {str(e)}")
            self.db = None
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Personalize the response based on user data and context.
        
        Args:
            input_data: Dictionary containing:
                - user_id: User ID for personalization
                - message: The message to personalize
                - context: Additional context for personalization
                - intent: The detected intent (optional)
                
        Returns:
            Dictionary containing:
                - personalized_message: The personalized message
                - user_preferences: Any user preferences used for personalization
                - interaction_history: Relevant interaction history
        """
        user_id = input_data.get("user_id")
        if not user_id:
            return {
                "personalized_message": input_data.get("message", ""),
                "user_preferences": {},
                "interaction_history": []
            }
        
        try:
            # Get user profile and recent interactions
            user_profile = await self._get_user_profile(user_id)
            recent_interactions = await self._get_recent_interactions(user_id)
            
            # Log the current interaction
            await self._log_interaction(user_id, input_data)
            
            # Personalize the message
            personalized_message = self._personalize_message(
                input_data.get("message", ""),
                user_profile,
                recent_interactions,
                input_data.get("intent")
            )
            
            return {
                "personalized_message": personalized_message,
                "user_preferences": user_profile.get("preferences", {}),
                "interaction_history": recent_interactions
            }
            
        except Exception as e:
            self.logger.error(f"Error in personalization: {str(e)}")
            # Return the original message if personalization fails
            return {
                "personalized_message": input_data.get("message", ""),
                "user_preferences": {},
                "interaction_history": []
            }
    
    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve the user's profile from Firestore.
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            Dictionary containing the user's profile data
        """
        if not self.db:
            return {}
            
        try:
            doc_ref = self.db.collection(self.user_collection).document(user_id)
            doc = await doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                # Create a default profile if it doesn't exist
                default_profile = {
                    "user_id": user_id,
                    "created_at": datetime.utcnow(),
                    "preferences": {},
                    "metadata": {}
                }
                await doc_ref.set(default_profile)
                return default_profile
                
        except Exception as e:
            self.logger.error(f"Error fetching user profile: {str(e)}")
            return {}
    
    async def _get_recent_interactions(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve the user's recent interactions.
        
        Args:
            user_id: The user's unique identifier
            limit: Maximum number of interactions to return
            
        Returns:
            List of recent interactions
        """
        if not self.db:
            return []
            
        try:
            # Query interactions from the last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            query = (
                self.db.collection(self.interaction_collection)
                .where(filter=FieldFilter("user_id", "==", user_id))
                .where(filter=FieldFilter("timestamp", ">=", thirty_days_ago))
                .order_by("timestamp", direction="DESCENDING")
                .limit(limit)
            )
            
            docs = await query.get()
            return [doc.to_dict() for doc in docs]
            
        except Exception as e:
            self.logger.error(f"Error fetching interaction history: {str(e)}")
            return []
    
    async def _log_interaction(self, user_id: str, interaction_data: Dict[str, Any]) -> None:
        """
        Log a user interaction to Firestore.
        
        Args:
            user_id: The user's unique identifier
            interaction_data: Interaction data to log
        """
        if not self.db:
            return
            
        try:
            interaction = {
                "user_id": user_id,
                "timestamp": datetime.utcnow(),
                "message": interaction_data.get("message", ""),
                "intent": interaction_data.get("intent"),
                "context": interaction_data.get("context", {})
            }
            
            await self.db.collection(self.interaction_collection).add(interaction)
            
        except Exception as e:
            self.logger.error(f"Error logging interaction: {str(e)}")
    
    def _personalize_message(
        self, 
        message: str, 
        user_profile: Dict[str, Any],
        recent_interactions: List[Dict[str, Any]],
        intent: Optional[str] = None
    ) -> str:
        """
        Personalize a message based on user data and context.
        
        Args:
            message: The original message
            user_profile: The user's profile data
            recent_interactions: List of recent interactions
            intent: The detected intent (if any)
            
        Returns:
            The personalized message
        """
        if not message:
            return message
            
        # Extract user preferences
        preferences = user_profile.get("preferences", {})
        name = preferences.get("name", "there")
        
        # Simple personalization based on user's name
        personalized = message
        if name and name != "there":
            # Only add the name if it's not already in the message
            if name.lower() not in message.lower():
                personalized = f"{name}, {message[0].lower()}{message[1:] if len(message) > 1 else ''}"
        
        # Add contextual personalization based on recent interactions
        if recent_interactions:
            last_interaction = recent_interactions[0]
            last_intent = last_interaction.get("intent")
            
            # If the user is asking about the same thing again
            if last_intent and last_intent == intent:
                personalized = f"To follow up on our previous conversation, {personalized.lower()}"
        
        # Add time-based personalization
        current_hour = datetime.utcnow().hour
        time_greeting = self._get_time_based_greeting(current_hour)
        
        # Only add greeting if the message starts with a greeting
        if any(msg.lower() in message.lower() for msg in ["hi", "hello", "hey"]):
            personalized = f"{time_greeting} {personalized}"
        
        return personalized
    
    def _get_time_based_greeting(self, hour: int) -> str:
        """
        Get an appropriate greeting based on the time of day.
        
        Args:
            hour: Current hour (0-23)
            
        Returns:
            Greeting string
        """
        if 5 <= hour < 12:
            return "Good morning!"
        elif 12 <= hour < 17:
            return "Good afternoon!"
        elif 17 <= hour < 22:
            return "Good evening!"
        else:
            return "Hello!"
    
    async def update_user_preferences(
        self, 
        user_id: str, 
        preferences: Dict[str, Any]
    ) -> bool:
        """
        Update a user's preferences in Firestore.
        
        Args:
            user_id: The user's unique identifier
            preferences: Dictionary of preferences to update
            
        Returns:
            True if the update was successful, False otherwise
        """
        if not self.db or not user_id or not preferences:
            return False
            
        try:
            doc_ref = self.db.collection(self.user_collection).document(user_id)
            await doc_ref.set({"preferences": preferences}, merge=True)
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating user preferences: {str(e)}")
            return False
