# LeanOps 枚举值定义

## 1. 用户与组织

### 角色 (roles.code)
| 编码 | 名称 | 说明 |
|------|------|------|
| `admin` | 系统管理员 | 最高权限 |
| `lean_mgr` | 精益经理 | 全局精益推进、审批、评估 |
| `supervisor` | 班组长/主管 | 本组审核、任务分配 |
| `worker` | 操作员工 | 基层操作、提案提交 |
| `manager` | 高层管理 | 查看报表、审批里程碑 |

### 工厂状态 (factories.is_active)
- `1` = 启用
- `0` = 停用

---

## 2. 工作流状态

### 改善提案状态 (kaizen_proposals.status / workflow_states.current_state)
```
draft → submitted → reviewing → approved → implementing → verified → closed
                         ↓           ↓
                      rejected    returned (退回修改)
```

| 状态 | 说明 | 允许操作的角色 |
|------|------|---------------|
| `draft` | 草稿 | 提交者 |
| `submitted` | 已提交（待班组长审核） | 班组长、精益经理 |
| `reviewing` | 审核中 | 班组长、精益经理 |
| `approved` | 已批准（待实施） | 提交者、班组长 |
| `implementing` | 实施中 | 提交者、班组长、精益经理 |
| `verified` | 已验证 | 精益经理 |
| `closed` | 已关闭 | 精益经理 |
| `rejected` | 已拒绝 | 提交者（可重新提交） |
| `returned` | 已退回 | 提交者（修改后重新提交） |

### 5S 审核状态 (five_s_audits.status)
| 状态 | 说明 |
|------|------|
| `scheduled` | 已排期 |
| `in_progress` | 审核中 |
| `completed` | 已完成 |

### 5S 改善状态 (five_s_improvements.status)
| 状态 | 说明 |
|------|------|
| `open` | 待整改 |
| `in_progress` | 整改中 |
| `completed` | 已完成 |
| `verified` | 已验证 |

### 培训状态 (training_sessions.status)
| 状态 | 说明 |
|------|------|
| `scheduled` | 已排期 |
| `in_progress` | 进行中 |
| `completed` | 已完成 |
| `cancelled` | 已取消 |

### 培训报名状态 (training_enrollments.status)
| 状态 | 说明 |
|------|------|
| `enrolled` | 已报名 |
| `attended` | 已签到 |
| `absent` | 缺席 |
| `certified` | 已通过 |
| `failed` | 未通过 |

### TPM 设备状态 (tpm_equipment.status)
| 状态 | 说明 |
|------|------|
| `normal` | 正常运行 |
| `fault` | 故障中 |
| `maintenance` | 维护中 |
| `retired` | 已报废 |

### TPM 维护记录状态 (tpm_maintenance_records.status)
| 状态 | 说明 |
|------|------|
| `planned` | 已计划 |
| `in_progress` | 执行中 |
| `completed` | 已完成 |
| `overdue` | 已逾期 |

### TPM 故障状态 (tpm_faults.status)
| 状态 | 说明 |
|------|------|
| `reported` | 已报修 |
| `diagnosing` | 诊断中 |
| `repairing` | 修复中 |
| `completed` | 已修复 |

### 故障严重程度 (tpm_faults.severity)
| 级别 | 说明 |
|------|------|
| `minor` | 轻微（不影响生产） |
| `major` | 严重（影响部分产线） |
| `critical` | 紧急（全线停产） |

### 项目状态 (projects.status)
| 状态 | 说明 |
|------|------|
| `planning` | 规划中 |
| `active` | 进行中 |
| `on_hold` | 暂停 |
| `completed` | 已完成 |
| `cancelled` | 已取消 |

### 项目任务状态 (project_tasks.status)
| 状态 | 说明 |
|------|------|
| `todo` | 待办 |
| `in_progress` | 进行中 |
| `done` | 已完成 |
| `blocked` | 阻塞 |

### 里程碑状态 (project_milestones.status)
| 状态 | 说明 |
|------|------|
| `pending` | 待开始 |
| `in_progress` | 进行中 |
| `completed` | 已完成 |
| `overdue` | 已逾期 |

### Best Practice 状态 (best_practices.status)
| 状态 | 说明 |
|------|------|
| `draft` | 草稿 |
| `published` | 已发布 |
| `archived` | 已归档 |

### 成熟度评估状态 (maturity_assessments.status)
| 状态 | 说明 |
|------|------|
| `draft` | 草稿 |
| `in_progress` | 评估中 |
| `completed` | 已完成 |

