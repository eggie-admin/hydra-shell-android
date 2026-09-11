# LuHm OS 1.0.0 Samsung release ceremony

This walkthrough completes the one-time trusted release setup for LuHm OS without touching Termux.

## 1. Select the Google Cloud project

<walkthrough-project-setup billing="true"></walkthrough-project-setup>

The bootstrap uses the project currently selected in Cloud Shell.

## 2. Upload the private signing bootstrap

Use the Cloud Shell file upload control to upload:

`LuHmOS_1.0.0_SIGNING_BOOTSTRAP_PRIVATE.zip`

Keep this archive private. It contains the persistent Android and F-Droid signing identities and must never be committed to Git.

## 3. Run the release bootstrap

<walkthrough-open-cloud-shell-button></walkthrough-open-cloud-shell-button>

Run:

```bash
chmod +x infra/gcp/full-samsung-release-bootstrap.sh
./infra/gcp/full-samsung-release-bootstrap.sh "$HOME/LuHmOS_1.0.0_SIGNING_BOOTSTRAP_PRIVATE.zip"
```

The script performs the authorized one-time Google/GitHub HTTPS authentication, configures GitHub-to-Google Workload Identity Federation, stores the six signing values in Secret Manager and GitHub Actions encrypted secrets, records the public signer fingerprints, and launches the signed LuHm OS public F-Droid release workflow.

Do not paste private keystore material or passwords into chat, issues, commits, workflow inputs, or logs.

## 4. Release success criteria

The release is GREEN only when all of the following are true:

- GitHub Release `v1.0.0` exists.
- Release asset `luhmos-1.0.0.apk` exists.
- Package is `art.eggiebagelface.luhmos`.
- Version is `1.0.0` / `versionCode` 100.
- APK signer SHA-256 is `0108A9FBF1EF63183CC749B102F5FAEFEFA5AD6F1F668A2686199EC0D5671DD5`.
- The public LuHm OS F-Droid repository is published.
- F-Droid repository fingerprint SHA-256 is `8235EC85F755C8851009D55DC2E8CB90D09CB5DFEBE3DB4AB34802BFE393E200`.

## 5. IzzyOnDroid

After the signed GitHub Release is public, use `release/IZZYONDROID_SUBMISSION_1.0.0.md` as the inclusion-request payload. IzzyOnDroid inclusion remains an external maintainer decision and must not be reported as GREEN until the package appears in its repository.
