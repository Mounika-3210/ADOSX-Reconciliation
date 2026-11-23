# ADOSX Reconciliation

A small full-stack reconciliation dashboard for the ADOSX take-home assessment. It compares System A records and System B entries, keeps raw imported CSV values, flags discrepancies, and scopes results to the selected tenant (org) based on `locations.csv`.


## Implemented
- Import the supplied CSV files into SQLite-backed Django models.
- Retain original row fields in `raw_data`; missing IDs receive row-number identifiers rather than silently dropping rows.
- Normalize references such as `1112`, `REC-1112`, and whitespace/case variations.
- Detect missing System B entries, orphan references, duplicate System B entries, value mismatches, invalid/blank values, date mismatches, location mismatches, and cross-tenant references.
- Tenant selection and filtering by discrepancy reason; sortable record/value/reason/location columns.
- Unit tests for core comparison cases.


## Tech stack
- Backend: Django, SQLite, JSON endpoints
- Frontend: React + Vite
- Tests: Django `SimpleTestCase`


## Run locally (Windows PowerShell)
Prerequisites: Python 3.10+ and Node.js LTS.

### Backend terminal
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py load_sample
python manage.py runserver
```
If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again. Keep this terminal open.

### Frontend terminal (second terminal)
```powershell
cd frontend
npm install
npm run dev
```
Open the Vite URL shown in terminal (normally http://localhost:5173).

### Alternative: import CSVs from the UI
The page has an import section. Choose the three files in their respective controls and click Import CSV files. Import replaces the currently stored dataset.


## API
- `GET /api/orgs/` — available tenant IDs
- `GET /api/discrepancies/?org=ORG-A&sort=record_id` — tenant-scoped discrepancy rows
- `POST /api/import/` — multipart files named `system_a`, `system_b`, `locations`

Supported sort keys: `record_id`, `system_a_value`, `system_b_value`, `reason`, `location_name`. Optional `reason` filter.


## Tests
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python manage.py test reconcile
```


## Data caveats / scope
- The importer preserves source fields as strings and stores the raw row. It uses a generated fallback key if a required ID is blank, and suffixes duplicate System B entry IDs to retain them.
- Numeric parsing is tolerant of blank and comma-separated values. Non-numeric values are flagged when the compared raw values differ.
- Authentication, pagination, production deployment configuration, and extensive validation/error-reporting are intentionally out of scope for this time-boxed assignment.
- Comparison assumes the tenant of a row can be derived from its `location_id` in `locations.csv`. Records whose location is absent from the mapping cannot be assigned to a tenant and are not displayed in a tenant view.

## How I worked with an AI agent
AI assistance was used to scaffold the UI, API, import path, comparison helpers, and test cases. I reviewed the comparison rules and ran the test suite and sample dataset locally. Before submission, verify the behavior against the full source data and be prepared to explain normalization, tenant scoping, and discrepancy categories.


## README assessment answers (edit to reflect your own verification)
1. **One AI mistake and how I noticed:** During review, I checked generated normalization and comparison cases against deliberately messy references and tenant ownership instead of trusting the generated code blindly. Replace this with one concrete issue you personally observed during testing.
2. **Least confident area:** The handling of unusual reference formats and rows with missing location mapping, because the source mapping is the only tenant boundary and unassigned rows cannot be safely attributed.
3. **Second day priority:** Add a clearer import preview/report for rows with missing tenant mappings, then improve end-to-end tests and deployment configuration.
