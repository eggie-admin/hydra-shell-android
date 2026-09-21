(()=>{
const q=s=>document.querySelector(s),qa=s=>[...document.querySelectorAll(s)];
const pretty=v=>{try{return JSON.stringify(JSON.parse(v),null,2)}catch{return String(v)}};
const cargo=[
'CURRENT_LUM_MIDNIGHT_1996_MODEL_SHEET.png',
'CURRENT_KAI9000_GAME_WORLD_BIBLE.png',
'CURRENT_KAI9000_CATHEDRAL_POSTER.png',
'CURRENT_LUM_ANIMATED_REEL.mp4',
'KAI9000_LUM_AVATAR_ACTUAL_ANIMATED.gif',
'KAI9000_LUM_AVATAR_ACTUAL_ANIMATED.manifest.json',
'brand/icon.svg','brand/logo-dark.svg','brand/logo-light.svg'];
function show(name){qa('.tab').forEach(x=>x.classList.toggle('active',x.dataset.tab===name));qa('.view').forEach(x=>x.classList.toggle('active',x.id===name));}
qa('.tab').forEach(x=>x.addEventListener('click',()=>show(x.dataset.tab)));qa('[data-jump]').forEach(x=>x.addEventListener('click',()=>show(x.dataset.jump)));
q('#cargo').replaceChildren(...cargo.map(x=>{const d=document.createElement('div');d.textContent='✓ '+x;return d;}));
function bridge(){q('#platform').textContent=pretty(window.LUHM?.platform?.()||'{"bridge":"unavailable"}');q('#engineStatus').textContent=pretty(window.LUHM?.engineStatus?.()||'{"engine":"unavailable"}');}
window.LUHMEngineReady=bridge;
q('#selfTest').addEventListener('click',()=>q('#selfResult').textContent=pretty(window.LUHM?.runTyped?.('self_test')||'{"ok":false,"error":"BRIDGE_UNAVAILABLE"}'));
q('#assetTest').addEventListener('click',()=>q('#assetResult').textContent=pretty(window.LUHM?.runTyped?.('asset_inventory')||'{"ok":false,"error":"BRIDGE_UNAVAILABLE"}'));
q('#localAudit').addEventListener('click',()=>{const spec=JSON.parse(q('#cathedral-assets').textContent);const checks=[['device',spec.device==='SM-X400'],['api',spec.targetApi===37],['drive cargo',spec.expectedDriveAssets===6],['brand cargo',spec.expectedBrandAssets===3],['native bridge',!!window.LUHM]];const ok=checks.every(x=>x[1]);q('#auditResult').textContent=checks.map(x=>(x[1]?'PASS ':'FAIL ')+x[0]).join('\n')+'\n\n'+(ok?'CATHEDRAL LOCAL AUDIT: PASS':'CATHEDRAL LOCAL AUDIT: FAIL');});
bridge();
})();
