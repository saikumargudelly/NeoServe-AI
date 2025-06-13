import sys
import os
import importlib.util

def check_module(module_name):
    try:
        module = importlib.import_module(module_name)
        return True, module.__file__
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def main():
    print("="*80)
    print("Python Environment Information")
    print("="*80)
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print(f"Python Path:")
    for path in sys.path:
        print(f"  {path}")
    
    print("\n" + "="*80)
    print("Module Import Tests")
    print("="*80)
    
    # Test google.cloud.discoveryengine
    print("\n1. Testing 'google.cloud.discoveryengine':")
    success, result = check_module('google.cloud.discoveryengine')
    if success:
        print(f"✅ Successfully imported google.cloud.discoveryengine")
        print(f"   Location: {result}")
    else:
        print(f"❌ Failed to import google.cloud.discoveryengine")
        print(f"   Error: {result}")
    
    # Test google.cloud (parent module)
    print("\n2. Testing 'google.cloud':")
    success, result = check_module('google.cloud')
    if success:
        print(f"✅ Successfully imported google.cloud")
        print(f"   Location: {result}")
        
        # List contents of google.cloud
        try:
            import google.cloud
            print("   Available submodules in google.cloud:")
            for name in dir(google.cloud):
                if not name.startswith('_'):
                    print(f"     - {name}")
        except Exception as e:
            print(f"   Could not list google.cloud contents: {e}")
    else:
        print(f"❌ Failed to import google.cloud")
        print(f"   Error: {result}")
    
    # Check if the module is in the expected location
    print("\n3. Checking module installation:")
    expected_path = "/Users/saikumargudelly/My Project/NeoServe AI/venv/lib/python3.12/site-packages/google/cloud/discoveryengine"
    if os.path.exists(expected_path):
        print(f"✅ Discovery Engine module found at: {expected_path}")
        print("   Contents:")
        try:
            for item in os.listdir(expected_path):
                print(f"     - {item}")
        except Exception as e:
            print(f"   Could not list directory contents: {e}")
    else:
        print(f"❌ Discovery Engine module not found at: {expected_path}")

if __name__ == "__main__":
    main()
