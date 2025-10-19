"""FastAPI 异常处理注册，统一输出 Envelope。"""
from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from common.config import ConfigManager
from common.models.envelope import Envelope, EnvelopeMeta

from .api import APIError
from .codes import ERROR_SPECS, ErrorCode

_HTTP_ERROR_MAP: dict[int, ErrorCode] = {
    400: ErrorCode.BAD_REQUEST,
    401: ErrorCode.UNAUTHENTICATED,
    403: ErrorCode.FORBIDDEN,
    404: ErrorCode.NOT_FOUND,
    409: ErrorCode.IDEMPOTENCY_CONFLICT,
    422: ErrorCode.CONTRACT_VIOLATION,
    502: ErrorCode.UPSTREAM_ERROR,
    504: ErrorCode.UPSTREAM_TIMEOUT,
}


def _ensure_trace_id(request: Request) -> str:
    """保证请求上下文携带 trace_id。"""

    security = ConfigManager.current().security
    trace_header = security.trace_header
    trace_id = getattr(request.state, 'trace_id', None) or request.headers.get(trace_header)
    if not trace_id:
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id
    return trace_id


def _make_response(content: Envelope[Any], status_code: int, trace_id: str) -> JSONResponse:
    """构造带统一响应头的 JSONResponse。"""

    security = ConfigManager.current().security
    response = JSONResponse(status_code=status_code, content=content.json_ready())
    response.headers[security.trace_header] = trace_id
    return response


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """处理业务抛出的 APIError。"""

    trace_id = _ensure_trace_id(request)
    meta = EnvelopeMeta()
    data = exc.details or None
    envelope = Envelope.from_error(exc.code, message=exc.message, trace_id=trace_id, meta=meta, data=data)
    return _make_response(envelope, exc.http_status, trace_id)


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """处理 FastAPI 层面的请求校验异常。"""

    trace_id = _ensure_trace_id(request)
    flattened = exc.errors()
    envelope = Envelope.from_error(
        ErrorCode.BAD_REQUEST,
        message="请求参数校验失败",
        trace_id=trace_id,
        data={'errors': flattened},
        meta=EnvelopeMeta(),
    )
    status_code = ERROR_SPECS[ErrorCode.BAD_REQUEST].http_status
    return _make_response(envelope, status_code, trace_id)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """处理 Starlette 层抛出的 HTTPException。"""

    trace_id = _ensure_trace_id(request)
    code = _HTTP_ERROR_MAP.get(exc.status_code, ErrorCode.INTERNAL_ERROR)
    message = exc.detail or ERROR_SPECS.get(code, ERROR_SPECS[ErrorCode.INTERNAL_ERROR]).default_message
    envelope = Envelope.from_error(code, message=message, trace_id=trace_id, meta=EnvelopeMeta())
    return _make_response(envelope, exc.status_code, trace_id)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """兜底处理未捕获异常。"""

    trace_id = _ensure_trace_id(request)
    envelope = Envelope.from_error(
        ErrorCode.INTERNAL_ERROR,
        message=ERROR_SPECS[ErrorCode.INTERNAL_ERROR].default_message,
        trace_id=trace_id,
        data={'error': str(exc)},
        meta=EnvelopeMeta(),
    )
    status_code = ERROR_SPECS[ErrorCode.INTERNAL_ERROR].http_status
    return _make_response(envelope, status_code, trace_id)


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器。"""

    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

