'use client';
import React, { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

export default function CareerPreferences({ onComplete }) {
  const [step, setStep] = useState('goal');
  const [careerGoal, setCareerGoal] = useState(null);
  const [discoveryAnswers, setDiscoveryAnswers] = useState({});
  const [suggestedCareers, setSuggestedCareers] = useState([]);
  const [selectedCareers, setSelectedCareers] = useState([]);
  const [loading, setLoading] = useState(false);

  const questions = [
    { id: 'q1', question: 'What subjects interest you?', options: ['Tech', 'Data', 'Design', 'Business', 'Science', 'People'] },
    { id: 'q2', question: 'What activities engage you?', options: ['Building', 'Solving', 'Creating', 'Helping', 'Analyzing', 'Leading'] },
    { id: 'q3', question: 'Preferred work style?', options: ['Alone', 'Team', 'Mix'] },
    { id: 'q4', question: 'Your dream impact?', options: ['Products', 'People', 'Knowledge', 'Problems'] },
    { id: 'q5', question: 'Work environment?', options: ['Office', 'Remote', 'Hybrid', 'Outdoors'] }
  ];

  const handleGoalSelection = (goal) => {
    if (goal === 'explore') {
      setStep('discovery');
    } else {
      setCareerGoal(goal);
      setStep('select');
    }
  };

  const handleAnswerQuestion = async (qId, answer) => {
    const newAnswers = { ...discoveryAnswers, [qId]: answer };
    setDiscoveryAnswers(newAnswers);

    if (Object.keys(newAnswers).length === 5) {
      setLoading(true);
      try {
        const response = await axios.post(
          `${process.env.REACT_APP_API_BASE_URL}/api/careers/discover/suggest-careers`,
          { userId: localStorage.getItem('userId'), answers: newAnswers }
        );
        setSuggestedCareers(response.data.careers || []);
        setStep('select');
      } catch (error) {
        toast.error('Failed to generate suggestions');
        console.error(error);
      } finally {
        setLoading(false);
      }
    }
  };

  const savePreferences = async () => {
    if (selectedCareers.length === 0) {
      toast.error('Select at least 1 career');
      return;
    }

    setLoading(true);
    try {
      await axios.post(
        `${process.env.REACT_APP_API_BASE_URL}/api/users/preferences/save`,
        {
          userId: localStorage.getItem('userId'),
          careers: selectedCareers,
          industries: [],
          workStyle: 'hybrid',
          location: 'worldwide'
        }
      );
      toast.success('Preferences saved!');
      onComplete({ careers: selectedCareers });
    } catch (error) {
      toast.error('Failed to save');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 to-blue-600 p-8">
      {/* GOAL CHECK */}
      {step === 'goal' && (
        <div className="max-w-2xl mx-auto bg-white rounded-3xl shadow-2xl p-12">
          <h1 className="text-4xl font-bold mb-4">Career Goals</h1>
          <p className="text-lg text-gray-600 mb-12">Do you have a career goal in mind?</p>
          
          <div className="space-y-4">
            <button onClick={() => handleGoalSelection('goal')} className="w-full p-6 bg-green-50 border-2 border-green-300 rounded-2xl text-left">
              <div className="text-2xl font-bold text-green-700">🎯 I have a goal</div>
              <p className="text-green-600">I know what career I want</p>
            </button>
            <button onClick={() => handleGoalSelection('ideas')} className="w-full p-6 bg-blue-50 border-2 border-blue-300 rounded-2xl text-left">
              <div className="text-2xl font-bold text-blue-700">🤔 I have ideas</div>
              <p className="text-blue-600">I have a few options</p>
            </button>
            <button onClick={() => handleGoalSelection('explore')} className="w-full p-6 bg-purple-50 border-2 border-purple-300 rounded-2xl text-left">
              <div className="text-2xl font-bold text-purple-700">🌟 Help me explore</div>
              <p className="text-purple-600">AI-guided discovery</p>
            </button>
          </div>
        </div>
      )}

      {/* DISCOVERY QUIZ */}
      {step === 'discovery' && (
        <div className="max-w-2xl mx-auto">
          {Object.keys(discoveryAnswers).length < 5 ? (
            <div className="bg-white rounded-3xl shadow-2xl p-8">
              {questions[Object.keys(discoveryAnswers).length] && (
                <>
                  <div className="mb-8">
                    <div className="flex justify-between mb-2">
                      <span className="font-bold">Q{Object.keys(discoveryAnswers).length + 1}/5</span>
                      <span>{Math.round((Object.keys(discoveryAnswers) / 5) * 100)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-indigo-600 h-2 rounded-full transition-all"
                        style={{ width: `${(Object.keys(discoveryAnswers) / 5) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                  <h2 className="text-3xl font-bold mb-6">{questions[Object.keys(discoveryAnswers).length].question}</h2>
                  <div className="grid grid-cols-2 gap-3">
                    {questions[Object.keys(discoveryAnswers).length].options.map(opt => (
                      <button
                        key={opt}
                        onClick={() => handleAnswerQuestion(questions[Object.keys(discoveryAnswers).length].id, opt)}
                        className="p-4 border-2 border-gray-200 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition-all font-semibold"
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-3xl shadow-2xl p-8 text-center">
              <p className="text-xl text-gray-600 mb-4">Generating suggestions...</p>
              {loading ? <div className="text-indigo-600 animate-spin">⏳</div> : null}
            </div>
          )}
        </div>
      )}

      {/* SELECT CAREERS */}
      {step === 'select' && (
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white mb-8">Select Your Careers</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            {suggestedCareers.map((career, i) => (
              <div
                key={i}
                onClick={() => {
                  if (selectedCareers.includes(career.id)) {
                    setSelectedCareers(selectedCareers.filter(c => c !== career.id));
                  } else if (selectedCareers.length < 10) {
                    setSelectedCareers([...selectedCareers, career.id]);
                  }
                }}
                className={`p-6 rounded-2xl border-2 cursor-pointer transition-all ${
                  selectedCareers.includes(career.id)
                    ? 'border-indigo-600 bg-indigo-50'
                    : 'border-gray-200 bg-white hover:border-indigo-300'
                }`}
              >
                <h3 className="font-bold text-lg text-gray-900">{career.title}</h3>
                <p className="text-sm text-gray-600 mt-2">{career.description}</p>
                {selectedCareers.includes(career.id) && <span className="text-2xl mt-3">✅</span>}
              </div>
            ))}
          </div>

          <button
            onClick={savePreferences}
            disabled={loading || selectedCareers.length === 0}
            className="w-full py-4 bg-white text-indigo-600 rounded-xl font-bold hover:bg-gray-100 disabled:opacity-50"
          >
            {loading ? 'Saving...' : `Complete (${selectedCareers.length} careers)`}
          </button>
        </div>
      )}
    </div>
  );
}
