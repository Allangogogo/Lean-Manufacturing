# LeanOps 数据库 ER 设计

## ER 关系图

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   factories  │     │  departments │     │    roles     │
│──────────────│     │──────────────│     │──────────────│
│ id (PK)      │◄──┐│ id (PK)      │     │ id (PK)      │
│ name         │   ││ factory_id(FK)│────►│ name         │
│ code         │   ││ name         │     │ code         │
│ address      │   ││ parent_id(FK)│──┐  │ description  │
│ is_active    │   │└──────────────┘  │  └──────────────┘
└──────────────┘   │                   │        │
                   │                   │        │
┌──────────────┐   │  ┌────────────────┴────┐   │  ┌──────────────┐
│    users     │   │  │ user_factory_roles  │   │  │permissions   │
│──────────────│   │  │─────────────────────│   │  │──────────────│
│ id (PK)      │◄──┤  │ user_id (FK)        │───┘  │ id (PK)      │
│ username     │   │  │ factory_id (FK)     │      │ role_id (FK) │
│ password_hash│   │  │ role_id (FK)        │      │ resource     │
│ display_name │   │  │ department_id (FK)  │      │ action       │
│ email        │   │  │ is_default          │      │ description  │
│ phone        │   │  │ created_at          │      └──────────────┘
│ avatar       │   │  └─────────────────────┘
│ is_active    │   │
│ created_at   │   │  ┌─────────────────────────────────────────┐
│ updated_at   │   │  │           workflow_states               │
└──────┬───────┘   │  │─────────────────────────────────────────│
       │           │  │ id (PK)                                  │
       │           │  │ entity_type (kaizen/5s/project/...)       │
       │           │  │ entity_id                                 │
       │           │  │ current_state                             │
       │           │  │ assigned_to_id (FK → users)              │
       │           │  │ created_by_id (FK → users)               │
       │           │  │ created_at / updated_at                  │
       │           │  └─────────────────────────────────────────┘
       │           │
       │           │  ┌─────────────────────────────────────────┐
       │           │  │           workflow_logs                  │
       │           │  │─────────────────────────────────────────│
       │           │  │ id (PK)                                  │
       │           │  │ state_id (FK → workflow_states)          │
       │           │  │ from_state → to_state                    │
       │           │  │ action (submit/approve/reject/return)    │
       │           │  │ operator_id (FK → users)                │
       │           │  │ comment                                  │
       │           │  │ created_at                               │
       │           │  └─────────────────────────────────────────┘
       │           │
       ├───────────┼──────────────────────────────────────────────────────
       │           │
       ▼           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        业务实体表                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │kaizen_      │  │five_s_      │  │training_    │                │
