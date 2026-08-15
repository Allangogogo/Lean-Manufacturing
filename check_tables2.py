import sqlite3
import os
conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'lean-ops', 'data', 'leanops.db'))
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
print("=== Tables ===")
for r in c.fetchall():
    print(f"  {r[0]}")

# Check checklist table
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%checklist%'")
checklist = c.fetchall()
if checklist:
    for t in checklist:
        c.execute(f"PRAGMA table_info({t[0]})")
        print(f"\n=== {t[0]} columns ===")
        for col in c.fetchall():
            print(f"  {col}")
        c.execute(f"SELECT COUNT(*) FROM {t[0]}")
        print(f"  Rows: {c.fetchone()[0]}")
conn.close()
