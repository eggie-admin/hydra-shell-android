# Lum Agent Skill Chain

Canonical in-app flow:

```text
User request
  -> Prime doctrine
  -> task classification
  -> load only relevant skill(s)
  -> read-only evidence tools
  -> Python AST/source inspection when coding
  -> deterministic compile/test evidence
  -> proposal
  -> deterministic application approval gate for mutation
  -> execution
  -> exact result/evidence
```

## Python coding defaults

1. `prime`
2. `python-core`
3. `python-debug` when diagnosing failures
4. `json-boundary` when data crosses process/language/API boundaries
5. `jquery-plugin` when the Python-owned browser plugin contract is involved
6. `android-backend` when Samsung/antenna/provider boundaries are involved

## Non-negotiable rules

- Read before write.
- AST/source evidence before structural Python claims where practical.
- Compile is not an integration test.
- A proposed spell is not execution.
- No agent self-approval.
- No ULTIMA self-cast from the in-app agent.
- No secrets in source, prompt doctrine, client code, logs, or agent state.
- Failed or missing evidence is reported as red/yellow, never silently promoted to green.
