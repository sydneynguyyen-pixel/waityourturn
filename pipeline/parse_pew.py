import re, csv, sys, json
from collections import Counter

B = "/home/claude/congress"
ROW = re.compile(
    r"^([A-Z]{2})\s+(\d+|AL|At-large|Senator)\s+(.+?)\s{2,}([RDI])\s+(Continuing|Freshman)\s+(.+?)\s*$"
)

def parse(txt):
    out = []
    for line in open(txt):
        m = ROW.match(line.rstrip("\n"))
        if m:
            st, dist, name, party, cf, fam = m.groups()
            out.append(dict(state=st, district=dist, name=name.strip(), party=party,
                            cont_fresh=cf, family=fam.strip()))
    return out

res = {}
for n, fn in ((117, "pew117.txt"), (118, "pew118.txt"), (119, "pew119.txt")):
    rows = parse(f"{B}/pdf/{fn}")
    res[n] = rows
    print(n, len(rows), "rows;",
          "senators", sum(r["district"] == "Senator" for r in rows),
          "house", sum(r["district"] != "Senator" for r in rows))
    print(Counter(r["family"] for r in rows).most_common())

json.dump(res, open(f"{B}/pew_parsed.json", "w"))
