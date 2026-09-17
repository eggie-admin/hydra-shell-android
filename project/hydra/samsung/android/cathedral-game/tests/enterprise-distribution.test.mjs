import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../enterprise-distribution.js', import.meta.url), 'utf8');
const sandbox = { URL, console, setTimeout, clearTimeout, AbortController, globalThis: null, __LUHM_TEST__: true, fetch: async()=>{ throw new Error('unexpected network'); } };
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(source, sandbox, { filename: 'enterprise-distribution.js' });
const core = sandbox.LuHmEnterpriseDistribution;

const sha = 'a'.repeat(64);
const release = {
  draft: false,
  prerelease: false,
  tag_name: 'v1.0.11',
  html_url: 'https://github.com/eggie-admin/hydra-shell-android/releases/tag/v1.0.11',
  assets: [
    { name: 'luhmos-release.json', browser_download_url: 'https://github.com/eggie-admin/hydra-shell-android/releases/download/v1.0.11/luhmos-release.json' },
    { name: 'luhmos-stable-1.0.11.apk', browser_download_url: 'https://github.com/eggie-admin/hydra-shell-android/releases/download/v1.0.11/luhmos-stable-1.0.11.apk' },
  ],
};
const manifest = {
  schema: 'luhm_os.release.v1', tag: 'v1.0.11', package_id: core.PROD_PACKAGE,
  version_name: '1.0.11', version_code: 111, apk_asset: 'luhmos-stable-1.0.11.apk', apk_sha256: sha,
};
function fakeFetch(url) {
  const body = String(url).endsWith('/latest') ? release : manifest;
  return Promise.resolve({ ok: true, status: 200, json: async()=>body });
}

test('pins updates to the LuHm GitHub Releases lane', () => {
  assert.equal(core.REPO, 'eggie-admin/hydra-shell-android');
  assert.equal(core.trustedReleaseAssetUrl('https://github.com/eggie-admin/hydra-shell-android/releases/download/v1.0.11/luhmos.apk'), true);
  assert.equal(core.trustedReleaseAssetUrl('https://example.test/releases/download/v1.0.11/luhmos.apk'), false);
  assert.equal(core.trustedReleaseAssetUrl('https://github.com/other/repo/releases/download/v1/luhmos.apk'), false);
});

test('stable tag and prerelease tags are channel-specific', () => {
  assert.equal(core.tagMatchesChannel('v1.2.3','stable'), true);
  assert.equal(core.tagMatchesChannel('v1.2.3-beta.2','stable'), false);
  assert.equal(core.tagMatchesChannel('v1.2.3-beta.2','beta'), true);
});

test('resolves a manifest-bound stable install plan', async () => {
  const plan = await core.resolveInstallPlan('stable', fakeFetch);
  assert.equal(plan.tag, 'v1.0.11');
  assert.equal(plan.packageId, core.PROD_PACKAGE);
  assert.equal(plan.apkSha256, sha);
  assert.match(plan.apkUrl, /\/releases\/download\/v1\.0\.11\//);
});

test('native update handoff includes digest package and tag', () => {
  const sent=[];
  const win={CathedralBridge:{postMessage(v){sent.push(JSON.parse(v));}}};
  const plan={apkUrl:'https://github.com/eggie-admin/hydra-shell-android/releases/download/v1.0.11/luhmos-stable-1.0.11.apk',apkSha256:sha,packageId:core.PROD_PACKAGE,tag:'v1.0.11'};
  assert.equal(core.postUpdate(win,plan).ok,true);
  assert.deepEqual(sent[0],{type:'app.update.install',payload:{url:plan.apkUrl,sha256:sha,package_id:core.PROD_PACKAGE,tag:'v1.0.11'}});
});

test('branded uninstall is explicit and delegates to native Android', () => {
  const sent=[];
  const win={CathedralBridge:{postMessage(v){sent.push(JSON.parse(v));}}};
  assert.equal(core.postUninstall(win).ok,true);
  assert.equal(sent.length,1);
  assert.equal(sent[0].type,'app.uninstall.open');
});

test('local harness probes only committed loopback origins', async () => {
  const seen=[];
  const fetchImpl=async url=>{seen.push(String(url)); return {ok:String(url).startsWith('http://127.0.0.1/'),status:200};};
  const out=await core.probeLocalHarness(fetchImpl);
  assert.equal(out.ok,true);
  assert.equal(out.origin,'http://127.0.0.1');
  assert.deepEqual(seen,['http://127.0.0.1/health']);
  assert.deepEqual(Array.from(core.LOCAL_BACKENDS),['http://127.0.0.1','http://localhost']);
  const privateSuffix='.'+'lan';
  assert.equal(source.includes(privateSuffix),false);
  assert.equal(seen.some(v=>v.includes('api.github.com')),false);
});
