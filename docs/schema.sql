-- ============================================================
-- LeanOps 精益运营管理系统 — 数据库 DDL
-- 数据库: SQLite (可切换 PostgreSQL)
-- 字符集: UTF-8
-- 编码: 每张表包含中文注释
-- ============================================================

PRAGMA foreign_keys = ON;

-- ============================================================
-- 1. 基础设施表 (Infrastructure)
-- ============================================================

-- 1.1 工厂表
CREATE TABLE IF NOT EXISTS factories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR(100) NOT NULL,                -- 工厂名称
    code        VARCHAR(20)  NOT NULL UNIQUE,         -- 工厂编码（如 F001）
    address     TEXT,                                 -- 地址
    contact     VARCHAR(50),                          -- 联系人
    phone       VARCHAR(20),                          -- 联系电话
    is_active   BOOLEAN    NOT NULL DEFAULT 1,        -- 是否启用
    created_at  DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 1.2 部门表（支持多级）
CREATE TABLE IF NOT EXISTS departments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    factory_id  INTEGER  NOT NULL REFERENCES factories(id),
    parent_id   INTEGER  REFERENCES departments(id), -- 上级部门（支持层级）
    name        VARCHAR(100) NOT NULL,
    code        VARCHAR(20)  NOT NULL,
    description TEXT,
    sort_order  INTEGER  NOT NULL DEFAULT 0,
    is_active   BOOLEAN  NOT NULL DEFAULT 1,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(factory_id, code)
);

-- 1.3 角色表
CREATE TABLE IF NOT EXISTS roles (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR(50)  NOT NULL UNIQUE,         -- 角色名称
    code        VARCHAR(30)  NOT NULL UNIQUE,         -- 角色编码
    description TEXT,
    is_system   BOOLEAN      NOT NULL DEFAULT 0,      -- 是否系统内置
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 1.4 权限表（RBAC）
CREATE TABLE IF NOT EXISTS permissions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id     INTEGER  NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    resource    VARCHAR(50) NOT NULL,                 -- 资源：kaizen/fives/training/tpm/project/practice/maturity/user/dashboard
    action      VARCHAR(20) NOT NULL,                 -- 动作：create/read/update/delete/approve/export
    scope       VARCHAR(20) NOT NULL DEFAULT 'own',   -- 范围：own/dept/factory/all
    description TEXT,
    UNIQUE(role_id, resource, action)
);

-- 1.5 用户表
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        VARCHAR(50)  NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    display_name    VARCHAR(100) NOT NULL,
    email           VARCHAR(100),
    phone           VARCHAR(20),
    avatar          VARCHAR(255),
    default_factory_id INTEGER REFERENCES factories(id),
    is_active       BOOLEAN  NOT NULL DEFAULT 1,
    last_login_at   DATETIME,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 1.6 用户-工厂-角色 关联表（多工厂多角色）
CREATE TABLE IF NOT EXISTS user_factory_roles (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    factory_id    INTEGER NOT NULL REFERENCES factories(id),
    role_id       INTEGER NOT NULL REFERENCES roles(id),
    department_id INTEGER REFERENCES departments(id),
    is_default    BOOLEAN NOT NULL DEFAULT 0,          -- 是否默认工厂
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, factory_id, role_id)
);

-- ============================================================
-- 2. 工作流引擎表 (Workflow)
-- ============================================================

-- 2.1 工作流状态表（通用）
CREATE TABLE IF NOT EXISTS workflow_states (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type   VARCHAR(30) NOT NULL,               -- 实体类型：kaizen/fives_audit/project/best_practice/maturity
    entity_id     INTEGER     NOT NULL,               -- 实体ID
    current_state VARCHAR(30) NOT NULL,               -- 当前状态
    assigned_to_id INTEGER   REFERENCES users(id),    -- 当前处理人
    created_by_id INTEGER    NOT NULL REFERENCES users(id),
    factory_id    INTEGER    NOT NULL REFERENCES factories(id),
    created_at    DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_type, entity_id)
);

-- 2.2 工作流日志表（审批记录）
CREATE TABLE IF NOT EXISTS workflow_logs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    state_id      INTEGER     NOT NULL REFERENCES workflow_states(id) ON DELETE CASCADE,
    from_state    VARCHAR(30),                        -- 原状态（可为空：首次提交）
    to_state      VARCHAR(30) NOT NULL,               -- 目标状态
    action        VARCHAR(30) NOT NULL,               -- 操作：submit/approve/reject/return/close/reopen
    operator_id   INTEGER     NOT NULL REFERENCES users(id),
    comment       TEXT,                               -- 审批意见
    created_at    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 3. 改善提案管理 (Kaizen)
