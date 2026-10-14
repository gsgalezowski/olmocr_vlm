#!/usr/bin/env python3
"""Run one-page RolmOCR inference with the native Transformers API."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import torch
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-new-tokens", type=int, default=4096)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("No ROCm GPU is visible to PyTorch")

    device = torch.device("cuda:0")
    started = time.monotonic()
    processor = AutoProcessor.from_pretrained(args.model)
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.model,
        torch_dtype=torch.bfloat16,
        attn_implementation="sdpa",
    ).to(device).eval()
    prompt = "Return the plain text representation of this document as if you were reading it naturally."
    messages = [{"role": "user", "content": [
        {"type": "image", "path": str(args.image)},
        {"type": "text", "text": prompt},
    ]}]
    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(device)
    with torch.inference_mode():
        generated = model.generate(**inputs, max_new_tokens=args.max_new_tokens, do_sample=False)
    text = processor.decode(generated[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
    torch.cuda.synchronize()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text + "\n", encoding="utf-8")
    print(json.dumps({
        "model": str(args.model),
        "image": str(args.image),
        "output": str(args.output),
        "seconds": round(time.monotonic() - started, 3),
        "generated_characters": len(text),
        "max_memory_bytes": torch.cuda.max_memory_allocated(device),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
