# KAI 9000 Relic Dungeon

Private-first Godot 4 experiment for turning legacy modding artifacts into bounded visual/gameplay behavior without committing third-party game assets.

## Core idea

The dungeon has three realms:

- **Local Vault** — user-owned/authorized files on the Android device.
- **Drive Relic Dungeon** — private remote archive and recovery mirror.
- **GitHub Code Dungeon** — parser/runtime code only. No proprietary game binaries, textures, model weights, or private Drive payloads.

## First spell: legacy Live2D motion -> Godot

`live2d_motion_parser.gd` parses the legacy text format beginning with `# Live2D Animator Motion Data`, including `$fps`, `$fadein`, `$fadeout`, and per-parameter numeric tracks.

A private runtime can map tracks such as `BODY_UPPER_X`, `BODY_UPPER_Y`, `BODY_UPPER_Z`, and `BREATH` onto Godot nodes, shaders, cameras, particles, or a user-supplied avatar. This lets an old animation relic drive a new Godot scene without redistributing the original game asset.

## PCK quarantine rule

Legacy `.pck` artifacts stay quarantined. Probe magic/metadata only until an explicit importer is selected. Do not execute or publish unknown binary payloads.

## Source-of-truth boundaries

- Git remains canonical for code/history.
- Google Drive remains the private asset/recovery mirror.
- The Samsung/AcodeX/X11 lane is a development cockpit only, not a production APK dependency.
- Production Android remains self-contained per `ARCHITECTURE.md`.
- Never claim GREEN without a device run.

## Suggested private runtime layout

```text
~/kai9000/relic-dungeon/
  project.godot
  main.tscn
  scripts/
    live2d_motion_parser.gd
    relic_pck_probe.gd
  assets-private/       # gitignored / never committed
  relics-private/       # Drive/local imports / never committed
```

## Next milestone

One Godot cathedral room with a user-supplied avatar, motion-possession mode, relic gates, gacha/date/boss toy loops, and a scanner that inventories local/Drive relic metadata without publishing the payloads.
