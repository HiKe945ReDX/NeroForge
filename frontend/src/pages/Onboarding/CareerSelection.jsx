'use client';
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check, ChevronRight, Loader2, Star } from 'lucide-react';
import toast from 'react-hot-toast';

export default function CareerSelection() {
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState([]);
  const [selectedCareers, setSelectedCareers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadRecommendations = async () => {
      try {
        const stored = localStorage.getItem('guidora_career_recommendations');
        if (stored) {
          const parsed = JSON.parse(stored);
          setRecommendations(Array.isArray(parsed) ? parsed : [parsed]);
          setIsLoading(false);
          return;
        }

        const answers = JSON.parse(localStorage.getItem('guidora_discovery_answers') || '{}');
        if (Object.keys(answers).length > 0) {
          const b2URL = process.env.REACT_APP_API_GATEWAY_URL || 'http://localhost:8001';
          const userId = localStorage.getItem('guidora_userid') || 'test-user';
          const response = await fetch(`${b2URL}/api/careers/from-discovery`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, ...answers })
          });

          if (!response.ok) throw new Error('Failed to fetch recommendations');
          const data = await response.json();
          setRecommendations(Array.isArray(data) ? data : [data]);
          localStorage.setItem('guidora_career_recommendations', JSON.stringify(data));
        } else {
          throw new Error('No discovery answers found');
        }
        setIsLoading(false);
      } catch (err) {
        setError(err.message);
        setIsLoading(false);
        toast.error('Failed to load career recommendations');
      }
    };
    loadRecommendations();
  }, []);

  const handleToggleCareer = (careerId) => {
    if (selectedCareers.includes(careerId)) {
      setSelectedCareers(selectedCareers.filter(id => id !== careerId));
    } else {
      if (selectedCareers.length < 10) {
        setSelectedCareers([...selectedCareers, careerId]);
      } else {
        toast.error('Maximum 10 careers allowed');
      }
    }
  };

  const handleSaveSelections = async () => {
    if (selectedCareers.length === 0) {
      toast.error('Please select at least 1 career');
      return;
    }

    setIsSaving(true);
    try {
      const b4URL = process.env.REACT_APP_B4_URL || 'http://localhost:8002';
      const userId = localStorage.getItem('guidora_userid') || 'test-user';
      const response = await fetch(`${b4URL}/api/profile/complete-discovery`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          selected_careers: selectedCareers,
          discovery_responses: JSON.parse(localStorage.getItem('guidora_discovery_answers') || '{}')
        })
      });

      if (!response.ok) throw new Error('Failed to save profile');
      localStorage.setItem('guidora_selected_careers', JSON.stringify(selectedCareers));
      localStorage.setItem('guidora_profile_completion', '95');
      toast.success('Career selection saved! 🎉');
      setTimeout(() => navigate('/career-details', { state: { careers: selectedCareers, recommendations } }), 500);
    } catch (err) {
      toast.error(err.message || 'Failed to save');
      setIsSaving(false);
    }
  };

  if (isLoading) return (<div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-50 flex items-center justify-center p-6"><div className="text-center"><Loader2 className="w-16 h-16 text-indigo-600 mx-auto mb-4 animate-spin" /><h2 className="text-2xl font-bold text-gray-900 mb-2">Loading career recommendations...</h2><p className="text-gray-600">AI is finding matches based on your profile</p></div></div>);

  if (error || recommendations.length === 0) return (<div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-50 flex items-center justify-center p-6"><div className="text-center max-w-md"><div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4"><span className="text-3xl">⚠️</span></div><h2 className="text-2xl font-bold text-gray-900 mb-2">Unable to load recommendations</h2><p className="text-gray-600 mb-6">{error || 'No recommendations found'}</p><button onClick={() => navigate('/onboarding/discovery/career-quiz')} className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition-colors">Try Again</button></div></div>);

  const progress = (selectedCareers.length / 3) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-blue-50 to-purple-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-3">Which careers interest you?</h1>
          <p className="text-lg text-gray-600">Based on your answers, we found <span className="font-semibold">{recommendations.length} matching careers</span>. Select 1-10 to explore.</p>
        </div>

        <div className="mb-8 max-w-2xl mx-auto">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">{selectedCareers.length} selected (minimum: 1)</span>
            <span className="text-sm font-medium text-indigo-600">{selectedCareers.length > 0 ? 'Ready to continue' : 'Select careers'}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-600 to-blue-600 h-2 transition-all duration-300" style={{ width: `${Math.min(progress, 100)}%` }}></div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {recommendations.map((career, idx) => {
            const careerId = career.career_id || career.id || `career-${idx}`;
            const isSelected = selectedCareers.includes(careerId);
            return (
              <button
                key={careerId}
                onClick={() => handleToggleCareer(careerId)}
                className={`text-left p-6 rounded-2xl border-2 transition-all hover:shadow-lg ${
                  isSelected ? 'border-indigo-600 bg-white shadow-lg scale-105' : 'border-gray-200 bg-white hover:border-indigo-300'
                }`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-900">{career.career_title || career.title || 'Career'}</h3>
                    <div className="flex items-center gap-1 mt-1">
                      <Star className="w-4 h-4 text-amber-500 fill-amber-500" />
                      <span className="text-xs font-semibold text-amber-600">{career.match_score || career.fit_score || 75}% match</span>
                    </div>
                  </div>
                  {isSelected && (<div className="w-7 h-7 bg-indigo-600 rounded-full flex items-center justify-center flex-shrink-0"><Check className="w-4 h-4 text-white" /></div>)}
                </div>
                <p className="text-gray-600 text-sm mb-4 line-clamp-2">{career.description || 'Career opportunity'}</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                    <div className="bg-gradient-to-r from-indigo-600 to-blue-600 h-2" style={{ width: `${career.fit_score || career.match_score || 75}%` }}></div>
                  </div>
                  <span className="text-sm font-bold text-gray-700 w-10 text-right">{career.fit_score || career.match_score || 75}%</span>
                </div>
              </button>
            );
          })}
        </div>

        <div className="flex gap-4 max-w-md mx-auto">
          <button onClick={() => navigate(-1)} className="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors">Back</button>
          <button onClick={handleSaveSelections} disabled={isSaving || selectedCareers.length === 0} className="flex-1 px-6 py-3 bg-gradient-to-r from-indigo-600 to-blue-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all">
            {isSaving ? (<><Loader2 className="w-5 h-5 animate-spin" /> Saving...</>) : (<>Continue <ChevronRight className="w-5 h-5" /></>)}
          </button>
        </div>
      </div>
    </div>
  );
}
