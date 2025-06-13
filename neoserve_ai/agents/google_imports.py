"""
Wrapper module for Google Cloud imports to help with debugging and provide a single point of import.

This module provides a centralized way to import and access Google Cloud client libraries
with proper error handling and logging. It ensures that all Google Cloud imports are
handled consistently across the application.
"""
import sys
import os
import importlib
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for generic type hints
T = TypeVar('T')

def debug_import(module_name: str) -> Any:
    """
    Debug helper to import a module and log information about it.
    
    Args:
        module_name: Fully qualified module name to import
        
    Returns:
        The imported module
        
    Raises:
        ImportError: If the module cannot be imported
    """
    debug_info = []
    debug_info.append(f"\n{'='*80}")
    debug_info.append(f"Attempting to import: {module_name}")
    debug_info.append(f"Current working directory: {os.getcwd()}")
    debug_info.append(f"Python executable: {sys.executable}")
    debug_info.append(f"Python path:")
    
    for p in sys.path:
        debug_info.append(f"  - {p}")
    
    try:
        # Check if the module is already imported
        if module_name in sys.modules:
            module = sys.modules[module_name]
            debug_info.append(f"✅ Module {module_name} is already imported")
            debug_info.append(f"  Module file: {getattr(module, '__file__', 'Unknown')}")
            logger.debug("\n".join(debug_info[-5:]))  # Log only the last few lines
            return module
            
        # Try to import the module
        module = importlib.import_module(module_name)
        debug_info.append(f"✅ Successfully imported {module_name}")
        debug_info.append(f"  Module file: {getattr(module, '__file__', 'Unknown')}")
        logger.debug("\n".join(debug_info[-5:]))  # Log only the last few lines
        return module
        
    except ImportError as e:
        debug_info.append(f"❌ Failed to import {module_name}")
        debug_info.append(f"  Error: {str(e)}")
        debug_info.append(f"  sys.path_importer_cache: {sys.path_importer_cache}")
        debug_info.append("  Environment variables:")
        
        for k, v in os.environ.items():
            if any(x in k.upper() for x in ['PYTHON', 'PATH', 'CONDA', 'VIRTUAL_ENV']):
                debug_info.append(f"    {k} = {v}")
        
        error_msg = "\n".join(debug_info)
        logger.error(error_msg)
        raise ImportError(f"Failed to import {module_name}. See logs for details.") from e

# Dictionary to store all imported modules and clients
google_imports: Dict[str, Any] = {}

def import_google_module(module_name: str, class_name: Optional[str] = None) -> Any:
    """
    Import a Google Cloud module and optionally a specific class from it.
    
    Args:
        module_name: The name of the module to import (e.g., 'google.cloud.firestore')
        class_name: Optional name of a class to import from the module
        
    Returns:
        The imported module or class
        
    Raises:
        ImportError: If the module or class cannot be imported
    """
    try:
        module = debug_import(module_name)
        
        if class_name:
            if hasattr(module, class_name):
                cls = getattr(module, class_name)
                google_imports[class_name] = cls
                return cls
            else:
                raise ImportError(f"Class {class_name} not found in module {module_name}")
        
        google_imports[module_name.split('.')[-1]] = module
        return module
        
    except ImportError as e:
        logger.error(f"Failed to import {module_name}.{class_name or ''}: {str(e)}")
        raise

# Import Google Cloud Discovery Engine
try:
    discoveryengine = import_google_module('google.cloud.discoveryengine')
    SEARCH_SERVICE_CLIENT = import_google_module('google.cloud.discoveryengine', 'SearchServiceClient')
    google_imports['discoveryengine'] = discoveryengine
except ImportError as e:
    logger.error("Failed to import Google Cloud Discovery Engine: %s", str(e))
    discoveryengine = None
    SEARCH_SERVICE_CLIENT = None

# Import Google Cloud Vertex AI
try:
    import vertexai
    from vertexai.preview.generative_models import GenerativeModel
    from google.cloud import aiplatform
    
    # Initialize Vertex AI with project and location from environment variables
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    if project_id:
        vertexai.init(project=project_id, location=location)
        logger.info(f"Initialized Vertex AI with project: {project_id}, location: {location}")
    else:
        logger.warning("GOOGLE_CLOUD_PROJECT not set. Vertex AI initialization skipped.")
    
    google_imports['vertexai'] = vertexai
    google_imports['GenerativeModel'] = GenerativeModel
    google_imports['aiplatform'] = aiplatform
    
