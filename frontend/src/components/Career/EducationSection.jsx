import React, { useState } from 'react';
import { ChevronDown, Award, BookOpen, ExternalLink, Zap } from 'lucide-react';

export default function EducationSection({ career }) {
  const [expandedEducation, setExpandedEducation] = useState(false);
  const [expandedCerts, setExpandedCerts] = useState(false);

  if (!career) return null;

  const education = career.education || {};
  const certifications = career.certifications || [
    { name: 'Industry Certification', provider: 'Professional Body', duration: '6 months' },
    { name: 'Advanced Credential', provider: 'Specialist Training', duration: '12 months' }
  ];

  return (
    <div className="bg-white rounded-2xl shadow-lg p-8 space-y-6">
      <h2 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
        <BookOpen className="w-8 h-8 text-indigo-600" />
        Education & Certifications
      </h2>

      {/* Education Requirements */}
      <div>
        <button
          onClick={() => setExpandedEducation(!expandedEducation)}
          className="w-full flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-cyan-50 border-2 border-blue-200 rounded-xl hover:border-blue-400 transition-all"
        >
          <div className="flex items-center gap-3">
            <BookOpen className="w-6 h-6 text-blue-600" />
            <span className="font-bold text-lg text-gray-900">Education Requirements</span>
          </div>
          <ChevronDown className={`w-5 h-5 text-blue-600 transition-transform ${expandedEducation ? 'rotate-180' : ''}`} />
        </button>

        {expandedEducation && (
          <div className="mt-4 space-y-4">
            {education.minimum && (
              <div className="p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                <h3 className="font-bold text-blue-900 mb-2">🎓 Minimum Education</h3>
                <p className="text-blue-800">{education.minimum}</p>
              </div>
            )}
            {education.preferred && (
              <div className="p-4 bg-cyan-50 rounded-lg border-l-4 border-cyan-500">
                <h3 className="font-bold text-cyan-900 mb-2">⭐ Preferred Education</h3>
                <p className="text-cyan-800">{education.preferred}</p>
              </div>
            )}
            {education.alternative && (
              <div className="p-4 bg-indigo-50 rounded-lg border-l-4 border-indigo-500">
                <h3 className="font-bold text-indigo-900 mb-2">🚀 Alternative Paths</h3>
                <p className="text-indigo-800">{education.alternative}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Certifications */}
      <div>
        <button
          onClick={() => setExpandedCerts(!expandedCerts)}
          className="w-full flex items-center justify-between p-4 bg-gradient-to-r from-amber-50 to-orange-50 border-2 border-amber-200 rounded-xl hover:border-amber-400 transition-all"
        >
          <div className="flex items-center gap-3">
            <Award className="w-6 h-6 text-amber-600" />
            <span className="font-bold text-lg text-gray-900">Recommended Certifications</span>
          </div>
          <ChevronDown className={`w-5 h-5 text-amber-600 transition-transform ${expandedCerts ? 'rotate-180' : ''}`} />
        </button>

        {expandedCerts && (
          <div className="mt-4 space-y-3">
            {certifications && certifications.length > 0 ? (
              certifications.map((cert, i) => (
                <div key={i} className="p-4 bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg border-2 border-amber-100 hover:border-amber-300 transition-all">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-bold text-amber-900">{cert.name}</h4>
                    <span className="px-2 py-1 bg-amber-200 text-amber-800 text-xs font-bold rounded">
                      ⏱️ {cert.duration}
                    </span>
                  </div>
                  <p className="text-sm text-amber-700 mb-2">{cert.provider}</p>
                  <div className="flex items-center gap-2 text-amber-600 text-sm">
                    <Zap className="w-4 h-4" />
                    <span>Boosts credibility and salary prospects</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500">No certification data available</p>
            )}
          </div>
        )}
      </div>

      {/* Pro Tip */}
      <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border-l-4 border-purple-500">
        <p className="text-purple-900 font-medium">
          💡 <span className="font-bold">Pro Tip:</span> While formal education is often required, alternative paths like bootcamps are increasingly valued by employers. Consider your learning style and budget.
        </p>
      </div>
    </div>
  );
}
