"""
It is a module which make a simple test of main.py from main_app directory
"""
import smtplib
import io
import requests
from flask_mail import Message
from main_app.main import mail, WEBCAMERA_APP_URL

def test_send_email_success(flask_test_client, monkeypatch):
    """Test successful email sending by mocking Flask-Mail"""

    monkeypatch.setenv('MAIL_USERNAME', 'test@example.com')

    sent_messages = []

    def mock_send(msg):
        """Mock send function to simulate email sending"""
        sent_messages.append(msg)

    monkeypatch.setattr(mail, 'send', mock_send)

    data = {
        'name': 'Test User',
        'email': 'user@example.com',
        'message': 'This is a test message.'
    }

    response = flask_test_client.post('/send-email', data=data)

    assert response.status_code == 200
    assert response.json == {'success': 'Email sent successfully!'}

    assert len(sent_messages) == 1

    email: Message = sent_messages[0]
    assert email.subject == "New Contact Form Submission from Test User"
    assert email.sender == "user@example.com"
    assert email.recipients == ["test@example.com"]
    assert "This is a test message." in email.body


def test_send_email_failure(flask_test_client, monkeypatch):
    """Test email sending failure due to an exception"""

    monkeypatch.setenv('MAIL_USERNAME', 'test@example.com')
    def mock_failed_email_send(msg):
        """Mock function to simulate email sendinf failure"""
        raise smtplib.SMTPException("SMTP Error: Unable to send email")

    monkeypatch.setattr(mail, 'send', mock_failed_email_send)

    data = {
        'name': 'Test User',
        'email': 'user@example.com',
        'message': 'This is a test message.'
    }

    response = flask_test_client.post('/send-email', data=data)

    assert response.status_code == 500
    assert 'error' in response.json
    assert "SMTP Error: Unable to send email" in response.json['error']


def test_send_email_missing_fields(flask_test_client):
    """Test email sending fails due to missing required fields"""

    data = {'name': 'User'}

    response = flask_test_client.post('/send-email', data=data)

    assert response.status_code == 400
    assert response.json == {'error': 'Missing form fields'}

def test_get_webcamera_pic(flask_test_client):
    """Test if the WebCamera app page renders correctly"""
    response = flask_test_client.get('/webcamera-app')

    assert response.status_code == 200
    assert b'WEBCAMERA_APP_URL' in response.data

def test_upload_photo_success(flask_test_client, monkeypatch, mock_response):
    """Test successful image upload and forwarding to the WebCamera service"""

    def mock_post(url, files, timeout):
        """Mock function to simulate a successful request to WebCamera service"""
        assert url == f"{WEBCAMERA_APP_URL}/upload"
        assert 'image' in files
        return mock_response({'success': 'Image uploaded'}, 200)

    monkeypatch.setattr(requests, "post", mock_post)

    fake_image = (io.BytesIO(b"fake_image_data"), "test.jpg")

    response = flask_test_client.post('/upload', data={'image': fake_image}, content_type='multipart/form-data')

    assert response.status_code == 200
    assert response.json == {'success': 'Image uploaded'}


def test_upload_photo_no_file(flask_test_client):
    """Test upload failure when no image file is provided"""

    response = flask_test_client.post('/upload', data={})

    assert response.status_code == 400
    assert response.json == {'error': 'No image file provided'}


def test_upload_photo_service_unavailable(flask_test_client, monkeypatch):
    """Test upload failure when the WebCamera service is unavailable"""

    def mock_post(*args, **kwargs):
        raise requests.exceptions.RequestException("Service Unavailable")

    monkeypatch.setattr(requests, "post", mock_post)

    fake_image = (io.BytesIO(b"fake_image_data"), "test.jpg")

    response = flask_test_client.post('/upload', data={'image': fake_image}, content_type='multipart/form-data')

    assert response.status_code == 500
    assert "Webcamera service unavailable" in response.json['error']

def test_download_photo_success(flask_test_client, monkeypatch, mock_response):
    """Test successful image download with redirection"""

    def mock_get(_url, timeout):
        return mock_response({'url': 'https://example.com/test.jpg'}, 200)

    monkeypatch.setattr(requests, "get", mock_get)

    response = flask_test_client.get('/download/test.jpg')

    assert response.status_code == 302
    assert response.location == "https://example.com/test.jpg"


def test_download_photo_not_found(flask_test_client, monkeypatch, mock_response):
    """Test failure when trying to download a missing file"""

    def mock_get(_url, timeout):
        return mock_response({}, 404)

    monkeypatch.setattr(requests, "get", mock_get)

    response = flask_test_client.get('/download/missing.jpg')

    assert response.status_code == 200
    assert response.json == {'error': 'File not found or already deleted.'}

