"""
LeanOps 数据库一键重建脚本（从零重建全部表 + 种子数据）

用途：
    当 data/leanops.db 缺失或需要从零重建时运行。
    编排顺序：ORM create_all → 建表 migrate → seed 基础数据 → 填清单数据

用法：
    py scripts/rebuild_db.py
"""

import asyncio
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

# 项目根目录（lean-ops/）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "data" / "leanops.db"

EXPECTED_TABLES = {
    # ORM create_all 建的表（43）
    "audit_logs", "automation_checklist_items", "automation_maturity",
    "automation_projects", "automation_reviews", "best_practice_attachments",
    "best_practice_comments", "best_practice_votes", "best_practices",
    "departments", "factories", "five_s_areas", "five_s_audits",
    "five_s_improvements", "five_s_items", "kaizen_attachments",
    "kaizen_comments", "kaizen_proposals", "lean20_assessments",
    "lean20_dimension_scores", "maturity_assessments", "maturity_criteria",
    "maturity_dimensions", "permissions", "production_orders", "project_members",
    "project_milestones", "project_risks", "project_tasks", "project_updates",
    "projects", "roles", "task_dependencies", "tpm_equipment", "tpm_faults",
    "tpm_maintenance_plans", "tpm_maintenance_records", "training_enrollments",
    "training_materials", "training_sessions", "user_factory_roles", "users",
    "wip_daily_snapshots", "wip_transactions", "work_order_operations",
    "workflow_logs", "workflow_states",
    # migrate 脚本建的表（9）
    "lean20_checklist_items", "lean20_checklist_responses",
    "pillar_dimension_mapping", "pillar_kpi_snapshots", "value_pillars",
}


def step(msg: str):
    print(f"\n=== {msg} ===")


async def init_orm():
    """Step 1: ORM create_all 建 43 张表。"""
    from app.database import init_db, engine
    await init_db()
    await engine.dispose()


def run_migrate_scripts():
    """Step 2: 运行建表 migrate 脚本（9 张表）。"""
    # 顺序：先 lean20（依赖 projects 已建），再其他
    scripts = [
        "migrate_lean20.py",
        "migrate_automation.py",
        "migrate_lean20_checklist.py",
        "migrate_vision_pillars.py",
        "migrate_wip.py",
    ]
    for s in scripts:
        path = PROJECT_ROOT / s
        print(f"  运行 {s} ...")
        result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  [警告] {s} 退出码 {result.returncode}")
            if result.stderr:
                print(f"    stderr: {result.stderr[-500:]}")
        else:
            out = (result.stdout or "").strip().splitlines()
            print(f"    OK: {out[-1] if out else '(no output)'}")


