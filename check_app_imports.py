import sys
import os
from pprint import pprint

def log_environment():
    print("\n" + "="*50)
    print("Python Environment Information")
    print("="*50)
    
    print("\nPython sys.path:")
    pprint(sys.path)
    
    print("\nEnvironment Variables:")
    for key, value in os.environ.items():
        if any(x in key.lower() for x in ['python', 'path', 'conda', 'venv']):
            print(f"{key}: {value}")

if __name__ == "__main__":
    log_environment()
    
    print("\n" + "="*50)
    print("Testing Google Cloud Imports")
    print("="*50)
    
    try:
        print("\nAttempting to import google.cloud.tasks_v2...")
        from google.cloud import tasks_v2
        print(f"✅ Successfully imported google.cloud.tasks_v2 version: {tasks_v2.__version__}")
        print(f"   Location: {tasks_v2.__file__}")
    except ImportError as e:
        print(f"❌ Failed to import google.cloud.tasks_v2")
        print(f"   Error: {str(e)}")
    
    try:
        print("\nAttempting to import google.cloud.firestore...")
        from google.cloud import firestore
        print(f"✅ Successfully imported google.cloud.firestore version: {firestore.__version__}")
        print(f"   Location: {firestore.__file__}")
    except ImportError as e:
        print(f"❌ Failed to import google.cloud.firestore")
        print(f"   Error: {str(e)}")
    
    try:
        print("\nAttempting to import google.cloud.pubsub_v1...")
        from google.cloud import pubsub_v1
        print(f"✅ Successfully imported google.cloud.pubsub_v1")
        print(f"   Location: {pubsub_v1.__file__}")
    except ImportError as e:
        print(f"❌ Failed to import google.cloud.pubsub_v1")
        print(f"   Error: {str(e)}")
    
    try:
        print("\nAttempting to import google.cloud.scheduler...")
        from google.cloud import scheduler
        print(f"✅ Successfully imported google.cloud.scheduler version: {scheduler.__version__}")
        print(f"   Location: {scheduler.__file__}")
    except ImportError as e:
        print(f"❌ Failed to import google.cloud.scheduler")
        print(f"   Error: {str(e)}")
    
    try:
        print("\nAttempting to import google.cloud.discoveryengine...")
        from google.cloud import discoveryengine
        print(f"✅ Successfully imported google.cloud.discoveryengine version: {discoveryengine.__version__}")
        print(f"   Location: {discoveryengine.__file__}")
    except ImportError as e:
        print(f"❌ Failed to import google.cloud.discoveryengine")
        print(f"   Error: {str(e)}")
    
    print("\n" + "="*50)
    print("Test Complete")
    print("="*50)
