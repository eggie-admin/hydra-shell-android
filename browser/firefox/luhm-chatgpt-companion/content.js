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
  const ALLOWED_EMOTIONS = new Set(["neutral", "happy", "teasing", "annoyed", "excited", "soft"]);
  const VOICE_MODE_PROMPT = [
    "LUM JAPANESE VOICE MODE ON.",
    "For spoken/playful replies, keep Lum original rather than imitating a specific copyrighted character or actor.",
    "Use short natural Japanese, usually 1-3 sentences, with warm playful sassy PG-13 goth-alt oni/JRPG energy.",
    "Technical accuracy outranks roleplay. Address me as Professor occasionally, not every sentence.",
    "End each voice-mode reply with exactly these three plain-text lines, with no markdown fences:",
    "LUM-JP: <natural Japanese line to speak>",
    "LUM-EN: <faithful concise English subtitle>",
    "LUM-EMOTION: <neutral|happy|teasing|annoyed|excited|soft>",
    "Do not put sound-effect instructions in those lines. The private Firefox companion handles audio cues separately."
  ].join("\n");

  let voiceModeEnabled = false;
  let lastVoiceSignature = "";
  let subtitleTimer = null;
  let inspectTimer = null;

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

  function subtitleNode() {
    let overlay = document.getElementById("luhm-subtitle-overlay");
    if (overlay) return overlay;
    overlay = document.createElement("aside");
    overlay.id = "luhm-subtitle-overlay";
    overlay.hidden = true;
    overlay.innerHTML = '<div class="luhm-subtitle-jp"></div><div class="luhm-subtitle-en"></div><div class="luhm-subtitle-emotion"></div>';
    document.documentElement.appendChild(overlay);
    return overlay;
  }

  function showSubtitle(ja, en, emotion) {
    const overlay = subtitleNode();
    overlay.querySelector(".luhm-subtitle-jp").textContent = ja;
    overlay.querySelector(".luhm-subtitle-en").textContent = en;
    overlay.querySelector(".luhm-subtitle-emotion").textContent = emotion || "neutral";
    overlay.hidden = false;
    if (subtitleTimer) clearTimeout(subtitleTimer);
    subtitleTimer = setTimeout(() => { overlay.hidden = true; }, Math.min(14000, Math.max(5000, en.length * 85)));
  }

  function japaneseVoice() {
    if (!("speechSynthesis" in window)) return null;
    const voices = window.speechSynthesis.getVoices();
    return voices.find(v => /^ja(-|$)/i.test(v.lang) && v.localService)
      || voices.find(v => /^ja(-|$)/i.test(v.lang))
      || null;
  }

  function browserSpeakJapanese(ja, emotion) {
    if (!("speechSynthesis" in window) || !window.SpeechSynthesisUtterance) return false;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(ja);
    utterance.lang = "ja-JP";
    const voice = japaneseVoice();
    if (voice) utterance.voice = voice;
    utterance.rate = emotion === "excited" ? 1.08 : emotion === "soft" ? 0.92 : 1.0;
    utterance.pitch = emotion === "teasing" ? 1.08 : emotion === "annoyed" ? 0.96 : 1.03;
    utterance.volume = 0.92;
    window.speechSynthesis.speak(utterance);
    return true;
  }

  async function speakJapanese(ja, emotion) {
    const cached = await runtime({type:"LUHM_VOICE_CACHE_GET", ja});
    if (cached?.ok && cached.data_url) {
      try {
        const audio = new Audio(cached.data_url);
        audio.volume = 0.92;
        await audio.play();
        return {ok:true, source:"local-ttl-cache", provider:cached.provider || "cache"};
      } catch (_) {}
    }
    return browserSpeakJapanese(ja, emotion)
      ? {ok:true, source:"web-speech"}
      : {ok:false, source:"subtitle-only"};
  }

  function parseVoiceBlock(text) {
    if (!text) return null;
    const jp = text.match(/(?:^|\n)LUM-JP:\s*(.+?)(?=\nLUM-EN:|$)/s);
    const en = text.match(/(?:^|\n)LUM-EN:\s*(.+?)(?=\nLUM-EMOTION:|$)/s);
    const emotionMatch = text.match(/(?:^|\n)LUM-EMOTION:\s*([a-zA-Z_-]+)/);
    if (!jp || !en) return null;
    const ja = jp[1].trim();
    const english = en[1].trim();
    const rawEmotion = (emotionMatch?.[1] || "neutral").toLowerCase();
    const emotion = ALLOWED_EMOTIONS.has(rawEmotion) ? rawEmotion : "neutral";
    if (!ja || !english || ja.length > 1000 || english.length > 1200) return null;
    return {ja, en:english, emotion};
  }

  function newestAssistantText() {
    const exact = [...document.querySelectorAll('[data-message-author-role="assistant"]')];
    if (exact.length) return exact[exact.length - 1].textContent || "";
    const articles = [...document.querySelectorAll("article")];
    for (let i = articles.length - 1; i >= 0; i--) {
      const text = articles[i].textContent || "";
      if (text.includes("LUM-JP:") && text.includes("LUM-EN:")) return text;
    }
    return "";
  }

  function signatureFor(parsed) {
    return parsed ? `${parsed.ja}\u241f${parsed.en}\u241f${parsed.emotion}` : "";
  }

  async function inspectNewestVoiceReply() {
    if (!voiceModeEnabled) return;
    const parsed = parseVoiceBlock(newestAssistantText());
    if (!parsed) return;
    const signature = signatureFor(parsed);
    if (signature === lastVoiceSignature) return;
    lastVoiceSignature = signature;
    showSubtitle(parsed.ja, parsed.en, parsed.emotion);
    await speakJapanese(parsed.ja, parsed.emotion);
  }

  function setVoiceMode(enabled) {
    voiceModeEnabled = Boolean(enabled);
    if (voiceModeEnabled) {
      lastVoiceSignature = signatureFor(parseVoiceBlock(newestAssistantText()));
      return;
    }
    lastVoiceSignature = "";
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    const overlay = document.getElementById("luhm-subtitle-overlay");
    if (overlay) overlay.hidden = true;
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
        <button type="button" data-tool="voice">VOICE MODE</button>
        <button type="button" data-tool="assets">ASSET VAULT</button>
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
        status.textContent = result.ok ? `${command} loaded. You choose Send.` : "Tap the ChatGPT composer once, then retry.";
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
      status.textContent = `${result.tier.toUpperCase()} · ${result.reward.label}${result.duplicate ? ` · copy #${result.copies}` : " · NEW"}`;
      if (result.tier === "Legendary") void playEventAudio("legendary");
    });

    panel.querySelector('[data-tool="scan"]').addEventListener("click", async () => {
      status.textContent = "Scanning 127.0.0.1:8799…";
      const result = await runtime({type:"LUHM_PRIVATE_STATUS"});
      status.textContent = result?.ok
        ? `Private cache GREEN: ${result.files} files${result.packs?.length ? ` / ${result.packs.length} packs` : ""}.`
        : "Private cache offline. Start the private asset bridge first.";
    });

    panel.querySelector('[data-tool="audio"]').addEventListener("click", async () => {
      status.textContent = "Reading Destiny audio index…";
      const result = await runtime({type:"LUHM_AUDIO_STATUS"});
      status.textContent = result?.ok
        ? `AUDIO: ${result.playable} playable / ${result.game_containers} game containers / ${result.recognized} recognized${result.vgmstream ? " · vgmstream READY" : ""}`
        : "Audio index offline. Run the private voice-cache sync first.";
    });

    panel.querySelector('[data-tool="voice"]').addEventListener("click", () => {
      if (voiceModeEnabled) {
        setVoiceMode(false);
        status.textContent = "Japanese voice mode OFF.";
        return;
      }
      const result = insertText(VOICE_MODE_PROMPT);
      if (!result.ok) {
        status.textContent = "Tap the ChatGPT composer once, then retry.";
        return;
      }
      setVoiceMode(true);
      status.textContent = "Japanese voice mode armed for this page session. Prompt loaded; you choose Send.";
      panel.hidden = true;
    });

    panel.querySelector('[data-tool="assets"]').addEventListener("click", async () => {
      const result = await runtime({type:"LUHM_OPEN_PRIVATE_CACHE"});
      status.textContent = result?.ok ? "Opened private asset vault." : "Private vault unavailable.";
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mountPanel, {once:true});
  else mountPanel();

  new MutationObserver(() => {
    if (!document.getElementById("luhm-pet-launcher")) mountPanel();
    if (!voiceModeEnabled) return;
    if (inspectTimer) clearTimeout(inspectTimer);
    inspectTimer = setTimeout(() => { void inspectNewestVoiceReply(); }, 350);
  }).observe(document.documentElement, {childList:true, subtree:true, characterData:true});
})();
