# SM-X400 Private F-Droid Cathedral Cockpit

## Goal

Turn the factory-reset Samsung SM-X400 into a clean LuHm OS cockpit without publishing the Cathedral build to the public F-Droid mirror.

## Trust model

- Professor holds final device/release authority.
- GitHub branch `luhmos-main` remains the integration source.
- The Cathedral stream is a private **debug channel**, but the APK is release-signed with the persistent LuHm OS signer so Android/F-Droid update continuity is preserved.
- GitHub output is attached only to a **draft release**, never a public release or `fdroid-public` branch.
- F-Droid imports the repo from localhost after an authenticated pull.
- No serials, IMEI, tokens, keystores, signing passwords, or account identifiers enter the repo bundle.

## Fresh tablet path

1. Factory reset the SM-X400 and finish Samsung setup.
2. Install F-Droid from its official bootstrap package.
3. From the normal F-Droid repository install Termux and GitHub CLI prerequisites as needed.
4. Authenticate `gh` to the Professor's GitHub account.
5. Run `tools/fdroid/kai-private-cathedral-pull.sh`.
6. Start the local server printed by the script.
7. In F-Droid, add the custom repository URL:

   `http://127.0.0.1:8796/fdroid/repo`

8. Refresh repositories and install/update **LuHm OS**.
9. Android remains the final installer confirmation gate.

## Release stream

Each successful private workflow run generates a monotonically increasing Cathedral version code and a signed F-Droid repository bundle. The bundle includes the APK, F-Droid indexes, SHA-256 evidence, signer fingerprints, and install helper.

The stream does not publish GitHub Pages, a public release, or the `fdroid-public` branch.

## Source-pass doctrine

The 2026-09-13 AI_LOGIC, OLLAMA, and DICTATION source passes are the operating doctrine for this lane: Professor holds the crown; proof is required for GREEN; secret printing and donor-code ingestion remain forbidden; the F-Droid stream is bounded to the requested private build/install workflow.
