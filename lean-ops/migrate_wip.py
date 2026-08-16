"""
Add WIP (Work-In-Process) tables.

Run: py migrate_wip.py
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "leanops.db")
# Fallback
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(os.path.dirname(__file__), "leanops.db")

MIGRATION_SQL = """
-- Production orders (工单主表)
CREATE TABLE IF NOT EXISTS production_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_no VARCHAR(30) NOT NULL UNIQUE,
    product_name VARCHAR(200) NOT NULL,
    product_code VARCHAR(50),
    quantity INTEGER NOT NULL,
    priority VARCHAR(10) DEFAULT 'normal',
    status VARCHAR(20) DEFAULT 'pending',
    factory_id INTEGER REFERENCES factories(id),
    planned_start DATE,
    planned_end DATE,
    actual_start DATETIME,
    actual_end DATETIME,
    created_by INTEGER REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Work order operations (工序在制，WIP 核心表)
CREATE TABLE IF NOT EXISTS work_order_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES production_orders(id) ON DELETE CASCADE,
    sequence_no INTEGER NOT NULL,
    operation_name VARCHAR(50) NOT NULL,
    equipment_id INTEGER REFERENCES tpm_equipment(id),
    input_qty INTEGER DEFAULT 0,
    output_qty INTEGER DEFAULT 0,
    wip_qty INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    start_time DATETIME,
    end_time DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_wop_order ON work_order_operations(order_id);
CREATE INDEX IF NOT EXISTS idx_wop_status ON work_order_operations(status);

-- WIP transactions (流转记录)
CREATE TABLE IF NOT EXISTS wip_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL REFERENCES work_order_operations(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    from_operation INTEGER REFERENCES work_order_operations(id),
    to_operation INTEGER REFERENCES work_order_operations(id),
    operator_id INTEGER REFERENCES users(id),
    occurred_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_wt_op ON wip_transactions(operation_id);

-- WIP daily snapshots (每日水位快照)
CREATE TABLE IF NOT EXISTS wip_daily_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_date DATE NOT NULL,
    factory_id INTEGER REFERENCES factories(id),
    operation_name VARCHAR(50) NOT NULL,
    wip_qty INTEGER DEFAULT 0,
    throughput INTEGER DEFAULT 0,
    cycle_time_min INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(snapshot_date, factory_id, operation_name)
);
CREATE INDEX IF NOT EXISTS idx_wds_date ON wip_daily_snapshots(snapshot_date);
"""

# 标准工序链（与 v2.0.0 泛化后一致）
OPERATION_CHAIN = [
    "机加工",
    "精加工",
    "热处理",
    "表面处理",
    "装配",
    "包装",
]


def seed_demo_orders(conn):
    """种子数据：3 张示例工单 + 工序 + 30 天历史快照。"""
    cur = conn.cursor()

    # 检查是否已有数据
    cur.execute("SELECT COUNT(*) FROM production_orders")
    if cur.fetchone()[0] > 0:
        print("  production_orders 已有数据，跳过种子。")
        return

    factory_id = None
    cur.execute("SELECT id FROM factories LIMIT 1")
    row = cur.fetchone()
    if row:
        factory_id = row[0]

    # 3 张工单（不同进度）
    demo_orders = [
        ("PO-20260816-001", "电机壳体", "MH-001", 600, "high", "in_progress"),
        ("PO-20260816-002", "齿轮轴", "GS-002", 400, "normal", "in_progress"),
        ("PO-20260816-003", "支架总成", "ZJ-003", 300, "low", "pending"),
    ]

    import datetime

    today = datetime.date.today()
    for idx, (no, name, code, qty, pri, status) in enumerate(demo_orders):
        cur.execute(
            """INSERT INTO production_orders
               (order_no, product_name, product_code, quantity, priority, status, factory_id,
                planned_start, planned_end, created_by)
               VALUES (?,?,?,?,?,?,?,?,?,1)""",
            (no, name, code, qty, pri, status, factory_id,
             today.isoformat(), (today + datetime.timedelta(days=14)).isoformat()),
        )
        order_id = cur.lastrowid

        # 为该工单创建 6 道工序，进度随工单不同
        for seq, op_name in enumerate(OPERATION_CHAIN, start=1):
            if status == "pending":
                op_status = "pending"
                input_qty = 0
                output_qty = 0
                wip = 0
            else:
                # 演示进度：按工单推进
                progress = {0: 0.0, 1: 0.3, 2: 0.6, 3: 0.85, 4: 1.0, 5: 1.0}
                p = progress.get(seq, 0.0)
                input_qty = int(qty * p)
                output_qty = int(qty * max(0.0, p - 0.15))
                wip = input_qty - output_qty
                op_status = "completed" if p >= 1.0 else ("in_progress" if p > 0 else "pending")

            cur.execute(
                """INSERT INTO work_order_operations
                   (order_id, sequence_no, operation_name, input_qty, output_qty, wip_qty, status)
                   VALUES (?,?,?,?,?,?,?)""",
                (order_id, seq, op_name, input_qty, output_qty, wip, op_status),
            )

    # 30 天历史快照（趋势图演示数据）
    cur.execute("SELECT COUNT(*) FROM wip_daily_snapshots")
    if cur.fetchone()[0] == 0:
        import random
        random.seed(42)
        for i in range(30, 0, -1):
            d = (today - datetime.timedelta(days=i)).isoformat()
            for op_name in OPERATION_CHAIN:
                base = {"机加工": 520, "精加工": 380, "热处理": 700,
                        "表面处理": 480, "装配": 260, "包装": 140}
                wobble = random.randint(-80, 80)
                wip_qty = max(0, base[op_name] + wobble)
                throughput = random.randint(180, 320)
                ct = random.randint(3, 12)
                cur.execute(
                    """INSERT INTO wip_daily_snapshots
                       (snapshot_date, factory_id, operation_name, wip_qty, throughput, cycle_time_min)
                       VALUES (?,?,?,?,?,?)""",
                    (d, factory_id, op_name, wip_qty, throughput, ct),
                )


def run_migration():
    print(f"Migrating: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(MIGRATION_SQL)
    conn.commit()

    seed_demo_orders(conn)
    conn.commit()

    # Verify
    for table in ["production_orders", "work_order_operations",
                  "wip_transactions", "wip_daily_snapshots"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} rows")

    conn.close()
    print("Migration complete.")


if __name__ == "__main__":
    run_migration()
