"""配置访问工具，提供 ConfigManager 单例封装。"""
from __future__ import annotations

from threading import RLock
from typing import Any, ClassVar

from .exceptions import ConfigError
from .loader import load_config
from .settings import (
    AppConfig,
    ContractConfig,
    CorsConfig,
    PostgresConfig,
    RDFConfig,
    SecurityConfig,
    Settings,
)


class ConfigManager:
    """配置管理器，负责加载并缓存 Settings。"""

    _instance: ClassVar[ConfigManager | None] = None
    _lock: ClassVar[RLock] = RLock()

    def __init__(self, settings: Settings) -> None:
        """初始化配置管理器。"""

        self._settings = settings

    @property
    def  settings(self) -> Settings:
        """返回完整配置对象。"""

        return self._settings

    @property
    def app(self) -> AppConfig:
        """获取应用基础配置。"""

        return self._settings.app

    @property
    def cors(self) -> CorsConfig:
        """获取 CORS 配置。"""

        return self._settings.cors

    @property
    def rdf(self) -> RDFConfig:
        """获取 RDF 相关配置。"""

        return self._settings.rdf

    @property
    def postgres(self) -> PostgresConfig:
        """获取 PostgreSQL 配置。"""

        return self._settings.postgres

    @property
    def contract(self) -> ContractConfig:
        """获取接口契约配置。"""

        return self._settings.contract

    @property
    def security(self) -> SecurityConfig:
        """获取安全配置。"""

        return self._settings.security

    @classmethod
    def load(cls, *, env: str | None = None, override_path: str | None = None) -> ConfigManager:
        """加载配置并初始化单例，可指定环境或覆盖文件。"""

        settings = load_config(env=env, override_path=override_path)
        with cls._lock:
            cls._instance = cls(settings)
        return cls._instance

    @classmethod
    def current(cls) -> ConfigManager:
        """返回当前单例，若未初始化则抛出异常。"""

        with cls._lock:
            if cls._instance is None:
                raise ConfigError("ConfigManager 尚未初始化，请在应用启动时调用 load().")
            return cls._instance

    def get(self, path: str, default: Any | None = None) -> Any:
        """按点分路径读取配置，未命中时返回默认值。"""

        cursor: Any = self._settings
        for segment in path.split("."):
            if hasattr(cursor, segment):
                cursor = getattr(cursor, segment)
            elif isinstance(cursor, dict) and segment in cursor:
                cursor = cursor[segment]
            else:
                return default
        return cursor

    def snapshot(self) -> Settings:
        """返回配置深拷贝，避免外部修改原始实例。"""

        return self._settings.model_copy(deep=True)

    @classmethod
    def settings_snapshot(cls) -> Settings:
        """兼容旧接口，返回配置快照。"""

        return cls.current().snapshot()

    def reload(self, *, env: str | None = None, override_path: str | None = None) -> Settings:
        """重新加载配置并返回最新 Settings。"""

        new_settings = load_config(env=env, override_path=override_path)
        self._settings = new_settings
        return new_settings


def load_settings(*, env: str | None = None, override_path: str | None = None) -> Settings:
    """辅助函数：加载配置并返回 Settings。"""

    manager = ConfigManager.load(env=env, override_path=override_path)
    return manager.settings
