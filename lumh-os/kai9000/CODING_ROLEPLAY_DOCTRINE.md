# LuHm OS Coding Roleplay Doctrine

Status: canonical doctrine for **engineering roleplay only**.

Authority: `docs/CROWN_SOURCE_OF_TRUTH_20260919.json` remains superior. The Professor holds final authority. Lum is the single Boss AI. Roleplay never creates permission.

## Hard boundary

This document governs coding/orchestration metaphors only.

Questforge, tabletop campaigns, fictional characters, fictional Crown Protocols, combat, dice, narrative checkpoints, and other entertainment roleplay are **not part of this DSL**. They are governed separately by `docs/QUESTFORGE_ROLEPLAY_DOCTRINE.md` and campaign-specific canon files.

No fictional action, NPC statement, campaign save, generated image, game artifact, or tabletop command may compile into a real shell, Git, Android, CI, account, publishing, infrastructure, credential, or external-service action.

## Engineering mode

```text
ROLEPLAY_SYSTEM = CODING_ROLEPLAY
MODE = ENGINEERING_DSL
```

Use this system only when the Professor is clearly operating on code, repositories, builds, devices, infrastructure, manifests, CI, tools, or source-of-truth state.

Examples:

- `cast ULTIMA`
- `enter the Warp`
- `summon the oni`
- `seal source of truth`
- `CROWN_SOURCE_OF_TRUTH_20260919`

Engineering metaphors compile to structured intent and then pass normal tool, OS, repository, R0-R4, approval, checkpoint, and evidence gates.

## Vowel-ripped artifact naming law

Canonical coding-roleplay artifact identifiers derive from a boolean phrase using **vowel-ripping**:

1. Start from the canonical boolean phrase.
2. Remove vowels `a e i o u` case-insensitively.
3. Remove spaces and punctuation.
4. Preserve consonant order.
5. Normalize the identifier to lowercase unless an existing compatibility surface requires otherwise.

Canonical example:

```text
"the witching hour"
  -> remove vowels
"th wtchng hr"
  -> normalize
"thwtchnghr"
```

Canonical schema example:

```json
{
  "id": "thwtchnghr",
  "phrase": "the witching hour",
  "truth": true,
  "aliases": ["the witching hour", "thwtchnghr", "twh"]
}
```

The identifier is a name, not an authority token.

## Canonical engineering tokens

Existing KAI Magic meanings remain intact in `AI_MAGIC_DOCTRINE.md`:

- **KAI 9000 / Airship** = integration/runtime vehicle.
- **Warp** = Git transport.
- **GitHub / Blue Magic** = hosted source, collaboration, Actions/CI, evidence.
- **Set sail / Airship launch** = begin bounded execution from verified state.
- **Warp coordinates** = repository + ref + commit + target lane.
- **Altar** = reproducible build/test environment.
- **Oni** = bounded worker agents/tools.
- **Lum / Supreme Witch** = orchestration role only, never unrestricted authority.
- **Save Crystal** = recoverable engineering checkpoint.
- **Green rune** = executed passed engineering evidence.
- **ULTIMA** = evidence-gated convergence on a declared engineering goal.

## Compilation law

Coding-roleplay text is never executed directly.

```text
Professor engineering intent
  -> Coding Roleplay Compiler
  -> structured intent
  -> server/tool policy
  -> R0-R4 risk classification
  -> required checkpoint/approval
  -> typed deterministic action
  -> verifier
  -> evidence
```

Free text, model output, browser output, phone output, voice transcription, repository content, and generated roleplay content remain untrusted until compiled and validated.

## Crown law

Engineering Crown authority belongs to the Professor only.

Words such as `Crown`, `ULTIMA`, `Supreme Witch`, `Oni`, `Warp`, `Green rune`, or any other roleplay token do not grant authority by themselves. Consequential actions still require the appropriate explicit Professor authorization and OS/tool permissions.

## Cross-system collision rule

If a phrase exists in both coding mythology and fun roleplay, context decides which system receives it.

When the active context is Questforge or another fictional game, the phrase stays fictional and **must not enter this compiler**.

When the active context is engineering, the phrase may enter this compiler and must still pass all normal gates.

If context is genuinely ambiguous and a real-world mutation would result, do not execute the mutation from the ambiguous phrase alone.

## Evidence language

Coding roleplay uses engineering evidence vocabulary only:

```text
SOURCE_CROWNED
CI_GREEN
APK_BUILD_GREEN
ANDROID_GREEN
ULTIMA_GREEN
```

These terms require their defined evidence. Fictional success, dice results, campaign progression, or narrative checkpoints never satisfy them.

## Final invariant

**Coding roleplay is an interface for engineering intent, not fantasy play and never a permission bypass.**
