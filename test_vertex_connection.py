import os
import json
from google.cloud import aiplatform
from google.oauth2 import service_account

# Load service account key
key_path = "./config/service-account-key.json"

if not os.path.exists(key_path):
    print(f"Error: Service account key file not found at {key_path}")
    exit(1)

try:
    # Initialize the Vertex AI client
    credentials = service_account.Credentials.from_service_account_file(
        key_path,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    
    # Initialize Vertex AI
    aiplatform.init(
        project="neoserve-ai",
        location="us-central1",
        credentials=credentials
    )
    
    print("Successfully connected to Vertex AI!")
    print("Available models:")
    
    # List available models (this is a simple test - actual implementation may vary)
    try:
        models = aiplatform.Model.list()
        for model in models:
            print(f"- {model.display_name} (ID: {model.name})")
    except Exception as e:
        print(f"Could not list models, but connection was successful. Error: {str(e)}")
        print("This might be due to missing permissions or no models deployed.")
    
except Exception as e:
    print(f"Error connecting to Vertex AI: {str(e)}")
    print("Please verify your service account key and project configuration.")
