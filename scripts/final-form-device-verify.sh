#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-status}"
PACKAGE_ID="${LUHMOS_PACKAGE_ID:-art.eggiebagelface.luhmos}"
REPO_URL="${LUHMOS_FDROID_REPO_URL:-https://raw.githubusercontent.com/eggie-admin/hydra-shell-android/fdroid-public/fdroid/repo}"
EXPECTED_REPO_FP="${LUHMOS_FDROID_REPO_FINGERPRINT_SHA256:-}"
BASELINE_VERSION_CODE="${LUHMOS_BASELINE_VERSION_CODE:-100}"
UPGRADE_VERSION_CODE="${LUHMOS_UPGRADE_VERSION_CODE:-101}"
EXPECTED_DEVICE_MODEL="${LUHMOS_DEVICE_MODEL:-SM-S721U1}"
EXPECTED_ANDROID_SDK="${LUHMOS_ANDROID_SDK:-36}"
FDROID_INSTALLER="${LUHMOS_FDROID_INSTALLER_PACKAGE:-org.fdroid.fdroid}"
WORK="${TMPDIR:-/tmp}/luhmos-final-green"
mkdir -p "$WORK"

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "RED: required command missing: $1" >&2
    exit 2
  }
}

norm_fp() {
  tr -d ':[:space:]' | tr '[:lower:]' '[:upper:]'
}

public_probe() {
  need curl
  need keytool
  curl -fsSL --max-time 30 "$REPO_URL/index-v2.json" -o "$WORK/index-v2.json"
  curl -fsSL --max-time 30 "$REPO_URL/index-v1.json" -o "$WORK/index-v1.json"
  curl -fsSL --max-time 30 "$REPO_URL/index-v1.jar" -o "$WORK/index-v1.jar"
  curl -fsSL --max-time 30 "$REPO_URL/entry.jar" -o "$WORK/entry.jar"
  test -s "$WORK/index-v2.json"
  test -s "$WORK/index-v1.json"
  test -s "$WORK/index-v1.jar"
  test -s "$WORK/entry.jar"

  local actual_fp
  actual_fp="$(keytool -printcert -jarfile "$WORK/index-v1.jar" 2>/dev/null \
    | sed -n 's/^[[:space:]]*SHA256: //p' | head -n1 | norm_fp)"
  test -n "$actual_fp" || { echo 'RED: could not derive repository certificate fingerprint' >&2; return 3; }
  echo "repo_fingerprint_sha256=$actual_fp"

  if [[ -n "$EXPECTED_REPO_FP" ]]; then
    local expected
    expected="$(printf '%s' "$EXPECTED_REPO_FP" | norm_fp)"
    [[ "$actual_fp" == "$expected" ]] || {
      echo "RED: repository fingerprint mismatch actual=$actual_fp expected=$expected" >&2
      return 3
    }
  else
    echo 'YELLOW: LUHMOS_FDROID_REPO_FINGERPRINT_SHA256 is not set; public signature exists but pin comparison was not performed.' >&2
  fi
  echo 'FDROID_PUBLIC_REPO_GREEN'
}

public_index_codes() {
  python3 - "$WORK/index-v1.json" "$PACKAGE_ID" <<'PY'
import json, sys
path, package = sys.argv[1:]
idx = json.load(open(path, encoding='utf-8'))
versions = idx.get('packages', {}).get(package, [])
print(','.join(str(x) for x in sorted(int(v['versionCode']) for v in versions)))
PY
}

require_public_phase() {
  local phase="$1" codes
  public_probe
  codes="$(public_index_codes)"
  case "$phase" in
    baseline)
      [[ ",$codes," == *",${BASELINE_VERSION_CODE},"* ]] || {
        echo "RED: public repo does not contain baseline versionCode $BASELINE_VERSION_CODE; codes=$codes" >&2
        return 4
      }
      ;;
    upgrade)
      [[ ",$codes," == *",${BASELINE_VERSION_CODE},"* ]] || {
        echo "RED: public repo lost baseline versionCode $BASELINE_VERSION_CODE; codes=$codes" >&2
        return 4
      }
      [[ ",$codes," == *",${UPGRADE_VERSION_CODE},"* ]] || {
        echo "RED: public repo does not contain upgrade versionCode $UPGRADE_VERSION_CODE; codes=$codes" >&2
        return 4
      }
      ;;
    *) echo "RED: unknown phase $phase" >&2; return 4 ;;
  esac
  echo "FDROID_PUBLIC_PHASE_GREEN=$phase codes=$codes"
}

adb_shell() {
  need adb
  adb shell "$@"
}

