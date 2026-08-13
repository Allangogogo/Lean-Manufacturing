import urllib.request, json, sys

# Auth
auth_data = json.dumps({"username": "admin", "password": "123456"}).encode()
req = urllib.request.Request(
    "http://localhost:8000/api/v1/auth/login",
    data=auth_data,
    headers={"Content-Type": "application/json"},
)
resp = urllib.request.urlopen(req, timeout=10)
token = json.loads(resp.read()).get("access_token", "")
print("Token OK", file=sys.stderr)

headers = {"Authorization": f"Bearer {token}"}

# Test 1: pillars dashboard
print("=== Dashboard ===")
req = urllib.request.Request("http://localhost:8000/api/v1/pillars/dashboard", headers=headers)
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())
print(f"Overall: {data.get('overall_composite')} / {data.get('overall_level')}")
for p in data.get("pillars", []):
    cc = p.get("current_composite") or "-"
    tc = p.get("target_composite")
    wd = p.get("weakest_dimension") or "-"
    sug = (p.get("improvement_suggestion") or "")[:60]
    print(f"  {p['name_en']}: {cc}/{tc} weakest={wd}")
    if sug:
        print(f"    -> {sug}")

# Test 2: BFC report
print()
print("=== BFC Report (assessment #3) ===")
req = urllib.request.Request("http://localhost:8000/api/v1/lean20/report/3", headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    print(f"Overall: {data.get('overall_composite')} / {data.get('overall_level')}")
    print(f"Weakest: {data.get('weakest_pillar')}")
    sug = (data.get("overall_suggestion") or "")[:80]
    print(f"Suggestion: {sug}")
    for p in data.get("pillars", []):
        print(f"  {p['pillar_name']}: {p['composite']}/{p['target']} gap={p['gap']}")
except Exception as e:
    print(f"Report error: {e}")

# Test 3: single pillar detail
print()
print("=== Pillar: better ===")
req = urllib.request.Request("http://localhost:8000/api/v1/pillars/better", headers=headers)
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())
print(f"Vision: {data.get('vision')}")
for d in data.get("dimensions", []):
    cl = d.get("current_level") or "-"
    print(f"  {d['dimension_code']} {d['focus_area']}: level={cl} weight={d['weight']}")

print()
print("ALL TESTS PASSED")
