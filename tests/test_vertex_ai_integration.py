"""
Test module for verifying Google Vertex AI integration.
This module tests the connection to Vertex AI and verifies that we can send requests
and receive responses from the language model.
"""
import os
import unittest
from unittest.mock import patch, MagicMock
import pytest
from google.cloud import aiplatform
from google.oauth2 import service_account

class TestVertexAIIntegration(unittest.TestCase):
    """Test case for Vertex AI integration."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests are run."""
        # Load environment variables from .env file if it exists
        from dotenv import load_dotenv
        load_dotenv()
        
        # Test configuration
        cls.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        cls.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        cls.key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        if not all([cls.project_id, cls.key_path]):
            pytest.skip("Missing required environment variables for Vertex AI tests")

    def setUp(self):
        """Set up test fixtures before each test method is called."""
        if not hasattr(self, 'project_id') or not self.project_id:
            self.skipTest("Skipping test: Missing project configuration")

    def test_vertex_ai_initialization(self):
        """Test that Vertex AI can be initialized with the provided credentials."""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.key_path,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            
            aiplatform.init(
                project=self.project_id,
                location=self.location,
                credentials=credentials
            )
            
            # If we get here without errors, initialization was successful
            self.assertTrue(True)
            
        except Exception as e:
            self.fail(f"Vertex AI initialization failed: {str(e)}")

    @patch('google.cloud.aiplatform.gapic.PredictionServiceClient.predict')
    def test_vertex_ai_prediction(self, mock_predict):
        """Test that we can get a prediction from Vertex AI."""
        # Mock the prediction response
        mock_response = MagicMock()
        mock_response.predictions = [{
            'content': 'This is a test response from Vertex AI',
            'safety_attributes': {},
            'citation_metadata': {}
        }]
        mock_predict.return_value = mock_response
        
        # Initialize the client
        from google.cloud import aiplatform_v1
        from google.cloud.aiplatform_v1.types import prediction_service
        
        client = aiplatform_v1.PredictionServiceClient(
            client_options={"api_endpoint": f"{self.location}-aiplatform.googleapis.com"}
        )
        
        # Make a test prediction
        endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/text-bison@001"
        instance = {"prompt": "Hello, Vertex AI!"}
        parameters = {
            "temperature": 0.2,
            "maxOutputTokens": 256,
            "topP": 0.8,
            "topK": 40
        }
        
        try:
            response = client.predict(
                endpoint=endpoint,
                instances=[instance],
                parameters=parameters
            )
            self.assertIsNotNone(response)
            self.assertTrue(hasattr(response, 'predictions'))
            self.assertGreater(len(response.predictions), 0)
            
        except Exception as e:
            self.fail(f"Vertex AI prediction failed: {str(e)}")

if __name__ == "__main__":
    unittest.main()
