"""Summary numbers for the data analysis report. Run from the project root: python3 analysis/analyze.py -> analysis/results.json"""
import csv, json, statistics as st, importlib.util, sys
from collections import Counter
from datetime import date

def rd(f): return list(csv.DictReader(open(f"data/{f}")))
def d(s):
    y, m, dd = map(int, str(s).split("-")); return date(y, m, dd)
def gen(y): return 0 if y >= 1997 else 1 if y >= 1981 else 2 if y >= 1965 else 3 if y >= 1946 else 4
GEN = ["Gen Z", "Millennial", "Gen X", "Boomer", "Silent"]
R = {}

base = rd("base_table.csv"); m119 = rd("merged_119.csv"); hist = rd("age_by_congress.csv"); pop = rd("population_age_baseline.csv")
people = json.load(open("data/raw/legislators-current.json")) + json.load(open("data/raw/legislators-historical.json"))
R["inventory"] = {"raw_people": len(people), "raw_terms": sum(len(p["terms"]) for p in people), "raw_no_birthday": sum(not p["bio"].get("birthday") for p in people),
    "base_rows": len(base), "base_cols": len(base[0]), "m119_rows": len(m119), "m119_cols": len(m119[0]), "hist_rows": len(hist), "hist_cols": len(hist[0]), "pop_rows": len(pop), "pop_cols": len(pop[0]),
    "portraits": len(json.load(open("data/img.json")))}

seat = lambda c: [r for r in base if r["congress"] == str(c) and r["voting"] == "Y" and r["seated_at_start"] == "Y"]
R["funnel"] = {c: {"rows": sum(r["congress"] == str(c) for r in base), "nonvoting": sum(r["congress"] == str(c) and r["voting"] != "Y" for r in base),
    "not_seated": sum(r["congress"] == str(c) and r["voting"] == "Y" and r["seated_at_start"] != "Y" for r in base), "seated": len(seat(c)),
    "no_birthday": sum(not r["birthday"] for r in seat(c)), "no_nominate": sum(not r["vv_nominate_dim1"] for r in seat(c))} for c in range(115, 120)}

R["congress"] = {}; prev = None
for c in range(115, 120):
    s = seat(c); a = [float(r["age_at_congress_start"]) for r in s]
    g = Counter(gen(int(r["birthday"][:4])) for r in s); ids = {r["bioguide"] for r in s}
    x = {"n": len(s), "median": round(st.median(a), 1), "mean": round(st.mean(a), 1), "min": min(a), "max": max(a), "a70": sum(v >= 70 for v in a), "a80": sum(v >= 80 for v in a), "u40": sum(v < 40 for v in a),
        "gen": {GEN[i]: g[i] for i in range(5)}}
    for k, f in (("House", lambda r: r["chamber"] == "House"), ("Senate", lambda r: r["chamber"] == "Senate"), ("Dem", lambda r: r["party"] == "Democrat"), ("Rep", lambda r: r["party"] == "Republican")):
        v = [float(r["age_at_congress_start"]) for r in s if f(r)]; x[k] = {"n": len(v), "median": round(st.median(v), 1), "a70": sum(q >= 70 for q in v)}
    if prev:
        new = [float(r["age_at_congress_start"]) for r in s if r["bioguide"] not in prev]; ret = [float(r["age_at_congress_start"]) for r in s if r["bioguide"] in prev]
        x["new"] = {"n": len(new), "median": round(st.median(new), 1)}; x["returning"] = {"n": len(ret), "median": round(st.median(ret), 1)}
    prev = ids; R["congress"][c] = x

# Who are the 70+ members of the 119th: already seated in the 115th?
s119 = seat(119); ids115 = {r["bioguide"] for r in seat(115)}; o = [r for r in s119 if float(r["age_at_congress_start"]) >= 70]
R["old119"] = {"n": len(o), "in115": sum(r["bioguide"] in ids115 for r in o)}

