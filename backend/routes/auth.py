"""
Auth Routes
============
POST /api/v1/auth/login   — Banker login with email + password
POST /api/v1/auth/logout  — Banker logout
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Banker
from backend.auth_service import verify_password, create_access_token, get_current_banker, hash_password
from backend.audit_service import log_action

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


# ── Request / Response schemas ───────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    banker_id: int
    banker_name: str
    email: str
    branch_code: str | None = None


class RegisterRequest(BaseModel):
    banker_name: str
    email: str
    password: str
    phone: str | None = None
    branch_code: str | None = None


# ── Endpoints ────────────────────────────────────────────────────────

@router.post("/register", response_model=LoginResponse)
async def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new banker."""
    # Check if email exists
    if db.query(Banker).filter(Banker.email == body.email).first():
        logger.warning(f"Registration failed — email exists: {body.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new banker
    new_banker = Banker(
        banker_name=body.banker_name,
        email=body.email,
        password_hash=hash_password(body.password),
        phone=body.phone,
        branch_code=body.branch_code,
    )
    db.add(new_banker)
    db.commit()
    db.refresh(new_banker)

    # Create token
    token = create_access_token(new_banker.banker_id, new_banker.email, new_banker.banker_name)

    # Log action
    log_action(
        db, new_banker.banker_id, "REGISTER", status="SUCCESS",
        details={"email": new_banker.email},
    )

    return LoginResponse(
        token=token,
        banker_id=new_banker.banker_id,
        banker_name=new_banker.banker_name,
        email=new_banker.email,
        branch_code=new_banker.branch_code,
    )

@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Authenticate banker and return JWT token."""
    banker = db.query(Banker).filter(Banker.email == body.email).first()

    if not banker:
        logger.warning(f"Login failed — email not found: {body.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not banker.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    if not verify_password(body.password, banker.password_hash):
        log_action(
            db, banker.banker_id, "LOGIN", status="FAILED",
            details={"ip": request.client.host, "reason": "wrong_password"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Success — update login stats
    banker.last_login = datetime.now(timezone.utc)
    banker.login_count = (banker.login_count or 0) + 1
    db.commit()

    token = create_access_token(banker.banker_id, banker.email, banker.banker_name)

    log_action(
        db, banker.banker_id, "LOGIN", status="SUCCESS",
        details={"ip": request.client.host},
    )

    return LoginResponse(
        token=token,
        banker_id=banker.banker_id,
        banker_name=banker.banker_name,
        email=banker.email,
        branch_code=banker.branch_code,
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_banker: dict = Depends(get_current_banker),
    db: Session = Depends(get_db),
):
    """Log out the current banker (audit only — client clears token)."""
    log_action(
        db, current_banker["banker_id"], "LOGOUT", status="SUCCESS",
        details={"ip": request.client.host},
    )
    return {"status": "logged_out"}


@router.get("/me")
async def get_me(current_banker: dict = Depends(get_current_banker)):
    """Return the current banker's identity from the JWT."""
    return {
        "banker_id": current_banker["banker_id"],
        "email": current_banker["email"],
        "banker_name": current_banker["banker_name"],
    }
