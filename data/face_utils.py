"""Face detection, alignment, cropping, quality, and skin-tone (ITA) utilities.

Detector: MTCNN (facenet-pytorch). Swap `get_detector()` if you prefer RetinaFace.
All functions operate on RGB numpy arrays (H, W, 3), uint8.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

import numpy as np

try:  # heavy imports are lazy-friendly so the module imports even without them
    import cv2
except Exception:  # pragma: no cover
    cv2 = None


@lru_cache(maxsize=1)
def get_detector(device: str = "cpu"):
    """Return a cached MTCNN detector. Requires facenet-pytorch + torch."""
    from facenet_pytorch import MTCNN
    return MTCNN(keep_all=True, post_process=False, device=device)


def detect_faces(rgb: np.ndarray, device: str = "cpu"):
    """Return (boxes, probs, landmarks). boxes: Nx4 [x1,y1,x2,y2] or None."""
    from PIL import Image
    det = get_detector(device)
    boxes, probs, landmarks = det.detect(Image.fromarray(rgb), landmarks=True)
    return boxes, probs, landmarks


def align_and_crop(rgb: np.ndarray, landmarks: np.ndarray, size: int = 224,
                   margin: float = 0.35) -> np.ndarray:
    """Eye-align a face by rotating so the eyes are horizontal, then center-crop.

    landmarks: 5x2 MTCNN points [left_eye, right_eye, nose, mouth_l, mouth_r].
    """
    if cv2 is None:
        raise RuntimeError("opencv is required for align_and_crop")
    left_eye, right_eye = landmarks[0], landmarks[1]
    dy, dx = (right_eye[1] - left_eye[1]), (right_eye[0] - left_eye[0])
    angle = np.degrees(np.arctan2(dy, dx))
    eyes_center = tuple(((left_eye + right_eye) / 2).astype(float))
    M = cv2.getRotationMatrix2D(eyes_center, angle, 1.0)
    rotated = cv2.warpAffine(rgb, M, (rgb.shape[1], rgb.shape[0]),
                             flags=cv2.INTER_CUBIC)
    eye_dist = np.linalg.norm(right_eye - left_eye)
    half = int(eye_dist * (1.0 + margin) * 1.6)
    cx, cy = int(eyes_center[0]), int(eyes_center[1] + eye_dist * 0.3)
    x1, y1 = max(cx - half, 0), max(cy - half, 0)
    x2, y2 = min(cx + half, rotated.shape[1]), min(cy + half, rotated.shape[0])
    crop = rotated[y1:y2, x1:x2]
    if crop.size == 0:
        crop = rgb
    return cv2.resize(crop, (size, size), interpolation=cv2.INTER_CUBIC)


def quality_score(rgb: np.ndarray) -> float:
    """Cheap 0..1 quality score from Laplacian sharpness + brightness sanity."""
    if cv2 is None:
        return 0.0
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    sharp = cv2.Laplacian(gray, cv2.CV_64F).var()
    sharp_score = float(np.clip(sharp / 500.0, 0, 1))
    mean = gray.mean()
    bright_score = float(np.clip(1.0 - abs(mean - 128) / 128.0, 0, 1))
    return round(0.7 * sharp_score + 0.3 * bright_score, 4)


def estimate_ita(rgb: np.ndarray, mask: Optional[np.ndarray] = None) -> float:
    """Individual Typology Angle (degrees) over skin pixels.

    ITA = arctan((L* - 50) / b*) * 180/pi, in CIE Lab. Higher = lighter skin.
    If `mask` is None, uses a central face region and a simple skin heuristic.
    """
    if cv2 is None:
        return float("nan")
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    L = lab[..., 0] * 100.0 / 255.0
    b = lab[..., 2] - 128.0
    if mask is None:
        h, w = rgb.shape[:2]
        mask = np.zeros((h, w), bool)
        mask[int(h * 0.35):int(h * 0.65), int(w * 0.3):int(w * 0.7)] = True
        # crude skin gate in YCrCb to drop hair/background
        ycrcb = cv2.cvtColor(rgb, cv2.COLOR_RGB2YCrCb)
        cr, cb = ycrcb[..., 1], ycrcb[..., 2]
        skin = (cr > 135) & (cr < 180) & (cb > 85) & (cb < 135)
        mask &= skin
    if mask.sum() < 50:
        return float("nan")
    Lm, bm = L[mask], b[mask]
    bm = np.where(np.abs(bm) < 1e-3, 1e-3, bm)
    ita = np.degrees(np.arctan2(Lm - 50.0, bm))
    return float(np.median(ita))
