# Installation

These instructions cover copying the files from this repository into an existing Streamrip installation. No patching script is required.

## Before you start

Check which version is installed:

```bash
rip --version
```

The files in this repository are aligned with the Streamrip 2.2.0 installation shown in the project context. If the new computer has a different version, do not assume that these files are drop-in replacements.

## 1. Find the installed package directory

For the uv tool installation shown in Dolphin, the package directory was:

```text
~/.local/share/uv/tools/streamrip/lib/python3.13/site-packages/streamrip/
```

The directory must contain `__init__.py`, plus `media/` and `metadata/` subdirectories. The Python version and installation path can differ between computers.

For a uv tool installation, you can search for the package file with:

```bash
find "$HOME/.local/share/uv/tools/streamrip/lib" \
  -type f -path '*/site-packages/streamrip/__init__.py' -print
```

Use the directory containing that `__init__.py` as the package directory. Do not use the parent `site-packages/` directory.

## 2. Download this repository

On GitHub, choose **Code → Download ZIP**, then extract the archive. Or clone the repository:

```bash
git clone https://github.com/YeaCosecInverse1/add-isrc-2-streamrip.git \
  "$HOME/src/add-isrc-2-streamrip"
```

The repository root is designed to mirror the contents of the installed `streamrip/` package. It is not a complete Streamrip installation.

## 3. Back up the installed package

Close any running Streamrip commands first. In Dolphin, copy the whole installed `streamrip/` directory to a nearby backup location before replacing files.

For example, in Konsole:

```bash
PKG_DIR="$HOME/.local/share/uv/tools/streamrip/lib/python3.13/site-packages/streamrip"
cp -a "$PKG_DIR" "${PKG_DIR}.backup-$(date +%Y%m%d-%H%M%S)"
```

Adjust `PKG_DIR` to the location found in step 1.

## 4. Copy the modified files

### Using Dolphin

Copy the files from the repository into the installed package as follows. Confirm overwrite when prompted, after the backup is made.

| Repository file | Destination |
| --- | --- |
| `__init__.py` | `streamrip/__init__.py` |
| `media/album.py` | `streamrip/media/album.py` |
| `media/playlist.py` | `streamrip/media/playlist.py` |
| `media/track.py` | `streamrip/media/track.py` |
| `metadata/track.py` | `streamrip/metadata/track.py` |

Do not replace the entire installed package with this repository. The other installed folders and files (such as `client/`, `rip/`, `utils/`, and `config.py`) are not included here.

### Using Konsole

If you cloned the repository to `$HOME/src/add-isrc-2-streamrip`, and the installed package path matches the example, run:

```bash
REPO="$HOME/src/add-isrc-2-streamrip"
PKG_DIR="$HOME/.local/share/uv/tools/streamrip/lib/python3.13/site-packages/streamrip"

cp "$REPO/__init__.py"       "$PKG_DIR/__init__.py"
cp "$REPO/media/album.py"    "$PKG_DIR/media/album.py"
cp "$REPO/media/playlist.py" "$PKG_DIR/media/playlist.py"
cp "$REPO/media/track.py"    "$PKG_DIR/media/track.py"
cp "$REPO/metadata/track.py" "$PKG_DIR/metadata/track.py"
```

Adjust both paths if the repository or installed package is elsewhere.

## 5. Check the installation

Use the Python version that belongs to the Streamrip environment to compile-check the copied files. For the example Python 3.13 install:

```bash
python3.13 -m py_compile \
  "$PKG_DIR/__init__.py" \
  "$PKG_DIR/media/album.py" \
  "$PKG_DIR/media/playlist.py" \
  "$PKG_DIR/media/track.py" \
  "$PKG_DIR/metadata/track.py"
```

Then run:

```bash
rip --version
```

Finally, test a small album or playlist before using the files for a large queue. A syntax check alone does not prove that an online download will succeed.

## 6. Roll back

Restore the saved `streamrip/` backup if Streamrip no longer starts or behaves unexpectedly. Stop Streamrip first, move the changed package directory out of the way, then copy the backup back to its original location.

Keep the backup until a real download test has passed.
