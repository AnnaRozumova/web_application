'''This module can be used in case of running application from local machine.'''
import cv2


class CameraController:

    @staticmethod
    def capture_frame():
        
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
            
