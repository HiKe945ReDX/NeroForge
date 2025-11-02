"""
Enhanced Authentication endpoints with email verification and password reset
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.database import get_database
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    validate_password_strength
)
from ..core.email_service import email_service
from ..core.token_service import token_service
from ..models.user import (
    UserCreate,
    UserResponse,
    TokenResponse,
    PasswordResetRequest,
    PasswordReset,
    EmailVerification
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ============================================================================
# SIGNUP WITH EMAIL VERIFICATION
# ============================================================================

@router.post("/signup", response_model=dict, status_code=status.HTTP_201_CREATED)
async def signup(
    user: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Register new user and send verification email
    - User account created but NOT active until email verified
    """
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    is_valid, error_msg = validate_password_strength(user.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Create user document
    user_doc = {
        "email": user.email.lower(),
        "full_name": user.full_name,
        "hashed_password": get_password_hash(user.password),
        "email_verified": False,
        "is_active": False,  # Inactive until email verified
        "is_superuser": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "failed_login_attempts": 0
    }
    
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    # Generate verification token
    verification_token = token_service.create_verification_token(user_id, user.email.lower())
    
    # Send verification email
    email_sent = await email_service.send_verification_email(
        to_email=user.email.lower(),
        token=verification_token,
        user_name=user.full_name or ""
    )
    
    if not email_sent:
        logger.warning(f"Failed to send verification email to {user.email}")
    
    return {
        "message": "Account created successfully. Please check your email to verify your account.",
        "email": user.email.lower(),
        "user_id": user_id,
        "email_sent": email_sent
    }


# ============================================================================
# EMAIL VERIFICATION
# ============================================================================

@router.post("/verify-email", response_model=dict)
async def verify_email(
    verification: EmailVerification,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Verify email address using token from email
    """
    # Verify token
    payload = token_service.verify_verification_token(verification.token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    user_id = payload.get("user_id")
    email = payload.get("email")
    
    # Update user
    result = await db.users.update_one(
        {"_id": user_id, "email": email},
        {
            "$set": {
                "email_verified": True,
                "is_active": True,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or already verified"
        )
    
    logger.info(f"✅ Email verified for user: {email}")
    
    return {
        "message": "Email verified successfully. You can now log in.",
        "email": email
    }


@router.post("/resend-verification", response_model=dict)
async def resend_verification(
    email: str = Body(..., embed=True),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Resend verification email
    """
    user = await db.users.find_one({"email": email.lower()})
    
    if not user:
        # Don't reveal if user exists for security
        return {"message": "If an account exists with this email, a verification link has been sent."}
    
    if user.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Generate new verification token
    user_id = str(user["_id"])
    verification_token = token_service.create_verification_token(user_id, email.lower())
    
    # Send email
    await email_service.send_verification_email(
        to_email=email.lower(),
        token=verification_token,
        user_name=user.get("full_name", "")
    )
    
    return {"message": "Verification email sent. Please check your inbox."}


# ============================================================================
# LOGIN (Enhanced with verification check)
# ============================================================================

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Login with email and password
    - Requires verified email
    - Returns access token + refresh token
    """
    # Find user
    user = await db.users.find_one({"email": form_data.username.lower()})
    
    if not user or not verify_password(form_data.password, user.get("hashed_password", "")):
        # Increment failed attempts
        if user:
            await db.users.update_one(
                {"_id": user["_id"]},
                {
                    "$inc": {"failed_login_attempts": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if email is verified
    if not user.get("email_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email for verification link."
        )
    
    # Check if account is active
    if not user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support."
        )
    
    # Check if account is locked
    locked_until = user.get("locked_until")
    if locked_until and locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked due to multiple failed login attempts. Try again later."
        )
    
    # Reset failed attempts on successful login
    user_id = str(user["_id"])
    await db.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "failed_login_attempts": 0,
                "last_login": datetime.utcnow(),
                "locked_until": None,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user_id, "email": user["email"]},
        expires_delta=timedelta(minutes=15)
    )
    
    refresh_token = token_service.create_refresh_token(user_id)
    
    logger.info(f"✅ User logged in: {user['email']}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=900  # 15 minutes
    )


# ============================================================================
# PASSWORD RESET
# ============================================================================

@router.post("/forgot-password", response_model=dict)
async def forgot_password(
    request: PasswordResetRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Request password reset link
    - Always returns success (don't reveal if user exists)
    """
    user = await db.users.find_one({"email": request.email.lower()})
    
    if user:
        user_id = str(user["_id"])
        reset_token = token_service.create_password_reset_token(user_id, request.email.lower())
        
        await email_service.send_password_reset_email(
            to_email=request.email.lower(),
            token=reset_token,
            user_name=user.get("full_name", "")
        )
        
        logger.info(f"Password reset requested for: {request.email.lower()}")
    
    # Always return success for security
    return {
        "message": "If an account exists with this email, a password reset link has been sent."
    }


@router.post("/reset-password", response_model=dict)
async def reset_password(
    reset: PasswordReset,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Reset password using token from email
    """
    # Verify token
    payload = token_service.verify_reset_token(reset.token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Validate new password
    is_valid, error_msg = validate_password_strength(reset.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    user_id = payload.get("user_id")
    email = payload.get("email")
    
    # Update password
    result = await db.users.update_one(
        {"_id": user_id, "email": email},
        {
            "$set": {
                "hashed_password": get_password_hash(reset.new_password),
                "updated_at": datetime.utcnow(),
                "failed_login_attempts": 0,
                "locked_until": None
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info(f"✅ Password reset for user: {email}")
    
    return {
        "message": "Password reset successfully. You can now log in with your new password."
    }


# ============================================================================
# REFRESH TOKEN
# ============================================================================

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get new access token using refresh token
    """
    # Verify refresh token
    payload = token_service.verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user_id = payload.get("user_id")
    
    # Verify user still exists and is active
    user = await db.users.find_one({"_id": user_id})
    if not user or not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    new_access_token = create_access_token(
        data={"sub": user_id, "email": user["email"]},
        expires_delta=timedelta(minutes=15)
    )
    
    # Optionally rotate refresh token (for extra security)
    new_refresh_token = token_service.create_refresh_token(user_id)
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=900
    )


# ============================================================================
# GET CURRENT USER
# ============================================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> dict:
    """
    Get current authenticated user from token
    """
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user = await db.users.find_one({"_id": user_id})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.get("is_active"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        return user
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile
    """
    return UserResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        full_name=current_user.get("full_name"),
        email_verified=current_user.get("email_verified", False),
        is_active=current_user.get("is_active", False),
        created_at=current_user.get("created_at"),
        last_login=current_user.get("last_login")
    )


# ============================================================================
# LOGOUT (Future: with token blacklist)
# ============================================================================

@router.post("/logout", response_model=dict)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout user
    TODO: Implement token blacklist in Redis
    """
    logger.info(f"User logged out: {current_user['email']}")
    
    return {
        "message": "Logged out successfully"
    }

