import sqlite3
import os
conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'lean-ops', 'leanops.db'))
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
print("=== Tables ===")
for r in c.fetchall():
    print(f"  {r[0]}")
conn.close()
