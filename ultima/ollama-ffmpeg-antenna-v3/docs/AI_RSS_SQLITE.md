# AI/RSS/SQLite additive integration

Canonical implementation location:
`ultima/ollama-ffmpeg-antenna-v3/ai_feed/`

Why this location:
- reuses the existing FastAPI process and port 8797;
- preserves Ollama loopback policy;
- preserves the existing Python authority kernel;
- avoids a second daemon and duplicated runtime tree.

Apply `patches/magic_server.py.patch` only after the build freeze is lifted.
The new router is additive under `/api/ai/*`.

No RSS fetch scheduler runs implicitly. Android/Termux supervisors should invoke refresh
on a bounded cadence. This avoids pretending a Python background thread is a reliable
Android lifecycle service.
