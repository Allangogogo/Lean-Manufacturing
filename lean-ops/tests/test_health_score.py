# tests/test_health_score.py
"""项目健康度算法测试。"""
import pytest
from unittest.mock import MagicMock
from decimal import Decimal
from app.services.dashboard_service import DashboardService


def test_health_score_green():
    """High progress, under budget, no risks -> green."""
    mock_db = MagicMock()
    service = DashboardService(mock_db)

    result = service._calculate_health_score(
        planned_progress=80,
        actual_progress=80,
        budget=Decimal("100000"),
        actual_cost=Decimal("60000"),
        open_risks=0,
        total_risks=5,
        total_tasks=20,
        completed_tasks=16,
    )
    assert result["level"] == "green"
    assert result["score"] >= 0.8


def test_health_score_red():
    """Far behind schedule, heavily over budget, all risks open -> red."""
    mock_db = MagicMock()
    service = DashboardService(mock_db)

    result = service._calculate_health_score(
        planned_progress=80,
        actual_progress=15,
        budget=Decimal("100000"),
        actual_cost=Decimal("150000"),
        open_risks=5,
        total_risks=5,
        total_tasks=20,
        completed_tasks=2,
    )
    assert result["level"] == "red"
    assert result["score"] < 0.4


def test_health_score_no_budget():
    """Budget not set -> default 0.5 score."""
    mock_db = MagicMock()
    service = DashboardService(mock_db)

    result = service._calculate_health_score(
        planned_progress=50,
        actual_progress=50,
        budget=Decimal("0"),
        actual_cost=Decimal("0"),
        open_risks=0,
        total_risks=0,
        total_tasks=10,
        completed_tasks=5,
    )
    assert result["breakdown"]["budget"] == 0.5


def test_health_score_no_tasks():
    """No tasks -> quality score 1.0."""
    mock_db = MagicMock()
    service = DashboardService(mock_db)

    result = service._calculate_health_score(
        planned_progress=0,
        actual_progress=0,
        budget=Decimal("100000"),
        actual_cost=Decimal("0"),
        open_risks=0,
        total_risks=0,
        total_tasks=0,
        completed_tasks=0,
    )
    assert result["breakdown"]["quality"] == 1.0
