#!/usr/bin/env sh
set -eu

REPORT_DIR="${HYDRA_REPORT_DIR:-$PWD/hydra-audit}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ 2>/dev/null || printf unknown-time)"
REPORT="$REPORT_DIR/hydra-sanity-$STAMP.txt"
REPORT_FILE="${REPORT##*/}"
mkdir -p "$REPORT_DIR"

have() { command -v "$1" >/dev/null 2>&1; }
line() { printf '%s\n' "$*" | tee -a "$REPORT"; }
check() {
  label="$1"; shift
  if "$@" >/dev/null 2>&1; then
    line "$label=PASS"
  else
    rc=$?
    line "$label=FAIL rc=$rc"
  fi
}
workspace_write_check() {
  write_file="${TMPDIR:-.}/.hydra-write-$$"
  : >"$write_file"
  rm -f "$write_file"
}

line "HYDRA_SAMSUNG_SANITY_AUDIT"
line "timestamp_utc=$STAMP"
line "authority=Professor"
line "mutation_policy=read_only_probe"
line "redaction_policy=shareable_no_device_identifiers"
line "report_file=$REPORT_FILE"
line ""
line "## Environment"
line "shell_name=${SHELL##*/}"
line "home_set=$([ -n "${HOME:-}" ] && printf yes || printf no)"
line "android_root_set=$([ -n "${ANDROID_ROOT:-}" ] && printf yes || printf no)"
line "termux_version_set=$([ -n "${TERMUX_VERSION:-}" ] && printf yes || printf no)"
line "kernel=$(uname -srm 2>/dev/null || printf unavailable)"

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
for tool in sh bash busybox apk curl wget python3 node npm git adb openssl sha256sum awk ss netstat ip ifconfig; do
  if have "$tool"; then
    line "$tool=present"
  else
    line "$tool=missing"
  fi
done

line ""
line "## Read-only probes"
check "identity_probe" id
check "workspace_write_probe" workspace_write_check
if have ip; then
  check "loopback_probe" ip link show lo
elif have ifconfig; then
  check "loopback_probe" ifconfig lo
else
  line "loopback_probe=FAIL tool_missing"
fi

line ""
line "## Listening ports"
if have ss; then
  listener_count="$(ss -lnt 2>/dev/null | awk 'NR>1 {n++} END {print n+0}')"
  line "tcp_listener_probe=ss"
  line "tcp_listener_count=$listener_count"
elif have netstat; then
  listener_count="$(netstat -lnt 2>/dev/null | awk 'NR>2 {n++} END {print n+0}')"
  line "tcp_listener_probe=netstat"
  line "tcp_listener_count=$listener_count"
else
  line "tcp_listener_probe=unavailable"
fi
line "listener_endpoints=REDACTED"
line "listener_processes=REDACTED"

line ""
line "## ADB target gate"
if have adb; then
  adb_output="$(adb devices 2>&1 || true)"
  target_count="$(printf '%s\n' "$adb_output" | awk '
    /^List of devices attached/ {seen=1; next}
    seen && NF >= 2 && $1 !~ /^\*/ {n++}
    END {print n+0}
  ')"
  authorized_count="$(printf '%s\n' "$adb_output" | awk '
    /^List of devices attached/ {seen=1; next}
    seen && $2 == "device" {n++}
    END {print n+0}
  ')"
  unauthorized_count="$(printf '%s\n' "$adb_output" | awk '
    /^List of devices attached/ {seen=1; next}
    seen && ($2 == "unauthorized" || $2 == "offline" || ($2 == "no" && $3 == "permissions")) {n++}
    END {print n+0}
  ')"
  line "adb_serials=REDACTED"
  line "adb_targets_total=$target_count"
  line "adb_targets_authorized=$authorized_count"
  line "adb_targets_blocked_or_unready=$unauthorized_count"
  if [ "$target_count" -eq 1 ] && [ "$authorized_count" -eq 1 ]; then
    line "adb_gate=PASS"
  else
    line "adb_gate=BLOCKED_requires_exactly_one_target_and_it_must_be_authorized"
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
