# Unit 1-style human–creature co-star illustrations

## Required dependency and video adaptation

Read **Section 3, Illustration Generation**, in the teacher's `/pokemon-vocab-cards` skill
(`/home/ubuntu/skills/pokemon-vocab-cards/SKILL.md` on Sandbox) when available. For colleagues without that
separate skill, read the bundled **`original_creature_design.md`** adaptation instead; this video workflow
does not require access to the card skill's separate private repositories. Inherit the artwork-only declaration,
no-text/no-symbol safeguards, rich environments, vibrant anime rendering, confident outlines and cel shading.
Do not inherit 4:5 composition, rarity, HP, frames, card UI, obsolete model identifiers or creature-only scenes.

Use **16:9**, at least 1920×1080 (preferably 2560×1440). Use a model supported by the current tool schema;
for the teacher's quality preference use `gpt-image-2.5` when available, not the obsolete `gpt-image-2` identifier.

## Default direction — Unit 1 co-stars, clarified 2026-10-18

The teacher prefers Unit 1 (`https://www.youtube.com/watch?v=qyCHApdUaDA`) over Unit 2
(`https://www.youtube.com/watch?v=JvUZ4nBdH4I`): **creatures should be memorable characters in the story,
not small decorative pets added to a human-only scene**. Unit 1 varies the balance: a creature can be a
shopkeeper receiving feedback, a bargaining partner, a craft tutor, a helper or a strongly expressive
companion. Retain a clearly readable human participant and the exact sample-sentence meaning; do not
require the human to be physically larger or visually dominant. A creature may be the principal action
partner while the human remains the customer, learner, decision-maker or person experiencing the situation.

This supersedes older instructions to use a “SMALL” creature, make humans dominate, or restrict creatures
to passive supporting roles. “Supporting” now means **supporting the vocabulary meaning**, not subordinate
screen space. Do not remove humans or turn every scene into a creature-only portrait.

### Reference calibration — before planning the full set

Inspect these actual Unit 1 files in the asset repo (`$KSLO_ASSETS/reference/unit1/illustrations/`, default
`~/kslo-vocab-video/reference/unit1/illustrations/`):

- `03_irrelevant.png`: distinctive blue/cream long-eared fantasy animal, readable foreground body and
  purposeful watering action; it is not merely a tiny animal looking at the human.
- `04_feedback.png`: prominent otter-like shopkeeper displaying soap and receiving human customers'
  reactions; creatures take meaningful social roles, not just sit next to the customers.
- `14_haggle.png`: human–creature negotiating partners; use the interaction and contrasting expressions.
- `29_try_your_hand_at.png`: substantial craft-helper beside a human learner, both engaged with the beads.

Use at least two relevant actual images as **style/composition references** in the generation call when
the current tool supports reference inputs. Discover the current input schema rather than inventing field
names. Reference design language and visual balance, not identities or scenes to copy. Never recolour an
existing creature into a new identity. If reference inputs are unsupported, inspect the files and describe
their concrete characteristics in the prompt. If the repo is unavailable, use the linked Unit 1 video to
extract/view representative artwork before settling the direction; do not silently fall back to generic
“cute animal” prompting. Treat legacy Unit 1 prompts as context only: their symbols, bubbles or logo-like
props are NOT exceptions to the current no-symbol/no-logo rules.

### Stage a character, not an accessory

Plan **one main original creature co-star per image**; additional creatures are optional only if they
improve the meaning without crowding the scene. Specify a role, an observable action, and its relationship
to the human before adding background detail. Use direct interaction (offering a prop, demonstrating,
negotiating, helping), shared work/focus, or a strong meaning-bearing emotional response. A creature that
merely sits smiling, watches from a corner, or provides unrelated comedy does not pass. For a concept
like “irrelevant”, a contrasting purposeful activity can be meaningful; physical contact is not mandatory.

Use medium or medium-close two-character staging where possible. Put the creature in the foreground or
same depth plane as the human, with its full face and characteristic body/ears/tail readable. **As a prompt
starting point, aim for the creature's visible body to span roughly 35–60% of the artwork height**, with a
face large enough to read beside the human face. This is a new composition target, not a measurement of
Unit 1 or an automatic pixel threshold. A counter-level creature can still be a co-star if its face,
action and silhouette are comparably prominent. Avoid distant floor pets, bottom-corner afterthoughts,
blocked faces and full-body wide shots that shrink the pair. If the scene needs a smaller creature,
bring it closer/on an appropriate surface and strengthen its meaningful action rather than accepting
an unreadable mascot. Do not enlarge it so much that the human action or essential prop becomes unclear.

