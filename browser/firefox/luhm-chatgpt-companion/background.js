const ASSET_BASE = "http://127.0.0.1:8799";
const SAFE_ASSET = /^[a-zA-Z0-9_./()\[\] -]+$/;
const MAX_INLINE_BYTES = 4 * 1024 * 1024;
const MAX_AUDIO_BYTES = 12 * 1024 * 1024;
const ADULT_CATALOG = `${ASSET_BASE}/private-gacha/adult-rewards.json`;
const AUDIO_INDEX = `${ASSET_BASE}/destiny-audio-index.json`;
const VOICE_CACHE_BASE = `${ASSET_BASE}/voice-cache`;

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
  for (let i = 0; i < bytes.length; i += chunk) binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
  return {ok:true, data_url:`data:${blob.type};base64,${btoa(binary)}`};
}

async function readAdultCatalog() {
  const response = await fetch(ADULT_CATALOG, {cache:"no-store"});
  if (!response.ok) throw new Error(`adult_catalog_${response.status}`);
  const catalog = await response.json();
  if (!catalog?.private_only || !catalog?.adult_only || !Array.isArray(catalog.rewards) || !catalog.rewards.length) {
    throw new Error("adult_catalog_invalid");
  }
  return catalog;
}

async function readAudioIndex() {
  const response = await fetch(AUDIO_INDEX, {cache:"no-store"});
  if (!response.ok) throw new Error(`audio_index_${response.status}`);
  const index = await response.json();
  if (index?.schema !== "luhm.private-destiny-audio.v1" || !Array.isArray(index.files)) {
    throw new Error("audio_index_invalid");
  }
  return index;
}

function secureRoll(max) {
  if (!Number.isInteger(max) || max <= 0) throw new Error("invalid_roll_range");
  const range = 0x100000000;
  const limit = Math.floor(range / max) * max;
  const values = new Uint32Array(1);
  do {
    crypto.getRandomValues(values);
  } while (values[0] >= limit);
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
  const state = stored[key] || {pity:0, pulls:0, unlock_counts:{}};
  if (!state.unlock_counts || typeof state.unlock_counts !== "object") state.unlock_counts = {};
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

  const previousCount = Number(state.unlock_counts[reward.id] || 0);
  state.unlock_counts[reward.id] = previousCount + 1;
  await browser.storage.local.set({[key]: state});

  return {
    ok:true,
    banner:catalog.banner || "AFTER DARK",
    tier,
    reward:{id:reward.id,label:reward.label,local_pack:reward.local_pack || null},
    pity:state.pity,
    hard_pity:catalog.hard_pity || 20,
    duplicate:previousCount > 0,
    copies:state.unlock_counts[reward.id],
    pulls:state.pulls
  };
}

function mimeForAudioPath(path, serverMime) {
  if (serverMime && serverMime.startsWith("audio/")) return serverMime;
  const ext = (path.split(".").pop() || "").toLowerCase();
  return ({wav:"audio/wav",mp3:"audio/mpeg",ogg:"audio/ogg",oga:"audio/ogg",opus:"audio/ogg",m4a:"audio/mp4",aac:"audio/aac",flac:"audio/flac",webm:"audio/webm"})[ext] || "application/octet-stream";
}

async function blobToDataUrl(blob, path) {
  if (blob.size > MAX_AUDIO_BYTES) throw new Error("audio_too_large");
  const bytes = new Uint8Array(await blob.arrayBuffer());
  let binary = "";
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
  return `data:${mimeForAudioPath(path, blob.type)};base64,${btoa(binary)}`;
}

async function audioStatus() {
  const index = await readAudioIndex();
  return {
    ok:true,
    recognized:index.recognized_count || 0,
    playable:index.playable_count || 0,
    game_containers:index.game_audio_container_count || 0,
    ffprobe:Boolean(index.ffprobe_available),
    vgmstream:Boolean(index.vgmstream_available)
  };
}