│  │proposals    │  │audits       │  │sessions     │                │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤                │
│  │ id          │  │ id          │  │ id          │                │
│  │ title       │  │ area_name   │  │ title       │                │
│  │ description │  │ audit_type  │  │ description │                │
│  │ category    │  │ auditor_id  │  │ trainer_id  │                │
│  │ submitter_id│  │ factory_id  │  │ factory_id  │                │
│  │ factory_id  │  │ score       │  │ level       │                │
│  │ status      │  │ max_score   │  │ status      │                │
│  │ priority    │  │ status      │  │ scheduled_  │                │
│  │ expected_   │  │ scheduled_  │  │ date        │                │
│  │  benefit    │  │ date        │  │ duration_   │                │
│  │ actual_     │  │ completed_  │  │ hours       │                │
│  │  benefit    │  │ date        │  └──────┬──────┘                │
│  └──────┬──────┘  └──────┬──────┘         │                       │
│         │                │                │                       │
│         ▼                ▼                ▼                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │kaizen_      │  │five_s_      │  │training_    │                │
│  │comments     │  │items        │  │enrollments  │                │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤                │
│  │ id          │  │ id          │  │ id          │                │
│  │ proposal_id │  │ audit_id    │  │ session_id  │                │
│  │ user_id     │  │ item_name   │  │ user_id     │                │
│  │ action      │  │ description │  │ status      │                │
│  │ comment     │  │ weight      │  │ score       │                │
│  └─────────────┘  │ score       │  └─────────────┘                │
│                    │ max_score   │                                  │
│  ┌─────────────┐  │ photo_path  │                                  │
│  │kaizen_      │  │ remarks     │                                  │
│  │attachments  │  └──────┬──────┘                                  │
│  ├─────────────┤         │                                         │
│  │ id          │         ▼                                         │
│  │ proposal_id │  ┌─────────────┐                                  │
│  │ filename    │  │five_s_      │                                  │
│  │ filepath    │  │improvements │                                  │
│  │ uploaded_by │  ├─────────────┤                                  │
│  └─────────────┘  │ id          │                                  │
│                    │ audit_id    │                                  │
│  ┌─────────────┐  │ item_desc   │                                  │
│  │tpm_         │  │ assigned_to │                                  │
│  │equipment    │  │ status      │                                  │
│  ├─────────────┤  │ due_date    │                                  │
│  │ id          │  └─────────────┘                                  │
│  │ equipment_  │                                                   │
│  │  code       │  ┌─────────────┐  ┌─────────────┐                │
│  │ equipment_  │  │projects     │  │best_        │                │
│  │  name       │  ├─────────────┤  │practices    │                │
│  │ equipment_  │  │ id          │  ├─────────────┤                │
│  │  type       │  │ name        │  │ id          │                │
│  │ location    │  │ description │  │ title       │                │
│  │ factory_id  │  │ project_type│  │ description │                │
│  │ status      │  │ owner_id    │  │ category    │                │
│  └──────┬──────┘  │ factory_id  │  │ subcategory │                │
│         │         │ status      │  │ author_id   │                │
│         ▼         │ priority    │  │ factory_id  │                │
│  ┌─────────────┐  │ start_date  │  │ status      │                │
│  │tpm_         │  │ target_end_ │  │ problem_    │                │
│  │maintenance_ │  │  date       │  │  statement  │                │
│  │plans        │  └──────┬──────┘  │ solution    │                │
│  ├─────────────┤         │         │ results     │                │
│  │ id          │         ▼         └──────┬──────┘                │
│  │ equipment_id│  ┌─────────────┐         │                       │
│  │ plan_type   │  │project_     │         ▼                       │
│  │ task_desc   │  │milestones   │  ┌─────────────┐                │
│  │ checklist   │  ├─────────────┤  │best_practice│                │
│  │ frequency_  │  │ id          │  │_votes       │                │
│  │  days       │  │ project_id  │  ├─────────────┤                │
│  │ assigned_to │  │ name        │  │ id          │                │
│  └──────┬──────┘  │ target_date │  │ practice_id │                │
│         │         │ status      │  │ user_id     │                │
│         ▼         └─────────────┘  │ vote_type   │                │
│  ┌─────────────┐                   └─────────────┘                │
│  │tpm_         │  ┌─────────────┐  ┌─────────────┐                │
│  │maintenance_ │  │project_     │  │best_practice│                │
│  │records      │  │tasks        │  │_comments    │                │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤                │
│  │ id          │  │ id          │  │ id          │                │
│  │ plan_id     │  │ project_id  │  │ practice_id │                │
│  │ equipment_id│  │ milestone_id│  │ user_id     │                │
│  │ executor_id │  │ name        │  │ comment     │                │
│  │ status      │  │ assigned_to │  │ rating      │                │
│  │ started_at  │  │ status      │  └─────────────┘                │
│  │ completed_at│  │ priority    │                                  │
│  │ findings    │  │ due_date    │  ┌─────────────┐                │
│  │ issues_found│  └─────────────┘  │maturity_    │                │
│  └─────────────┘                   │assessments  │                │
│                                    ├─────────────┤                │
│  ┌─────────────┐  ┌─────────────┐  │ id          │                │
│  │tpm_faults   │  │project_     │  │ assessment_ │                │
│  ├─────────────┤  │members      │  │  type       │                │
│  │ id          │  ├─────────────┤  │ area_name   │                │
│  │ equipment_id│  │ id          │  │ assessor_id │                │
│  │ reporter_id │  │ project_id  │  │ factory_id  │                │
│  │ fault_type  │  │ user_id     │  │ overall_    │                │
│  │ severity    │  │ role        │  │  level      │                │
│  │ status      │  └─────────────┘  │ total_score │                │
│  │ reported_at │                   │ status      │                │
│  │ root_cause  │  ┌─────────────┐  └──────┬──────┘                │
│  └─────────────┘  │project_     │         │                       │
│                    │updates      │         ▼                       │
│  ┌─────────────┐  ├─────────────┤  ┌─────────────┐                │
│  │training_    │  │ id          │  │maturity_    │                │
│  │materials    │  │ project_id  │  │dimensions   │                │
│  ├─────────────┤  │ author_id   │  ├─────────────┤                │
│  │ id          │  │ progress_   │  │ id          │                │
│  │ session_id  │  │  pct        │  │ assessment_ │                │
│  │ material_   │  │ accomplish- │  │  id         │                │
│  │  name       │  │  ments      │  │ dimension_  │                │
│  │ material_   │  │ plan_next_  │  │  name       │                │
│  │  type       │  │  week       │  │ weight      │                │
│  │ filepath    │  │ risks_issues│  │ score       │                │
│  │ uploaded_by │  └─────────────┘  │ level       │                │
│  └─────────────┘                   └──────┬──────┘                │
│                                            │                       │
│                                            ▼                       │
│                                    ┌─────────────┐                │
│                                    │maturity_    │                │
│                                    │criteria     │                │
│                                    ├─────────────┤                │
│                                    │ id          │                │
│                                    │ dimension_id│                │
│                                    │ criterion_  │                │
│                                    │  name       │                │
│                                    │ weight      │                │
│                                    │ score       │                │
│                                    │ evidence    │                │
│                                    └─────────────┘                │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    audit_logs                                │  │
│  ├─────────────────────────────────────────────────────────────┤  │
│  │ id | user_id | action | resource | resource_id | detail     │  │
│  │ ip_address | user_agent | created_at                        │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## 表清单

