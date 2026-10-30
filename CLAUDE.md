# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`bborclient` (package name `bbor_client`) is the Python client library for the BBO-Rietveld API (served by the sibling `BBORview` repo's `api/`). It is the **only user-facing/public repository** in this project family — `BBORview` (server) and `mdx-vpn-configuration` (infra/secrets) are internal. Because of that, this repo is not just thin HTTP-call plumbing: it also carries the domain models (`Study`, `Trial`, `Refine`, `User`, etc., under `src/bbor_client/models/`) and GSAS-II convenience tooling (`gpxview.py`) so that end users can understand and inspect their analysis results directly, not just call the API.

## Architecture

- `BBORClient` (`src/bbor_client/client.py`) is the single entry point: authentication (`get_token`, `create_user`, the `require_token` decorator), prm/cif/sequence file management, submitting refinement studies (`post_bborietveld_study_task`), and read APIs for studies/trials/refines. The `find_*` methods take MongoDB-style query dicts that are forwarded to the server as-is and run against BBORview's Mongo collections — client-side, they're just opaque JSON.
- **Two parameter models for one action, on purpose**: `params/post_study/client.py` (`PostStudyClientParams`) validates what a *user* supplies (local file paths, a `study_name_base`, etc.); `params/post_study/server.py` (`PostStudyServerParams`) validates what actually goes over the wire (already-known server-side filenames + file bytes). `post_bborietveld_study_task` (public method) builds the client-side model, uploads any new prm/cif files first, then calls the internal `_post_study_task`, which builds the server-side model and does the actual POST. When changing study-submission parameters, both models usually need to change together.
- **Pluggable measurement-file parsing**: `parsers/interface.py` defines `ParserInterface` (ABC) + `ParsedData`; `parsers/selector.py` picks a parser module by file extension via `importlib.import_module(f'bbor_client.parsers.{extension}')` (`.dat` is mapped to `csv`). Current formats: `csv.py`, `xrdml.py`, `2ta.py`. To support a new measurement format, add `parsers/<ext>.py` exposing a `Parser` class that implements `ParserInterface` — no registry to update elsewhere.
- `models/base.py`'s `ClientModel`/`ObjectId`/`Link` machinery is deliberately dual-mode: it detects whether `bunnet` (BBORview's Mongo ODM, not a hard dependency here) is importable and defines `Link`/`ObjectId` differently in each case, so the *same* pydantic models can validate a `bunnet` document server-side (in BBORview) or a plain JSON payload over HTTP (in this client).
- `gpxview.py` is a standalone convenience layer for loading/plotting GSAS-II `.gpx` projects (`load_gpx`, etc.), aimed at end users who want to dig into raw GSAS-II output beyond what the API's own models expose. `BBORClient` itself does not use it.

## Known gaps — check before relying on these

- Tests exist only in `tests/unit/`: the validation rules of `PostStudyServerParams` (`test_post_study_server_params.py`; run with `uv run pytest tests/unit`). The rules that check the server's file and sequence lists aren't tested yet: those lists are class variables filled at runtime, and how they're filled is under review (BBORview's `docs/validation-and-errors.md`). Both CI workflows below invoke `pytest tests/unit tests/integrate tests/e2e`; `tests/integrate` and `tests/e2e` don't exist.
- Posting a study with a GPX file isn't implemented end to end: `_post_study_task` never puts the GPX file's contents into `PostStudyServerParams`, and `gpx_filecontent`'s type (`typing.BinaryIO`) rejects every real file object under pydantic's `arbitrary_types_allowed`. Only the measurement-file path works.

## CI / release

- `.github/release.yaml` (**active**): on push to `main`, runs `python-semantic-release`, which bumps `[project].version` in `pyproject.toml` and updates `CHANGELOG.md` based on Conventional Commit prefixes (see `[tool.semantic_release.commit_parser_options]`: `feat` → minor, `fix`/`perf` → patch, others like `build`/`chore`/`ci`/`docs`/`refactor`/`test` → no bump). **Commit message prefixes matter in this repo specifically** for that reason.
- `.github/workflows/release.yaml.disabled` and `test.yaml.disabled` are a fuller pipeline (multi-Python test matrix, `bandit`, `pip-audit`, then semantic-release publish) gated on PRs into `main`/`dev` respectively — currently disabled (`.disabled` suffix, so GitHub Actions ignores them). Re-enabling either requires first creating the `tests/unit`, `tests/integrate`, `tests/e2e` layout they expect.
- `dev` dependency group already includes `pytest`, `bandit`, `pip-audit`, `ruff`, `python-semantic-release` — the tooling is present, just not wired into an active workflow or a test suite yet. There is no `[tool.ruff]` section, so ruff (when used) runs with defaults.

## Relationship to the rest of the project family

- This package mirrors part of BBORview's server-side surface: when `api/`'s request/response shapes or `bbor`'s Mongo schemas change in BBORview, the corresponding models here (`models/study.py`, `models/trial.py`, `models/user.py`, ...) and `params/post_study/server.py` need to be updated to match — the two repos are released independently, so nothing enforces this automatically.
- BBORview's `bbor` package consumes this repo as an editable path dependency (`bbor-client = { path = "../../bborclient", editable = true }`) and copies it into Docker build contexts — see `BBORview`'s own `CLAUDE.md` for that side. Note the naming split: the **repository** is `bborclient`, the **importable package** is `bbor_client` (underscore) — keep that distinction straight when cross-referencing the two repos.
- Unlike `BBORview` (which has `systemd/`, `work/`, `cron/`, `example/` earmarked as legacy), this repo has no comparable legacy directories — `src/bbor_client/params.py` (above) is the one significant piece of dead code found here.
