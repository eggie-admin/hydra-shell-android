# Firefox Android companion shell (generic)

This companion shell keeps private runtime assets on-device while staying signing-friendly for a public WebExtension repository.

## Security boundary

- Manifest V3 extension shell only.
- Local bridge is restricted to `http://127.0.0.1` and only `data/` or `images/` paths.
- Terminal launch opens a user-controlled localhost web terminal URL in a tab. The extension does **not** get shell execution privileges.
- No prompt auto-send.
- No credential, cookie, or chat transcript scraping.
- DOM controls fail closed when expected ChatGPT composer elements are missing.

## Runtime expectations

- Chat companion controls are touch-friendly floating buttons.
- Localhost endpoints are operator-managed services outside the extension package.
- Private asset packs remain out-of-scope and must not be committed here.
