'use client';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, ChevronLeft, Loader2, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const QUESTIONS = [
  { id: 'q1_interests', question: 'What subjects interest you most?', options: [
    { value: 'math_science', label: '🔬 Math & Science' },
    { value: 'art_design', label: '🎨 Art & Design' },
    { value: 'people', label: '👥 People & Society' },
    { value: 'business', label: '💼 Business & Economy' }
  ]},
  { id: 'q2_activities', question: 'What activities make you lose track of time?', options: [
    { value: 'coding_building', label: '💻 Coding & Building' },
    { value: 'creating', label: '✨ Creating & Designing' },
    { value: 'helping', label: '🤝 Helping Others' },
    { value: 'organizing', label: '📋 Organizing & Planning' }
  ]},
  { id: 'q3_work_style', question: 'Do you prefer working...?', options: [
    { value: 'alone', label: '🎯 Independently' },
    { value: 'collaborative', label: '👨‍💼 In teams' },
    { value: 'mixed', label: '⚖️ Mix of both' }
  ]},
  { id: 'q4_impact', question: 'What\'s your ideal impact?', options: [
    { value: 'build_products', label: '🏗️ Build products' },
    { value: 'help_people', label: '❤️ Help people' },
    { value: 'solve_problems', label: '🔍 Solve problems' },
    { value: 'lead_inspire', label: '🌟 Lead & inspire' }
  ]},
  { id: 'q5_environment', question: 'Work environment preference?', options: [
    { value: 'office', label: '🏢 Office-based' },
    { value: 'remote', label: '🏠 Remote' },
    { value: 'outdoors', label: '🌳 Outdoors' },
    { value: 'hybrid', label: '🔄 Hybrid' }
  ]}
];

export default function CareerQuiz() {
  const navigate = useNavigate();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnswer = (answer) => {
    const currentQ = QUESTIONS[currentQuestion];
    setAnswers({ ...answers, [currentQ.id]: answer });
    if (currentQuestion < QUESTIONS.length - 1) {
      setTimeout(() => setCurrentQuestion(currentQuestion + 1), 200);
    }
  };

  const handleSubmit = async () => {
    if (Object.keys(answers).length !== QUESTIONS.length) {
      toast.error('Please answer all questions');
      return;
    }

    setIsAnalyzing(true);

    try {
      const b2URL = process.env.REACT_APP_API_GATEWAY_URL || 'http://localhost:8001';
      const userId = localStorage.getItem('guidora_userid') || `test-user-${Date.now()}`;

      const response = await fetch(`${b2URL}/api/careers/from-discovery`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, ...answers })
      });

      if (!response.ok) throw new Error('Failed to get recommendations');

      const recommendations = await response.json();
      localStorage.setItem('guidora_career_recommendations', JSON.stringify(recommendations));
      localStorage.setItem('guidora_discovery_answers', JSON.stringify(answers));
      localStorage.setItem('guidora_userid', userId);

      toast.success('Analysis complete! 🎉');
      setTimeout(() => navigate('/onboarding/discovery/career-selection', { state: { recommendations } }), 500);
    } catch (err) {
      toast.error(err.message || 'Failed to analyze');
      setIsAnalyzing(false);
    }
  };

  const currentQ = QUESTIONS[currentQuestion];
  const progress = ((currentQuestion + 1) / QUESTIONS.length) * 100;
  const isLastQuestion = currentQuestion === QUESTIONS.length - 1;
  const isFirstQuestion = currentQuestion === 0;

  if (isAnalyzing) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 flex flex-col items-center justify-center p-6">
        <Loader2 className="w-16 h-16 text-purple-600 animate-spin mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Analyzing your responses...</h2>
        <p className="text-gray-600">AI is finding the best career matches for you</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 p-6">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <div className="flex justify-between items-center mb-3">
            <span className="text-sm font-semibold text-gray-700">Question {currentQuestion + 1} of {QUESTIONS.length}</span>
            <span className="text-sm font-semibold text-purple-600">{Math.round(progress)}%</span>
          </div>
          <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-purple-600 to-pink-600 transition-all duration-500" style={{ width: `${progress}%` }}></div>
          </div>
        </div>

        <div className="bg-white rounded-3xl shadow-lg p-10 mb-8">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-8">{currentQ.question}</h2>
          <div className="space-y-3">
            {currentQ.options.map((option) => (
              <button
                key={option.value}
                onClick={() => handleAnswer(option.value)}
                disabled={isAnalyzing}
                className={`w-full p-5 rounded-xl border-2 transition-all font-medium text-lg ${
                  answers[currentQ.id] === option.value ? 'border-purple-600 bg-purple-50 text-purple-900 shadow-lg' : 'border-gray-200 bg-gray-50 text-gray-700 hover:border-purple-300 hover:bg-purple-50/30'
                } disabled:opacity-50`}
              >
                <div className="flex items-center justify-between">
                  <span>{option.label}</span>
                  {answers[currentQ.id] === option.value && <CheckCircle className="w-5 h-5 text-purple-600" />}
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-4">
          <button
            onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
            disabled={isFirstQuestion || isAnalyzing}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-xl font-semibold hover:border-gray-400 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <ChevronLeft className="w-5 h-5" /> Previous
          </button>
          <button
            onClick={() => isLastQuestion ? handleSubmit() : null}
            disabled={!answers[currentQ.id] || isAnalyzing}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg"
          >
            {isAnalyzing ? (<><Loader2 className="w-5 h-5 animate-spin" /> Analyzing...</>) : isLastQuestion ? (<>Get Recommendations <CheckCircle className="w-5 h-5" /></>) : (<>Next <ChevronRight className="w-5 h-5" /></>)}
          </button>
        </div>

        <div className="flex gap-2 justify-center mt-8">
          {QUESTIONS.map((_, idx) => (
            <div key={idx} className={`h-2 rounded-full transition-all ${idx === currentQuestion ? 'bg-purple-600 w-8' : idx < currentQuestion ? 'bg-purple-400 w-2' : 'bg-gray-300 w-2'}`}></div>
          ))}
        </div>
      </div>
    </div>
  );
}