# Tenure and entry age for every Congress, using the same seating rules as build_history
spec = importlib.util.spec_from_file_location("h", "pipeline/build_history.py")
src = open("pipeline/build_history.py").read().split("rows = []")[0]; ns = {}; exec(src, ns)
tr = []
for n in range(1, 120):
    day = ns["opening"](n); ten, ent, ages = [], [], []
    for p in people:
        if not any(d(t["start"]) <= day < d(t["end"]) and ns["voting"](t, day) for t in p["terms"]): continue
        ts = sorted(p["terms"], key=lambda t: t["start"]); days = 0
        for t in ts:
            a, b = d(t["start"]), min(d(t["end"]), day)
            if b > a: days += (b - a).days
        ten.append(days / 365.2425); bd = p["bio"].get("birthday")
        if bd:
            ent.append((d(ts[0]["start"]) - d(bd)).days / 365.2425); ages.append((day - d(bd)).days / 365.2425)
    tr.append({"c": n, "year": day.year, "tenure": round(st.median(ten), 1), "entry": round(st.median(ent), 1), "age": round(st.median(ages), 1)})
R["tenure"] = tr

# Congress vs adults, 2025
p25 = [r for r in pop if r["year"] == "2025"][0]; adults, total = float(p25["adults_18plus"]), float(p25["total_pop"])
a119 = [float(r["age_at_congress_start"]) for r in s119]; n = len(a119)
R["pop"] = {"row": p25, "adult_65": round(float(p25["pct_aged_65plus_of_total"]) * total / adults, 1), "adult_18_29": float(p25["pct_of_adults_aged_18_29"]),
    "cong_u30": sum(v < 30 for v in a119), "cong_u30_pct": round(100 * sum(v < 30 for v in a119) / n, 1), "cong_65": sum(v >= 65 for v in a119), "cong_65_pct": round(100 * sum(v >= 65 for v in a119) / n, 1)}
R["hist119"] = Counter(int(v // 5 * 5) for v in a119)

# 119th missingness and votes
m = [r for r in m119 if r["voting_member"] == "Y" and r["seated_at_start"] == "Y"]
R["m119"] = {"n": len(m), "race_unlisted": sum(r["race_ethnicity_groups"].startswith("not listed") for r in m), "rel_missing": sum(r["religion_group"] == "not in Pew list" or r["religion_group"].startswith("Unknown") for r in m),
    "imm_unlisted": sum(r["immigrant_background"].startswith("not listed") for r in m), "imm_values": Counter(r["immigrant_background"] for r in m), "rel_values": Counter(r["religion_group"] for r in m).most_common(12)}
qx = {q["slot"]: q for q in rd("quiz_explainers.csv")}; qc = {q["slot"]: q for q in rd("quiz_vote_candidates.csv") if q["slot"].isdigit()}
V = []
for sl, q in qx.items():
    if not q["quiz_order"]: continue
    k = f"v{sl}"; row = {"order": int(q["quiz_order"]), "t": qc[sl]["short_title"], "slot": sl}
    for v in "YN":
        a = [float(r["age_at_congress_start"]) for r in m if r[k] == v]; row[v] = {"n": len(a), "median": round(st.median(a), 1) if a else None}
        for pty in ("Democrat", "Republican"): row[v][pty] = sum(r[k] == v and r["party"] == pty for r in m)
    row["absent"] = sum(r[k] not in ("Y", "N") for r in m); V.append(row)
R["votes"] = sorted(V, key=lambda x: x["order"]); R["vote_values"] = Counter(r["v1"] for r in m)

def pear(x, y):
    mx, my = st.mean(x), st.mean(y); return round(sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)) ** .5, 3)
R["corr"] = {}
for pty in ("Democrat", "Republican"):
    z = [(float(r["age_at_congress_start"]), float(r["nominate_dim1"])) for r in m if r["party"] == pty and r["nominate_dim1"]]
    R["corr"][pty] = {"n": len(z), "r": pear(*zip(*z))}
json.dump(R, open("analysis/results.json", "w"), indent=1, default=str)
for k in R:
    if k != "tenure": print(k, json.dumps(R[k], default=str)[:1700])
for t in R["tenure"]:
    if t["c"] in (1, 20, 40, 60, 70, 80, 90, 94, 95, 96, 97, 98, 100, 105, 110, 115, 116, 117, 118, 119): print(t)
