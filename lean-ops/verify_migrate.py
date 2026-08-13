import sqlite3
conn = sqlite3.connect('data/leanops.db')
cols = [r[1] for r in conn.execute('PRAGMA table_info(projects)').fetchall()]
print('projects new cols:', [c for c in cols if c in ['lean20_dimensions', 'source_assessment_id']])
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print('lean20_assessments:', 'lean20_assessments' in tables)
print('lean20_dimension_scores:', 'lean20_dimension_scores' in tables)
for t in ['lean20_assessments', 'lean20_dimension_scores']:
    cols = conn.execute(f'PRAGMA table_info({t})').fetchall()
    print(f'  {t}: {len(cols)} columns - {[c[1] for c in cols]}')
conn.close()
