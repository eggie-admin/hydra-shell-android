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
  const SOUND_EVENTS = {
    "PET LUM": "pet",
    "ROLL D20": "ui",
    "GACHA PULL": "gacha",
    "DATE EVENT": "date",
    "SUMMON IMAGE": "summon",
    "CAST ULTIMA": "ultima",
    "SAVEPOINT": "ui"
  };
  const VOICE_TUNE_PROMPT = "LUM VOICE MODE: Keep spoken replies natural and compact, usually 1-3 sentences. Use quick conversational cadence, warm playful sassy PG-13 goth-alt oni/JRPG quest-giver energy, and call me Professor occasionally rather than every sentence. Technical accuracy outranks roleplay. Use contractions and speech-friendly phrasing. Avoid markdown-heavy formatting unless I ask for structure. Do not imitate a specific actor or copyrighted character voice, and do not narrate SFX tags aloud; the private Firefox companion handles sound cues separately.";

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

  function insertText(text) {
    const composer = findComposer();
    if (!composer) return {ok:false, error:"composer_not_found"};
    placeText(composer, text);
    return {ok:true};
  }

  function insertCommand(command) {
    if (!COMMANDS.has(command)) return {ok:false, error:"command_not_sealed"};
    return insertText(command);
  }

  async function runtime(message) {
    try { return await api.runtime.sendMessage(message); }
    catch (error) { return {ok:false, error:String(error)}; }
  }

  async function playEventAudio(eventName) {
    const result = await runtime({type:"LUHM_AUDIO_PICK", event:eventName});
    if (!result?.ok || !result.data_url) return result;
    try {
      const audio = new Audio(result.data_url);
      audio.volume = 0.72;
      await audio.play();
      return {ok:true, path:result.path};
    } catch (error) {
      return {ok:false, error:`playback:${String(error)}`};
    }
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
    launcher.setAttribute("aria-label", "Open LuHm Companion");
    launcher.innerHTML = '<span class="luhm-mini-horn left"></span><span class="luhm-mini-face">L</span><span class="luhm-mini-horn right"></span>';

    const panel = document.createElement("section");
    panel.id = "luhm-pet-panel";
    panel.hidden = true;
    panel.innerHTML = `
      <div class="luhm-head">
        <div class="luhm-jrpg-avatar" aria-hidden="true">
          <i class="horn h1"></i><i class="horn h2"></i>
          <i class="hair"></i><i class="face"></i><i class="eye e1"></i><i class="eye e2"></i>
        </div>
        <div class="luhm-title"><strong>LuHm Cathedral</strong><br><small>private Firefox pet console</small></div>
        <button id="luhm-close" type="button" aria-label="Close">×</button>
      </div>
      <div class="luhm-hud"><span>♥ AFF 17</span><span>⚡ SPARKS 500</span><span id="luhm-pity">🎲 PITY 0/20</span></div>
      <div class="luhm-grid">
        <button type="button" data-luhm="PET LUM">PET LUM</button>
        <button type="button" data-luhm="ROLL D20">ROLL D20</button>
        <button type="button" data-luhm="GACHA PULL">GACHA PULL</button>
        <button type="button" data-luhm="DATE EVENT">DATE EVENT</button>
        <button type="button" data-luhm="SUMMON IMAGE">SUMMON IMAGE</button>
        <button type="button" data-luhm="SAVEPOINT">SAVEPOINT</button>
        <button type="button" data-luhm="CAST ULTIMA">CAST ULTIMA ⚡</button>
        <button type="button" data-private-gacha="after-dark">AFTER DARK PULL</button>
      </div>
      <div class="luhm-tools">
        <button type="button" data-tool="scan">CACHE</button>
        <button type="button" data-tool="audio">AUDIO</button>
        <button type="button" data-tool="voice">VOICE TUNE</button>
        <button type="button" data-tool="assets">ASSET VAULT</button>
        <button type="button" data-tool="terminal">TERMINAL</button>
      </div>
      <div id="luhm-pet-status">Lum is lurking. Private cache not scanned.</div>`;

    document.documentElement.append(launcher, panel);
    const status = panel.querySelector("#luhm-pet-status");
    const pity = panel.querySelector("#luhm-pity");

    launcher.addEventListener("click", () => { panel.hidden = !panel.hidden; });
    panel.querySelector("#luhm-close").addEventListener("click", () => { panel.hidden = true; });

    panel.querySelectorAll("[data-luhm]").forEach(btn => {
      btn.addEventListener("click", () => {
        const command = btn.dataset.luhm;
        void playEventAudio(SOUND_EVENTS[command] || "ui");
        const result = insertCommand(command);
        status.textContent = result.ok
          ? `${command} loaded. You choose Send.`
          : "Tap the ChatGPT composer once, then retry.";
        if (result.ok) panel.hidden = true;
      });
    });

    panel.querySelector('[data-private-gacha="after-dark"]').addEventListener("click", async () => {
      void playEventAudio("gacha");
      status.textContent = "Rolling private reward banner…";
      const result = await runtime({type:"LUHM_PRIVATE_GACHA_PULL"});
      if (!result?.ok) {
        status.textContent = "After Dark catalog offline. Sync the private reward pack first.";
        return;
      }
      pity.textContent = `🎲 PITY ${result.pity}/${result.hard_pity}`;
      status.textContent = `${result.tier.toUpperCase()} · ${result.reward.label}`;
      if (result.tier === "Legendary") void playEventAudio("legendary");
    });

    panel.querySelector('[data-tool="scan"]').addEventListener("click", async () => {
      status.textContent = "Scanning 127.0.0.1:8799…";
      const result = await runtime({type:"LUHM_PRIVATE_STATUS"});
      status.textContent = result?.ok
        ? `Private cache GREEN: ${result.files} files${result.packs?.length ? ` / ${result.packs.length} packs` : ""}.`
        : "Private cache offline. Start the private bridge first.";
    });

    panel.querySelector('[data-tool="audio"]').addEventListener("click", async () => {
      status.textContent = "Reading Destiny audio index…";
      const result = await runtime({type:"LUHM_AUDIO_STATUS"});
      status.textContent = result?.ok
        ? `AUDIO: ${result.playable} playable / ${result.game_containers} game containers / ${result.recognized} recognized${result.vgmstream ? " · vgmstream READY" : ""}`
        : "Audio index offline. Run private bridge reindex after syncing assets.";
    });

    panel.querySelector('[data-tool="voice"]').addEventListener("click", () => {
      const result = insertText(VOICE_TUNE_PROMPT);
      status.textContent = result.ok
        ? "Lum voice profile loaded into the composer. You choose Send."
        : "Tap the ChatGPT composer once, then retry.";
      if (result.ok) panel.hidden = true;
    });

    panel.querySelector('[data-tool="assets"]').addEventListener("click", async () => {
      const result = await runtime({type:"LUHM_OPEN_PRIVATE_CACHE"});
      status.textContent = result?.ok ? "Opened private asset vault." : "Private vault unavailable.";
    });

    panel.querySelector('[data-tool="terminal"]').addEventListener("click", async () => {
      const result = await runtime({type:"LUHM_OPEN_TERMINAL"});
      status.textContent = result?.ok ? "Opened loopback terminal." : "Terminal bridge unavailable.";
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mountPanel, {once:true});
  else mountPanel();

  new MutationObserver(() => {
    if (!document.getElementById("luhm-pet-launcher")) mountPanel();
  }).observe(document.documentElement, {childList:true, subtree:true});
})();
