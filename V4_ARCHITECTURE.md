# GAUR CRM v4.0 Stable Architecture

## Objective
Stop the regression cycle where a new dashboard/report/chat change breaks previously working pages.

## Core rule
`legacy_core.py` is a frozen compatibility layer containing the current v3.98 feature set.
Routine development must **not** modify it.

New work is implemented under `modules/<feature>/` and registered through `modules/registry.py`.

## Module boundaries
- dashboard
- leads
- enrollments
- accounts
- reporting
- chat
- profiles
- filing
- system

A module owns its own routes, services, templates/static assets and tests. Cross-module changes
should use service interfaces rather than template string replacement or runtime DOM patching.

## Release workflow
1. Freeze a production release.
2. Make one module change on development.
3. Run regression tests and route snapshot checks.
4. Deploy to staging.
5. Approve and tag a new release.
6. Production rollback is always to the previous zip/tag.

## Database policy
Existing database/data is preserved. Schema changes must be additive and versioned. Destructive
schema edits require an explicit migration and backup.

## UI policy
No runtime Jinja string surgery for new v4 features.
No global CSS/JS patches for module-specific UI.
Shared layout changes require a dedicated shared component and regression test.
