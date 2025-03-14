'''These tests ensure that:
- The `/upload` endpoint correctly processes image uploads.
- Error handling works when an image file is missing or an S3 upload fails.'''
from unittest.mock import patch
from io import BytesIO

def test_upload_image_success(test_client, mock_s3_handler):
    """Test successful image upload to S3."""
    mock_url = "https://mock-s3-url"

    with patch.object(mock_s3_handler, "upload_bytes_and_get_presigned_url", return_value=mock_url):
        with patch("webcamera_app.webcamera_app.s3_handler", mock_s3_handler):
            data = {"image": (BytesIO(b"test_image_data"), "test.jpg")}
            response = test_client.post("/upload", data=data, content_type="multipart/form-data")

            assert response.status_code == 200
            assert response.json["url"] == mock_url
            assert response.json["download_url"] == mock_url

def test_upload_image_no_file(test_client):
    """Test handling of a request without an image file."""
    response = test_client.post("/upload", data={}, content_type="multipart/form-data")

    assert response.status_code == 400
    assert response.json["error"] == "No image file provided"

def test_upload_image_s3_failure(test_client, mock_s3_handler):
    """Test handling of an S3 upload failure."""
    with patch.object(mock_s3_handler, "upload_bytes_and_get_presigned_url", side_effect=Exception("S3 upload failed")):
        with patch("webcamera_app.webcamera_app.s3_handler", mock_s3_handler):
            data = {"image": (BytesIO(b"test_image_data"), "test.jpg")}
            response = test_client.post("/upload", data=data, content_type="multipart/form-data")

            assert response.status_code == 500
            assert "Upload failed: S3 upload failed" in response.json["error"]
