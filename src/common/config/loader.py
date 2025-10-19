"""配置加载工具函数，负责合并 YAML 与环境变量。"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Iterable

import yaml
from dotenv import load_dotenv
from pydantic import ValidationError

from .exceptions import ConfigError
from .settings import Settings

# 环境变量到配置键路径的映射表
ENV_KEY_MAP: dict[str, tuple[str, ...]] = {
    "APP_NAME": ("app", "name"),
    "APP_ENV": ("app", "env"),
    "APP_PORT": ("app", "port"),
    "APP_DEBUG": ("app", "debug"),
    "CORS_ORIGINS": ("cors", "origins"),
    "RDF_ENDPOINT": ("rdf", "endpoint"),
    "RDF_DATASET": ("rdf", "dataset"),
    "RDF_USERNAME": ("rdf", "auth", "username"),
    "RDF_PASSWORD": ("rdf", "auth", "password"),
    "RDF_TIMEOUT_DEFAULT": ("rdf", "timeout", "default"),
    "RDF_TIMEOUT_MAX": ("rdf", "timeout", "max"),
    "RDF_RETRY_MAX": ("rdf", "retries", "max_attempts"),
    "RDF_RETRY_BACKOFF": ("rdf", "retries", "backoff_seconds"),
    "RDF_RETRY_MULTIPLIER": ("rdf", "retries", "backoff_multiplier"),
    "RDF_RETRY_JITTER": ("rdf", "retries", "jitter_seconds"),
    "POSTGRES_DSN": ("postgres", "dsn"),
    "POSTGRES_SCHEMA": ("postgres", "schema"),
    "REDIS_URL": ("redis", "url"),
    "REDIS_NAMESPACE": ("redis", "namespace"),
    "QDRANT_HTTP_URL": ("qdrant", "http_url"),
    "QDRANT_GRPC_URL": ("qdrant", "grpc_url"),
    "LOG_LEVEL": ("logging", "level"),
    "LOG_FORMAT": ("logging", "format"),
    "CONTRACT_ENVELOPE_VERSION": ("contract", "envelope_version"),
    "CONTRACT_DEFAULT_TIMEOUT": ("contract", "default_timeout"),
    "CONTRACT_DEFAULT_PAGE_SIZE": ("contract", "pagination", "default_size"),
    "CONTRACT_MAX_PAGE_SIZE": ("contract", "pagination", "max_size"),
    "TRACE_HEADER": ("security", "trace_header"),
    "CLIENT_HEADER": ("security", "client_header"),
    "IDEMPOTENCY_HEADER": ("security", "idempotency_header"),
    "REQUIRE_API_KEY": ("security", "require_api_key"),
    "API_KEY_HEADER": ("security", "api_key_header"),
}


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _config_dir() -> Path:
    return _backend_root() / "config"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    except yaml.YAMLError as exc:  # pragma: no cover - rare
        raise ConfigError(f"配置文件解析失败: {path}", cause=exc) from exc
    if not isinstance(data, dict):
        raise ConfigError(f"配置文件必须以字典为根节点: {path}")
    return data


def _deep_merge(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in overrides.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _set_in_mapping(mapping: dict[str, Any], path: Iterable[str], value: Any) -> None:
    cursor = mapping
    *parents, final_key = tuple(path)
    for key in parents:
        if key not in cursor or not isinstance(cursor[key], dict):
            cursor[key] = {}
        cursor = cursor[key]
    cursor[final_key] = value


def _parse_env_value(raw: str) -> Any:
    value = raw.strip()
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        if value.startswith("0") and value != "0":  # keep strings like 0123 intact
            raise ValueError
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def _apply_env_overrides(config_dict: dict[str, Any]) -> dict[str, Any]:
    result = dict(config_dict)
    for env_key, path in ENV_KEY_MAP.items():
        env_value = os.getenv(env_key)
        if env_value is None:
            continue
        _set_in_mapping(result, path, _parse_env_value(env_value))
    return result


def load_config(*, env: str | None = None, override_path: str | os.PathLike[str] | None = None) -> Settings:
    """Load configuration by composing defaults, environment overlays, and env vars."""

    load_dotenv()

    resolved_env = (env or os.getenv("APP_ENV") or "development").lower()
    config_dir = _config_dir()

    default_cfg = _load_yaml(config_dir / "default.yaml")
    env_cfg = _load_yaml(config_dir / f"{resolved_env}.yaml")
    composed = _deep_merge(default_cfg, env_cfg)

    explicit_override = override_path or os.getenv("APP_CONFIG_PATH")
    if explicit_override:
        composed = _deep_merge(composed, _load_yaml(Path(explicit_override)))

    with_env = _apply_env_overrides(composed)

    try:
        settings = Settings.model_validate(with_env)
    except ValidationError as exc:  # pragma: no cover - executed in runtime, hard to unit test
        raise ConfigError("Failed to validate application settings", cause=exc) from exc

    return settings
