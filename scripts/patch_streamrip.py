#!/usr/bin/env python3
"""Apply the documented local Streamrip patches without replacing custom track files."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

HEADER_MARKER = "http.client._MAXHEADERS = max(http.client._MAXHEADERS, 1000)"
BATCH_MARKER = "STREAMRIP_TRACK_BATCH_SIZE"
DEFAULT_BATCH_SIZE = 10

ALBUM_DOWNLOAD_RE = re.compile(
    r"(?ms)^    async def download\(self\):\n.*?(?=^    async def postprocess\(self\):)"
)

ALBUM_DOWNLOAD_REPLACEMENT = '''    async def download(self):
        """Resolve and download tracks in bounded, sequential batches."""
        try:
            batch_size = int(os.environ.get("STREAMRIP_TRACK_BATCH_SIZE", "10"))
        except ValueError:
            logger.warning(
                "Invalid STREAMRIP_TRACK_BATCH_SIZE; using the default batch size of 10"
            )
            batch_size = 10

        if batch_size < 1:
            logger.warning(
                "STREAMRIP_TRACK_BATCH_SIZE must be positive; using the default batch size of 10"
            )
            batch_size = 10

        async def _resolve_and_download(pending: Pending):
            try:
                track = await pending.resolve()
                if track is None:
                    return
                await track.rip()
            except Exception as e:
                logger.error(f"Error downloading track: {e}")

        # Do not resolve every track in a large album up front. A batch is fully
        # processed before the next batch obtains its download information.
        for start in range(0, len(self.tracks), batch_size):
            batch = self.tracks[start : start + batch_size]
            results = await asyncio.gather(
                *[_resolve_and_download(pending) for pending in batch],
                return_exceptions=True,
            )

            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Album track processing error: {result}")

'''


def patch_header_limit(source: str) -> tuple[str, bool]:
    """Raise the standard-library response-header count limit to at least 1000."""
    if HEADER_MARKER in source:
        return source, False

    lines = source.splitlines(keepends=True)
    import_line = next(
        (i for i, line in enumerate(lines) if line.strip() == "import http.client"),
        None,
    )
    if import_line is not None:
        insertion = import_line + 1
        addition = [
            "\n",
            "# Qobuz/CDN responses can exceed Python's default 100-header limit.\n",
            HEADER_MARKER + "\n",
        ]
    else:
        # Place the standard-library import and assignment before Streamrip's
        # package imports so the limit is set during package initialization.
        insertion = next(
            (
                i
                for i, line in enumerate(lines)
                if line.startswith(("from . import ", "from .config import ", "import "))
            ),
            0,
        )
        addition = [
            "import http.client\n",
            "\n",
            "# Qobuz/CDN responses can exceed Python's default 100-header limit.\n",
            HEADER_MARKER + "\n",
            "\n",
        ]

    lines[insertion:insertion] = addition
    return "".join(lines), True


def patch_album_batching(source: str) -> tuple[str, bool]:
    """Replace only Album.download, retaining the surrounding class and methods."""
    if BATCH_MARKER in source and "Album track processing error" in source:
        return source, False

    match = ALBUM_DOWNLOAD_RE.search(source)
    if match is None:
        raise ValueError(
            "Could not locate Album.download() in media/album.py. "
            "The installed source may differ from the supported layout; no files were changed."
        )

    original = match.group(0)
    if "self.tracks" not in original or "asyncio.gather" not in original:
        raise ValueError(
            "Album.download() does not match the expected Streamrip structure; no files were changed."
        )

    return source[: match.start()] + ALBUM_DOWNLOAD_REPLACEMENT + source[match.end() :], True


def patch_playlist_batching(source: str) -> tuple[str, bool]:
    """Use the shared batch-size setting in Streamrip's existing playlist batching."""
    if BATCH_MARKER in source and "track_resolve_chunk_size" in source:
        return source, False

    original = "        track_resolve_chunk_size = 20"
    if original not in source:
        raise ValueError(
            "Could not locate the expected playlist batch-size setting in media/playlist.py. "
            "The installed source may differ from the supported layout; no files were changed."
        )

    replacement = '''        # Keep playlist resolution and downloading bounded, using the same
        # setting as album downloads.
        try:
            track_resolve_chunk_size = int(
                os.environ.get("STREAMRIP_TRACK_BATCH_SIZE", "10")
            )
        except ValueError:
            logger.warning(
                "Invalid STREAMRIP_TRACK_BATCH_SIZE; using the default batch size of 10"
            )
            track_resolve_chunk_size = 10

        if track_resolve_chunk_size < 1:
            logger.warning(
                "STREAMRIP_TRACK_BATCH_SIZE must be positive; using the default batch size of 10"
            )
            track_resolve_chunk_size = 10'''
    return source.replace(original, replacement, 1), True


