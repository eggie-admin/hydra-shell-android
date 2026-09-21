"""Strict YAML configuration loader for the LuHm service lane."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field


class SecurityConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    execution_posture: Literal["advisory_only"] = "advisory_only"
    direct_shell_execution: bool = False
    secrets_from_environment_only: bool = True
    allow_browser_secrets: bool = False


class ProviderConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: bool = False
    api_key_env: str


class ProvidersConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    default: Literal["none", "openai", "google"] = "none"
    openai: ProviderConfig
    google: ProviderConfig


class LuhmConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema: Literal["luhm_os.runtime_config.v1"]
    mode: str
    security: SecurityConfig
    providers: ProvidersConfig
    services: dict[str, object] = Field(default_factory=dict)
    android: dict[str, object] = Field(default_factory=dict)
    logging: dict[str, object] = Field(default_factory=dict)


def load_config(path: str | Path) -> LuhmConfig:
    source = Path(path)
    raw = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("LuHm YAML root must be a mapping")
    config = LuhmConfig.model_validate(raw)
    if config.security.direct_shell_execution:
        raise ValueError("direct shell execution is forbidden")
    if not config.security.secrets_from_environment_only:
        raise ValueError("secrets must come from environment")
    if config.security.allow_browser_secrets:
        raise ValueError("browser secrets are forbidden")
    return config
