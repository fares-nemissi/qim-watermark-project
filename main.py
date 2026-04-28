from __future__ import annotations

import argparse
from pathlib import Path

import cv2

from attacks import add_gaussian_noise, apply_jpeg_compression
from metrics import compute_ber, compute_psnr
from watermark import EmbeddingConfig, crop_to_block_size, embed_watermark, extract_watermark, generate_watermark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="QIM watermarking demo for 2D grayscale images."
    )
    parser.add_argument(
        "--input",
        default="images/host.png",
        help="Path to the grayscale host image.",
    )
    parser.add_argument(
        "--output-dir",
        default="results",
        help="Folder where generated images and the report will be saved.",
    )
    parser.add_argument(
        "--watermark-size",
        type=int,
        default=16,
        help="Size of the square binary watermark.",
    )
    parser.add_argument(
        "--delta",
        type=float,
        default=20.0,
        help="QIM quantization step.",
    )
    parser.add_argument(
        "--key",
        type=int,
        default=1234,
        help="Secret key used to choose embedding blocks.",
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=12,
        help="How many blocks will store the same watermark bit.",
    )
    parser.add_argument(
        "--noise-sigma",
        type=float,
        default=0.25,
        help="Standard deviation for Gaussian noise.",
    )
    parser.add_argument(
        "--jpeg-quality",
        type=int,
        default=80,
        help="JPEG quality factor between 0 and 100.",
    )
    return parser.parse_args()


def load_grayscale_image(image_path: Path):
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")
    return image


def save_binary_watermark(path: Path, watermark):
    cv2.imwrite(str(path), (watermark * 255).astype("uint8"))


def write_report(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    config = EmbeddingConfig(delta=args.delta, key=args.key, repetitions=args.repetitions)
    host_image = load_grayscale_image(input_path)
    host_image = crop_to_block_size(host_image, config.block_size)
    watermark = generate_watermark(size=args.watermark_size, seed=args.key)

    watermarked = embed_watermark(host_image, watermark, config)
    extracted_clean = extract_watermark(watermarked, watermark.shape, config)

    attacked_noise = add_gaussian_noise(watermarked, sigma=args.noise_sigma, seed=args.key)
    extracted_noise = extract_watermark(attacked_noise, watermark.shape, config)

    attacked_jpeg = apply_jpeg_compression(watermarked, quality=args.jpeg_quality)
    attacked_jpeg = crop_to_block_size(attacked_jpeg, config.block_size)
    extracted_jpeg = extract_watermark(attacked_jpeg, watermark.shape, config)

    cv2.imwrite(str(output_dir / "host_cropped.png"), host_image)
    cv2.imwrite(str(output_dir / "watermarked.png"), watermarked)
    cv2.imwrite(str(output_dir / "attacked_noise.png"), attacked_noise)
    cv2.imwrite(str(output_dir / "attacked_jpeg.png"), attacked_jpeg)
    save_binary_watermark(output_dir / "watermark_reference.png", watermark)
    save_binary_watermark(output_dir / "extracted_clean.png", extracted_clean)
    save_binary_watermark(output_dir / "extracted_noise.png", extracted_noise)
    save_binary_watermark(output_dir / "extracted_jpeg.png", extracted_jpeg)

    psnr_value = compute_psnr(host_image, watermarked)
    ber_clean = compute_ber(watermark, extracted_clean)
    ber_noise = compute_ber(watermark, extracted_noise)
    ber_jpeg = compute_ber(watermark, extracted_jpeg)

    report_lines = [
        "QIM WATERMARKING REPORT",
        f"Input image: {input_path}",
        f"Host size after cropping: {host_image.shape[1]}x{host_image.shape[0]}",
        f"Watermark size: {watermark.shape[1]}x{watermark.shape[0]}",
        f"QIM delta: {args.delta}",
        f"Secret key: {args.key}",
        f"Bit repetitions: {args.repetitions}",
        f"Noise sigma: {args.noise_sigma}",
        f"JPEG quality: {args.jpeg_quality}",
        "",
        f"PSNR(host, watermarked): {psnr_value:.4f} dB",
        f"BER(clean extraction): {ber_clean:.4f}",
        f"BER(after Gaussian noise): {ber_noise:.4f}",
        f"BER(after JPEG compression): {ber_jpeg:.4f}",
    ]
    write_report(output_dir / "report.txt", report_lines)

    print("\n".join(report_lines))


if __name__ == "__main__":
    main()
