# LuHm OS Vendor Partner / Proprietary Dev Channel Playbook

Branch: `luhmos/dev/samsung-android-paid-pro`
Scope: Samsung Android paid-Pro development only

## Truth rule

A vendor lane is not marked APPROVED until we have a vendor approval artifact, account state, or other direct evidence. User-stated approvals remain preserved as user-stated until the artifact is attached. Paid-service or partner status never grants build, signing, merge, install, publish, root, or Crown authority.

## Priority order

1. Samsung Remote Test Lab Partner Program
   - Goal: more Remote Test Lab credits and longer Galaxy device sessions.
   - Why now: closest match to the existing Google edge/testing lane and directly aligned with Samsung Android validation.

2. Samsung Galaxy Store commercial seller + Developer API
   - Goal: proprietary Samsung distribution/API channel for app management, IAP, and statistics.
   - Gate: Samsung account, Seller Portal, commercial seller status, app registration.

3. GitHub Developer Program
   - Goal: formalize LuHm OS as a GitHub-integrated developer project.
   - Current fit: project already uses the GitHub API/integration in development.
   - Remaining application datum: a support email/contact for GitHub users.

4. Cloudflare Technology Partner Program
   - Goal: validated LuHm OS integration around Zero Trust, application/network security, or developer platform services.
   - Gate: first produce a functional, documented Cloudflare integration and proof receipts.

5. Cloudflare for Startups
   - Goal: credits and enhanced Cloudflare services if business eligibility is met.
   - Gate: verify incorporation, age/funding criteria, live public site, business email, and other current program requirements before applying.

6. OpenAI for Startups
   - Goal: builder resources now; credit/support paths when eligible through VC partners or qualifying startup events/programs.
   - Do not assume credits or partner status without approval evidence.

## Integration tracks, not partner claims

- Sentry: build an OAuth/custom integration with least-privilege scopes for CI, releases, and Android error telemetry.
- Hugging Face: treat Team/Enterprise/Inference access as paid platform entitlements unless a separate partner approval is later documented.

## Application packet template

Keep one secretless packet per vendor:

- project: LuHm OS
- repo: `eggie-admin/hydra-shell-android`
- working branch: `luhmos/dev/samsung-android-paid-pro`
- platform: Samsung Android only
- package: `art.eggiebagelface.luhmos`
- public site: `eggiebagelface.art` when production-ready
- integration summary
- current working demo / test evidence
- privacy and security model
- support contact
- requested program / benefit
- vendor approval artifact reference after acceptance

Do not put API keys, access tokens, signing material, payment credentials, private CA keys, or recovery secrets in this packet or repository.

## Promotion rule

A program changes status from `TARGET_*` to `APPLIED` only after a real application is submitted. It changes to `APPROVED` only after vendor confirmation is captured in the hardened private source of truth.
