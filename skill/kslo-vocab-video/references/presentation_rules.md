# Presenting words and phrases

`init_project.py` applies rules P1-P6 automatically and prints an **ASK list** for the P7 cases. Never guess an ASK case: put the
question and a recommended option to the user (an `ask` message with options), then edit `items.json`.

## Rules (confirmed by the user)

| Rule | What to do | Unit 1 examples |
|---|---|---|
| P1 Order | **All phrases first, then all words** (format v2); keep the DOCX table order inside each group. A phrase = a display form with more than one word ("a variety of" counts). `init_project.py` prints the order as P/W letters. |
| P2 Trailing placeholders | Strip trailing **sth / sb / sb/sth / sth/sb** from the display. **"do sth"** at the end is stripped too, keeping "to". | "be combined with sth" → **be combined with**; "formulate strategies to do sth" → **formulate strategies to** |
| P3 What Miss K says | The **shortened display form**. The full headword (with sth) appears only in small text on the meaning card. | she says "be combined with" |
| P4 Single-letter words | Shown as the letter itself, with no blank. | "a variety of" → **a v _ _ _ _ _ _   o _** |
| P5 Blanks | First letter, then **one bar per missing letter**, letters spaced. Phrases get a **natural word gap** (0.42 × font size, not wider). The row auto-shrinks to fit. | stunning → s _ _ _ _ _ _ _ |
| P6 Question | One token: **"What's the word?"** More than one: **"What's the phrase?"** | |
| P7 ASK cases | Placeholders inside a phrase (sb / sth / A / B / v-ing / one's): "assist sb in v-ing", "mistake A for B", "it gladdens sb to see"; hyphens ("tip-top"); brackets or slashes; apostrophes; interleaved order; unknown POS; a POS that conflicts with the token count. | Unit 2/6 had all of these |

For P7, give the user concrete options in the ask. For example, for "assist sb in v-ing": (a) show "assist   in" and say
"assist in"; (b) show "assist sb in doing sth" with blanks only on assist/in; (c) leave the item out. Record the
answer in `items.json` `display` (and in `project.json` notes if it is a general rule).

**Display-only ellipses (Unit 2 update, 2026-10-18):** Keep `display` as the spoken lexical form, and use optional
`answer_display` for a different visual form. Set `display: "assist in"`, `answer_display: "assist ... in"`, and
`display: "mistake for"`, `answer_display: "mistake ... for"`. Show the literal `...` in the main first-letter blanks
and revealed answer; do not replace its dots with letter bars. Do not speak the ellipsis or change these approved
recordings. Keep the original full headword on the meaning card and keep sample-sentence clues unchanged.

**Approved Unit 3 cases (19 October 2026):** Set `display: "lighten mood"` and
`answer_display: "lighten ... mood"`; keep literal dots throughout the countdown/reveal, the full
`lighten sb's mood` headword on the card, and `lighten our mood` in the source sentence. For
`self-disciplined`, retain one lexical word/word question, the literal hyphen and an initial for both
components: `s _ _ _ - d _ _ _ _ _ _ _ _ _ _`. Main bars count missing letters; the sentence clue
uses the same fixed-length blank after each initial (`s_____-d_____`). Use the tested hyphen-aware
renderer. These approvals are recorded examples, not permission to guess a new P7 placeholder case.

Preserve approved source wording, including `break sweat`, rather than silently adding an article;
source US spellings are not automatically rewritten during an image/audio revision. Keep intervening
sentence words outside discontinuous highlights: `get` / `addicted to` leaves `too` visible, and
`developed` / `a` / `routine` leaves `fitness` visible. Check exact inflections before speaking-list approval.

## Meaning card (after the reveal)

- Header: the **headword first, then the POS pill**, for example "sustainable (adj)". POS labels have **no full stop**: v / n / adj / adv / phr / prep. [V2, V3]
- Then the large Chinese meaning (Traditional, `zh`), then the definition, then the sample sentence with the item **highlighted**.
- `highlight`: the exact substring(s) of the sentence to colour. `init_project.py` guesses it (inflections, be-forms, "sb" gaps) and lists `CHECK highlights` where the sentence changes the form. Fix those by hand. Examples: "gave up in frustration" for "give up in frustration"; "variety of" when the sentence says "an amazing variety of".
- If the full headword differs from the display (P2), the full form appears in small text under the answer.

## Illustrations (one per item, 16:9, 2560x1440, `illus/NN_slug.png`)

Read the definition **and the sample sentence**, and depict that meaning in that context. For example, "feature" in
"The market features local crafts" shows a market showcasing crafts, not a facial feature. Read Section 3 of
`/pokemon-vocab-cards` when available (otherwise bundled `original_creature_design.md`) and apply
**`illustration_style.md`**: retain a central human and a prominent, meaning-bearing original co-star,
not a tiny subordinate pet; use a different identity in each image. Do not copy card aspect ratio/UI or
make creatures optional. Generate batches of up to 5 (16:9). Inspect each actual image and compare the set for
genuine species/silhouette variety; correct missing/oversized companions, disliked reptilian forms, repeated
mascots, text/symbols, franchise lookalikes or wrong context. Save fresh hash-bound visual checks to
`work/illustration_review.json` and run `check_illustrations.py` before finalization.

## Clue sentence on the thinking screen (P8, added 2026-10-17)

During the countdown, the question panel shows the sample sentence under the blanks, with the item blanked out and only
the first letter of each word given:
- "sustainable": *A large international meeting was held with the aim of promoting s\_\_\_\_\_ development in all countries.*
- "formulate strategies to": *Big data helps companies f\_\_\_\_\_ s\_\_\_\_\_ t\_\_\_\_\_ attract the most customers and drive sales.*

Rules:
- **Every clue blank has the same length** (one solid gold bar, `CLUE_BLANK` in `render.py`), whatever the word's
  length. The first letter is gold. This is different from the main blanks above it, which show one bar per letter.
- Blank the item **as it appears in the sentence** (the `highlight` spans): "gave up in frustration" →
  "g\_\_\_\_\_ u\_\_\_\_\_ i\_\_\_\_\_ f\_\_\_\_\_"; "be greeted with" → "I was even g\_\_\_\_\_ w\_\_\_\_\_". A capital stays capital ("N\_\_\_\_\_ m\_\_\_\_\_ what type…").
- **Phrases starting with "be": show the form of "be" in full, never blank it** (user, 2026-10-17). The form can be
  be, is, am, are, was, were, been or being. Examples: "I was even g\_\_\_\_\_ w\_\_\_\_\_ a coupon code…", "This data might be
  c\_\_\_\_\_ w\_\_\_\_\_ information…", "many items are m\_\_\_\_\_ f\_\_\_\_\_ recycled materials". Keep the be-form inside the `highlight`
  (`["was", "greeted with"]`, `["be combined with"]`), so the revealed sentence still highlights it; `clue_sentence()`
  leaves it unblanked automatically. The letter blanks above the sentence stay "b_ g_ w_" (P3).
- Whole words only: "features" → "f\_\_\_\_\_", never "f\_\_\_\_\_s". One-letter words stay as they are ("a").
- At the reveal, the clue fades out and the full sentence with the gold highlight fades in at the same place.
- An item with an empty `highlight` has no blank in its clue. `review_list.py` lists these under "To fix", and they must
  be fixed before approval.
