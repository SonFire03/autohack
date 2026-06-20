from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI

from core.catalog import CommandCatalog
from core.checker import ToolChecker
from core.metrics import usage_metrics

app = FastAPI(title="Autohack Local API", version="1.0")


@lru_cache(maxsize=1)
def _catalog() -> CommandCatalog:
    return CommandCatalog()


@lru_cache(maxsize=1)
def _checker() -> ToolChecker:
    return ToolChecker(_catalog())


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/catalog/stats")
def catalog_stats():
    catalog = _catalog()
    cmds = catalog.get_all()
    tools = {c.get("tool_required") for c in cmds if c.get("tool_required")}
    return {
        "total": len(cmds),
        "categories": len(catalog.get_categories()),
        "safe": sum(1 for c in cmds if c.get("safe_to_run")),
        "dangerous": sum(1 for c in cmds if c.get("dangerous")),
        "tools_total": len(tools),
        "tools_ready": sum(1 for t in tools if _checker().check(t)),
    }


@app.get("/catalog/search")
def search(q: str, limit: int = 20):
    catalog = _catalog()
    results = catalog.search(q)[: max(1, min(limit, 200))]
    return [
        {
            "id": r.get("id"),
            "name": r.get("name"),
            "category": r.get("category"),
            "tool": r.get("tool_required"),
            "dangerous": bool(r.get("dangerous")),
        }
        for r in results
    ]


@app.get("/metrics")
def metrics():
    return usage_metrics()
