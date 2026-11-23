# Decisions

1. **SQLite for persistence** — Chose SQLite over Postgres; the assignment dataset is small and local setup should stay quick.
2. **Keep source rows as JSON** — Chose raw JSON fields over a wide set of typed columns; dirty strings and extra source columns are retained rather than rejected.
3. **Normalize record references in comparison** — Chose a small normalization helper over exact string matching; references like `1112` and `REC-1112` should match.
4. **Tenant derived from locations** — Chose the locations mapping as the only tenant source; it is the only source of organization ownership in the brief.
5. **Require tenant selection** — Chose to return records only after an org is selected; avoids accidentally showing cross-tenant data in a default view.
6. **Flag multiple entries, don't pick a winner** — Chose to surface duplicate System B rows rather than arbitrarily selecting one.
7. **Simple table UI** — Chose a readable table, filter, and sorting over a complex visual dashboard; the brief prioritizes correctness over styling.
8. **No authentication** — Omitted auth as explicitly out of scope in the assessment.
