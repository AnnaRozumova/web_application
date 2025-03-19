import pytest
from main_app.main import app

@pytest.fixture
def flask_test_client():
    """Fixture to set up a Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class MockResponse:
    """Reusable Mock response for simulating requests responses"""
    def __init__(self, json_data=None, status_code=200):
        self.json_data = json_data or {}
        self.status_code = status_code

    def json(self):
        return self.json_data

@pytest.fixture
def mock_response():
    """Fixture that returns a reusable MockResponse class"""
    return MockResponse
