'''These tests verify that images can be uploaded to a mocked AWS S3 bucket
and that a presigned URL is correctly generated.'''
from unittest.mock import patch
from botocore.exceptions import ClientError
import pytest

def test_upload_bytes_and_get_presigned_url(mock_s3_handler):
    """Test uploading image bytes to S3 and retrieving a presigned URL."""
    image_bytes = b"test_image_data"
    object_name = "test_image.jpg"

    with patch.object(mock_s3_handler.s3_client, "upload_fileobj") as mock_upload, \
         patch.object(mock_s3_handler.s3_client, "generate_presigned_url", return_value="https://mock-s3-url") as mock_presigned_url:

        url = mock_s3_handler.upload_bytes_and_get_presigned_url(image_bytes, object_name)

        mock_upload.assert_called_once()
        mock_presigned_url.assert_called_once_with(
            'get_object',
            Params={'Bucket': "webcamera-app-hu2119tru05", 'Key': object_name},
            ExpiresIn=3600
        )

        assert url == "https://mock-s3-url"

def test_upload_bytes_and_get_presigned_url_failure(mock_s3_handler):
    """Test handling of upload failure."""
    image_bytes = b"test_image_data"
    object_name = "test_image.jpg"

    mock_error_response = {"Error": {"Code": "500", "Message": "Upload failed"}}
    mock_client_error = ClientError(mock_error_response, "UploadFileObj")

    with patch.object(mock_s3_handler.s3_client, "upload_fileobj", side_effect=mock_client_error):
        with pytest.raises(RuntimeError, match="Failed to upload or generate URL: .*Upload failed"):
            mock_s3_handler.upload_bytes_and_get_presigned_url(image_bytes, object_name)
