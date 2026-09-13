# Architectural Decisions

### 1. Preserve raw exports
- **Decision:** Store source values as text and retain the original row number.
- **Alternative:** Cast values into strict numeric/date columns during import.
- **Reasoning:** Dirty exports must survive ingestion; parsing belongs to reconciliation, not ingestion.

### 2. Canonical reference matching
- **Decision:** Normalize references by removing separators/whitespace, lowercasing, and treating numeric-only refs as `REC-<number>` shorthand.
- **Alternative:** Exact string matching.
- **Reasoning:** The brief explicitly says System B references appear in multiple formats, so exact matching would create false discrepancies.

### 3. Tenant boundary is part of the match key
- **Decision:** Match on `(org_id, normalized_record_ref)` rather than record reference alone.
- **Alternative:** Match globally and filter discrepancies by tenant afterward.
- **Reasoning:** A record from another tenant must never satisfy a local match, even if identifiers collide.

### 4. Python reconciliation service
- **Decision:** Keep comparison logic in a pure Python service using dictionaries and dataclasses.
- **Alternative:** Encode reconciliation as complex SQL joins.
- **Reasoning:** The dataset is tiny and the business rules are easier to test and review as deterministic Python code.

### 5. Decimal for numeric comparison
- **Decision:** Parse values with `Decimal` after defensive cleanup.
- **Alternative:** Use `float`.
- **Reasoning:** Currency-like values should not depend on binary floating-point precision.

### 6. Compute on read
- **Decision:** Reconcile the imported rows when the discrepancy endpoint is requested.
- **Alternative:** Persist a separate discrepancy snapshot during import.
- **Reasoning:** With only ~120 rows per source, on-demand computation removes stale-cache concerns while remaining effectively instantaneous.

### 7. No authentication in this slice
- **Decision:** Require `org_id` on discrepancy reads but do not build authentication/authorization.
- **Alternative:** Add a full identity provider and user/tenant permission model.
- **Reasoning:** The brief explicitly says authentication is not being tested; tenant scoping is the security requirement that matters here.