require_device() {
  need adb
  adb get-state >/dev/null
  local model sdk
  model="$(adb shell getprop ro.product.model | tr -d '\r')"
  sdk="$(adb shell getprop ro.build.version.sdk | tr -d '\r')"
  echo "device_model=$model"
  echo "android_sdk=$sdk"
  [[ "$model" == "$EXPECTED_DEVICE_MODEL" ]] || {
    echo "RED: expected $EXPECTED_DEVICE_MODEL, got $model" >&2
    return 5
  }
  [[ "$sdk" == "$EXPECTED_ANDROID_SDK" ]] || {
    echo "RED: expected SDK $EXPECTED_ANDROID_SDK, got $sdk" >&2
    return 5
  }
  echo 'S24FE_DEVICE_IDENTITY_GREEN'
}

installed_version_code() {
  adb shell dumpsys package "$PACKAGE_ID" 2>/dev/null \
    | sed -n 's/.*versionCode=\([0-9][0-9]*\).*/\1/p' \
    | head -n1 \
    | tr -d '\r'
}

install_source() {
  adb shell cmd package get-install-source "$PACKAGE_ID" 2>/dev/null | tr -d '\r'
}

require_fdroid_installer() {
  local src
  src="$(install_source)"
  echo "$src"
  printf '%s\n' "$src" | grep -q "$FDROID_INSTALLER" || {
    echo "RED: package installer is not $FDROID_INSTALLER" >&2
    return 6
  }
  echo 'FDROID_INSTALLER_VERIFIED'
}

require_launcher_and_launch() {
  local resolved
  resolved="$(adb shell cmd package resolve-activity --brief -c android.intent.category.LAUNCHER "$PACKAGE_ID" 2>/dev/null | tr -d '\r')"
  echo "launcher_activity=$resolved"
  [[ -n "$resolved" && "$resolved" != 'No activity found' ]] || {
    echo 'RED: launcher activity not resolved' >&2
    return 7
  }
  adb shell monkey -p "$PACKAGE_ID" -c android.intent.category.LAUNCHER 1 >/dev/null
  sleep 2
  if adb shell pidof "$PACKAGE_ID" >/dev/null 2>&1; then
    echo 'S24FE_LAUNCH_VERIFIED'
  else
    echo 'YELLOW: launcher intent was sent but process was not visible after two seconds' >&2
    return 7
  fi
}

open_repo() {
  require_device
  public_probe
  local actual_fp uri
  actual_fp="$(keytool -printcert -jarfile "$WORK/index-v1.jar" 2>/dev/null \
    | sed -n 's/^[[:space:]]*SHA256: //p' | head -n1 | norm_fp)"
  uri="${REPO_URL}?fingerprint=${actual_fp}"
  echo "repo_uri=$uri"
  adb shell am start -a android.intent.action.VIEW -d "$uri" >/dev/null
  echo 'FDROID_IMPORT_UI_OPENED'
  echo 'Complete the add-repository confirmation in F-Droid on the device.'
}

check_installed_version() {
  local expected="$1" label="$2" vc
  require_device
  vc="$(installed_version_code)"
  [[ -n "$vc" ]] || { echo "RED: $PACKAGE_ID is not installed" >&2; return 8; }
  echo "installed_version_code=$vc"
  [[ "$vc" == "$expected" ]] || {
    echo "RED: $label requires versionCode $expected; found $vc" >&2
    return 8
  }
  require_fdroid_installer
  require_launcher_and_launch
}

check_baseline_install() {
  require_public_phase baseline
  check_installed_version "$BASELINE_VERSION_CODE" baseline
  echo 'FDROID_IMPORT_VERIFIED'
  echo 'S24FE_INSTALL_VERIFIED'
  echo 'BASELINE_100_INSTALLED'
}

check_upgrade() {
  require_public_phase upgrade
  check_installed_version "$UPGRADE_VERSION_CODE" upgrade
  echo 'FDROID_IMPORT_VERIFIED'
  echo 'S24FE_INSTALL_VERIFIED'
  echo 'UPGRADE_100_TO_101_VERIFIED'
  echo 'LUHMOS_S24FE_FDROID_PUBLIC_INSTALL_GREEN'
}

case "$MODE" in
  public-baseline) require_public_phase baseline ;;
  public-upgrade) require_public_phase upgrade ;;
  import) open_repo ;;
  baseline-check|install-check) check_baseline_install ;;
  upgrade-check) check_upgrade ;;
  status)
    echo "repo_url=$REPO_URL/"
    echo "package_id=$PACKAGE_ID"
    echo "baseline_version_code=$BASELINE_VERSION_CODE"
    echo "upgrade_target_version_code=$UPGRADE_VERSION_CODE"
    if command -v adb >/dev/null 2>&1 && adb get-state >/dev/null 2>&1; then
      vc="$(installed_version_code || true)"
      echo "installed_version_code=${vc:-NONE}"
      install_source || true
    else
      echo 'device=NOT_CONNECTED'
    fi
    ;;
  *)
    echo "usage: $0 {status|public-baseline|import|baseline-check|public-upgrade|upgrade-check}" >&2
    exit 2
    ;;
esac
