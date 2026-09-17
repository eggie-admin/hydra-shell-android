import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../apk-install-gui.js', import.meta.url), 'utf8');
const sandbox = {
  URL,
  console,
  globalThis: null,
  __LUHM_TEST__: true,
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(source, sandbox, { filename: 'apk-install-gui.js' });

const core = sandbox.LuHmApkInstallGuiCore;

test('exports a deterministic install contract', () => {
  assert.equal(core.EVENT, 'app.update.install');
  assert.equal(core.APP_HOST, 'appassets.androidplatform.net');
});

test('rejects empty, malformed, and non-HTTPS URLs', () => {
  assert.equal(core.normalizeUrl('').ok, false);
  assert.equal(core.normalizeUrl('not a url').ok, false);
  assert.equal(core.normalizeUrl('http://example.test/luhmos.apk').ok, false);
});

test('builds only the native app.update.install message', () => {
  const out = core.makeInstallMessage('https://example.test/luhmos.apk');
  assert.equal(out.ok, true);
  assert.equal(out.message.type, 'app.update.install');
  assert.equal(out.message.payload.url, 'https://example.test/luhmos.apk');
});

test('requires packaged appassets origin and native bridge', () => {
  const good = { location: { hostname: 'appassets.androidplatform.net' }, CathedralBridge: { postMessage() {} } };
  const web = { location: { hostname: 'example.test' }, CathedralBridge: { postMessage() {} } };
  assert.equal(core.nativeAvailable(good), true);
  assert.equal(core.nativeAvailable(web), false);
});

test('postInstall sends one JSON message only after explicit call', () => {
  const sent = [];
  const win = {
    location: { hostname: 'appassets.androidplatform.net' },
    CathedralBridge: { postMessage(value) { sent.push(JSON.parse(value)); } },
  };
  assert.equal(sent.length, 0);
  const result = core.postInstall(win, 'https://example.test/luhmos.apk');
  assert.equal(result.ok, true);
  assert.equal(sent.length, 1);
  assert.deepEqual(sent[0], { type: 'app.update.install', payload: { url: 'https://example.test/luhmos.apk' } });
});

test('native update events become UI status without granting authority', () => {
  const verified = core.parseNativeEvent(JSON.stringify({ type: 'app.update.verified', payload: { message: 'verified' } }));
  const success = core.parseNativeEvent(JSON.stringify({ type: 'app.update.success', payload: { message: 'installed' } }));
  assert.equal(verified.message, 'verified');
  assert.equal(verified.terminal, false);
  assert.equal(success.terminal, true);
  assert.equal(core.parseNativeEvent(JSON.stringify({ type: 'other.event' })), null);
});
