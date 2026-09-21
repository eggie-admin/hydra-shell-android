/* LUHM_SYSTEM_SHELL_V2
   Loading/login gate + Android shell + local system harness.
   Pairing is loopback-only, ephemeral, and memory-only. No direct shell execution. */
(()=>{'use strict';
const MODES=Object.freeze({FULL:0,TASKBAR:1,SPRITE:2});
const HARNESSES=Object.freeze(['http://127.0.0.1:8791','http://localhost:8791']);
const PAIR_SCHEMA='luhm_os.local_harness_pair.v1';
function normalizeLevel(v){v=Number(v);return v===1?1:v===2?2:0}
function nextLevel(v){const n=normalizeLevel(v);return n===0?1:n===1?2:0}
function bridge(win=globalThis,type,payload={}){if(!win?.CathedralBridge||typeof win.CathedralBridge.postMessage!=='function')return {ok:false};const message={type,payload};win.CathedralBridge.postMessage(JSON.stringify(message));return {ok:true,message}}
async function probe(fetchImpl=fetch){const checks=[];for(const origin of HARNESSES){const ctl=new AbortController(),timer=setTimeout(()=>ctl.abort(),900);try{const r=await fetchImpl(origin+'/health',{cache:'no-store',credentials:'omit',signal:ctl.signal});checks.push({origin,ok:r.ok,status:r.status});if(r.ok)return {ok:true,origin,checks}}catch(e){checks.push({origin,ok:false,error:e?.name||'offline'})}finally{clearTimeout(timer)}}return {ok:false,origin:null,checks}}
async function pair(code,fetchImpl=fetch){if(!/^\d{6}$/.test(String(code||'')))return {ok:false,error:'Pair code must be six digits.'};for(const origin of HARNESSES){try{const r=await fetchImpl(origin+'/auth/pair',{method:'POST',cache:'no-store',credentials:'omit',headers:{'Content-Type':'application/json','X-LuHm-Request':'pair'},body:JSON.stringify({code:String(code)})});if(!r.ok)continue;const d=await r.json();if(d?.schema!==PAIR_SCHEMA||typeof d.token!=='string'||!d.token||!Number.isFinite(Number(d.expires_at)))continue;return {ok:true,origin,token:d.token,expiresAt:Number(d.expires_at)}}catch{}}return {ok:false,error:'Local operator pairing failed.'}}
async function authJson(origin,token,path,method='GET',fetchImpl=fetch){if(!origin||!token)throw new Error('Operator session unavailable.');const r=await fetchImpl(origin+path,{method,cache:'no-store',credentials:'omit',headers:{Authorization:'Bearer '+token,'X-LuHm-Request':'operator'}});if(!r.ok)throw new Error('Operator session rejected.');return r.json()}
const core=Object.freeze({MODES,HARNESSES,PAIR_SCHEMA,normalizeLevel,nextLevel,bridge,probe,pair,authJson});
globalThis.LuHmSystemShell=core;
if(globalThis.__LUHM_TEST__)return;

const KEY='luhmos_system_shell_v2';
const saved=(()=>{try{return JSON.parse(localStorage.getItem(KEY)||'{}')}catch{return {}}})();
let level=normalizeLevel(saved.level),chrome=saved.chrome==='borderless'?'borderless':'system';
let session={origin:null,token:null,expiresAt:0};
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify({level,chrome}))}catch{}};
const q=(s,r=document)=>r.querySelector(s);
const paired=()=>!!session.token&&Date.now()/1000<session.expiresAt;
function apply(){document.body.dataset.shellLevel=String(level);document.body.dataset.shellChrome=chrome;document.body.dataset.operator=paired()?'paired':'guest';save();q('#shellMin')?.classList.toggle('active',level>0)}
function showPanel(title,html){const p=q('#luhmShellPanel');q('#luhmShellTitle').textContent=title;q('#luhmShellBody').innerHTML=html;p.hidden=false}
function closePanel(){const p=q('#luhmShellPanel');if(p)p.hidden=true}
function showGame(){level=0;apply();closePanel();q('#crownCathedral')?.scrollIntoView({block:'start',behavior:'smooth'})}
function requireOperator(){if(paired())return true;showLogin('Operator login required for SYSTEM and ADMIN.');return false}
function showAdmin(){if(!requireOperator())return;level=0;apply();closePanel();q('#luhmPetBubble')?.click();setTimeout(()=>q('#ffDeckFull')?.click(),20)}
async function showSystem(){
 if(!requireOperator())return;
 try{const t=await authJson(session.origin,session.token,'/auth/ticket','POST');showPanel('SYSTEM // LOCAL HARNESS',`<iframe id="luhmHarnessFrame" title="LuHm local system harness" src="${session.origin}/cockpit?ticket=${encodeURIComponent(t.ticket)}"></iframe><div class="luhm-shell-status">LOCAL HARNESS GREEN · ${session.origin}\nSession: ephemeral memory-only\nTermux role: external loopback host only\nDirect shell: forbidden</div>`)}
 catch(e){session={origin:null,token:null,expiresAt:0};apply();showLogin(e.message)}
}
function showSettings(){showPanel('SETTINGS // ANDROID SHELL',`<div class="luhm-shell-grid"><button data-setting="fullscreen">FULL SCREEN</button><button data-setting="systembars">SYSTEM BARS</button><button data-setting="borderless">BORDERLESS UI</button><button data-setting="min1">MINIMIZE I</button><button data-setting="min2">MINIMIZE II</button><button data-setting="logout">LOG OUT</button><button data-setting="quit">QUIT</button></div><div class="luhm-shell-status">Fullscreen = Android immersive shell. Borderless = in-app chrome only. Min I = icon taskbar. Min II = Lum bubble. Operator login only unlocks SYSTEM and ADMIN. Quit requires this explicit tap.</div>`)}
function gateHtml(msg,online){return `<div class="luhm-login-card"><small>LUHM OS // CROWN CATHEDRAL</small><h2>OPERATOR GATE</h2><p>${msg}</p><div class="luhm-login-state">${online?'LOCAL HARNESS ONLINE':'LOCAL HARNESS OFFLINE'}</div><input id="luhmPairCode" inputmode="numeric" autocomplete="one-time-code" maxlength="6" pattern="[0-9]{6}" placeholder="6-DIGIT PAIR CODE" ${online?'':'disabled'}><div class="luhm-login-actions"><button id="luhmPairSubmit" ${online?'':'disabled'}>UNLOCK OPERATOR</button><button id="luhmGuestEnter">GAME ONLY</button><button id="luhmPairRetry">RETRY HARNESS</button></div><output id="luhmLoginStatus">Session tokens remain in memory only.</output></div>`}
async function showLogin(msg='Loading local system harness…'){
 let gate=q('#luhmBootGate');if(!gate){gate=document.createElement('section');gate.id='luhmBootGate';document.body.append(gate)}
 gate.hidden=false;gate.innerHTML=gateHtml(msg,false);
 const result=await probe();gate.innerHTML=gateHtml(result.ok?'Enter the ephemeral code printed by the Termux harness.':'Harness unavailable. Game-only mode remains usable.',result.ok);
 q('#luhmGuestEnter').onclick=()=>{gate.hidden=true;session={origin:null,token:null,expiresAt:0};apply();showGame()};
 q('#luhmPairRetry').onclick=()=>showLogin('Rechecking loopback harness…');
 if(result.ok)q('#luhmPairSubmit').onclick=async()=>{const status=q('#luhmLoginStatus');status.textContent='PAIRING…';const r=await pair(q('#luhmPairCode').value);if(!r.ok){status.textContent=r.error;return}session={origin:r.origin,token:r.token,expiresAt:r.expiresAt};apply();status.textContent='OPERATOR GREEN';setTimeout(()=>{gate.hidden=true;showGame()},180)};
}
async function logout(){if(paired())try{await authJson(session.origin,session.token,'/auth/logout','POST')}catch{}session={origin:null,token:null,expiresAt:0};apply();closePanel();showLogin('Operator session closed.')}
function mount(){
 const bar=document.createElement('nav');bar.id='luhmSystemTaskbar';bar.setAttribute('aria-label','LuHm system taskbar');bar.innerHTML='<button data-shell="game" aria-label="Game">🎮</button><button data-shell="system" aria-label="System">⚙</button><button data-shell="admin" aria-label="Admin">♜</button><button data-shell="lum" aria-label="Lum">✦</button><button id="shellMin" data-shell="min" aria-label="Minimize">▁</button><button data-shell="settings" aria-label="Settings">☰</button>';
 const panel=document.createElement('section');panel.id='luhmShellPanel';panel.hidden=true;panel.innerHTML='<div class="luhm-shell-head"><strong id="luhmShellTitle">LUHM</strong><button id="luhmShellClose" type="button">×</button></div><div id="luhmShellBody" class="luhm-shell-pane"></div>';
 document.body.append(bar,panel);apply();
 bar.addEventListener('click',e=>{const b=e.target.closest('[data-shell]');if(!b)return;({game:showGame,system:showSystem,admin:showAdmin,lum:()=>{level=0;apply();q('[data-crown-action="lum"]')?.click()},min:()=>{level=nextLevel(level);apply();if(level===2)q('#luhmPetBubble')?.click()},settings:showSettings}[b.dataset.shell]||(()=>{}))()});
 q('#luhmShellClose').onclick=closePanel;
 panel.addEventListener('click',e=>{const b=e.target.closest('[data-setting]');if(!b)return;const a=b.dataset.setting;if(a==='fullscreen'){chrome='borderless';apply();bridge(window,'app.window.immersive')}if(a==='systembars'){chrome='system';apply();bridge(window,'app.window.system_bars')}if(a==='borderless'){chrome=chrome==='borderless'?'system':'borderless';apply()}if(a==='min1'){level=1;apply();closePanel()}if(a==='min2'){level=2;apply();closePanel();q('#luhmPetBubble')?.click()}if(a==='logout')logout();if(a==='quit')bridge(window,'app.quit')});
 showLogin('Booting Crown Cathedral and probing local harness…');
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount,{once:true});else mount();
})();
