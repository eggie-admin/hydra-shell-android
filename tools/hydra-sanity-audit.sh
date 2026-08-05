#!/usr/bin/env sh
set -eu

REPORT_DIR="${HYDRA_REPORT_DIR:-$PWD/hydra-audit}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ 2>/dev/null || printf unknown-time)"
REPORT="$REPORT_DIR/hydra-sanity-$STAMP.txt"
mkdir -p "$REPORT_DIR"

have() { command -v "$1" >/dev/null 2>&1; }
line() { printf '%s\n' "$*" | tee -a "$REPORT"; }
probe() {
  label="$1"; shift
  line ""
  line "## $label"
  if "$@" >>"$REPORT" 2>&1; then
    line "status=PASS"
  else
    rc=$?
    line "status=FAIL rc=$rc"
  fi
}

line "HYDRA_SAMSUNG_SANITY_AUDIT"
line "timestamp_utc=$STAMP"
line "authority=Professor"
line "mutation_policy=read_only_probe"
line "report=$REPORT"
line ""
line "## Environment"
line "shell=${SHELL:-unknown}"
line "home=${HOME:-unknown}"
line "pwd=$PWD"
line "user=$(id -un 2>/dev/null || printf unknown)"
line "uid=$(id -u 2>/dev/null || printf unknown)"
line "kernel=$(uname -a 2>/dev/null || printf unavailable)"
line "android_root=${ANDROID_ROOT:-unset}"
line "termux_version=${TERMUX_VERSION:-unset}"

case "${PREFIX:-}" in
  /data/data/com.termux/*) runtime=termux ;;
  *)
    if have apk && [ -f /etc/alpine-release ]; then runtime=alpine
    elif have busybox; then runtime=busybox
    else runtime=unknown
    fi
    ;;
esac
line "runtime=$runtime"

line ""
line "## Tool inventory"
for tool in sh bash busybox apk curl wget python3 node npm git adb openssl sha256sum ss netstat; do
  if have "$tool"; then
    path="$(command -v "$tool")"
    line "$tool=present:$path"
  else
    line "$tool=missing"
  fi
done

probe "Identity" id
probe "Filesystem" sh -c 'df -h .; printf "write_test="; f="${TMPDIR:-.}/.hydra-write-$$"; : > "$f" && rm -f "$f" && echo PASS'
probe "Loopback" sh -c 'if command -v ip >/dev/null 2>&1; then ip addr show lo; elif command -v ifconfig >/dev/null 2>&1; then ifconfig lo; else echo "No ip/ifconfig"; exit 1; fi'

line ""
line "## Listening ports"
if have ss; then ss -lntup >>"$REPORT" 2>&1 || true
elif have netstat; then netstat -lntup >>"$REPORT" 2>&1 || true
else line "port_probe=unavailable"
fi

line ""
line "## ADB target gate"
if have adb; then
  adb_output="$(adb devices 2>&1 || true)"
  printf '%s\n' "$adb_output" >>"$REPORT"
  authorized_count="$(printf '%s\n' "$adb_output" | awk 'NR>1 && $2=="device" {n++} END {print n+0}')"
  line "authorized_adb_targets=$authorized_count"
  if [ "$authorized_count" -eq 1 ]; then line "adb_gate=PASS"
  else line "adb_gate=BLOCKED_requires_exactly_one_authorized_target"
  fi
else
  line "adb_gate=SKIP_adb_missing"
fi

line ""
line "## Security assertions"
line "browser_secrets=FORBIDDEN"
line "public_repo_secrets=FORBIDDEN"
line "direct_webview_privileged_shell=FORBIDDEN"
line "api_default_bind=127.0.0.1"
line "external_state_changes=require_explicit_Professor_approval"

line ""
line "## Result"
case "$runtime" in
  alpine|busybox) line "environment_gate=PASS_WITH_REVIEW" ;;
  termux) line "environment_gate=LEGACY_REVIEW_REQUIRED" ;;
  *) line "environment_gate=BLOCKED_UNKNOWN_RUNTIME" ;;
esac
line "full_mutation=NOT_ATTESTED"
line "next=Review this redacted report and implement the API boundary before enabling writes."

printf '\nAudit complete: %s\n' "$REPORT"
