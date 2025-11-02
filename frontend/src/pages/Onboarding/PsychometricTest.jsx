'use client';
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, ChevronRight } from 'lucide-react';
import toast from 'react-hot-toast';

const API_GATEWAY = process.env.REACT_APP_API_GATEWAY_URL || 'https://guidora-api-746485305795.us-central1.run.app';

export default function PsychometricTest() {
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetch(`${API_GATEWAY}/api/psychometric/questions`).then(r => r.json()).then(d => { setQuestions(d.questions); setLoading(false); }).catch(e => { toast.error('Failed'); setLoading(false); });
  }, []);

  const handleSubmit = async () => {
    if (Object.keys(answers).length < questions.length) { toast.error('Answer all'); return; }
    setSubmitting(true);
    try {
      const userId = localStorage.getItem('user_id') || 'temp-' + Date.now();
      const res = await fetch(`${API_GATEWAY}/api/psychometric/complete`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({user_id: userId, answers}) });
      const data = await res.json();
      localStorage.setItem('psychometric', JSON.stringify(data));
      toast.success('Complete!');
      navigate('/onboarding/step-5');
    } catch (e) { toast.error('Error'); } finally { setSubmitting(false); }
  };

  if (loading) return <div className="flex justify-center items-center min-h-screen"><Loader2 className="w-8 h-8 animate-spin" /></div>;

  const progress = (Object.keys(answers).length / questions.length) * 100;
  return (
    <div className="max-w-4xl mx-auto p-8 bg-blue-50 rounded-lg">
      <h1 className="text-4xl font-bold mb-2">🌟 Discover Your Work Style</h1>
      <p className="text-gray-600 mb-6">15 quick questions</p>
      <div className="w-full bg-gray-200 h-2 rounded mb-6"><div className="bg-blue-600 h-2 rounded" style={{width: `${progress}%`}}></div></div>
      <div className="space-y-4">
        {questions.map((q, i) => (
          <div key={q.id} className="bg-white p-4 rounded">
            <p className="font-bold mb-3">Q{i+1}: {q.text}</p>
            <div className="flex gap-2">
              {[1,2,3,4,5].map(v => (
                <label key={v} className="flex-1"><input type="radio" name={`q${q.id}`} value={v} checked={answers[q.id] === v} onChange={e => setAnswers({...answers, [q.id]: parseInt(e.target.value)})} /> {['❌','😕','😐','😊','😄'][v-1]}</label>
              ))}
            </div>
          </div>
        ))}
      </div>
      <div className="flex gap-4 mt-8">
        <button onClick={() => navigate(-1)} className="px-4 py-2 border rounded">← Back</button>
        <button onClick={handleSubmit} disabled={submitting} className="flex-1 px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50">{submitting ? 'Analyzing...' : 'Complete'}</button>
      </div>
    </div>
  );
}
