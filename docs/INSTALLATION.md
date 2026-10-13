# Installation, application, and rollback

## Requirements

- An existing Streamrip installation that you can modify.
- Python access to the same environment that runs the `rip` command.
- A copy of this repository.
- A short test download before using the changes for a large collection.

The patcher edits the installed package in place. It does not reinstall Streamrip, change credentials, or alter the user's configuration database.

## 1. Identify the installed package directory

For a uv tool installation, the directory commonly looks like:

```text
~/.local/share/uv/tools/streamrip/lib/python3.13/site-packages/streamrip/
```

Use the actual Python version on the machine. The directory passed to `--package-dir` must contain `__init__.py`, and its `media/` subdirectory must contain `album.py` and `playlist.py`.

If Streamrip is installed elsewhere, locate the package directory and pass that path explicitly. Do not point the option at the parent `site-packages` directory.

## 2. Review before applying

From the repository root, run a dry run:

```bash
python3 scripts/patch_streamrip.py \
  --package-dir "$HOME/.local/share/uv/tools/streamrip/lib/python3.13/site-packages/streamrip" \
  --dry-run
```

The script validates the expected source patterns before writing any file. If the installed source has a different layout, it stops and reports the mismatch rather than trying a fuzzy edit.

## 3. Apply the patches

After reviewing the dry-run output:

```bash
python3 scripts/patch_streamrip.py \
  --package-dir "$HOME/.local/share/uv/tools/streamrip/lib/python3.13/site-packages/streamrip"
```

Before changing a file, the script creates a timestamped backup beside it. It then writes the change and runs Python syntax checks on the modified files.

The patcher modifies only:

- `streamrip/__init__.py`
- `streamrip/media/album.py`
- `streamrip/media/playlist.py`

It deliberately leaves `streamrip/metadata/track.py` and `streamrip/media/track.py` untouched.

## 4. Configure the batch size

The default is 10. To use 25, export the variable in the same shell or service environment that launches Streamrip:

```bash
export STREAMRIP_TRACK_BATCH_SIZE=25
rip url "YOUR_ALBUM_URL"
```

To return to the default, unset the variable:

```bash
unset STREAMRIP_TRACK_BATCH_SIZE
```

The value must be a positive integer. The documented choices are 10 and 25; other positive values are accepted but have not been specifically evaluated. The setting applies to album and playlist track processing, not to the number of independent URLs accepted by the CLI.

## 5. Validate the installation

First check that the command still starts:

```bash
rip --version
```

Then download a small album or playlist and inspect the log and output. See [Testing](TESTING.md) for the recommended checks. Do not treat a successful syntax check as proof that the Qobuz API, CDN, authentication, or every download path is working.

## 6. Roll back

The backup names include the original filename, a timestamp, and the `.bak` suffix, for example:

```text
album.py.streamrip-backup-20261013-090000-0600.bak
```

To restore a file, stop Streamrip and copy the corresponding backup over the modified file. Example:

```bash
cp -a /path/to/album.py.streamrip-backup-TIMESTAMP.bak /path/to/album.py
```

Repeat for each file you want to restore. Substitute the exact backup path printed by the patcher. Keep the backup until a real download test has passed.

## Operational notes

- The header-limit patch addresses Python's `http.client` response-header count limit; it does not change aiohttp's parser configuration.
- Batch processing reduces how long resolved download information waits before download begins. It cannot guarantee that signed URLs never expire.
- A failed or unavailable track can still be skipped or fail for reasons unrelated to these patches.
- Reinstalling or upgrading Streamrip may overwrite local edits. Re-check the installed version and reapply only after reviewing compatibility.
