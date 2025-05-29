from typing import Dict, Any, List, Optional, Set
import asyncio
import logging
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from google.cloud import pubsub_v1
from google.cloud import scheduler
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

class ProactiveEngagementAgent(BaseAgent):
    """
    Agent responsible for initiating proactive engagement with users.
    Handles scheduling and sending of proactive messages based on triggers.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Proactive Engagement Agent.
        
        Args:
            config: Configuration dictionary containing:
                - project_id: Google Cloud project ID
                - location: Google Cloud region (default: 'us-central1')
                - topic_id: Pub/Sub topic for sending messages (default: 'proactive-engagements')
                - scheduler_region: Cloud Scheduler region (default: same as location)
                - tasks_region: Cloud Tasks region (default: same as location)
        """
        super().__init__("proactive_engagement_agent", config)
        self.publisher = None
        self.scheduler_client = None
        self.tasks_client = None
        self.location = None
        self.topic_path = None
        self.initialized = False
    
    def initialize_agent(self) -> None:
        """Initialize the required GCP clients and resources."""
        try:
            project_id = self.config.project_id
            self.location = self.config.location
            topic_id = self.config.topic_id
            default_delay_minutes = self.config.default_delay_minutes
            max_engagement_attempts = self.config.max_engagement_attempts
            enable_proactive_engagement = self.config.enable_proactive_engagement
            
            if not project_id:
                self.logger.warning(
                    "Missing project_id in configuration. "
                    "Proactive engagement features will be limited."
                )
                return
            
            # Initialize Pub/Sub publisher
            self.publisher = pubsub_v1.PublisherClient()
            self.topic_path = self.publisher.topic_path(project_id, topic_id)
            
            # Ensure the topic exists
            try:
                self.publisher.get_topic(topic=self.topic_path)
            except Exception:
                self.logger.warning(f"Topic {topic_id} does not exist. It will be created when the first message is published.")
            
            # Initialize Cloud Scheduler client
            self.scheduler_client = scheduler.CloudSchedulerClient()
            
            # Initialize Cloud Tasks client
            self.tasks_client = tasks_v2.CloudTasksClient()
            
            self.initialized = True
            self.logger.info("Initialized Proactive Engagement Agent with GCP services")
            
        except Exception as e:
            self.logger.error(f"Error initializing Proactive Engagement Agent: {str(e)}")
            self.initialized = False
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a proactive engagement request.
        
        Args:
            input_data: Dictionary containing:
                - user_id: Target user ID
                - engagement_type: Type of engagement (e.g., 'follow_up', 'promotion', 'tip')
                - message: The message to send (optional, can be generated based on type)
                - trigger_time: When to send the message (ISO format string or datetime object)
                - metadata: Additional data for message personalization
                
        Returns:
            Dictionary containing:
                - status: Success/failure status
                - message_id: ID of the scheduled message (if applicable)
                - scheduled_time: When the message is scheduled for
        """
        if not self.initialized:
            return {
                "status": "error",
                "message": "Agent not properly initialized"
            }
        
        try:
            engagement_type = input_data.get("engagement_type")
            user_id = input_data.get("user_id")
            
            if not user_id or not engagement_type:
                return {
                    "status": "error",
                    "message": "Missing required fields: user_id and engagement_type are required"
                }
            
            # Determine trigger time (default to now + 1 hour)
            trigger_time = self._parse_trigger_time(input_data.get("trigger_time"))
            
            # Generate message if not provided
            message = input_data.get("message")
            if not message:
                message = self._generate_engagement_message(
                    engagement_type,
                    input_data.get("metadata", {})
                )
            
            # Schedule the message
            result = await self._schedule_engagement(
                user_id=user_id,
                message=message,
                engagement_type=engagement_type,
                trigger_time=trigger_time,
                metadata=input_data.get("metadata", {})
            )
            
            return {
                "status": "success",
                "message_id": result.get("message_id"),
                "scheduled_time": trigger_time.isoformat(),
                "message": "Engagement scheduled successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error processing proactive engagement: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to schedule engagement: {str(e)}"
            }
    
    async def _schedule_engagement(
        self,
        user_id: str,
        message: str,
        engagement_type: str,
        trigger_time: datetime,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Schedule a proactive engagement to be sent at a specific time.
        
        Args:
            user_id: Target user ID
            message: The message to send
            engagement_type: Type of engagement
            trigger_time: When to send the message
            metadata: Additional data for the engagement
            
        Returns:
            Dictionary with scheduling details
        """
        # For immediate or near-future messages, use Pub/Sub directly
        if trigger_time <= datetime.utcnow() + timedelta(minutes=1):
            return await self._publish_immediate_engagement(
                user_id=user_id,
                message=message,
                engagement_type=engagement_type,
                metadata=metadata
            )
        
        # For future messages, use Cloud Scheduler + Cloud Tasks
        return await self._schedule_future_engagement(
            user_id=user_id,
            message=message,
            engagement_type=engagement_type,
            trigger_time=trigger_time,
            metadata=metadata
        )
    
    async def _publish_immediate_engagement(
        self,
        user_id: str,
        message: str,
        engagement_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Publish an immediate engagement message via Pub/Sub."""
        try:
            message_data = {
                "user_id": user_id,
                "message": message,
                "engagement_type": engagement_type,
                "scheduled_time": datetime.utcnow().isoformat(),
                "metadata": metadata
            }
            
            # Publish the message
            future = self.publisher.publish(
                self.topic_path,
                data=message_data["message"].encode("utf-8"),
                **{
                    "user_id": user_id,
                    "engagement_type": engagement_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            message_id = future.result()
            
            return {
                "message_id": message_id,
                "delivery_method": "pubsub"
            }
            
        except Exception as e:
            self.logger.error(f"Error publishing immediate engagement: {str(e)}")
            raise
    
    async def _schedule_future_engagement(
        self,
        user_id: str,
        message: str,
        engagement_type: str,
        trigger_time: datetime,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Schedule a future engagement using Cloud Scheduler and Cloud Tasks."""
        try:
            project_id = self.config.project_id
            location = self.config.location
            
            # Create a unique ID for this scheduled engagement
            job_id = f"{user_id}-{engagement_type}-{int(trigger_time.timestamp())}"
            
            # Prepare the task payload
            task = {
                "http_request": {
                    "http_method": "POST",
                    "url": f"https://{location}-{project_id}.cloudfunctions.net/trigger-engagement",
                    "headers": {
                        "Content-Type": "application/json",
                    },
                    "body": json.dumps({
                        "user_id": user_id,
                        "message": message,
                        "engagement_type": engagement_type,
                        "metadata": metadata
                    }).encode(),
                }
            }
            
            # Set the schedule time
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(trigger_time)
            task["schedule_time"] = timestamp
            
            # Create the task
            parent = self.tasks_client.queue_path(project_id, location, "proactive-engagements")
            response = self.tasks_client.create_task(parent=parent, task=task)
            
            return {
                "message_id": response.name,
                "delivery_method": "cloud_tasks",
                "schedule_time": trigger_time.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error scheduling future engagement: {str(e)}")
            raise
    
    def _parse_trigger_time(self, trigger_time) -> datetime:
        """Parse the trigger time from various input formats."""
        if trigger_time is None:
            return datetime.utcnow() + timedelta(hours=1)
            
        if isinstance(trigger_time, datetime):
            return trigger_time
            
        if isinstance(trigger_time, str):
            try:
                return datetime.fromisoformat(trigger_time)
            except ValueError:
                pass
                
            try:
                return datetime.utcfromtimestamp(int(trigger_time))
            except (ValueError, TypeError):
                pass
        
        # Default to 1 hour from now if parsing fails
        self.logger.warning(f"Could not parse trigger_time: {trigger_time}. Defaulting to 1 hour from now.")
        return datetime.utcnow() + timedelta(hours=1)
    
    def _generate_engagement_message(
        self,
        engagement_type: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Generate an engagement message based on type and metadata.
        
        Args:
            engagement_type: Type of engagement
            metadata: Additional data for personalization
            
        Returns:
            Generated message string
        """
        user_name = metadata.get("user_name", "there")
        
        messages = {
            "welcome": [
                f"Welcome to our service, {user_name}! We're excited to have you on board.",
                f"Hi {user_name}, welcome! Let us know if you have any questions.",
                f"Hello {user_name}! Thanks for joining us. Here's what you can do..."
            ],
            "follow_up": [
                f"Hi {user_name}, just following up on our conversation. Do you have any questions?",
                f"Hello {user_name}, we wanted to check if you need any assistance with your recent inquiry.",
                f"Hi {user_name}, we're here to help if you need any clarification."
            ],
            "tip": [
                f"Pro tip, {user_name}: {metadata.get('tip', 'Did you know you can...')}",
                f"{user_name}, here's a helpful tip: {metadata.get('tip', 'You can...')}",
                f"Just a quick tip, {user_name}: {metadata.get('tip', 'Try this trick to...')}"
            ],
            "promotion": [
                f"{user_name}, we have a special offer just for you! {metadata.get('promo_details', '')}",
                f"Exclusive deal for you, {user_name}: {metadata.get('promo_details', '')}",
                f"{user_name}, don't miss out on this limited-time offer! {metadata.get('promo_details', '')}"
            ],
            "abandoned_cart": [
                f"Hi {user_name}, you left something in your cart! Complete your purchase now.",
                f"{user_name}, your cart is waiting! Complete your order before these items are gone.",
                f"Don't forget about your cart, {user_name}! Your selected items are still available."
            ]
        }
        
        # Default message if type not found
        default_messages = [
            f"Hello {user_name}, we have an update for you!",
            f"Hi {user_name}, just wanted to share something with you.",
            f"{user_name}, we thought you might find this interesting."
        ]
        
        # Select a random message from the appropriate list
        import random
        message_list = messages.get(engagement_type, default_messages)
        return random.choice(message_list)
