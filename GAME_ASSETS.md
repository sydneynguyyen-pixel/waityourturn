# Wait Your Turn: asset list and Gemini prompts

Everything the game needs, in the order to make it. Save each image into a new `game-assets/` folder using the file name given, as a PNG, as large as Gemini will export.

## How to use this

1. **Do Phase 1 first and stop.** It is five images. I'll build one finished scene from them so you can judge the look before making the other 40 or so.
2. **Paste the style block at the end of every prompt.** It is what keeps the set consistent.
3. **Use your first good image as a reference.** Once you like the Capitol, attach it to every later prompt and add: "Match the attached image's style, ink colors and line quality exactly."
4. **Attach your own references too.** The riso moodboard and cross-stitch posters you sent me are worth attaching to the first few prompts.
5. **One object per image, on plain white.** I cut them out and add the paper texture, ink overlap, misregistration and motion in the browser.

## The style block (paste after every prompt)

```
Style: two-color risograph print, hand-drawn illustration. Only two inks: black and warm mustard yellow (#c9ad3b), on off-white paper. Where the inks overlap they darken. Visible coarse halftone dots for shading, uneven patchy ink coverage, slight misregistration between the black and yellow layers, rough hand-cut edges. Flat shapes, no gradients, no 3D, no glossy digital look, no drop shadows. No red and no blue anywhere. No text or lettering. Isolated on a plain pure white background, centered, whole object visible with space around it.
```

