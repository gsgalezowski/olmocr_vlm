#!/usr/bin/env python3
"""Decode validation PDF pages with the tested olmOCR LoRA adapter."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pypdfium2 as pdfium
import torch
from peft import PeftModel
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration


PROMPT = """Attached is one page of a document that you must process. Just return the plain text representation of this document as if you were reading it naturally. Convert equations to LateX and tables to HTML. If there are any figures or charts, label them with the following markdown syntax ![Alt text describing the contents of the figure](page_startx_starty_width_height.png)
Return your output as markdown, with a front matter section on top specifying values for the primary_language, is_rotation_valid, rotation_correction, is_table, and is_diagram parameters."""


def render(pdf_path: Path):
    document = pdfium.PdfDocument(pdf_path)
    image = document[0].render(scale=2).to_pil().convert("RGB")
    image.thumbnail((1288, 1288))
    return image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--adapter", type=Path)
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--page", action="append", required=True)
    args = parser.parse_args()

    device = torch.device("cuda:0")
    processor = AutoProcessor.from_pretrained(args.model, local_files_only=True)
    base_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.model, torch_dtype=torch.bfloat16, local_files_only=True
    ).to(device).eval()
    model = PeftModel.from_pretrained(base_model, args.adapter).eval() if args.adapter else base_model
    args.output_dir.mkdir(parents=True, exist_ok=True)
    runtimes = []
    for page_id in args.page:
        image = render(args.input_dir / f"{page_id}.pdf")
        messages = [{"role": "user", "content": [
            {"type": "text", "text": PROMPT}, {"type": "image", "image": image},
        ]}]
        prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[prompt], images=[image], padding=True, return_tensors="pt")
        inputs = {key: value.to(device) for key, value in inputs.items()}
        started = time.monotonic()
        with torch.inference_mode():
            output = model.generate(**inputs, max_new_tokens=4096, do_sample=False)
        generated = output[:, inputs["input_ids"].shape[1]:]
        text = processor.tokenizer.batch_decode(generated, skip_special_tokens=True)[0]
        (args.output_dir / f"olmocr2_page_{page_id}.txt").write_text(text + "\n", encoding="utf-8")
        runtimes.append({"page_id": page_id, "seconds": round(time.monotonic() - started, 3), "characters": len(text)})
    (args.output_dir / "runtime.json").write_text(json.dumps(runtimes, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
