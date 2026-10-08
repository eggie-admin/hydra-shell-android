import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url));
const game=path.join(here,'..');
const gd=fs.readFileSync(path.join(game,'godot-world','scripts','world_first.gd'),'utf8');
const scene=fs.readFileSync(path.join(game,'godot-world','scenes','main.tscn'),'utf8');
const manifest=JSON.parse(fs.readFileSync(path.join(game,'godot-world','WORLD_FIRST_MANIFEST.json'),'utf8'));

assert.match(scene,/world_first\.gd/);
assert.match(gd,/KAI9000_GODOT_WORLD_FIRST_HUD_V[12]/);
assert.match(gd,/CanvasLayer/);
assert.match(gd,/Sprite3D/);
assert.match(gd,/Camera3D/);
assert.match(gd,/CORKTOWN SWITCHYARD/);
assert.match(gd,/explicit cockpit summon/);
assert.match(gd,/_plugin\.openCms\(\)/);
assert.doesNotMatch(gd,/func _ready\([\s\S]{0,700}_plugin\.openCms\(\)/);
assert.doesNotMatch(gd,/\beval\s*\(|\bnew\s+Function\s*\(/);
assert.ok(
  ['LUHM_OS_GODOT_WORLD_FIRST_HUD_1.0.7','LUHM_OS_WINDOWS_VN_CATHEDRAL_1.0.8'].includes(manifest.mutation),
  `unexpected world-first mutation ${manifest.mutation}`
);
assert.equal(manifest.main_layer,'native Godot 3D world');
assert.equal(manifest.authority.game_to_admin_escalation,false);
assert.equal(manifest.authority.cockpit_auto_open,false);
assert.equal(manifest.rights.third_party_private_reference_bundled,false);
assert.equal(manifest.authority.public_publish,'OFF');

for (const file of ['lum_world_sprite.svg','lum_hud_icon.svg']) {
  const svg=fs.readFileSync(path.join(game,'godot-world','assets',file),'utf8');
  assert.match(svg,/^<svg/);
  assert.doesNotMatch(svg,/<script|javascript:/i);
}

console.log('LUHM_GODOT_WORLD_FIRST_SOURCE_GREEN');
