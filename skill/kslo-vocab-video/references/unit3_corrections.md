# Unit 3 correction record and regression checklist

## Latest verified state

**S2 Unit 3 is complete at video version 3 (19 October 2026).** Retain the five approved illustration corrections and the later concern/boost repairs. Earlier “pending” notes and discarded candidates are historical, not current approvals. This skill update does not authorise regenerating any delivered video.

Source: asset repo `ksloenglish/kslo-vocab-video`, production source commit `e21ff77efb0de2bab9291f4ad079b991366aea75`; `vocab/S2_Vocab_Items_by_Unit_with_Definitions.docx`, SHA-256 `650fc4d39106dce3dc6581741d839562171ad715bf00d246df8ff496d47897d9`. Exact title: **S2 Unit 3 Useful Words and Phrases**; 16 phrases then 14 words, unchanged format-v2 Miss K library and Leda voice.

## Approved display/source decisions

- `lighten sb's mood`: spoken `lighten mood`, visual `lighten ... mood`, dots literal during countdown/reveal, full headword on card and `lighten our mood` in sentence.
- `self-disciplined`: one lexical word with literal hyphen, first letters for self/disciplined, letter-count main bars and equal fixed-length sentence-clue bars. Ported/tested hyphen-aware renderer.
- Keep approved source `break sweat` (no added a), `dietary fiber` and `recognize`; no unsolicited source-language edits. Full placeholder forms remain in YouTube lists.
- Preserve source inflections and intervening words: `you're` stays visible with `short on`; `get`/`addicted to` does not blank `too`; `developed`/`a`/`routine` does not blank `fitness`. Correct struggling/regarded/boosted/motivating/demonstrated highlights.

## Illustration planning and original production

Inspected actual Unit 1 anchors `03_irrelevant`, `04_feedback`, `14_haggle`, `29_try_your_hand_at`. Three Unit 3 pilots were #1 overwhelmed (emotional pressure), #10 instead of (shared stair climbing), #14 break sweat (VR exercise). Teacher approved the pilot style and complete speaking list on 18 October at23:02 HKT. The VR pilot was widened for safe raised-hand/feet framing; inspected actual 0%/6% artwork cards, not only source images.

Compared all30 actual creature identities. `trend` initially resembled the red-panda family and `remind` resembled a fox: replaced them with a silver-blue round-eared raccoon and a stout beaver with flat paddle tail. A beaver edit introduced floating attention triangles; removed and reinspected. Metadata is not proof of actual design diversity.

### Teacher-reported defects and accepted fixes

| Item | Rejected defect | Final approved fix | Prevention |
|---|---|---|---|
| #4 not to mention | Weird toucan beak; two beak-edit attempts still uncanny | **Regenerated entire food-shop scene with NEW cream/plum fantasy ferret**, normal mammal nose/smile, leaf-tuft tail; presents extra flavouring bottle beside overflowing snack basket | Check one coherent mouth, stop patching a rejected face, use accepted style anchors without rejected identity, obtain new preview approval |
| #12 work out | Creature looked as if a limb was missing | Four connected, countable limbs in the shared stretch; three ground-contact limbs plus one raised limb | Trace shoulder/hip-to-paw/hoof for every intended limb, do not count the tail as a limb |
| #16 develop a routine | Too close to break sweat’s standing VR dance | Distinct **seated stationary cycling** with co-star timing/helper role | Plan action/posture/props/viewpoint differences for related meanings, compare full set |
| #18 beneficial | Boy’s trouser-clothed legs appeared submerged | Dry rolled-up cuffs above water, bare lower legs in the countryside water | Inspect actual waterline and clothing logic |
| #23 wary | Beak plus separate mouth | One unified bird bill/mouth, no second human-like mouth | Trace connected upper/lower beak and oral cavity; reject extra facial mouth plate |

