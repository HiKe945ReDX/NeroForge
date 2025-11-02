'use client';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function BasicInfoForm() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    fullName: localStorage.getItem('guidora_user_name') || '',
    email: localStorage.getItem('guidora_user_email') || '',
    phone: '',
    educationLevel: '',
    currentField: '',
  });

  const educationLevels = [
    { value: 'high-school', label: '🎓 High School Student (exploring careers)' },
    { value: 'ug', label: '🎓 Undergraduate Student (UG)' },
    { value: 'pg', label: '🎓 Postgraduate Student (PG/Master\'s/PhD)' },
    { value: 'professional-1-3', label: '💼 Working Professional (1-3 years)' },
    { value: 'professional-3-10', label: '💼 Experienced Professional (3-10 years)' },
    { value: 'professional-10plus', label: '💼 Senior Professional (10+ years)' },
    { value: 'career-switcher', label: '🔄 Career Switcher' },
    { value: 'entrepreneur', label: '🚀 Entrepreneur/Startup Founder' },
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Save to localStorage
    localStorage.setItem('guidora_basic_info', JSON.stringify(formData));
    
    // Navigate to STEP 2: Resume Upload
    navigate('/onboarding/resume-upload');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-2xl mx-auto">
        {/* Progress */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Step 1 of 6</span>
            <span className="text-sm text-gray-500">Basic Information</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-indigo-600 h-2 rounded-full transition-all duration-300" style={{ width: '16.6%' }}></div>
          </div>
        </div>

        {/* Form Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Let's Get Started! 🚀
            </h1>
            <p className="text-gray-600">Tell us a bit about yourself</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Full Name *</label>
              <input
                type="text"
                required
                value={formData.fullName}
                onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="Enter your full name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="your.email@example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Phone (Optional)</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="+1 (555) 000-0000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">What best describes you? *</label>
              <select
                required
                value={formData.educationLevel}
                onChange={(e) => setFormData({ ...formData, educationLevel: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">-- Select --</option>
                {educationLevels.map(level => (
                  <option key={level.value} value={level.value}>{level.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Current Field/Major *</label>
              <input
                type="text"
                required
                value={formData.currentField}
                onChange={(e) => setFormData({ ...formData, currentField: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="e.g., Computer Science, Marketing, Engineering"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-indigo-600 text-white py-4 rounded-lg font-semibold hover:bg-indigo-700 transition text-lg"
            >
              Continue →
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
