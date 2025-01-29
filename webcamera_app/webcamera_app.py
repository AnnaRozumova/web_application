"""This is an app which activates a web camera and make a picture of user. User can save the pic, otherwise, it will be deleted.
"""
import datetime
from flask import Flask, jsonify
from camera_controller import CameraController
from s3_handler import S3Handler

app = Flask(__name__)

s3_handler = S3Handler()

@app.route('/capture-photo', methods=['POST'])
def capture_photo():
    try:
        image_bytes = CameraController.capture_frame()

        # 2. Upload + get presigned URL
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        object_name = f'image_{timestamp}.jpg'
        url = s3_handler.upload_bytes_and_get_presigned_url(
            image_bytes=image_bytes,
            object_name=object_name
        )

        # 3. Return the presigned URL
        return jsonify({'url': url, 'download_url': url})

    except RuntimeError as re:
        # Catch the raised error and convert it to an HTTP 500 or similar
        raise HTTPException(status_code=500, detail=str(re))
    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5454)
 
