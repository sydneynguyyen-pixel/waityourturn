"""Draws the report's charts as inline SVG from data/ and analysis/results.json."""
import csv, json
R = json.load(open("analysis/results.json"))
hist = list(csv.DictReader(open("data/age_by_congress.csv")))
W = 672; F = 'font-family="Archivo,Arial,sans-serif" fill="#000"'
GC = {"Gen Z": "#c9ad3b", "Millennial": "#45a86f", "Gen X": "#e98dca", "Boomer": "#9e63d6", "Silent": "#ae6c18"}
GRAY = "#b9b6ae"; GRID = "#e4e2dc"
def T(x, y, s, size=11, anchor="start", w=400): return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{w}" text-anchor="{anchor}" {F}>{s}</text>'
def L(a, b, c, d, col=GRID, sw=1, dash=""): return f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{d:.1f}" stroke="{col}" stroke-width="{sw}"' + (f' stroke-dasharray="{dash}"' if dash else "") + "/>"
def svg(h, body, label): return f'<svg viewBox="0 0 {W} {h}" width="100%" role="img" aria-label="{label}">{"".join(body)}</svg>'

X0, X1 = 44, 590
def xs(y): return X0 + (y - 1789) / (2025 - 1789) * (X1 - X0)
def xaxis(b, y):
    for yr in range(1800, 2025, 50): b += [L(xs(yr), y, xs(yr), y + 4, "#000"), T(xs(yr), y + 17, yr, 11, "middle")]

def fig_entry():
    h, top, bot = 240, 34, 202; ys = lambda v: bot - (v - 30) / 35 * (bot - top); b = []
    for v in range(30, 66, 10): b += [L(X0, ys(v), X1, ys(v), "#000" if v == 30 else GRID), T(X0 - 8, ys(v) + 4, v, 11, "end")]
    t = R["tenure"]
    for k, dash in (("age", ""), ("entry", "6 4")):
        b.append(f'<polyline fill="none" stroke="#000" stroke-width="2" stroke-linejoin="round"' + (f' stroke-dasharray="{dash}"' if dash else "") + ' points="' + " ".join(f"{xs(r['year']):.1f},{ys(r[k]):.1f}" for r in t) + '"/>')
    b += [L(X0, 12, X0 + 26, 12, "#000", 2), T(X0 + 32, 16, "Median age on opening day"), L(X0 + 200, 12, X0 + 226, 12, "#000", 2, "6 4"), T(X0 + 232, 16, "Median age when those members first took office")]
    last = t[-1]; low = [r for r in t if r["c"] == 97][0]
    b += [T(X1 + 6, ys(last["age"]) + 4, f"{last['age']}", 11, w=600), T(X1 + 6, ys(last["entry"]) + 4, f"{last['entry']}", 11, w=600)]
    for k, dy in (("age", 18), ("entry", 18)):
        b += [f'<circle cx="{xs(low["year"]):.1f}" cy="{ys(low[k]):.1f}" r="3.5" fill="#000"/>', T(xs(low["year"]), ys(low[k]) + dy, f"{low[k]} in 1981", 11, "middle", 600)]
    xaxis(b, bot); return svg(h, b, "Median age and median age at first taking office by Congress, 1789 to 2025")

def fig_share():
    h, top, bot = 185, 16, 147; ys = lambda v: bot - v / 25 * (bot - top); b = []
    for v in range(0, 26, 5): b += [L(X0, ys(v), X1, ys(v), "#000" if v == 0 else GRID), T(X0 - 8, ys(v) + 4, f"{v}%", 11, "end")]
    for r in hist:
        y = int(r["opening_day"][:4]); p = 100 * int(r["age70plus"]) / int(r["known_age"]); recent = int(r["congress"]) >= 115
        b.append(f'<rect x="{xs(y) - 1.9:.1f}" y="{ys(p):.1f}" width="3.8" height="{max(bot - ys(p), 0):.1f}" fill="{"#000" if recent else GRAY}"/>')
    b.append(T(X1 + 6, ys(22) + 4, "22.0%", 11, w=600)); xaxis(b, bot)
    return svg(h, b, "Share of members aged 70 or older by Congress")

