"""
Test script to verify the google_imports.py module functionality.
"""
import sys
import os
import logging
from pprint import pprint

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def test_imports():
    """Test importing and using Google Cloud clients."""
    logger.info("=" * 80)
    logger.info("Testing Google Cloud Imports")
    logger.info("=" * 80)
    
    # Import the google_imports module
    try:
        from neoserve_ai.agents import google_imports as gi
        logger.info("✅ Successfully imported google_imports module")
        logger.info(f"Module location: {os.path.abspath(gi.__file__)}")
        
        # Test Discovery Engine
        if gi.discoveryengine and gi.SEARCH_SERVICE_CLIENT:
            logger.info("✅ Discovery Engine imports successful")
            logger.info(f"  - discoveryengine: {gi.discoveryengine.__file__}")
            logger.info(f"  - SEARCH_SERVICE_CLIENT: {gi.SEARCH_SERVICE_CLIENT}")
        
        # Test Firestore
        if gi.firestore and gi.FIRESTORE_CLIENT and gi.FieldFilter:
            logger.info("✅ Firestore imports successful")
            logger.info(f"  - firestore: {gi.firestore.__file__}")
            logger.info(f"  - FIRESTORE_CLIENT: {gi.FIRESTORE_CLIENT}")
            logger.info(f"  - FieldFilter: {gi.FieldFilter}")
        
        # Test Pub/Sub
        if gi.pubsub and gi.PUBSUB_PUBLISHER_CLIENT and gi.PUBSUB_SUBSCRIBER_CLIENT:
            logger.info("✅ Pub/Sub imports successful")
            logger.info(f"  - pubsub: {gi.pubsub.__file__}")
            logger.info(f"  - PUBSUB_PUBLISHER_CLIENT: {gi.PUBSUB_PUBLISHER_CLIENT}")
            logger.info(f"  - PUBSUB_SUBSCRIBER_CLIENT: {gi.PUBSUB_SUBSCRIBER_CLIENT}")
        
        # Test Scheduler
        if gi.scheduler and gi.CLOUD_SCHEDULER_CLIENT:
            logger.info("✅ Cloud Scheduler imports successful")
            logger.info(f"  - scheduler: {gi.scheduler.__file__}")
            logger.info(f"  - CLOUD_SCHEDULER_CLIENT: {gi.CLOUD_SCHEDULER_CLIENT}")
        
        # Test Tasks
        if gi.tasks_v2 and gi.CLOUD_TASKS_CLIENT:
            logger.info("✅ Cloud Tasks imports successful")
            logger.info(f"  - tasks_v2: {gi.tasks_v2.__file__}")
            logger.info(f"  - CLOUD_TASKS_CLIENT: {gi.CLOUD_TASKS_CLIENT}")
        
        # Test direct imports
        try:
            from neoserve_ai.agents.google_imports import (
                discoveryengine, SEARCH_SERVICE_CLIENT,
                firestore, FIRESTORE_CLIENT, FieldFilter,
                pubsub_v1, PublisherClient, SubscriberClient,
                scheduler, CLOUD_SCHEDULER_CLIENT,
                tasks_v2, CLOUD_TASKS_CLIENT
            )
            logger.info("✅ Direct imports from google_imports successful")
        except ImportError as e:
            logger.error(f"❌ Direct imports failed: {e}")
            return False
            
        return True
        
    except ImportError as e:
        logger.error(f"❌ Failed to import google_imports: {e}")
        return False

if __name__ == "__main__":
    # Add project root to Python path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    logger.info("Starting Google Cloud imports test...")
    success = test_imports()
    
    if success:
        logger.info("\n🎉 All Google Cloud imports tested successfully!")
    else:
        logger.error("\n❌ Some Google Cloud imports failed. Check the logs above for details.")
    
    logger.info("Test completed.")
