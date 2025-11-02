import React, { useState, useEffect } from 'react';
import { Bookmark, Share2, TrendingUp, Users, Briefcase } from 'lucide-react';

export default function NewsFeed() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('https://guidora-backend-746485305795.us-central1.run.app/api/news?career=Software%20Engineer')
      .then(r => r.json())
      .then(setArticles)
      .catch(() => {
        setArticles([
          { title: 'Software Engineer Salary Up 12% in Q4', source: 'LinkedIn Pulse', summary: 'Market trends show demand surge', date: 'Today', icon: '💰' },
          { title: '15,000 Job Openings Posted', source: 'Indeed', summary: 'Engineering roles in high demand', date: 'Yesterday', icon: '📈' },
          { title: 'Kubernetes Now Required for DevOps', source: 'Stack Overflow', summary: 'New skill trend in 2024', date: '2 days ago', icon: '🛠️' },
        ]);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <h1 className="text-4xl font-bold text-white mb-2">📰 Career News Feed</h1>
      <p className="text-slate-300 mb-8">Stay updated with market trends for your career path</p>

      <div className="max-w-3xl mx-auto space-y-4">
        {loading ? (
          <p className="text-slate-400">Loading articles...</p>
        ) : (
          articles.map((article, idx) => (
            <div key={idx} className="bg-slate-700 rounded-lg p-6 hover:bg-slate-650 transition">
              <div className="flex items-start gap-4">
                <span className="text-3xl">{article.icon}</span>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-2">{article.title}</h3>
                  <p className="text-slate-300 mb-3">{article.summary}</p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 text-sm text-slate-400">
                      <span className="bg-slate-600 px-3 py-1 rounded">{article.source}</span>
                      <span>{article.date}</span>
                    </div>
                    <div className="flex gap-2">
                      <button className="p-2 bg-slate-600 rounded hover:bg-slate-500">
                        <Bookmark size={18} className="text-slate-300" />
                      </button>
                      <button className="p-2 bg-slate-600 rounded hover:bg-slate-500">
                        <Share2 size={18} className="text-slate-300" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="max-w-3xl mx-auto mt-12 grid grid-cols-3 gap-4">
        <div className="bg-slate-700 rounded-lg p-4 text-center text-white">
          <TrendingUp className="mx-auto mb-2 text-emerald-400" size={24} />
          <p className="font-bold">Salary Trends</p>
          <p className="text-xl text-emerald-400">+8% YoY</p>
        </div>
        <div className="bg-slate-700 rounded-lg p-4 text-center text-white">
          <Briefcase className="mx-auto mb-2 text-blue-400" size={24} />
          <p className="font-bold">Open Roles</p>
          <p className="text-xl text-blue-400">15,234</p>
        </div>
        <div className="bg-slate-700 rounded-lg p-4 text-center text-white">
          <Users className="mx-auto mb-2 text-purple-400" size={24} />
          <p className="font-bold">Hiring Companies</p>
          <p className="text-xl text-purple-400">2,847</p>
        </div>
      </div>
    </div>
  );
}
