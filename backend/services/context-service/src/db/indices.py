async def ensure_indices(db):
    """Ensure database indices exist"""
    try:
        # Create index but allow null userId (not unique)
        await db.resumes.create_index("userId", unique=False, sparse=True)
        await db.contexts.create_index("userId", unique=False, sparse=True)
        await db.contexts.create_index("createdAt", expireAfterSeconds=2592000)  # 30 days TTL
        print("✓ Database indices ensured")
    except Exception as e:
        print(f"⚠️ Index creation warning: {e}")
        # Don't fail startup on index errors
