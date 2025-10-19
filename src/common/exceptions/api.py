"""应用层异常定义，统一携带错误码与扩展信息。"""
from __future__ import annotations

from typing import Any

from .codes import DEFAULT_ERROR_CODE, ERROR_SPECS, ErrorCode


class APIError(Exception):
    """领域通用异常，封装错误码、消息与附加信息。"""

    def __init__(
        self,
        code: ErrorCode,
        message: str | None = None,
        *,
        details: dict[str, Any] | None = None,
        http_status: int | None = None,
    ) -> None:
        spec = ERROR_SPECS.get(code, ERROR_SPECS[DEFAULT_ERROR_CODE])
        self.code = code
        self.message = message or spec.default_message
        self.details = details or {}
        self.http_status = http_status or spec.http_status
        super().__init__(self.message)

    def as_dict(self) -> dict[str, Any]:
        """以字典形式返回异常信息，便于统一包装响应。"""

        return {"code": int(self.code), "message": self.message, "details": self.details}


class ExternalServiceError(APIError):
    """上游服务调用失败时抛出的异常。"""

    def __init__(self, code: ErrorCode, message: str | None = None, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(code, message, details=details)


class ContractViolation(APIError):
    """请求负载违反契约约束时抛出的异常。"""

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(ErrorCode.CONTRACT_VIOLATION, message, details=details)
