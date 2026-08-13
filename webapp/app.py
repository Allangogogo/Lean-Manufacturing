"""
Lean Manufacturing Knowledge Base - Web Application
Phase 1-3: Knowledge Base + Lean2.0 + Pillars + Automation + TPM + 5S/Kaizen + Projects + Training + Best Practices
"""

from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
import os
import re
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional

app = FastAPI(title="Lean Manufacturing System", version="3.0.0")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")

jinja2_env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=True,
    cache_size=0,
)
templates = Jinja2Templates(env=jinja2_env)

LEAN_ROOT = Path(__file__).parent.parent
DB_PATH = str(LEAN_ROOT / "lean-ops" / "data" / "leanops.db")
templates_dir = "templates"

# ==================== Module Definitions ====================
MODULES = {
    "01-精益工具知识库": {"name": "Lean Tools KB", "short_name": "Tools", "icon": "🔧", "color": "#2563eb", "description": "Lean philosophy, 13 core tools, fastener industry applications", "roles": "All"},
    "02-精益培训": {"name": "Training", "short_name": "Training", "icon": "📚", "color": "#059669", "description": "Training strategy, 4-level materials, evaluation", "roles": "Training, HR"},
    "03-成熟度评估": {"name": "Maturity Assessment", "short_name": "Assessment", "icon": "📊", "color": "#d97706", "description": "5-level maturity model, assessment tools", "roles": "Management, Lean"},
    "04-实施战略": {"name": "Implementation Strategy", "short_name": "Strategy", "icon": "🎯", "color": "#dc2626", "description": "5-phase roadmap, 3 path comparisons, 6 tools", "roles": "Management, PMO"},
    "05-项目管理": {"name": "Project Management", "short_name": "Projects", "icon": "📋", "color": "#7c3aed", "description": "Project charter, schedule, risk, performance", "roles": "PMO, PM"},
    "appendix": {"name": "Appendix", "short_name": "Appendix", "icon": "📖", "color": "#6b7280", "description": "Glossary, references, template guides", "roles": "All"},
}

SUPPORTED_EXTENSIONS = {".md", ".docx", ".xlsx", ".pptx", ".pdf"}

# ==================== DB Helper ====================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== File Scanning Helpers ====================
def format_file_size(size_bytes):
    if size_bytes < 1024: return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024: return f"{size_bytes / 1024:.1f} KB"
    else: return f"{size_bytes / (1024 * 1024):.1f} MB"

def get_file_type_label(ext):
    labels = {".md": "Markdown", ".docx": "Word", ".xlsx": "Excel", ".pptx": "PPT", ".pdf": "PDF"}
    return labels.get(ext, ext.upper().lstrip("."))

def get_file_type_color(ext):
    colors = {".md": "#6b7280", ".docx": "#2563eb", ".xlsx": "#059669", ".pptx": "#d97706", ".pdf": "#dc2626"}
    return colors.get(ext, "#6b7280")

