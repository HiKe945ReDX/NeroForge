import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/Layout';

// Pages
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
    <AuthProvider>
      <Router>
        <div className="App">
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
              duration: 3000,
              style: {
                background: '#333',
                color: '#fff',
              },
              success: {
                iconTheme: {
                  primary: '#10B981',
                  secondary: '#fff',
                },
              },
              error: {
                iconTheme: {
                  primary: '#EF4444',
                  secondary: '#fff',
                },
              },
            }}
          />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
