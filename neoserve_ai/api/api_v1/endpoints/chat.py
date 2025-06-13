from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import uuid
import logging

from neoserve_ai.agents.orchestrator import AgentOrchestrator
from neoserve_ai.config.settings import get_config, get_agent_config
from neoserve_ai.schemas.chat import ChatRequest, ChatResponse, ChatMessage, EscalationDetails
from neoserve_ai.schemas.user import User, UserInDB
from neoserve_ai.utils.auth import get_current_user, any_authenticated
from neoserve_ai.api.api_v1.deps import get_optional_user

# Initialize logger
logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(prefix="/chat", tags=["chat"])

# Get configuration
settings = get_config()

# Initialize agent orchestrator
orchestrator = AgentOrchestrator(config={
    "intent_classifier": get_agent_config("intent_classifier"),
    "knowledge_base": get_agent_config("knowledge_agent"),
    "personalization": get_agent_config("personalization_agent"),
    "proactive_engagement": get_agent_config("proactive_engagement_agent"),
    "max_history_size": settings.max_history_size
})

# Initialize the orchestrator
@router.on_event("startup")
async def startup_event():
    try:
        await orchestrator.initialize()
        logger.info("Agent orchestrator initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent orchestrator: {str(e)}")
        raise

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: Optional[User] = Depends(get_optional_user)
) -> ChatResponse:
    """
    Process a chat message and return a response from the appropriate agent.
    
    In development mode, this endpoint can be accessed without authentication.
    In production, a valid JWT token is required.
    
    Args:
        request: The chat request containing the user's message and metadata
        current_user: The authenticated user, or None if not authenticated
        
    Returns:
        ChatResponse containing the agent's response
    """
    # Get config
    config = get_config()
    
    # In development, use a mock user if not authenticated
    if not current_user:
        if config.ENVIRONMENT == "development":
            current_user = UserInDB(
                id=1,
                username="dev_user",
                email="dev@example.com",
                hashed_password="",
                full_name="Development User",
                is_active=True,
                is_superuser=False
            )
        else:
            # In production, require authentication
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Log the incoming request
    logger.info(f"Processing chat request from user {current_user.id}")
    logger.info(f"Message: {request.message}")
    logger.info(f"Session ID: {request.session_id}")
    
    try:
        # Process the message using the orchestrator
        response = await orchestrator.process_message(
            message=request.message,
            session_id=request.session_id,
            user_id=str(current_user.id),
            metadata=request.metadata or {}
        )
        
        # Log the response
        logger.info(f"Generated response: {response.get('response')}")
        
        # Return the response with all required fields
        return ChatResponse(
            message_id=str(uuid.uuid4()),
            session_id=request.session_id,
            timestamp=datetime.utcnow(),
            response=response.get('response', 'No response generated'),
            intent=response.get('intent', 'general_query'),
            confidence=float(response.get('confidence', 0.8)),
            source=response.get('source', 'knowledge_base'),
            metadata=response.get('metadata', {}) or {},
            requires_follow_up=response.get('requires_follow_up', False),
            suggested_responses=response.get('suggested_responses', []),
            sources=response.get('sources', []),
            escalation=response.get('escalation')
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your message"
        )

@router.get("/history/{session_id}", response_model=List[ChatMessage])
async def get_chat_history(
    session_id: str,
    limit: int = 20,
    current_user: Optional[User] = Depends(get_optional_user)
) -> List[ChatMessage]:
    """
    Retrieve chat history for a specific session.
    
    Args:
        session_id: The session ID to retrieve history for
        limit: Maximum number of messages to return
        current_user: The authenticated user (from JWT token)
        
    Returns:
        List of chat messages in the session
    """
    try:
        # In a real implementation, this would fetch from a database
        # For now, return an empty list as a placeholder
        return []
        
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving chat history"
        )

@router.post("/escalate", response_model=Dict[str, Any], tags=["escalation"])
async def escalate_conversation(
    request: Dict[str, Any],
    current_user: User = Depends(any_authenticated)
) -> Dict[str, Any]:
    """
    Manually escalate a conversation to a human agent.
    
    Args:
        request: Dictionary containing escalation details
        current_user: The authenticated user (from JWT token)
        
    Returns:
        Dictionary with the result of the escalation
    """
    try:
        session_id = request.get("session_id")
        reason = request.get("reason", "User requested escalation")
        
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="session_id is required"
            )
        
        # Process the escalation
        result = await orchestrator.process_message(
            user_id=current_user.user_id,
            session_id=session_id,
            message=request.get("message", "I would like to speak with a human agent."),
            metadata={
                "force_escalation": True,
                "escalation_reason": reason,
                "user_metadata": current_user.dict(),
                "request_metadata": request.get("metadata", {})
            }
        )
        
        return {
            "status": "success",
            "escalation_id": result.get("escalation", {}).get("escalation_id"),
            "message": "Your request has been escalated to a human agent.",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error escalating conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your escalation request"
        )

@router.get("/status", response_model=Dict[str, Any], tags=["health"])
async def get_system_status() -> Dict[str, Any]:
    """
    Get the current status of the chat system and its agents.
    
    Returns:
        Dictionary with system status information
    """
    try:
        # In a real implementation, this would check the status of all agents
        # For now, return a simple status
        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "agents": {
                "intent_classifier": "operational",
                "knowledge_base": "operational",
                "personalization": "operational",
                "proactive_engagement": "operational",
                "escalation": "operational"
            },
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving system status"
        )
