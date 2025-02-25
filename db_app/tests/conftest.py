from moto import mock_aws
import pytest
import boto3

@pytest.fixture
def mock_dynamodb_setup():
    """Mock DynamoDB for all tests."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="eu-central-1")

        dynamodb.create_table(
            TableName='clients',
            KeySchema=[{'AttributeName': 'client_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'client_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        yield dynamodb

@pytest.fixture
def test_client(mock_dynamodb_setup):
    '''Test updating a client in database.'''
    import db_app
    db_app.app.config.update({
        "TESTING": True,
        "DEBUG": True,
        })
    return db_app.app.test_client()