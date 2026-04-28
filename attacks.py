from __future__ import annotations

import cv2
import numpy as np


def add_gaussian_noise(image: np.ndarray, sigma: float = 7.0, seed: int = 2026) -> np.ndarray:
    rng = np.random.default_rng(seed)
    noise = rng.normal(loc=0.0, scale=sigma, size=image.shape)
    attacked = image.astype(np.float32) + noise
    return np.clip(np.rint(attacked), 0, 255).astype(np.uint8)


def apply_jpeg_compression(image: np.ndarray, quality: int = 50) -> np.ndarray:
    success, encoded = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not success:
        raise RuntimeError("JPEG compression failed.")

    decoded = cv2.imdecode(encoded, cv2.IMREAD_GRAYSCALE)
    if decoded is None:
        raise RuntimeError("JPEG decompression failed.")

    return decoded
