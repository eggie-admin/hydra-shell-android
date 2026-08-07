#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(dirname "$0")"
ROOT="$(CDPATH='' cd "$SCRIPT_DIR/.." && pwd)"
TMP="${TMPDIR:-/tmp}/hydra-sanity-test-$$"
FAKEBIN="$TMP/bin"
REPORT_DIR="$TMP/reports"
trap 'rm -rf "$TMP"' EXIT HUP INT TERM
mkdir -p "$FAKEBIN" "$REPORT_DIR"

cat >"$FAKEBIN/adb" <<'EOF'
#!/usr/bin/env sh
cat <<'OUT'
* daemon not running; starting now at tcp:5037
* daemon started successfully
List of devices attached
SERIAL-ONE	device
SERIAL-TWO	unauthorized
OUT
EOF
chmod +x "$FAKEBIN/adb"

PATH="$FAKEBIN:$PATH" HYDRA_REPORT_DIR="$REPORT_DIR" sh "$ROOT/tools/hydra-sanity-audit.sh" >/dev/null
REPORT="$(find "$REPORT_DIR" -type f -name 'hydra-sanity-*.txt' | head -n 1)"

[ -n "$REPORT" ]
grep -q '^adb_targets_total=2$' "$REPORT"
grep -q '^adb_targets_authorized=1$' "$REPORT"
grep -q '^adb_targets_blocked_or_unready=1$' "$REPORT"
grep -q '^adb_gate=BLOCKED_requires_exactly_one_target_and_it_must_be_authorized$' "$REPORT"
grep -q '^adb_serials=REDACTED$' "$REPORT"

if grep -Eq 'SERIAL-ONE|SERIAL-TWO' "$REPORT"; then
  echo 'FAIL: ADB serial leaked into redacted report' >&2
  exit 1
fi

if grep -Eq '^(home|pwd|user|uid)=' "$REPORT"; then
  echo 'FAIL: identifying environment detail leaked into redacted report' >&2
  exit 1
fi

printf 'PASS: hydra sanity audit redaction and ADB gate\n'
