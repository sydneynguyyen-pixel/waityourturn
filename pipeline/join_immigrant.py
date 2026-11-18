import csv, re, unicodedata
from collections import Counter, defaultdict
B="/home/claude/congress"
def norm(s):
    s=unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode().lower().replace("’","'")
    return re.sub(r"[^a-z' ]"," ",s.replace("-"," ").replace("."," "))
def toks(s): return [t for t in norm(s).split() if t not in {"jr","sr","ii","iii","iv"}]
roster=list(csv.DictReader(open(f"{B}/base_table.csv")))
# parse raw
data=defaultdict(list); meta={}
cur=None
for line in open(f"{B}/pew_immigrant_raw.txt"):
    line=line.rstrip("\n")
    if line.startswith("#CONGRESS"):
        p=[x.strip() for x in line.split("|")]
        cur=int(p[0].split()[1]); meta[cur]=(p[1].replace("as of ",""),p[2]); continue
    if not line.strip(): continue
    nm,st,orig,party,off,state=line.split("|")
    data[cur].append(dict(name=nm,status="Immigrant (foreign-born)" if st=="I" else "Child of an immigrant",
        origin=orig,party=party,chamber="Senate" if off=="S" else "House",state=state))
stated={119:(19,61),118:(17,64),117:(17,59),116:(16,52),115:(16,48)}
out=[]; problems=[]
for c in sorted(data):
    rows=data[c]
    s=sum(r["chamber"]=="Senate" for r in rows); h=len(rows)-s
    print(c,"rows",len(rows),"Senate",s,"House",h,"| Pew text: Senate/House",stated[c], "OK" if (s,h)==stated[c] else "<-- DIFFERS")
    pool=[r for r in roster if r["congress"]==str(c) and r["voting"]=="Y"]
    used=set()
    for p in rows:
        last,first=[x.strip() for x in p["name"].split(",",1)]
        lt=toks(last)[-1]; ft=toks(first)
        cands=[r for r in pool if r["state"]==p["state"] and lt in toks(r["name"]) and r["chamber"]==p["chamber"]]
        if len(cands)>1:
            c2=[r for r in cands if any(f in toks(r["name"]) for f in ft)]
            cands=c2 or cands
        if not cands:  # chamber may differ in roster (moved chambers)
            cands=[r for r in pool if r["state"]==p["state"] and lt in toks(r["name"])]
            if len(cands)>1:
                cands=[r for r in cands if any(f in toks(r["name"]) for f in ft)] or cands
        if len(cands)==1:
            r=cands[0]
            if r["bioguide"] in used: problems.append((c,"DUP",p["name"])); 
            used.add(r["bioguide"])
            out.append(dict(congress=c,bioguide=r["bioguide"],roster_name=r["name"],pew_name=p["name"],
               status=p["status"],origin=p["origin"],chamber=r["chamber"],state=r["state"],
               pew_as_of=meta[c][0],pew_source=meta[c][1]))
        else:
            problems.append((c,len(cands),p["name"],p["state"],p["chamber"]))
print("matched",len(out),"problems:",problems)
w=csv.DictWriter(open(f"{B}/immigrant_table.csv","w",newline=""),fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
