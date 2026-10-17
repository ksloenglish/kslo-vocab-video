---
name: kslo-vocab-video
description: Produce K S Lo English vocabulary revision videos titled like "S2 Unit N Useful Words and Phrases" for HKMA K S Lo College students. Anime tutor Miss K (reusable generic clips from the ksloenglish GitHub library) greets "K S Lo students"; phrases first, then words; each item shows an anime illustration, first-letter blanks, a 3-2-1 film-leader countdown, Miss K's voice with a speaking badge, and a meaning card; encouragement pop-ups every 5 items; K S Lo English branding; YouTube title and description. Use when asked to make a words-and-phrases revision video for any unit of the vocabulary DOCX, or to revise or fix such a video.
---

# K S Lo vocab revision video (format v2)

This skill builds the approved revision video for any unit. **Format v2** (2026-10-17) cuts the production cost:
- No Miss K clip per item. A Miss K badge "speaks" each answer.
- Miss K appears only in reusable, generic library clips: intro, transition, outro and six pop-ups.
- Phrases come first, then words.

Per unit, only the items, the illustrations and the item voice takes are new, so **a normal unit needs no video
generation.**

**Read `references/requirements.md` first.** It lists every rule the user set (presentation, falling tone,
gesture-speech sync, branding, mockups, format v2). They are acceptance criteria, not suggestions.

| Topic | Read when |
|---|---|
| `references/presentation_rules.md` | building `items.json`, answering ASK cases, illustrations |
| `references/voice_and_audio.md` | recording item takes, falling tone, loudness |
| `references/missk_clips.md` | what the library holds; regenerating a library clip (only if asked or failing QA) |
| `references/visual_spec.md` | layout and timing, illustration prompt, mockups for visual changes |

## Setup

```bash
sudo pip3 install -q python-docx opencv-python-headless soundfile scipy pyloudnorm praat-parselmouth
S=/home/ubuntu/skills/kslo-vocab-video/scripts
bash $S/fetch_assets.sh          # clones private ksloenglish/kslo-vocab-video to ~/kslo-vocab-video (needs GitHub access)
export VOCAB_PROJECT=/home/ubuntu/kslo_s2_u2        # one folder per video; every script reads it
df -h /home/ubuntu                                  # need about 8 GB free
```

If `fetch_assets.sh` cannot reach the repo, ask the user to enable the GitHub integration for an account with access to
`ksloenglish`. The repo also holds the vocabulary DOCX (`vocab/`), the character design images (`character/`) and the
Unit 1 reference build (`reference/unit1/`; the final MP4 is a release asset).

## Workflow

1. **Initialise.** Run `python3 $S/init_project.py $VOCAB_PROJECT --docx ~/kslo-vocab-video/vocab/<file>.docx --unit 2 --level S2`.
   It creates the folders, copies the templates and the Miss K library, and writes `items.json` and `project.json`:
   phrases first, then words, with the display rules applied.
   - Ask the user every `ASK` case it prints, with concrete options (`ask`; deferred is fine while you start the illustrations).
   - Fix every `CHECK highlights` line in `items.json`.
2. **Illustrations.** For each item, write `image_prompt` from the definition and the sample sentence, using the template in `visual_spec.md`.
   - Generate 5 per `generate_image` call (16:9) into `illus/NN_slug.png`.
   - Review a contact sheet. Regenerate any image with text, a franchise lookalike, or the wrong meaning.
3. **Item voice takes** (`voice_and_audio.md`):
   - Make one `generate_speech` call per item, saved to `audio/items_raw/NN.wav`.
   - Run `check_pitch.py` on every take. Re-record rising takes with carrier sentences, then `extract_take.py`.
   - Listen-check for creaky, swallowed or unclear words.
   - Record the picks in `project.json` `item_takes`.
   - Then run `python3 $S/prep_items.py` and `python3 $S/check_loudness.py`.
