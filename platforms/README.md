# LuHm OS platform lanes

This directory defines the platform boundary for LuHm OS.

- `android/` — active Samsung/Android implementation lane.
- `apple/` — staged placeholder for future iOS/iPadOS/macOS shell work.
- `windows11/` — staged placeholder for future Windows 11 desktop shell work.
- `ubuntu-debian/` — staged placeholder for future Ubuntu/Debian desktop/package work.

The shared architecture belongs above platform-specific code: Python 3 control plane, shared API contracts, media/job logic, and platform-neutral assets. Native packaging, lifecycle integration, permissions, signing, and store/distribution rules stay inside the relevant platform lane.