### 成熟度等级
| 等级 | 名称 | 分数范围 |
|------|------|---------|
| `L1` | 初始级 | 0-20 |
| `L2` | 已管理级 | 21-40 |
| `L3` | 已定义级 | 41-60 |
| `L4` | 已优化级 | 61-80 |
| `L5` | 卓越级 | 81-100 |

---

## 3. 业务分类

### 改善提案分类 (kaizen_proposals.category)
| 编码 | 名称 |
|------|------|
| `quality` | 质量 |
| `cost` | 成本 |
| `delivery` | 交期 |
| `safety` | 安全 |
| `morale` | 士气 |
| `environment` | 环保 |

### 优先级 (通用)
| 编码 | 名称 |
|------|------|
| `low` | 低 |
| `medium` | 中 |
| `high` | 高 |
| `urgent` | 紧急 |

### 5S 维度 (five_s_items.s_category)
| 编码 | 日文 | 中文 |
|------|------|------|
| `sort` | 整理 | 区分必要/不必要物品 |
| `straighten` | 整顿 | 定位放置 |
| `shine` | 清扫 | 清洁点检 |
| `standardize` | 清洁 | 标准化 |
| `sustain` | 素养 | 习惯化 |

### 培训类型 (training_sessions.training_type)
| 编码 | 名称 |
|------|------|
| `lean_tool` | 精益工具 |
| `safety` | 安全 |
| `quality` | 质量 |
| `process` | 工艺 |
| `management` | 管理 |
| `equipment` | 设备 |

### 培训等级 (training_sessions.level)
| 编码 | 名称 | 对象 |
|------|------|------|
| `L1_basics` | 基础认知 | 全员 |
| `L2_intermediate` | 进阶应用 | 班组长/骨干 |
| `L3_advanced` | 高级实战 | 精益推进人员 |
| `L4_expert` | 专家级 | 精益经理 |

### 设备类型 (tpm_equipment.equipment_type)
| 编码 | 名称 |
|------|------|
| `cold_header` | 冷镦机 |
| `thread_roller` | 搓丝机 |
| `heat_treat` | 热处理设备 |
| `electroplating` | 电镀/表面处理设备 |
| `sorter` | 分选机 |
| `packager` | 包装机 |
| `other` | 其他 |

### 项目类型 (projects.project_type)
| 编码 | 名称 |
|------|------|
| `kaizen_event` | Kaizen 改善周 |
| `vsm_redux` | VSM 价值流优化 |
| `5s_deployment` | 5S 部署 |
| `tpm_rollout` | TPM 推行 |
| `training_program` | 培训项目 |
| `other` | 其他 |

### Best Practice 分类
| category | subcategory | 名称 |
|----------|-------------|------|
| `tool` | `kanban` | 看板 |
| `tool` | `5s` | 5S 管理 |
| `tool` | `smed` | 快速换型 |
| `tool` | `poka_yoke` | 防错 |
| `tool` | `vsm` | 价值流图 |
| `tool` | `tpm` | 全面生产维护 |
| `method` | `kaizen` | 改善 |
| `method` | `six_sigma` | 六西格玛 |
| `method` | `a3` | A3 问题解决 |
| `method` | `pdca` | PDCA 循环 |
| `method` | `fishbone` | 鱼骨图 |
| `process` | `layout` | 布局优化 |
| `process` | `flow` | 流程优化 |
| `mindset` | `leader_std_work` | 领导者标准作业 |

### 审计日志动作 (audit_logs.action)
| 编码 | 说明 |
|------|------|
| `create` | 创建 |
| `update` | 更新 |
| `delete` | 删除 |
| `approve` | 审批通过 |
| `reject` | 审批拒绝 |
| `return` | 退回修改 |
| `login` | 登录 |
| `logout` | 登出 |
| `export` | 导出 |
| `upload` | 上传 |
| `submit` | 提交 |
| `close` | 关闭 |

---

## 4. RBAC 权限资源与动作

### 资源 (permissions.resource)
`user` | `kaizen` | `fives` | `training` | `tpm` | `project` | `practice` | `maturity` | `dashboard` | `report`

### 动作 (permissions.action)
`create` | `read` | `update` | `delete` | `approve` | `export` | `manage`

### 范围 (permissions.scope)
| 编码 | 说明 |
|------|------|
| `own` | 仅自己的数据 |
| `dept` | 本部门数据 |
| `factory` | 本工厂数据 |
| `all` | 所有工厂数据 |
