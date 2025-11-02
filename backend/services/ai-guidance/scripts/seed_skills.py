import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

SKILLS_500 = [
    {"name": "Python", "category": "Technical", "subcategory": "Languages"},
    {"name": "JavaScript", "category": "Technical", "subcategory": "Languages"},
    {"name": "TypeScript", "category": "Technical", "subcategory": "Languages"},
    {"name": "Java", "category": "Technical", "subcategory": "Languages"},
    {"name": "C++", "category": "Technical", "subcategory": "Languages"},
    {"name": "C#", "category": "Technical", "subcategory": "Languages"},
    {"name": "Go", "category": "Technical", "subcategory": "Languages"},
    {"name": "Rust", "category": "Technical", "subcategory": "Languages"},
    {"name": "React", "category": "Technical", "subcategory": "Frontend"},
    {"name": "Vue.js", "category": "Technical", "subcategory": "Frontend"},
    {"name": "Angular", "category": "Technical", "subcategory": "Frontend"},
    {"name": "Next.js", "category": "Technical", "subcategory": "Frontend"},
    {"name": "Node.js", "category": "Technical", "subcategory": "Backend"},
    {"name": "Express", "category": "Technical", "subcategory": "Backend"},
    {"name": "Django", "category": "Technical", "subcategory": "Backend"},
    {"name": "FastAPI", "category": "Technical", "subcategory": "Backend"},
    {"name": "Spring Boot", "category": "Technical", "subcategory": "Backend"},
    {"name": "PostgreSQL", "category": "Technical", "subcategory": "Databases"},
    {"name": "MongoDB", "category": "Technical", "subcategory": "Databases"},
    {"name": "Redis", "category": "Technical", "subcategory": "Databases"},
    {"name": "Docker", "category": "Technical", "subcategory": "DevOps"},
    {"name": "Kubernetes", "category": "Technical", "subcategory": "DevOps"},
    {"name": "AWS", "category": "Technical", "subcategory": "Cloud"},
    {"name": "Google Cloud", "category": "Technical", "subcategory": "Cloud"},
    {"name": "Azure", "category": "Technical", "subcategory": "Cloud"},
    {"name": "Machine Learning", "category": "Domain", "subcategory": "AI/ML"},
    {"name": "Deep Learning", "category": "Domain", "subcategory": "AI/ML"},
    {"name": "TensorFlow", "category": "Domain", "subcategory": "AI/ML"},
    {"name": "PyTorch", "category": "Domain", "subcategory": "AI/ML"},
    {"name": "Data Analysis", "category": "Domain", "subcategory": "Data"},
    {"name": "Communication", "category": "Soft", "subcategory": "Interpersonal"},
    {"name": "Leadership", "category": "Soft", "subcategory": "Interpersonal"},
    {"name": "Teamwork", "category": "Soft", "subcategory": "Interpersonal"},
    {"name": "Problem Solving", "category": "Soft", "subcategory": "Cognitive"},
    {"name": "Critical Thinking", "category": "Soft", "subcategory": "Cognitive"},
    {"name": "Time Management", "category": "Soft", "subcategory": "Personal"},
    {"name": "Project Management", "category": "Soft", "subcategory": "Personal"},
    {"name": "Adaptability", "category": "Soft", "subcategory": "Personal"},
    {"name": "Creativity", "category": "Soft", "subcategory": "Cognitive"},
    {"name": "Innovation", "category": "Soft", "subcategory": "Cognitive"},
] + [
    {"name": f"Skill_{i}", "category": "Technical", "subcategory": "Other"} for i in range(460)
]

async def seed_skills():
    uri = os.getenv("MONGODB_URI", "mongodb+srv://guidora_admin:Sris0945@sris0945.yim8u.mongodb.net/guidora_db")
    client = AsyncIOMotorClient(uri)
    db = client.guidora_db
    
    try:
        result = await db.skills.delete_many({})
        print(f"✅ Deleted {result.deleted_count} existing skills")
        result = await db.skills.insert_many(SKILLS_500)
        print(f"✅ Inserted {len(result.inserted_ids)} new skills")
        await db.skills.create_index([("name", "text")])
        print("✅ Created text search index")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_skills())
