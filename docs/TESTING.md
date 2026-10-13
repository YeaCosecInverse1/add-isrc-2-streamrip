# Validation and test plan

## Validation levels

A successful patch has several distinct validation stages. Passing one stage does not imply that later stages have passed.

| Stage | What it checks | What it does not establish |
| --- | --- | --- |
| Source-pattern validation | The installed files contain the expected edit points. | Runtime behavior or API availability. |
| Python syntax check | Modified files compile. | Successful imports, authentication, or downloads. |
| CLI smoke test | The installed `rip` command starts and reports its version. | Correct behavior against a live service. |
| Small download test | A real album or playlist completes under the selected batch size. | Reliability for every release, network, or collection size. |

## 1. Dry-run validation

Run the patcher with `--dry-run`. Confirm that it identifies only:

- `streamrip/__init__.py`
- `streamrip/media/album.py`
- `streamrip/media/playlist.py`

It should explicitly report that `metadata/track.py` and `media/track.py` will remain untouched.

## 2. Unit tests for patch transformations

Run from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

These tests exercise the source transformations using small representative fixtures. They do not execute Streamrip or contact Qobuz.

## 3. Syntax and CLI smoke test

After applying the patch:

```bash
rip --version
```

If the command fails to start, restore the relevant backup before attempting another edit.

## 4. Controlled download test

Use a small album or playlist that you are authorized to access. First test with the default batch size:

```bash
unset STREAMRIP_TRACK_BATCH_SIZE
rip url "YOUR_ALBUM_URL"
```

Then test with a batch size of 25:

```bash
STREAMRIP_TRACK_BATCH_SIZE=25 rip url "YOUR_ALBUM_URL"
```

Check that:

- The command reaches later batches after an individual track is skipped.
- Existing ISRC-based filenames are still generated as configured.
- The existing non-streamable-track behavior still logs and skips the affected track where applicable.
- Downloaded files can be opened and tagged as expected.
- Logs do not show the same header-count exception.

Do not use a large collection as the first test.

## 5. Interpreting failures

- `got more than 100 headers`: verify the installed `streamrip/__init__.py` contains the header-limit assignment and that the command is using the patched environment.
- `410 Gone`: batching may reduce URL age, but this status can have other causes and is not proof that the batching patch failed.
- `NonStreamableError`: the track may be unavailable for streaming; this patch set does not make it available.
- Syntax or import errors: stop and restore from backup before continuing.
- A source-pattern mismatch: the installed Streamrip version differs from the expected layout; do not force the patch.

## Test status

Repository-side transformation tests and Python syntax checks should be run before release. A live download test must be performed on the target installation; it cannot be inferred from static checks.