def scan_files(directory):
    files = []
    if not directory.exists(): return files
    for item in sorted(directory.iterdir()):
        if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS:
            stat = item.stat()
            files.append({
                "name": item.stem, "filename": item.name, "ext": item.suffix.lower(),
                "size": stat.st_size, "size_formatted": format_file_size(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d"),
                "modified_timestamp": stat.st_mtime,
                "path": str(item.relative_to(LEAN_ROOT)).replace("\\", "/"),
                "type_label": get_file_type_label(item.suffix.lower()),
                "type_color": get_file_type_color(item.suffix.lower()),
            })
    return files

def scan_directory_tree():
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
                    if nested.is_dir(): nested_files.extend(scan_files(nested))
                all_files = files + nested_files
                if all_files:
                    subdirs[sub.name] = {"name": sub.name, "files": all_files, "count": len(all_files), "path": str(sub.relative_to(LEAN_ROOT)).replace("\\", "/")}
        root_files = scan_files(module_path)
        tree[module_dir] = {"info": info, "subdirs": subdirs, "root_files": root_files, "total_files": sum(d["count"] for d in subdirs.values()) + len(root_files), "exists": True}
    return tree

def simplify_module(data):
    return {"info": data.get("info", {}), "subdirs": {name: {"name": s["name"], "count": s["count"], "path": s.get("path", "")} for name, s in data.get("subdirs", {}).items()}, "root_files": data.get("root_files", []), "total_files": data.get("total_files", 0), "exists": data.get("exists", False)}

def simplify_all_modules(tree):
    return {key: {"info": d.get("info", {}), "total_files": d.get("total_files", 0)} for key, d in tree.items()}

def search_files(tree, query):
    results = []
    query_lower = query.lower()
    for module_dir, module_data in tree.items():
        for subdir_name, subdir_data in module_data.get("subdirs", {}).items():
            for f in subdir_data.get("files", []):
                match_score = 0
                if query_lower in f["name"].lower(): match_score += 10
                if query_lower in f["filename"].lower(): match_score += 5
                if match_score > 0:
                    results.append({**f, "module": module_dir, "module_name": MODULES[module_dir]["name"], "module_icon": MODULES[module_dir]["icon"], "subdir": subdir_name, "match_score": match_score})
        for f in module_data.get("root_files", []):
            if query_lower in f["name"].lower() or query_lower in f["filename"].lower():
                results.append({**f, "module": module_dir, "module_name": MODULES[module_dir]["name"], "module_icon": MODULES[module_dir]["icon"], "subdir": "", "match_score": 8})
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results

def read_template(name):
    with open(os.path.join(templates_dir, name), encoding="utf-8") as f:
        return f.read()

# ==================== KB Routes ====================
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    tree = scan_directory_tree()
    total_files = sum(m["total_files"] for m in tree.values())
    type_counts = {"md": 0, "docx": 0, "xlsx": 0, "pptx": 0, "pdf": 0}
    for module_data in tree.values():
        for subdir_data in module_data.get("subdirs", {}).values():
            for f in subdir_data.get("files", []):
                ext_key = f["ext"].lstrip(".")
                type_counts[ext_key] = type_counts.get(ext_key, 0) + 1
        for f in module_data.get("root_files", []):
            ext_key = f["ext"].lstrip(".")
            type_counts[ext_key] = type_counts.get(ext_key, 0) + 1

    conn = get_db()
    # Lean 2.0 checklist counts per dimension
    dim_file_counts = {"O": {"count": 0}, "D": {"count": 0}, "G": {"count": 0}, "R": {"count": 0}, "H": {"count": 0}}
    try:
        for row in conn.execute("SELECT dimension_code, COUNT(*) as cnt FROM lean20_checklist_items GROUP BY dimension_code").fetchall():
            dim_file_counts[row["dimension_code"]] = {"count": row["cnt"]}
    except:
        pass

    # Latest Lean 2.0 assessment scores
    latest_assessment = None
    dim_scores = []
    try:
        a = conn.execute("SELECT * FROM lean20_assessments ORDER BY assessment_date DESC LIMIT 1").fetchone()
        if a:
            latest_assessment = dict(a)
            scores = conn.execute("SELECT dimension_code, level, weight, weighted_score FROM lean20_dimension_scores WHERE assessment_id=? ORDER BY dimension_code", (a["id"],)).fetchall()
            dim_scores = [dict(s) for s in scores]
    except:
        pass

    # Pillars
    pillars = []
    try:
        pillars = [dict(r) for r in conn.execute("SELECT * FROM value_pillars ORDER BY sort_order").fetchall()]
    except:
        pass

    # Automation maturity
    auto_maturity = None
    try:
        auto_maturity = conn.execute("SELECT * FROM automation_maturity ORDER BY created_at DESC LIMIT 1").fetchone()
        if auto_maturity:
            auto_maturity = dict(auto_maturity)
    except:
        pass

    # Counts for dashboard cards
    project_count = conn.execute("SELECT COUNT(*) as c FROM projects").fetchone()["c"]
    tpm_equipment_count = conn.execute("SELECT COUNT(*) as c FROM tpm_equipment").fetchone()["c"]
    five_s_area_count = conn.execute("SELECT COUNT(*) as c FROM five_s_areas").fetchone()["c"]
    kaizen_count = conn.execute("SELECT COUNT(*) as c FROM kaizen_proposals").fetchone()["c"]
    training_count = conn.execute("SELECT COUNT(*) as c FROM training_sessions").fetchone()["c"]
    best_practice_count = conn.execute("SELECT COUNT(*) as c FROM best_practices").fetchone()["c"]
    tpm_fault_count = conn.execute("SELECT COUNT(*) as c FROM tpm_faults WHERE status != 'closed'").fetchone()["c"]
    kaizen_approved = conn.execute("SELECT COUNT(*) as c FROM kaizen_proposals WHERE status='approved'").fetchone()["c"]
    project_active = conn.execute("SELECT COUNT(*) as c FROM projects WHERE status IN ('planning','in_progress')").fetchone()["c"]
    training_upcoming = conn.execute("SELECT COUNT(*) as c FROM training_sessions WHERE status='scheduled'").fetchone()["c"]

    conn.close()

    return templates.TemplateResponse(request, "index.html", {
        "modules": simplify_all_modules(tree),
        "module_defs": MODULES,
        "total_files": total_files,
        "type_counts": type_counts,
        "dim_file_counts": dim_file_counts,
        "latest_assessment": latest_assessment,
        "dim_scores": dim_scores,
        "pillars": pillars,
        "auto_maturity": auto_maturity,
        "project_count": project_count,
        "tpm_equipment_count": tpm_equipment_count,
        "five_s_area_count": five_s_area_count,
        "kaizen_count": kaizen_count,
        "training_count": training_count,
        "best_practice_count": best_practice_count,
        "tpm_fault_count": tpm_fault_count,
        "kaizen_approved": kaizen_approved,
        "project_active": project_active,
        "training_upcoming": training_upcoming,
    })

@app.get("/module/{module_name:path}", response_class=HTMLResponse)
async def module_view(request: Request, module_name: str):
    tree = scan_directory_tree()
    module = tree.get(module_name, None)
    if module is None:
        return templates.TemplateResponse(request, "search.html", {"query": module_name, "results": [], "result_count": 0, "module_defs": MODULES, "error": f"Module '{module_name}' not found"})
    return templates.TemplateResponse(request, "knowledge.html", {"module": simplify_module(module), "module_name": module_name, "module_info": MODULES.get(module_name, {}), "all_modules": simplify_all_modules(tree), "module_defs": MODULES})

@app.get("/file/{file_path:path}", response_class=HTMLResponse)
async def file_view(request: Request, file_path: str):
    full_path = LEAN_ROOT / file_path
    if not full_path.exists():
        return templates.TemplateResponse(request, "search.html", {"query": file_path, "results": [], "result_count": 0, "module_defs": MODULES, "error": f"File '{file_path}' not found"})
    content = ""
    if full_path.suffix.lower() == ".md":
        try: content = full_path.read_text(encoding="utf-8")
        except: content = "Cannot read file"
    parts = Path(file_path).parts
    parent_module = parts[0] if parts else ""
    return templates.TemplateResponse(request, "file_view.html", {"file_path": file_path, "file_name": full_path.name, "file_ext": full_path.suffix.lower(), "file_size": format_file_size(full_path.stat().st_size), "content": content, "parent_module": parent_module, "module_info": MODULES.get(parent_module, {}), "module_defs": MODULES})

@app.get("/search", response_class=HTMLResponse)
async def search_view(request: Request, q: str = Query("", alias="q")):
    tree = scan_directory_tree()
    results = search_files(tree, q) if q else []
    return templates.TemplateResponse(request, "search.html", {"query": q, "results": results, "result_count": len(results), "module_defs": MODULES})

# ==================== KB API ====================
@app.get("/api/tree")
async def api_tree(): return scan_directory_tree()

@app.get("/api/files")
async def api_files(module: Optional[str] = Query(None), subdir: Optional[str] = Query(None)):
    tree = scan_directory_tree()
    if module and module in tree:
        if subdir:
            subdir_data = tree[module]["subdirs"].get(subdir, {})
            return {"files": subdir_data.get("files", []), "count": subdir_data.get("count", 0)}
        return {"root_files": tree[module]["root_files"], "subdirs": {k: {"name": v["name"], "count": v["count"]} for k, v in tree[module]["subdirs"].items()}, "total_files": tree[module]["total_files"]}
    return {"error": "Module not found"}

@app.get("/api/search")
async def api_search(q: str = Query("")):
    tree = scan_directory_tree()
    results = search_files(tree, q)
    return {"query": q, "results": results, "count": len(results)}

@app.get("/api/modules")
async def api_modules():
    tree = scan_directory_tree()
    result = {}
    for key, info in MODULES.items():
        module_data = tree.get(key, {})
        result[key] = {**info, "total_files": module_data.get("total_files", 0), "exists": module_data.get("exists", False)}
    return result

@app.get("/download/{file_path:path}")
async def download_file(file_path: str):
    full_path = LEAN_ROOT / file_path
    if full_path.exists() and full_path.is_file():
        return FileResponse(full_path, filename=full_path.name, media_type="application/octet-stream")
    return {"error": "File not found"}

@app.get("/raw/{file_path:path}")
async def raw_file(file_path: str):
    full_path = LEAN_ROOT / file_path
    if full_path.exists() and full_path.suffix.lower() == ".md":
        try:
            content = full_path.read_text(encoding="utf-8")
            return PlainTextResponse(content)
        except: return PlainTextResponse("Cannot read file", status_code=500)
    return PlainTextResponse("File not found", status_code=404)

# ==================== Lean 2.0 Assessment API ====================
@app.get("/api/v1/lean20/latest")
def api_lean20_latest():
    conn = get_db()
    try:
        a = conn.execute("SELECT * FROM lean20_assessments ORDER BY assessment_date DESC LIMIT 1").fetchone()
        if not a:
            return {"has_data": False, "assessment": None, "dimension_scores": []}
        scores = [dict(s) for s in conn.execute(
            "SELECT dimension_code, level, weight, weighted_score FROM lean20_dimension_scores WHERE assessment_id=? ORDER BY dimension_code",
            (a["id"],)
        ).fetchall()]
        assessment = dict(a)
        assessment["dimension_scores"] = scores
        return {"has_data": True, "assessment_id": a["id"], "assessment": assessment, "dimension_scores": scores}
    finally:
        conn.close()

@app.get("/api/v1/lean20/benchmark")
def api_lean20_benchmark():
    conn = get_db()
    try:
        rows = conn.execute("SELECT a.id, a.assessment_date, a.composite_index, a.overall_level, s.dimension_code, s.level, s.weighted_score FROM lean20_assessments a LEFT JOIN lean20_dimension_scores s ON a.id=s.assessment_id ORDER BY a.assessment_date, s.dimension_code").fetchall()
        if not rows:
            return {"industry_avg": {}, "best": None}
        dim_scores = {}
        for r in rows:
            dc = r["dimension_code"]
            if dc:
                dim_scores.setdefault(dc, []).append(r["level"])
        industry_avg = {dc: round(sum(v)/len(v), 2) for dc, v in dim_scores.items()}
        best = conn.execute("SELECT * FROM lean20_assessments ORDER BY composite_index DESC LIMIT 1").fetchone()
        return {"industry_avg": industry_avg, "best": dict(best) if best else None, "leader": dict(best) if best else None}
    finally:
        conn.close()

@app.get("/api/v1/lean20/reassessment-suggestions")
def api_lean20_suggestions():
    conn = get_db()
    try:
        a = conn.execute("SELECT * FROM lean20_assessments ORDER BY assessment_date DESC LIMIT 1").fetchone()
        if not a:
            return {"suggestions": []}
        scores = conn.execute("SELECT dimension_code, level, weight FROM lean20_dimension_scores WHERE assessment_id=? ORDER BY level ASC", (a["id"],)).fetchall()
        suggestions = []
        dim_names = {"O": "Operations", "D": "Digital", "G": "Green", "R": "Resilience", "H": "Human-centric"}
        for s in scores:
            dc = s["dimension_code"]
            level = s["level"]
            if level <= 2.0:
                suggestions.append({"dimension": dc, "dimension_name": dim_names.get(dc, dc), "current_level": level, "target_level": 3.0, "priority": "high", "gap": round(3.0 - level, 1)})
            elif level <= 3.0:
                suggestions.append({"dimension": dc, "dimension_name": dim_names.get(dc, dc), "current_level": level, "target_level": 4.0, "priority": "medium", "gap": round(4.0 - level, 1)})
            else:
                suggestions.append({"dimension": dc, "dimension_name": dim_names.get(dc, dc), "current_level": level, "target_level": 5.0, "priority": "low", "gap": round(5.0 - level, 1)})
        return {"assessment_id": a["id"], "suggestions": suggestions}
    finally:
        conn.close()

@app.get("/api/v1/lean20/checklist")
def api_lean20_checklist_all():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM lean20_checklist_items ORDER BY dimension_code, sort_order").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/lean20/report/{aid}")
def api_lean20_report(aid: int):
    conn = get_db()
    try:
        a = conn.execute("SELECT * FROM lean20_assessments WHERE id=?", (aid,)).fetchone()
        if not a:
            return {"error": "Not found"}
        scores = conn.execute("SELECT * FROM lean20_dimension_scores WHERE assessment_id=?", (aid,)).fetchall()
        responses = conn.execute("SELECT r.*, i.item_name, i.dimension_code FROM lean20_checklist_responses r LEFT JOIN lean20_checklist_items i ON r.item_id=i.id WHERE r.assessment_id=?", (aid,)).fetchall()
        dim_summary = {}
        for s in scores:
            dc = s["dimension_code"]
            notes = s["notes"] if "notes" in s.keys() else ""
            dim_summary[dc] = {"level": s["level"], "weight": s["weight"], "weighted_score": s["weighted_score"], "notes": notes}
        return {"assessment": dict(a), "scores": [dict(r) for r in scores], "dimension_summary": dim_summary, "responses": [dict(r) for r in responses]}
    finally:
        conn.close()

