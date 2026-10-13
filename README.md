# Streamrip — modified source files

This repository stores modified Streamrip source files in a layout that mirrors the installed `streamrip/` package. Copy the files into a matching installation; there is no patching script.

The files are aligned with the Streamrip **2.2.0** installation reported during setup. Check the installed version before using them with another release.

## Files in this repository

| Repository file | Copy to | Purpose |
| --- | --- | --- |
| `__init__.py` | `streamrip/__init__.py` | Raises Python's standard-library HTTP response-header count limit to at least 1,000. |
| `media/album.py` | `streamrip/media/album.py` | Resolves and downloads album tracks in batches. |
| `media/playlist.py` | `streamrip/media/playlist.py` | Uses the shared configurable playlist batch size. |
| `media/track.py` | `streamrip/media/track.py` | Handles a specific `NonStreamableError` path while resolving an individual track. |
| `metadata/track.py` | `streamrip/metadata/track.py` | Exposes ISRC, bit depth, and sample rate as filename-template fields. |
| `rip/main.py` | `streamrip/rip/main.py` | Adds batched resolve-and-download processing for large files of URLs. |
| `rip/cli.py` | `streamrip/rip/cli.py` | Makes `rip file` use batched resolve-and-download processing. |

## Why the `rip/` files matter for large track lists

For a file containing thousands of individual track URLs, the original workflow resolves every pending item before starting the download phase. That can leave early signed download URLs waiting while the rest of the list is resolved.

The modified `rip file` workflow processes a bounded number of items at a time: resolve one batch, download that batch, then move to the next batch. The default is **10** items per batch. This workflow is separate from the album and playlist batching inside `media/album.py` and `media/playlist.py`.

## Folder layout

```text
.
├── README.md
├── __init__.py
├── media/
│   ├── album.py
│   ├── playlist.py
│   └── track.py
├── metadata/
│   └── track.py
├── rip/
│   ├── cli.py
│   └── main.py
└── docs/
    ├── CHANGELOG.md
    ├── FILE-MAP.md
    ├── INSTALLATION.md
    ├── PATCH-REFERENCE.md
    ├── TESTING.md
    └── UPSTREAM-FILES.md
```

The repository root represents the *inside* of the installed `streamrip/` package. Do not copy the whole repository over the installed package. Copy the seven Python files into the matching destinations listed above.

## Install / update on a new PC

1. Install Streamrip normally.
2. Check `rip --version`.
3. Back up the installed `streamrip/` directory.
4. Copy the seven source files into their matching paths.
5. Run the syntax and startup checks in [Installation](docs/INSTALLATION.md), then test a small list before running the full list.

For the uv installation shown during setup, the package path was:

```text
~/.local/share/uv/tools/streamrip/lib/python3.13/site-packages/streamrip/
```

The Python version and installation path may differ on another computer.

## Batch size

The default is 10. To use 25 for one command:

```bash
STREAMRIP_TRACK_BATCH_SIZE=25 rip -q 4 file /path/to/Qobuz.txt
```

The usual command needs no extra setting:

```bash
rip -q 4 file /path/to/Qobuz.txt
```

Replace the example path with the actual location of the URL list.

Batching reduces how long a resolved download URL waits before its download starts. It cannot guarantee that HTTP 410 responses or signed-URL expiration will never occur.

## Documentation

- [Installation and rollback](docs/INSTALLATION.md)
- [File map](docs/FILE-MAP.md)
- [Original behavior vs. modified behavior](docs/PATCH-REFERENCE.md)
- [Original upstream files](docs/UPSTREAM-FILES.md)
- [Testing and remaining limitations](docs/TESTING.md)
- [Change log](docs/CHANGELOG.md)

## Verification status

The repository owner has reported that the updated `rip file` workflow works with the installed Streamrip setup. This is user-reported manual verification, not an independently reproduced test or a formal automated test result.

## Important limitations

- The header-count setting targets Python's `http.client` parser; it does not change every HTTP library's limit.
- The non-streamable-track handling does not make restricted tracks streamable.
- Batch processing reduces URL age, but cannot guarantee recovery from every API error or expired URL.
- The upstream links point to the moving `dev` branch and are references, not exact backups of the files on your machine.
