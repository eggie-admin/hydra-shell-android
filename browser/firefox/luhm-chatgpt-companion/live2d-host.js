(() => {
  const api = globalThis.browser ?? globalThis.chrome;
  const EVENT_MAP = {
    "PET LUM": "pet",
    "ROLL D20": "ui",
    "GACHA PULL": "gacha",
    "DATE EVENT": "date",
    "SUMMON IMAGE": "summon",
    "CAST ULTIMA": "ultima",
    "SAVEPOINT": "save"
  };
  let lastVoiceActive = false;

  function frameWindow() {
    return document.querySelector("#luhm-live2d-shell iframe")?.contentWindow || null;
  }

  function send(type, extra = {}) {
    frameWindow()?.postMessage({type, ...extra}, "*");
  }

  function mountShell() {
    if (document.getElementById("luhm-live2d-shell")) return;
    const shell = document.createElement("aside");
    shell.id = "luhm-live2d-shell";
    shell.hidden = true;
    shell.setAttribute("aria-label", "LuHm Live2D companion");
    const iframe = document.createElement("iframe");
    iframe.src = api.runtime.getURL("live2d-frame.html");
    iframe.title = "LuHm Live2D companion";
    iframe.setAttribute("allow", "autoplay");
    shell.appendChild(iframe);
    document.documentElement.appendChild(shell);
  }

  function statusNode() {
    return document.getElementById("luhm-pet-status");
  }

  function ensureControls() {
    const tools = document.querySelector("#luhm-pet-panel .luhm-tools");
    if (!tools || document.getElementById("luhm-live2d-toggle")) return;

    const toggle = document.createElement("button");
    toggle.id = "luhm-live2d-toggle";
    toggle.type = "button";
    toggle.textContent = "LIVE2D";
    toggle.addEventListener("click", () => {
      const shell = document.getElementById("luhm-live2d-shell");
      if (!shell) return;
      shell.hidden = !shell.hidden;
      const status = statusNode();
      if (status) status.textContent = shell.hidden ? "Live2D companion hidden." : "Live2D companion awake.";
      if (!shell.hidden) send("LUHM_LIVE2D_RELOAD");
    });

    const next = document.createElement("button");
    next.type = "button";
    next.textContent = "MODEL ▶";
    next.addEventListener("click", () => {
      const shell = document.getElementById("luhm-live2d-shell");
      if (shell) shell.hidden = false;
      send("LUHM_LIVE2D_NEXT");
    });

    tools.append(toggle, next);
  }

  function voiceActive() {
    const overlay = document.getElementById("luhm-subtitle-overlay");
    return Boolean(overlay && !overlay.hidden);
  }

  function syncVoice() {
    const active = voiceActive();
    if (active === lastVoiceActive) return;
    lastVoiceActive = active;
    send("LUHM_LIVE2D_VOICE", {active});
  }

  document.addEventListener("click", (event) => {
    const button = event.target?.closest?.("[data-luhm]");
    if (!button) return;
    const reaction = EVENT_MAP[button.dataset.luhm];
    if (reaction) send("LUHM_LIVE2D_REACT", {event:reaction});
  }, true);

  window.addEventListener("message", (event) => {
    const frame = frameWindow();
    if (!frame || event.source !== frame || event.data?.type !== "LUHM_LIVE2D_FRAME_STATUS") return;
    const status = statusNode();
    if (!status) return;
    if (event.data.ok) {
      status.textContent = `Live2D GREEN · ${event.data.model || "private model"} · ${event.data.index + 1}/${event.data.models}`;
    } else if (event.data.error === "runtime_missing") {
      status.textContent = "Live2D shell ready; private renderer not forged into this XPI.";
    }
  });

  function reconcile() {
    mountShell();
    ensureControls();
    syncVoice();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", reconcile, {once:true});
  else reconcile();

  new MutationObserver(reconcile).observe(document.documentElement, {childList:true, subtree:true, attributes:true, attributeFilter:["hidden"]});
})();
