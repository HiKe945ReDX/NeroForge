#!/usr/bin/env python3
import asyncio
import json
import os
import subprocess
from motor.motor_asyncio import AsyncIOMotorClient

def get_gcp_secret_via_gcloud(secret_name: str) -> str:
    """Fetch secret from GCP Secret Manager using gcloud CLI"""
    try:
        result = subprocess.run(
            ["gcloud", "secrets", "versions", "access", "latest", f"--secret={secret_name}"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to fetch secret '{secret_name}': {e.stderr}")
        raise

async def import_careers():
    try:
        print("🔐 Fetching MongoDB URI from GCP Secret Manager via gcloud...")
        mongodb_uri = get_gcp_secret_via_gcloud("guidora-mongodb-uri")
        print("✅ Retrieved MongoDB URI securely!")
        
        print("📍 Connecting to MongoDB...")
        client = AsyncIOMotorClient(mongodb_uri, maxPoolSize=100)
        await client.admin.command('ping')
        print("✅ Connected!")
        
        db = client.guidora_db
        collection = db.careers
        
        with open("careers_database_expanded.json") as f:
            careers = json.load(f)
        
        print(f"📋 Importing {len(careers)} careers...")
        
        # Upsert to avoid duplicates
        operations = [
            {
                "updateOne": {
                    "filter": {"id": career["id"]},
                    "update": {"$set": career},
                    "upsert": True
                }
            }
            for career in careers
        ]
        
        result = await collection.bulk_write(operations)
        print(f"✅ Upserted {result.upserted_count} new careers!")
        print(f"✅ Modified {result.modified_count} existing careers!")
        
        count = await collection.count_documents({})
        print(f"📊 Total careers: {count}")
        
        client.close()
        print("🎉 Done!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(import_careers())
