"""
Test module for Vertex AI operations.
Verifies integration with Google's Vertex AI services including model loading and text generation.
"""
import os
import unittest
from unittest.mock import patch, MagicMock
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestVertexAIOperations(unittest.TestCase):
    """Test case for Vertex AI operations."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests are run."""
        cls.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        cls.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        
        if not cls.project_id:
            pytest.skip("GOOGLE_CLOUD_PROJECT environment variable not set")

    def setUp(self):
        """Set up test fixtures before each test method is called."""
        from neoserve_ai.agents.google_imports import vertexai, GenerativeModel, aiplatform
        self.vertexai = vertexai
        self.GenerativeModel = GenerativeModel
        self.aiplatform = aiplatform

    def test_vertex_ai_initialization(self):
        """Test that Vertex AI is properly initialized."""
        self.assertIsNotNone(self.vertexai)
        self.assertIsNotNone(self.GenerativeModel)
        self.assertIsNotNone(self.aiplatform)

    @patch('vertexai.preview.generative_models.GenerativeModel.generate_content')
    def test_text_generation(self, mock_generate):
        """Test text generation with a mock response."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.text = "This is a test response from Vertex AI"
        mock_generate.return_value = mock_response

        # Test the generation
        model = self.GenerativeModel("gemini-pro")
        response = model.generate_content("Hello, Vertex AI!")
        
        self.assertEqual(response.text, "This is a test response from Vertex AI")
        mock_generate.assert_called_once()

    def test_list_models(self):
        """Test listing available Vertex AI models."""
        from google.cloud import aiplatform_v1
        
        client = aiplatform_v1.ModelServiceClient(
            client_options={"api_endpoint": f"{self.location}-aiplatform.googleapis.com"}
        )
        
        parent = f"projects/{self.project_id}/locations/{self.location}"
        
        try:
            models = list(client.list_models(parent=parent))
            self.assertIsInstance(models, list)
            self.logger.info(f"Found {len(models)} models in project {self.project_id}")
        except Exception as e:
            self.fail(f"Failed to list models: {str(e)}")

    @patch('google.cloud.aiplatform.gapic.PredictionServiceClient.predict')
    def test_prediction_endpoint(self, mock_predict):
        """Test prediction endpoint with mock."""
        # Mock the prediction response
        mock_response = MagicMock()
        mock_response.predictions = [{
            'content': 'Test response content',
            'safety_attributes': {},
            'citation_metadata': {}
        }]
        mock_predict.return_value = mock_response

        from google.cloud import aiplatform_v1
        from google.cloud.aiplatform_v1.types import prediction_service
        
        client = aiplatform_v1.PredictionServiceClient(
            client_options={"api_endpoint": f"{self.location}-aiplatform.googleapis.com"}
        )
        
        endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/text-bison@001"
        
        try:
            response = client.predict(
                endpoint=endpoint,
                instances=[{"prompt": "Test prompt"}],
                parameters={
                    "temperature": 0.2,
                    "maxOutputTokens": 256,
                    "topP": 0.8,
                    "topK": 40
                }
            )
            self.assertIsNotNone(response)
            self.assertTrue(hasattr(response, 'predictions'))
        except Exception as e:
            self.fail(f"Prediction failed: {str(e)}")

if __name__ == "__main__":
    unittest.main()
