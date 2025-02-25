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
from boto3.dynamodb.conditions import Attr

load_dotenv()

app = Flask(__name__)

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_REGION'))
TABLE_NAME = 'clients'
table = dynamodb.Table(TABLE_NAME)

try:
    dynamodb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[{'AttributeName': 'client_id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'client_id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    print("Creating DynamoDB table...")
    print(f"Table '{TABLE_NAME}' created successfully!")
except boto3.exceptions.botocore.exceptions.ClientError:
    print(f"Table '{TABLE_NAME}' already exists.")


@app.route('/add-client', methods=['POST'])
def add_client() -> tuple[Response, int]:
    '''Add client to the DataBase'''
    data: Optional[dict[str, Any]] = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    client_id: str = str(uuid.uuid4())
    client_data = {
        "client_id": client_id,
        "name": data.get("name"),
        "surname": data.get("surname"),
        "email": data.get("email"),
        "shipping_address": data.get("shipping_address"),
        "products": data.get("products", [])
    }
    table.put_item(Item=client_data)
    return jsonify({"message": "Client added successfully", "id": client_id}), 201

@app.route('/update-client/<client_id>', methods=['PUT'])
def update_client(client_id: str) -> tuple[Response, int]:
    '''Fetch the client by ID, update data'''
    data: Optional[dict[str, Any]] = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    update_expression = "SET " + ", ".join(f"#{k} = :{k}" for k in data.keys())
    expression_attribute_names = {f"#{k}": k for k in data.keys()}
    expression_attribute_values = {f":{k}": v for k, v in data.items()}
    response = table.update_item(
        Key={'client_id': client_id},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values,
        ReturnValues="UPDATED_NEW"
    )
    if response.get("Attributes"):
        return jsonify({"message": "Client updated successfully"}), 200

    return jsonify({"error": "Client not found"}), 404

@app.route('/delete-client/<client_id>', methods=['DELETE'])
def delete_client(client_id: str) -> tuple[Response, int]:
    '''Fetch the client by ID, delete client'''
    response = table.delete_item(
        Key={'client_id': client_id},
        ReturnValues='ALL_OLD'
    )
    if 'Attributes' in response:
        return jsonify({"message": "Client deleted successfully"}), 200
    return jsonify({"error": "Client not found"}), 404

@app.route('/search-clients', methods=['GET'])
def search_clients() -> tuple[Response, int]:
    '''Search item in DB by fetching parametres'''
    name = request.args.get('name')
    surname = request.args.get('surname')
    product = request.args.get('product')

    filter_expression = None
    if name:
        filter_expression = Attr('name').contains(name)
    if surname:
        filter_expression = (filter_expression & Attr('surname').contains(surname)) if filter_expression else Attr('surname').contains(surname)
    if product:
        filter_expression = (filter_expression & Attr('products').contains(product)) if filter_expression else Attr('products').contains(product)

    if filter_expression:
        response = table.scan(FilterExpression=filter_expression)
    else:
        response = table.scan()

    clients = response.get('Items', [])
    return jsonify(clients), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
