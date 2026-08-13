import sqlite3
conn = sqlite3.connect('data/leanops.db')
conn.execute("UPDATE projects SET actual_end_date = '2026-06-17' WHERE id = 1")
conn.commit()
print('Updated project actual_end_date')
conn.close()
