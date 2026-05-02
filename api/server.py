from __future__ import annotations

from fastapi import FastAPI

from core.catalog import CommandCatalog
from core.checker import ToolChecker
from core.metrics import usage_metrics

app = FastAPI(title="Autohack Local API", version="1.0")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/catalog/stats")
def catalog_stats():
    catalog = CommandCatalog()
    cmds = catalog.get_all()
    checker = ToolChecker(catalog)
    tools = {c.get("tool_required") for c in cmds if c.get("tool_required")}
    return {
        "total": len(cmds),
        "categories": len(catalog.get_categories()),
        "safe": sum(1 for c in cmds if c.get("safe_to_run")),
        "dangerous": sum(1 for c in cmds if c.get("dangerous")),
        "tools_total": len(tools),
        "tools_ready": sum(1 for t in tools if checker.check(t)),
    }


@app.get("/catalog/search")
def search(q: str, limit: int = 20):
    catalog = CommandCatalog()
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
