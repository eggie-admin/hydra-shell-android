const ASSET_BASE = "http://127.0.0.1:8799";
const TERMINAL_URL = "http://127.0.0.1:7681/";
const SAFE_ASSET = /^[a-zA-Z0-9_./()\[\] -]+$/;
const MAX_INLINE_BYTES = 4 * 1024 * 1024;
const ADULT_CATALOG = `${ASSET_BASE}/private-gacha/adult-rewards.json`;

async function privateStatus() {
  const response = await fetch(`${ASSET_BASE}/luhm-manifest.json`, {cache: "no-store"});
  if (!response.ok) throw new Error(`asset_manifest_${response.status}`);
  const manifest = await response.json();
  return {
    ok: true,
    title: manifest.title || "LuHm Private Asset Cache",
    generated_at: manifest.generated_at || null,
    files: Array.isArray(manifest.files) ? manifest.files.length : 0,
    packs: Array.isArray(manifest.packs) ? manifest.packs : []
  };
}

async function privateAsset(relativePath) {
  if (typeof relativePath !== "string" || !SAFE_ASSET.test(relativePath) || relativePath.includes("..")) {
    return {ok:false, error:"invalid_asset_path"};
  }
  const response = await fetch(`${ASSET_BASE}/${relativePath}`, {cache:"no-store"});
  if (!response.ok) return {ok:false, error:`asset_${response.status}`};
  const blob = await response.blob();
  if (blob.size > MAX_INLINE_BYTES) return {ok:false, error:"asset_too_large"};
  if (!/^image\//.test(blob.type)) return {ok:false, error:"asset_type_not_previewable"};
  const bytes = new Uint8Array(await blob.arrayBuffer());
  let binary = "";
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
  }
  return {ok:true, data_url:`data:${blob.type};base64,${btoa(binary)}`};
}

async function readAdultCatalog() {
  const response = await fetch(ADULT_CATALOG, {cache:"no-store"});
  if (!response.ok) throw new Error(`adult_catalog_${response.status}`);
  const catalog = await response.json();
  if (!catalog?.private_only || !catalog?.adult_only || !Array.isArray(catalog.rewards)) {
    throw new Error("adult_catalog_invalid");
  }
  return catalog;
}

function secureRoll(max) {
  const values = new Uint32Array(1);
  crypto.getRandomValues(values);
  return values[0] % max;
}

function chooseByTier(rewards, tier) {
  const pool = rewards.filter((reward) => reward.tier === tier && reward.enabled !== false);
  if (!pool.length) return null;
  return pool[secureRoll(pool.length)];
}

async function pullAdultReward() {
  const catalog = await readAdultCatalog();
  const key = "luhm_after_dark_state";
  const stored = await browser.storage.local.get(key);
  const state = stored[key] || {pity:0, pulls:0, unlocked:[]};
  state.pity += 1;
  state.pulls += 1;

  let tier;
  const roll = secureRoll(10000) / 100;
  if (state.pity >= (catalog.hard_pity || 20)) tier = "Legendary";
  else if (roll < 5) tier = "Legendary";
  else if (roll < 25) tier = "Epic";
  else tier = "Rare";

  let reward = chooseByTier(catalog.rewards, tier);
  if (!reward) reward = catalog.rewards[secureRoll(catalog.rewards.length)];
  if (tier === "Legendary") state.pity = 0;
  if (!state.unlocked.includes(reward.id)) state.unlocked.push(reward.id);
  await browser.storage.local.set({[key]: state});

  return {
    ok:true,
    banner:catalog.banner || "AFTER DARK",
    tier,
    reward:{id:reward.id,label:reward.label,local_pack:reward.local_pack || null},
    pity:state.pity,
    hard_pity:catalog.hard_pity || 20,
    duplicate:state.unlocked.filter((id) => id === reward.id).length > 1
  };
}

browser.runtime.onMessage.addListener((msg) => {
  if (!msg || typeof msg !== "object") return;

  if (msg.type === "LUHM_PRIVATE_STATUS") {
    return privateStatus().catch((error) => ({ok:false, error:String(error.message || error)}));
  }
  if (msg.type === "LUHM_PRIVATE_ASSET") {
    return privateAsset(msg.path).catch((error) => ({ok:false, error:String(error.message || error)}));
  }
  if (msg.type === "LUHM_PRIVATE_GACHA_PULL") {
    return pullAdultReward().catch((error) => ({ok:false, error:String(error.message || error)}));
  }
  if (msg.type === "LUHM_OPEN_TERMINAL") {
    return browser.tabs.create({url: TERMINAL_URL}).then(() => ({ok:true}));
  }
  if (msg.type === "LUHM_OPEN_PRIVATE_CACHE") {
    return browser.tabs.create({url: `${ASSET_BASE}/`}).then(() => ({ok:true}));
  }
});
