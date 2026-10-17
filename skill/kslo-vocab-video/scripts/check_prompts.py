#!/usr/bin/env python3
"""Check every items.json image_prompt BEFORE calling generate_image (rule S2).

Each prompt must:
  - start with the no-text preamble from references/visual_spec.md
  - include at least one ORIGINAL pocket-monster-style companion creature in the Scene (the word "creature")
  - include the style line (anime + pocket-monster wording)
  - not name any franchise or franchise character
Exit code 1 if any prompt fails. Fix the prompts and re-run.

usage: python3 check_prompts.py
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import load_items

BANNED = ['pokemon', 'pokémon', 'pikachu', 'eevee', 'bulbasaur', 'charmander', 'squirtle', 'jigglypuff', 'snorlax',
          'digimon', 'yo-kai', 'yokai watch', 'ghibli', 'totoro', 'sanrio', 'hello kitty', 'disney', 'nintendo']
bad = 0
for it in load_items():
    pr = it.get('image_prompt', '')
    low = pr.lower()
    probs = []
    if not pr:
        probs.append('no prompt')
    else:
        if not low.startswith('pure illustration only'):
            probs.append('missing the no-text preamble')
        scene = low.split('scene:', 1)[1] if 'scene:' in low else ''
        if not re.search(r'creature', scene.split('vibrant japanese anime')[0]):
            probs.append('the Scene has no companion creature (every image needs one, taking part in the action)')
        if 'pocket-monster' not in low or 'anime' not in low:
            probs.append('missing the style line (anime + original pocket-monster-style creatures)')
        hit = [b for b in BANNED if b in low]
        if hit:
            probs.append('names a franchise: ' + ', '.join(hit))
    if probs:
        bad += 1
        print(f"#{it['n']} {it['display']}: " + '; '.join(probs))
print(f'{len(load_items()) - bad} OK, {bad} to fix')
sys.exit(1 if bad else 0)
