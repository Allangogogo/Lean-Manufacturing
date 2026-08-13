"""
种子数据脚本

初始化 LeanOps 系统的基础数据：
- 1 个工厂
- 4 个角色 + 权限
- 4 个测试用户
- 示例部门
"""

import asyncio
import sys
import os

# 将项目根目录加入 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db_context, init_db
from app.core.security import hash_password
from app.models.fives import FiveSArea
from app.models.user import Department, Factory, Permission, Role, User, UserFactoryRole


async def seed():
    """创建种子数据。"""
    await init_db()

    async with get_db_context() as db:
        # ---- 工厂 ----
        factory = Factory(
            name="紧固件制造一厂",
            code="F001",
            address="江苏省苏州市",
            contact="张厂长",
            is_active=True,
        )
        db.add(factory)
        await db.flush()

        # ---- 角色 ----
        roles = {
            "admin": Role(name="系统管理员", code="admin", is_system=True),
            "lean_mgr": Role(name="精益经理", code="lean_mgr", is_system=True),
            "supervisor": Role(name="班组长", code="supervisor", is_system=True),
            "worker": Role(name="操作员工", code="worker", is_system=True),
            "manager": Role(name="高层管理", code="manager", is_system=True),
        }
        for role in roles.values():
            db.add(role)
        await db.flush()

        # ---- 权限 ----
        permissions_data = [
            # 精益经理 — 全部权限
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
            # 班组长
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
            # 操作员工
            ("worker", "kaizen", "create", "own"),
            ("worker", "kaizen", "read", "own"),
            ("worker", "fives", "read", "own"),
            ("worker", "training", "read", "factory"),
            ("worker", "tpm", "read", "factory"),
            ("worker", "practice", "create", "factory"),
            ("worker", "practice", "read", "factory"),
            ("worker", "dashboard", "read", "own"),
            # 高层管理
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
            perm = Permission(
                role_id=roles[role_code].id,
                resource=resource,
                action=action,
                scope=scope,
            )
            db.add(perm)
        await db.flush()

        # ---- 部门 ----
        dept_production = Department(
            factory_id=factory.id, name="生产部", code="D001", sort_order=1
        )
        dept_quality = Department(
            factory_id=factory.id, name="质量部", code="D002", sort_order=2
        )
        dept_maint = Department(
            factory_id=factory.id, name="设备部", code="D003", sort_order=3
        )
        for dept in [dept_production, dept_quality, dept_maint]:
            db.add(dept)
        await db.flush()

        # ---- 用户 ----
        users_data = [
            {
                "username": "admin",
                "display_name": "系统管理员",
                "role": "admin",
                "dept": dept_production,
            },
            {
                "username": "lean_zhang",
                "display_name": "张精益",
                "role": "lean_mgr",
                "dept": dept_production,
            },
            {
                "username": "super_li",
                "display_name": "李班长",
                "role": "supervisor",
                "dept": dept_production,
            },
            {
                "username": "worker_wang",
                "display_name": "王操作",
                "role": "worker",
                "dept": dept_production,
            },
            {
                "username": "mgr_chen",
                "display_name": "陈总",
                "role": "manager",
                "dept": dept_production,
            },
        ]

        password_hash = hash_password("123456")
        lean_mgr_user_id = None
        for u in users_data:
            user = User(
                username=u["username"],
                password_hash=password_hash,
                display_name=u["display_name"],
                default_factory_id=factory.id,
                is_active=True,
            )
            db.add(user)
            await db.flush()

            if u["role"] == "lean_mgr":
                lean_mgr_user_id = user.id

            ufr = UserFactoryRole(
                user_id=user.id,
                factory_id=factory.id,
                role_id=roles[u["role"]].id,
                department_id=u["dept"].id,
                is_default=True,
            )
            db.add(ufr)

        # ---- 5S 区域 ----
        areas_data = [
            ("冷镦车间", "A001", "冷镦生产线区域"),
            ("螺纹加工区", "A002", "螺纹滚压与搓丝区域"),
            ("热处理车间", "A003", "热处理炉及冷却区域"),
            ("表面处理区", "A004", "电镀与涂覆区域"),
            ("分选包装区", "A005", "自动分选与包装区域"),
            ("原材料仓库", "A006", "钢材线材存储区"),
            ("成品仓库", "A007", "成品存储与出货区"),
        ]
        for name, code, desc in areas_data:
            area = FiveSArea(
                factory_id=factory.id,
                name=name,
                code=code,
                description=desc,
                responsible_id=lean_mgr_user_id,
                is_active=True,
            )
            db.add(area)

        await db.commit()
        print("种子数据创建完成！")
        print("测试用户 (密码均为 123456):")
        print("  admin        — 系统管理员")
        print("  lean_zhang   — 精益经理")
        print("  super_li     — 班组长")
        print("  worker_wang  — 操作员工")
        print("  mgr_chen     — 高层管理")


if __name__ == "__main__":
    asyncio.run(seed())
