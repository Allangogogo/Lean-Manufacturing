# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Knowledge Base Overview

This is a comprehensive Lean Manufacturing knowledge base and management system for discrete manufacturing. It covers lean tools, training, maturity assessment, implementation strategy, and project management.

**Industry**: Discrete manufacturing (machining → precision machining → heat treatment → surface treatment → assembly → packaging)

**Target**: Lean transformation from L2 to L4 maturity over 36 months

## Directory Index

| Directory | Content Type | Key Topics |
|-----------|-------------|------------|
| `01-精益工具知识库/` | Knowledge Base | Lean philosophy, 13 core tools (+深化), 5 problem-solving methods, manufacturing applications, deep-dive topics, case studies |
| `01-精益工具知识库/06-深度专题/` | Advanced Topics | Change management, advanced VSM, quality standards integration, digital lean & Industry 4.0 |
| `02-精益培训/` | Training | Training strategy, materials, plans, templates, tracking, feedback |
| `03-成熟度评估/` | Assessment | 5-level maturity model, factory-wide & process-specific assessments |
| `04-实施战略/` | Strategy | 5-phase roadmap, 3 implementation paths, 6 tool templates |
| `05-项目管理/` | PM | Charter, schedule, risk, performance templates |
| `appendix/` | Reference | Glossary, bibliography, template guide |

## Quick Lookup by Topic

**Lean Tools (13 core tools + 深化文档):**
- Kanban → `01-精益工具知识库/02-核心工具/01-看板Kanban.md`
- VSM → `01-精益工具知识库/02-核心工具/02-价值流图VSM.md` | [高级实战](01-精益工具知识库/06-深度专题/02-价值流图高级实战指南.md)
- Andon → `01-精益工具知识库/02-核心工具/03-安灯Andon.md`
- Standard Work → `01-精益工具知识库/02-核心工具/04-标准作业StandardWork.md`
- TPM → `01-精益工具知识库/02-核心工具/05-全面生产维护TPM.md` | [深化：预测性维护](01-精益工具知识库/02-核心工具/05-全面生产维护TPM-深化.md)
- 5S → `01-精益工具知识库/02-核心工具/06-5S管理.md`
- Kaizen → `01-精益工具知识库/02-核心工具/07-改善Kaizen.md`
- Heijunka → `01-精益工具知识库/02-核心工具/08-平准化Heijunka.md`
- Poka-Yoke → `01-精益工具知识库/02-核心工具/09-防错PokaYoke.md`
- SMED → `01-精益工具知识库/02-核心工具/10-快速换模SMED.md`
- Jidoka → `01-精益工具知识库/02-核心工具/11-自働化Jidoka.md`
- JIT → `01-精益工具知识库/02-核心工具/12-准时化JIT.md`
- Visual Management → `01-精益工具知识库/02-核心工具/13-可视化管理.md`

**Deep-Dive Topics (06-深度专题):**
- Change Management → `01-精益工具知识库/06-深度专题/01-精益实施变革管理指南.md`
- Advanced VSM → `01-精益工具知识库/06-深度专题/02-价值流图高级实战指南.md`
- Quality Standards → `01-精益工具知识库/06-深度专题/03-制造业质量标准与精益整合.md`
- Digital Lean → `01-精益工具知识库/06-深度专题/04-精益数字化与智能制造.md`
- **Industry 5.0 & Lean** → `01-精益工具知识库/06-深度专题/06-Industry5.0与精益融合框架.md`
- **Leagile** → `01-精益工具知识库/06-深度专题/07-Leagile精益敏捷融合策略.md`
- **Automation & Digital** → `01-精益工具知识库/06-深度专题/08-制造自动化与数字化实战.md`
- **Resilient Supply Chain** → `01-精益工具知识库/06-深度专题/09-韧性供应链与精益.md`
- **Lean Strategy** → `01-精益工具知识库/06-深度专题/10-精益战略思维与商业模式创新.md`
- **Lean 2.0 Tool Upgrade Index** → `01-精益工具知识库/06-深度专题/11-核心工具Lean2.0升级路径索引.md`

**Navigation & Practice:**
- Quick Reference → `01-精益工具知识库/精益工具快速参考指南.md`
- Tool Relationships → `01-精益工具知识库/工具关联与应用指南.md`
- Improvement Proposal → `01-精益工具知识库/05-实践案例集/02-精益改善提案模板.md`
- SMED Case Study → `01-精益工具知识库/05-实践案例集/01-机加工工序SMED改善案例.md`

