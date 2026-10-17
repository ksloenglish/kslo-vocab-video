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

## Meaning card (after the reveal)

- Header: the **headword first, then the POS pill**, for example "sustainable (adj)". POS labels have **no full stop**: v / n / adj / adv / phr / prep. [V2, V3]
- Then the large Chinese meaning (Traditional, `zh`), then the definition, then the sample sentence with the item **highlighted**.
- `highlight`: the exact substring(s) of the sentence to colour. `init_project.py` guesses it (inflections, be-forms, "sb" gaps) and lists `CHECK highlights` where the sentence changes the form. Fix those by hand. Examples: "gave up in frustration" for "give up in frustration"; "variety of" when the sentence says "an amazing variety of".
- If the full headword differs from the display (P2), the full form appears in small text under the answer.

## Illustrations (one per item, 16:9, 2560x1440, `illus/NN_slug.png`)

Read the definition **and the sample sentence**, and depict that meaning in that context. For example, "feature" in
"The market features local crafts" shows a market showcasing crafts, not a facial feature. Style: see the prompt
template in `visual_spec.md`. Generate in batches of 5 with `generate_image` (16:9) and review a contact sheet.
Regenerate any image that shows text or letters, a franchise lookalike, or the wrong meaning.

## Clue sentence on the thinking screen (P8, added 2026-10-17)

During the countdown, the question panel shows the sample sentence under the blanks, with the item blanked out and only
the first letter of each word given:
- "sustainable": *A large international meeting was held with the aim of promoting s\_\_\_\_\_ development in all countries.*
- "formulate strategies to": *Big data helps companies f\_\_\_\_\_ s\_\_\_\_\_ t\_\_\_\_\_ attract the most customers and drive sales.*

Rules:
- **Every clue blank has the same length** (one solid gold bar, `CLUE_BLANK` in `render.py`), whatever the word's
  length. The first letter is gold. This is different from the main blanks above it, which show one bar per letter.
- Blank the item **as it appears in the sentence** (the `highlight` spans): "gave up in frustration" →
  "g\_\_\_\_\_ u\_\_\_\_\_ i\_\_\_\_\_ f\_\_\_\_\_"; "was … greeted with" → "I w\_\_\_\_\_ even g\_\_\_\_\_ w\_\_\_\_\_"
  (highlight `["was", "greeted with"]`). A capital stays capital ("N\_\_\_\_\_ m\_\_\_\_\_ what type…").
- Whole words only: "features" → "f\_\_\_\_\_", never "f\_\_\_\_\_s". One-letter words stay as they are ("a").
- At the reveal, the clue fades out and the full sentence with the gold highlight fades in at the same place.
- An item with an empty `highlight` has no blank in its clue. `review_list.py` lists these under "To fix", and they must
  be fixed before approval.
