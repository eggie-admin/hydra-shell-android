# LuHm Crown Gate

`KAI9000_LUHM_CROWN_GATE_V1`

The Crown Gate is the final evidence boundary for LuHm OS. It exists so the UI can be theatrical without the engineering becoming theatrical.

## Authority chain

1. **Professor** authorizes consequential actions.
2. **Lum** plans, inspects, challenges assumptions, keeps source-of-truth alignment, and refuses fake GREEN.
3. **GitHub Actions** proves source can compile and produces signed build evidence.
4. **Android** enforces package identity, signer continuity, version monotonicity, and user-confirmed installation.
5. **Physical hardware** proves launch, persistence, Secure Folder behavior, reboot behavior, and runtime integrations.

## Crown states

- `SOURCE_GREEN`: canonical package/build doctrine matches source.
- `AGENT_GREEN`: Lum authority/secret/no-self-approval tests pass.
- `FORGE_GREEN`: APK build, signing identity, 16 KiB alignment, ABI, SDK levels, and bundled assets pass CI.
- `UPDATE_GREEN`: same package + same signer + higher versionCode contract passes.
- `DEVICE_GREEN`: current candidate is physically installed and launched on target hardware.
- `PERSISTENCE_GREEN`: save/reload and reboot observations are physically proven.

`FULL_GREEN` means every required state for the claimed scope has executed evidence. A UI button, role-play state, document, or previous build never substitutes for runtime proof.

## Public release rule

Public publishing is opt-in and manual-only. Normal pushes, merges, tests, and private update builds must not publish public APKs or a public F-Droid mirror.

## Asset rule

Only KAI/LuHm-owned or explicitly redistribution-cleared assets may ship in a generally distributable APK. Community assets remain third-party and retain author/license/commit receipts. Unknown or mixed-provenance packs remain quarantined.

## Final-form cockpit

The in-app Crown panel is an offline evidence ledger. It can display immutable build facts and locally remembered human confirmations. It must not perform background network checks, execute shell commands, claim socket health it cannot observe, or self-award FULL GREEN.

The crown is a gate, not a shortcut.
