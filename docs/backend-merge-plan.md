# Lean 精益制造系统：双后端合并迁移方案（P0 架构收敛）

> 版本：v1.0 | 日期：2026-08-16 | 状态：待评审
> 关联：v2.0.0 泛化重构完成后架构收敛第一步

---

## 1. 现状盘点（实测）

### 1.1 双后端共存
| 维度 | webapp/ | lean-ops/ |
|---|---|---|
| 框架 | FastAPI（`app.py` 1162 行单文件） | FastAPI + 分层架构 |
| 数据访问 | 原生 `sqlite3` 直连 | SQLAlchemy ORM（异步） |
| 数据库 | **同一个** `lean-ops/data/leanops.db` | **同一个** `lean-ops/data/leanops.db` |
| 页面 | 16 个模板（Tailwind CDN + Alpine.js + Chart.js） | 25 个模板（自研 design-system.css + Alpine.js） |
| 静态资源 | `static/app.js`(209行) + `style.css` | `static/js/app.js`(231行) + `css/*` |
| API | 约 45 个路由（`/api/v1/*` 前缀与 lean-ops 相同！） | 19 个 API 模块（router.py 聚合） |
| 启动 | `uvicorn app:app`（端口 8000） | `uvicorn app.main:app`（端口 8000） |

### 1.2 严重问题
1. **两套应用抢同一端口 8000**，不能同时运行——必须二选一
2. **同前缀 API 冲突**：webapp 和 lean-ops 都有 `/api/v1/lean20/*`、`/api/v1/pillars/*`、`/api/v1/automation/*`、`/api/v1/tpm/*`、`/api/v1/projects/*`、`/api/v1/5s|fives/*`、`/api/v1/kaizen/*`、`/api/v1/training/*`——**实现是两套，但路径相同**
3. **webapp 独有**：知识库浏览（`/knowledge`、`/file/{path}`、`/raw`、`/download`）、全文搜索（`/search`）、实施路线图（`/implementation`）、成熟度评估（`/assessment`）——lean-ops 完全没有这些页面
4. **lean-ops 独有**：登录认证（auth）、用户管理（admin）、甘特图（gantt）、风险（risks）、报表中心（reports）、项目仪表盘（project_dashboard）——webapp 没有
5. **数据一致性风险**：webapp 用 sqlite3 直连 UPDATE，lean-ops 用 ORM——两边对同一张表的写入约定（如自动计算 composite_score）可能不一致

### 1.3 重叠功能矩阵（核心结论）
| 业务域 | webapp 实现 | lean-ops 实现 | 建议保留 |
|---|---|---|---|
| Lean 2.0 成熟度 | `/api/v1/lean20/*` + `lean20.html`/`lean20_assess.html` | `/api/v1/lean20/*` + 无模板 | **lean-ops API + webapp 模板** |
| 价值支柱 Pillars | `/api/v1/pillars/*` + `pillars.html` | `/api/v1/pillars/*` + 无模板 | **lean-ops API + webapp 模板** |
| 自动化成熟度 | `/api/v1/automation/*` + `automation.html` | `/api/v1/automation/*` + 无模板 | **lean-ops API + webapp 模板** |
| TPM | `/api/v1/tpm/*` + `tpm.html` | `/api/v1/tpm/*` + `tpm/equipment.html`/`faults.html` | **lean-ops API + lean-ops 模板**（更完整） |
| 5S | `/api/v1/5s/*` + `fives-kaizen.html` | `/api/v1/fives/*` + `fives/*` | **lean-ops 全套** |
| Kaizen | `/api/v1/kaizen/*` + `fives-kaizen.html` | `/api/v1/kaizen/*` + `kaizen/*` | **lean-ops 全套** |
| 项目 | `/api/v1/projects/*` + `projects.html`/`project-detail.html` | `/api/v1/projects/*` + `project/*` | **lean-ops 全套** |
| 培训 | `/api/v1/training/*` + `training.html` | `/api/v1/training/*` + `training/*` | **lean-ops 全套** |
| Best Practices | `/api/v1/best-practices/*` + `best-practices.html` | `/api/v1/practices/*` + `practice/*` | **lean-ops 全套** |
| 成熟度评估 | `/assessment` + `assessment.html` | `/maturity/*` + `maturity/*` | **lean-ops 全套**（表单更完善） |
| 知识库 | `/knowledge` `/file/*` `/search`（独有） | — | **迁移到 lean-ops** |
| 实施路线图 | `/implementation`（独有） | — | **迁移到 lean-ops** |

