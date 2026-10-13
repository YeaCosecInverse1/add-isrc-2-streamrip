# File map

The repository root mirrors the inside of the installed `streamrip/` package. Copy each tracked Python file to the same relative path inside that package.

## Repository layout

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

## Copy destination mapping

For an installation at `~/.local/share/uv/tools/streamrip/lib/python3.13/site-packages/streamrip/`:

| Repository file | Installed destination | Reason |
| --- | --- | --- |
| `__init__.py` | `streamrip/__init__.py` | HTTP header-count limit. |
| `media/album.py` | `streamrip/media/album.py` | Batch album track workflows. |
| `media/playlist.py` | `streamrip/media/playlist.py` | Configurable playlist batching. |
| `media/track.py` | `streamrip/media/track.py` | Non-streamable single-track failure handling. |
| `metadata/track.py` | `streamrip/metadata/track.py` | ISRC and extra filename-template keys. |
| `rip/main.py` | `streamrip/rip/main.py` | Batch pending-item resolution and download. |
| `rip/cli.py` | `streamrip/rip/cli.py` | Routes `rip file` through the batched pipeline. |

## What is not included

This is not a full Streamrip checkout. It does not contain unchanged directories such as `client/`, `utils/`, or other parts of `rip/`, nor does it contain the installation's config, database, or credentials. Leave those files in place.

The repository also does not include a patching script: the intended workflow is to copy these seven modified source files into a compatible Streamrip installation.
