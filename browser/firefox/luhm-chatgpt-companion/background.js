const ASSET_BASE = "http://127.0.0.1:8799";
const TERMINAL_URL = "http://127.0.0.1:7681/";
const SAFE_ASSET = /^[a-zA-Z0-9_./()\[\] -]+$/;
const MAX_INLINE_BYTES = 4 * 1024 * 1024;

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

browser.runtime.onMessage.addListener((msg) => {
  if (!msg || typeof msg !== "object") return;

  if (msg.type === "LUHM_PRIVATE_STATUS") {
    return privateStatus().catch((error) => ({ok:false, error:String(error.message || error)}));
  }

  if (msg.type === "LUHM_PRIVATE_ASSET") {
    return privateAsset(msg.path).catch((error) => ({ok:false, error:String(error.message || error)}));
  }

  if (msg.type === "LUHM_OPEN_TERMINAL") {
    return browser.tabs.create({url: TERMINAL_URL}).then(() => ({ok:true}));
  }

  if (msg.type === "LUHM_OPEN_PRIVATE_CACHE") {
    return browser.tabs.create({url: `${ASSET_BASE}/`}).then(() => ({ok:true}));
  }
});
