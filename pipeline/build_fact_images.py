"""Turns the photos picked in data/fact_images.csv (Wikimedia Commons, free licenses only) into 56x56 luminance grids
for the generation did-you-know cards, with credits read from Commons. Uses curl and macOS sips (no Pillow needed).
Downloads go to data/raw/facts/. Run from the project root: python3 pipeline/build_fact_images.py  ->  data/fact_img.json"""
import base64, csv, json, os, re, subprocess, time, urllib.parse
N = 56
UA = "OldestCongress/1.0 (SJSU student data viz)"
FREE = re.compile(r"^(Public domain|CC0|CC BY(-SA)? [0-9.]+( [a-z]+)?)$")
RAW = "data/raw/facts"
os.makedirs(RAW, exist_ok=True)

def curl(url, out=None):
    for i in range(6):
        r = subprocess.run(["curl", "-sL", "-A", UA, "-w", "%{http_code}", url] + (["-o", out] if out else []), capture_output=True, text=True)
        code = r.stdout[-3:]
        if code == "200":
            return r.stdout[:-3]
        time.sleep(15)  # Wikimedia rate limit
    raise RuntimeError(f"{code} {url}")

def bmp_gray(path):
    b = open(path, "rb").read()
    off, w, h, bpp = int.from_bytes(b[10:14], "little"), int.from_bytes(b[18:22], "little", signed=True), int.from_bytes(b[22:26], "little", signed=True), int.from_bytes(b[28:30], "little")
    step, row = bpp // 8, ((bpp * w + 31) // 32) * 4
    px = []
    for y in range(abs(h)):
        o = off + (abs(h) - 1 - y if h > 0 else y) * row
        px.append([int(.114 * b[o + x * step] + .587 * b[o + x * step + 1] + .299 * b[o + x * step + 2]) for x in range(w)])
    return px

picks = list(csv.DictReader(open("data/fact_images.csv")))
files = sorted({p["file"] for p in picks})
meta = {}
for i in range(0, len(files), 40):
    q = urllib.parse.urlencode(dict(action="query", titles="|".join("File:" + f for f in files[i:i + 40]), prop="imageinfo",
                                    iiprop="extmetadata|url", iiurlwidth=400, format="json", formatversion=2))
    for p in json.loads(curl("https://commons.wikimedia.org/w/api.php?" + q))["query"]["pages"]:
        ii = p["imageinfo"][0]; m = ii["extmetadata"]
        v = lambda k: re.sub(r"\s+", " ", re.sub("<[^>]+>", "", m.get(k, {}).get("value", ""))).strip()
        meta[p["title"][5:].replace(" ", "_")] = dict(thumb=ii["thumburl"], page=ii["descriptionurl"], license=v("LicenseShortName"), artist=v("Artist")[:90] or "Unknown")
out = {}
for p in picks:
    m = meta[p["file"]]
    if not FREE.match(m["license"]):
        print("SKIP non-free:", p["file"], m["license"]); continue
    src = os.path.join(RAW, re.sub(r"[^A-Za-z0-9._-]", "_", p["file"]))
    if not os.path.exists(src):
        curl(m["thumb"], src); time.sleep(1)
    bmp = src + ".bmp"
    w, h = [int(x) for x in re.findall(r"pixel(?:Width|Height): (\d+)", subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", src], capture_output=True, text=True).stdout)]
    side = ["--resampleWidth", str(N)] if w < h else ["--resampleHeight", str(N)]
    subprocess.run(["sips", "-s", "format", "bmp", *side, src, "--out", bmp], capture_output=True, check=True)
    g = bmp_gray(bmp)
    H, W = len(g), len(g[0])
    y0 = 0 if p["crop"] == "t" else (H - N) // 2
    x0 = (W - N) // 2
    cell = [g[y0 + y][x0 + x] for y in range(N) for x in range(N)]
    lo, hi = sorted(cell)[len(cell) // 50], sorted(cell)[-len(cell) // 50]  # stretch contrast, 2% clipped each end
    # stretch, then lift the midtones so dark photos don't turn into solid black dots
    cell = [round(255 * (max(0, min(255, (c - lo) * 255 / max(1, hi - lo))) / 255) ** .7) for c in cell]
    out[p["key"]] = dict(g=base64.b64encode(bytes(cell)).decode(), file=p["file"].replace("_", " "), page=m["page"], license=m["license"], artist=m["artist"])
    print(p["key"], m["license"], "|", m["artist"][:50])
json.dump(out, open("data/fact_img.json", "w"), ensure_ascii=False)
print(len(out), "images -> data/fact_img.json")
