"""Provider-neutral policy. SDK imports stay lazy and network calls stay caller-controlled."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

from .config import LuhmConfig

ProviderName = Literal["openai", "google"]


@dataclass(frozen=True, slots=True)
class ProviderPolicy:
    provider: ProviderName
    api_key_env: str
    advisory_only: bool = True
    direct_shell_execution: bool = False

    def require_key(self) -> str:
        value = os.environ.get(self.api_key_env, "").strip()
        if not value:
            raise RuntimeError(f"required environment variable is missing: {self.api_key_env}")
        return value


def policy_from_config(config: LuhmConfig, provider: ProviderName) -> ProviderPolicy:
    selected = getattr(config.providers, provider)
    if not selected.enabled:
        raise RuntimeError(f"provider is disabled by config: {provider}")
    return ProviderPolicy(provider=provider, api_key_env=selected.api_key_env)


def build_sdk_client(policy: ProviderPolicy):
    """Build a provider SDK client without making a network request."""
    key = policy.require_key()
    if policy.provider == "openai":
        from openai import OpenAI
        return OpenAI(api_key=key)
    if policy.provider == "google":
        from google import genai
        return genai.Client(api_key=key)
    raise AssertionError(f"unsupported provider: {policy.provider}")
