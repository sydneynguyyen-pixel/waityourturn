"""Median age and members aged 70+ on opening day, 1st-119th Congress.
Same rules as build_base.py: a member counts if one of their terms covers opening day, voting members only,
age = (opening day - birthday) / 365.2425. Opening day is the day the Congress first convened, taken as the most
common House term start in the data between its legal start (March 4 to 1933, January 3 from 1935) and the next one.
For the 115th-119th that is January 3, matching the chamber. Territorial delegates are left out until statehood.
Run from the project root: python3 pipeline/build_history.py  ->  data/age_by_congress.csv"""
import json, csv, statistics
from datetime import date
from collections import Counter

RAW = "data/raw"
NONVOTING = {"AS", "DC", "GU", "MP", "PR", "VI", "PI"}
# admission dates; a House member from a state before this date was a non-voting territorial delegate
ADMITTED = {"VT": "1791-03-04", "KY": "1792-06-01", "TN": "1796-06-01", "OH": "1803-03-01", "LA": "1812-04-30",
    "IN": "1816-12-11", "MS": "1817-12-10", "IL": "1818-12-03", "AL": "1819-12-14", "ME": "1820-03-15",
    "MO": "1821-08-10", "AR": "1836-06-15", "MI": "1837-01-26", "FL": "1845-03-03", "TX": "1845-12-29",
    "IA": "1846-12-28", "WI": "1848-05-29", "CA": "1850-09-09", "MN": "1858-05-11", "OR": "1859-02-14",
    "KS": "1861-01-29", "WV": "1863-06-20", "NV": "1864-10-31", "NE": "1867-03-01", "CO": "1876-08-01",
    "ND": "1889-11-02", "SD": "1889-11-02", "MT": "1889-11-08", "WA": "1889-11-11", "ID": "1890-07-03",
    "WY": "1890-07-10", "UT": "1896-01-04", "OK": "1907-11-16", "NM": "1912-01-06", "AZ": "1912-02-14",
    "AK": "1959-01-03", "HI": "1959-08-21"}
ORIGINAL = {"DE", "PA", "NJ", "GA", "CT", "MA", "MD", "SC", "NH", "VA", "NY", "NC", "RI"}
STATES = ORIGINAL | set(ADMITTED)

def d(s):
    y, m, dd = map(int, str(s).split("-"))
    return date(y, m, dd)

def legal(n):
    y = 1789 + 2 * (n - 1)
    return date(y, 3, 4) if n <= 73 else date(y, 1, 3)

def voting(t, day):
    st = t["state"]
    if st in NONVOTING or st not in STATES:
        return False
    return st in ORIGINAL or day >= d(ADMITTED[st])

people = []
for fn in ("legislators-current.json", "legislators-historical.json"):
    people += json.load(open(f"{RAW}/{fn}"))

starts = Counter(d(t["start"]) for p in people for t in p["terms"] if t["type"] == "rep")
def opening(n):
    a, b = legal(n), legal(n + 1)
    return max((c, -x.toordinal(), x) for x, c in starts.items() if a <= x < b)[2]

rows = []
for n in range(1, 120):
    day = opening(n)
    seated, ages = 0, []
    for p in people:
        if not any(d(t["start"]) <= day < d(t["end"]) and voting(t, day) for t in p["terms"]):
            continue
        seated += 1
        b = p["bio"].get("birthday")
        if b:
            ages.append((day - d(b)).days / 365.2425)
    rows.append(dict(congress=n, opening_day=day.isoformat(), seated=seated, known_age=len(ages),
        median_age=round(statistics.median(ages), 1), age70plus=sum(a >= 70 for a in ages)))

with open("data/age_by_congress.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print("wrote data/age_by_congress.csv")
