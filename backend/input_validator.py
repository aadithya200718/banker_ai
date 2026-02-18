"""
Input Validator Module
=======================
Pre-inference validation for images and user inputs.
Ensures data quality before ML pipeline processing.
"""

import re
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
MIN_RESOLUTION = 64                 # Minimum 64x64 pixels
MAX_RESOLUTION = 8000               # Maximum 8000x8000 pixels
SUPPORTED_FORMATS = {"image/jpeg", "image/png", "image/jpg", "image/webp", "image/bmp"}
USER_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]{1,50}$")


class ValidationError(Exception):
    """Raised when input validation fails."""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error on '{field}': {message}")


def validate_image_bytes(data: bytes, label: str = "image") -> np.ndarray:
    """
    Validate raw image bytes before inference.

    Checks:
    - Non-empty data
    - File size within limits
    - Valid image decode (not corrupt)
    - Minimum and maximum resolution
    - At least 3 color channels (BGR)

    Args:
        data: Raw image bytes.
        label: Human-friendly label for error messages (e.g., "live", "reference").

    Returns:
        Decoded OpenCV BGR image (np.ndarray).

    Raises:
        ValidationError: If any check fails.
    """
    # 1. Non-empty check
    if not data or len(data) == 0:
        raise ValidationError(label, "Image data is empty")

    # 2. File size cap
    if len(data) > MAX_IMAGE_SIZE:
        size_mb = len(data) / (1024 * 1024)
        raise ValidationError(
            label,
            f"Image too large ({size_mb:.1f} MB). Maximum allowed is {MAX_IMAGE_SIZE // (1024*1024)} MB"
        )

    # 3. Decode check (corrupt data detection)
    try:
        nparr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception as e:
        raise ValidationError(label, f"Failed to decode image: {str(e)}")

    if img is None:
        raise ValidationError(label, "Image is corrupt or in an unsupported format")

    # 4. Resolution checks
    h, w = img.shape[:2]
    if h < MIN_RESOLUTION or w < MIN_RESOLUTION:
        raise ValidationError(
            label,
            f"Image resolution too low ({w}x{h}). Minimum is {MIN_RESOLUTION}x{MIN_RESOLUTION}"
        )

    if h > MAX_RESOLUTION or w > MAX_RESOLUTION:
        raise ValidationError(
            label,
            f"Image resolution too high ({w}x{h}). Maximum is {MAX_RESOLUTION}x{MAX_RESOLUTION}"
        )

    # 5. Channel check
    if len(img.shape) < 3 or img.shape[2] < 3:
        raise ValidationError(label, "Image must be a color image (at least 3 channels)")

    logger.debug(f"✅ Validated {label} image: {w}x{h}, {len(data)} bytes")
    return img


def validate_content_type(content_type: str | None, label: str = "image") -> None:
    """
    Validate that the uploaded file has a supported image MIME type.

    Args:
        content_type: MIME type string from the upload.
        label: Human-friendly label for error messages.

    Raises:
        ValidationError: If the content type is missing or unsupported.
    """
    if not content_type:
        raise ValidationError(label, "Missing content type header")

    if content_type.lower() not in SUPPORTED_FORMATS:
        raise ValidationError(
            label,
            f"Unsupported format '{content_type}'. Supported: JPEG, PNG, WebP, BMP"
        )


def validate_user_id(user_id: str) -> str:
    """
    Sanitize and validate user ID string.

    Rules:
    - Alphanumeric, underscores, hyphens, dots only
    - 1-50 characters
    - Stripped of leading/trailing whitespace

    Args:
        user_id: Raw user ID input.

    Returns:
        Cleaned user ID string.

    Raises:
        ValidationError: If the user ID is invalid.
    """
    if not user_id or not user_id.strip():
        return "UNKNOWN"

    cleaned = user_id.strip()

    if len(cleaned) > 50:
        raise ValidationError("user_id", "User ID must be 50 characters or fewer")

    if not USER_ID_PATTERN.match(cleaned):
        raise ValidationError(
            "user_id",
            "User ID may only contain letters, numbers, underscores, hyphens, and dots"
        )

    return cleaned


def validate_image_pair(
    live_bytes: bytes,
    ref_bytes: bytes,
    live_content_type: str | None = None,
    ref_content_type: str | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Validate both images in a verification pair.

    Args:
        live_bytes: Raw bytes for the live capture image.
        ref_bytes: Raw bytes for the reference ID image.
        live_content_type: MIME type of the live image upload.
        ref_content_type: MIME type of the reference image upload.

    Returns:
        Tuple of (live_img, ref_img) as OpenCV BGR arrays.

    Raises:
        ValidationError: If either image fails validation.
    """
    # Validate content types if provided
    if live_content_type:
        validate_content_type(live_content_type, "live_image")
    if ref_content_type:
        validate_content_type(ref_content_type, "reference_image")

    # Validate and decode images
    live_img = validate_image_bytes(live_bytes, "live_image")
    ref_img = validate_image_bytes(ref_bytes, "reference_image")

    return live_img, ref_img
