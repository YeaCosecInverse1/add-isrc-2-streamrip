# File map

The repository intentionally mirrors the contents of the installed `streamrip/` package. The repository root itself is **not** the package root on disk; it represents the files that live inside that package.

## Repository structure

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
└── docs/
    ├── CHANGELOG.md
    ├── FILE-MAP.md
    ├── INSTALLATION.md
    ├── PATCH-REFERENCE.md
    ├── TESTING.md
    └── UPSTREAM-FILES.md
```

## How the paths map

If the installed package is:

```text
~/.local/share/uv/tools/streamrip/lib/python3.13/site-packages/streamrip/
```

then the copy destinations are:

| Repository path | Installed path, relative to `site-packages/` | Purpose |
| --- | --- | --- |
| `__init__.py` | `streamrip/__init__.py` | HTTP response-header limit. |
| `media/album.py` | `streamrip/media/album.py` | Album batching. |
| `media/playlist.py` | `streamrip/media/playlist.py` | Playlist batching. |
| `media/track.py` | `streamrip/media/track.py` | Non-streamable single-track handling. |
| `metadata/track.py` | `streamrip/metadata/track.py` | Filename-template fields for ISRC, bit depth, and sample rate. |

## Deliberately not included

The repository does not copy the whole Streamrip project. It does not include unchanged directories such as `client/`, `rip/`, or `utils/`, nor the installation's configuration, database, or authentication data. Leave those files in place.

It also does not include an installation patcher. The intended workflow is to back up the installed package and copy the tracked files into their matching locations.
