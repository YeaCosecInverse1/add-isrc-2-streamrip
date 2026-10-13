# Change log

## Current repository layout

The repository now stores the five modified Streamrip source files in paths that mirror the contents of the installed `streamrip/` package. The Python patching script and script-oriented installation process are not part of this repository.

## Changes preserved in the source files

- `__init__.py`: raises Python's `http.client` header-count limit to at least 1,000.
- `media/album.py`: processes album track tasks in sequential batches.
- `media/playlist.py`: uses `STREAMRIP_TRACK_BATCH_SIZE`, default 10, for playlist batches.
- `media/track.py`: catches `NonStreamableError` during the single-track cover/downloadable operation.
- `metadata/track.py`: makes ISRC, bit depth, and sample rate available to filename templates and documents the supported fields.

## Documentation

Added installation, file-map, patch-reference, upstream-source, and testing notes describing the intended manual-copy workflow.

## Limitations

- The files are aligned with the Streamrip 2.2.0 installation reported during setup; compatibility with other versions is not guaranteed.
- Batching does not guarantee that signed URLs will remain valid.
- A syntax check is not the same as a successful live download.
