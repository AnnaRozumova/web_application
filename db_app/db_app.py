'''
This is simple application, which has a database of 'clients' on DynamoDB AWS, 
and user can add clients, update, search or delete them.
'''
import os
import uuid
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import boto3
from boto3.dynamodb.conditions import Attr, Key
from boto3.exceptions import Boto3Error
from botocore.exceptions import ClientError

load_dotenv()

app = Flask(__name__)
CORS(app)

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_REGION'))

customer_table = dynamodb.Table('customers')
purchase_table = dynamodb.Table("purchases")
product_table = dynamodb.Table("products")

@app.route('/all-customers', methods=['GET'])
def list_all_customers() -> tuple[Response, int]:
    '''This function will list all the customers.'''
    response = customer_table.scan()
    customers = response.get('Items', [])
    return jsonify(customers), 200

@app.route('/all-products', methods=['GET'])
def list_all_products() -> tuple[Response, int]:
    '''This function will list all available products.'''
    response = product_table.scan()
    products = response.get('Items', [])
    return jsonify(products), 200

@app.route('/all-purchases', methods=['GET'])
def list_all_purchases() -> tuple[Response, int]:
    '''This function will list all purchases.'''
    response = purchase_table.scan()
    purchases = response.get('Items', [])
    return jsonify(purchases), 200


@app.route('/add-product', methods=['GET', 'POST'])
def add_product() -> tuple[Response, int]:
    '''Add a new product or update an existing product'''
    try:
        app.logger.info("Received request: /add-product | Method: %s", request.method)
        if request.method == "GET":
            product_name = request.args.get("product_name")
            if not product_name:
                app.logger.warning("Product name is missing in GET request")
                return jsonify({"error": "Product name is required"}), 400

            response = product_table.get_item(Key={"product_name": product_name})
            existing_product = response.get("Item") if response else None

            if existing_product:
                app.logger.info("Product found: %s", product_name)
                return jsonify(existing_product), 200
            return jsonify({"message": "Product not found"}), 404

        if request.method == "POST":
            data = request.get_json()
            product_name = data.get("product_name")
            product_price = data.get("price")
            product_amount = data.get("available_amount")

            if not product_name or product_price is None or product_amount is None:
                app.logger.warning("Missing product fields in POST request")
                return jsonify({"error": "All fields (product_name, price, available_amount) are required"}), 400
            try:
                product_price = int(product_price)
                product_amount = int(product_amount)
            except ValueError:
                app.logger.error("Invalid price or amount format")
                return jsonify({"error": "Price must be a number and Available Amount must be an integer"}), 400

            response = product_table.get_item(Key={"product_name": product_name})
            existing_product = response.get("Item")

            if existing_product:
                updated_amount = int(existing_product["available_amount"]) + product_amount
                updated_price = product_price

                product_table.update_item(
                    Key={"product_name": product_name},
                    UpdateExpression="SET available_amount = :a, price = :p",
                    ExpressionAttributeValues={
                        ":a": updated_amount,
                        ":p": updated_price
                    }
                )
                app.logger.info("Product updated: %s", product_name)
                return jsonify({"message": "Product updated successfully"}), 200

            new_product = {
                "product_name": product_name,
                "price": product_price,
                "available_amount": product_amount
            }

            product_table.put_item(Item=new_product)
            app.logger.info("New product added: %s", product_name)
            return jsonify({"message": "Product added successfully"}), 201

    except RuntimeError as e:
        app.logger.critical("Unexpected runtime error: %s", str(e))
        return jsonify({'error': f"Unexpected runtime error: {str(e)}"}), 500
    return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/search-customers', methods=['GET'])
def search_customers() -> tuple[Response, int]:
    '''Search customers by email (query) or by name/surname (scan)'''
    name = request.args.get("name", "").strip()
    surname = request.args.get("surname", "").strip()
    email = request.args.get("email", "").strip()
    app.logger.info("Received request: /search-customers | Params: name=%s, surname=%s, email=%s", name, surname, email)

    try:
        customers = []

        if email:
            try:
                response = customer_table.get_item(Key={"email": email})
                customer = response.get("Item") if response else None
                if customer:
                    customers.append(customer)
                    app.logger.info("Customer found by email: %s", email)
            except ClientError as e:
                app.logger.error("AWS Client Error while quering by email: %s | Error: %s", email, str(e))
                return jsonify({"error": f"AWS Client Error: {e.response['Error']['Message']}"}), 500

        elif name or surname:
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
                customers = response.get("Items", []) if response else []
                app.logger.info("Customers found by name/surname: %s %s | Count: %d", name, surname, len(customers))

        if not customers:
            return jsonify({"error": "Customer not found"}), 404

        for customer in customers:
            try:
                purchase_response = purchase_table.query(
                    KeyConditionExpression=Key("customer_email").eq(customer["email"])
                )
                customer["purchases"] = purchase_response.get("Items", []) if purchase_response else []
                app.logger.info("Fetched purchases for customer: %s", customer["email"])
            except KeyError:
                app.logger.error("KeyError: Unexpected response format while fetching purchases for customer: %s", customer["email"])
                return jsonify({"error": "Unexpected response format from purchase database"}), 500

        return jsonify({"customers": customers}), 200

    except RuntimeError as e:
        app.logger.critical("Runtime error in search_customers: %s", str(e))
        return jsonify({'error': f"Unexpected runtime error: {str(e)}"}), 500

