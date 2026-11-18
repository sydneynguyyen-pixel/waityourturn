"""Logo and favicon: a gavel and its sound block, charted on a 24 x 24 dot grid in thread white.
Sydney picked the gavel on Nov 17 from four options (temple, gavel, hourglass, ballot box).
Run from the project root, then python3 src/build.py. Patches src/template.html in place
(the <svg id="logo"> and the <link rel="icon">) and rewrites logo-preview.html."""
import math, re, urllib.parse
N, TH = 24, "#f4f1e8"
A = math.radians(-35)  # tilt of the gavel
def rot(x, y, cx, cy, a):
    c, s = math.cos(a), math.sin(a); x -= cx; y -= cy
    return x * c + y * s, -x * s + y * c
def cell(x, y):
    """'g' gavel dot, 'b' small band dot on the gavel head, 'k' sound block dot, None empty."""
    u, v = rot(x, y, 10, 9, A)
    if abs(u) <= 6.5 and abs(v) <= 3.2: return "g" if abs(abs(u) - 4.2) > .6 else "b"
    if -0.9 <= u <= 0.9 and 3.2 < v <= 14: return "g"
    if 19 <= y <= 21.5 and 12 <= x <= 23: return "k"
    if 18 <= y < 19 and 13.5 <= x <= 21.5: return "k"
cells = [(x, y, cell(x + .5, y + .5)) for y in range(N) for x in range(N)]
cells = [c for c in cells if c[2]]
# the gavel swings around the end of its handle (u=0, v=14 back in grid coordinates)
c, s = math.cos(A), math.sin(A)
px, py = 10 + 0 * c - 14 * s, 9 + 0 * s + 14 * c
def dot(x, y, k):
    r = .24 if k == "b" else .4
    return f'<g style="--y:{N-1-y}"><circle cx="{x+.5}" cy="{y+.5}" r="{r}" style="--x:{x}"/></g>'
gav = "".join(dot(*c) for c in cells if c[2] != "k")
blk = "".join(dot(*c) for c in cells if c[2] == "k")
logo = (f'<svg id="logo" viewBox="0 0 {N} {N}" width="34" height="34" fill="{TH}" aria-hidden="true">'
        f'<g class="lgv" style="transform-origin:{px:.2f}px {py:.2f}px">{gav}</g><g class="lgb">{blk}</g></svg>')
k = 28 / N
pix = "".join(f'<rect x="{2+x*k:.2f}" y="{2+y*k:.2f}" width="{k*.92:.2f}" height="{k*.92:.2f}"/>'
              for x, y, t in cells)
fav = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#10151b"/>'
       f'<g fill="{TH}">{pix}</g></svg>')
uri = "data:image/svg+xml," + urllib.parse.quote(fav, safe="/:=' ")
p = "src/template.html"; s = open(p).read()
s, n1 = re.subn(r'<svg id="logo".*?</svg>', lambda m: logo, s, count=1, flags=re.S)
s, n2 = re.subn(r'<link rel="icon" type="image/svg\+xml" href="[^"]*">',
                lambda m: f'<link rel="icon" type="image/svg+xml" href="{uri}">', s)
assert n1 == 1 and n2 == 1, (n1, n2)
open(p, "w").write(s)
big = lambda w: fav.replace("<svg ", f'<svg width="{w}" height="{w}" ')
open("logo-preview.html", "w").write(f'''<!doctype html><meta charset="utf-8"><title>Logo preview</title>
<body style="margin:0;background:#1b222b;display:flex;gap:56px;align-items:center;justify-content:center;min-height:100vh;font:14px sans-serif;color:#ccc">
<figure>{logo.replace('width="34" height="34"', 'width="200" height="200"')}<figcaption>Logo</figcaption></figure>
<figure>{big(192)}<figcaption>Favicon (6x)</figcaption></figure>
<figure><div style="display:flex;gap:12px;align-items:end">{logo}{big(32)}{big(16)}</div><figcaption>Actual sizes</figcaption></figure></body>''')
print("logo:", len(cells), "dots; pivot", round(px, 2), round(py, 2))
