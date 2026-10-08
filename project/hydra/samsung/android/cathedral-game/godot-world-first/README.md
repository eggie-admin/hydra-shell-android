# LuHm OS Godot World-First HUD

`LUHM_OS_GODOT_WORLD_FIRST_HUD_1.0.8_CANDIDATE`

Goal: launch into the Godot world first, with a minimal CanvasLayer HUD and Lum as the floating continuity anchor. The cockpit remains available only when explicitly summoned.

The 1.0.8 candidate adds a deliberately boring-but-useful physical proof harness so the Samsung test does not depend on memory or vibes. It exposes the current UI mode, realm, runtime session identifier, savepoint counter, and last restored session directly inside the full cockpit. Persistence uses Godot `ConfigFile` under `user://`; it adds no shell, network, privilege bridge, silent install, or background authority.

Core scene contract:

```text
WorldFirstRoot
├── World3D
│   ├── CathedralFloor
│   ├── SwitchyardRails
│   ├── Shrine
│   ├── CameraRig
│   └── LumGuide
└── HUD (CanvasLayer)
    ├── QuestSigil
    ├── ContextAction
    ├── MapSigil
    ├── StatusSigils
    ├── LumBubble
    ├── MicroMenu / WIDGET_DECK
    └── CockpitOverlay / FULL_COCKPIT (hidden by default)
        ├── ProofState
        └── RealmSwitch / GAME · ADMIN · SYSTEM
```

Interaction law:

- SPRITE_BUBBLE -> tap Lum -> WIDGET_DECK.
- WIDGET_DECK -> CROWN / FULL COCKPIT -> FULL_COCKPIT.
- FULL_COCKPIT -> return -> SPRITE_BUBBLE.
- GAME / ADMIN / SYSTEM buttons change presentation realm only; they do not grant authority.
- EXPLORE becomes world movement.
- CONTACT becomes proximity/context interaction.
- BOND is invoked from Lum/context interaction.
- FUSION is bound to shrine/ritual objects.
- DATE is a quest/event trigger.
- REST is a world object.
- SAVEPOINT writes only the local proof counter/session receipt to `user://luhmos_physical_proof.cfg`.
- UPDATE/CROWN/LOG stay in the ADMIN cockpit.
- GAME state never creates ADMIN authority.
- Lum bubble is presentation, not sudo.

Candidate promotion law:

`SOURCE_GREEN -> SIGNED_BUILD_GREEN -> AMBER_PHYSICAL_CANDIDATE -> DEVICE_PROOF -> GREEN`

A successful CI build is intentionally classified AMBER for the physical cockpit-swap milestone until Android accepts the same-signer update and the Samsung test proves launch/render, SPRITE_BUBBLE <-> WIDGET_DECK <-> FULL_COCKPIT, realm separation, save/reload, Secure Folder where intended, and reboot/return.

The implementation is intentionally asset-light and procedural so it remains LuHm-owned and build-safe. Third-party/private reference assets stay outside the public APK unless separately cleared.
