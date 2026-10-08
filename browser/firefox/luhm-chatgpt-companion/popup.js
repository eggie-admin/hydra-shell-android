const api = globalThis.browser ?? globalThis.chrome;
const status = document.getElementById("status");

async function activeChatTab() {
  const tabs = await api.tabs.query({active: true, currentWindow: true});
  const tab = tabs[0];
  if (!tab?.id) return null;
  if (!/^https:\/\/(chatgpt\.com|chat\.openai\.com)\//.test(tab.url || "")) return null;
  return tab;
}

async function insert(command) {
  status.textContent = "Finding Lum's console…";
  const tab = await activeChatTab();
  if (!tab) {
    status.textContent = "Open chatgpt.com in this tab first.";
    return;
  }
  try {
    const result = await api.tabs.sendMessage(tab.id, {
      type: "LUHM_INSERT_COMMAND",
      command
    });
    status.textContent = result?.ok
      ? `${command} loaded. You choose Send.`
      : "Chat composer not ready. Tap it once and retry.";
  } catch (_) {
    status.textContent = "Reload the ChatGPT tab once, then retry.";
  }
}

document.querySelectorAll("[data-cmd]").forEach(btn => {
  btn.addEventListener("click", () => insert(btn.dataset.cmd));
});
