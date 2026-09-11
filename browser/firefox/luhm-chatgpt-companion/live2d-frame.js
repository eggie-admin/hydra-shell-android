(() => {
  const ASSET_BASE = "http://127.0.0.1:8799";
  const INDEX_URL = `${ASSET_BASE}/live2d-runtime-index.json`;
  const badge = document.getElementById("runtime-badge");
  const label = document.getElementById("model-label");
  const stage = document.getElementById("stage");
  let models = [];
  let current = 0;
  let engine = null;
  let voiceTimer = null;
  let voiceActive = false;

  function report(ok, detail = {}) {
    try {
      parent.postMessage({type:"LUHM_LIVE2D_FRAME_STATUS", ok, ...detail}, "*");
    } catch (_) {}
  }

  function runtimeReady() {
    return Boolean(globalThis.L2D?.init) && !globalThis.L2D?.__luhm_stub;
  }

  function freshCanvas() {
    const old = document.getElementById("live2d-canvas");
    const canvas = document.createElement("canvas");
    canvas.id = "live2d-canvas";
    canvas.width = 300;
    canvas.height = 420;
    canvas.setAttribute("aria-label", "LuHm Live2D model");
    old.replaceWith(canvas);
    return canvas;
  }

  function modelUrl(model) {
    const encoded = String(model.entry_path || "").split("/").map(encodeURIComponent).join("/");
    return `${ASSET_BASE}/${encoded}`;
  }

  async function readIndex() {
    const response = await fetch(INDEX_URL, {cache:"no-store"});
    if (!response.ok) throw new Error(`live2d_index_${response.status}`);
    const index = await response.json();
    if (index?.schema !== "luhm.private-live2d-runtime.v1" || !Array.isArray(index.models)) {
      throw new Error("live2d_index_invalid");
    }
    models = index.models.filter(m => m?.runtime_family === "cubism2" && typeof m.entry_path === "string");
    current = Math.min(Math.max(Number(index.default_index || 0), 0), Math.max(models.length - 1, 0));
    return index;
  }

  function stopVoice() {
    voiceActive = false;
    if (voiceTimer) clearTimeout(voiceTimer);
    voiceTimer = null;
    try { engine?.setParams?.({PARAM_MOUTH_OPEN_Y:0}); } catch (_) {}
  }

  function voiceTick() {
    if (!voiceActive || !engine) return;
    try {
      engine.setParams?.({PARAM_MOUTH_OPEN_Y: 0.18 + Math.random() * 0.82});
    } catch (_) {}
    voiceTimer = setTimeout(voiceTick, 85 + Math.random() * 75);
  }

  function startVoice() {
    if (!engine) return;
    stopVoice();
    voiceActive = true;
    voiceTick();
  }

  function motionGroups() {
    try { return engine?.getMotions?.() || {}; }
    catch (_) { return {}; }
  }

  function chooseGroup(eventName) {
    const groups = Object.keys(motionGroups());
    if (!groups.length) return null;
    const preferences = {
      pet:["tap","touch","happy","idle"],
      ui:["idle","tap"],
      gacha:["special","attack","skill","idle"],
      date:["happy","tap","touch","idle"],
      summon:["special","skill","attack","idle"],
      ultima:["special","skill","attack","damage","idle"],
      save:["idle"]
    }[eventName] || ["idle"];
    for (const pref of preferences) {
      const hit = groups.find(g => g.toLowerCase().includes(pref));
      if (hit) return hit;
    }
    return groups[Math.floor(Math.random() * groups.length)];
  }

  function fallbackWiggle(eventName) {
    if (!engine?.setParams) return;
    const strong = ["gacha","summon","ultima"].includes(eventName);
    const amount = strong ? 20 : 9;
    try {
      engine.setParams({PARAM_ANGLE_X: amount, PARAM_BODY_ANGLE_X: amount * .35});
      setTimeout(() => {
        try { engine?.setParams?.({PARAM_ANGLE_X:-amount, PARAM_BODY_ANGLE_X:-amount * .35}); } catch (_) {}
      }, 130);
      setTimeout(() => {
        try { engine?.setParams?.({PARAM_ANGLE_X:0, PARAM_BODY_ANGLE_X:0}); } catch (_) {}
      }, 330);
    } catch (_) {}
  }

  function react(eventName = "ui") {
    if (!engine) return;
    const group = chooseGroup(eventName);
    if (group) {
      try {
        engine.playMotion(group, undefined, eventName === "ultima" ? 4 : 2);
        return;
      } catch (_) {}
    }
    fallbackWiggle(eventName);
  }

  async function loadModel(index) {
    if (!models.length) throw new Error("no_live2d_models");
    current = (Number(index) + models.length) % models.length;
    stopVoice();
    try { engine?.destroy?.(); } catch (_) {}
    const canvas = freshCanvas();
    const model = models[current];
    label.textContent = model.label || model.id || `model ${current + 1}`;
    badge.textContent = `LIVE2D · loading ${current + 1}/${models.length}`;
    const init = globalThis.L2D?.init;
    if (typeof init !== "function" || globalThis.L2D?.__luhm_stub) {
      document.body.className = "runtime-missing";
      badge.textContent = "LIVE2D · private runtime not forged";
      report(false, {error:"runtime_missing", models:models.length});
      return;
    }
    engine = init(canvas);
    if (!engine) throw new Error("runtime_init_failed");
    engine.on?.("loaded", () => report(true, {model:model.label || model.id, index:current, models:models.length}));
    engine.on?.("tap", () => react("pet"));
    await engine.load({path:modelUrl(model), scale:0.78, position:[0,-0.12], volume:0, logLevel:"error"});
    document.body.className = "";
    badge.textContent = `LIVE2D · GREEN · ${current + 1}/${models.length}`;
  }

  async function boot() {
    try {
      if (!runtimeReady()) {
        document.body.className = "runtime-missing";
        badge.textContent = "LIVE2D · install private runtime";
      }
      await readIndex();
      if (!models.length) throw new Error("no_live2d_models");
      await loadModel(current);
    } catch (error) {
      document.body.className = "runtime-error";
      badge.textContent = `LIVE2D · ${String(error.message || error)}`;
      report(false, {error:String(error.message || error)});
    }
  }

  document.getElementById("prev").addEventListener("click", () => { void loadModel(current - 1); });
  document.getElementById("next").addEventListener("click", () => { void loadModel(current + 1); });
  document.getElementById("react").addEventListener("click", () => react("pet"));
  stage.addEventListener("dblclick", () => react("gacha"));

  window.addEventListener("message", (event) => {
    if (event.source !== parent || !event.data || typeof event.data !== "object") return;
    const msg = event.data;
    if (msg.type === "LUHM_LIVE2D_REACT") react(String(msg.event || "ui"));
    if (msg.type === "LUHM_LIVE2D_NEXT") void loadModel(current + 1);
    if (msg.type === "LUHM_LIVE2D_PREV") void loadModel(current - 1);
    if (msg.type === "LUHM_LIVE2D_RELOAD") void boot();
    if (msg.type === "LUHM_LIVE2D_VOICE") msg.active ? startVoice() : stopVoice();
  });

  void boot();
})();
