# Visual spec (implemented in `render.py`; keep it unchanged unless the user asks)

## Timeline (`timeline.py`)

| Segment | Duration | Content |
|---|---|---|
| opening | 5.4 s + intro clip (15 s) | logo reveal in the centre (sting); logo rises into the centred lockup; at 5.4 s the lockup slides to the left-aligned column with a smaller logo, Miss K enters large on the right, and the name tag sits beside her. The unit appears only as text ("S2 · UNIT N" pill, header title) |
| part 1 card | 2.4 s | "PART 1 · PHRASES", "N phrases to revise"; Miss K slides out to the right as it starts |
| item | 8.6 s | see below |
| pop-up | clip length + 0.3 s (4.3-5.3 s) | after every 5th item of a part (not after the last item of a part): Miss K slides in from the right, white speech bubble (headline in Bebas, second line in coral), "N of TOTAL done" with a segment progress bar, then slides out |
| transition | 0.8 + 6.0 + 1.0 s | Miss K slides in: "Great job with the phrases! Now let's try some words!"; Part 2 card "WORDS" |
| conclusion | 0.8 + 12.0 + 1.0 s | Miss K slides in; "WELL DONE!", "You've revised all {N} words / and phrases from Unit N." and chips "13 phrases", "17 words" |
| outro | 8.0 s | logo and "Thanks for revising with Miss K!" centred vertically; 3 s hold, 2 s eased fade to black, 1 s black |

Unit 1 data in this format: 30 items, 5 pop-ups, 333.9 s (5:34). Each extra item adds 8.6 s.

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

> Pure illustration only: absolutely NO text, NO letters, NO words, NO numbers, NO captions, NO speech-bubble text, NO logos with lettering, NO watermark anywhere in the image. Any screens, signs, books, labels or papers must be blank or show only simple pictures and icons. Composition: wide 16:9 scene, the key action clearly readable at a glance in the centre of the frame, main characters fully visible and not cropped. Scene: {a concrete scene showing the meaning AS USED IN THE SAMPLE SENTENCE: who, doing what, where, with which visible cue. ALWAYS name at least one cute original companion creature here, with its look and type, e.g. "her small round fluffy yellow-and-blue electric-type companion creature", and give it a part in the action}. Vibrant Japanese anime illustration, cel-shaded with clean thick outlines, bright saturated colours, soft dynamic lighting, rich detailed background, expressive faces. Every scene includes at least one cute ORIGINAL fantasy pocket-monster-style companion creature, clearly visible and part of the action, in the spirit of 1990s monster-collecting anime, but entirely original designs that do not resemble any existing franchise character.

**Every illustration must have the Pokémon-like look: anime characters together with at least one original
pocket-monster-style companion creature** (user requirement; the Unit 1 look). The style line alone is not enough. Unless
the Scene names a creature, the model draws plain anime people. Unit 1 creatures, for variety: a round fluffy
yellow-and-blue electric-type companion, a clever owl-like creature, a sleepy cat-like creature, an otter-like shopkeeper
creature, leaf-sprout creatures, a fox-like creature in a cape. Vary species, colours and elemental types across items,
and never reuse a real franchise design.
Store each prompt in `items.json` `image_prompt`. Run `python3 $S/check_prompts.py` before generating; it fails any
prompt without a creature, the no-text preamble or the style line, or with a franchise name. Save the images as `illus/NN_slug.png`. Abstract items need a visible cue
taken from the sentence:
- "irrelevant" ("Many people consider politics irrelevant to their lives"): a teenager enjoys their hobbies and shrugs, turning away from a TV political debate.
- "no matter" ("No matter what type of online shop you visit, they're tracking your every click"): floating shop windows of every kind, each with a tiny spy creature watching the cursor.

See `templates/examples/unit1_items.json` for all 30 Unit 1 prompts.

## Mockups before visual changes (W1)

Render stills and show them to the user before any full render:

```bash
export VOCAB_PROJECT=<project>; S=<skill>/scripts
python3 -c "import sys;sys.path.insert(0,'$S');from timeline import seg_by_key;d=seg_by_key();print({k:round(v['start'],2) for k,v in d.items()})"
python3 $S/render.py test 2.0 4.8 8.5 <item1+5.0> <conclusion+3> <outro+1.5>      # -> work/test/frame_XXXX.XX.png
```

Crop or annotate the stills with PIL if needed (for example a close-up of the meaning card). Copy them to `output/mockups/`, link
them in the message, and wait for approval.
