# Tracks gaze direction using eye landmarks
# Detects continuous deviation for proctor alerts

import time
from typing import Optional, Tuple


class GazeTracker:
    def __init__(self):
        # MediaPipe landmark indices for eyes
        self.LEFT_EYE_INNER = 133
        self.LEFT_EYE_OUTER = 33
        self.RIGHT_EYE_INNER = 362
        self.RIGHT_EYE_OUTER = 263
        
        # Eye center landmarks (use multiple points to approximate center)
        self.LEFT_EYE_TOP = 159
        self.LEFT_EYE_BOTTOM = 145
        self.RIGHT_EYE_TOP = 386
        self.RIGHT_EYE_BOTTOM = 374
        
        self.deviation_start_time: Optional[float] = None
        self.current_gaze_direction: Optional[str] = None
        self.alert_threshold_seconds = 4.0

    def calculate_gaze_direction(self, landmarks: dict) -> Optional[str]:
        """
        Determines gaze direction: LEFT, RIGHT, UP, DOWN, CENTER
        Returns None if landmarks are invalid
        """
        if not landmarks:
            return None

        def get_point(idx):
            point = landmarks.get(idx)
            if point:
                return (point['x'], point['y'])
            return None

        left_inner = get_point(self.LEFT_EYE_INNER)
        left_outer = get_point(self.LEFT_EYE_OUTER)
        right_inner = get_point(self.RIGHT_EYE_INNER)
        right_outer = get_point(self.RIGHT_EYE_OUTER)

        if not all([left_inner, left_outer, right_inner, right_outer]):
            return None

        left_eye_center_x = (left_inner[0] + left_outer[0]) / 2
        right_eye_center_x = (right_inner[0] + right_outer[0]) / 2
        
        left_eye_top = get_point(self.LEFT_EYE_TOP)
        left_eye_bottom = get_point(self.LEFT_EYE_BOTTOM)
        right_eye_top = get_point(self.RIGHT_EYE_TOP)
        right_eye_bottom = get_point(self.RIGHT_EYE_BOTTOM)

        if not all([left_eye_top, left_eye_bottom, right_eye_top, right_eye_bottom]):
            return "CENTER"

        left_eye_center_y = (left_eye_top[1] + left_eye_bottom[1]) / 2
        right_eye_center_y = (right_eye_top[1] + right_eye_bottom[1]) / 2

        left_eye_width = abs(left_outer[0] - left_inner[0])
        left_eye_height = abs(left_eye_top[1] - left_eye_bottom[1])
        right_eye_width = abs(right_outer[0] - right_inner[0])
        right_eye_height = abs(right_eye_top[1] - right_eye_bottom[1])

        # Use inner corner position relative to eye center as proxy for gaze
        left_inner_offset = left_inner[0] - left_eye_center_x
        right_inner_offset = right_inner[0] - right_eye_center_x
        
        if left_eye_width > 0 and right_eye_width > 0:
            left_ratio = left_inner_offset / left_eye_width
            right_ratio = right_inner_offset / right_eye_width
            avg_horizontal_ratio = (left_ratio + right_ratio) / 2

            if avg_horizontal_ratio < -0.2:
                return "LEFT"
            elif avg_horizontal_ratio > 0.2:
                return "RIGHT"
        
        # Check vertical gaze: when looking up, eyes appear more closed (top/bottom closer)
        if left_eye_height > 0 and right_eye_height > 0:
            face_width = abs(right_outer[0] - left_outer[0])
            if face_width > 0:
                # Expected eye height is roughly 1/10 of face width
                expected_eye_height = face_width / 10
                height_ratio_left = left_eye_height / expected_eye_height if expected_eye_height > 0 else 1.0
                height_ratio_right = right_eye_height / expected_eye_height if expected_eye_height > 0 else 1.0
                avg_height_ratio = (height_ratio_left + height_ratio_right) / 2
                
                if avg_height_ratio < 0.7:
                    return "UP"
                elif avg_height_ratio > 1.3:
                    return "DOWN"

        return "CENTER"

    def check_continuous_deviation(self, gaze_direction: str) -> bool:
        """
        Tracks if gaze has been deviated (not CENTER) for >= 4 seconds
        Returns True if alert should be triggered
        """
        current_time = time.time()
        
        if gaze_direction != "CENTER":
            if self.deviation_start_time is None:
                self.deviation_start_time = current_time
            
            elapsed = current_time - self.deviation_start_time
            if elapsed >= self.alert_threshold_seconds:
                return True
        else:
            self.deviation_start_time = None
        
        return False

    def get_status(self, landmarks: dict) -> dict:
        """
        Returns current gaze status and alert state
        """
        gaze_direction = self.calculate_gaze_direction(landmarks)
        alert_triggered = False
        
        if gaze_direction:
            alert_triggered = self.check_continuous_deviation(gaze_direction)
        
        return {
            'direction': gaze_direction,
            'alert_triggered': alert_triggered,
            'deviation_duration': (
                time.time() - self.deviation_start_time 
                if self.deviation_start_time else 0
            )
        }

