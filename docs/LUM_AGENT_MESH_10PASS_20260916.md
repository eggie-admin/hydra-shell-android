# LuHm OS Lum Agent Mesh 10-Pass Candidate

Status: CANDIDATE / DRY-RUN GREEN TARGET
Date: 2026-09-16
Authority: Professor

## Goal

Keep Lum as the single user-facing boss while using small deterministic helper stages to prepare RSS/XML or JSON evidence for one bounded OpenAI agent call.

This is intentionally not a peer-to-peer swarm. Helpers do not recursively recruit helpers. Ten passes are logic stages, not ten paid model calls.

## Pipeline

```text
RSS URL (HTTPS allowlist) | inline RSS/XML | inline JSON items
        |
        v
01 INPUT GATE
02 INGEST
03 NORMALIZE JSON
04 DEDUPE
05 RELEVANCE RANK
06 PROVENANCE GATE
07 CONTEXT BUDGET
08 BOSS ROUTE
09 REMOTE AI (Lum boss, max 1 model call)
10 FINAL GUARD
        |
        v
structured result + evidence + pass trace
```

Endpoint:

```text
POST /api/lum/mesh
```

The existing `/api/lum/chat` endpoint remains unchanged for direct chat.

## Boss routing

Fast/default:

```text
model: gpt-5.6-luna
reasoning: none
max turns: 4 for mesh synthesis
```

Deep/escalated:

```text
model: gpt-5.6-sol
reasoning: medium
max turns: 6 for mesh synthesis
```

The deep route is explicit (`deep=true`) or selected only when the evidence packet crosses the configured complexity threshold.

## RSS network law

Remote RSS fetching is disabled unless the source hostname is explicitly listed in:

```text
LUM_RSS_ALLOWED_HOSTS
```

Network feed URLs must use HTTPS. Redirects are not followed. Feed byte size, timeout, and context character budgets are bounded. Inline RSS/XML and inline JSON remain available for deterministic tests without network access.

## Secret boundary

`OPENAI_API_KEY` remains protected runtime material. It is not returned to clients and does not enter the RSS packet.

Before the normalized evidence packet reaches the Lum boss, the existing LuHm secret-shaped-content guard is run again as an egress check.

## Authority law

The mesh is advisory analysis. It cannot self-authorize mutation, release, signing, publishing, root, shell, or device actions. Provider output is evidence/data until LuHm policy validates it.

## Efficiency law

Normal path:

```text
10 bounded logic passes
0 or 1 remote model calls
max 25 selected items
bounded evidence characters
one final Lum synthesis
```

No provider failover occurs silently. No second model is invoked merely to repeat the first model's work.

## Candidate acceptance

Promote only after:

1. Python compile/test gate is GREEN.
2. Existing Lum agent tests remain GREEN.
3. New ten-pass JSON dry-run test is GREEN.
4. New inline RSS normalization test is GREEN.
5. Existing authority/secret guards remain GREEN.
6. No-key mode makes zero remote model calls.
7. Optional live OpenAI smoke call is separately authorized because it is billable external execution.

Public publish: OFF.