4. **Key the library clips.** Run `python3 $S/prep_clips.py` (about 1 minute). Framing comes from the shipped `stab.json`.
5. **Check the timeline.** `python3 $S/timeline.py` prints the segments, the part order and the pop-up slots. It warns about any item without a prepared voice.
6. **Preview stills.** Run `python3 $S/render.py test <times>` (see `visual_spec.md`) and inspect:
   - the opening
   - the Part 1 card
   - a phrase item before and after the reveal (the badge speaking)
   - a pop-up
   - the transition
   - a word item
   - the outro wave
   For a new unit with the unchanged design, check them yourself. **For any visual change, show the user mockups and wait for approval (W1).**
7. **Render.** Run `bash $S/finalize.sh 6` in the background (about 15 min), then `job wait`. It renders the segments, mixes the audio (`build_audio.py`) and muxes to `project.json` `output`.
8. **Final QA:**
   - Transcribe the full video and check the order: intro, phrases, pop-up lines, transition, words, outro.
   - Check frames: opening lockup, a pop-up, an item before and after the reveal, the meaning card, and the outro fade to black.
9. **YouTube.** `python3 $S/youtube_text.py` writes `output/youtube.md` (title and description with chapters, phrases listed first). It never mentions AI, Manus or "generated".
10. **Deliver** the MP4 and `output/youtube.md`. Record decisions in a `NOTES.md` in the project.

## Revisions: what to re-run

| Feedback | Fix | Re-run |
|---|---|---|
| one item sounds wrong, rising or unclear | new takes, then `check_pitch`, then `item_takes` | `prep_items.py N`, then `SKIP_RENDER=1 bash finalize.sh` (audio only); re-render that item's segment if its length changed a lot (badge timing) |
| item too quiet | `item_gain_extra_db` | `SKIP_RENDER=1 bash finalize.sh` |
| illustration wrong | regenerate `illus/NN_slug.png` | `python3 $S/render.py pool 6 <seg idx>`, then `SKIP_RENDER=1 bash finalize.sh` |
| a library clip is wrong (gesture, glitch, lips) | follow "Regenerating a library clip" in `missk_clips.md`, then update the GitHub repo | re-render its segments, then `SKIP_RENDER=1 bash finalize.sh` |
| layout or text change | edit `render.py` constants or `project.json` text, then **mockups first** | after approval, full `finalize.sh` |

Segment indices: `python3 $S/timeline.py` (0 opening, 1 part card, then items with pop-ups, transition, conclusion, outro last).
Keep the previous MP4 as `_vN` and name new outputs `_v(N+1)`.

## Scripts

| Script | Purpose |
|---|---|
| `config.py` | project root (`VOCAB_PROJECT`), folder layout, `project.json` access |
| `fetch_assets.sh` | clone or update the GitHub asset repo (`KSLO_ASSETS`, default `~/kslo-vocab-video`) |
| `init_project.py` | DOCX/CSV → `items.json`, `project.json` (phrases first); copies templates and library; ASK and CHECK lists |
| `timeline.py` | segments, parts, pop-up slots, Miss K clip schedule (shared by the renderer and the mixer) |
| `render.py` | `test <t...>` stills, `pool <workers> <idx,...>` segments, `all <workers>` |
| `prep_items.py` | trim the chosen item takes → `audio/items/`, `work/item_voice.json` |
| `extract_take.py` | cut an item out of a carrier-sentence take, with an ASR check |
| `prep_clips.py`, `keying.py` | chroma key and stabilisation of the library clips → `clips/keyed/*.npy` |
| `make_refs.py`, `retime_clip.py` | library maintenance only: Seedance audio refs; warp a clip so its lips follow the clean voice |
| `check_pitch.py`, `check_loudness.py`, `contact_sheet.py` | QA: falling tone, loudness, gestures |
| `build_audio.py`, `finalize.sh` | mix (voice, SFX, ducked music, loudnorm) and render + concat + mux |
| `youtube_text.py` | YouTube title and description |

Templates: `brand/logo_white.png` (transparent; never add a backing), `missk/missk_neutral.webp` (neutral keyframe;
the badge and any new clip use it), `audio/` (music and SFX), `fonts/`, and `examples/unit1_items.json` (all 30 Unit 1
items with highlights and illustration prompts, as a reference).

**Package size:** the skill must stay under the 11 MB upload limit. All video lives in the GitHub repo, never in the
skill. Never add per-unit media (illustrations, voice) to the skill or the library.
