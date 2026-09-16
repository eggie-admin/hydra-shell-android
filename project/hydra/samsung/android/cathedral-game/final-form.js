/* KAI9000_FINAL_FORM_PET_V1
   KAI9000_UPDATE_LANE_V1
   In-app LuHm pet/cockpit. No eval, no shell, no background network fetch.
   The UPDATE tab only opens the owner's private Drive staging lane externally;
   Android still owns package-install confirmation and signer/version enforcement. */
(()=>{'use strict';
const $=(s,r=document)=>r.querySelector(s);
const storageKey='luhmos_final_form_pet_v1';
const updateVault='https://drive.google.com/drive/folders/17nODHVpnjQ1jtzJxvjxy0Ec1X-osLCkB';
const saved=(()=>{try{return JSON.parse(localStorage.getItem(storageKey)||'{}')}catch{return {}}})();
const state={x:Number.isFinite(saved.x)?saved.x:null,y:Number.isFinite(saved.y)?saved.y:null,closed:false,final:!!saved.final};

function pressGame(action){const b=document.querySelector(`[data-a="${action}"]`);if(b){b.click();return true}return false}
function latestDialogue(){return ($('#dialogue')?.textContent||'Cathedral is awake.').trim()}
function save(){try{localStorage.setItem(storageKey,JSON.stringify({x:state.x,y:state.y,final:state.final}))}catch{}}
function setTab(name){document.querySelectorAll('.ff-tab').forEach(b=>b.classList.toggle('active',b.dataset.tab===name));document.querySelectorAll('.ff-pane').forEach(p=>p.hidden=p.dataset.pane!==name);if(name==='pet') $('#ffDialogue').textContent=latestDialogue()}
function logLine(text){const log=$('#log');if(!log)return;const e=document.createElement('div');e.className='entry';e.innerHTML='<b>FINAL FORM</b> '+text;log.prepend(e)}
function castFinal(){state.final=true;save();document.body.classList.add('luhm-final-form');const d=$('#dialogue');if(d)d.textContent='THE IRON GIANT, THE GREAT AND TERRIBLE, stirs beneath the cathedral. Lum holds the crown.';const h=$('#hint');if(h)h.textContent='Final Form is theatrical state only. Base game remains deterministic and offline.';$('#ffBossState').textContent='IRON GIANT: AWAKE';logLine('Crown protocol invoked. No cloud automation. No shell. No privilege escalation.');if(navigator.vibrate) navigator.vibrate([45,35,80]);}

const bubble=document.createElement('button');bubble.id='luhmPetBubble';bubble.type='button';bubble.setAttribute('aria-label','Open LuHm pet');bubble.innerHTML='<i></i><b></b>';
const panel=document.createElement('section');panel.id='luhmPetPanel';panel.hidden=true;panel.innerHTML=`
  <div class="ff-head"><strong>LUM // PORTRAIT FORM</strong><button id="ffMin" type="button">—</button><button id="ffClose" type="button">×</button></div>
  <div class="ff-tabs"><button class="ff-tab active" data-tab="pet" type="button">PET</button><button class="ff-tab" data-tab="system" type="button">SYSTEM</button><button class="ff-tab" data-tab="update" type="button">UPDATE</button><button class="ff-tab" data-tab="boss" type="button">BOSS</button></div>
  <div class="ff-body">
    <div class="ff-pane" data-pane="pet"><div class="ff-line" id="ffDialogue"></div><div class="ff-actions"><button class="ff-action hot" data-pet-action="bond" type="button">PET / BOND</button><button class="ff-action" data-pet-action="roll" type="button">ROLL D20</button><button class="ff-action" data-pet-action="explore" type="button">EXPLORE</button><button class="ff-action" data-pet-action="save" type="button">SAVEPOINT</button></div></div>
    <div class="ff-pane" data-pane="system" hidden><div class="ff-kv"><span>PACKAGE</span><b>art.eggiebagelface.luhmos</b><span>BUILD</span><b>1.0.4 / 104</b><span>VIEW</span><b class="ff-good">PORTRAIT</b><span>BASE GAME</span><b class="ff-good">BUNDLED</b><span>LOCAL SAVE</span><b class="ff-good">ON-DEVICE</b><span>UPDATE RULE</span><b>SAME SIGNER + HIGHER CODE</b><span>TERMUX</span><b class="ff-amber">OPTIONAL</b><span>REBOOT PROOF</span><b class="ff-amber">PENDING</b></div><div class="ff-muted">This panel reports build doctrine, not live socket truth. The APK never fakes GREEN runtime status and never executes shell commands.</div></div>
    <div class="ff-pane" data-pane="update" hidden><div class="ff-update"><h3>PRIVATE UPDATE LANE</h3><p>Open the owner-only staging vault, download the next signed LuHm APK, then let Android verify the same package, signer and increasing versionCode. No silent install.</p><a class="ff-update-link" href="${updateVault}">OPEN UPDATE VAULT</a><div class="ff-muted">Current build: 1.0.4 / 104. Update handoff is explicit and user-confirmed.</div></div></div>
    <div class="ff-pane" data-pane="boss" hidden><div class="ff-boss"><h3 id="ffBossState">IRON GIANT: ${state.final?'AWAKE':'ASLEEP'}</h3><p>Black iron below. Red moon above. One crown. The final-form ritual only mutates the game presentation layer.</p><button class="ff-cast" id="ffCast" type="button">CAST FINAL FORM</button></div></div>
  </div>`;
document.body.append(bubble,panel);
$('#ffDialogue').textContent=latestDialogue();
if(state.final) document.body.classList.add('luhm-final-form');

document.querySelectorAll('.ff-tab').forEach(b=>b.addEventListener('click',()=>setTab(b.dataset.tab)));
document.querySelectorAll('[data-pet-action]').forEach(b=>b.addEventListener('click',()=>{pressGame(b.dataset.petAction);setTimeout(()=>$('#ffDialogue').textContent=latestDialogue(),30)}));
$('#ffCast').addEventListener('click',castFinal);
$('#ffMin').addEventListener('click',()=>{panel.hidden=true;bubble.hidden=false});
$('#ffClose').addEventListener('click',()=>{panel.hidden=true;bubble.hidden=true;state.closed=true});
bubble.addEventListener('click',()=>{if(bubble.dataset.dragged==='1'){bubble.dataset.dragged='0';return}panel.hidden=false;bubble.hidden=true;setTab('pet')});

let drag=null;
bubble.addEventListener('pointerdown',e=>{drag={sx:e.clientX,sy:e.clientY,left:bubble.offsetLeft,top:bubble.offsetTop};bubble.setPointerCapture(e.pointerId);bubble.dataset.dragged='0'});
bubble.addEventListener('pointermove',e=>{if(!drag)return;const dx=e.clientX-drag.sx,dy=e.clientY-drag.sy;if(Math.abs(dx)+Math.abs(dy)>8)bubble.dataset.dragged='1';const x=Math.max(4,Math.min(innerWidth-bubble.offsetWidth-4,drag.left+dx));const y=Math.max(4,Math.min(innerHeight-bubble.offsetHeight-4,drag.top+dy));bubble.style.left=x+'px';bubble.style.top=y+'px';bubble.style.right='auto';state.x=x;state.y=y});
bubble.addEventListener('pointerup',e=>{drag=null;try{bubble.releasePointerCapture(e.pointerId)}catch{}save()});
if(state.x!==null&&state.y!==null){bubble.style.left=Math.max(4,Math.min(innerWidth-66,state.x))+'px';bubble.style.top=Math.max(4,Math.min(innerHeight-66,state.y))+'px';bubble.style.right='auto'}
window.addEventListener('resize',()=>{if(state.x!==null){state.x=Math.max(4,Math.min(innerWidth-66,state.x));state.y=Math.max(4,Math.min(innerHeight-66,state.y));bubble.style.left=state.x+'px';bubble.style.top=state.y+'px';save()}});
})();
