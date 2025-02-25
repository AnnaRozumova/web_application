import pytest

def test_add_client(test_client):
    '''Test adding a client to database'''
    data = {
        "name": "John",
        "surname": "Doe",
        "email": "johndoe@example.com",
        "shipping_address": "123 Street, City",
        "products": ["Headphones"]
    }
    
    response = test_client.post('/add-client', json=data)
    json_data = response.get_json()

    assert response.status_code == 201
    assert "Client added successfully" in json_data["message"]


def test_update_client(test_client):
    '''Test updating a client in database.'''
    
    response = test_client.post('/add-client', json=data)
    json_data = response.get_json()

    assert response.status_code == 201
    assert "Client added successfully" in json_data["message"]