async function pickAudio(eventName) {
  const index = await readAudioIndex();
  const preferences = index.event_preferences?.[eventName] || [eventName];
  const playable = index.files.filter((item) => item.directly_playable && typeof item.path === "string");
  if (!playable.length) return {ok:false, error:"no_playable_audio"};

  let candidates = playable.filter((item) => (item.tags || []).some((tag) => preferences.includes(tag)));
  if (!candidates.length) candidates = playable;
  const chosen = candidates[secureRoll(candidates.length)];
  if (!SAFE_ASSET.test(chosen.path) || chosen.path.includes("..")) return {ok:false,error:"invalid_audio_path"};

  const response = await fetch(`${ASSET_BASE}/${chosen.path}`, {cache:"no-store"});
  if (!response.ok) return {ok:false,error:`audio_${response.status}`};
  const blob = await response.blob();
  return {ok:true,event:eventName,path:chosen.path,tags:chosen.tags || [],data_url:await blobToDataUrl(blob, chosen.path)};
}

async function sha256Hex(text) {
  const encoded = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", encoded);
  return [...new Uint8Array(digest)].map((value) => value.toString(16).padStart(2,"0")).join("");
}

async function cachedVoiceForJapanese(jaText) {
  if (typeof jaText !== "string" || !jaText.trim() || jaText.length > 1000) return {ok:false,error:"invalid_voice_text"};
  const key = await sha256Hex(jaText.trim());
  const metadataResponse = await fetch(`${VOICE_CACHE_BASE}/${key}.json`, {cache:"no-store"});
  if (!metadataResponse.ok) return {ok:false,error:"cache_miss",key};
  const metadata = await metadataResponse.json();
  if (metadata?.key !== key || typeof metadata?.audio_path !== "string") return {ok:false,error:"cache_metadata_invalid",key};
  if (metadata.expires_at && Date.now() / 1000 >= Number(metadata.expires_at)) return {ok:false,error:"cache_expired",key};
  if (!SAFE_ASSET.test(metadata.audio_path) || metadata.audio_path.includes("..")) return {ok:false,error:"cache_path_invalid",key};

  const audioResponse = await fetch(`${ASSET_BASE}/${metadata.audio_path}`, {cache:"no-store"});
  if (!audioResponse.ok) return {ok:false,error:`cache_audio_${audioResponse.status}`,key};
  const blob = await audioResponse.blob();
  return {
    ok:true,
    key,
    provider:metadata.provider || "local-cache",
    emotion:metadata.emotion || null,
    expires_at:metadata.expires_at || null,
    data_url:await blobToDataUrl(blob, metadata.audio_path)
  };
}

browser.runtime.onMessage.addListener((msg) => {
  if (!msg || typeof msg !== "object") return;
  if (msg.type === "LUHM_PRIVATE_STATUS") return privateStatus().catch((error) => ({ok:false,error:String(error.message || error)}));
  if (msg.type === "LUHM_PRIVATE_ASSET") return privateAsset(msg.path).catch((error) => ({ok:false,error:String(error.message || error)}));
  if (msg.type === "LUHM_PRIVATE_GACHA_PULL") return pullAdultReward().catch((error) => ({ok:false,error:String(error.message || error)}));
  if (msg.type === "LUHM_AUDIO_STATUS") return audioStatus().catch((error) => ({ok:false,error:String(error.message || error)}));
  if (msg.type === "LUHM_AUDIO_PICK") return pickAudio(msg.event).catch((error) => ({ok:false,error:String(error.message || error)}));
  if (msg.type === "LUHM_VOICE_CACHE_GET") return cachedVoiceForJapanese(msg.ja).catch((error) => ({ok:false,error:String(error.message || error)}));
  if (msg.type === "LUHM_OPEN_PRIVATE_CACHE") return browser.tabs.create({url: `${ASSET_BASE}/`}).then(() => ({ok:true}));
});
