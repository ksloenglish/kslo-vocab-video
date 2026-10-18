# Teacher review of all generated images — required before assembly

The teacher explicitly requested this on **19 October 2026**. **Three-pilot/style approval is not full-image-set approval.** It authorises generating the rest of the images only. After generation and the agent's own inspection, let the teacher review **every actual generated image**, then wait for explicit approval before the full production render/final video assembly.

## Prepare the complete review

1. Complete all generated/revised PNGs and the own-image QA in `illustration_style.md`: exact meaning, coherent faces/beaks, all intended limbs, water/clothing logic, device orientation, actual identity/scene variety, no text/symbols and source/start/maxzoom framing.
2. Run `python3 $S/review_images.py`. It lists all items in actual video order, creates readable paginated source contact sheets and writes **`output/illustration_review.md`** with individual full-resolution PNG links. Do not submit only tiny thumbnails or omit the three pilots. For a selective revision, use `--items <all regenerated item numbers>`; untouched accepted legacy artwork need not be reviewed again.
3. Link the complete review and relevant contact sheets in a **blocking `ask`**, clearly stating the total images and asking **“Approve all images”** or **“Request changes”**. The individual PNG links allow close inspection of beaks, limbs and clothing. Keep preview layout/card views available for meaningful crops. A contact sheet is an overview, not evidence that each image is sound.
4. Wait for the teacher's actual reply. Do not infer full-set approval from pilot approval, approval of the speaking list, elapsed time, silence, a generic visual PASS or the existence of a finished older MP4. One batch approval covers the presented set; do not demand30 separate dialogs.

## Record and bind the approval

`review_images.py` records a pending review ID tied to the ordered numbers/current PNG SHA-256. **Only after an explicit teacher reply**, record it using:

```bash
python3 $S/review_images.py --approve --review-id <presented-ID> --note "<teacher's explicit approval>"
```

For partial approval, pass `--items <approved subset>` with the same presented ID. Preserve exact approved hashes and identify the rejected/unapproved items. Fix/regenerate **only** those items, rerun their review gallery and ask again. Never silently change accepted images while replacing one rejected character.

If the actual PNG changes after presentation/approval, its approval is stale. Regenerate a preview and obtain fresh approval. Do not generate a new hash and label it approved using a reply to an older image. Keep the note, review ID and per-image approval hashes in `work/image_approval.json` and record the decision in project `NOTES.md`.

## Assembly guard and scope

```bash
python3 $S/review_images.py --check
```

Normal full finalization checks that **all current images** are approved and hash-current before rendering/muxing. Image-only finalization checks the changed/generated image numbers against its pre-edit snapshot, preserving accepted untouched legacy images. Missing, pending, wrong-ID or stale approvals block assembly; own-image QA remains a separate required gate.

New image-revision snapshots include source PNG hashes. Older baselines lacking `image_files` are
rejected safely: establish the updated snapshot **before edits**, or restore the genuine pre-edit
state from its archive first. Never backfill the baseline from already changed images to evade the gate.

Approved audio preparation and generic reusable-library work may continue independently after the speaking-list gate. Do not spend on new video generation or silently assemble the final video while the image review is pending. For an audio-only repair with **no generated/changed images**, keep the old accepted artwork and use the selective audio baseline workflow; do not ask to review unchanged images again.

The script validates records/hashes; it **cannot authenticate a conversational reply**. The agent must call `--approve` only when the current conversation explicitly authorises the actual presented images. This update is prospective and does not authorise rebuilding previously delivered units.
