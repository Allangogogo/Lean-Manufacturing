# WIP（在制品）管理 Dashboard 设计方案

> 版本：v1.0 | 日期：2026-08-16 | 状态：待评审
> 前置依赖：双后端合并（见 `backend-merge-plan.md`），本方案基于合并后的 lean-ops 单后端

---

## 1. 业务背景与目标

### 1.1 为什么做 WIP 管理
精益生产中，**在制品（Work-In-Process）是七大浪费中"库存浪费"的核心**：
- 在制品过多 → 资金占用、质量问题放大（缺陷晚发现）、生产周期（LT）拉长、柔性下降
- 在制品过少 → 断料、设备闲置、产出不稳
- **目标是：找到并维持最优 WIP 水位（Little's Law: WIP = TH × CT）**

### 1.2 现状缺口（基于 leanops.db 实测）
| 维度 | 现状 | 缺口 |
|---|---|---|
| 数据 | 49 张表：设备/5S/Kaizen/项目/培训/成熟度 | **无生产工单、无工序流转、无在制量记录** |
| 工序链 | 泛化后：机加工→精加工→热处理→表面处理→装配→包装 | 无工序级数据表 |
| 设备 | tpm_equipment（10 台，含工序类型） | 设备无"当前加工件/产量/节拍"实时字段 |
| 项目 | project_tasks（改进项目任务） | 与生产在制无关 |

**结论：WIP Dashboard 需要新增生产执行数据模型**（工单/工序在制/流转记录），这是本方案的核心设计点。

---

## 2. 数据模型设计（新增 4 张表）

### 2.1 生产工单 `production_orders`（主表）
```sql
CREATE TABLE production_orders (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    order_no      TEXT NOT NULL UNIQUE,          -- 工单号：PO-20260816-001
    product_name  TEXT NOT NULL,                  -- 产品名称
    product_code  TEXT,                           -- 产品编码
    quantity      INTEGER NOT NULL,               -- 计划数量
    priority      TEXT DEFAULT 'normal',          -- high/medium/low
    status        TEXT DEFAULT 'pending',         -- pending/in_progress/completed/on_hold
    factory_id    INTEGER,                        -- FK factories.id
    planned_start DATE,
    planned_end   DATE,
    actual_start  DATETIME,
    actual_end    DATETIME,
    created_by    INTEGER,                        -- FK users.id
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2 工序在制 `work_order_operations`（核心 WIP 表）
```sql
CREATE TABLE work_order_operations (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id       INTEGER NOT NULL,              -- FK production_orders.id
    sequence_no    INTEGER NOT NULL,              -- 工序顺序 1..6
    operation_name TEXT NOT NULL,                 -- 机加工/精加工/热处理/表面处理/装配/包装
    equipment_id   INTEGER,                       -- FK tpm_equipment.id（关联设备）
    input_qty      INTEGER,                       -- 投入数量
    output_qty     INTEGER,                       -- 产出数量
    wip_qty        INTEGER,                       -- 当前在制（= input - output）
    status         TEXT DEFAULT 'pending',        -- pending/in_progress/completed
    start_time     DATETIME,
    end_time       DATETIME,
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);
```
> **WIP 水位 = Σ(input_qty - output_qty) for status='in_progress'**，即各工序当前积压量。

### 2.3 流转记录 `wip_transactions`（审计/趋势）
```sql
CREATE TABLE wip_transactions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id  INTEGER NOT NULL,               -- FK work_order_operations.id
    transaction_type TEXT NOT NULL,               -- move_in/move_out/complete
    quantity      INTEGER NOT NULL,
    from_operation INTEGER,                       -- 上道工序 id（move_in 时）
    to_operation   INTEGER,                       -- 下道工序 id（move_out 时）
    operator_id   INTEGER,                        -- FK users.id
    occurred_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 2.4 每日水位快照 `wip_daily_snapshots`（趋势图数据）
```sql
CREATE TABLE wip_daily_snapshots (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_date  DATE NOT NULL,
    factory_id     INTEGER,
    operation_name TEXT,
    wip_qty        INTEGER,
    throughput     INTEGER,                       -- 当日产出
    cycle_time_min INTEGER,                       -- 平均节拍(分钟)
    UNIQUE(snapshot_date, factory_id, operation_name)
);
```
> 每日定时任务（cron）或当日结束时写入，支撑趋势图。

---

## 3. Dashboard 页面设计（合并后 lean-ops 体系）

### 3.1 路由与 API
```
页面：/wip                          → templates/wip/dashboard.html
API：
GET  /api/v1/wip/overview           → 全局指标卡
GET  /api/v1/wip/operations         → 工序 WIP 水位（柱状图）
GET  /api/v1/wip/orders?status=     → 工单列表
GET  /api/v1/wip/orders/{id}        → 工单详情（各工序进度）
POST /api/v1/wip/orders             → 创建工单
POST /api/v1/wip/operations/{id}/move  → 工序流转（登记 in/out）
GET  /api/v1/wip/trends?days=30     → 水位趋势（折线图）
GET  /api/v1/wip/bottlenecks        → 瓶颈识别（WIP 最高的工序 + 等待时间）
```

### 3.2 页面布局（信息密度高，麦肯锡风格）

