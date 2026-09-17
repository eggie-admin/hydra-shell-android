const DEFAULT_BRIDGE_ORIGIN = "http://127.0.0.1";
const DEFAULT_TERMINAL_URL = "http://127.0.0.1:8767/";
const ALLOWED_ASSET_PREFIXES = ["/data/", "/images/"];

function normalizeAssetPath(input) {
  if (typeof input !== "string") {
    return null;
  }
  if (!input.startsWith("/")) {
    return null;
  }
  if (!ALLOWED_ASSET_PREFIXES.some((prefix) => input.startsWith(prefix))) {
    return null;
  }
  if (input.includes("..")) {
    return null;
  }
  return input;
}

async function fetchLocalAsset(assetPath) {
  const safePath = normalizeAssetPath(assetPath);
  if (!safePath) {
    return { ok: false, error: "asset-path-not-allowed" };
  }

  const settings = await browser.storage.local.get(["bridgeOrigin"]);
  const bridgeOrigin = settings.bridgeOrigin || DEFAULT_BRIDGE_ORIGIN;
  if (!/^http:\/\/127\.0\.0\.1(?::\d+)?$/u.test(bridgeOrigin)) {
    return { ok: false, error: "bridge-origin-not-allowed" };
  }

  const response = await fetch(`${bridgeOrigin}${safePath}`, { method: "GET" });
  if (!response.ok) {
    return { ok: false, error: `bridge-fetch-failed-${response.status}` };
  }

  const contentType = response.headers.get("content-type") || "application/octet-stream";
  const bytes = await response.arrayBuffer();
  const encoded = btoa(String.fromCharCode(...new Uint8Array(bytes)));
  return { ok: true, contentType, payloadBase64: encoded };
}

async function openTerminal() {
  const settings = await browser.storage.local.get(["terminalUrl"]);
  const terminalUrl = settings.terminalUrl || DEFAULT_TERMINAL_URL;
  if (!/^http:\/\/127\.0\.0\.1(?::\d+)?\/.*$/u.test(terminalUrl)) {
    return { ok: false, error: "terminal-url-not-allowed" };
  }
  await browser.tabs.create({ url: terminalUrl, active: true });
  return { ok: true };
}

browser.runtime.onMessage.addListener((message) => {
  if (!message || typeof message !== "object") {
    return Promise.resolve({ ok: false, error: "invalid-message" });
  }

  switch (message.type) {
    case "bridge:fetch-local-asset":
      return fetchLocalAsset(message.assetPath);
    case "launcher:open-terminal":
      return openTerminal();
    default:
      return Promise.resolve({ ok: false, error: "unsupported-action" });
  }
});
