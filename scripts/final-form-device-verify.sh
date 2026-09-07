#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-status}"
PACKAGE_ID="art.eggiebagelface.videoforge.dev"
REPO_URL="https://fdroid.eggiebagelface.art/fdroid/repo"
REPO_FP="BFB900A9EC913D35C22F1DC3DE7B152D1AF5CA11B7B07E5FAFDD06B44811F66D"
BASELINE_VERSION_CODE=6
UPGRADE_VERSION_CODE="${KAI_UPGRADE_VERSION_CODE:-7}"
WORK="${TMPDIR:-/tmp}/kai9000-final-green"
mkdir -p "$WORK"

public_probe() {
  command -v curl >/dev/null || { echo 'RED: curl is required' >&2; return 2; }
  local fp
  fp="$(curl -fsSL --max-time 20 "$REPO_URL/repo-fingerprint-sha256.txt" | tr -d ':[:space:]' | tr '[:lower:]' '[:upper:]')"
  [ "$fp" = "$REPO_FP" ] || { echo "RED: repo fingerprint mismatch: $fp" >&2; return 3; }
  curl -fsSL --max-time 30 "$REPO_URL/index-v1.jar" -o "$WORK/index-v1.jar"
  curl -fsSL --max-time 30 "$REPO_URL/index-v1.json" -o "$WORK/index-v1.json"
  test -s "$WORK/index-v1.jar"
  test -s "$WORK/index-v1.json"
  echo 'FDROID_PUBLIC_HTTPS_GREEN'
}

installed_version_code() {
  local dump=""
  if command -v dumpsys >/dev/null 2>&1; then
    dump="$(dumpsys package "$PACKAGE_ID" 2>/dev/null || true)"
  fi
  if [ -z "$dump" ] && command -v pm >/dev/null 2>&1; then
    dump="$(pm dump "$PACKAGE_ID" 2>/dev/null || true)"
  fi
  printf '%s\n' "$dump" | sed -n 's/.*versionCode=\([0-9][0-9]*\).*/\1/p' | head -n1
}

open_repo() {
  public_probe
  local uri="$REPO_URL?fingerprint=$REPO_FP"
  echo "repo_uri=$uri"
  if command -v termux-open-url >/dev/null 2>&1; then
    termux-open-url "$uri"
  elif command -v am >/dev/null 2>&1; then
    am start -a android.intent.action.VIEW -d "$uri" >/dev/null
  else
    echo 'YELLOW: no Android URL opener found; open repo_uri manually' >&2
    return 4
  fi
  echo 'FDROID_IMPORT_UI_OPENED'
  echo 'Confirm the fingerprint in F-Droid and add the repository.'
}

check_install() {
  public_probe
  local vc
  vc="$(installed_version_code)"
  [ -n "$vc" ] || { echo "RED: $PACKAGE_ID is not visible as installed" >&2; return 5; }
  echo "installed_version_code=$vc"
  if [ "$vc" -lt "$BASELINE_VERSION_CODE" ]; then
    echo "RED: installed versionCode $vc is below baseline $BASELINE_VERSION_CODE" >&2
    return 6
  fi
  echo 'FDROID_IMPORT_VERIFIED'
}

check_upgrade() {
  public_probe
  local vc
  vc="$(installed_version_code)"
  [ -n "$vc" ] || { echo "RED: $PACKAGE_ID is not visible as installed" >&2; return 5; }
  echo "installed_version_code=$vc"
  if [ "$vc" -lt "$UPGRADE_VERSION_CODE" ]; then
    echo "RED: upgrade not proven; need installed versionCode >= $UPGRADE_VERSION_CODE" >&2
    return 7
  fi
  echo 'FDROID_IMPORT_VERIFIED'
  echo 'UPGRADE_VERIFIED'
  echo 'FINAL_FORM_GREEN'
}

case "$MODE" in
  public)
    public_probe
    ;;
  import)
    open_repo
    ;;
  install-check)
    check_install
    ;;
  upgrade-check)
    check_upgrade
    ;;
  status)
    echo "repo_url=$REPO_URL/"
    echo "repo_fingerprint_sha256=$REPO_FP"
    echo "package_id=$PACKAGE_ID"
    echo "baseline_version_code=$BASELINE_VERSION_CODE"
    echo "upgrade_target_version_code=$UPGRADE_VERSION_CODE"
    vc="$(installed_version_code || true)"
    echo "installed_version_code=${vc:-NONE}"
    ;;
  *)
    echo "usage: $0 {status|public|import|install-check|upgrade-check}" >&2
    exit 2
    ;;
esac
