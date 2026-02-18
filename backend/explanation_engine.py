"""
Explanation Engine Module
==========================
Converts raw verification signals into banker-friendly text explanations.
ENHANCED: Feature importance highlighting and structured summaries.
"""

def generate_explanation(
    similarity_score: float,
    confidence_level: str,
    decision: str,
    variations: list[str],
    variation_details: dict,
    quality: dict,
    feature_importance: dict | None = None
) -> str:
    """
    Generate a human-readable explanation of the verification result.
    
    Args:
        similarity_score: 0.0 - 1.0
        confidence_level: HIGH / MEDIUM / LOW
        decision: approve / manual_review / reject
        variations: detected tags
        quality: image metrics
        feature_importance: contribution weights
    """
    lines = []
    pct = int(similarity_score * 100)

    # 1. Primary Headline
    if decision == "approve":
        lines.append(f"**Verification Successful ({pct}% Match)**.")
        lines.append("System confidently matched the live person to ID.")
    elif decision == "manual_review":
        lines.append(f"**Manual Review Required ({pct}% Match)**.")
        lines.append("Resemblance detected, but confidence is reduced due to quality or variations.")
    else:
        lines.append(f"**Verification Rejected ({pct}% Match)**.")
        lines.append("Faces do not match sufficiently.")

    # 2. Feature Contributors (Explainability)
    if feature_importance:
        # Find dominant factor
        factors = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        top_factor = factors[0][0]
        if top_factor == "similarity":
            lines.append("Decision was primarily driven by face geometry.")
        elif top_factor == "quality":
            lines.append("Image quality significantly impacted the confidence score.")
        elif top_factor == "variations":
            lines.append("Detected appearance changes (glasses/beard/aging) were key factors.")

    # 3. Variations Detail
    if variations:
        lines.append("Observations:")
        for v in variations:
            note = variation_details.get(v, {}).get("note", "").strip()
            if v == "glasses":
                lines.append("- Eyewear detected (compared to ID).")
            elif v == "aging_difference":
                lines.append("- Age-related features or makeup differences detected.")
            elif v == "lighting_difference":
                lines.append("- Significant lighting difference observed.")
            else:
                formatted = v.replace("_", " ").title()
                lines.append(f"- {formatted}: {note if note else 'Detected'}.")

    # 4. Quality Alerts
    q_notes = []
    if quality.get("sharpness", 1.0) < 0.3: q_notes.append("Live image is blurry")
    if quality.get("brightness", 0.5) < 0.2: q_notes.append("Lighting is too dark")
    
    if q_notes:
        lines.append("Quality Warning: " + ", ".join(q_notes) + ".")

    return " ".join(lines)
