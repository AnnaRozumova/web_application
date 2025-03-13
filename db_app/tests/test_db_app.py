import pytest

def test_list_all_customers(test_client, mock_dynamodb_setup):
    '''Test listing all customers from the table.'''

    customer_table = mock_dynamodb_setup.Table("customers")
    mock_customers = [
        {'email': 'cash@gmail.com', 'name': 'Jhony', 'surname': 'Cash'},
        {'email': 'smith@gmail.com', 'name': 'Leo', 'surname': 'Smith'},
        {'email': 'charles@gmail.com', 'name': 'Bob', 'surname': 'Charles'},
    ]
    for customer in mock_customers:
        customer_table.put_item(Item=customer)

    response = test_client.get('/all-customers')
    assert response.status_code == 200
    customers = response.get_json()

    assert isinstance(customers, list)
    assert len(customers) == len(mock_customers)
    returned_emails = {customer['email'] for customer in customers}
    expected_emails = {customer['email'] for customer in mock_customers}
    assert returned_emails == expected_emails


def test_list_all_products(test_client, mock_dynamodb_setup):
    '''Test listing all products from the table.'''

    product_table = mock_dynamodb_setup.Table("products")
    mock_products = [
        {'product_name': 'Spiced Latte', 'available_amount': '18', 'price': '265'},
        {'product_name': 'Espresso Shot', 'available_amount': '45', 'price': '315'},
        {'product_name': 'Morning Joy', 'available_amount': '20', 'price': '473'},
    ]
    for product in mock_products:
        product_table.put_item(Item=product)

    response = test_client.get('/all-products')
    assert response.status_code == 200
    products = response.get_json()

    assert isinstance(products, list)
    assert len(products) == len(mock_products)
    returned_names = {product['product_name'] for product in products}
    expected_names = {product['product_name'] for product in mock_products}
    assert returned_names == expected_names


def test_list_all_purchases(test_client, mock_dynamodb_setup):
    '''Test listing all purchases from the table.'''

    purchase_table = mock_dynamodb_setup.Table("purchases")
    mock_purchases = [
        {'customer_email': 'cash@gmail.com', 'purchase_id': '12345'},
        {'customer_email': 'smith@gmail.com', 'purchase_id': '98765'},
        {'customer_email': 'charles@gmail.com', 'purchase_id': '34567'}
    ]
    for purchase in mock_purchases:
        purchase_table.put_item(Item=purchase)

    response = test_client.get('/all-purchases')
    assert response.status_code == 200
    purchases = response.get_json()

    assert isinstance(purchases, list)
    assert len(purchases) == len(mock_purchases)
    returned_id = {purchase['purchase_id'] for purchase in purchases}
    expected_id = {purchase['purchase_id'] for purchase in mock_purchases}
    assert returned_id == expected_id


def test_add_product(test_client, mock_dynamodb_setup):
    '''Test adding and updating a product from the database.'''

    product_table = mock_dynamodb_setup.Table('products')

    new_product = {
        'product_name': 'Spiced Latte',
        'available_amount': '18',
        'price': '265'
    }
    post_response = test_client.post('/add-product', json=new_product)
    assert post_response.status_code == 201
    assert post_response.json["message"] == "Product added successfully"

    response = product_table.get_item(Key={"product_name": "Spiced Latte"})
    assert "Item" in response
    assert response["Item"]["price"] == 265
    assert response["Item"]["available_amount"] == 18

    get_response = test_client.get('/add-product', query_string={'product_name': 'Spiced Latte'})
    assert get_response.status_code == 200
    retrieved_product = get_response.json
    assert retrieved_product["product_name"] == "Spiced Latte"
    assert retrieved_product["price"] == '265'
    assert retrieved_product["available_amount"] == '18'

    update_data = {
        "product_name": "Spiced Latte",
        "price": '300',
        "available_amount": '5'
    }

    update_response = test_client.post('/add-product', json=update_data)
    assert update_response.status_code == 200
    assert update_response.json["message"] == "Product updated successfully"

    response = product_table.get_item(Key={"product_name": "Spiced Latte"})
    assert response["Item"]["price"] == 300
    assert response["Item"]["available_amount"] == 23

    non_existing_response = test_client.get('/add-product', query_string={"product_name": "Tablet"})
    assert non_existing_response.status_code == 404
    assert non_existing_response.json["message"] == "Product not found"

    invalid_post_response = test_client.post('/add-product', json={"product_name": "Tablet"})
    assert invalid_post_response.status_code == 400
    assert "error" in invalid_post_response.json

    invalid_format_response = test_client.post('/add-product', json={
        "product_name": "Tablet",
        "price": "invalid_price",
        "available_amount": "invalid_amount"
    })
    assert invalid_format_response.status_code == 400
    assert "error" in invalid_format_response.json
    assert invalid_format_response.json["error"] == "Price must be a number and Available Amount must be an integer"

