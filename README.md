# Streamrip local patches

A small, documented patch set for a local Streamrip installation. It preserves the project's existing customizations for ISRC-based filenames and non-streamable-track handling while adding two narrowly scoped fixes:

- Raise Python's standard-library HTTP response-header limit to 1,000.
- Process album and playlist tracks in sequential batches, resolving and downloading each batch before starting the next.

These changes are intended for a local installation, not as a replacement for the upstream Streamrip package. Review the patch reference and backup/rollback instructions before applying them.

## What this repository changes

| Installed file | Change |
| --- | --- |
| `streamrip/__init__.py` | Sets `http.client._MAXHEADERS` to at least 1,000 during package initialization. |
| `streamrip/media/album.py` | Processes album tracks in bounded batches instead of resolving the entire album concurrently. |
| `streamrip/media/playlist.py` | Makes the existing playlist batch size configurable and uses the same setting. |

The patcher does **not** replace `streamrip/metadata/track.py` or `streamrip/media/track.py`. Your ISRC/filename changes and `NonStreamableError` handling remain separate and untouched.

## Quick start

Use the same Python environment that owns the `rip` command. For a uv tool installation, the package is commonly located under:

```text
~/.local/share/uv/tools/streamrip/lib/pythonX.Y/site-packages/streamrip/
```

Review [Installation and usage](docs/INSTALLATION.md), then run:

```bash
python3 scripts/patch_streamrip.py --package-dir "$HOME/.local/share/uv/tools/streamrip/lib/python3.13/site-packages/streamrip"
```

Change `python3.13` if your installed environment uses another Python version. The patcher creates timestamped backups before writing. It checks for expected source patterns and stops rather than guessing when the installed code differs.

To select a batch size, set `STREAMRIP_TRACK_BATCH_SIZE` to `10` or `25` in the environment used to run `rip`. The default is `10`.

## Documentation

- [Installation, application, and rollback](docs/INSTALLATION.md)
- [Patch reference: original behavior and modified behavior](docs/PATCH-REFERENCE.md)
- [Validation and test plan](docs/TESTING.md)
- [Repository file map](docs/FILE-MAP.md)
- [Change log](docs/CHANGELOG.md)

## Scope and limitations

The header-limit change addresses the specific Python error `HTTPException('got more than 100 headers')`. It does not repair authentication, network failures, unavailable tracks, or HTTP 410 responses by itself.

Batching reduces the time between resolving a track's download information and starting its download. It does not guarantee that a signed URL will never expire. Batch jobs still run concurrently within each batch; the next batch starts only after the current batch's track tasks finish.

The patch has not been validated against every Streamrip release or every source. Run the checks in [Testing](docs/TESTING.md) and perform a small real-world download before relying on it for a large library.

## Upstream references

- [Streamrip](https://github.com/nathom/streamrip)
- [Upstream PR #1033: increase `http.client._MAXHEADERS`](https://github.com/nathom/streamrip/pull/1033)
