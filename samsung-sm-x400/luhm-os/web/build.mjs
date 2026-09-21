import {readFile,readdir,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {join,relative} from 'node:path';
const root=new URL('../app/src/main/assets/',import.meta.url);
const manifest=JSON.parse(await readFile(new URL('../app/src/main/assets/cathedral-assets.json',import.meta.url),'utf8'));
const hash=b=>createHash('sha256').update(b).digest('hex');
for(const item of manifest.drive_assets){const u=new URL('../app/src/main/assets/cathedral/'+item.name,import.meta.url);const b=await readFile(u);if(b.length!==item.bytes)throw new Error('CANONICAL_SIZE_RED '+item.name);if(hash(b)!==item.sha256)throw new Error('CANONICAL_HASH_RED '+item.name);}
for(const item of manifest.repo_assets){const u=new URL('../app/src/main/assets/brand/'+item.name,import.meta.url);const b=await readFile(u);if(hash(b)!==item.sha256)throw new Error('BRAND_HASH_RED '+item.name);}
async function walk(dir,base=dir){let out=[];for(const e of await readdir(dir,{withFileTypes:true})){const p=join(dir,e.name);if(e.isDirectory())out.push(...await walk(p,base));else out.push(relative(base,p).replaceAll('\\','/'));}return out;}
const files=(await walk(root.pathname)).sort();const receipt={schema:'luhm-os.web-build-receipt.v2',canonical_asset_manifest:manifest.id,files:{}};for(const f of files){receipt.files[f]=hash(await readFile(new URL('../app/src/main/assets/'+f,import.meta.url)));}
await writeFile(new URL('../web-build-receipt.json',import.meta.url),JSON.stringify(receipt,null,2)+'\n');
console.log('LUHM_WEB_BUILD_GREEN');console.log('CATHEDRAL_CANONICAL_ASSETS_GREEN');console.log('CATHEDRAL_DRIVE_ASSETS='+manifest.drive_assets.length);console.log('CATHEDRAL_BRAND_ASSETS='+manifest.repo_assets.length);
