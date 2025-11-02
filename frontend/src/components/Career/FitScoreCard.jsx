import React, { useState, useEffect } from 'react';
import { TrendingUp, AlertCircle, CheckCircle, Award, Zap } from 'lucide-react';

export default function FitScoreCard({ career, userSkills = [] }) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const [showDetails, setShowDetails] = useState(false);

  // Calculate scores based on career + user profile
  const skillMatchScore = userSkills.length > 0 
    ? Math.round((userSkills.filter(s => 
        career?.required_skills?.some(rs => rs.toLowerCase() === s.toLowerCase())
      ).length / Math.max(userSkills.length, 1)) * 100) 
    : 78;

  const personalityFit = career?.ideal_personality ? 72 : 65;
  const marketDemand = career?.job_outlook?.includes('Growing') ? 82 : 68;
  const experienceMatch = 78;
  
  const overallScore = Math.round(
    (skillMatchScore * 0.35 + personalityFit * 0.20 + marketDemand * 0.15 + experienceMatch * 0.30)
  );

  // Animate score on mount
  useEffect(() => {
    const interval = setInterval(() => {
      setAnimatedScore(prev => {
        if (prev < overallScore) return prev + 1;
        clearInterval(interval);
        return prev;
      });
    }, 20);
    return () => clearInterval(interval);
  }, [overallScore]);

  const getScoreColor = (score) => {
    if (score >= 80) return {
      bg: 'bg-gradient-to-br from-green-50 to-emerald-50',
      border: 'border-green-300',
      text: 'text-green-700',
      badge: 'bg-green-500',
      icon: '🎯',
      label: 'Excellent Match'
    };
    if (score >= 60) return {
      bg: 'bg-gradient-to-br from-blue-50 to-cyan-50',
      border: 'border-blue-300',
      text: 'text-blue-700',
      badge: 'bg-blue-500',
      icon: '👍',
      label: 'Good Match'
    };
    return {
      bg: 'bg-gradient-to-br from-yellow-50 to-orange-50',
      border: 'border-yellow-300',
      text: 'text-yellow-700',
      badge: 'bg-yellow-500',
      icon: '⚠️',
      label: 'Fair Match'
    };
  };

  const colors = getScoreColor(overallScore);

  const ScoreBars = ({ label, score, icon }) => (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-semibold text-gray-700">{label}</span>
        <span className="text-xs font-bold px-2 py-1 bg-gray-200 rounded">{score}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
        <div
          className={`h-full ${colors.badge} transition-all duration-1000 ease-out rounded-full`}
          style={{ width: `${score}%` }}
        ></div>
      </div>
    </div>
  );

  return (
    <div className={`border-2 ${colors.border} ${colors.bg} rounded-3xl shadow-lg p-8 transition-all duration-300 hover:shadow-xl`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Career Match Score</h2>
        <Award className="w-8 h-8 text-amber-500" />
      </div>

      {/* Main Score Circle */}
      <div className="flex justify-center mb-8">
        <div className="relative w-48 h-48">
          <svg className="w-full h-full transform -rotate-90">
            <circle cx="96" cy="96" r="80" fill="none" stroke="rgba(0,0,0,0.1)" strokeWidth="8" />
            <circle
              cx="96"
              cy="96"
              r="80"
              fill="none"
              stroke="currentColor"
              strokeWidth="8"
              strokeDasharray={`${(animatedScore / 100) * 502.65} 502.65`}
              className={`${colors.badge} transition-all duration-100`}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-5xl font-bold text-gray-900">{animatedScore}</span>
            <span className="text-xs text-gray-600 mt-1">out of 100</span>
          </div>
        </div>
      </div>

      {/* Score Label */}
      <div className="text-center mb-6">
        <span className={`text-2xl font-bold ${colors.text}`}>{colors.icon} {colors.label}</span>
      </div>

      {/* Detailed Scores */}
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="w-full text-left p-3 bg-white rounded-lg border-2 border-gray-200 hover:border-indigo-300 transition-colors mb-4 flex justify-between items-center"
      >
        <span className="font-semibold text-gray-700">View Detailed Breakdown</span>
        <span className={`transform transition-transform ${showDetails ? 'rotate-180' : ''}`}>▼</span>
      </button>

      {showDetails && (
        <div className="bg-white p-4 rounded-lg mb-4 space-y-3 border-2 border-gray-100">
          <ScoreBars label="Skills Match" score={skillMatchScore} icon={Zap} />
          <ScoreBars label="Personality Fit" score={personalityFit} icon={Award} />
          <ScoreBars label="Market Demand" score={marketDemand} icon={TrendingUp} />
          <ScoreBars label="Experience Match" score={experienceMatch} icon={CheckCircle} />
        </div>
      )}

      {/* Recommendation */}
      <div className={`p-4 rounded-lg ${colors.bg} border-l-4 ${colors.border}`}>
        <p className="text-sm text-gray-700">
          {overallScore >= 80
            ? `✨ Excellent fit! You have strong fundamentals. Consider advanced certifications to maximize earning potential.`
            : overallScore >= 60
            ? `👍 Good foundation. Build skills in ${skillMatchScore < 60 ? 'technical areas' : 'soft skills'} to increase competitiveness.`
            : `⚠️ Developing fit. Focus on skill development through bootcamps or specialized courses.`}
        </p>
      </div>
    </div>
  );
}
