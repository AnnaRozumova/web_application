'''This Flask application activates a web camera, allows users to take a picture, 
and uploads the captured image to an AWS S3 bucket. The user receives a 
presigned URL to access or download the image.'''

import datetime
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from s3_handler import S3Handler

app = Flask(__name__)
s3_handler = S3Handler()
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_image() -> tuple[Response, int]:
    '''Receives an image from the frontend and uploads it directly to S3.'''
    try:
        app.logger.info("Received request to /upload")
        if 'image' not in request.files:
            app.logger.info("No image file")
            return jsonify({'error': 'No image file provided'}), 400
        image = request.files['image']

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        object_name = f'image_{timestamp}.jpg'
        app.logger.info("Uploading image %s", object_name)
        url = s3_handler.upload_bytes_and_get_presigned_url(
            image_bytes=image.read(),
            object_name=object_name
        )
        app.logger.info("Image uploaded successfully: %s", url)
        return jsonify({'url': url, 'download_url': url}), 200

    except Exception as e:
        app.logger.error("Upload failed: %s", e, exc_info=True)
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5454)
