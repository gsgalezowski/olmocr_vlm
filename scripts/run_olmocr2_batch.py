#!/usr/bin/env python3
"""Run the official olmOCR-2 protocol on a fixed, auditable page batch."""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import torch
from PIL import Image
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

from run_olmocr2 import PROMPT


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--max-new-tokens", type=int, default=4096)
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("No ROCm GPU is visible to PyTorch")

    device = torch.device("cuda:0")
    processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct")
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.model,
        torch_dtype=torch.bfloat16,
    ).to(device).eval()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    with args.manifest.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            page_id = row["page_id"]
            image = Image.open(args.input_dir / row["image_name"]).convert("RGB")
            image.thumbnail((1288, 1288))
            messages = [{"role": "user", "content": [
                {"type": "text", "text": PROMPT},
                {"type": "image", "image": image},
            ]}]
            prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = processor(text=[prompt], images=[image], padding=True, return_tensors="pt")
            inputs = {key: value.to(device) for key, value in inputs.items()}
            started = time.monotonic()
            with torch.inference_mode():
                output = model.generate(**inputs, max_new_tokens=args.max_new_tokens, do_sample=False)
            torch.cuda.synchronize()
            generated = output[:, inputs["input_ids"].shape[1]:]
            transcription = processor.tokenizer.batch_decode(generated, skip_special_tokens=True)[0]
            output_path = args.output_dir / f"olmocr2_page_{page_id}.txt"
            output_path.write_text(transcription + "\n", encoding="utf-8")
            rows.append({
                "page_id": page_id,
                "image": row["image_name"],
                "reference": row["reference_name"],
                "prediction": output_path.name,
                "image_size": list(image.size),
                "seconds": round(time.monotonic() - started, 3),
                "generated_characters": len(transcription),
                "max_memory_bytes": torch.cuda.max_memory_allocated(device),
            })
            print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
