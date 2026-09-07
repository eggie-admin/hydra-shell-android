# KAI 9000 Secure Folder one-APK HTTPS lane

Goal: one APK installed inside Samsung Secure Folder. No AcodeX, no Termux runtime,
no Python runtime, no VNC, no websockify, and no second user-installed package.

Runtime:
- Native Android Java only
- Foreground service type: `specialUse`
- `START_STICKY`
- HTTPS bind: `https://127.0.0.1:8443`
- SQLite app-private database
- TLS private key generated inside Android Keystore on first run
- Per-install self-signed localhost certificate
- Health payload exposes `tls_sha256` fingerprint for client pinning
- Cleartext traffic disabled in the manifest
- first app launch starts the backend from a visible Activity

Endpoints:
- `GET https://127.0.0.1:8443/api/health`
- `GET https://127.0.0.1:8443/api/status`
- `GET https://127.0.0.1:8443/api/kv/<key>`
- `POST https://127.0.0.1:8443/api/kv/<key>` with `{"value": ...}`

The certificate is intentionally per-install and self-signed. Clients outside this APK
must pin or explicitly trust the `tls_sha256` fingerprint returned by the app. The
private key never leaves Android Keystore and is not stored in GitHub.

Android cannot guarantee immortal execution. Samsung/Android may still stop the app,
especially after force-stop, Secure Folder lock/policy changes, or reboot. A boot
receiver makes a best-effort restart; opening the app is the deterministic ignition.

Build:
`gradle :app:assembleDebug`

APK:
`app/build/outputs/apk/debug/app-debug.apk`
