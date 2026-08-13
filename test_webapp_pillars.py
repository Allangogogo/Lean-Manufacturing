import urllib.request, json

# Test webapp pillars dashboard API
req = urllib.request.Request("http://localhost:8080/api/v1/pillars/dashboard")
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())
oc = data.get("overall_composite") or "-"
ol = data.get("overall_level") or "-"
print(f"Overall: {oc} / {ol}")
for p in data.get("pillars", []):
    cc = p.get("current_composite") or "-"
    tc = p.get("target_composite")
    wd = p.get("weakest_dimension") or "-"
    name = p.get("name_en", "?")
    print(f"  {name}: {cc}/{tc} weakest={wd}")

# Test BFC report
print()
req = urllib.request.Request("http://localhost:8080/api/v1/lean20/report/3")
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())
print(f"BFC Report: Overall {data.get('overall_composite')} / {data.get('overall_level')}")
print(f"Weakest: {data.get('weakest_pillar')}")
for p in data.get("pillars", []):
    name = p.get("pillar_name", "?")
    comp = p.get("composite")
    target = p.get("target")
    gap = p.get("gap")
    print(f"  {name}: {comp}/{target} gap={gap}")
