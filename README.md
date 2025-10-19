# sf-common

SemanticForge 公共库：配置、异常、日志、观测、模型、工具。

- 包提供 `common.*` 命名空间，作为其他库/服务的基础依赖。
- 配置查找默认指向仓库根下的 `config/` 目录（兼容 monorepo 行为）。

开发：

```
cd projects/sf-common
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -e .
```

