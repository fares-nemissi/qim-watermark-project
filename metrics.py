from __future__ import annotations

import numpy as np
from skimage.metrics import peak_signal_noise_ratio


def compute_psnr(reference_image: np.ndarray, test_image: np.ndarray) -> float:
    return float(peak_signal_noise_ratio(reference_image, test_image, data_range=255))


def compute_ber(reference_watermark: np.ndarray, test_watermark: np.ndarray) -> float:
    total_bits = reference_watermark.size
    if total_bits == 0:
        raise ValueError("BER cannot be computed with an empty watermark.")

    different_bits = np.count_nonzero(reference_watermark != test_watermark)
    return float(different_bits / total_bits)
