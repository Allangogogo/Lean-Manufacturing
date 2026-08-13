"""枚举定义测试。"""
import pytest
from app.models.enums import (
    ProjectStatus, ProjectPriority, TaskStatus,
    MilestoneStatus, MemberRole, RiskProbability,
    RiskImpact, RiskStatus,
)


def test_project_status_values():
    assert ProjectStatus.DRAFT == "draft"
    assert ProjectStatus.PLANNING == "planning"
    assert ProjectStatus.ACTIVE == "active"
    assert ProjectStatus.ON_HOLD == "on_hold"
    assert ProjectStatus.COMPLETED == "completed"
    assert ProjectStatus.CANCELLED == "cancelled"


def test_task_status_values():
    assert TaskStatus.TODO == "todo"
    assert TaskStatus.IN_PROGRESS == "in_progress"
    assert TaskStatus.BLOCKED == "blocked"
    assert TaskStatus.DONE == "done"
    assert TaskStatus.CANCELLED == "cancelled"


def test_project_priority_values():
    assert ProjectPriority.LOW == "low"
    assert ProjectPriority.MEDIUM == "medium"
    assert ProjectPriority.HIGH == "high"
    assert ProjectPriority.CRITICAL == "critical"


def test_milestone_status_values():
    assert MilestoneStatus.PENDING == "pending"
    assert MilestoneStatus.IN_PROGRESS == "in_progress"
    assert MilestoneStatus.COMPLETED == "completed"


def test_member_role_values():
    assert MemberRole.OWNER == "owner"
    assert MemberRole.EDITOR == "editor"
    assert MemberRole.MEMBER == "member"
    assert MemberRole.VIEWER == "viewer"
    assert MemberRole.CONSULTANT == "consultant"


def test_risk_probability_values():
    assert RiskProbability.LOW == "low"
    assert RiskProbability.MEDIUM == "medium"
    assert RiskProbability.HIGH == "high"
    assert RiskProbability.CRITICAL == "critical"


def test_risk_impact_values():
    assert RiskImpact.LOW == "low"
    assert RiskImpact.MEDIUM == "medium"
    assert RiskImpact.HIGH == "high"
    assert RiskImpact.CRITICAL == "critical"


def test_risk_status_values():
    assert RiskStatus.IDENTIFIED == "identified"
    assert RiskStatus.ANALYZING == "analyzing"
    assert RiskStatus.MITIGATING == "mitigating"
    assert RiskStatus.MONITORING == "monitoring"
    assert RiskStatus.CLOSED == "closed"
    assert RiskStatus.ACCEPTED == "accepted"


def test_enum_is_string_subclass():
    """All enums should be str subclasses for SQLAlchemy compatibility."""
    assert issubclass(ProjectStatus, str)
    assert issubclass(ProjectPriority, str)
    assert issubclass(TaskStatus, str)
    assert issubclass(MilestoneStatus, str)
    assert issubclass(MemberRole, str)
    assert issubclass(RiskProbability, str)
    assert issubclass(RiskImpact, str)
    assert issubclass(RiskStatus, str)
