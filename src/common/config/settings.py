from __future__ import annotations

from typing import Literal

from pydantic import (
    AnyHttpUrl,
    AnyUrl,
    BaseModel,
    ConfigDict,
    Field,
    PostgresDsn,
    field_validator,
)


class AppConfig(BaseModel):

    model_config = ConfigDict(extra="ignore")

    name: str = Field(default="SemanticForge")
    env: Literal["development", "testing", "production"] = Field(default="development")
    port: int = Field(default=8000, ge=1, le=65535)
    debug: bool = Field(default=True)


class CorsConfig(BaseModel):

    model_config = ConfigDict(extra="ignore")

    origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    @field_validator("origins", mode="before")
    @classmethod
    def _split_origins(cls, value: list[str] | str) -> list[str]:

        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value


class CredentialsConfig(BaseModel):

    model_config = ConfigDict(extra="ignore")

    username: str | None = None
    password: str | None = None


class TimeoutConfig(BaseModel):

    model_config = ConfigDict(extra="ignore")

    default: int = Field(default=30, ge=1, le=600)
    max: int = Field(default=120, ge=1, le=3600)


class RetryConfig(BaseModel):

    model_config = ConfigDict(extra="ignore")

    max_attempts: int = Field(default=3, ge=0, le=10)
    backoff_seconds: float = Field(default=0.5, ge=0.0, le=30.0)
    backoff_multiplier: float = Field(default=2.0, ge=1.0, le=10.0)
    jitter_seconds: float | None = Field(default=0.1, ge=0.0, le=10.0)


class CircuitBreakerConfig(BaseModel):

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    failure_threshold: int = Field(default=5, ge=1, le=20, alias="failureThreshold")
    recovery_timeout: float = Field(default=30.0, ge=1.0, le=600.0, alias="recoveryTimeout")
    record_timeout_only: bool = Field(default=False, alias="recordTimeoutOnly")


class GraphProjectionProfileConfig(BaseModel):

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    edge_predicates: list[str] = Field(default_factory=list, alias="edgePredicates")
    node_types: list[str] = Field(default_factory=list, alias="nodeTypes")
    include_literals: bool = Field(default=False, alias="includeLiterals")
    flatten_reification: bool = Field(default=True, alias="flattenReification")
    directed: bool = Field(default=True)
    weight_predicate: str | None = Field(default=None, alias="weightPredicate")
    limit: int = Field(default=1000, ge=1, le=20000)
    description: str | None = None


class GraphAlgorithmLimitConfig(BaseModel):

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    allowed_algorithms: list[str] = Field(
        default_factory=lambda: ["pagerank", "shortest_path", "khop"],
        alias="allowedAlgorithms",
    )
    max_khop: int = Field(default=4, ge=1, le=10, alias="maxKhops")
    max_nodes: int = Field(default=2000, ge=1, le=20000, alias="maxNodes")
    max_edges: int = Field(default=5000, ge=1, le=50000, alias="maxEdges")
    default_timeout: int = Field(default=30, ge=1, le=600, alias="defaultTimeout")
    max_timeout: int = Field(default=120, ge=1, le=3600, alias="maxTimeout")


class GraphConfig(BaseModel):

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    projection_profiles: dict[str, GraphProjectionProfileConfig] = Field(
        default_factory=dict,
        alias="projectionProfiles",
    )
    algorithm: GraphAlgorithmLimitConfig = Field(default_factory=GraphAlgorithmLimitConfig)


class GraphNamingConfig(BaseModel):

    model_config = ConfigDict(extra="ignore")

    graph_format: str = Field(default="urn:sf:{model}:{version}:{env}")
    snapshot_format: str = Field(default="urn:sf:{model}:{version}:{env}:snapshot:{ts}")


class RDFConfig(BaseModel):

    model_config = ConfigDict(extra="ignore")

    endpoint: AnyHttpUrl = Field(default="http://192.168.0.119:3030")
    dataset: str = Field(default="semantic_forge_test")
    auth: CredentialsConfig = Field(default_factory=CredentialsConfig)
    timeout: TimeoutConfig = Field(default_factory=TimeoutConfig)
    retries: RetryConfig = Field(default_factory=RetryConfig)
    circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig, alias="circuitBreaker")
    naming: GraphNamingConfig = Field(default_factory=GraphNamingConfig)

    @field_validator("dataset")
    @classmethod
    def _validate_dataset(cls, value: str) -> str:

        if not value:
            raise ValueError("dataset name must not be empty")
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
        if any(ch not in allowed for ch in value):
            raise ValueError("dataset may only contain alphanumerics, '-' or '_'")
        return value


class PostgresConfig(BaseModel):

    model_config = ConfigDict(extra="ignore", populate_by_name=True, protected_namespaces=())

    dsn: PostgresDsn = Field(default="postgresql://postgres:123456@192.168.0.119:5432/semantic_forge")
    schema_: str = Field(default="rdf_acl", alias="schema")
    migrations_table: str = Field(default="rdf_acl_migrations")

    @property
    def schema(self) -> str:

        return self.schema_


class RedisConfig(BaseModel):

    model_config = ConfigDict(extra="ignore")

    url: AnyUrl = Field(default="redis://:123456@192.168.0.119:6379/0")
    namespace: str = Field(default="semanticforge")


class QdrantConfig(BaseModel):

    model_config = ConfigDict(extra="ignore")

    http_url: AnyHttpUrl = Field(default="http://192.168.0.119:6333")
    grpc_url: AnyUrl | None = Field(default="grpc://192.168.0.119:6334")
    timeout: TimeoutConfig = Field(default_factory=TimeoutConfig)


class LoggingConfig(BaseModel):

    model_config = ConfigDict(extra="ignore")

    level: str = Field(default="INFO")
    format: Literal["json", "text"] = Field(default="json")
    json_indent: int | None = Field(default=None, ge=0, le=4)


class PaginationConfig(BaseModel):

    model_config = ConfigDict(extra="ignore")

    default_size: int = Field(default=50, ge=1, le=500)
    max_size: int = Field(default=500, ge=50, le=2000)


class ContractConfig(BaseModel):

    model_config = ConfigDict(extra="ignore")

    envelope_version: str = Field(default="v1")
    default_timeout: int = Field(default=30, ge=1, le=600)
    pagination: PaginationConfig = Field(default_factory=PaginationConfig)


class SecurityConfig(BaseModel):

    model_config = ConfigDict(extra="ignore")

    trace_header: str = Field(default="X-Trace-Id")
    client_header: str = Field(default="X-Client-Id")
    idempotency_header: str = Field(default="Idempotency-Key")
    require_api_key: bool = Field(default=False)
    api_key_header: str = Field(default="X-API-Key")


class Settings(BaseModel):

    model_config = ConfigDict(extra="ignore")

    app: AppConfig = Field(default_factory=AppConfig)
    cors: CorsConfig = Field(default_factory=CorsConfig)
    rdf: RDFConfig = Field(default_factory=RDFConfig)
    graph: GraphConfig = Field(default_factory=GraphConfig)
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    qdrant: QdrantConfig = Field(default_factory=QdrantConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    contract: ContractConfig = Field(default_factory=ContractConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)


