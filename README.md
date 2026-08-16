# 精益制造管理系统 (Lean Manufacturing Management System)

> 面向离散制造企业的精益转型全生命周期知识库 + Web 管理系统。
> 覆盖精益工具知识库、培训体系、成熟度评估、实施战略、项目管理与数字化运营看板。

| 元数据 | 值 |
|--------|-----|
| 版本 | v2.0.0 |
| 适用行业 | 离散制造（机加工 → 精加工 → 热处理 → 表面处理 → 装配 → 包装） |
| 技术栈 | Python · FastAPI/Starlette · SQLite · Jinja2 · Alpine.js · TailwindCSS |
| 目标成熟度 | L2 → L4，周期 36 个月 |
| 文档总数 | ~117 份（Markdown + Excel 模板） |

---

## 仓库结构

```
lean-management-system/
├── webapp/                     # Lean 管理 Web 应用
│   ├── app.py                  # FastAPI/Starlette 主应用（16 个页面路由 + API）
│   ├── seed_lean20.py          # Lean 2.0 / Industry 5.0 维度种子数据
│   ├── static/                 # CSS / JS 前端资源
│   └── templates/              # Jinja2 页面模板（16 页统一 Linear/Vercel 风格）
│
├── lean-ops/                   # 运营后端（FastAPI + SQLAlchemy 2.0 异步 ORM）
│   ├── app/                    # API 路由（auth/dashboard/kaizen/fives/training/tpm/
│   │                          #   projects/practices/maturity/admin/reports/wip 等 19 模块）
│   ├── app/models/             # SQLAlchemy ORM 模型
│   ├── app/schemas/            # Pydantic 请求/响应模型
│   ├── app/services/           # 业务逻辑层
│   ├── app/templates/          # Jinja2 页面模板
│   ├── migrate_*.py            # 数据库迁移与种子脚本
│   ├── scripts/                # 种子数据与工具脚本（rebuild_db.py 一键重建）
│   ├── tests/                  # pytest 测试
│   ├── data/leanops.db         # SQLite 生产数据库（不入库，rebuild_db.py 重建）
│   └── Dockerfile / docker-compose.yml
│
├── 01-精益工具知识库/           # 精益哲学、13 个核心工具、问题解决方法、行业应用
├── 02-精益培训/                 # 培训策略、材料、计划、模板、效果评估
├── 03-成熟度评估/               # 5 级成熟度模型、工厂整体/局部评估
├── 04-实施战略/                 # 5 阶段路线图、实施工具模板
├── 05-项目管理/                 # 项目章程、进度/风险/绩效管理模板
├── appendix/                   # 术语表、参考文献、模板说明
├── docs/                       # 补充文档（backend-merge-plan.md 后端合并方案、
│                               #   wip-dashboard-design.md WIP 看板设计）
├── convert_md_to_office.py     # 知识库 Markdown → Office(docx/xlsx/pptx) 生成器
├── create_methodology_docs.py  # 世界级制造方法论文档/培训 PPT 生成器
├── CLAUDE.md                   # AI 助手导航索引
└── README.md                   # 本文件
```

---

## Web 应用快速启动

### 环境要求

- Python 3.10+
- `uvicorn`（已包含在标准 Starlette/FastAPI 工作流中）

### 启动服务

```bash
cd lean-ops
python run.py
```

服务默认运行在 `http://localhost:8000`。

### 数据库初始化

数据库文件（`data/leanops.db`）不入库（见 `.gitignore`），首次启动或重置数据时运行一键重建：

```bash
cd lean-ops
py scripts/rebuild_db.py
```

该脚本自动完成：ORM 建表（43 张）→ migrate 脚本建表（9 张）→ 种子数据（工厂/角色/权限/部门/用户/5S/Lean 2.0 清单/支柱/WIP 工单）。默认登录账号见脚本输出（密码均为 `123456`）。

### 访问页面

