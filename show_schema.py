import os
import sqlite3
conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'lean-ops', 'data', 'leanops.db'))
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in c.fetchall()]
print(f"=== {len(tables)} Tables ===")
for t in tables:
    c.execute(f"SELECT COUNT(*) FROM [{t}]")
    count = c.fetchone()[0]
    c.execute(f"PRAGMA table_info([{t}])")
    cols = [r[1] for r in c.fetchall()]
    print(f"  {t} ({count} rows): {', '.join(cols[:8])}{'...' if len(cols)>8 else ''}")
conn.close()