async def run_seed():
    """Step 3: 基础种子数据（工厂/角色/权限/部门/用户/5S）。"""
    from app.database import get_db_context, init_db
    from app.core.security import hash_password
    from app.models.fives import FiveSArea
    from app.models.user import Department, Factory, Permission, Role, User, UserFactoryRole

    await init_db()

    async with get_db_context() as db:
        # 检查是否已有数据
        from sqlalchemy import select, func
        from app.models.user import Factory as F
        cnt = await db.scalar(select(func.count()).select_from(F))
        if cnt and cnt > 0:
            print("  基础数据已存在，跳过 seed")
            return

        factory = Factory(name="制造一厂", code="F001", address="江苏省苏州市",
                          contact="张厂长", is_active=True)
        db.add(factory)
        await db.flush()

        roles = {
            "admin": Role(name="系统管理员", code="admin", is_system=True),
            "lean_mgr": Role(name="精益经理", code="lean_mgr", is_system=True),
            "supervisor": Role(name="班组长", code="supervisor", is_system=True),
            "worker": Role(name="操作员工", code="worker", is_system=True),
            "manager": Role(name="高层管理", code="manager", is_system=True),
        }
        for r in roles.values():
            db.add(r)
        await db.flush()

        permissions_data = [
            ("lean_mgr", "kaizen", "create", "factory"),
            ("lean_mgr", "kaizen", "read", "factory"),
            ("lean_mgr", "kaizen", "update", "factory"),
            ("lean_mgr", "kaizen", "approve", "factory"),
            ("lean_mgr", "fives", "create", "factory"),
            ("lean_mgr", "fives", "read", "factory"),
            ("lean_mgr", "fives", "update", "factory"),
            ("lean_mgr", "training", "create", "factory"),
            ("lean_mgr", "training", "read", "factory"),
            ("lean_mgr", "tpm", "read", "factory"),
            ("lean_mgr", "tpm", "manage", "factory"),
            ("lean_mgr", "project", "create", "factory"),
            ("lean_mgr", "project", "read", "factory"),
            ("lean_mgr", "project", "update", "factory"),
            ("lean_mgr", "practice", "create", "factory"),
            ("lean_mgr", "practice", "read", "factory"),
            ("lean_mgr", "practice", "approve", "factory"),
            ("lean_mgr", "maturity", "create", "factory"),
            ("lean_mgr", "maturity", "read", "factory"),
            ("lean_mgr", "maturity", "update", "factory"),
            ("lean_mgr", "dashboard", "read", "factory"),
            ("lean_mgr", "user", "manage", "factory"),
            ("supervisor", "kaizen", "create", "dept"),
            ("supervisor", "kaizen", "read", "dept"),
            ("supervisor", "kaizen", "approve", "dept"),
            ("supervisor", "fives", "create", "dept"),
            ("supervisor", "fives", "read", "dept"),
            ("supervisor", "training", "read", "factory"),
            ("supervisor", "tpm", "read", "factory"),
            ("supervisor", "tpm", "manage", "dept"),
            ("supervisor", "project", "read", "dept"),
            ("supervisor", "project", "update", "dept"),
            ("supervisor", "practice", "create", "factory"),
            ("supervisor", "practice", "read", "factory"),
            ("supervisor", "dashboard", "read", "dept"),
            ("worker", "kaizen", "create", "own"),
            ("worker", "kaizen", "read", "own"),
            ("worker", "fives", "read", "own"),
            ("worker", "training", "read", "factory"),
            ("worker", "tpm", "read", "factory"),
            ("worker", "practice", "create", "factory"),
            ("worker", "practice", "read", "factory"),
            ("worker", "dashboard", "read", "own"),
            ("manager", "kaizen", "read", "all"),
            ("manager", "fives", "read", "all"),
            ("manager", "training", "read", "all"),
            ("manager", "tpm", "read", "all"),
            ("manager", "project", "read", "all"),
            ("manager", "practice", "read", "all"),
            ("manager", "maturity", "read", "all"),
            ("manager", "dashboard", "read", "all"),
        ]
        for role_code, resource, action, scope in permissions_data:
            db.add(Permission(role_id=roles[role_code].id, resource=resource,
                              action=action, scope=scope))
        await db.flush()

        dept_production = Department(factory_id=factory.id, name="生产部", code="D001", sort_order=1)
        dept_quality = Department(factory_id=factory.id, name="质量部", code="D002", sort_order=2)
        dept_maint = Department(factory_id=factory.id, name="设备部", code="D003", sort_order=3)
        for d in [dept_production, dept_quality, dept_maint]:
            db.add(d)
        await db.flush()

        users_data = [
            ("admin", "系统管理员", "admin", dept_production),
            ("lean_zhang", "张精益", "lean_mgr", dept_production),
            ("super_li", "李班长", "supervisor", dept_production),
            ("worker_wang", "王操作", "worker", dept_production),
            ("mgr_chen", "陈总", "manager", dept_production),
        ]
        password_hash = hash_password("123456")
        lean_mgr_user_id = None
        for username, display, role_code, dept in users_data:
            user = User(username=username, password_hash=password_hash,
                        display_name=display, default_factory_id=factory.id,
                        is_active=True)
            db.add(user)
            await db.flush()
            if role_code == "lean_mgr":
                lean_mgr_user_id = user.id
            db.add(UserFactoryRole(user_id=user.id, factory_id=factory.id,
                                   role_id=roles[role_code].id,
                                   department_id=dept.id, is_default=True))

        areas_data = [
            ("机加工车间", "A001", "机加工生产线区域"),
            ("精加工区", "A002", "精加工与精加工区域"),
            ("热处理车间", "A003", "热处理炉及冷却区域"),
            ("表面处理区", "A004", "涂覆与表面处理区域"),
            ("装配包装区", "A005", "自动装配与包装区域"),
            ("原材料仓库", "A006", "原材料存储区"),
            ("成品仓库", "A007", "成品存储与出货区"),
        ]
        for name, code, desc in areas_data:
            db.add(FiveSArea(factory_id=factory.id, name=name, code=code,
                             description=desc, responsible_id=lean_mgr_user_id,
                             is_active=True))
        await db.commit()
        print("  基础种子数据创建完成（5 用户 / 5 角色 / 3 部门 / 7 5S 区域）")


def run_checklist_seed():
    """Step 4: 填 lean20 清单数据（migrate_checklist_deep）。"""
    path = PROJECT_ROOT / "migrate_checklist_deep.py"
    if path.exists():
        print("  运行 migrate_checklist_deep.py ...")
        result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  [警告] 退出码 {result.returncode}: {result.stderr[-300:]}")
        else:
            print("  OK")
    else:
        print("  跳过（脚本不存在）")


def verify():
    """Step 5: 校验 53 张表 + 关键种子数据。"""
    conn = sqlite3.connect(str(DB_PATH))
    tables = set(r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"))
    missing = EXPECTED_TABLES - tables
    extra = tables - EXPECTED_TABLES - {"sqlite_sequence"}

    print(f"\n=== 校验结果 ===")
    print(f"  实际表数: {len(tables)}，期望: {len(EXPECTED_TABLES)}")
    if missing:
        print(f"  [缺失] {sorted(missing)}")
    else:
        print("  [OK] 53 张表全部建齐")

    # 关键种子数据
    checks = {
        "users": "SELECT COUNT(*) FROM users",
        "factories": "SELECT COUNT(*) FROM factories",
        "roles": "SELECT COUNT(*) FROM roles",
        "permissions": "SELECT COUNT(*) FROM permissions",
        "five_s_areas": "SELECT COUNT(*) FROM five_s_areas",
        "lean20_checklist_items": "SELECT COUNT(*) FROM lean20_checklist_items",
        "value_pillars": "SELECT COUNT(*) FROM value_pillars",
        "production_orders": "SELECT COUNT(*) FROM production_orders",
    }
    for name, sql in checks.items():
        try:
            n = conn.execute(sql).fetchone()[0]
            print(f"  {name}: {n} 行")
        except Exception as e:
            print(f"  {name}: [错误] {e}")
    conn.close()
    return not missing


async def main():
    step("Step 1/5: ORM create_all")
    await init_orm()
    step("Step 2/5: 建表 migrate 脚本")
    run_migrate_scripts()
    step("Step 3/5: 基础种子数据")
    await run_seed()
    step("Step 4/5: lean20 清单数据")
    run_checklist_seed()
    ok = verify()
    print("\n" + ("✅ 数据库重建完成" if ok else "❌ 有表缺失，见上"))


if __name__ == "__main__":
    asyncio.run(main())