| 页面 | 路径 | 说明 |
|------|------|------|
| 首页仪表盘 | `/` | KPI 汇总、近期项目、成熟度概览 |
| 知识库 | `/knowledge` | 精益知识库文件浏览 |
| 成熟度评估 | `/assessment` | 工厂/工序维度评分与报告 |
| 精益 2.0 评估 | `/lean20_assess` | Industry 5.0 扩展维度评估 |
| 培训管理 | `/training` | 培训体系与效果跟踪 |
| 项目管理 | `/projects` | 改善项目列表与详情 |
| 项目管理详情 | `/project/{id}` | 单项目进度/风险/绩效 |
| 5S & Kaizen | `/fives-kaizen` | 5S 审核与 Kaizen 事件 |
| TPM | `/tpm` | 全面生产维护 |
| 自动化 | `/automation` | 自动化与数字化项目 |
| 最佳实践 | `/best-practices` | 知识沉淀 |
| 实施战略 | `/implementation` | 精益转型实施路线图 |
| 精益 2.0 | `/lean20` | Industry 5.0 融合框架 |
| 八大支柱 | `/pillars` | 精益运营支柱 |
| 生产运维 WIP | `/wip` | 在制品水位看板（工单/工序/流转） |
| 搜索 | `/search` | 全文检索 |

---

## 核心模块导航

### 1. 精益工具知识库 (`01-精益工具知识库/`)

| 子目录 | 内容 |
|--------|------|
| `01-精益基础/` | 精益思想、TPS、浪费识别 |
| `02-核心工具/` | 13 个核心工具：看板、VSM、安灯、标准作业、TPM、5S、Kaizen、平准化、防错、SMED、自働化、JIT、可视化管理 |
| `03-问题解决方法/` | Gemba Walk、A3、PDCA、DMAIC、VA/VE |
| `04-制造工序应用/` | 机加工、精加工、热处理、表面处理、包装工序应用 |
| `05-实践案例集/` | SMED 改善案例、改善提案模板 |
| `06-深度专题/` | 变革管理、高级 VSM、质量标准整合、精益数字化、Industry 5.0、Leagile、韧性供应链等 |

### 2. 精益培训 (`02-精益培训/`)

- 培训体系规划
- 四层培训架构
- 培训材料、计划、模板
- 培训记录追踪
- 柯氏四级评估框架

### 3. 成熟度评估 (`03-成熟度评估/`)

- 5 级精益成熟度模型
- Lean 2.0 / Industry 5.0 扩展维度
- 工厂整体评估表（Excel）
- 5 大工序局部评估表

### 4. 实施战略 (`04-实施战略/`)

- 精益转型总体规划
- 五阶段实施路线图
- Lean 2.0 实施路线图
- 6 个实施工具模板（Kaizen、A3、VSM、标准作业、5S 审核、改善提案）

### 5. 项目管理 (`05-项目管理/`)

- 项目章程
- 进度管理
- 风险管理
- 绩效管理

---

## 关键指标（KPIs）

| 指标 | 当前基线 | 目标值 | 来源 |
|------|---------|--------|------|
| OEE | 72% | **85%** | TPM |
| 换型时间 | 60 min | **<10 min** | SMED |
| 不良率 | 2.5% | **1.0%** | Poka-Yoke |
| WIP 库存 | 3 天 | **<1 天** | Kanban |
| 交付周期 | 15 天 | **7 天** | VSM |
| 成熟度等级 | L2 | **L4** | 成熟度评估 |

---

## 使用建议

- **管理层**：从 `04-实施战略/01-精益转型总体规划.md` 入手，结合首页仪表盘看全局。
- **精益推进/教练**：使用 `01-精益工具知识库/` 做培训，`03-成熟度评估/` 跟踪进展。
- **PMO/项目经理**：使用 `05-项目管理/` 模板，参考 `04-实施战略/02-详细计划/` 制定计划。
- **工程师/班组长**：从 `01-精益工具知识库/02-核心工具/` 学具体工具，参考 `04-制造工序应用/`。
- **AI 助手**：使用 `CLAUDE.md` 作为入口，快速定位文档与数据。

---

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| v1.0.0 | 2026-04-29 | 基线建立：完成全部 5 大模块知识库文档 |
| v1.1.0 | 2026-08 | 新增 Lean Management Web 应用（16 页 UI + SQLite + API），完整数字化运营入口 |
| v2.0.0 | 2026-08 | 行业定位重构：由金属紧固件专属泛化为制造业通用（离散制造），工序链泛化为机加工/精加工/热处理/表面处理/装配/包装 |

---

## 贡献与维护

本仓库为个人精益数字化转型工作空间，持续迭代中。欢迎通过 Issue 或 PR 提交改进建议。
