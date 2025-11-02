import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Brain, 
  Award, 
  Map,
  Activity,
  Users,
  Target,
  Zap
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalPoints: 1250,
    level: 'Intermediate',
    achievements: 5,
    weeklyProgress: 75
  });

  const chartData = [
    { name: 'Mon', progress: 20 },
    { name: 'Tue', progress: 35 },
    { name: 'Wed', progress: 28 },
    { name: 'Thu', progress: 45 },
    { name: 'Fri', progress: 60 },
    { name: 'Sat', progress: 75 },
    { name: 'Sun', progress: 80 },
  ];

  const skillData = [
    { name: 'Python', value: 85, color: '#3B82F6' },
    { name: 'AI/ML', value: 70, color: '#8B5CF6' },
    { name: 'FastAPI', value: 60, color: '#10B981' },
    { name: 'React', value: 75, color: '#F59E0B' },
  ];

  const StatCard = ({ title, value, icon: Icon, color, change }) => (
    <div className="card hover:shadow-md transition-shadow bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
          {change && (
            <p className="text-sm text-green-600 mt-1">
              +{change}% from last week
            </p>
          )}
        </div>
        <div className="p-3 rounded-full bg-blue-100">
          <Icon className="w-8 h-8 text-blue-600" />
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Welcome back to Guidora! 🚀</h1>
            <p className="text-blue-100 text-lg">
              Your AI-powered career journey continues. You're on level <strong>{stats.level}</strong> with <strong>{stats.totalPoints}</strong> points!
            </p>
          </div>
          <div className="hidden md:block">
            <div className="bg-white bg-opacity-20 rounded-xl p-4">
              <Zap className="w-12 h-12 text-yellow-300" />
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Points"
          value={stats.totalPoints.toLocaleString()}
          icon={TrendingUp}
          color="blue"
          change={12}
        />
        <StatCard
          title="AI Sessions"
          value="23"
          icon={Brain}
          color="purple"
          change={8}
        />
        <StatCard
          title="Achievements"
          value={stats.achievements}
          icon={Award}
          color="green"
          change={20}
        />
        <StatCard
          title="Career Paths"
          value="4"
          icon={Map}
          color="yellow"
          change={5}
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Progress Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Progress</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Area 
                type="monotone" 
                dataKey="progress" 
                stroke="#3B82F6" 
                fill="#3B82F6" 
                fillOpacity={0.1}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Skills Distribution */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Skills Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={skillData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}%`}
              >
                {skillData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Activity & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-blue-600" />
            Recent Activity
          </h3>
          <div className="space-y-4">
            {[
              { action: 'Completed AI Persona Creation', time: '2 hours ago', type: 'success' },
              { action: 'Resume Analysis - 85% ATS Score', time: '1 day ago', type: 'info' },
              { action: 'Earned "Quick Learner" Achievement', time: '2 days ago', type: 'success' },
              { action: 'Started Career Roadmap for AI Engineer', time: '3 days ago', type: 'info' },
            ].map((activity, index) => (
              <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <div className={`w-2 h-2 rounded-full ${activity.type === 'success' ? 'bg-green-500' : 'bg-blue-500'}`}></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                  <p className="text-xs text-gray-500">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Target className="w-5 h-5 mr-2 text-purple-600" />
            Quick Actions
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <button className="p-4 bg-blue-50 hover:bg-blue-100 rounded-lg text-center transition-colors">
              <Brain className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <span className="text-sm font-medium text-blue-900">AI Analysis</span>
            </button>
            <button className="p-4 bg-purple-50 hover:bg-purple-100 rounded-lg text-center transition-colors">
              <Map className="w-8 h-8 text-purple-600 mx-auto mb-2" />
              <span className="text-sm font-medium text-purple-900">Career Map</span>
            </button>
            <button className="p-4 bg-green-50 hover:bg-green-100 rounded-lg text-center transition-colors">
              <Users className="w-8 h-8 text-green-600 mx-auto mb-2" />
              <span className="text-sm font-medium text-green-900">Mock Interview</span>
            </button>
            <button className="p-4 bg-yellow-50 hover:bg-yellow-100 rounded-lg text-center transition-colors">
              <Award className="w-8 h-8 text-yellow-600 mx-auto mb-2" />
              <span className="text-sm font-medium text-yellow-900">Achievements</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
