# Repository file map

```text
.
├── README.md
├── docs/
│   ├── CHANGELOG.md
│   ├── FILE-MAP.md
│   ├── INSTALLATION.md
│   ├── PATCH-REFERENCE.md
│   └── TESTING.md
├── scripts/
│   └── patch_streamrip.py
└── tests/
    └── test_patch_streamrip.py
```

## File responsibilities

- `README.md` — project overview, scope, quick start, and links to detailed documentation.
- `docs/INSTALLATION.md` — package-path identification, dry run, application, batch-size configuration, and rollback.
- `docs/PATCH-REFERENCE.md` — exact target files, original behavior, modified behavior, rationale, and compatibility boundaries.
- `docs/TESTING.md` — transformation tests, smoke tests, and a controlled live-download test plan.
- `docs/CHANGELOG.md` — user-visible changes and known limitations.
- `scripts/patch_streamrip.py` — guarded patcher for the installed Streamrip package.
- `tests/test_patch_streamrip.py` — tests for the patch transformations and their idempotency.

The repository contains patching and documentation assets, not a vendored copy of the Streamrip package. This avoids implying that these files are a complete replacement for upstream source.
