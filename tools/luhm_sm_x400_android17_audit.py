#!/usr/bin/env python3
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CROWN=ROOT/'docs/CROWN_SOURCE_OF_TRUTH_20260920.json'
PKG=ROOT/'samsung-sm-x400/luhm-os/package.manifest.json'
APP=ROOT/'samsung-sm-x400/luhm-os/app/build.gradle.kts'
MANIFEST=ROOT/'samsung-sm-x400/luhm-os/app/src/main/AndroidManifest.xml'
MAIN=ROOT/'samsung-sm-x400/luhm-os/app/src/main/java/art/eggiebagelface/kai9000/dev/MainActivity.java'
ENGINE=ROOT/'samsung-sm-x400/luhm-os/app/src/main/java/art/eggiebagelface/kai9000/dev/EngineService.java'

def need(x,m):
    if not x: raise SystemExit('LUHM_AUDIT_RED: '+m)
def main():
    c=json.loads(CROWN.read_text()); p=json.loads(PKG.read_text()); g=APP.read_text(); m=MANIFEST.read_text(); j=MAIN.read_text(); e=ENGINE.read_text()
    need(c['android']['hardware_target']['model']=='SM-X400','device target')
    need(c['android']['platform_target']['api']==37,'api37 crown')
    need(c['android']['termux_runtime_dependency'] is False,'termux crown')
    need(p['runtime']['termux'] is False and p['runtime']['bash_installer'] is False,'package termux/bash')
    for s in ['compileSdk = 37','targetSdk = 37','minSdk = 31','versionCode = 9','versionName = "0.9.0-dev"']:
        need(s in g,'gradle '+s)
    need('android:label="LuHm OS"' in m,'app label')
    need('android.permission.INTERNET' not in m,'internet permission present')
    need('android:usesCleartextTraffic="false"' in m,'cleartext not disabled')
    joined=(j+'\n'+e).lower()
    for forbidden in ['termux','processbuilder','runtime.getruntime','127.0.0.1','httpurlconnection']:
        need(forbidden not in joined,'forbidden runtime dependency '+forbidden)
    need('ACTION_NOT_ALLOWLISTED' in e,'typed action deny gate')
    print('LUHM_SM_X400_SOURCE_TRUTH_GREEN')
    print('LUHM_API37_HEADLESS_PACKAGE_GREEN')
    print('TERMUX_DEPENDENCY=false')
    print('BASH_INSTALLER=false')
    print('EXTERNAL_DAEMON=false')
if __name__=='__main__': main()
