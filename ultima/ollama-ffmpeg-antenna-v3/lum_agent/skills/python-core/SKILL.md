# Lum Python 3 Core Skill

## Layout

Use a `src/` layout for reusable libraries. Keep tests outside the package. Keep shell helpers under `scripts/`. Keep generated artifacts, caches, runtime state, and secrets out of source control.

## Classes

- Prefer dataclasses for state containers.
- Use normal classes for behavior.
- Prefer composition before inheritance.
- Reserve abstract base classes and protocols for stable extension boundaries.
- Keep constructors cheap and unsurprising.

## Functions

- One job per function.
- Typed inputs and outputs.
- Pure functions in the core where practical.
- Put filesystem, subprocess, network, database, and provider calls at explicit boundaries.
- Raise domain-specific exceptions and chain root causes with `raise ... from exc`.

## Variables

- Module constants are `UPPER_CASE`.
- Mutable state lives in an explicit object or context, not mystery globals.
- Use local variables normally. Do not wrap every value in framework state.
- Configuration comes from typed settings or environment boundaries, never embedded secrets.

## Collections

- `list[T]` for mutable ordered collections.
- `tuple[T, ...]` for immutable sequences/records.
- `collections.abc.Sequence[T]` for read-only API inputs.
- `dict[str, T]` only when the mapping is truly dynamic. Prefer dataclasses or typed models for stable records.
- Use `array.array` or specialized numeric libraries only when compact numeric storage materially matters.

## JSON

JSON is the default language-neutral boundary:

DECODE -> VALIDATE -> TYPED PYTHON -> OPERATE -> ENCODE

Do not let unvalidated dictionaries leak through the core.

## SDK boundaries

SDK request/response contracts belong in adapter modules. Transport-specific details must not leak into business logic.

## Typing and stubs

- Type public functions and methods.
- Ship `py.typed` for typed packages.
- Use `.pyi` stubs for intentionally separated public typing surfaces or foreign/runtime boundaries.
- Prefer `Protocol` where structural typing avoids unnecessary inheritance.

## Python coding pass

1. Understand the existing module and tests.
2. Outline classes/functions with AST or source inspection.
3. Make the smallest coherent change.
4. Compile.
5. Run focused tests.
6. Run broader lint/type/test gates only when justified.
7. Report exact evidence and unresolved risks.
