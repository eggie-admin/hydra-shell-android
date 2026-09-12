# LuHm OS Chrome Dev / Canary Learning Plugin

Private local-only Manifest V3 browser-extension experiment for learning and UI testing.

## Scope

- Chrome Dev / Chrome Canary desktop development only.
- Not an Android APK.
- Not a Chrome Web Store release.
- No telemetry or outbound network requests.
- No private/copyrighted game assets.
- Destiny Child / Live2D quarantine payloads are never bundled here.
- Chrome Dev and Canary on Android remain behavior/debug harnesses only because Chrome Android does not load normal desktop extensions.

## Features

- Floating LuHm local control orb on ChatGPT pages.
- Page zoom controls from 60% to 120%.
- Reset zoom button.
- Compact-layout toggle.
- Local persistence through `chrome.storage.local` only.
- Keyboard shortcuts while the page is focused:
  - Alt+Shift+- : zoom out
  - Alt+Shift++ : zoom in
  - Alt+Shift+0 : reset

## Local install on desktop Chrome Dev or Canary

1. Open `chrome://extensions`.
2. Enable Developer mode.
3. Choose **Load unpacked**.
4. Select this folder.
5. Open ChatGPT and click the LuHm orb.

## Packaging

The repository workflow `.github/workflows/luhmos-chrome-dev-canary-private-plugin.yml` is manual-only. It validates the Manifest V3 package, rejects quarantined payload types and secret-like files, and creates a short-lived ZIP artifact for private learning use.
