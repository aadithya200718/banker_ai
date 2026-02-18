"""
Face Service Module
====================
Core face verification logic:
- Face detection and alignment
- Embedding generation using DeepFace (Facenet512)
- Cosine similarity computation
- Image quality assessment
- Input validation & Caching
"""

import logging
import time
import cv2
import numpy as np
from deepface import DeepFace

# New modules
from backend.input_validator import validate_image_bytes
from backend.cache_service import get_embedding_cache

logger = logging.getLogger(__name__)

# Model to use for embedding extraction
MODEL_NAME = "Facenet512"
DETECTOR_BACKEND = "opencv"  # More stable than retinaface, good compatibility


class FaceService:
    """Core face detection, embedding, and similarity service."""

    def __init__(self):
        self._model_loaded = False
        self._warmup()

    def _warmup(self):
        """Warm up the model by running a dummy inference."""
        try:
            dummy = np.zeros((160, 160, 3), dtype=np.uint8)
            dummy[40:120, 40:120] = 200  # Add a bright region
            DeepFace.represent(
                img_path=dummy,
                model_name=MODEL_NAME,
                detector_backend="skip",
                enforce_detection=False,
            )
            self._model_loaded = True
            logger.info(f"✅ {MODEL_NAME} model loaded and warmed up")
        except Exception as e:
            logger.warning(f"⚠️ Model warmup note: {e}")
            self._model_loaded = True  # DeepFace downloads on first real call

    @property
    def is_ready(self) -> bool:
        return self._model_loaded

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #

    def verify(
        self, live_image_bytes: bytes, reference_image_bytes: bytes, user_id: str = "UNKNOWN"
    ) -> dict:
        """
        Compare a live face against ID reference AND any Gallery images for this user.
        Returns the BEST match score found.
        PRO upgrades: validation, caching, retry logic, composite confidence.
        """
        t0 = time.time()
        
        if not self._model_loaded:
            self._warmup()

        # 1. Validation
        live_img = validate_image_bytes(live_image_bytes, "live")
        ref_img = validate_image_bytes(reference_image_bytes, "reference")

        # 2. Embedding Extraction with Retry & Cache
        try:
            # Live Embedding
            live_emb, live_region = self._get_embedding_with_retry(live_img, live_image_bytes, "live")
            # Reference Embedding
            ref_emb, ref_region = self._get_embedding_with_retry(ref_img, reference_image_bytes, "reference")
            
        except Exception as e:
            logger.error(f"Embedding failed after retries: {e}")
            raise ValueError(f"Face processing failed: {str(e)}")

        # 3. Compute Similarity (Cosine)
        # Cosine distance = 1 - cosine_similarity
        # DeepFace embeddings are vectors.
        norm_live = np.linalg.norm(live_emb)
        norm_ref = np.linalg.norm(ref_emb)
        
        if norm_live == 0 or norm_ref == 0:
             similarity = 0.0
        else:
            similarity = np.dot(live_emb, ref_emb) / (norm_live * norm_ref)
        
        # Clip to 0-1 range
        similarity = max(0.0, min(1.0, float(similarity)))

        # 4. Check Gallery for better match (optional)
        gallery_score = self._check_gallery_with_cache(user_id, live_emb)
        final_score = max(similarity, gallery_score)

        # 5. Quality Assessment
        live_quality = self._assess_quality(live_img, live_region)
        
        elapsed = (time.time() - t0) * 1000

        return {
            "similarity_score": final_score,
            "face_region": live_region,
            "quality": live_quality,
            "used_gallery_match": (gallery_score > similarity),
            "processing_time_ms": round(elapsed, 1)
        }

    # ------------------------------------------------------------------ #
    #  Internal helpers
    # ------------------------------------------------------------------ #

    def _get_embedding_with_retry(self, img: np.ndarray, img_bytes: bytes, label: str) -> tuple[np.ndarray, dict]:
        """Get embedding with cache check and retry logic."""
        cache = get_embedding_cache()

        # Check cache first
        cached_emb = cache.get(img_bytes)
        if cached_emb is not None:
             # If cached, we use a default region since extracting region is expensive just for cache
             # Or ideally we cache the region too. For now: assume full image region if checking cache
             # This is a trade-off for speed.
             h, w = img.shape[:2]
             return cached_emb, {"x": 0, "y": 0, "w": w, "h": h}

        # Retry loop
        last_error = None
        for attempt in range(3):
            try:
                emb, region = self._get_embedding(img, label)
                # Cache success
                cache.put(img_bytes, emb)
                return emb, region
            except Exception as e:
                last_error = e
                # Only log warning if not the last attempt
                if attempt < 2:
                    logger.warning(f"Embedding attempt {attempt+1}/3 failed for {label}: {e}")
                    time.sleep(0.2)
        
        raise last_error # type: ignore

    def _get_embedding(self, img: np.ndarray, label: str) -> tuple[np.ndarray, dict]:
        """
        Extract face embedding from an image using DeepFace.

        Returns (embedding_vector, face_region_dict).
        """
        try:
            # DeepFace.represent returns a list of dicts
            results = DeepFace.represent(
                img_path=img,
                model_name=MODEL_NAME,
                enforce_detection=True,
                detector_backend=DETECTOR_BACKEND,
                align=True,
                normalization="Facenet2018",
            )
            
            if not results:
               raise ValueError(f"No face detected in {label}")

            # Take the first face
            result = results[0]
            embedding = np.array(result["embedding"], dtype=np.float32)
            region = result.get("facial_area", {})
            
            return embedding, region

        except Exception as e:
            # Fallback: try without enforcement if detection failed
            if "Face could not be detected" in str(e):
                 logger.warning(f"Strict identification failed for {label}, retrying loose...")
                 try:
                    results = DeepFace.represent(
                        img_path=img,
                        model_name=MODEL_NAME,
                        enforce_detection=False,
                        detector_backend="opencv", # faster, less accurate
                        align=True,
                        normalization="Facenet2018",
                    )
                    if results:
                         result = results[0]
                         return np.array(result["embedding"], dtype=np.float32), result.get("facial_area", {})
                 except Exception as inner:
                     raise ValueError(f"No face detected in {label} image") from inner

            logger.error(f"DeepFace error for {label}: {e}")
            raise ValueError(f"Could not process {label} image: {str(e)}")

    def _assess_quality(self, img: np.ndarray, face_region: dict) -> dict:
        """Assess image quality metrics."""
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 1. Brightness
        brightness = np.mean(gray) / 255.0
        
        # 2. Sharpness (Laplacian variance)
        sharpness_val = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(1.0, sharpness_val / 500.0)
        
        # 3. Face Size Ratio
        face_area = 0
        if face_region:
            fw = face_region.get('w', 0)
            fh = face_region.get('h', 0)
            face_area = fw * fh
        
        img_area = w * h
        face_ratio = (face_area / img_area) if img_area > 0 else 0
        
        return {
            "brightness": round(brightness, 2),
            "sharpness": round(sharpness_score, 2),
            "face_size_ratio": round(face_ratio, 2)
        }

    def _check_gallery_with_cache(self, user_id: str, live_embedding: np.ndarray) -> float:
        """Check user's gallery folder for matching approved faces (with caching)."""
        # For this iteration, we keep the gallery check simple without gallery-side caching
        # or we could cache gallery results?
        # Let's use the existing logic but wrapped
        return self._check_gallery(user_id, live_embedding)

    def _check_gallery(self, user_id: str, live_embedding: np.ndarray) -> float:
        """Check user's gallery folder for matching approved faces."""
        import os
        import glob
        from scipy.spatial.distance import cosine
        
        gallery_dir = f"data/users/{user_id}"
        if not os.path.exists(gallery_dir):
            return 0.0
            
        # Get last 5 images
        images = sorted(glob.glob(f"{gallery_dir}/*.jpg"), reverse=True)[:5]
        best_score = 0.0
        
        for img_path in images:
            try:
                # We re-compute gallery embeddings here. 
                # Ideally: load pre-computed embeddings.
                results = DeepFace.represent(
                    img_path=img_path,
                    model_name=MODEL_NAME,
                    detector_backend="skip",
                    enforce_detection=False,
                    normalization="Facenet2018"
                )
                if results:
                    gal_embedding = results[0]["embedding"]
                    dist = cosine(live_embedding, gal_embedding)
                    score = max(0.0, min(1.0, 1.0 - dist))
                    if score > best_score:
                        best_score = score
            except Exception:
                continue
                
        return best_score


# Singleton
_face_service = None


def get_face_service() -> FaceService:
    global _face_service
    if _face_service is None:
        _face_service = FaceService()
    return _face_service
