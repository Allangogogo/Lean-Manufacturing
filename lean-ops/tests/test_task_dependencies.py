"""任务依赖关系测试。"""
import pytest
from app.models.project import ProjectTask, task_dependencies


def test_task_dependencies_table_exists():
    """task_dependencies association table should exist."""
    from app.models.base import Base
    table_names = {t.name for t in Base.metadata.sorted_tables}
    assert "task_dependencies" in table_names


def test_task_dependencies_table_has_required_columns():
    """task_dependencies table should have task_id and depends_on_id columns."""
    columns = {c.name for c in task_dependencies.columns}
    assert "task_id" in columns
    assert "depends_on_id" in columns


def test_project_service_has_set_task_dependencies():
    """ProjectService should have set_task_dependencies method."""
    from app.services.project_service import ProjectService
    assert hasattr(ProjectService, "set_task_dependencies")
