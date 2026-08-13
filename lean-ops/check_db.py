import sqlite3
conn = sqlite3.connect('data/leanops.db')
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cursor.fetchall()]
print(f'Tables: {len(tables)}')
for t in tables:
    print(f'  {t}')
    cols = conn.execute(f"PRAGMA table_info({t})").fetchall()
    for c in cols:
        print(f'    {c[1]} {c[2]} {"PK" if c[5] else ""}')
conn.close()