@app.post("/api/v1/lean20/assessments/checklist")
async def api_lean20_submit_checklist(request: Request):
    body = await request.json()
    conn = get_db()
    try:
        cur = conn.execute("INSERT INTO lean20_assessments (assessment_date, factory_id, status, composite_index, created_at) VALUES (?, ?, 'completed', ?, datetime('now'))",
            (body.get("assessment_date", datetime.now().strftime("%Y-%m-%d")), body.get("factory_id", 1), body.get("composite_index", 0)))
        aid = cur.lastrowid
        for score in body.get("scores", []):
            conn.execute("INSERT INTO lean20_dimension_scores (assessment_id, dimension_code, level, weight, weighted_score) VALUES (?, ?, ?, ?, ?)",
                (aid, score["dimension_code"], score["level"], score.get("weight", 0.2), score.get("weighted_score", 0)))
        for resp in body.get("responses", []):
            conn.execute("INSERT INTO lean20_checklist_responses (assessment_id, item_id, score, evidence) VALUES (?, ?, ?, ?)",
                (aid, resp["item_id"], resp.get("score", 0), resp.get("evidence", "")))
        conn.commit()
        return {"id": aid, "status": "created"}
    finally:
        conn.close()

@app.get("/api/v1/lean20/dimensions")
def api_lean20_dimensions():
    conn = get_db()
    try:
        rows = conn.execute("SELECT dimension_code, COUNT(*) as qcount FROM lean20_checklist_items GROUP BY dimension_code ORDER BY dimension_code").fetchall()
        return [{"dimension": r["dimension_code"], "question_count": r["qcount"]} for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/lean20/checklist/{dimension}")
def api_lean20_checklist(dimension: str):
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM lean20_checklist_items WHERE dimension_code=? ORDER BY sort_order", (dimension,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/lean20/assessments")
def api_lean20_assessments():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM lean20_assessments ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/lean20/assessments/{aid}")
def api_lean20_assessment_detail(aid: int):
    conn = get_db()
    try:
        a = conn.execute("SELECT * FROM lean20_assessments WHERE id=?", (aid,)).fetchone()
        if not a: return {"error": "Not found"}
        scores = conn.execute("SELECT * FROM lean20_dimension_scores WHERE assessment_id=?", (aid,)).fetchall()
        responses = conn.execute("SELECT * FROM lean20_checklist_responses WHERE assessment_id=?", (aid,)).fetchall()
        return {"assessment": dict(a), "scores": [dict(r) for r in scores], "responses": [dict(r) for r in responses]}
    finally:
        conn.close()

