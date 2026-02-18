"""
ORM Models
===========
SQLAlchemy models for bankers, verifications, decisions, audit_logs.
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, JSON,
    ForeignKey, Enum, LargeBinary, TIMESTAMP
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database import Base


class Banker(Base):
    __tablename__ = "bankers"

    banker_id = Column(Integer, primary_key=True, autoincrement=True)
    banker_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=True)
    branch_code = Column(String(10), nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_login = Column(TIMESTAMP, nullable=True)
    login_count = Column(Integer, default=0)

    decisions = relationship("Decision", back_populates="banker")
    audit_logs = relationship("AuditLog", back_populates="banker")

    def __repr__(self):
        return f"<Banker(id={self.banker_id}, name='{self.banker_name}', email='{self.email}')>"


class Verification(Base):
    __tablename__ = "verifications"

    verification_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    reference_image_path = Column(String(255), nullable=True)
    reference_image_base64 = Column(LargeBinary, nullable=True)
    quality_score = Column(Float, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    is_active = Column(Boolean, default=True)

    decisions = relationship("Decision", back_populates="verification")

    def __repr__(self):
        return f"<Verification(id={self.verification_id}, user='{self.user_id}')>"


class Decision(Base):
    __tablename__ = "decisions"

    decision_id = Column(Integer, primary_key=True, autoincrement=True)
    banker_id = Column(Integer, ForeignKey("bankers.banker_id"), nullable=False, index=True)
    verification_id = Column(Integer, ForeignKey("verifications.verification_id"), nullable=False)
    user_id = Column(String(50), nullable=True, index=True)
    live_image_path = Column(String(255), nullable=True)
    live_image_base64 = Column(LargeBinary, nullable=True)
    match_score = Column(Float, nullable=True)
    adjusted_score = Column(Float, nullable=True)
    confidence_level = Column(Enum("HIGH", "MEDIUM", "LOW", name="confidence_enum"), nullable=True)
    decision = Column(Enum("APPROVE", "REJECT", "REVIEW", name="decision_enum"), nullable=True)
    banker_action = Column(String(50), nullable=True)
    variations_detected = Column(JSON, nullable=True)
    liveness_score = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    decision_time_seconds = Column(Integer, nullable=True)
    banker_reasoning = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    device_info = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    banker = relationship("Banker", back_populates="decisions")
    verification = relationship("Verification", back_populates="decisions")

    def __repr__(self):
        return f"<Decision(id={self.decision_id}, banker={self.banker_id}, score={self.match_score})>"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    banker_id = Column(Integer, ForeignKey("bankers.banker_id"), nullable=False)
    action = Column(String(50), nullable=True, index=True)
    decision_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    status = Column(Enum("SUCCESS", "FAILED", name="status_enum"), nullable=True)
    error_message = Column(Text, nullable=True)

    banker = relationship("Banker", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.log_id}, banker={self.banker_id}, action='{self.action}')>"


class InferenceLog(Base):
    __tablename__ = "inference_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(100), nullable=False, index=True)
    banker_id = Column(Integer, ForeignKey("bankers.banker_id"), nullable=False, index=True)
    user_id = Column(String(50), nullable=True)
    similarity_score = Column(Float, nullable=False)
    adjusted_score = Column(Float, nullable=True)
    confidence_level = Column(Enum("HIGH", "MEDIUM", "LOW", name="confidence_enum"), nullable=True)
    decision = Column(String(50), nullable=True)
    variations_json = Column(JSON, nullable=True)
    quality_json = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=True)
    feature_importance = Column(JSON, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    is_anomaly = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
