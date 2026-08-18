# Safe Change Rules

1. Never patch `legacy_core.py` for a normal feature request.
2. One feature = one module.
3. Never change global CSS to solve a page-local layout problem.
4. Never inject raw JavaScript into visible HTML strings.
5. Every route addition gets a smoke test.
6. Every database change is additive/versioned.
7. MD/GM/AM authorization must be tested separately.
8. Before release, compare the route map to the locked snapshot.
9. Create a release zip before starting the next feature.
10. If a regression appears, roll back first; do not stack another emergency patch on production.