For serious contexts, retain dignity and a non-graphic tone. Use a concerned, protective or meaningful
reactive co-star; do not make the creature the attacker or use unrelated cute comedy to trivialise harm.

### Character-design language

Use a recognisable **animal-inspired fantasy body plan**, lovable expressive anime face, exaggerated
memorable ears/tail and simple graphic colour markings. Combine an animal base (fox, rabbit, otter, cat,
glider, bird, etc.) with distinctive fantasy accents such as leaf-shaped ears, fin tails or a petal collar.
Use confident clean linework, smooth cel shading and a coherent limited palette. A few flat illustrated
cheek/chest tufts are appropriate; realistic fuzzy fur, fleece, pom-poms and plush-toy rendering are not.

Avoid generic fluffy baby animals AND abstract seed/blob/geometric crystal mascots. An elemental accent
must not replace the expressive animal-inspired face/body. Keep companions cute and friendly; do not
restore the rejected realistic scaly lizard, long reptilian snout or aggressive spiky/fanged design.
Do not copy actual Pokémon, franchise characters, recognisable lookalikes, creature-catching balls or
trademark accessories. Accessories may communicate a role but cannot substitute for an original design.

Allocate a **different creature identity in every new picture**, varying body plan, ears, tail, limbs,
markings and fantasy motif, not just palette/accessories. Compare the actual generated set: metadata alone
does not prove diversity. Record `creature_family`, `creature_signature`, `creature_role`,
`human_creature_interaction`, `creature_scale_plan`, `image_prompt` and the actual reference inputs used
in `style_reference_files` (or the viewed video timestamps when files are unavailable).

## Approval and preservation

Before generating the full set in this direction, create **three pilot illustrations** spanning different
needs: an active human–creature task, an emotional/contextual meaning, and a prop/device scene if the unit
contains one. Choose pilots from the teacher's real items, not invented vocabulary. Preview them inside
the unchanged item layout at the beginning and maximum 6% zoom, and show representative mockups for
style approval (W1). Do not infer image approval from audio-list approval. Pilot/direction approval
authorises generating the remaining items only; it does **not** approve images the teacher has not seen.
Use approved pilots and Unit 1 anchors as references where supported. After own QA, show **every generated
image** in the complete `review_images.py` gallery and obtain explicit full-set approval before rendering/
assembly (W7, `image_review.md`). One batch approval suffices; do not request thirty separate dialogs.

For a selective revision, apply the direction **only to approved replacements**. Retain other accepted
artwork unchanged; do not regenerate Unit 1 or Unit 2 merely because this skill was updated. Set
`illustration_policy: "unit1_costars_v1"` in `project.json` for new productions. In an older project,
set that field on replacement items only if untouched legacy images should keep their earlier policy.
New projects made by `init_project.py` receive the new policy automatically; an existing project.json
is not overwritten. Never clear/downgrade the policy to bypass failed reviews.

## Meaning, anatomy and ordinary-device construction

Show the definition **as used in the exact sample sentence**, with a simple readable human–creature scene.
Use literal props, expressions and body language, not floating explanatory pictograms. Avoid crowded
scenes and unnecessary devices. Preserve the user's wording and semantic roles; creature participation
must not change who is doing/experiencing the action or replace an explicitly human subject.

Keep human faces, hands involved in the action, the creature and key props inside the central safe area
for the slight zoom. Humans have two arms/two hands anatomically, including naturally hidden limbs;
trace each visible hand to its forearm/shoulder. Do not invent a third hand to hold a prop while two others
perform gestures. Check wrists, shoulders, grips and body weight for plausible articulation.

### Unit 3 regression checks — run on every applicable scene

- **One coherent bird mouth:** trace the bill into the face and its connected upper/lower mandibles. An
  open beak can be valid, but a second mammal-like mouth, red lip/muzzle below the bill, detached facial
  plate or uncanny patched beak is not. Do not mistake an added red mouth for harmless shading.
- **Complete creature anatomy:** state the intended body plan, then count and trace each visible limb
  from shoulder/hip to paw/hoof. Wings, raised limbs and naturally hidden limbs must make sense; a tail
  is not a substitute for a missing leg. In a four-limbed stretch, explicitly account for all four limbs,
  not merely the three touching the mat. Do not force four legs onto birds or other different body plans.
