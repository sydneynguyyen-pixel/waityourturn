"""Adds photos Sydney supplied herself (not from Commons) to data/fact_img.json as 56x56 luminance grids.
Same processing as build_fact_images.py. Edit LOCAL below, then run from the project root: python3 pipeline/add_local_fact_image.py
build_fact_images.py rewrites fact_img.json from Commons only, so run this again after it."""
import base64, json, subprocess
N = 56
LOCAL = [dict(key="3-born-1954", src="data/raw/facts/GettyImages-brown_v_board.jpg", file="Brown v. Board of Education, 1954 (Getty Images)",
              crop=(680*1.19, 780*1.19, 820*1.19), artist="Getty Images", license="", page="",
              ),
         dict(key="0-born-1998", src="data/raw/facts/larry-page-and-sergey-brin.webp", file="Larry Page and Sergey Brin (via SEO PowerSuite / link-assistant.com)",
              crop=(0, 314, 833), artist="SEO PowerSuite (link-assistant.com)", license="", page="", by="SEO PowerSuite")
         ]  # crop = (top, left, side) in source pixels; this square holds the woman, the child and the newspaper

def bmp_gray(path):
    b = open(path, "rb").read()
    off, w, h, bpp = int.from_bytes(b[10:14], "little"), int.from_bytes(b[18:22], "little", signed=True), int.from_bytes(b[22:26], "little", signed=True), int.from_bytes(b[28:30], "little")
    step, row = bpp // 8, ((bpp * w + 31) // 32) * 4
    px = []
    for y in range(abs(h)):
        o = off + (abs(h) - 1 - y if h > 0 else y) * row
        px.append([int(.114 * b[o + x * step] + .587 * b[o + x * step + 1] + .299 * b[o + x * step + 2]) for x in range(w)])
    return px

out = json.load(open("data/fact_img.json"))
for p in LOCAL:
    top, left, side = [int(v) for v in p["crop"]]
    sq, bmp = p["src"] + ".sq.jpg", p["src"] + ".bmp"
    png = p["src"] + ".png"
    subprocess.run(["sips", "-s", "format", "png", p["src"], "--out", png], capture_output=True, check=True)  # sips cannot crop webp directly
    subprocess.run(["sips", "-c", str(side), str(side), "--cropOffset", str(top), str(left), png, "--out", sq], capture_output=True, check=True)
    subprocess.run(["sips", "-s", "format", "bmp", "--resampleWidth", str(N), sq, "--out", bmp], capture_output=True, check=True)
    g = bmp_gray(bmp); cell = [g[y][x] for y in range(N) for x in range(N)]
    lo, hi = sorted(cell)[len(cell) // 50], sorted(cell)[-len(cell) // 50]
    cell = [round(255 * (max(0, min(255, (c - lo) * 255 / max(1, hi - lo))) / 255) ** .7) for c in cell]
    out[p["key"]] = dict(g=base64.b64encode(bytes(cell)).decode(), file=p["file"], page=p["page"], license=p["license"], artist=p["artist"], src=p.get("by","Getty Images"))
    print("added", p["key"])
json.dump(out, open("data/fact_img.json", "w"), ensure_ascii=False)
