# Resolves current session state based on priority rules
# States: PROCTOR_ALERT > CONFUSED > FOCUSED

from typing import Dict, Optional
import time
from collections import deque


class StateResolver:
    def __init__(self):
        self.current_state = "FOCUSED"
        self.last_update_time = None
        
        # Time-accumulated violation tracking
        self.face_count_violations = deque()
        self.violation_window_seconds = 2.0
        self.gaze_alert_active = False
        self.gaze_clear_start_time: Optional[float] = None
        self.gaze_clear_duration = 2.0  # Need 2 seconds of valid gaze to clear alert
        
    def resolve(
        self,
        face_count: int,
        gaze_alert: bool,
        is_confused: bool
    ) -> str:
        """
        Determines active state based on priority:
        1. PROCTOR_ALERT: face_count != 1 (time-accumulated) OR gaze deviation (time-accumulated)
        2. CONFUSED: confusion detected
        3. FOCUSED: default state
        
        Returns state string
        """
        current_time = time.time()
        
        cutoff_time = current_time - self.violation_window_seconds
        
        if face_count != 1:
            self.face_count_violations.append(current_time)
        
        while self.face_count_violations and self.face_count_violations[0] < cutoff_time:
            self.face_count_violations.popleft()
        
        face_count_violation = len(self.face_count_violations) > 0
        
        if gaze_alert:
            self.gaze_alert_active = True
            self.gaze_clear_start_time = None
        else:
            if self.gaze_alert_active:
                if self.gaze_clear_start_time is None:
                    self.gaze_clear_start_time = current_time
                elif current_time - self.gaze_clear_start_time >= self.gaze_clear_duration:
                    self.gaze_alert_active = False
                    self.gaze_clear_start_time = None
            else:
                self.gaze_clear_start_time = None
        
        if face_count_violation or self.gaze_alert_active:
            self.current_state = "PROCTOR_ALERT"
            return self.current_state
        
        if is_confused:
            self.current_state = "CONFUSED"
            return self.current_state
        
        self.current_state = "FOCUSED"
        return self.current_state

    def get_state_payload(self, additional_data: Optional[Dict] = None) -> Dict:
        """
        Returns structured JSON payload for teacher dashboard
        """
        import time
        
        payload = {
            'type': 'state_update',
            'state': self.current_state,
            'timestamp': int(time.time() * 1000)
        }
        
        if additional_data:
            payload['details'] = additional_data
        
        return payload

