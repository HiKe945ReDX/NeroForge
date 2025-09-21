import React, { useState, useEffect } from 'react';
import { AwardIcon, TrophyIcon, StarIcon, TrendingUpIcon } from 'lucide-react';
import { gamificationService } from '../services/api';
import toast from 'react-hot-toast';

const Gamification = () => {
  const [userStats, setUserStats] = useState({});
  const [achievements, setAchievements] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadGamificationData();
  }, []);

  const loadGamificationData = async () => {
    setLoading(true);
    try {
      const userId = 'demo_user';
      
      // Load user points
      const pointsResponse = await gamificationService.getUserPoints(userId);
      setUserStats(pointsResponse.data);

      // Load achievements
      const achievementsResponse = await gamificationService.getAchievements();
      setAchievements(achievementsResponse.data.achievements || []);

      // Load leaderboard
      const leaderboardResponse = await gamificationService.getLeaderboard('global');
      setLeaderboard(leaderboardResponse.data.top_users || []);

      toast.success('Gamification data loaded!');
    } catch (error) {
      toast.error('Failed to load gamification data');
    } finally {
      setLoading(false);
    }
  };

  const awardPoints = async (action, points) => {
    try {
      await gamificationService.awardPoints({
        user_id: 'demo_user',
        action: action,
        points: points
      });
      toast.success(`+${points} points earned!`);
      loadGamificationData(); // Refresh data
    } catch (error) {
      toast.error('Failed to award points');
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Gamification Hub</h1>
        <p className="text-lg text-gray-600">Track your progress and earn rewards</p>
      </div>

      {/* User Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100">Total Points</p>
              <p className="text-3xl font-bold">{userStats.total_points?.toLocaleString() || '1,250'}</p>
            </div>
            <TrendingUpIcon className="w-10 h-10 text-blue-200" />
          </div>
        </div>

        <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100">Current Level</p>
              <p className="text-3xl font-bold">{userStats.current_level || 'Intermediate'}</p>
            </div>
            <StarIcon className="w-10 h-10 text-purple-200" />
          </div>
        </div>

        <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100">Weekly Points</p>
              <p className="text-3xl font-bold">{userStats.weekly_points || '275'}</p>
            </div>
            <TrophyIcon className="w-10 h-10 text-green-200" />
          </div>
        </div>

        <div className="bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-100">Global Rank</p>
              <p className="text-3xl font-bold">#15</p>
            </div>
            <AwardIcon className="w-10 h-10 text-yellow-200" />
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-lg font-semibold text-gray-900">Level Progress</h3>
          <span className="text-sm text-gray-600">
            {userStats.points_to_next_level || 350} points to next level
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div 
            className="bg-gradient-to-r from-blue-500 to-purple-500 h-4 rounded-full transition-all duration-300"
            style={{ width: `${userStats.level_progress || 75}%` }}
          ></div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Earn Points</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button
            onClick={() => awardPoints('daily_login', 10)}
            className="p-4 bg-blue-50 hover:bg-blue-100 rounded-lg text-center transition-colors"
          >
            <div className="text-2xl mb-2">📅</div>
            <div className="text-sm font-medium text-blue-900">Daily Login</div>
            <div className="text-xs text-blue-600">+10 points</div>
          </button>
          
          <button
            onClick={() => awardPoints('skill_assessment', 50)}
            className="p-4 bg-green-50 hover:bg-green-100 rounded-lg text-center transition-colors"
          >
            <div className="text-2xl mb-2">📊</div>
            <div className="text-sm font-medium text-green-900">Skill Test</div>
            <div className="text-xs text-green-600">+50 points</div>
          </button>

          <button
            onClick={() => awardPoints('resume_upload', 25)}
            className="p-4 bg-purple-50 hover:bg-purple-100 rounded-lg text-center transition-colors"
          >
            <div className="text-2xl mb-2">📄</div>
            <div className="text-sm font-medium text-purple-900">Resume Upload</div>
            <div className="text-xs text-purple-600">+25 points</div>
          </button>

          <button
            onClick={() => awardPoints('interview_practice', 75)}
            className="p-4 bg-yellow-50 hover:bg-yellow-100 rounded-lg text-center transition-colors"
          >
            <div className="text-2xl mb-2">🎤</div>
            <div className="text-sm font-medium text-yellow-900">Interview Prep</div>
            <div className="text-xs text-yellow-600">+75 points</div>
          </button>
        </div>
      </div>

      {/* Achievements & Leaderboard */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Achievements */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Achievements</h3>
          <div className="space-y-3">
            {achievements.slice(0, 5).map((achievement, index) => (
              <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <div className="text-2xl">{achievement.icon}</div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{achievement.name}</h4>
                  <p className="text-sm text-gray-600">{achievement.description}</p>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-blue-600">+{achievement.points}</div>
                  <div className="text-xs text-gray-500">{achievement.rarity}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Leaderboard */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Global Leaderboard</h3>
          <div className="space-y-3">
            {leaderboard.slice(0, 5).map((user, index) => (
              <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  index === 0 ? 'bg-yellow-100 text-yellow-800' :
                  index === 1 ? 'bg-gray-100 text-gray-800' :
                  index === 2 ? 'bg-orange-100 text-orange-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {user.rank}
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{user.username}</h4>
                  <p className="text-sm text-gray-600">{user.level}</p>
                </div>
                <div className="text-right">
                  <div className="font-medium text-gray-900">{user.points?.toLocaleString()}</div>
                  <div className="text-xs text-gray-500">points</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Gamification;
