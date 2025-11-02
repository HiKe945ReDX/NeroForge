import React from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './pages/Dashboard';
import CareerAtlas from './pages/CareerAtlas';
import AIRoadmap from './pages/AIRoadmap';
import CoachSelection from './pages/CoachSelection';
import MockInterview from './pages/MockInterview';
import NewsFeed from './pages/NewsFeed';

export default function App() {
  const isAuth = !!localStorage.getItem('user_id');
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={isAuth ? <Dashboard /> : <Navigate to="/login" />} />
        <Route path="/career-atlas" element={isAuth ? <CareerAtlas /> : <Navigate to="/login" />} />
        <Route path="/ai-roadmap" element={isAuth ? <AIRoadmap /> : <Navigate to="/login" />} />
        <Route path="/coach" element={isAuth ? <CoachSelection /> : <Navigate to="/login" />} />
        <Route path="/interview" element={isAuth ? <MockInterview /> : <Navigate to="/login" />} />
        <Route path="/news" element={isAuth ? <NewsFeed /> : <Navigate to="/login" />} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}
