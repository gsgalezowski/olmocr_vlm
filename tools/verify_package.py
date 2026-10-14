"""Verify package integrity and numerical consistency without GPU dependencies."""
from pathlib import Path
import ast, csv, hashlib, json, statistics

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'FILE_MANIFEST.json').read_text(encoding='utf-8'))
for entry in manifest:
    path = root / entry['path']
    assert path.stat().st_size == entry['bytes'], entry['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'], entry['path']
for path in root.rglob('*.py'):
    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
conditions = 0
for folder in sorted((root / 'results').glob('*_evaluation')):
    with (folder / 'metrics_per_page.csv').open(encoding='utf-8', newline='') as h:
        rows = list(csv.DictReader(h))
    summary = json.loads((folder / 'metrics_summary.json').read_text())
    assert len(rows) == summary['pages'], folder.name
    refs = sum(int(r['ref_chars']) for r in rows)
    pooled = sum(float(r['cer']) * int(r['ref_chars']) for r in rows) / refs
    assert abs(pooled - summary['cer_pooled']) <= 0.000002, folder.name
    if 'cer_median' in summary:
        assert abs(statistics.median(float(r['cer']) for r in rows) - summary['cer_median']) <= 0.000002
        assert refs == summary['total_reference_characters']
        assert sum(int(r['pred_chars']) for r in rows) == summary['total_prediction_characters']
        assert abs(statistics.median(float(r['wer']) for r in rows) - summary['wer_median']) <= 0.000002
    conditions += 1
assert conditions == 4
print(f'PASS: {len(manifest)} file hashes, Python syntax, and {conditions} evaluation tables. No inference rerun.')
