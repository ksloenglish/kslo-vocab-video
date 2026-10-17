#!/usr/bin/env python3
"""Write output/review_list.md: the list the user approves BEFORE any item audio is generated (rule W5).

For every item, in video order (phrases first, then words), it shows:
  - what Miss K will say (the display form), and the exact text sent to generate_speech ("Based on.")
  - the on-screen blanks ("b_____ o_____") and the clue sentence with the item blanked (rule P8)
Show the table to the user with `ask` (blocking) and wait for approval or corrections. Do not call generate_speech
for items until the user approves; apply corrections to items.json (display / highlight) and re-run this script.

usage: python3 review_list.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import p, proj, load_items
from render import clue_sentence, blank_words


def tts_text(it):
    return it['display'][0].upper() + it['display'][1:] + '.'


items = load_items()
rows, warn = [], []
for it in items:
    kind = 'phrase' if len(it['display'].split()) > 1 else 'word'
    clue, spans = clue_sentence(it['sentence'], it['highlight'])
    if not spans:
        warn.append(f"#{it['n']} {it['display']}: no highlight found in the sentence, so the clue has no blank. Fix items.json 'highlight'.")
    esc = lambda x: x.replace('_', '\\_')          # keep underscores literal in Markdown
    rows.append(f"| {it['n']} | {kind} | {it['headword']} | **{it['display']}** | `{tts_text(it)}` | {esc(blank_words(it['display']))} | {esc(clue)} |")

out = p('output', 'review_list.md')
os.makedirs(os.path.dirname(out), exist_ok=True)
txt = (f"# {proj('title')}: items for approval before recording\n\n"
       "Miss K says each item once, with a falling tone. Please check the wording and the clue sentences.\n\n"
       "| # | Type | Headword (DOCX) | Miss K says | TTS text | Blanks | Clue sentence (thinking screen) |\n"
       "|---|---|---|---|---|---|---|\n" + '\n'.join(rows) + '\n')
if warn:
    txt += '\n## To fix before approval\n\n' + '\n'.join('- ' + w for w in warn) + '\n'
open(out, 'w').write(txt)
print(txt)
print('wrote', out)
