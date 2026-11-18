"""Writes proposal/data_analysis.html. Run from the project root."""
import csv, html, sys
sys.path.insert(0, "analysis")
import charts as c

CSS = """@page{size:letter;margin:0.75in}
*{box-sizing:border-box}
body{margin:0;background:#fff;color:#000;font:400 10.5pt/1.45 Archivo,Arial,sans-serif}
h1{font:600 24pt/1.15 Archivo;margin:0 0 4pt}
h2{font:600 15pt/1.2 Archivo;margin:20pt 0 6pt}
h3{font:600 11pt/1.25 Archivo;margin:12pt 0 4pt}
h2,h3{break-after:avoid}
p{margin:0 0 7pt}
.meta{margin:0 0 2pt}
figure{margin:0;break-inside:avoid}
figure img{width:100%;display:block;border:.5pt solid #bbb}
figure svg{display:block}
figcaption{font-size:9pt;line-height:1.4;margin-top:4pt}
.fig2{display:grid;grid-template-columns:1fr 1fr;gap:14pt;margin:8pt 0 12pt;align-items:start}
.fig{margin:8pt 0 10pt}
table{width:100%;border-collapse:collapse;font-size:9.5pt;line-height:1.35;margin:6pt 0 10pt;break-inside:avoid}
tr{break-inside:avoid}
th,td{border:.75pt solid #000;padding:5pt 6pt;text-align:left;vertical-align:top;overflow-wrap:anywhere}
th{font-weight:600}
b,strong{font-weight:600}
ul{margin:0 0 8pt;padding-left:18pt}li{margin:0 0 3pt}
.refs p{margin:0 0 3.5pt;padding-left:18pt;text-indent:-18pt;font-size:9pt;line-height:1.32;overflow-wrap:anywhere}"""

def table(head, rows, widths=None):
    w = widths or [None] * len(head)
    th = "".join(f'<th{f" style=width:{x}%" if x else ""}>{h}</th>' for h, x in zip(head, w))
    return "<table><tr>" + th + "</tr>" + "".join("<tr>" + "".join(f"<td>{v}</td>" for v in r) + "</tr>" for r in rows) + "</table>"

def fig(svg, cap): return f'<figure class="fig">{svg}<figcaption>{cap}</figcaption></figure>'

events = sorted(csv.DictReader(open("data/generation_timeline.csv")), key=lambda r: int(r["year"]))
events = list({r["url"]: r for r in reversed(events)}.values())[::-1]
timeline = "".join(f'<p>{html.escape(r["source"])}. {html.escape(r["text"])} ({r["year"]}). {html.escape(r["url"].replace("https://", "").replace("www.", ""))}</p>' for r in events)

