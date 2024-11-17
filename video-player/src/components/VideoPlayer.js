import React, { useRef, useState, useEffect } from 'react';
import './VideoPlayer.css';

const VideoPlayer = () => {
  const videoRef = useRef(null);
  const [videoSource, setVideoSource] = useState('');
  const [fileName, setFileName] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [volumeLevel, setVolumeLevel] = useState(0.5); // State for volume level
  const [predictedGesture, setPredictedGesture] = useState(''); // State to store the predicted gesture

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const fileURL = URL.createObjectURL(file);
      setVideoSource(fileURL);
      setFileName(file.name);
    }
  };

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.load();
      videoRef.current.play();
      setIsPlaying(true);
      videoRef.current.volume = volumeLevel; // Initialize volume to 0.5
    }
  }, [videoSource]);

  const playPauseVideo = () => {
    if (videoRef.current.paused || videoRef.current.ended) {
      videoRef.current.play();
      setIsPlaying(true);
    } else {
      videoRef.current.pause();
      setIsPlaying(false);
    }
  };

  const handleVolumeChange = (event) => {
    const newVolume = event.target.value;
    setVolumeLevel(newVolume);
    videoRef.current.volume = newVolume; // Update the video element's volume
  };

  const handleProgress = () => {
    const progress = (videoRef.current.currentTime / videoRef.current.duration) * 100;
    document.getElementById('progress-bar').style.width = `${progress}%`;
  };

  // WebSocket for gesture-based control
  useEffect(() => {
    const socket = new WebSocket('ws://localhost:5678');

    socket.onopen = () => {
      console.log('WebSocket connection established');
    };

    socket.onmessage = (event) => {
      const gesture = event.data;
      console.log('Gesture received:', gesture);

      // Update the predicted gesture in state
      setPredictedGesture(gesture);

      // Control video based on gesture
      try {
        if (gesture === 'play') {
          videoRef.current.play();
          setIsPlaying(true);
        } else if (gesture === 'pause') {
          videoRef.current.pause();
          setIsPlaying(false);
        } else if (gesture === 'increase') {
          const newVolume = Math.min(videoRef.current.volume + 0.1, 1);
          videoRef.current.volume = newVolume;
          setVolumeLevel(newVolume); // Sync volume with slider
        } else if (gesture === 'decrease') {
          const newVolume = Math.max(videoRef.current.volume - 0.1, 0);
          videoRef.current.volume = newVolume;
          setVolumeLevel(newVolume); // Sync volume with slider
        } else if (gesture === 'forward') {
          videoRef.current.currentTime = Math.min(videoRef.current.currentTime + 10, videoRef.current.duration);
        } else if (gesture === 'rewind') {
          videoRef.current.currentTime = Math.max(videoRef.current.currentTime - 10, 0);
        }
      } catch (error) {
        console.error("An error occurred:", error);
        // Suppressing errors for undefined gestures
      }
    };

    socket.onclose = () => {
      console.log('WebSocket connection closed');
    };

    return () => {
      socket.close();
    };
  }, []);

  return (
    <div className="video-player">
      {videoSource && (
        <>
          <video ref={videoRef} onTimeUpdate={handleProgress} className="video-element" controls>
            <source src={videoSource} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
          <div className="file-name">{fileName}</div>
          <div className="controls">
            <button className={`play-pause-button ${isPlaying ? 'playing' : ''}`} onClick={playPauseVideo}>
              {isPlaying ? '❚❚' : '►'}
            </button>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={volumeLevel} // Sync the slider value with volumeLevel state
              onChange={handleVolumeChange}
            />
          </div>
          <div className="progress-container">
            <div id="progress-bar"></div>
          </div>

          {/* Predicted gesture display */}
          <div className="gesture-display">
            Gesture: {predictedGesture || "No gesture detected"}
          </div>
        </>
      )}
      {!videoSource && (
        <div className="file-upload-center">
          <label className="file-upload-label">Choose File</label>
          <label className="custom-file-input">
            <input type="file" accept="video/*" onChange={handleFileChange} className="file-input" />
            📂
          </label>
        </div>
      )}
      {videoSource && (
        <div className="file-upload-bottom-left">
          <label className="file-upload-label-small">Choose File</label>
          <label className="custom-file-input-small">
            <input type="file" accept="video/*" onChange={handleFileChange} className="file-input" />
            📂
          </label>
        </div>
      )}
    </div>
  );
};

export default VideoPlayer;
