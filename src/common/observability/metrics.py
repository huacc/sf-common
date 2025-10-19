"""Prometheus 指标埋点工具。"""
from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

# 这里使用全局注册表，配合 Prometheus 默认采集方式即可完成抓取。
_FUSEKI_LATENCY = Histogram(
    'sf_fuseki_request_duration_seconds',
    'Fuseki 请求耗时分布，单位秒',
    labelnames=('operation', 'status'),
    buckets=(0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0),
)

_FUSEKI_TOTAL = Counter(
    'sf_fuseki_requests_total',
    'Fuseki 请求总次数',
    labelnames=('operation', 'status'),
)

_FUSEKI_FAILURE = Counter(
    'sf_fuseki_request_failures_total',
    'Fuseki 请求失败次数',
    labelnames=('operation', 'reason'),
)

_FUSEKI_CIRCUIT = Gauge(
    'sf_fuseki_circuit_breaker_state',
    'Fuseki 熔断器状态，1 表示打开，0 表示关闭',
    labelnames=('operation',),
)

# 初始化 Gauge，确保默认状态为关闭。
_FUSEKI_CIRCUIT.labels(operation='query').set(0)
_FUSEKI_CIRCUIT.labels(operation='update').set(0)


def observe_fuseki_response(operation: str, status_code: int, duration_seconds: float) -> None:
    """记录 Fuseki 请求成功或失败后的指标信息。"""

    label_status = str(status_code)
    _FUSEKI_TOTAL.labels(operation=operation, status=label_status).inc()
    _FUSEKI_LATENCY.labels(operation=operation, status=label_status).observe(duration_seconds)


def observe_fuseki_failure(operation: str, reason: str) -> None:
    """记录 Fuseki 请求失败原因，用于计算错误率。"""

    _FUSEKI_FAILURE.labels(operation=operation, reason=reason).inc()


def set_fuseki_circuit_state(operation: str, opened: bool) -> None:
    """更新熔断器状态指标。"""

    _FUSEKI_CIRCUIT.labels(operation=operation).set(1 if opened else 0)
