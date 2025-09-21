import React, { useState, useEffect } from 'react';
import { 
  Mic, 
  MicOff, 
  Play, 
  Square,
  RotateCcw,
  CheckCircle,
  AlertCircle,
  Clock,
  Award,
  Star,
  Volume2
} from 'lucide-react';
import toast from 'react-hot-toast';

const InterviewPrep = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [showFeedback, setShowFeedback] = useState(false);
  const [sessionActive, setSessionActive] = useState(false);

  const mockQuestions = [
    "Tell me about yourself and your background.",
    "What interests you most about this role?",
    "Describe a challenging project you've worked on.",
    "How do you handle tight deadlines and pressure?",
    "Where do you see yourself in 5 years?"
  ];

  const mockFeedback = {
    overallScore: 85,
    strengths: [
      "Clear and confident communication",
      "Good use of specific examples",
      "Professional demeanor maintained"
    ],
    improvements: [
      "Could provide more quantified results",
      "Consider using the STAR method more consistently",
      "Speak slightly slower for better clarity"
    ],
    recommendations: [
      "Practice with more technical questions",
      "Prepare 2-3 more concrete examples",
      "Work on concluding answers more definitively"
    ]
  };

  const startInterview = () => {
    setSessionActive(true);
    setCurrentQuestion(0);
    setAnswers([]);
    setShowFeedback(false);
    toast.success('Mock interview started! Good luck!');
  };

  const toggleRecording = () => {
    if (!isRecording) {
      setIsRecording(true);
      toast.success('Recording started');
    } else {
      setIsRecording(false);
      // Simulate saving answer
      const newAnswer = {
        question: mockQuestions[currentQuestion],
        duration: Math.floor(Math.random() * 120) + 30,
        timestamp: new Date()
      };
      setAnswers([...answers, newAnswer]);
      toast.success('Answer recorded');
    }
  };

  const nextQuestion = () => {
    if (currentQuestion < mockQuestions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // End interview
      setSessionActive(false);
      setShowFeedback(true);
      toast.success('Interview completed! Generating feedback...');
    }
  };

  const restartInterview = () => {
    setSessionActive(false);
    setCurrentQuestion(0);
    setAnswers([]);
    setShowFeedback(false);
    setIsRecording(false);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-2xl p-8 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-black bg-opacity-10"></div>
        <div className="relative z-10">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2 flex items-center">
                <Mic className="w-10 h-10 mr-3 text-indigo-300" />
                AI Mock Interview
              </h1>
              <p className="text-indigo-100 text-lg">Practice interviews with AI-powered feedback and analysis</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-indigo-200">Practice Mode</p>
              <div className="flex items-center mt-1">
                <div className="w-3 h-3 bg-green-400 rounded-full mr-2 animate-pulse"></div>
                <p className="text-lg font-bold text-green-300">Ready</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        {!sessionActive && !showFeedback && (
          // Start Screen
          <div className="p-8">
            <div className="text-center mb-8">
              <Mic className="w-16 h-16 text-indigo-500 mx-auto mb-4" />
              <h2 className="text-3xl font-bold text-gray-900 mb-2">Mock Interview Session</h2>
              <p className="text-gray-600">Practice common interview questions and get AI-powered feedback</p>
            </div>

            <div className="max-w-2xl mx-auto">
              <div className="bg-indigo-50 rounded-xl border border-indigo-200 p-6 mb-8">
                <h3 className="text-xl font-bold text-gray-900 mb-4">What to Expect</h3>
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="text-gray-700">5 common interview questions</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="text-gray-700">Voice recording and analysis</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="text-gray-700">Detailed feedback and recommendations</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="text-gray-700">Performance scoring and insights</span>
                  </div>
                </div>
              </div>

              <div className="text-center">
                <button
                  onClick={startInterview}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-4 rounded-lg font-medium text-lg transition-colors flex items-center space-x-2 mx-auto"
                >
                  <Play className="w-6 h-6" />
                  <span>Start Mock Interview</span>
                </button>
                <p className="text-sm text-gray-500 mt-3">Session duration: ~10-15 minutes</p>
              </div>
            </div>
          </div>
        )}

        {sessionActive && (
          // Interview Session
          <div className="p-8">
            {/* Progress */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-medium text-gray-700">
                  Question {currentQuestion + 1} of {mockQuestions.length}
                </span>
                <button
                  onClick={restartInterview}
                  className="text-gray-400 hover:text-gray-600 flex items-center space-x-1"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>Restart</span>
                </button>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${((currentQuestion + 1) / mockQuestions.length) * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Current Question */}
            <div className="text-center mb-8">
              <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl border border-indigo-200 p-8 mb-6">
                <div className="flex items-center justify-center mb-4">
                  <Volume2 className="w-6 h-6 text-indigo-600 mr-2" />
                  <span className="text-sm font-medium text-indigo-600">Interview Question</span>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 leading-relaxed">
                  {mockQuestions[currentQuestion]}
                </h3>
              </div>

              {/* Recording Controls */}
              <div className="flex items-center justify-center space-x-6">
                <button
                  onClick={toggleRecording}
                  className={`p-6 rounded-full transition-colors ${
                    isRecording
                      ? 'bg-red-600 hover:bg-red-700 text-white animate-pulse'
                      : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                  }`}
                >
                  {isRecording ? (
                    <Square className="w-8 h-8" />
                  ) : (
                    <Mic className="w-8 h-8" />
                  )}
                </button>

                {!isRecording && answers.length === currentQuestion + 1 && (
                  <button
                    onClick={nextQuestion}
                    className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2"
                  >
                    <span>{currentQuestion === mockQuestions.length - 1 ? 'Finish Interview' : 'Next Question'}</span>
                    <CheckCircle className="w-5 h-5" />
                  </button>
                )}
              </div>

              <p className="text-sm text-gray-600 mt-4">
                {isRecording ? 'Recording your answer...' : 'Click the microphone to start recording'}
              </p>
            </div>

            {/* Answers Summary */}
            {answers.length > 0 && (
              <div className="bg-gray-50 rounded-xl p-6">
                <h4 className="font-semibold text-gray-900 mb-4">Answered Questions ({answers.length})</h4>
                <div className="space-y-3">
                  {answers.map((answer, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-white rounded-lg">
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-green-600" />
                        <span className="text-sm text-gray-700">Question {index + 1}</span>
                      </div>
                      <div className="flex items-center space-x-2 text-sm text-gray-500">
                        <Clock className="w-4 h-4" />
                        <span>{answer.duration}s</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {showFeedback && (
          // Feedback Screen
          <div className="p-8">
            <div className="text-center mb-8">
              <Award className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
              <h2 className="text-3xl font-bold text-gray-900 mb-2">Interview Complete!</h2>
              <p className="text-gray-600">Here's your AI-powered feedback and performance analysis</p>
            </div>

            <div className="space-y-8">
              {/* Overall Score */}
              <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6 border border-green-200 text-center">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Overall Performance</h3>
                <div className="flex items-center justify-center space-x-4 mb-4">
                  <div className="text-4xl font-bold text-green-600">{mockFeedback.overallScore}/100</div>
                  <div className="flex">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-6 h-6 ${
                          i < Math.floor(mockFeedback.overallScore / 20)
                            ? 'text-yellow-500 fill-current'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                </div>
                <p className="text-green-700 font-medium">Great job! You're well-prepared for interviews.</p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Strengths */}
                <div className="bg-white rounded-xl border border-gray-200 p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                    <CheckCircle className="w-6 h-6 mr-2 text-green-600" />
                    Strengths
                  </h3>
                  <div className="space-y-3">
                    {mockFeedback.strengths.map((strength, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                        <p className="text-gray-700 text-sm">{strength}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Areas for Improvement */}
                <div className="bg-white rounded-xl border border-gray-200 p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                    <AlertCircle className="w-6 h-6 mr-2 text-orange-600" />
                    Improvements
                  </h3>
                  <div className="space-y-3">
                    {mockFeedback.improvements.map((improvement, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-orange-500 rounded-full mt-2"></div>
                        <p className="text-gray-700 text-sm">{improvement}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommendations */}
                <div className="bg-white rounded-xl border border-gray-200 p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                    <Star className="w-6 h-6 mr-2 text-blue-600" />
                    Next Steps
                  </h3>
                  <div className="space-y-3">
                    {mockFeedback.recommendations.map((rec, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                        <p className="text-gray-700 text-sm">{rec}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-center space-x-4">
                <button
                  onClick={restartInterview}
                  className="px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
                >
                  Practice Again
                </button>
                <button className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors">
                  Save Results
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InterviewPrep;
