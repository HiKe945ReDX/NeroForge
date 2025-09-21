import React, { useState, useEffect } from 'react';
import { 
  Trophy, 
  Award, 
  Crown, 
  Star, 
  Target, 
  TrendingUp,
  Users,
  Medal,
  Zap,
  Flame,
  Gift,
  Calendar
} from 'lucide-react';

const Gamification = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [userStats] = useState({
    totalPoints: 2850,
    level: 'Expert',
    rank: 5,
    streak: 12,
    achievements: 15,
    weeklyTarget: 500,
    weeklyProgress: 380
  });

  // Demo leaderboard without avatars
  const [leaderboard] = useState([
    {
      id: 1,
      name: 'Alex Chen',
      points: 3420,
      level: 'Master',
      badges: ['AI Expert', 'Code Ninja', 'Quick Learner'],
      streak: 25,
      location: 'San Francisco, CA'
    },
    {
      id: 2,
      name: 'Sarah Johnson',
      points: 3180,
      level: 'Master',
      badges: ['Data Scientist', 'ML Engineer', 'Problem Solver'],
      streak: 18,
      location: 'New York, NY'
    },
    {
      id: 3,
      name: 'Michael Rodriguez',
      points: 2950,
      level: 'Expert',
      badges: ['Full Stack', 'DevOps', 'Team Player'],
      streak: 14,
      location: 'Austin, TX'
    },
    {
      id: 4,
      name: 'Emily Zhang',
      points: 2890,
      level: 'Expert',
      badges: ['React Expert', 'UI/UX', 'Creative'],
      streak: 21,
      location: 'Seattle, WA'
    },
    {
      id: 5,
      name: 'Sridhar Shanmugam',
      points: 2850,
      level: 'Expert',
      badges: ['AI Innovator', 'Python Master', 'Rising Star'],
      streak: 12,
      location: 'Chennai, India',
      isCurrentUser: true
    },
    {
      id: 6,
      name: 'David Kim',
      points: 2720,
      level: 'Expert',
      badges: ['Backend Pro', 'Database Expert'],
      streak: 8,
      location: 'Toronto, CA'
    }
  ]);

  const [achievements] = useState([
    {
      id: 1,
      title: 'First Steps',
      description: 'Complete your first AI analysis',
      icon: 'star',
      points: 100,
      unlocked: true,
      unlockedAt: '2024-09-15',
      rarity: 'common'
    },
    {
      id: 2,
      title: 'AI Innovator',
      description: 'Build 5+ AI projects',
      icon: 'brain',
      points: 500,
      unlocked: true,
      unlockedAt: '2024-09-18',
      rarity: 'rare'
    },
    {
      id: 3,
      title: 'Code Master',
      description: 'Achieve 1000+ GitHub commits',
      icon: 'code',
      points: 300,
      unlocked: true,
      unlockedAt: '2024-09-20',
      rarity: 'uncommon'
    },
    {
      id: 4,
      title: 'Quick Learner',
      description: 'Complete 10 certifications',
      icon: 'book',
      points: 250,
      unlocked: true,
      unlockedAt: '2024-09-19',
      rarity: 'uncommon'
    }
  ]);

  const getRarityColor = (rarity) => {
    switch (rarity) {
      case 'common': return 'bg-gray-100 text-gray-800 border-gray-300';
      case 'uncommon': return 'bg-green-100 text-green-800 border-green-300';
      case 'rare': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'epic': return 'bg-purple-100 text-purple-800 border-purple-300';
      case 'legendary': return 'bg-gradient-to-r from-yellow-100 to-orange-100 text-orange-800 border-orange-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getLevelColor = (level) => {
    switch (level) {
      case 'Beginner': return 'bg-gray-100 text-gray-800';
      case 'Intermediate': return 'bg-green-100 text-green-800';
      case 'Advanced': return 'bg-blue-100 text-blue-800';
      case 'Expert': return 'bg-purple-100 text-purple-800';
      case 'Master': return 'bg-gradient-to-r from-yellow-100 to-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const StatCard = ({ icon: Icon, value, label, color = 'blue', suffix = '' }) => (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-3xl font-bold text-gray-900">{value}{suffix}</p>
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
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 rounded-2xl p-8 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-black bg-opacity-10"></div>
        <div className="relative z-10">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2 flex items-center">
                <Trophy className="w-10 h-10 mr-3 text-yellow-300" />
                Gamification Hub
              </h1>
              <p className="text-purple-100 text-lg">Level up your career with achievements and rewards!</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-purple-200">Current Level</p>
              <p className="text-3xl font-bold text-yellow-300">{userStats.level}</p>
              <p className="text-sm text-purple-200">Rank #{userStats.rank} globally</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 justify-center">
        {[
          { id: 'overview', label: 'Overview', icon: Target },
          { id: 'leaderboard', label: 'Leaderboard', icon: Crown },
          { id: 'achievements', label: 'Achievements', icon: Award },
          { id: 'rewards', label: 'Rewards', icon: Gift }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-purple-100 text-purple-700 border border-purple-200'
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
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="p-8">
            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
              <StatCard icon={Zap} value={userStats.totalPoints} label="Total Points" color="yellow" />
              <StatCard icon={Flame} value={userStats.streak} label="Day Streak" color="orange" />
              <StatCard icon={Trophy} value={userStats.achievements} label="Achievements" color="purple" />
              <StatCard icon={TrendingUp} value={userStats.rank} label="Global Rank" color="blue" suffix="" />
            </div>

            {/* Progress Sections */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Weekly Progress */}
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
                <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                  <Calendar className="w-5 h-5 mr-2 text-blue-600" />
                  Weekly Challenge
                </h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Progress</span>
                    <span className="font-bold text-blue-600">{userStats.weeklyProgress}/{userStats.weeklyTarget} points</span>
                  </div>
                  <div className="w-full bg-blue-200 rounded-full h-3">
                    <div 
                      className="bg-blue-600 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${(userStats.weeklyProgress / userStats.weeklyTarget) * 100}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-blue-600">
                    {userStats.weeklyTarget - userStats.weeklyProgress} points to go for bonus reward!
                  </p>
                </div>
              </div>

              {/* Level Progress */}
              <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-200">
                <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                  <Star className="w-5 h-5 mr-2 text-purple-600" />
                  Level Progress
                </h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Current Level</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-bold ${getLevelColor(userStats.level)}`}>
                      {userStats.level}
                    </span>
                  </div>
                  <div className="w-full bg-purple-200 rounded-full h-3">
                    <div className="bg-purple-600 h-3 rounded-full w-[75%]"></div>
                  </div>
                  <p className="text-sm text-purple-600">750 points to Master level!</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Leaderboard Tab */}
        {activeTab === 'leaderboard' && (
          <div className="p-8">
            <div className="text-center mb-8">
              <Crown className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
              <h2 className="text-3xl font-bold text-gray-900 mb-2">Global Leaderboard</h2>
              <p className="text-gray-600">Compete with career builders worldwide</p>
            </div>

            <div className="space-y-4">
              {leaderboard.map((user, index) => (
                <div
                  key={user.id}
                  className={`p-6 rounded-xl border-2 transition-all hover:shadow-lg ${
                    user.isCurrentUser
                      ? 'bg-gradient-to-r from-blue-50 to-purple-50 border-blue-300 shadow-md'
                      : 'bg-white border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-6">
                      {/* Rank */}
                      <div className="flex-shrink-0">
                        {index < 3 ? (
                          <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-white ${
                            index === 0 ? 'bg-gradient-to-r from-yellow-400 to-yellow-600' :
                            index === 1 ? 'bg-gradient-to-r from-gray-400 to-gray-600' :
                            'bg-gradient-to-r from-yellow-600 to-yellow-800'
                          }`}>
                            {index === 0 ? '👑' : index + 1}
                          </div>
                        ) : (
                          <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center font-bold text-gray-600">
                            {index + 1}
                          </div>
                        )}
                      </div>

                      {/* User Info without avatar */}
                      <div>
                        <div className="flex items-center space-x-3">
                          <h3 className="text-xl font-bold text-gray-900">{user.name}</h3>
                          {user.isCurrentUser && (
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-bold rounded-full">YOU</span>
                          )}
                        </div>
                        <p className="text-gray-600 mb-2">{user.location}</p>
                        <div className="flex flex-wrap gap-2">
                          {user.badges.slice(0, 2).map((badge, idx) => (
                            <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                              {badge}
                            </span>
                          ))}
                          {user.badges.length > 2 && (
                            <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                              +{user.badges.length - 2} more
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Stats */}
                    <div className="text-right">
                      <p className="text-3xl font-bold text-gray-900">{user.points.toLocaleString()}</p>
                      <p className="text-sm text-gray-600">points</p>
                      <div className="flex items-center justify-end mt-2 space-x-2">
                        <Flame className="w-4 h-4 text-orange-500" />
                        <span className="text-sm font-medium text-orange-600">{user.streak} day streak</span>
                      </div>
                      <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold mt-2 ${getLevelColor(user.level)}`}>
                        {user.level}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Achievements Tab */}
        {activeTab === 'achievements' && (
          <div className="p-8">
            <div className="text-center mb-8">
              <Award className="w-16 h-16 text-purple-500 mx-auto mb-4" />
              <h2 className="text-3xl font-bold text-gray-900 mb-2">Achievement Gallery</h2>
              <p className="text-gray-600">Unlock badges by completing challenges and goals</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {achievements.map((achievement) => (
                <div
                  key={achievement.id}
                  className={`relative p-6 rounded-xl border-2 transition-all hover:shadow-lg ${
                    achievement.unlocked
                      ? `${getRarityColor(achievement.rarity)} shadow-md`
                      : 'bg-gray-50 border-gray-200 opacity-70'
                  }`}
                >
                  {/* Rarity Badge */}
                  <div className="absolute top-4 right-4">
                    <span className={`px-2 py-1 text-xs font-bold rounded-full capitalize ${getRarityColor(achievement.rarity)}`}>
                      {achievement.rarity}
                    </span>
                  </div>

                  {/* Achievement Icon */}
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 ${
                    achievement.unlocked ? 'bg-white' : 'bg-gray-200'
                  }`}>
                    {achievement.unlocked ? (
                      <Trophy className="w-8 h-8 text-yellow-500" />
                    ) : (
                      <div className="w-8 h-8 bg-gray-400 rounded-full"></div>
                    )}
                  </div>

                  {/* Achievement Info */}
                  <h3 className="text-lg font-bold text-gray-900 mb-2">{achievement.title}</h3>
                  <p className="text-gray-600 text-sm mb-4">{achievement.description}</p>

                  {/* Progress or Unlock Date */}
                  {achievement.unlocked ? (
                    <div className="text-sm text-gray-500">
                      <p>Unlocked on {new Date(achievement.unlockedAt).toLocaleDateString()}</p>
                      <p className="font-bold text-green-600">+{achievement.points} points earned</p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-blue-600">+{achievement.points} points when unlocked</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Rewards Tab */}
        {activeTab === 'rewards' && (
          <div className="p-8">
            <div className="text-center mb-8">
              <Gift className="w-16 h-16 text-pink-500 mx-auto mb-4" />
              <h2 className="text-3xl font-bold text-gray-900 mb-2">Reward Store</h2>
              <p className="text-gray-600">Redeem your points for exclusive rewards</p>
              <p className="text-lg font-bold text-blue-600 mt-2">Available Points: {userStats.totalPoints.toLocaleString()}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                {
                  id: 1,
                  title: 'Premium Profile Badge',
                  description: 'Stand out with a premium badge on your profile',
                  cost: 500,
                  image: '🏆',
                  category: 'Profile'
                },
                {
                  id: 2,
                  title: '1-on-1 Career Coaching',
                  description: '30-minute session with an industry expert',
                  cost: 2000,
                  image: '👨‍🏫',
                  category: 'Coaching'
                },
                {
                  id: 3,
                  title: 'Custom Portfolio Template',
                  description: 'Exclusive premium portfolio designs',
                  cost: 750,
                  image: '🎨',
                  category: 'Design'
                }
              ].map((reward) => (
                <div key={reward.id} className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
                  <div className="text-center mb-4">
                    <div className="text-4xl mb-2">{reward.image}</div>
                    <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-bold rounded-full">
                      {reward.category}
                    </span>
                  </div>
                  
                  <h3 className="font-bold text-gray-900 mb-2">{reward.title}</h3>
                  <p className="text-gray-600 text-sm mb-4">{reward.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-bold text-purple-600">{reward.cost} points</span>
                    <button
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        userStats.totalPoints >= reward.cost
                          ? 'bg-purple-600 hover:bg-purple-700 text-white'
                          : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                      }`}
                      disabled={userStats.totalPoints < reward.cost}
                    >
                      Redeem
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Gamification;
