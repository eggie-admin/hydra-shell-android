# LuHm OS Modular Sprite Cockpit

`KAI9000_LUHM_MODULAR_SPRITE_COCKPIT_20260916`

Status: SOURCE IMPLEMENTATION CANDIDATE
Authority: Professor

## Purpose

LuHm OS uses an original modular cockpit inspired by the general idea of compact dockable media/control shells, without copying Winamp skins, artwork, branding, layout files, or proprietary assets.

The canonical presentation scales are:

```text
SPRITE_BUBBLE <-> WIDGET_DECK <-> FULL_COCKPIT
```

Changing scale changes presentation only. One stable session/state tree survives minimize/restore.

## Realms

### GAME

Pet interaction, original folklore/JRPG presentation, quests, collection/cosmetics, gacha/date surfaces, and Personal Reckoning Parley.

### ADMIN

Crown evidence, source-of-truth, update staging, logs, provenance, security/recovery status, CI/build evidence, and explicitly gated machine-operation requests.

### SYSTEM

Neutral local application status and health information.

The GAME -> ADMIN firewall is absolute. GAME state, affection, rolls, gacha, folklore form, Crossweave, Parley consensus, or dramatic dialogue cannot create ADMIN authority.

## State Pass

Canonical machine state:

```text
mode=SPRITE_BUBBLE|WIDGET_DECK|FULL_COCKPIT
realm=GAME|ADMIN|SYSTEM
active_widget=widget_id|null
return_target=SPRITE_BUBBLE|WIDGET_DECK|FULL_COCKPIT
session_id=stable current session
state_pass=true
pending_reckoning=false|typed intent reference
layout_profile=portrait_phone|tablet|desktop
tier=WHISPER|CROSSING|RECKONING
```

State-pass requirements:
- minimizing/maximizing preserves `session_id`;
- the active widget and safe presentation state survive round trips;
- transitions do not duplicate jobs;
- transitions do not resend prompts;
- transitions do not restart services;
- transitions do not replay mutations;
- safe persisted state does not serialize arbitrary unknown secret fields.

## Widget contract

Every widget declares:

```text
widget_id
version
surface
mount_point
allowed_events
subscribed_state_keys
emitted_intents
required_tier
authority_ceiling
provenance_ref
ship_allowed
reduced_motion
```

Current source candidate defines PET, QUEST, PARLEY, STATUS, MEDIA, UPDATE, CROWN, and LOG.

Presentation emits typed allowlisted intents only. JavaScript/WebView code may not execute arbitrary shell, evaluate model-authored code, silently cross GAME -> ADMIN, or self-authorize RECKONING.

## Folklore Crossing binding

Active tiers:
- WHISPER: read/inspect/presentation only;
- CROSSING: reversible Mirror Route staging;
- RECKONING: consequential mutation requiring exact Professor authorization.

A RECKONING-capable UI control may only stage a `pending_reckoning` record. It does not execute the action.

## Personal Reckoning binding

Every material Parley view preserves:
- ROLEPLAY VOICE;
- literal TRUTH STRIP;
- structured MACHINE ENVELOPE.

Default budget:

```text
OPEN -> COUNTER -> RECKON
```

The source candidate hard-caps the default exchange at three rounds. No hidden agent call, hidden backchannel, recursive debate loop, or autonomous swarm is created by the UI.

## Android and overlay boundary

The sprite bubble is an in-app surface. It is not a system-wide draw-over-other-apps overlay by default. Picture-in-Picture, accessibility, notification-listener, foreground overlay, or similar Android special capabilities require a separate permission/security mutation and physical-device proof.

## Source files

```text
project/hydra/samsung/android/cathedral-game/final-form.js
project/hydra/samsung/android/cathedral-game/final-form.css
project/hydra/samsung/android/cathedral-game/modular-cockpit.css
project/hydra/samsung/android/cathedral-game/tests/modular-cockpit.test.mjs
```

The existing 1.0.5 signed Crown Gate build remains the sealed build baseline. This source candidate does not silently change versionCode, signer, update channel, or public-release state.

## Source GREEN gate

Source readiness requires all of the following:
- JavaScript syntax check passes;
- widget required-field contract passes;
- SPRITE_BUBBLE -> WIDGET_DECK -> FULL_COCKPIT -> SPRITE_BUBBLE state-pass test passes with stable `session_id`;
- GAME requesting an ADMIN mutation returns `DENY_REALM_FIREWALL`;
- ADMIN RECKONING intent is staged with `executed=false`;
- Parley stops at three default rounds;
- safe serialization excludes unknown token/key-like fields used by the test fixture;
- source contains no `eval`, `new Function`, XMLHttpRequest, WebSocket, or EventSource execution lane;
- modular CSS supplies reduced-motion behavior;
- active repository doctrine uses WHISPER/CROSSING/RECKONING and demotes ULTIMA to historical compatibility;
- no compile, signing, install, merge, publication, or physical-device GREEN is inferred from source-test success.

## Next gates after source seal

A later explicitly authorized RECKONING may create the next signed APK candidate. Only then may forge/signature/package/alignment evidence be refreshed. Physical Samsung install, launch, transitions, firewall behavior, save/reload, Secure Folder, and reboot continuity remain separate hardware gates.

The modular cockpit can be SOURCE_GREEN before it is BUILD_GREEN or DEVICE_GREEN. That distinction is intentional.
