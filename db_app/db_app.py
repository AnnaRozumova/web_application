'''
This is simple application, which has a database of 'clients' on DynamoDB AWS, 
and user can add clients, update, search or delete them.
'''
import os
import uuid
from typing import Optional, Any
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response
import boto3
from boto3.dynamodb.conditions import Attr, Key

load_dotenv()

app = Flask(__name__)

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_REGION'))

customer_table = dynamodb.Table('customers')
purchase_table = dynamodb.Table("purchases")
product_table = dynamodb.Table("products")

@app.route('/all-customers', methods=['GET'])
def list_all_customers():
    '''This function will list all the customers.'''
    response = customer_table.scan()
    customers = response.get('Items', [])
    return jsonify(customers), 200

@app.route('/all-products', methods=['GET'])
def list_all_products():
    '''This function will list all available products.'''
    response = product_table.scan()
    products = response.get('Items', [])
    return jsonify(products), 200

@app.route('/all-purchases', methods=['GET'])
def list_all_purchases():
    '''This function will list all purchases.'''
    response = purchase_table.scan()
    purchases = response.get('Items', [])
    return jsonify(purchases), 200


@app.route('/get-product', methods=['GET'])
def get_product():
    '''Check if a product exists in the database using Query instead of Scan'''
    product_name = request.args.get("name")
    
    if not product_name:
        return jsonify({"error": "Product name is required"}), 400

    # Query the table for the product
    response = product_table.get_item(Key={"name": product_name})

    # If product exists, return it; otherwise, return an empty object
    if "Item" in response:
        return jsonify(response["Item"]), 200
    else:
        return jsonify({}), 200


@app.route('/add-product', methods=['POST'])
def add_product():
    '''Add a new product or update an existing product'''
    try:
        data = request.json
        product_name = data.get("product_name")
        product_price = data.get("price")
        product_amount = data.get("available_amount")

        if not product_name or product_price is None or product_amount is None:
            return jsonify({"error": "All fields (product_name, price, available_amount) are required"}), 400
        
        try:
            product_price = int(product_price)
            product_amount = int(product_amount)
        except ValueError:
            return jsonify({"error": "Price must be a number and Available Amount must be an integer"}), 400

        # Check if the product exists using get_item (efficient Query)
        response = product_table.get_item(Key={"product_name": product_name})
        existing_product = response.get("Item")

        if existing_product:
            # Product exists, update amount and price
            updated_amount = int(existing_product["available_amount"]) + product_amount
            updated_price = product_price  # Overwrite with new price

            product_table.update_item(
                Key={"product_name": product_name},
                UpdateExpression="SET available_amount = :a, price = :p",
                ExpressionAttributeValues={
                    ":a": updated_amount,
                    ":p": updated_price
                }
            )
            return jsonify({"message": "Product updated successfully"}), 200

        # If product does not exist, insert a new one
        new_product = {
            "product_name": product_name,  # Since name is the partition key, we don't need an ID
            "price": product_price,
            "available_amount": product_amount
        }

        product_table.put_item(Item=new_product)

        return jsonify({"message": "Product added successfully"}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/search-customers', methods=['GET'])
def search_customers():
    '''Search customers by email (query) or by name/surname (scan)'''
    name = request.args.get("name", "").strip()
    surname = request.args.get("surname", "").strip()
    email = request.args.get("email", "").strip()

    try:
        customer = None

        if email:  # If email is provided, use Query (efficient)
            response = customer_table.get_item(Key={"email": email})
            customer = response.get("Item")

        elif name or surname:  # If name or surname is provided, use Scan (slower)
            filter_expression = None
            if name:
                filter_expression = Attr("name").eq(name)
            if surname:
                if filter_expression:
                    filter_expression &= Attr("surname").eq(surname)
                else:
                    filter_expression = Attr("surname").eq(surname)

            if filter_expression:
                response = customer_table.scan(FilterExpression=filter_expression)
                customers = response.get("Items", [])
                customer = customers[0] if customers else None  # Take the first match

        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        # Fetch customer's purchases using their email (since email is the partition key in the purchases table)
        purchase_response = purchase_table.query(
            KeyConditionExpression=Key("customer_email").eq(customer["email"])
        )
        purchases = purchase_response.get("Items", [])

        # Combine customer and purchases data
        customer["purchases"] = purchases

        return jsonify(customer), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
