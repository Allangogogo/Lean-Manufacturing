import sqlite3
conn = sqlite3.connect('data/leanops.db')
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print('lean20 tables:', [t for t in tables if 'lean20' in t.lower()])
print('Total tables:', len(tables))
conn.close()