---

## 2. 目标架构（合并后）

```
lean-ops/                          ← 唯一后端（保留现状结构）
├── app/
│   ├── main.py                    ← 唯一入口（端口 8000）
│   ├── api/v1/                    ← 全部 API（19 模块 + 新增知识库模块）
│   │   ├── router.py              ← 聚合全部路由
│   │   ├── knowledge.py           ← 新增：知识库浏览/搜索/文件
│   │   └── ...
│   ├── templates/                 ← 全部页面（25 现有 + 8 webapp 迁入）
│   │   ├── base.html              ← 统一壳（保留 lean-ops design-system）
│   │   ├── lean20.html            ← 迁入（适配 base.html）
│   │   ├── pillars.html           ← 迁入
│   │   ├── automation.html        ← 迁入
│   │   ├── knowledge.html         ← 迁入
│   │   ├── search.html            ← 迁入
│   │   ├── implementation.html    ← 迁入
│   │   └── assessment.html        ← 迁入
│   ├── static/                    ← 统一静态（design-system.css 为主）
│   └── ...
├── data/leanops.db                ← 唯一数据库（不变）
├── scripts/seed_data.py           ← 唯一种子
├── tests/                         ← 唯一测试
└── ...
webapp/                            ← 删除（合并完成后归档到 _archive/）
```

**关键原则**：
- **API 全部走 lean-ops**（ORM + Pydantic + 分层），webapp 的 sqlite3 直连全部废弃
- **页面模板保留 webapp 视觉**（Tailwind/Linear 风格用户认可度高），但**接入 lean-ops 的 base.html 布局体系**——实际是"取 webapp 的视觉、取 lean-ops 的骨架"
- 也可以反过来（保留 lean-ops 全套模板+design-system，把 webapp 独有页面按 design-system 重写）——**二选一，我推荐后者**，理由见 §5 决策点

---

## 3. 迁移步骤（分 6 个阶段，每阶段可独立验证）

### Phase 0：基线（0.5 天）
- [ ] 确认本地与远程同步（`git status` 干净，HEAD=94d8dcb）
- [ ] 用 lean-ops 启动（`uvicorn app.main:app`）验证全页面可访问
- [ ] 备份数据库 `leanops.db`（cp 到仓库外）
- [ ] 建立迁移分支 `refactor/merge-backends`

### Phase 1：路由去重（1 天）
- [ ] 逐域对比 webapp vs lean-ops API 实现，确认 lean-ops 版本功能覆盖（尤其 lean20/pillars/automation 三个 webapp 独有页面依赖的 API 是否在 lean-ops 完整）
- [ ] **若 lean-ops API 有缺**：把 webapp 缺失端点补进 lean-ops 对应模块（用 ORM 重写，不是复制 sqlite3 代码）
- [ ] 删除 webapp 的 `/api/v1/*` 重复端点（保留页面路由）

### Phase 2：独有页面迁入（2 天）
- [ ] 知识库：新建 `lean-ops/app/api/v1/knowledge.py`（树浏览/文件读取/搜索），模板迁入 `knowledge.html`/`file_view.html`/`search.html`
- [ ] 实施路线图：`implementation.html` + 静态数据（或 DB 表）
- [ ] 成熟度评估：`assessment.html` 迁入（与 lean-ops `/maturity` 对齐或替换）
- [ ] 每个页面验证：路由 → 模板渲染 → 静态资源加载 → 交互（Alpine.js）→ 数据正确

### Phase 3：统一 UI 体系（2-3 天，与 Phase 2 可并行）
- [ ] **决策**：视觉体系二选一（§5）
- [ ] 若选"webapp 视觉进 lean-ops"：把 Tailwind CDN 依赖改为本地（离线可用），把 webapp 的 `--accent` 等 CSS 变量并入 design-system.css
- [ ] 若选"lean-ops 视觉统一"：按 design-system 组件重写 8 个迁入页面
- [ ] 统一导航：base.html 侧边栏加入知识库/搜索/实施/评估入口