@app.post("/api/v1/lean20/assessments")
async def api_lean20_create_assessment(request: Request):
    body = await request.json()
    conn = get_db()
    try:
        cur = conn.execute("INSERT INTO lean20_assessments (factory_id, assessor_name, status, total_score, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            (body.get("factory_id", 1), body.get("assessor_name", ""), "in_progress", 0))
        aid = cur.lastrowid
        conn.commit()
        return {"id": aid, "status": "created"}
    finally:
        conn.close()

@app.get("/lean20", response_class=HTMLResponse)
async def lean20_page(request: Request): return templates.TemplateResponse(request, "lean20.html", {})

@app.get("/lean20-assess", response_class=HTMLResponse)
async def lean20_assess_page(request: Request): return templates.TemplateResponse(request, "lean20_assess.html", {})

# ==================== Pillars API ====================
@app.get("/api/v1/pillars/dashboard")
def api_pillars_dashboard():
    conn = get_db()
    try:
        pillars = [dict(r) for r in conn.execute("SELECT * FROM value_pillars ORDER BY sort_order").fetchall()]
        a = conn.execute("SELECT * FROM lean20_assessments ORDER BY assessment_date DESC LIMIT 1").fetchone()
        dim_scores = []
        if a:
            dim_scores = [dict(r) for r in conn.execute(
                "SELECT dimension_code, level, weight, weighted_score FROM lean20_dimension_scores WHERE assessment_id=? ORDER BY dimension_code",
                (a["id"],)
            ).fetchall()]
        mappings = [dict(r) for r in conn.execute("SELECT * FROM pillar_dimension_mapping ORDER BY pillar_code, dimension_code").fetchall()]
        kpis = [dict(r) for r in conn.execute("SELECT * FROM pillar_kpi_snapshots ORDER BY pillar_code, snapshot_date DESC").fetchall()]

        PILLAR_NAMES = {
            "better": {"name": "更好", "name_en": "Better", "color": "#2563eb"},
            "faster": {"name": "更快", "name_en": "Faster", "color": "#059669"},
            "closer": {"name": "更近", "name_en": "Closer", "color": "#d97706"},
        }
        DIM_NAMES = {"O": "Operations", "D": "Digital", "G": "Green", "R": "Resilience", "H": "Human-Centric"}

        overall_score = 0
        overall_weight = 0
        pillar_list = []
        for p in pillars:
            code = p["code"]
            p_mappings = [m for m in mappings if m["pillar_code"] == code]
            p_score = 0
            p_weight = 0
            dimensions = []
            for m in p_mappings:
                for ds in dim_scores:
                    if ds["dimension_code"] == m["dimension_code"]:
                        p_score += ds["level"] * float(m["weight_in_pillar"])
                        p_weight += float(m["weight_in_pillar"])
                        dimensions.append({
                            "dimension_code": ds["dimension_code"],
                            "dimension_name": DIM_NAMES.get(ds["dimension_code"], ds["dimension_code"]),
                            "current_level": ds["level"],
                            "weight_in_pillar": float(m["weight_in_pillar"]),
                        })
            avg_score = round(p_score / p_weight, 2) if p_weight > 0 else 0
            target = float(p.get("target_composite", 4.0))
            meta = PILLAR_NAMES.get(code, {"name": p["name"], "name_en": code, "color": "#6b7280"})
            pillar_list.append({
                "code": code,
                "name": meta["name"],
                "name_en": meta["name_en"],
                "color": meta["color"],
                "current_composite": avg_score,
                "target_composite": target,
                "gap_composite": round(target - avg_score, 2),
                "dimensions": dimensions,
                "kpi_count": len([k for k in kpis if k["pillar_code"] == code]),
            })
            overall_score += avg_score * float(p.get("weight", 0.33))
            overall_weight += float(p.get("weight", 0.33))

        overall_composite = round(overall_score / overall_weight, 2) if overall_weight > 0 else 0
        level = "L1" if overall_composite < 1.5 else "L2" if overall_composite < 2.5 else "L3" if overall_composite < 3.5 else "L4" if overall_composite < 4.5 else "L5"

        # Compute per-pillar weakest dimension and add frontend aliases
        for p in pillar_list:
            if p["dimensions"]:
                weakest = min(p["dimensions"], key=lambda d: d["current_level"])
                p["weakest_dimension"] = weakest["dimension_code"]
                p["improvement_suggestion"] = f"Strengthen {weakest['dimension_name']} ({weakest['dimension_code']}) to close the {p['gap_composite']:.2f} point gap to target."
                for d in p["dimensions"]:
                    d["focus_area"] = d["dimension_name"]
                    d["weight"] = d["weight_in_pillar"]
            else:
                p["weakest_dimension"] = None
                p["improvement_suggestion"] = None

        # Build Better-Faster-Closer report compatible with pillars.html
        bfc_pillars = []
        for p in pillar_list:
            bfc_pillars.append({
                "pillar_code": p["code"],
                "pillar_name": p["name"],
                "composite": p["current_composite"],
                "target": p["target_composite"],
                "gap": p["gap_composite"],
                "weakest_dimension": p.get("weakest_dimension"),
                "improvement_suggestion": p.get("improvement_suggestion"),
            })
        bfc_report = {
            "assessment_id": a["id"] if a else None,
            "assessment_date": a["assessment_date"] if a else None,
            "weakest_pillar": max(pillar_list, key=lambda p: p["gap_composite"])["name"] if pillar_list else None,
            "overall_suggestion": "Focus improvement investments on the highest-gaps pillars first to lift the overall Value North Star score.",
            "pillars": bfc_pillars,
        }

        improvement_areas = []
        for p in pillar_list:
            gap = p["gap_composite"]
            if gap > 0.5:
                improvement_areas.append({
                    "pillar": p["name"],
                    "gap": gap,
                    "priority": "high" if gap > 1.0 else "medium",
                })
        improvement_areas.sort(key=lambda x: x["gap"], reverse=True)

        return {
            "overall_composite": overall_composite,
            "overall_level": level,
            "latest_assessment_date": a["assessment_date"] if a else None,
            "pillars": pillar_list,
            "improvement_areas": improvement_areas[:5],
            "bfcReport": bfc_report,
            "assessment": dict(a) if a else None,
            "dim_scores": dim_scores,
            "mappings": mappings,
            "kpis": kpis,
        }
    finally:
        conn.close()

@app.get("/api/v1/pillars")
def api_pillars():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM value_pillars ORDER BY id").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/pillars/{code}")
def api_pillar_detail(code: str):
    conn = get_db()
    try:
        p = conn.execute("SELECT * FROM value_pillars WHERE code=?", (code,)).fetchone()
        if not p: return {"error": "Not found"}
        mappings = conn.execute("SELECT * FROM pillar_dimension_mapping WHERE pillar_code=?", (code,)).fetchall()
        # Also get KPIs
        kpis = conn.execute("SELECT * FROM pillar_kpi_snapshots WHERE pillar_code=?", (code,)).fetchall()
        return {"pillar": dict(p), "mappings": [dict(r) for r in mappings], "kpis": [dict(r) for r in kpis]}
    finally:
        conn.close()

