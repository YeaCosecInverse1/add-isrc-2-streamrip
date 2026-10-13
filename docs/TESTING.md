# Testing and verification

## What is covered by the new batch workflow

For the `rip file` command, the modified code resolves one batch of pending URLs, downloads the media resolved from that batch, then proceeds to the next batch. The default batch size is 10, configurable with `STREAMRIP_TRACK_BATCH_SIZE`.

This specifically addresses the workflow used for a file containing thousands of individual track URLs. Album/playlist batching alone did not cover that input path.

## Checks to run after copying

For a Python 3.13 uv installation, define `PKG_DIR` as the installed `streamrip/` directory and run:

```bash
python3.13 -m py_compile \
  "$PKG_DIR/__init__.py" \
  "$PKG_DIR/media/album.py" \
  "$PKG_DIR/media/playlist.py" \
  "$PKG_DIR/media/track.py" \
  "$PKG_DIR/metadata/track.py" \
  "$PKG_DIR/rip/main.py" \
  "$PKG_DIR/rip/cli.py"
rip --version
```

Then make a short file of a few individual Qobuz track URLs and run:

```bash
rip -q 4 file /path/to/short-test.txt
```

Watch the output to confirm that the command progresses through batches and downloads each batch before resolving the next one.

When that succeeds, run the full list:

```bash
rip -q 4 file /run/media/yea/Storage/Qobuz.txt
```

Use the correct path on the machine you're running.

## Known limitations

- Syntax checking does not prove that authentication, API access, or every URL is valid.
- A track error such as `No result matching given argument` may be caused by an unavailable/invalid item; batching does not make it streamable.
- The header-count patch targets Python's `http.client` parser only.
- Batching reduces the time signed URLs wait before download; it cannot guarantee that every HTTP 410 or expiration error disappears.
- The repository owner has reported that the updated `rip file` workflow works in their installed setup. This is user-reported manual verification; it has not been independently reproduced here, and automated regression tests have not been run as part of this repository update.
