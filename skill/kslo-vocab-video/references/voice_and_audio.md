# Voice and audio

Read the `tts-prompter` skill before the first `generate_speech` call.

## Miss K's voice (fixed)

| Setting | Value |
|---|---|
| `voice_name` | `Leda` (studio voice; the teacher loves this voice and explicitly chose to retain it, including for targeted British-pronunciation corrections; no pitch lift) |
| `language_code` | `en-GB` |
| style, long lines | `high pitch, bubbly, cheerful and excited inflection` |
| style, items | `clear, high pitch, bright and cheerful; calm statement with a falling tone at the end` |
| Pronunciation | Write **"K S Low"** for K S Lo ("Lo" = "low", never "law"). Write "Miss K". ASR shows these as "KS Low" and "Miss Kay", which is correct. |

### British pronunciation (teacher preference, 2026-10-18)

Use British English readings. **`Leda` is a studio voice with a General American base; `en-GB` does not guarantee a British accent.** Listen for the actual vowels, stress, consonants and diagnostic rhotic R. Compare unclear UK/US distinctions with an authoritative dictionary, not the ASR spelling. Cambridge lists privacy as UK /ˈprɪv.ə.si/ versus US /ˈpraɪ.və.si/, and antisocial as UK /ˌæn.tiˈsəʊ.ʃəl/ rather than the US "ant-eye" variant.

For an explicitly requested whole-video British-pronunciation audit, audit **every** take and regenerate only those with concrete American-specific pronunciation (plus any separately reported unclear word); retain neutral/shared and already British-compatible takes. For named-word stress/consonant repairs, change **only the named items**, not the whole voice bank. Check every occurrence when the reported word repeats. Preserve Leda with reliable respellings; phonetic TTS spellings must never appear on screen. Listen to replacements: ASR cannot verify accent, stress or a final consonant.

**Preserve Miss K's familiar Leda voice in current and future videos unless the teacher explicitly approves a change.** The teacher rejected switching to a native British sample and asked for particular-word corrections while keeping Leda (2026-10-18). Retain the exact baseline style where possible; broad delivery changes can sound unlike the familiar takes. Try continuous phonetic respellings or IPA for a stubborn word, then check the actual result. Hyphenated "priv-uh-see" caused broken, hesitant delivery in Unit 2 and must not be accepted merely because it has the correct first vowel. Reject spoken symbols, missing words, extra syllables or a conspicuous voice change. If correction is unreliable, keep the better natural take and disclose the unresolved pronunciation; do not silently substitute another voice or promise a fully British accent. Offer a native British voice only as an explicitly approved alternative.

**Unit 2 results:** With Leda, `en-GB` and the unchanged item style, `Invade privicy. <long pause> That's the phrase.` gave a smooth, familiar-voice candidate; extract the **first** group. Isolated listening checks reported the British short-i vowel, but the final mixed-audio check disagreed, so **do not treat this as a verified British-pronunciation recipe**. Keep "privacy" on screen and disclose any uncertainty rather than claim success. Continuous `privvacy` changed the audible timbre, and IPA often normalized back to the American reading or produced symbol names. In contrast, `Criticism. <long pause> Criticism.` with the same baseline style, extracting the **last** group, gave confirmed clearer complete syllables and a falling ending without a voice change. Check every new take.

For repeated words, reuse a same-voice word take when another full-phrase recording fails. Unit 2 "respect privacy" retained the original "respect" and used the natural "privacy" candidate from "invade privacy". Locate each actual word boundary with waveform/speech-group inspection, preserve consonant guards and a natural short gap, and audition the join; never copy time offsets blindly to a new take. This edit preserved completeness, naturalness, voice identity and a falling ending without pitch/timbre processing, but final checks did **not consistently verify the British vowel**. Keep unnatural takes out of the video, and explicitly identify original readings retained or pronunciation changes still unconfirmed.

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
   - Multisyllabic words are not rushed or compressed. If the teacher finds a word unclear (Unit 2: "criticism"), regenerate it with unhurried articulation, check all consonants/syllables by listening, and retain its natural duration. An ASR match or pitch PASS alone is insufficient.
   - After extracting a carrier take, confirm the initial consonant and final syllable were not cut off; keep small leading/trailing guards and reject incomplete takes.
   - Check the **stressed syllable and weak-vowel reduction**, not merely whether ASR spells the word correctly.
   - Listen through final **unvoiced** consonants: a correct voiced pitch contour cannot verify /s/→/t/.
     Retain the stop closure/release, but reject an added vowel such as “boost-uh”. Check the prepared
     cut and actual music/SFX mix, because a good raw ending can be trimmed or masked later.
