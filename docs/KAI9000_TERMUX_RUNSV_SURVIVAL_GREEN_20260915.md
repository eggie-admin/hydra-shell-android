# KAI9000_TERMUX_RUNSV_SURVIVAL_GREEN_20260915

Date: 2026-09-15  
Human authority: Professor  
Status: SEALED_RUNTIME_PROOF

## Scope

This milestone records direct Samsung/Termux runtime proof that KAI-owned local services survive interactive terminal closure when supervised by `runit`/`runsv` instead of being children of the interactive shell.

## Verified runtime topology

- `kai-vnc` -> `127.0.0.1:5901`, Xvnc display `:1`, geometry `1280x720`, depth `24`.
- `kai-websocket` -> `127.0.0.1:6080` forwarding to `127.0.0.1:5901`.
- `kai-sshd` -> `127.0.0.1:8022`, localhost-only, public-key authentication, password authentication disabled, root login disabled.
- `kai-ollama` -> `127.0.0.1:11434`.
- `runsvdir` owns the four KAI service supervisors.

## Survival proof

The interactive Termux terminal was closed/killed in the same manner that previously terminated manually launched daemons. After Termux was reopened, the same supervised service processes remained alive and all four loopback probes returned GREEN.

```text
VNC         GREEN  127.0.0.1:5901
WEBSOCKET   GREEN  127.0.0.1:6080
SSH         GREEN  127.0.0.1:8022
OLLAMA      GREEN  127.0.0.1:11434
```

## Verdict

```text
INTERACTIVE_SHELL_INDEPENDENCE = GREEN
SERVICE_SUPERVISION = GREEN
LOOPBACK_ONLY_BASELINE = GREEN
REBOOT_PERSISTENCE = NOT_YET_PROVEN
ANDROID_FORCE_STOP_SURVIVAL = NOT_CLAIMED
WAKE_LOCK_CURRENT_PASS = NOT_YET_REPROVEN
SHIZUKU_CURRENT_PASS = NOT_YET_PROVEN
ACODEX_TO_TERMUX_LOGIN_CURRENT_PASS = NOT_YET_PROVEN
AXS_8767_CURRENT_PASS = NOT_TESTED
```

## Boundaries

No public bind, root, bootloader unlock, APK install, compile, release publication, secret print, signing-key mutation, SIM identifier access, or destructive storage action is part of this proof.

Closing an interactive terminal is now proven non-fatal to the supervised four-head stack. Android reboot and explicit Android Force stop remain separate failure domains and must not be called GREEN until independently tested.

## Next proof order

1. Re-prove current Termux wake lock and Samsung unrestricted/background policy.
2. Start and prove Shizuku through the intended stock Android flow.
3. Prove AcodeX/Secure Folder to ordinary Termux authenticated client path.
4. Add boot recovery only after the live supervisor state is preserved.
5. Reboot-test the complete stack before promoting `REBOOT_PERSISTENCE` to GREEN.

Professor retains final authority.
