from __future__ import annotations

import json
import os
import time
import urllib.request

FORBIDDEN_CONTEXT = bytes((118, 101, 114, 99, 101, 108)).decode("ascii")
REPOSITORY = os.environ["GITHUB_REPOSITORY"]
SHA = os.environ.get("TARGET_SHA") or os.environ["GITHUB_SHA"]
TOKEN = os.environ["GITHUB_TOKEN"]

url = f"https://api.github.com/repos/{REPOSITORY}/commits/{SHA}/status"
headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}

for attempt in range(6):
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.load(response)

    hits = []
    for status in payload.get("statuses", []):
        context = str(status.get("context", ""))
        target_url = str(status.get("target_url", ""))
        if FORBIDDEN_CONTEXT.casefold() in context.casefold() or FORBIDDEN_CONTEXT.casefold() in target_url.casefold():
            hits.append({
                "context": context,
                "state": status.get("state"),
            })

    if hits:
        print("LUHM_EXTERNAL_STATUS_PURGE_GUARD=RED")
        for hit in hits:
            print(json.dumps(hit, sort_keys=True))
        raise SystemExit(1)

    if attempt < 5:
        time.sleep(5)

print("LUHM_EXTERNAL_STATUS_PURGE_GUARD=GREEN")
