"""
Seed a test Lean 2.0 assessment + dimension scores for API testing.
"""
import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lean-ops", "data", "leanops.db")

def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check if test data already exists
    existing = cur.execute("SELECT COUNT(*) FROM lean20_assessments").fetchone()[0]
    if existing > 0:
        print(f"[SKIP] Already have {existing} assessments")
        conn.close()
        return

    # Create a test assessment
    cur.execute(
        "INSERT INTO lean20_assessments (assessment_date, factory_id, assessor_id, status, weights, composite_index, overall_level, summary, recommendations) "
        "VALUES (date('now'), 1, 1, 'completed', ?, 2.17, 'L2-发展', 'Test assessment for lean system', 'Focus on Digital and Green dimensions')",
        (json.dumps({"O": 0.30, "D": 0.20, "G": 0.15, "R": 0.20, "H": 0.15}),)
    )
    aid = cur.lastrowid
    print(f"[OK] Created assessment #{aid}")

    # Insert dimension scores (typical manufacturing factory profile)
    scores = [
        ("O", 2.8, 0.30),  # Operations - developing
        ("D", 1.8, 0.20),  # Digital - early stage
        ("G", 1.5, 0.15),  # Green - basic compliance
        ("R", 2.0, 0.20),  # Resilience - some buffers
        ("H", 2.2, 0.15),  # Human - team building
    ]
    for code, level, weight in scores:
        cur.execute(
            "INSERT INTO lean20_dimension_scores (assessment_id, dimension_code, level, weight, weighted_score, notes) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (aid, code, level, weight, round(level * weight, 2), f"Test score for {code}")
        )

    # Also create a completed project with lean20_dimensions for A3 testing
    cur.execute(
        "INSERT INTO projects (name, description, project_type, owner_id, factory_id, status, priority, budget, actual_cost, objectives, lean20_dimensions, source_assessment_id, actual_end_date) "
        "VALUES (?, ?, ?, 1, 1, 'completed', 'high', 0, 0, ?, ?, ?, date('now'))",
        (
            "Green Lean Initiative - Energy Management",
            "Created from Lean 2.0 assessment. Target dimension: G (current L1).",
            "kaizen_event",
            "Raise Green maturity from L1 to L2",
            json.dumps(["G"]),
            aid,
        )
    )
    pid = cur.lastrowid
    print(f"[OK] Created test project #{pid}")

    conn.commit()
    conn.close()
    print("Seed complete!")

if __name__ == "__main__":
    seed()