| # | 表名 | 说明 | 预估行数 |
|---|------|------|---------|
| 1 | factories | 工厂 | 1-10 |
| 2 | departments | 部门 | 10-50 |
| 3 | roles | 角色 | 4 |
| 4 | permissions | 角色权限 | 50-100 |
| 5 | users | 用户 | 50-500 |
| 6 | user_factory_roles | 用户-工厂-角色关联 | 100-1000 |
| 7 | workflow_states | 工作流状态 | 100-1000 |
| 8 | workflow_logs | 工作流日志 | 500-10000 |
| 9 | kaizen_proposals | 改善提案 | 100-5000 |
| 10 | kaizen_comments | 提案评论 | 500-20000 |
| 11 | kaizen_attachments | 提案附件 | 200-5000 |
| 12 | five_s_areas | 5S 审核区域 | 10-50 |
| 13 | five_s_audits | 5S 审核记录 | 500-5000 |
| 14 | five_s_items | 5S 审核细项 | 2500-25000 |
| 15 | five_s_improvements | 5S 改善跟踪 | 200-5000 |
| 16 | training_sessions | 培训场次 | 50-500 |
| 17 | training_enrollments | 培训报名 | 500-5000 |
| 18 | training_materials | 培训材料 | 100-1000 |
| 19 | tpm_equipment | 设备台账 | 50-500 |
| 20 | tpm_maintenance_plans | 维护计划 | 100-1000 |
| 21 | tpm_maintenance_records | 维护记录 | 1000-20000 |
| 22 | tpm_faults | 设备故障 | 100-5000 |
| 23 | projects | 项目 | 10-100 |
| 24 | project_milestones | 项目里程碑 | 30-300 |
| 25 | project_tasks | 项目任务 | 100-1000 |
| 26 | project_members | 项目成员 | 50-500 |
| 27 | project_updates | 项目周报 | 100-1000 |
| 28 | best_practices | 最佳实践 | 50-500 |
| 29 | best_practice_votes | 点赞/收藏 | 200-5000 |
| 30 | best_practice_comments | 实践评论 | 200-5000 |
| 31 | best_practice_attachments | 实践附件 | 50-500 |
| 32 | maturity_assessments | 成熟度评估 | 20-200 |
| 33 | maturity_dimensions | 评估维度 | 80-800 |
| 34 | maturity_criteria | 评估细项 | 400-4000 |
| 35 | audit_logs | 操作审计日志 | 10000-100000 |

共 **35 张表**，预估数据量 10 万行以内，SQLite 完全胜任。
