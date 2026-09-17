# LuHm Agent Mesh v1

Seal: `LUHM_AGENT_MESH_V1_20260917`

## One Boss

`Lum` is the only user-facing agent identity. Lum owns conversation, intent normalization, Crown/tier interpretation, routing, structured state, and final synthesis.

## Three default blades

- `CONTEXT` retrieves the minimum relevant source-of-truth/evidence references.
- `BUILD` inspects code/build/test evidence and returns compact findings.
- `RESEARCH` obtains current external evidence when freshness is required.

## Conditional blade

`CRITIC` checks consequential or multi-source work for contradiction, authority drift, stale proof, and false-green claims.

## Deterministic edge

`TOOL_EXECUTOR` is an allowlisted typed edge. It does not interpret roleplay or self-authorize. Consequential work remains RECKONING and needs exact Professor authorization before the edge may be opened.

## Hard rules

1. Boss speaks to Professor. Helpers speak to Boss.
2. Helpers never recursively recruit helpers.
3. Direct questions bypass the mesh.
4. Default helper count is zero.
5. Maximum helpers per turn is three.
6. Maximum parallel read-only helpers is two.
7. Delegation depth is one.
8. Helper history is `NONE`; helpers receive minimum typed TaskPackets and EvidenceRefs.
9. AI-to-AI talk is capped at three rounds.
10. FOR LOOP evidence passes are capped at ten and NULL never becomes GREEN.
11. Provider capability never changes Crown authority.
12. Public publish is OFF by default. No secret may be embedded in TaskPackets, receipts, logs, or APK assets.

## API role split

The policy core is provider-independent. The intended adapter boundary is:

- fast interactive/tool work: Responses-style adapter;
- managed long-horizon work: Agents-style adapter;
- local/custom Python orchestration: Agents-SDK-style adapter.

Those adapters are not implemented in this first candidate. This keeps the policy contract testable without API keys, network access, or provider lock-in.

## Debug candidate purpose

The Android debug candidate mirrors these deterministic routing rules in an offline Godot screen. It is a logic/proof harness, not a live OpenAI client. It must use a separate debug package identity so it can coexist with canonical LuHm OS and cannot silently replace the stable handoff.

Run locally:

```bash
python3 project/hydra/openai/lum-agent-mesh/test_mesh.py
python3 project/hydra/openai/lum-agent-mesh/mesh.py --smoke
```

Expected milestone progression:

`SOURCE_GREEN -> SIGNED_DEBUG_BUILD_GREEN -> AMBER_INSTALL_CANDIDATE -> DEVICE_DEBUG_PROOF -> GREEN`
