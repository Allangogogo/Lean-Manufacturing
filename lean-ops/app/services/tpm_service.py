"""
TPM 设备管理业务逻辑层

职责：
1. 设备台账 CRUD
2. 维护计划管理
3. 维护执行记录
4. 故障管理
5. 统计查询
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppError, ForbiddenError, NotFoundError
from app.core.pagination import PaginatedResponse, paginate
from app.models.tpm import (
    TPMFault,
    TPMEquipment,
    TPMMaintenancePlan,
    TPMMaintenanceRecord,
)
from app.models.user import User
from app.schemas.tpm import (
    EquipmentCreateRequest,
    EquipmentResponse,
    EquipmentUpdateRequest,
    FaultCreateRequest,
    FaultResponse,
    FaultUpdateRequest,
    MaintenancePlanCreateRequest,
    MaintenancePlanResponse,
    MaintenanceRecordCreateRequest,
    TPMStatsResponse,
)


class TPMService:
    """TPM 设备管理业务服务。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # 设备台账
    # ============================================================

    async def list_equipment(
        self,
        factory_id: int,
        equipment_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse:
        """查询设备列表。"""
        query = select(TPMEquipment).where(TPMEquipment.factory_id == factory_id)
        if equipment_type:
            query = query.where(TPMEquipment.equipment_type == equipment_type)
        if status:
            query = query.where(TPMEquipment.status == status)
        query = query.order_by(TPMEquipment.equipment_code)

        result = await paginate(self.db, query, page, page_size)

        items = []
        for eq in result.data:
            responsible = await self.db.get(User, eq.responsible_id) if eq.responsible_id else None
            # 活跃维护计划数
            plan_count = await self.db.execute(
                select(func.count(TPMMaintenancePlan.id)).where(
                    TPMMaintenancePlan.equipment_id == eq.id,
                    TPMMaintenancePlan.is_active == True,
                )
            )
            # 未解决故障数
            fault_count = await self.db.execute(
                select(func.count(TPMFault.id)).where(
                    TPMFault.equipment_id == eq.id,
                    TPMFault.status.notin_(["completed"]),
                )
            )
            items.append(EquipmentResponse(
                id=eq.id,
                equipment_code=eq.equipment_code,
                equipment_name=eq.equipment_name,
                equipment_type=eq.equipment_type,
                location=eq.location,
                factory_id=eq.factory_id,
                manufacturer=eq.manufacturer,
                model=eq.model,
                serial_number=eq.serial_number,
                install_date=eq.install_date,
                warranty_until=eq.warranty_until,
                status=eq.status,
                responsible_id=eq.responsible_id,
                responsible_name=responsible.display_name if responsible else "",
                notes=eq.notes,
                created_at=eq.created_at,
                active_plans=plan_count.scalar() or 0,
                open_faults=fault_count.scalar() or 0,
            ))

        return PaginatedResponse.create(
            items=[i.model_dump() for i in items],
            total=result.pagination["total"],
            page=page,
            page_size=page_size,
        )

    async def get_equipment(self, equipment_id: int) -> EquipmentResponse:
        """获取设备详情。"""
        eq = await self.db.get(TPMEquipment, equipment_id)
        if eq is None:
            raise NotFoundError("设备", equipment_id)

        responsible = await self.db.get(User, eq.responsible_id) if eq.responsible_id else None
        plan_count = await self.db.execute(
            select(func.count(TPMMaintenancePlan.id)).where(
                TPMMaintenancePlan.equipment_id == eq.id,
                TPMMaintenancePlan.is_active == True,
            )
        )
        fault_count = await self.db.execute(
            select(func.count(TPMFault.id)).where(
                TPMFault.equipment_id == eq.id,
                TPMFault.status.notin_(["completed"]),
            )
        )

        return EquipmentResponse(
            id=eq.id,
            equipment_code=eq.equipment_code,
            equipment_name=eq.equipment_name,
            equipment_type=eq.equipment_type,
            location=eq.location,
            factory_id=eq.factory_id,
            manufacturer=eq.manufacturer,
            model=eq.model,
            serial_number=eq.serial_number,
            install_date=eq.install_date,
            warranty_until=eq.warranty_until,
            status=eq.status,
            responsible_id=eq.responsible_id,
            responsible_name=responsible.display_name if responsible else "",
            notes=eq.notes,
            created_at=eq.created_at,
            active_plans=plan_count.scalar() or 0,
            open_faults=fault_count.scalar() or 0,
        )

    async def create_equipment(
        self,
        data: EquipmentCreateRequest,
        factory_id: int,
    ) -> EquipmentResponse:
        """添加设备。"""
        # 检查编号唯一性
        existing = await self.db.execute(
            select(TPMEquipment).where(TPMEquipment.equipment_code == data.equipment_code)
        )
        if existing.scalar_one_or_none():
            raise AppError(f"设备编号 {data.equipment_code} 已存在", code="CONFLICT")

        eq = TPMEquipment(
            equipment_code=data.equipment_code,
            equipment_name=data.equipment_name,
            equipment_type=data.equipment_type,
            location=data.location,
            factory_id=factory_id,
            manufacturer=data.manufacturer,
            model=data.model,
            serial_number=data.serial_number,
            install_date=data.install_date,
            warranty_until=data.warranty_until,
            responsible_id=data.responsible_id,
            notes=data.notes,
            status="normal",
        )
        self.db.add(eq)
        await self.db.flush()
        return await self.get_equipment(eq.id)

    async def update_equipment(
        self,
        equipment_id: int,
        data: EquipmentUpdateRequest,
    ) -> EquipmentResponse:
        """更新设备。"""
        eq = await self.db.get(TPMEquipment, equipment_id)
        if eq is None:
            raise NotFoundError("设备", equipment_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(eq, field, value)

        return await self.get_equipment(equipment_id)

    # ============================================================
    # 维护计划
    # ============================================================

    async def list_plans(
        self,
        factory_id: int,
        equipment_id: Optional[int] = None,
        plan_type: Optional[str] = None,
        overdue_only: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse:
        """查询维护计划。"""
        query = (
            select(TPMMaintenancePlan)
            .join(TPMEquipment, TPMMaintenancePlan.equipment_id == TPMEquipment.id)
            .where(TPMEquipment.factory_id == factory_id)
        )
        if equipment_id:
            query = query.where(TPMMaintenancePlan.equipment_id == equipment_id)
        if plan_type:
            query = query.where(TPMMaintenancePlan.plan_type == plan_type)
        if overdue_only:
            query = query.where(TPMMaintenancePlan.next_due < date.today())
        query = query.order_by(TPMMaintenancePlan.next_due)

        result = await paginate(self.db, query, page, page_size)

        items = []
        for p in result.data:
            eq = await self.db.get(TPMEquipment, p.equipment_id)
            assigned = await self.db.get(User, p.assigned_to_id) if p.assigned_to_id else None
            items.append(MaintenancePlanResponse(
                id=p.id,
                equipment_id=p.equipment_id,
                equipment_name=eq.equipment_name if eq else "",
                plan_type=p.plan_type,
                task_description=p.task_description,
                frequency_days=p.frequency_days,
                last_executed=p.last_executed,
                next_due=p.next_due,
                assigned_to_id=p.assigned_to_id,
                assigned_to_name=assigned.display_name if assigned else "",
                is_active=p.is_active,
            ))

        return PaginatedResponse.create(
            items=[i.model_dump() for i in items],
            total=result.pagination["total"],
            page=page,
            page_size=page_size,
        )

    async def create_plan(
        self,
        data: MaintenancePlanCreateRequest,
        factory_id: int,
    ) -> MaintenancePlanResponse:
        """创建维护计划。"""
        eq = await self.db.get(TPMEquipment, data.equipment_id)
        if eq is None:
            raise NotFoundError("设备", data.equipment_id)
        if eq.factory_id != factory_id:
            raise ForbiddenError("无权操作其他工厂的设备")

        plan = TPMMaintenancePlan(
            equipment_id=data.equipment_id,
            plan_type=data.plan_type,
            task_description=data.task_description,
            frequency_days=data.frequency_days,
            next_due=data.next_due,
            assigned_to_id=data.assigned_to_id,
            is_active=True,
        )
        self.db.add(plan)
        await self.db.flush()

        assigned = await self.db.get(User, plan.assigned_to_id) if plan.assigned_to_id else None
        return MaintenancePlanResponse(
            id=plan.id,
            equipment_id=plan.equipment_id,
            equipment_name=eq.equipment_name,
            plan_type=plan.plan_type,
            task_description=plan.task_description,
            frequency_days=plan.frequency_days,
            next_due=plan.next_due,
            assigned_to_id=plan.assigned_to_id,
            assigned_to_name=assigned.display_name if assigned else "",
            is_active=plan.is_active,
        )

    # ============================================================
    # 维护执行
    # ============================================================

    async def record_maintenance(
        self,
        data: MaintenanceRecordCreateRequest,
        user_id: int,
        factory_id: int,
    ) -> dict:
        """记录维护执行。"""
        eq = await self.db.get(TPMEquipment, data.equipment_id)
        if eq is None:
            raise NotFoundError("设备", data.equipment_id)
        if eq.factory_id != factory_id:
            raise ForbiddenError("无权操作其他工厂的设备")

        record = TPMMaintenanceRecord(
            plan_id=data.plan_id,
            equipment_id=data.equipment_id,
            executor_id=user_id,
            status="completed",
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            findings=data.findings,
            issues_found=data.issues_found,
            parts_replaced=data.parts_replaced,
            downtime_hours=data.downtime_hours,
        )
        self.db.add(record)

        # 更新维护计划的上次执行和下次到期
        if data.plan_id:
            plan = await self.db.get(TPMMaintenancePlan, data.plan_id)
            if plan:
                plan.last_executed = date.today()
                from datetime import timedelta
                plan.next_due = date.today() + timedelta(days=plan.frequency_days)

        await self.db.flush()
        return {"success": True, "record_id": record.id}

    # ============================================================
    # 故障管理
    # ============================================================

    async def list_faults(
        self,
        factory_id: int,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse:
        """查询故障列表。"""
        query = (
            select(TPMFault)
            .join(TPMEquipment, TPMFault.equipment_id == TPMEquipment.id)
            .where(TPMEquipment.factory_id == factory_id)
        )
        if status:
            query = query.where(TPMFault.status == status)
        if severity:
            query = query.where(TPMFault.severity == severity)
        query = query.order_by(desc(TPMFault.reported_at))

        result = await paginate(self.db, query, page, page_size)

        items = []
        for f in result.data:
            eq = await self.db.get(TPMEquipment, f.equipment_id)
            reporter = await self.db.get(User, f.reporter_id)
            items.append(FaultResponse(
                id=f.id,
                equipment_id=f.equipment_id,
                equipment_name=eq.equipment_name if eq else "",
                reporter_name=reporter.display_name if reporter else "",
                fault_type=f.fault_type,
                description=f.description,
                severity=f.severity,
                status=f.status,
                reported_at=f.reported_at,
                diagnosed_at=f.diagnosed_at,
                repaired_at=f.repaired_at,
                root_cause=f.root_cause,
                corrective_action=f.corrective_action,
                downtime_hours=f.downtime_hours,
                repair_cost=f.repair_cost,
            ))

        return PaginatedResponse.create(
            items=[i.model_dump() for i in items],
            total=result.pagination["total"],
            page=page,
            page_size=page_size,
        )

    async def create_fault(
        self,
        data: FaultCreateRequest,
        user_id: int,
        factory_id: int,
    ) -> FaultResponse:
        """报修。"""
        eq = await self.db.get(TPMEquipment, data.equipment_id)
        if eq is None:
            raise NotFoundError("设备", data.equipment_id)
        if eq.factory_id != factory_id:
            raise ForbiddenError("无权操作其他工厂的设备")

        fault = TPMFault(
            equipment_id=data.equipment_id,
            reporter_id=user_id,
            fault_type=data.fault_type,
            description=data.description,
            severity=data.severity,
            status="reported",
        )
        self.db.add(fault)

        # 更新设备状态
        if data.severity in ("major", "critical"):
            eq.status = "fault"

        await self.db.flush()

        reporter = await self.db.get(User, fault.reporter_id)
        return FaultResponse(
            id=fault.id,
            equipment_id=fault.equipment_id,
            equipment_name=eq.equipment_name,
            reporter_name=reporter.display_name if reporter else "",
            fault_type=fault.fault_type,
            description=fault.description,
            severity=fault.severity,
            status=fault.status,
            reported_at=fault.reported_at,
        )

    async def update_fault(
        self,
        fault_id: int,
        data: FaultUpdateRequest,
    ) -> FaultResponse:
        """更新故障状态。"""
        fault = await self.db.get(TPMFault, fault_id)
        if fault is None:
            raise NotFoundError("故障记录", fault_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(fault, field, value)

        # 如果状态变为 completed，记录修复时间
        if data.status == "completed" and not fault.repaired_at:
            fault.repaired_at = datetime.now(timezone.utc)
            # 恢复设备状态
            eq = await self.db.get(TPMEquipment, fault.equipment_id)
            if eq:
                eq.status = "normal"

        await self.db.flush()
        return await self._get_fault(fault_id)

    async def _get_fault(self, fault_id: int) -> FaultResponse:
        fault = await self.db.get(TPMFault, fault_id)
        eq = await self.db.get(TPMEquipment, fault.equipment_id)
        reporter = await self.db.get(User, fault.reporter_id)
        return FaultResponse(
            id=fault.id,
            equipment_id=fault.equipment_id,
            equipment_name=eq.equipment_name if eq else "",
            reporter_name=reporter.display_name if reporter else "",
            fault_type=fault.fault_type,
            description=fault.description,
            severity=fault.severity,
            status=fault.status,
            reported_at=fault.reported_at,
            diagnosed_at=fault.diagnosed_at,
            repaired_at=fault.repaired_at,
            root_cause=fault.root_cause,
            corrective_action=fault.corrective_action,
            downtime_hours=fault.downtime_hours,
            repair_cost=fault.repair_cost,
        )

    # ============================================================
    # 统计
    # ============================================================

    async def get_stats(self, factory_id: int) -> TPMStatsResponse:
        """获取 TPM 统计。"""
        # 设备状态统计
        result = await self.db.execute(
            select(
                TPMEquipment.status,
                func.count(TPMEquipment.id),
            )
            .where(TPMEquipment.factory_id == factory_id)
            .group_by(TPMEquipment.status)
        )
        status_counts = {row[0]: row[1] for row in result.all()}
        total = sum(status_counts.values())

        # 逾期维护计划
        overdue_result = await self.db.execute(
            select(func.count(TPMMaintenancePlan.id))
            .join(TPMEquipment, TPMMaintenancePlan.equipment_id == TPMEquipment.id)
            .where(
                TPMEquipment.factory_id == factory_id,
                TPMMaintenancePlan.is_active == True,
                TPMMaintenancePlan.next_due < date.today(),
            )
        )
        overdue = overdue_result.scalar() or 0

        # 未解决故障
        fault_result = await self.db.execute(
            select(func.count(TPMFault.id))
            .join(TPMEquipment, TPMFault.equipment_id == TPMEquipment.id)
            .where(
                TPMEquipment.factory_id == factory_id,
                TPMFault.status.notin_(["completed"]),
            )
        )
        open_faults = fault_result.scalar() or 0

        # 总停机时长
        downtime_result = await self.db.execute(
            select(func.sum(TPMMaintenanceRecord.downtime_hours))
            .join(TPMEquipment, TPMMaintenanceRecord.equipment_id == TPMEquipment.id)
            .where(TPMEquipment.factory_id == factory_id)
        )
        total_downtime = downtime_result.scalar() or 0

        return TPMStatsResponse(
            total_equipment=total,
            normal=status_counts.get("normal", 0),
            fault=status_counts.get("fault", 0),
            maintenance=status_counts.get("maintenance", 0),
            overdue_maintenance=overdue,
            open_faults=open_faults,
            total_downtime=float(total_downtime),
        )
