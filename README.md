# Streamrip — modified source files

This repository stores the modified Streamrip files so they can be copied into a fresh Streamrip installation. The folder layout mirrors the contents of Streamrip's installed `site-packages/streamrip/` directory.

There is **no patching script** here. Install Streamrip, back up its installed package folder, then copy these files into the matching locations. The files currently match the Streamrip **2.2.0** installation and customizations documented here; review compatibility before using them with a different version.

## Files

| File in this repository | Copy to | Change |
| --- | --- | --- |
| `__init__.py` | `streamrip/__init__.py` | Raises Python's `http.client` response-header limit to at least 1,000. |
| `media/album.py` | `streamrip/media/album.py` | Resolves and downloads album tracks in batches. Default batch size: 10. |
| `media/playlist.py` | `streamrip/media/playlist.py` | Uses the same configurable batch size for playlists. |
| `media/track.py` | `streamrip/media/track.py` | Handles `NonStreamableError` when resolving a single track's cover/download information. |
| `metadata/track.py` | `streamrip/metadata/track.py` | Adds `isrc`, `bit_depth`, and `sample_rate` to filename-template fields. |

The repository root represents the inside of the installed `streamrip/` package. **Do not copy the whole repository over the installed package folder.** Copy the five Python files using the paths in the table.

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
└── docs/
    ├── CHANGELOG.md
    ├── FILE-MAP.md
    ├── INSTALLATION.md
    ├── PATCH-REFERENCE.md
    ├── TESTING.md
    └── UPSTREAM-FILES.md
```

## Install or restore the files

1. Install Streamrip normally and check its version with `rip --version`.
2. Back up the installed `streamrip/` package directory.
3. Copy the five files into their matching paths. The full instructions and commands are in [Installation](docs/INSTALLATION.md).
4. Check that `rip --version` still works, then test a small download.

For the uv installation shown in Dolphin, the package directory was:

```text
~/.local/share/uv/tools/streamrip/lib/python3.13/site-packages/streamrip/
```

The Python version or installation location may be different on another machine.

## Batch size

Album and playlist batch processing defaults to 10. To use 25 for one command, set the variable for that run:

```bash
STREAMRIP_TRACK_BATCH_SIZE=25 rip -q 4 file /path/to/Qobuz.txt
```

Your normal command needs no extra setting when using the default:

```bash
rip -q 4 file /path/to/Qobuz.txt
```

Replace `/path/to/Qobuz.txt` with the actual path to your list file.

Batching limits how many track workflows are active at once and reduces the time between fetching download information and using it. It cannot guarantee that a signed URL will not expire.

## Original source and change notes

- [Original upstream file links](docs/UPSTREAM-FILES.md)
- [Original behavior vs. modified behavior](docs/PATCH-REFERENCE.md)
- [Installed/repository file map](docs/FILE-MAP.md)
- [Testing notes](docs/TESTING.md)
- [Change log](docs/CHANGELOG.md)

The original upstream links point to the `dev` branch and may change over time. They are references, not exact backups of the files on your computer. Keep your local backups when replacing files.

## Known limits

- The header change targets Python's standard-library `http.client` header-count error. It does not solve authentication problems, unavailable tracks, or every HTTP error.
- Batch processing does not guarantee recovery from HTTP 410 or expired download URLs.
- The code has not been confirmed against every Streamrip release. Review [Patch reference](docs/PATCH-REFERENCE.md) and [Testing](docs/TESTING.md) before applying it to a different version.