Why mustard and black: red and blue would read as party colors, which the site avoids everywhere. If you want a third ink, add soft pink (#e98dca). It overlaps mustard into a warm orange.

Character parts use a different block (black ink only), given in Phase 3.

---

## Phase 1: style test (5 images)

| File | What it is |
|---|---|
| `capitol.png` | The Capitol, the main image of the game |
| `street.png` | Background row of buildings |
| `quorum-idle.png` | The pigeon guide |
| `quorum-talk.png` | The pigeon, beak open |
| `paper.png` | Paper texture under everything |

**capitol.png**
```
The United States Capitol building seen straight on from the front: the big central dome with its small statue on top, the columned portico and wide steps, and the two wings. Simple, bold and a little wonky, like a cut-paper poster. The dome is mustard with black halftone shading on the right side.
```

**street.png**
```
A long horizontal row of small Washington DC rowhouses seen straight on, side by side, all touching, like a strip of cut paper. Different heights and roof shapes, simple square windows, a few doors. Very wide image, 4:1. The row must run edge to edge so it can repeat as a seamless strip. Flat bottom edge.
```

**quorum-idle.png**
```
A plump city pigeon wearing a tiny black top hat, standing, seen from the side, facing left. Friendly and a bit smug. Round body, small head, short beak closed, thin legs. Grey areas made from black halftone dots, a mustard band on the neck.
```

**quorum-talk.png** (attach `quorum-idle.png`)
```
The exact same pigeon in the attached image, same size, same position, same pose. Change only one thing: the beak is open, mid-sentence.
```

**paper.png** (do not add the style block to this one)
```
A flat scan of off-white risograph paper, uncoated and slightly warm, with fine visible fibers and very subtle uneven tone. Nothing printed on it. No shadows, no folds, no edges visible. Evenly lit. Square, seamless so it can tile.
```

---

## Phase 2: the rest of the world (about 20 images)

Only after you like Phase 1.

### Scenery

| File | Prompt |
|---|---|
| `skyline.png` | `A very wide, low strip of distant Washington DC rooftops and trees as one flat silhouette, drawn in pale mustard with sparse black halftone dots. 5:1. Runs edge to edge so it can repeat. Flat bottom edge.` |
| `sidewalk.png` | `A very wide strip of city sidewalk and curb seen from the side, with a checkerboard band along the top edge. 6:1. Runs edge to edge so it can repeat seamlessly.` |
| `sunburst.png` | `A circular sunburst of alternating mustard and paper-white rays, like a vintage poster background. Rough printed edges. Square.` |
| `cloud.png` | `One small cartoon cloud made only of black halftone dots that fade out at the bottom.` |
| `chamber-room.png` | `The inside of the House of Representatives chamber seen from the back of the room: curved rows of wooden desks facing a tall marble rostrum with a flag behind it, a balcony above. Empty, no people. Simplified, like a stage set. The flag is drawn in black and mustard only. Wide image, 16:9. Fills the whole frame, no white border.` |

### Props (one per image)

| File | Prompt |
|---|---|
| `lamp.png` | `An old-fashioned street lamp post with a round glass globe.` |
| `tree.png` | `A small round street tree with a thin trunk. The leaves are one round mustard shape with black halftone dots on one side.` |
| `sign.png` | `A blank street signpost: a wooden pole with one empty rectangular board at the top, nothing written on it.` |
| `ballot-box.png` | `A wooden ballot box seen from the front with a slot in the top. Nothing written on it.` |
| `ballot.png` | `A single folded paper ballot, slightly tilted.` |
| `bench.png` | `A park bench seen from the front, wooden slats, iron legs.` |
| `rosette.png` | `A campaign rosette: a round pleated ribbon badge with two ribbon tails. Blank center.` |
| `megaphone.png` | `A hand-held megaphone seen from the side.` |

### Print pieces

| File | Prompt |
|---|---|
| `stamp-still-there.png` | `A rubber stamp impression in black ink that reads "STILL THERE" in bold capital letters inside a rough rectangular border. Uneven ink, patchy, slightly tilted. On pure white.` (drop the "no text" line from the style block) |
| `stamp-seat-open.png` | Same prompt, with the words "SEAT OPEN". |
| `stamp-still-waiting.png` | Same prompt, with the words "STILL WAITING". |
| `speech.png` | `A wide torn scrap of off-white paper with rough torn edges, blank, for writing on. 4:1.` |
| `card.png` | `A blank election poster: off-white paper, a wide mustard band across the top with black halftone dots fading in from the right, the rest empty. Rough printed edges. Portrait, 3:4.` |
| `aida.png` | `A flat scan of cream aida cross-stitch fabric showing its even woven grid of small holes. Nothing stitched on it. Evenly lit, no shadows, seamless. Square.` (no style block) |
| `stitch-x.png` | `Extreme close-up of one single cross stitch: two strands of thick black embroidery thread crossing in an X, seen from directly above, on pure white. Square.` (no style block) |
| `stitch-border.png` | `A decorative cross-stitch sampler border as a hollow rectangular frame, made of small black and mustard X stitches in a repeating scalloped pattern, like an old embroidered sampler. Empty in the middle. On pure white.` (no style block) |

With `stitch-x.png` and `aida.png` I can stitch any word in real thread, so the title, the year and the signs don't need to be generated as lettering.

---

## Phase 3: the character (about 20 images)

This is the hard part, and the one most likely to need a few tries. Every piece has to line up with the body, so make the body first and attach it to every later prompt.

The parts are black ink only. I add skin, hair and outfit color in the browser, which is what lets players pick any color.

**Character style block (use this one, not the main one)**
```
Style: hand-drawn risograph illustration in black ink only, on a pure white background. Bold slightly wobbly outlines, coarse black halftone dots for shading, uneven patchy ink. Flat shapes, no gradients, no color, no grey fills. No text.
```

**body.png**
```
A full-body cartoon person standing and facing the viewer, arms relaxed at the sides, feet slightly apart. Simple friendly proportions with a large round head. Completely bald, no hair. Plain blank face with no eyes, nose or mouth. Wearing only a plain fitted t-shirt and plain straight trousers with no details. Outlines only, white inside, with a little halftone shading on one side. Centered, whole figure visible, portrait 3:4.
```

**Every other part** (attach `body.png` each time)
```
The exact same figure as the attached image: same size, same position, same pose, same outlines. Change only one thing: [PART]. Do not move or redraw anything else.
```

| File | [PART] |
|---|---|
| `hair-short.png` | add short cropped hair |
| `hair-bob.png` | add a chin-length bob with a fringe |
| `hair-long.png` | add long straight hair past the shoulders |
| `hair-curls.png` | add big round curly hair |
| `hair-bun.png` | add hair tied in a bun on top of the head |
| `hair-buzz.png` | add a buzz cut drawn as fine halftone dots |
| `fit-blazer.png` | replace the clothes with a blazer, shirt and tie, and trousers |
| `fit-hoodie.png` | replace the clothes with a hoodie with a front pocket, and trousers |
| `fit-dress.png` | replace the clothes with a knee-length dress |
| `fit-overalls.png` | replace the clothes with overalls over a t-shirt |
| `face-smile.png` | add a face: two dot eyes and a wide smile |
| `face-game.png` | add a face: two dot eyes, straight mouth, determined eyebrows |
| `face-smirk.png` | add a face: two dot eyes and a lopsided smirk |
| `face-wow.png` | add a face: two dot eyes, raised eyebrows, small round open mouth |
| `extra-glasses.png` | add round glasses |
| `extra-cap.png` | add a baseball cap |
| `extra-headphones.png` | add over-ear headphones |

I pull each part out by comparing the image with `body.png`, so the less Gemini changes, the cleaner the result. If it keeps redrawing the whole figure, the fallback is 6 to 8 finished characters to choose from, each still recolorable.

There is no walking pose on purpose. The character moves like a paper puppet on a stick, with a hop and a tilt, which suits the print look and means one drawing per part is enough.

---

## What I add in the browser (no assets needed)

- Paper texture under every scene, and grain inside the flat colors.
- Inks set to overlap and darken, with each layer nudged slightly off the others.
- Stepped, slightly jittery motion at 8 to 12 frames a second.
- Halftone portraits of the real members (already on the site).
- All the real data: who stayed, who left, who took each seat.

## Check before you start

Ask whether your class allows AI-generated art in the final, and how it wants it credited. If it doesn't, the same list works as a shot list for drawing or scanning the pieces by hand.
