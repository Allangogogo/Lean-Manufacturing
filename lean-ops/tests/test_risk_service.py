"""风险管理服务测试。"""
import pytest
from app.models.risk import ProjectRisk


def test_risk_model_has_required_columns():
    columns = {c.name for c in ProjectRisk.__table__.columns}
    assert "project_id" in columns
    assert "title" in columns
    assert "probability" in columns
    assert "impact" in columns
    assert "status" in columns
    assert "owner_id" in columns
    assert "is_deleted" in columns


def test_risk_model_has_soft_delete():
    columns = {c.name for c in ProjectRisk.__table__.columns}
    assert "is_deleted" in columns
    assert "deleted_at" in columns
