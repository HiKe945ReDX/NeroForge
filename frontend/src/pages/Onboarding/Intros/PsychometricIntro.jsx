'use client';
import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function PsychometricIntro() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 flex items-center justify-center p-6">
      <div className="max-w-2xl bg-white rounded-2xl shadow-2xl p-10">
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🧠</div>
          <h1 className="text-4xl font-bold text-gray-900 mb-3">Discover Your Work Style</h1>
          <p className="text-xl text-gray-600">Understand how you work best</p>
        </div>

        <div className="space-y-6 mb-8">
          <div className="bg-indigo-50 rounded-lg p-6">
            <h3 className="font-bold text-lg text-indigo-900 mb-2">📊 What we'll discover:</h3>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-green-500">✓</span>
                <span>Your personality traits and strengths</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500">✓</span>
                <span>How you approach problem-solving</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500">✓</span>
                <span>Your ideal work environment</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500">✓</span>
                <span>Career paths that match your style</span>
              </li>
            </ul>
          </div>

          <div className="bg-yellow-50 rounded-lg p-6">
            <h3 className="font-bold text-lg text-yellow-900 mb-2">⏱️ Time & Format:</h3>
            <p className="text-gray-700 mb-2">25 questions • 5-7 minutes</p>
            <p className="text-sm text-gray-600">There are no right or wrong answers - just be yourself!</p>
          </div>

          <div className="bg-green-50 rounded-lg p-6">
            <h3 className="font-bold text-lg text-green-900 mb-2">🔒 Your privacy matters:</h3>
            <p className="text-gray-700">Your responses are confidential and used only to personalize your career guidance.</p>
          </div>
        </div>

        <button
          onClick={() => navigate('/onboarding/psychometric-test')}
          className="w-full bg-indigo-600 text-white py-4 rounded-lg text-lg font-semibold hover:bg-indigo-700 transition"
        >
          Let's Get Started! →
        </button>
      </div>
    </div>
  );
}
