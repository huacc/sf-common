"""可观测性工具集。"""

from .metrics import (
    observe_fuseki_failure,
    observe_fuseki_response,
    set_fuseki_circuit_state,
)

__all__ = [
    "observe_fuseki_failure",
    "observe_fuseki_response",
    "set_fuseki_circuit_state",
]
