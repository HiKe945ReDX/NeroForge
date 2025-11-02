import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, TrendingUp, AlertCircle } from 'lucide-react';

export default function ProConsSection({ career }) {
  const [selectedTab, setSelectedTab] = useState('pros');

  if (!career) return null;

  const pros = career.pros || [
    '💰 Competitive salary packages',
    '📈 Strong job growth and demand',
    '🌟 Opportunities for innovation',
    '🤝 Collaborative work environment',
    '🎓 Continuous learning opportunities',
    '⏰ Good work-life balance potential'
  ];

  const cons = career.cons || [
    '⏰ Can involve long working hours',
    '�� High-pressure deadlines',
    '🔄 Rapidly changing technologies',
    '💼 Corporate environment demands',
    '📊 Performance-based metrics',
    '�� Occasional travel requirement'
  ];

  const proIcons = ['💰', '📈', '🌍', '⏰', '🧠', '🤝', '🎯', '✨'];
  const conIcons = ['⚠️', '😓', '💼', '📊', '🎓', '🏢', '⏰', '🌪️'];

  return (
    <div className="bg-white rounded-2xl shadow-lg p-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-6">Pros & Cons</h2>

      {/* Tab buttons */}
      <div className="flex gap-4 mb-8">
        <button
          onClick={() => setSelectedTab('pros')}
          className={`flex items-center gap-2 px-6 py-3 rounded-lg font-bold transition-all ${
            selectedTab === 'pros'
              ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          <ThumbsUp className="w-5 h-5" />
          Advantages
        </button>
        <button
          onClick={() => setSelectedTab('cons')}
          className={`flex items-center gap-2 px-6 py-3 rounded-lg font-bold transition-all ${
            selectedTab === 'cons'
              ? 'bg-gradient-to-r from-red-500 to-orange-500 text-white shadow-lg'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          <ThumbsDown className="w-5 h-5" />
          Challenges
        </button>
      </div>

      {/* Content */}
      <div className="min-h-96">
        {selectedTab === 'pros' ? (
          <div className="space-y-3">
            {pros && pros.length > 0 ? (
              pros.map((pro, i) => (
                <div
                  key={i}
                  className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border-2 border-green-200 hover:border-green-400 hover:shadow-md transition-all flex items-start gap-3"
                >
                  <span className="text-2xl flex-shrink-0">{proIcons[i % proIcons.length]}</span>
                  <span className="text-gray-700 font-medium">{pro}</span>
                </div>
              ))
            ) : (
              <p className="text-gray-500">No pros information available</p>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {cons && cons.length > 0 ? (
              cons.map((con, i) => (
                <div
                  key={i}
                  className="p-4 bg-gradient-to-r from-red-50 to-orange-50 rounded-lg border-2 border-red-200 hover:border-red-400 hover:shadow-md transition-all flex items-start gap-3"
                >
                  <span className="text-2xl flex-shrink-0">{conIcons[i % conIcons.length]}</span>
                  <span className="text-gray-700 font-medium">{con}</span>
                </div>
              ))
            ) : (
              <p className="text-gray-500">No cons information available</p>
            )}
          </div>
        )}
      </div>

      {/* Summary */}
      <div className="mt-8 p-4 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-xl border-l-4 border-indigo-500">
        <p className="text-indigo-900 font-medium">
          {selectedTab === 'pros'
            ? '✨ <strong>Summary:</strong> This career offers meaningful growth opportunities and competitive compensation. Consider starting with internships or entry-level positions to gain industry experience.'
            : '⚠️ <strong>Considerations:</strong> Be prepared for these challenges through proper time management, continuous learning, and seeking mentorship from experienced professionals.'}
        </p>
      </div>
    </div>
  );
}