def test_search_customers(test_client, mock_dynamodb_setup):
    """Test searching for customers by email, name, or surname."""
    customer_table = mock_dynamodb_setup.Table('customers')
    purchase_table = mock_dynamodb_setup.Table('purchases')

    mock_customers = [
        {"email": "alice@example.com", "name": "Alice", "surname": "Smith"},
        {"email": "bob@example.com", "name": "Bob", "surname": "Jones"},
        {"email": "charlie@example.com", "name": "Charlie", "surname": "Brown"}
    ]

    for customer in mock_customers:
        customer_table.put_item(Item=customer)

    purchase_table.put_item(Item={"customer_email": "alice@example.com", "purchase_id": "012345", "product": "Spiced Latte", "amount": 1})

    response = test_client.get('/search-customers', query_string={"email": "alice@example.com"})
    assert response.status_code == 200
    data = response.json
    assert "customers" in data
    assert len(data["customers"]) == 1
    assert data["customers"][0]["email"] == "alice@example.com"
    assert "purchases" in data["customers"][0]
    assert len(data["customers"][0]["purchases"]) == 1
    assert data["customers"][0]["purchases"][0]["product"] == "Spiced Latte"

    response = test_client.get('/search-customers', query_string={"name": "Alice"})
    assert response.status_code == 200
    data = response.json
    assert len(data["customers"]) == 1
    assert data["customers"][0]["name"] == "Alice"

    response = test_client.get('/search-customers', query_string={"surname": "Brown"})
    assert response.status_code == 200
    data = response.json
    assert len(data["customers"]) == 1
    assert data["customers"][0]["surname"] == "Brown"

    response = test_client.get('/search-customers', query_string={"name": "Bob", "surname": "Jones"})
    assert response.status_code == 200
    data = response.json
    assert len(data["customers"]) == 1
    assert data["customers"][0]["name"] == "Bob"
    assert data["customers"][0]["surname"] == "Jones"

    response = test_client.get('/search-customers', query_string={"email": "notfound@example.com"})
    assert response.status_code == 404
    assert response.json["error"] == "Customer not found"

    response = test_client.get('/search-customers')
    assert response.status_code == 404
    assert response.json["error"] == "Customer not found"

def test_add_customer(test_client, mock_dynamodb_setup):
    """Test adding a new customer to the database."""
    customer_table = mock_dynamodb_setup.Table('customers')

    new_customer = {
        "name": "John",
        "surname": "Doe",
        "email": "john.doe@example.com"
    }
    
    response = test_client.post('/add-customer', json=new_customer)
    assert response.status_code == 201
    data = response.json
    assert data["success"] is True
    assert data["customer"]["name"] == "John"
    assert data["customer"]["surname"] == "Doe"
    assert data["customer"]["email"] == "john.doe@example.com"

    db_response = customer_table.get_item(Key={"email": "john.doe@example.com"})
    assert "Item" in db_response
    assert db_response["Item"]["name"] == "John"
    assert db_response["Item"]["surname"] == "Doe"

    response = test_client.post('/add-customer', json=new_customer)
    assert response.status_code == 400
    assert response.json["error"] == "Customer already exists"

    invalid_customer = {"name": "Jane"}
    response = test_client.post('/add-customer', json=invalid_customer)
    assert response.status_code == 400
    assert "error" in response.json
    assert response.json["error"] == "Missing required fields: name, surname, or email"

    response = test_client.post('/add-customer', json={})
    assert response.status_code == 400
    assert response.json["error"] == "Missing required fields: name, surname, or email"

    from botocore.exceptions import ClientError

    error_response = {"Error": {"Code": "500", "Message": "AWS Internal Error"}}
    with pytest.raises(ClientError):
        raise ClientError(error_response, "PutItem")

def test_make_purchase(test_client, mock_dynamodb_setup):
    """Test making a purchase, including validation and stock checks."""
    customer_table = mock_dynamodb_setup.Table('customers')
    product_table = mock_dynamodb_setup.Table('products')
    purchase_table = mock_dynamodb_setup.Table('purchases')

    mock_customer = {"email": "john.doe@example.com", "name": "John", "surname": "Doe"}
    customer_table.put_item(Item=mock_customer)

    mock_product = {"product_name": "Spiced Latte", "price": 300, "available_amount": 5}
    product_table.put_item(Item=mock_product)

    purchase_data = {
        "customer_email": "john.doe@example.com",
        "product_name": "Spiced Latte",
        "amount_to_purchase": 2
    }
    response = test_client.post('/make-purchase', json=purchase_data)
    assert response.status_code == 201
    assert "message" in response.json
    assert "You successfully purchased 2 pieces of Spiced Latte" in response.json["message"]

    purchase_items = purchase_table.scan().get("Items", [])
    assert len(purchase_items) == 1
    assert purchase_items[0]["customer_email"] == "john.doe@example.com"
    assert purchase_items[0]["total_price"] == 600

    updated_product = product_table.get_item(Key={"product_name": "Spiced Latte"}).get("Item")
    assert updated_product["available_amount"] == 3

    purchase_data["amount_to_purchase"] = 10
    response = test_client.post('/make-purchase', json=purchase_data)
    assert response.status_code == 400
    assert "error" in response.json
    assert "The maximum amount you can purchase is 3" in response.json["error"]

    purchase_data["customer_email"] = "notfound@example.com"
    purchase_data["amount_to_purchase"] = 1
    response = test_client.post('/make-purchase', json=purchase_data)
    assert response.status_code == 404
    assert "error" in response.json
    assert response.json["error"] == "Customer not found"

    purchase_data["customer_email"] = "john.doe@example.com"
    purchase_data["product_name"] = "NonExistentProduct"
    response = test_client.post('/make-purchase', json=purchase_data)
    assert response.status_code == 404
    assert "error" in response.json
    assert response.json["error"] == "Product not found"

    invalid_data = {"customer_email": "john.doe@example.com"}
    response = test_client.post('/make-purchase', json=invalid_data)
    assert response.status_code == 400
    assert "error" in response.json
    assert response.json["error"] == "All fields (email, product_name, amount) are required"

    invalid_data = {
        "customer_email": "john.doe@example.com",
        "product_name": "Spiced Latte",
        "amount_to_purchase": "invalid"
    }
    response = test_client.post('/make-purchase', json=invalid_data)
    assert response.status_code == 400
    assert "error" in response.json
    assert response.json["error"] == "Amount must be an integer"

    from botocore.exceptions import ClientError
    error_response = {"Error": {"Code": "500", "Message": "AWS Internal Error"}}
    with pytest.raises(ClientError):
        raise ClientError(error_response, "PutItem")