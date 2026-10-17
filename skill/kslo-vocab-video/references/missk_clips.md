# Miss K clips: the reusable library (format v2)

Since format v2 (2026-10-17), **a normal unit generates no Miss K clips**. Every video reuses one library of generic
clips, stored in the private GitHub repo `ksloenglish/kslo-vocab-video` under `library/`. `scripts/fetch_assets.sh`
clones it to `~/kslo-vocab-video`, and `init_project.py` copies the clips, the lip-matched voice, `library.json` and
`stab.json` into the project.

## Library contents

| Name | Length | Line (Leda, en-GB) | Used where |
|---|---|---|---|
| `intro` | 15.0 s | "Hello, K S Lo students! I'm Miss K, your virtual English tutor. Let's revise some useful words and phrases together. Look at each picture, think of the answer, and say it out loud before time runs out. Ready? Let's go!" | opening, large on the right; wave on "Hello", open palm on "let's revise" |
| `transition` | 6.0 s | "Great job with the phrases! Now let's try some words!" | between Part 1 (phrases) and Part 2 (words) |
| `outro` | 12.0 s | "Fantastic work, K S Lo students! Keep revising these words and phrases, and try using them in your writing and speaking. See you next time!" | conclusion; **wave only on "See you next time"** (about 9.7-10.7 s) |
| `pop1`-`pop6` | 4-5 s | "Great job! Keep going!" · "You're doing really well. Let's keep going!" · "Nice work! Here come some more." · "Brilliant! You're on a roll!" · "Keep it up! You've got this!" · "Almost there! Just a few more to go!" | encouragement pop-ups after every 5 items; `pop6` is preferred for the last pop-up of the video |
| `idle` | 10 s | none | fills every gap (sine ping-pong, so both ends are neutral) |

`library/clips/missk_<name>.mp4` has been **retimed** so the lips follow `library/aligned/<name>.wav` exactly, and that
WAV (0.5 s lead, then the clean voice) is placed at the clip's start. No alignment step runs per project.
`library/source_clips/` keeps the raw Seedance outputs, and `library.json` records each line, its length and its source.

Known limits of the 2026-10-17 library (credits ran out during generation):
- `pop6` reuses the `pop2` video, retimed to the pop6 voice, because Seedance refused the pop6 audio as a false
  copyright match. Regenerate it when credits allow (try rewording to "Nearly there! Only a few more to go!").
- In `intro`, Seedance rushed "I'm Miss K, your virtual English tutor" and "Look at each picture... runs out", so
  those lips play at about 0.7x speed. Regenerate it if the user notices.

## Regenerating a library clip (only when asked, or when one fails QA)

1. Record the line with the fixed voice (`voice_and_audio.md`) to `audio/vo/<name>.wav`, then run
   `python3 $S/make_refs.py lines <name>` to get `audio/refs/<name>.wav` (0.5 s lead, padded to whole seconds).
2. Call `generate_video` with `model: seedance-2-5`, `aspect_ratio: landscape`, `resolution: 720p`,
   `generate_audio: true`, `keyframes: {first: assets/missk_neutral.png, last: assets/missk_neutral.png}`,
   `audio_references: [audio/refs/<name>.wav]`, `duration_seconds` = the ref length. Make **two variants in parallel**
   and keep the better one. Using the same first and last keyframe makes every splice neutral to neutral (M2).
3. Retime it to the voice: `python3 $S/retime_clip.py raw.mp4 audio/refs/<name>.wav clips/missk_<name>.mp4`
   (add `--gap 0.12` for short lines). Speech parts flagged `<- strong` (outside 0.75-1.33x) look rushed or slow, so
   regenerate those if possible.
4. Run the QA below, delete `<name>` from `clips/keyed/stab.json`, and run `python3 $S/prep_clips.py <name>`.
5. Update the repo: the clip, `aligned/<name>.wav` (a copy of the ref), `source_clips/`, the `library.json` entry
   (`dur`, `line`, `source`) and `stab.json`. Commit and push, so every Manus account gets the new clip.

## Prompt templates

Use one shared character line in every prompt:
> Anime-style young female English tutor "Miss K" exactly as in the keyframe: brown shoulder-length hair with a gold star hair clip, navy school blazer, white shirt, coral-red bow. Same framing as the keyframe (thigh-up, centred). Flat pure chroma-green #00FF00 background, even lighting, no shadows on the background. Static locked-off camera: no zoom, no pan, no cuts.

**Intro:**
> [character line] She speaks the lines in the audio reference with accurate lip-sync, cheerful and warm. Gestures only on their words: a small wave of her right hand only while saying "Hello, K S Lo students"; one brief open-palm gesture only on "let's revise some useful words and phrases together". At all other times her hands are gently clasped in front of her waist. She starts and ends in exactly the keyframe pose.

**Outro.** This exact structure fixed the V3 early wave:
> [character line] She speaks the closing lines in the audio reference with accurate lip-sync, proud and encouraging. Her hands stay gently clasped in front of her waist for the whole clip, **except** during the final words "See you next time!": only then does she raise her right hand and wave, and she lowers it back to the clasped pose right after the line. She does not wave or raise her hands at any earlier moment. She ends in exactly the keyframe pose.

**Transition and pop-ups:**
> [character line] She says the line in the audio reference with accurate lip-sync, bright and encouraging, with a small friendly nod. Her hands stay gently clasped in front of her waist for the whole clip, with no hand or arm movement. No other speech or sounds. She ends in exactly the keyframe pose.

## Gesture-speech sync (M4)

A gesture belongs to its words. Everywhere else, the hands stay clasped. Check every large clip:
1. Transcribe the clip audio (`manus-speech-to-text`) to get the time of each phrase.
2. `python3 $S/contact_sheet.py clips/missk_outro.mp4 <t-1.5> <t+1.5> 0.25 sheet.jpg`, where t = the start of
   "See you next time". The hand must rise **after** the phrase starts and come down by its end. If it doesn't,
   regenerate the clip.

## QA for a new library clip

| Check | How | Failure it caught |
|---|---|---|
| Green background | `python3 -c "import sys;sys.path.insert(0,'$S');from keying import bg_check;print(bg_check('clips/missk_x.mp4'))"` prints OK (G > 200, R and B < 80) | one Unit 1 clip came out on black |
| Framing | `STAB_ONLY=1 python3 $S/prep_clips.py <name>`: scale within about 4 % of the others (library: 1.02-1.03), common zoom no more than 1.04 | a clip zoomed 10 % |
| Speech | transcript equals the line; no extra words; `retime_clip.py` has no `<- strong` speech parts | intro rushed two sentences |
| Gestures (M4) | contact sheet around each gesture; hands clasped elsewhere, no arm that rises and snaps back (M2) | V3 wave before "See you next time" |

## Keying and stabilisation (per project, automatic)

`prep_clips.py` keys the green (spill suppression, a slight alpha choke). It uses the shipped `stab.json` framing,
estimated per clip by SIFT + RANSAC against `missk_neutral.png` from the neutral first and last 0.7 s, with drift
interpolated linearly. It applies one common zoom so every clip covers the bottom edge. Output: `clips/keyed/*.npy`
(about 5 GB, about 1 minute with 8 cores).
