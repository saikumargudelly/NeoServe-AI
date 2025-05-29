from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl

class ChatMessage(BaseModel):
    """Represents a single message in a chat conversation."""
    message_id: str = Field(..., description="Unique identifier for the message")
    session_id: str = Field(..., description="ID of the chat session")
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="The message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the message was sent")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the message")

class ChatRequest(BaseModel):
    """Request model for sending a chat message."""
    message: str = Field(..., description="The user's message")
    session_id: str = Field(..., description="ID of the chat session")
    message_id: Optional[str] = Field(None, description="Optional client-generated message ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional context or metadata")

class SourceDocument(BaseModel):
    """Represents a source document used to generate a response."""
    title: str = Field(..., description="Title of the document")
    url: Optional[HttpUrl] = Field(None, description="URL to the document")
    snippet: Optional[str] = Field(None, description="Relevant snippet from the document")
    confidence: Optional[float] = Field(None, description="Confidence score of the document's relevance")

class EscalationDetails(BaseModel):
    """Details about an escalation to a human agent."""
    escalated: bool = Field(..., description="Whether the conversation was escalated")
    reason: Optional[str] = Field(None, description="Reason for escalation")
    priority: Optional[str] = Field(None, description="Priority level of the escalation")
    timestamp: Optional[datetime] = Field(None, description="When the escalation occurred")
    estimated_wait_time: Optional[int] = Field(None, description="Estimated wait time in minutes")

class ChatResponse(BaseModel):
    """Response model for a chat interaction."""
    message_id: str = Field(..., description="Unique identifier for the response message")
    session_id: str = Field(..., description="ID of the chat session")
    timestamp: datetime = Field(..., description="When the response was generated")
    response: str = Field(..., description="The assistant's response")
    intent: str = Field(..., description="Detected intent of the user's message")
    confidence: float = Field(..., description="Confidence score of the intent classification (0-1)")
    source: str = Field(..., description="Which agent or component generated the response")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional response metadata")
    requires_follow_up: bool = Field(False, description="Whether a follow-up is needed")
    suggested_responses: List[str] = Field(default_factory=list, description="List of suggested follow-up responses")
    sources: List[SourceDocument] = Field(default_factory=list, description="Source documents used for the response")
    escalation: Optional[EscalationDetails] = Field(None, description="Details about any escalation")

class ConversationHistory(BaseModel):
    """Represents a conversation history with multiple messages."""
    session_id: str = Field(..., description="ID of the chat session")
    user_id: str = Field(..., description="ID of the user who owns the conversation")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the conversation was started")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="When the conversation was last updated")
    messages: List[ChatMessage] = Field(default_factory=list, description="List of messages in the conversation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional conversation metadata")

class ChatFeedback(BaseModel):
    """Feedback on a chat response."""
    message_id: str = Field(..., description="ID of the message being rated")
    session_id: str = Field(..., description="ID of the chat session")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 (poor) to 5 (excellent)")
    feedback: Optional[str] = Field(None, description="Optional detailed feedback")
    tags: List[str] = Field(default_factory=list, description="Tags to categorize the feedback")
