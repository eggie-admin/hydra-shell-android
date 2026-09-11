# LuHm ChatGPT Companion

Desktop Chrome helper for the **ChatGPT-only** Lum Roleplay lane.

## What it does

- Adds quick buttons for the sealed commands:
  - `PET LUM`
  - `ROLL D20`
  - `GACHA PULL`
  - `DATE EVENT`
  - `SUMMON IMAGE`
  - `CAST ULTIMA`
  - `SAVEPOINT`
- Inserts the selected command into the ChatGPT composer.
- Never clicks Send and never submits a prompt without the Professor.
- Does not store API keys or call OpenAI directly.

## Install

Chrome does not allow ordinary websites to silently install unpacked extensions. For development, unzip the package, open `chrome://extensions`, enable Developer mode, choose **Load unpacked**, and select this folder.

For a true **Add to Chrome** flow, the extension must be published through the Chrome Web Store or deployed through managed enterprise policy.

## Android note

Google Chrome on Android does not support normal Chrome extensions. This helper is therefore a desktop-Chrome companion. The actual Lum game remains inside ChatGPT and does not depend on this extension.

## Scope

This extension is convenience UI only. It must not become an external autonomous agent, publish content, mutate repositories, or bypass ChatGPT/user confirmation.