### Phase 4：静态资源与依赖收敛（0.5 天）
- [ ] CDN 依赖本地化：tailwindcss、alpinejs、chart.js、Google Fonts → 下载到 `static/vendor/`
- [ ] 删除 webapp 的 static/ 与 lean-ops 重复文件
- [ ] 统一 `static/js/app.js`（保留一份，合并功能）

### Phase 5：清理与测试（1 天）
- [ ] 删除 webapp/ 目录（先移入 `_archive/` 观察 1 周）
- [ ] 全量回归：所有页面 200、所有 API 可调、数据库无写入错误
- [ ] 补充 lean-ops tests/ 缺失的 API 测试（重点 lean20/pillars/automation/knowledge）

### Phase 6：文档与发布（0.5 天）
- [ ] README 更新启动方式（单命令 `uvicorn app.main:app`）
- [ ] CLAUDE.md 更新架构说明（单后端）
- [ ] 提交推送

**总工期：约 6-8 个工作日（一个人）**

---

## 4. 风险与缓解

| 风险 | 等级 | 缓解 |
|---|---|---|
| lean-ops 的 lean20/pillars/automation API 不完整，webapp 页面迁入后功能缺失 | 高 | Phase 1 先行比对，缺什么补什么；迁入前逐页面点测 |
| 两套 UI 视觉冲突，用户不适应 | 中 | 保留用户认可的 webapp 视觉；或先统一骨架再统一样式 |
| 知识库文件路径（`01-精益工具知识库/` 中文目录）在 lean-ops 静态服务下 404 | 中 | 知识库不走 StaticFiles，走专用路由（webapp 已有 `file/{path}` 模式可移植） |
| 数据库被两套写入逻辑（sqlite3 vs ORM）改坏 | 中 | 合并后只剩 ORM 一套；迁移期间禁止 webapp 写操作 |
| Tailwind CDN 在离线/内网环境失效 | 低 | 本地化 vendor（Phase 4） |

---

## 5. 关键决策点（需用户拍板）

### 决策 A：视觉体系保留哪套？
- **A1：保留 webapp 视觉**（Tailwind + Linear/Vercel 风格，index.html 691 行最精致）→ lean-ops 25 个模板要重写样式，工作量大
- **A2：保留 lean-ops 视觉**（design-system.css 已组件化，25 个模板现成）→ 只重写 8 个迁入页面，工作量小
- **推荐 A2**：因为 lean-ops 是目标架构主体，且 design-system 已成型；8 个页面重写可控

### 决策 B：webapp 删除时机
- 合并完成后立即删（干净）vs 移入 `_archive/` 观察一周再删（稳妥）
- 推荐后者

### 决策 C：知识库是否纳入数据库索引
- 现状：`search` 是遍历文件系统
- 可选：升级为 SQLite FTS5 全文索引（搜索更快、可排序）——工作量 +1 天，建议后续做

---

## 6. 合并后的目录结构（最终形态）

```
Lean/
├── lean-ops/                  ← 唯一应用
│   ├── app/
│   │   ├── main.py            ← 唯一入口
│   │   ├── api/v1/            ← 19+1 模块
│   │   ├── models/ schemas/ services/ core/   ← 分层
│   │   ├── templates/         ← 33 页面（25 现有 + 8 迁入）
│   │   ├── static/            ← 统一资源（含 vendor/ 本地化）
│   │   └── utils/
│   ├── data/leanops.db
│   ├── scripts/seed_data.py
│   ├── tests/
│   └── Dockerfile / docker-compose.yml
├── 01-精益工具知识库/         ← 知识库文档（应用只读）
├── 02-精益培训/ ... 05-项目管理/ appendix/ docs/
├── README.md  CLAUDE.md
└── _archive/webapp/           ← 观察期后删除
```

---

## 7. 验收标准
- [ ] 单命令启动：`uvicorn app.main:app --port 8000`，全部页面可达
- [ ] 无任何 `/api/v1/*` 重复端点
- [ ] 知识库浏览/搜索/下载可用（中文路径无 404）
- [ ] 全量回归测试通过（lean-ops tests/）
- [ ] webapp/ 目录已归档或删除
- [ ] README/CLAUDE.md 更新为单后端说明
