const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
class Element{constructor(){this.style={};this.value='';this.children=[];this.textContent='';this.disabled=false;this.dataset={};this.files=[];}append(...x){this.children.push(...x);}setAttribute(){}click(){this.onclick?.();}}
const els={};for(const [,id]of html.matchAll(/id="([^"]+)"/g))els[id]=new Element();els.scale.value='150';els.state.value='idle';const toys=['wave','jump','review'].map(x=>{const e=new Element();e.dataset.toy=x;return e;});let now=0,frameCallback,exported;
const context={document:{hidden:false,getElementById:id=>els[id]||find(id),querySelectorAll:()=>toys,createElement:()=>new Element()},performance:{now:()=>now},requestAnimationFrame:fn=>frameCallback=fn,Date,console,URL:{createObjectURL:b=>{exported=b;return 'blob:test'},revokeObjectURL(){}},Blob,setTimeout:()=>0,Image:class{decode(){return Promise.reject(Error('Invalid image bytes'));}}};
function find(id){function visit(el){if(el.id===id)return el;for(const c of el.children||[]){const f=visit(c);if(f)return f;}}for(const e of Object.values(els)){const f=visit(e);if(f)return f;}}
vm.createContext(context);vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],context);const checks=[];function check(name,fn){fn();checks.push({name,result:'PASS'});}function at(t){now=t;frameCallback(now);}
(async()=>{
check('default_preview_scale_150_percent',()=>{assert.equal(els['scale-value'].textContent,'150%');assert.equal(els.sprite.style.width,'288px');assert.equal(els.sprite.style.height,'312px')});
check('three_helper_cap',()=>{['Context','Build','Research'].forEach(r=>find('start-'+r).click());assert.equal(els['mesh-status'].textContent,'3/3 helpers active');find('start-Critic').click();assert.equal(els['mesh-status'].textContent,'3/3 helpers active');assert.equal(find('status-Critic').textContent,'Idle');});
check('operation_budget_and_critic_slot',()=>{for(let i=0;i<8;i++)find('op-Context').click();assert.equal(find('status-Context').textContent,'Idle');find('start-Critic').click();assert.equal(els['mesh-status'].textContent,'3/3 helpers active');});
check('wall_time_budget',()=>{at(180001);assert.equal(els['mesh-status'].textContent,'0/3 helpers active');});
check('paused_toy_queue_cap',()=>{els.pause.click();for(let i=0;i<6;i++)toys[1].click();assert.equal(els['event-status'].textContent,'Idle · queue 4/4 · paused');assert(els.log.textContent.includes('request rejected'));});
check('stop_clears_queue',()=>{els.stop.click();assert.equal(els['event-status'].textContent,'Idle · queue 0/4 · paused');});
check('toy_returns_to_idle',()=>{els.pause.click();toys[0].click();assert.equal(els.state.value,'wave');at(181202);assert.equal(els.state.value,'idle');});
check('manual_selection',()=>{els.state.value='review';els.state.onchange();assert.equal(els.state.value,'review');});
check('scale_change',()=>{els.scale.value='100';els.scale.oninput();assert.equal(els.sprite.style.width,'192px');els.scale.value='150';els.scale.oninput();});
els.sheet.files=[{type:'image/png',size:42}];await els.sheet.onchange();check('invalid_image_rejected',()=>{assert.equal(els.error.textContent,'Invalid image bytes');});
els.export.click();const receipt=JSON.parse(await exported.text());check('receipt_scope',()=>{assert.equal(receipt.deployed,false);assert.equal(receipt.chatgpt_pet_modified,false);assert.equal(receipt.mesh_mode,'simulation');assert.equal(receipt.preview_scale,1.5);});
check('network_disabled_by_policy',()=>assert(html.includes("connect-src 'none'")));
const report={milestone:'LUHM_GUI_DEBUG_CANDIDATE',logic_status:'PASS',passed:checks.length,checks,method:'Node VM with minimal DOM test doubles; not a browser rendering test',browser_status:'BLOCKED: Chromium missing; download timed out',visual_layout:'UNVERIFIED',pet_artwork:'NOT_INCLUDED',deployment:'NOT_PERFORMED'};fs.writeFileSync(path.join(__dirname,'verification.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exit(1)});
