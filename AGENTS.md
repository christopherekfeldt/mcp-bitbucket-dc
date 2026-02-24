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
- `.github/workflows/`: CI (`test.yml`) and publish (`publish.yml`).

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

Publishing is tag-driven via GitHub Actions (`publish.yml`):

1. Ensure tests are passing.
2. Create annotated semver tag (example):
   ```bash
   git tag -a v0.5.0 -m "v0.5.0"
   git push origin v0.5.0
   ```
3. Wait for the `Publish to PyPI` workflow to run after tag push.

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
