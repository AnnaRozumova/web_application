'''This module provides functionality for capturing a frame using a webcam. 
It can be used when running the application locally.'''
import cv2


class CameraController:
    '''A static class that provides a method to capture a frame from the default webcam,
    encode it as a JPG image, and return the byte data.'''

    @staticmethod
    def capture_frame() -> bytes:
        '''Captures a single frame from the webcam.'''
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise ValueError("Could not open webcamera")

        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise RuntimeError("Failed to capture image from webcamera")

        success, buffer = cv2.imencode('.jpg', frame)
        if not success:
            raise RuntimeError("Failed to encode frame to JPG")

        return buffer.tobytes()
