"""
ORM 模型聚合

导入所有模型，确保 Alembic 能发现它们。
"""

from app.models.base import Base, BaseModel, TimestampMixin  # noqa: F401
from app.models.user import (  # noqa: F401
    Department,
    Factory,
    Permission,
    Role,
    User,
    UserFactoryRole,
)
from app.models.workflow import WorkflowLog, WorkflowState  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.kaizen import (  # noqa: F401
    KaizenAttachment,
    KaizenComment,
    KaizenProposal,
)
from app.models.fives import (  # noqa: F401
    FiveSArea,
    FiveSAudit,
    FiveSImprovement,
    FiveSItem,
)
from app.models.training import (  # noqa: F401
    TrainingEnrollment,
    TrainingMaterial,
    TrainingSession,
)
from app.models.tpm import (  # noqa: F401
    TPMFault,
    TPMEquipment,
    TPMMaintenancePlan,
    TPMMaintenanceRecord,
)
from app.models.project import (  # noqa: F401
    Project,
    ProjectMember,
    ProjectMilestone,
    ProjectTask,
    ProjectUpdate,
)
from app.models.risk import ProjectRisk  # noqa: F401
from app.models.practice import (  # noqa: F401
    BestPractice,
    BestPracticeAttachment,
    BestPracticeComment,
    BestPracticeVote,
)
from app.models.maturity import (  # noqa: F401
    MaturityAssessment,
    MaturityCriterion,
    MaturityDimension,
)
from app.models.lean20 import (  # noqa: F401
    Lean20Assessment,
    Lean20ChecklistItem,
    Lean20ChecklistResponse,
    Lean20DimensionScore,
)
from app.models.wip import (  # noqa: F401
    ProductionOrder,
    WIPDailySnapshot,
    WIPTransaction,
    WorkOrderOperation,
)
