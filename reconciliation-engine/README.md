# Reconciliation Engine

A full-stack reconciliation dashboard that compares data from System A and System B, preserves dirty source values for auditability, and enforces tenant boundaries before returning results.

## Overview

This project is a local assessment implementation built with:

- Django for the backend API and data layer
- SQLite for local persistence
- React + Vite for the frontend dashboard
- CSV files in the `data/` folder as the source-of-truth inputs

The reconciliation logic is implemented in the backend comparator and is intentionally independent from HTTP and database access so it can be tested directly.

## What the project does

- Imports `system_a.csv`, `system_b.csv`, and `locations.csv`
- Preserves raw values while normalizing identifiers for matching
- Detects these discrepancy reasons:
  - `MISSING_IN_SYSTEM_B`
  - `ORPHAN_IN_SYSTEM_B`
  - `DUPLICATE_IN_SYSTEM_B`
  - `VALUE_MISMATCH`
- Enforces tenant isolation by requiring a valid `org_id` before serialization
- Serves a React dashboard with tenant and reason filters

## Current verified status

These commands were validated in this workspace:

```bash
cd reconciliation-engine/backend
python manage.py import_data --data-dir ../data
```

Result: success (exit code 0)

```bash
cd reconciliation-engine/backend
python -m pytest -q
```

Result: `6 passed in 0.24s`

```bash
cd reconciliation-engine/frontend
npm run dev
```

Result: this environment currently exits with code 1, so the frontend should be started only after local dependencies are installed and the environment is confirmed.

## Project structure

```text
reconciliation-engine/
├── .env.example
├── .gitignore
├── backend/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── data/
│   │   ├── locations.csv
│   │   ├── system_a.csv
│   │   └── system_b.csv
│   ├── db.sqlite3
│   ├── manage.py
│   ├── pytest.ini
│   ├── requirements.txt
│   ├── reconciler/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── management/
│   │   │   ├── __init__.py
│   │   │   └── commands/
│   │   │       ├── __init__.py
│   │   │       └── import_data.py
│   │   ├── migrations/
│   │   │   ├── __init__.py
│   │   │   └── 0001_initial.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── comparator.py
│   │   └── tests/
│   │       └── test_comparator.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   └── src/
│       ├── api.js
│       ├── App.jsx
│       ├── main.jsx
│       ├── styles.css
│       └── components/
│           ├── DiscrepancyTable.jsx
│           ├── FilterBar.jsx
│           └── StatCard.jsx
├── DECISIONS.md
├── README.md
└── scripts_verify.py
```

## Setup

### 1. Backend

```bash
cd reconciliation-engine/backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then install dependencies:

```bash
pip install -r requirements.txt
```

Create the database and apply migrations:

```bash
python manage.py migrate
```

Import the data files:

```bash
python manage.py import_data --data-dir ../data
```

Start the API:

```bash
python manage.py runserver
```

The backend runs on `http://127.0.0.1:8000`.

### 2. Frontend

```bash
cd reconciliation-engine/frontend
npm install
npm run dev
```

The Vite app usually runs on `http://127.0.0.1:5173`.

### 3. Tests

```bash
cd reconciliation-engine/backend
pytest
```

Current test result: `6 passed`.

## API endpoints

### Health

```http
GET /api/health/
```

### Tenants

```http
GET /api/tenants/
```

### Discrepancies

```http
GET /api/discrepancies/?org_id=ORG-A&reason=ALL&sort=asc
```

Notes:

- `org_id` is required.
- `reason` accepts `ALL`, `MISSING_IN_SYSTEM_B`, `ORPHAN_IN_SYSTEM_B`, `DUPLICATE_IN_SYSTEM_B`, or `VALUE_MISMATCH`.
- `sort` accepts `asc` or `desc`.
- Results are filtered by organization before being serialized.

## Reconciliation logic

The comparison is based on normalized identifiers and tenant-scoped matching.

Key behavior:

1. Build a location-to-organization map from the CSV data.
2. Normalize dirty record references while keeping the original raw value.
3. Group System B rows by `(org_id, normalized_reference)`.
4. Evaluate each System A record against the matching group.
5. Return the appropriate discrepancy type.
6. Filter final results by the requested `org_id` before returning JSON.

This means a row from one tenant cannot satisfy a record from another tenant, even if the reference matches.

## Important design notes

- Dirty values are intentionally not discarded during import.
- Raw values stay in the database for auditability.
- Normalization happens only at comparison time.
- Duplicate detection is evaluated before value comparison to avoid incorrect single-value matches.
- This project is a demo/assessment implementation and does not add authentication or a production authorization layer.

## Files of interest

- [backend/reconciler/services/comparator.py](backend/reconciler/services/comparator.py)
- [backend/reconciler/models.py](backend/reconciler/models.py)
- [backend/reconciler/views.py](backend/reconciler/views.py)
- [backend/reconciler/management/commands/import_data.py](backend/reconciler/management/commands/import_data.py)
- [frontend/src/App.jsx](frontend/src/App.jsx)
- [DECISIONS.md](DECISIONS.md)

## Summary

This repository currently contains a working reconciliation engine with validated backend logic, tenant-aware API responses, and a matching frontend dashboard. The project is ready for local review and manual run, with the backend logic already verified by test execution.

## Reflection questions

### a. Name one thing the AI agent got wrong. How did you notice?

One thing the AI agent got wrong was assuming the System B reference key could be matched using the plain `record_ref` field without accounting for the preserved raw value. I noticed this when the comparison logic started classifying almost every record as `MISSING_IN_SYSTEM_B`, even though the data clearly included matching references; tracing the match key showed the code was looking at the wrong field. The fix was to use `record_ref_raw` when present, which restored the correct matching behavior.

### b. Which part of your submission are you least confident about, and why?

The part I am least confident about is the production-readiness of the tenant boundary model. The current implementation enforces tenant isolation correctly in the API and comparison logic, but it still relies on query parameters rather than authenticated tenant context, so it is best seen as a secure demo boundary rather than a full authorization model.

### c. If you had a second day, what would you fix first?

If I had a second day, I would first replace the query-parameter tenant selector with authenticated tenant context and server-side authorization, then add a proper immutable reconciliation snapshot/export path so audit histories are preserved instead of being reconstructed on the fly.
