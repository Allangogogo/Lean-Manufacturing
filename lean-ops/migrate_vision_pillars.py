"""
Phase 1: Vision Refactoring - Data Layer Migration

Creates 3 new tables for the Better-Faster-Closer value pillar model:
1. value_pillars - Pillar definitions
2. pillar_dimension_mapping - Pillar <-> Lean2.0 dimension mapping
3. pillar_kpi_snapshots - KPI tracking per pillar

DB: lean-ops/data/leanops.db (SQLite)
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "leanops.db"

def migrate():
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    # ================================================================
    # Table 1: value_pillars
    # ================================================================
    c.execute("""
        CREATE TABLE IF NOT EXISTS value_pillars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code VARCHAR(10) NOT NULL UNIQUE,
            name VARCHAR(50) NOT NULL,
            name_en VARCHAR(50) NOT NULL,
            vision_statement TEXT,
            target_composite DECIMAL(3,2) DEFAULT 0.00,
            icon VARCHAR(20),
            color VARCHAR(10),
            sort_order INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Seed data
    pillars = [
        ("better", "品质卓越", "Better",
         "持续追求零缺陷和世界级运营卓越，让每一颗产品都成为品质承诺",
         3.80, "diamond", "#2563eb", 1),
        ("faster", "敏捷交付", "Faster",
         "以最短路径将价值传递到客户手中，快速响应、短交付周期、柔性生产",
         3.50, "bolt", "#059669", 2),
        ("closer", "客户亲密", "Closer",
         "与客户深度连接，从供应商升级为价值伙伴，价值共创、深度服务、生态连接",
         3.20, "handshake", "#d97706", 3),
    ]
    for p in pillars:
        c.execute("""
            INSERT OR IGNORE INTO value_pillars
            (code, name, name_en, vision_statement, target_composite, icon, color, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, p)

    # ================================================================
    # Table 2: pillar_dimension_mapping
    # ================================================================
    c.execute("""
        CREATE TABLE IF NOT EXISTS pillar_dimension_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pillar_code VARCHAR(10) NOT NULL,
            dimension_code VARCHAR(1) NOT NULL,
            focus_area VARCHAR(50) NOT NULL,
            key_metrics TEXT,
            core_tools TEXT,
            weight_in_pillar DECIMAL(3,2) NOT NULL,
            UNIQUE(pillar_code, dimension_code),
            FOREIGN KEY (pillar_code) REFERENCES value_pillars(code),
            FOREIGN KEY (dimension_code) REFERENCES lean20_checklist_items(dimension_code)
        )
    """)

    # Mapping data: (pillar, dimension, focus_area, metrics_json, tools_json, weight)
    mappings = [
        # -- BETTER --
        ("better", "O", "品质运营",
         json.dumps(["OEE", "PPM", "COPQ", "一次合格率", "标准作业覆盖率"], ensure_ascii=False),
         json.dumps(["5S", "SPC", "TPM", "Poka-Yoke", "标准作业"], ensure_ascii=False),
         0.35),
        ("better", "D", "数据驱动质量",
         json.dumps(["检测准确率", "缺陷逃逸率", "质量数据实时率"], ensure_ascii=False),
         json.dumps(["AI视觉检测", "SPC数字化", "质量看板"], ensure_ascii=False),
         0.20),
        ("better", "G", "绿色品质",
         json.dumps(["碳强度", "CBAM合规率", "危废减量率"], ensure_ascii=False),
         json.dumps(["碳足迹VSM", "LCA", "绿色采购"], ensure_ascii=False),
         0.20),
        ("better", "R", "韧性品质",
         json.dumps(["供应中断次数", "MTTR", "来料合格率波动"], ensure_ascii=False),
         json.dumps(["双源策略", "缓冲管理", "来料SPC"], ensure_ascii=False),
         0.10),
        ("better", "H", "工匠精神",
         json.dumps(["多技能率", "改善参与率", "技能认证覆盖率"], ensure_ascii=False),
         json.dumps(["技能矩阵", "Kaizen", "OJT"], ensure_ascii=False),
         0.15),

        # -- FASTER --
        ("faster", "O", "流动效率",
         json.dumps(["Lead Time", "OTD", "WIP", "增值比"], ensure_ascii=False),
         json.dumps(["VSM", "Kanban", "SMED", "Heijunka"], ensure_ascii=False),
         0.30),
        ("faster", "D", "实时可视",
         json.dumps(["数据延迟", "决策周期", "可视化覆盖率"], ensure_ascii=False),
         json.dumps(["MES", "IoT", "数字孪生", "安灯系统"], ensure_ascii=False),
         0.25),
        ("faster", "G", "绿色流程效率",
         json.dumps(["能耗/单位", "水耗/单位", "工艺能耗占比"], ensure_ascii=False),
         json.dumps(["能源监控", "工艺优化", "余热回收"], ensure_ascii=False),
         0.10),
        ("faster", "R", "响应速度",
         json.dumps(["异常感知时间", "恢复时间", "应急响应率"], ensure_ascii=False),
         json.dumps(["预警系统", "应急SOP", "快速切换"], ensure_ascii=False),
         0.20),
        ("faster", "H", "组织敏捷",
         json.dumps(["变革周期", "赋权率", "跨部门协作效率"], ensure_ascii=False),
         json.dumps(["变革管理", "赋权框架", "敏捷站会"], ensure_ascii=False),
         0.15),

        # -- CLOSER --
        ("closer", "O", "需求响应",
         json.dumps(["定制件占比", "客户投诉率", "需求响应时间"], ensure_ascii=False),
         json.dumps(["Leagile", "解耦点策略", "延迟差异化"], ensure_ascii=False),
         0.25),
        ("closer", "D", "客户数字接口",
         json.dumps(["门户使用率", "在线下单率", "数据对接率"], ensure_ascii=False),
         json.dumps(["客户门户", "EDI", "API集成"], ensure_ascii=False),
         0.15),
        ("closer", "G", "碳数据服务",
         json.dumps(["客户碳数据需求满足率", "EPD覆盖率", "碳标签产品占比"], ensure_ascii=False),
         json.dumps(["产品碳标签", "EPD", "碳数据门户"], ensure_ascii=False),
         0.15),
        ("closer", "R", "供应保障",
         json.dumps(["关键客户缺供率", "VMI覆盖率", "优先交付满足率"], ensure_ascii=False),
         json.dumps(["客户分级", "优先保障", "VMI"], ensure_ascii=False),
         0.25),
        ("closer", "H", "客户共创",
         json.dumps(["客户NPS", "联合改善数", "客户参与设计比例"], ensure_ascii=False),
         json.dumps(["客户Gemba", "联合Kaizen", "方案共创"], ensure_ascii=False),
         0.20),
    ]

    for m in mappings:
        c.execute("""
            INSERT OR IGNORE INTO pillar_dimension_mapping
            (pillar_code, dimension_code, focus_area, key_metrics, core_tools, weight_in_pillar)
            VALUES (?, ?, ?, ?, ?, ?)
        """, m)

    # ================================================================
    # Table 3: pillar_kpi_snapshots
    # ================================================================
    c.execute("""
        CREATE TABLE IF NOT EXISTS pillar_kpi_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pillar_code VARCHAR(10) NOT NULL,
            dimension_code VARCHAR(1),
            kpi_name VARCHAR(100) NOT NULL,
            kpi_value DECIMAL(10,4),
            target_value DECIMAL(10,4),
            unit VARCHAR(20),
            snapshot_date DATE NOT NULL,
            source VARCHAR(20) DEFAULT 'manual',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pillar_code) REFERENCES value_pillars(code)
        )
    """)

    conn.commit()

    # Verification
    for table in ["value_pillars", "pillar_dimension_mapping", "pillar_kpi_snapshots"]:
        c.execute(f"SELECT COUNT(*) FROM [{table}]")
        count = c.fetchone()[0]
        print(f"  {table}: {count} rows")

    # Verify mapping weights sum to 1.0 per pillar
    for pillar_code in ["better", "faster", "closer"]:
        c.execute("""
            SELECT SUM(weight_in_pillar) FROM pillar_dimension_mapping
            WHERE pillar_code = ?
        """, (pillar_code,))
        total = c.fetchone()[0]
        print(f"  {pillar_code} weight sum: {total:.2f}")

    conn.close()
    print("Phase 1 migration complete.")


if __name__ == "__main__":
    migrate()
