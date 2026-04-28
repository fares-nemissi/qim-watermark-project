from __future__ import annotations

import unittest
from pathlib import Path

import cv2

from metrics import compute_ber, compute_psnr
from watermark import EmbeddingConfig, crop_to_block_size, embed_watermark, extract_watermark, generate_watermark


class WatermarkPipelineTests(unittest.TestCase):
    def test_embed_and_extract_without_attack(self) -> None:
        image_path = Path("images/host.png")
        host = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

        self.assertIsNotNone(host, "Host image should be readable.")
        host = crop_to_block_size(host)

        config = EmbeddingConfig(delta=20.0, key=1234, repetitions=12)
        watermark = generate_watermark(size=16, seed=1234)

        watermarked = embed_watermark(host, watermark, config)
        extracted = extract_watermark(watermarked, watermark.shape, config)

        self.assertEqual(compute_ber(watermark, extracted), 0.0)
        self.assertGreater(compute_psnr(host, watermarked), 40.0)


if __name__ == "__main__":
    unittest.main()
