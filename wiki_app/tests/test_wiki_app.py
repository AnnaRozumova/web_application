"""This module tests wiki_app functionality."""
from unittest.mock import patch

def test_valid_wikipedia_query(test_client):
    """Test querying a valid Wikipedia page."""
    query = "Python (programming language)"

    with patch("wikipediaapi.Wikipedia.page") as mock_page, \
         patch("requests.get") as mock_requests:

        mock_page.return_value.exists.return_value = True
        mock_page.return_value.title = query
        mock_page.return_value.summary = "Python is a programming language..."
        mock_page.return_value.fullurl = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"

        mock_requests.return_value.status_code = 200
        mock_requests.return_value.json.return_value = {
            "thumbnail": {"source": "https://example.com/image.jpg"}
        }

        response = test_client.post("/query", json={"query": query})
        assert response.status_code == 200
        data = response.get_json()

        assert data["title"] == query
        assert "Python is a programming language" in data["summary"]
        assert data["url"] == f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
        assert data["main_image"] == "https://example.com/image.jpg"

def test_non_existent_wikipedia_page(test_client):
    """Test querying a Wikipedia page that does not exist."""
    query = "ThisPageDoesNotExist"

    with patch("wikipediaapi.Wikipedia.page") as mock_page:
        mock_page.return_value.exists.return_value = False

        response = test_client.post("/query", json={"query": query})
        assert response.status_code == 200
        data = response.get_json()

        assert "error" in data
        assert data["error"] == f"No article found for '{query}'"

def test_empty_query(test_client):
    """Test querying with an empty string."""
    response = test_client.post("/query", json={})
    assert response.status_code == 200
    data = response.get_json()

    assert "error" in data
    assert data["error"] == "No query provided"

def test_wikipedia_api_failure(test_client):
    """Simulate a failure in the Wikipedia API."""
    query = "Python (programming language)"

    with patch("wikipediaapi.Wikipedia.page", side_effect=Exception("Wikipedia API error")):
        response = test_client.post("/query", json={"query": query})

        assert "error" in response.json
        assert "Internal Server Error: Wikipedia API error" in response.json["error"]

def test_image_fetch_failure(test_client):
    """Simulate a failure in fetching the article image."""
    query = "Python (programming language)"

    with patch("wikipediaapi.Wikipedia.page") as mock_page, \
         patch("requests.get") as mock_requests:

        mock_page.return_value.exists.return_value = True
        mock_page.return_value.title = query
        mock_page.return_value.summary = "Python is a programming language..."
        mock_page.return_value.fullurl = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"

        mock_requests.return_value.status_code = 500

        response = test_client.post("/query", json={"query": query})
        assert response.status_code == 200
        data = response.get_json()

        assert data["title"] == query
        assert "Python is a programming language" in data["summary"]
        assert data["main_image"] is None
