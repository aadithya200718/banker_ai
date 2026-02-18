"""
Variation Detector Module
==========================
Detects appearance variations between live and reference images:
- Glasses / sunglasses
- Lighting differences
- Pose angle deviation
- Face occlusion

Uses OpenCV-based analysis (MediaPipe-free for Python 3.13 compatibility).
"""

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class VariationDetector:
    """Detects appearance variations between face images using OpenCV."""

    def __init__(self):
        # Load Haar cascade for eye detection (glasses proxy)
        self._eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_eye_tree_eyeglasses.xml"
        )
        self._face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        
        # Initialize MediaPipe Face Mesh (Safe Import)
        self.mp_face_mesh = None
        self.face_mesh = None
        try:
            import mediapipe as mp
            if hasattr(mp, "solutions"):
                self.mp_face_mesh = mp.solutions.face_mesh
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    static_image_mode=True,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5
                )
                logger.info("✅ MediaPipe FaceMesh initialized successfully")
            else:
                logger.warning("⚠️ MediaPipe installed but 'solutions' not found. Fallback to OpenCV.")
        except Exception as e:
            logger.warning(f"⚠️ MediaPipe initialization failed: {e}. Fallback to OpenCV.")

    def detect(
        self,
        live_image_bytes: bytes,
        reference_image_bytes: bytes,
    ) -> dict:
        """
        Analyze both images and detect variations.

        Returns:
            {
                "variations": ["glasses", "lighting_difference", ...],
                "threshold_adjustment": 0.05,
                "details": { ... per-variation detail ... }
            }
        """
        live_img = self._bytes_to_cv2(live_image_bytes)
        ref_img = self._bytes_to_cv2(reference_image_bytes)

        variations = []
        details = {}
        threshold_adj = 0.0

        if live_img is None or ref_img is None:
            return {
                "variations": [],
                "threshold_adjustment": 0.0,
                "details": {"error": "Could not decode image(s)"},
            }

        # ── Glasses detection ──
        glasses_result = self._detect_glasses(live_img, ref_img)
        if glasses_result["detected"]:
            variations.append("glasses")
            details["glasses"] = glasses_result
            threshold_adj += 0.05

        # ── Lighting difference ──
        lighting_result = self._detect_lighting_diff(live_img, ref_img)
        if lighting_result["significant"]:
            variations.append("lighting_difference")
            details["lighting_difference"] = lighting_result
            threshold_adj += 0.03

        # ── Face occlusion ──
        occlusion_result = self._detect_occlusion(live_img)
        if occlusion_result["detected"]:
            variations.append("partial_occlusion")
            details["partial_occlusion"] = occlusion_result
            threshold_adj += 0.05

        # ── Pose difference ──
        pose_result = self._detect_pose_diff(live_img, ref_img)
        if pose_result["significant"]:
            variations.append("pose_difference")
            details["pose_difference"] = pose_result
            threshold_adj += 0.03

        # ── Aging / texture difference ──
        age_result = self._detect_age_variation(live_img, ref_img)
        if age_result["detected"]:
            variations.append("aging_difference")
            details["aging_difference"] = age_result
            threshold_adj += 0.02

        # ── Liveness / AI Detection ──
        liveness_result = self._detect_liveness(live_img)
        if liveness_result["is_suspicious"]:
            variations.append("artificial_manipulation")
            details["artificial_manipulation"] = liveness_result
            # Penalize score for suspicious images
            threshold_adj -= 0.10  # Make it HARDER to pass if fake

        # ── Hair / Baldness ──
        hair_result = self._detect_hair_change(live_img, ref_img)
        if hair_result["detected"]:
            variations.append("hair_change")
            details["hair_change"] = hair_result
            threshold_adj += 0.02

        # ── Facial Marks / Scars ──
        marks_result = self._detect_facial_marks(live_img, ref_img)
        if marks_result["detected"]:
            variations.append("facial_marks")
            details["facial_marks"] = marks_result
            threshold_adj += 0.03

        # Cap
        threshold_adj = min(threshold_adj, 0.10)

        return {
            "variations": variations,
            "threshold_adjustment": float(np.round(threshold_adj, 3)),
            "details": details,
        }

    # ── Liveness / AI Detection ────────────────────────────────────── #

    # ── Liveness / AI Detection (MediaPipe Depth) ──────────────────── #

    def _detect_liveness(self, img: np.ndarray) -> dict:
        """
        Check for 3D Liveness using Face Mesh Depth.
        Real faces have depth (Nose Z < Ear Z). Flat screens have constant Z.
        """
        # Initialize default values to prevent UnboundLocalError
        face_depth = 0.1  # Default safe depth (avoids flagging as flat)
        is_suspicious = False
        note = ""

        try:
            if self.face_mesh:
                # 3D Depth Analysis
                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(rgb)

                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark
                    nose_z = landmarks[1].z
                    left_ear_z = landmarks[234].z
                    right_ear_z = landmarks[454].z
                    
                    # Calculate depth magnitude
                    face_depth = (left_ear_z + right_ear_z) / 2 - nose_z
                    
                    if abs(face_depth) < 0.02: 
                        is_suspicious = True
                        note = "Image lacks 3D depth (Likely a screen or photo)."
            
            # Simple Noise Check (Always run as backup or complement)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

            # 2. Texture Check
            if laplacian_var < 50:
                is_suspicious = True
                note = "Image is unnaturally smooth (Digital/AI)."

            return {
                "is_suspicious": bool(is_suspicious),
                "depth_score": float(np.round(face_depth, 4)),
                "noise_score": float(np.round(laplacian_var, 3)),
                "note": note
            }
        except Exception:
             return {"is_suspicious": False, "note": ""}

    # ── Glasses Detection ──────────────────────────────────────────── #

    def _detect_glasses(self, live_img: np.ndarray, ref_img: np.ndarray) -> dict:
        """Detect glasses using edge density in the eye region."""
        try:
            live_score = self._glasses_score(live_img)
            ref_score = self._glasses_score(ref_img)
            diff = abs(live_score - ref_score)
            # TUNED: Increased thresholds (0.25->0.30, 0.55->0.80) to avoid false alarms
            detected = diff > 0.30 or live_score > 0.80 or ref_score > 0.80

            note = ""
            if detected:
                if live_score > ref_score:
                    note = "Glasses detected in live capture"
                else:
                    note = "Glasses detected in reference photo"

            return {
                "detected": bool(detected),
                "live_glasses_score": float(np.round(live_score, 3)),
                "ref_glasses_score": float(np.round(ref_score, 3)),
                "note": note,
            }
        except Exception as e:
            logger.warning(f"Glasses detection error: {e}")
            explanation = "Variation detected: unknown. Please ensure consistent lighting and pose."
            return {"detected": False, "note": ""}

    def _glasses_score(self, img: np.ndarray) -> float:
        """Edge density in the eye region → higher = likely glasses."""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape

            # Detect face first
            faces = self._face_cascade.detectMultiScale(gray, 1.3, 5)
            if len(faces) == 0:
                # Fallback: use the upper-middle region as proxy
                y1, y2 = int(h * 0.2), int(h * 0.5)
                x1, x2 = int(w * 0.15), int(w * 0.85)
            else:
                fx, fy, fw, fh = faces[0]
            # Eye region: Strict ROI to avoid eyebrows
                # Original: y1 = fy + int(fh * 0.15), y2 = fy + int(fh * 0.45) -> Caught eyebrows
                # New: y1 = fy + int(fh * 0.28), y2 = fy + int(fh * 0.50) -> Focus on eye/nose bridge
                y1 = fy + int(fh * 0.28) 
                y2 = fy + int(fh * 0.50)
                x1 = fx + int(fw * 0.15)
                x2 = fx + int(fw * 0.85)

            eye_region = gray[y1:y2, x1:x2]
            if eye_region.size == 0:
                return 0.0

            edges = cv2.Canny(eye_region, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # TUNED: Increased divisor to 0.60 (was 0.40) to be very strict
            # This drastically reduces confusion with dark circles/shadows
            return float(min(1.0, edge_density / 0.60))

        except Exception:
            return 0.0

    # ── Lighting Difference ────────────────────────────────────────── #

    def _detect_lighting_diff(self, live_img: np.ndarray, ref_img: np.ndarray) -> dict:
        try:
            live_gray = cv2.cvtColor(live_img, cv2.COLOR_BGR2GRAY)
            ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)

            brightness_diff = abs(float(live_gray.mean()) - float(ref_gray.mean())) / 255.0
            contrast_diff = abs(float(live_gray.std()) - float(ref_gray.std())) / 128.0

            significant = brightness_diff > 0.2 or contrast_diff > 0.3

            return {
                "significant": bool(significant),
                "brightness_diff": float(np.round(brightness_diff, 3)),
                "contrast_diff": float(np.round(contrast_diff, 3)),
                "note": "Noticeable lighting difference between images" if significant else "",
            }
        except Exception as e:
            logger.warning(f"Lighting detection error: {e}")
            return {"significant": False, "note": ""}

    # ── Occlusion Detection ────────────────────────────────────────── #

    def _detect_occlusion(self, img: np.ndarray) -> dict:
        """Detect partial face occlusion via face-detection confidence."""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self._face_cascade.detectMultiScale(gray, 1.1, 4)

            if len(faces) == 0:
                return {
                    "detected": True,
                    "note": "Face not fully visible — possible occlusion or angle issue",
                }

            # Check if the detected face is oddly small relative to image
            h, w = gray.shape
            fx, fy, fw, fh = faces[0]
            face_ratio = (fw * fh) / (w * h)

            if face_ratio < 0.03:
                return {
                    "detected": True,
                    "note": "Detected face is very small — possible partial occlusion",
                }

            return {"detected": False, "note": ""}

        except Exception as e:
            logger.warning(f"Occlusion detection error: {e}")
            return {"detected": False, "note": ""}

    # ── Pose Difference ────────────────────────────────────────────── #

    # ── Pose Difference (MediaPipe 3D) ─────────────────────────────── #

    def _detect_pose_diff(self, live_img: np.ndarray, ref_img: np.ndarray) -> dict:
        """Calculate 3D head pose difference (Pitch, Yaw, Roll) using MediaPipe."""
        try:
            live_pose = self._get_head_pose(live_img)
            ref_pose = self._get_head_pose(ref_img)

            if not live_pose or not ref_pose:
                return {"significant": False, "note": ""}

            # Compare Yaw (Left/Right turn) and Pitch (Up/Down)
            yaw_diff = abs(live_pose["yaw"] - ref_pose["yaw"])
            pitch_diff = abs(live_pose["pitch"] - ref_pose["pitch"])

            # Thresholds: >15 degrees difference is significant
            significant = yaw_diff > 15 or pitch_diff > 15

            note = ""
            if significant:
                if yaw_diff > 15:
                    note = f"Face is turned differently (Yaw diff: {int(yaw_diff)}°)"
                else:
                    note = f"Face is tilted differently (Pitch diff: {int(pitch_diff)}°)"

            return {
                "significant": bool(significant),
                "yaw_diff": float(np.round(yaw_diff, 1)),
                "pitch_diff": float(np.round(pitch_diff, 1)),
                "note": note,
            }
        except Exception as e:
            logger.warning(f"Pose detection error: {e}")
            return {"significant": False, "note": ""}

    def _get_head_pose(self, img: np.ndarray) -> dict | None:
        """Estimate Pitch, Yaw, Roll from 3D Mesh."""
        try:
            if self.face_mesh is None:
                return None

            h, w, c = img.shape
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)

            if not results.multi_face_landmarks:
                return None

            landmarks = results.multi_face_landmarks[0].landmark
            
            # Key points
            nose_tip = landmarks[1]
            left_ear = landmarks[234]
            right_ear = landmarks[454]
            chin = landmarks[152]
            
            # Simple Geometry for Yaw (Left/Right)
            # Compare nose distance to left vs right ear
            left_dist = abs(nose_tip.x - left_ear.x)
            right_dist = abs(nose_tip.x - right_ear.x)
            total_dist = left_dist + right_dist
            
            # Yaw estimate (-90 to +90 approximation)
            # ratio 0.5 = center. 0.0 = full left, 1.0 = full right
            yaw_ratio = (left_dist / total_dist) - 0.5 
            yaw = yaw_ratio * 180.0  # Rough degrees

            # Pitch (Up/Down)
            # Nose vertical position relative to ears/eyes center
            # This is complex without PNP solver, but relative nose-to-chin ratio works
            # For this simple version, we stick to Yaw which is most critical
            
            return {"yaw": yaw, "pitch": 0.0, "roll": 0.0}

        except Exception:
            return None

    def _face_symmetry(self, img: np.ndarray) -> float | None:
        """Compute left-right face symmetry score (0=symmetric, 1=asymmetric)."""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self._face_cascade.detectMultiScale(gray, 1.3, 5)
            if len(faces) == 0:
                return None

            fx, fy, fw, fh = faces[0]
            face = gray[fy:fy+fh, fx:fx+fw]

            mid = fw // 2
            left_half = face[:, :mid]
            right_half = cv2.flip(face[:, mid:2*mid], 1)

            if left_half.shape != right_half.shape:
                min_w = min(left_half.shape[1], right_half.shape[1])
                left_half = left_half[:, :min_w]
                right_half = right_half[:, :min_w]

            if left_half.size == 0:
                return None

            diff = np.mean(np.abs(left_half.astype(float) - right_half.astype(float))) / 255.0
            return diff

        except Exception:
            return None

    # ── Age / Texture Variation ────────────────────────────────────── #

    def _detect_age_variation(self, live_img: np.ndarray, ref_img: np.ndarray) -> dict:
        try:
            live_t = self._texture_score(live_img)
            ref_t = self._texture_score(ref_img)
            diff = abs(live_t - ref_t)
            detected = diff > 0.15

            return {
                "detected": bool(detected),
                "texture_diff": float(np.round(diff, 3)),
                "note": "Possible age difference between images" if detected else "",
            }
        except Exception:
            return {"detected": False, "note": ""}

    def _texture_score(self, img: np.ndarray) -> float:
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            kernel = cv2.getGaborKernel((21, 21), 8.0, np.pi / 4, 10.0, 0.5, 0)
            filtered = cv2.filter2D(gray, cv2.CV_8UC3, kernel)
            return float(filtered.std()) / 128.0
        except Exception:
            return 0.0

    # ── Hair / Baldness Detection ──────────────────────────────────── #

    def _detect_hair_change(self, live_img: np.ndarray, ref_img: np.ndarray) -> dict:
        """Detect significant changes in hair texture (e.g., baldness)."""
        try:
            live_hair = self._hair_texture_score(live_img)
            ref_hair = self._hair_texture_score(ref_img)

            # If face not found or scores invalid
            if live_hair < 0 or ref_hair < 0:
                 return {"detected": False, "note": ""}

            # Heuristic: Hair has high texture. Bald/Skin has lower texture.
            # Thresholds need tuning, but > 10.0 usually implies "Texture Present"
            # Difference > 15.0 implies "State Change"
            
            diff = abs(live_hair - ref_hair)
            detected = diff > 20.0

            note = ""
            if detected:
                if ref_hair > live_hair:
                    note = "Subject appears to have less hair (or is bald) compared to ID"
                else:
                    note = "Subject appears to have different hairstyle/more hair than ID"

            return {
                "detected": bool(detected),
                "hair_diff": float(np.round(diff, 3)),
                "note": note,
            }
        except Exception:
            return {"detected": False, "note": ""}

    def _hair_texture_score(self, img: np.ndarray) -> float:
        """Estimate texture in the upper forehead/hair region."""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self._face_cascade.detectMultiScale(gray, 1.3, 5)
            if len(faces) == 0:
                return -1.0 # Detection failed

            fx, fy, fw, fh = faces[0]
            
            # ROI: Top 25% of the face box (Forehead + Hairline)
            # Expanding slightly upwards might capture more style, 
            # but strictly inside the box is safer for "forehead vs hair"
            y_end = fy + int(fh * 0.25)
            # Clip to image bounds
            y_start = max(0, fy)
            y_end = min(gray.shape[0], y_end)
            
            roi = gray[y_start:y_end, fx:fx+fw]
            if roi.size == 0: 
                return 0.0

            # Calculate variation/texture
            laplacian_var = cv2.Laplacian(roi, cv2.CV_64F).var()
            return float(laplacian_var)

        except Exception:
            return 0.0

    # ── Facial Marks / Scars Detection ─────────────────────────────── #

    def _detect_facial_marks(self, live_img: np.ndarray, ref_img: np.ndarray) -> dict:
        """Detect localized texture anomalies (scars, moles, acne) in cheek regions."""
        try:
            # Resize to standard size for consistent ROI
            target_size = (200, 200)
            live_resized = cv2.resize(live_img, target_size)
            ref_resized = cv2.resize(ref_img, target_size)

            live_score = self._marks_score(live_resized)
            ref_score = self._marks_score(ref_resized)

            diff = abs(live_score - ref_score)
            # Threshold for "significant difference in skin texture/marks"
            detected = diff > 15.0  # Tuned for edge count difference

            return {
                "detected": bool(detected),
                "marks_diff_score": float(np.round(diff, 3)),
                "note": "Distinct facial marks/scars/features detected" if detected else "",
            }
        except Exception:
            return {"detected": False, "note": ""}

    def _marks_score(self, img: np.ndarray) -> float:
        """Calculate edge density specifically in cheek regions."""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Enhance contrast to bring out scars/marks
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Canny edge detection specifically for fine features
            edges = cv2.Canny(enhanced, 80, 150)

            # Define Cheek ROIs (relative to 200x200)
            # Left Cheek: x=30..70, y=90..140
            # Right Cheek: x=130..170, y=90..140
            left_cheek = edges[90:140, 30:70]
            right_cheek = edges[90:140, 130:170]

            # Count edge pixels
            score = np.sum(left_cheek > 0) + np.sum(right_cheek > 0)
            return float(score) / 255.0 # Normalize slightly
        except Exception:
            return 0.0

    # ── Utils ──────────────────────────────────────────────────────── #

    def _bytes_to_cv2(self, image_bytes: bytes) -> np.ndarray:
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception:
            return None


# Singleton
_detector = None


def get_variation_detector() -> VariationDetector:
    global _detector
    if _detector is None:
        _detector = VariationDetector()
    return _detector
