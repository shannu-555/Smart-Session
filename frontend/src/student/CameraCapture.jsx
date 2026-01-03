import { useEffect, useRef, useState } from 'react';

// Captures webcam frames at controlled FPS
// Sends frames via callback when ready
export default function CameraCapture({ onFrameReady, fps = 10 }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);
  const onFrameReadyRef = useRef(onFrameReady);
  const [error, setError] = useState(null);
  const [isActive, setIsActive] = useState(false);

  // Keep callback ref up to date without triggering effects
  useEffect(() => {
    onFrameReadyRef.current = onFrameReady;
  }, [onFrameReady]);

  // Request camera access and start stream - runs once on mount
  useEffect(() => {
    let mounted = true;
    
    const startCamera = async () => {
      try {
        setError(null);
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 640, height: 480, facingMode: 'user' }
        });
        
        if (!mounted) {
          // Component unmounted, stop the stream
          stream.getTracks().forEach(track => track.stop());
          return;
        }
        
        streamRef.current = stream;
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
          if (mounted) {
            setIsActive(true);
          }
        }
      } catch (err) {
        if (!mounted) return;
        
        if (err.name === 'NotAllowedError') {
          setError('Camera permission denied. Please allow camera access.');
        } else if (err.name === 'NotFoundError') {
          setError('No camera found. Please connect a camera.');
        } else {
          setError(`Camera error: ${err.message}`);
        }
        setIsActive(false);
      }
    };

    startCamera();

    // Cleanup on unmount
    return () => {
      mounted = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    };
  }, []);

  // Capture frames at specified FPS
  useEffect(() => {
    if (!isActive || !videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    // Set canvas size to match video
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const frameInterval = 1000 / fps;

    intervalRef.current = setInterval(() => {
      if (video.readyState === video.HAVE_ENOUGH_DATA) {
        // Draw current video frame to canvas
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert canvas to blob for transmission
        canvas.toBlob((blob) => {
          if (blob && onFrameReadyRef.current) {
            onFrameReadyRef.current(blob);
          }
        }, 'image/jpeg', 0.85);
      }
    }, frameInterval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isActive, fps]);

  // Handle camera disconnect
  useEffect(() => {
    if (!videoRef.current) return;

    const video = videoRef.current;
    const handleEnded = () => {
      setError('Camera disconnected. Please reconnect your camera.');
      setIsActive(false);
    };

    video.addEventListener('ended', handleEnded);
    return () => video.removeEventListener('ended', handleEnded);
  }, []);

  return (
    <div style={{ position: 'relative', width: '100%', maxWidth: '640px' }}>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        style={{
          width: '100%',
          display: isActive ? 'block' : 'none',
          transform: 'scaleX(-1)' // Mirror for user
        }}
      />
      <canvas ref={canvasRef} style={{ display: 'none' }} />
      
      {error && (
        <div style={{
          padding: '1rem',
          backgroundColor: '#fee',
          color: '#c33',
          borderRadius: '4px',
          marginTop: '1rem'
        }}>
          {error}
        </div>
      )}
      
      {!isActive && !error && (
        <div style={{
          padding: '2rem',
          textAlign: 'center',
          backgroundColor: '#f5f5f5',
          borderRadius: '4px'
        }}>
          Starting camera...
        </div>
      )}
    </div>
  );
}

