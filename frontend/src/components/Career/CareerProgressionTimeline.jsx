import React, { useState } from 'react';
import { Briefcase, DollarSign, TrendingUp, ChevronDown } from 'lucide-react';

export default function CareerProgressionTimeline({ career }) {
  const [expandedLevel, setExpandedLevel] = useState(null);

  if (!career) return null;

  const progression = career.career_path || [
    {
      level: 'Junior',
      years_min: 0,
      years_max: 2,
      salary: { min: 50000, max: 70000 },
      description: 'Entry-level position with mentorship focus',
      skills: ['Core technical skills', 'Team collaboration', 'Project support']
    },
    {
      level: 'Mid-Level',
      years_min: 2,
      years_max: 5,
      salary: { min: 70000, max: 100000 },
      description: 'Growing expertise and independent responsibility',
      skills: ['Leadership basics', 'Technical depth', 'Project ownership']
    },
    {
      level: 'Senior',
      years_min: 5,
      years_max: 10,
      salary: { min: 100000, max: 150000 },
      description: 'Strategic leadership and mentoring role',
      skills: ['Team leadership', 'Strategic planning', 'Mentoring']
    }
  ];

  if (!progression || progression.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <h2 className="text-2xl font-bold mb-4 text-gray-900">Career Progression</h2>
        <p className="text-gray-500">Career progression data not available</p>
      </div>
    );
  }

  const getSalaryRange = (level) => {
    if (typeof level.salary === 'object') {
      return `$${(level.salary.min / 1000).toFixed(0)}K - $${(level.salary.max / 1000).toFixed(0)}K`;
    }
    return `$${(level.salary / 1000).toFixed(0)}K`;
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-8">
      <div className="flex items-center gap-3 mb-8">
        <TrendingUp className="w-8 h-8 text-indigo-600" />
        <h2 className="text-3xl font-bold text-gray-900">Career Progression Path</h2>
      </div>

      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-8 top-0 bottom-0 w-1 bg-gradient-to-b from-indigo-600 via-indigo-400 to-indigo-200"></div>

        {/* Timeline items */}
        <div className="space-y-6">
          {progression.map((level, i) => (
            <div key={i} className="pl-32 pb-4">
              {/* Timeline dot */}
              <div className="absolute left-0 top-4 w-16 h-16 bg-gradient-to-br from-indigo-600 to-indigo-700 rounded-full flex items-center justify-center border-4 border-white shadow-lg hover:scale-110 transition-transform">
                <Briefcase className="w-8 h-8 text-white" />
              </div>

              {/* Content card */}
              <button
                onClick={() => setExpandedLevel(expandedLevel === i ? null : i)}
                className="w-full text-left"
              >
                <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-6 hover:shadow-lg transition-all border-2 border-indigo-100 hover:border-indigo-300">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="text-2xl font-bold text-gray-900">{level.level}</h3>
                    <div className="flex gap-3">
                      <span className="text-sm font-bold px-3 py-1 bg-indigo-600 text-white rounded-full">
                        {level.years_min || level.years}-{level.years_max} yrs
                      </span>
                      <ChevronDown className={`w-5 h-5 text-indigo-600 transition-transform ${expandedLevel === i ? 'rotate-180' : ''}`} />
                    </div>
                  </div>

                  <p className="text-gray-700 mb-4">{level.description}</p>

                  <div className="flex items-center gap-2 text-lg font-bold text-indigo-600">
                    <DollarSign className="w-5 h-5" />
                    {getSalaryRange(level)}
                  </div>

                  {/* Expanded details */}
                  {expandedLevel === i && (
                    <div className="mt-4 pt-4 border-t-2 border-indigo-200 space-y-3">
                      <div>
                        <h4 className="font-bold text-gray-900 mb-2">Key Skills:</h4>
                        <div className="flex flex-wrap gap-2">
                          {(level.skills || []).map((skill, si) => (
                            <span key={si} className="px-3 py-1 bg-indigo-200 text-indigo-800 rounded-full text-sm font-medium">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 italic">
                        💡 These are estimates based on industry standards. Actual progression varies by company and individual performance.
                      </p>
                    </div>
                  )}
                </div>
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
