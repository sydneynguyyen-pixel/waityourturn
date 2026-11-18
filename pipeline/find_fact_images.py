"""Finds a lead image for each row of data/generation_timeline.csv on Wikipedia and reads its license from Commons.
Writes data/fact_image_candidates.csv for review. Only free licenses (public domain, CC0, CC BY, CC BY-SA) are kept later.
Run from the project root: python3 pipeline/find_fact_images.py"""
import csv, json, re, subprocess, time, urllib.parse
UA = {"User-Agent": "OldestCongress/1.0 (SJSU student data viz)"}
# article to take the picture from, for rows whose source is not a Wikipedia article
TITLE = {"Federal Reserve History": "Wall Street Crash of 1929", "National Archives": None, "NASA": None,
         "IBM": "IBM Personal Computer", "Centers for Medicare & Medicaid Services": "Medicare (United States)",
         "Google": "Google", "9/11 Memorial & Museum": "September 11 attacks", "Apple Newsroom": "iPhone (1st generation)"}
BYTEXT = {"The U.S. enters World War II (to 1945)": "Attack on Pearl Harbor", "Brown v. Board of Education rules school segregation unconstitutional": "Brown v. Board of Education",
          "Sputnik, the first satellite, launches": "Sputnik 1", "Apollo 11 lands on the Moon": "Apollo 11",
          "The Beatles play The Ed Sullivan Show; the Civil Rights Act becomes law": "The Beatles on The Ed Sullivan Show"}
def get(url):
    # curl, since this Python build has no CA certificates
    for i in range(5):
        out = subprocess.run(["curl", "-s", "-A", UA["User-Agent"], url], capture_output=True, text=True).stdout
        if out.startswith("{"):
            return json.loads(out)
        time.sleep(2 + 3 * i)  # rate limited; back off
    raise RuntimeError("no JSON from " + url)
def api(host, **q):
    q.update(format="json", formatversion=2)
    return get(f"https://{host}/w/api.php?" + urllib.parse.urlencode(q))
rows = []
for r in csv.DictReader(open("data/generation_timeline.csv")):
    t = BYTEXT.get(r["text"])
    if not t and "wikipedia.org/wiki/" in r["url"]:
        t = urllib.parse.unquote(r["url"].split("/wiki/")[1]).replace("_", " ")
    rows.append(dict(gen=r["gen"], year=r["year"], text=r["text"], article=t or TITLE.get(r["source"]) or "", file="", license="", artist="", nonfree="", thumb=""))
# two batched requests (Wikipedia rate-limits one-by-one lookups): lead images for all articles, then licenses for all files
titles = sorted({r["article"] for r in rows if r["article"]})
q = api("en.wikipedia.org", action="query", titles="|".join(titles), prop="pageimages", piprop="name|thumbnail", pithumbsize=320, redirects=1, pilimit=50)["query"]
alias = {x["from"]: x["to"] for x in q.get("normalized", []) + q.get("redirects", [])}
img = {p["title"]: p for p in q["pages"] if p.get("pageimage")}
files = sorted({p["pageimage"] for p in img.values()})
time.sleep(2)
md = {}
for i in range(0, len(files), 50):
    for p in api("en.wikipedia.org", action="query", titles="|".join("File:" + f for f in files[i:i+50]), prop="imageinfo", iiprop="extmetadata")["query"]["pages"]:
        md[p["title"][5:].replace(" ", "_")] = (p.get("imageinfo") or [{}])[0].get("extmetadata", {})
for r in rows:
    t = r["article"]
    t = alias.get(alias.get(t, t), alias.get(t, t))
    p = img.get(t)
    if not p: continue
    m = md.get(p["pageimage"], {})
    v = lambda k: re.sub("<[^>]+>", "", m.get(k, {}).get("value", "")).strip()
    r.update(file=p["pageimage"], thumb=p["thumbnail"]["source"], license=v("LicenseShortName"), artist=v("Artist")[:120], nonfree=v("NonFree"))
for r in rows: print(r["year"], r["article"], "|", r["file"][:55], "|", r["license"], r["nonfree"])
with open("data/fact_image_candidates.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
