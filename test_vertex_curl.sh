#!/bin/bash

# Get the access token
TOKEN=$(python get_token.py)

# Set your project and location
PROJECT_ID="neoserve-ai"
LOCATION="us-central1"
MODEL_ID="text-bison@001"

# Define the API endpoint
ENDPOINT="https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/${MODEL_ID}:predict"

# Create a temporary JSON file with the request payload
cat > /tmp/request.json << 'EOL'
{
  "instances": [
    {
      "prompt": "Tell me a fun fact about artificial intelligence:"
    }
  ],
  "parameters": {
    "temperature": 0.2,
    "maxOutputTokens": 100,
    "topP": 0.8,
    "topK": 40
  }
}
EOL

# Make the API request
echo "Making request to Vertex AI API..."
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @/tmp/request.json \
  $ENDPOINT

# Clean up
rm /tmp/request.json
