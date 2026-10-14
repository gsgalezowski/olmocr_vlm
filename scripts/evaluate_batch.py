#!/usr/bin/env python3
"""Evaluate a fixed OlmOCR page batch against manual page transcriptions."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import unicodedata
from pathlib import Path


def normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n").strip()


def distance(left: list[str] | str, right: list[str] | str) -> int:
    previous = list(range(len(right) + 1))
    for index, left_item in enumerate(left, 1):
        current = [index]
        for right_index, right_item in enumerate(right, 1):
            current.append(min(
                current[right_index - 1] + 1,
                previous[right_index] + 1,
                previous[right_index - 1] + (left_item != right_item),
            ))
        previous = current
    return previous[-1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--prediction-dir", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--prediction-prefix", default="olmocr2", type=str)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    total_char_edits = total_ref_chars = total_word_edits = total_ref_words = 0
    with args.manifest.open(encoding="utf-8", newline="") as handle:
        for item in csv.DictReader(handle, delimiter="\t"):
            page_id = item["page_id"]
            reference = normalize((args.input_dir / item["reference_name"]).read_text(encoding="utf-8"))
            prediction = normalize((args.prediction_dir / f"{args.prediction_prefix}_page_{page_id}.txt").read_text(encoding="utf-8"))
            char_edits = distance(reference, prediction)
            ref_words, pred_words = reference.split(), prediction.split()
            word_edits = distance(ref_words, pred_words)
            ref_chars, pred_chars = len(reference), len(prediction)
            total_char_edits += char_edits
            total_ref_chars += ref_chars
            total_word_edits += word_edits
            total_ref_words += len(ref_words)
            rows.append({
                "page_id": page_id,
                "ref_chars": ref_chars,
                "pred_chars": pred_chars,
                "length_ratio": round(pred_chars / ref_chars if ref_chars else 0, 6),
                "cer": round(char_edits / ref_chars if ref_chars else 0, 6),
                "wer": round(word_edits / len(ref_words) if ref_words else 0, 6),
            })
    with (args.out_dir / "metrics_per_page.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "pages": len(rows),
        "cer_median": round(statistics.median(float(row["cer"]) for row in rows), 6),
        "wer_median": round(statistics.median(float(row["wer"]) for row in rows), 6),
        "cer_pooled": round(total_char_edits / total_ref_chars, 6),
        "wer_pooled": round(total_word_edits / total_ref_words, 6),
        "length_ratio_median": round(statistics.median(float(row["length_ratio"]) for row in rows), 6),
        "total_reference_characters": total_ref_chars,
        "total_prediction_characters": sum(int(row["pred_chars"]) for row in rows),
    }
    (args.out_dir / "metrics_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
