# KAI 9000 Secure Folder one-APK lane

Goal: one APK installed inside Samsung Secure Folder. No AcodeX, no Termux runtime,
no Python runtime, no VNC, no websockify, and no second user-installed package.

Runtime:
- Native Android Java only
- Foreground service type: `specialUse`
- `START_STICKY`
- localhost bind: `127.0.0.1:8000`
- SQLite app-private database
- first app launch starts the backend from a visible Activity

Endpoints:
- `GET /api/health`
- `GET /api/status`
- `GET /api/kv/<key>`
- `POST /api/kv/<key>` with `{"value": ...}`

Android cannot guarantee immortal execution. Samsung/Android may still stop the app,
especially after force-stop, Secure Folder lock/policy changes, or reboot. A boot
receiver makes a best-effort restart; opening the app is the deterministic ignition.

Build:
`gradle :app:assembleDebug`

APK:
`app/build/outputs/apk/debug/app-debug.apk`
