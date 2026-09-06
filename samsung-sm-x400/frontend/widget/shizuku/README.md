# Shizuku privilege-broker lane

This is an **optional** Samsung SM-X400 widget capability. It is not part of the APK dependency graph and it does not make root a requirement.

## Preferred Secure Folder development mode

Use Shizuku in ADB / wireless-debugging mode on the stock Knox-capable target.

- Developer Options enabled
- USB or Wireless debugging controlled by the operator
- Shizuku installed separately
- explicit per-app authorization
- no root requirement
- no Sui requirement
- no hidden-API bypass dependency by default

Missing Shizuku is a capability downgrade, not a build failure.

## Rooted laboratory mode

A rooted Samsung may use Shizuku root mode or Sui, but that is a separate laboratory trust lane. It must not claim Secure Folder/Knox trust.

Root is never auto-selected merely because `su` exists. Root-only actions require an explicit architecture and operator authorization gate.

## Stage 1

1. detect Shizuku manager/service presence
2. request normal Shizuku user authorization
3. expose read-only device diagnostics through typed actions
4. fall back cleanly when unavailable

No arbitrary model-authored shell execution is allowed.

## Stage 2 gate

Direct Shizuku API dependencies, package-manager mutations, cross-user operations, and root-only actions remain blocked until a concrete feature requires them and the Android permission boundary has been reviewed.

## Validation

From the repository root:

```bash
python3 tools/sm_x400_shizuku_sanity.py
python3 tools/sm_x400_shizuku_sanity.py --device
```

The second command is read-only and requires an ADB-visible device.
