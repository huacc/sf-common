"""异常工具聚合，对外输出统一接口。"""
from .api import APIError, ContractViolation, ExternalServiceError
from .catalog import ErrorCatalog
from .codes import DEFAULT_ERROR_CODE, ERROR_SPECS, ErrorCode
from .handlers import register_exception_handlers

__all__ = [
    "APIError",
    "ContractViolation",
    "ExternalServiceError",
    "ErrorCatalog",
    "ErrorCode",
    "DEFAULT_ERROR_CODE",
    "ERROR_SPECS",
    "register_exception_handlers",
]
