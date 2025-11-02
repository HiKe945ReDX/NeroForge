'use client';
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

const API_GATEWAY = process.env.REACT_APP_API_GATEWAY_URL || 'https://guidora-api-746485305795.us-central1.run.app';

export default function EmpathyTest() {
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetch(`${API_GATEWAY}/api/empathy/questions`).then(r => r.json()).then(d => { setQuestions(d.questions); setLoading(false); }).catch(e => { toast.error('Failed'); setLoading(false); });
  }, []);

  const handleSubmit = async () => {
    if (Object.keys(answers).length < 15) { toast.error('Answer 15+'); return; }
    setSubmitting(true);
    try {
      const userId = localStorage.getItem('user_id') || 'temp-' + Date.now();
      const res = await fetch(`${API_GATEWAY}/api/empathy/submit`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({user_id: userId, answers}) });
      const data = await res.json();
      localStorage.setItem('empathy', JSON.stringify(data));
      localStorage.setItem('team_role', data.team_role);
      toast.success(`Team Role: ${data.team_role}!`);
      navigate('/onboarding/step-6');
    } catch (e) { toast.error('Error'); } finally { setSubmitting(false); }
  };

  if (loading) return <div className="flex justify-center items-center min-h-screen"><Loader2 className="w-8 h-8 animate-spin" /></div>;

  const progress = (Object.keys(answers).length / questions.length) * 100;
  const quadrants = {say: questions.filter(q => q.quadrant === 'say'), do: questions.filter(q => q.quadrant === 'do'), think: questions.filter(q => q.quadrant === 'think'), feel: questions.filter(q => q.quadrant === 'feel')};
  const labels = {say: '💬 What You Say', do: '🎯 What You Do', think: '🧠 What You Think', feel: '❤️ What You Feel'};

  return (
    <div className="max-w-4xl mx-auto p-8 bg-purple-50 rounded-lg">
      <h1 className="text-4xl font-bold mb-2">👥 Team Compatibility</h1>
      <p className="text-gray-600 mb-6">20 questions across 4 dimensions</p>
      <div className="w-full bg-gray-200 h-2 rounded mb-6"><div className="bg-purple-600 h-2 rounded" style={{width: `${progress}%`}}></div></div>
      <div className="space-y-6">
        {Object.entries(quadrants).map(([q, qs]) => (
          <div key={q} className="bg-white p-4 rounded">
            <h3 className="font-bold text-purple-700 mb-4">{labels[q]}</h3>
            <div className="space-y-3">
              {qs.map(qu => (
                <div key={qu.id} className="border-l-4 border-purple-200 pl-4">
                  <p className="text-sm font-semibold mb-2">{qu.text}</p>
                  <div className="flex gap-2">
                    {qu.options.map((o, i) => (
                      <label key={i} className="flex-1 text-xs"><input type="radio" name={`q${qu.id}`} value={i} checked={answers[qu.id] === i} onChange={e => setAnswers({...answers, [qu.id]: parseInt(e.target.value)})} /> {o}</label>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      <div className="flex gap-4 mt-8">
        <button onClick={() => navigate(-1)} className="px-4 py-2 border rounded">← Back</button>
        <button onClick={handleSubmit} disabled={submitting} className="flex-1 px-4 py-2 bg-purple-600 text-white rounded disabled:opacity-50">{submitting ? 'Analyzing...' : 'Complete'}</button>
      </div>
    </div>
  );
}
