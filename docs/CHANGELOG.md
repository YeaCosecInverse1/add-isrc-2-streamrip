# Change log

## Unreleased

### Added

- A guarded patcher for the HTTP response-header limit.
- Sequential, bounded album-track processing with a configurable batch size.
- A shared configurable batch-size setting for playlist processing.
- Timestamped backups and syntax checks during patch application.
- Structured installation, patch-reference, testing, file-map, and upstream-source-link documentation.
- Direct links to the original upstream files corresponding to the local package layout shown in the supplied screenshot.

### Preserved

- The existing local ISRC and filename-template customization in `streamrip/metadata/track.py`.
- The existing `NonStreamableError` handling in `streamrip/media/track.py`.

### Limitations

- The patcher targets a known Streamrip source layout and stops when expected edit points are missing.
- Syntax checks are not a substitute for a real download test.
- Batching reduces the age of resolved download information but cannot guarantee that signed URLs remain valid.
- The header-limit change addresses the standard-library `http.client` header count, not unrelated HTTP errors.
- Upstream source links are reference links to the `dev` branch and may not exactly match the installed package version.
