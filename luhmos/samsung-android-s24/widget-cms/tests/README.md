# Widget CMS tests

Smoke target:

```bash
cd luhmos/samsung-android-s24/widget-cms
uv run python -m pytest
```

The API health contract should return `mode = donor-purged` from `/api/health`.