**Problem Solving:**
- Gemba Walk → `01-精益工具知识库/03-问题解决方法/01-现场走动GembaWalk.md`
- A3 → `01-精益工具知识库/03-问题解决方法/02-A3问题解决法.md`
- PDCA → `01-精益工具知识库/03-问题解决方法/03-PDCA循环.md`
- DMAIC → `01-精益工具知识库/03-问题解决方法/04-DMAIC方法论.md`
- VA/VE → `01-精益工具知识库/03-问题解决方法/05-价值分析VA_VE.md`

**Manufacturing Process Applications:**
- Machining → `01-精益工具知识库/04-制造工序应用/01-机加工工序精益应用.md`
- Precision machining → `01-精益工具知识库/04-制造工序应用/02-精加工工序精益应用.md`
- Heat treatment → `01-精益工具知识库/04-制造工序应用/03-热处理工序精益应用.md`
- Surface treatment → `01-精益工具知识库/04-制造工序应用/04-表面处理工序精益应用.md`
- Packaging → `01-精益工具知识库/04-制造工序应用/05-包装工序精益应用.md`

**Maturity Assessment:**
- 5-level model → `03-成熟度评估/01-评估框架/01-精益成熟度模型(5级).md`
- **Lean 2.0 model (I5.0)** → `03-成熟度评估/01-评估框架/02-精益2.0成熟度模型-Industry5.0扩展维度.md`
- Factory-wide → `03-成熟度评估/02-工厂整体评估/01-工厂整体成熟度评估表.xlsx`
- Process-specific → `03-成熟度评估/03-局部评估/`

**Implementation:**
- Master plan → `04-实施战略/01-实施战略/01-精益转型总体规划.md`
- 5-phase roadmap → `04-实施战略/01-实施战略/02-五阶段实施路线图.md`
- **Lean 2.0 roadmap (I5.0)** → `04-实施战略/01-实施战略/03-Lean2.0实施路线图.md`
- Phase details → `04-实施战略/02-详细计划/`

**Templates & Checklists:**
- Kaizen event → `04-实施战略/03-实施工具/01-Kaizen事件策划模板.xlsx`
- A3 report → `04-实施战略/03-实施工具/02-A3报告模板.xlsx`
- VSM template → `04-实施战略/03-实施工具/03-价值流图模板.xlsx`
- Standard work → `04-实施战略/03-实施工具/04-标准作业模板.xlsx`
- 5S audit → `04-实施战略/03-实施工具/05-5S审核表模板.xlsx`
- Improvement proposal → `04-实施战略/03-实施工具/06-改善提案表模板.xlsx`

**Training:**
- Training strategy → `02-精益培训/01-培训策略/01-精益培训体系规划.md`
- 4-tier architecture → `02-精益培训/01-培训策略/02-四层培训架构设计.md`
- Kirkpatrick model → `02-精益培训/06-效果反馈/01-柯氏四级评估框架.md`

## Key Data Points

| Metric | Value | Source |
|--------|-------|--------|
| OEE target | 72% → 85% | `01-精益工具知识库/02-核心工具/05-全面生产维护TPM.md` |
| Changeover time | 60min → <10min | `01-精益工具知识库/02-核心工具/10-快速换模SMED.md` |
| Defect rate | 2.5% → 1.0% | `01-精益工具知识库/02-核心工具/09-防错PokaYoke.md` |
| Maturity target | L2 → L4 | `03-成熟度评估/01-评估框架/01-精益成熟度模型(5级).md` |
| Implementation | 36 months, 5 phases | `04-实施战略/01-实施战略/02-五阶段实施路线图.md` |

## How to Use This Knowledge Base

**For Management:** Start with `04-实施战略/01-实施战略/01-精益转型总体规划.md` for the big picture. Use `03-成熟度评估/` to assess current state.

**For Lean Champions:** Start with `01-精益工具知识库/` for tool knowledge. Use `02-精益培训/` to organize training. Track progress with `03-成熟度评估/`.

**For PMO:** Use `05-项目管理/` for project templates. Reference `04-实施战略/02-详细计划/` for implementation planning.

**For Engineers/Team Leaders:** Start with `01-精益工具知识库/02-核心工具/` for specific tools. See `01-精益工具知识库/04-制造工序应用/` for industry practice.

**For AI Assistants:** Use this CLAUDE.md as the entry point. The `appendix/01-精益术语表.md` provides essential domain context.
