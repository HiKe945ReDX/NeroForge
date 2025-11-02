import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Signup from './components/Signup';
import Login from './components/Login';
import Dashboard from './components/Dashboard';

// Onboarding Steps
import BasicInfoForm from './pages/Onboarding/BasicInfoForm';
import ResumeUpload from './pages/Onboarding/ResumeUpload';
import SkillsPicker from './pages/Onboarding/SkillsPicker';
import PsychometricIntro from './pages/Onboarding/Intros/PsychometricIntro';
import PsychometricTest from './pages/Onboarding/PsychometricTest';
import EmpathyIntro from './pages/Onboarding/Intros/EmpathyIntro';
import EmpathyTest from './pages/Onboarding/EmpathyTest';
import CareerPreferences from './pages/Onboarding/CareerPreferences';
import CareerSelection from './pages/Onboarding/CareerSelection';
import CareerQuiz from './pages/Onboarding/CareerQuiz';
import CareerDiscovery from './pages/Onboarding/CareerDiscovery';

// Profile & Career Pages
import UserProfile from './pages/Profile/UserProfile';
import CareerAtlas from './pages/CareerAtlas';
import CareerDetail from './pages/Career/CareerDetail';

import './App.css';

function App() {
  const isAuthenticated = !!localStorage.getItem('guidora_user_id');

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/signup" />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/login" element={<Login />} />
        
        {/* ONBOARDING FLOW */}
        <Route path="/onboarding/basic-info" element={<BasicInfoForm />} />
        <Route path="/onboarding/resume-upload" element={<ResumeUpload />} />
        <Route path="/onboarding/skills-picker" element={<SkillsPicker />} />
        <Route path="/onboarding/psychometric" element={<PsychometricIntro />} />
        <Route path="/onboarding/psychometric-test" element={<PsychometricTest />} />
        <Route path="/onboarding/empathy" element={<EmpathyIntro />} />
        <Route path="/onboarding/empathy-test" element={<EmpathyTest />} />
        <Route path="/onboarding/career-preferences" element={<CareerPreferences />} />
        <Route path="/onboarding/career-selection" element={<CareerSelection />} />
        <Route path="/onboarding/career-quiz" element={<CareerQuiz />} />
        <Route path="/onboarding/career-discovery" element={<CareerDiscovery />} />
        
        {/* MAIN APP */}
        <Route path="/profile" element={isAuthenticated ? <UserProfile /> : <Navigate to="/signup" />} />
        <Route path="/career-atlas" element={isAuthenticated ? <CareerAtlas /> : <Navigate to="/signup" />} />
        <Route path="/career/:careerId" element={isAuthenticated ? <CareerDetail /> : <Navigate to="/signup" />} />
        <Route path="/dashboard" element={isAuthenticated ? <Dashboard /> : <Navigate to="/signup" />} />
      </Routes>
    </Router>
  );
}

export default App;
