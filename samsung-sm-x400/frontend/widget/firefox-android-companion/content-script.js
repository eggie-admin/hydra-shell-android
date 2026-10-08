const ROOT_ID = "kai9000-firefox-companion-controls";

function findComposer() {
  const form = document.querySelector("form");
  if (!(form instanceof HTMLFormElement)) {
    return null;
  }
  const textarea = form.querySelector("textarea");
  if (!(textarea instanceof HTMLTextAreaElement)) {
    return null;
  }
  return { form, textarea };
}

function showDisabledState(root, reason) {
  root.classList.add("kai-disabled");
  root.dataset.state = "disabled";
  root.title = reason;
}

function setPromptOnly(textarea, value) {
  textarea.value = value;
  textarea.dispatchEvent(new Event("input", { bubbles: true }));
  textarea.focus();
}

function makeButton(label, className, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.textContent = label;
  button.addEventListener("click", onClick);
  return button;
}

async function bridgeAsset(path) {
  const reply = await browser.runtime.sendMessage({
    type: "bridge:fetch-local-asset",
    assetPath: path,
  });

  if (!reply || reply.ok !== true || typeof reply.payloadBase64 !== "string") {
    return null;
  }

  return `data:${reply.contentType};base64,${reply.payloadBase64}`;
}

function installControls() {
  if (document.getElementById(ROOT_ID)) {
    return;
  }

  const root = document.createElement("div");
  root.id = ROOT_ID;
  root.className = "kai-controls";

  const composer = findComposer();
  if (!composer) {
    showDisabledState(root, "composer-not-found");
    root.textContent = "KAI companion unavailable on this page.";
    document.body.appendChild(root);
    return;
  }

  const { textarea } = composer;
  const terminal = makeButton("Open local terminal", "kai-btn", async () => {
    await browser.runtime.sendMessage({ type: "launcher:open-terminal" });
  });

  const draft = makeButton("Insert local draft", "kai-btn", () => {
    setPromptOnly(textarea, "Review local bridge response and edit before sending.");
  });

  const image = makeButton("Load local image", "kai-btn", async () => {
    const dataUrl = await bridgeAsset("/images/preview.png");
    if (!dataUrl) {
      return;
    }
    setPromptOnly(textarea, `Local image ready: ${dataUrl.slice(0, 80)}...`);
  });

  root.append(terminal, draft, image);
  document.body.appendChild(root);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", installControls, { once: true });
} else {
  installControls();
}
