"""Small data audit helper; no Django/database required."""
import csv
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'backend'))
from reconciler.services.comparator import reconcile_records

with (ROOT / 'data/system_a.csv').open(encoding='utf-8', newline='') as f:
    a = list(csv.DictReader(f))
with (ROOT / 'data/system_b.csv').open(encoding='utf-8', newline='') as f:
    b = list(csv.DictReader(f))
with (ROOT / 'data/locations.csv').open(encoding='utf-8', newline='') as f:
    locations = list(csv.DictReader(f))

org_map = {r['location_id']: r['org_id'] for r in locations}
for row in a:
    row['total_value_raw'] = row.get('total_value', '')
for row in b:
    row['value_raw'] = row.get('value', '')

results = reconcile_records(a, b, org_map)
print(f'System A rows: {len(a)}')
print(f'System B rows: {len(b)}')
print(f'Locations: {len(locations)}')
print(f'Discrepancies: {len(results)}')
print(dict(Counter(r.reason for r in results)))
