# LuHm OS work lanes

Canonical integration trunk: `luhmos-main`

Work branches:

- `luhmos/ai-logic` — AI routing, agent policy, model/provider adapters, prompt/doctrine contracts, AI tests.
- `luhmos/frontend` — cockpit UI, web assets, Godot/WebView presentation layer, platform UI shells.
- `luhmos/backend` — Python/FastAPI control plane, jobs, media orchestration, persistence, API contracts.

Release promotion branches remain separate:

`luhmos/testing -> luhmos/proposed -> luhmos/beta -> luhmos/stable`

## Rules

1. New product work starts in exactly one work lane unless a change truly spans boundaries.
2. Work lanes branch from and merge back into `luhmos-main` through pull requests.
3. `luhmos-main` is the only integration trunk for cross-lane convergence.
4. Release channels do not receive feature development directly.
5. Promotion flows from `luhmos-main` into `luhmos/testing`, then proposed, beta, stable after CI/device gates.
6. Python 3 remains orchestration authority; frontend code does not gain shell authority.
7. AI logic may propose actions but must pass typed backend policy before mutation.
8. Frontend owns presentation only; secrets, provider credentials, signing material, and privileged operations remain outside frontend assets.
9. Backend owns state mutation, process control, API validation, and job lifecycle.
10. Cross-lane API changes require a versioned contract or coordinated PRs before promotion.

## Path ownership

AI logic primary paths:
- `lumh-os/**`
- `ultima/**`
- AI/router/provider modules under `backend/**`
- AI doctrine and model manifests under `project/hydra/**` and `docs/**`

Frontend primary paths:
- `backend/web/**`
- UI/cockpit assets and presentation code
- Godot/WebView presentation integration
- `platforms/**` UI shell staging

Backend primary paths:
- `backend/**` except frontend-owned `backend/web/**`
- `tools/**`
- service/runtime tests
- control-plane manifests and API contracts

Shared paths such as `.github/**`, `release/**`, `project/hydra/**`, and platform packaging files require integration review on `luhmos-main`.

## Pull-request direction

- `luhmos/ai-logic` -> `luhmos-main`
- `luhmos/frontend` -> `luhmos-main`
- `luhmos/backend` -> `luhmos-main`
- `luhmos-main` -> `luhmos/testing`
- `luhmos/testing` -> `luhmos/proposed`
- `luhmos/proposed` -> `luhmos/beta`
- `luhmos/beta` -> `luhmos/stable`

No reverse promotion and no direct stable feature merge.
