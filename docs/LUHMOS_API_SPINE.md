# LuHm OS API Spine v1

Status: candidate, non-breaking unification.

LuHm OS now has one canonical application API namespace: `/api/v1`. New clients target this namespace. Existing API surfaces remain available only as compatibility or component planes during migration.

## Canonical front door

- `GET /api/v1/health`
- `GET /api/v1/status`
- `GET /api/v1/providers`
- `GET /api/v1/capabilities`
- `POST /api/v1/assist/plan`
- `POST /api/v1/assist/query`
- `POST /api/v1/ai/chat`
- `POST /api/v1/providers/route`

The composition root is `ultima/ollama-ffmpeg-antenna-v3/magic_server.py`; the canonical contract router is `api_spine.py`.

## Authority boundary

Provider output is advisory data. The Professor remains final authority. Lum is the single parent writer. Default helper recruitment is zero. An explicit mesh may use at most two read-only helpers with delegation depth one. Helpers cannot recursively recruit and consensus never grants authority.

No API route grants release, signing, deploy, DNS, billing, shell, or Crown authority. Credentials stay server-side and outside client payloads, repository content, and distributable Android assets.

## Compatibility planes

The previous `/api/assist/*`, `/api/remote-ai/*`, antenna gateway, media `/api/*`, widget CMS `/api/pages*`, and local Flask `/v1/*` routes remain intact for compatibility. They are not the namespace for new clients and should not grow new cross-project responsibilities.

This migration intentionally avoids a big-bang deletion. Compatibility routes can be retired only after consumers are inventoried and migrated with evidence.

## Provider spine

The vendor adapter catalog remains OpenAI, Google, GitHub, Cloudflare, and Hugging Face. Only bounded reasoning adapters participate in AI calls. GitHub provides versioned evidence/context, Cloudflare is edge transport, and no provider silently inherits another provider's authority or receives a prompt through silent cross-provider failover.

## Green definition

`tools/api_spine_guard.py` verifies the canonical prefix, route registry, provider catalog, composition root, compatibility policy, and the sealed LuHm coding-roleplay limits. Static GREEN proves the repository contract only. It does not prove live provider credentials, external IAM, edge state, deployment, signing, or physical-device operation.
