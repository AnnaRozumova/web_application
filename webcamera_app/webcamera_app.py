"""This is an app which activates a web camera and make a picture of user. User can save the pic, otherwise, it will be deleted.
"""
import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from s3_handler import S3Handler

app = Flask(__name__)
s3_handler = S3Handler()
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_image():
    '''Receives an image from the frontend and uploads it directly to S3.'''
    try:
        print("Received request to /upload")  # Debugging log
        
        if 'image' not in request.files:
            print("No image file in request")  # Debugging log
            return jsonify({'error': 'No image file provided'}), 400
        
        image = request.files['image']
        print(f"Image received: {image.filename}")  # Debugging log

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        object_name = f'image_{timestamp}.jpg'

        url = s3_handler.upload_bytes_and_get_presigned_url(
            image_bytes=image.read(),
            object_name=object_name
        )

        print(f"Upload successful. URL: {url}")  # Debugging log
        return jsonify({'url': url, 'download_url': url}), 200

    except Exception as e:
        print(f"Upload failed: {str(e)}")  # Debugging log
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5454)
 
