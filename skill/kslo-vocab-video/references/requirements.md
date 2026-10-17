# Requirements (the user's standing rules)

Every rule below was stated or approved by the user (K S Lo English teacher) while producing the S2 Unit 1 video
(versions V1-V5), plus the cost-saving format v2 agreed on 2026-10-17 (tag [F]). Treat them as fixed requirements for
every new unit. The tag in brackets is where it came from. Where format v2 changed an older rule, the older rule is marked.

## Audience, tone, branding

| # | Requirement |
|---|---|
| A1 | Audience: S2 students of HKMA K S Lo College, usually called **K S Lo**. Address them as **"K S Lo students"**. [brief] |
| A2 | Look professional but appealing to teenagers: navy/gold/coral palette, anime tutor, playful countdown. [brief] |
| A3 | Title format: **"S2 Unit N Useful Words and Phrases"**. [brief] |
| A4 | Open with the K S Lo English branding and a **subtle** logo; end with the branding and logo. [brief] |
| A5 | The logo is white on a transparent background. The knocked-out "KSLO" letters must show the real background. **Never put a glow, plate, fill or solid box behind the logo.** [V1 fix 1] |
| A6 | Opening: the logo appears in the centre, then rises to join the title as **one lockup** (logo, "S2 · UNIT N" pill, USEFUL WORDS / AND PHRASES, underline, subtitle). **The logo never shrinks or flies to the top-left corner.** A small header logo may fade in on the item screens. [V1 fix 2] |
| A7 | When Miss K appears in the opening, the lockup moves to a **left-aligned** column with a **smaller logo** and breathing space above the title. The **"Miss K / Your Virtual English Tutor" tag sits on the right, next to Miss K**. [V2 fix 1, V3 round 2] |
| A8 | Final screen: the logo and **"Thanks for revising with Miss K!"** only, with no extra line beneath. The whole group is **vertically centred**, then it **fades to black** (about 3 s hold, 2 s eased fade, 1 s black, music silent in the black). [V2 fix 8, V3 round 2, V5] |
| A9 | Video: 16:9, 1920x1080, about 5 min for about 30 items. [first reply] |

## Content and order

| # | Requirement |
|---|---|
| C1 | Use the unit's table from the DOCX. **All phrases come first, then all words** (Part 1 Phrases, Part 2 Words); keep table order inside each group. (Unit 1 V1-V5 had words first; changed in [F].) |
| C2 | Miss K greets the students as K S Lo students and offers to revise the vocabulary with them. Since [F] this is the **generic library intro** (no unit number in speech; the unit is shown only as text). [brief, F] |
| C3 | After all items, Miss K gives a quick conclusion with an encouraging remark (generic library outro since [F]). [brief, F] |
| C4 | Extras the user wanted: (a) after each reveal, a meaning card with the **headword, POS pill, Chinese meaning, definition** and the **sample sentence with the item highlighted**; (b) a progress counter **"ITEM 07 / 30"**; (c) a Part 2 link line after Part 1 (since [F]: **"Great job with the phrases! Now let's try some words!"**); (d) soft, upbeat background music, quieter than Miss K. [first reply, V2 note 9] |
| C5 | Display and blank rules for words and phrases: see `presentation_rules.md`. **Always ask the user when unsure how an item should be shown.** [brief] |

## Per-item sequence (8.6 s per item)

| # | Requirement |
|---|---|
| S1 | Show an illustration of the item's meaning **as used in the sample sentence**. Study the definition and sentence first. [brief] |
| S2 | Illustration style: vibrant anime characters **together with at least one cute original pocket-monster-like companion creature in every image** (the Pokémon-like look of Unit 1). The creature is named in the prompt's Scene and takes part in the action (`check_prompts.py`). **Never copy Pokémon or any franchise character.** No text in images. [brief; made mandatory 2026-10-18 after a unit came out with no creatures] |
| S3 | Below the image: **"What's the word?"** or **"What's the phrase?"**, then the first letter(s) with blanks. [brief] |
| S3b | Under the blanks, during the thinking time: the **sample sentence with the item blanked out**, first letter(s) given, **every blank the same length**; for phrases starting with "be", the form of "be" in the sentence is shown in full ("I was even g_____ w_____ …") (see P8 in `presentation_rules.md`). [2026-10-17] |
| S4 | A 3-second think time with a **film-leader countdown** (3-2-1) and sound effects (beeps and projector). Since [F], Miss K is **not animated on quiz screens**: a round **Miss K badge** (face crop of the neutral keyframe, gold ring, "Say it out loud!") sits under the countdown, and while she says the answer it shows gold ripple rings and voice bars. (V1-V5: a keyed Miss K clip at the bottom right.) [brief, F] |
| S5 | When time is up, Miss K **says the item** (the shortened display form, see P3), and the answer is revealed. [brief, first reply] |

## Voice and pronunciation (details in `voice_and_audio.md`)

