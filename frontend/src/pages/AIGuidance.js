import React, { useState } from 'react';
import { 
  Brain, 
  FileText, 
  Upload, 
  Download,
  BarChart3,
  CheckCircle,
  AlertCircle,
  Lightbulb,
  Zap
} from 'lucide-react';
import { aiGuidanceService } from '../services/api';
import toast from 'react-hot-toast';

const AIGuidance = () => {
  const [activeTab, setActiveTab] = useState('resume');
  const [loading, setLoading] = useState(false);
  const [resumeAnalysis, setResumeAnalysis] = useState(null);
  const [roadmap, setRoadmap] = useState(null);
  const [skillGaps, setSkillGaps] = useState(null);

  // Analyze Resume
  const handleResumeAnalysis = async (file) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('resume', file);
      
      const result = await aiGuidanceService.analyzeResume(formData);
      if (result.error) {
        toast.error('Using demo data - backend service unavailable');
      } else {
        toast.success('Resume analyzed successfully!');
      }
      setResumeAnalysis(result.data.analysis);
    } catch (error) {
      toast.error('Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  // Generate Career Roadmap
  const handleGenerateRoadmap = async () => {
    setLoading(true);
    try {
      const profileData = {
        currentRole: "Student",
        targetRole: "AI Engineer", 
        skills: ["Python", "Machine Learning", "React"],
        experience: "2 years"
      };
      
      const result = await aiGuidanceService.generateRoadmap(profileData);
      if (result.error) {
        toast.error('Using demo data - backend service unavailable');
      } else {
        toast.success('Career roadmap generated!');
      }
      setRoadmap(result.data.roadmap);
    } catch (error) {
      toast.error('Roadmap generation failed');
    } finally {
      setLoading(false);
    }
  };

  // Analyze Skill Gaps
  const handleSkillGapAnalysis = async () => {
    setLoading(true);
    try {
      const currentSkills = ["Python", "React", "FastAPI", "MongoDB"];
      const targetRole = "Senior AI Engineer";
      
      const result = await aiGuidanceService.analyzeSkillGaps(currentSkills, targetRole);
      if (result.error) {
        toast.error('Using demo data - backend service unavailable');  
      } else {
        toast.success('Skill gaps analyzed!');
      }
      setSkillGaps(result.data.skillGaps);
    } catch (error) {
      toast.error('Skill analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 rounded-2xl p-8 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-black bg-opacity-10"></div>
        <div className="relative z-10">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2 flex items-center">
                <Brain className="w-10 h-10 mr-3 text-blue-300" />
                AI-Powered Career Guidance
              </h1>
              <p className="text-blue-100 text-lg">Get personalized insights and recommendations powered by advanced AI</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-blue-200">AI Status</p>
              <div className="flex items-center mt-1">
                <div className="w-3 h-3 bg-green-400 rounded-full mr-2 animate-pulse"></div>
                <p className="text-lg font-bold text-green-300">Active</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex flex-wrap gap-2 justify-center">
        {[
          { id: 'resume', label: 'Resume Analysis', icon: FileText },
          { id: 'roadmap', label: 'Career Roadmap', icon: BarChart3 },
          { id: 'skills', label: 'Skill Assessment', icon: Zap }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-100 text-blue-700 border border-blue-200'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        {/* Resume Analysis Tab */}
        {activeTab === 'resume' && (
          <div className="p-8">
            <div className="text-center mb-8">
              <FileText className="w-16 h-16 text-blue-500 mx-auto mb-4" />
              <h2 className="text-3xl font-bold text-gray-900 mb-2">AI Resume Analysis</h2>
              <p className="text-gray-600">Upload your resume for detailed AI-powered analysis and suggestions</p>
            </div>

            {/* Upload Section */}
            {!resumeAnalysis && (
              <div className="max-w-md mx-auto">
                <div className="border-2 border-dashed border-blue-300 rounded-xl p-8 text-center hover:border-blue-400 transition-colors">
                  <Upload className="w-12 h-12 text-blue-500 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload Your Resume</h3>
                  <p className="text-gray-600 mb-4">Supports PDF, DOC, and DOCX files</p>
                  
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx"
                    onChange={(e) => {
                      const file = e.target.files[0]; 
                      if (file) {
                        handleResumeAnalysis(file);
                      }
                    }}
                    className="hidden"
                    id="resume-upload"
                  />
                  
                  <label 
                    htmlFor="resume-upload"
                    className="inline-flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium cursor-pointer transition-colors"
                  >
                    <Upload className="w-5 h-5" />
                    <span>{loading ? 'Analyzing...' : 'Choose File'}</span>
                  </label>
                </div>
                
                {/* Demo Button */}
                <div className="text-center mt-4">
                  <button
                    onClick={() => handleResumeAnalysis(new File(["demo"], "demo.pdf", { type: "application/pdf" }))}
                    className="text-blue-600 hover:text-blue-700 font-medium"
                    disabled={loading}
                  >
                    {loading ? 'Analyzing...' : 'Try Demo Analysis'}
                  </button>
                </div>
              </div>
            )}

            {/* Analysis Results */}
            {resumeAnalysis && (
              <div className="space-y-6">
                {/* Overall Score */}
                <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6 border border-green-200">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-gray-900">Overall Score</h3>
                    <div className="text-3xl font-bold text-green-600">{resumeAnalysis.score || 0}/100</div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-4">
                    <div 
                      className="bg-green-600 h-4 rounded-full transition-all duration-500"
                      style={{ width: `${resumeAnalysis.score || 0}%` }}
                    ></div>
                  </div>
                </div>

                {/* Strengths */}
                <div className="bg-white rounded-xl border border-gray-200 p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                    <CheckCircle className="w-6 h-6 mr-2 text-green-600" />
                    Strengths
                  </h3>
                  <div className="space-y-3">
                    {(resumeAnalysis.strengths || []).map((strength, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                        <p className="text-gray-700">{strength}</p>
                      </div>
                    ))}
                  </div>
                  {(!resumeAnalysis.strengths || resumeAnalysis.strengths.length === 0) && (
                    <p className="text-gray-500 italic">No strengths identified yet.</p>
                  )}
                </div>

                {/* Improvements */}
                <div className="bg-white rounded-xl border border-gray-200 p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                    <AlertCircle className="w-6 h-6 mr-2 text-orange-600" />
                    Areas for Improvement
                  </h3>
                  <div className="space-y-3">
                    {(resumeAnalysis.improvements || []).map((improvement, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-orange-500 rounded-full mt-2"></div>
                        <p className="text-gray-700">{improvement}</p>
                      </div>
                    ))}
                  </div>
                  {(!resumeAnalysis.improvements || resumeAnalysis.improvements.length === 0) && (
                    <p className="text-gray-500 italic">No improvements identified yet.</p>
                  )}
                </div>

                {/* Recommendations */}
                <div className="bg-white rounded-xl border border-gray-200 p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                    <Lightbulb className="w-6 h-6 mr-2 text-blue-600" />
                    AI Recommendations
                  </h3>
                  <div className="space-y-3">
                    {(resumeAnalysis.recommendations || []).map((recommendation, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                        <p className="text-gray-700">{recommendation}</p>
                      </div>
                    ))}
                  </div>
                  {(!resumeAnalysis.recommendations || resumeAnalysis.recommendations.length === 0) && (
                    <p className="text-gray-500 italic">No recommendations available yet.</p>
                  )}
                </div>

                {/* Actions */}
                <div className="flex justify-center space-x-4">
                  <button
                    onClick={() => setResumeAnalysis(null)}
                    className="px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
                  >
                    Analyze New Resume
                  </button>
                  <button className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center space-x-2">
                    <Download className="w-5 h-5" />
                    <span>Download Report</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Career Roadmap Tab */}
        {activeTab === 'roadmap' && (
          <div className="p-8">
            <div className="text-center mb-8">
              <BarChart3 className="w-16 h-16 text-purple-500 mx-auto mb-4" />
              <h2 className="text-3xl font-bold text-gray-900 mb-2">AI Career Roadmap</h2>
              <p className="text-gray-600">Get a personalized career path based on your goals and current skills</p>
            </div>

            {!roadmap ? (
              <div className="text-center">
                <button
                  onClick={handleGenerateRoadmap}
                  disabled={loading}
                  className="px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium text-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 mx-auto"
                >
                  <Brain className="w-6 h-6" />
                  <span>{loading ? 'Generating...' : 'Generate My Roadmap'}</span>
                </button>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Roadmap Header */}
                <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 border border-purple-200">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{roadmap.title || 'Career Roadmap'}</h3>
                  <p className="text-purple-600 font-medium">Timeline: {roadmap.timeline || 'Custom'}</p>
                </div>

                {/* Roadmap Phases */}
                <div className="space-y-6">
                  {(roadmap.phases || []).map((phase, index) => (
                    <div key={index} className="bg-white rounded-xl border border-gray-200 p-6">
                      <h4 className="text-xl font-bold text-gray-900 mb-4">{phase.phase || `Phase ${index + 1}`}</h4>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Skills */}
                        <div>
                          <h5 className="font-semibold text-gray-900 mb-3">Key Skills</h5>
                          <div className="space-y-2"> 
                            {(phase.skills || []).map((skill, idx) => (
                              <div key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                                {skill}
                              </div>
                            ))}
                          </div>
                          {(!phase.skills || phase.skills.length === 0) && (
                            <p className="text-gray-500 text-sm italic">No skills defined</p>
                          )}
                        </div>

                        {/* Resources */}
                        <div>
                          <h5 className="font-semibold text-gray-900 mb-3">Learning Resources</h5>
                          <div className="space-y-2"> 
                            {(phase.resources || []).map((resource, idx) => (
                              <div key={idx} className="text-gray-700 text-sm">{resource}</div>
                            ))}
                          </div>
                          {(!phase.resources || phase.resources.length === 0) && (
                            <p className="text-gray-500 text-sm italic">No resources defined</p>
                          )}
                        </div>

                        {/* Milestones */}
                        <div>
                          <h5 className="font-semibold text-gray-900 mb-3">Milestones</h5>
                          <div className="space-y-2"> 
                            {(phase.milestones || []).map((milestone, idx) => (
                              <div key={idx} className="flex items-center space-x-2">
                                <CheckCircle className="w-4 h-4 text-green-500" />
                                <span className="text-gray-700 text-sm">{milestone}</span>
                              </div>
                            ))}
                          </div>
                          {(!phase.milestones || phase.milestones.length === 0) && (
                            <p className="text-gray-500 text-sm italic">No milestones defined</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                {(!roadmap.phases || roadmap.phases.length === 0) && (
                  <div className="text-center py-8">
                    <p className="text-gray-500 italic">No roadmap phases generated yet.</p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex justify-center space-x-4">
                  <button
                    onClick={() => setRoadmap(null)}
                    className="px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
                  >
                    Generate New Roadmap
                  </button>
                  <button className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors">
                    Save Roadmap
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Skills Assessment Tab */}
        {activeTab === 'skills' && (
          <div className="p-8">
            <div className="text-center mb-8">
              <Zap className="w-16 h-16 text-orange-500 mx-auto mb-4" />
              <h2 className="text-3xl font-bold text-gray-900 mb-2">AI Skill Assessment</h2>
              <p className="text-gray-600">Identify skill gaps and get recommendations for your career growth</p>
            </div>

            {!skillGaps ? (
              <div className="text-center">
                <button
                  onClick={handleSkillGapAnalysis}
                  disabled={loading}
                  className="px-8 py-4 bg-orange-600 hover:bg-orange-700 text-white rounded-lg font-medium text-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 mx-auto"
                >
                  <Zap className="w-6 h-6" />
                  <span>{loading ? 'Analyzing...' : 'Analyze My Skills'}</span>
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Strong Skills */}
                <div className="bg-green-50 rounded-xl border border-green-200 p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                    <CheckCircle className="w-6 h-6 mr-2 text-green-600" />
                    Strong Skills
                  </h3>
                  <div className="space-y-3">
                    {(skillGaps.strong || []).map((skill, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                        <span className="text-gray-700 font-medium">{skill}</span>
                      </div>
                    ))}
                  </div>
                  {(!skillGaps.strong || skillGaps.strong.length === 0) && (
                    <p className="text-gray-500 italic">No strong skills identified yet.</p>
                  )}
                </div>

                {/* Skills to Develop */}
                <div className="bg-yellow-50 rounded-xl border border-yellow-200 p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                    <AlertCircle className="w-6 h-6 mr-2 text-yellow-600" />
                    Skills to Develop
                  </h3>
                  <div className="space-y-3">
                    {(skillGaps.developing || []).map((skill, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                        <span className="text-gray-700 font-medium">{skill}</span>
                      </div>
                    ))}
                  </div>
                  {(!skillGaps.developing || skillGaps.developing.length === 0) && (
                    <p className="text-gray-500 italic">No developing skills identified yet.</p>
                  )}
                </div>

                {/* Missing Skills */}
                <div className="bg-red-50 rounded-xl border border-red-200 p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                    <AlertCircle className="w-6 h-6 mr-2 text-red-600" />
                    Missing Skills
                  </h3>
                  <div className="space-y-3">
                    {(skillGaps.missing || []).map((skill, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                        <span className="text-gray-700 font-medium">{skill}</span>
                      </div>
                    ))}
                  </div>
                  {(!skillGaps.missing || skillGaps.missing.length === 0) && (
                    <p className="text-gray-500 italic">No missing skills identified yet.</p>
                  )}
                </div>

                {/* Recommendations */}
                <div className="bg-blue-50 rounded-xl border border-blue-200 p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                    <Lightbulb className="w-6 h-6 mr-2 text-blue-600" />
                    AI Recommendations
                  </h3>
                  <div className="space-y-3">
                    {(skillGaps.recommendations || []).map((rec, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                        <p className="text-gray-700">{rec}</p>
                      </div>
                    ))}
                  </div>
                  {(!skillGaps.recommendations || skillGaps.recommendations.length === 0) && (
                    <p className="text-gray-500 italic">No recommendations available yet.</p>
                  )}
                </div>
              </div>
            )}

            {skillGaps && (
              <div className="flex justify-center space-x-4 mt-8">
                <button
                  onClick={() => setSkillGaps(null)}
                  className="px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
                >
                  Analyze Again
                </button>
                <button className="px-6 py-3 bg-orange-600 hover:bg-orange-700 text-white rounded-lg font-medium transition-colors">
                  Create Learning Plan
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AIGuidance;
