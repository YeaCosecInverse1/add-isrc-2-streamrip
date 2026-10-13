# Change log

## Current source set

The repository stores seven ready-to-copy modified Streamrip source files in a layout mirroring the installed package. It does not include a file-patching script.

## Changes

- `__init__.py`: raise the standard-library `http.client` response-header count limit to at least 1,000.
- `media/album.py`: resolve and download album tracks in sequential batches.
- `media/playlist.py`: use the shared configurable batch size, default 10.
- `media/track.py`: handle a specific `NonStreamableError` path during single-track resolution.
- `metadata/track.py`: expose ISRC, bit depth, and sample rate as filename-template fields.
- `rip/main.py`: add a batch pipeline that resolves and downloads pending items batch by batch.
- `rip/cli.py`: route `rip file` through that pipeline, so a file containing 7,500 individual URLs no longer resolves every track before any download begins.

## Limitations

- The files are aligned with the Streamrip 2.2.0 installation reported during setup; other versions may require review.
- Batching reduces the age of signed download URLs but cannot guarantee that they will never expire.
- The repository owner has reported that the new large-file `rip file` workflow works in their installed setup; this is user-reported manual verification, not an independently reproduced test.
