# Patch reference

This document records the installed-file changes, the behavior before and after each change, and the intended boundaries of the patch set. Each target entry includes a link to the corresponding original upstream file on the `dev` branch of [nathom/streamrip](https://github.com/nathom/streamrip). Upstream links are reference copies, not a guarantee that the source exactly matches the installed version.

## Summary

| Installed file | Original upstream file | Original behavior | Modified behavior | Reason |
| --- | --- | --- | --- | --- |
| `streamrip/__init__.py` | [View original](https://github.com/nathom/streamrip/blob/dev/streamrip/__init__.py) | Python's standard-library `http.client` uses its default response-header count limit (100). | Sets `http.client._MAXHEADERS` to at least 1,000 during package initialization. | Avoids aborting responses that contain more than 100 headers. |
| `streamrip/media/album.py` | [View original](https://github.com/nathom/streamrip/blob/dev/streamrip/media/album.py) | Album track tasks are all passed to one `asyncio.gather()`, so every track can begin resolving at once. | Resolves and downloads a bounded group, waits for that group to finish, then starts the next group. | Reduces the interval between obtaining a track's download information and using it. |
| `streamrip/media/playlist.py` | [View original](https://github.com/nathom/streamrip/blob/dev/streamrip/media/playlist.py) | Playlist processing uses a fixed chunk size of 20. | Uses `STREAMRIP_TRACK_BATCH_SIZE`, defaulting to 10. | Gives albums and playlists a consistent, configurable batch size. |

For the complete list of original source links matching the screenshot, see [UPSTREAM-FILES.md](UPSTREAM-FILES.md).

## 1. Header limit

### Location and original

Installed target: `streamrip/__init__.py`

Original upstream file: [streamrip/__init__.py](https://github.com/nathom/streamrip/blob/dev/streamrip/__init__.py)

### Added behavior

The patch imports Python's `http.client` module and sets:

```python
http.client._MAXHEADERS = max(http.client._MAXHEADERS, 1000)
```

The assignment is placed during package initialization, before Streamrip's package imports proceed. The `max()` call avoids lowering a limit that is already higher than 1,000.

### Why

The reported failure is:

```text
HTTPException('got more than 100 headers')
```

Python's standard-library HTTP response parser enforces a default header-count limit. Certain CDN responses can exceed it. Upstream Streamrip PR [#1033](https://github.com/nathom/streamrip/pull/1033) describes this issue and the same targeted limit increase.

### Boundaries

This is a narrow workaround for the response-header count. It does not fix a `410 Gone` response, expired signed URLs, authentication failures, rate limits, or unavailable tracks. The setting changes a private standard-library constant, so it should be reviewed when changing Python versions.

## 2. Album batching

### Location and original

Installed target: `streamrip/media/album.py`

Original upstream file: [streamrip/media/album.py](https://github.com/nathom/streamrip/blob/dev/streamrip/media/album.py)

### Original behavior

The existing implementation creates a task for every pending track and submits all of them to one `asyncio.gather()`. That allows resolution for the entire album to begin concurrently.

### Modified behavior

The patch replaces only `Album.download()`. It reads `STREAMRIP_TRACK_BATCH_SIZE` (default `10`), slices the pending tracks into groups, and waits for each group's resolve-and-download tasks to finish before moving to the next group.

Within a batch, tracks still run concurrently. The patch does not force every track to download one at a time; it bounds the number of track workflows active in a group.

### Failure handling

The existing per-track exception logging is retained. A failed track does not intentionally prevent later batches from being attempted. This does not guarantee recovery from every exception or remote-service failure.

## 3. Playlist batching

### Location and original

Installed target: `streamrip/media/playlist.py`

Original upstream file: [streamrip/media/playlist.py](https://github.com/nathom/streamrip/blob/dev/streamrip/media/playlist.py)

### Original behavior

The upstream implementation already processes playlist tracks in chunks, with a fixed chunk size of 20.

### Modified behavior

The patch changes the fixed size to the same `STREAMRIP_TRACK_BATCH_SIZE` environment setting used for albums, defaulting to 10. The existing playlist batch workflow is retained.

## 4. Files intentionally left unchanged

The patcher does not write to these files:

- `streamrip/metadata/track.py`: local ISRC extraction and filename-template changes, including `isrc`, `bit_depth`, and `sample_rate`. [Original upstream file](https://github.com/nathom/streamrip/blob/dev/streamrip/metadata/track.py)
- `streamrip/media/track.py`: local `NonStreamableError` handling for track resolution. [Original upstream file](https://github.com/nathom/streamrip/blob/dev/streamrip/media/track.py)

This separation is deliberate. The new changes do not require replacing either customized track file.

## 5. Compatibility checks

The patcher uses exact structural checks and stops if it cannot find the expected album method or playlist batch-size line. This is safer than applying a guessed edit to an unknown Streamrip version, but it means upstream changes may require an updated patcher.

The patcher creates backups before writing and runs Python syntax checks. It does not run Streamrip's complete test suite or prove that a live download succeeds.
