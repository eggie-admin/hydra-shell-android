const status = document.getElementById("status");

async function getChatGPTTab() {
  const tabs = await chrome.tabs.query({ currentWindow: true });
  return tabs.find((t) =>
    /^https:\/\/(chatgpt\.com|chat\.openai\.com)\//.test(t.url || "")
  );
}

async function sendCommand(command) {
  status.textContent = "Looking for ChatGPT…";
  const tab = await getChatGPTTab();
  if (!tab?.id) {
    status.textContent = "Open ChatGPT first.";
    await chrome.tabs.create({ url: "https://chatgpt.com/" });
    return;
  }

  try {
    const response = await chrome.tabs.sendMessage(tab.id, {
      type: "LUHM_INSERT_COMMAND",
      command
    });
    if (response?.ok) {
      status.textContent = `${command} loaded. You choose Send.`;
    } else {
      status.textContent = "Composer not ready. Click inside ChatGPT and retry.";
    }
  } catch (_err) {
    status.textContent = "Reload the ChatGPT tab once, then retry.";
  }
}

document.querySelectorAll("[data-command]").forEach((button) => {
  button.addEventListener("click", () => sendCommand(button.dataset.command));
});

document.getElementById("openChatGPT").addEventListener("click", async () => {
  await chrome.tabs.create({ url: "https://chatgpt.com/" });
  status.textContent = "ChatGPT opened.";
});
