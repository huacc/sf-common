"""日志工厂骨架，负责统一输出格式与级别控制。"""
from __future__ import annotations

import json
import logging
from typing import Any

_RESERVED_KEYS = {
    'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename', 'module',
    'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName', 'created', 'msecs',
    'relativeCreated', 'thread', 'threadName', 'processName', 'process', 'message',
}


class JsonFormatter(logging.Formatter):
    """结构化 JSON 格式化器，配合配置项输出统一字段。"""

    def __init__(self, *, indent: int | None = None) -> None:
        super().__init__()
        self._indent = indent

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _RESERVED_KEYS and not key.startswith('_')
        }
        if extras:
            payload.update(extras)
        return json.dumps(payload, ensure_ascii=False, indent=self._indent)


class LoggerFactory:
    """日志工厂，统一管理日志实例创建。"""

    @staticmethod
    def create_logger(name: str, *, level: int = logging.INFO, handlers: list[logging.Handler] | None = None) -> logging.Logger:
        """根据名称创建日志记录器，后续可扩展 JSON 格式化等能力。"""

        logger = logging.getLogger(name)
        logger.setLevel(level)
        if handlers:
            logger.handlers = handlers
        return logger

    @staticmethod
    def get_default_handler() -> logging.Handler:
        """返回符合配置的默认 Handler，供快速接入使用。"""

        handler = logging.StreamHandler()
        formatter: logging.Formatter
        fmt_type = 'text'
        indent: int | None = None
        try:
            from common.config import ConfigManager  # 延迟导入，避免初始化顺序问题

            settings = ConfigManager.current().settings
            fmt_type = settings.logging.format
            indent = settings.logging.json_indent
        except Exception:  # noqa: BLE001 - 在初始化早期可能尚未加载配置
            fmt_type = 'text'
            indent = None
        if fmt_type == 'json':
            formatter = JsonFormatter(indent=indent)
        else:
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
        handler.setFormatter(formatter)
        return handler

    @classmethod
    def create_default_logger(cls, name: str) -> logging.Logger:
        """创建带默认处理器的日志记录器。"""

        logger = cls.create_logger(name)
        if not logger.handlers:
            logger.addHandler(cls.get_default_handler())
        return logger
