import React, { useState, useEffect } from 'react';
import { Map, Network, Target, TrendingUp, Brain } from 'lucide-react';
import { careerService } from '../services/api';
import toast from 'react-hot-toast';

const CareerAtlas = () => {
  const [activeTab, setActiveTab] = useState('paths');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState({});

  const loadCareerPaths = async () => {
    setLoading(true);
    try {
      const response = await careerService.getCareerPaths({
        user_id: 'demo_user',
        current_role: 'Student',
        interests: ['AI', 'Machine Learning']
      });
      setData(prev => ({ ...prev, paths: response.data }));
      toast.success('Career paths loaded!');
    } catch (error) {
      console.log('Demo mode - showing mock data');
      setData(prev => ({ ...prev, paths: {
        recommended_paths: [
          {
            title: 'AI Engineer',
            description: 'Build intelligent systems and machine learning models',
            timeline: '2-3 years',
            salary_range: '$80,000 - $150,000',
            market_demand: 'Very High'
          },
          {
            title: 'Data Scientist', 
            description: 'Analyze complex data to drive business insights',
            timeline: '1-2 years',
            salary_range: '$70,000 - $130,000',
            market_demand: 'High'
          }
        ]
      }}));
    } finally {
      setLoading(false);
    }
  };

  const loadKnowledgeGraph = async () => {
    setLoading(true);
    try {
      const response = await careerService.getKnowledgeGraph({ domain: 'AI', depth: 3 });
      setData(prev => ({ ...prev, knowledge: response.data }));
      toast.success('Knowledge graph loaded!');
    } catch (error) {
      console.log('Demo mode - showing mock data');
      setData(prev => ({ ...prev, knowledge: {
        knowledge_graph: {
          core_concepts: ['Python', 'Machine Learning', 'Deep Learning', 'Data Analysis', 'Statistics'],
          career_paths: [
            { role: 'ML Engineer', skills: ['TensorFlow', 'PyTorch', 'Python'] },
            { role: 'Data Scientist', skills: ['Pandas', 'Scikit-learn', 'SQL'] },
            { role: 'AI Researcher', skills: ['Research', 'Publications', 'Mathematics'] }
          ]
        }
      }}));
    } finally {
      setLoading(false);
    }
  };

  const loadMarketAnalysis = async () => {
    setLoading(true);
    try {
      const response = await careerService.getMarketAnalysis({ role: 'AI Engineer' });
      setData(prev => ({ ...prev, market: response.data }));
      toast.success('Market analysis loaded!');
    } catch (error) {
      console.log('Demo mode - showing mock data');
      setData(prev => ({ ...prev, market: {
        market_data: {
          demand_level: 'Very High',
          job_availability: { total_openings: 15420 },
          salary_trends: { yoy_growth: '+15%' }
        }
      }}));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'paths') loadCareerPaths();
    else if (activeTab === 'knowledge') loadKnowledgeGraph();
    else if (activeTab === 'market') loadMarketAnalysis();
  }, [activeTab]);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Career Atlas</h1>
        <p className="text-lg text-gray-600">Navigate your career path with AI-powered insights</p>
      </div>

      {/* Tabs */}
      <div className="flex justify-center space-x-4">
        {[
          { id: 'paths', label: 'Career Paths', icon: Map },
          { id: 'knowledge', label: 'Knowledge Graph', icon: Network },
          { id: 'market', label: 'Market Analysis', icon: TrendingUp }
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

      {/* Content */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading career insights...</p>
          </div>
        ) : (
          <>
            {activeTab === 'paths' && data.paths && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Recommended Career Paths</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {data.paths.recommended_paths?.map((path, index) => (
                    <div key={index} className="p-6 bg-gray-50 rounded-xl">
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">{path.title}</h3>
                      <p className="text-gray-600 mb-4">{path.description}</p>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-500">Timeline:</span>
                          <span className="font-medium">{path.timeline}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-500">Salary Range:</span>
                          <span className="font-medium text-green-600">{path.salary_range}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-500">Market Demand:</span>
                          <span className="font-medium text-blue-600">{path.market_demand}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'knowledge' && data.knowledge && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">AI Knowledge Graph</h2>
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Core Concepts</h3>
                    <div className="flex flex-wrap gap-3">
                      {data.knowledge.knowledge_graph?.core_concepts?.map((concept, index) => (
                        <span key={index} className="px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                          {concept}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Career Paths</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {data.knowledge.knowledge_graph?.career_paths?.map((career, index) => (
                        <div key={index} className="p-4 bg-purple-50 rounded-lg">
                          <h4 className="font-medium text-purple-900">{career.role}</h4>
                          <div className="mt-2 flex flex-wrap gap-1">
                            {career.skills?.map((skill, idx) => (
                              <span key={idx} className="text-xs px-2 py-1 bg-purple-200 text-purple-700 rounded">
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'market' && data.market && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Market Analysis</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div className="p-6 bg-green-50 rounded-xl">
                    <h3 className="font-semibold text-green-900 mb-2">Demand Level</h3>
                    <p className="text-2xl font-bold text-green-700">{data.market.market_data?.demand_level}</p>
                  </div>
                  <div className="p-6 bg-blue-50 rounded-xl">
                    <h3 className="font-semibold text-blue-900 mb-2">Job Openings</h3>
                    <p className="text-2xl font-bold text-blue-700">
                      {data.market.market_data?.job_availability?.total_openings?.toLocaleString()}
                    </p>
                  </div>
                  <div className="p-6 bg-purple-50 rounded-xl">
                    <h3 className="font-semibold text-purple-900 mb-2">Salary Growth</h3>
                    <p className="text-2xl font-bold text-purple-700">
                      {data.market.market_data?.salary_trends?.yoy_growth}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default CareerAtlas;
