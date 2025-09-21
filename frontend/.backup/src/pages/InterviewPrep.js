import React, { useState } from 'react';
import { MicIcon, PlayIcon, PauseIcon, CheckCircleIcon } from 'lucide-react';
import { interviewService } from '../services/api';
import toast from 'react-hot-toast';

const InterviewPrep = () => {
  const [activeTab, setActiveTab] = useState('questions');
  const [loading, setLoading] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [sessionActive, setSessionActive] = useState(false);

  const generateQuestions = async () => {
    setLoading(true);
    try {
      const response = await interviewService.generateQuestions({
        user_id: 'demo_user',
        role: 'AI Engineer',
        difficulty: 'intermediate'
      });
      setQuestions(response.data.questions || [
        {
          question: "Explain the difference between supervised and unsupervised learning.",
          category: "Technical",
          difficulty: "Medium"
        },
        {
          question: "How would you handle missing data in a machine learning dataset?",
          category: "Technical", 
          difficulty: "Medium"
        },
        {
          question: "Describe a challenging project you worked on and how you overcame obstacles.",
          category: "Behavioral",
          difficulty: "Medium"
        }
      ]);
      toast.success('Interview questions generated!');
    } catch (error) {
      toast.error('Failed to generate questions');
    } finally {
      setLoading(false);
    }
  };

  const startSession = async () => {
    setLoading(true);
    try {
      const response = await interviewService.startSession({
        user_id: 'demo_user',
        role: 'AI Engineer',
        duration_minutes: 30
      });
      setSessionActive(true);
      toast.success('Interview session started!');
    } catch (error) {
      toast.error('Failed to start session');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Interview Preparation</h1>
        <p className="text-lg text-gray-600">Practice with AI-powered mock interviews</p>
      </div>

      {/* Tabs */}
      <div className="flex justify-center space-x-4">
        {[
          { id: 'questions', label: 'Practice Questions' },
          { id: 'session', label: 'Mock Interview' },
          { id: 'feedback', label: 'Feedback & Tips' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-blue-100 text-blue-700 border border-blue-200'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        {activeTab === 'questions' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Practice Questions</h2>
              <button
                onClick={generateQuestions}
                disabled={loading}
                className="btn-primary disabled:opacity-50"
              >
                {loading ? 'Generating...' : 'Generate Questions'}
              </button>
            </div>

            {questions.length > 0 && (
              <div className="space-y-4">
                {questions.map((q, index) => (
                  <div key={index} className="p-6 bg-gray-50 rounded-xl">
                    <div className="flex justify-between items-start mb-3">
                      <span className="text-sm font-medium text-blue-600">
                        {q.category} • {q.difficulty}
                      </span>
                    </div>
                    <p className="text-lg text-gray-900 font-medium">{q.question}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'session' && (
          <div>
            <div className="text-center">
              <MicIcon className="w-16 h-16 text-blue-600 mx-auto mb-6" />
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Mock Interview Session</h2>
              
              {!sessionActive ? (
                <div>
                  <p className="text-gray-600 mb-6">
                    Start a 30-minute mock interview session with AI feedback
                  </p>
                  <button
                    onClick={startSession}
                    disabled={loading}
                    className="btn-primary disabled:opacity-50"
                  >
                    {loading ? 'Starting...' : 'Start Mock Interview'}
                  </button>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="p-6 bg-green-50 rounded-xl">
                    <div className="flex items-center justify-center space-x-3">
                      <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                      <span className="text-green-700 font-medium">Session Active</span>
                    </div>
                  </div>
                  
                  <div className="text-left">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Question:</h3>
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <p className="text-blue-900">
                        {questions[currentQuestion]?.question || "Tell me about yourself and your experience with AI."}
                      </p>
                    </div>
                  </div>

                  <div className="flex justify-center space-x-4">
                    <button className="flex items-center space-x-2 px-6 py-3 bg-green-100 text-green-700 rounded-lg hover:bg-green-200">
                      <PlayIcon className="w-5 h-5" />
                      <span>Record Answer</span>
                    </button>
                    <button 
                      onClick={() => setCurrentQuestion(prev => prev + 1)}
                      className="flex items-center space-x-2 px-6 py-3 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200"
                    >
                      <span>Next Question</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'feedback' && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Interview Tips & Feedback</h2>
            <div className="space-y-6">
              <div className="p-6 bg-green-50 rounded-xl">
                <div className="flex items-start space-x-3">
                  <CheckCircleIcon className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-semibold text-green-900 mb-2">Strengths</h3>
                    <ul className="text-green-800 space-y-1">
                      <li>• Clear technical explanations</li>
                      <li>• Good problem-solving approach</li>
                      <li>• Confident communication</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="p-6 bg-yellow-50 rounded-xl">
                <h3 className="font-semibold text-yellow-900 mb-2">Areas for Improvement</h3>
                <ul className="text-yellow-800 space-y-1">
                  <li>• Include more specific examples</li>
                  <li>• Practice behavioral questions</li>
                  <li>• Work on concise answers</li>
                </ul>
              </div>

              <div className="p-6 bg-blue-50 rounded-xl">
                <h3 className="font-semibold text-blue-900 mb-2">General Tips</h3>
                <ul className="text-blue-800 space-y-1">
                  <li>• Research the company thoroughly</li>
                  <li>• Prepare STAR format examples</li>
                  <li>• Practice coding problems</li>
                  <li>• Ask thoughtful questions</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InterviewPrep;
