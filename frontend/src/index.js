import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import StudentApp from './student/App.jsx';
import TeacherApp from './teacher/App.jsx';

// Simple router component - checks pathname on mount and navigation
function AppRouter() {
  const [path, setPath] = useState(window.location.pathname);

  useEffect(() => {
    // Listen for browser navigation (back/forward buttons)
    const handlePopState = () => {
      setPath(window.location.pathname);
    };

    window.addEventListener('popstate', handlePopState);
    
    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, []);

  // Re-check path when component re-renders (handles direct URL changes)
  useEffect(() => {
    if (window.location.pathname !== path) {
      setPath(window.location.pathname);
    }
  });

  if (path.includes('/teacher')) {
    return <TeacherApp />;
  }
  
  return <StudentApp />;
}

// Render app
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <AppRouter />
  </React.StrictMode>
);

