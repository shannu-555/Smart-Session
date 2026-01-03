import { useEffect, useState } from 'react';

// Displays current session state with color coding
// States: PROCTOR_ALERT (red), CONFUSED (yellow), FOCUSED (green)
export default function StatusIndicator({ currentState, confusionReasons = [] }) {
  const [stateConfig, setStateConfig] = useState({
    color: '#999',
    label: 'Waiting...',
    message: 'Waiting for session data'
  });

  useEffect(() => {
    if (!currentState) {
      setStateConfig({
        color: '#999',
        label: 'Waiting...',
        message: 'Waiting for session data'
      });
      return;
    }

    switch (currentState) {
      case 'PROCTOR_ALERT':
        setStateConfig({
          color: '#d32f2f',
          label: 'Proctor Alert',
          message: 'Attention required: Face detection or gaze issue detected'
        });
        break;
      case 'CONFUSED':
        setStateConfig({
          color: '#f57c00',
          label: 'Confused',
          message: 'Student appears confused - may need assistance'
        });
        break;
      case 'FOCUSED':
        setStateConfig({
          color: '#388e3c',
          label: 'Focused',
          message: 'Student is engaged and focused'
        });
        break;
      default:
        setStateConfig({
          color: '#999',
          label: 'Unknown',
          message: 'No state data available'
        });
    }
  }, [currentState]);

  return (
    <div>
      <div style={{
        padding: '2rem',
        backgroundColor: stateConfig.color,
        color: 'white',
        borderRadius: '8px',
        textAlign: 'center',
        marginBottom: '2rem',
        boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
      }}>
        <h2 style={{ margin: '0 0 0.5rem 0', fontSize: '2rem' }}>
          {stateConfig.label}
        </h2>
        <p style={{ margin: 0, opacity: 0.9 }}>
          {stateConfig.message}
        </p>
      </div>
      
      {currentState === 'CONFUSED' && confusionReasons.length > 0 && (
        <div style={{
          padding: '1rem',
          backgroundColor: '#fff3cd',
          color: '#856404',
          borderRadius: '4px',
          marginBottom: '2rem',
          border: '1px solid #ffeaa7'
        }}>
          <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>Confusion indicators:</div>
          <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
            {confusionReasons.map((reason, index) => (
              <li key={index} style={{ marginBottom: '0.25rem' }}>{reason}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

