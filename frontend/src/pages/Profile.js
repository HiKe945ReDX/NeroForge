import React, { useState } from 'react';
import { 
  User, 
  Edit, 
  Mail, 
  Phone, 
  MapPin, 
  Calendar,
  Github,
  Linkedin,
  Globe,
  Award,
  Briefcase,
  GraduationCap,
  Star,
  Trophy,
  Target,
  TrendingUp,
  Save,
  X
} from 'lucide-react';

const Profile = () => {
  const [profile] = useState({
    user_id: 'demo_user',
    full_name: 'Sridhar Shanmugam',
    email: 'sridhar@guidora.com',
    phone: '+91 9876543210',
    location: 'Chennai, Tamil Nadu, India',
    bio: 'Passionate AI & Data Science engineer with expertise in machine learning, deep learning, and full-stack development. Currently pursuing B.Tech in AI & Data Science.',
    github_url: 'https://github.com/HiKe945ReDX',
    linkedin_url: 'https://linkedin.com/in/sridhar-ai',
    portfolio_url: 'https://sridhar-portfolio.dev',
    skills: ['Python', 'TensorFlow', 'React', 'FastAPI', 'Docker', 'MongoDB', 'PostgreSQL', 'AWS'],
    experience: [
      {
        title: 'AI Engineering Intern',
        company: 'TechCorp Solutions',
        duration: 'Jun 2024 - Present',
        description: 'Developing ML models for predictive analytics and automation systems.'
      },
      {
        title: 'Full Stack Developer',
        company: 'StartupXYZ',
        duration: 'Jan 2024 - May 2024',
        description: 'Built scalable web applications using React and Python FastAPI.'
      }
    ],
    education: [
      {
        degree: 'B.Tech in AI & Data Science',
        institution: 'Anna University',
        year: '2022-2026',
        grade: 'CGPA: 8.7/10'
      }
    ],
    achievements: [
      { title: 'AI Innovator', description: 'Built 5+ ML projects', date: '2024', icon: 'brain' },
      { title: 'Code Master', description: '1000+ commits on GitHub', date: '2024', icon: 'code' },
      { title: 'Quick Learner', description: 'Completed 10 certifications', date: '2024', icon: 'book' }
    ],
    stats: {
      totalProjects: 12,
      githubStars: 156,
      certifications: 8,
      yearsExperience: 2.5
    }
  });
  
  const [editing, setEditing] = useState(false);

  const StatCard = ({ icon: Icon, value, label, color = 'blue' }) => (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          <p className="text-sm text-gray-600 mt-1">{label}</p>
        </div>
        <div className={`p-3 rounded-full bg-${color}-100`}>
          <Icon className={`w-6 h-6 text-${color}-600`} />
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header Section without avatar */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 rounded-2xl p-8 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-black bg-opacity-20"></div>
        <div className="relative z-10">
          <div className="flex flex-col md:flex-row items-start md:items-center space-y-6 md:space-y-0 md:space-x-8">
            {/* User Icon instead of avatar */}
            <div className="relative">
              <div className="w-32 h-32 rounded-full border-4 border-white shadow-lg bg-white bg-opacity-20 flex items-center justify-center">
                <User className="w-16 h-16 text-white" />
              </div>
            </div>

            {/* Profile Info */}
            <div className="flex-1">
              <div className="flex items-start justify-between">
                <div>
                  <h1 className="text-3xl font-bold mb-2">{profile.full_name}</h1>
                  <p className="text-blue-100 text-lg mb-4">{profile.bio}</p>
                  
                  <div className="flex flex-wrap gap-4 text-sm text-blue-100">
                    <div className="flex items-center space-x-2">
                      <Mail className="w-4 h-4" />
                      <span>{profile.email}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <MapPin className="w-4 h-4" />
                      <span>{profile.location}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Phone className="w-4 h-4" />
                      <span>{profile.phone}</span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => setEditing(true)}
                  className="bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
                >
                  <Edit className="w-4 h-4" />
                  <span>Edit Profile</span>
                </button>
              </div>

              {/* Social Links */}
              <div className="flex space-x-4 mt-6">
                <a href={profile.github_url} target="_blank" rel="noopener noreferrer" 
                   className="bg-white bg-opacity-20 hover:bg-opacity-30 p-2 rounded-lg transition-colors">
                  <Github className="w-5 h-5" />
                </a>
                <a href={profile.linkedin_url} target="_blank" rel="noopener noreferrer"
                   className="bg-white bg-opacity-20 hover:bg-opacity-30 p-2 rounded-lg transition-colors">
                  <Linkedin className="w-5 h-5" />
                </a>
                <a href={profile.portfolio_url} target="_blank" rel="noopener noreferrer"
                   className="bg-white bg-opacity-20 hover:bg-opacity-30 p-2 rounded-lg transition-colors">
                  <Globe className="w-5 h-5" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <StatCard icon={Briefcase} value={profile.stats.totalProjects} label="Projects" color="blue" />
        <StatCard icon={Star} value={profile.stats.githubStars} label="GitHub Stars" color="yellow" />
        <StatCard icon={Award} value={profile.stats.certifications} label="Certifications" color="green" />
        <StatCard icon={TrendingUp} value={`${profile.stats.yearsExperience}Y`} label="Experience" color="purple" />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Skills */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <Target className="w-5 h-5 mr-2 text-blue-600" />
              Skills & Technologies
            </h3>
            <div className="flex flex-wrap gap-3">
              {profile.skills.map((skill, index) => (
                <span
                  key={index}
                  className="px-4 py-2 bg-gradient-to-r from-blue-100 to-purple-100 text-blue-800 rounded-full text-sm font-medium hover:from-blue-200 hover:to-purple-200 transition-colors"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {/* Experience */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
              <Briefcase className="w-5 h-5 mr-2 text-green-600" />
              Work Experience
            </h3>
            <div className="space-y-6">
              {profile.experience.map((exp, index) => (
                <div key={index} className="relative pl-8 pb-6 border-l-2 border-gray-200 last:pb-0">
                  <div className="absolute -left-2 top-0 w-4 h-4 bg-green-600 rounded-full"></div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900">{exp.title}</h4>
                    <p className="text-blue-600 font-medium">{exp.company}</p>
                    <p className="text-sm text-gray-500 mb-3">{exp.duration}</p>
                    <p className="text-gray-700">{exp.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Education */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
              <GraduationCap className="w-5 h-5 mr-2 text-purple-600" />
              Education
            </h3>
            {profile.education.map((edu, index) => (
              <div key={index} className="bg-purple-50 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900">{edu.degree}</h4>
                <p className="text-purple-600 font-medium">{edu.institution}</p>
                <div className="flex justify-between items-center mt-2">
                  <span className="text-sm text-gray-500">{edu.year}</span>
                  <span className="text-sm font-medium text-green-600">{edu.grade}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Achievements */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <Trophy className="w-5 h-5 mr-2 text-yellow-600" />
              Recent Achievements
            </h3>
            <div className="space-y-4">
              {profile.achievements.map((achievement, index) => (
                <div key={index} className="flex items-center space-x-4 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-200">
                  <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
                    <Award className="w-6 h-6 text-yellow-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">{achievement.title}</h4>
                    <p className="text-sm text-gray-600">{achievement.description}</p>
                    <p className="text-xs text-yellow-600 font-medium">{achievement.date}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Stats */}
          <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl p-6 text-white">
            <h3 className="text-lg font-semibold mb-4">Career Progress</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span>Profile Completion</span>
                <span className="font-bold">95%</span>
              </div>
              <div className="w-full bg-white bg-opacity-20 rounded-full h-2">
                <div className="bg-white rounded-full h-2 w-[95%]"></div>
              </div>
              
              <div className="flex justify-between items-center">
                <span>Skill Level</span>
                <span className="font-bold">Advanced</span>
              </div>
              <div className="w-full bg-white bg-opacity-20 rounded-full h-2">
                <div className="bg-white rounded-full h-2 w-[85%]"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
