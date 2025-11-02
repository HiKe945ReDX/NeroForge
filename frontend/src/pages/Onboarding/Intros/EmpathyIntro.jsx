'use client';
import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function EmpathyIntro() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 to-purple-100 flex items-center justify-center p-6">
      <div className="max-w-2xl bg-white rounded-2xl shadow-2xl p-10">
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">💝</div>
          <h1 className="text-4xl font-bold text-gray-900 mb-3">Team Compatibility Assessment</h1>
          <p className="text-xl text-gray-600">Discover your emotional intelligence & team role</p>
        </div>

        <div className="space-y-6 mb-8">
          <div className="bg-pink-50 rounded-lg p-6">
            <h3 className="font-bold text-lg text-pink-900 mb-2">💡 What we'll discover:</h3>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-green-500">✓</span>
                <span>Your emotional intelligence score</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500">✓</span>
                <span>How you communicate in teams</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500">✓</span>
                <span>Your natural team role (Leader, Collaborator, Mediator, etc.)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500">✓</span>
                <span>Careers that match your interpersonal style</span>
              </li>
            </ul>
          </div>

          <div className="bg-purple-50 rounded-lg p-6">
            <h3 className="font-bold text-lg text-purple-900 mb-2">🎯 The 4 Quadrants:</h3>
            <div className="grid grid-cols-2 gap-3 text-gray-700 text-sm">
              <div className="flex items-center gap-2">
                <span className="font-bold">SAY:</span>
                <span>Communication style</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-bold">DO:</span>
                <span>Actions & behaviors</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-bold">THINK:</span>
                <span>Internal thoughts</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-bold">FEEL:</span>
                <span>Emotional awareness</span>
              </div>
            </div>
          </div>

          <div className="bg-yellow-50 rounded-lg p-6">
            <h3 className="font-bold text-lg text-yellow-900 mb-2">⏱️ Time & Format:</h3>
            <p className="text-gray-700 mb-2">20 questions • 4-6 minutes</p>
            <p className="text-sm text-gray-600">Answer honestly - this helps us find the best career fit for YOU!</p>
          </div>
        </div>

        <button
          onClick={() => navigate('/onboarding/empathy-test')}
          className="w-full bg-pink-600 text-white py-4 rounded-lg text-lg font-semibold hover:bg-pink-700 transition"
        >
          Begin Assessment →
        </button>
      </div>
    </div>
  );
}
