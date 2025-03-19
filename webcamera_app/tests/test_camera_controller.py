'''These tests verify that the `capture_frame` method correctly captures a frame,
handles errors, and encodes the image properly using OpenCV.'''
from unittest.mock import patch, MagicMock
import pytest
from camera_controller import CameraController

def test_capture_frame_success(mock_video_capture):
    '''Ensures that the CameraController captures a frame, encodes it as JPG,
    and returns the correct byte data.'''
    mock_video_capture.isOpened.return_value = True
    mock_video_capture.read.return_value = (True, "mock_frame")

    mock_np_array = MagicMock()
    mock_np_array.tobytes.return_value = b'mocked_bytes'

    with patch('cv2.imencode', return_value=(True, mock_np_array)) as mock_imencode:
        result = CameraController.capture_frame()

        mock_video_capture.isOpened.assert_called_once()
        mock_video_capture.read.assert_called_once()
        mock_video_capture.release.assert_called_once()
        mock_imencode.assert_called_once_with('.jpg', "mock_frame")
        assert result == b'mocked_bytes'

def test_capture_frame_camera_not_opened(mock_video_capture):
    '''Ensures that the function raises a ValueError when the webcam cannot be accessed.'''
    mock_video_capture.isOpened.return_value = False

    with pytest.raises(ValueError, match="Could not open webcamera"):
        CameraController.capture_frame()

def test_capture_frame_failure_to_capture(mock_video_capture):
    '''Ensures that a RuntimeError is raised when no frame is retrieved from the webcam.'''
    mock_video_capture.isOpened.return_value = True
    mock_video_capture.read.return_value = (False, None)

    with pytest.raises(RuntimeError, match="Failed to capture image from webcamera"):
        CameraController.capture_frame()

def test_capture_frame_failure_to_encode(mock_video_capture):
    '''Ensures that a RuntimeError is raised when the frame cannot be encoded to JPG format.'''
    mock_video_capture.isOpened.return_value = True
    mock_video_capture.read.return_value = (True, "mock_frame")

    with patch('cv2.imencode', return_value=(False, None)):
        with pytest.raises(RuntimeError, match="Failed to encode frame to JPG"):
            CameraController.capture_frame()