def fig_gen():
    order = ["Silent", "Boomer", "Gen X", "Millennial", "Gen Z"]; h = 212; x0, x1 = 92, W - 8; b = []; lx = x0
    for g in order:
        b += [f'<rect x="{lx}" y="4" width="12" height="12" fill="{GC[g]}"/>', T(lx + 17, 14, g)]; lx += 40 + len(g) * 6.6
    for i, c in enumerate(range(115, 120)):
        d = R["congress"][str(c)]; y = 32 + i * 35; x = x0; b.append(T(x0 - 10, y + 18, f"{c}th · {2 * c + 1787}", 11, "end"))
        for g in order:
            n = d["gen"][g]; w = n / d["n"] * (x1 - x0)
            if n:
                b.append(f'<rect x="{x:.1f}" y="{y}" width="{max(w - 2, 1):.1f}" height="27" fill="{GC[g]}"/>')
                if w > 24: b.append(T(x + w / 2 - 1, y + 18, n, 11, "middle", 600))
            x += w
    return svg(h, b, "Members by generation, 115th to 119th Congress")

def fig_hist():
    h, top, bot = 215, 44, 180; x0, x1 = 44, W - 12; xa = lambda a: x0 + (a - 25) / 70 * (x1 - x0); ys = lambda v: bot - v / 80 * (bot - top); b = []
    for v in range(0, 81, 20): b += [L(x0, ys(v), x1, ys(v), "#000" if v == 0 else GRID), T(x0 - 8, ys(v) + 4, v, 11, "end")]
    for a, n in sorted(((int(k), v) for k, v in R["hist119"].items())):
        b.append(f'<rect x="{xa(a) + 1:.1f}" y="{ys(n):.1f}" width="{xa(a + 5) - xa(a) - 2:.1f}" height="{bot - ys(n):.1f}" fill="{"#000" if a >= 70 else GRAY}"/>')
    for a in range(25, 96, 10): b += [L(xa(a), bot, xa(a), bot + 4, "#000"), T(xa(a), bot + 17, a, 11, "middle")]
    b += [L(xa(39), 30, xa(39), bot, "#000", 1.5, "5 4"), T(xa(39), 22, "U.S. median 39", 11, "middle", 600), L(xa(58.9), 30, xa(58.9), bot, "#000", 1.5), T(xa(58.9), 22, "Congress median 58.9", 11, "middle", 600), T(xa(85.5), ys(44), "117 members", 11, "middle", 600), T(xa(85.5), ys(44) + 14, "aged 70 or older", 11, "middle")]
    return svg(h, b, "Age distribution of the 119th Congress")

def fig_votes():
    rows = [("GENIUS Act (stablecoins)", 53.3, 120, 65.5, 136), ("California clean cars waiver", 52.5, 36, 60.1, 206), ("Laken Riley Act (detention)", 53.1, 58, 60.4, 189), ("HALT Fentanyl Act", 58.6, 134, 58.8, 118)]
    h = 196; x0, x1 = 190, W - 40; xa = lambda a: x0 + (a - 50) / 20 * (x1 - x0); bot = 166; b = []
    b += [f'<circle cx="{x0 + 6}" cy="11" r="5.5" fill="#000"/>', T(x0 + 17, 15, "Democrats who voted Yes"), f'<circle cx="{x0 + 186}" cy="11" r="5" fill="#fff" stroke="#000" stroke-width="2"/>', T(x0 + 197, 15, "Democrats who voted No")]
    for a in range(50, 71, 5): b += [L(xa(a), 30, xa(a), bot, GRID), T(xa(a), bot + 17, a, 11, "middle")]
    b.append(L(x0, bot, x1, bot, "#000"))
    for i, (t, yv, yn, nv, nn) in enumerate(rows):
        y = 50 + i * 33; b += [T(x0 - 12, y + 4, t, 11, "end"), L(xa(yv), y, xa(nv), y, "#000", 2), f'<circle cx="{xa(yv):.1f}" cy="{y}" r="5.5" fill="#000"/>', f'<circle cx="{xa(nv):.1f}" cy="{y}" r="5" fill="#fff" stroke="#000" stroke-width="2"/>']
        if nv - yv > 1: b += [T(xa(yv) - 10, y + 4, yv, 11, "end", 600), T(xa(nv) + 10, y + 4, nv, 11, "start", 600)]
        else: b.append(T(xa(nv) + 10, y + 4, f"{yv} / {nv}", 11, "start", 600))
    return svg(h, b, "Median age of Democrats by vote on four crossover votes")
