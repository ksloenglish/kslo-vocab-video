# Visual spec (implemented in `render.py`; keep it unchanged unless the user asks)

## Timeline (`timeline.py`)

| Segment | Duration | Content |
|---|---|---|
| opening | 5.4 s + intro clip (15 s) | logo reveal in the centre (sting); logo rises into the centred lockup; at 5.4 s the lockup slides to the left-aligned column with a smaller logo, Miss K enters large on the right, and the name tag sits beside her. The unit appears only as text ("S2 · UNIT N" pill, header title) |
| part 1 card | 2.4 s | "PART 1 · PHRASES", "N phrases to revise"; Miss K slides out to the right as it starts |
| item | 8.6 s | see below |
| pop-up | clip length + 0.3 s (4.3-5.3 s) | after every 5th item of a part **only when at least three items remain in that same part**: Miss K slides in from the right, white speech bubble (glyph-fitted Bebas headline, coral subtitle), "N of TOTAL done" with a segment progress bar, then slides out |
| transition | 0.8 + 6.0 + 1.0 s | Miss K slides in: "Great job with the phrases! Now let's try some words!"; Part 2 card "WORDS" |
| conclusion | 0.8 + 12.0 + 1.0 s | Miss K slides in; "WELL DONE!", "You've revised all {N} words / and phrases from Unit N." and chips "13 phrases", "17 words" |
| outro | 8.0 s | logo and "Thanks for revising with Miss K!" centred vertically; 3 s hold, 2 s eased fade to black, 1 s black |

Compute total duration from the selected pop-ups in `timeline.py`. Each extra item adds 8.6 s; section lengths also determine which encouragement clips are permitted. Unit 2's 16 phrases and 14 words permit pop-ups after global items 5, 10, 21 and 26, never 15.

## Item screen layout (1920x1080)

The header (y 28-92) holds the small logo (fades in), the title and the "ITEM 07 / 30" chip with a progress bar. The illustration card is
at x 70-1170, y 115-734. The question/answer panel is at x 70-1850, y 752-1052 (full width since format v2) ("What's the word?" and blanks, then the answer). The right panel
(x 1210-1870, y 115-415) shows the countdown first, then the meaning card. The **Miss K badge** (172 px disc, gold ring, centre
x 1540, y 548) sits under it with "Miss K" and "Say it out loud!"; from the reveal until her voice ends (`work/item_voice.json`)
the caption becomes gold voice bars and three gold ripple rings expand from the disc. No keyed Miss K on item screens.
During the countdown, the clue sentence (P8) sits at y = panel + 190, under the blanks (Poppins 30, width `SENT_W` 1700,
max 2 lines; it fades in 0.45-0.9 s and out at the reveal). The revealed sentence with its highlight then fades in at
the same place.

## Brand rules

- Palette: navy background with a subtle diagonal texture; gold `title_lines[1]` and accents; coral underline and POS pill; white text.
- Fonts (templates): Bebas Neue for titles and numbers, Poppins for UI text, Noto Sans CJK (HK face, index 4) for Chinese.
- Logo `assets/logo_white.png`: white on transparent and drawn as-is. **No glow, plate or shadow box behind it** (A5).

## Illustration prompt template (`generate_image`, aspect 16:9, 5 per call)

**Read `illustration_style.md` and Section 3 of `/pokemon-vocab-cards` before generation.** Follow the Unit 1 co-star template: **a clear human participant plus a different prominent adorable original creature with a meaning-bearing role**, no forced human size/dominance, no tiny decorative pet, no actual franchise characters, text/symbols or card UI. Keep the surrounding video design unchanged.

Store `image_prompt`, `creature_family`, `creature_signature`, `creature_role`, `human_creature_interaction`, `creature_scale_plan` and actual `style_reference_files` in `items.json`. Save artwork as `illus/NN_slug.png`, preferably 2560×1440. Keep both faces, the creature's distinctive silhouette and key action inside the safe area for the item's 6% zoom. Abstract meanings need contextual props, expressions and body language, not floating pictograms.

Approve three real-item co-star pilots before bulk generation, even with unchanged UI. Inspect every source image AND its 1100×619 card at beginning/maximum zoom; fill `work/illustration_review.json` with the policy-aware prominence/role/design/readability checks, then run `check_illustrations.py`. Inspect encoded item screens too. Unit 1 prompts are **legacy context only**, not permission to omit creatures or copy old optional-creature wording, symbols, bubbles or logo-like props.

## Mockups before visual changes (W1)

Render stills and show them to the user before any full render:

```bash
export VOCAB_PROJECT=<project>; S=<skill>/scripts
python3 -c "import sys;sys.path.insert(0,'$S');from timeline import seg_by_key;d=seg_by_key();print({k:round(v['start'],2) for k,v in d.items()})"
python3 $S/render.py test 2.0 4.8 8.5 <item1+5.0> <conclusion+3> <outro+1.5>      # -> work/test/frame_XXXX.XX.png
```

Crop or annotate the stills with PIL if needed (for example a close-up of the meaning card). Copy them to `output/mockups/`, link
them in the message, and wait for approval.

## Speech-bubble text safety (F7)

Use `popup_layout.py`, shared by the renderer and the blocking preflight. Keep the bubble 1000×300 at (150,330).
Measure and rasterize complete glyphs with bearing-aware guard pixels, then fit the headline to (64,48)-(936,166)
and subtitle to (64,190)-(936,268), in bubble-local coordinates. Centre the actual ink, not the font advance width.
For a headline without a subtitle, use (64,80)-(936,220). Reduce headline 128→72 px and subtitle 50→32 px as needed;
if no readable size fits, raise `PopupTextOverflow`. Never solve overflow by clipping, ellipsis or deleting words.

Run `python3 $S/check_popup_layout.py --stills` before render. It tests all six messages, punctuation, long-copy
failure cases and the easing overshoot; it saves metrics and entry/overshoot/hold/exit images for every used pop-up
in `work/popup_qa/`. Inspect every image, especially the full `YOU'RE DOING REALLY WELL.` headline. A single short
"Great job!" preview is insufficient. Show corrected hold mockups for approval when changing this layout (W1).
After encoding, inspect every pop-up again; an automated general video-analysis PASS cannot replace text-fit tests.
