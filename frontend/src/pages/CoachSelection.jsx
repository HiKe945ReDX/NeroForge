import React, { useState, useEffect } from 'react';
import { Zap, Heart, Target, Users, TrendingUp } from 'lucide-react';

const COACHES = [
  { id: 1, name: 'Sarah', emoji: '💪', role: 'Motivator', desc: 'Energetic & Uplifting', style: 'You\'re CRUSHING it! Keep that momentum! ��' },
  { id: 2, name: 'Marcus', emoji: '🎯', role: 'Strategist', desc: 'Analytical & Structured', style: 'Let\'s break this down step-by-step.' },
  { id: 3, name: 'Anjali', emoji: '🧘', role: 'Mentor', desc: 'Patient & Supportive', style: 'It\'s a journey, not a race.' },
  { id: 4, name: 'Alex', emoji: '⚡', role: 'Challenger', desc: 'Direct & No-Nonsense', style: 'You\'re behind. Get back to work!' },
  { id: 5, name: 'Jordan', emoji: '🤝', role: 'Collaborator', desc: 'Friendly & Balanced', style: 'Let\'s tackle this together.' },
];

export default function CoachSelection() {
  const [selectedCoach, setSelectedCoach] = useState(null);
  const [aiMatch, setAiMatch] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    const persona = { openness: 65, conscientiousness: 72, extraversion: 58, agreeableness: 70, neuroticism: 40 };
    fetch('https://guidora-backend-746485305795.us-central1.run.app/api/coach/select', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(persona),
    })
      .then(r => r.json())
      .then(data => setAiMatch(data.id))
      .catch(() => setAiMatch(2));
    setLoading(false);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <h1 className="text-4xl font-bold text-white mb-2">🏆 Choose Your AI Coach</h1>
      <p className="text-slate-300 mb-8">Your roadmap is ready! Now, who should guide you?</p>
      
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-12">
        {COACHES.map(coach => (
          <div
            key={coach.id}
            onClick={() => setSelectedCoach(coach.id)}
            className={`cursor-pointer p-6 rounded-lg transition transform hover:scale-105 ${
              selectedCoach === coach.id
                ? 'bg-emerald-600 ring-4 ring-emerald-400'
                : aiMatch === coach.id
                ? 'bg-purple-600 ring-2 ring-purple-400'
                : 'bg-slate-700 hover:bg-slate-600'
            }`}
          >
            <div className="text-5xl mb-3">{coach.emoji}</div>
            <h3 className="text-xl font-bold text-white">{coach.name}</h3>
            <p className="text-sm text-slate-200">{coach.role}</p>
            <p className="text-xs text-slate-300 mt-2">{coach.desc}</p>
            <blockquote className="text-xs italic text-slate-300 mt-3">"{coach.style}"</blockquote>
            {aiMatch === coach.id && <p className="text-xs text-yellow-300 mt-2">✨ AI Recommended</p>}
          </div>
        ))}
      </div>

      {selectedCoach && (
        <div className="bg-slate-700 rounded-lg p-8 text-white text-center max-w-2xl mx-auto">
          <p className="text-lg mb-4">Great choice! Let's get started with <strong>{COACHES[selectedCoach - 1].name}</strong>.</p>
          <button className="px-8 py-3 bg-emerald-600 text-white rounded font-bold hover:bg-emerald-500 mr-4">
            Start Roadmap
          </button>
          <button className="px-8 py-3 bg-purple-600 text-white rounded font-bold hover:bg-purple-500">
            → Next
          </button>
        </div>
      )}
    </div>
  );
}
