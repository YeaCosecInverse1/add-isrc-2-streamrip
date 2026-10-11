YES! Now we have the actual modified source code. We can finally explain how your ISRC filename feature works. 🔍

The file you uploaded is not a separate downloader script. It's the modified `track.py` module inside your installed Streamrip package.

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
