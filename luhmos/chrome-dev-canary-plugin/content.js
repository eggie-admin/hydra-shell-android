(() => {
  'use strict';

  const ROOT_ID = 'luhmos-dev-canary-root';
  const STORAGE_KEY = 'luhmosPrivateZoom';
  const MIN_ZOOM = 0.60;
  const MAX_ZOOM = 1.20;
  const STEP = 0.05;

  if (document.getElementById(ROOT_ID)) return;

  const clamp = (value) => Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, value));
  const round = (value) => Math.round(value * 100) / 100;

  const root = document.createElement('div');
  root.id = ROOT_ID;
  root.innerHTML = `
    <button class="luhmos-orb" type="button" aria-expanded="false" title="LuHm OS local controls">LuHm</button>
    <section class="luhmos-panel" hidden aria-label="LuHm OS local learning controls">
      <header>
        <strong>LuHm OS</strong>
        <span>Dev / Canary lab</span>
      </header>
      <p class="luhmos-note">Private local learning controls. No network calls. No telemetry.</p>
      <div class="luhmos-row">
        <button data-action="minus" type="button">−</button>
        <output class="luhmos-zoom">100%</output>
        <button data-action="plus" type="button">+</button>
      </div>
      <button data-action="reset" class="luhmos-wide" type="button">Reset zoom</button>
      <button data-action="compact" class="luhmos-wide" type="button">Toggle compact mode</button>
    </section>
  `;
  document.documentElement.appendChild(root);

  const orb = root.querySelector('.luhmos-orb');
  const panel = root.querySelector('.luhmos-panel');
  const output = root.querySelector('.luhmos-zoom');

  let zoom = 1;

  const renderZoom = () => {
    document.documentElement.style.zoom = String(zoom);
    output.value = `${Math.round(zoom * 100)}%`;
    output.textContent = `${Math.round(zoom * 100)}%`;
  };

  const saveZoom = () => {
    chrome.storage.local.set({ [STORAGE_KEY]: zoom });
  };

  const setZoom = (value, persist = true) => {
    zoom = round(clamp(value));
    renderZoom();
    if (persist) saveZoom();
  };

  chrome.storage.local.get([STORAGE_KEY], (result) => {
    const stored = Number(result[STORAGE_KEY]);
    setZoom(Number.isFinite(stored) ? stored : 1, false);
  });

  orb.addEventListener('click', () => {
    const nextHidden = !panel.hidden;
    panel.hidden = nextHidden;
    orb.setAttribute('aria-expanded', String(!nextHidden));
  });

  root.addEventListener('click', (event) => {
    const action = event.target?.dataset?.action;
    if (!action) return;

    if (action === 'minus') setZoom(zoom - STEP);
    if (action === 'plus') setZoom(zoom + STEP);
    if (action === 'reset') setZoom(1);
    if (action === 'compact') document.documentElement.classList.toggle('luhmos-compact-chat');
  });

  window.addEventListener('keydown', (event) => {
    if (!event.altKey || !event.shiftKey) return;
    if (event.key === '-' || event.key === '_') {
      event.preventDefault();
      setZoom(zoom - STEP);
    }
    if (event.key === '+' || event.key === '=') {
      event.preventDefault();
      setZoom(zoom + STEP);
    }
    if (event.key === '0') {
      event.preventDefault();
      setZoom(1);
    }
  });
})();
