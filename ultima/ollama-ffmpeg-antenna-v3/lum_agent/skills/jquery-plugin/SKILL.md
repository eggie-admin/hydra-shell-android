# Lum Python-owned jQuery Plugin Skill

jQuery remains a JavaScript browser runtime. Python owns the plugin contract.

## Ownership

Python owns:

- plugin name and metadata,
- defaults,
- lifecycle state,
- validation,
- allowed public methods,
- JSON boundary,
- deterministic JavaScript wrapper generation.

The browser owns actual jQuery execution.

## Rules

- Plugin names and public method names must be valid JavaScript identifiers.
- Defaults cross the boundary through JSON only.
- Generated wrappers must be deterministic.
- Provider or AI text never becomes executable plugin code automatically.
- Plugin registration is explicit, not arbitrary import/discovery from writable directories.
- Browser code never owns provider keys or filesystem authority.
- All mutation-capable operations remain behind the Python policy gateway and human approval rules.
