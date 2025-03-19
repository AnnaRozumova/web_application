'''Pytest configuration for test fixtures.'''
from unittest.mock import MagicMock, patch
import pytest
import boto3
from moto import mock_aws
from webcamera_app import webcamera_app
from webcamera_app.s3_handler import S3Handler

@pytest.fixture
def mock_video_capture():
    '''Fixture to mock OpenCV's VideoCapture'''
    with patch('cv2.VideoCapture') as mock_capture:
        mock_cap = MagicMock()
        mock_capture.return_value = mock_cap
        yield mock_cap

@pytest.fixture
def mock_s3_client():
    '''Fixture to movk boto3 S3 client.'''
    with mock_aws():
        s3_client = boto3.client("s3", region_name="eu-central-1")
        s3_client.create_bucket(
            Bucket="webcamera-app-hu2119tru05",
            CreateBucketConfiguration={"LocationConstraint": "eu-central-1"},    
        )
        yield s3_client

@pytest.fixture
def mock_s3_handler(mock_s3_client):
    '''Fixture to initialize S3Handler with a mocked S3 client.'''
    handler = S3Handler()
    handler.s3_client = mock_s3_client
    return handler

@pytest.fixture
def test_client():
    """Fixture to create a test client for the Flask app."""
    webcamera_app.app.config["TESTING"] = True
    return webcamera_app.app.test_client()
