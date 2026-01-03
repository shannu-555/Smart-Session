# FastAPI WebSocket server
# Coordinates all modules and handles client connections

import asyncio
import time
import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from websocket_manager import WebSocketManager
from frame_receiver import decode_frame, validate_frame
from face_detection import FaceDetector
from gaze_tracker import GazeTracker
from confusion_logic import ConfusionDetector
from state_resolver import StateResolver

app = FastAPI()

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize modules
ws_manager = WebSocketManager()
face_detector = FaceDetector()
gaze_tracker = GazeTracker()
confusion_detector = ConfusionDetector()
state_resolver = StateResolver()

# Processing state
processing_active = False
last_state_broadcast_time = 0
state_broadcast_interval = 0.5  # Broadcast state every 500ms
pending_broadcast = None  # Store pending broadcast task


@app.websocket("/ws/student")
async def student_endpoint(websocket: WebSocket):
    await ws_manager.connect_student(websocket)
    global processing_active
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get('type') == 'frame':
                frame_data = data.get('data')
                timestamp = data.get('timestamp', time.time() * 1000)
                
                # Decode frame
                frame_array = decode_frame(frame_data)
                if not validate_frame(frame_array):
                    continue
                
                # Convert to BGR for OpenCV
                frame_bgr = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
                
                # Process frame asynchronously
                processing_active = True
                await process_frame_async(frame_bgr, timestamp / 1000.0)  # Convert to seconds
                processing_active = False
                
    except WebSocketDisconnect:
        ws_manager.disconnect_student(websocket)
    except Exception as e:
        print(f"Student WebSocket error: {e}")
        ws_manager.disconnect_student(websocket)


@app.websocket("/ws/teacher")
async def teacher_endpoint(websocket: WebSocket):
    await ws_manager.connect_teacher(websocket)
    
    try:
        # Send current state immediately on connection
        current_payload = state_resolver.get_state_payload()
        await websocket.send_json(current_payload)
        
        # Keep connection alive
        while True:
            await asyncio.sleep(1)
            # State updates are broadcast by process_frame
            
    except WebSocketDisconnect:
        ws_manager.disconnect_teacher(websocket)
    except Exception as e:
        print(f"Teacher WebSocket error: {e}")
        ws_manager.disconnect_teacher(websocket)


async def process_frame_async(frame: np.ndarray, current_time: float):
    """
    Main processing pipeline (async version):
    1. Detect faces
    2. Track gaze
    3. Detect confusion
    4. Resolve state
    5. Broadcast to teachers
    """
    global last_state_broadcast_time
    
    # Step 1: Face detection
    detection_result = face_detector.detect(frame)
    face_count = detection_result['face_count']
    landmarks = detection_result['landmarks']
    
    # Step 2: Gaze tracking (only if face detected)
    gaze_status = {'alert_triggered': False, 'direction': None}
    if landmarks:
        gaze_status = gaze_tracker.get_status(landmarks)
    
    # Step 3: Confusion detection (only if face detected)
    is_confused = False
    confusion_reasons = []
    if landmarks:
        # Check if proctor alert is active (for baseline initialization)
        proctor_alert_active = (face_count != 1 or gaze_status['alert_triggered'])
        
        is_confused = confusion_detector.detect_confusion(
            landmarks, 
            current_time,
            face_count=face_count,
            gaze_direction=gaze_status['direction'] or "CENTER",
            proctor_alert_active=proctor_alert_active
        )
        
        # Get confusion reasons if confused
        if is_confused:
            confusion_reasons = confusion_detector.get_confusion_reasons(landmarks, current_time)
    
    # Step 4: Resolve state
    new_state = state_resolver.resolve(
        face_count=face_count,
        gaze_alert=gaze_status['alert_triggered'],
        is_confused=is_confused
    )
    
    # Step 5: Broadcast state update (throttled)
    current_time_ms = time.time()
    if current_time_ms - last_state_broadcast_time >= state_broadcast_interval:
        payload = state_resolver.get_state_payload({
            'face_count': face_count,
            'gaze_direction': gaze_status['direction'],
            'confusion_detected': is_confused,
            'confusion_reasons': confusion_reasons if is_confused else []
        })
        
        # Broadcast to teachers
        await ws_manager.broadcast_to_teachers(payload)
        last_state_broadcast_time = current_time_ms


@app.get("/")
def root():
    return {"message": "SmartSession Backend API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}

