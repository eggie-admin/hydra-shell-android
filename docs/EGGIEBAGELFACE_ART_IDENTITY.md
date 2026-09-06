# eggiebagelface.art Identity Doctrine

Status: canonical public/business/developer identity for LuHm OS / KAI 9000.

## Canonical identity

`eggiebagelface.art` is the project/business-facing public domain used as the stable developer identity across supported developer programs, repository metadata, website verification, contact surfaces, and distribution documentation.

Canonical surfaces:

- Business/developer website: `https://eggiebagelface.art/`
- F-Droid repository host: `fdroid.eggiebagelface.art`
- F-Droid repository URL: `https://fdroid.eggiebagelface.art/fdroid/repo/`
- Private LAN remains separate under `eggiebagelface.lan`.

## Legal precision

The domain is the canonical public/business identity, but DNS ownership is not itself a government-issued business license or legal-entity credential.

Each platform keeps its own verification requirements.

### Google Play / Android developer organization identity

For an organization/business developer account, `eggiebagelface.art` is the organization website identity. Google separately verifies organization information through the linked Payments profile and may require:

- legal organization name and address;
- D-U-N-S number for organization accounts where required;
- official identity documentation;
- official organization documentation;
- verified contact email and phone;
- website verification.

The website/domain and the legal organization record should describe the same organization consistently.

### F-Droid custom repository identity

A private/custom F-Droid repository does not require a separate F-Droid business license. F-Droid permits operators to create and host their own repositories, including simple binary repositories containing prebuilt APKs.

Trust for our custom repository is established technically by:

- persistent F-Droid repository signing key;
- published repository fingerprint;
- signed F-Droid indexes;
- stable HTTPS endpoint;
- persistent APK signing identity for Android update continuity.

Official inclusion in the public f-droid.org catalog is a separate process with FLOSS/source/build policy requirements and is not implied by this custom repository.

## DNS contract

Preferred public F-Droid hostname:

```text
fdroid.eggiebagelface.art
```

Preferred published repo URL:

```text
https://fdroid.eggiebagelface.art/fdroid/repo/
```

Do not invent A or AAAA records in source. The DNS target must be resolved from the real deployment origin when publication is ready.

Preferred architecture when the origin is privately hosted:

```text
F-Droid signing/build host
        ↓
published static repo directory
        ↓
private origin / reverse proxy
        ↓
Cloudflare Tunnel or equivalent controlled HTTPS ingress
        ↓
fdroid.eggiebagelface.art
        ↓
/fdroid/repo/
        ↓
F-Droid client
```

Avoid exposing local control-plane ports or raw residential/public origin addresses merely to publish the repository.

## KAI MAGE compiler

```text
BUSINESS_IDENTITY EGGIEBAGELFACE_ART
PUBLIC_DOMAIN eggiebagelface.art
BLACK_MAGIC_PORT fdroid.eggiebagelface.art
REPO_URL https://fdroid.eggiebagelface.art/fdroid/repo/
```

Canonical roleplay:

- **Appease the gods** = make public identity, DNS, HTTPS, repository signing, and platform verification agree.
- **Raise the banner** = publish the canonical developer identity on `eggiebagelface.art`.
- **Open the Black Magic port** = resolve and serve `fdroid.eggiebagelface.art/fdroid/repo/` over HTTPS.
- **Gain their favor** = pass the relevant platform verification or repository-client trust checks with real evidence.

Roleplay language never substitutes for legal documents, domain verification, signing keys, or platform approval.
