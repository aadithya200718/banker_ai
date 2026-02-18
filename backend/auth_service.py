"""
Authentication Service
=======================
Password hashing (bcrypt) and JWT token management.
"""

from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRY_HOURS, BCRYPT_ROUNDS

security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Compare a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(
    banker_id: int,
    email: str,
    banker_name: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT token containing banker identity."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(hours=JWT_EXPIRY_HOURS)
    )
    payload = {
        "banker_id": banker_id,
        "email": email,
        "banker_name": banker_name,
        "iat": datetime.now(timezone.utc),
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """Validate and decode a JWT token. Returns payload dict or raises."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        banker_id = payload.get("banker_id")
        if banker_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing banker_id",
            )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
        )


def get_current_banker(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """FastAPI dependency — extract and validate banker from JWT."""
    return verify_token(credentials.credentials)