@app.route('/add-customer', methods=['POST'])
def add_customer() -> tuple[Response, int]:
    '''Add a new customer if they do not already exist'''
    try:
        app.logger.info("Received request: /add-customer")
        data = request.get_json()
        if data is None:
            app.logger.warning("Request body is missing")
            return jsonify({"error": "Request body is required"}), 400
        name = data.get("name", "").strip()
        surname = data.get("surname", "").strip()
        email = data.get("email", "").strip()

        if not name or not surname or not email:
            app.logger.warning("Missing required fields: name=%s, surname=%s, email=%s", name, surname, email)
            return jsonify({"error": "Missing required fields: name, surname, or email"}), 400

        existing_customer = customer_table.get_item(Key={"email": email}).get("Item")
        if existing_customer:
            return jsonify({"error": "Customer already exists"}), 400

        new_customer = {
            "name": name,
            "surname": surname,
            "email": email
        }

        customer_table.put_item(Item=new_customer)

        return jsonify({"success": True, "customer": new_customer}), 201

    except ClientError as e:
        return jsonify({"error": f"AWS Client Error: {e.response['Error']['Message']}"}), 500
    except KeyError as e:
        return jsonify({"error": f"Missing expected data: {str(e)}"}), 500


@app.route('/make-purchase', methods=['POST'])
def make_purchase() -> tuple[Response, int]:
    '''Check if customer exist and product amount is available. Add a new purchase.'''
    try:
        data = request.get_json()
        customer_email = data.get("customer_email")
        product_name = data.get("product_name")
        amount_to_purchase = data.get("amount_to_purchase")

        if not customer_email or product_name is None or amount_to_purchase is None:
            return jsonify({"error": "All fields (email, product_name, amount) are required"}), 400
        try:
            amount_to_purchase = int(amount_to_purchase)
        except ValueError:
            return jsonify({"error": "Amount must be an integer"}), 400

        try:
            response_customer = customer_table.get_item(Key={"email": customer_email})
            customer = response_customer.get("Item")

            if not customer:
                return jsonify({"error": "Customer not found"}), 404
        except ClientError as e:
            return jsonify({"error": f"AWS Client Error: {e.response['Error']['Message']}"}), 500

        try:
            response = product_table.get_item(Key={"product_name": product_name})
            product_in_stock = response.get("Item")

            if not product_in_stock:
                return jsonify({"error": "Product not found"}), 404
        except ClientError as e:
            return jsonify({"error": f"AWS Client Error: {e.response['Error']['Message']}"}), 500

        available_amount = int(product_in_stock["available_amount"])

        if available_amount < amount_to_purchase:
            return jsonify({"error": f"The maximum amount you can purchase is {available_amount}"}), 400
        price = int(product_in_stock["price"])
        purchase_id = str(uuid.uuid4())
        products = [{"product_name": product_name, "amount": amount_to_purchase}]
        total = round((price*amount_to_purchase), 2)
        new_purchase = {
            "purchase_id": purchase_id,
            "customer_email": customer_email,
            "products": products,
            "total_price": total
        }

        purchase_table.put_item(Item=new_purchase)

        product_table.update_item(
            Key={"product_name": product_name},
        UpdateExpression="SET available_amount = :a",
        ExpressionAttributeValues={
            ":a": (available_amount - amount_to_purchase)
            }
        )

        return jsonify({"message": f"You successfully purchased {amount_to_purchase} pieces of {product_name} for a total price of {total}"}), 201

    except Boto3Error as e:
        return jsonify({"error": f"Boto3 error: {str(e)}"}), 500

    except KeyError as e:
        return jsonify({"error": f"Unexpected missing data: {str(e)}"}), 500

    except RuntimeError as e:
        return jsonify({"error": f"Unexpected runtime error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
