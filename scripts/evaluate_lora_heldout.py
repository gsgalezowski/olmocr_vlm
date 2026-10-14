from pathlib import Path
import csv
import json
import unicodedata

def norm(value):
    return unicodedata.normalize("NFC", value).replace("\r\n", "\n").strip()

def dist(a, b):
    prior = list(range(len(b) + 1))
    for i, left in enumerate(a, 1):
        current = [i]
        for j, right in enumerate(b, 1):
            current.append(min(current[j - 1] + 1, prior[j] + 1, prior[j - 1] + (left != right)))
        prior = current
    return prior[-1]

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--prediction-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for page in ("19", "29"):
        ref = norm((args.input_dir / f"{page}.md").read_text(encoding="utf-8"))
        pred = norm((args.prediction_dir / f"olmocr2_page_{page}.txt").read_text(encoding="utf-8"))
        rows.append({"page_id": page, "ref_chars": len(ref), "pred_chars": len(pred), "cer": round(dist(ref, pred) / len(ref), 6)})
    with (args.out_dir / "metrics_per_page.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    result = {"pages": len(rows), "cer_pooled": round(sum(dist(norm((args.input_dir / f"{r['page_id']}.md").read_text(encoding="utf-8")), norm((args.prediction_dir / f"olmocr2_page_{r['page_id']}.txt").read_text(encoding="utf-8"))) for r in rows) / sum(r["ref_chars"] for r in rows), 6)}
    (args.out_dir / "metrics_summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))

if __name__ == "__main__":
    main()
