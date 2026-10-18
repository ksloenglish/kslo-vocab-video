---
name: kslo-vocab-video
description: Produce K S Lo English vocabulary revision videos titled like "S2 Unit N Useful Words and Phrases" for HKMA K S Lo College (S2 items from the vocab DOCX; other levels need the teacher's items and title). Reusable anime tutor Miss K greets "K S Lo students"; phrases first, then words. Every item has a human participant and a different adorable ORIGINAL pocket-monster-style prominent, meaning-bearing co-star, calibrated to Unit 1 rather than a tiny decorative pet; no actual franchise characters. Requires three-pilot style approval and separate full generated-image-set approval before assembly. Includes first-letter blanks, 3-2-1 countdown, familiar Leda voice and speaking badge, meaning card, safely fitted encouragement pop-ups only when at least three items remain in the part, K S Lo English branding and YouTube text. Use to create, revise or fix vocabulary videos, creature illustrations, pronunciation, text or layout.
---

# K S Lo vocab revision video (format v2)

This skill builds the approved revision video for any unit. **Format v2** (2026-10-17) cuts production cost:
- No Miss K clip per item. A Miss K badge speaks each answer.
- Miss K appears only in reusable generic library clips: intro, transition, outro and six pop-ups.
- Phrases come first, then words.

Per unit, only items, illustrations and item voice takes are new; **a normal unit needs no video generation**.

**Read `references/requirements.md` first.** Every presentation, falling-tone, gesture-sync, branding,
mockup and approval rule is an acceptance criterion, not a suggestion.

| Topic | Read when |
|---|---|
| `references/presentation_rules.md` | items.json, ASK cases, placeholders, ellipses, hyphens and exact sentence highlights |
| `references/illustration_style.md` and Section 3 of `/pokemon-vocab-cards` when available, otherwise `references/original_creature_design.md` | before every illustration plan/generation/revision: actual Unit 1 calibration, co-star role/prominence, coherent faces/limbs, waterline and scene variety |
| `references/image_review.md` | every complete generated/revised image set before assembly: full gallery, explicit teacher approval, partial approvals and current-PNG hash gate |
| `references/voice_and_audio.md` | recording, pronunciation/stress/consonants, falling tone, loudness, JSON verification and selective audio revisions |
| `references/missk_clips.md` | library contents or regenerating a library clip, only if requested/failing QA |
| `references/visual_spec.md` | layout, timing, illustration prompt and visual mockups |
| `references/youtube_copy.md` | every final delivery/copy-only request: approved Unit 1 format, final chapters, full headword lists and copy checks |
| `references/unit3_corrections.md` | Unit 3, reported anatomy/scene/pronunciation faults, or complete failsafe production records |
| `references/sharing_and_access.md` | colleague setup, repository access/visibility or delivering a stored skill update |

## Setup

```bash
sudo pip3 install -q python-docx opencv-python-headless soundfile scipy pyloudnorm praat-parselmouth
S=/home/ubuntu/skills/kslo-vocab-video/scripts
bash $S/fetch_assets.sh                     # public ksloenglish/kslo-vocab-video; no owner-specific permission
export VOCAB_PROJECT=/home/ubuntu/kslo_s2_u2 # one folder per video; every script reads it
# Need about 8 GB free:
df -h /home/ubuntu
```

The repository became **PUBLIC on 19 October 2026 at the owner's request**, with anonymous access verified.
Colleagues can use public HTTPS Git/ZIP without a GitHub account/integration. If fetching fails, check live
visibility, network and the existing directory before requesting authentication (`sharing_and_access.md`).
The repo contains `vocab/` DOCX, `character/` images, branding/library and `reference/unit1/` (final MP4 is a
release asset). The bundled original-creature guidance avoids requiring colleagues' access to separate private card repos.

## Inputs: ask first

- **S2:** use the asset-repo DOCX unit table. Default title: "S2 Unit N Useful Words and Phrases", unless the teacher gives another.
- **Any other level (S1, S3–S6…) or items absent from that DOCX: before anything else, blocking ask for (1) the full item list and (2) exact video title. Never guess either.** Each item needs headword, POS, English definition, Traditional Chinese meaning and sample sentence. If fields are missing, ask whether the teacher supplies them or wants drafts for approval.
- Accept DOCX, Excel/CSV or pasted text; convert to CSV `headword,pos,definition,zh,sentence`, retaining order inside phrases/words. Use `init_project.py ... --csv items.csv --unit <N> --level <S3> --title "<teacher title>"`.
- For a custom title not ending "Useful Words and Phrases", set `title_lines`/`kicker` in project.json and show an opening mockup (W1).

## Workflow

1. **Initialise.** Run `python3 $S/init_project.py $VOCAB_PROJECT --docx ~/kslo-vocab-video/vocab/<file>.docx --unit 2 --level S2`. It creates folders, copies templates/library and writes items.json/project.json with phrases first. Ask every printed ASK case with concrete options; deferred is fine while starting illustrations. Fix every CHECK highlights entry before approval.
2. **Plan and generate illustrations.** Read `illustration_style.md` plus the card Section 3 or bundled fallback. Adapt to **16:9 human–creature co-star scenes**, not card UI/creature-only art. Inspect actual Unit 1 anchors and use reference inputs when supported; generic adjectives alone are insufficient.
   - Plan exact meaning, `image_prompt`, `creature_family`, `creature_signature`, `creature_role`, `human_creature_interaction`, `creature_scale_plan` and actual `style_reference_files`. Each picture needs a different adorable ORIGINAL animal-inspired pocket-monster-style co-star with prominent face/silhouette and meaning-bearing action/reaction. Keep a central human, but do not impose human size/dominance or a small passive pet. Use expressive anime faces, distinctive ears/tails, graphic markings and cel shading; no generic plush animals, blobs, franchise lookalikes or realistic scaly lizards.
   - New productions use `illustration_policy: "unit1_costars_v1"` (initialiser default). Produce three representative real-item pilots in the unchanged layout and obtain **style approval before bulk generation**. For selective revisions, apply the policy only to approved replacements; this skill update does not authorise remaking delivered videos.
   - Generate up to five per call into `illus/NN_slug.png`, using current tool schema/quality guidance. Retry failed images only after partial/rate-limited calls.
   - Inspect every actual PNG and start/max-6%-zoom final-size artwork card: exact sentence meaning, human/creature anatomy, prominence/action/design, ordinary-device geometry, waterline/clothing, scene logic and whole-set variety. Trace one coherent bird mouth and every intended limb. A generic PASS never overrides a specific teacher-reported defect. If a patched face remains rejected, regenerate the whole scene with a new character when authorised; keep accepted neighbours unchanged.
   - For laptops trace **keyboard → hinge → lid face**. A picture-facing camera with keyboard extending behind it is an invalid outside-lid screen. A three-quarter-angle assertion is not evidence; prefer plain rear lids/inward screen hidden. Record `device_kinds`, `laptop_lid_check` and concrete `device_structure_evidence`.
   - Run `check_illustrations.py --template`; populate fresh hash-bound reviews, co-star evidence, resolved complaint notes and no unresolved issues, then run the gate. It checks records, not automatic visual correctness.
3. **Full-image review (W7).** After own QA, run `python3 $S/review_images.py` and show **all generated images**, including pilots, in the complete gallery with readable sheets and full-resolution links. Obtain explicit teacher approval in a blocking ask **before full rendering/final assembly**. Pilot/style approval does not approve unseen images. One full-gallery approval suffices, not thirty dialogs. Record the presented ID/reply using `--approve`; preserve partial approvals by exact hashes, fix only rejected images and re-present them. `--check` blocks missing/stale approval. See `image_review.md`.
4. **Approval before audio (W5).** Fix highlights, run `python3 $S/review_list.py` and show `output/review_list.md` in a blocking ask: every spoken form, TTS text, blanks and clue sentence. **Generate no item audio before approval.** Apply corrections and regenerate the list. Speaking-list approval and image approval are separate; approved audio preparation may proceed independently while image review is pending.
5. **Item voice takes** (`voice_and_audio.md`). One generate_speech call per item into `audio/items_raw/NN.wav`, keeping familiar Leda/en-GB/baseline style. Run check_pitch on every take; re-record rising takes with carriers and extract_take. Listen for actual stress/weak vowels, all consonants/syllables, fully voiced natural words and falling endings. Pitch/ASR cannot prove a final /t/; preserve quiet unvoiced tails and reject added vowels. Read authoritative saved JSON, not repeated terminal snippets. Validate all selected candidates before changing shared files; save `project.json` `item_takes`, then `prep_items.py` and `check_loudness.py`.
6. **Key/check library and timeline.** Run `prep_clips.py` (shipped stab.json framing). `timeline.py` prints parts, segments and pop-ups and warns about unprepared voices. Pop-ups only after each fifth item with **at least three following items in that same part**, never counting the next part.
7. **Preview stills.** `render.py test <times>` (`visual_spec.md`): opening; Part1; phrase countdown/blanks/clue and reveal/speaking badge; every used pop-up entry/overshoot/hold/exit; transition; word item; outro wave. `check_popup_layout.py --stills` validates all six lines including unused ones, rejects unreadable overflow and checks minimum-three policy. Check unchanged designs yourself; show mockups and await approval for a new visual direction (W1). Direction/regeneration approval permits generation, not bypassing the complete-image review.
8. **Render/assemble.** Run `bash $S/finalize.sh 6` as finite background work, then job wait. It blocks failed own-image QA, missing/stale **teacher image approvals** and pop-up checks before rendering/mixing/muxing. Image-only revisions copy old encoded audio/preserve untouched segments and check approval of every changed image (`illustration_style.md`). Named audio-only repairs use `audio_revision.py snapshot/finish`, preserving all images and original PCM outside repaired-word windows; unchanged images need no new review.
9. **Final QA.** Transcribe full video and verify intro, phrases, permitted pop-ups, transition, words and outro in order. Check encoded opening lockup, every pop-up's complete text, every changed illustration's faces/actions, countdown/reveal/meaning card and clean outro fade. Verify no pop-up leaves fewer than three items before a part boundary; generic video-analysis PASS is not text-containment evidence. Re-listen to repaired words in actual music/SFX. For image-only unchanged timing/identical copied audio, verify encoded-audio hash/content invariants instead of repeating the already-passed speech audit.
10. **YouTube copy is required for every unit.** Follow `youtube_copy.md`: `youtube_text.py` writes `output/youtube.md` with branded title, friendly description, final-timeline chapters, all full headwords/counts in actual order, revision tips and hashtags. Finalizers generate it; regenerate after title/content/timing changes. Never mention AI, Manus or "generated". Check against the final video.
11. **Deliver MP4 and the `output/youtube.md` link together.** Copy-only requests generate text without re-rendering; explicit chat requests get separate copyable title/description blocks. No YouTube upload/publishing unless separately requested. Maintain current status plus chronological project NOTES.md: source/checksums, exact approvals, prompts/refs, defects/resolutions, rejected/selected takes, metrics/listening disagreements, hashes/preservation proofs, output/version and unresolved limits (`unit3_corrections.md`).

## Revisions: what to re-run

| Feedback | Fix | Re-run |
|---|---|---|
| Named item has wrong stress, missing consonant, rising/unclear speech | `audio_revision.py snapshot --source <old MP4>` BEFORE edits; new same-Leda takes; phonetic/pitch/JSON checks; validate all candidates | `prep_items.py <N ...>` with per-item guards if needed, then `audio_revision.py finish --items <N ...>`; final-mix/JSON verification; no new review of unchanged images |
| Item too quiet | Snapshot first; change only its `item_gain_extra_db` | `audio_revision.py finish --items <N>`; other word windows preserved |
| Wrong/missing/uncanny creature or scene | `image_revision.py snapshot --source <old MP4>` BEFORE edits; fix only reported items, refresh own QA and show all replacements with `review_images.py --items …` for explicit approval | check QA/approval, render only affected items, then `SOURCE_MP4=<old MP4> SKIP_RENDER=1 bash finalize.sh`; content/timing/audio protected |
| Library gesture/glitch/lips wrong | Follow missk_clips.md regeneration; update GitHub clip/library.json/stab.json | re-render its segments, then SKIP_RENDER finalization |
| Layout/text change | Edit render.py constants/project text; mockups first | approved full finalization; preserve accepted artwork/approvals where unchanged |
| Clipped pop-up words | Glyph-bound popup_layout.py, never fixed-size unmeasured text | check_popup_layout.py --stills; approval; render affected pop-ups; inspect encoded bubbles |
| Pop-up isolates one/two final items | popup_positions(), POP_MIN_REMAINING=3 per part | timeline/full render after mockup approval; regenerate chapters/check speech order |
| YouTube copy only | youtube_copy.md and actual video data | youtube_text.py; review/deliver copy; no render/publishing |

Use timeline.py for actual segment indices (opening0, part card1, then items/pop-ups, transition, conclusion/outro).
Preserve previous MP4 as `_vN`; name new output `_v(N+1)`. Never overwrite a baseline after edits.

## Scripts

| Script | Purpose |
|---|---|
| config.py | VOCAB_PROJECT root, paths and project.json |
| fetch_assets.sh | public GitHub clone/update or explicitly supplied snapshot (KSLO_ASSETS, default ~/kslo-vocab-video) |
| init_project.py | DOCX/CSV→items/project, phrases first; templates/library; ASK/CHECK |
| timeline.py | shared renderer/mixer segments, parts, pop-ups and library schedule |
| render.py | test stills; pool workers/indices; all workers; tested literal ellipsis/hyphen blanks |
| review_list.py | full speaking-list approval before item audio |
| review_images.py | complete/paginated image gallery, bound review ID, explicit per-image approval hashes, blocking --check |
| prep_items.py | chosen take trim→audio/items and item_voice duration; optional per-item item_trim, safe consonant tail |
| extract_take.py | carrier extraction with configurable guards/group threshold and authoritative JSON ASR |
| verify_transcription.py | strict isolated/full JSON lexical count/order; explicit reported optional ASR normalisations, not phonetic proof |
| audio_revision.py | pre-edit snapshot; named-word PCM-window patch/guards; unchanged imagery/timing/voices; AAC mux/new version |
| prep_clips.py, keying.py | chroma key/stabilise library into keyed clips |
| make_refs.py, retime_clip.py | library only: Seedance audio refs, video lip-retiming to untouched clean voice |
| check_pitch.py, check_loudness.py, contact_sheet.py | falling-tone/loudness/gesture QA |
| popup_layout.py, check_popup_layout.py | glyph-fit blocking checks for six lines, minimum-three policy and pop-up phase stills |
| check_illustrations.py | current-PNG/hash/size, distinct metadata, policy-aware co-star role/prominence/design/card/device evidence |
| image_revision.py | snapshot then finish: protected text/timing/library; approval of changed images; identical copied encoded audio |
| build_audio.py, finalize.sh | matched voice/SFX/ducked music/loudnorm, gated render/concat/mux |
| youtube_text.py | checked title/description |
| test_illustration_policy.py, test_presentation.py, test_audio_safety.py, test_image_approval.py | synthetic policy, hyphen, consonant/JSON/PCM and teacher-approval regression tests |

Templates retain original transparent `brand/logo_white.png` (no backing), neutral `missk/missk_neutral.webp`
(badge/new clips), music/SFX audio, fonts and `examples/unit1_items.json` with30 highlighted reference items/prompts.

## Update and share this skill

Validate the full package and regression tests after changes. Sync only the verified skill snapshot to the asset
repository; never remake accepted media as part of a skill update. Deliver this **SKILL.md attachment** to package
all references/scripts/templates, and offer **Add to My Skills** for the user's stored future-task update.
Local edits alone do not prove the global account skill changed. Colleagues install the whole updated package;
`sharing_and_access.md` explains public downloads and the bundled design fallback.

**Package must stay under11MB.** Large video assets live in GitHub, never in the skill. Never add per-unit images,
voice or MP4s to the skill/reusable library; exclude test outputs/bytecode caches from the delivered package.
