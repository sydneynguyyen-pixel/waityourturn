# Handoff: The Oldest Congress

Context for picking this project up in a new Claude account. Read this, then CLAUDE.md.

## What this is
Sydney Nguyen's SJSU MDes data visualization final. An interactive web page where every seat in a semicircle chamber is a member of Congress, drawn as a black halftone portrait on a generation-colored chip. Filters light up matching seats and dim the rest.

## Status (as of Nov 17, 2026)
- **Site:** built and working (`chamber.html`). Four views: Chamber, How Congress works, About the data, Sources. `src/template.html` last changed Oct 27.
- **Updated proposal:** submitted Nov 3 (`proposal/Data Viz Final - Updated Proposal.pdf`). It still mentions the 3D skyline, which has since been dropped.
- **Data analysis:** done for the Nov 10 deadline (`proposal/Data Viz Final - Data Analysis.pdf`, 9 pages). A longer 16-page version is kept as `proposal/Data Viz Final - Data Analysis (16 pages).pdf`.
- **3D-printed skyline:** dropped on Nov 10. The final deliverable is the web page only.
- **Final submission and presentation dates:** not known yet. Ask Sydney.

## Next steps (from the data analysis, section 6)
1. Finish the data: Census median age for 2017 and 2019, missing Pew links, reconcile race (136 vs. 139 Pew) and Senate immigrant (18 vs. 19) counts, click through the Congress.gov quiz links by hand.
2. Add the new finding to the site: a "median age when they first took office" line on the history chart, with a note that it only counts members still in office.
3. Finish the site: keyboard access for seats, test on a real phone and in Safari, publish online.
4. Final check of numbers and sources, then submit.
5. Presentation: walk through the chamber, one tool and the findings.

## Key findings (verified, from analysis/analyze.py)
- Since 1981 (the low point, median 49.3): median age +9.6 years, median age at first taking office +7.8, median years served +0.8. Congress aged mainly because people arrive older.
- 2017 to 2025: median flat (59.4 to 58.9), but members 70+ grew 75 to 117 (22.0%, the highest share of any Congress). 100 of the 117 were already in office in 2017.
- 119th median 58.9 vs. U.S. median 39. Adults under 30 are 20.5% of U.S. adults but hold 1 seat.
- Generations 2017 to 2025: Boomers 334 to 229, Millennials 5 to 71, Gen Z 0 to 1.
- On the 8 quiz votes, party explains the split. Democrats who crossed over on the GENIUS Act, clean cars waiver and Laken Riley Act were 7 to 12 years younger than other Democrats.

## How things are built
- Site: edit `src/template.html`, then `python3 src/build.py`. Never edit `chamber.html` by hand.
- Analysis numbers: `python3 analysis/analyze.py` writes `analysis/results.json`.
- Data analysis PDF: `python3 analysis/build_sheets.py` (design system and assets sheets, as HTML in `proposal/sheets/`), screenshot those with headless Chrome at 1360px wide and 2x into `proposal/img/sheet-*.jpg`, then `python3 analysis/build_report.py` writes `proposal/data_analysis.html`. Print it with:
  `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-pdf-header-footer --virtual-time-budget=10000 --print-to-pdf="proposal/Data Viz Final - Data Analysis.pdf" "file://$PWD/proposal/data_analysis.html"`
- Charts in the PDF are inline SVG from `analysis/charts.py` (stdlib Python, no pandas or matplotlib on this Mac).
- `proposal/img/` holds the site screenshots and early sketches used in the PDFs.

## Sydney's preferences
- Site: less text, fewer levels of hierarchy, more white space. Each section is its own box with one title and one short line. Prefer interactive widgets over paragraphs.
- Never a row of identical big-number stat tiles, especially four in a row. Show one number at a time with a picker, or use a chart, list or sentence.
- Class documents (proposal, data analysis): plain, like a Google Doc. Archivo only, regular or semi-bold, all black text, no pills, no colored boxes, simple black-bordered tables, no subtitle under the title. Keep text short and plain. Tables should be simple to read.
- Halftone dots are always black. Generation colors avoid red and blue. Seats are never colored by party.
- Missing data means unknown, never "no."

## Memory files
Claude's saved memories from the old account are in `handoff/memory/`. In the new account, copy them into that account's project memory folder, or just keep this file and CLAUDE.md as the source of truth.
