# Lum Python Debugging Skill

Use the cheapest deterministic checks first.

## Debug ladder

1. Syntax/import compile: `python3 -m compileall -q src tests` or focused `python3 -m py_compile FILE.py`.
2. Formatting/lint: `ruff check .` and `ruff format --check .`.
3. Types: `mypy src`.
4. Focused unit test for the changed behavior.
5. Broader `pytest -q` or unittest suite.
6. Project doctor command.
7. Integration smoke for filesystem, network, Android, provider, database, or external service boundaries.

Do not jump to a costly integration test when syntax or a focused unit test can reproduce the problem.

## Reproduction rule

A bug is not fixed until either:

- a deterministic test reproduces the old failure and passes after the correction, or
- a deterministic command demonstrates the old failure and the corrected behavior.

## Exception context

When an exception crosses a subsystem boundary, preserve:

- operation name,
- component name,
- safe identifiers/metadata,
- root exception using `raise ... from exc`.

Never put secrets or raw authorization headers into exception text or debug metadata.

## No fake green

Compilation proves syntax/import viability only. A unit test proves only its asserted behavior. CI green is not live-deployment green. State the exact gate that passed.
