# K S Lo English: vocabulary revision video assets

This repo holds the shared assets for the **"S2 Unit N Useful Words and Phrases"** revision videos made with the Manus
skill `kslo-vocab-video`, featuring the anime tutor **Miss K**. Clone it in any Manus account to build a new unit with the
same character, voice, branding and reusable clips.

**Public from 19 October 2026.** Colleagues can browse, download the ZIP or clone without a GitHub
account or owner-specific permission. The updated skill includes the required design guidance, so the
separate teacher-created card skill/private card repositories are not prerequisites.

## Quick start (new unit, in Manus)

1. Add the skill from `skill/kslo-vocab-video/` if the account doesn't have it yet. Zip that folder, or upload it as a skill.
2. Download/clone the public assets; GitHub integration is optional for reading them. Install the **whole
   skill directory**, not only its SKILL.md, so all scripts/references/templates are present. A shared
   Manus skill attachment can be added directly to **My Skills** for future tasks.
3. Ask Manus: *"Use the kslo-vocab-video skill to make the S2 Unit 2 video from the vocab DOCX in the ksloenglish GitHub repo."*
   The skill runs `scripts/fetch_assets.sh`, which clones this repo to `~/kslo-vocab-video`, and then follows its workflow.

A normal unit needs **no video generation**. Only illustrations and the item voice takes are new.

The teacher first approves three style pilots and the complete speaking list. After all illustrations
are generated and checked, the skill shows **every image in a readable gallery with full-resolution
links** and waits for explicit full-set approval **before video assembly**. Rejected images are corrected
and re-presented; approved images are protected by hashes. A pilot approval does not approve unseen art.

Recent Unit 3 safeguards cover coherent beaks/mouths, complete limbs, clothing at the waterline,
distinct exercise scenes, second-syllable concern stress and audible final /t/ in boost. See
`skill/kslo-vocab-video/references/unit3_corrections.md` for the correction/verification record and
`references/sharing_and_access.md` inside that skill for access/install guidance. Public availability
does not assign a new blanket copyright licence to assets; retain existing rights and notices.

## Contents

| Folder | What |
|---|---|
| `library/` | **Reusable Miss K clips (format v2).** `clips/missk_<name>.mp4`: `intro`, `transition`, `outro`, `pop1`-`pop6`, `idle`, on chroma green, 1280x720, 24 fps. `aligned/<name>.wav`: the clean voice, already lip-matched (place it at the clip's start). `library.json`: lines and lengths. `stab.json`: framing. `source_clips/`: the raw Seedance outputs. |
| `character/` | Miss K design: `missk_master_design.png` (original design) and `missk_neutral_keyframe.png` (2560x1440 on green; the first and last keyframe for every clip, also used for the badge). |
| `brand/` | K S Lo English logo: the original transparent PNG and `logo_white.png` used in the videos. Never add a glow or backing behind it. |
| `vocab/` | `S2_Vocab_Items_by_Unit_with_Definitions.docx` (all units). |
| `voice/` | `library_lines/`: the TTS takes behind the library clips (voice **Leda**, en-GB; "K S Lo" written as "K S Low"), with transcripts. `samples/`: the voice options the teacher chose from (A: natural was chosen). |
| `reference/unit1/` | Unit 1 reference build (V5, words first, per-item Miss K clips): 30 illustrations, items, YouTube text, production notes. The final MP4 is a **release asset** (`unit1-v5`). |
| `reference/mockups/` | Approved mockups: the format v2 quiz screen, the badge speaking, the pop-up, a pop-up preview MP4; Unit 1 V3 mockups. |
| `skill/kslo-vocab-video/` | A copy of the Manus skill (scripts, references, templates). |

## Library lines

| Clip | Line |
|---|---|
| intro (15 s) | Hello, K S Lo students! I'm Miss K, your virtual English tutor. Let's revise some useful words and phrases together. Look at each picture, think of the answer, and say it out loud before time runs out. Ready? Let's go! |
| transition (6 s) | Great job with the phrases! Now let's try some words! |
| outro (12 s) | Fantastic work, K S Lo students! Keep revising these words and phrases, and try using them in your writing and speaking. See you next time! (the wave happens only on "See you next time") |
| pop1-pop6 (4-5 s) | Great job! Keep going! · You're doing really well. Let's keep going! · Nice work! Here come some more. · Brilliant! You're on a roll! · Keep it up! You've got this! · Almost there! Just a few more to go! |

Known limits of this library:
- `pop6` reuses the `pop2` video, retimed to its own voice, because generation was refused as a false copyright match.
- In `intro`, two sentences play with lips at about 0.7x speed.

Regenerate either one if needed (see `skill/kslo-vocab-video/references/missk_clips.md`), then commit the new clip, its
`library.json` entry and `stab.json`.

## Format v2 at a glance

The video runs in this order:
1. Opening logo lockup, with Miss K's intro.
2. Part 1: phrases.
3. Transition clip.
4. Part 2: words.
5. "Well done", the outro clip, and the logo screen fading to black.

Each item shows an illustration, then "What's the phrase?" with first-letter blanks and a 3-2-1 film-leader
countdown. The answer is then revealed with the Miss K badge speaking, plus a meaning card (POS, Chinese, definition,
highlighted sample sentence). A Miss K encouragement follows every fifth item **only when at least three
items remain in that same part**. The full rules are in
`skill/kslo-vocab-video/references/requirements.md`.
