# KAI 9000 Edge Gallery + Mini Ollama Antenna

This mutation preserves the canonical Samsung trust split while adding Google AI Edge Gallery as a protected local model lab.

## Canonical split

- **Ordinary Termux outside Samsung Secure Folder** owns daemon/orchestration processes.
- **Samsung Secure Folder** remains a protected cockpit/client/sandbox and probes localhost services rather than owning ordinary-Termux PIDs.
- **Google AI Edge Gallery** is a standalone local Android inference/runtime lab.
- **Mini Ollama antenna** exposes a small loopback-only compatibility surface on `127.0.0.1:11434`.
- **Canonical KAI antenna** remains FastAPI on `127.0.0.1:8797`.
- **LiteRT-LM** is the future direct production bridge for Edge-Gallery-class models inside LuHm OS.

## Why Edge Gallery is not directly proxied

The Edge Gallery Android app is treated as its own sandbox. This lane does not assume an exported HTTP API, does not scrape private app storage, and does not bypass Android package/profile boundaries.

The current mini Ollama shim is therefore deliberately fail-closed:

1. it is always loopback-only;
2. it reports Edge Gallery as a manual protected runtime;
3. it can proxy chat only when an explicit loopback `llama.cpp` OpenAI-compatible server is available;
4. otherwise `/api/chat` returns `503 no_callable_local_backend` rather than inventing a response.

That lets existing Ollama-aware KAI code probe `127.0.0.1:11434` without pretending Edge Gallery is Ollama.

## Edge Gallery model profile

Preferred on-device model:

- `Gemma-4-E2B-it`
- Edge Gallery UI status observed 2026-09-11: **ready / Try it**
- model card size: about 2.6 GB
- 32K context
- text/image/audio input
- GPU/CPU

Secondary model:

- `Gemma-4-E4B-it`
- larger memory/storage lane; do not make it the default phone model until the device gate is explicitly proven.

The screenshot confirms Edge Gallery UI readiness for E2B. It does **not** by itself prove whether Edge Gallery is installed in the owner profile or inside Samsung Secure Folder. That remains a separate gate.

## Install in ordinary Termux

```bash
cd ~/kai9000
# copy or clone termux/kai-edge-antenna
cd termux/kai-edge-antenna
chmod +x kai-edge-antenna
./kai-edge-antenna bootstrap
./kai-edge-antenna start
./kai-edge-antenna status
```

Expected service:

```text
http://127.0.0.1:11434
```

Useful commands:

```bash
./kai-edge-antenna status
./kai-edge-antenna logs
./kai-edge-antenna restart
./kai-edge-antenna secure-probe
```

## Optional callable local backend

The shim can route chat to a local OpenAI-compatible `llama.cpp` server:

```bash
export KAI_LLAMA_CPP_URL=http://127.0.0.1:8080
```

No non-loopback backend is accepted.

This is intentionally separate from Edge Gallery. Edge Gallery remains the manual/local model lab until LuHm OS integrates LiteRT-LM directly.

## Secure Folder sanity probe

From the Secure Folder AcodeX client terminal, probe only localhost services:

```bash
curl -fsS http://127.0.0.1:11434/health | python -m json.tool
curl -fsS http://127.0.0.1:8797/api/antenna/status | python -m json.tool
```

Do not inspect ordinary-Termux PIDs from Secure Folder and do not enable root/Sui in the trusted Secure Folder lane.

## Green semantics

- **GREEN service**: mini antenna process answers `/health` on loopback.
- **YELLOW backend**: no callable `llama.cpp` backend yet; Edge Gallery is manual only.
- **GREEN model UI**: Edge Gallery shows Gemma-4-E2B-it ready with `Try it`.
- **YELLOW profile placement**: screenshot does not yet prove Edge Gallery is inside Secure Folder.
- **Future GREEN production inference**: LiteRT-LM is directly integrated behind LuHm's typed local inference interface and passes device smoke tests.