def test_wiki_app_get(flask_test_client):
    """Test if the Wiki app page renders correctly"""
    response = flask_test_client.get('/wiki-app')

    assert response.status_code == 200
    assert b'<title>Wikipedia Article Fetcher</title>' in response.data

def test_wiki_app_post_success(flask_test_client, monkeypatch, mock_response):
    """Test successful Wikipedia search (POST request)."""

    def mock_post(_url, json, timeout):
        """Mock Wikipedia API returning a successful search result."""
        assert json == {'query': 'Python'}
        return mock_response({
            'title': 'Python (programming language)',
            'summary': 'Python is an interpreted, high-level, general-purpose programming language.',
            'url': 'https://en.wikipedia.org/wiki/Python_(programming_language)',
            'main_image': 'https://example.com/python.jpg'
        }, 200)

    monkeypatch.setattr(requests, "post", mock_post)

    response = flask_test_client.post('/wiki-app', data={'query': 'Python'})

    assert response.status_code == 200
    assert b'Python (programming language)' in response.data
    assert b'Python is an interpreted, high-level, general-purpose programming language.' in response.data
    assert b'https://en.wikipedia.org/wiki/Python_(programming_language)' in response.data
    assert b'https://example.com/python.jpg' in response.data


def test_wiki_app_post_not_found(flask_test_client, monkeypatch, mock_response):
    """Test Wikipedia search returning 404 (article not found)."""

    def mock_post(_url, json, timeout):
        return mock_response({'error': 'Article not found.'}, 404)

    monkeypatch.setattr(requests, "post", mock_post)

    response = flask_test_client.post('/wiki-app', data={'query': 'Nonexistent'})

    assert response.status_code == 200
    assert b'Article not found.' in response.data


def test_wiki_app_post_service_error(flask_test_client, monkeypatch):
    """Test Wikipedia search service failure (500 or timeout)."""

    def mock_post(_url, json, timeout):
        raise requests.exceptions.RequestException("Service unavailable")

    monkeypatch.setattr(requests, "post", mock_post)

    response = flask_test_client.post('/wiki-app', data={'query': 'Python'})

    assert response.status_code == 200
    assert b'Wikipedia service is currently unavailable.' in response.data

def test_db_app(flask_test_client):
    """Test if the DB app page renders correctly"""
    response = flask_test_client.get('/db-app')

    assert response.status_code == 200

def test_list_all_customers_success(flask_test_client, monkeypatch, mock_response):
    """Test successful retrieval of all customers."""

    def mock_get(_url, timeout):
        """Mock function simulating a successful DB API call."""
        return mock_response([
            {"email": "alice@example.com", "name": "Alice", "surname": "White"},
            {"email": "bob@example.com", "name": "Bob", "surname": "Black"}
        ], 200)

    monkeypatch.setattr(requests, "get", mock_get)

    response = flask_test_client.get('/all-customers')

    assert response.status_code == 200
    assert response.json == [
        {"email": "alice@example.com", "name": "Alice", "surname": "White"},
        {"email": "bob@example.com", "name": "Bob", "surname": "Black"}
    ]

def test_list_all_customers_service_error(flask_test_client, monkeypatch):
    """Test handling when database service is unavailable."""

    def mock_get(_url, timeout):
        raise requests.exceptions.RequestException("Database service unavailable")

    monkeypatch.setattr(requests, "get", mock_get)

    response = flask_test_client.get('/all-customers')

    assert response.status_code == 500
    assert b'Database service unavailable' in response.data

def test_list_all_products_success(flask_test_client, monkeypatch, mock_response):
    """Test successful retrieval of all products."""

    def mock_get(_url, timeout):
        """Mock function simulating a successful DB API call."""
        return mock_response([
            {'product_name': 'Spiced Latte', 'available_amount': '18', 'price': '265'},
            {'product_name': 'Espresso Shot', 'available_amount': '45', 'price': '315'}
        ], 200)

    monkeypatch.setattr(requests, "get", mock_get)

    response = flask_test_client.get('/all-products')

    assert response.status_code == 200
    assert response.json == [
        {'product_name': 'Spiced Latte', 'available_amount': '18', 'price': '265'},
        {'product_name': 'Espresso Shot', 'available_amount': '45', 'price': '315'}
    ]


