# Patch reference

This page describes the behavior before and after each local source-file change.

## Summary

| File | Original behavior | Modified behavior |
| --- | --- | --- |
| `__init__.py` | Python's standard-library `http.client` uses its normal response-header count limit. | Raises `http.client._MAXHEADERS` to at least 1,000. |
| `media/album.py` | All pending album tracks are resolved in a single `asyncio.gather()`. | Album tracks are resolved and downloaded in sequential batches. |
| `media/playlist.py` | Playlist tracks use a fixed chunk size of 20. | Playlist batches use `STREAMRIP_TRACK_BATCH_SIZE`, default 10. |
| `media/track.py` | A `NonStreamableError` during a single track's concurrent cover/downloadable lookup can escape the resolution method. | Logs the issue and returns `None` from that specific resolution path. |
| `metadata/track.py` | Filename formatting does not expose the added metadata fields used by the local template. | Exposes `isrc`, `bit_depth`, and `sample_rate`, along with existing fields. |
| `rip/main.py` | `Main.resolve()` gathers every pending item at once; the later download phase starts only after all pending items resolve. | Adds a sequential batch pipeline that resolves a group, downloads that group's media, then moves to the next group. |
| `rip/cli.py` | The `file` command invokes `resolve()` for the entire list and then `rip()` once. | The `file` command invokes `resolve_and_rip_batched()`. |

## 1. `__init__.py`: HTTP headers

The added assignment is:

```python
http.client._MAXHEADERS = max(http.client._MAXHEADERS, 1000)
```

It targets `HTTPException('got more than 100 headers')` from Python's standard-library `http.client` parser. It does not modify `aiohttp`'s parser settings and does not fix unrelated service errors.

## 2. `media/album.py` and `media/playlist.py`: album and playlist batches

Both use `STREAMRIP_TRACK_BATCH_SIZE`, defaulting to 10. Tracks within a batch still run concurrently; the next batch waits until the current batch's resolve-and-download work finishes.

This applies inside individual album/playlist workflows. It does not on its own batch a `rip file` list of thousands of individual track URLs.

## 3. `rip/main.py` and `rip/cli.py`: batches for individual URLs in a file

This is the additional change for large `rip file` inputs. The original `Main.resolve()` constructs a coroutine for every pending URL and passes all of them to a single `asyncio.gather()`. For 7,500 individual track URLs, that starts resolution for the entire list before `Main.rip()` begins downloading.

The modified file-command path instead does this for each batch:

1. Resolve at most `STREAMRIP_TRACK_BATCH_SIZE` pending items.
2. Download the media returned by that batch.
3. Clear that batch's media from the in-memory queue.
4. Only then resolve the next batch.

The default is 10. Set it to 25 for one command with:

```bash
STREAMRIP_TRACK_BATCH_SIZE=25 rip -q 4 file /path/to/Qobuz.txt
```

This does not change the ordinary `resolve()` method used by other CLI operations; `rip file` is specifically routed through the new batched method. Because this method processes any media type found in the file, album and playlist URLs in the file are also handled batch by batch; their own track-level batching still applies inside them.

## 4. `media/track.py`: non-streamable single-track resolution

During `PendingSingle.resolve()`, the concurrent cover download and request for downloadable track data are wrapped in a `NonStreamableError` handler. That error is logged, and the track returns `None` rather than escaping that path. It does not grant access to content the provider won't stream.

## 5. `metadata/track.py`: filename keys

Available keys include:

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

Missing ISRC or bit-depth values use `Unknown`. Sampling rates given in hertz are formatted in kilohertz.

## Compatibility and limitations

The tracked files are aligned with the Streamrip 2.2.0 installation reported during setup and were compared against upstream source on the `dev` branch. The upstream links are not version-pinned. Back up the installed package before copying files over another release.

Batching reduces how long signed URLs wait before download begins, but cannot prevent every API failure or URL expiration.
