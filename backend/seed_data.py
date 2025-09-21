import asyncio
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
import bcrypt
import os

# MongoDB connection
MONGO_URL = "mongodb+srv://guidora:guidora123@guidora.fhpsf.mongodb.net/guidora?retryWrites=true&w=majority"
client = MongoClient(MONGO_URL)
db = client.guidora

async def seed_fake_users():
    """Create fake users for demo purposes"""
    
    fake_users = [
        {
            "_id": "user_001",
            "username": "alex_chen",
            "email": "alex@guidora.com",
            "password": bcrypt.hashpw("demo123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "full_name": "Alex Chen",
            "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
            "bio": "Senior AI Engineer with 5+ years in machine learning and deep learning. Love building scalable AI systems.",
            "location": "San Francisco, CA",
            "phone": "+1 555-0101",
            "skills": ["Python", "TensorFlow", "PyTorch", "AWS", "Docker", "Kubernetes"],
            "github_url": "https://github.com/alexchen",
            "linkedin_url": "https://linkedin.com/in/alexchen",
            "portfolio_url": "https://alexchen.dev",
            "created_at": datetime.utcnow() - timedelta(days=365),
            "profile_completion": 95,
            "level": "Master",
            "total_points": 3420,
            "achievements": ["AI Expert", "Code Ninja", "Quick Learner", "Team Player", "Problem Solver"]
        },
        {
            "_id": "user_002", 
            "username": "sarah_johnson",
            "email": "sarah@guidora.com",
            "password": bcrypt.hashpw("demo123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "full_name": "Sarah Johnson",
            "avatar": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face",
            "bio": "Data Scientist passionate about extracting insights from complex datasets. Expertise in ML and statistical analysis.",
            "location": "New York, NY",
            "phone": "+1 555-0102",
            "skills": ["Python", "R", "SQL", "Tableau", "Pandas", "Scikit-learn"],
            "github_url": "https://github.com/sarahjohnson",
            "linkedin_url": "https://linkedin.com/in/sarahjohnson",
            "portfolio_url": "https://sarahjohnson.dev",
            "created_at": datetime.utcnow() - timedelta(days=300),
            "profile_completion": 92,
            "level": "Master",
            "total_points": 3180,
            "achievements": ["Data Scientist", "ML Engineer", "Problem Solver", "Analytics Pro"]
        },
        {
            "_id": "user_003",
            "username": "michael_rodriguez", 
            "email": "michael@guidora.com",
            "password": bcrypt.hashpw("demo123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "full_name": "Michael Rodriguez",
            "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
            "bio": "Full-stack developer with DevOps expertise. Building scalable web applications and cloud infrastructure.",
            "location": "Austin, TX",
            "phone": "+1 555-0103",
            "skills": ["JavaScript", "React", "Node.js", "Docker", "AWS", "Jenkins"],
            "github_url": "https://github.com/michaelrodriguez",
            "linkedin_url": "https://linkedin.com/in/michaelrodriguez",
            "portfolio_url": "https://michaelrodriguez.dev",
            "created_at": datetime.utcnow() - timedelta(days=250),
            "profile_completion": 88,
            "level": "Expert",
            "total_points": 2950,
            "achievements": ["Full Stack", "DevOps", "Team Player", "Cloud Expert"]
        },
        {
            "_id": "user_004",
            "username": "emily_zhang",
            "email": "emily@guidora.com", 
            "password": bcrypt.hashpw("demo123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "full_name": "Emily Zhang",
            "avatar": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face",
            "bio": "Frontend developer and UI/UX designer. Creating beautiful and intuitive user experiences.",
            "location": "Seattle, WA", 
            "phone": "+1 555-0104",
            "skills": ["React", "Vue.js", "CSS", "Figma", "Adobe XD", "TypeScript"],
            "github_url": "https://github.com/emilyzhang",
            "linkedin_url": "https://linkedin.com/in/emilyzhang",
            "portfolio_url": "https://emilyzhang.design",
            "created_at": datetime.utcnow() - timedelta(days=200),
            "profile_completion": 90,
            "level": "Expert",
            "total_points": 2890,
            "achievements": ["React Expert", "UI/UX", "Creative", "Frontend Pro"]
        },
        {
            "_id": "user_005",
            "username": "sridhar_demo",
            "email": "sridhar@guidora.com",
            "password": bcrypt.hashpw("demo123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "full_name": "Sridhar Shanmugam", 
            "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
            "bio": "Passionate AI & Data Science engineer with expertise in machine learning, deep learning, and full-stack development. Currently pursuing B.Tech in AI & Data Science.",
            "location": "Chennai, India",
            "phone": "+91 9876543210",
            "skills": ["Python", "TensorFlow", "React", "FastAPI", "Docker", "MongoDB"],
            "github_url": "https://github.com/HiKe945ReDX",
            "linkedin_url": "https://linkedin.com/in/sridhar-ai",
            "portfolio_url": "https://sridhar-portfolio.dev",
            "created_at": datetime.utcnow() - timedelta(days=100),
            "profile_completion": 95,
            "level": "Expert", 
            "total_points": 2850,
            "achievements": ["AI Innovator", "Python Master", "Rising Star", "Quick Learner"]
        }
    ]
    
    # Clear existing demo users
    db.users.delete_many({"email": {"$regex": "@guidora.com"}})
    
    # Insert fake users
    for user in fake_users:
        try:
            db.users.insert_one(user)
            print(f"✅ Created user: {user['full_name']}")
        except Exception as e:
            print(f"❌ Error creating user {user['full_name']}: {e}")

async def seed_gamification_data():
    """Create gamification data for demo"""
    
    # Clear existing gamification data
    db.user_points.delete_many({})
    db.achievements.delete_many({})
    db.leaderboard.delete_many({})
    
    # Create user points
    user_points = [
        {"user_id": "user_001", "total_points": 3420, "level": "Master", "streak": 25, "weekly_points": 450},
        {"user_id": "user_002", "total_points": 3180, "level": "Master", "streak": 18, "weekly_points": 380},
        {"user_id": "user_003", "total_points": 2950, "level": "Expert", "streak": 14, "weekly_points": 290},
        {"user_id": "user_004", "total_points": 2890, "level": "Expert", "streak": 21, "weekly_points": 350},
        {"user_id": "user_005", "total_points": 2850, "level": "Expert", "streak": 12, "weekly_points": 380},
    ]
    
    for points in user_points:
        db.user_points.insert_one({
            **points,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
    
    # Create achievements
    achievements = [
        {
            "id": "first_steps",
            "title": "First Steps",
            "description": "Complete your first AI analysis", 
            "points": 100,
            "rarity": "common",
            "icon": "star"
        },
        {
            "id": "ai_innovator", 
            "title": "AI Innovator",
            "description": "Build 5+ AI projects",
            "points": 500,
            "rarity": "rare",
            "icon": "brain"
        },
        {
            "id": "code_master",
            "title": "Code Master", 
            "description": "Achieve 1000+ GitHub commits",
            "points": 300,
            "rarity": "uncommon",
            "icon": "code"
        },
        {
            "id": "quick_learner",
            "title": "Quick Learner",
            "description": "Complete 10 certifications",
            "points": 250,
            "rarity": "uncommon", 
            "icon": "book"
        },
        {
            "id": "team_player",
            "title": "Team Player",
            "description": "Collaborate on 5+ projects",
            "points": 200,
            "rarity": "common",
            "icon": "users"
        }
    ]
    
    for achievement in achievements:
        db.achievements.insert_one({
            **achievement,
            "created_at": datetime.utcnow()
        })
    
    print("✅ Created gamification data")

async def seed_activities():
    """Create user activities for demo"""
    
    db.user_activities.delete_many({})
    
    activities = []
    for user_id in ["user_001", "user_002", "user_003", "user_004", "user_005"]:
        for i in range(10):
            activity = {
                "user_id": user_id,
                "action": random.choice([
                    "completed_resume_analysis",
                    "generated_career_roadmap", 
                    "earned_achievement",
                    "completed_interview_prep",
                    "generated_portfolio",
                    "updated_profile"
                ]),
                "points_earned": random.randint(25, 100),
                "timestamp": datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                "metadata": {
                    "description": random.choice([
                        "AI Resume Analysis completed",
                        "Career roadmap generated",
                        "Achievement unlocked",
                        "Mock interview completed", 
                        "Portfolio generated",
                        "Profile updated"
                    ])
                }
            }
            activities.append(activity)
    
    db.user_activities.insert_many(activities)
    print("✅ Created user activities")

async def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    
    await seed_fake_users()
    await seed_gamification_data()
    await seed_activities()
    
    print("🎉 Database seeding completed!")
    print("\n📊 Summary:")
    print(f"Users: {db.users.count_documents({})}")
    print(f"User Points: {db.user_points.count_documents({})}")
    print(f"Achievements: {db.achievements.count_documents({})}")
    print(f"Activities: {db.user_activities.count_documents({})}")
    
    print("\n🔑 Demo Login Credentials:")
    print("Email: alex@guidora.com | Password: demo123")
    print("Email: sarah@guidora.com | Password: demo123")
    print("Email: sridhar@guidora.com | Password: demo123")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
