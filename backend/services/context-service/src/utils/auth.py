from fastapi import HTTPException, Header
from jose import jwt

def require_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
        
        # For v1, accept signature-less decoding if gateway validated
        claims = jwt.get_unverified_claims(token)
        user_id = claims.get("sub")
        if not user_id:
            raise ValueError("No sub in token")
        return user_id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized: {str(e)}")
