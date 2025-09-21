import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Upload, 
  Brain, 
  FileText, 
  User,
  Map,
  Github,
  Linkedin,
  Target,
  TrendingUp
} from 'lucide-react';
import { aiService } from '../services/api';
import toast from 'react-hot-toast';

const AIGuidance = () => {
  const [activeTab, setActiveTab] = useState('resume');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState({});

  // Resume Analysis
  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setLoading(true);
    try {
      const response = await aiService.analyzeResume(file);
      setResults(prev => ({ ...prev, resume: response.data }));
      toast.success('Resume analyzed successfully!');
    } catch (error) {
      toast.error('Resume analysis failed');
    } finally {
      setLoading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1
  });

  // Persona Creation
  const handlePersonaCreation = async () => {
    setLoading(true);
    try {
      const response = await aiService.createPersona({
        user_id: 'demo_user',
        name: 'Demo User',
        field: 'AI Engineering',
        experience: 'Intermediate'
      });
      setResults(prev => ({ ...prev, persona: response.data }));
      toast.success('AI Persona created successfully!');
    } catch (error) {
      toast.error('Persona creation failed');
    } finally {
      setLoading(false);
    }
  };

  // Psychometric Assessment
  const handlePsychometricAssessment = async () => {
    setLoading(true);
    try {
      const response = await aiService.psychometricAssessment({
        user_id: 'demo_user',
        responses: [
          { question: 'I enjoy complex problems', rating: 9 },
          { question: 'I prefer working alone', rating: 7 },
          { question: 'I adapt to change easily', rating: 8 }
        ]
      });
      setResults(prev => ({ ...prev, psychometric: response.data }));
      toast.success('Psychometric assessment completed!');
    } catch (error) {
      toast.error('Assessment failed');
    } finally {
      setLoading(false);
    }
  };

  // Roadmap Generation  
  const handleRoadmapGeneration = async () => {
    setLoading(true);
    try {
      const response = await aiService.generateRoadmap({
        user_id: 'demo_user',
        current_role: 'Junior AI Engineer',
        target_role: 'Senior AI Engineer',
        timeline: '18 months'
      });
      setResults(prev => ({ ...prev, roadmap: response.data }));
      toast.success('Career roadmap generated!');
    } catch (error) {
      toast.error('Roadmap generation failed');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'resume', label: 'Resume Analysis', icon: FileText },
    { id: 'persona', label: 'AI Persona', icon: User },
    { id: 'assessment', label: 'Psychometric', icon: Brain },
    { id: 'roadmap', label: 'Career Roadmap', icon: Map },
  ];

  const TabButton = ({ tab, isActive, onClick }) => {
    const Icon = tab.icon;
    return (
      <button
        onClick={() => onClick(tab.id)}
        className={`flex items-center space-x-2 px-4 py-3 rounded-lg font-medium transition-colors ${
          isActive
            ? 'bg-blue-100 text-blue-700 border border-blue-200'
            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
        }`}
      >
        <Icon className="w-5 h-5" />
        <span>{tab.label}</span>
      </button>
    );
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">AI-Powered Career Guidance</h1>
        <p className="text-lg text-gray-600">
          Get personalized insights and recommendations powered by advanced AI
        </p>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 justify-center">
        {tabs.map((tab) => (
          <TabButton
            key={tab.id}
            tab={tab}
            isActive={activeTab === tab.id}
            onClick={setActiveTab}
          />
        ))}
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        {/* Resume Analysis Tab */}
        {activeTab === 'resume' && (
          <div className="p-8">
            <div className="text-center mb-8">
              <FileText className="w-12 h-12 text-blue-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Resume Analysis</h2>
              <p className="text-gray-600">Upload your resume for AI-powered analysis and optimization suggestions</p>
            </div>

            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors ${
                isDragActive 
                  ? 'border-blue-400 bg-blue-50' 
                  : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              {isDragActive ? (
                <p className="text-lg text-blue-600">Drop your resume here...</p>
              ) : (
                <div>
                  <p className="text-lg text-gray-600 mb-2">
                    Drag & drop your resume here, or click to browse
                  </p>
                  <p className="text-sm text-gray-500">
                    Supports PDF, DOC, and DOCX files
                  </p>
                </div>
              )}
            </div>

            {results.resume && (
              <div className="mt-8 p-6 bg-gray-50 rounded-xl">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Results</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">ATS Score</h4>
                    <div className="flex items-center">
                      <div className="flex-1 bg-gray-200 rounded-full h-3 mr-4">
                        <div 
                          className="bg-green-500 h-3 rounded-full" 
                          style={{ width: `${results.resume.analysis?.ats_score || 85}%` }}
                        ></div>
                      </div>
                      <span className="font-semibold text-green-600">
                        {results.resume.analysis?.ats_score || 85}%
                      </span>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Experience Level</h4>
                    <p className="text-gray-600">{results.resume.analysis?.experience_level || 'Intermediate'}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Persona Tab */}
        {activeTab === 'persona' && (
          <div className="p-8">
            <div className="text-center mb-8">
              <User className="w-12 h-12 text-purple-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">AI Persona Creation</h2>
              <p className="text-gray-600">Generate a personalized professional persona based on your profile</p>
            </div>

            <div className="text-center">
              <button
                onClick={handlePersonaCreation}
                disabled={loading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Creating Persona...' : 'Generate AI Persona'}
              </button>
            </div>

            {results.persona && (
              <div className="mt-8 p-6 bg-purple-50 rounded-xl">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Your AI Persona</h3>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-gray-900">Professional Identity</h4>
                    <p className="text-gray-600">{results.persona.persona?.professional_identity || 'AI Engineering Specialist focused on innovative solutions'}</p>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Brand Statement</h4>
                    <p className="text-gray-600">{results.persona.persona?.brand_statement || 'Passionate about leveraging AI to solve complex problems'}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Assessment Tab */}
        {activeTab === 'assessment' && (
          <div className="p-8">
            <div className="text-center mb-8">
              <Brain className="w-12 h-12 text-green-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Psychometric Assessment</h2>
              <p className="text-gray-600">Discover your personality type and work preferences</p>
            </div>

            <div className="text-center">
              <button
                onClick={handlePsychometricAssessment}
                disabled={loading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Analyzing...' : 'Start Assessment'}
              </button>
            </div>

            {results.psychometric && (
              <div className="mt-8 p-6 bg-green-50 rounded-xl">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Assessment Results</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-gray-900">Personality Type</h4>
                    <p className="text-gray-600 text-lg font-semibold">
                      {results.psychometric.assessment_results?.personality_type || 'Analytical Innovator'}
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Confidence Score</h4>
                    <p className="text-gray-600 text-lg font-semibold">
                      {Math.round((results.psychometric.confidence_score || 0.85) * 100)}%
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Roadmap Tab */}
        {activeTab === 'roadmap' && (
          <div className="p-8">
            <div className="text-center mb-8">
              <Map className="w-12 h-12 text-orange-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Career Roadmap</h2>
              <p className="text-gray-600">Get a personalized career path with milestones and timelines</p>
            </div>

            <div className="text-center">
              <button
                onClick={handleRoadmapGeneration}
                disabled={loading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Generating Roadmap...' : 'Generate Career Roadmap'}
              </button>
            </div>

            {results.roadmap && (
              <div className="mt-8 p-6 bg-orange-50 rounded-xl">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Career Roadmap</h3>
                <div className="space-y-6">
                  {(results.roadmap.roadmap?.milestones || [
                    {
                      phase: 'Foundation Phase (0-6 months)',
                      objectives: ['Master Python fundamentals', 'Learn machine learning basics', 'Build first AI project']
                    },
                    {
                      phase: 'Growth Phase (6-12 months)', 
                      objectives: ['Advanced ML algorithms', 'Deep learning frameworks', 'Industry experience']
                    },
                    {
                      phase: 'Leadership Phase (12-18 months)',
                      objectives: ['Lead AI projects', 'Mentor junior developers', 'Strategic AI planning']
                    }
                  ]).map((milestone, index) => (
                    <div key={index} className="flex items-start space-x-4">
                      <div className="w-8 h-8 bg-orange-200 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-orange-800 font-semibold text-sm">{index + 1}</span>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900">{milestone.phase}</h4>
                        <ul className="text-gray-600 text-sm mt-2 space-y-1">
                          {milestone.objectives?.map((objective, idx) => (
                            <li key={idx}>• {objective}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-xl flex items-center space-x-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <span className="text-gray-700">Processing with AI...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIGuidance;
