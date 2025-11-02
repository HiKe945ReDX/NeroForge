'use client';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function SkillsPicker() {
  const navigate = useNavigate();
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  const skillsDatabase = [
    'JavaScript', 'Python', 'React', 'Node.js', 'Data Analysis',
    'Machine Learning', 'Communication', 'Leadership', 'Problem Solving',
    'Project Management', 'SQL', 'AWS', 'Docker', 'Git',
  ];

  const handleSkillToggle = (skill) => {
    if (selectedSkills.includes(skill)) {
      setSelectedSkills(selectedSkills.filter(s => s !== skill));
    } else if (selectedSkills.length < 20) {
      setSelectedSkills([...selectedSkills, skill]);
    }
  };

  const handleSubmit = () => {
    localStorage.setItem('guidora_skills', JSON.stringify(selectedSkills));
    navigate('/onboarding/psychometric');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Step 3 of 6</span>
            <span className="text-sm text-gray-500">Skills Selection ({selectedSkills.length}/20)</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-indigo-600 h-2 rounded-full" style={{ width: '50%' }}></div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h1 className="text-4xl font-bold mb-4">Select Your Skills 🎯</h1>
          <p className="text-gray-600 mb-6">Choose up to 20 skills that best represent you</p>

          <input
            type="text"
            placeholder="Search skills..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-3 border rounded-lg mb-6"
          />

          <div className="flex flex-wrap gap-3 mb-8">
            {skillsDatabase.filter(s => s.toLowerCase().includes(searchTerm.toLowerCase())).map(skill => (
              <button
                key={skill}
                onClick={() => handleSkillToggle(skill)}
                className={`px-4 py-2 rounded-full font-medium transition ${
                  selectedSkills.includes(skill)
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {skill}
              </button>
            ))}
          </div>

          <button
            onClick={handleSubmit}
            disabled={selectedSkills.length === 0}
            className="w-full bg-indigo-600 text-white py-4 rounded-lg font-semibold hover:bg-indigo-700 disabled:opacity-50"
          >
            Continue →
          </button>
        </div>
      </div>
    </div>
  );
}
