import re
from collections import defaultdict
from dataclasses import dataclass, asdict
from decimal import Decimal, InvalidOperation
from typing import Any


MISSING = {'', 'N/A', 'NULL', 'NONE', '-', 'NAN', '########'}


def normalize_reference(value: Any) -> str:
    """Canonicalize dirty references while retaining raw values elsewhere."""
    if value is None:
        return ''
    canonical = re.sub(r'[^a-zA-Z0-9]', '', str(value)).lower()
    # Numeric-only exports such as `1112` are treated as shorthand for `REC-1112`.
    if canonical.isdigit():
        canonical = f'rec{canonical}'
    return canonical


def safe_decimal(value: Any) -> Decimal | None:
    """Parse numeric exports defensively; return None for non-numeric/missing values."""
    if value is None:
        return None
    raw = str(value).replace('\u00a0', ' ').strip()
    if raw.upper() in MISSING:
        return None
    cleaned = re.sub(r'[^0-9.\-]', '', raw)
    if cleaned in {'', '-', '.', '-.'}:
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def decimal_equal(left: Any, right: Any) -> bool:
    """Compare parseable values numerically; missing/invalid values only equal each other."""
    a, b = safe_decimal(left), safe_decimal(right)
    if a is None or b is None:
        return a is None and b is None and str(left or '').strip() == str(right or '').strip()
    return a == b


@dataclass(frozen=True)
class Discrepancy:
    reason: str
    record_id: str
    location_id: str
    org_id: str
    val_a: str | None
    val_b: str | None
    entry_ids: tuple[str, ...] = ()

    def to_dict(self):
        data = asdict(self)
        data['entry_ids'] = list(self.entry_ids)
        return data


def reconcile_records(records_a: list[dict], records_b: list[dict], location_org_map: dict[str, str]) -> list[Discrepancy]:
    """Deterministically reconcile A and B within tenant boundaries.

    Matching is by normalized record id/reference AND organization. This means a B row
    cannot satisfy an A row belonging to another tenant, even if their IDs happen to match.
    """
    a_by_key: dict[tuple[str, str], dict] = {}
    b_by_key: dict[tuple[str, str], list[dict]] = defaultdict(list)

    for a in records_a:
        org = location_org_map.get(a.get('location_id'), 'UNKNOWN')
        key = (org, normalize_reference(a.get('record_id')))
        if key[1]:
            a_by_key[key] = a

    for b in records_b:
        org = location_org_map.get(b.get('location_id'), 'UNKNOWN')
        key = (org, normalize_reference(b.get('record_ref')))
        b_by_key[key].append(b)

    discrepancies: list[Discrepancy] = []
    matched_keys: set[tuple[str, str]] = set()

    for key, a in a_by_key.items():
        org, normalized_id = key
        entries = b_by_key.get(key, [])
        if not entries:
            discrepancies.append(Discrepancy(
                'MISSING_IN_SYSTEM_B', a['record_id'], a.get('location_id', ''), org,
                str(a.get('total_value_raw', a.get('value', ''))), None
            ))
            continue

        matched_keys.add(key)
        if len(entries) > 1:
            discrepancies.append(Discrepancy(
                'DUPLICATE_IN_SYSTEM_B', a['record_id'], a.get('location_id', ''), org,
                str(a.get('total_value_raw', a.get('value', ''))),
                '; '.join(str(e.get('value_raw', e.get('value', ''))) for e in entries),
                tuple(str(e.get('entry_id', '')) for e in entries),
            ))
            continue

        b = entries[0]
        val_a = str(a.get('total_value_raw', a.get('value', '')))
        val_b = str(b.get('value_raw', b.get('value', '')))
        if not decimal_equal(val_a, val_b):
            discrepancies.append(Discrepancy(
                'VALUE_MISMATCH', a['record_id'], a.get('location_id', ''), org,
                val_a, val_b, (str(b.get('entry_id', '')),)
            ))

    for key, entries in b_by_key.items():
        org, normalized_ref = key
        if not normalized_ref or key in matched_keys or key in a_by_key:
            continue
        for b in entries:
            discrepancies.append(Discrepancy(
                'ORPHAN_IN_SYSTEM_B', b.get('record_ref', b.get('record_ref_raw', '')),
                b.get('location_id', ''), org, None,
                str(b.get('value_raw', b.get('value', ''))),
                (str(b.get('entry_id', '')),),
            ))

    return discrepancies