- **Water/clothing logic:** locate the actual waterline. For the countryside-health scene, rolled-up
  trouser cuffs stay dry above the water and bare lower legs enter it, or use sensible swimwear. Do not
  accept submerged trouser-clothed legs without a context that genuinely warrants wet clothing.
- **Different scenes, not just different animals:** record action, posture, setting, viewpoint and key
  props for similar meanings before generation. Compare whole-set contact sheets after individual
  inspection. `develop a routine` uses seated stationary cycling with a timing/helper role; it must not
  repeat `break sweat`'s standing VR dance composition. Related exercise topics may share an appropriate
  context, but vary meaningful activity and staging rather than recolouring the co-star.

If a face/beak remains uncanny after an edit, or the teacher rejects the patched character, **stop making
successive beak patches**. Regenerate the entire scene with a new original animal-inspired character when
authorised (Unit 3: replace the rejected toucan with a normal-muzzled fantasy ferret). Use accepted Unit 1
style anchors, not the rejected character as an identity reference. Keep the sentence meaning and an
integrated human–creature environment; show the replacement in the unchanged layout for approval.

Bind partial approvals to the exact PNG hashes. Keep already-approved neighbouring corrections unchanged
while an outstanding image is regenerated. After every edit, recheck the exact reported region at source,
start-card and maximum 6% zoom; edits can introduce new symbols, anatomy faults or awkward framing.
Record the specific defect and visible resolution, not only a broad PASS. See `unit3_corrections.md`.

Ordinary devices must remain physically ordinary, regardless of fantastical creatures:

- Phones/tablets: one coherent front screen, plain rear case, sensible thickness/perspective and natural
  grip/support. Show a screen to the viewer only when the camera is on the same viewing side as its user.
  Do not put a display on the back. For complicated poses, rest the device screen-up on a table.
- Laptops: one rectangular display joined by a plausible hinge to a single keyboard/base. Screen faces
  its user, keyboard extends toward the user, device rests coherently on a surface. No inside-out,
  double-sided, fused or floating displays. **Identify the face from the keyboard, not panel artwork.**
  Trace base to rear hinge: the INSIDE face above/facing the keyboard is the front screen; the opposite
  OUTSIDE lid is plain opaque casing. If the keyboard extends BEHIND the picture-bearing panel toward
  the user, the camera sees the OUTSIDE lid and that picture is an invalid rear screen. Do not excuse
  it as a three-quarter view or invent a second display. Prefer a normal rear view with a **plain lid**
  and inward screen hidden when the camera is behind the laptop. Never force screen content outward.
- Smart speakers: conventional screenless fabric-grille cylinder/puck with a small status light if useful.
  Do not invent wraparound picture screens or structural parts to depict recording/listening.
- Other props: plausible scale, support, contact and connections; no fused furniture, impossible camera,
  unnatural cables or unexplained extra structures.

No text, letters, digits, logos, overlay symbols, arrows, ticks/crosses, musical notation, thought/speech
bubbles, card UI or game stats. Ordinary screens/photos may show picture-only content when needed.
Do not invite writing with signs, comment text, prices, graffiti or labelled charts. Product decoration
must not become a fake brand mark or interface.

## Prompt structure and example

Begin with the card skill's artwork-only/no-text declaration, adapted to wide video. Put the co-star
staging **before** rich background detail; do not append a little mascot after designing a human-only scene.

1. State the exact meaning and human role, then the creature's equally readable meaning-bearing role.
2. Describe its original fantasy body plan, face, ears/tail/markings and expressive action.
3. Specify interaction/shared focus, foreground scale and protected two-character framing.
4. Describe hand placement and ordinary-device geometry where needed; then environment, light and cel shading.
5. Repeat no text/UI/overlay symbols and no franchise identities/lookalikes; no tiny passive corner pet.

Example for **try your hand at**, adapted from Unit 1 without copying its character:

