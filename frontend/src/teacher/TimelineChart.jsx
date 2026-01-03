import { useEffect, useRef } from 'react';

// Displays session timeline with color-coded states
// Timeline shows rolling 60-second buffer with one entry per second
export default function TimelineChart({ timeline }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    if (timeline.length === 0) {
      // Draw empty state
      ctx.fillStyle = '#f5f5f5';
      ctx.fillRect(0, 0, width, height);
      return;
    }

    // Color mapping
    const stateColors = {
      'PROCTOR_ALERT': '#d32f2f',
      'CONFUSED': '#f57c00',
      'FOCUSED': '#388e3c'
    };

    // Calculate time range
    const now = Date.now();
    const timeWindow = 60000; // 60 seconds
    const startTime = now - timeWindow;

    // Draw timeline segments
    timeline.forEach((entry, index) => {
      const { state, timestamp } = entry;
      const nextEntry = timeline[index + 1];
      const endTime = nextEntry ? nextEntry.timestamp : now;

      const x1 = Math.max(0, ((timestamp - startTime) / timeWindow) * width);
      const x2 = Math.min(width, ((endTime - startTime) / timeWindow) * width);

      ctx.fillStyle = stateColors[state] || '#999';
      ctx.fillRect(x1, 0, x2 - x1, height);
    });

    // Draw time labels
    ctx.fillStyle = '#333';
    ctx.font = '12px system-ui';
    ctx.textAlign = 'center';
    
    for (let i = 0; i <= 6; i++) {
      const time = startTime + (i * timeWindow / 6);
      const x = (i / 6) * width;
      const secondsAgo = Math.round((now - time) / 1000);
      ctx.fillText(`${secondsAgo}s ago`, x, height - 5);
    }
  }, [timeline]);

  if (timeline.length === 0) {
    return null;
  }

  return (
    <div>
      <h3 style={{ marginBottom: '0.5rem' }}>Session Timeline (Last 60 seconds)</h3>
      <canvas
        ref={canvasRef}
        width={800}
        height={40}
        style={{
          width: '100%',
          maxWidth: '800px',
          border: '1px solid #ddd',
          borderRadius: '4px',
          backgroundColor: '#f5f5f5'
        }}
      />
      <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#666' }}>
        <span style={{ display: 'inline-block', marginRight: '1rem' }}>
          <span style={{ display: 'inline-block', width: '12px', height: '12px', backgroundColor: '#d32f2f', marginRight: '4px', verticalAlign: 'middle' }}></span>
          Proctor Alert
        </span>
        <span style={{ display: 'inline-block', marginRight: '1rem' }}>
          <span style={{ display: 'inline-block', width: '12px', height: '12px', backgroundColor: '#f57c00', marginRight: '4px', verticalAlign: 'middle' }}></span>
          Confused
        </span>
        <span style={{ display: 'inline-block' }}>
          <span style={{ display: 'inline-block', width: '12px', height: '12px', backgroundColor: '#388e3c', marginRight: '4px', verticalAlign: 'middle' }}></span>
          Focused
        </span>
      </div>
    </div>
  );
}

