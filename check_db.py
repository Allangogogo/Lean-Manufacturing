import sqlite3
import os
conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'lean-ops', 'leanops.db'))
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
print("=== Tables ===")
for r in c.fetchall():
    print(f"  {r[0]}")

# Check if checklist table exists
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%checklist%'")
checklist_tables = c.fetchall()
if checklist_tables:
    for t in checklist_tables:
        print(f"\n=== {t[0]} ===")
        c.execute(f"PRAGMA table_info({t[0]})")
        for col in c.fetchall():
            print(f"  {col}")
        c.execute(f"SELECT COUNT(*) FROM {t[0]}")
        print(f"  Rows: {c.fetchone()[0]}")
        c.execute(f"SELECT * FROM {t[0]} LIMIT 3")
        for r in c.fetchall():
            print(f"  Sample: {r}")
else:
    print("\nNo checklist tables found")

conn.close()
