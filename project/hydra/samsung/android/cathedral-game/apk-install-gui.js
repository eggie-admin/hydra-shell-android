/* LUHMOS_APK_INSTALL_GUI_V1
 * LUHM_AVATAR_SOURCE_OF_TRUTH_V1
 * Explicit-user Android APK install/update bridge for the packaged LuHm OS WebView.
 * The authoritative LuHm avatar is packaged locally as lum-avatar-actual-animated.mp4.
 * No background checks. No silent install. No shell. No self-approval.
 */
(()=>{'use strict';
const APP_HOST='appassets.androidplatform.net';
const EVENT='app.update.install';
const LUM_AVATAR_LOCAL='lum-avatar-actual-animated.mp4';
const LUM_AVATAR_SOURCE_SEAL='KAI9000_LUM_AVATAR_ACTUAL_ANIMATED_GREEN_20260906';
const TERMINAL=new Set(['app.update.success','app.update.error','app.update.permission.required']);
function normalizeUrl(value){
  const raw=String(value||'').trim();
  if(!raw)return {ok:false,error:'Paste an HTTPS APK URL.'};
  let url;
  try{url=new URL(raw)}catch{return {ok:false,error:'APK URL is not valid.'}}
  if(url.protocol!=='https:')return {ok:false,error:'APK URL must use HTTPS.'};
  if(!url.hostname)return {ok:false,error:'APK URL needs a host.'};
  return {ok:true,url:url.toString()};
}
function makeInstallMessage(value){
  const checked=normalizeUrl(value);
  if(!checked.ok)return checked;
  return {ok:true,message:{type:EVENT,payload:{url:checked.url}}};
}
function nativeAvailable(win=globalThis){
  return !!(win?.location?.hostname===APP_HOST && win?.CathedralBridge && typeof win.CathedralBridge.postMessage==='function');
}
function postInstall(win,value){
  const built=makeInstallMessage(value);
  if(!built.ok)return built;
  if(!nativeAvailable(win))return {ok:false,error:'Native installer bridge is available only inside the packaged LuHm OS APK.'};
  win.CathedralBridge.postMessage(JSON.stringify(built.message));
  return {ok:true,message:built.message};
}
function parseNativeEvent(data){
  if(typeof data!=='string')return null;
  try{
    const msg=JSON.parse(data);
    if(!msg || typeof msg.type!=='string' || !msg.type.startsWith('app.update.'))return null;
    return {type:msg.type,message:String(msg.payload?.message||msg.type),terminal:TERMINAL.has(msg.type)};
  }catch{return null}
}
const core=Object.freeze({APP_HOST,EVENT,LUM_AVATAR_LOCAL,LUM_AVATAR_SOURCE_SEAL,normalizeUrl,makeInstallMessage,nativeAvailable,postInstall,parseNativeEvent});
globalThis.LuHmApkInstallGuiCore=core;
if(globalThis.__LUHM_TEST__)return;

function mountLumAvatar(){
  const host=document.querySelector('.avatar');
  const fallback=document.getElementById('oni');
  if(!host || host.querySelector('.luhm-avatar-video'))return;
  const video=document.createElement('video');
  video.className='luhm-avatar-video';
  video.src=LUM_AVATAR_LOCAL;
  video.muted=true;
  video.loop=true;
  video.autoplay=true;
  video.playsInline=true;
  video.preload='auto';
  video.disablePictureInPicture=true;
  video.setAttribute('aria-label','LuHm animated avatar');
  video.setAttribute('data-source-seal',LUM_AVATAR_SOURCE_SEAL);
  const reduced=globalThis.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches===true;
  video.addEventListener('canplay',()=>{
    fallback?.classList.add('luhm-avatar-fallback-hidden');
    host.classList.add('luhm-avatar-ready');
    if(reduced){video.loop=false;video.currentTime=Math.min(.125,video.duration||.125);video.pause();return}
    video.play().catch(()=>{});
  },{once:true});
  video.addEventListener('error',()=>{
    host.classList.remove('luhm-avatar-ready');
    fallback?.classList.remove('luhm-avatar-fallback-hidden');
    video.remove();
  },{once:true});
  host.append(video);
}

function mount(){
  if(document.getElementById('luhmApkInstallDock'))return;
  const dock=document.createElement('section');
  dock.id='luhmApkInstallDock';
  dock.className='luhm-apk-dock';
  dock.dataset.open='0';
  dock.innerHTML=`
    <button id="luhmApkToggle" class="luhm-apk-toggle" type="button" aria-controls="luhmApkPanel" aria-expanded="false">APK / INSTALL</button>
    <div id="luhmApkPanel" class="luhm-apk-panel" hidden>
      <div class="luhm-apk-head"><strong>LuHm OS Install Lane</strong><button id="luhmApkClose" type="button" aria-label="Close install lane">×</button></div>
      <p class="luhm-apk-copy">Explicit-user install/update only. Android verifies package identity, signer continuity and version direction before showing its installer confirmation.</p>
      <label class="luhm-apk-label" for="luhmApkUrl">HTTPS APK candidate URL</label>
      <input id="luhmApkUrl" class="luhm-apk-input" type="url" inputmode="url" autocomplete="off" placeholder="https://…/candidate.apk">
      <div class="luhm-apk-actions">
        <button id="luhmApkInstall" class="luhm-apk-primary" type="button">VERIFY + OPEN ANDROID INSTALLER</button>
        <button id="luhmApkClear" type="button">CLEAR</button>
      </div>
      <div class="luhm-apk-contract"><span>PACKAGE</span><b>art.eggiebagelface.luhmos</b><span>SIGNER</span><b>SAME AS INSTALLED</b><span>DOWNGRADE</span><b>REJECT</b><span>USER ACTION</span><b>REQUIRED</b></div>
      <output id="luhmApkStatus" class="luhm-apk-status" aria-live="polite">${nativeAvailable(window)?'Native installer bridge ready.':'Preview mode. Open inside packaged LuHm OS to install.'}</output>
    </div>`;
  document.body.appendChild(dock);
  const toggle=document.getElementById('luhmApkToggle');
  const panel=document.getElementById('luhmApkPanel');
  const close=document.getElementById('luhmApkClose');
  const install=document.getElementById('luhmApkInstall');
  const clear=document.getElementById('luhmApkClear');
  const input=document.getElementById('luhmApkUrl');
  const status=document.getElementById('luhmApkStatus');
  function setOpen(open){dock.dataset.open=open?'1':'0';panel.hidden=!open;toggle.setAttribute('aria-expanded',open?'true':'false')}
  function setBusy(busy){install.disabled=!!busy;input.disabled=!!busy;install.textContent=busy?'ANDROID VERIFIER WORKING…':'VERIFY + OPEN ANDROID INSTALLER'}
  toggle.addEventListener('click',()=>setOpen(panel.hidden));
  close.addEventListener('click',()=>setOpen(false));
  clear.addEventListener('click',()=>{input.value='';status.textContent='Candidate URL cleared.';setBusy(false)});
  install.addEventListener('click',()=>{
    const result=postInstall(window,input.value);
    if(!result.ok){status.textContent=result.error;setBusy(false);return}
    status.textContent='Candidate handed to native verifier. No install occurs until Android confirms it.';
    setBusy(true);
  });
  window.addEventListener('message',(event)=>{
    const msg=parseNativeEvent(event.data);
    if(!msg)return;
    status.textContent=msg.message;
    setBusy(!msg.terminal && msg.type!=='app.update.confirmation');
  });
}
function boot(){mountLumAvatar();mount()}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
