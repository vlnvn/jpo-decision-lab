# Contributing

Create a feature branch from `main`; keep commits limited to one testable problem. Explain changes to model behavior, database schema, or criterion definitions separately from visual changes.

Review before pull request:

1. `python -m pytest tests -q` and `node --check web/app.js` pass.
2. Research definitions are consistent with Table II; update `docs/METHOD.md` if a methodological convention changes.
3. New observations have source/period metadata. Do not add 'realistic looking' field values without observation records.
4. Keep synthetic inputs marked synthetic; never blend simulated and measured data.
5. Check desktop (1920 px) and mobile (390 px), keyboard input, status labels and map attribution.
6. Update README/architecture documents when API or setup changes.

Do not commit generated SQLite files, exports with private field data, build caches, or unused asset libraries. CI is configured but is not evidence of production deployment.