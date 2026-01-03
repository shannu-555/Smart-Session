# Rule-based confusion detection using facial landmarks
# No ML models - only geometric calculations

from typing import Optional, Dict
import math


class ConfusionDetector:
    def __init__(self):
        # MediaPipe landmark indices
        self.LEFT_INNER_BROW = 107
        self.RIGHT_INNER_BROW = 336
        self.LEFT_OUTER_BROW = 70
        self.RIGHT_OUTER_BROW = 300
        self.MOUTH_LEFT = 61
        self.MOUTH_RIGHT = 291
        self.MOUTH_TOP = 13
        self.MOUTH_BOTTOM = 14
        self.NOSE_TIP = 4
        self.CHIN = 175
        self.LEFT_TEMPLE = 234
        self.RIGHT_TEMPLE = 454
        
        # Thresholds adjusted for realistic human behavior
        self.brow_furrow_threshold = 0.80  # 20% reduction indicates furrowing (more tolerant)
        self.mouth_flatness_threshold = 0.08  # Curvature below this = flat (more relaxed)
        self.head_movement_min = 2.0
        
        self.baseline_brow_distance: Optional[float] = None
        self.baseline_locked = False
        self.baseline_init_samples = []
        self.baseline_init_duration = 3.0
        self.baseline_init_start_time: Optional[float] = None
        self.head_positions = []
        self.time_window_seconds = 3.0  # Shorter window (3 seconds instead of 5)

    def _get_point(self, landmarks: dict, index: int) -> Optional[tuple]:
        """Helper to get (x, y) coordinates"""
        if landmarks and index in landmarks:
            return (landmarks[index]['x'], landmarks[index]['y'])
        return None

    def _distance(self, p1: tuple, p2: tuple) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def _calculate_curvature(self, points: list) -> float:
        """
        Calculate curvature by measuring deviation from straight line.
        Lower values indicate flatter curve.
        """
        if len(points) < 3:
            return 0.0
        
        start = points[0]
        end = points[-1]
        
        if start[0] == end[0]:
            distances = [abs(p[0] - start[0]) for p in points[1:-1]]
        else:
            a = end[1] - start[1]
            b = start[0] - end[0]
            c = end[0] * start[1] - start[0] * end[1]
            denom = math.sqrt(a*a + b*b)
            if denom > 0:
                distances = [abs(a*p[0] + b*p[1] + c) / denom for p in points[1:-1]]
            else:
                distances = [0.0]
        
        if distances:
            return sum(distances) / len(distances)
        return 0.0

    def initialize_baseline(self, landmarks: dict, current_time: float, face_count: int, gaze_direction: str, proctor_alert_active: bool) -> bool:
        """
        Initialize baseline during stable period.
        Only initializes when: exactly 1 face, head forward (gaze CENTER), no proctor alert.
        Returns True if baseline was just locked.
        """
        if face_count != 1 or gaze_direction != "CENTER" or proctor_alert_active:
            self.baseline_init_samples = []
            self.baseline_init_start_time = None
            return False
        
        if self.baseline_locked:
            return False
        
        left_inner = self._get_point(landmarks, self.LEFT_INNER_BROW)
        right_inner = self._get_point(landmarks, self.RIGHT_INNER_BROW)
        
        if not left_inner or not right_inner:
            return False
        
        current_distance = self._distance(left_inner, right_inner)
        
        if self.baseline_init_start_time is None:
            self.baseline_init_start_time = current_time
        
        elapsed = current_time - self.baseline_init_start_time
        if elapsed < self.baseline_init_duration:
            self.baseline_init_samples.append(current_distance)
            return False
        
        if len(self.baseline_init_samples) > 0:
            self.baseline_brow_distance = sum(self.baseline_init_samples) / len(self.baseline_init_samples)
            self.baseline_locked = True
            self.baseline_init_samples = []
            self.baseline_init_start_time = None
            return True
        
        return False

    def detect_brow_furrowing(self, landmarks: dict) -> bool:
        """
        Detects if inner eyebrows are closer together (furrowing).
        Uses locked baseline - no updating after initialization.
        """
        if not self.baseline_locked or self.baseline_brow_distance is None:
            return False
        
        left_inner = self._get_point(landmarks, self.LEFT_INNER_BROW)
        right_inner = self._get_point(landmarks, self.RIGHT_INNER_BROW)
        
        if not left_inner or not right_inner:
            return False
        
        current_distance = self._distance(left_inner, right_inner)
        
        if self.baseline_brow_distance > 0:
            ratio = current_distance / self.baseline_brow_distance
            if ratio < self.brow_furrow_threshold:
                return True
        
        return False

    def detect_mouth_flatness(self, landmarks: dict) -> bool:
        """Detects if mouth is flat (not smiling) using curvature of mouth landmarks."""
        mouth_left = self._get_point(landmarks, self.MOUTH_LEFT)
        mouth_right = self._get_point(landmarks, self.MOUTH_RIGHT)
        mouth_top = self._get_point(landmarks, self.MOUTH_TOP)
        mouth_bottom = self._get_point(landmarks, self.MOUTH_BOTTOM)
        
        if not all([mouth_left, mouth_right, mouth_top, mouth_bottom]):
            return False
        
        mouth_points = [
            mouth_left,
            mouth_top,
            mouth_right,
            mouth_bottom
        ]
        
        curvature = self._calculate_curvature(mouth_points)
        return curvature < self.mouth_flatness_threshold

    def detect_head_rigidity(self, landmarks: dict, current_time: float) -> bool:
        """
        Detects if head has been rigid (minimal movement) over time window.
        Prolonged stillness can indicate confusion or disengagement.
        """
        nose_tip = self._get_point(landmarks, self.NOSE_TIP)
        if not nose_tip:
            return False
        
        self.head_positions.append((current_time, nose_tip))
        
        cutoff_time = current_time - self.time_window_seconds
        self.head_positions = [(t, pos) for t, pos in self.head_positions if t > cutoff_time]
        
        if len(self.head_positions) < 3:
            return False
        
        positions = [pos for _, pos in self.head_positions]
        total_movement = 0.0
        
        for i in range(1, len(positions)):
            total_movement += self._distance(positions[i-1], positions[i])
        
        return total_movement < self.head_movement_min

    def detect_confusion(self, landmarks: dict, current_time: float, face_count: int = 1, gaze_direction: str = "CENTER", proctor_alert_active: bool = False) -> bool:
        """
        Main confusion detection logic.
        Returns True if 2+ indicators are active.
        Also handles baseline initialization.
        """
        if not landmarks:
            return False
        
        if not self.baseline_locked:
            self.initialize_baseline(landmarks, current_time, face_count, gaze_direction, proctor_alert_active)
        
        if not self.baseline_locked:
            return False
        
        indicators = 0
        
        if self.detect_brow_furrowing(landmarks):
            indicators += 1
        
        if self.detect_mouth_flatness(landmarks):
            indicators += 1
        
        if self.detect_head_rigidity(landmarks, current_time):
            indicators += 1
        
        return indicators >= 2

    def get_confusion_reasons(self, landmarks: dict, current_time: float) -> list:
        """Returns human-readable reasons for confusion. Returns empty list if not confused."""
        if not landmarks or not self.baseline_locked:
            return []
        
        reasons = []
        
        if self.detect_brow_furrowing(landmarks):
            reasons.append("Brow furrowing detected")
        
        if self.detect_mouth_flatness(landmarks):
            reasons.append("No smile detected")
        
        if self.detect_head_rigidity(landmarks, current_time):
            reasons.append("Prolonged stillness")
        
        if len(reasons) >= 2:
            return reasons
        
        return []

    def get_confusion_details(self, landmarks: dict, current_time: float) -> Dict:
        """
        Returns detailed confusion analysis for debugging
        """
        if not landmarks:
            return {
                'is_confused': False,
                'indicators': {
                    'brow_furrowing': False,
                    'mouth_flat': False,
                    'head_rigid': False
                }
            }
        
        return {
            'is_confused': self.detect_confusion(landmarks, current_time),
            'indicators': {
                'brow_furrowing': self.detect_brow_furrowing(landmarks),
                'mouth_flat': self.detect_mouth_flatness(landmarks),
                'head_rigid': self.detect_head_rigidity(landmarks, current_time)
            }
        }

