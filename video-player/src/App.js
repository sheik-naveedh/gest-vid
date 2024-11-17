import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import VideoPlayer from './components/VideoPlayer';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/video-player" element={<VideoPlayer />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
