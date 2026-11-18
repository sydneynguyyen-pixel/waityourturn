import csv, json, re, unicodedata
B = "/home/claude/congress"
pew = {int(k): v for k, v in json.load(open(f"{B}/pew_parsed.json")).items()}
roster = list(csv.DictReader(open(f"{B}/base_table.csv")))

PROT = {"Baptist", "Methodist", "Presbyterian", "Episcopalian", "Lutheran", "Congregationalist",
        "Nondenominational", "Restorationist", "Reformed", "Pentecostal", "Adventist", "Pietist",
        "Protestant unspecified"}
def coarse(f):
    if f in PROT: return "Protestant"
    return {"Catholic": "Catholic", "Jewish": "Jewish", "Mormon": "Mormon", "Orthodox": "Orthodox Christian",
            "Muslim": "Muslim", "Hindu": "Hindu", "Buddhist": "Buddhist",
            "Unitarian Universalist": "Unitarian Universalist",
            "Unaffiliated": "Unaffiliated / humanist", "Humanist": "Unaffiliated / humanist",
            "Don't know/refused": "Unknown (declined / not reached)"}.get(f, "Other")

def toks(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().replace("\u2019", "'")
    s = re.sub(r"[^a-z' ]", " ", s.lower().replace("-", " "))
    return [t for t in s.split() if t not in {"jr", "sr", "ii", "iii", "iv"}]

def name_ok(pew_name, ros_name):
    pt, rt = toks(pew_name), toks(ros_name)
    return bool(pt) and pt[-1] in rt

out_rows, unmatched_pew, unmatched_roster = [], [], []
for n in (117, 118, 119):
    ros = [r for r in roster if r["congress"] == str(n) and r["voting"] == "Y" and r["seated_at_start"] == "Y"]
    used = set()
    for p in pew[n]:
        cands = []
        for i, r in enumerate(ros):
            if i in used or r["state"] != p["state"]:
                continue
            if p["district"] == "Senator":
                if r["chamber"] == "Senate" and name_ok(p["name"], r["name"]):
                    cands.append(i)
            else:
                d = "0" if p["district"] in ("AL", "At-large") else p["district"]
                if r["chamber"] == "House" and r["district"] == d:
                    cands.append(i)
        if not cands:
            allv = [r for r in roster if r["congress"] == str(n) and r["voting"] == "Y"]
            for r in allv:
                if r["state"] != p["state"] or r in [ros[j] for j in used]:
                    continue
                if p["district"] == "Senator":
                    ok = r["chamber"] == "Senate" and name_ok(p["name"], r["name"])
                else:
                    d = "0" if p["district"] in ("AL", "At-large") else p["district"]
                    ok = r["chamber"] == "House" and r["district"] == d and name_ok(p["name"], r["name"])
                if ok:
                    ros.append(r); cands.append(len(ros) - 1)
        if len(cands) == 1:
            i = cands[0]; used.add(i); r = ros[i]
            flag = "" if name_ok(p["name"], r["name"]) else "NAME_MISMATCH"
            out_rows.append(dict(congress=n, bioguide=r["bioguide"], roster_name=r["name"], pew_name=p["name"],
                                 chamber=r["chamber"], state=r["state"], district=r["district"],
                                 pew_family=p["family"], religion_group=coarse(p["family"]),
                                 pew_cont_fresh=p["cont_fresh"], check=flag))
        else:
            unmatched_pew.append((n, p, len(cands)))
    for i, r in enumerate(ros):
        if i not in used:
            unmatched_roster.append((n, r["name"], r["chamber"], r["state"], r["district"]))

with open(f"{B}/religion_table.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
    w.writeheader(); w.writerows(out_rows)

print("matched", len(out_rows))
mm = [r for r in out_rows if r["check"]]
print("name mismatches:", len(mm))
for r in mm: print("  ", r["congress"], r["state"], r["district"], "pew:", r["pew_name"], "| roster:", r["roster_name"])
print("pew rows unmatched:", len(unmatched_pew))
for n, p, c in unmatched_pew: print("  ", n, p["state"], p["district"], p["name"], "cands", c)
print("roster members with no pew row:", len(unmatched_roster))
for u in unmatched_roster: print("  ", u)
