"""
Test script to verify imports in the same context as FastAPI application.
"""
import sys
import os
import logging
from pprint import pprint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def log_environment():
    """Log environment information."""
    logger.info("=" * 50)
    logger.info("Python Environment Information")
    logger.info("=" * 50)
    
    logger.info("\nPython sys.path:")
    for path in sys.path:
        logger.info(f"  {path}")
    
    logger.info("\nEnvironment Variables:")
    for key, value in os.environ.items():
        if any(x in key.lower() for x in ['python', 'path', 'conda', 'venv']):
            logger.info(f"{key}: {value}")

def test_google_imports():
    """Test Google Cloud imports."""
    logger.info("\n" + "=" * 50)
    logger.info("Testing Google Cloud Imports")
    logger.info("=" * 50)
    
    try:
        logger.info("\nAttempting to import google.cloud.tasks_v2...")
        from google.cloud import tasks_v2
        logger.info(f"✅ Successfully imported google.cloud.tasks_v2 version: {tasks_v2.__version__}")
        logger.info(f"   Location: {tasks_v2.__file__}")
    except ImportError as e:
        logger.error(f"❌ Failed to import google.cloud.tasks_v2")
        logger.error(f"   Error: {str(e)}")
    
    try:
        logger.info("\nAttempting to import google.cloud.firestore...")
        from google.cloud import firestore
        logger.info(f"✅ Successfully imported google.cloud.firestore version: {firestore.__version__}")
        logger.info(f"   Location: {firestore.__file__}")
    except ImportError as e:
        logger.error(f"❌ Failed to import google.cloud.firestore")
        logger.error(f"   Error: {str(e)}")
    
    try:
        logger.info("\nAttempting to import google.cloud.pubsub_v1...")
        from google.cloud import pubsub_v1
        logger.info(f"✅ Successfully imported google.cloud.pubsub_v1")
        logger.info(f"   Location: {pubsub_v1.__file__}")
    except ImportError as e:
        logger.error(f"❌ Failed to import google.cloud.pubsub_v1")
        logger.error(f"   Error: {str(e)}")
    
    try:
        logger.info("\nAttempting to import google.cloud.scheduler...")
        from google.cloud import scheduler
        logger.info(f"✅ Successfully imported google.cloud.scheduler version: {scheduler.__version__}")
        logger.info(f"   Location: {scheduler.__file__}")
    except ImportError as e:
        logger.error(f"❌ Failed to import google.cloud.scheduler")
        logger.error(f"   Error: {str(e)}")
    
    try:
        logger.info("\nAttempting to import google.cloud.discoveryengine...")
        from google.cloud import discoveryengine
        logger.info(f"✅ Successfully imported google.cloud.discoveryengine version: {discoveryengine.__version__}")
        logger.info(f"   Location: {discoveryengine.__file__}")
    except ImportError as e:
        logger.error(f"❌ Failed to import google.cloud.discoveryengine")
        logger.error(f"   Error: {str(e)}")

def test_agent_imports():
    """Test agent imports."""
    logger.info("\n" + "=" * 50)
    logger.info("Testing Agent Imports")
    logger.info("=" * 50)
    
    try:
        logger.info("\nAttempting to import KnowledgeBaseAgent...")
        from neoserve_ai.agents.knowledge_agent import KnowledgeBaseAgent
        logger.info("✅ Successfully imported KnowledgeBaseAgent")
        logger.info(f"   Location: {KnowledgeBaseAgent.__module__}")
    except ImportError as e:
        logger.error(f"❌ Failed to import KnowledgeBaseAgent")
        logger.error(f"   Error: {str(e)}")
    
    try:
        logger.info("\nAttempting to import PersonalizationAgent...")
        from neoserve_ai.agents.personalization_agent import PersonalizationAgent
        logger.info("✅ Successfully imported PersonalizationAgent")
        logger.info(f"   Location: {PersonalizationAgent.__module__}")
    except ImportError as e:
        logger.error(f"❌ Failed to import PersonalizationAgent")
        logger.error(f"   Error: {str(e)}")
    
    try:
        logger.info("\nAttempting to import ProactiveEngagementAgent...")
        from neoserve_ai.agents.proactive_engagement_agent import ProactiveEngagementAgent
        logger.info("✅ Successfully imported ProactiveEngagementAgent")
        logger.info(f"   Location: {ProactiveEngagementAgent.__module__}")
    except ImportError as e:
        logger.error(f"❌ Failed to import ProactiveEngagementAgent")
        logger.error(f"   Error: {str(e)}")
    
    try:
        logger.info("\nAttempting to import EscalationAgent...")
        from neoserve_ai.agents.escalation_agent import EscalationAgent
        logger.info("✅ Successfully imported EscalationAgent")
        logger.info(f"   Location: {EscalationAgent.__module__}")
    except ImportError as e:
        logger.error(f"❌ Failed to import EscalationAgent")
        logger.error(f"   Error: {str(e)}")

if __name__ == "__main__":
    # Add project root to Python path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    log_environment()
    test_google_imports()
    test_agent_imports()
    
    logger.info("\n" + "=" * 50)
    logger.info("Test Complete")
    logger.info("=" * 50)
