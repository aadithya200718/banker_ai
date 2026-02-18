"""
Decision Engine Module
=======================
Applies threshold logic to determine verification outcome.
Adjusts thresholds when appearance variations are detected.
ENHANCED: Probability thresholds, anomaly detection, feature importance.
"""


# Default thresholds (Tuned for Facenet512 + Cosine Similarity)
APPROVE_THRESHOLD = 0.40
REVIEW_THRESHOLD = 0.30

# Fallback threshold: if confidence is below this, always review/reject
MIN_CONFIDENCE_THRESHOLD = 0.30


def make_decision(
    similarity_score: float,
    threshold_adjustment: float = 0.0,
    quality_metrics: dict | None = None,
    variations_count: int = 0
) -> dict:
    """
    Determine verification decision with enhanced logic.

    Args:
        similarity_score: 0.0 - 1.0
        threshold_adjustment: relaxation amount (0.0 - 0.10)
        quality_metrics: dict of brightness, sharpness, etc.
        variations_count: number of detected variations

    Returns:
        Dict with decision, confidence, explanation data, and feature importance.
    """
    # 1. Threshold Calculation
    adj = min(threshold_adjustment, 0.10)
    effective_approve = APPROVE_THRESHOLD - adj
    effective_review = REVIEW_THRESHOLD - adj

    decision = "reject"
    confidence_level = "LOW"
    reasons = []
    
    # 2. Base Decision
    sim_percent = int(similarity_score * 100)
    
    if similarity_score >= effective_approve:
        decision = "approve"
        confidence_level = "HIGH"
        reasons.append(f"✅ Facial Match: Strong similarity ({sim_percent}%)")
    elif similarity_score >= effective_review:
        decision = "manual_review"
        confidence_level = "MEDIUM"
        reasons.append(f"⚠️ Facial Match: Moderate similarity ({sim_percent}%) - Needs Review")
    else:
        decision = "reject"
        confidence_level = "LOW"
        reasons.append(f"❌ Facial Match: Low similarity ({sim_percent}%) - ID Mismatch")

    # 3. Probability / Confidence Calculation (Heuristic)
    # We combine similarity, quality, and variation penalties into a 0-1 confidence float
    # Base confidence is the similarity score relative to the threshold
    # Normalized so that approve threshold maps to ~0.8
    if similarity_score > 0:
        base_conf = min(1.0, similarity_score / (effective_approve * 1.2))
    else:
        base_conf = 0.0

    # Penalties
    quality_penalty = 0.0
    if quality_metrics:
        if quality_metrics.get("sharpness", 1.0) < 0.3: quality_penalty += 0.1
        if quality_metrics.get("brightness", 0.5) < 0.2: quality_penalty += 0.1
    
    var_penalty = variations_count * 0.05
    
    comp_confidence = max(0.0, base_conf - quality_penalty - var_penalty)
    
    # 4. Fallback Logic
    if comp_confidence < MIN_CONFIDENCE_THRESHOLD and decision == "approve":
        decision = "manual_review"
        reasons.append("⚠️ Low holistic confidence despite high similarity (Quality/Variations)")
        confidence_level = "LOW"

    # 5. Anomaly Detection
    is_anomaly = False
    if similarity_score > 0.95 and variations_count > 3:
        # Suspicious: perfect match but many variations (e.g. deepfake mask?)
        is_anomaly = True
        reasons.append("🚩 Anomaly: High similarity with multiple diverse variations")
    
    if similarity_score == 0.0 and quality_metrics and quality_metrics.get("sharpness", 0) > 0.8:
        # Suspicious: clear image but zero match? (Wrong person or spoof)
        pass # Not necessarily an anomaly, just a mismatch

    # 6. Feature Importance (Explainability)
    # Estimate contribution of each factor
    feature_importance = {
        "similarity": round(0.7 + (0.1 if decision=="approve" else 0), 2),
        "quality": round(0.2 if quality_penalty > 0 else 0.1, 2),
        "variations": round(0.1 + (0.1 if variations_count > 0 else 0), 2)
    }

    # Narrative construction handled by Explanation Engine, but we pass partials here
    if threshold_adjustment > 0:
        reasons.append(f"ℹ️ Threshold relaxed by {adj:.2f} due to variations")

    return {
        "decision": decision,
        "confidence_level": confidence_level,
        "confidence_score": round(comp_confidence, 3), # New field
        "effective_approve_threshold": round(float(effective_approve), 3),
        "effective_review_threshold": round(float(effective_review), 3),
        "threshold_adjustment_applied": round(float(adj), 3),
        "reasons": reasons,
        "feature_importance": feature_importance,
        "is_anomaly": is_anomaly
    }
