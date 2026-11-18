import csv, re, unicodedata
from collections import defaultdict, Counter

B = "/home/claude/congress"
roster = list(csv.DictReader(open(f"{B}/base_table.csv")))

def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = s.replace("’", "'")
    return re.sub(r"[^a-z' ]", " ", s.replace("-", " "))

def toks(s):
    return [t for t in norm(s).split() if t not in {"jr", "sr", "ii", "iii", "iv", "mr", "dr"}]

# unique members across 115-119
members = {}
for r in roster:
    members.setdefault(r["bioguide"], r)

LIFE = re.compile(r"^(.{3,80})\n\((?:born |b\. )?(\d{4})(?:[–-](?:\d{4}|present))?\)\s*$", re.M)

LISTS = {
    "Hispanic or Latino": ("hisp_raw.txt", "Wikipedia: List of Hispanic and Latino Americans in the US Congress (lineage from Spain/Latin America; includes Brazil, excludes Portugal)"),
    "Asian American / Pacific Islander": ("asian_raw.txt", "Wikipedia: List of Asian Americans and Pacific Islander Americans in the US Congress"),
    "Native American": ("native_raw.txt", "Wikipedia: List of Native Americans in the US Congress (documented tribal ancestry/affiliation; excludes Native Hawaiians)"),
    "Black or African American": ("black_reps_raw.txt", "Wikipedia: List of African-American US representatives (House only)"),
}
# Note (2026): this script only read the House list. Black senators in data/merged_119 (Booker, Warnock, Alsobrooks, plus
# Blunt Rochester and Tim Scott, who are also on the House list) match Wikipedia's "List of African-American United States
# senators"; the step that added them is not in this folder. That list is cited on the Sources page.

def entries(fn):
    txt = open(f"{B}/pdf/{fn}").read()
    out = []
    for m in LIFE.finditer(txt):
        name = m.group(1).strip()
        # drop obvious non-name lines
        if len(name.split()) > 7 or any(c.isdigit() for c in name):
            continue
        out.append((name, int(m.group(2))))
    return out


def load(fn):
    t = open(f"{B}/pdf/{fn}").read()
    t = re.sub(r"\[[^\]]*\]", "", t)           # drop footnote markers like [note 3] / [12]
    return norm(t).replace("  ", " ")

BORN = re.compile(r"\(\s*(?:born |b )?\s*(\d{4})")
tags = defaultdict(list)
unmatched = defaultdict(list)
for group, (fn, src) in LISTS.items():
    raw = open(f"{B}/pdf/{fn}").read()
    raw = re.sub(r"\[[^\]]*\]", "", raw)
    txt = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode().lower().replace("\u2019", "'")
    txt = re.sub(r"\s+", " ", txt)
    for bg, r in members.items():
        by = int(r["birthday"][:4])
        t = toks(r["name"])
        last = t[-1]
        firsts = [x for x in t[:-1] if len(x) >= 3] or [t[0]]
        found = None
        for fst in firsts:
            for m in re.finditer(rf"\b{re.escape(fst)}\b[a-z' .\"]{{0,30}}?\b{re.escape(last)}\b", txt):
                tail = txt[m.end(): m.end() + 220]
                for b in BORN.finditer(tail):
                    if abs(int(b.group(1)) - by) <= 2:
                        found = m.group(0); break
                if found: break
            if found: break
        if found:
            tags[bg].append((group, src, found))


# second method: explicit "Name\n(born YYYY)" list entries, footnotes stripped, +-2y tolerance
def entries2(fn):
    txt = re.sub(r"\[[^\]]*\]", "", open(f"{B}/pdf/{fn}").read())
    out = []
    for m in LIFE.finditer(txt):
        name = m.group(1).strip()
        if len(name.split()) > 7 or any(c.isdigit() for c in name):
            continue
        out.append((name, int(m.group(2))))
    return out
for group, (fn, src) in LISTS.items():
    for name, by in entries2(fn):
        nt = toks(name)
        if not nt: continue
        for bg, r in members.items():
            if abs(int(r["birthday"][:4]) - by) > 2: continue
            rt = toks(r["name"])
            if nt[-1] in rt and any(x in rt for x in nt[:-1]) or (len(nt) == 1 and nt[0] in rt):
                if not any(t[0] == group for t in tags[bg]):
                    tags[bg].append((group, src, name))
print("members tagged:", len(tags))
for g in LISTS:
    print(g, sum(1 for bg in tags if any(t[0] == g for t in tags[bg])))

with open(f"{B}/race_table_draft.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["bioguide", "name", "group", "source", "listed_as"])
    for bg, lst in tags.items():
        for g, s, n in lst:
            w.writerow([bg, members[bg]["name"], g, s, n])

# counts per Congress (voting, seated at start) by group
print("\nseated-at-start voting members tagged, by Congress")
for c in range(115, 120):
    rs = [r for r in roster if r["congress"] == str(c) and r["voting"] == "Y" and r["seated_at_start"] == "Y"]
    cnt = Counter()
    anytag = 0
    for r in rs:
        gs = {t[0] for t in tags.get(r["bioguide"], [])}
        for g in gs: cnt[(r["chamber"], g)] += 1
        if gs: anytag += 1
    print(c, len(rs), "any non-White tag:", anytag, dict(sorted(cnt.items())))
