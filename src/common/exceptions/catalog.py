"""错误目录占位实现，统一维护业务错误码与说明。"""
from __future__ import annotations

from typing import Dict

from .codes import ErrorCode


class ErrorCatalog:
    """错误目录，提供错误码到说明的映射查询。"""

    _catalog: Dict[ErrorCode, str] = {
        ErrorCode.OK: "请求成功",
        ErrorCode.BAD_REQUEST: "请求参数校验失败",
        ErrorCode.INTERNAL_ERROR: "服务内部错误",
    }

    @classmethod
    def get_message(cls, code: ErrorCode) -> str:
        """根据错误码返回默认说明，未配置时使用通用提示。"""

        return cls._catalog.get(code, "未知错误，请联系管理员")

    @classmethod
    def register(cls, code: ErrorCode, message: str) -> None:
        """注册新的错误码说明。"""

        cls._catalog[code] = message
