import csv
from collections import defaultdict, Counter
B="/home/claude/congress"
cands=[r for r in csv.DictReader(open(f"{B}/quiz_vote_candidates.csv")) if r["slot"].isdigit()]
roster=[r for r in csv.DictReader(open(f"{B}/base_table.csv")) if r["congress"]=="119"]
vm={r["icpsr"]:r for r in csv.DictReader(open(f"{B}/up/HS119_members.csv")) if r["chamber"] in("House","Senate") and r["bioguide_id"]}
byg={r["bioguide"]:r for r in roster}
# index votes
need=defaultdict(dict)  # (chamber,roll)->{icpsr:cast}
want=set()
for c in cands:
    want.add(("House",c["house_rollnumber"])); want.add(("Senate",c["senate_rollnumber"]))
for v in csv.DictReader(open(f"{B}/up/HS119_votes.csv")):
    k=(v["chamber"],v["rollnumber"])
    if k in want: need[k][v["icpsr"]]=int(v["cast_code"])
def code(x): return "Y" if x in (1,2,3) else "N" if x in (4,5,6) else ""
# verify tallies vs rollcalls
rc={(r["chamber"],r["rollnumber"]):r for r in csv.DictReader(open(f"{B}/up/HS119_rollcalls.csv"))}
bad=0
for k in sorted(want):
    y=sum(1 for x in need[k].values() if x in(1,2,3)); n=sum(1 for x in need[k].values() if x in(4,5,6))
    r=rc[k]
    if (y,n)!=(int(r["yea_count"]),int(r["nay_count"])): bad+=1; print("TALLY MISMATCH",k,(y,n),(r["yea_count"],r["nay_count"]))
print("tally check: mismatches",bad,"of",len(want))
# member rows
out=[]; unmapped=Counter()
members={}
for ic,m in vm.items():
    r=byg.get(m["bioguide_id"])
    if r and r["voting"]=="Y":
        rr=dict(r); rr["chamber"]=m["chamber"]; members[ic]=rr
for ic,r in members.items():
    row=dict(bioguide=r["bioguide"],name=r["name"],chamber=r["chamber"],state=r["state"],district=r["district"],party=r["party"])
    cast=0; elig=0
    for c in cands:
        roll=c["house_rollnumber"] if r["chamber"]=="House" else c["senate_rollnumber"]
        k=("House" if r["chamber"]=="House" else "Senate",roll)
        x=need[k].get(ic)
        v=code(x) if x is not None else ""
        row["v"+c["slot"]]=v
        if v: cast+=1
    row["votes_cast"]=cast
    out.append(row)
# votes cast by icpsr not in roster (e.g. members who left / chamber switch)
for k in want:
    for ic in need[k]:
        if ic not in members: unmapped[ic]+=1
print("members",len(out),"; icpsr voting ids not in roster:",len(unmapped))
w=csv.DictWriter(open(f"{B}/quiz_votes_matrix.csv","w",newline=""),fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
dist=Counter(r["votes_cast"] for r in out)
print("votes cast distribution:",sorted(dist.items()))
low=[(r["name"],r["chamber"],r["votes_cast"]) for r in out if r["votes_cast"]<8]
print("members with <8 of 14:",len(low)); print(low)