| # | Requirement |
|---|---|
| V1 | Miss K's voice must sound **young and natural, slightly anime but not exaggerated**. The user chose studio voice **Leda**, en-GB, with **no pitch lift** ("A: natural"). [V1 fix 3] |
| V2 | **"K S Lo"**: "Lo" sounds like **"low"**, never "law". Write "K S Low" in TTS text. [V1 note] |
| V3 | Every word and phrase ends with a **falling (statement) tone, never a rising question-like tone**. Check every take. [V2 fix 5] |
| V4 | Pronunciation must be natural and fully voiced. 'haggle' came out creaky ("weird") and was re-recorded. [V2 fix 3] |
| V5 | **Every word in a phrase is clear**, including short function words. In 'a variety of', the "of" was too short and unclear. [V3 fix 2] |
| V6 | **All items sound equally loud** ('unique' sounded quieter). [V3 fix 1] |
| V7 | Long lines have **no stray sounds** (an extra "s" after "K S Lo students") and **no unclear passages** (05:02-05:04 was smeared). [V2 fixes 6-7] |
| V8 | Miss K says the full phrase, including a leading article ("a variety of"). [V1 note 8] |
| V9 | **British accent, same voice.** Miss K speaks with a British English accent **while keeping her voice: always studio voice Leda.** Never switch to another voice (including en-GB library voices) to get a stronger accent. That changes Miss K and no longer matches the library clips. Controls: `language_code` `en-GB` on every call, British spelling and wording in the TTS text, and a British-accent listen check on every take (see "British accent" in `voice_and_audio.md`). If the accent is still not British enough, tell the user and ask before changing anything. [2026-10-18] |

## Miss K's look and motion (details in `missk_clips.md`)

| # | Requirement |
|---|---|
| M1 | Miss K is an anime-style young female tutor: brown shoulder-length hair, gold star hair clip, navy blazer, white shirt, coral-red bow. Keep her consistent, always generated from `assets/missk_neutral.png`. [brief] |
| M2 | **No glitchy arm or hand movements.** Her arm must never rise and snap back (V1 at 00:30). Every clip starts and ends in the same neutral pose, and no clip is cut mid-gesture. **Check the entire video for this.** [V1 fix 4] |
| M3 | **No jumps in size or position** between clips (V1 at 01:39). Stabilise every clip to one reference pose. [V1 fix 5] |
| M4 | **Gestures must match the speech.** Example: the wave must happen **while** she says "See you next time", not before. Any gesture (wave, open palm, point, nod) happens on the words it illustrates; otherwise her hands stay clasped. [V3 fix 3] |

## Workflow preferences

| # | Requirement |
|---|---|
| W1 | **Visual changes: show mockup stills first and wait for approval before the full render.** Audio changes: implement directly, because the user checks audio in the video. [V2 feedback, 23:16] |
| W2 | Ask the user when something is unclear. Suggest improvements, but do not block on them. [brief] |
| W3 | Deliver a **YouTube title and description** with the video. **Never mention AI, Manus, or "generated".** [after V5] |
| W5 | **Before generating any item audio, show the user the full list of what Miss K will say** (`review_list.py`: display form, TTS text, blanks, clue sentence) with a blocking `ask`, and wait for approval. Apply corrections, regenerate the list and confirm again if anything changed. [2026-10-17] |
| W6 | **Levels other than S2 (or items not in the DOCX): ask the teacher for the list of items to feature and the title of the video before starting.** Do not guess either. Use the teacher's title exactly (`init_project.py --title`). [2026-10-17] |
| W4 | Video model: `seedance-2-5` (4-30 s, 720p) unless the user names another model. [brief] |

## Format v2: lower production cost (agreed 2026-10-17)

| # | Requirement |
|---|---|
| F1 | **No per-item Miss K clips.** Generating 30 lip-synced clips per unit was the main cost. Item answers are voice-only with the badge (S4). |
| F2 | **Reusable, generic Miss K clips** made once and reused for every unit: intro, transition, outro, idle, and six encouragement pop-ups. Their scripts never mention a unit, a number or specific words, so they fit any video. **The unit title appears only as on-screen text.** |
| F3 | **Encouragement pop-ups**: after every 5 items within a part, Miss K slides in from the right with a short line ("Great job! Keep going!") in a speech bubble with an "N of TOTAL done" progress bar, then slides out (about 4-5 s). No pop-up when the 5th item is the last item of a part (the transition or the outro follows). Lines `pop1`-`pop5` rotate; `pop6` ("Almost there!") is kept for the last pop-up of the video. |
| F4 | The library lives in the private GitHub repo **ksloenglish/kslo-vocab-video** (with the character design images, brand logo, vocabulary DOCX and the Unit 1 reference build), so another Manus account can build new units. Fetch it with `scripts/fetch_assets.sh`. |
| F5 | **Do not regenerate library clips for a normal unit.** Regenerate one only if the user asks or it fails QA, and then update the repo (new clip, `library.json`, `stab.json`). The gesture rule M4 applies to library clips too (intro wave on "Hello"; outro wave only on "See you next time"). |
| F6 | Unit 1 (V5) stays as delivered; the new format starts with Unit 2. |
