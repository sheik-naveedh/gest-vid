import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

const LandingPage = () => {
  const [showTitle, setShowTitle] = useState(false);
  const [playButtonVisible, setPlayButtonVisible] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const titleTimer = setTimeout(() => {
      setShowTitle(true);
    }, 300);

    return () => clearTimeout(titleTimer);
  }, []);

  useEffect(() => {
    if (showTitle) {
      const buttonTimer = setTimeout(() => {
        setPlayButtonVisible(true);
      }, 100);

      return () => clearTimeout(buttonTimer);
    }
  }, [showTitle]);

  return (
    <div className="landing-page">
      <div className="background">
        <video className="background-video" autoPlay loop muted>
          <source src="https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4" type="video/mp4" />
        </video>
        <div className="floating-elements">
          <div className="circle"></div>
          <div className="triangle"></div>
          <div className="square"></div>
        </div>
      </div>
      <div className="overlay">
        {showTitle && (
          <div className="title-container">
            <div className="title" style={{ opacity: 1, transform: 'translateY(0)' }}>
              GestVid
            </div>
            <div className="caption" style={{ opacity: 1, transform: 'translateY(0)' }}>
              Hands-Free Media Control
            </div>
          </div>
        )}
        {playButtonVisible && (
          <button className="play-button" onClick={() => navigate('/video-player')}>
            <i className="fas fa-play"></i> Start
          </button>
        )}
      </div>
      <footer>
        <p>© 2024 GestVid. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default LandingPage;
