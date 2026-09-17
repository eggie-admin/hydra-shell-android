# LuHm OS Godot World-First HUD

`LUHM_OS_GODOT_WORLD_FIRST_HUD_1.0.9_VIRGIN_INSTALL_CANDIDATE`

Goal: launch into the Godot world first from a genuinely fresh Android app install, with no prior LuHm OS package state, migration step, saved config, network dependency, shell bridge, or privilege bridge required.

The 1.0.9 virgin-install candidate keeps the 1.0.8 physical proof harness and makes first-run state explicit. If `user://luhmos_physical_proof.cfg` does not exist, the app must render normally with `INSTALL: VIRGIN_FIRST_RUN`, `SAVEPOINT: 0`, and `RESTORED SESSION: NONE`. After the first local SAVEPOINT, the state becomes `LOCAL_STATE_SEALED`; a later launch may report `RESTORED_LOCAL_STATE`.

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

First-install proof law:

- package remains `art.eggiebagelface.luhmos`.
- persistent LuHm OS release signer remains mandatory.
- fresh install does not require any previously installed LuHm OS version.
- fresh install does not require a pre-existing `user://` save file.
- missing proof-state file is a normal first-run condition, not an error.
- Android Package Installer remains human-confirmed; silent install is forbidden.
- public publish remains OFF.
- a clean install may be tested on a genuinely clean profile/device or an isolated profile such as Samsung Secure Folder. Do not erase an existing profile merely to manufacture a virgin test unless the Professor explicitly chooses to discard that app data.

Interaction law:

- SPRITE_BUBBLE -> tap Lum -> WIDGET_DECK.
- WIDGET_DECK -> CROWN / FULL COCKPIT -> FULL_COCKPIT.
- FULL_COCKPIT -> return -> SPRITE_BUBBLE.
- GAME / ADMIN / SYSTEM buttons change presentation realm only; they do not grant authority.
- SAVEPOINT writes only the local proof counter/session receipt to `user://luhmos_physical_proof.cfg`.
- UPDATE/CROWN/LOG stay in the ADMIN cockpit.
- GAME state never creates ADMIN authority.
- Lum bubble is presentation, not sudo.

Candidate promotion law:

`SOURCE_GREEN -> SIGNED_BUILD_GREEN -> AMBER_VIRGIN_INSTALL_CANDIDATE -> FIRST_INSTALL_DEVICE_PROOF -> GREEN`

A successful CI build remains AMBER for the first-install milestone until Android accepts the signed APK on a profile with no installed LuHm OS package and the Samsung test proves launch/render, `VIRGIN_FIRST_RUN`, SPRITE_BUBBLE <-> WIDGET_DECK <-> FULL_COCKPIT, realm separation, save/reload, and the intended isolated-profile/reboot checks.

The implementation is intentionally asset-light and procedural so it remains LuHm-owned and build-safe. Third-party/private reference assets stay outside the public APK unless separately cleared.
