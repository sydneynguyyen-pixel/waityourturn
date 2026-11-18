"""Builds ../chamber.html: reads data/ and injects it into src/template.html. Run: python3 src/build.py"""
import json,csv,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D=lambda f:os.path.join(R,"data",f)
base=list(csv.DictReader(open(D("base_table.csv"))))
P={"Democrat":"D","Republican":"R"}
data={}
def yrs(b,y):  # whole years on January 3 of year y
    by,bm,bd=map(int,b.split("-"));return y-by-((bm,bd)>(1,3))
for c in range(115,120):
    rows=[]
    for r in base:
        if r["congress"]==str(c) and r["voting"]=="Y" and r["seated_at_start"]=="Y":
            nom=r["vv_nominate_dim1"]
            rows.append([r["bioguide"],r["name"],r["chamber"][0],r["state"],P.get(r["party"],"I"),round(float(r["age_at_congress_start"]),1),int(r["birthday"][:4]),round(float(nom),3) if nom else None,yrs(r["birthday"],2*c+1787)])
    data[c]=rows
ext={}
for x in json.load(open(D("merged_119.json"))):
    if x["voting_member"]!="Y" or x["seated_at_start"]!="Y": continue
    race=[] if x["race_ethnicity_groups"].startswith("not listed") else x["race_ethnicity_groups"].split("; ")
    rel=x["religion_group"]; rel="" if rel=="not in Pew list" or rel.startswith("Unknown") else rel
    imm="" if x["immigrant_background"].startswith("not listed") else x["immigrant_background"]
    ext[x["bioguide"]]=[x["gender"],rel,race,imm,"".join((x[f"v{i}"] or "-") for i in range(1,15))]
EX={r["slot"]:r for r in csv.DictReader(open(D("quiz_explainers.csv")))}
votes=[{"n":int(q["slot"]),"area":q["area"],"t":q["short_title"],"y":q["yes_means"],"no":q["no_means"],"hr":int(q["house_rollnumber"]),"hd":q["house_date"],"sr":int(q["senate_rollnumber"]),"sd":q["senate_date"],"ht":q["house_tally_yea_nay"],"st":q["senate_tally_yea_nay"],"bill":EX[q["slot"]]["bill"],"url":EX[q["slot"]]["url"],"url2":EX[q["slot"]]["url2"],"law":EX[q["slot"]]["became_law"]=="1","what":EX[q["slot"]]["what_it_does"],"q":EX[q["slot"]]["question"],"o":int(EX[q["slot"]]["quiz_order"])} for q in csv.DictReader(open(D("quiz_vote_candidates.csv"))) if q["slot"].isdigit() and EX[q["slot"]]["quiz_order"]]
votes.sort(key=lambda v:v["o"])  # the Issues tab asks only the votes with a quiz_order, in that order
pop={int(r["year"]):float(r["median_age_pop"]) for r in csv.DictReader(open(D("population_age_baseline.csv")))}
tl=[[int(r["gen"]),r["when"],int(r["year"]),r["text"],r["source"],r["url"]] for r in csv.DictReader(open(D("generation_timeline.csv")))]
hist=[[int(r["congress"]),r["opening_day"],int(r["seated"]),int(r["known_age"]),float(r["median_age"]),int(r["age70plus"])] for r in csv.DictReader(open(D("age_by_congress.csv")))]
# game ("Wait your turn"): for each 115th member, [first year in Congress, seat label, first Congress they are gone from that chamber (0 = still there in the 119th), who took the seat ("" unless a brand-new member holds the same seat number), 1 if they moved to the other chamber]
raw={p["id"]["bioguide"]:p for f in ("legislators-current.json","legislators-historical.json") for p in json.load(open(D("raw/"+f)))}
seat={};key=lambda r:(r["chamber"],r["state"],r["district"] if r["chamber"]=="House" else r["senate_class"])
for r in base:
    if r["voting"]=="Y" and r["seated_at_start"]=="Y": seat.setdefault(int(r["congress"]),{})[r["bioguide"]]=r
game={}
for b,r in seat[115].items():
    lab=r["state"]+" Senate" if r["chamber"]=="Senate" else r["state"]+(" at-large" if r["district"] in ("0","") else "-"+r["district"])
    out,succ,moved=0,"",0
    for c in range(116,120):
        x=seat[c].get(b)
        if x and x["chamber"]==r["chamber"]: continue
        out=c;moved=int(bool(x))
        h=[y for y in seat[c].values() if key(y)==key(r)]
        if len(h)==1 and h[0]["bioguide"] not in seat[c-1]: succ=h[0]["bioguide"]
        break
    game[b]=[min(int(t["start"][:4]) for t in raw[b]["terms"]),lab,out,succ,moved]
S=lambda f:open(os.path.join(R,"src",f)).read()  # the game lives in src/game.html, game.css and game.js
import base64
bg="data:image/webp;base64,"+base64.b64encode(open(os.path.join(R,"game-assets","capitol-sunrise.webp"),"rb").read()).decode()  # page background for the ASCII look, inlined so chamber.html stays one file
blob=json.dumps({"bg":bg,"game":game,"stitch":json.load(open(D("stitch_capitol.json"))),"data":data,"ext":ext,"votes":votes,"pop":pop,"hist":hist,"tl":tl,"fimg":json.load(open(D("fact_img.json"))),"img":json.load(open(D("img.json")))},separators=(",",":"))
open(os.path.join(R,"chamber.html"),"w").write(open(os.path.join(R,"src","template.html")).read().replace("<!--GAME_HTML-->",S("game.html")).replace("/*GAME_CSS*/",S("game.css")).replace("/*GAME_JS*/",S("game.js")).replace("/*DATA*/",blob))
print("built chamber.html")