body = f"""
<p class="meta">Data Visualization · Final project · Data analysis · November 10, 2026</p>
<h1>The Oldest Congress</h1>
<p class="meta">Sydney Nguyen · SJSU MDes</p>

<h2>1. Data sources</h2>
<p>This project shows who is in Congress and how that compares to the people it represents. It needs data on every member, including exact birthdays. Links are in section 7.</p>
{table(["Data", "Source", "Why"], [
 ["Members and birthdays", "@unitedstates (GitHub)", "Used to calculate every age"],
 ["Portraits", "@unitedstates (GitHub)", "Become the seats in the chamber"],
 ["Voting records", "Voteview", "Order the seats and power the quiz"],
 ["U.S. population by age", "Census Bureau", "Compare Congress to the country"],
 ["Religion, immigrant background, generations", "Pew Research Center", "Add traits to filter by"],
 ["Race and ethnicity", "Wikipedia lists", "No official list exists"],
 ["Bill summaries", "Congressional Research Service", "Explain each vote plainly"],
 ["Historic events and photos", "Various; Wikimedia Commons", "Show what each generation lived through"],
], [38, 28, 34])}

<h2>2. Data description</h2>
<p><b>Type:</b> mixed. Numbers (age, dates, voting scores), categories (party, chamber, religion) and images (portraits).</p>
{table(["Dataset", "Records", "Variables"], [
 ["Everyone who has served in Congress", "12,770 people", "Name, birthday, terms"],
 ["Every Congress since 1789", "119", "6"],
 ["Members of the last five Congresses", "2,777", "24"],
 ["119th Congress with traits and votes", "555", "39"],
 ["Portraits", "874", "720 brightness values each"],
], [54, 18, 28])}
<h3>Key variables</h3>
{table(["Variable", "What it means"], [
 ["Age", "Age on the first day of that Congress"],
 ["Generation", "Silent, Boomer, Gen X, Millennial or Gen Z, from birth year"],
 ["Party and chamber", "Democrat, Republican or Independent; House or Senate"],
 ["Voting score", "Liberal to conservative. Sets the seat order."],
 ["Race, religion, immigrant background", "From outside lists. Blank means unknown."],
], [40, 60])}

<h2>3. Data cleaning and preparation</h2>
<ul>
<li>Made one row per member per Congress.</li>
<li>Calculated each member's age on opening day.</li>
<li>Removed non-voting delegates and anyone not seated that day.</li>
<li>Matched voting records and trait lists to each member.</li>
</ul>
<h3>Raw vs. cleaned: one member</h3>
{table(["Raw", "Cleaned"], [
 ['"official_full": "Maria Cantwell"', "Maria Cantwell"],
 ['"birthday": "1958-10-13"', "Age 66.2"],
 ['"terms": [{{"type": "rep", "start": "1993-01-05", …}}, {{"type": "sen", …}}, …]', "119th Congress, Senate, Washington, Democrat"],
 ["Separate Voteview file", "Voting score −0.308"],
], [58, 42])}
<h3>Missing values (533 members of the 119th)</h3>
{table(["Field", "Known", "Unknown"], [
 ["Birthday", "533", "0"],
 ["Religion", "510", "23"],
 ["Race or ethnicity", "136", "397"],
 ["Immigrant background", "79", "454"],
], [54, 23, 23])}
<h3>Limitations</h3>
<ul>
<li>Unknown is never treated as no.</li>
<li>Race labels come from Wikipedia lists, not from the members themselves.</li>
<li>Early Congresses are missing up to 30.5% of birthdays, and U.S. median age covers only 2020–2025.</li>
</ul>

<h2>4. Preliminary data analysis</h2>
<h3>Chart 1. Members are arriving older</h3>
{fig(c.fig_entry(), "Median age of members, and the median age when they first took office.")}
<p>Since 1981, median age is up 9.6 years. Age at first taking office is up 7.8 years. Time served is up only 0.8 years. Congress got older mainly because people arrive older. This only counts members still in office.</p>

<h3>Chart 2. The share aged 70 or older is a record</h3>
{fig(c.fig_share(), "Share of members aged 70 or older, every Congress since 1789. The last five are in black.")}
<p>The median barely moved from 2017 to 2025, but members 70 or older grew from 75 to 117. Of those 117, 100 were already in office in 2017.</p>

<h3>Chart 3. Congress vs. the country</h3>
{fig(c.fig_hist(), "Members of the 119th Congress by age. Members 70 or older are in black.")}
<p>The median member is about 20 years older than the median American. Adults under 30 are 20.5% of U.S. adults but hold 1 seat, partly because of the age minimums.</p>

<h3>What this means for the design</h3>
{table(["Finding", "Design decision"], [
 ["Typical age stayed flat, but more members are 70 or older", "The headline counts members 70 or older"],
 ["Congress is much older than the public", "The Your age tool compares you to every seat"],
 ["Party explains most votes, not age", "The Issues quiz compares votes directly"],
], [50, 50])}
<h3>Open questions</h3>
<ul>
<li>Are people running for Congress later in life, or are younger candidates losing more often?</li>
<li>How much of the 70+ rise follows the aging of the U.S.?</li>
</ul>

<h2>5. Initial design direction</h2>
<p>Every seat is a real person. Filters light up the seats that match and dim the rest.</p>
{table(["Area", "Direction"], [
 ["Interaction", "Filter by generation and party, move through five Congresses, try three tools"],
 ["Format", "One interactive web page, with a phone layout"],
 ["Audience", "Young and first-time voters"],
 ["Takeaway", "Who represents you, and how old that group is"],
], [24, 76])}
<h3 style="break-before:page;margin-top:0">Early sketches</h3>
<div class="fig2" style="grid-template-columns:1fr 1.15fr;width:68%">
<figure><img src="img/old-oldch.jpg" alt="Chamber wireframe"><figcaption>Chamber wireframe.</figcaption></figure>
<figure><img src="img/old-wire.jpg" alt="Sidebar tool wireframes"><figcaption>Sidebar tools: Your age, Who fits and Issues.</figcaption></figure>
</div>
<div><h3>Design system</h3>
<figure class="fig"><img style="width:85%;margin:0 auto" src="img/sheet-design_system.jpg" alt="Design system sheet: type, color, seat states and components"><figcaption>Type, color, seat states and components, taken from the site's stylesheet.</figcaption></figure></div>
<div style="break-before:page"><h3 style="margin-top:0">Assets</h3>
<figure class="fig"><img src="img/sheet-assets.jpg" alt="Assets sheet: portrait pipeline, portraits, event photos, year tiles, collage and icons"><figcaption>Generated from the project's halftone data. Event photos, in order: {open("proposal/sheets/photo_credits.txt").read()}. All via Wikimedia Commons; halftone versions are adaptations.</figcaption></figure></div>
<div style="break-before:page"><h3 style="margin-top:0">Core screens</h3>
<figure class="fig"><img src="img/chamber.jpg" alt="Chamber view"><figcaption><b>Chamber.</b> Every seat is a member.</figcaption></figure>
<div class="fig2">
<figure><img src="img/genmodal.jpg" alt="Generation card"><figcaption><b>Did you know?</b> What each generation lived through.</figcaption></figure>
<figure><img src="img/age.jpg" alt="Your age tool"><figcaption><b>Your age.</b> You compared to every seat.</figcaption></figure>
</div></div>
<div style="break-before:page">
<div class="fig2">
<figure><img src="img/who.jpg" alt="Who fits tool"><figcaption><b>Who fits.</b> Stack traits and see who matches.</figcaption></figure>
<figure><img src="img/issues.jpg" alt="Issues quiz"><figcaption><b>Issues.</b> See who voted like you.</figcaption></figure>
</div>
<div class="fig2">
<figure><img src="img/how-run.jpg" alt="Could you run"><figcaption><b>Could you run?</b> Your birth year against the age rules.</figcaption></figure>
<figure><img src="img/how-ballot.jpg" alt="Who's on the ballot"><figcaption><b>Who's on the ballot?</b> Seats up in 2026, 2028 and 2030.</figcaption></figure>
</div>
<div class="fig2">
<figure><img src="img/about-history.jpg" alt="Every Congress since 1789"><figcaption><b>Every Congress since 1789.</b> The full history.</figcaption></figure>
<figure><img src="img/about-young.jpg" alt="When they were young"><figcaption><b>When they were young.</b> Who was born before key events.</figcaption></figure>
</div></div>

<h2>6. Next steps and timeline</h2>
{table(["Milestone", "Work left"], [
 ["1. Finish the data", "Fill the last gaps and check every link"],
 ["2. Add the new finding", "Add age at first taking office to the history chart"],
 ["3. Finish the site", "Add keyboard access, test on phones, publish"],
 ["4. Final submission", "Check numbers and sources, then submit"],
 ["5. Presentation", "Walk through the chamber, one tool and the findings"],
], [34, 66])}

<section class="refs">
<h2>7. References</h2>
<p>The @unitedstates project. <i>congress-legislators</i>. GitHub. github.com/unitedstates/congress-legislators</p>
<p>The @unitedstates project. <i>images</i>: official congressional portraits, public domain. GitHub. github.com/unitedstates/images</p>
<p>Lewis, Jeffrey B., Keith Poole, Howard Rosenthal, Adam Boche, Aaron Rudkin, and Luke Sonnet. <i>Voteview: Congressional Roll-Call Votes Database.</i> voteview.com/data</p>
<p>Congressional Research Service bill summaries, via GovInfo BILLSUM. govinfo.gov/bulkdata/BILLSUM</p>
<p>U.S. Census Bureau. Population Estimates Program, Vintage 2025. census.gov/programs-surveys/popest.html</p>
<p>Pew Research Center. Faith on the Hill (2021, 2023, 2025). pewresearch.org/religion/2025/01/02/faith-on-the-hill-2025/; pewresearch.org/religion/2023/01/03/faith-on-the-hill-2023/; pewresearch.org/religion/2021/01/04/faith-on-the-hill-2021/</p>
<p>Pew Research Center. Immigrants and children of immigrants in Congress (2023, 2025). pewresearch.org/short-reads/2025/02/27/immigrants-and-children-of-immigrants-make-up-at-least-15-of-119th-congress/; pewresearch.org/short-reads/2023/02/28/immigrants-and-children-of-immigrants-make-up-at-least-15-of-the-118th-congress/</p>
<p>Pew Research Center. Defining generations. 2019. pewresearch.org/short-reads/2019/01/17/where-millennials-end-and-generation-z-begins/</p>
<p>Wikipedia. Lists of members of Congress by race and ethnicity, at en.wikipedia.org/wiki/: List_of_African-American_United_States_representatives; List_of_African-American_United_States_senators; List_of_Hispanic_and_Latino_Americans_in_the_United_States_Congress; List_of_Asian_Americans_and_Pacific_Islands_Americans_in_the_United_States_Congress; List_of_Native_Americans_in_the_United_States_Congress</p>
<p>U.S. Constitution, Article I; 17th, 22nd and 26th Amendments. law.cornell.edu/constitution; archives.gov/founding-docs/constitution-transcript</p>
<p><i>U.S. Term Limits, Inc. v. Thornton</i>, 514 U.S. 779 (1995). law.cornell.edu/supremecourt/text/514/779. 2 U.S.C. § 7. law.cornell.edu/uscode/text/2/7</p>
<p>U.S. Senate. Filibusters and cloture. senate.gov/about/powers-procedures/filibusters-cloture.htm</p>
<p>Quiz votes (Voteview roll calls, 119th Congress): S. 331 (HALT Fentanyl); S.J.Res. 18 (CFPB overdraft); S. 5 (Laken Riley); H.J.Res. 72 / S.J.Res. 77 (Canada tariffs); H.Con.Res. 86 (Iran war powers); H.J.Res. 88 (California clean cars); H.J.Res. 131 (Coastal Plain leasing); S. 1582 (GENIUS). Roll numbers are on the site's Sources page.</p>
<p>Generation timeline and photos: 38 historic events, each with its own source link, and 28 Wikimedia Commons photos with full credits are on the site's Sources page.</p>
</section>
"""
open("proposal/data_analysis.html", "w").write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>The Oldest Congress - Data Analysis</title><link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600&display=swap" rel="stylesheet"><style>{CSS}</style></head><body>{body}</body></html>')
