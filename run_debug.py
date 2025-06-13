import os
import sys
import importlib

def log_imports():
    print("="*80)
    print("Python Environment Information")
    print("="*80)
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print("\nPython Path:")
    for path in sys.path:
        print(f"  {path}")
    
    # Test importing google.cloud.discoveryengine
    print("\n" + "="*80)
    print("Importing google.cloud.discoveryengine")
    print("="*80)
    try:
        from google.cloud import discoveryengine
        print(f"✅ Successfully imported google.cloud.discoveryengine")
        print(f"   Location: {discoveryengine.__file__}")
    except ImportError as e:
        print(f"❌ Failed to import google.cloud.discoveryengine")
        print(f"   Error: {e}")
    
    # Start the FastAPI app
    print("\n" + "="*80)
    print("Starting FastAPI Application")
    print("="*80)
    from neoserve_ai.main import app
    import uvicorn
    
    uvicorn.run(
        "neoserve_ai.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )

if __name__ == "__main__":
    log_imports()
