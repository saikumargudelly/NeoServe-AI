import sys
import importlib

def check_import(module_name):
    try:
        module = importlib.import_module(module_name)
        print(f"✅ Successfully imported {module_name}")
        print(f"   Location: {getattr(module, '__file__', 'Unknown')}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_name}")
        print(f"   Error: {e}")
        return False

print("Python sys.path:")
for path in sys.path:
    print(f" - {path}")

print("\nChecking imports:")
check_import("google.cloud.discoveryengine")

# Try to import the module directly
print("\nTrying direct import:")
try:
    from google.cloud import discoveryengine
    print("✅ Direct import successful")
    print(f"   discoveryengine location: {discoveryengine.__file__}")
except Exception as e:
    print(f"❌ Direct import failed: {e}")

# Check if the module is in the namespace
print("\nChecking module in sys.modules:")
if 'google.cloud.discoveryengine' in sys.modules:
    print("✅ Module found in sys.modules")
    print(f"   Location: {sys.modules['google.cloud.discoveryengine'].__file__}")
else:
    print("❌ Module not found in sys.modules")

# Try importing a specific submodule
print("\nTrying to import a submodule:")
try:
    from google.cloud.discoveryengine_v1 import DocumentServiceClient
    print("✅ Successfully imported DocumentServiceClient from discoveryengine_v1")
except Exception as e:
    print(f"❌ Failed to import DocumentServiceClient: {e}")
