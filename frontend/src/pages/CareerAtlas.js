import React, { useState, useEffect } from 'react';
import { 
  MapPin, 
  Briefcase, 
  TrendingUp, 
  DollarSign,
  Users,
  BarChart3,
  Globe,
  Lightbulb,
  Star,
  ChevronRight,
  Search
} from 'lucide-react';
import { careerAtlasService } from '../services/api';
import toast from 'react-hot-toast';

const CareerAtlas = () => {
  const [activeTab, setActiveTab] = useState('insights');
  const [loading, setLoading] = useState(false);
  const [insights, setInsights] = useState(null);
  const [trends, setTrends] = useState(null);
  const [selectedField, setSelectedField] = useState('Artificial Intelligence');

  // Load Career Insights
  const loadCareerInsights = async (field) => {
    setLoading(true);
    try {
      const result = await careerAtlasService.getCareerInsights(field);
      if (result.error) {
        toast.error('Using demo data - backend service unavailable');
      } else {
        toast.success('Career insights loaded!');
      }
      setInsights(result.data.insights);
    } catch (error) {
      toast.error('Failed to load insights');
    } finally {
      setLoading(false);
    }
  };

  // Load Industry Trends
  const loadIndustryTrends = async () => {
    setLoading(true);
    try {
      const result = await careerAtlasService.getIndustryTrends();
      if (result.error) {
        toast.error('Using demo data - backend service unavailable');
      } else {
        toast.success('Industry trends loaded!');
      }
      setTrends(result.data.trends);
    } catch (error) {
      toast.error('Failed to load trends');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'insights') {
      loadCareerInsights(selectedField);
    } else if (activeTab === 'trends') {
      loadIndustryTrends();
    }
  }, [activeTab, selectedField]);

  const careerFields = [
    'Artificial Intelligence',
    'Data Science',
    'Software Engineering',
    'Product Management',
    'Digital Marketing',
    'Cybersecurity'
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 via-teal-600 to-blue-600 rounded-2xl p-8 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-black bg-opacity-10"></div>
        <div className="relative z-10">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2 flex items-center">
                <Globe className="w-10 h-10 mr-3 text-green-300" />
                Career Atlas
              </h1>
              <p className="text-green-100 text-lg">Explore career paths and industry insights powered by real-time data</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-green-200">Market Status</p>
              <div className="flex items-center mt-1">
                <div className="w-3 h-3 bg-green-400 rounded-full mr-2 animate-pulse"></div>
                <p className="text-lg font-bold text-green-300">Live</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex flex-wrap gap-2 justify-center">
        {[
          { id: 'insights', label: 'Career Insights', icon: Lightbulb },
          { id: 'trends', label: 'Industry Trends', icon: TrendingUp },
          { id: 'explorer', label: 'Path Explorer', icon: MapPin }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-green-100 text-green-700 border border-green-200'
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
        {/* Career Insights Tab */}
        {activeTab === 'insights' && (
          <div className="p-8">
            <div className="mb-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Career Field Insights</h2>
                <div className="flex items-center space-x-3">
                  <Search className="w-5 h-5 text-gray-400" />
                  <select
                    value={selectedField}
                    onChange={(e) => setSelectedField(e.target.value)}
                    className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  >
                    {careerFields.map(field => (
                      <option key={field} value={field}>{field}</option>
                    ))}
                  </select>
                </div>
              </div>

              {loading && (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
                  <p className="text-gray-600 mt-4">Loading insights...</p>
                </div>
              )}

              {insights && (
                <div className="space-y-8">
                  {/* Field Overview */}
                  <div className="bg-green-50 rounded-xl border border-green-200 p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                      <Briefcase className="w-6 h-6 mr-2 text-green-600" />
                      {insights.field} Overview
                    </h3>
                    <p className="text-gray-700 text-lg leading-relaxed">{insights.overview}</p>
                  </div>

                  {/* Key Trends */}
                  <div className="bg-white rounded-xl border border-gray-200 p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
                      <TrendingUp className="w-6 h-6 mr-2 text-blue-600" />
                      Key Market Trends
                    </h3>
                    <div className="space-y-4">
                      {insights.trends.map((trend, index) => (
                        <div key={index} className="flex items-start space-x-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                          <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                          <p className="text-gray-700 flex-1">{trend}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Career Opportunities */}
                  <div className="bg-white rounded-xl border border-gray-200 p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
                      <Star className="w-6 h-6 mr-2 text-yellow-600" />
                      Top Career Opportunities
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {insights.opportunities.map((opp, index) => (
                        <div key={index} className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl border border-yellow-200 p-6 hover:shadow-lg transition-shadow">
                          <div className="flex items-center justify-between mb-4">
                            <h4 className="font-bold text-gray-900 text-lg">{opp.role}</h4>
                            <div className={`px-2 py-1 rounded-full text-xs font-bold ${
                              opp.demand === 'Very High' ? 'bg-red-100 text-red-800' :
                              opp.demand === 'High' ? 'bg-orange-100 text-orange-800' : 
                              'bg-yellow-100 text-yellow-800'
                            }`}>
                              {opp.demand}
                            </div>
                          </div>
                          
                          <div className="space-y-3">
                            <div className="flex items-center space-x-2">
                              <DollarSign className="w-4 h-4 text-green-600" />
                              <span className="text-sm text-gray-700">Salary: <strong>{opp.salaryRange}</strong></span>
                            </div>
                            <div className="flex items-center space-x-2">
                              <TrendingUp className="w-4 h-4 text-blue-600" />
                              <span className="text-sm text-gray-700">Growth: <strong>{opp.growth}</strong></span>
                            </div>
                          </div>

                          <button className="w-full mt-4 bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2">
                            <span>Explore Path</span>
                            <ChevronRight className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Industry Trends Tab */}
        {activeTab === 'trends' && (
          <div className="p-8">
            <div className="text-center mb-8">
              <TrendingUp className="w-16 h-16 text-blue-500 mx-auto mb-4" />
              <h2 className="text-3xl font-bold text-gray-900 mb-2">Industry Trends</h2>
              <p className="text-gray-600">Stay ahead with the latest market movements and emerging opportunities</p>
            </div>

            {loading && (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p className="text-gray-600 mt-4">Loading trends...</p>
              </div>
            )}

            {trends && (
              <div className="space-y-6">
                {trends.map((trend, index) => (
                  <div key={index} className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-gray-900 mb-2">{trend.title}</h3>
                        <p className="text-gray-700">{trend.description}</p>
                      </div>
                      <div className={`px-3 py-1 rounded-full text-sm font-bold ml-4 ${
                        trend.impact === 'High' ? 'bg-red-100 text-red-800' :
                        trend.impact === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {trend.impact} Impact
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <span>🚀 Trending #{index + 1}</span>
                        <span>📈 Growing Fast</span>
                      </div>
                      <button className="text-blue-600 hover:text-blue-700 font-medium text-sm">
                        Learn More →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Path Explorer Tab */}
        {activeTab === 'explorer' && (
          <div className="p-8">
            <div className="text-center mb-8">
              <MapPin className="w-16 h-16 text-purple-500 mx-auto mb-4" />
              <h2 className="text-3xl font-bold text-gray-900 mb-2">Career Path Explorer</h2>
              <p className="text-gray-600">Discover personalized career paths based on your interests and goals</p>
            </div>

            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-200 p-8 text-center">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Interactive Career Mapping</h3>
              <p className="text-gray-600 mb-6">Explore different career trajectories, skill requirements, and growth opportunities in an interactive format.</p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                <div className="bg-white rounded-lg p-6 shadow-sm">
                  <Users className="w-8 h-8 text-purple-600 mx-auto mb-3" />
                  <h4 className="font-semibold text-gray-900 mb-2">Role Matching</h4>
                  <p className="text-sm text-gray-600">Find roles that match your skills and interests</p>
                </div>
                <div className="bg-white rounded-lg p-6 shadow-sm">
                  <BarChart3 className="w-8 h-8 text-blue-600 mx-auto mb-3" />
                  <h4 className="font-semibold text-gray-900 mb-2">Growth Analytics</h4>
                  <p className="text-sm text-gray-600">Analyze career growth potential and trajectories</p>
                </div>
                <div className="bg-white rounded-lg p-6 shadow-sm">
                  <Lightbulb className="w-8 h-8 text-yellow-600 mx-auto mb-3" />
                  <h4 className="font-semibold text-gray-900 mb-2">Smart Recommendations</h4>
                  <p className="text-sm text-gray-600">Get AI-powered career recommendations</p>
                </div>
              </div>

              <button className="mt-8 bg-purple-600 hover:bg-purple-700 text-white px-8 py-3 rounded-lg font-medium transition-colors">
                Launch Explorer (Coming Soon)
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CareerAtlas;
