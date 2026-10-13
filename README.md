# ADD ISRC

## 1. Where the ISRC comes from

In your uploaded file, lines 38–41 contain this code:&#x20;

track.py



```
@classmethoddef from_qobuz(cls, album: AlbumMetadata, resp: dict) -> TrackMetadata | None:    title = typed(resp["title"].strip(), str)    isrc = typed(resp["isrc"], str)
```

Here's what that means:

- Streamrip receives a Qobuz track metadata response, called `resp`.
- It reads the track title from `resp["title"]`.
- It reads the ISRC directly from `resp["isrc"]`.
- It stores that ISRC in its track metadata object.

Your modification does not independently search an ISRC database. It uses the ISRC supplied in the Qobuz response. We haven't inspected the actual network response body, so we cannot independently verify Qobuz's returned value from your logs alone.

## 2. What the modification added

This is the most important section, at lines 230–255.&#x20;

track.py



Your modified code builds this dictionary:

```
info = {    "id": self.info.id,    "title": self.title,    "tracknumber": self.tracknumber,    "artist": self.artist,    "albumartist": self.album.albumartist,    "albumcomposer": self.album.albumcomposer or none_text,    "composer": self.composer or none_text,    "explicit": " (Explicit)" if self.info.explicit else "",    "isrc": self.isrc or none_text,    "bit_depth": self.info.bit_depth or none_text,    "sample_rate": sample_rate,}return format_string.format(**info)
```

The three crucial additions are:

| Added field   | Purpose                                                    |
| ------------- | ---------------------------------------------------------- |
| `isrc`        | Makes the ISRC available to filename templates.            |
| `bit_depth`   | Makes the audio bit depth available to filename templates. |
| `sample_rate` | Makes the sample rate available to filename templates.     |

It also formats the sample rate and uses `Unknown` when certain values aren't available.

## 3. How the final filename is created

Your current configuration specifies:

```
track_format = "{title} - {artist} - ISRC-{isrc} - Qobuz-{id}"
```

Streamrip substitutes the metadata values into the template and constructs the download path.

Your real test proves that this works:

Observed file creation · October 11, 2026

`Future Island - Calliope Mori - ISRC-JPPO02302154 - Qobuz-223669566.flac`

&#x20;Created directly under the final filename

Your filesystem watcher and system-call trace recorded the file being created under this exact name. No post-download rename was observed.

That matches the implementation in your uploaded source code.

___
___

# Handle non-streamable tracks without crashing the entire download process

1\. Adds error handling

Originally, the code runs these two operations concurrently:

- Download the album cover.
- Request downloadable data for the track.

The patch wraps both operations in `try/except NonStreamableError`.

2\. Logs the error and skips the track

If `NonStreamableError` is raised, it logs the track number, track ID, and error message, then returns `None` instead of allowing that exception to propagate from this code block.

3\. Validates and backs up the file

- Compiles the modified source to check Python syntax.
- Saves the original as `track.py.py.bak`.
- Writes the patched version to `track.py`.
- Prints the success message you saw.

## Before vs. after

Before the patch:

```
embedded_cover_path, downloadable = await asyncio.gather(    self._download_cover(album.covers, folder),    self.client.get_downloadable(self.id, quality),)
```

If `get_downloadable()` raises `NonStreamableError`, the exception can propagate to the caller and potentially interrupt the download workflow.

After the patch:

```
try:    embedded_cover_path, downloadable = await asyncio.gather(        self._download_cover(album.covers, folder),        self.client.get_downloadable(self.id, quality),    )except NonStreamableError as e:    logger.error(        f"Error getting downloadable data for track "        f"{meta.tracknumber} [{self.id}]: {e}"    )    return None
```

The intended result is to log the failure and let the calling code handle the returned `None`, ideally by skipping that track and continuing with the remaining tracks.

## Important limitations

This patch does not:

- Make an unstreamable or unavailable Qobuz track downloadable.
- Retry failed requests.
- Fix authentication, network, or general API errors.
- Guarantee that the entire album download continues; that depends on how the caller handles `None`.
- Guarantee that the album-cover download is cancelled if `get_downloadable()` fails. Because `asyncio.gather()` runs both operations concurrently, the cover task may continue or behave differently depending on the failure and Python version.

One subtle point: the `except` block catches only `NonStreamableError`. Other exceptions can still propagate.

## What the success message means

`SUCCESS: Patch applied; Python syntax check passed.`

This confirms that the script found its target, generated syntactically valid Python code, and wrote the patched file. It does not confirm that the patch works correctly during an actual Streamrip download.

Your backup is located at:

`/home/yea/.local/share/uv/tools/streamrip/lib/python3.13/site-packages/streamrip/media/track.py.py.bak`
