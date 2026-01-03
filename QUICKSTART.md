# Quick Start Guide

## Step 1: Install Dependencies

### Backend
```bash
cd backend
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
```

## Step 2: Start Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Backend will run on `http://localhost:8000`

## Step 3: Start Frontend

In a new terminal:
```bash
cd frontend
npm start
```

Frontend will run on `http://localhost:3000`

## Step 4: Test the System

1. Open `http://localhost:3000` in your browser (Student Portal)
   - Allow camera access when prompted
   - You should see your webcam feed
   - Connection status should show "✓ Connected to server"

2. Open `http://localhost:3000/teacher` in another browser window/tab (Teacher Dashboard)
   - You should see the status indicator
   - Timeline chart will populate as states change

## Testing Behaviors

### Test Confusion Detection
- Furrow your eyebrows (bring them closer together)
- Keep your mouth flat (no smile)
- Hold for a few seconds
- Teacher dashboard should show "CONFUSED" (yellow)

### Test Proctor Alert - Gaze
- Look away from camera (left or right)
- Hold for 4+ seconds
- Teacher dashboard should show "PROCTOR_ALERT" (red)

### Test Proctor Alert - Face Count
- Cover your face or move out of frame
- Teacher dashboard should show "PROCTOR_ALERT" (red)

### Test Focused State
- Look at camera with normal expression
- Teacher dashboard should show "FOCUSED" (green)

## Troubleshooting

### Camera not working
- Check browser permissions
- Try a different browser (Chrome recommended)
- Ensure no other app is using the camera

### WebSocket connection failed
- Ensure backend is running on port 8000
- Check browser console for errors
- Verify CORS settings in `backend/main.py`

### No face detection
- Ensure good lighting
- Face the camera directly
- Check MediaPipe is installed correctly

## Architecture Notes

- **Frame Rate**: 10 FPS (configurable in `CameraCapture.jsx`)
- **State Broadcast**: Every 500ms (configurable in `main.py`)
- **Gaze Alert Threshold**: 4 seconds (configurable in `gaze_tracker.py`)
- **Confusion Thresholds**: Adjustable in `confusion_logic.py`

