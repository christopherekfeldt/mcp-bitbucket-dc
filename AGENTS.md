# AGENTS.md

Guidance for AI agents and contributors working in this repository.

## Purpose

- Keep changes minimal, focused, and easy to review.
- Prefer root-cause fixes over surface patches.
- Preserve existing public behavior unless the task explicitly requires change.

## Repository Map

- `src/mcp_bitbucket_dc/`: server, client, config, models, formatting, and tool modules.
- `src/mcp_bitbucket_dc/tools/`: user-facing Bitbucket tool implementations.
- `tests/`: unit tests and integration smoke tests.
- `.github/workflows/`: CI (`test.yml`), publish (`publish.yml`), and release (`release.yml`).

## Local Setup

```bash
uv sync
uv run pre-commit install
```

Required env for real Bitbucket calls:

- `BITBUCKET_HOST` **or** `BITBUCKET_URL`
- `BITBUCKET_API_TOKEN`

## Day-to-Day Workflow

1. Understand scope from user request.
2. Read only relevant files first.
3. Implement the smallest viable change.
4. Run targeted checks, then broader checks if needed.
5. Update docs when behavior, tools, or workflows change.

## Coding Guidelines

- Match existing style and naming patterns.
- Avoid unrelated refactors.
- Do not add dependencies unless clearly justified.
- Keep tool output formatting consistent (`markdown` vs `json` behavior).
- Do not hardcode environment-specific values.

## Testing and Validation

Start narrow, then expand:

```bash
uv run pytest -q
```

Integration smoke tests (real/staging Bitbucket):

```bash
RUN_LIVE_SMOKE=1 uv run pytest -m integration -q
```

Lint/format checks via pre-commit hooks:

```bash
uv run pre-commit run --all-files
```

## Release Workflow

Releases are automated via `release.yml` (workflow dispatch):

1. Ensure tests pass and PR is merged to `main`.
2. Go to **Actions → Release → Run workflow**.
3. Enter the version (e.g. `1.0.0`) and optionally enable dry run.
4. The workflow runs tests, creates the git tag, publishes to PyPI, and creates a GitHub Release with auto-generated notes.

The legacy `publish.yml` still works as a fallback (triggered by manual tag push).

## Documentation Expectations

- Keep `README.md` accurate for install, config, tools, and release notes.
- Keep acknowledgements and external references public and accessible.
- Add short usage examples for new tools when practical.

## PR Checklist

- Scope is limited to requested change.
- Tests/lint pass for changed areas.
- Docs updated if needed.
- No secrets, tokens, or private URLs committed.

## Notes

- If `.claude/napkin.md` exists, keep it curated as a high-signal runbook (not a session log).
