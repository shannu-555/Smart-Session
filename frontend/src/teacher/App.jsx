import { useEffect, useState, useRef } from 'react';
import StatusIndicator from './StatusIndicator';
import TimelineChart from './TimelineChart';

// Teacher Dashboard: Receives live insights from backend
export default function TeacherApp() {
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [studentStatus, setStudentStatus] = useState(null);
  const [confusionReasons, setConfusionReasons] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [lastUpdateTime, setLastUpdateTime] = useState(null);
  const wsRef = useRef(null);
  const studentStatusRef = useRef(null);

  // Backend WebSocket URL
  const serverUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws/teacher';

  // Update timeline every second with current state
  useEffect(() => {
    if (connectionStatus !== 'connected') {
      setTimeline([]);
      return;
    }

    const intervalId = setInterval(() => {
      const now = Date.now();
      const cutoffTime = now - 60000; // 60 seconds ago
      const currentSecond = Math.floor(now / 1000) * 1000;

      setTimeline(prev => {
        // Remove entries older than 60 seconds
        let filtered = prev.filter(entry => entry.timestamp >= cutoffTime);
        
        // Add current state for this second (if we have a state)
        if (studentStatusRef.current) {
          const lastEntry = filtered[filtered.length - 1];
          
          // Add entry if this is a new second
          if (!lastEntry || lastEntry.timestamp < currentSecond) {
            filtered = [...filtered, { state: studentStatusRef.current, timestamp: currentSecond }];
          } else if (lastEntry.timestamp === currentSecond) {
            // Update existing entry if state changed
            if (lastEntry.state !== studentStatusRef.current) {
              filtered = [...filtered.slice(0, -1), { state: studentStatusRef.current, timestamp: currentSecond }];
            }
          }
        }
        
        return filtered;
      });
    }, 1000);

    return () => clearInterval(intervalId);
  }, [connectionStatus]);

  useEffect(() => {
    const websocket = new WebSocket(serverUrl);

    websocket.onopen = () => {
      console.log('Teacher dashboard connected');
      setConnectionStatus('connected');
    };

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'state_update') {
          const newState = data.state;
          const timestamp = data.timestamp || Date.now();
          const reasons = data.details?.confusion_reasons || [];
          
          setStudentStatus(newState);
          setConfusionReasons(reasons);
          studentStatusRef.current = newState;
          setLastUpdateTime(timestamp);
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionStatus('disconnected');
    };

    websocket.onclose = () => {
      console.log('Teacher dashboard disconnected');
      setConnectionStatus('disconnected');
      setStudentStatus(null);
      setConfusionReasons([]);
      studentStatusRef.current = null;
    };

    wsRef.current = websocket;

    return () => {
      websocket.close();
    };
  }, [serverUrl]);

  return (
    <div style={{
      maxWidth: '1200px',
      margin: '2rem auto',
      padding: '1rem',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <h1>SmartSession - Teacher Dashboard</h1>
      
      <div style={{ marginBottom: '1rem', fontSize: '0.9rem', color: '#666' }}>
        Connection: {connectionStatus === 'connected' ? '✓ Connected' : connectionStatus === 'connecting' ? '⏳ Connecting...' : '✗ Disconnected'}
        {lastUpdateTime && connectionStatus === 'connected' && (
          <span style={{ marginLeft: '1rem' }}>
            Last update: {new Date(lastUpdateTime).toLocaleTimeString()}
          </span>
        )}
      </div>
      
      {connectionStatus === 'connected' ? (
        <>
          <StatusIndicator currentState={studentStatus} confusionReasons={confusionReasons} />
          <TimelineChart timeline={timeline} />
        </>
      ) : (
        <div style={{
          padding: '2rem',
          backgroundColor: '#f5f5f5',
          color: '#666',
          borderRadius: '8px',
          textAlign: 'center',
          marginBottom: '2rem'
        }}>
          {connectionStatus === 'connecting' ? 'Connecting to backend...' : 'Disconnected from backend'}
        </div>
      )}
    </div>
  );
}