```
┌─────────────────────────────────────────────────────────────┐
│ WIP 在制品管理                                    [新建工单] │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│ 总在制   │ 在制工单 │ 今日产出 │ 平均LT   │ 瓶颈工序       │
│ 3,280件  │ 12 单    │ 1,150件  │ 4.2天    │ 热处理 (820件) │
│ ▲12%    │ 8 进行中 │ ▲8%     │ ▼0.3天  │ 等待 2.1 天    │
├──────────┴──────────┴──────────┴──────────┴────────────────┤
│ 工序 WIP 水位（堆积图）                                    │
│ ┌─────────────────────────────────────────────┐            │
│ │ 机加工 ████ 520   精加工 ███ 380             │            │
│ │ 热处理 ██████ 820  表面处理 ████ 560          │            │
│ │ 装配 ██ 240   包装 █ 120   【红黄绿灯】      │            │
│ └─────────────────────────────────────────────┘            │
├──────────────────────────────┬──────────────────────────────┤
│ WIP 趋势（30 天折线）        │ 在制工单列表                 │
│                              │ PO-20260816-001 机加工 60%  │
│  ── 总WIP ── 目标水位        │ PO-20260816-002 热处理 40%  │
│                              │ ...                          │
├──────────────────────────────┴──────────────────────────────┤
│ 工单详情展开：                                               │
│ 机加工 ██████ 500/600 精加工 ████ 400/600                  │
│ 热处理 ██████ 480/600 [瓶颈!] 表面 ██ 200/600              │
│ 装配 ██ 150/600   包装 █ 80/600   [推进流转] [登记产出]     │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 核心指标（KPI 定义）
| 指标 | 公式 | 红黄绿阈值（示例） |
|---|---|---|
| 总在制 | Σ 各工序 wip_qty | 绿 < 3000 / 黄 3000-5000 / 红 > 5000 |
| 工序水位 | 单工序 wip_qty | 相对该工序标准水位 ±20% |
| 平均提前期 LT | Σ(完成时间-开始时间)/单数 | 绿 < 4 天 / 红 > 6 天 |
| 今日产出 | 当日 move_out 总量 | 与目标产出比 |
| 瓶颈工序 | max(wip_qty) 或 max(等待时间) | 自动标记 ⚠ |
| WIP 周转率 | 产出 / 平均 WIP | 越高越好 |

### 3.4 关键交互
1. **新建工单**：产品、数量、优先级、计划起止 → POST /wip/orders
2. **流转登记**：任一工序"登记投入/产出/完成" → 自动更新上/下工序 wip_qty + 写 wip_transactions
3. **瓶颈预警**：wip_qty > 阈值时页面红色高亮 + 侧边栏角标
4. **趋势下钻**：点击折线图某天 → 看当日各工序水位明细

---

## 4. 实施步骤

### Phase A：数据层（0.5-1 天）
- [ ] lean-ops 新增 models/wip.py（4 张表 ORM 定义）
- [ ] alembic 迁移或手写 migrate_wip.py（沿用项目现有 migrate 模式）
- [ ] 种子数据：6 道工序模板 + 示例工单 3 单 + 历史快照 30 天（供趋势图演示）

### Phase B：API 层（1 天）
- [ ] api/v1/wip.py：8 个端点（§3.1）
- [ ] services/wip_service.py：WIP 计算、瓶颈识别、趋势聚合
- [ ] schemas/wip.py：Pydantic 校验

### Phase C：前端（1.5-2 天）
- [ ] templates/wip/dashboard.html（按 lean-ops design-system 组件）
- [ ] 图表：Chart.js（水位堆积柱状图 + 趋势折线图）
- [ ] Alpine.js 交互：新建工单表单、流转登记弹窗、工单详情展开
- [ ] 侧边栏导航加入 WIP 入口

### Phase D：报表与优化（1 天，可选）
- [ ] wip_daily_snapshots 定时快照（cron 或启动任务）
- [ ] 报表中心加入 WIP 周报导出
- [ ] 与 tpm_equipment 联动：设备停机时该工序水位预警

**总工期：约 4-5.5 个工作日**

---

## 5. 与现有系统的关系

| 现有模块 | 关联方式 |
|---|---|
| tpm_equipment | work_order_operations.equipment_id 关联，设备停机 → 工序水位预警 |
| five_s_areas | 区域可映射到工序（机加工区/精加工区等），共享工厂维度 |
| projects | 改进项目可关联到瓶颈工序（如"热处理瓶颈改善项目"） |
| users/roles | 流转登记 operator_id、工单 created_by |
| factories | 多工厂维度（当前单工厂，预留） |
| automation_maturity | 工序自动化水平影响 WIP 目标水位设定 |

---

## 6. 后续演进（Roadmap）

| 阶段 | 内容 | 价值 |
|---|---|---|
| v1（本期） | WIP 水位看板 + 工单管理 + 流转登记 | 看清在制现状 |
| v2 | 目标水位设定（按工序节拍/产能计算）+ 看板拉动（Kanban 电子化） | 从"看到"到"控制" |
| v3 | 与 MES/IoT 实时对接（PLC 产量信号 → 自动更新 wip_qty） | 实时化、免人工登记 |
| v4 | 约束理论（TOC）集成：瓶颈排产建议、DBR 缓冲管理 | 主动优化 |

---

## 7. 验收标准
- [ ] `/wip` 页面可访问，6 大 KPI 卡 + 水位图 + 趋势图 + 工单列表全部渲染
- [ ] 新建工单 → 流转登记 → 完成，全流程数据正确落库
- [ ] 瓶颈工序自动识别并高亮
- [ ] 30 天趋势图有数据（种子或真实）
- [ ] 全量 API 测试通过
