# KAI 9000 / LuHm OS Android 10-Pass Hard Audit — 2026-09-06

Status: TESTING ONLY

Target repository: `eggie-admin/hydra-shell-android`
Target branch: `testing/luhm-os-android`
Promotion target: none until separate review and build evidence.

This audit consolidates Android-relevant KAI 9000 / LuHm OS work recovered from the active project history, connected GitHub repositories, current Samsung manifests, and stranded donor branches. Newer default-branch state wins over older donor branches. Diverged branches are transplanted selectively instead of force-merged.

## Pass 1 — Identity and lane topology

- Working title: KAI 9000.
- OS/project identity: LuHm OS, Linux / Unix approach Hydra manifest.
- Android APK forge: `eggie-admin/hydra-shell-android`.
- Isolated integration lane: `testing/luhm-os-android`.
- Godot/JRPG experiment remains a separate donor forge in `eggie-admin/amplify-godot-engine-template:testing/jrpg-dating-sim`.
- No mutation in this audit is promoted to `main`.

Result: GREEN.

## Pass 2 — Samsung trust boundary

Preserved doctrine:

- Ordinary Termux owns daemon/control-plane processes.
- Samsung Secure Folder AcodeX is a protected cockpit/client.
- Secure Folder probes localhost services; it does not inspect or own ordinary-Termux PIDs.
- Stock Shizuku is the preferred privilege broker.
- No automatic root.
- No Sui inside Secure Folder.
- Privileged actions must be typed and allowlisted.

Result: GREEN.

## Pass 3 — Local control-plane contract

Canonical loopback services:

- AcodeX/AXS: `127.0.0.1:8767`
- TigerVNC: `127.0.0.1:5901`
- WebSocket bridge: `127.0.0.1:6080`
- Hydra cockpit: `127.0.0.1:8787`
- Ollama: `127.0.0.1:11434`

The recovered local Flask/Ollama backend binds to `127.0.0.1` and exposes bounded read-only agent tools for time/device/service status. No arbitrary model shell is added.

Result: GREEN.

## Pass 4 — APK / Godot / WebView artifacts

Retained current Samsung APK references and manifests already present on main.

Donor references retained rather than copied wholesale:

- Godot Android export workflow and KAI cockpit project in `eggie-admin/amplify-godot-engine-template:testing/jrpg-dating-sim`.
- Lum spell-agent doctrine and jQuery bridge remain a forge reference until the OpenAI credential/runtime lane is separately authorized.
- Vue headless CMS Samsung build candidate remains the pinned APK/frontend source reference.

Result: GREEN, build proof still required before promotion.

## Pass 5 — Local AI runtime

Recovered from `hydra-ollama-local-001`:

- `backend/server.py`
- Python requirements and tests
- local Web UI
- `tools/hydra-full-green.sh`
- `tools/hydra-ollama-up.sh`
- local CI workflow and documentation

Policy:

- Ollama remains localhost-first.
- Models cannot execute arbitrary shell.
- Runtime shell access is not exposed through the agent API.

Result: GREEN for testing.

## Pass 6 — RSS / SQLite / agent antenna

Recovered from `kai9000-samsung-agent-rss-merge-010` by selective transplant after a direct branch merge was rejected due divergence:

- `ai_feed/agent.py`
- `ai_feed/db.py`
- `ai_feed/feeds.py`
- `ai_feed/learning.py`
- `ai_feed/router.py`
- AI feed docs
- loopback `magic_server.py` router integration
- archived Ollama-Termux upstream reference

No stale branch state replaced newer September 6 files outside these paths.

Result: GREEN for testing.

## Pass 7 — Media / FFmpeg lane

Recovered `tools/kai_media_server.py` from `kai9000-media-forge`.

Existing Ultima Ollama/FFmpeg antenna remains canonical for current media experimentation. Media generation/transcoding stays a separate worker capability and must not gain unrestricted filesystem or network authority from chat prompts.

Result: GREEN for testing.

## Pass 8 — Privilege, Knox, ADB and install hardening

Recovered and hardened:

- `tools/knox-termux-mutate.sh` as a manual source-forge helper only.
- `tools/install-shizuku.sh` replaced with the audited variant that requires exactly one authorized ADB device and selects that serial explicitly.
- PR guardrails and sanity-audit scripts/tests restored from the August audit branch.

The Knox mutation helper edits a Termux source checkout and deliberately blocks if a matching bootstrap for the mutated package is unavailable. It is never invoked automatically by the agent or APK.

Result: GREEN with manual-only forge restriction.

## Pass 9 — Camera / USB / proprietary asset / secret boundaries

Preserved known Android/Knox camera limitation:

- USB bus enumeration may succeed.
- Direct `/dev/video*` and `/sys/class/video4linux` access can remain blocked by Android/Knox permissions.
- Camera recovery is isolated from the green GUI/control-plane stack.

Asset and secret policy:

- No proprietary Destiny Child runtime art, audio, `.pck`, `.moc`, `.mtn`, or other extracted game assets are bundled.
- Lum visual references remain reference-not-copy.
- No OpenAI API key or other secret is committed or embedded in APK artifacts.
- Split base64 backup bundles from the old Lum dungeon backup branch are intentionally quarantined and not merged.

Result: GREEN.

## Pass 10 — CI, provenance, rollback and promotion

Recovered:

- PR guardrails
- local Hydra workflow
- Cathedral source/F-Droid workflow
- Cathedral architecture/helper
- sanity audit test harness

Promotion doctrine:

1. Work only in `testing/luhm-os-android`.
2. Run repo guards/tests and Android/APK build checks.
3. Verify package identity and installable APK evidence.
4. Verify localhost-only service binding.
5. Verify no secret/proprietary binary leakage.
6. Verify Secure Folder remains client-only.
7. Only then open a separate proposed/promotion review.

Rollback point before this audit: `f4ef83e83355fa55fbec093719b7262bb39c45cc`.
Initial consolidated donor commit: `70eafa7bcaa62786593922bdcc7e1706cba0bf04`.

Result: TESTING GREEN, NOT RELEASE GREEN.

## Donor disposition summary

| Donor | Disposition |
|---|---|
| `audit/full-mutation-2026-08-05` | selected hardening + audit tools transplanted |
| `experiment/knox-termux-mutation-001` | manual forge helper transplanted |
| `hydra-ollama-local-001` | localhost backend/UI/tests/tools transplanted |
| `kai9000-media-forge` | media worker transplanted |
| `kai9000-samsung-agent-rss-merge-010` | RSS/SQLite/router artifacts transplanted |
| `video-forge-cathedral-npm-fdroid` | CI/architecture/helper transplanted |
| Project Hydra structure branches | already superseded by newer main; not regressed |
| Lum dungeon base64 backup branch | quarantined; not APK/runtime material |
| Amplify Godot testing branch | reference/donor only; no credential-bearing OpenAI runtime copied |

## Final audit state

`testing/luhm-os-android` is the sole consolidated Samsung Android testing lane produced by this audit. Main remains unchanged.
