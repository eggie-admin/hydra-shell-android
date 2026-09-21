#!/usr/bin/env python3
"""Fail closed if canonical deploy lanes regain automatic or weakly-confirmed authority."""
from pathlib import Path
import re
import sys

CF = Path('.github/workflows/cloudflare-coming-soon.yml')
GCP = Path('.github/workflows/google-white-magic-strict-free-vm.yml')

errors: list[str] = []

for path in (CF, GCP):
    if not path.is_file():
        errors.append(f'missing:{path}')

if not errors:
    cf = CF.read_text(encoding='utf-8')
    gcp = GCP.read_text(encoding='utf-8')

    cf_required = (
        'workflow_dispatch:',
        "if: github.event_name == 'workflow_dispatch'",
        'confirm_publish:',
        'test "$CONFIRM" = YES',
        'Publish eggiebagelface.art',
        'contents: read',
    )
    for marker in cf_required:
        if marker not in cf:
            errors.append(f'cloudflare_missing:{marker}')
    if 'contents: write' in cf or 'actions: write' in cf:
        errors.append('cloudflare_write_permission')

    gcp_required = (
        'workflow_dispatch:',
        'confirm_provision:',
        "if: inputs.confirm_provision == 'PROVISION'",
        'test "$CONFIRM_PROVISION" = PROVISION',
        'environment: testing',
        'contents: read',
        'id-token: write',
    )
    for marker in gcp_required:
        if marker not in gcp:
            errors.append(f'gcp_missing:{marker}')
    if re.search(r'(?m)^  (?:push|pull_request|workflow_run):', gcp):
        errors.append('gcp_nonmanual_trigger')
    if '${{ secrets.' in gcp or 'GOOGLE_APPLICATION_CREDENTIALS' in gcp:
        errors.append('gcp_static_secret_reference')

if errors:
    print('LUHMOS_DEPLOY_AUTHORITY_LOCK_RED', file=sys.stderr)
    for error in errors:
        print(error, file=sys.stderr)
    raise SystemExit(1)

print('LUHMOS_DEPLOY_AUTHORITY_LOCK_GREEN')
print('CLOUDFLARE_PRODUCTION_CONFIRMATION=REQUIRED')
print('GCP_PROVISION_CONFIRMATION=PROVISION_REQUIRED')
print('AUTO_GCP_PROVISION_TRIGGER=ABSENT')
