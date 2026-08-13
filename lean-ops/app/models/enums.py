"""精益运营管理系统 — 枚举定义。"""

from enum import Enum


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"


class MilestoneStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class MemberRole(str, Enum):
    OWNER = "owner"
    EDITOR = "editor"
    MEMBER = "member"
    VIEWER = "viewer"
    CONSULTANT = "consultant"


class RiskProbability(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskImpact(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskStatus(str, Enum):
    IDENTIFIED = "identified"
    ANALYZING = "analyzing"
    MITIGATING = "mitigating"
    MONITORING = "monitoring"
    CLOSED = "closed"
    ACCEPTED = "accepted"


class AssessmentType(str, Enum):
    """Maturity assessment type."""
    OVERALL = "overall"
    PROCESS = "process"
    DEPARTMENT = "department"
    LEAN20 = "lean20"


class Lean20Dimension(str, Enum):
    """Lean 2.0 five dimensions (Industry 5.0 extended)."""
    O = "O"  # Operational Lean
    D = "D"  # Digital Lean
    G = "G"  # Green Lean
    R = "R"  # Resilience
    H = "H"  # Human-Centric


class Lean20Level(str, Enum):
    """Lean 2.0 composite level labels."""
    L1 = "L1 - Initial"
    L2 = "L2 - Developing"
    L3 = "L3 - Systematic"
    L4 = "L4 - Proactive"
    L5 = "L5 - World-class"


# Valid status transitions for projects
PROJECT_STATUS_TRANSITIONS = {
    ProjectStatus.DRAFT: {ProjectStatus.PLANNING, ProjectStatus.CANCELLED},
    ProjectStatus.PLANNING: {ProjectStatus.ACTIVE, ProjectStatus.CANCELLED},
    ProjectStatus.ACTIVE: {ProjectStatus.ON_HOLD, ProjectStatus.COMPLETED, ProjectStatus.CANCELLED},
    ProjectStatus.ON_HOLD: {ProjectStatus.ACTIVE, ProjectStatus.CANCELLED},
    ProjectStatus.COMPLETED: set(),
    ProjectStatus.CANCELLED: set(),
}

# Valid status transitions for tasks
TASK_STATUS_TRANSITIONS = {
    TaskStatus.TODO: {TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED, TaskStatus.CANCELLED},
    TaskStatus.IN_PROGRESS: {TaskStatus.DONE, TaskStatus.BLOCKED, TaskStatus.CANCELLED},
    TaskStatus.BLOCKED: {TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
    TaskStatus.DONE: set(),
    TaskStatus.CANCELLED: set(),
}
