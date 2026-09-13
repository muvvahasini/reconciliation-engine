# Reconciliation Engine

A focused full-stack reconciliation dashboard for the AdosX Engineering assessment.

> **Core promise:** dirty source exports survive ingestion, disagreements are deterministic and explainable, and every discrepancy response is tenant-scoped before serialization.

## What I built

- Django + SQLite backend.
- Resilient CSV importer for `system_a.csv`, `system_b.csv`, and `locations.csv`.
- Raw-value preservation for auditability.
- Reference normalization for formats such as `REC-1034`, `rec_1034`, `REC - 1070`, and numeric-only shorthand such as `1112`.
- Four discrepancy classes:
  - `MISSING_IN_SYSTEM_B`
  - `ORPHAN_IN_SYSTEM_B`
  - `DUPLICATE_IN_SYSTEM_B`
  - `VALUE_MISMATCH`
- Tenant-aware matching using organization as part of the reconciliation key.
- Mandatory `org_id` on discrepancy reads; tenant filtering happens before JSON serialization.
- React/Vite dashboard with tenant and reason filters, value sorting, summary cards, responsive table, loading/error/empty states.
- Six focused reconciliation tests, including a cross-tenant collision regression.

## Dataset note

The assessment text says 120 rows per system. The supplied System A file contains 120 data rows. The System B table supplied for this implementation contains **121 data rows**, including two duplicate references and one orphan reference. The importer intentionally preserves every row rather than silently dropping the extra row.

The supplied System B export also contains deliberately dirty values such as `########`, blank value, whitespace/non-breaking-space references, and a numeric-only reference. Those are preserved as raw strings and handled by the reconciliation layer.

## Project structure

```text
reconciliation-engine/
├── backend/
│   ├── manage.py
│   ├── core/
│   └── reconciler/
│       ├── management/commands/import_data.py
│       ├── migrations/0001_initial.py
│       ├── services/comparator.py
│       ├── models.py
│       ├── views.py
│       ├── urls.py
│       └── tests/test_comparator.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   └── styles.css
│   ├── package.json
│   └── vite.config.js
├── data/
├── DECISIONS.md
└── README.md
```

## Run from a clean clone

### Prerequisites

- Python 3.10–3.12
- Node.js 18 or 20 LTS
- npm

### 1. Backend

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create/update the database:

```bash
python manage.py migrate
```

Import the three exports:

```bash
python manage.py import_data
```

Start Django:

```bash
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/`.

### 2. Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally `http://127.0.0.1:5173`.

Vite proxies `/api` requests to Django during development.

### 3. Tests

From `backend/`:

```bash
pytest
```

The comparison tests are intentionally independent of HTTP and the database so they execute quickly.

## API

### Health

```text
GET /api/health/
```

### Tenants

```text
GET /api/tenants/
```

### Discrepancies

`org_id` is mandatory:

```text
GET /api/discrepancies/?org_id=ORG-A&reason=ALL&sort=asc
```

Supported reasons:

- `ALL`
- `MISSING_IN_SYSTEM_B`
- `ORPHAN_IN_SYSTEM_B`
- `DUPLICATE_IN_SYSTEM_B`
- `VALUE_MISMATCH`

Supported sort values:

- `asc`
- `desc`

A request without `org_id` returns HTTP 400 instead of falling back to a global result set.

## Reconciliation rules

1. Build the location → organization lookup from `locations.csv`.
2. Normalize A record IDs and B references.
3. Build B groups using `(org_id, normalized_reference)`.
4. For every A record:
   - no B group → `MISSING_IN_SYSTEM_B`
   - multiple B entries → `DUPLICATE_IN_SYSTEM_B`
   - one B entry with unequal numeric values → `VALUE_MISMATCH`
5. Any remaining B group without a same-tenant A record → `ORPHAN_IN_SYSTEM_B`.
6. Serialize only results belonging to the requested `org_id`.

This ordering matters: duplicate detection happens before value comparison, so a one-to-many relationship is reported as a duplicate rather than pretending there is a single authoritative B value.

## What I deliberately did not build

- Authentication / login / identity provider.
- Role-based access control beyond the required tenant query boundary.
- Pagination or server-side search; the assessment dataset is intentionally small.
- Background workers or batch processing.
- PostgreSQL deployment configuration.
- Export-to-CSV/PDF.
- A large component/design-system dependency.

These are scope cuts, not accidental omissions.

## How I worked with the AI agent

I used the agent as an implementation partner for scaffolding, repetitive UI code, test scaffolding, and review prompts, while keeping the reconciliation rules and security boundary explicit. I treated generated code as a draft: I inspected the real CSV shapes, ran the core comparison tests, checked dirty reference cases manually, and adjusted the implementation when the generated assumptions did not match the supplied data.

### a. Name one thing the AI agent got wrong. How did you notice?

The first normalization approach treated a numeric-only System B reference such as `1112` as a completely different identifier from `REC-1112`. I noticed this by reviewing the deliberately dirty reference formats in the supplied export and comparing the normalized keys against System A. I changed the canonicalization rule so numeric-only references are interpreted as the `REC-<number>` shorthand while still retaining the raw value for auditability. The regression test now proves that this dirty reference does not create a false discrepancy.

### b. Which part of the submission are you least confident about, and why?

The least certain part is the exact business interpretation of cross-tenant identifier collisions. I chose the conservative security rule: organization is part of the match key, so a B row in another tenant can never satisfy an A row. This is the safest behavior for the explicit tenant-isolation requirement, but in a production system I would confirm the identifier ownership semantics with the product owner and encode that decision in an authorization model.

### c. If you had a second day, what would you fix first?

I would replace the query-parameter tenant selector with authenticated tenant context and server-side authorization, then add an immutable reconciliation snapshot/export path. That would move the demo boundary from “safe scoped assessment slice” toward a production-ready audit workflow without changing the core comparison engine.

## Engineering notes

The most important implementation boundary is `backend/reconciler/services/comparator.py`. It contains no Django HTTP code, which keeps the business decision logic easy to test, reason about, and reuse.

The importer intentionally does not reject rows because a value is not numeric or a reference is malformed. A dirty value is data, not an ingestion failure. Normalization and interpretation happen later.
