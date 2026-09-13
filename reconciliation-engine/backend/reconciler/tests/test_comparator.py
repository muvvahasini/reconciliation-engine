from reconciler.services.comparator import reconcile_records


def test_detects_record_missing_in_system_b():
    results = reconcile_records(
        [{'record_id': 'REC-01', 'total_value_raw': '100', 'location_id': 'LOC-1'}],
        [],
        {'LOC-1': 'ORG-1'},
    )
    assert [r.reason for r in results] == ['MISSING_IN_SYSTEM_B']


def test_detects_orphan_record_in_system_b():
    results = reconcile_records(
        [],
        [{'entry_id': 'E1', 'record_ref': 'REC-999', 'value_raw': '250', 'location_id': 'LOC-1'}],
        {'LOC-1': 'ORG-1'},
    )
    assert len(results) == 1
    assert results[0].reason == 'ORPHAN_IN_SYSTEM_B'


def test_detects_duplicate_entries_in_system_b():
    results = reconcile_records(
        [{'record_id': 'REC-01', 'total_value_raw': '100', 'location_id': 'LOC-1'}],
        [
            {'entry_id': 'E1', 'record_ref': 'REC-01', 'value_raw': '100', 'location_id': 'LOC-1'},
            {'entry_id': 'E2', 'record_ref': ' rec-01 ', 'value_raw': '100', 'location_id': 'LOC-1'},
        ],
        {'LOC-1': 'ORG-1'},
    )
    assert len(results) == 1
    assert results[0].reason == 'DUPLICATE_IN_SYSTEM_B'


def test_detects_value_mismatch():
    results = reconcile_records(
        [{'record_id': 'REC-01', 'total_value_raw': '100.00', 'location_id': 'LOC-1'}],
        [{'entry_id': 'E1', 'record_ref': 'REC-01', 'value_raw': '120.00', 'location_id': 'LOC-1'}],
        {'LOC-1': 'ORG-1'},
    )
    assert len(results) == 1
    assert results[0].reason == 'VALUE_MISMATCH'
    assert results[0].val_a == '100.00'
    assert results[0].val_b == '120.00'


def test_normalized_dirty_references_are_matched():
    results = reconcile_records(
        [{'record_id': 'REC-1034', 'total_value_raw': '84939.99', 'location_id': 'LOC-101'}],
        [{'entry_id': 'E1', 'record_ref_raw': ' rec_1034 ', 'value_raw': '84939.99', 'location_id': 'LOC-101'}],
        {'LOC-101': 'ORG-A'},
    )
    assert results == []


def test_uses_record_ref_raw_from_db_rows():
    results = reconcile_records(
        [{'record_id': 'REC-01', 'total_value_raw': '100', 'location_id': 'LOC-1'}],
        [{'entry_id': 'E1', 'record_ref_raw': 'REC-01', 'value_raw': '100', 'location_id': 'LOC-1'}],
        {'LOC-1': 'ORG-1'},
    )
    assert results == []


def test_tenant_boundary_isolation():
    # Same normalized record id exists in both tenants. A B row from ORG-B
    # must not satisfy the ORG-A record.
    results = reconcile_records(
        [{'record_id': 'REC-01', 'total_value_raw': '100', 'location_id': 'LOC-A'}],
        [{'entry_id': 'E1', 'record_ref': 'REC-01', 'value_raw': '100', 'location_id': 'LOC-B'}],
        {'LOC-A': 'ORG-A', 'LOC-B': 'ORG-B'},
    )
    assert {(r.reason, r.org_id) for r in results} == {
        ('MISSING_IN_SYSTEM_B', 'ORG-A'),
        ('ORPHAN_IN_SYSTEM_B', 'ORG-B'),
    }