def discover_package_dir() -> Path | None:
    """Find a conventional uv-tool installation when --package-dir is omitted."""
    home = Path.home()
    candidates = sorted(
        (home / ".local/share/uv/tools/streamrip/lib").glob(
            "python*/site-packages/streamrip"
        ),
        reverse=True,
    )
    for candidate in candidates:
        if (candidate / "__init__.py").is_file():
            return candidate
    return None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def atomic_write(path: Path, content: str) -> None:
    """Write through a temporary file in the same directory, then replace."""
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        temp_path = Path(handle.name)
        handle.write(content)
    try:
        shutil.copystat(path, temp_path)
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply the documented Streamrip header-limit and track-batching patches."
    )
    parser.add_argument(
        "--package-dir",
        type=Path,
        help="Path to the installed streamrip package directory (the directory containing __init__.py).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which files would change without writing backups or modifying files.",
    )
    args = parser.parse_args()

    package_dir = args.package_dir or discover_package_dir()
    if package_dir is None:
        parser.error(
            "Could not find a uv Streamrip installation. Pass --package-dir with the path to the streamrip package directory."
        )
    package_dir = package_dir.expanduser().resolve()

    targets = {
        package_dir / "__init__.py": patch_header_limit,
        package_dir / "media" / "album.py": patch_album_batching,
        package_dir / "media" / "playlist.py": patch_playlist_batching,
    }

    # Prepare and validate every change before writing any file. A mismatch in
    # one target therefore cannot leave a partially patched installation.
    planned: list[tuple[Path, str, str]] = []
    try:
        for path, patcher in targets.items():
            if not path.is_file():
                raise FileNotFoundError(f"Required file not found: {path}")
            original = read_text(path)
            modified, changed = patcher(original)
            if changed:
                planned.append((path, original, modified))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if not planned:
        print("No changes needed: all supported patches are already present.")
        return 0

    print("Planned changes:")
    for path, _, _ in planned:
        print(f"  - {path}")
    print("Untouched by design:")
    print(f"  - {package_dir / 'metadata' / 'track.py'}")
    print(f"  - {package_dir / 'media' / 'track.py'}")

    if args.dry_run:
        print("Dry run complete; no files were changed.")
        return 0

    timestamp = dt.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%z")
    backups: list[tuple[Path, Path]] = []
    try:
        for path, original, modified in planned:
            backup = path.with_name(f"{path.name}.streamrip-backup-{timestamp}.bak")
            if backup.exists():
                raise FileExistsError(f"Refusing to overwrite existing backup: {backup}")
            shutil.copy2(path, backup)
            backups.append((path, backup))
            atomic_write(path, modified)

        # Syntax-check every modified Python file before reporting success.
        import py_compile

        for path, _, _ in planned:
            py_compile.compile(str(path), doraise=True)
    except Exception as exc:
        print(f"ERROR while applying or validating patches: {exc}", file=sys.stderr)
        print("Backups created during this run:")
        for path, backup in backups:
            print(f"  {path} <- {backup}")
        print(
            "Review the files before retrying. The script does not automatically restore files after a validation failure.",
            file=sys.stderr,
        )
        return 1

    print("Patch applied and Python syntax checks passed.")
    print("Backups:")
    for path, backup in backups:
        print(f"  {path} <- {backup}")
    print("Recommended batch sizes: 10 (default) or 25.")
    print("Set STREAMRIP_TRACK_BATCH_SIZE in the environment used to launch rip.")
    print("A successful syntax check does not replace a real download test.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
