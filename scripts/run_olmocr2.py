#!/usr/bin/env python3
"""Minimal local inference for the official olmOCR-2 prompt protocol."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import torch
from PIL import Image
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration


PROMPT = """Attached is one page of a document that you must process. Just return the plain text representation of this document as if you were reading it naturally. Convert equations to LateX and tables to HTML. If there are any figures or charts, label them with the following markdown syntax ![Alt text describing the contents of the figure](page_startx_starty_width_height.png)
Return your output as markdown, with a front matter section on top specifying values for the primary_language, is_rotation_valid, rotation_correction, is_table, and is_diagram parameters."""


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
    processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct")
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.model,
        torch_dtype=torch.bfloat16,
    ).to(device).eval()
    image = Image.open(args.image).convert("RGB")
    image.thumbnail((1288, 1288))
    messages = [{"role": "user", "content": [
        {"type": "text", "text": PROMPT},
        {"type": "image", "image": image},
    ]}]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[text], images=[image], padding=True, return_tensors="pt")
    inputs = {key: value.to(device) for key, value in inputs.items()}
    with torch.inference_mode():
        output = model.generate(**inputs, max_new_tokens=args.max_new_tokens, do_sample=False)
    generated = output[:, inputs["input_ids"].shape[1]:]
    transcription = processor.tokenizer.batch_decode(generated, skip_special_tokens=True)[0]
    torch.cuda.synchronize()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(transcription + "\n", encoding="utf-8")
    print(json.dumps({
        "model": str(args.model),
        "image": str(args.image),
        "resized_image": list(image.size),
        "output": str(args.output),
        "seconds": round(time.monotonic() - started, 3),
        "generated_characters": len(transcription),
        "max_memory_bytes": torch.cuda.max_memory_allocated(device),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
