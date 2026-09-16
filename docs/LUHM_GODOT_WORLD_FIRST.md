# LuHm OS Godot World First

`LUHM_OS_GODOT_WORLD_FIRST_HUD_1.0.7`

Status: ACTIVE 1.0.7 MUTATION CANDIDATE
Human authority: Professor

## Canonical presentation law

The Godot 4 world owns the screen.

```text
NATIVE GODOT WORLD
    ↓
MINIMAL CANVASLAYER HUD
    ↓ tap Lum
LUM MICRO MENU
    ↓ explicit CROWN
FULL WEBVIEW COCKPIT
```

The old cockpit is preserved as an explicitly summoned ADMIN surface. It is no longer the automatic first layer.

## Persistent HUD budget

Only these elements remain permanently available over the world:

- quest sigil;
- map ping;
- one context action;
- floating Lum icon;
- tiny status line.

Everything else is contextual or hidden until summoned.

## Gameplay absorbs the old menu

- EXPLORE becomes world navigation.
- CONTACT becomes a proximity/context action.
- BOND becomes a character interaction.
- FUSION becomes a shrine/ritual interaction.
- DATE becomes an event/quest trigger.
- REST becomes a place/object interaction.
- SAVEPOINT becomes a world save terminal/crystal.
- UPDATE, CROWN, and LOG remain ADMIN-only cockpit functions.

## Authority firewall

Godot GAME state cannot create ADMIN authority. Lum, affection, D20, quest success, Parley consensus, world progress, or a HUD interaction cannot self-authorize RECKONING.

The full cockpit opens only from the Lum micro menu after an explicit user CROWN gesture. `cockpit_auto_open=false` is part of the 1.0.7 build contract.

## Native world implementation

The source candidate uses Godot-native 3D primitive geometry plus LuHm-original SVG character art. The first zone is an original `Corktown Switchyard` cathedral-tech diorama with rails, neon markers, procedural industrial blocks, cathedral geometry, a floating Lum guide, and minimal world-space interaction prompts.

No private-reference gacha/mod asset is bundled into the public repository or APK by this mutation. The rights firewall remains unchanged.

## Current source paths

```text
project/hydra/samsung/android/cathedral-game/godot-world/
├── WORLD_FIRST_MANIFEST.json
├── scenes/main.tscn
├── scripts/world_first.gd
└── assets/
    ├── lum_world_sprite.svg
    └── lum_hud_icon.svg
```

The existing modular WebView cockpit remains under `cathedral-game/` and is packaged as the explicit admin overlay.

## 1.0.7 build contract

- package `art.eggiebagelface.luhmos`
- version `1.0.7` / versionCode `107`
- minSdk 24
- targetSdk 36
- arm64-v8a
- portrait-first
- same persistent release signer as 1.0.6
- Android confirmation required
- silent install false
- public publish OFF/manual only

## GREEN ladder

`SOURCE_GREEN` requires static source tests plus successful Godot headless parse/runtime smoke.

`FORGE_GREEN` requires signed APK export, same signer, version monotonicity, SDK/ABI checks, 16 KiB alignment, packaged cockpit/update assets, and no forbidden secret/private-reference ingress.

`DEVICE_GREEN` requires physical Samsung install/update, launch into the native Godot world, visible minimal HUD, Lum micro menu, explicit cockpit summon, and world/cockpit return behavior.

CI cannot claim the physical gate.
