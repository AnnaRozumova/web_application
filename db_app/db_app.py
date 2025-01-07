'''
This is simple application, which has a database of 'clients' on DynamoDB AWS, 
and user can add clients, update, search or delete them.
'''
import os
import uuid
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import boto3
from boto3.dynamodb.conditions import Attr

load_dotenv()

app = Flask(__name__)

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_REGION'))
table_name = 'clients'
table = dynamodb.Table(table_name)

try:
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{'AttributeName': 'client_id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'client_id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    print("Creating DynamoDB table...")
    table.wait_until_exists()
    print(f"Table '{table_name}' created successfully!")
except boto3.exceptions.botocore.exceptions.ClientError:
    print(f"Table '{table_name}' already exists.")


@app.route('/add-client', methods=['POST'])
def add_client():
    data = request.json
    client_id = str(uuid.uuid4())
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
def update_client(client_id):
    data = request.json
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
    else:
        return jsonify({"error": "Client not found"}), 404

@app.route('/delete-client/<client_id>', methods=['DELETE'])
def delete_client(client_id):
    response = table.delete_item(
        Key={'client_id': client_id},
        ReturnValues='ALL_OLD'
    )
    if 'Attributes' in response:
        return jsonify({"message": "Client deleted successfully"}), 200
    return jsonify({"error": "Client not found"}), 404

@app.route('/search-clients', methods=['GET'])
def search_clients():
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

    # Perform a scan with the filter
    if filter_expression:
        response = table.scan(FilterExpression=filter_expression)
    else:
        response = table.scan()

    clients = response.get('Items', [])
    return jsonify(clients), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)  # Runs on a separate port within the network
