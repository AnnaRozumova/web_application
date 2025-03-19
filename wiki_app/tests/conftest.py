import pytest
from wiki_app import wiki_app

@pytest.fixture
def test_client():
    """Fixture to create a test client for the Flask app."""
    wiki_app.app.config["TESTING"] = True
    return wiki_app.app.test_client()