@app.get("/api/v1/pillars/{code}/kpis")
def api_pillar_kpis(code: str):
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM pillar_kpi_snapshots WHERE pillar_code=? ORDER BY snapshot_date DESC", (code,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/pillars/radar/{factory_id}")
def api_pillar_radar(factory_id: int):
    conn = get_db()
    try:
        rows = conn.execute("SELECT dimension_code as dimension, AVG(level) as avg_score FROM lean20_dimension_scores s JOIN lean20_assessments a ON s.assessment_id=a.id WHERE a.factory_id=? GROUP BY dimension_code", (factory_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/pillars/trends")
def api_pillar_trends():
    conn = get_db()
    try:
        rows = conn.execute("SELECT a.created_at, s.dimension_code as dimension, s.level as score FROM lean20_dimension_scores s JOIN lean20_assessments a ON s.assessment_id=a.id ORDER BY a.created_at").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/pillars", response_class=HTMLResponse)
async def pillars_page(request: Request): return templates.TemplateResponse(request, "pillars.html", {})

# ==================== Automation API ====================
@app.get("/api/v1/automation/maturity")
def api_auto_maturity():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM automation_maturity ORDER BY id").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/automation/latest")
def api_auto_latest():
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM automation_maturity ORDER BY created_at DESC LIMIT 1").fetchone()
        if not row:
            return {"error": "No assessments found"}
        return dict(row)
    finally:
        conn.close()

@app.get("/api/v1/automation/radar/{assessment_id}")
def api_auto_radar(assessment_id: int):
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM automation_maturity WHERE id=?", (assessment_id,)).fetchone()
        if not row:
            return {"error": "Not found"}
        DIM_META = [
            {"code": "quality", "name": "AI视觉质检"},
            {"code": "tooling", "name": "快速换模自动化"},
            {"code": "feeding", "name": "自动上料系统"},
            {"code": "heat_treatment", "name": "热处理AI优化"},
            {"code": "logistics", "name": "AGV物料搬运"},
        ]
        points = []
        for m in DIM_META:
            score = row[m["code"] + "_score"] or 0
            level_desc = "L1 - Manual" if score < 1.5 else "L2 - Semi-Auto" if score < 2.5 else "L3 - Automated" if score < 3.5 else "L4 - Intelligent" if score < 4.5 else "L5 - Adaptive"
            points.append({"name": m["name"], "score": score, "level_desc": level_desc})
        return {"assessment": dict(row), "points": points}
    finally:
        conn.close()

@app.get("/api/v1/automation/assessments")
def api_auto_assessments(limit: int = Query(10)):
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM automation_maturity ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.post("/api/v1/automation/assessments")
async def api_auto_create_assessment(request: Request):
    body = await request.json()
    conn = get_db()
    try:
        cur = conn.execute("INSERT INTO automation_maturity (factory_id, assessor_name, quality_score, tooling_score, feeding_score, heat_treatment_score, logistics_score, composite_score, maturity_level, is_completed, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))",
            (body.get("factory_id"), body.get("assessor_name", ""), body.get("quality_score", 0), body.get("tooling_score", 0), body.get("feeding_score", 0), body.get("heat_treatment_score", 0), body.get("logistics_score", 0), body.get("composite_score", 0), body.get("maturity_level", 1), 0))
        conn.commit()
        return {"id": cur.lastrowid, "status": "created"}
    finally:
        conn.close()

@app.get("/api/v1/automation/assessments/{aid}")
def api_auto_assessment_detail(aid: int):
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM automation_maturity WHERE id=?", (aid,)).fetchone()
        if not row:
            return {"error": "Not found"}
        checklist = [dict(r) for r in conn.execute("SELECT * FROM automation_checklist_items WHERE assessment_id=? ORDER BY sort_order", (aid,)).fetchall()]
        result = dict(row)
        result["items"] = checklist
        return result
    finally:
        conn.close()

@app.put("/api/v1/automation/assessments/{aid}")
async def api_auto_update_assessment(aid: int, request: Request):
    body = await request.json()
    conn = get_db()
    try:
        fields = []
        vals = []
        for k in ["quality_score", "tooling_score", "feeding_score", "heat_treatment_score", "logistics_score", "composite_score", "maturity_level", "notes", "is_completed"]:
            if k in body:
                fields.append(f"{k}=?")
                vals.append(body[k])
        # Auto-compute composite and maturity level from dimension scores if any score is provided
        dim_keys = ["quality_score", "tooling_score", "feeding_score", "heat_treatment_score", "logistics_score"]
        if any(k in body for k in dim_keys):
            row = conn.execute("SELECT * FROM automation_maturity WHERE id=?", (aid,)).fetchone()
            scores = []
            for k in dim_keys:
                v = body.get(k, row[k] if row else 0)
                try:
                    scores.append(float(v))
                except (TypeError, ValueError):
                    scores.append(0)
            composite = round(sum(scores) / len(scores), 2) if scores else 0
            maturity_level = 1 if composite < 1.5 else 2 if composite < 2.5 else 3 if composite < 3.5 else 4 if composite < 4.5 else 5
            if "composite_score" not in body:
                fields.append("composite_score=?")
                vals.append(composite)
            if "maturity_level" not in body:
                fields.append("maturity_level=?")
                vals.append(maturity_level)
        if fields:
            vals.append(aid)
            conn.execute(f"UPDATE automation_maturity SET {','.join(fields)} WHERE id=?", vals)
            conn.commit()
        return {"id": aid, "status": "updated"}
    finally:
        conn.close()

@app.post("/api/v1/automation/assessments/{aid}/complete")
def api_auto_complete_assessment(aid: int):
    conn = get_db()
    try:
        conn.execute("UPDATE automation_maturity SET is_completed=1, completed_at=datetime('now') WHERE id=?", (aid,))
        conn.commit()
        return {"id": aid, "status": "completed"}
    finally:
        conn.close()

@app.get("/api/v1/automation/roi-summary")
def api_auto_roi():
    conn = get_db()
    try:
        rows = [dict(r) for r in conn.execute("SELECT * FROM automation_projects ORDER BY id").fetchall()]
        total_invest = sum(r["investment_amount"] or 0 for r in rows)
        total_expected_benefit = sum(r["expected_annual_benefit"] or 0 for r in rows)
        avg_expected_roi = round(total_expected_benefit / total_invest * 100, 1) if total_invest > 0 else 0

        projects_by_status = {}
        projects_by_priority = {}
        for r in rows:
            projects_by_status[r.get("status", "unknown")] = projects_by_status.get(r.get("status", "unknown"), 0) + 1
            projects_by_priority[r.get("priority", "unknown")] = projects_by_priority.get(r.get("priority", "unknown"), 0) + 1

        top_roi = sorted(rows, key=lambda r: r.get("expected_roi", 0) or 0, reverse=True)[:5]

        return {
            "total_investment": total_invest,
            "total_expected_benefit": total_expected_benefit,
            "avg_expected_roi": avg_expected_roi,
            "project_count": len(rows),
            "projects_by_status": projects_by_status,
            "projects_by_priority": projects_by_priority,
            "top_roi_projects": top_roi,
            "projects": rows,
        }
    finally:
        conn.close()

@app.get("/api/v1/automation/checklist")
def api_auto_checklist():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM automation_checklist_items ORDER BY sort_order").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/automation/projects")
def api_auto_projects():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM automation_projects ORDER BY id").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.post("/api/v1/automation/projects")
async def api_auto_create_project(request: Request):
    body = await request.json()
    conn = get_db()
    try:
        invest = body.get("investment_amount", 0) or 0
        benefit = body.get("expected_annual_benefit", 0) or 0
        roi = round(benefit / invest * 100, 1) if invest > 0 else 0
        payback = round(invest / benefit * 12, 1) if benefit > 0 else 0
        cur = conn.execute(
            "INSERT INTO automation_projects (project_name, category, priority, investment_amount, expected_annual_benefit, expected_roi, expected_payback_months, status, start_date, target_date, owner, notes, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
            (body.get("project_name", ""), body.get("category", "quality"), body.get("priority", "P3"),
             invest, benefit, roi, payback,
             body.get("status", "planned"), body.get("start_date"), body.get("target_date"),
             body.get("owner", ""), body.get("notes", ""))
        )
        conn.commit()
        return {"id": cur.lastrowid, "status": "created"}
    finally:
        conn.close()

