import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url));
const source=fs.readFileSync(path.join(here,'..','final-form.js'),'utf8');

globalThis.__LUHM_TEST__=true;
vm.runInThisContext(source,{filename:'final-form.js'});
const core=globalThis.LuHmModularCockpitCore;
assert.ok(core,'core export missing');

const requiredWidgetFields=['widget_id','version','surface','mount_point','allowed_events','subscribed_state_keys','emitted_intents','required_tier','authority_ceiling','provenance_ref','ship_allowed','reduced_motion'];
for(const [id,w] of Object.entries(core.WIDGETS)){
  for(const field of requiredWidgetFields) assert.ok(Object.hasOwn(w,field),`${id} missing ${field}`);
}

let s=core.createState({session_id:'session-12345678',mode:'SPRITE_BUBBLE',realm:'GAME'});
const sid=s.session_id;
s=core.transition(s,{type:'RESTORE'});
assert.equal(s.mode,'WIDGET_DECK');
s=core.transition(s,{type:'OPEN_WIDGET',widget_id:'PARLEY'});
assert.equal(s.mode,'FULL_COCKPIT');
assert.equal(s.realm,'GAME');
assert.equal(s.active_widget,'PARLEY');
s=core.transition(s,{type:'MINIMIZE'});
assert.equal(s.mode,'SPRITE_BUBBLE');
assert.equal(s.return_target,'FULL_COCKPIT');
s=core.transition(s,{type:'RESTORE'});
assert.equal(s.mode,'FULL_COCKPIT');
assert.equal(s.session_id,sid);
assert.equal(s.active_widget,'PARLEY');
assert.equal(s.state_pass,true);

const gameToAdmin=core.routeIntent({...s,realm:'GAME'},'admin.stage_update',{});
assert.equal(gameToAdmin.status,'DENY_REALM_FIREWALL');
assert.equal(gameToAdmin.executed,false);

const adminState={...s,realm:'ADMIN',tier:'WHISPER'};
const staged=core.routeIntent(adminState,'admin.stage_update',{channel:'private'});
assert.equal(staged.status,'STAGED_RECKONING');
assert.equal(staged.executed,false);
assert.equal(staged.state.pending_reckoning.intent_id,'admin.stage_update');
assert.equal(staged.state.pending_reckoning.status,'AWAITING_EXACT_PROFESSOR_AUTHORIZATION');

let p=core.createState({session_id:'session-parley1',realm:'GAME'});
for(let i=0;i<3;i++) p=core.advanceParley(p,'CHALLENGE').state;
assert.equal(p.parley.round,3);
const fourth=core.advanceParley(p,'PROBE');
assert.equal(fourth.state.parley.round,3);
assert.equal(fourth.complete,true);

const safe=core.serializeSafeState({...staged.state,api_key:'SHOULD_NOT_SERIALIZE',token:'NOPE'});
assert.equal(Object.hasOwn(safe,'api_key'),false);
assert.equal(Object.hasOwn(safe,'token'),false);
assert.equal(safe.session_id,sid);

assert.match(source,/KAI9000_MODULAR_SPRITE_COCKPIT_V1/);
assert.match(source,/KAI9000_FOLKLORE_CROSSING_V1/);
assert.match(source,/KAI9000_PERSONAL_RECKONING_PARLEY_V1/);
assert.match(source,/ROLEPLAY VOICE|ffParleyVoice/);
assert.match(source,/TRUTH STRIP/);
assert.match(source,/MACHINE ENVELOPE|ffMachineEnvelope/);
assert.doesNotMatch(source,/\beval\s*\(/);
assert.doesNotMatch(source,/\bnew\s+Function\s*\(/);
assert.doesNotMatch(source,/\bXMLHttpRequest\b|\bWebSocket\b|\bEventSource\b/);

console.log('LUHM_MODULAR_SPRITE_COCKPIT_SOURCE_GREEN');
