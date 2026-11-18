import csv, statistics
from collections import defaultdict

B = "/home/claude/congress"
roster = list(csv.DictReader(open(f"{B}/base_table_roster.csv")))

# ---- Voteview ----
vv = defaultdict(list)
for r in csv.DictReader(open(f"{B}/up/HSall_members.csv")):
    c = int(r["congress"])
    if 115 <= c <= 119 and r["chamber"] != "President":
        vv[(r["bioguide_id"], c)].append(r)

cols = ["nominate_dim1", "nominate_dim2", "nokken_poole_dim1", "nominate_number_of_votes", "conditional"]
matched = unmatched = multi = 0
for r in roster:
    k = (r["bioguide"], int(r["congress"]))
    hits = vv.get(k, [])
    # prefer the row in the same chamber
    same = [h for h in hits if h["chamber"] == r["chamber"]]
    use = same or hits
    if len(use) > 1:
        multi += 1
    if use:
        h = use[0]
        matched += 1
        for c in cols:
            r["vv_" + c] = h[c]
    else:
        unmatched += 1
        for c in cols:
            r["vv_" + c] = ""
print("voteview matched", matched, "unmatched", unmatched, "multi-row", multi)

# who is unmatched among voting members seated at start?
um = [r for r in roster if r["vv_nominate_dim1"] == "" and r["voting"] == "Y" and r["seated_at_start"] == "Y"]
print("seated voting members with no NOMINATE score:", len(um))
by = defaultdict(int)
for r in um:
    by[int(r["congress"])] += 1
print(dict(sorted(by.items())))
print([f'{r["name"]} ({r["congress"]})' for r in um if int(r["congress"]) == 119][:15])
print("conditional=1 (provisional) count, 119th:",
      sum(1 for r in roster if r["congress"] == "119" and r["vv_conditional"] == "1"))

# ---- Census ----
pop = {}
for r in csv.DictReader(open(f"{B}/up/census_agesex.csv")):
    if r["SEX"] == "0":
        pop[int(r["AGE"])] = {y: int(r[f"POPESTIMATE{y}"]) for y in range(2020, 2026)}
tot = {y: pop[999][y] for y in range(2020, 2026)}
census = []
for y in range(2020, 2026):
    ages = {a: pop[a][y] for a in pop if a != 999}
    def share(lo, hi):
        return sum(v for a, v in ages.items() if lo <= a <= hi)
    adults = share(18, 100)
    # median age (age 100 = 100+)
    cum, half = 0, tot[y] / 2
    for a in sorted(ages):
        cum += ages[a]
        if cum >= half:
            med = a
            break
    census.append(dict(
        year=y, total_pop=tot[y], adults_18plus=adults,
        pct_under_25_of_total=round(100 * share(0, 24) / tot[y], 1),
        pct_under_30_of_total=round(100 * share(0, 29) / tot[y], 1),
        pct_of_adults_aged_18_24=round(100 * share(18, 24) / adults, 1),
        pct_of_adults_aged_18_29=round(100 * share(18, 29) / adults, 1),
        pct_aged_25plus_of_total=round(100 * share(25, 100) / tot[y], 1),
        pct_aged_30plus_of_total=round(100 * share(30, 100) / tot[y], 1),
        pct_aged_65plus_of_total=round(100 * share(65, 100) / tot[y], 1),
        median_age_pop=med,
    ))
for c in census:
    print(c)

# ---- write outputs ----
with open(f"{B}/base_table.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(roster[0].keys()))
    w.writeheader(); w.writerows(roster)
with open(f"{B}/population_age_baseline.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(census[0].keys()))
    w.writeheader(); w.writerows(census)

# ---- comparison for the 119th ----
seated = [r for r in roster if r["congress"] == "119" and r["voting"] == "Y" and r["seated_at_start"] == "Y"]
ages = [float(r["age_at_congress_start"]) for r in seated]
print("119th seated voting:", len(seated), "median age", round(statistics.median(ages), 1),
      "under 40:", sum(a < 40 for a in ages), "under 30:", sum(a < 30 for a in ages),
      "over 70:", sum(a >= 70 for a in ages), "oldest", max(ages), "youngest", min(ages))
