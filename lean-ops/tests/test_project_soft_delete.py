"""软删除测试。"""
import pytest
from app.models.project import (
    Project, ProjectMilestone, ProjectTask, ProjectMember, ProjectUpdate,
)


def test_project_has_soft_delete_fields():
    columns = {c.name for c in Project.__table__.columns}
    assert "is_deleted" in columns
    assert "deleted_at" in columns


def test_project_task_has_soft_delete_fields():
    columns = {c.name for c in ProjectTask.__table__.columns}
    assert "is_deleted" in columns
    assert "deleted_at" in columns


def test_project_milestone_has_soft_delete_fields():
    columns = {c.name for c in ProjectMilestone.__table__.columns}
    assert "is_deleted" in columns
    assert "deleted_at" in columns


def test_project_member_has_soft_delete_fields():
    columns = {c.name for c in ProjectMember.__table__.columns}
    assert "is_deleted" in columns
    assert "deleted_at" in columns


def test_project_update_has_soft_delete_fields():
    columns = {c.name for c in ProjectUpdate.__table__.columns}
    assert "is_deleted" in columns
    assert "deleted_at" in columns


def test_project_task_has_sort_order():
    columns = {c.name for c in ProjectTask.__table__.columns}
    assert "sort_order" in columns
