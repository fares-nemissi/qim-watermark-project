from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.fft import dctn, idctn


BLOCK_SIZE = 8
DEFAULT_COEFFICIENT_PAIR = ((1, 2), (2, 1))


@dataclass(frozen=True)
class EmbeddingConfig:
    delta: float = 20.0
    key: int = 1234
    block_size: int = BLOCK_SIZE
    coefficient_pair: tuple[tuple[int, int], tuple[int, int]] = DEFAULT_COEFFICIENT_PAIR
    repetitions: int = 12


def crop_to_block_size(image: np.ndarray, block_size: int = BLOCK_SIZE) -> np.ndarray:
    height, width = image.shape
    cropped_height = height - (height % block_size)
    cropped_width = width - (width % block_size)
    return image[:cropped_height, :cropped_width]


def generate_watermark(size: int = 32, seed: int = 1234) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, 2, size=(size, size), dtype=np.uint8)


def _block_count(image_shape: tuple[int, int], block_size: int) -> tuple[int, int, int]:
    height, width = image_shape
    blocks_y = height // block_size
    blocks_x = width // block_size
    return blocks_y, blocks_x, blocks_y * blocks_x


def _choose_block_indices(total_blocks: int, bit_count: int, key: int) -> np.ndarray:
    if bit_count > total_blocks:
        raise ValueError(
            f"Watermark has {bit_count} bits but the image only has {total_blocks} blocks."
        )

    rng = np.random.default_rng(key)
    return rng.choice(total_blocks, size=bit_count, replace=False)


def _dct2(block: np.ndarray) -> np.ndarray:
    return dctn(block, type=2, norm="ortho")


def _idct2(block: np.ndarray) -> np.ndarray:
    return idctn(block, type=2, norm="ortho")


def _embed_bit_in_value(value: float, bit: int, delta: float) -> float:
    quantization_index = int(round(value / delta))
    if (quantization_index & 1) != int(bit):
        lower_index = quantization_index - 1
        upper_index = quantization_index + 1
        lower_distance = abs(value - (lower_index * delta))
        upper_distance = abs(value - (upper_index * delta))
        quantization_index = lower_index if lower_distance <= upper_distance else upper_index
    return float(quantization_index * delta)


def _extract_bit_from_value(value: float, delta: float) -> int:
    return int(round(value / delta)) & 1


def embed_watermark(
    image: np.ndarray,
    watermark: np.ndarray,
    config: EmbeddingConfig,
) -> np.ndarray:
    working_image = crop_to_block_size(image, config.block_size).astype(np.float32).copy()
    flat_bits = watermark.flatten()
    blocks_y, blocks_x, total_blocks = _block_count(working_image.shape, config.block_size)
    chosen_blocks = _choose_block_indices(
        total_blocks, flat_bits.size * config.repetitions, config.key
    )
    (row_a, col_a), (row_b, col_b) = config.coefficient_pair

    for bit_index, bit in enumerate(flat_bits):
        start = bit_index * config.repetitions
        end = start + config.repetitions
        for block_index in chosen_blocks[start:end]:
            block_y = (block_index // blocks_x) * config.block_size
            block_x = (block_index % blocks_x) * config.block_size
            block = working_image[
                block_y : block_y + config.block_size,
                block_x : block_x + config.block_size,
            ]
            transformed = _dct2(block)
            difference = transformed[row_a, col_a] - transformed[row_b, col_b]
            target_difference = _embed_bit_in_value(difference, int(bit), config.delta)
            adjustment = (target_difference - difference) / 2.0
            transformed[row_a, col_a] += adjustment
            transformed[row_b, col_b] -= adjustment
            working_image[
                block_y : block_y + config.block_size,
                block_x : block_x + config.block_size,
            ] = _idct2(transformed)

    return np.clip(np.rint(working_image), 0, 255).astype(np.uint8)


def extract_watermark(
    image: np.ndarray,
    watermark_shape: tuple[int, int],
    config: EmbeddingConfig,
) -> np.ndarray:
    working_image = crop_to_block_size(image, config.block_size).astype(np.float32)
    bit_count = math.prod(watermark_shape)
    _, blocks_x, total_blocks = _block_count(working_image.shape, config.block_size)
    chosen_blocks = _choose_block_indices(
        total_blocks, bit_count * config.repetitions, config.key
    )
    (row_a, col_a), (row_b, col_b) = config.coefficient_pair
    extracted_bits = np.zeros(bit_count, dtype=np.uint8)

    for output_index in range(bit_count):
        start = output_index * config.repetitions
        end = start + config.repetitions
        votes = []

        for block_index in chosen_blocks[start:end]:
            block_y = (block_index // blocks_x) * config.block_size
            block_x = (block_index % blocks_x) * config.block_size
            block = working_image[
                block_y : block_y + config.block_size,
                block_x : block_x + config.block_size,
            ]
            transformed = _dct2(block)
            difference = transformed[row_a, col_a] - transformed[row_b, col_b]
            votes.append(_extract_bit_from_value(difference, config.delta))

        extracted_bits[output_index] = 1 if sum(votes) > (config.repetitions / 2) else 0

    return extracted_bits.reshape(watermark_shape)
