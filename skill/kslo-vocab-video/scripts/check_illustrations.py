#!/usr/bin/env python3
"""Fail finalization unless every current illustration has a fresh visual review.

usage: VOCAB_PROJECT=/path python3 check_illustrations.py
       ... --template  # write work/illustration_review_template.json for inspection

This is a manifest/hash gate, NOT automated visual recognition. Populate review fields
only after viewing each actual image and its final-size card, never from prompts alone.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
from PIL import Image

# Retain human_main for compatibility: central human participant, NOT pixel dominance.
CHECKS = ('human_main', 'supporting_creature', 'adorable', 'original_design', 'distinct_from_other_images',
          'sentence_context', 'no_text_or_symbols', 'safe_framing',
          'human_anatomy', 'logical_devices', 'physical_scene')
COSTAR_POLICY = 'unit1_costars_v1'
COSTAR_CHECKS = ('prominent_creature', 'meaning_bearing_role',
                 'unit1_character_design', 'final_card_readability')
COSTAR_EVIDENCE = ('creature_prominence_evidence', 'creature_role_evidence', 'creature_design_evidence')
COSTAR_PLANS = ('creature_role', 'human_creature_interaction', 'creature_scale_plan')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nonempty_text(value):
    return isinstance(value, str) and bool(value.strip())


def policy_for(item, project_policy):
    policy = item.get('illustration_policy', project_policy)
    if policy not in (None, '', COSTAR_POLICY):
        raise ValueError(f"#{item['n']}: unknown illustration_policy {policy!r}")
    if project_policy == COSTAR_POLICY and policy != COSTAR_POLICY:
        raise ValueError(f"#{item['n']}: cannot downgrade the new project's co-star policy")
    return policy


def check(project, review_path=None):
    root = Path(project)
    items = json.loads((root / 'items.json').read_text())
    config_path = root / 'project.json'
    config = json.loads(config_path.read_text()) if config_path.exists() else {}
    project_policy = config.get('illustration_policy')
    if project_policy not in (None, '', COSTAR_POLICY):
        raise ValueError(f'Unknown project illustration_policy {project_policy!r}')
    review_path = Path(review_path) if review_path else root / 'work/illustration_review.json'
    if not review_path.exists():
        raise ValueError('Missing work/illustration_review.json. Inspect all actual images, fill the template, then re-run.')
    review = json.loads(review_path.read_text())
    issues_file = root / 'work/illustration_issues.json'
    issues = json.loads(issues_file.read_text()) if issues_file.exists() else {}
    signatures = set()
    families = set()
    for item in items:
        n = str(item['n'])
        policy = policy_for(item, project_policy)
        file = root / 'illus' / f"{item['n']:02d}_{item['slug']}.png"
        if not file.exists():
            raise ValueError(f'#{n}: missing illustration {file}')
        with Image.open(file) as im:
            im.load()
            if im.width * 9 != im.height * 16:
                raise ValueError(f'#{n}: must be video 16:9, not a 4:5 card')
            if im.width < 1920 or im.height < 1080:
                raise ValueError(f'#{n}: needs at least 1920x1080 artwork')
        entry = review.get(n, {})
        if entry.get('sha256') != sha(file):
            raise ValueError(f'#{n}: missing or stale review; inspect the current image, not an earlier one')
        required = CHECKS + (COSTAR_CHECKS if policy == COSTAR_POLICY else ())
        failed = [field for field in required if entry.get(field) is not True]
        if failed:
            raise ValueError(f'#{n}: review has not passed: {", ".join(failed)}')
        if policy == COSTAR_POLICY:
            for field in COSTAR_EVIDENCE:
                if not nonempty_text(entry.get(field)):
                    raise ValueError(f'#{n}: missing actual co-star evidence: {field}; presence/cuteness alone is insufficient')
            for field in COSTAR_PLANS:
                if not nonempty_text(item.get(field)):
                    raise ValueError(f'#{n}: missing co-star story plan: {field}')
            refs = item.get('style_reference_files')
            if not isinstance(refs, list) or not refs or any(not nonempty_text(ref) for ref in refs):
                raise ValueError(f'#{n}: record actual viewed/used style_reference_files or Unit 1 video timestamp references')
        if entry.get('unresolved_issues') != []:
            raise ValueError(f'#{n}: unresolved issues or missing explicit unresolved_issues review')
        if issues.get(n) and not str(entry.get('issue_resolution_notes', '')).strip():
            raise ValueError(f'#{n}: verify teacher-reported faults and record issue_resolution_notes; a generic PASS is insufficient')
        kinds = entry.get('device_kinds')
        if not isinstance(kinds, list) or any(not isinstance(kind, str) for kind in kinds):
            raise ValueError(f'#{n}: record device_kinds after inspecting the actual image')
        lid_check = entry.get('laptop_lid_check')
        if lid_check not in ('pass', 'not_applicable'):
            raise ValueError(f'#{n}: laptop lid check missing, failed or uncertain; recheck keyboard/hinge/lid geometry')
        has_laptop = any('laptop' in kind.lower() for kind in kinds)
        if has_laptop and lid_check != 'pass':
            raise ValueError(f'#{n}: laptop present but its lid face has not explicitly passed')
        evidence = str(entry.get('device_structure_evidence', '')).strip().lower()
        if not evidence:
            raise ValueError(f'#{n}: missing actual device-structure evidence; a generic PASS is insufficient')
        if has_laptop and not all(word in evidence for word in ('keyboard', 'hinge', 'lid')):
            raise ValueError(f'#{n}: describe keyboard, hinge and camera-visible lid face before approving the laptop')
        signature = item.get('creature_signature', '').strip().casefold()
        family = item.get('creature_family', '').strip().casefold()
        if not signature or not family:
            raise ValueError(f'#{n}: record creature_signature and creature_family; creatures are mandatory')
        if signature in signatures:
            raise ValueError(f'#{n}: repeated creature design; recolours/accessory swaps are not enough')
        if family in families:
            raise ValueError(f'#{n}: repeated creature_family; allocate visibly different species/silhouettes')
        signatures.add(signature)
        families.add(family)
        prompt = item.get('image_prompt', '').lower()
        for anchor in ('human', 'original'):
            if anchor not in prompt:
                raise ValueError(f'#{n}: prompt must explicitly preserve {anchor} role/design')
        # Explicit co-star interaction/role metadata is equivalent supporting
        # language; do not rewrite the stored submitted prompt just to add a token.
        if 'support' not in prompt and not (
                'co-star' in prompt and all(nonempty_text(item.get(field)) for field in COSTAR_PLANS)):
            raise ValueError(f'#{n}: prompt/plan must explicitly preserve the supporting meaning-bearing role')
        if policy == COSTAR_POLICY and 'co-star' not in prompt:
            raise ValueError(f'#{n}: prompt must explicitly stage the creature as a co-star, not append a passive pet')
    return len(items)


def template(project):
    root = Path(project)
    items = json.loads((root / 'items.json').read_text())
    data = {}
    for item in items:
        file = root / 'illus' / f"{item['n']:02d}_{item['slug']}.png"
        data[str(item['n'])] = dict(sha256=sha(file) if file.exists() else '',
                                    **{field: False for field in CHECKS + COSTAR_CHECKS},
                                    **{field: '' for field in COSTAR_EVIDENCE},
                                    unresolved_issues=['Not inspected yet'], issue_resolution_notes='',
                                    device_kinds=[], laptop_lid_check='not_reviewed', device_structure_evidence='')
    out = root / 'work/illustration_review_template.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, indent=2) + '\n')
    print(f'Wrote {out}; inspect each actual image AND final-size card before marking checks true. Save as illustration_review.json.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', default=os.environ.get('VOCAB_PROJECT'))
    parser.add_argument('--review')
    parser.add_argument('--template', action='store_true')
    args = parser.parse_args()
    if not args.project:
        parser.error('Set VOCAB_PROJECT or pass --project')
    try:
        if args.template:
            template(args.project)
        else:
            count = check(args.project, args.review)
            print(f'Illustration gate PASS: {count} fresh reviews; central humans, distinct original creatures and applicable co-star checks.')
    except (ValueError, OSError, KeyError) as error:
        print(f'Illustration gate FAILED: {error}', file=sys.stderr)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