def test_list_all_products_service_error(flask_test_client, monkeypatch):
    """Test handling when database service is unavailable."""

    def mock_get(_url, timeout):
        raise requests.exceptions.RequestException("Database service unavailable")

    monkeypatch.setattr(requests, "get", mock_get)

    response = flask_test_client.get('/all-products')

    assert response.status_code == 500
    assert response.json == {'error': 'Database service unavailable'}

def test_list_all_purchases_success(flask_test_client, monkeypatch, mock_response):
    """Test successful retrieval of all purchases."""

    def mock_get(_url, timeout):
        """Mock function simulating a successful DB API call."""
        return mock_response([
            {'customer_email': 'cash@gmail.com', 'purchase_id': '12345'},
            {'customer_email': 'smith@gmail.com', 'purchase_id': '98765'}
        ], 200)

    monkeypatch.setattr(requests, "get", mock_get)

    response = flask_test_client.get('/all-purchases')

    assert response.status_code == 200
    assert response.json == [
        {'customer_email': 'cash@gmail.com', 'purchase_id': '12345'},
        {'customer_email': 'smith@gmail.com', 'purchase_id': '98765'}
    ]


def test_list_all_purchases_service_error(flask_test_client, monkeypatch):
    """Test handling when database service is unavailable."""

    def mock_get(_url, timeout):
        raise requests.exceptions.RequestException("Database service unavailable")

    monkeypatch.setattr(requests, "get", mock_get)

    response = flask_test_client.get('/all-purchases')

    assert response.status_code == 500
    assert response.json == {'error': 'Database service unavailable'}

def test_total_price_all_purchases_success(flask_test_client, monkeypatch, mock_response):
    """Test successful calculation of total price for all purchases."""

    def mock_get(_url, timeout):
        """Mock function simulating a successful DB API call."""
        return mock_response([
            {'customer_email': 'cash@gmail.com', 'purchase_id': '12345', "total_price": "999.99"},
            {'customer_email': 'smith@gmail.com', 'purchase_id': '98765', "total_price": "499.50"},
            {'customer_email': 'charles@gmail.com', 'purchase_id': '34567', "total_price": "250.51"}
        ], 200)

    monkeypatch.setattr(requests, "get", mock_get)

    response = flask_test_client.get('/all-purchases-price')

    assert response.status_code == 200
    assert response.json == {"total_price": 1750.0}


def test_total_price_all_purchases_service_error(flask_test_client, monkeypatch):
    """Test handling when database service is unavailable."""

    def mock_get(_url, timeout):
        raise requests.exceptions.RequestException("Database service unavailable")

    monkeypatch.setattr(requests, "get", mock_get)

    response = flask_test_client.get('/all-purchases-price')

    assert response.status_code == 500
    assert 'error' in response.json
    assert response.json['error'] == "Database service unavailable"

def test_add_product_get_success(flask_test_client, monkeypatch, mock_response):
    """Test successful retrieval of product details (GET request)."""

    def mock_get(_url, params, timeout):
        """Mock function simulating a successful product lookup."""
        assert params == {"product_name": "Spiced Latte"}
        return mock_response({"available_amount": "18", "price": "265"}, 200)

    monkeypatch.setattr(requests, "get", mock_get)

    response = flask_test_client.get('/add-product', query_string={"product_name": "Spiced Latte"})

    assert response.status_code == 200
    assert response.json == {"available_amount": "18", "price": "265"}


def test_add_product_get_missing_name(flask_test_client):
    """Test GET request failure when no product name is provided."""

    response = flask_test_client.get('/add-product')

    assert response.status_code == 400
    assert response.json == {"error": "Product name is required"}


def test_add_product_get_service_error(flask_test_client, monkeypatch):
    """Test handling when database service is unavailable during GET request."""

    def mock_get(_url, params, timeout):
        raise requests.exceptions.RequestException("Database service unavailable")

    monkeypatch.setattr(requests, "get", mock_get)

    response = flask_test_client.get('/add-product', query_string={"product_name": "Spiced Latte"})

    assert response.status_code == 500
    assert "error" in response.json
    assert response.json["error"] == "Database service unavailable"


def test_add_product_post_success(flask_test_client, monkeypatch, mock_response):
    """Test successful product addition (POST request)."""

    def mock_post(_url, json, timeout):
        """Mock function simulating a successful product addition."""
        assert json == {
            'product_name': 'Spiced Latte',
            'price': 265,
            'available_amount': '18'
        }
        return mock_response({"message": "Product added successfully"}, 201)

    monkeypatch.setattr(requests, "post", mock_post)

    response = flask_test_client.post('/add-product', json={'product_name': 'Spiced Latte', 'price': 265, 'available_amount': '18'})

    assert response.status_code == 201
    assert response.json == {"message": "Product added successfully"}