@app.get("/api/v1/automation/reviews")
def api_auto_reviews():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM automation_reviews ORDER BY review_date DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

# Alias for frontend compatibility (frontend calls pdca-reviews)
@app.get("/api/v1/automation/pdca-reviews")
def api_auto_pdca_reviews():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM automation_reviews ORDER BY review_date DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/automation/projects/{pid}/reviews")
def api_auto_project_reviews(pid: int):
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM automation_reviews WHERE project_id=? ORDER BY review_date DESC", (pid,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.post("/api/v1/automation/projects/{pid}/review")
async def api_auto_create_review(pid: int, request: Request):
    body = await request.json()
    conn = get_db()
    try:
        # Accept both frontend-friendly fields (findings, next_actions, actual_benefit, completion_pct)
        # and detailed PDCA fields (plan_goals, check_results, act_next_steps, check_roi_actual, do_progress)
        findings = body.get("findings", "")
        next_actions = body.get("next_actions", "")
        actual_benefit = body.get("actual_benefit", 0)
        completion_pct = body.get("completion_pct", 0)
        pdca_phase = body.get("pdca_phase", "check")
        cycle_number = body.get("cycle_number", 1)
        reviewer = body.get("reviewer", "")
        review_date = body.get("review_date", datetime.now().strftime("%Y-%m-%d"))

        cur = conn.execute(
            "INSERT INTO automation_reviews (project_id, pdca_phase, cycle_number, reviewer, plan_goals, plan_actions, do_progress, do_issues, check_results, check_roi_actual, act_decision, act_next_steps, review_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))",
            (pid, pdca_phase, cycle_number, reviewer,
             body.get("plan_goals", findings),
             body.get("plan_actions", ""),
             body.get("do_progress", str(completion_pct)),
             body.get("do_issues", ""),
             body.get("check_results", findings),
             body.get("check_roi_actual", actual_benefit),
             body.get("act_decision", ""),
             body.get("act_next_steps", next_actions),
             review_date)
        )
        conn.commit()
        return {"id": cur.lastrowid, "status": "created"}
    finally:
        conn.close()

