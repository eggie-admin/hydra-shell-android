---
applyTo: "project/hydra/**,tools/**,.github/workflows/**,.github/agents/**,.github/instructions/**"
---

# Project Hydra enterprise operating instructions

Treat `project/hydra/runtime/enterprise.policy.json` as the active canonical enterprise operating contract, subordinate to the newest applicable Crowned source-of-truth.

For enterprise-directed work:

- resolve exact branch/head and newest applicable Crown once;
- prefer immutable `path@sha` references over repeated reads;
- keep proposal, canonical source, release candidate, and public release as separate states;
- build once and promote by immutable digest instead of rebuilding after approval;
- require exact-head CI before human promotion;
- require package/version/hash/signer/SBOM/provenance/device proof before calling an Android release candidate complete;
- preserve least-privilege workflow permissions and immutable action pinning;
- never put secrets, signing material, tokens, or private runtime data in source, HTML assets, proof payloads, or logs;
- keep Lum as the single parent writer; helpers remain read/search only by default;
- never let AI output execute directly in a shell and never let model consensus create authority;
- benchmark before speed claims and record source SHA, artifact hash, startup/TTFT where applicable, throughput where applicable, memory, and thermal notes;
- preserve checkpoint/rollback evidence for consequential mutation;
- treat branch protection/rulesets, release signing, public publication, deployment, DNS, and billing as separate human-controlled gates.

Do not describe the project as compliant, certified, SOC 2, ISO 27001, HIPAA, FedRAMP, or equivalent unless a real external certification or audit supports that claim.
