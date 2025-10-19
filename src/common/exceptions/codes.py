"""RDF 防腐层统一错误码定义。"""
from __future__ import annotations

from enum import IntEnum
from typing import NamedTuple


class ErrorCode(IntEnum):
    OK = 2000
    BAD_REQUEST = 4001
    DRY_RUN_OPTION_MISSING = 4002
    UNAUTHENTICATED = 4011
    FORBIDDEN = 4031
    NOT_FOUND = 4041
    IDEMPOTENCY_CONFLICT = 4201
    VERSION_CONFLICT = 4202
    CONTRACT_VIOLATION = 4211
    UPSTREAM_TIMEOUT = 4301
    UPSTREAM_ERROR = 4302
    INTERNAL_ERROR = 5001
    FUSEKI_CONNECT_ERROR = 5101
    FUSEKI_QUERY_ERROR = 5102
    POSTGRES_ERROR = 5103
    FUSEKI_CIRCUIT_OPEN = 5104


class ErrorSpec(NamedTuple):
    http_status: int
    default_message: str


ERROR_SPECS: dict[ErrorCode, ErrorSpec] = {
    ErrorCode.OK: ErrorSpec(200, "请求成功"),
    ErrorCode.BAD_REQUEST: ErrorSpec(400, "请求参数校验失败"),
    ErrorCode.DRY_RUN_OPTION_MISSING: ErrorSpec(400, "缺少 Dry-Run 必填选项"),
    ErrorCode.UNAUTHENTICATED: ErrorSpec(401, "未认证"),
    ErrorCode.FORBIDDEN: ErrorSpec(403, "无访问权限"),
    ErrorCode.NOT_FOUND: ErrorSpec(404, "资源不存在"),
    ErrorCode.IDEMPOTENCY_CONFLICT: ErrorSpec(409, "幂等冲突"),
    ErrorCode.VERSION_CONFLICT: ErrorSpec(409, "版本冲突"),
    ErrorCode.CONTRACT_VIOLATION: ErrorSpec(422, "契约校验失败"),
    ErrorCode.UPSTREAM_TIMEOUT: ErrorSpec(504, "上游服务超时"),
    ErrorCode.UPSTREAM_ERROR: ErrorSpec(502, "上游服务异常"),
    ErrorCode.INTERNAL_ERROR: ErrorSpec(500, "服务内部错误"),
    ErrorCode.FUSEKI_CONNECT_ERROR: ErrorSpec(500, "Fuseki 连接失败"),
    ErrorCode.FUSEKI_QUERY_ERROR: ErrorSpec(500, "Fuseki 查询失败"),
    ErrorCode.POSTGRES_ERROR: ErrorSpec(500, "PostgreSQL 操作失败"),
}


DEFAULT_ERROR_CODE = ErrorCode.INTERNAL_ERROR
