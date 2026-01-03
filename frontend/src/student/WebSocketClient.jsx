import { useEffect, useRef, useState } from 'react';

// Manages WebSocket connection to backend
// Handles reconnection logic and frame transmission
export default function WebSocketClient({ frameBlob, serverUrl }) {
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const maxReconnectAttempts = 5;
  const reconnectDelay = 2000;

  // Convert blob to base64 for WebSocket transmission
  const blobToBase64 = (blob) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  };

  // Establish WebSocket connection
  const connect = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const ws = new WebSocket(serverUrl);
      
      ws.onopen = () => {
        setConnectionStatus('connected');
        setReconnectAttempts(0);
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
      };

      ws.onerror = (error) => {
        setConnectionStatus('error');
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        setConnectionStatus('disconnected');
        
        // Attempt reconnection if not manually closed
        if (reconnectAttempts < maxReconnectAttempts) {
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectAttempts(prev => prev + 1);
            connect();
          }, reconnectDelay);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      setConnectionStatus('error');
      console.error('Failed to create WebSocket:', error);
    }
  };

  // Connect on mount
  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [serverUrl]);

  // Send frame when available
  useEffect(() => {
    if (!frameBlob || connectionStatus !== 'connected') {
      return;
    }

    const sendFrame = async () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        try {
          const base64 = await blobToBase64(frameBlob);
          wsRef.current.send(JSON.stringify({
            type: 'frame',
            data: base64,
            timestamp: Date.now()
          }));
        } catch (error) {
          console.error('Failed to send frame:', error);
        }
      }
    };

    sendFrame();
  }, [frameBlob, connectionStatus]);

  return (
    <div style={{ marginTop: '1rem' }}>
      <div style={{
        padding: '0.5rem',
        backgroundColor: connectionStatus === 'connected' ? '#dfd' : '#fdd',
        color: connectionStatus === 'connected' ? '#060' : '#600',
        borderRadius: '4px',
        fontSize: '0.9rem'
      }}>
        {connectionStatus === 'connected' && '✓ Connected to server'}
        {connectionStatus === 'disconnected' && '✗ Disconnected'}
        {connectionStatus === 'error' && '✗ Connection error'}
        {reconnectAttempts > 0 && reconnectAttempts < maxReconnectAttempts && 
          ` (Reconnecting ${reconnectAttempts}/${maxReconnectAttempts})...`}
      </div>
    </div>
  );
}

