"""This is an app which activates a web camera and make a picture of user. User can save the pic, otherwise, it will be deleted.
"""
import os
import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify
import cv2
import boto3
from botocore.exceptions import NoCredentialsError

load_dotenv()

app = Flask(__name__)

S3_BUCKET = 'webcamera-app-hu2119tru05'
S3_REGION = 'eu-central-1'
S3_BASE_URL = f'https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com'

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
print(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)

s3_client = session.client('s3')
#print(s3_client.list_buckets())

def upload_to_s3(filepath, filename):
    try:
        s3_client.upload_file(filepath, S3_BUCKET, filename)
        s3_url = f"{S3_BASE_URL}/{filename}"
        print(f"Uploaded {filename} to S3 at {s3_url}")
        return s3_url
    except NoCredentialsError:
        print("AWS credentials not available.")
        return None

def generate_presigned_url(filename, expiration=3600):
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': filename},
            ExpiresIn=expiration
        )
        print(f"Generated pre-signed URL: {url}")
        return url
    except Exception as e:
        print(f"Error generating pre-signed URL: {e}")
        return None


@app.route('/take-screenshot', methods=['POST'])
def take_screenshot():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return jsonify({'error': 'Could not open webcam'}), 500

    ret, frame = cap.read()

    if not ret:
        return jsonify({'error': 'Failed to capture frame'}), 500

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    screenshot_filename = f'screenshot_{timestamp}.png'
    screenshot_filepath = os.path.join('/tmp', screenshot_filename)

    # Save the screenshot
    cv2.imwrite(screenshot_filepath, frame)
    print(f"File saved at {screenshot_filepath}")
    cap.release()

    s3_url = upload_to_s3(screenshot_filepath, screenshot_filename)

    os.remove(screenshot_filepath)

    if not s3_url:
        return jsonify({'error': 'Failed to upload screenshot to S3'}), 500

    presigned_url = generate_presigned_url(screenshot_filename)
    if not presigned_url:
        return jsonify({'error': 'Failed to generate pre-signed URL'}), 500

    return jsonify({'url': s3_url, 'download_url': presigned_url}), 200

@app.route('/uploads/<filename>', methods=['GET'])
def view_file(filename):
    presigned_url = generate_presigned_url(filename)
    if not presigned_url:
        return jsonify({'error': 'Failed to generate pre-signed URL for viewing'}), 500
    return jsonify({'url': presigned_url}), 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    presigned_url = generate_presigned_url(filename)
    if not presigned_url:
        return jsonify({'error': 'Failed to generate pre-signed URL for downloading'}), 500
    return jsonify({'url': presigned_url}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5454)
