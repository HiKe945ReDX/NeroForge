import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, TrendingUp, Briefcase, DollarSign } from 'lucide-react';
import { API_CONFIG } from '../config/api';

export default function CareerAtlas() {
  const navigate = useNavigate();
  const [careers, setCareers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedField, setSelectedField] = useState('all');

  useEffect(() => {
    fetchCareers();
  }, []);

  const fetchCareers = async () => {
    try {
      const response = await fetch(`${API_CONFIG.GATEWAY_URL}/api/careers`);
      const data = await response.json();
      setCareers(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching careers:', error);
      setLoading(false);
    }
  };

  const filteredCareers = careers.filter(career => {
    const matchesSearch = career.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         career.field.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesField = selectedField === 'all' || career.field === selectedField;
    return matchesSearch && matchesField;
  });

  const fields = ['all', ...new Set(careers.map(c => c.field))];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-2xl font-semibold text-gray-700">Loading careers...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Career Atlas</h1>

        {/* Search & Filter */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search careers..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <select
                value={selectedField}
                onChange={(e) => setSelectedField(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                {fields.map(field => (
                  <option key={field} value={field}>
                    {field === 'all' ? 'All Fields' : field}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Career Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCareers.map((career) => (
            <div
              key={career._id || career.id}
              onClick={() => navigate(`/career/${career._id || career.id}`)}
              className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all cursor-pointer group"
            >
              <div className="flex items-start gap-4 mb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-xl flex items-center justify-center text-3xl group-hover:scale-110 transition-transform">
                  {career.icon || '💼'}
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">
                    {career.name}
                  </h3>
                  <p className="text-gray-600">{career.field}</p>
                </div>
              </div>

              <p className="text-gray-700 mb-4 line-clamp-2">{career.description}</p>

              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-1 text-green-600">
                  <DollarSign className="w-4 h-4" />
                  ${(career.salary?.avg || 80000).toLocaleString()}
                </div>
                <div className="flex items-center gap-1 text-blue-600">
                  <TrendingUp className="w-4 h-4" />
                  {career.market_trends?.growth_rate || '+15%'}
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredCareers.length === 0 && (
          <div className="text-center py-12">
            <Briefcase className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 text-lg">No careers found matching your search.</p>
          </div>
        )}
      </div>
    </div>
  );
}
