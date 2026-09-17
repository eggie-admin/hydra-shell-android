/* LUHM_OS_ENTERPRISE_DISTRIBUTION_V1
 * Branded install/update/uninstall + local-first frontend/backend harness.
 * Published GitHub Releases are the only remote update authority.
 * Optional LAN origins belong in protected local operator config, never public source.
 */
(()=>{'use strict';
const REPO='eggie-admin/hydra-shell-android';
const RELEASES_PAGE=`https://github.com/${REPO}/releases`;
const RELEASES_API=`https://api.github.com/repos/${REPO}/releases`;
const RELEASE_ASSET_PATH_PREFIX='/eggie-admin/hydra-shell-android/releases/download/';
const ASSET_PREFIX=`https://github.com${RELEASE_ASSET_PATH_PREFIX}`;
const MANIFEST_ASSET='luhmos-release.json';
const CANDIDATE_PACKAGE='art.eggiebagelface.luhmos.candidate';
const PROD_PACKAGE='art.eggiebagelface.luhmos';
const UPDATE_EVENT='app.update.install';
const UNINSTALL_EVENT='app.uninstall.open';
const LOCAL_BACKENDS=Object.freeze([
  'http://127.0.0.1',
  'http://localhost'
]);
const CHANNELS=Object.freeze(['testing','proposed','preview','beta','stable']);

function tagMatchesChannel(tag,channel){
  const t=String(tag||'');
  if(channel==='stable')return /^v\d+\.\d+\.\d+$/.test(t);
  return new RegExp(`^v\\d+\\.\\d+\\.\\d+-${channel}\\.\\d+$`).test(t);
}
function trustedReleaseAssetUrl(value){
  let u; try{u=new URL(String(value||''))}catch{return false}
  return u.protocol==='https:' && u.hostname==='github.com' && u.pathname.startsWith(RELEASE_ASSET_PATH_PREFIX);
}
function validSha256(value){return /^[0-9a-f]{64}$/.test(String(value||'').toLowerCase())}
function validPackage(value){return value===CANDIDATE_PACKAGE || value===PROD_PACKAGE}
function pickManifestAsset(release){return release?.assets?.find(a=>a?.name===MANIFEST_ASSET && trustedReleaseAssetUrl(a.browser_download_url))||null}
function pickApkAsset(release,name){return release?.assets?.find(a=>a?.name===name && /^luhmos-[a-z0-9.-]+\.apk$/.test(a.name) && trustedReleaseAssetUrl(a.browser_download_url))||null}
async function githubJson(url,fetchImpl=fetch){
  const res=await fetchImpl(url,{headers:{Accept:'application/vnd.github+json'},cache:'no-store',credentials:'omit'});
  if(!res.ok)throw new Error(`GitHub release lookup failed: HTTP ${res.status}`);
  return res.json();
}
async function resolveRelease(channel='stable',fetchImpl=fetch){
  if(!CHANNELS.includes(channel))throw new Error('Unknown LuHm release channel.');
  if(channel==='stable'){
    const release=await githubJson(`${RELEASES_API}/latest`,fetchImpl);
    if(release.draft || release.prerelease || !tagMatchesChannel(release.tag_name,'stable'))throw new Error('Latest GitHub release is not an eligible LuHm stable release.');
    return release;
  }
  const releases=await githubJson(`${RELEASES_API}?per_page=30`,fetchImpl);
  const release=releases.find(r=>!r.draft && r.prerelease && tagMatchesChannel(r.tag_name,channel));
  if(!release)throw new Error(`No published LuHm ${channel} release is available.`);
  return release;
}
async function resolveInstallPlan(channel='stable',fetchImpl=fetch){
  const release=await resolveRelease(channel,fetchImpl);
  const manifestAsset=pickManifestAsset(release);
  if(!manifestAsset)throw new Error('Release is missing luhmos-release.json.');
  const manifest=await githubJson(manifestAsset.browser_download_url,fetchImpl);
  if(manifest?.schema!=='luhm_os.release.v1')throw new Error('Release manifest schema rejected.');
  if(manifest.tag!==release.tag_name)throw new Error('Release manifest tag does not match GitHub release.');
  if(!validPackage(manifest.package_id))throw new Error('Release manifest package rejected.');
  if(!validSha256(manifest.apk_sha256))throw new Error('Release manifest APK digest rejected.');
  const apk=pickApkAsset(release,manifest.apk_asset);
  if(!apk)throw new Error('Manifest APK asset is absent from the GitHub release.');
  return Object.freeze({
    tag:release.tag_name,
    channel,
    packageId:manifest.package_id,
    versionName:String(manifest.version_name||''),
    versionCode:Number(manifest.version_code),
    apkUrl:apk.browser_download_url,
    apkSha256:String(manifest.apk_sha256).toLowerCase(),
    releaseUrl:release.html_url
  });
}
function bridgeAvailable(win=globalThis){return !!(win?.CathedralBridge && typeof win.CathedralBridge.postMessage==='function')}
function postUpdate(win,plan){
  if(!bridgeAvailable(win))return {ok:false,error:'LuHm native bridge unavailable.'};
  if(!trustedReleaseAssetUrl(plan?.apkUrl)||!validSha256(plan?.apkSha256)||!validPackage(plan?.packageId))return {ok:false,error:'Release plan rejected before native handoff.'};
  const message={type:UPDATE_EVENT,payload:{url:plan.apkUrl,sha256:plan.apkSha256,package_id:plan.packageId,tag:plan.tag}};
  win.CathedralBridge.postMessage(JSON.stringify(message));
  return {ok:true,message};
}
function postUninstall(win=globalThis){
  if(!bridgeAvailable(win))return {ok:false,error:'LuHm native bridge unavailable.'};
  const message={type:UNINSTALL_EVENT,payload:{reason:'user_requested_branded_uninstall'}};
  win.CathedralBridge.postMessage(JSON.stringify(message));
  return {ok:true,message};
}
async function probeLocalHarness(fetchImpl=fetch){
  const checks=[];
  for(const origin of LOCAL_BACKENDS){
    const controller=new AbortController();
    const timer=setTimeout(()=>controller.abort(),1200);
    try{
      const res=await fetchImpl(`${origin}/health`,{method:'GET',cache:'no-store',credentials:'omit',signal:controller.signal});
      checks.push({origin,ok:res.ok,status:res.status});
      if(res.ok)return {ok:true,origin,checks};
    }catch(error){checks.push({origin,ok:false,error:error?.name||'unreachable'})}
    finally{clearTimeout(timer)}
  }
  return {ok:false,origin:null,checks};
}
function retireLegacyInstallDock(){document.getElementById('luhmApkInstallDock')?.remove()}
function mount(){
  retireLegacyInstallDock();
  if(document.getElementById('luhmEnterpriseDock'))return;
  const dock=document.createElement('section');
  dock.id='luhmEnterpriseDock'; dock.className='luhm-apk-dock';
  dock.innerHTML=`<button id="luhmEnterpriseToggle" class="luhm-apk-toggle" type="button">LUHM CONTROL</button>
  <div id="luhmEnterprisePanel" class="luhm-apk-panel" hidden>
    <div class="luhm-apk-head"><strong>LuHm OS Control Center</strong><button id="luhmEnterpriseClose" type="button" aria-label="Close">×</button></div>
    <p class="luhm-apk-copy">Local-first runtime · GitHub Release updates · Android-confirmed install and removal.</p>
    <label class="luhm-apk-label" for="luhmReleaseChannel">RELEASE CHANNEL</label>
    <select id="luhmReleaseChannel" class="luhm-apk-input">${CHANNELS.map(c=>`<option value="${c}" ${c==='stable'?'selected':''}>${c.toUpperCase()}</option>`).join('')}</select>
    <div class="luhm-apk-actions"><button id="luhmCheckRelease" class="luhm-apk-primary" type="button">CHECK GITHUB RELEASE</button><button id="luhmProbeLocal" type="button">LOCAL HARNESS</button></div>
    <div class="luhm-apk-actions"><button id="luhmApplyRelease" class="luhm-apk-primary" type="button" disabled>VERIFY + UPDATE</button><button id="luhmOpenReleases" type="button">RELEASE PAGE</button></div>
    <div class="luhm-apk-actions"><button id="luhmUninstall" type="button">REMOVE LUHM OS…</button></div>
    <output id="luhmEnterpriseStatus" class="luhm-apk-status" aria-live="polite">Control Center ready. No background update check is running.</output>
  </div>`;
  document.body.appendChild(dock);
  const panel=document.getElementById('luhmEnterprisePanel'); const status=document.getElementById('luhmEnterpriseStatus'); const apply=document.getElementById('luhmApplyRelease');
  let plan=null;
  document.getElementById('luhmEnterpriseToggle').onclick=()=>{panel.hidden=!panel.hidden};
  document.getElementById('luhmEnterpriseClose').onclick=()=>{panel.hidden=true};
  document.getElementById('luhmOpenReleases').onclick=()=>globalThis.open(RELEASES_PAGE,'_blank','noopener,noreferrer');
  document.getElementById('luhmCheckRelease').onclick=async()=>{try{status.textContent='Checking published GitHub Releases…';plan=await resolveInstallPlan(document.getElementById('luhmReleaseChannel').value);apply.disabled=false;status.textContent=`${plan.tag} ready · ${plan.packageId} · SHA ${plan.apkSha256.slice(0,12)}…`;}catch(e){plan=null;apply.disabled=true;status.textContent=e.message}};
  apply.onclick=()=>{const r=postUpdate(window,plan);status.textContent=r.ok?'Release handed to native verifier. Android confirmation remains required.':r.error};
  document.getElementById('luhmProbeLocal').onclick=async()=>{status.textContent='Probing local loopback harness…';const r=await probeLocalHarness();status.textContent=r.ok?`LOCAL GREEN · ${r.origin}`:'LOCAL OFFLINE · packaged frontend remains available.'};
  document.getElementById('luhmUninstall').onclick=()=>{const r=postUninstall(window);status.textContent=r.ok?'Opening Android removal confirmation…':r.error};
}
const core=Object.freeze({REPO,RELEASES_PAGE,RELEASES_API,RELEASE_ASSET_PATH_PREFIX,ASSET_PREFIX,MANIFEST_ASSET,CANDIDATE_PACKAGE,PROD_PACKAGE,LOCAL_BACKENDS,CHANNELS,tagMatchesChannel,trustedReleaseAssetUrl,validSha256,validPackage,pickManifestAsset,pickApkAsset,resolveRelease,resolveInstallPlan,bridgeAvailable,postUpdate,postUninstall,probeLocalHarness,retireLegacyInstallDock});
globalThis.LuHmEnterpriseDistribution=core;
if(globalThis.__LUHM_TEST__)return;
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount,{once:true});else mount();
})();
