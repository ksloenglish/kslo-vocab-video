# Voice and audio

Read the `tts-prompter` skill before the first `generate_speech` call.

## Miss K's voice (fixed)

| Setting | Value |
|---|---|
| `voice_name` | `Leda` (studio voice; the user chose the natural version, no pitch lift) |
| `language_code` | `en-GB` |
| style, long lines | `high pitch, bubbly, cheerful and excited inflection` |
| style, items | `clear, high pitch, bright and cheerful; calm statement with a falling tone at the end` |
| Pronunciation | Write **"K S Low"** for K S Lo ("Lo" = "low", never "law"). Write "Miss K". ASR shows these as "KS Low" and "Miss Kay", which is correct. |

## British accent, same voice (V9)

Miss K must sound British **and** keep her voice. The voice always stays **Leda**; never change the voice to get the accent.
Leda is a studio voice catalogued as General American English, so the accent can only be steered, as follows:

1. **`language_code` `en-GB` on every `generate_speech` call**: items, carrier sentences, retakes and regenerated library
   lines. Never leave it out and never use `en-US`.
2. **British spelling and wording in the TTS text**: analyse, colour, practise (verb), centre, programme, favourite,
   organise, travelling. For the generic lines, use British wording (e.g. "brilliant", "revise", "have a go").
3. **Never write the accent into `style`** ("British accent", "RP" and so on). The `tts-prompter` skill forbids it and it
   can distort the voice. Keep the fixed style phrases above.
4. **Listen check on every take**, as well as the falling-tone check. Reject and re-record (or use a carrier sentence)
   any take with clearly American features:
   - a strong "r" after vowels ("feature", "latest offer", "bargain", "matter", "for", "car")
   - a flapped "t" that sounds like "d" ("latest", "matter", "a variety of", "better")
   - American vowels in words such as "can't", "bath", "staff" (long "ah" in British), "not", "got" (rounded in
     British), and "privacy" (British "PRIV-", short i)
   - American stress or forms: "advertisement", "laboratory", "garage", "schedule", "vitamin", "route", "leisure"
5. If a word keeps sounding American after 3 takes, try a carrier sentence with British context ("In Britain, we say
   latest.") and extract the word with `extract_take.py`. If that still fails, tell the user which items are affected
   and ask how to proceed. **Do not switch voices without the user's approval**, because a new voice would also need the
   library lines re-recorded and every Miss K clip regenerated.

## Long lines: the library (format v2)

The intro, transition, outro and pop-up lines are **already recorded and lip-matched** in the GitHub library
(`missk_clips.md` lists the exact lines). They are generic, with no unit or numbers, so **never re-record them for a
unit.** For a regenerated library clip, record with the long-line style and write "K S Low". The transcript must match
the line word for word.

## Word and phrase takes: falling tone (V3) and clarity (V4, V5)

1. Record **each item in its own `generate_speech` call**. Text = the display form with a full stop ("Based on."). Reading a list in one call gives rising, list-like intonation.
2. Run `check_pitch.py audio/items_raw/*.wav`. A RISE (> 3 st) is rejected. "mild" (1.5-3 st) is usually rejected for phrases.
3. For items that keep rising, use **carrier sentences** and cut the item out with `extract_take.py`:
   - end-carrier: "The next phrase is: based on." then `--group last`
   - start-carrier: "Based on. That's the phrase." then `--group first`
   The ASR line printed by `extract_take.py` must be exactly the item. Save several takes (`21_A`, `21_C`, then `21_Cw` after extraction).
4. Listen-level checks that the pitch tool cannot do:
   - The word is fully voiced (not creaky or whispered, as 'haggle' was in V2).
   - Every function word is clear and long enough ("of" in "a variety of").
   - The ending is not emphatic or odd ("with" heard as "with one").
   - There are no extra words.
5. Record the chosen take per item in `project.json` `item_takes` (e.g. `{"14": "14_A", "21": "21_Cw"}`). The default is `items_raw/NN.wav`.
6. Hand-fitted takes: if a short word is swallowed, slow the rest a little (atempo 0.85) and keep the function word at its natural length. Save the result as a new take and list the item in `nostretch`.
7. Run `python3 $S/prep_items.py`. It trims each chosen take to `audio/items/NN_slug.wav` and writes `work/item_voice.json`
   (the length drives the badge's speaking animation). Items have no lip-sync in format v2, so any take can be swapped at
   any time: rerun `prep_items.py N`, then the audio-only finalise.

## Loudness (V6)

`build_audio.py` loudness-matches every item: max short-term loudness (400 ms) to −18.2 LUFS, within ±3 dB.
`check_loudness.py` lists items more than 1 dB below the median. If an item still sounds soft, add
`item_gain_extra_db` (Unit 1: `{"12": 1.0}` for 'unique'). The final mix is loudnorm −16 LUFS, TP −1.5.

## Library lines and lips (V7)

Seedance re-times and sometimes rushes speech. Do not stretch the voice to fit. `retime_clip.py` warps the **video**,
so each speech stretch of the clip lands on the matching phrase of the clean voice (it merges the shortest pauses
until the phrase counts match, and absorbs differences in the idle pauses). The clean voice then plays untouched, and
there are no stray sounds or smeared passages (the V2 "s" and 05:02 problems came from cutting and stretching the
voice).

## Music and SFX (templates, already levelled)

`bgm_a` (opening and Part 1) and `bgm_b` (Part 2 and ending): soft, upbeat and ducked under the voice. Music stops for the final black.
SFX: logo sting, whoosh per card and on each pop-up in and out, 1 kHz countdown beeps on 3-2-1 with a projector loop, a reveal chime at "time's up", and a finale sparkle.

## Final audio QA

Transcribe the whole video (`ffmpeg -vn -ac 1 -ar 16000` then `manus-speech-to-text`) and check, in order: intro, the phrases then the
words (each exactly once, with no extra words), each pop-up line after its 5th item, the transition, and the outro.
