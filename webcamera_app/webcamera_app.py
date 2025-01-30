"""This is an app which activates a web camera and make a picture of user. User can save the pic, otherwise, it will be deleted.
"""
import datetime
from flask import Flask, jsonify, Response
from camera_controller import CameraController
from s3_handler import S3Handler

app = Flask(__name__)

@app.route('/capture-photo', methods=["POST"])
def capture_photo():
    '''Function captures the photo and returns responce for frontend'''
    try:
        image_bytes = CameraController.capture_frame()
        return Response(image_bytes, content_type='image/jpeg')
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 500
    except RuntimeError as re:
        return jsonify({'error': str(re)}), 500
    except Exception as e:
        return jsonify({'error': 'Unexpected error: ' + str(e)}), 500



s3_handler = S3Handler()

@app.route('/capture-and-save-photo', methods=['POST'])
def capture_and_save_photo():
    '''Function captures the photo, saves it in s3 bucket and returns url of the image'''
    try:
        image_bytes = CameraController.capture_frame()

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        object_name = f'image_{timestamp}.jpg'
        url = s3_handler.upload_bytes_and_get_presigned_url(
            image_bytes=image_bytes,
            object_name=object_name
        )

        return jsonify({'url': url, 'download_url': url})

    except RuntimeError as re:
        raise HTTPException(status_code=500, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5454)
 
