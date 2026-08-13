"""
系统管理业务逻辑层

职责：
1. 用户 CRUD
2. 角色管理
3. 系统统计
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppError, NotFoundError
from app.core.pagination import PaginatedResponse, paginate
from app.core.security import hash_password
from app.models.user import Department, Role, User, UserFactoryRole
from app.models.kaizen import KaizenProposal
from app.models.fives import FiveSAudit
from app.models.training import TrainingSession
from app.models.tpm import TPMEquipment
from app.models.project import Project
from app.models.practice import BestPractice
from app.schemas.admin import (
    AdminStatsResponse,
    PasswordResetRequest,
    RoleResponse,
    UserCreateRequest,
    UserListItem,
    UserUpdateRequest,
)


class AdminService:
    """系统管理业务服务。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # 用户管理
    # ============================================================

    async def list_users(
        self,
        factory_id: int,
        keyword: Optional[str] = None,
        role_code: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse:
        """查询用户列表。"""
        query = (
            select(User)
            .join(UserFactoryRole, UserFactoryRole.user_id == User.id)
            .where(UserFactoryRole.factory_id == factory_id)
            .order_by(desc(User.created_at))
        )
        if keyword:
            query = query.where(
                User.display_name.contains(keyword) | User.username.contains(keyword)
            )
        if role_code:
            query = query.join(Role, Role.id == UserFactoryRole.role_id).where(
                Role.code == role_code
            )

        result = await paginate(self.db, query, page, page_size)

        items = []
        for u in result.data:
            # 获取该用户在此工厂的角色
            ufr = await self.db.execute(
                select(UserFactoryRole)
                .options(selectinload(UserFactoryRole.role))
                .where(
                    UserFactoryRole.user_id == u.id,
                    UserFactoryRole.factory_id == factory_id,
                )
                .limit(1)
            )
            ufr_obj = ufr.scalar_one_or_none()
            role_name = ""
            role_code_val = ""
            dept_name = ""
            if ufr_obj and ufr_obj.role:
                role_name = ufr_obj.role.name
                role_code_val = ufr_obj.role.code
            if ufr_obj and ufr_obj.department_id:
                dept = await self.db.get(Department, ufr_obj.department_id)
                dept_name = dept.name if dept else ""

            items.append(UserListItem(
                id=u.id, username=u.username, display_name=u.display_name,
                email=u.email, phone=u.phone,
                role_name=role_name, role_code=role_code_val,
                department_name=dept_name, is_active=u.is_active,
                last_login_at=u.last_login_at, created_at=u.created_at,
            ))

        return PaginatedResponse.create(
            items=[i.model_dump() for i in items],
            total=result.pagination["total"], page=page, page_size=page_size,
        )

    async def create_user(
        self, data: UserCreateRequest, factory_id: int,
    ) -> UserListItem:
        """创建用户。"""
        # 检查用户名唯一
        existing = await self.db.execute(
            select(User).where(User.username == data.username)
        )
        if existing.scalar_one_or_none():
            raise AppError("用户名已存在", code="CONFLICT")

        # 查找角色
        role = await self.db.execute(
            select(Role).where(Role.code == data.role_code)
        )
        role_obj = role.scalar_one_or_none()
        if role_obj is None:
            raise AppError("无效的角色代码", code="INVALID_PARAMS")

        user = User(
            username=data.username,
            password_hash=hash_password(data.password),
            display_name=data.display_name,
            email=data.email, phone=data.phone,
            default_factory_id=factory_id, is_active=True,
        )
        self.db.add(user)
        await self.db.flush()

        # 分配角色
        ufr = UserFactoryRole(
            user_id=user.id, factory_id=factory_id,
            role_id=role_obj.id, department_id=data.department_id,
        )
        self.db.add(ufr)
        await self.db.flush()

        return UserListItem(
            id=user.id, username=user.username, display_name=user.display_name,
            email=user.email, phone=user.phone,
            role_name=role_obj.name, role_code=role_obj.code,
            is_active=user.is_active, created_at=user.created_at,
        )

    async def update_user(
        self, user_id: int, data: UserUpdateRequest, factory_id: int,
    ) -> UserListItem:
        """更新用户。"""
        user = await self.db.get(User, user_id)
        if user is None:
            raise NotFoundError("用户", user_id)

        if data.display_name is not None:
            user.display_name = data.display_name
        if data.email is not None:
            user.email = data.email
        if data.phone is not None:
            user.phone = data.phone
        if data.is_active is not None:
            user.is_active = data.is_active
        await self.db.flush()

        # 更新角色
        if data.role_code:
            role = await self.db.execute(
                select(Role).where(Role.code == data.role_code)
            )
            role_obj = role.scalar_one_or_none()
            if role_obj:
                ufr = await self.db.execute(
                    select(UserFactoryRole).where(
                        UserFactoryRole.user_id == user_id,
                        UserFactoryRole.factory_id == factory_id,
                    )
                )
                ufr_obj = ufr.scalar_one_or_none()
                if ufr_obj:
                    ufr_obj.role_id = role_obj.id
                if data.department_id is not None and ufr_obj:
                    ufr_obj.department_id = data.department_id
                await self.db.flush()

        return await self._get_user_item(user_id, factory_id)

    async def reset_password(
        self, user_id: int, data: PasswordResetRequest,
    ) -> None:
        """重置用户密码。"""
        user = await self.db.get(User, user_id)
        if user is None:
            raise NotFoundError("用户", user_id)
        user.password_hash = hash_password(data.new_password)
        await self.db.flush()

    async def list_roles(self) -> list[RoleResponse]:
        """查询所有角色。"""
        result = await self.db.execute(select(Role).order_by(Role.id))
        return [
            RoleResponse(id=r.id, name=r.name, code=r.code, description=r.description)
            for r in result.scalars().all()
        ]

    async def list_departments(self, factory_id: int) -> list[dict]:
        """查询部门列表。"""
        result = await self.db.execute(
            select(Department)
            .where(Department.factory_id == factory_id, Department.is_active == True)
            .order_by(Department.sort_order)
        )
        return [
            {"id": d.id, "name": d.name, "code": d.code}
            for d in result.scalars().all()
        ]

    async def _get_user_item(
        self, user_id: int, factory_id: int,
    ) -> UserListItem:
        """构建用户列表项。"""
        user = await self.db.get(User, user_id)
        if user is None:
            raise NotFoundError("用户", user_id)
        ufr = await self.db.execute(
            select(UserFactoryRole)
            .options(selectinload(UserFactoryRole.role))
            .where(
                UserFactoryRole.user_id == user_id,
                UserFactoryRole.factory_id == factory_id,
            )
            .limit(1)
        )
        ufr_obj = ufr.scalar_one_or_none()
        role_name = ""
        role_code_val = ""
        dept_name = ""
        if ufr_obj and ufr_obj.role:
            role_name = ufr_obj.role.name
            role_code_val = ufr_obj.role.code
        if ufr_obj and ufr_obj.department_id:
            dept = await self.db.get(Department, ufr_obj.department_id)
            dept_name = dept.name if dept else ""

        return UserListItem(
            id=user.id, username=user.username, display_name=user.display_name,
            email=user.email, phone=user.phone,
            role_name=role_name, role_code=role_code_val,
            department_name=dept_name, is_active=user.is_active,
            last_login_at=user.last_login_at, created_at=user.created_at,
        )

    # ============================================================
    # 系统统计
    # ============================================================

    async def get_stats(self, factory_id: int) -> AdminStatsResponse:
        """获取系统统计。"""
        users_result = await self.db.execute(
            select(func.count(User.id))
            .join(UserFactoryRole, UserFactoryRole.user_id == User.id)
            .where(UserFactoryRole.factory_id == factory_id)
        )
        total_users = users_result.scalar() or 0

        active_result = await self.db.execute(
            select(func.count(User.id))
            .join(UserFactoryRole, UserFactoryRole.user_id == User.id)
            .where(UserFactoryRole.factory_id == factory_id, User.is_active == True)
        )
        active_users = active_result.scalar() or 0

        proposals = await self.db.execute(
            select(func.count(KaizenProposal.id))
            .where(KaizenProposal.factory_id == factory_id)
        )
        audits = await self.db.execute(
            select(func.count(FiveSAudit.id))
            .where(FiveSAudit.factory_id == factory_id)
        )
        training = await self.db.execute(
            select(func.count(TrainingSession.id))
            .where(TrainingSession.factory_id == factory_id)
        )
        equipment = await self.db.execute(
            select(func.count(TPMEquipment.id))
            .where(TPMEquipment.factory_id == factory_id)
        )
        projects = await self.db.execute(
            select(func.count(Project.id))
            .where(Project.factory_id == factory_id)
        )
        practices = await self.db.execute(
            select(func.count(BestPractice.id))
            .where(BestPractice.factory_id == factory_id)
        )

        return AdminStatsResponse(
            total_users=total_users, active_users=active_users,
            total_proposals=proposals.scalar() or 0,
            total_audits=audits.scalar() or 0,
            total_training=training.scalar() or 0,
            total_equipment=equipment.scalar() or 0,
            total_projects=projects.scalar() or 0,
            total_practices=practices.scalar() or 0,
        )
