"""
Add automation maturity, project, and PDCA tables.

Run: py -c "from app.database import engine; from app.models.automation import *; import asyncio; asyncio.run(run_migration())"
Or:  py migrate_automation.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "leanops.db")
# Fallback
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(os.path.dirname(__file__), "leanops.db")

MIGRATION_SQL = """
-- Automation maturity assessments
CREATE TABLE IF NOT EXISTS automation_maturity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factory_id INTEGER REFERENCES factories(id),
    assessor_id INTEGER REFERENCES users(id),
    assessor_name VARCHAR(100),
    quality_score NUMERIC(4,2) DEFAULT 0,
    tooling_score NUMERIC(4,2) DEFAULT 0,
    feeding_score NUMERIC(4,2) DEFAULT 0,
    heat_treatment_score NUMERIC(4,2) DEFAULT 0,
    logistics_score NUMERIC(4,2) DEFAULT 0,
    composite_score NUMERIC(4,2),
    maturity_level INTEGER,
    notes TEXT,
    is_completed BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);

-- Checklist items for automation maturity assessment
CREATE TABLE IF NOT EXISTS automation_checklist_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL REFERENCES automation_maturity(id),
    dimension VARCHAR(20) NOT NULL,
    item_text TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0,
    is_checked BOOLEAN DEFAULT 0,
    evidence TEXT
);

-- Automation projects with ROI tracking
CREATE TABLE IF NOT EXISTS automation_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER REFERENCES automation_maturity(id),
    project_name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    priority VARCHAR(10) DEFAULT 'P1',
    investment_amount NUMERIC(12,2) DEFAULT 0,
    investment_breakdown TEXT,
    expected_annual_benefit NUMERIC(12,2) DEFAULT 0,
    expected_roi NUMERIC(8,2),
    expected_payback_months NUMERIC(6,1),
    actual_annual_benefit NUMERIC(12,2),
    actual_roi NUMERIC(8,2),
    actual_payback_months NUMERIC(6,1),
    pdca_phase VARCHAR(20) DEFAULT 'plan',
    pdca_cycle INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'planned',
    start_date VARCHAR(20),
    target_date VARCHAR(20),
    completed_date VARCHAR(20),
    owner VARCHAR(100),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

-- PDCA review records
CREATE TABLE IF NOT EXISTS automation_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES automation_projects(id),
    pdca_phase VARCHAR(20) NOT NULL,
    cycle_number INTEGER DEFAULT 1,
    reviewer VARCHAR(100),
    plan_goals TEXT,
    plan_actions TEXT,
    do_progress TEXT,
    do_issues TEXT,
    check_results TEXT,
    check_roi_actual NUMERIC(8,2),
    act_decision VARCHAR(50),
    act_next_steps TEXT,
    review_date VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

def run_migration():
    print(f"Migrating: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(MIGRATION_SQL)
    conn.commit()

    # Verify
    for table in ["automation_maturity", "automation_checklist_items", "automation_projects", "automation_reviews"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} rows")

    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    run_migration()