@app.get("/automation", response_class=HTMLResponse)
async def automation_page(request: Request): return templates.TemplateResponse(request, "automation.html", {})

# ==================== TPM API ====================
@app.get("/api/v1/tpm/equipment")
def api_tpm_equipment():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM tpm_equipment ORDER BY id").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/tpm/faults")
def api_tpm_faults():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM tpm_faults ORDER BY reported_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.post("/api/v1/tpm/faults")
async def api_tpm_create_fault(request: Request):
    body = await request.json()
    conn = get_db()
    try:
        cur = conn.execute("INSERT INTO tpm_faults (equipment_id, fault_type, description, severity, status, reported_at, created_at) VALUES (?, ?, ?, ?, 'open', datetime('now'), datetime('now'))",
            (body.get("equipment_id"), body.get("fault_type", ""), body.get("description", ""), body.get("severity", "medium")))
        conn.commit()
        return {"id": cur.lastrowid, "status": "created"}
    finally:
        conn.close()

@app.get("/api/v1/tpm/maintenance/plans")
def api_tpm_plans():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM tpm_maintenance_plans ORDER BY next_due").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/tpm/maintenance/records")
def api_tpm_records():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM tpm_maintenance_records ORDER BY completed_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/tpm", response_class=HTMLResponse)
async def tpm_page(request: Request): return templates.TemplateResponse(request, "tpm.html", {})

