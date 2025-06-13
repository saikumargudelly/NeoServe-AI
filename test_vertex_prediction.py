import os
from google.cloud import aiplatform
from google.oauth2 import service_account

def test_vertex_prediction():
    try:
        # Load service account key
        key_path = "./config/service-account-key.json"
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
        
        print("Testing text generation with Vertex AI...")
        
        # Try to use the text-bison model
        from vertexai.preview.language_models import TextGenerationModel
        
        model = TextGenerationModel.from_pretrained("text-bison@001")
        response = model.predict(
            "Tell me a fun fact about artificial intelligence:",
            temperature=0.2,
            max_output_tokens=100,
            top_p=0.8,
            top_k=40
        )
        
        print("\nResponse from Vertex AI:")
        print(response.text)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nNote: Make sure the service account has the 'Vertex AI User' role")
        print("and the necessary APIs are enabled in your Google Cloud project.")

if __name__ == "__main__":
    test_vertex_prediction()
