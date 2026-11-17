"""
scripts/prepare_dataset.py

Real, working utility that generates damaged/masked training pairs from
clean transcriptions, for training or evaluating the reconstruction module.
Requires only the Python standard library.

Usage:
    python scripts/prepare_dataset.py \
        --input data/reconstruction/original \
        --output data/reconstruction/damaged \
        --mask-rate 0.15
"""
import argparse
import os
import random


def mask_text(text: str, mask_rate: float, marker: str = "[?]") -> str:
    """Randomly masks characters (missing-character damage simulation)."""
    chars = list(text)
    for i, ch in enumerate(chars):
        if ch.strip() and random.random() < mask_rate:
            chars[i] = marker
    return "".join(chars)


def mask_contiguous_span(text: str, min_len: int = 1, max_len: int = 3) -> str:
    """Simulates a contiguous damaged/blurred region (e.g. a crack)."""
    if len(text) <= min_len:
        return text
    span_len = random.randint(min_len, min(max_len, len(text)))
    start = random.randint(0, len(text) - span_len)
    return text[:start] + "_" * span_len + text[start + span_len :]


def process_directory(input_dir: str, output_dir: str, mask_rate: float, strategy: str):
    os.makedirs(output_dir, exist_ok=True)
    count = 0
    for fname in os.listdir(input_dir):
        if not fname.endswith(".txt"):
            continue
        with open(os.path.join(input_dir, fname), encoding="utf-8") as f:
            text = f.read().strip()

        if strategy == "random":
            damaged = mask_text(text, mask_rate)
        elif strategy == "span":
            damaged = mask_contiguous_span(text)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        with open(os.path.join(output_dir, fname), "w", encoding="utf-8") as f:
            f.write(damaged)
        count += 1

    print(f"Processed {count} file(s) from {input_dir} -> {output_dir} (strategy={strategy})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate damaged-text training pairs.")
    parser.add_argument("--input", default="data/reconstruction/original")
    parser.add_argument("--output", default="data/reconstruction/damaged")
    parser.add_argument("--mask-rate", type=float, default=0.15)
    parser.add_argument("--strategy", choices=["random", "span"], default="random")
    args = parser.parse_args()

    if not os.path.isdir(args.input):
        print(f"Input directory not found: {args.input}")
        print("Add clean, verified transcriptions there first (see docs/datasets.md).")
    else:
        process_directory(args.input, args.output, args.mask_rate, args.strategy)
