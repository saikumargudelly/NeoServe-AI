import sys
import os
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/test-import")
async def test_import():
    try:
        # Try to import the module
        from google.cloud import discoveryengine
        
        # If successful, try to create a client
        try:
            client = discoveryengine.SearchServiceClient()
            return {
                "status": "success",
                "message": "Successfully imported discoveryengine and created client",
                "client_type": str(type(client)),
                "module_location": discoveryengine.__file__
            }
        except Exception as e:
            return {
                "status": "partial_success",
                "message": f"Imported but failed to create client: {str(e)}",
                "module_location": discoveryengine.__file__
            }
    except ImportError as e:
        return {
            "status": "error",
            "message": f"Failed to import discoveryengine: {str(e)}",
            "python_path": sys.path,
            "env_vars": {k: v for k, v in os.environ.items() if 'python' in k.lower() or 'path' in k.lower()}
        }

if __name__ == "__main__":
    print("Starting test server...")
    print(f"Python path: {sys.path}")
    print(f"Environment variables: {os.environ.get('PYTHONPATH', 'Not set')}")
    
    # Try to import the module directly
    try:
        from google.cloud import discoveryengine
        print(f"✅ Successfully imported discoveryengine from {discoveryengine.__file__}")
    except ImportError as e:
        print(f"❌ Failed to import discoveryengine: {e}")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