5. Record the chosen take per item in `project.json` `item_takes` (e.g. `{"14": "14_A", "21": "21_Cw"}`). The default is `items_raw/NN.wav`.
6. Hand-fitted takes: if a short word is swallowed, slow the rest a little (atempo 0.85) and keep the function word at its natural length. Save the result as a new take and list the item in `nostretch`.
7. Run `python3 $S/prep_items.py`. It trims each chosen take to `audio/items/NN_slug.wav` and writes `work/item_voice.json`
   (the length drives the badge's speaking animation). Items have no lip-sync in format v2, so any take can be swapped at
   any time: rerun `prep_items.py N`, then the audio-only finalise.

## Unit 3 pronunciation recipes and rejection checks

These are **tested starting points, not guaranteed readings**. Keep `Leda`, `en-GB` and the exact baseline
item style, with only a short delivery addition where required. Recheck every returned reading.

- **Concern:** target weak first syllable and stressed second — con-**CERN**. Generate
  two unhurried readings separated by a long pause, retaining the baseline style and explicitly
  requesting weak-first/stressed-second delivery. In Unit 3, the **first** reading was selected rather
  than the rising alternative. The chosen first
  reading had a 2.8-st mild pitch metric, but isolated and final-mix listening confirmed a natural
  fall with a short schwa-like first syllable and a fuller longer second. Record that metric/listening
  discrepancy explicitly; never use it to excuse a >3-st rising take. The final vowel remained rhotic,
  so do not claim this recipe establishes a fully British accent.
- **Boost:** target `/buːst/`, clearly audible `/s/` then `/t/`, with no extra vowel. Plain
  `Boost. <long pause> Boost.` plus `crisp final t release` still produced too-soft /t/. A second call
  `Boostt. <long pause> Boostt.` plus `precise enunciation` gave two different outcomes: reject the
  first for exaggerated aspiration/schwa-like ending; the **second** had a crisp natural final /t/
  and a −2.2-st falling pitch result. Keep **boost** on screen and in the word list. Do not assume a
  correct ASR “Boost” makes the consonant complete; inspect/listen through the unvoiced release.

Locate new speech groups from the actual waveform; never copy Unit 3 timestamps into another take.
Too-low RMS thresholds can bridge a pause using background breath/noise. Inspect groups and tune
`--gap`/`--rel` rather than treating two readings as one word. Use `extract_take.py --head … --tail …`
and per-item `item_trim` overrides in `project.json` for consonant guards; for a weak final stop, start
with roughly 40 ms head / 180 ms tail and `rel: 0.01`, then verify the actual boundary and retained
release. Defaults remain 20/60 ms for ordinary prepared items. Place fades in the guard silence, not
on the stop burst. A larger guard must not accidentally include another word or carrier.

When broad auditions, pitch metrics and mixed-fragment models conflict, use a neutral isolated A/B
comparison with concrete phonetic questions and the measured contour. Verify the assembled take by
waveform/correlation if needed. Do not repeatedly regenerate a correct take or change voice identity
based solely on a contradictory context-dependent “mature voice” label; retain/document uncertainty.

## Authoritative transcript verification

Read the **saved ASR JSON**, not terminal snippets/progress screens. The CLI can display the same line
twice: Unit 3 printed “Boost” twice, but JSON contained one segment and `full_text: "Boost"`. Treating
rendered output as transcript falsely rejected it. Very short shared words may get an unreliable
language label (`nld` for boost); that is not proof of a wrong language/accent. Verify actual phonetics.

Validate **all selected candidates before changing shared takes/prepared files**, and fail fast on
errors. Check isolated JSON equals the intended lexical word/phrase once, with no carrier, extra
article, spoken symbol or added syllable. Then check final full-video JSON for all answers once in
order and the library/part order. Use `verify_transcription.py --transcript <JSON>` and its isolated
`--expected "boost"` mode. Explicitly document any ASR normalisation; never silently normalise away an
actual spoken error. ASR spelling still cannot prove stress, British vowels or a final /t/.

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
words (each exactly once, with no extra words), each permitted pop-up after its 5th item with at least three remaining items in the same part, the transition, and the outro. Re-listen to regenerated unclear words in the actual mixed video.

## Selective audio-only revisions

Before editing, run `audio_revision.py snapshot --source <current MP4>` and retain its original
uncompressed soundtrack, selected-take metadata and hashes. Archive a previous baseline before a
new correction; never create a new baseline after files have changed. Change only named verified
takes, prepare only those items, and set a new output version. Finish with
`audio_revision.py finish --items <N ...>`; it uses the proven Unit 3 patching approach rather than
replacing the whole soundtrack with a newly normalised mix. See `unit3_corrections.md` for the record.

Preserve all approved artwork, text, timeline, other prepared voices and library segments. Update only
the affected badge-animation duration when necessary. Match new word loudness/backing level, replace
only small word windows with silent-edge crossfades, and verify original PCM samples outside those
windows are unchanged. Verify no overlap, cut consonants, clipping or masked release in the final mix.
The revised audio is AAC-encoded, so **do not claim byte-identical encoded audio for an audio change**.
That claim belongs only to image-only revisions that copy the old encoded audio stream exactly.
