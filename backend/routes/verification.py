"""
Verification Routes
====================
POST /api/v1/verify  — Run ML pipeline, create decision record, log inference
POST /api/v1/decide  — Banker approves / rejects a decision
GET  /api/v1/my-decisions — Get current banker's decisions
"""

import time
import uuid
import logging
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Verification, Decision, InferenceLog
from backend.auth_service import get_current_banker
from backend.audit_service import log_action
from backend.face_service import get_face_service
from backend.variation_detector import get_variation_detector
from backend.explanation_engine import generate_explanation
from backend.decision_engine import make_decision

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Verification"])


# ── Schemas ──────────────────────────────────────────────────────────

class DecideRequest(BaseModel):
    decision_id: int
    action: str  # BANKER_APPROVE, BANKER_REJECT, REQUEST_RECAPTURE
    reasoning: str | None = None


# ── Endpoints ────────────────────────────────────────────────────────

@router.post("/verify")
async def verify_faces(
    request: Request,
    live_image: UploadFile = File(..., description="Live face image from camera"),
    reference_image: UploadFile = File(..., description="Reference ID image"),
    user_id: str = "UNKNOWN",
    current_banker: dict = Depends(get_current_banker),
    db: Session = Depends(get_db),
):
    """
    JWT-protected verification endpoint.
    Runs the ML pipeline and creates a Decision record tied to banker_id.
    """
    banker_id = current_banker["banker_id"]
    request_id = f"ver_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    t0 = time.time()

    try:
        # Validate MIME types
        for img_file, name in [(live_image, "live"), (reference_image, "reference")]:
            if not img_file.content_type or not img_file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail=f"{name} file must be an image")

        live_bytes = await live_image.read()
        ref_bytes = await reference_image.read()

        if len(live_bytes) == 0 or len(ref_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image file(s)")

        # Step 1 — Face Service (Enhanced with caching, validation, retry)
        face_svc = get_face_service()
        # verify() now returns dict with keys: similarity_score, quality, processing_time_ms, used_gallery_match
        face_result = face_svc.verify(live_bytes, ref_bytes, user_id=user_id)
        
        similarity = face_result["similarity_score"]
        quality = face_result["quality"]
        
        # Step 2 — Variation Detection
        var_detector = get_variation_detector()
        var_result = var_detector.detect(live_bytes, ref_bytes)
        variations = var_result["variations"]
        threshold_adj = var_result["threshold_adjustment"]
        var_details = var_result["details"]

        # Step 3 — Decision Engine (Enhanced)
        decision_result = make_decision(
            similarity_score=similarity,
            threshold_adjustment=threshold_adj,
            quality_metrics=quality,
            variations_count=len(variations)
        )
        
        decision_str = decision_result["decision"]
        confidence_level = decision_result["confidence_level"]
        feature_importance = decision_result["feature_importance"]
        is_anomaly = decision_result["is_anomaly"]
        reasons = decision_result["reasons"]

        # Step 4 — Explanation (Enhanced)
        explanation = generate_explanation(
            similarity_score=similarity,
            confidence_level=confidence_level,
            decision=decision_str,
            variations=variations,
            variation_details=var_details,
            quality=quality,
            feature_importance=feature_importance
        )

        processing_time = (time.time() - t0) * 1000

        # Step 5 — DB Logic
        
        # 5a. Inference Log (New Observability)
        try:
            inf_log = InferenceLog(
                request_id=request_id,
                banker_id=banker_id,
                user_id=user_id,
                similarity_score=similarity,
                adjusted_score=similarity + threshold_adj,
                confidence_level=confidence_level,
                decision=decision_str,
                variations_json=variations,
                quality_json=quality,
                explanation=explanation,
                feature_importance=feature_importance,
                processing_time_ms=int(processing_time),
                is_anomaly=is_anomaly
            )
            db.add(inf_log)
        except Exception as e:
            logger.error(f"Failed to create InferenceLog: {e}")

        # 5b. Verification record
        verification = Verification(
            user_id=user_id,
            quality_score=quality.get("sharpness", 0),
        )
        db.add(verification)
        db.flush()

        # Map decision string to enum for Decision table
        decision_enum = decision_str.upper()
        if decision_enum not in ("APPROVE", "REJECT", "REVIEW"):
            decision_enum = "REVIEW"
        if decision_str == "manual_review":
            decision_enum = "REVIEW"

        # 5c. Decision record
        decision_record = Decision(
            banker_id=banker_id,
            verification_id=verification.verification_id,
            user_id=user_id,
            match_score=similarity,
            adjusted_score=similarity + threshold_adj,
            confidence_level=confidence_level,
            decision=decision_enum,
            banker_action=None,
            variations_detected=var_details,
            processing_time_ms=int(processing_time),
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("user-agent", ""),
        )
        db.add(decision_record)
        db.commit()
        db.refresh(decision_record)

        # 5d. Audit Log
        log_action(
            db, banker_id, "VERIFY", status="SUCCESS",
            decision_id=decision_record.decision_id,
            details={"request_id": request_id, "user_id": user_id, "result": decision_str},
        )

        logger.info(
            f"✅ [{request_id}] banker={banker_id} Score={similarity:.3f} "
            f"Decision={decision_str} Conf={confidence_level} Time={processing_time:.0f}ms"
        )
        
        # ── Learning: Save Approved Live Image ───────────────────────
        if decision_enum == "APPROVE":
            try:
                import os
                gallery_dir = f"data/users/{user_id}"
                os.makedirs(gallery_dir, exist_ok=True)
                filename = f"{gallery_dir}/{int(time.time())}.jpg"
                with open(filename, "wb") as f:
                    f.write(live_bytes)
            except Exception as e:
                logger.warning(f"Failed to save gallery image: {e}")

        # Final Response
        return {
            "request_id": request_id,
            "decision_id": decision_record.decision_id,
            "status": "success",
            "similarity_score": similarity,
            "match_score": similarity,
            "adjusted_score": round(similarity + threshold_adj, 4),
            "confidence_level": confidence_level,
            "confidence_probability": decision_result.get("confidence_score", 0.0), # New field
            "decision": decision_str,
            "recommendation": _format_recommendation(decision_str, confidence_level),
            "explanation": explanation,
            "detected_variations": variations,
            "variation_details": var_details,
            "quality": quality,
            "feature_importance": feature_importance, # New field
            "reasons": reasons,
            "is_anomaly": is_anomaly,
            "thresholds": {
                "approve": decision_result["effective_approve_threshold"],
                "review": decision_result["effective_review_threshold"],
                "adjustment_applied": threshold_adj,
            },
            "processing_time_ms": round(processing_time, 1),
        }

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"❌ [{request_id}] Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ [{request_id}] Internal error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.post("/decide")
async def banker_decide(
    body: DecideRequest,
    request: Request,
    current_banker: dict = Depends(get_current_banker),
    db: Session = Depends(get_db),
):
    """Banker approves or rejects a verification."""
    banker_id = current_banker["banker_id"]

    decision = db.query(Decision).filter(Decision.decision_id == body.decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    if decision.banker_id != banker_id:
        log_action(
            db, banker_id, "UNAUTHORIZED_DECIDE", status="FAILED",
            decision_id=body.decision_id,
            details={"attempted_action": body.action},
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    decision.banker_action = body.action
    decision.banker_reasoning = body.reasoning
    db.commit()

    action_log = body.action.replace("BANKER_", "")
    log_action(
        db, banker_id, action_log, status="SUCCESS",
        decision_id=body.decision_id,
        details={"reasoning": body.reasoning, "ip": request.client.host if request.client else None},
    )

    return {"status": "success", "message": f"Decision recorded: {body.action}"}


@router.get("/my-decisions")
async def get_my_decisions(
    current_banker: dict = Depends(get_current_banker),
    db: Session = Depends(get_db),
    limit: int = 50,
):
    """Get the current banker's decisions only."""
    banker_id = current_banker["banker_id"]
    decisions = (
        db.query(Decision)
        .filter(Decision.banker_id == banker_id)
        .order_by(Decision.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "banker_id": banker_id,
        "total": len(decisions),
        "decisions": [
            {
                "decision_id": d.decision_id,
                "user_id": d.user_id,
                "match_score": d.match_score,
                "confidence_level": d.confidence_level,
                "decision": d.decision,
                "banker_action": d.banker_action,
                "variations_detected": d.variations_detected,
                "created_at": str(d.created_at) if d.created_at else None,
            }
            for d in decisions
        ],
    }


# ── Helpers ──────────────────────────────────────────────────────────

def _format_recommendation(decision: str, confidence: str) -> str:
    if decision == "approve":
        return f"Auto Approve — {confidence.lower()} confidence match"
    elif decision == "manual_review":
        return "Manual Review Required — match is inconclusive"
    else:
        return "Reject — faces do not appear to match"
