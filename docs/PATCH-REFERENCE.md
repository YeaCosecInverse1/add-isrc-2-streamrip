# Patch reference

This page explains what differs from the original Streamrip source and why each file is kept in this repository. The code files are intended to be copied into a matching Streamrip installation.

## Summary

| File | Original behavior | Modified behavior |
| --- | --- | --- |
| `__init__.py` | Uses Python's default `http.client` response-header count limit. | Sets `http.client._MAXHEADERS` to at least 1,000. |
| `media/album.py` | Starts resolving the album's pending tracks together through one `asyncio.gather()`. | Resolves and downloads tracks in batches, waiting for one batch to finish before starting the next. |
| `media/playlist.py` | Uses a fixed playlist chunk size of 20. | Reads `STREAMRIP_TRACK_BATCH_SIZE`, defaulting to 10. |
| `media/track.py` | A `NonStreamableError` raised during the concurrent cover/downloadable work for a single track can escape from `PendingSingle.resolve()`. | Logs the track number, ID, and error, then returns `None` for that track. |
| `metadata/track.py` | The filename formatter does not expose the additional keys used by the local filename template. | Exposes `isrc`, `bit_depth`, and `sample_rate`, alongside the existing formatter keys. |

## 1. `__init__.py`: HTTP response headers

Added near the beginning of package initialization:

```python
import http.client
http.client._MAXHEADERS = max(http.client._MAXHEADERS, 1000)
```

This targets the error `HTTPException('got more than 100 headers')`. Using `max()` means it will not reduce the limit if Python already has a higher value. The setting affects Python's standard-library `http.client` parser; it does not change every HTTP library's limits and does not fix unrelated HTTP errors.

## 2. `media/album.py`: bounded album batches

Album tracks are divided into groups using `STREAMRIP_TRACK_BATCH_SIZE`. The default is 10. Track resolve-and-download work remains concurrent inside a group, but the next group does not start until the current group finishes.

This reduces how long a track's download information waits before that track is downloaded. It does not guarantee that a signed URL cannot expire.

## 3. `media/playlist.py`: shared playlist batch size

The previous fixed chunk size of 20 is replaced with `STREAMRIP_TRACK_BATCH_SIZE`, defaulting to 10. The value must be a positive integer; invalid or non-positive values fall back to 10 with a warning.

Set it for one command like this:

```bash
STREAMRIP_TRACK_BATCH_SIZE=25 rip -q 4 file /path/to/Qobuz.txt
```

Without this variable, batches of 10 are used.

## 4. `media/track.py`: a non-streamable single track

In `PendingSingle.resolve()`, the concurrent attempt to download artwork and retrieve downloadable track information is wrapped in a `NonStreamableError` handler. When that exception is raised, Streamrip logs the track number, track ID, and error and returns `None`, rather than letting this particular exception escape from the resolution method.

This does not make a track streamable when the source does not provide it.

## 5. `metadata/track.py`: filename template fields

The filename formatter can use these fields:

- `{id}`
- `{title}`
- `{tracknumber}`
- `{artist}`
- `{albumartist}`
- `{albumcomposer}`
- `{composer}`
- `{explicit}`
- `{isrc}`
- `{bit_depth}`
- `{sample_rate}`

Example:

```text
{title} - {artist} - ISRC-{isrc} - Qobuz-{id}
```

If ISRC or bit depth is not available, the formatter uses `Unknown`. Sampling rates reported in hertz are formatted in kilohertz (for example, 96000 becomes `96`); values already below 1000 are kept as-is.

## Compatibility

The files were compared with corresponding source files on the upstream `dev` branch during this repository update. These links are not version-pinned, and the upstream branch may change. Keep a backup of the installed files and check the installed Streamrip version before copying these files over a different release.
