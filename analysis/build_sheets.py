"""Writes the design system and assets sheets (proposal/sheets/*.html) from the site's real tokens and halftone data."""
import csv, json, os
GC = ["#c9ad3b", "#45a86f", "#e98dca", "#9e63d6", "#ae6c18"]
def gi(y): return 0 if y >= 1997 else 1 if y >= 1981 else 2 if y >= 1965 else 3 if y >= 1946 else 4
IMG = json.load(open("data/img.json")); FI = json.load(open("data/fact_img.json"))
rows = [r for r in csv.DictReader(open("data/base_table.csv")) if r["congress"] == "119" and r["seated_at_start"] == "Y" and r["voting"] == "Y" and r["bioguide"] in IMG]
rows.sort(key=lambda r: r["birthday"], reverse=True)
N = 30; pick = [rows[round(i * (len(rows) - 1) / (N - 1))] for i in range(N)]
P = [{"g": IMG[r["bioguide"]], "c": GC[gi(int(r["birthday"][:4]))]} for r in pick]
Y, O = rows[0], rows[-1]
EV = [("3-20-1969", "1969"), ("4-20-1957", "1957"), ("2-20-1989", "1989"), ("1-20-2007", "2007"), ("3-born-1947", "1947"), ("2-born-1974", "1974"), ("1-born-1986", "1986"), ("0-20-2020", "2020")]
E = [{"g": FI[k]["g"], "c": GC[int(k[0])], "y": y} for k, y in EV]
credits = "; ".join(f'{FI[k].get("artist") or "Unknown"} ({FI[k]["license"]})' for k, _ in EV)
TILES = [("Superman", 1938, 4), ("Barbie", 1959, 3), ("Star Wars", 1977, 3), ("Friends", 1994, 2), ("TikTok", 2018, 0)]

HEAD = """<!doctype html><meta charset=utf-8><link rel=stylesheet href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=Instrument+Serif:ital@1&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>:root{--paper:#fdfcfa;--panel:#f2f0ea;--ink:#121212;--mute:#6d6b66;--soft:#e9e7e2;--sun:#f7c600;--pink:#e98dca;--display:"Archivo",Arial,sans-serif;--serif:"Instrument Serif",Georgia,serif;--mono:"IBM Plex Mono",monospace;--body:"IBM Plex Sans",sans-serif}
*{box-sizing:border-box}html,body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.45 var(--body)}
.page{width:1360px;min-height:100vh;padding:44px 48px;display:flex;flex-direction:column;gap:18px;overflow:hidden}
.top{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:3px solid var(--ink);padding-bottom:14px}
.top h1{font:900 66px/.9 var(--display);font-stretch:112%;letter-spacing:-.045em;margin:0}.top h1 em{font:italic 400 70px/.9 var(--serif);letter-spacing:-.01em}
.mono,.lab{font:500 12px/1.4 var(--mono);text-transform:uppercase;letter-spacing:.07em;color:var(--mute)}
.p{background:var(--panel);border-radius:24px;padding:24px 26px;min-width:0}.p h2{font:900 26px/1 var(--display);font-stretch:108%;letter-spacing:-.03em;margin:0 0 16px}
.row{display:grid;gap:18px}canvas{display:block}
button{font:500 13px var(--body);color:var(--ink);background:transparent;border:2px solid var(--ink);border-radius:999px;padding:5px 13px}button.on{background:var(--ink);color:var(--paper)}
</style>"""
HT = """<script>const dec=b=>{const s=atob(b),g=new Uint8Array(s.length);for(let i=0;i<s.length;i++)g[i]=s.charCodeAt(i);return g};
function seat(c,grid,chip,dot,gain){const x=c.getContext('2d'),w=c.width,h=c.height,cols=24,rows=30;x.save();x.beginPath();x.ellipse(w/2,h/2,w/2,h/2,0,0,7);x.fillStyle=chip;x.fill();x.clip();
if(grid){const px=w/cols,py=h/rows,rm=Math.min(px,py)*.62;x.fillStyle=dot;x.beginPath();for(let j=0;j<rows;j++)for(let i=0;i<cols;i++){const r=rm*Math.sqrt(1-grid[j*cols+i]/255)*(gain||1);if(r<.18)continue;const cx=(i+.5)*px+((j&1)?px*.18:0),cy=(j+.5)*py;x.moveTo(cx+r,cy);x.arc(cx,cy,r,0,7)}x.fill()}
else{x.fillStyle=dot;x.globalAlpha=.5;x.beginPath();x.arc(w/2,h*.38,w*.2,0,7);x.ellipse(w/2,h,w*.4,h*.34,0,0,7);x.fill()}x.restore()}
function sq(c,grid,chip){const x=c.getContext('2d'),W=c.width,n=56,p=W/n,rm=p*.6;x.fillStyle=chip;x.fillRect(0,0,W,W);x.fillStyle='#121212';x.beginPath();for(let j=0;j<n;j++)for(let i=0;i<n;i++){const r=rm*Math.sqrt(1-grid[j*n+i]/255)*1.05;if(r<.25)continue;const cx=(i+.5)*p+((j&1)?p*.18:0),cy=(j+.5)*p;x.moveTo(cx+r,cy);x.arc(cx,cy,r,0,7)}x.fill()}
function raw(c,grid){const x=c.getContext('2d'),p=c.width/24;for(let j=0;j<30;j++)for(let i=0;i<24;i++){const v=grid[j*24+i];x.fillStyle=`rgb(${v},${v},${v})`;x.fillRect(i*p,j*p,p+.5,p+.5)}}</script>"""

