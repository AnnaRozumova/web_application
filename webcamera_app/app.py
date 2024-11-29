"""This is an app which activates a web camera and make a picture of user. User can save the pic, otherwise, it will be deleted.
To run this in docker container use(from webcamera_app directory):
docker network create my_network
docker build -t webcamera_app_image .
docker run -d --name webcamera_app --network my_network -p 5454:5454 webcamera_app_image
"""
import os
import time
import datetime
import threading
from flask import Flask, render_template, jsonify, send_from_directory
import cv2


app = Flask(__name__)

# Directory to save screenshots
UPLOAD_FOLDER = '/app/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  

# Function to delete a file after 4 minute
def delete_file_after_delay(filepath, delay=240):
    time.sleep(delay)  
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"{filepath} has been deleted.")

# Route to take a screenshot
@app.route('/take_screenshot', methods=['POST'])
def take_screenshot():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return jsonify({'error': 'Could not open webcam'}), 500

    ret, frame = cap.read()

    if not ret:
        return jsonify({'error': 'Failed to capture frame'}), 500

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    screenshot_filename = f'screenshot_{timestamp}.png'
    screenshot_filepath = os.path.join(UPLOAD_FOLDER, screenshot_filename)

    # Save the screenshot
    cv2.imwrite(screenshot_filepath, frame)
    print(f"File saved at {screenshot_filepath}")
    cap.release()

    threading.Thread(target=delete_file_after_delay, args=(screenshot_filepath,)).start()

    return jsonify({'filename': screenshot_filename}), 200

@app.route('/download/<filename>')
def download_file(filename):
    if filename:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    else:
        return jsonify({'error':'Your picture was deleted from the server. Please make another one'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5454)
