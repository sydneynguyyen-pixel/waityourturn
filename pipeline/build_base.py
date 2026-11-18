import sys, yaml, csv, statistics
from datetime import date

RAW = sys.argv[1]
OUT = sys.argv[2]
NONVOTING = {"AS", "DC", "GU", "MP", "PR", "VI"}

def cong_start(n):
    return date(1789 + 2 * (n - 1), 1, 3)

def d(s):
    y, m, dd = map(int, str(s).split("-"))
    return date(y, m, dd)

people = []
for fn in ("legislators-current.yaml", "legislators-historical.yaml"):
    with open(f"{RAW}/{fn}") as f:
        people += yaml.load(f, Loader=yaml.CSafeLoader)

rows = []
for p in people:
    ids = p["id"]
    bg = ids.get("bioguide")
    bday = d(p["bio"]["birthday"]) if p["bio"].get("birthday") else None
    for n in range(115, 120):
        cs, ce = cong_start(n), cong_start(n + 1)
        hits = [t for t in p["terms"] if d(t["start"]) < ce and d(t["end"]) > cs]
        if not hits:
            continue
        at_start = [t for t in hits if d(t["start"]) <= cs < d(t["end"])]
        t = (at_start or hits)[-1]
        age = None
        if bday:
            age = round((cs - bday).days / 365.2425, 1)
        rows.append(dict(
            congress=n, bioguide=bg, name=p["name"].get("official_full") or f'{p["name"]["first"]} {p["name"]["last"]}',
            chamber="Senate" if t["type"] == "sen" else "House",
            state=t["state"], district=t.get("district", ""), senate_class=t.get("class", ""),
            party=t.get("party", ""), gender=p["bio"].get("gender", ""),
            birthday=str(bday) if bday else "", age_at_congress_start=age,
            voting=("N" if t["state"] in NONVOTING else "Y"),
            seated_at_start=("Y" if at_start else "N"),
            term_start=t["start"], term_end=t["end"],
            icpsr=ids.get("icpsr", ""), govtrack=ids.get("govtrack", ""),
            wikipedia=ids.get("wikipedia", ""), ballotpedia=ids.get("ballotpedia", ""),
        ))

rows.sort(key=lambda r: (r["congress"], r["chamber"], r["state"], str(r["district"]), r["name"]))
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print("congress chamber seated_voting served_any_voting median_age_seated mean_age_seated")
for n in range(115, 120):
    for ch in ("House", "Senate"):
        sub = [r for r in rows if r["congress"] == n and r["chamber"] == ch and r["voting"] == "Y"]
        seated = [r for r in sub if r["seated_at_start"] == "Y"]
        ages = [r["age_at_congress_start"] for r in seated if r["age_at_congress_start"]]
        print(n, ch, len(seated), len(sub), round(statistics.median(ages), 1), round(statistics.mean(ages), 1))
missing = [r for r in rows if not r["bioguide"]]
print("rows:", len(rows), "missing bioguide:", len(missing),
      "missing birthday:", sum(1 for r in rows if not r["birthday"]))
