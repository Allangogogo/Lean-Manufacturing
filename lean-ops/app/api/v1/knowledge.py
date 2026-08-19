"""
知识库模块（从 webapp 迁移）

提供：
- 文件系统扫描（知识库目录树）
- 知识库页面：首页 / 模块浏览 / 文件查看 / 搜索
- 文件下载 / 原始内容

注意：知识库不走 StaticFiles（中文路径 404），走专用路由。
"""

from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

# 知识库根目录 = 仓库根目录（Lean/）
# knowledge.py 位于 lean-ops/app/api/v1/，parents[4] 为仓库根
LEAN_ROOT = Path(__file__).resolve().parents[4]
print(f"[knowledge] LEAN_ROOT = {LEAN_ROOT}")

# 模块定义（与 webapp 一致，颜色用十六进制字符串避免主题依赖）
MODULES = {
    "01-精益工具知识库": {"name": "Lean Tools KB", "short_name": "Tools", "icon": "tools", "color": "#2563eb", "description": "Lean philosophy, 13 core tools, manufacturing process applications", "roles": "All"},
    "02-精益培训": {"name": "Training", "short_name": "Training", "icon": "training", "color": "#059669", "description": "Training strategy, 4-level materials, evaluation", "roles": "Training, HR"},
    "03-成熟度评估": {"name": "Maturity Assessment", "short_name": "Assessment", "icon": "assessment", "color": "#d97706", "description": "5-level maturity model, assessment tools", "roles": "Management, Lean"},
    "04-实施战略": {"name": "Implementation Strategy", "short_name": "Strategy", "icon": "strategy", "color": "#dc2626", "description": "5-phase roadmap, 3 path comparisons, 6 tools", "roles": "Management, PMO"},
    "05-项目管理": {"name": "Project Management", "short_name": "Projects", "icon": "projects", "color": "#7c3aed", "description": "Project charter, schedule, risk, performance", "roles": "PMO, PM"},
    "appendix": {"name": "Appendix", "short_name": "Appendix", "icon": "appendix", "color": "#6b7280", "description": "Glossary, references, template guides", "roles": "All"},
}

SUPPORTED_EXTENSIONS = {".md", ".docx", ".xlsx", ".pptx", ".pdf"}


def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def get_file_type_label(ext: str) -> str:
    labels = {".md": "Markdown", ".docx": "Word", ".xlsx": "Excel", ".pptx": "PPT", ".pdf": "PDF"}
    return labels.get(ext, ext.upper().lstrip("."))


def get_file_type_color(ext: str) -> str:
    colors = {".md": "#6b7280", ".docx": "#2563eb", ".xlsx": "#059669", ".pptx": "#d97706", ".pdf": "#dc2626"}
    return colors.get(ext, "#6b7280")


