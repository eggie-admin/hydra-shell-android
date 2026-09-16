import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const game = path.join(here, '..');
const world = path.join(game, 'godot-world');

const read = p => fs.readFileSync(p, 'utf8');
const worldFirst = read(path.join(world, 'scripts', 'world_first.gd'));
const desktop = read(path.join(world, 'scripts', 'ui', 'desktop_shell.gd'));
const manager = read(path.join(world, 'scripts', 'ui', 'window_manager.gd'));
const settings = read(path.join(world, 'scripts', 'ui', 'settings_store.gd'));

assert.match(worldFirst, /LUHM_OS_WINDOWS_VN_CATHEDRAL_1_0_8/);
assert.match(worldFirst, /DesktopShellScript/);
assert.match(worldFirst, /_plugin\.openCms\(\)/);
assert.match(worldFirst, /DESK/);
assert.match(worldFirst, /show_dialogue/);
assert.doesNotMatch(worldFirst, /func _ready\([^)]*\)[\s\S]{0,300}_plugin\.openCms\(\)/);

assert.match(desktop, /extends CanvasLayer/);
assert.match(desktop, /VISUAL|dialogue/i);
assert.match(desktop, /SETTINGS/);
assert.match(desktop, /FRONT \/ BACK/);
assert.match(desktop, /GAME cannot grant ADMIN authority/);
assert.match(desktop, /typed_intent/);
assert.match(desktop, /toggle_window/);
assert.match(desktop, /user:\/\/luhm_ui_settings\.json|SettingsStoreScript/);

assert.match(manager, /InputEventScreenDrag/);
assert.match(manager, /focus_window/);
assert.match(manager, /_snap_inside/);
assert.match(settings, /offline_fallback/);
assert.match(settings, /explicit_crown_required/);
assert.match(settings, /game_may_grant_admin/);

const forbidden = /\beval\s*\(|\bOS\.execute\s*\(|\bFileAccess\.open\([^\n]*res:\/\/.*WRITE|\bHTTPRequest\b|\bWebSocketPeer\b/;
for (const [name, source] of Object.entries({worldFirst, desktop, manager, settings})) {
  assert.doesNotMatch(source, forbidden, `${name} contains forbidden execution/network lane`);
}

console.log('LUHM_WINDOWS_VN_CATHEDRAL_SOURCE_GREEN');