Teacher feedback at23:36 superseded earlier generic PASS. Snapshotted BEFORE edits. At23:48, four fixes (#12/16/18/23) were approved while #4 remained rejected; preserved their exact hashes. Entire #4 regeneration was explicitly authorised and approved at23:53. Source/start/maxzoom/full-layout previews and final encoded changed screens were inspected. Only five item segments changed; all25 other PNGs and34 other encoded segments remained hash-identical. Version2 copied and verified identical original encoded audio; ADTS SHA-256 `eec047c57471170a7af5a6e0cc1c76a10a4c1b8de510b89ccb5f600442abf17e`.

## Pronunciation and take-selection lessons

Keep the familiar Leda studio voice, en-GB, no pitch lift. Initial production removed unwanted articles from lighten mood/break sweat, restored the better familiar work-out take and resolved motivate using neutral isolated comparison: `25_Ew` (three clear syllables, falling result−2.4st), not discarded `25_Fw`. Broad/mixed model “mature” labels conflicted with dry comparison; verified which actual prepared take was encoded rather than silently swapping voices. Natural British-compatible candidates for regarded/alternative/proper were adopted; other retained American-base readings were not advertised as fully British.

| Item | Fault and failed candidates | Verified current take | Concrete final check |
|---|---|---|---|
| #17 concern | Teacher reported first-syllable stress; rising alternative rejected | `17_V3w`, first unhurried repeated reading, requested weak-first/stressed-second delivery in the familiar Leda style; prepared0.92s | Short weak first schwa-like syllable, louder/longer full stressed second, complete nasal ending, natural fall. Mild2.8st metric caveat documented against direct listening; final vowel still rhotic, so no fully British claim |
| #19 boost | Initial new reading still lacked/softened finalt. First stronger `Boostt` reading added excessive aspiration/schwa-like tail | `19_V3B1`, **second** reading of `Boostt. <long pause> Boostt.`, baseline style + precise enunciation; prepared0.86s, pitch−2.2st | `/s/` then closure and crisp light `/t/` release, no boost-uh, complete single syllable, preserved in actual music/SFX mix |

Actual new group boundaries differed: permissive RMS with too-long gap bridged low-level noise; measured new groups and used suitable gap/threshold plus40ms head/180ms tail. Do not reuse these times in another call. Recheck after preparation, because generic silence trimming can swallow a quiet unvoiced stop. Do not infer correct stress/t from pitch or ASR spelling.

The boost CLI rendered “Boost” twice (full result and snippet), but authoritative JSON had **one** segment and `full_text: "Boost"`. It also labelled the very short shared word `nld`; independent phonetic listening verified the target rather than treating a short-word language guess as accent evidence. Validate all selected JSON results before updating shared clips; use fail-fast commands and consistent selected-take/duration metadata.

## Selective audio revision and verification

Snapshotted version2 before edits. Re-recorded only #17/#19 and re-rendered only their badge segments21/23. Fresh normalised proposed mix was inserted into small windows of the backed-up original PCM:181.14–183.01s and198.34–200.15s, with12ms silent-edge fades and backing-gain ratios approximately1.00021/1.00047. All PCM samples outside those windows remained exactly identical. All30 approved PNGs,37 other encoded segments, other28 prepared voices, text, renderer/layout, total duration and YouTube copy were preserved. AAC re-encoding means this is **not** an identical encoded-audio-stream claim.

Final encoded-mix listening confirmed concern’s weak–strong stress and boost’s clean finite final/t/, no extra vowel, no masking, no conspicuous voice change or digital clipping. Saved full-video ASR JSON verified all30 answers exactly once in order and correct intro/phrases/popups/transition/words/outro sequence. Checked the two final speaking/reveal screens. Full MP4 decode integrity passed; ending/unchanged clips inherited prior verified state and protected hashes.

## Deliverables and record locations

Project folder in the original production sandbox: `/home/ubuntu/kslo_s2_u3`.

| Version/artifact | Record |
|---|---|
| Initial MP4 | `output/S2_Unit_3_Useful_Words_and_Phrases.mp4`,232,024,071bytes |
| Five image fixes | `output/S2_Unit_3_Useful_Words_and_Phrases_v2.mp4`,233,124,484bytes |
| **Latest video** | `output/S2_Unit_3_Useful_Words_and_Phrases_v3.mp4`,233,145,290bytes;1920×1080/30fps,329.6s |
| Required companion | `output/youtube.md`,1,457bytes; title85characters; full16/14 headword lists |
| Chapters |0:00 Welcome;0:20 Phrases;2:50 Words;5:07 Wrap-up |
| Spot-check audio | Concern3:01 (181.49s); boost3:18 (198.69s) |
| Image-preservation evidence | `work/revision_v2/`, source/approved hashes and changed encoded previews |
| Audio-preservation evidence | `work/revision_v3_audio/`, baselines, candidate reviews, rejected takes, JSON transcripts, patch/verification reports |
| Complete chronological project record | `NOTES.md` (later explicit status supersedes earlier pending/provisional notes) |

These are production records, **not bundled or newly uploaded Unit3 media**. Keep large unit-specific media outside the small skill and reusable library. No video/YouTube metadata was published in this task. The asset repository was subsequently made public at the owner’s explicit request; see `sharing_and_access.md`.

## Required future failsafe record

Maintain a concise current-state header plus chronological `NOTES.md`: source commit/file checksum; title/order/counts; exact approved display forms; pilot/list/partial/final approvals; prompt and style-reference provenance; original/candidate/current hashes; reported faults and visible resolutions; selected raw/prepared takes/style/phonetic recipe; ASR JSON and concrete auditory evidence; metric disagreements/rejected candidates; preserved content/timing/audio/segment proofs; final file size/codec/duration/cue points; required YouTube copy; unresolved accent/quality limits and publication/access actions. Archive old baselines before new revisions and never turn a provisional PASS into a claim that later teacher feedback was already satisfied.
