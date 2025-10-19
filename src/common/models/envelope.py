"""Unified API envelope models."""
from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.generics import GenericModel

from common.config import ConfigManager
from common.exceptions.codes import ERROR_SPECS, ErrorCode

T = TypeVar('T')


class PagingMeta(BaseModel):
    """Metadata describing pagination information."""

    model_config = ConfigDict(populate_by_name=True)

    total: int | None = None
    offset: int | None = None
    size: int | None = None
    next_offset: int | None = Field(default=None, alias='nextOffset')


class EnvelopeMeta(BaseModel):
    """Additional metadata returned alongside data payloads."""

    model_config = ConfigDict(populate_by_name=True)

    version: str = Field(default_factory=lambda: ConfigManager.current().contract.envelope_version)
    paging: PagingMeta | None = None


class Envelope(GenericModel, Generic[T]):
    """Standard response envelope wrapping business data with metadata."""

    model_config = ConfigDict(populate_by_name=True)

    code: int
    message: str
    data: T | None = None
    trace_id: str = Field(alias='traceId')
    meta: EnvelopeMeta | None = None

    @classmethod
    def success(
        cls,
        *,
        data: T | None = None,
        message: str | None = None,
        trace_id: str,
        meta: EnvelopeMeta | None = None,
    ) -> 'Envelope[T]':
        """Create a success envelope."""

        spec = ERROR_SPECS[ErrorCode.OK]
        return cls(
            code=int(ErrorCode.OK),
            message=message or spec.default_message,
            data=data,
            trace_id=trace_id,
            meta=meta,
        )

    @classmethod
    def from_error(
        cls,
        code: ErrorCode,
        *,
        message: str,
        trace_id: str,
        meta: EnvelopeMeta | None = None,
        data: Any | None = None,
    ) -> 'Envelope[Any]':
        """Create an envelope from an error code."""

        return cls(code=int(code), message=message, data=data, trace_id=trace_id, meta=meta)

    def json_ready(self) -> dict[str, Any]:
        """Return a JSON-serialisable dictionary representation."""

        return self.model_dump(by_alias=True, exclude_none=True)
