#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${1:-termux-app}"
TARGET_PACKAGE="${HYDRA_TERMUX_PACKAGE:-com.hydra.termux}"
REPORT_DIR="${HYDRA_REPORT_DIR:-build/knox-mutation}"
BUILD_APK="${HYDRA_BUILD_APK:-0}"

CONSTANTS="$SOURCE_DIR/termux-shared/src/main/java/com/termux/shared/termux/TermuxConstants.java"
GRADLE="$SOURCE_DIR/app/build.gradle"

mkdir -p "$REPORT_DIR"
REPORT="$REPORT_DIR/report.txt"
: > "$REPORT"

log() { printf '%s\n' "$*" | tee -a "$REPORT"; }
fail() { log "ERROR: $*"; exit 1; }

[[ -d "$SOURCE_DIR/.git" ]] || fail "Termux source repository not found at $SOURCE_DIR"
[[ -f "$CONSTANTS" ]] || fail "Missing TermuxConstants.java"
[[ -f "$GRADLE" ]] || fail "Missing app/build.gradle"

log "HYDRA_KNOX_TERMUX_MUTATION_001"
log "source=$SOURCE_DIR"
log "target_package=$TARGET_PACKAGE"
log "source_commit=$(git -C "$SOURCE_DIR" rev-parse HEAD)"

cp "$CONSTANTS" "$REPORT_DIR/TermuxConstants.java.before"
cp "$GRADLE" "$REPORT_DIR/build.gradle.before"

python3 - "$CONSTANTS" "$GRADLE" "$TARGET_PACKAGE" <<'PY'
from pathlib import Path
import re
import sys

constants = Path(sys.argv[1])
gradle = Path(sys.argv[2])
target = sys.argv[3]

text = constants.read_text()
old = 'public static final String TERMUX_PACKAGE_NAME = "com.termux";'
new = f'public static final String TERMUX_PACKAGE_NAME = "{target}";'
if old not in text:
    raise SystemExit('TERMUX_PACKAGE_NAME declaration did not match expected source')
constants.write_text(text.replace(old, new, 1))

gtext = gradle.read_text()
patterns = [
    (r'applicationId\s+["\']com\.termux["\']', f'applicationId "{target}"'),
    (r'applicationId\s*=\s*["\']com\.termux["\']', f'applicationId = "{target}"'),
]
for pattern, replacement in patterns:
    updated, count = re.subn(pattern, replacement, gtext, count=1)
    if count:
        gradle.write_text(updated)
        break
else:
    raise SystemExit('applicationId com.termux was not found in app/build.gradle')
PY

log "mutated_constants=$CONSTANTS"
log "mutated_gradle=$GRADLE"

grep -RInE "/data/(data|user/[0-9]+)/com\.termux|com\.termux/files/usr|applicationId[^A-Za-z].*com\.termux" \
  "$SOURCE_DIR" \
  --exclude-dir=.git \
  --exclude-dir=.gradle \
  --exclude-dir=build \
  > "$REPORT_DIR/hardcoded-prefixes.txt" || true

PREFIX_COUNT=$(wc -l < "$REPORT_DIR/hardcoded-prefixes.txt" | tr -d ' ')
log "remaining_hardcoded_prefix_hits=$PREFIX_COUNT"

BOOTSTRAP_MATCH=0
if find "$SOURCE_DIR" -type f \( -name 'bootstrap-*.zip' -o -name 'bootstrap.zip' \) -print0 2>/dev/null \
  | xargs -0 -r strings 2>/dev/null \
  | grep -Fq "/data/data/$TARGET_PACKAGE/files/usr"; then
  BOOTSTRAP_MATCH=1
fi
log "matching_bootstrap=$BOOTSTRAP_MATCH"

if [[ "$BOOTSTRAP_MATCH" != "1" ]]; then
  log "BLOCKED: source mutated, but no bootstrap compiled for /data/data/$TARGET_PACKAGE/files/usr was found."
  log "NEXT: build termux-packages with TERMUX_APP_PACKAGE=$TARGET_PACKAGE, then inject the matching bootstrap."
  exit 20
fi

if [[ "$BUILD_APK" == "1" ]]; then
  log "building_debug_apk=1"
  (cd "$SOURCE_DIR" && ./gradlew assembleDebug)
else
  log "building_debug_apk=0"
fi

log "status=GREEN"