def scan_files(directory: Path) -> list[dict]:
    """扫描单个目录下的支持文件（不含子目录）。"""
    files = []
    if not directory.exists():
        return files
    for item in sorted(directory.iterdir()):
        if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS:
            try:
                stat = item.stat()
            except OSError:
                continue
            files.append({
                "name": item.stem,
                "filename": item.name,
                "ext": item.suffix.lower(),
                "size": stat.st_size,
                "size_formatted": format_file_size(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d"),
                "modified_timestamp": stat.st_mtime,
                "path": str(item.relative_to(LEAN_ROOT)).replace("\\", "/"),
                "type_label": get_file_type_label(item.suffix.lower()),
                "type_color": get_file_type_color(item.suffix.lower()),
            })
    return files


def scan_directory_tree() -> dict:
    """扫描整个知识库目录树（模块 → 子目录 → 文件）。"""
    tree = {}
    for module_dir, info in MODULES.items():
        module_path = LEAN_ROOT / module_dir
        if not module_path.exists():
            tree[module_dir] = {"info": info, "subdirs": {}, "root_files": [], "total_files": 0, "exists": False}
            continue
        subdirs = {}
        for sub in sorted(module_path.iterdir()):
            if sub.is_dir():
                files = scan_files(sub)
                nested_files = []
                for nested in sorted(sub.iterdir()):
                    if nested.is_dir():
                        nested_files.extend(scan_files(nested))
                all_files = files + nested_files
                if all_files:
                    subdirs[sub.name] = {
                        "name": sub.name,
                        "files": all_files,
                        "count": len(all_files),
                        "path": str(sub.relative_to(LEAN_ROOT)).replace("\\", "/"),
                    }
        root_files = scan_files(module_path)
        tree[module_dir] = {
            "info": info,
            "subdirs": subdirs,
            "root_files": root_files,
            "total_files": sum(d["count"] for d in subdirs.values()) + len(root_files),
            "exists": True,
        }
    return tree


def simplify_module(data: dict) -> dict:
    return {
        "info": data.get("info", {}),
        "subdirs": {name: {"name": s["name"], "count": s["count"], "path": s.get("path", "")}
                    for name, s in data.get("subdirs", {}).items()},
        "root_files": data.get("root_files", []),
        "total_files": data.get("total_files", 0),
        "exists": data.get("exists", False),
    }


def simplify_all_modules(tree: dict) -> dict:
    return {key: {"info": d.get("info", {}), "total_files": d.get("total_files", 0)}
            for key, d in tree.items()}


def search_files(tree: dict, query: str) -> list[dict]:
    """按文件名搜索知识库。"""
    results = []
    query_lower = query.lower()
    for module_dir, module_data in tree.items():
        for subdir_name, subdir_data in module_data.get("subdirs", {}).items():
            for f in subdir_data.get("files", []):
                match_score = 0
                if query_lower in f["name"].lower():
                    match_score += 10
                if query_lower in f["filename"].lower():
                    match_score += 5
                if match_score > 0:
                    results.append({**f, "module": module_dir, "module_name": MODULES[module_dir]["name"],
                                    "module_icon": MODULES[module_dir]["icon"], "subdir": subdir_name,
                                    "match_score": match_score})
        for f in module_data.get("root_files", []):
            if query_lower in f["name"].lower() or query_lower in f["filename"].lower():
                results.append({**f, "module": module_dir, "module_name": MODULES[module_dir]["name"],
                                "module_icon": MODULES[module_dir]["icon"], "subdir": "",
                                "match_score": 8})
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results


def setup_kb_routes(app, templates: Jinja2Templates) -> None:
    """注册知识库页面路由与 API（挂载到主 app）。"""

    @app.get("/module/{module_name:path}", response_class=HTMLResponse, include_in_schema=False)
    async def kb_module_view(request: Request, module_name: str):
        tree = scan_directory_tree()
        module = tree.get(module_name, None)
        if module is None:
            return templates.TemplateResponse(
                "kb/search.html",
                {"request": request, "query": module_name, "results": [], "result_count": 0,
                 "module_defs": MODULES, "error": f"Module '{module_name}' not found"},
            )
        return templates.TemplateResponse(
            "kb/knowledge.html",
            {"request": request, "module": simplify_module(module), "module_name": module_name,
             "module_info": MODULES.get(module_name, {}), "all_modules": simplify_all_modules(tree),
             "module_defs": MODULES},
        )

    @app.get("/file/{file_path:path}", response_class=HTMLResponse, include_in_schema=False)
    async def kb_file_view(request: Request, file_path: str):
        full_path = LEAN_ROOT / file_path
        if not full_path.exists():
            return templates.TemplateResponse(
                "kb/search.html",
                {"request": request, "query": file_path, "results": [], "result_count": 0,
                 "module_defs": MODULES, "error": f"File '{file_path}' not found"},
            )
        content = ""
        if full_path.suffix.lower() == ".md":
            try:
                content = full_path.read_text(encoding="utf-8")
            except Exception:
                content = "Cannot read file"
        parts = Path(file_path).parts
        parent_module = parts[0] if parts else ""
        return templates.TemplateResponse(
            "kb/file_view.html",
            {"request": request, "file_path": file_path, "file_name": full_path.name,
             "file_ext": full_path.suffix.lower(),
             "file_size": format_file_size(full_path.stat().st_size),
             "content": content, "parent_module": parent_module,
             "module_info": MODULES.get(parent_module, {}), "module_defs": MODULES},
        )

    @app.get("/search", response_class=HTMLResponse, include_in_schema=False)
    async def kb_search_view(request: Request, q: str = Query("", alias="q")):
        tree = scan_directory_tree()
        results = search_files(tree, q) if q else []
        return templates.TemplateResponse(
            "kb/search.html",
            {"request": request, "query": q, "results": results, "result_count": len(results),
             "module_defs": MODULES},
        )

    @app.get("/knowledge", response_class=HTMLResponse, include_in_schema=False)
    async def kb_knowledge_view(request: Request):
        tree = scan_directory_tree()
        type_counts = {"md": 0, "docx": 0, "xlsx": 0, "pptx": 0, "pdf": 0}
        for module_data in tree.values():
            for subdir_data in module_data.get("subdirs", {}).values():
                for f in subdir_data.get("files", []):
                    key = f["ext"].lstrip(".")
                    type_counts[key] = type_counts.get(key, 0) + 1
            for f in module_data.get("root_files", []):
                key = f["ext"].lstrip(".")
                type_counts[key] = type_counts.get(key, 0) + 1
        return templates.TemplateResponse(
            "kb/index.html",
            {"request": request, "modules": simplify_all_modules(tree),
             "module_defs": MODULES, "total_files": sum(m["total_files"] for m in tree.values()),
             "type_counts": type_counts},
        )

    # ---------------- KB API ----------------
    @app.get("/api/tree")
    async def api_kb_tree():
        return scan_directory_tree()

    @app.get("/api/files")
    async def api_kb_files():
        tree = scan_directory_tree()
        all_files = []
        for module_dir, module_data in tree.items():
            for subdir_name, subdir_data in module_data.get("subdirs", {}).items():
                for f in subdir_data.get("files", []):
                    all_files.append({**f, "module": module_dir, "subdir": subdir_name})
            for f in module_data.get("root_files", []):
                all_files.append({**f, "module": module_dir, "subdir": ""})
        return all_files

    @app.get("/api/search")
    async def api_kb_search(q: str = Query("")):
        tree = scan_directory_tree()
        return search_files(tree, q)

    @app.get("/api/modules")
    async def api_kb_modules():
        return MODULES

    @app.get("/download/{file_path:path}")
    async def api_kb_download(file_path: str):
        full_path = LEAN_ROOT / file_path
        if not full_path.exists() or not full_path.is_file():
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(full_path, filename=full_path.name)

    @app.get("/raw/{file_path:path}")
    async def api_kb_raw(file_path: str):
        full_path = LEAN_ROOT / file_path
        if not full_path.exists() or not full_path.is_file():
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="File not found")
        try:
            return PlainTextResponse(full_path.read_text(encoding="utf-8"))
        except Exception:
            return PlainTextResponse("Binary file", status_code=415)
