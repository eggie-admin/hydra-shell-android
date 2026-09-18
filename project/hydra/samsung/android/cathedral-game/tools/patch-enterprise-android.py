#!/usr/bin/env python3
"""Deterministically harden the pinned Cathedral Android bridge for LuHm enterprise distribution."""
from __future__ import annotations

import sys
from pathlib import Path

MARKER = "LUHM_ENTERPRISE_DISTRIBUTION_NATIVE_V1"
REPO_PATH_PREFIX = "/eggie-admin/hydra-shell-android/releases/download/"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"ENTERPRISE_ANDROID_PATCH_RED: {label} expected once, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: patch-enterprise-android.py CathedralAndroidPlugin.kt")
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print("LUHM_ENTERPRISE_ANDROID_PATCH_ALREADY_GREEN")
        return 0

    text = replace_once(
        text,
        '        private const val MAX_APK_BYTES = 350L * 1024L * 1024L\n',
        '        private const val MAX_APK_BYTES = 350L * 1024L * 1024L\n'
        '        private const val RELEASE_HOST = "github.com"\n'
        f'        private const val RELEASE_PATH_PREFIX = "{REPO_PATH_PREFIX}"\n'
        f'        private const val ENTERPRISE_MARKER = "{MARKER}"\n',
        "enterprise constants",
    )

    old_listener = '''                if (parsed?.optString("type") == "app.update.install") {
                    val payload = parsed.optJSONObject("payload")
                    val updateUrl = payload?.optString("url").orEmpty()
                    beginApkUpdate(updateUrl)
                }
'''
    new_listener = '''                when (parsed?.optString("type")) {
                    "app.update.install" -> {
                        val payload = parsed.optJSONObject("payload")
                        val updateUrl = payload?.optString("url").orEmpty()
                        val expectedSha256 = payload?.optString("sha256").orEmpty()
                        val expectedPackageId = payload?.optString("package_id").orEmpty()
                        beginApkUpdate(updateUrl, expectedSha256, expectedPackageId)
                    }
                    "app.uninstall.open" -> openUninstallConfirmation()
                    "app.window.immersive" -> setImmersiveKiosk(true)
                    "app.window.system_bars" -> setImmersiveKiosk(false)
                    "app.quit" -> requestQuit()
                }
'''
    text = replace_once(text, old_listener, new_listener, "bridge dispatch")

    old_nav = '''                if (uri.scheme == "https" && uri.host == "appassets.androidplatform.net") {
                    return false
                }
'''
    new_nav = '''                if (uri.scheme == "https" && uri.host == "appassets.androidplatform.net") {
                    return false
                }
                if (
                    uri.scheme == "http" &&
                    (uri.host == "127.0.0.1" || uri.host == "localhost") &&
                    uri.port == 8791
                ) {
                    return false
                }
'''
    text = replace_once(text, old_nav, new_nav, "loopback navigation")

    old_begin = '''    private fun beginApkUpdate(rawUrl: String) {
        val hostActivity = activity ?: run {
            emitUpdateEvent("app.update.error", "Android host activity unavailable.")
            return
        }
        val uri = runCatching { Uri.parse(rawUrl.trim()) }.getOrNull()
        if (uri == null || uri.scheme != "https" || uri.host.isNullOrBlank()) {
            emitUpdateEvent("app.update.error", "Update URL must be HTTPS.")
            return
        }

        if (!canRequestPackageInstalls(hostActivity)) {
'''
    new_begin = '''    private fun beginApkUpdate(rawUrl: String, expectedSha256: String, expectedPackageId: String) {
        val hostActivity = activity ?: run {
            emitUpdateEvent("app.update.error", "Android host activity unavailable.")
            return
        }
        val uri = runCatching { Uri.parse(rawUrl.trim()) }.getOrNull()
        val digest = expectedSha256.trim().lowercase()
        if (uri == null || uri.scheme != "https" || uri.host != RELEASE_HOST || !uri.path.orEmpty().startsWith(RELEASE_PATH_PREFIX)) {
            emitUpdateEvent("app.update.error", "Update rejected: only LuHm GitHub Release assets are allowed.")
            return
        }
        if (!digest.matches(Regex("^[0-9a-f]{64}$"))) {
            emitUpdateEvent("app.update.error", "Update rejected: release manifest SHA-256 is missing or invalid.")
            return
        }
        if (expectedPackageId != hostActivity.packageName) {
            emitUpdateEvent("app.update.error", "Update rejected: release package does not match this LuHm installation.")
            return
        }

        if (!canRequestPackageInstalls(hostActivity)) {
'''
    text = replace_once(text, old_begin, new_begin, "update entry validation")

    text = replace_once(
        text,
        '        Thread({ downloadVerifyAndInstall(hostActivity.applicationContext, uri.toString()) }, "luhmos-apk-updater").start()\n',
        '        Thread({ downloadVerifyAndInstall(hostActivity.applicationContext, uri.toString(), digest) }, "luhmos-apk-updater").start()\n',
        "updater thread",
    )
    text = replace_once(
        text,
        '    private fun downloadVerifyAndInstall(context: Context, url: String) {\n',
        '    private fun downloadVerifyAndInstall(context: Context, url: String, expectedSha256: String) {\n',
        "download signature",
    )
    text = replace_once(
        text,
        '            val sha256 = digest.digest().joinToString("") { "%02x".format(it) }\n\n            val packageManager = context.packageManager\n',
        '            val sha256 = digest.digest().joinToString("") { "%02x".format(it) }\n'
        '            if (sha256 != expectedSha256) error("Rejected APK: SHA-256 does not match GitHub release manifest")\n\n'
        '            val packageManager = context.packageManager\n',
        "digest enforcement",
    )

    anchor = '''    private fun emitUpdateEvent(type: String, message: String) {
'''
    uninstall = '''    private fun requestQuit() {
        runOnHostThread {
            val hostActivity = activity ?: return@runOnHostThread
            hostActivity.finishAndRemoveTask()
        }
    }

    private fun openUninstallConfirmation() {
        val hostActivity = activity ?: run {
            emitUpdateEvent("app.uninstall.error", "Android host activity unavailable.")
            return
        }
        runOnHostThread {
            val intent = Intent(Intent.ACTION_DELETE, Uri.parse("package:${hostActivity.packageName}"))
            runCatching { hostActivity.startActivity(intent) }
                .onSuccess { emitUpdateEvent("app.uninstall.opened", "Android removal confirmation opened for LuHm OS.") }
                .onFailure { emitUpdateEvent("app.uninstall.error", it.message ?: "Unable to open Android removal confirmation.") }
        }
    }

'''
    text = replace_once(text, anchor, uninstall + anchor, "uninstall action")

    path.write_text(text, encoding="utf-8")
    print("LUHM_ENTERPRISE_ANDROID_PATCH_GREEN")
    print(f"marker={MARKER}")
    print(f"release_path_prefix={REPO_PATH_PREFIX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
