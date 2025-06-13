import json
import requests
from google.oauth2 import service_account

# Load the service account key
SERVICE_ACCOUNT_FILE = "./config/service-account-key.json"
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

# Get credentials
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Get access token
access_token = credentials.token

# Vertex AI endpoint
PROJECT_ID = "neoserve-ai"
LOCATION = "us-central1"
MODEL_ID = "text-bison@001"
ENDPOINT = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL_ID}:predict"

# Headers
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Request payload
payload = {
    "instances": [
        {"prompt": "Tell me a fun fact about artificial intelligence:"}
    ],
    "parameters": {
        "temperature": 0.2,
        "maxOutputTokens": 100,
        "topP": 0.8,
        "topK": 40
    }
}

try:
    print("Sending request to Vertex AI API...")
    response = requests.post(ENDPOINT, headers=headers, json=payload)
    response.raise_for_status()
    print("\nResponse from Vertex AI:")
    print(json.dumps(response.json(), indent=2))
    
except requests.exceptions.HTTPError as err:
    print(f"\nHTTP Error: {err}")
    print(f"Status code: {response.status_code}")
    print("Response content:")
    print(response.text)
    
except Exception as e:
    print(f"\nAn error occurred: {str(e)}")
