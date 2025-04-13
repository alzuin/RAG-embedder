# test_main.py
import unittest
from unittest.mock import patch, MagicMock
import json
from main import handler, combine_fields

# Mock AWS Lambda context
class MockContext:
    def __init__(self):
        self.aws_request_id = "test-request-id"

class TestEmbeddingAPI(unittest.TestCase):
    def setUp(self):
        self.context = MockContext()

    def create_event(self, method, path, body=None, query_params=None):
        event = {
            "httpMethod": method,
            "path": path,
            "queryStringParameters": query_params
        }
        if body:
            event["body"] = json.dumps(body)
        return event

    def test_combine_fields(self):
        payload = {
            "id": "123",
            "title": "Test",
            "content": "Content",
            "author": "Author"
        }
        result = combine_fields(payload)
        self.assertEqual(result, "Test. Content. Author")

    @patch('main.get_embedding')
    @patch('main.store_to_qdrant')
    def test_create_document(self, mock_store, mock_embedding):
        # Setup mocks
        mock_embedding.return_value = [0.1, 0.2, 0.3]
        mock_store.return_value = {"status": "success"}

        # Test data
        test_doc = {
            "id": "doc123",
            "title": "Test Document",
            "content": "Test Content"
        }

        # Create test event
        event = self.create_event("POST", "/embedding-api", test_doc)

        # Execute request
        response = handler(event, self.context)

        # Assertions
        self.assertEqual(response["statusCode"], 201)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["id"], "doc123")
        mock_embedding.assert_called_once()
        mock_store.assert_called_once()

    @patch('main.get_embedding')
    @patch('main.search_qdrant')
    def test_search_documents(self, mock_search, mock_embedding):
        # Setup mocks
        mock_embedding.return_value = [0.1, 0.2, 0.3]
        mock_search.return_value = [{"id": "doc123", "score": 0.95}]

        # Create test event
        event = self.create_event(
            "GET",
            "/embedding-api",
            query_params={"query": "test search"}
        )

        # Execute request
        response = handler(event, self.context)

        # Assertions
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertIn("result", response_body)
        mock_embedding.assert_called_once()
        mock_search.assert_called_once()

    @patch('main.get_embedding')
    @patch('main.store_to_qdrant')
    def test_update_document(self, mock_store, mock_embedding):
        # Setup mocks
        mock_embedding.return_value = [0.1, 0.2, 0.3]
        mock_store.return_value = {"status": "success"}

        # Test data
        test_doc = {
            "title": "Updated Document",
            "content": "Updated Content"
        }

        # Create test event
        event = self.create_event(
            "PUT",
            "/embedding-api/doc123",
            test_doc
        )

        # Execute request
        response = handler(event, self.context)

        # Assertions
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertTrue(response_body["updated"])
        self.assertEqual(response_body["id"], "doc123")
        mock_embedding.assert_called_once()
        mock_store.assert_called_once()

    @patch('main.delete_from_qdrant')
    def test_delete_document(self, mock_delete):
        # Setup mock
        mock_delete.return_value = {"status": "success"}

        # Create test event
        event = self.create_event("DELETE", "/embedding-api/doc123")

        # Execute request
        response = handler(event, self.context)

        # Assertions
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertIn("result", response_body)
        mock_delete.assert_called_once_with("doc123")

    def test_invalid_route(self):
        event = self.create_event("GET", "/invalid-route")
        response = handler(event, self.context)
        self.assertEqual(response["statusCode"], 404)

    def test_missing_query_parameter(self):
        event = self.create_event("GET", "/embedding-api")
        response = handler(event, self.context)
        self.assertEqual(response["statusCode"], 400)

    def test_missing_id_in_delete(self):
        event = self.create_event("DELETE", "/embedding-api/")
        response = handler(event, self.context)
        self.assertEqual(response["statusCode"], 400)

if __name__ == '__main__':
    unittest.main()
