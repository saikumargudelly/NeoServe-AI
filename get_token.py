from google.oauth2 import service_account
from google.auth.transport.requests import Request
import requests
import json

# Path to your service account key file
SERVICE_ACCOUNT_FILE = './config/service-account-key.json'

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

try:
    # Create credentials object
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    # Refresh the token
    credentials.refresh(Request())
    
    # Get the access token
    access_token = credentials.token
    if access_token:
        print(access_token)
    else:
        print("Error: Failed to get access token")
        exit(1)
        
except Exception as e:
    print(f"Error: {str(e)}")
    exit(1)
