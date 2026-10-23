# TV Summary

A typed Python package that summarizes TVMaze shows by genre and average rating
by language. Lab 04 preserves the Lab 03 calculations and adds reproducible featured
shows, offline tests, explicit errors, logging and TOML settings.

## Setup

Run from the repository root in PowerShell:

```powershell
conda env create -f environment.yml
conda activate tvsummary-lab04
python -m pip install -r requirements.txt
python -m pip install -e .
```

The new environment uses Python 3.11 from conda-forge. The requirements were frozen
before editable installation; the Conda build-path entry for packaging was replaced
with its portable version pin. No local editable-install path is in requirements.txt.

## Run

```powershell
python -m tvsummary.main
python -m tvsummary.main --config config/tvsummary.toml
```

A successful run writes `data/processed/summary.json` and
`data/processed/run_info.json`. `python main.py` is a compatibility wrapper around
the package entry point. The source API requires network access; tests do not.

## Check it

```powershell
python -m ruff format --check .
python -m ruff check .
python -m mypy
python -m pytest
```

The settings for all checking tools are in pyproject.toml. All package functions
and methods have type annotations; the package includes an empty py.typed marker.
No type-ignore or noqa comments are used.

## Settings

Edit `config/tvsummary.toml`, or pass another complete TOML file using `--config`.
Settings are loaded with tomllib into a frozen Settings dataclass.

| Setting | Meaning |
| --- | --- |
| source_url | HTTP or HTTPS endpoint returning at least 50 show objects. |
| timeout | Positive finite requests timeout in seconds. |
| output_folder | Folder containing summary.json and run_info.json. Relative paths use the current working directory. |
| seed | Integer seed for a local random.Random instance. |
| sample_size | Number of show names sampled without replacement; between zero and the number of downloaded shows. |
| log_level | DEBUG, INFO, WARNING, ERROR or CRITICAL. |

No settings file is silently substituted for a missing or incomplete one. Invalid
ratings are excluded from calculations and logged as warnings; the show itself is
retained, preserving the original Lab 03 behavior. A seed and sample size are passed
explicitly by main, so custom configs do not accidentally use the default config.

## Errors and exit codes

| Error class | When raised | What the user sees |
| --- | --- | --- |
| TVSummaryError | Base class for expected package failures; subclasses identify the cause. | An ERROR log and a line starting `Error:` on stderr; exit 1. |
| DownloadError | Connection, timeout or HTTP status failure. | `Error: Could not download shows: ...` |
| ResponseShapeError | Invalid JSON, a non-list response, fewer than 50 records, or a non-object record. | `Error:` followed by a response validation explanation. |
| SettingsError | Missing, malformed, incomplete or invalid config; an oversized sample; or a missing required checking tool. | `Error:` followed by the setting or file that needs attention. |
| OutputError | A report directory or JSON file cannot be written. | `Error: Could not write summary or run info to ...` |

Exit **0** means both reports were written. Exit **1** means an expected failure;
no traceback is shown. main is the only application function catching package
exceptions. Low-level download, parsing and filesystem errors retain their cause
through `raise ... from error`. Unexpected programming errors are allowed to surface.
Argparse uses its normal exit 2 for invalid command-line syntax.

Check the failure path in PowerShell:

```powershell
python -m tvsummary.main --config config/does-not-exist.toml
$LASTEXITCODE
```

The diagnostic includes a line beginning `Error:` and the exit code is 1.
Logging is configured at the entry point; modules use named loggers and lazy `%s`
arguments. DEBUG reports response details, INFO reports milestones, WARNING reports
excluded invalid ratings, and ERROR reports expected failures.

## Reproducing a run

The seed lives in `config/tvsummary.toml`. `run_info.json` records every setting used,
the Python version and the installed pytest, mypy and Ruff versions. Install the
pinned requirements in the named Conda environment and use the same complete config.

Exactly reproducing `featured_shows` also requires **identical input records in
identical order**, the same sample size and seed, and a compatible Python runtime.
Sampling uses `random.Random(seed).sample`, so it does not modify global random state.
The live TVMaze API can change names, ratings and ordering. Preserve the raw API
response separately if you need an exact historical replay; a seed cannot freeze an
external service. Identical input preserves every original Lab 03 summary key and
value; the only additional summary key is `featured_shows`. Offline regression tests
check the complete legacy summary for handmade input.

For a clean-machine check, clone this repository into a different directory, create
the environment from environment.yml, install requirements and the package, run all
four checks above, run the app and check the missing-config failure. If the named
Conda environment already exists, use a distinct verification environment name:

```powershell
conda env create -f environment.yml -n tvsummary-lab04-check
conda activate tvsummary-lab04-check
python -m pip install -r requirements.txt
python -m pip install -e .
```

## What the tests cover

The offline suite covers missing genres and ratings, cleaning, rating boundaries,
each concrete aggregation with handmade records, empty inputs, source response
validation, HTTP/connection/JSON failures, exception causes, warning/info logs,
immutable validated settings, file output, CLI success and failure messages and
exit codes, same-seed sampling, global-random-state isolation and preservation of
all legacy summary values. Shared fixtures live in tests/conftest.py. Parametrized
cases, pytest.raises with match, tmp_path, monkeypatch, caplog and capsys are used.
An autouse guard fails any test that accidentally attempts a real requests.get.

Live-service uptime and current TVMaze ratings are deliberately not asserted by
unit tests: those are external, mutable conditions. The real application is also
run separately as an integration check.

## Known limitations

Only TVMaze page 0 is fetched and responses with fewer than 50 records are rejected.
Duplicate show names can appear in the featured list if different input records
share a name; sampling selects records without replacement. Set-based genre cleaning
removes duplicate genres per show. JSON outputs are written sequentially, so a later
run-info failure may leave a newly written summary beside older run metadata.
Run from the repository root for the default relative config and output paths.

## Repository history

Lab 03 remains unchanged in its original repository. This repository starts with
its unchanged .gitignore in a dedicated commit, followed by all remaining unchanged
Lab 03 files. This resolves the lab's conflicting instructions to put .gitignore
before code while retaining an unchanged Lab 03 starting point. Formatting and
import cleanup have their own commit, separate from behavior changes.

## Verification results

Verified on October 22, 2026, from a fresh clone in a separate folder and a newly
created `tvsummary-lab04-check` Conda environment. The pinned requirements and the
editable package installed successfully; pip check reported no broken requirements.
The imported package path pointed into the verification clone.

- Ruff format check: passed (20 Python files).
- Ruff lint: passed.
- Mypy: passed (9 package source files).
- Pytest: 61 offline cases passed.
- Real application: exit 0, 240 shows, both JSON reports written.
- Missing config: exit 1, an `Error:` line on stderr, no stdout or traceback.
- Original Lab 03 saved summary: every original key and value matched the new
  successful run exactly; only `featured_shows` was added.
