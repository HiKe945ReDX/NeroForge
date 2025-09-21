from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
import redis.asyncio as redis
from datetime import datetime, timedelta
from typing import Dict, Any
import uuid

from ..models.user import UserCreate, UserLogin, UserPublic, TokenResponse, OAuthUserData
from ..core.security import SecurityManager, get_current_active_user
from ..core.database import get_database, get_redis

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user document
    user_id = str(uuid.uuid4())
    hashed_password = SecurityManager.get_password_hash(user_data.password)
    
    user_doc = {
        "_id": user_id,
        "email": user_data.email,
        "hashed_password": hashed_password,
        "full_name": user_data.full_name,
        "role": "user",
        "status": "active",
        "is_verified": False,
        "profile": {},
        "preferences": {},
        "oauth_providers": {},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "login_count": 0
    }
    
    # Insert user
    result = await db.users.insert_one(user_doc)
    
    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Create access token
    token_data = {"user_id": user_id, "email": user_data.email}
    access_token = SecurityManager.create_access_token(token_data)
    
    # Create public user object
    user_public = UserPublic(
        id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        avatar_url=None,
        bio=None,
        location=None,
        role="user",
        status="active",
        is_verified=False,
        created_at=user_doc["created_at"],
        last_login=None,
        skills=[]
    )
    
    print(f"✅ User registered: {user_data.email} ({user_id})")
    
    return TokenResponse(
        access_token=access_token,
        expires_in=1440 * 60,  # 24 hours in seconds
        user_id=user_id,
        user=user_public
    )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    credentials: UserLogin,
    db: AsyncIOMotorDatabase = Depends(get_database),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Authenticate user and return access token"""
    
    # Find user
    user = await db.users.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not SecurityManager.verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if user.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is not active"
        )
    
    # Update login info
    await db.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"last_login": datetime.utcnow()},
            "$inc": {"login_count": 1}
        }
    )
    
    # Create access token
    token_data = {"user_id": user["_id"], "email": user["email"]}
    access_token = SecurityManager.create_access_token(token_data)
    
    # Cache user session in Redis
    await redis_client.setex(
        f"user_session:{user['_id']}",
        3600,  # 1 hour
        access_token
    )
    
    # Create public user object
    user_public = UserPublic(
        id=user["_id"],
        email=user["email"],
        full_name=user.get("full_name"),
        avatar_url=user.get("avatar_url"),
        bio=user.get("bio"),
        location=user.get("location"),
        role=user.get("role", "user"),
        status=user.get("status", "active"),
        is_verified=user.get("is_verified", False),
        created_at=user["created_at"],
        last_login=datetime.utcnow(),
        current_role=user.get("profile", {}).get("current_role"),
        skills=user.get("profile", {}).get("skills", []),
        github_username=user.get("profile", {}).get("github_username"),
        portfolio_url=user.get("profile", {}).get("portfolio_url")
    )
    
    print(f"✅ User login: {credentials.email} ({user['_id']})")
    
    return TokenResponse(
        access_token=access_token,
        expires_in=1440 * 60,
        user_id=user["_id"],
        user=user_public
    )

@router.post("/logout")
async def logout_user(
    current_user: Dict = Depends(get_current_active_user),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Logout user (invalidate session)"""
    
    # Remove from Redis cache
    await redis_client.delete(f"user_session:{current_user['_id']}")
    
    print(f"🔒 User logout: {current_user['email']} ({current_user['_id']})")
    
    return {"message": "Successfully logged out"}
