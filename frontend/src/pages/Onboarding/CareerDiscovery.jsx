'use client';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

const API_GATEWAY = process.env.REACT_APP_API_GATEWAY_URL || 'https://guidora-api-746485305795.us-central1.run.app';
const QUESTIONS = [
  {id: 1, text: "What subjects do you enjoy most?", options: ["Math & Algorithms", "Science & Research", "Art & Design", "Writing", "Business"]},
  {id: 2, text: "What makes you lose track of time?", options: ["Building", "Solving", "Learning", "Helping", "Creating"]},
  {id: 3, text: "Do you prefer working...", options: ["Alone", "Teams", "Mix", "Large groups", "Flexible"]},
  {id: 4, text: "Your dream impact...", options: ["Products", "Humanitarian", "Science", "Systems", "People"]},
  {id: 5, text: "Ideal environment...", options: ["Office", "Startup", "Remote", "Outdoors", "Mix"]},
];

export default function CareerDiscovery() {
  const navigate = useNavigate();
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (Object.keys(answers).length < QUESTIONS.length) { toast.error('Answer all'); return; }
    setSubmitting(true);
    try {
      const userId = localStorage.getItem('user_id') || 'temp-' + Date.now();
      const res = await fetch(`${API_GATEWAY}/api/careers/discover`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({user_id: userId, responses: answers}) });
      const data = await res.json();
      localStorage.setItem('discovered_careers', JSON.stringify(data.discovered_domains));
      toast.success('5 careers discovered!');
      navigate('/onboarding/complete');
    } catch (e) { toast.error('Error'); } finally { setSubmitting(false); }
  };

  const progress = (Object.keys(answers).length / QUESTIONS.length) * 100;
  return (
    <div className="max-w-4xl mx-auto p-8 bg-green-50 rounded-lg">
      <h1 className="text-4xl font-bold mb-2">🚀 Career Discovery</h1>
      <p className="text-gray-600 mb-6">AI will suggest 5 perfect paths</p>
      <div className="w-full bg-gray-200 h-2 rounded mb-6"><div className="bg-green-600 h-2 rounded" style={{width: `${progress}%`}}></div></div>
      <div className="space-y-4">
        {QUESTIONS.map((q, i) => (
          <div key={q.id} className="bg-white p-4 rounded">
            <p className="font-bold mb-3">Q{i+1}: {q.text}</p>
            <div className="grid grid-cols-2 gap-2">
              {q.options.map((o, oi) => (
                <label key={oi} className="flex items-center gap-2 p-2 border rounded hover:border-green-400"><input type="radio" name={`q${q.id}`} value={o} checked={answers[q.id] === o} onChange={e => setAnswers({...answers, [q.id]: e.target.value})} /> {o}</label>
              ))}
            </div>
          </div>
        ))}
      </div>
      <div className="flex gap-4 mt-8">
        <button onClick={() => navigate(-1)} className="px-4 py-2 border rounded">← Back</button>
        <button onClick={handleSubmit} disabled={submitting} className="flex-1 px-4 py-2 bg-green-600 text-white rounded disabled:opacity-50">{submitting ? 'Discovering...' : 'Get AI Suggestions'}</button>
      </div>
    </div>
  );
}
