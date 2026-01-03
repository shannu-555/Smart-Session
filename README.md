                              -- -- SMART SESSION -- --

   SmartSession is a full-stack web application built as part of an internship selection assignment.The goal of the project is to analyze a student’s live video feed during an online session and provide real-time, actionable signals to a teacher. The system focuses on engagement monitoring and basic proctoring using computer vision, without relying on black-box emotion models.

The project consists of two interfaces:

1.A Student Portal that captures webcam video and streams it for analysis

2.A Teacher Dashboard that receives live status updates and visualizes session behavior

--- ARCHITECTURE OVERVIEW ---

--- SYSTEM DESIGN ---

The application follows a real-time, event-driven architecture.
Student Browser (React)
   → WebSocket
   → Backend (FastAPI)
   → Computer Vision & State Logic
   → WebSocket
   → Teacher Dashboard (React)
The student’s browser sends video frames to the backend at a controlled rate.
The backend processes each frame, derives a behavioral state, and pushes structured updates to the teacher dashboard.


--- Why WebSockets? --- 

1. WebSockets were chosen because this system requires continuous, low-latency      communication.
2. The student must stream frames continuously

3. The teacher must receive state updates instantly

4. Polling would introduce unnecessary delay and overhead

5. A single persistent connection simplifies synchronization between clients

6. This choice aligns directly with the real-time requirement stated in the assignment.

--- CORE COMPONENTS

--- BACKEND MODULES

The backend is implemented using FastAPI and is intentionally modular. Each file has a single responsibility.

-- main.py
   Starts the FastAPI server and initializes WebSocket routes.

-- websocket_manager.py
   Manages student and teacher connections and message routing.

-- frame_receiver.py
   Receives and decodes video frames sent from the student client.

-- face_detection.py
   Uses MediaPipe to detect faces and extract facial landmarks.

-- gaze_tracker.py
   Estimates gaze direction using eye landmark geometry.

-- confusion_logic.py
   Implements rule-based confusion detection using facial landmarks.

-- state_resolver.py
   Determines the final student state using a fixed priority order.

No backend state is persisted. All decisions are made on live data.

--- FRONTEND MODULES

The frontend is built with React and separated into two logical views.

-- Student Portal

Responsible only for:

   1. Accessing the webcam

   2. Capturing frames at a fixed frame rate

   3. Sending frames to the backend via WebSocket

   4. Handling camera and connection errors

Key files:

1. CameraCapture.jsx

2. WebSocketClient.jsx

3. App.jsx

-- Teacher Dashboard

Responsible only for:

   1. Receiving state updates from the backend

   2. Displaying the current student status

   3. Visualizing session behavior over time

Key files:

1. StatusIndicator.jsx

2. TimelineChart.jsx

3. App.jsx

The frontend does not perform any computer vision or inference.

--- CONFUSION DETECTION LOGIC --- 

The system does not use pre-trained emotion classifiers.
Confusion is defined using explicit, explainable rules based on facial landmarks.

Three indicators are evaluated:

1. Brow Furrowing

   The distance between inner eyebrow landmarks is measured and compared against an initial baseline. A significant reduction indicates brow contraction, often associated with cognitive effort or confusion.

2. Mouth Neutrality

   Mouth landmarks are analyzed to estimate curvature. A nearly flat mouth indicates the absence of a positive expression.

3. Head Stillness

   The movement of the nose tip is tracked over a short time window. Very low movement over time indicates prolonged rigidity.

A confused state is triggered when at least two of these indicators are active simultaneously.
All thresholds are defined as constants and can be adjusted easily.


--- STATE RESOLUTION PRIORITY ---

At any moment, exactly one student state is active.
States are resolved using a fixed priority order:

1. Proctor Alert

   No face detected

   More than one face detected

   Gaze away from screen for more than 4 continuous seconds

2. Confused

   Confusion logic conditions met

3. Focused

   Default state when no alerts are active

This priority system prevents conflicting signals.

--- INSTALLATION & SETUP ---

Prerequisites

   1. Python 3.10+

   2. Node.js 16+

   3.A working webcam

--- BACKEND SETUP ---

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

--- FRONTEND SETUP ---

```bash
cd frontend
npm install
npm start
```

Frontend runs on `http://localhost:3000`
   - Student portal: `http://localhost:3000`
   - Teacher dashboard: `http://localhost:3000/teacher`

--- ENVIRONMENT VARIABLES ---

Create `.env` in `frontend/` (optional):
```
REACT_APP_WS_URL=ws://localhost:8000
```

## Running Locally

1. **Start backend**:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. **Start frontend** (new terminal):
   ```bash
   cd frontend
   npm start
   ```

3. **Open two browser windows**:
   - Window 1: `http://localhost:3000` (Student portal)
   - Window 2: `http://localhost:3000/teacher` (Teacher dashboard)

4. **Allow camera access** in student portal

5. **Observe real-time state updates** in teacher dashboard

EDGE CASES HANDLED

   -- Camera permission denial

   -- Camera disconnects

   -- Temporary face loss

   -- Multiple faces in frame

   -- No face detected

   -- WebSocket disconnect and reconnect

   -- Invalid or dropped frames

Each case results in a predictable and explainable state change.

                        [FILE STRUCTURE]


.
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── websocket_manager.py    # Connection management
│   ├── frame_receiver.py       # Frame decoding
│   ├── face_detection.py       # MediaPipe detection
│   ├── gaze_tracker.py         # Gaze calculation
│   ├── confusion_logic.py      # Confusion rules
│   ├── state_resolver.py       # State priority
│   └── requirements.txt
├── frontend/
│   ├── student/
│   │   ├── App.jsx
│   │   ├── CameraCapture.jsx
│   │   └── WebSocketClient.jsx
│   ├── teacher/
│   │   ├── App.jsx
│   │   ├── StatusIndicator.jsx
│   │   └── TimelineChart.jsx
│   ├── src/
│   │   └── index.js
│   ├── public/
│   │   └── index.html
│   └── package.json
└── README.md



