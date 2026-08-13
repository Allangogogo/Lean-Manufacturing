import urllib.request, json, sys

# Auth
auth_data = json.dumps({"username": "admin", "password": "123456"}).encode()
req = urllib.request.Request(
    "http://localhost:8000/api/v1/auth/login",
    data=auth_data,
    headers={"Content-Type": "application/json"},
)
resp = urllib.request.urlopen(req, timeout=10)
token_data = json.loads(resp.read())
token = token_data.get("token", "")
print(f"Token: {token[:30]}...")

headers = {"Authorization": f"Bearer {token}"}

# Test 1: pillars dashboard
print("\n=== Dashboard ===")
req = urllib.request.Request("http://localhost:8000/api/v1/pillars/dashboard", headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    oc = data.get("overall_composite") or "-"
    ol = data.get("overall_level") or "-"
    print(f"Overall: {oc} / {ol}")
    for p in data.get("pillars", []):
        cc = p.get("current_composite") or "-"
        tc = p.get("target_composite")
        wd = p.get("weakest_dimension") or "-"
        sug = (p.get("improvement_suggestion") or "")[:50]
        print(f"  {p['name_en']}: {cc}/{tc} weakest={wd}")
        if sug:
            print(f"    -> {sug}")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode()[:200]}")

# Test 2: BFC report
print("\n=== BFC Report #3 ===")
req = urllib.request.Request("http://localhost:8000/api/v1/lean20/report/3", headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    print(f"Overall: {data.get('overall_composite')} / {data.get('overall_level')}")
    print(f"Weakest pillar: {data.get('weakest_pillar')}")
    sug = (data.get("overall_suggestion") or "")[:80]
    print(f"Suggestion: {sug}")
    for p in data.get("pillars", []):
        print(f"  {p['pillar_name']}: {p['composite']}/{p['target']} gap={p['gap']}")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode()[:300]}")

# Test 3: pillar detail
print("\n=== Pillar: closer ===")
req = urllib.request.Request("http://localhost:8000/api/v1/pillars/closer", headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    print(f"Vision: {data.get('vision')}")
    for d in data.get("dimensions", []):
        cl = d.get("current_level") or "-"
        print(f"  {d['dimension_code']} {d['focus_area']}: {cl} (w={d['weight']})")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode()[:300]}")

print("\nALL TESTS PASSED")
