"""
Database migration: Add Lean 2.0 tables and project columns.

Run: py migrate_lean20.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "leanops.db")


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Add lean20_dimensions column to projects table (if not exists)
    cols = [r[1] for r in cursor.execute("PRAGMA table_info(projects)").fetchall()]
    if "lean20_dimensions" not in cols:
        cursor.execute(
            "ALTER TABLE projects ADD COLUMN lean20_dimensions TEXT"
        )
        print("[OK] Added lean20_dimensions to projects")
    else:
        print("[SKIP] lean20_dimensions already in projects")

    if "source_assessment_id" not in cols:
        cursor.execute(
            "ALTER TABLE projects ADD COLUMN source_assessment_id INTEGER"
        )
        print("[OK] Added source_assessment_id to projects")
    else:
        print("[SKIP] source_assessment_id already in projects")

    # 2. Create lean20_assessments table (if not exists)
    tables = [r[0] for r in cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]

    if "lean20_assessments" not in tables:
        cursor.execute("""
            CREATE TABLE lean20_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_date DATE NOT NULL,
                factory_id INTEGER NOT NULL REFERENCES factories(id),
                assessor_id INTEGER NOT NULL REFERENCES users(id),
                status VARCHAR(20) NOT NULL DEFAULT 'draft',
                weights TEXT,
                composite_index NUMERIC(4, 2),
                overall_level VARCHAR(50),
                summary TEXT,
                recommendations TEXT,
                completed_at DATETIME,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute(
            "CREATE INDEX ix_lean20_assessments_factory_id ON lean20_assessments(factory_id)"
        )
        cursor.execute(
            "CREATE INDEX ix_lean20_assessments_assessor_id ON lean20_assessments(assessor_id)"
        )
        cursor.execute(
            "CREATE INDEX ix_lean20_assessments_status ON lean20_assessments(status)"
        )
        print("[OK] Created lean20_assessments table")
    else:
        print("[SKIP] lean20_assessments already exists")

    # 3. Create lean20_dimension_scores table (if not exists)
    if "lean20_dimension_scores" not in tables:
        cursor.execute("""
            CREATE TABLE lean20_dimension_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_id INTEGER NOT NULL REFERENCES lean20_assessments(id) ON DELETE CASCADE,
                dimension_code VARCHAR(1) NOT NULL,
                level NUMERIC(3, 1) NOT NULL,
                weight NUMERIC(3, 2) NOT NULL DEFAULT 0.20,
                weighted_score NUMERIC(4, 2),
                notes TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute(
            "CREATE INDEX ix_lean20_dim_scores_assessment_id ON lean20_dimension_scores(assessment_id)"
        )
        print("[OK] Created lean20_dimension_scores table")
    else:
        print("[SKIP] lean20_dimension_scores already exists")

    conn.commit()
    conn.close()
    print("\nMigration complete!")


if __name__ == "__main__":
    migrate()
