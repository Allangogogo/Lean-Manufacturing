import sqlite3
conn = sqlite3.connect("data/leanops.db")
cursor = conn.cursor()
print("=== workflow_states ===")
cursor.execute("SELECT * FROM workflow_states")
rows = cursor.fetchall()
print(f"Count: {len(rows)}")
for row in rows:
    print(row)
print("\n=== workflow_logs ===")
cursor.execute("SELECT * FROM workflow_logs")
rows = cursor.fetchall()
print(f"Count: {len(rows)}")
for row in rows:
    print(row)
conn.close()
