# Installation and rollback

This repository stores ready-to-copy modified Streamrip source files. It does not include a script that edits the installed files for you.

## Before copying

Check the installed version:

```bash
rip --version
```

The files are aligned with the Streamrip 2.2.0 installation reported during setup. If your installation reports a different version, review the source differences before overwriting its files.

## 1. Find the installed package folder

For the uv tool installation shown during setup:

```text
~/.local/share/uv/tools/streamrip/lib/python3.13/site-packages/streamrip/
```

To locate the package on a uv tool installation:

```bash
find "$HOME/.local/share/uv/tools/streamrip/lib" \
  -type f -path '*/site-packages/streamrip/__init__.py' -print
```

Use the folder containing `__init__.py`. Do not use the parent `site-packages/` folder.

## 2. Download the repository

Clone it:

```bash
git clone https://github.com/YeaCosecInverse1/add-isrc-2-streamrip.git \
  "$HOME/src/add-isrc-2-streamrip"
```

Or use GitHub's **Code → Download ZIP** option and extract the archive.

The repository root mirrors the inside of the installed `streamrip/` folder.

## 3. Back up the installed package

Close running Streamrip commands. Then back up the package before copying anything:

```bash
PKG_DIR="$HOME/.local/share/uv/tools/streamrip/lib/python3.13/site-packages/streamrip"
cp -a "$PKG_DIR" "${PKG_DIR}.backup-$(date +%Y%m%d-%H%M%S)"
```

Adjust `PKG_DIR` to the path found in step 1.

## 4. Copy all seven modified files

These source files must land at the matching paths:

| Repository file | Destination relative to `site-packages/` |
| --- | --- |
| `__init__.py` | `streamrip/__init__.py` |
| `media/album.py` | `streamrip/media/album.py` |
| `media/playlist.py` | `streamrip/media/playlist.py` |
| `media/track.py` | `streamrip/media/track.py` |
| `metadata/track.py` | `streamrip/metadata/track.py` |
| `rip/main.py` | `streamrip/rip/main.py` |
| `rip/cli.py` | `streamrip/rip/cli.py` |

### Copy with Dolphin

Open the repository folder and the installed `streamrip/` folder in two Dolphin windows. Copy each file or subfolder to the matching destination. Allow the seven listed files to be overwritten only after your backup is complete.

### Copy with Konsole

If the repository and install path match the examples:

```bash
REPO="$HOME/src/add-isrc-2-streamrip"
PKG_DIR="$HOME/.local/share/uv/tools/streamrip/lib/python3.13/site-packages/streamrip"

cp "$REPO/__init__.py"       "$PKG_DIR/__init__.py"
cp "$REPO/media/album.py"    "$PKG_DIR/media/album.py"
cp "$REPO/media/playlist.py" "$PKG_DIR/media/playlist.py"
cp "$REPO/media/track.py"    "$PKG_DIR/media/track.py"
cp "$REPO/metadata/track.py" "$PKG_DIR/metadata/track.py"
cp "$REPO/rip/main.py"       "$PKG_DIR/rip/main.py"
cp "$REPO/rip/cli.py"        "$PKG_DIR/rip/cli.py"
```

Change the variables to match your real paths. Do not copy the repository's `docs/` directory into the installed package.

## 5. Check syntax and command startup

Use the Python minor version associated with the Streamrip tool. For Python 3.13:

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

Then run a short file containing a handful of track URLs before processing the full list.

## 6. Roll back

If Streamrip fails to start or the test behaves unexpectedly, stop Streamrip and restore the package backup created in step 3. Keep the backup until a real download run has been confirmed.

## Notes

- Reinstalling or upgrading Streamrip can overwrite local edits.
- A successful syntax check is not proof that service metadata, authentication, or downloads will work.
- Read [Patch reference](PATCH-REFERENCE.md) to understand exactly what these files change.
