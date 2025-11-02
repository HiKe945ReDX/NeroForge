'use client';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function ResumeUpload() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    resume: null,
    githubUsername: '',
    linkedinUrl: '',
  });

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file && (file.type === 'application/pdf' || file.type.includes('document'))) {
      setFormData({ ...formData, resume: file });
    } else {
      alert('Please upload a PDF or Word document');
    }
  };

  const handleSkip = () => {
    navigate('/onboarding/skills-picker');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    localStorage.setItem('guidora_resume_data', JSON.stringify({
      hasResume: !!formData.resume,
      githubUsername: formData.githubUsername,
      linkedinUrl: formData.linkedinUrl,
    }));
    navigate('/onboarding/skills-picker');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Step 2 of 6</span>
            <span className="text-sm text-gray-500">Experience Upload</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-indigo-600 h-2 rounded-full transition-all" style={{ width: '33.3%' }}></div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Upload Your Experience 📄</h1>
            <p className="text-gray-600">Help us understand your background better (optional)</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Resume Upload */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-500 transition">
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={handleFileUpload}
                className="hidden"
                id="resume-upload"
              />
              <label htmlFor="resume-upload" className="cursor-pointer">
                <div className="text-6xl mb-4">📤</div>
                <p className="text-lg font-medium text-gray-700">
                  {formData.resume ? formData.resume.name : 'Upload Resume (PDF/DOCX)'}
                </p>
                <p className="text-sm text-gray-500 mt-2">Click to browse</p>
              </label>
            </div>

            {/* GitHub */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">GitHub Username (Optional)</label>
              <input
                type="text"
                value={formData.githubUsername}
                onChange={(e) => setFormData({ ...formData, githubUsername: e.target.value })}
                className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="github-username"
              />
            </div>

            {/* LinkedIn */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">LinkedIn URL (Optional)</label>
              <input
                type="url"
                value={formData.linkedinUrl}
                onChange={(e) => setFormData({ ...formData, linkedinUrl: e.target.value })}
                className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="https://linkedin.com/in/yourprofile"
              />
            </div>

            <div className="flex gap-4">
              <button type="button" onClick={handleSkip} className="flex-1 border-2 border-gray-300 text-gray-700 py-4 rounded-lg font-semibold hover:bg-gray-50">
                Skip for Now
              </button>
              <button type="submit" className="flex-1 bg-indigo-600 text-white py-4 rounded-lg font-semibold hover:bg-indigo-700">
                Continue →
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
