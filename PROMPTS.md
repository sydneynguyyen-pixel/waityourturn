# First prompts for Claude Code

## 1. Make the chamber the main visual
Read CLAUDE.md. In src/template.html, restructure the layout so the chamber is the hero: centered, full width of the content column, and the largest thing on the page. Move the headline and hero collage above it, smaller. Move the Your age / Who fits / Issues controls out of the right column into a panel below the chamber (or a drawer that slides over the page edge), so the chamber stays centered and visible while filtering. Keep the House/Senate/Both toggle and Congress scrubber directly attached to the chamber. Rebuild with python3 src/build.py, open it in a browser at 1280px and 400px wide, and fix overflow.

## 2. Skyline scrubber, 1789 to today
Add a skyline strip under the chamber: one bar per Congress, height = median age of seated voting members, from the 1st Congress (1789) to the 119th. Clicking or dragging selects that Congress and redraws the chamber. Needs roster + Voteview data for all Congresses (data/ has only 115-119 now; plan the data build first and show me the schema before running it). For Congresses before 2017, color seats by age band instead of generation, drop portraits and show plain chips, and disable the trait and issue filters with a short note.

## 3. Population comparison before 2020
Plan how to add the US median age by year (Census historical tables). Do not invent numbers; if a year is missing, leave the line blank.
