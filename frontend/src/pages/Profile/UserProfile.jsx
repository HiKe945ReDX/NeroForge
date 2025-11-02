import React, { useState, useEffect } from 'react';
import { User, Edit2, Save, X, Award, Brain, Heart, Code, Briefcase } from 'lucide-react';
import { API_CONFIG } from '../../config/api';
import { Radar } from 'react-chartjs-2';
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

export default function UserProfile() {
  const [loading, setLoading] = useState(true);
  const [persona, setPersona] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedInfo, setEditedInfo] = useState({});

  useEffect(() => {
    fetchUserPersona();
  }, []);

  const fetchUserPersona = async () => {
    try {
      const userId = localStorage.getItem('guidora_user_id');
      const response = await fetch(`${API_CONFIG.GATEWAY_URL}/api/context/persona/${userId}`);
      const data = await response.json();
      setPersona(data);
      setEditedInfo({
        name: data.basic_info?.name || '',
        email: data.basic_info?.email || '',
        phone: data.basic_info?.phone || '',
        education_level: data.basic_info?.education_level || '',
        current_role: data.basic_info?.current_role || '',
      });
      setLoading(false);
    } catch (error) {
      console.error('Error fetching persona:', error);
      setLoading(false);
    }
  };

  const handleSaveBasicInfo = async () => {
    try {
      const userId = localStorage.getItem('guidora_user_id');
      await fetch(`${API_CONFIG.GATEWAY_URL}/api/users/${userId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editedInfo),
      });
      setIsEditing(false);
      fetchUserPersona();
    } catch (error) {
      console.error('Error updating basic info:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-2xl font-semibold text-gray-700">Loading your profile...</div>
      </div>
    );
  }

  if (!persona) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl text-red-600">Failed to load profile. Please try again.</div>
      </div>
    );
  }

  const portfolioScore = persona.portfolio_score || 0;
  const readinessTier = persona.readiness_tier || 'Beginner';
  const personality = persona.personality || {};
  const empathyScore = personality.empathy_score || 0;
  const teamRole = personality.team_role || 'Unknown';
  const skills = persona.skills || {};

  const getScoreColor = (score) => {
    if (score >= 70) return 'text-green-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score) => {
    if (score >= 70) return 'bg-green-100';
    if (score >= 40) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const getTierColor = (tier) => {
    if (tier === 'Advanced') return 'bg-gradient-to-r from-purple-500 to-pink-500';
    if (tier === 'Intermediate') return 'bg-gradient-to-r from-blue-500 to-indigo-500';
    return 'bg-gradient-to-r from-gray-500 to-gray-600';
  };

  const radarData = {
    labels: ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism'],
    datasets: [
      {
        label: 'Your Personality',
        data: [
          (personality.big_five?.openness || 0) * 100,
          (personality.big_five?.conscientiousness || 0) * 100,
          (personality.big_five?.extraversion || 0) * 100,
          (personality.big_five?.agreeableness || 0) * 100,
          (personality.big_five?.neuroticism || 0) * 100,
        ],
        backgroundColor: 'rgba(99, 102, 241, 0.2)',
        borderColor: 'rgba(99, 102, 241, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(99, 102, 241, 1)',
      },
    ],
  };

  const radarOptions = {
    scales: {
      r: {
        min: 0,
        max: 100,
        ticks: { stepSize: 20 },
      },
    },
    plugins: {
      legend: { display: false },
    },
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-24 h-24 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white text-3xl font-bold">
                {persona.basic_info?.name?.charAt(0) || 'U'}
              </div>
              <div>
                <h1 className="text-4xl font-bold text-gray-900">{persona.basic_info?.name || 'User'}</h1>
                <p className="text-gray-600">{persona.basic_info?.email || 'No email'}</p>
                <div className={`inline-block mt-2 px-4 py-1 ${getTierColor(readinessTier)} text-white rounded-full text-sm font-semibold`}>
                  {readinessTier}
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 flex items-center gap-2"
            >
              {isEditing ? <X className="w-5 h-5" /> : <Edit2 className="w-5 h-5" />}
              {isEditing ? 'Cancel' : 'Edit Profile'}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                <Award className="w-7 h-7 text-indigo-600" />
                Portfolio Score
              </h2>
              <div className="flex items-center justify-center mb-6">
                <div className="relative">
                  <svg className="w-48 h-48">
                    <circle cx="96" cy="96" r="80" fill="none" stroke="#e5e7eb" strokeWidth="16" />
                    <circle
                      cx="96"
                      cy="96"
                      r="80"
                      fill="none"
                      stroke={portfolioScore >= 70 ? '#10b981' : portfolioScore >= 40 ? '#fbbf24' : '#ef4444'}
                      strokeWidth="16"
                      strokeDasharray={`${portfolioScore * 5.02} 502`}
                      strokeLinecap="round"
                      transform="rotate(-90 96 96)"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <div className={`text-5xl font-bold ${getScoreColor(portfolioScore)}`}>
                        {portfolioScore}
                      </div>
                      <div className="text-sm text-gray-500">out of 100</div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className={`p-4 rounded-lg ${getScoreBgColor(persona.scores?.resume_score * 100 || 0)}`}>
                  <div className="text-sm text-gray-600 mb-1">Resume</div>
                  <div className={`text-2xl font-bold ${getScoreColor((persona.scores?.resume_score * 100) || 0)}`}>
                    {Math.round((persona.scores?.resume_score || 0) * 100)}/25
                  </div>
                </div>
                <div className={`p-4 rounded-lg ${getScoreBgColor((persona.scores?.github_score || 0) * 100)}`}>
                  <div className="text-sm text-gray-600 mb-1">GitHub</div>
                  <div className={`text-2xl font-bold ${getScoreColor((persona.scores?.github_score || 0) * 100)}`}>
                    {Math.round((persona.scores?.github_score || 0) * 100)}/25
                  </div>
                </div>
                <div className={`p-4 rounded-lg ${getScoreBgColor((persona.scores?.psychometric_score || 0) * 100)}`}>
                  <div className="text-sm text-gray-600 mb-1">Psychometric</div>
                  <div className={`text-2xl font-bold ${getScoreColor((persona.scores?.psychometric_score || 0) * 100)}`}>
                    {Math.round((persona.scores?.psychometric_score || 0) * 100)}/25
                  </div>
                </div>
                <div className={`p-4 rounded-lg ${getScoreBgColor((persona.scores?.empathy_score || 0) * 100)}`}>
                  <div className="text-sm text-gray-600 mb-1">Empathy</div>
                  <div className={`text-2xl font-bold ${getScoreColor((persona.scores?.empathy_score || 0) * 100)}`}>
                    {Math.round((persona.scores?.empathy_score || 0) * 100)}/25
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                <Code className="w-7 h-7 text-indigo-600" />
                Skills Breakdown
              </h2>
              <div className="space-y-6">
                {skills.technical_skills && skills.technical_skills.length > 0 && (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-lg font-semibold text-gray-900">Technical Skills</h3>
                      <span className="text-indigo-600 font-bold">{skills.technical_skills.length}</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {skills.technical_skills.map((skill, idx) => (
                        <span key={idx} className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {skills.soft_skills && skills.soft_skills.length > 0 && (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-lg font-semibold text-gray-900">Soft Skills</h3>
                      <span className="text-green-600 font-bold">{skills.soft_skills.length}</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {skills.soft_skills.map((skill, idx) => (
                        <span key={idx} className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {skills.domain_knowledge && skills.domain_knowledge.length > 0 && (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-lg font-semibold text-gray-900">Domain Knowledge</h3>
                      <span className="text-purple-600 font-bold">{skills.domain_knowledge.length}</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {skills.domain_knowledge.map((skill, idx) => (
                        <span key={idx} className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                <Brain className="w-7 h-7 text-indigo-600" />
                Personality Summary
              </h2>
              <div className="flex justify-center mb-4">
                <div style={{ width: '400px', height: '400px' }}>
                  <Radar data={radarData} options={radarOptions} />
                </div>
              </div>
              <div className="text-center text-gray-600">
                <p className="font-medium">{personality.work_style || 'No work style data'}</p>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                  <User className="w-6 h-6 text-indigo-600" />
                  Basic Info
                </h2>
                {isEditing && (
                  <button
                    onClick={handleSaveBasicInfo}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-semibold hover:bg-green-700 flex items-center gap-1"
                  >
                    <Save className="w-4 h-4" />
                    Save
                  </button>
                )}
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Name</label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editedInfo.name}
                      onChange={(e) => setEditedInfo({ ...editedInfo, name: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                  ) : (
                    <p className="text-gray-900 font-medium">{persona.basic_info?.name || 'N/A'}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Email</label>
                  {isEditing ? (
                    <input
                      type="email"
                      value={editedInfo.email}
                      onChange={(e) => setEditedInfo({ ...editedInfo, email: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                  ) : (
                    <p className="text-gray-900 font-medium">{persona.basic_info?.email || 'N/A'}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Phone</label>
                  {isEditing ? (
                    <input
                      type="tel"
                      value={editedInfo.phone}
                      onChange={(e) => setEditedInfo({ ...editedInfo, phone: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                  ) : (
                    <p className="text-gray-900 font-medium">{persona.basic_info?.phone || 'N/A'}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Education Level</label>
                  <p className="text-gray-900 font-medium">{persona.basic_info?.education_level || 'N/A'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Current Role</label>
                  <p className="text-gray-900 font-medium">{persona.basic_info?.current_role || 'N/A'}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Heart className="w-6 h-6 text-pink-600" />
                Empathy & Team Role
              </h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-pink-50 rounded-lg">
                  <span className="text-gray-700 font-medium">Empathy Score</span>
                  <span className="text-2xl font-bold text-pink-600">{empathyScore}/100</span>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <span className="text-gray-700 font-medium block mb-2">Team Role</span>
                  <span className="text-lg font-bold text-purple-600">{teamRole}</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Briefcase className="w-6 h-6 text-indigo-600" />
                Experience
              </h2>
              <div className="space-y-3">
                <div>
                  <span className="text-gray-600 text-sm">Years of Experience</span>
                  <p className="text-lg font-bold text-gray-900">
                    {persona.experience?.years_of_experience || 0} years
                  </p>
                </div>
                {persona.experience?.current_role && (
                  <div>
                    <span className="text-gray-600 text-sm">Current Role</span>
                    <p className="font-medium text-gray-900">{persona.experience.current_role}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
