import sys
import os
from pprint import pprint

def check_import(module_name):
    print(f"\n{'='*50}")
    print(f"Attempting to import: {module_name}")
    try:
        module = __import__(module_name, fromlist=[''])
        print(f"✅ Successfully imported {module_name}")
        if hasattr(module, '__version__'):
            print(f"   Version: {module.__version__}")
        elif hasattr(module, '__file__'):
            print(f"   Location: {module.__file__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_name}")
        print(f"   Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Python sys.path:")
    pprint(sys.path)
    
    print("\nEnvironment Variables:")
    for key, value in os.environ.items():
        if "python" in key.lower() or "path" in key.lower() or "conda" in key.lower():
            print(f"{key}: {value}")
    
    # Test imports
    modules_to_test = [
        'google',
        'google.cloud',
        'google.cloud.tasks_v2',
        'google.cloud.firestore',
        'google.cloud.pubsub_v1',
        'google.cloud.scheduler',
        'google.cloud.discoveryengine'
    ]
    
    results = {}
    for module in modules_to_test:
        results[module] = check_import(module)
    
    print("\nImport Results:")
    for module, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {module}")
    
    if all(results.values()):
        print("\n🎉 All imports successful!")
    else:
        print("\n⚠️ Some imports failed. Check the output above for details.")