> Pure illustration artwork only — no card frame, border, text, letters, digits, logos, symbols, speech
> bubbles or UI anywhere; full-bleed 16:9 scene. A human teenage learner tries making a beaded bracelet
> for the first time beside a prominent ORIGINAL pocket-monster-style craft-tutor co-star. The creature
> supports the meaning by offering the next bead while the human carefully threads the bracelet; both
> look at the same work with delighted, focused expressions. Design an animal-inspired fantasy otter
> with petal-shaped ears, a broad fin-like tail, cream/teal graphic markings and an expressive anime face;
> smooth illustrated cel shading, not realistic fur or a plush toy. Medium-close view at bench height,
> both faces clearly readable at similar visual emphasis, creature occupying about half the artwork
> height rather than sitting as a tiny corner pet. Trace the human's two hands to natural arms, show the
> creature's coherent grip, keep faces, bead and bracelet safe within the 6% zoom. Warm detailed craft
> workshop behind them, vibrant colours and clean confident outlines. No recognisable franchise
> character/lookalike or catching-ball accessories. Aprons are plain; no lettering or emblems.

Store the final submitted prompt and actual reference inputs. Generate up to five images per call;
retry only failed images after rate limits, never successful images from a partial batch.

## Inspect every image; block unresolved faults

Inspect **every generated/revised actual PNG** at a readable size, not just a contact sheet or its prompt.
Also inspect its final **1100×619 artwork card** at beginning and maximum zoom: a creature readable only
in the 2560×1440 source is not prominent enough. Check both faces, creature action/silhouette, actual
character design/variety, exact sentence meaning, anatomy, ordinary-device logic, scene coherence,
no text/symbols and safe framing. Inspect changed encoded item screens after rendering too.

For a user-requested all-image audit, keep sound images unchanged and fix confirmed material faults only.
Distinguish uncertainty from visible errors. A generic PASS never overrides a teacher-reported defect:
recheck the exact area, count limbs and explicitly verify device front/back orientation. A valid image
need not illustrate every incidental clause/time reference. Do not fail sound artwork merely for a
natural pose variation. Background patrons are not an extra-limb defect; counts apply to each person.
Explain and resolve conflicting findings against actual visible evidence before setting review fields.

Run `check_illustrations.py --template`. After inspection save `work/illustration_review.json` with current
PNG SHA-256 and true booleans for `human_main`, `supporting_creature`, `adorable`, `original_design`,
`distinct_from_other_images`, `sentence_context`, `no_text_or_symbols`, `safe_framing`, `human_anatomy`,
`logical_devices`, `physical_scene`, plus `unresolved_issues: []`. **`human_main` is retained for legacy
compatibility: it means a clear central human participant, not greater pixel area than the creature.**

For `unit1_costars_v1`, additionally pass `prominent_creature`, `meaning_bearing_role`,
`unit1_character_design` and `final_card_readability`; record concrete `creature_prominence_evidence`,
`creature_role_evidence` and `creature_design_evidence` from the actual image/layout. A present, cute,
original creature is insufficient if it is tiny, passive, generic or unreadable. Record planned role,
interaction and scale in items.json too. These are inspection judgements, not automatic image recognition.

For reported faults record `work/illustration_issues.json` as `{ "28": ["extra hand", "back screen"] }`;
each flagged review needs non-empty `issue_resolution_notes` describing direct verification. Record
`device_kinds` (empty only when none), `laptop_lid_check` (`pass` or `not_applicable`, never uncertain)
and `device_structure_evidence`. For laptops, explicitly describe **keyboard, hinge, lid**, camera-visible
face and why it is correctly oriented. A lid silhouette alone is not proof. Simplify/recheck uncertainty;
never set fields true from prompts alone. The hash-bound gate blocks absent/stale reviews and missing
required evidence; it does not guarantee visual correctness.

## Image-only revision preservation

Snapshot BEFORE replacement with `image_revision.py snapshot --source /absolute/previous.mp4`.
Archive an older baseline explicitly before a new revision; never replace a baseline after edits. Back up
source images and record hashes of untouched images/encoded segments for a selective revision. Preserve
all content, item order, timing, Miss K clips/voice, music and UI. Re-render only affected item segments,
refresh own reviews, show every replacement for explicit approval with `review_images.py --items <N ...>`,
bind the presented ID/PNG hashes and retain partial approvals. Set a new output version and finish with:

```bash
SOURCE_MP4=/absolute/previous.mp4 SKIP_RENDER=1 bash $S/finalize.sh
```

This copies/verifies previous encoded audio instead of rebuilding it. Verify untouched PNGs and item
segments too. Keep the previous MP4; regenerate/deliver YouTube copy (identical if content/timing are
unchanged). Do not apply discarded wording mockups or regenerate Leda during an image revision.