def sw(hexv, name, note=""): return f'<div class=sw><i style="background:{hexv}"></i><div><b>{name}</b><span>{hexv}{(" · " + note) if note else ""}</span></div></div>'
gens = ["Gen Z", "Millennial", "Gen X", "Boomer", "Silent"]; yrs = ["1997+", "1981–96", "1965–80", "1946–64", "≤1945"]
design = HEAD + """<style>
.spec{display:grid;grid-template-columns:1fr 196px;gap:14px;align-items:baseline;padding:13px 0;border-top:1.5px solid #d9d6ce}.spec:first-of-type{border-top:0;padding-top:0}.spec p{margin:0}
.sw{display:grid;grid-template-columns:50px 1fr;gap:12px;align-items:center}.sw i{height:50px;border-radius:50%;border:1.5px solid var(--ink);width:42px}.sw b{font:800 16px/1.1 var(--display);display:block}.sw span{font:500 12px var(--mono);color:var(--mute)}
.sws{display:grid;gap:9px}.g2{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.st{display:grid;justify-items:center;gap:8px;text-align:center}.st b{font:800 15px/1 var(--display)}.st span{font:400 12.5px/1.3 var(--body);color:var(--mute)}
.chips{display:flex;flex-wrap:wrap;gap:6px;align-items:center}.lab{display:block;margin:0 0 7px}
.wbox{background:#fff;border-radius:16px;padding:16px;display:grid;gap:10px}.wbig{display:flex;align-items:baseline;gap:12px}.wbig b{font:900 52px/.85 var(--display);font-stretch:112%;letter-spacing:-.05em}.wbig span{font:500 14px/1.3 var(--body)}
.wbar{display:flex;height:16px;border-radius:99px;overflow:hidden;border:1.5px solid var(--ink);background:#e9e7e2}.wbar i{display:block}
.qcard{border:2px solid var(--ink);border-radius:14px;padding:13px 15px;display:grid;gap:9px;box-shadow:3px 3px 0 var(--ink);background:#fff}.qcard h3{font:800 19px/1.1 var(--display);letter-spacing:-.015em;margin:0}.qcard .opts{display:grid;grid-template-columns:1fr 1fr;gap:6px}.qcard .opts button{border-radius:10px;border-width:1.5px;text-align:left;padding:7px 10px}
.track{height:6px;background:var(--ink);border-radius:3px;position:relative;margin:14px 6px 12px}.knob{position:absolute;right:18%;top:-11px;width:28px;height:28px;border-radius:50%;border:1px solid #c9c5bd;background:radial-gradient(circle,#ebe8e2 0 36%,#d3cfc7 41%,#fff 47%,#0000 50%),linear-gradient(#fff,#dcd8d0);box-shadow:0 3px 6px #0000002e,0 1px 1px #00000033}
.ticks{display:flex;justify-content:space-between;font:500 12px var(--mono)}.badge{font:500 10px var(--mono);text-transform:uppercase;letter-spacing:.06em;background:var(--sun);border:1px solid var(--ink);border-radius:999px;padding:1px 6px}
.rules{display:grid;grid-template-columns:1.1fr 1fr 1fr;gap:26px}.rules ul{margin:0;padding:0;list-style:none;display:grid;gap:7px;font-size:14.5px}.rules li b{font-weight:600}
</style><div class=page>
<div class=top><h1>Design system <em>The Oldest Congress</em></h1><span class=mono>Web · Light only</span></div>
<div class=row style="grid-template-columns:1.32fr 1fr">
<section class=p><h2>Type</h2>
<div class=spec><p style="font:900 52px/.95 var(--display);font-stretch:108%;letter-spacing:-.045em;white-space:nowrap">117 members</p><span class=mono>Archivo 900<br>Headlines, big numbers</span></div>
<div class=spec><p style="font:italic 400 46px/1 var(--serif)">Up from 75 in 2017.</p><span class=mono>Instrument Serif Italic<br>The turn in a headline</span></div>
<div class=spec><p style="font:800 24px/1.1 var(--display);letter-spacing:-.015em">Did you know?</p><span class=mono>Archivo 800<br>Section and card titles</span></div>
<div class=spec><p style="font:400 17px/1.45 var(--body)">Seats run left to right by voting record. It is not the real seating plan.</p><span class=mono>IBM Plex Sans 400<br>Body and hints</span></div>
<div class=spec><p style="font:500 14px var(--mono);text-transform:uppercase;letter-spacing:.07em">Since 2023 · +11 aged 70+</p><span class=mono>IBM Plex Mono 500<br>Labels, captions, data</span></div>
</section>
<section class=p><h2>Color</h2><div class=g2><div><span class=lab>Generation</span><div class=sws>""" + "".join(sw(GC[i], gens[i]) for i in range(5)) + """</div></div><div><span class=lab>Surface and ink</span><div class=sws>""" + sw("#fdfcfa", "Paper") + sw("#f2f0ea", "Panel") + sw("#e9e7e2", "Soft") + sw("#6d6b66", "Mute") + sw("#121212", "Ink") + """</div></div></div>
<p style="margin:16px 0 0;font-size:14px">Generation colors avoid red and blue so they never read as party. Worst colorblind separation ΔE 8.5. Labels always sit beside the color.</p></section></div>
<section class=p><h2>Seat states</h2><div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px">
<div class=st><canvas id=s1 width=216 height=270 style="width:108px;height:135px"></canvas><b>Lit</b><span>Matches the current view</span></div>
<div class=st><canvas id=s3 width=216 height=270 style="width:108px;height:135px"></canvas><b>Dim</b><span>A known non-match</span></div>
<div class=st><div style="width:108px;height:135px;border-radius:50%;background:#efede8;border:2.5px dashed #121212"></div><b>Unknown</b><span>Missing data, never “no”</span></div>
<div class=st><div style="width:108px;height:135px;border-radius:50%;border:2.5px dashed #bdbab2"></div><b>Empty</b><span>Vacant on opening day</span></div>
</div></section>
<section class=p><h2>Components</h2><div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px">
<div style="display:grid;gap:18px;align-content:start"><div><span class=lab>Chips</span><div class=chips><button class=on>All</button><button>Democrat</button><button>Republican</button><button>Independent</button></div></div>
<div><span class=lab>Segmented control</span><div class=chips><button class=on>Every vote</button><button>All but 1</button><button>All but 2</button></div></div>
<div><span class=lab>Scrubber</span><div class=track><div class=knob></div></div><div class=ticks><span>115</span><span>116</span><span>117</span><span>118</span><span>119</span></div></div>
<div><span class=lab>Status badge</span><span class=badge>Filtering</span></div></div>
<div><span class=lab>Widget box</span><div class=wbox><div class=wbig><b>22</b><span>Your age on opening day</span></div><div class=wbar><i style="width:0"></i><i style="width:1%;background:#c9ad3b"></i><i style="width:99%;background:#9e63d6"></i></div><div style="font:500 12px var(--mono)">0 within 5 years · 533 older</div></div></div>
<div><span class=lab>Question card</span><div class=qcard><span class=mono style="font-size:11px">Vote 3 of 8</span><h3>Should immigrants here illegally be held in detention once they're charged with theft or a violent crime?</h3><div class=opts><button class=on>Yes</button><button>No</button></div></div></div>
</div>
<div class=rules style="margin-top:22px;padding-top:18px;border-top:1.5px solid #d9d6ce">
<ul><li><b>Shape.</b> Panels 24 px, cards 14 px, chips fully round.</li><li><b>Line.</b> 2 px ink borders. Hard 3 px offset shadow on cards.</li></ul>
<ul><li><b>Halftone.</b> Dots are always black, never inverted.</li><li><b>Party.</b> Filterable, never a seat color.</li></ul>
<ul><li><b>Text.</b> One title and one line per box.</li><li><b>Numbers.</b> One at a time, with a picker.</li></ul>
</div></section></div>""" + HT + f"""<script>const g=dec({json.dumps(IMG[pick[2]["bioguide"]])});document.fonts.ready.then(()=>{{}});seat(s1,g,'#45a86f','#121212',1.1);seat(s3,g,'#efede8','#d0cdc5',1.1)</script>"""