def test_add_product_post_service_error(flask_test_client, monkeypatch):
    """Test handling when database service is unavailable during POST request."""

    def mock_post(_url, json, timeout):
        raise requests.exceptions.RequestException("Database service unavailable")

    monkeypatch.setattr(requests, "post", mock_post)

    response = flask_test_client.post('/add-product', json={'product_name': 'Spiced Latte', 'price': '265'})

    assert response.status_code == 500
    assert "error" in response.json
    assert response.json["error"] == "Database service unavailable"

def test_search_customers_success(flask_test_client, monkeypatch, mock_response):
    """Test successful customer search (GET request)."""

    def mock_get(_url, params, timeout):
        """Mock function simulating a successful customer search."""
        assert dict(params) == {"name": "Alice"}
        return mock_response([
            {"email": "alice@example.com", "name": "Alice", "surname": "White"}
        ], 200)

    monkeypatch.setattr(requests, "get", mock_get)

    response = flask_test_client.get('/search-customers', query_string={"name": "Alice"})

    assert response.status_code == 200
    assert response.json == [
        {"email": "alice@example.com", "name": "Alice", "surname": "White"}
    ]


def test_search_customers_no_results(flask_test_client, monkeypatch, mock_response):
    """Test customer search returning no results (empty list)."""

    def mock_get(_url, params, timeout):
        return mock_response([], 200)

    monkeypatch.setattr(requests, "get", mock_get)

    response = flask_test_client.get('/search-customers', query_string={"name": "Unknown"})

    assert response.status_code == 200
    assert response.json == []


def test_search_customers_service_error(flask_test_client, monkeypatch):
    """Test handling when database service is unavailable during search."""

    def mock_get(_url, params, timeout):
        raise requests.exceptions.RequestException("Database service unavailable")

    monkeypatch.setattr(requests, "get", mock_get)

    response = flask_test_client.get('/search-customers', query_string={"name": "Alice"})

    assert response.status_code == 500
    assert "error" in response.json
    assert "Database service unavailable" in response.json["error"]

def test_add_customer_success(flask_test_client, monkeypatch, mock_response):
    """Test successful customer addition (POST request)."""

    def mock_post(_url, json, timeout):
        """Mock function simulating a successful customer addition."""
        assert json == {"name": "Alice", "email": "alice@example.com"}
        return mock_response({"message": "Customer added successfully"}, 201)

    monkeypatch.setattr(requests, "post", mock_post)

    response = flask_test_client.post('/add-customer', json={"name": "Alice", "email": "alice@example.com"})

    assert response.status_code == 201
    assert response.json == {"message": "Customer added successfully"}


def test_add_customer_service_error(flask_test_client, monkeypatch):
    """Test handling when database service is unavailable during customer addition."""

    def mock_post(_url, json, timeout):
        raise requests.exceptions.RequestException("Database service unavailable")

    monkeypatch.setattr(requests, "post", mock_post)

    response = flask_test_client.post('/add-customer', json={"name": "Alice", "email": "alice@example.com"})

    assert response.status_code == 500
    assert "error" in response.json
    assert response.json["error"] == "Database service unavailable"

def test_make_purchase_success(flask_test_client, monkeypatch, mock_response):
    """Test successful purchase transaction (POST request)."""

    def mock_post(_url, json, timeout):
        """Mock function simulating a successful purchase transaction."""
        assert json == {
            "customer_email": "john.doe@example.com",
            "product_name": "Spiced Latte",
            "amount_to_purchase": 2
        }
        return mock_response({"message": "Purchase completed successfully"}, 201)

    monkeypatch.setattr(requests, "post", mock_post)

    response = flask_test_client.post('/make-purchase', json={
        "customer_email": "john.doe@example.com",
        "product_name": "Spiced Latte",
        "amount_to_purchase": 2})

    assert response.status_code == 201
    assert response.json == {"message": "Purchase completed successfully"}


def test_make_purchase_service_error(flask_test_client, monkeypatch):
    """Test handling when database service is unavailable during purchase transaction."""

    def mock_post(_url, json, timeout):
        raise requests.exceptions.RequestException("Database service unavailable")

    monkeypatch.setattr(requests, "post", mock_post)

    response = flask_test_client.post('/make-purchase', json={
        "customer_email": "john.doe@example.com",
        "product_name": "Spiced Latte",
        "amount_to_purchase": 2
    })

    assert response.status_code == 500
    assert "error" in response.json
    assert response.json["error"] == "Database service unavailable"