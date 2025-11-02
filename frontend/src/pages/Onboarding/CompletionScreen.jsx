import React from 'react';
import { useNavigate } from 'react-router-dom';
import confetti from 'canvas-confetti';

const CompletionScreen = ({ userData }) => {
  const navigate = useNavigate();

  React.useEffect(() => {
    confetti();
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-96">
      <div className="text-center">
        <div className="mb-6">
          <svg className="w-20 h-20 mx-auto text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
        </div>

        <h1 className="text-4xl font-bold text-gray-900 mb-4">Onboarding Complete!</h1>
        <p className="text-xl text-gray-600 mb-8">
          Welcome to Guidora! Your profile is all set up.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8 max-w-2xl mx-auto">
          <div className="p-4 bg-purple-100 rounded-lg">
            <p className="text-sm text-purple-600">📊 Personality Insights</p>
            <p className="text-xs text-gray-600 mt-2">Explore your assessments</p>
          </div>
          <div className="p-4 bg-blue-100 rounded-lg">
            <p className="text-sm text-blue-600">🎯 Career Recommendations</p>
            <p className="text-xs text-gray-600 mt-2">Get personalized matches</p>
          </div>
          <div className="p-4 bg-green-100 rounded-lg">
            <p className="text-sm text-green-600">📈 Learning Roadmap</p>
            <p className="text-xs text-gray-600 mt-2">Your growth plan</p>
          </div>
          <div className="p-4 bg-orange-100 rounded-lg">
            <p className="text-sm text-orange-600">🤝 Community</p>
            <p className="text-xs text-gray-600 mt-2">Connect with mentors</p>
          </div>
        </div>

        <div className="space-y-3">
          <button
            onClick={() => navigate('/dashboard')}
            className="w-full max-w-xs px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition"
          >
            Go to Dashboard
          </button>
          <button
            onClick={() => navigate('/career-atlas')}
            className="w-full max-w-xs px-6 py-3 bg-gray-200 text-gray-900 rounded-lg font-semibold hover:bg-gray-300 transition"
          >
            Explore Careers
          </button>
        </div>
      </div>
    </div>
  );
};

export default CompletionScreen;
