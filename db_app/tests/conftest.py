from moto import mock_aws
import pytest
import boto3

@pytest.fixture
def mock_dynamodb_setup():
    """Mock DynamoDB for all tests."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="eu-central-1")

        dynamodb.create_table(
            TableName='customers',
            KeySchema=[{'AttributeName': 'email', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'email', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        dynamodb.create_table(
            TableName='products',
            KeySchema=[{'AttributeName': 'product_name', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'product_name', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        dynamodb.create_table(
            TableName='purchases',
            KeySchema=[
                {'AttributeName': 'customer_email', 'KeyType': 'HASH'},
                {'AttributeName': 'purchase_id', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'customer_email', 'AttributeType': 'S'},
                {'AttributeName': 'purchase_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        yield dynamodb

@pytest.fixture
def test_client(mock_dynamodb_setup):
    '''Create a test client for Flask application.'''
    import db_app
    db_app.app.config.update({
        "TESTING": True,
        "DEBUG": True,
        })
    return db_app.app.test_client()