assets = HEAD + """<style>
.flow{display:grid;grid-template-columns:auto 34px auto 34px auto 1fr;gap:20px;align-items:center}.flow .a{font:900 28px var(--display)}figure{margin:0;display:grid;gap:8px;justify-items:center;text-align:center}figcaption{font:500 12px/1.35 var(--mono);color:var(--mute)}
.pgrid{display:grid;grid-template-columns:repeat(15,1fr);gap:8px 7px}
.egrid{display:grid;grid-template-columns:repeat(8,1fr);gap:10px}.egrid figure{gap:5px}
.tile{aspect-ratio:1;width:100%;display:grid;place-items:center;font:900 24px var(--display);font-stretch:108%;letter-spacing:-.04em;border:1.5px solid var(--ink)}
.tiles{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}
.collage{position:relative;width:340px;height:304px;margin-top:20px!important}.collage>*{position:absolute}.sun{width:52%;aspect-ratio:1;border-radius:50%;background:var(--sun);right:6%;top:2%}.sheet{left:4%;top:20%;width:66%;height:60%;background:#ddd9d1;background-image:repeating-linear-gradient(#0000 0 15px,#b8b4aa 15px 16px)}.slab{left:24%;bottom:2%;width:58%;height:15%;background:var(--pink);padding:6px 10px;font:500 10px/1.25 var(--mono);display:flex;align-items:center}.cut{filter:drop-shadow(0 2px 0 #0003)}.cap{font:500 10px/1.25 var(--mono);background:var(--paper);padding:2px 5px;border:1px solid var(--ink)}
.parts{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;align-items:end}.parts figure>div{height:104px;display:grid;place-items:center}
.ic{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.ic>div{background:#fff;border-radius:14px;padding:10px;display:grid;gap:8px;justify-items:center;align-content:center;height:112px}.ic span{font:500 12px var(--mono);color:var(--mute)}
.note{margin:12px 0 0;font-size:13.5px;color:var(--mute)}
</style><div class=page>
<div class=top><h1>Assets <em>The Oldest Congress</em></h1><span class=mono>Halftone · Cut paper · Icons</span></div>
<section class=p><h2>Portrait pipeline</h2><div class=flow>
<figure><canvas id=r1 width=240 height=300 style="width:120px;height:150px"></canvas><figcaption>24×30 brightness grid<br>from the official photo</figcaption></figure><span class=a>→</span>
<figure><canvas id=r2 width=240 height=300 style="width:120px;height:150px"></canvas><figcaption>Black halftone dots<br>on a generation chip</figcaption></figure><span class=a>→</span>
<figure><canvas id=r3 width=54 height=66 style="width:27px;height:33px"></canvas><figcaption>Seat at<br>chamber size</figcaption></figure>
<p style="margin:0 0 0 20px;font-size:15.5px;max-width:42ch">874 portraits, all public-domain official photos. The grid is stored as data and drawn on canvas, so the whole chamber ships inside one page. The 6 members without a photo get a silhouette.</p></div></section>
<section class=p><h2>Member portraits, youngest to oldest</h2><div class=pgrid id=pg></div></section>
<section class=p><h2>Event photos</h2><div class=egrid id=eg></div><p class=note>Free-license photos only, stored as 56×56 halftones.</p></section>
<div class=row style="grid-template-columns:400px 300px 1fr;flex:1">
<section class=p><h2>Cut-paper collage</h2><div class=collage style="margin:auto"><div class=sun></div><div class=sheet></div><canvas class=cut id=cy width=300 height=372 style="left:8%;top:12%;width:36%"></canvas><canvas class=cut id=co width=300 height=372 style="left:44%;top:22%;width:38%"></canvas><div class=cap style="left:6%;top:67%">""" + Y["name"] + """ · 28</div><div class=cap style="left:50%;top:6%">""" + O["name"] + """ · 91</div><div class=slab><span>Opening day · January 3, 2025 · 119th Congress</span></div></div></section>
<section class=p><h2>Year tiles</h2><div class=tiles style="grid-template-columns:repeat(2,1fr)">""" + "".join(f'<figure><div class=tile style="background:{GC[g]}">{y}</div><figcaption>{n}</figcaption></figure>' for n, y, g in TILES[:4]) + """</div><p class=note>Replace photos for copyrighted pop culture.</p></section>
<section class=p><h2>Pieces and icons</h2><div class=ic>
<div><i style="width:66px;height:66px;border-radius:50%;background:var(--sun)"></i><span>Sun</span></div>
<div><i style="width:90px;height:66px;background:#ddd9d1;background-image:repeating-linear-gradient(#0000 0 11px,#b8b4aa 11px 12px)"></i><span>Ruled paper</span></div>
<div><i style="width:96px;height:30px;background:var(--pink)"></i><span>Label slab</span></div>
<div><i style="font:500 12px var(--mono);background:var(--paper);padding:3px 6px;border:1px solid var(--ink)">Name · 28</i><span>Caption tag</span></div>
<div><svg width=120 height=64 viewBox="0 0 200 104"><g fill=none stroke-linecap=round stroke-dasharray="0 11"><path d="M14 92A86 86 0 0 1 186 92" stroke="#9e63d6" stroke-width=8 /><path d="M30 92A70 70 0 0 1 170 92" stroke="#e98dca" stroke-width=8 /><path d="M46 92A54 54 0 0 1 154 92" stroke="#45a86f" stroke-width=8 /></g></svg><span>Seat order</span></div>
<div><b style="font:900 24px/1 var(--display);font-stretch:112%;letter-spacing:-.04em;background:var(--sun);padding:5px 10px 6px;transform:rotate(-3deg)">Jan 3</b><span>Date stamp</span></div>
<div><i style="width:30px;height:36px;border-radius:50%;background:radial-gradient(circle,#121212 0 34%,#0000 38%) 0 0/7px 7px,#c9ad3b"></i><span>Key: lit</span></div>
<div><i style="width:30px;height:36px;border-radius:50%;background:#efede8;border:1.5px dashed #121212"></i><span>Key: unknown</span></div>
<div><canvas id=sil width=60 height=74 style="width:30px;height:37px"></canvas><span>Silhouette</span></div>
</div></section></div></div>""" + HT + f"""<script>const P={json.dumps(P)},E={json.dumps(E)},F=dec({json.dumps(IMG[Y["bioguide"]])}),O=dec({json.dumps(IMG[O["bioguide"]])});
raw(r1,F);seat(r2,F,'#c9ad3b','#121212',1.1);seat(r3,F,'#c9ad3b','#121212',1.1);seat(cy,F,'#c9ad3b','#121212',1.1);seat(co,O,'#ae6c18','#121212',1.1);seat(sil,null,'#e9e7e2','#121212');
P.forEach(p=>{{const c=document.createElement('canvas');c.width=144;c.height=180;c.style.width='100%';pg.append(c);seat(c,dec(p.g),p.c,'#121212',1.1)}});
E.forEach(e=>{{const f=document.createElement('figure'),c=document.createElement('canvas');c.width=c.height=336;c.style.width='100%';f.append(c);const n=document.createElement('figcaption');n.textContent=e.y;f.append(n);eg.append(f);sq(c,dec(e.g),e.c)}});</script>"""
os.makedirs("proposal/sheets", exist_ok=True)
open("proposal/sheets/design_system.html", "w").write(design); open("proposal/sheets/assets.html", "w").write(assets)
open("proposal/sheets/photo_credits.txt", "w").write(credits); print(credits)