# ==================== 5S & Kaizen API ====================
@app.get("/api/v1/5s/areas")
def api_5s_areas():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM five_s_areas ORDER BY id").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/5s/items")
def api_5s_items():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM five_s_items ORDER BY id LIMIT 200").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/5s/audits")
def api_5s_audits():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM five_s_audits ORDER BY completed_date DESC LIMIT 50").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/5s/improvements")
def api_5s_improvements():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM five_s_improvements ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/kaizen/proposals")
def api_kaizen_proposals():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM kaizen_proposals ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/kaizen/comments")
def api_kaizen_comments():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM kaizen_comments ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/fives-kaizen", response_class=HTMLResponse)
async def fives_kaizen_page(request: Request): return templates.TemplateResponse(request, "fives-kaizen.html", {})

# ==================== Projects API ====================
@app.get("/api/v1/projects")
def api_projects():
    conn = get_db()
    try:
        rows = conn.execute("SELECT p.*, u.display_name as owner_name FROM projects p LEFT JOIN users u ON p.owner_id=u.id ORDER BY p.priority, p.start_date").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/projects/{pid}")
def api_project_detail(pid: int):
    conn = get_db()
    try:
        r = conn.execute("SELECT p.*, u.display_name as owner_name FROM projects p LEFT JOIN users u ON p.owner_id=u.id WHERE p.id=?", (pid,)).fetchone()
        return dict(r) if r else {"error": "Not found"}
    finally:
        conn.close()

@app.get("/api/v1/projects/{pid}/milestones")
def api_project_milestones(pid: int):
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM project_milestones WHERE project_id=? ORDER BY sort_order, target_date", (pid,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/projects/{pid}/tasks")
def api_project_tasks(pid: int):
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM project_tasks WHERE project_id=? ORDER BY due_date", (pid,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/projects/{pid}/updates")
def api_project_updates(pid: int):
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM project_updates WHERE project_id=? ORDER BY update_date DESC", (pid,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/projects/{pid}/risks")
def api_project_risks(pid: int):
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM project_risks WHERE project_id=? AND is_deleted=0 ORDER BY CASE probability WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END", (pid,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/projects/{pid}/members")
def api_project_members(pid: int):
    conn = get_db()
    try:
        rows = conn.execute("SELECT pm.*, u.display_name as user_name FROM project_members pm LEFT JOIN users u ON pm.user_id=u.id WHERE pm.project_id=? ORDER BY CASE pm.role WHEN 'lead' THEN 0 ELSE 1 END, pm.joined_at", (pid,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/projects", response_class=HTMLResponse)
async def projects_page(request: Request): return templates.TemplateResponse(request, "projects.html", {})

@app.get("/project-detail", response_class=HTMLResponse)
async def project_detail_page(request: Request): return templates.TemplateResponse(request, "project-detail.html", {})

# ==================== Training API ====================
@app.get("/api/v1/training/sessions")
def api_training_sessions():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM training_sessions ORDER BY scheduled_date DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/training/enrollments")
def api_training_enrollments():
    conn = get_db()
    try:
        rows = conn.execute("SELECT e.*, s.title as session_title, u.display_name as user_name FROM training_enrollments e JOIN training_sessions s ON e.session_id=s.id LEFT JOIN users u ON e.user_id=u.id ORDER BY e.enrolled_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/training/materials")
def api_training_materials():
    conn = get_db()
    try:
        rows = conn.execute("SELECT m.*, s.title as session_title FROM training_materials m JOIN training_sessions s ON m.session_id=s.id ORDER BY m.created_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/training-page", response_class=HTMLResponse)
async def training_mgmt_page(request: Request): return templates.TemplateResponse(request, "training.html", {})

@app.get("/training", response_class=HTMLResponse)
async def training_redirect(request: Request):
    return templates.TemplateResponse(request, "training.html", {})

@app.get("/knowledge", response_class=HTMLResponse)
async def knowledge_overview(request: Request):
    tree = scan_directory_tree()
    return templates.TemplateResponse(request, "knowledge.html", {
        "module": {"total_files": 0, "subdirs": {}, "root_files": []},
        "module_name": "all",
        "module_info": {}, "all_modules": simplify_all_modules(tree),
        "module_defs": MODULES
    })

# ==================== Best Practices API ====================
@app.get("/api/v1/best-practices")
def api_best_practices():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM best_practices WHERE status='published' ORDER BY view_count DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/best-practices/comments")
def api_bp_comments():
    conn = get_db()
    try:
        rows = conn.execute("SELECT c.*, b.title as practice_title FROM best_practice_comments c JOIN best_practices b ON c.practice_id=b.id ORDER BY c.created_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/best-practices/votes")
def api_bp_votes():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM best_practice_votes ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/best-practices", response_class=HTMLResponse)
async def best_practices_page(request: Request): return templates.TemplateResponse(request, "best-practices.html", {})

# ==================== Assessment & Implementation (old routes) ====================
@app.get("/assessment", response_class=HTMLResponse)
async def assessment_page(request: Request):
    tree = scan_directory_tree()
    module = simplify_module(tree.get("03-成熟度评估", {"info": MODULES.get("03-成熟度评估", {}), "subdirs": {}, "root_files": [], "total_files": 0, "exists": False}))
    return templates.TemplateResponse(request, "assessment.html", {"module": module})

@app.get("/implementation", response_class=HTMLResponse)
async def implementation_page(request: Request):
    tree = scan_directory_tree()
    impl_module = simplify_module(tree.get("04-实施战略", {"info": MODULES.get("04-实施战略", {}), "subdirs": {}, "root_files": [], "total_files": 0, "exists": False}))
    project_module = simplify_module(tree.get("05-项目管理", {"info": MODULES.get("05-项目管理", {}), "subdirs": {}, "root_files": [], "total_files": 0, "exists": False}))
    return templates.TemplateResponse(request, "implementation.html", {"impl_module": impl_module, "project_module": project_module})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
