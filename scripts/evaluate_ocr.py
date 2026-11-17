"""
scripts/evaluate_ocr.py

Computes Character Error Rate (CER), Word Error Rate (WER), and exact-match
rate for the configured OCR provider against ground-truth transcriptions in
data/ocr/transcriptions/. Pure Python (Levenshtein distance) — no extra
dependencies beyond the backend app itself.

Usage:
    python scripts/evaluate_ocr.py --images data/ocr/images --gt data/ocr/transcriptions
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


def levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            curr[j] = min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost)
        prev = curr
    return prev[-1]


def cer(reference: str, hypothesis: str) -> float:
    if not reference:
        return 0.0 if not hypothesis else 1.0
    return levenshtein(reference, hypothesis) / len(reference)


def wer(reference: str, hypothesis: str) -> float:
    ref_words, hyp_words = reference.split(), hypothesis.split()
    if not ref_words:
        return 0.0 if not hyp_words else 1.0
    return levenshtein_words(ref_words, hyp_words) / len(ref_words)


def levenshtein_words(a: list[str], b: list[str]) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, wa in enumerate(a, 1):
        curr = [i] + [0] * len(b)
        for j, wb in enumerate(b, 1):
            cost = 0 if wa == wb else 1
            curr[j] = min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost)
        prev = curr
    return prev[-1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", default="data/ocr/images")
    parser.add_argument("--gt", default="data/ocr/transcriptions")
    parser.add_argument("--demo", action="store_true", help="Use the demo OCR provider (default if no real provider configured)")
    args = parser.parse_args()

    if not os.path.isdir(args.images) or not os.path.isdir(args.gt):
        print(f"Expected image dir {args.images} and ground-truth dir {args.gt}.")
        print("Populate them first — see docs/datasets.md.")
        return

    from app.ocr.providers import get_ocr_provider

    provider = get_ocr_provider(use_demo=args.demo)
    print(f"Evaluating provider: {provider.__class__.__name__}")

    cers, wers, exact = [], [], 0
    n = 0
    for fname in sorted(os.listdir(args.images)):
        base, _ = os.path.splitext(fname)
        gt_path = os.path.join(args.gt, base + ".txt")
        if not os.path.exists(gt_path):
            continue
        with open(gt_path, encoding="utf-8") as f:
            reference = f.read().strip()

        result = provider.extract_text(os.path.join(args.images, fname))
        hypothesis = result.text.strip()

        c = cer(reference, hypothesis)
        w = wer(reference, hypothesis)
        cers.append(c)
        wers.append(w)
        exact += int(reference == hypothesis)
        n += 1
        print(f"{fname}: CER={c:.3f} WER={w:.3f}")

    if n == 0:
        print("No matching image/ground-truth pairs found.")
        return

    print("\n--- Summary ---")
    print(f"Samples evaluated: {n}")
    print(f"Mean CER: {sum(cers) / n:.3f}")
    print(f"Mean WER: {sum(wers) / n:.3f}")
    print(f"Exact match rate: {exact / n:.3f}")


if __name__ == "__main__":
    main()
