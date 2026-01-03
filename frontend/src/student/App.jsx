import { useState, useCallback } from 'react';
import CameraCapture from './CameraCapture';
import WebSocketClient from './WebSocketClient';

// Student Portal: Captures webcam and streams to backend
export default function StudentApp() {
  const [currentFrame, setCurrentFrame] = useState(null);
  
  // Backend WebSocket URL - adjust port as needed
  const serverUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws/student';

  // Stable callback to prevent camera re-initialization
  const handleFrameReady = useCallback((blob) => {
    setCurrentFrame(blob);
  }, []);

  return (
    <div style={{
      maxWidth: '800px',
      margin: '2rem auto',
      padding: '1rem',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <h1>SmartSession - Student Portal</h1>
      
      <div style={{ marginBottom: '1rem' }}>
        <p>Your camera feed is being analyzed in real-time.</p>
      </div>

      <CameraCapture 
        onFrameReady={handleFrameReady}
        fps={10}
      />

      <WebSocketClient 
        frameBlob={currentFrame}
        serverUrl={serverUrl}
      />
    </div>
  );
}