except ImportError as e:
    logger.error("Failed to import Google Cloud Vertex AI: %s", str(e))
    vertexai = None
    GenerativeModel = None
    aiplatform = None

# Import Google Cloud Firestore
try:
    firestore = import_google_module('google.cloud.firestore')
    firestore_v1 = import_google_module('google.cloud.firestore_v1')
    from google.cloud.firestore_v1.base_query import FieldFilter
    
    FIRESTORE_CLIENT = firestore.Client
    
    google_imports['firestore'] = firestore
    google_imports['firestore_v1'] = firestore_v1
    google_imports['FieldFilter'] = FieldFilter
except ImportError as e:
    logger.error("Failed to import Google Cloud Firestore: %s", str(e))
    firestore = None
    firestore_v1 = None
    FIRESTORE_CLIENT = None
    FieldFilter = None

# Import Google Cloud Pub/Sub
try:
    pubsub = import_google_module('google.cloud.pubsub_v1')
    from google.cloud.pubsub_v1 import PublisherClient, SubscriberClient
    
    PUBSUB_PUBLISHER_CLIENT = PublisherClient
    PUBSUB_SUBSCRIBER_CLIENT = SubscriberClient
    
    google_imports['pubsub'] = pubsub
    google_imports['pubsub_v1'] = pubsub
    google_imports['PublisherClient'] = PublisherClient
    google_imports['SubscriberClient'] = SubscriberClient
except ImportError as e:
    logger.error("Failed to import Google Cloud Pub/Sub: %s", str(e))
    pubsub = None
    PUBSUB_PUBLISHER_CLIENT = None
    PUBSUB_SUBSCRIBER_CLIENT = None

# Import Google Cloud Scheduler
try:
    scheduler = import_google_module('google.cloud.scheduler')
    CLOUD_SCHEDULER_CLIENT = import_google_module('google.cloud.scheduler', 'CloudSchedulerClient')
    google_imports['scheduler'] = scheduler
except ImportError as e:
    logger.error("Failed to import Google Cloud Scheduler: %s", str(e))
    scheduler = None
    CLOUD_SCHEDULER_CLIENT = None

# Import Google Cloud Tasks
try:
    tasks_v2 = import_google_module('google.cloud.tasks_v2')
    CLOUD_TASKS_CLIENT = import_google_module('google.cloud.tasks_v2', 'CloudTasksClient')
    google_imports['tasks_v2'] = tasks_v2
except ImportError as e:
    logger.error("Failed to import Google Cloud Tasks: %s", str(e))
    tasks_v2 = None
    CLOUD_TASKS_CLIENT = None

# Define all exports
__all__ = [
    # Discovery Engine
    'discoveryengine', 'SEARCH_SERVICE_CLIENT',
    
    # Firestore
    'firestore', 'firestore_v1', 'FIRESTORE_CLIENT', 'FieldFilter',
    
    # Pub/Sub
    'pubsub', 'pubsub_v1', 'PUBSUB_PUBLISHER_CLIENT', 'PUBSUB_SUBSCRIBER_CLIENT',
    'PublisherClient', 'SubscriberClient',
    
    # Scheduler
    'scheduler', 'CLOUD_SCHEDULER_CLIENT',
    
    # Tasks
    'tasks_v2', 'CLOUD_TASKS_CLIENT',
    
    # Vertex AI
    'vertexai', 'GenerativeModel', 'aiplatform',
    
    # Utility
    'debug_import', 'import_google_module', 'google_imports'
]

# Update the module's __dict__ to make imports available directly
# This allows importing directly from the module, e.g., `from neoserve_ai.agents.google_imports import FirestoreClient`
globals().update(google_imports)

# Add a final log message showing what was successfully imported
if __name__ == "__main__":
    logger.info("Successfully imported the following Google Cloud components:")
    for name, obj in google_imports.items():
        if obj is not None:
            module = getattr(obj, '__module__', 'unknown')
            logger.info(f"  - {name}: {module}.{obj.__name__ if hasattr(obj, '__name__') else type(obj).__name__}")
        else:
            logger.warning(f"  - {name}: NOT AVAILABLE")
