#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CROWN = ROOT / 'docs/CROWN_SOURCE_OF_TRUTH_20260920.json'
PKG = ROOT / 'samsung-sm-x400/luhm-os/package.manifest.json'
APP = ROOT / 'samsung-sm-x400/luhm-os/app/build.gradle.kts'
MANIFEST = ROOT / 'samsung-sm-x400/luhm-os/app/src/main/AndroidManifest.xml'
MAIN = ROOT / 'samsung-sm-x400/luhm-os/app/src/main/java/art/eggiebagelface/kai9000/dev/MainActivity.java'
ASSETS = ROOT / 'samsung-sm-x400/luhm-os/app/src/main/assets/cathedral-assets.json'
INDEX = ROOT / 'samsung-sm-x400/luhm-os/app/src/main/assets/index.html'
GODOT_PROJECT = ROOT / 'samsung-sm-x400/luhm-os/app/src/main/assets/project.godot'
GODOT_SCENE = ROOT / 'samsung-sm-x400/luhm-os/app/src/main/assets/main.tscn'
GODOT_SCRIPT = ROOT / 'samsung-sm-x400/luhm-os/app/src/main/assets/main.gd'

EXPECTED = {
    'CURRENT_LUM_MIDNIGHT_1996_MODEL_SHEET.png': '60a84012d60965c3cfb02c2f94aaeca11401f0965c85595fc9ebcc79a0961ce0',
    'CURRENT_KAI9000_GAME_WORLD_BIBLE.png': 'fe6cbd614e5078c21b7de4896eaff2c600329ab1cb969694d45669ad8b1c7175',
    'CURRENT_KAI9000_CATHEDRAL_POSTER.png': '02a7b16dd88c6574d9f230c45335736fdebe9098002ea1fb42c7001497aaf794',
    'CURRENT_LUM_ANIMATED_REEL.mp4': '1a20bd7bf495ee930d2cc9dab9342d7cb29d326ce0c7f433c206581ebdddad97',
    'KAI9000_LUM_AVATAR_ACTUAL_ANIMATED.gif': 'a9df1d2b5c63d5740be8c476b59f389171b99609a14cd02fc8ae7568d27b2aba',
    'KAI9000_LUM_AVATAR_ACTUAL_ANIMATED.manifest.json': '6b95f05e2532464022fa363c1d067755c3358600cfced0d791fd9fd7b95e2742'
}

def need(value, message):
    if not value:
        raise SystemExit('LUHM_AUDIT_RED: ' + message)

def main():
    c = json.loads(CROWN.read_text())
    p = json.loads(PKG.read_text())
    a = json.loads(ASSETS.read_text())
    g = APP.read_text()
    m = MANIFEST.read_text()
    j = MAIN.read_text()
    h = INDEX.read_text()
    project = GODOT_PROJECT.read_text()
    scene = GODOT_SCENE.read_text()
    script = GODOT_SCRIPT.read_text()

    need(c['android']['hardware_target']['model'] == 'SM-X400', 'device target')
    need(c['android']['platform_target']['api'] == 37, 'api37 crown baseline')
    need(c['android']['termux_runtime_dependency'] is False, 'termux crown baseline')

    need(p['app']['version_name'] == '0.10.0-dev' and p['app']['version_code'] == 10, 'game candidate version')
    need(p['game']['engine'] == 'Godot 4.7.2 stable', 'Godot version')
    need(p['game']['questforge_engineering_authority'] is False, 'Questforge authority boundary')
    need(p['runtime']['termux'] is False and p['runtime']['bash_installer'] is False, 'package termux/bash')
    need(p['runtime']['webview_primary_runtime'] is False, 'WebView still primary runtime')

    for s in ['compileSdk = 37', 'targetSdk = 37', 'minSdk = 31', 'versionCode = 10', 'versionName = "0.10.0-dev"']:
        need(s in g, 'gradle ' + s)
    need('implementation("org.godotengine:godot:4.7.2.stable")' in g, 'Godot Android AAR dependency')

    need('android:label="LuHm OS"' in m, 'app label')
    need('android.permission.INTERNET' not in m, 'internet permission present')
    need('android:usesCleartextTraffic="false"' in m, 'cleartext not disabled')
    need('android:glEsVersion="0x00030000"' in m, 'GLES3 requirement missing')
    need('extends GodotActivity' in j, 'MainActivity is not GodotActivity')
    need('WebView' not in j, 'WebView remains in primary activity')

    joined = (j + '\n' + script).lower()
    for forbidden in ['com.termux', 'termux-api', 'processbuilder', 'runtime.getruntime', '127.0.0.1', 'httpurlconnection', '/bin/bash', '/system/bin/sh']:
        need(forbidden not in joined, 'forbidden runtime dependency ' + forbidden)

    need('run/main_scene="res://main.tscn"' in project, 'Godot main scene')
    need('renderer/rendering_method="gl_compatibility"' in project, 'mobile compatibility renderer')
    need('type="Node3D"' in scene, 'main scene is not Node3D')
    for token in ['CharacterBody3D', 'Camera3D', 'CollisionShape3D', '_physics_process', '_interact', 'user://iron_saint_save.json', 'WITNESS ACKNOWLEDGED']:
        need(token in script, '3D gameplay token missing: ' + token)
    need('CURRENT_KAI9000_CATHEDRAL_POSTER.png' in script, 'canonical Cathedral poster not used in 3D world')
    need('CURRENT_LUM_MIDNIGHT_1996_MODEL_SHEET.png' in script, 'canonical Lum model sheet not used in 3D world')

    need(a['id'] == 'LUHM_OS_CATHEDRAL_CANONICAL_ASSETS_20260921', 'canonical asset manifest id')
    got = {x['name']: x['sha256'] for x in a['drive_assets']}
    need(got == EXPECTED, 'canonical Drive cargo or hashes drifted')
    need(len(a['repo_assets']) == 3, 'LuHm brand cargo count')
    need(all(x['class'] in {'CURRENT_PRODUCTION_ANCHOR', 'SEALED_LUHM_ORIGINAL', 'SEALED_LUHM_ORIGINAL_MANIFEST'} for x in a['drive_assets']), 'uncleared Drive asset class')
    excluded = {x.get('name', x.get('pattern')): x['reason'] for x in a['explicit_exclusions']}
    need('00000000.txt' in excluded and 'c246_10.pck.bin' in excluded, 'third-party quarantine exclusions missing')
    need('AI_GENERATED_DEMO_ONLY' in excluded['luhm_*_demo.png'], 'prototype demo exclusion missing')
    need('http://' not in h and 'https://' not in h, 'external URL in legacy Cathedral UI')

    print('LUHM_SM_X400_SOURCE_TRUTH_GREEN')
    print('LUHM_API37_HEADLESS_PACKAGE_GREEN')
    print('LUHM_GODOT3D_SOURCE_GREEN')
    print('IRON_SAINT_PLAYABLE_SOURCE_GREEN')
    print('GODOT_VERSION=4.7.2.stable')
    print('CANONICAL_DRIVE_ASSETS=6')
    print('PUBLIC_BRAND_ASSETS=3')
    print('TERMUX_DEPENDENCY=false')
    print('BASH_INSTALLER=false')
    print('EXTERNAL_DAEMON=false')

if __name__ == '__main__':
    main()
