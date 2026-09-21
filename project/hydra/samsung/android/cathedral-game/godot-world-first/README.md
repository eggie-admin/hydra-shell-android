# LuHm OS Godot World-First HUD

`LUHM_OS_GODOT_WORLD_FIRST_HUD_1.0.7`

Goal: launch into the Godot world first, with a minimal CanvasLayer HUD and Lum as the floating continuity anchor. The cockpit remains available only when explicitly summoned.

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
    └── CockpitOverlay (hidden by default)
```

Interaction law:

- EXPLORE becomes world movement.
- CONTACT becomes proximity/context interaction.
- BOND is invoked from Lum/context interaction.
- FUSION is bound to shrine/ritual objects.
- DATE is a quest/event trigger.
- REST is a world object.
- SAVEPOINT is a world terminal/crystal.
- UPDATE/CROWN/LOG stay in the ADMIN cockpit.
- GAME state never creates ADMIN authority.
- Lum bubble is presentation, not sudo.

The implementation is intentionally asset-light and procedural so it remains LuHm-owned and build-safe. Third-party/private reference assets stay outside the public APK unless separately cleared.
