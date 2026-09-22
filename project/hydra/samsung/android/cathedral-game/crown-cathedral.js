/* LUHM_CROWN_CATHEDRAL_DEMO_V1
   Local-only game presentation. No shell, network, mutation, signing, or release authority.
   LUHM_PUBLIC_BETA_IDENTITY_OVERLAY_V1 keeps historical save/runtime identifiers compatible while presenting canonical LuHm OS identity.
   LUHM_NATIVE_3D_WORLD_BRIDGE_V1 routes WORLD MODE into the packaged Godot runtime. */
(()=>{'use strict';
const identity={
 '.brand small':'LUHM OS CATHEDRAL V1 · local-first Samsung build',
 '.crown-copy small':'LUHM OS // SOURCE-OF-TRUTH DEMO',
 '.foot':'PUBLIC BETA CANDIDATE · ORIGINAL LUHM OS SYSTEMS · NO COPIED FRANCHISE ASSETS OR DIALOGUE'
};
for(const [selector,text] of Object.entries(identity)){const el=document.querySelector(selector);if(el)el.textContent=text}
const root=document.getElementById('crownCathedral'); if(!root)return;
const line=document.getElementById('crownLine');
const state=document.getElementById('crownState');
const video=document.getElementById('crownLumVideo');
const assets=document.getElementById('crownAssets');
const assetList=[
 ['CATHEDRAL','index.html'],['FINAL FORM','final-form.js'],['COCKPIT','modular-cockpit.css'],
 ['INSTALL UI','apk-install-gui.js'],['ENTERPRISE','enterprise-distribution.js'],['UPDATE','update-channel.json'],
 ['WORLD SPRITE','godot-world/assets/lum_world_sprite.svg'],['HUD SIGIL','godot-world/assets/lum_hud_icon.svg'],
 ['GODOT WORLD','godot-world/WORLD_FIRST_MANIFEST.json'],['SECONDARY MOTION','godot4-cleared/secondary-motion-profile.json'],
 ['LUM AVATAR','lum-avatar-actual-animated.mp4']
];
for(const [name,path] of assetList){const s=document.createElement('span');s.textContent=name;s.dataset.ok='1';s.title=path;assets.append(s)}
function say(a,b){state.textContent=a;line.textContent=b}
function click(sel){const el=document.querySelector(sel);if(el){el.click();return true}return false}
function bridge(type,payload={}){if(!globalThis.CathedralBridge||typeof globalThis.CathedralBridge.postMessage!=='function')return false;globalThis.CathedralBridge.postMessage(JSON.stringify({type,payload}));return true}
root.addEventListener('click',async e=>{
 const b=e.target.closest('[data-crown-action]'); if(!b)return;
 const a=b.dataset.crownAction;
 if(a==='enter'){root.dataset.mode='nave';click('[data-a="explore"]');say('NAVE OPEN // GAME','Cathedral exploration routed into the existing local game loop.')}
 if(a==='world'){
  root.dataset.mode='world';
  click('[data-a="explore"]');
  const native=bridge('ui.world.enter',{source:'crown-cathedral',tier:'godot-3d'});
  say(native?'NATIVE WORLD // GODOT 3D':'WORLD PREVIEW // WEB FALLBACK',native?'Switching to the packaged Godot 3D runtime. Native HUD returns to Cathedral.':'Native bridge unavailable in this source view; keeping the local web preview visible.');
 }
 if(a==='lum'){root.dataset.lum='video';try{await video.play()}catch{}say('LUM // SUMMONED','Packaged local avatar selected. SVG sprite remains the offline fallback.')}
 if(a==='crown'){root.dataset.mode='crown';const bubble=document.getElementById('luhmPetBubble');if(bubble)bubble.click();say('CROWN GATE // USER GESTURE','Cockpit opened by explicit gesture. Authority remains with Professor.')}
});
video.addEventListener('error',()=>{root.dataset.lum='sprite';say('LUM // SPRITE FALLBACK','Avatar video unavailable in this source view. Packaged demo uses the verified local MP4 when present.')});
})();
