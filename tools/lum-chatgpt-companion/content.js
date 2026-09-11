const COMMANDS = new Set([
  "PET LUM",
  "ROLL D20",
  "GACHA PULL",
  "DATE EVENT",
  "SUMMON IMAGE",
  "CAST ULTIMA",
  "SAVEPOINT"
]);

function findComposer() {
  const selectors = [
    "textarea",
    "div[contenteditable='true'][role='textbox']",
    "div[contenteditable='true']"
  ];
  for (const selector of selectors) {
    const nodes = [...document.querySelectorAll(selector)];
    const visible = nodes.reverse().find((el) => {
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0 && !el.disabled;
    });
    if (visible) return visible;
  }
  return null;
}

function setComposerText(el, text) {
  el.focus();
  if (el.tagName === "TEXTAREA") {
    const setter = Object.getOwnPropertyDescriptor(
      HTMLTextAreaElement.prototype,
      "value"
    )?.set;
    setter ? setter.call(el, text) : (el.value = text);
    el.dispatchEvent(new Event("input", { bubbles: true }));
    return;
  }

  el.textContent = text;
  el.dispatchEvent(new InputEvent("input", {
    bubbles: true,
    inputType: "insertText",
    data: text
  }));
}

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type !== "LUHM_INSERT_COMMAND") return;
  if (!COMMANDS.has(msg.command)) {
    sendResponse({ ok: false, error: "command_not_sealed" });
    return;
  }

  const composer = findComposer();
  if (!composer) {
    sendResponse({ ok: false, error: "composer_not_found" });
    return;
  }

  // Safety rule: insert only. Never auto-submit or click Send.
  setComposerText(composer, msg.command);
  sendResponse({ ok: true });
});
