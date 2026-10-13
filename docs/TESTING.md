# Testing and verification

These checks help confirm that the copied files are in the right place and can be loaded by Python. They do not guarantee that every source or download URL will work.

## Checks completed for this repository

- Compared the five tracked Python files with their corresponding files on the upstream `dev` branch. The differences are limited to the changes described in [Patch reference](PATCH-REFERENCE.md).
- The user applied the original patcher to the installed package. It reported that Python syntax checks passed.
- The installed command returned `rip, version 2.2.0`.

The original patching script is no longer stored in this repository. No live Qobuz download result has been confirmed here.

## After copying files

### 1. Check syntax

Run this using the Python minor version associated with the Streamrip environment. For Python 3.13:

```bash
python3.13 -m py_compile \
  "$PKG_DIR/__init__.py" \
  "$PKG_DIR/media/album.py" \
  "$PKG_DIR/media/playlist.py" \
  "$PKG_DIR/media/track.py" \
  "$PKG_DIR/metadata/track.py"
```

Define `PKG_DIR` first, pointing to the installed `streamrip/` directory.

### 2. Check the command

```bash
rip --version
```

If Streamrip fails to start, restore the backup before attempting further changes.

### 3. Test a small download

Start with a small album or playlist and check the log and output. On the machine used during setup, the usual list command was:

```bash
rip -q 4 file /run/media/yea/Storage/Qobuz.txt
```

On another computer, use the actual path to its list file. For the first test, use a short list rather than a large download queue.

## What these checks do not prove

- A successful syntax check does not prove that the service credentials or API work.
- The HTTP header limit change only targets the standard-library `http.client` count limit.
- Batching reduces the age of the resolved download information but cannot prevent every HTTP 410 or signed-URL expiration.
- A test of one source or album does not validate every provider or playlist type.
