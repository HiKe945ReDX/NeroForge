import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import AIGuidance from './pages/AIGuidance';
import CareerAtlas from './pages/CareerAtlas';
import Portfolio from './pages/Portfolio';
import InterviewPrep from './pages/InterviewPrep';
import Gamification from './pages/Gamification';
import Profile from './pages/Profile';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/ai-guidance" element={<AIGuidance />} />
            <Route path="/career-atlas" element={<CareerAtlas />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/interview-prep" element={<InterviewPrep />} />
            <Route path="/gamification" element={<Gamification />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </Layout>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App;
