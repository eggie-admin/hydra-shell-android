(() => {
  const api = globalThis.browser ?? globalThis.chrome;
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
      "#prompt-textarea",
      "div.ProseMirror[contenteditable='true']",
      "div[contenteditable='true'][role='textbox']",
      "textarea"
    ];
    for (const selector of selectors) {
      const candidates = [...document.querySelectorAll(selector)].reverse();
      const found = candidates.find(el => {
        const r = el.getBoundingClientRect();
        return r.width > 0 && r.height > 0 && !el.disabled;
      });
      if (found) return found;
    }
    return null;
  }

  function placeText(el, text) {
    el.focus();
    if (el instanceof HTMLTextAreaElement || el instanceof HTMLInputElement) {
      const proto = el instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
      const setter = Object.getOwnPropertyDescriptor(proto, "value")?.set;
      setter ? setter.call(el, text) : (el.value = text);
      el.dispatchEvent(new Event("input", {bubbles: true}));
      return true;
    }
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(el);
    selection.removeAllRanges();
    selection.addRange(range);
    let ok = false;
    try { ok = document.execCommand("insertText", false, text); } catch (_) {}
    if (!ok) {
      el.textContent = text;
      el.dispatchEvent(new InputEvent("input", {bubbles:true,inputType:"insertText",data:text}));
    }
    return true;
  }

  function insertCommand(command) {
    if (!COMMANDS.has(command)) return {ok:false, error:"command_not_sealed"};
    const composer = findComposer();
    if (!composer) return {ok:false, error:"composer_not_found"};
    placeText(composer, command);
    return {ok:true};
  }

  api.runtime.onMessage.addListener((msg) => {
    if (msg?.type !== "LUHM_INSERT_COMMAND") return;
    return Promise.resolve(insertCommand(msg.command));
  });

  function mountPanel() {
    if (document.getElementById("luhm-pet-launcher")) return;
    const launcher = document.createElement("button");
    launcher.id = "luhm-pet-launcher";
    launcher.type = "button";
    launcher.title = "LuHm Companion";
    launcher.textContent = "👹";

    const panel = document.createElement("section");
    panel.id = "luhm-pet-panel";
    panel.hidden = true;
    panel.innerHTML = `
      <div class="luhm-head">
        <div><strong>LuHm Companion</strong><br><small>ChatGPT-only play controls</small></div>
        <button id="luhm-close" type="button" aria-label="Close">×</button>
      </div>
      <div class="luhm-grid">
        <button type="button" data-luhm="PET LUM">PET LUM</button>
        <button type="button" data-luhm="ROLL D20">ROLL D20</button>
        <button type="button" data-luhm="GACHA PULL">GACHA PULL</button>
        <button type="button" data-luhm="DATE EVENT">DATE EVENT</button>
        <button type="button" data-luhm="SUMMON IMAGE">SUMMON IMAGE</button>
        <button type="button" data-luhm="SAVEPOINT">SAVEPOINT</button>
        <button type="button" data-luhm="CAST ULTIMA">CAST ULTIMA ⚡</button>
      </div>
      <div id="luhm-pet-status">Lum is lurking.</div>`;

    document.documentElement.append(launcher, panel);
    launcher.addEventListener("click", () => { panel.hidden = !panel.hidden; });
    panel.querySelector("#luhm-close").addEventListener("click", () => { panel.hidden = true; });
    panel.querySelectorAll("[data-luhm]").forEach(btn => {
      btn.addEventListener("click", () => {
        const result = insertCommand(btn.dataset.luhm);
        const status = panel.querySelector("#luhm-pet-status");
        status.textContent = result.ok ? `${btn.dataset.luhm} loaded. You choose Send.` : "Tap the ChatGPT composer once, then retry.";
        if (result.ok) panel.hidden = true;
      });
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mountPanel, {once:true});
  else mountPanel();

  new MutationObserver(() => {
    if (!document.getElementById("luhm-pet-launcher")) mountPanel();
  }).observe(document.documentElement, {childList:true, subtree:true});
})();
