import urllib.request

req = urllib.request.Request("http://localhost:8080/pillars")
resp = urllib.request.urlopen(req, timeout=10)
html = resp.read().decode("utf-8", errors="replace")
print(f"Status: {resp.status}")
print(f"Length: {len(html)} bytes")

checks = [
    ("Title", "Better"),
    ("Vision header", "Better, Faster and Closer to Customer"),
    ("Pillar cards", "pillar-card"),
    ("Radar chart", "pillarRadarChart"),
    ("Gap chart", "gapBarChart"),
    ("BFC report section", "Better-Faster-Closer Report"),
    ("Matrix table", "Dimension x Pillar"),
    ("Alpine.js", "alpinejs"),
    ("Chart.js", "chart.js"),
]
for name, keyword in checks:
    found = keyword in html
    status = "OK" if found else "MISS"
    print(f"  [{status}] {name}: {keyword}")
