/* KAI9000_FINAL_FORM_PET_V2
   KAI9000_MODULAR_SPRITE_COCKPIT_V1
   KAI9000_FOLKLORE_CROSSING_V1
   KAI9000_PERSONAL_RECKONING_PARLEY_V1
   KAI9000_CROWN_GATE_V1
   Presentation-only LuHm cockpit. No eval, no shell, no background network fetch.
   UI scale, roleplay state, and AI-to-AI consensus never grant machine authority. */
(()=>{'use strict';
const MODES=Object.freeze(['SPRITE_BUBBLE','WIDGET_DECK','FULL_COCKPIT']);
const REALMS=Object.freeze(['GAME','ADMIN','SYSTEM']);
const TIERS=Object.freeze(['WHISPER','CROSSING','RECKONING']);
const TIER_RANK=Object.freeze({WHISPER:0,CROSSING:1,RECKONING:2});
const WIDGETS=Object.freeze({
  PET:{widget_id:'PET',version:1,surface:'GAME',mount_point:'pet',allowed_events:['game.bond','game.roll','game.save'],subscribed_state_keys:['mode','session_id'],emitted_intents:['game.bond','game.roll','game.save'],required_tier:'WHISPER',authority_ceiling:'GAME_ONLY',provenance_ref:'KAI9000_LUHM_MODULAR_SPRITE_COCKPIT_20260916',ship_allowed:true,reduced_motion:'static'},
  QUEST:{widget_id:'QUEST',version:1,surface:'GAME',mount_point:'quest',allowed_events:['game.explore','game.contact','game.date'],subscribed_state_keys:['mode','session_id'],emitted_intents:['game.explore','game.contact','game.date'],required_tier:'WHISPER',authority_ceiling:'GAME_ONLY',provenance_ref:'KAI9000_LUHM_MODULAR_SPRITE_COCKPIT_20260916',ship_allowed:true,reduced_motion:'static'},
  PARLEY:{widget_id:'PARLEY',version:1,surface:'GAME',mount_point:'parley',allowed_events:['parley.probe','parley.challenge','parley.corroborate','parley.reckon'],subscribed_state_keys:['parley','tier','session_id'],emitted_intents:['parley.probe','parley.challenge','parley.corroborate','parley.reckon'],required_tier:'WHISPER',authority_ceiling:'PRESENTATION_ONLY',provenance_ref:'KAI9000_PERSONAL_RECKONING_PARLEY_20260916',ship_allowed:true,reduced_motion:'static'},
  STATUS:{widget_id:'STATUS',version:1,surface:'SYSTEM',mount_point:'status',allowed_events:['status.read'],subscribed_state_keys:['mode','realm','tier','layout_profile','session_id','state_pass'],emitted_intents:['status.read'],required_tier:'WHISPER',authority_ceiling:'READ_ONLY',provenance_ref:'LUHM_OS_CROWN_GATE_RECONCILED_DOCTRINE_20260916',ship_allowed:true,reduced_motion:'static'},
  MEDIA:{widget_id:'MEDIA',version:1,surface:'GAME',mount_point:'media',allowed_events:['media.local.select'],subscribed_state_keys:['session_id'],emitted_intents:['media.local.select'],required_tier:'WHISPER',authority_ceiling:'LOCAL_PRESENTATION_ONLY',provenance_ref:'KAI9000_LUHM_MODULAR_SPRITE_COCKPIT_20260916',ship_allowed:true,reduced_motion:'static'},
  UPDATE:{widget_id:'UPDATE',version:1,surface:'ADMIN',mount_point:'update',allowed_events:['admin.open_update_vault','admin.stage_update'],subscribed_state_keys:['pending_reckoning','session_id'],emitted_intents:['admin.open_update_vault','admin.stage_update'],required_tier:'RECKONING',authority_ceiling:'STAGE_ONLY',provenance_ref:'LUHM_OS_CROWN_GATE_RECONCILED_DOCTRINE_20260916',ship_allowed:true,reduced_motion:'static'},
  CROWN:{widget_id:'CROWN',version:1,surface:'ADMIN',mount_point:'crown',allowed_events:['admin.crown.local_proof','admin.crown.stage_seal'],subscribed_state_keys:['proof','pending_reckoning','session_id'],emitted_intents:['admin.crown.stage_seal'],required_tier:'RECKONING',authority_ceiling:'STAGE_ONLY',provenance_ref:'LUHM_OS_CROWN_GATE_RECONCILED_DOCTRINE_20260916',ship_allowed:true,reduced_motion:'static'},
  LOG:{widget_id:'LOG',version:1,surface:'ADMIN',mount_point:'log',allowed_events:['admin.log.read'],subscribed_state_keys:['session_id'],emitted_intents:['admin.log.read'],required_tier:'WHISPER',authority_ceiling:'READ_ONLY',provenance_ref:'LUHM_OS_CROWN_GATE_RECONCILED_DOCTRINE_20260916',ship_allowed:true,reduced_motion:'static'}
});
const INTENTS=Object.freeze({
  'game.bond':{realm:'GAME',tier:'WHISPER',effect:'LOCAL_GAME'},
  'game.roll':{realm:'GAME',tier:'WHISPER',effect:'LOCAL_GAME'},
  'game.save':{realm:'GAME',tier:'WHISPER',effect:'LOCAL_GAME'},
  'game.explore':{realm:'GAME',tier:'WHISPER',effect:'LOCAL_GAME'},
  'game.contact':{realm:'GAME',tier:'WHISPER',effect:'LOCAL_GAME'},
  'game.date':{realm:'GAME',tier:'WHISPER',effect:'LOCAL_GAME'},
  'parley.probe':{realm:'GAME',tier:'WHISPER',effect:'PARLEY'},
  'parley.challenge':{realm:'GAME',tier:'WHISPER',effect:'PARLEY'},
  'parley.corroborate':{realm:'GAME',tier:'WHISPER',effect:'PARLEY'},
  'parley.reckon':{realm:'GAME',tier:'WHISPER',effect:'PARLEY'},
  'status.read':{realm:'SYSTEM',tier:'WHISPER',effect:'READ_ONLY'},
  'media.local.select':{realm:'GAME',tier:'WHISPER',effect:'LOCAL_PRESENTATION_ONLY'},
  'admin.log.read':{realm:'ADMIN',tier:'WHISPER',effect:'READ_ONLY'},
  'admin.open_update_vault':{realm:'ADMIN',tier:'RECKONING',effect:'STAGE_ONLY'},
  'admin.stage_update':{realm:'ADMIN',tier:'RECKONING',effect:'STAGE_ONLY'},
  'admin.crown.stage_seal':{realm:'ADMIN',tier:'RECKONING',effect:'STAGE_ONLY'}
});
const PARLEY_PHASES=Object.freeze(['OPEN','COUNTER','RECKON']);
const defaultProof=Object.freeze({install:false,saveReload:false,secureFolder:false,reboot:false});
function copyProof(v){return {...defaultProof,...(v&&typeof v==='object'?v:{})}}
function safeMode(v){return MODES.includes(v)?v:'SPRITE_BUBBLE'}
function safeRealm(v){return REALMS.includes(v)?v:'GAME'}
function safeTier(v){return TIERS.includes(v)?v:'WHISPER'}
function safeWidget(v){return v&&WIDGETS[v]?v:null}
function makeSessionId(saved){if(typeof saved==='string'&&saved.length>=8)return saved;if(globalThis.crypto?.randomUUID)return globalThis.crypto.randomUUID();return `luhm-${Date.now().toString(36)}-${Math.random().toString(36).slice(2,10)}`}
function detectLayout(width=globalThis.innerWidth||1080){if(width<700)return 'portrait_phone';if(width<1100)return 'tablet';return 'desktop'}
function createState(saved={}){
  const mode=safeMode(saved.mode);
  return {
    mode,
    realm:safeRealm(saved.realm),
    active_widget:safeWidget(saved.active_widget),
    return_target:MODES.includes(saved.return_target)&&saved.return_target!=='SPRITE_BUBBLE'?saved.return_target:'WIDGET_DECK',
    session_id:makeSessionId(saved.session_id),
    state_pass:true,
    pending_reckoning:saved.pending_reckoning&&typeof saved.pending_reckoning==='object'?{...saved.pending_reckoning}:null,
    layout_profile:['portrait_phone','tablet','desktop'].includes(saved.layout_profile)?saved.layout_profile:detectLayout(saved.viewport_width),
    tier:safeTier(saved.tier),
    x:Number.isFinite(saved.x)?saved.x:null,
    y:Number.isFinite(saved.y)?saved.y:null,
    final:!!saved.final,
    proof:copyProof(saved.proof),
    parley:{round:Math.max(0,Math.min(3,Number(saved.parley?.round)||0)),phase:PARLEY_PHASES.includes(saved.parley?.phase)?saved.parley.phase:'OPEN',mode:typeof saved.parley?.mode==='string'?saved.parley.mode:'PROBE'}
  };
}
function transition(input,event={}){
  const s=createState(input);
  switch(event.type){
    case 'MINIMIZE':
      if(s.mode!=='SPRITE_BUBBLE')s.return_target=s.mode;
      s.mode='SPRITE_BUBBLE';
      break;
    case 'RESTORE':
      s.mode=s.return_target==='FULL_COCKPIT'?'FULL_COCKPIT':'WIDGET_DECK';
      break;
    case 'OPEN_DECK':
      s.mode='WIDGET_DECK';s.return_target='WIDGET_DECK';
      break;
    case 'OPEN_FULL':
      s.mode='FULL_COCKPIT';s.return_target='FULL_COCKPIT';
      break;
    case 'OPEN_WIDGET':{
      const id=safeWidget(event.widget_id);
      if(!id)break;
      s.active_widget=id;s.realm=WIDGETS[id].surface;s.mode=event.full===false?'WIDGET_DECK':'FULL_COCKPIT';s.return_target=s.mode;
      break;
    }
    case 'SET_REALM':
      s.realm=safeRealm(event.realm);
      break;
    case 'STAGE_RECKONING':
      s.pending_reckoning={intent_id:String(event.intent_id||'unknown'),payload:event.payload&&typeof event.payload==='object'?{...event.payload}:{},requested_at:event.requested_at||'local-ui',status:'AWAITING_EXACT_PROFESSOR_AUTHORIZATION'};
      break;
    case 'CLEAR_RECKONING':
      s.pending_reckoning=null;
      break;
  }
  s.state_pass=true;
  return s;
}
function routeIntent(input,intent_id,payload={}){
  const s=createState(input);
  const contract=INTENTS[intent_id];
  if(!contract)return {status:'DENY_UNKNOWN_INTENT',executed:false,state:s};
  if(s.realm!==contract.realm)return {status:'DENY_REALM_FIREWALL',executed:false,state:s};
  if(TIER_RANK[safeTier(s.tier)]<TIER_RANK[contract.tier]){
    if(contract.tier==='RECKONING')return {status:'STAGED_RECKONING',executed:false,state:transition(s,{type:'STAGE_RECKONING',intent_id,payload})};
    return {status:'DENY_TIER',executed:false,state:s};
  }
  if(contract.tier==='RECKONING')return {status:'STAGED_RECKONING',executed:false,state:transition(s,{type:'STAGE_RECKONING',intent_id,payload})};
  return {status:'ALLOW_PRESENTATION_LOCAL',executed:false,state:s,effect:contract.effect};
}
function advanceParley(input,mode='PROBE'){
  const s=createState(input);
  if(s.parley.round>=3)return {state:s,complete:true,phase:'RECKON'};
  const round=s.parley.round+1;
  s.parley={round,phase:PARLEY_PHASES[round-1],mode:String(mode||'PROBE').toUpperCase()};
  return {state:s,complete:round>=3,phase:s.parley.phase};
}
function serializeSafeState(input){
  const s=createState(input);
  return {mode:s.mode,realm:s.realm,active_widget:s.active_widget,return_target:s.return_target,session_id:s.session_id,state_pass:true,pending_reckoning:s.pending_reckoning,layout_profile:s.layout_profile,tier:s.tier,x:s.x,y:s.y,final:s.final,proof:copyProof(s.proof),parley:{...s.parley}};
}
const core=Object.freeze({MODES,REALMS,TIERS,WIDGETS,INTENTS,PARLEY_PHASES,createState,transition,routeIntent,advanceParley,serializeSafeState,detectLayout});
globalThis.LuHmModularCockpitCore=core;
if(globalThis.__LUHM_TEST__)return;

const $=(s,r=document)=>r.querySelector(s);
const $$=(s,r=document)=>Array.from(r.querySelectorAll(s));
const storageKey='luhmos_modular_sprite_cockpit_v1';
const legacyKey='luhmos_final_form_pet_v1';
const updateVault='https://drive.google.com/drive/folders/17nODHVpnjQ1jtzJxvjxy0Ec1X-osLCkB';
function readSaved(){for(const key of [storageKey,legacyKey]){try{const v=JSON.parse(localStorage.getItem(key)||'null');if(v&&typeof v==='object')return v}catch{}}return {}}
let state=core.createState(readSaved());
function save(){try{localStorage.setItem(storageKey,JSON.stringify(core.serializeSafeState(state)))}catch{}}
function latestDialogue(){return ($('#dialogue')?.textContent||'Cathedral is awake.').trim()}
function pressGame(action){const b=document.querySelector(`[data-a="${action}"]`);if(b){b.click();return true}return false}
function logLine(text){const log=$('#ffLog');if(!log)return;const e=document.createElement('div');e.className='entry';const b=document.createElement('b');b.textContent='LUHM';e.append(b,document.createTextNode(' '+text));log.prepend(e)}
function allPhysicalProof(){return Object.values(state.proof).every(Boolean)}
function setState(next,reason){const before=state.session_id;state=core.createState(next);if(state.session_id!==before)state.session_id=before;state.state_pass=true;save();render();if(reason)logLine(reason)}
function openWidget(id,full=true){if(!WIDGETS[id])return;setState(core.transition(state,{type:'OPEN_WIDGET',widget_id:id,full}),`Widget ${id} opened in ${WIDGETS[id].surface}.`)}
function emitIntent(intent,payload={}){
  const routed=core.routeIntent(state,intent,payload);
  state=routed.state;save();render();
  if(routed.status==='STAGED_RECKONING'){logLine(`${intent} staged. Exact Professor authorization remains required.`);return routed}
  if(routed.status.startsWith('DENY_')){logLine(`${intent} denied by ${routed.status}.`);return routed}
  if(routed.effect==='LOCAL_GAME'){
    const action=intent.split('.').pop();
    pressGame(action);
    setTimeout(()=>{const line=$('#ffDialogue');if(line)line.textContent=latestDialogue()},30);
  }
  logLine(`${intent} accepted as ${routed.effect}.`);
  return routed;
}
function parley(mode){
  const intent=`parley.${String(mode).toLowerCase()}`;
  const routed=core.routeIntent(state,intent,{});
  if(routed.status.startsWith('DENY_')){state=routed.state;save();render();return}
  const out=core.advanceParley(routed.state,mode);
  state=out.state;save();renderParley();renderHeader();
  logLine(`Parley ${state.parley.phase}: ${state.parley.mode}. No hidden AI call was made.`);
}
function renderHeader(){
  const meta=$('#ffMeta');if(meta)meta.textContent=`${state.mode} · ${state.realm} · ${state.tier}`;
  $$('.ff-realm').forEach(b=>b.classList.toggle('active',b.dataset.realm===state.realm));
  const pending=$('#ffPending');if(pending)pending.textContent=state.pending_reckoning?`PENDING RECKONING: ${state.pending_reckoning.intent_id}`:'NO PENDING RECKONING';
}
function renderCrown(){
  $$('.ff-proof').forEach(b=>{const key=b.dataset.proof;const ok=!!state.proof[key];b.dataset.ok=ok?'1':'0';const small=b.querySelector('small');if(small)small.textContent=ok?'LOCAL CONFIRMATION SAVED':'TAP AFTER PHYSICAL PROOF'});
  const complete=allPhysicalProof();const s=$('#ffCrownState');
  if(s){s.classList.toggle('complete',complete);s.classList.toggle('pending',!complete);s.textContent=complete?'LOCAL PROOF CHECKLIST COMPLETE':'SOURCE/CI GREEN · DEVICE PROOF PENDING'}
  document.body.classList.toggle('luhm-crown-complete',complete);
}
function renderParley(){
  const phase=$('#ffParleyPhase');if(phase)phase.textContent=`${state.parley.phase} · ROUND ${state.parley.round}/3`;
  const voice=$('#ffParleyVoice');if(voice)voice.textContent=state.parley.round===0?'Lum waits at the threshold. Pick a bounded Parley mode.':state.parley.phase==='OPEN'?`Lum opens ${state.parley.mode.toLowerCase()} with a bounded question.`:state.parley.phase==='COUNTER'?'Countervoice challenges the claim and asks for evidence.':'Reckon: disagreements stay AMBER until proof resolves them.';
  const truth=$('#ffTruthStrip');if(truth)truth.textContent='TRUTH STRIP: local presentation only · no hidden agent call · consensus is not approval';
  const env=$('#ffMachineEnvelope');if(env)env.textContent=JSON.stringify({schema:'luhm.parley.v1',session_id:state.session_id,tier:state.tier,phase:state.parley.phase,round:state.parley.round,mode:state.parley.mode,authority:'Professor',mutation_authority:false},null,2);
  $$('.ff-parley-action').forEach(b=>b.disabled=state.parley.round>=3);
}
function renderDeck(){
  const host=$('#ffDeckWidgets');if(!host)return;host.innerHTML='';
  Object.values(WIDGETS).forEach(w=>{const b=document.createElement('button');b.type='button';b.className='ff-deck-widget';b.dataset.realm=w.surface;b.innerHTML=`<b>${w.widget_id}</b><small>${w.surface} · ${w.required_tier}</small>`;b.addEventListener('click',()=>openWidget(w.widget_id,true));host.append(b)});
}
function renderWidget(){
  $$('.ff-widget-pane').forEach(p=>p.hidden=p.dataset.widget!==state.active_widget);
  $$('.ff-widget-tab').forEach(b=>b.classList.toggle('active',b.dataset.widget===state.active_widget));
  if(state.active_widget==='PET'){const d=$('#ffDialogue');if(d)d.textContent=latestDialogue()}
  if(state.active_widget==='PARLEY')renderParley();
  if(state.active_widget==='CROWN')renderCrown();
  if(state.active_widget==='STATUS'){
    const s=$('#ffStatusJson');if(s)s.textContent=JSON.stringify({mode:state.mode,realm:state.realm,active_widget:state.active_widget,return_target:state.return_target,session_id:state.session_id,state_pass:true,pending_reckoning:state.pending_reckoning?state.pending_reckoning.intent_id:null,layout_profile:state.layout_profile,tier:state.tier},null,2);
  }
}
function render(){
  const bubble=$('#luhmPetBubble'),deck=$('#luhmWidgetDeck'),panel=$('#luhmPetPanel');
  if(!bubble||!deck||!panel)return;
  bubble.hidden=state.mode!=='SPRITE_BUBBLE';deck.hidden=state.mode!=='WIDGET_DECK';panel.hidden=state.mode!=='FULL_COCKPIT';
  document.body.dataset.luhmMode=state.mode;document.body.dataset.luhmRealm=state.realm;
  renderHeader();renderWidget();renderCrown();
}
function toggleProof(key){if(!(key in state.proof))return;state.proof[key]=!state.proof[key];save();renderCrown();logLine(`${key} local proof ${state.proof[key]?'marked':'cleared'}.`)}
function clearProof(){state.proof=copyProof(null);save();renderCrown();logLine('Physical proof checklist cleared. Source/CI evidence remains separate.')}
function stageSeal(){state=core.transition(state,{type:'STAGE_RECKONING',intent_id:'admin.crown.final_source_of_truth_seal',payload:{scope:'source_of_truth'}});save();render();logLine('Final source-of-truth seal staged as RECKONING. UI did not authorize or execute it.')}

const bubble=document.createElement('button');bubble.id='luhmPetBubble';bubble.type='button';bubble.setAttribute('aria-label','Restore LuHm modular cockpit');bubble.innerHTML='<i></i><b></b><span>LUHM</span>';
const deck=document.createElement('section');deck.id='luhmWidgetDeck';deck.hidden=true;deck.innerHTML=`<div class="ff-head"><strong>LUM // WIDGET DECK</strong><small id="ffDeckMeta"></small><button id="ffDeckFull" type="button">FULL</button><button id="ffDeckMin" type="button">●</button></div><div class="ff-deck-grid" id="ffDeckWidgets"></div><div class="ff-deck-foot">STATE PASS ON · one session · typed widgets · no arbitrary shell</div>`;
const panel=document.createElement('section');panel.id='luhmPetPanel';panel.hidden=true;panel.innerHTML=`
  <div class="ff-head"><strong>LUM // MODULAR COCKPIT</strong><small id="ffMeta"></small><button id="ffToDeck" type="button">DECK</button><button id="ffMin" type="button">●</button></div>
  <div class="ff-realms"><button class="ff-realm" data-realm="GAME" type="button">GAME</button><button class="ff-realm" data-realm="ADMIN" type="button">ADMIN</button><button class="ff-realm" data-realm="SYSTEM" type="button">SYSTEM</button></div>
  <div class="ff-tabs">${Object.values(WIDGETS).map(w=>`<button class="ff-widget-tab" data-widget="${w.widget_id}" data-realm="${w.surface}" type="button">${w.widget_id}</button>`).join('')}</div>
  <div class="ff-body">
    <div class="ff-pending" id="ffPending"></div>
    <div class="ff-widget-pane" data-widget="PET"><div class="ff-line" id="ffDialogue"></div><div class="ff-actions"><button class="ff-action hot" data-intent="game.bond" type="button">PET / BOND</button><button class="ff-action" data-intent="game.roll" type="button">ROLL D20</button><button class="ff-action" data-intent="game.save" type="button">SAVEPOINT</button></div></div>
    <div class="ff-widget-pane" data-widget="QUEST" hidden><div class="ff-line">Folklore Crossing quest surface. Gameplay remains inside GAME.</div><div class="ff-actions"><button class="ff-action" data-intent="game.explore" type="button">EXPLORE</button><button class="ff-action" data-intent="game.contact" type="button">CONTACT</button><button class="ff-action" data-intent="game.date" type="button">DATE</button></div><div class="ff-muted">WHISPER is inspect/play presentation. CROSSING is reversible Mirror Route. RECKONING is never granted by game state.</div></div>
    <div class="ff-widget-pane" data-widget="PARLEY" hidden><div class="ff-parley-phase" id="ffParleyPhase"></div><div class="ff-line" id="ffParleyVoice"></div><div class="ff-truth-strip" id="ffTruthStrip"></div><pre class="ff-envelope" id="ffMachineEnvelope"></pre><div class="ff-actions ff-parley-actions"><button class="ff-action ff-parley-action" data-parley="PROBE" type="button">PROBE</button><button class="ff-action ff-parley-action" data-parley="CHALLENGE" type="button">CHALLENGE</button><button class="ff-action ff-parley-action" data-parley="CORROBORATE" type="button">CORROBORATE</button><button class="ff-action ff-parley-action" data-parley="RECKON" type="button">RECKON</button></div></div>
    <div class="ff-widget-pane" data-widget="STATUS" hidden><pre class="ff-envelope" id="ffStatusJson"></pre><div class="ff-muted">SYSTEM is neutral status. It cannot grant ADMIN authority.</div></div>
    <div class="ff-widget-pane" data-widget="MEDIA" hidden><div class="ff-line">Local media slot. No remote fetch is performed by the cockpit.</div><div class="ff-muted">Private/quarantined third-party assets stay external and local-only unless separately rights-cleared.</div></div>
    <div class="ff-widget-pane" data-widget="UPDATE" hidden><div class="ff-update"><h3>PRIVATE UPDATE LANE</h3><p>Opening the vault is a user gesture. Android still enforces package, signer, versionCode, and installer confirmation.</p><button class="ff-update-link" id="ffStageUpdate" type="button">STAGE UPDATE RECKONING</button><a class="ff-update-link" href="${updateVault}">OPEN OWNER VAULT</a><div class="ff-muted">No silent install. No background update check.</div></div></div>
    <div class="ff-widget-pane" data-widget="CROWN" hidden><div class="ff-crown"><h3>♛ CROWN GATE</h3><div class="ff-crown-sub">SOURCE → AGENT → FORGE → UPDATE → HARDWARE</div><div class="ff-chain"><div class="ff-node proven"><i></i><b>SOURCE</b><span>CANONICAL CONTRACT</span></div><div class="ff-node proven"><i></i><b>AGENT</b><span>NO SELF-APPROVAL</span></div><div class="ff-node proven"><i></i><b>FORGE</b><span>SIGNED + 16K + ARM64</span></div><div class="ff-node proven"><i></i><b>UPDATE</b><span>SAME SIGNER</span></div><div class="ff-node pending"><i></i><b>HARDWARE</b><span>HUMAN OBSERVATION</span></div></div><div class="ff-proof-grid"><button class="ff-proof" data-proof="install" type="button">INSTALLED<small></small></button><button class="ff-proof" data-proof="saveReload" type="button">SAVE / RELOAD<small></small></button><button class="ff-proof" data-proof="secureFolder" type="button">SECURE FOLDER<small></small></button><button class="ff-proof" data-proof="reboot" type="button">REBOOT / RETURN<small></small></button></div><div class="ff-crown-state pending" id="ffCrownState"></div><button class="ff-seal" id="ffStageSeal" type="button">STAGE FINAL SOURCE-OF-TRUTH SEAL</button><button class="ff-action" id="ffClearProof" type="button" style="width:100%;margin-top:6px">CLEAR LOCAL PROOF</button><div class="ff-muted">This panel can remember observations. It cannot perform, approve, or attest a RECKONING action.</div></div></div>
    <div class="ff-widget-pane" data-widget="LOG" hidden><div class="ff-log" id="ffLog"></div><div class="ff-muted">Human-auditable local presentation log only.</div></div>
  </div>`;
document.body.append(bubble,deck,panel);
renderDeck();
if(!state.active_widget)state=core.transition(state,{type:'OPEN_WIDGET',widget_id:'PET',full:false});
if(state.mode==='FULL_COCKPIT'&&state.active_widget===null)state.active_widget='PET';
state.layout_profile=core.detectLayout();save();render();

$$('.ff-widget-tab').forEach(b=>b.addEventListener('click',()=>openWidget(b.dataset.widget,true)));
$$('[data-intent]').forEach(b=>b.addEventListener('click',()=>emitIntent(b.dataset.intent)));
$$('[data-parley]').forEach(b=>b.addEventListener('click',()=>parley(b.dataset.parley)));
$$('.ff-proof').forEach(b=>b.addEventListener('click',()=>toggleProof(b.dataset.proof)));
$$('.ff-realm').forEach(b=>b.addEventListener('click',()=>{const first=Object.values(WIDGETS).find(w=>w.surface===b.dataset.realm);if(first)openWidget(first.widget_id,true)}));
$('#ffClearProof').addEventListener('click',clearProof);
$('#ffStageSeal').addEventListener('click',stageSeal);
$('#ffStageUpdate').addEventListener('click',()=>{state.realm='ADMIN';emitIntent('admin.stage_update',{channel:'private_owner_vault'})});
$('#ffMin').addEventListener('click',()=>setState(core.transition(state,{type:'MINIMIZE'}),'Cockpit minimized. Session preserved.'));
$('#ffToDeck').addEventListener('click',()=>setState(core.transition(state,{type:'OPEN_DECK'}),'Full cockpit collapsed to widget deck.'));
$('#ffDeckMin').addEventListener('click',()=>setState(core.transition(state,{type:'MINIMIZE'}),'Widget deck minimized. Session preserved.'));
$('#ffDeckFull').addEventListener('click',()=>setState(core.transition(state,{type:'OPEN_FULL'}),'Widget deck expanded to full cockpit.'));
bubble.addEventListener('click',()=>{if(bubble.dataset.dragged==='1'){bubble.dataset.dragged='0';return}setState(core.transition(state,{type:'RESTORE'}),'Sprite bubble restored previous surface.')});

let drag=null;
bubble.addEventListener('pointerdown',e=>{drag={sx:e.clientX,sy:e.clientY,left:bubble.offsetLeft,top:bubble.offsetTop};bubble.setPointerCapture(e.pointerId);bubble.dataset.dragged='0'});
bubble.addEventListener('pointermove',e=>{if(!drag)return;const dx=e.clientX-drag.sx,dy=e.clientY-drag.sy;if(Math.abs(dx)+Math.abs(dy)>8)bubble.dataset.dragged='1';const x=Math.max(4,Math.min(innerWidth-bubble.offsetWidth-4,drag.left+dx));const y=Math.max(4,Math.min(innerHeight-bubble.offsetHeight-4,drag.top+dy));bubble.style.left=x+'px';bubble.style.top=y+'px';bubble.style.right='auto';state.x=x;state.y=y});
bubble.addEventListener('pointerup',e=>{drag=null;try{bubble.releasePointerCapture(e.pointerId)}catch{}save()});
if(state.x!==null&&state.y!==null){bubble.style.left=Math.max(4,Math.min(innerWidth-66,state.x))+'px';bubble.style.top=Math.max(4,Math.min(innerHeight-66,state.y))+'px';bubble.style.right='auto'}
window.addEventListener('resize',()=>{state.layout_profile=core.detectLayout();if(state.x!==null){state.x=Math.max(4,Math.min(innerWidth-66,state.x));state.y=Math.max(4,Math.min(innerHeight-66,state.y));bubble.style.left=state.x+'px';bubble.style.top=state.y+'px'}save();renderHeader()});
})();
