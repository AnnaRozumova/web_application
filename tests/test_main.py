"""
It is a module which make a simple test of main.py from main_app directory
"""
import unittest
from unittest.mock import patch
from main_app.main import app

class TestMainApp(unittest.TestCase):
    '''Create a class for testing'''
    def setUp(self):
        ''' Create a test client'''
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_home_route(self):
        '''Test redirect to home page'''
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Home', response.data)  # Assuming 'Home' is in home.html

    def test_get_webcamera_pic_route(self):
        '''Test redirect to app page'''
        response = self.client.get('/webcamera-app')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Screenshot', response.data)

    @patch('requests.post')
    def test_take_screenshot(self, mock_post):
        '''Mock the external API for the POST request'''
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "success"}       
        response = self.client.post('/take-screenshot')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "success"})

    @patch('requests.get')
    def test_download_file(self, mock_get):
        '''Mock the external API for the GET request'''
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"url": "http://example.com/test_image.jpg"}       
        response = self.client.get('/download/test_image.jpg')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "http://example.com/test_image.jpg")

    @patch('requests.get')
    def test_uploaded_file(self, mock_get):
        '''Mock the external API for the GET request'''
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"url": "http://example.com/test_image.jpg"}       
        response = self.client.get('/uploads/test_image.jpg')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "http://example.com/test_image.jpg")


    def test_wiki_app_get(self):
        ''' Test the GET request'''
        response = self.client.get('/wiki-app')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<form', response.data)

    @patch('requests.post')
    def test_wiki_app_post_success(self, mock_post):
        ''' Mock the external API response for a successful query'''
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'title': 'Python',
            'summary': 'Python is a programming language.',
            'url': 'http://example.com/python',
            'main_image': 'http://example.com/python_image.jpg'
        }
        # Simulate a POST request with form data
        response = self.client.post('/wiki-app', data={'query': 'Python'})
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Python', response.data)  # Check if the title is in the rendered HTML
        self.assertIn(b'Python is a programming language.', response.data)  # Check the summary
        self.assertIn(b'http://example.com/python', response.data)  # Check the URL

    @patch('requests.post')
    def test_wiki_app_post_not_found(self, mock_post):
        '''Mock the external API response for a 404 error'''
        mock_post.return_value.status_code = 404
        mock_post.return_value.json.return_value = {
            'error': 'Article not found.'
        }
        # Simulate a POST request with form data
        response = self.client.post('/wiki-app', data={'query': 'Unknown Query'})
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Article not found.', response.data)  # Check the error message in the rendered HTML

    @patch('requests.post')
    def test_wiki_app_post_error(self, mock_post):
        '''Mock the external API response for a server error'''
        mock_post.return_value.status_code = 500
        # Simulate a POST request with form data
        response = self.client.post('/wiki-app', data={'query': 'Python'})
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'An error occured while fetching data.', response.data)  # Check the generic error message

    def test_db_app_route(self):
        '''Test redirect to app page'''
        response = self.client.get('/db-app')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Search', response.data)


    @patch('requests.post')
    def test_add_client_success(self, mock_post):
        ''' Mock the external API response for adding a client'''
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"success": True, "message": "Client added successfully!"}

        # Simulate a POST request with form data
        client_data = {
            "name": "John",
            "surname": "Doe",
            "email": "john.doe@example.com",
            "shipping_address": "123 Main Street",
            "products": ["Product1", "Product2"]
        }
        response = self.client.post('/add-client', data=client_data)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"success": True, "message": "Client added successfully!"})

    @patch('requests.post')
    def test_add_client_failure(self, mock_post):
        '''Mock the external API response for adding a client failure'''
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {"success": False, "message": "Failed to add client."}

        # Simulate a POST request with form data
        client_data = {
            "name": "John",
            "surname": "Doe",
            "email": "invalid-email",
            "shipping_address": "123 Main Street",
            "products": ["Product1", "Product2"]
        }
        response = self.client.post('/add-client', data=client_data)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"success": False, "message": "Failed to add client."})

    @patch('requests.put')
    def test_update_client_success(self, mock_put):
        ''' Mock the external API response for updating a client'''
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = {"success": True, "message": "Client updated successfully!"}

        # Simulate a POST request with form data to update a client
        client_id = "123"
        update_data = {
            "name": "Jane",
            "surname": "Smith",
            "email": "jane.smith@example.com",
            "shipping_address": "456 Elm Street",
            "products": ["Product3"]
        }
        response = self.client.post(f'/update-client/{client_id}', data=update_data)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"success": True, "message": "Client updated successfully!"})

    @patch('requests.delete')
    def test_delete_client_success(self, mock_delete):
        '''Mock the external API response for deleting a client'''
        mock_delete.return_value.status_code = 200
        mock_delete.return_value.json.return_value = {"success": True, "message": "Client deleted successfully!"}

        # Simulate a DELETE request to delete a client
        client_id = "123"
        response = self.client.delete(f'/delete-client/{client_id}')

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"success": True, "message": "Client deleted successfully!"})

    @patch('requests.get')
    def test_search_clients(self, mock_get):
        ''' Mock the external API response for searching clients'''
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {"name": "John", "surname": "Doe", "email": "john.doe@example.com"}
        ]

        # Simulate a GET request to search clients
        params = {"name": "John", "surname": "Doe", "product": "Product1"}
        response = self.client.get('/search-clients', query_string=params)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["name"], "John")


if __name__ == '__main__':
    unittest.main()
