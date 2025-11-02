import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def cleanup():
    client = AsyncIOMotorClient("mongodb+srv://guidora_admin:Sris0945@sris0945.yim8u.mongodb.net/guidora_db?retryWrites=true&w=majority&appName=Sris0945")
    db = client.guidora_db
    
    # Delete all documents with null user_id
    result = await db.personas.delete_many({"user_id": None})
    print(f"✅ Deleted {result.deleted_count} null user_id documents")
    
    # Also check for empty string user_ids
    result2 = await db.personas.delete_many({"user_id": ""})
    print(f"✅ Deleted {result2.deleted_count} empty user_id documents")
    
    client.close()

asyncio.run(cleanup())
