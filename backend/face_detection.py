# Detects faces and extracts landmarks using MediaPipe
# Returns face count and landmark coordinates

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os


class FaceDetector:
    def __init__(self):
        # MediaPipe 0.10+ requires downloading the model
        # For now, use a simpler approach with OpenCV + MediaPipe solutions fallback
        # Try to use the new API, fallback to OpenCV if model not available
        try:
            # Try to use FaceLandmarker with downloaded model
            model_path = os.path.join(os.path.dirname(__file__), "face_landmarker.task")
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}. Run download_model.py first.")
            
            base_options = python.BaseOptions(
                model_asset_path=model_path
            )
            options = vision.FaceLandmarkerOptions(
                base_options=base_options,
                output_face_blendshapes=False,
                output_facial_transformation_matrixes=False,
                num_faces=1,
                min_face_detection_confidence=0.5,
                min_face_presence_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.detector = vision.FaceLandmarker.create_from_options(options)
            self.use_new_api = True
        except Exception as e:
            print(f"FaceLandmarker initialization failed: {e}")
            print("Falling back to OpenCV face detection")
            # Fallback to OpenCV for basic face detection
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.use_new_api = False

    def detect(self, frame: np.ndarray):
        """
        Detects face and returns:
        - face_count: int (0, 1, or >1)
        - landmarks: dict with landmark coordinates or None
        """
        h, w = frame.shape[:2]
        
        if self.use_new_api:
            # Use new MediaPipe FaceLandmarker API
            try:
                # MediaPipe requires RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                detection_result = self.detector.detect(mp_image)
                
                face_count = len(detection_result.face_landmarks)
                landmarks = None

                if face_count == 1:
                    face_landmarks = detection_result.face_landmarks[0]
                    landmarks = {}
                    for idx, landmark in enumerate(face_landmarks):
                        landmarks[idx] = {
                            'x': landmark.x * w,
                            'y': landmark.y * h,
                            'z': landmark.z
                        }
                
                return {
                    'face_count': face_count,
                    'landmarks': landmarks
                }
            except Exception as e:
                print(f"FaceLandmarker detection failed: {e}")
                # Fall through to OpenCV fallback
        
        # Fallback: Use OpenCV for basic face detection
        # Note: This only detects faces, not landmarks
        # For full functionality, MediaPipe model needs to be downloaded
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        face_count = len(faces)
        
        # Return basic detection (no landmarks in fallback mode)
        return {
            'face_count': face_count,
            'landmarks': None  # OpenCV doesn't provide detailed landmarks
        }

    def get_landmark_point(self, landmarks: dict, index: int) -> tuple:
        """
        Helper to get (x, y) coordinates of a specific landmark
        MediaPipe face mesh has 468 landmarks
        """
        if landmarks and index in landmarks:
            return (landmarks[index]['x'], landmarks[index]['y'])
        return None