-- ============================================================

-- 3.1 改善提案主表
CREATE TABLE IF NOT EXISTS kaizen_proposals (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    title               VARCHAR(200) NOT NULL,
    description         TEXT         NOT NULL,
    category            VARCHAR(30)  NOT NULL,        -- quality/cost/delivery/safety/morale
    submitter_id        INTEGER      NOT NULL REFERENCES users(id),
    factory_id          INTEGER      NOT NULL REFERENCES factories(id),
    department_id       INTEGER      REFERENCES departments(id),
    status              VARCHAR(20)  NOT NULL DEFAULT 'draft',  -- 见枚举定义
    priority            VARCHAR(10)  NOT NULL DEFAULT 'medium', -- low/medium/high/urgent
    current_approver_id INTEGER      REFERENCES users(id),
    expected_benefit    TEXT,                          -- 预期收益（文字描述）
    expected_saving     DECIMAL(12,2),                 -- 预期节约金额（元）
    actual_benefit      TEXT,                          -- 实际收益
    actual_saving       DECIMAL(12,2),                 -- 实际节约金额
    root_cause          TEXT,                          -- 根因分析
    solution            TEXT,                          -- 解决方案
    implementation_plan TEXT,                          -- 实施计划
    result              TEXT,                          -- 实施结果
    due_date            DATE,                          -- 截止日期
    closed_at           DATETIME,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3.2 提案评论/审批记录
CREATE TABLE IF NOT EXISTS kaizen_comments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    proposal_id INTEGER NOT NULL REFERENCES kaizen_proposals(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    action      VARCHAR(20) NOT NULL,                -- comment/approve/reject/return
    comment     TEXT,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3.3 提案附件
CREATE TABLE IF NOT EXISTS kaizen_attachments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    proposal_id INTEGER NOT NULL REFERENCES kaizen_proposals(id) ON DELETE CASCADE,
    filename    VARCHAR(255) NOT NULL,
    filepath    VARCHAR(500) NOT NULL,
    filesize    INTEGER,
    uploaded_by INTEGER NOT NULL REFERENCES users(id),
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 4. 5S 审核管理 (Five S)
-- ============================================================

-- 4.1 5S 审核区域
CREATE TABLE IF NOT EXISTS five_s_areas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    factory_id  INTEGER NOT NULL REFERENCES factories(id),
    name        VARCHAR(100) NOT NULL,                -- 区域名称（如：冷镦车间A线）
    code        VARCHAR(20),                          -- 区域编码
    description TEXT,
    responsible_id INTEGER REFERENCES users(id),      -- 区域负责人
    is_active   BOOLEAN NOT NULL DEFAULT 1,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4.2 5S 审核记录
CREATE TABLE IF NOT EXISTS five_s_audits (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    area_id         INTEGER     NOT NULL REFERENCES five_s_areas(id),
    factory_id      INTEGER     NOT NULL REFERENCES factories(id),
    auditor_id      INTEGER     NOT NULL REFERENCES users(id),   -- 审核员
    audit_type      VARCHAR(20) NOT NULL,             -- daily/weekly/monthly/quarterly
    score           DECIMAL(5,2),                     -- 总分
    max_score       DECIMAL(5,2) NOT NULL DEFAULT 100,
    status          VARCHAR(20) NOT NULL DEFAULT 'scheduled', -- scheduled/in_progress/completed
    scheduled_date  DATE        NOT NULL,
    completed_date  DATE,
    remarks         TEXT,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4.3 5S 审核细项（每项 S 的评分）
CREATE TABLE IF NOT EXISTS five_s_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_id    INTEGER     NOT NULL REFERENCES five_s_audits(id) ON DELETE CASCADE,
    s_category  VARCHAR(20) NOT NULL,                 -- sort/straighten/shine/standardize/sustain
    item_name   VARCHAR(200) NOT NULL,                -- 检查项名称
    description TEXT,
    weight      DECIMAL(3,1) NOT NULL DEFAULT 1.0,    -- 权重
    score       DECIMAL(5,2),                         -- 得分
    max_score   DECIMAL(5,2) NOT NULL DEFAULT 10.0,
    photo_path  VARCHAR(500),                         -- 现场照片路径
    remarks     TEXT,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4.4 5S 改善跟踪
CREATE TABLE IF NOT EXISTS five_s_improvements (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_id        INTEGER     NOT NULL REFERENCES five_s_audits(id),
    item_description TEXT       NOT NULL,              -- 整改项描述
    assigned_to_id  INTEGER     REFERENCES users(id),  -- 负责人
    status          VARCHAR(20) NOT NULL DEFAULT 'open', -- open/in_progress/completed/verified
    due_date        DATE,
    completed_date  DATE,
    evidence_path   VARCHAR(500),                      -- 完成证据照片
    verified_by_id  INTEGER     REFERENCES users(id),  -- 验证人
    verified_at     DATETIME,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 5. 培训管理 (Training)
-- ============================================================

-- 5.1 培训场次
CREATE TABLE IF NOT EXISTS training_sessions (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    title             VARCHAR(200) NOT NULL,
    description       TEXT,
    trainer_id        INTEGER     NOT NULL REFERENCES users(id),
    factory_id        INTEGER     NOT NULL REFERENCES factories(id),
    training_type     VARCHAR(30) NOT NULL,            -- lean_tool/safety/quality/process/management
    level             VARCHAR(20) NOT NULL,            -- L1_basics/L2_intermediate/L3_advanced/L4_expert
    scheduled_date    DATE        NOT NULL,
    start_time        TIME,
    end_time          TIME,
    duration_hours    DECIMAL(4,1) NOT NULL DEFAULT 1.0,
    location          VARCHAR(200),
    max_participants  INTEGER     NOT NULL DEFAULT 30,
    status            VARCHAR(20) NOT NULL DEFAULT 'scheduled', -- scheduled/in_progress/completed/cancelled
    pass_score        DECIMAL(5,2) NOT NULL DEFAULT 60.0,      -- 及格分
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 5.2 培训报名/签到/成绩
CREATE TABLE IF NOT EXISTS training_enrollments (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id    INTEGER NOT NULL REFERENCES training_sessions(id) ON DELETE CASCADE,
    user_id       INTEGER NOT NULL REFERENCES users(id),
    status        VARCHAR(20) NOT NULL DEFAULT 'enrolled', -- enrolled/attended/absent/certified/failed
    score         DECIMAL(5,2),                            -- 考核成绩
    feedback_rating INTEGER,                               -- 课后评分 1-5
    feedback_comment TEXT,                                 -- 课后反馈
    enrolled_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    attended_at   DATETIME,
    certified_at  DATETIME,
    UNIQUE(session_id, user_id)
);

-- 5.3 培训材料
CREATE TABLE IF NOT EXISTS training_materials (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id    INTEGER      NOT NULL REFERENCES training_sessions(id) ON DELETE CASCADE,
    material_name VARCHAR(200) NOT NULL,
    material_type VARCHAR(20) NOT NULL,                -- ppt/doc/video/quiz/worksheet
    filepath      VARCHAR(500) NOT NULL,
    filesize      INTEGER,
    uploaded_by   INTEGER      NOT NULL REFERENCES users(id),
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 6. TPM 设备管理
-- ============================================================

-- 6.1 设备台账
CREATE TABLE IF NOT EXISTS tpm_equipment (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_code    VARCHAR(30)  NOT NULL UNIQUE,    -- 设备编号
    equipment_name    VARCHAR(200) NOT NULL,
    equipment_type    VARCHAR(30)  NOT NULL,           -- cold_header/thread_roller/heat_treat/electroplating/sorter/packager/other
    location          VARCHAR(200),
    factory_id        INTEGER      NOT NULL REFERENCES factories(id),
    manufacturer      VARCHAR(100),                    -- 制造商
    model             VARCHAR(100),                    -- 型号
    serial_number     VARCHAR(100),                    -- 序列号
    install_date      DATE,
    warranty_until    DATE,
    status            VARCHAR(20) NOT NULL DEFAULT 'normal', -- normal/fault/maintenance/retired
    responsible_id    INTEGER      REFERENCES users(id),
    notes             TEXT,
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 6.2 TPM 维护计划
CREATE TABLE IF NOT EXISTS tpm_maintenance_plans (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id      INTEGER     NOT NULL REFERENCES tpm_equipment(id) ON DELETE CASCADE,
    plan_type         VARCHAR(20) NOT NULL,            -- daily/weekly/monthly/quarterly/yearly
    task_description  TEXT        NOT NULL,             -- 维护任务描述
    checklist_items   TEXT,                             -- 检查项 JSON 数组
    frequency_days    INTEGER     NOT NULL DEFAULT 1,   -- 维护周期（天）
    last_executed     DATE,                             -- 上次执行日期
    next_due          DATE        NOT NULL,             -- 下次到期日期
    assigned_to_id    INTEGER     REFERENCES users(id),
    is_active         BOOLEAN     NOT NULL DEFAULT 1,
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 6.3 维护执行记录
CREATE TABLE IF NOT EXISTS tpm_maintenance_records (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id         INTEGER     NOT NULL REFERENCES tpm_maintenance_plans(id),
    equipment_id    INTEGER     NOT NULL REFERENCES tpm_equipment(id),
    executor_id     INTEGER     NOT NULL REFERENCES users(id),
    status          VARCHAR(20) NOT NULL DEFAULT 'planned', -- planned/in_progress/completed/overdue
    started_at      DATETIME,
    completed_at    DATETIME,
    findings        TEXT,                                  -- 巡检发现
    issues_found    TEXT,                                  -- 发现问题
    parts_replaced  TEXT,                                  -- 更换配件
    downtime_hours  DECIMAL(5,2) DEFAULT 0,                -- 停机时长
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 6.4 设备故障记录
CREATE TABLE IF NOT EXISTS tpm_faults (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id    INTEGER     NOT NULL REFERENCES tpm_equipment(id),
    reporter_id     INTEGER     NOT NULL REFERENCES users(id),
    fault_type      VARCHAR(50) NOT NULL,                 -- mechanical/electrical/software/other
    description     TEXT        NOT NULL,
    severity        VARCHAR(10) NOT NULL DEFAULT 'minor', -- minor/major/critical
    status          VARCHAR(20) NOT NULL DEFAULT 'reported', -- reported/diagnosing/repairing/completed
    reported_at     DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    diagnosed_at    DATETIME,
    repaired_at     DATETIME,
    root_cause      TEXT,                                  -- 根因分析
    corrective_action TEXT,                                -- 纠正措施
    downtime_hours  DECIMAL(5,2) DEFAULT 0,
    repair_cost     DECIMAL(10,2) DEFAULT 0,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 7. 项目管理 (Project)
-- ============================================================

-- 7.1 精益项目
CREATE TABLE IF NOT EXISTS projects (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    project_type    VARCHAR(30) NOT NULL,               -- kaizen_event/vsm_redux/5s_deployment/tpm_rollout/training_program/other
    owner_id        INTEGER     NOT NULL REFERENCES users(id),
    factory_id      INTEGER     NOT NULL REFERENCES factories(id),
    status          VARCHAR(20) NOT NULL DEFAULT 'planning', -- planning/active/on_hold/completed/cancelled
    priority        VARCHAR(10) NOT NULL DEFAULT 'medium',
    start_date      DATE,
    target_end_date DATE,
    actual_end_date DATE,
    budget          DECIMAL(12,2) DEFAULT 0,
    actual_cost     DECIMAL(12,2) DEFAULT 0,
    scope           TEXT,
    objectives      TEXT,
    success_criteria TEXT,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 7.2 项目里程碑
CREATE TABLE IF NOT EXISTS project_milestones (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id    INTEGER     NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name          VARCHAR(200) NOT NULL,
    description   TEXT,
    target_date   DATE,
    actual_date   DATE,
    status        VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending/in_progress/completed/overdue
    sort_order    INTEGER NOT NULL DEFAULT 0,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 7.3 项目任务
CREATE TABLE IF NOT EXISTS project_tasks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id      INTEGER     NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    milestone_id    INTEGER     REFERENCES project_milestones(id),
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    assigned_to_id  INTEGER     REFERENCES users(id),
    status          VARCHAR(20) NOT NULL DEFAULT 'todo', -- todo/in_progress/done/blocked
    priority        VARCHAR(10) NOT NULL DEFAULT 'medium',
    due_date        DATE,
    completed_date  DATE,
    estimated_hours DECIMAL(6,1),
    actual_hours    DECIMAL(6,1),
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 7.4 项目成员
CREATE TABLE IF NOT EXISTS project_members (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    role        VARCHAR(20) NOT NULL DEFAULT 'member', -- owner/member/consultant
    joined_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, user_id)
);

-- 7.5 项目周报
CREATE TABLE IF NOT EXISTS project_updates (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id        INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    author_id         INTEGER NOT NULL REFERENCES users(id),
    update_date       DATE    NOT NULL,
    progress_pct      INTEGER NOT NULL DEFAULT 0,       -- 进度百分比 0-100
    accomplishments   TEXT,                              -- 本周完成
    plan_next_week    TEXT,                              -- 下周计划
    risks_issues      TEXT,                              -- 风险问题
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 8. Best Practice 管理
-- ============================================================

-- 8.1 最佳实践
CREATE TABLE IF NOT EXISTS best_practices (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    title                 VARCHAR(200) NOT NULL,
    description           TEXT         NOT NULL,
    category              VARCHAR(30)  NOT NULL,        -- tool/method/mindset/process
    subcategory           VARCHAR(30)  NOT NULL,        -- kanban/5s/smed/poka_yoke/vsm/tpm/kaizen/six_sigma
    author_id             INTEGER      NOT NULL REFERENCES users(id),
    factory_id            INTEGER      NOT NULL REFERENCES factories(id),
    status                VARCHAR(20)  NOT NULL DEFAULT 'draft', -- draft/published/archived
    problem_statement     TEXT,                          -- 问题描述
    root_cause            TEXT,                          -- 根因分析
    solution              TEXT         NOT NULL,         -- 解决方案
    results               TEXT,                          -- 实施结果
    applicable_areas      TEXT,                          -- 适用领域 JSON: ["production","quality","safety"]
    estimated_saving      DECIMAL(12,2),                 -- 预期节约（万元）
    actual_saving         DECIMAL(12,2),                 -- 实际节约（万元）
    difficulty_level      VARCHAR(10)  NOT NULL DEFAULT 'medium', -- easy/medium/hard
    implementation_time_days INTEGER,                    -- 实施周期（天）
    tags                  TEXT,                          -- 标签 JSON 数组
    view_count            INTEGER NOT NULL DEFAULT 0,
    usage_count           INTEGER NOT NULL DEFAULT 0,
    published_at          DATETIME,
    created_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 8.2 点赞/收藏
CREATE TABLE IF NOT EXISTS best_practice_votes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    practice_id INTEGER NOT NULL REFERENCES best_practices(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    vote_type   VARCHAR(10) NOT NULL,                 -- like/bookmark
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(practice_id, user_id, vote_type)
);

-- 8.3 评论
CREATE TABLE IF NOT EXISTS best_practice_comments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    practice_id INTEGER NOT NULL REFERENCES best_practices(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    comment     TEXT    NOT NULL,
    rating      INTEGER,                               -- 1-5 评分
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 8.4 附件
CREATE TABLE IF NOT EXISTS best_practice_attachments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    practice_id INTEGER      NOT NULL REFERENCES best_practices(id) ON DELETE CASCADE,
    filename    VARCHAR(255) NOT NULL,
    filepath    VARCHAR(500) NOT NULL,
    filesize    INTEGER,
    uploaded_by INTEGER      NOT NULL REFERENCES users(id),
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 9. 成熟度评估 (Maturity Assessment)
-- ============================================================

-- 9.1 评估主表
CREATE TABLE IF NOT EXISTS maturity_assessments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_type VARCHAR(30) NOT NULL,              -- overall/process/department
    area_name       VARCHAR(100) NOT NULL,             -- 评估区域
    assessor_id     INTEGER     NOT NULL REFERENCES users(id),
    factory_id      INTEGER     NOT NULL REFERENCES factories(id),
    overall_level   VARCHAR(20),                       -- L1_initial/L2_managed/L3_defined/L4_optimized/L5_excellent
    total_score     DECIMAL(6,2),
    max_score       DECIMAL(6,2) NOT NULL DEFAULT 100,
    status          VARCHAR(20) NOT NULL DEFAULT 'draft', -- draft/in_progress/completed
    summary         TEXT,                              -- 评估总结
    recommendations TEXT,                              -- 改善建议
    assessment_date DATE,
    completed_at    DATETIME,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 9.2 评估维度（一级指标）
CREATE TABLE IF NOT EXISTS maturity_dimensions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id   INTEGER     NOT NULL REFERENCES maturity_assessments(id) ON DELETE CASCADE,
    dimension_name  VARCHAR(100) NOT NULL,             -- 维度名称
    weight          DECIMAL(3,2) NOT NULL DEFAULT 0.25, -- 权重
    score           DECIMAL(6,2),                      -- 得分
    max_score       DECIMAL(6,2) NOT NULL DEFAULT 25,
    level           VARCHAR(20),                       -- L1-L5
    findings        TEXT,                              -- 发现
    action_items    TEXT,                              -- 改善行动项
    sort_order      INTEGER NOT NULL DEFAULT 0,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 9.3 评估细项（二级指标）
CREATE TABLE IF NOT EXISTS maturity_criteria (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    dimension_id          INTEGER     NOT NULL REFERENCES maturity_dimensions(id) ON DELETE CASCADE,
    criterion_name        VARCHAR(200) NOT NULL,
    description           TEXT,
    weight                DECIMAL(3,2) NOT NULL DEFAULT 0.1,
    score                 DECIMAL(5,2),
    max_score             DECIMAL(5,2) NOT NULL DEFAULT 5,
    level                 VARCHAR(10),                    -- L1-L5
    evidence              TEXT,                           -- 证据/依据
    remarks               TEXT,
    improvement_suggestion TEXT,                           -- 改善建议
    sort_order            INTEGER NOT NULL DEFAULT 0,
    created_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 10. 操作审计日志 (Audit Log)
-- ============================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER     REFERENCES users(id),
    factory_id  INTEGER     REFERENCES factories(id),
    action      VARCHAR(30) NOT NULL,                   -- create/update/delete/approve/login/logout
    resource    VARCHAR(50) NOT NULL,                   -- 资源类型
    resource_id INTEGER,                                -- 资源ID
    detail      TEXT,                                   -- 变更详情 JSON
    ip_address  VARCHAR(45),
    user_agent  VARCHAR(255),
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 索引
-- ============================================================

-- 用户相关
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_ufr_user ON user_factory_roles(user_id);
CREATE INDEX idx_ufr_factory ON user_factory_roles(factory_id);
CREATE INDEX idx_ufr_role ON user_factory_roles(role_id);

-- 工作流
CREATE INDEX idx_wf_entity ON workflow_states(entity_type, entity_id);
CREATE INDEX idx_wf_assigned ON workflow_states(assigned_to_id);
CREATE INDEX idx_wf_state ON workflow_states(current_state);
CREATE INDEX idx_wfl_state ON workflow_logs(state_id);
CREATE INDEX idx_wfl_operator ON workflow_logs(operator_id);

-- 改善提案
CREATE INDEX idx_kaizen_submitter ON kaizen_proposals(submitter_id);
CREATE INDEX idx_kaizen_factory ON kaizen_proposals(factory_id);
CREATE INDEX idx_kaizen_status ON kaizen_proposals(status);
CREATE INDEX idx_kaizen_created ON kaizen_proposals(created_at);
CREATE INDEX idx_kaizen_comments_proposal ON kaizen_comments(proposal_id);
CREATE INDEX idx_kaizen_attach_proposal ON kaizen_attachments(proposal_id);

-- 5S 审核
CREATE INDEX idx_fives_audit_area ON five_s_audits(area_id);
CREATE INDEX idx_fives_audit_factory ON five_s_audits(factory_id);
CREATE INDEX idx_fives_audit_auditor ON five_s_audits(auditor_id);
CREATE INDEX idx_fives_audit_date ON five_s_audits(scheduled_date);
CREATE INDEX idx_fives_items_audit ON five_s_items(audit_id);
CREATE INDEX idx_fives_impr_audit ON five_s_improvements(audit_id);
CREATE INDEX idx_fives_impr_assigned ON five_s_improvements(assigned_to_id);

-- 培训
CREATE INDEX idx_training_session_factory ON training_sessions(factory_id);
CREATE INDEX idx_training_session_trainer ON training_sessions(trainer_id);
CREATE INDEX idx_training_session_date ON training_sessions(scheduled_date);
CREATE INDEX idx_training_enroll_session ON training_enrollments(session_id);
CREATE INDEX idx_training_enroll_user ON training_enrollments(user_id);
CREATE INDEX idx_training_materials_session ON training_materials(session_id);

-- TPM 设备
CREATE INDEX idx_tpm_equip_factory ON tpm_equipment(factory_id);
CREATE INDEX idx_tpm_equip_type ON tpm_equipment(equipment_type);
CREATE INDEX idx_tpm_equip_status ON tpm_equipment(status);
CREATE INDEX idx_tpm_plan_equip ON tpm_maintenance_plans(equipment_id);
CREATE INDEX idx_tpm_plan_due ON tpm_maintenance_plans(next_due);
CREATE INDEX idx_tpm_record_plan ON tpm_maintenance_records(plan_id);
CREATE INDEX idx_tpm_record_equip ON tpm_maintenance_records(equipment_id);
CREATE INDEX idx_tpm_fault_equip ON tpm_faults(equipment_id);
CREATE INDEX idx_tpm_fault_status ON tpm_faults(status);
CREATE INDEX idx_tpm_fault_reported ON tpm_faults(reported_at);

-- 项目管理
CREATE INDEX idx_project_factory ON projects(factory_id);
CREATE INDEX idx_project_owner ON projects(owner_id);
CREATE INDEX idx_project_status ON projects(status);
CREATE INDEX idx_project_milestone_project ON project_milestones(project_id);
CREATE INDEX idx_project_task_project ON project_tasks(project_id);
CREATE INDEX idx_project_task_assigned ON project_tasks(assigned_to_id);
CREATE INDEX idx_project_task_status ON project_tasks(status);
CREATE INDEX idx_project_member_project ON project_members(project_id);
CREATE INDEX idx_project_update_project ON project_updates(project_id);

-- Best Practice
CREATE INDEX idx_bp_author ON best_practices(author_id);
CREATE INDEX idx_bp_factory ON best_practices(factory_id);
CREATE INDEX idx_bp_category ON best_practices(category, subcategory);
CREATE INDEX idx_bp_status ON best_practices(status);
CREATE INDEX idx_bp_votes_practice ON best_practice_votes(practice_id);
CREATE INDEX idx_bp_comments_practice ON best_practice_comments(practice_id);
CREATE INDEX idx_bp_attach_practice ON best_practice_attachments(practice_id);

-- 成熟度评估
CREATE INDEX idx_maturity_factory ON maturity_assessments(factory_id);
CREATE INDEX idx_maturity_assessor ON maturity_assessments(assessor_id);
CREATE INDEX idx_maturity_date ON maturity_assessments(assessment_date);
CREATE INDEX idx_maturity_dim_assessment ON maturity_dimensions(assessment_id);
CREATE INDEX idx_maturity_criteria_dim ON maturity_criteria(dimension_id);

-- 审计日志
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_resource ON audit_logs(resource, resource_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at);
CREATE INDEX idx_audit_action ON audit_logs(action);

-- ============================================================
-- 触发器：自动更新 updated_at
-- ============================================================

CREATE TRIGGER trg_factories_updated AFTER UPDATE ON factories
BEGIN UPDATE factories SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER trg_departments_updated AFTER UPDATE ON departments
BEGIN UPDATE departments SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER trg_users_updated AFTER UPDATE ON users
BEGIN UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER trg_kaizen_updated AFTER UPDATE ON kaizen_proposals
BEGIN UPDATE kaizen_proposals SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER trg_fives_audit_updated AFTER UPDATE ON five_s_audits
BEGIN UPDATE five_s_audits SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER trg_fives_impr_updated AFTER UPDATE ON five_s_improvements
BEGIN UPDATE five_s_improvements SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER trg_training_updated AFTER UPDATE ON training_sessions
BEGIN UPDATE training_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER trg_tpm_equip_updated AFTER UPDATE ON tpm_equipment
BEGIN UPDATE tpm_equipment SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER trg_tpm_plan_updated AFTER UPDATE ON tpm_maintenance_plans
BEGIN UPDATE tpm_maintenance_plans SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER trg_tpm_fault_updated AFTER UPDATE ON tpm_faults
BEGIN UPDATE tpm_faults SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER trg_project_updated AFTER UPDATE ON projects
BEGIN UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER trg_project_milestone_updated AFTER UPDATE ON project_milestones
BEGIN UPDATE project_milestones SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER trg_project_task_updated AFTER UPDATE ON project_tasks
BEGIN UPDATE project_tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER trg_bp_updated AFTER UPDATE ON best_practices
BEGIN UPDATE best_practices SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER trg_maturity_updated AFTER UPDATE ON maturity_assessments
BEGIN UPDATE maturity_assessments SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER trg_wf_updated AFTER UPDATE ON workflow_states
BEGIN UPDATE workflow_states SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;
