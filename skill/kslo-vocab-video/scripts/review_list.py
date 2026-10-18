#!/usr/bin/env python3
"""Write output/review_list.md before item recording (W5).

Show visual wording separately from spoken display; answer_display may contain
silent ellipses. Keep punctuation literal in the main first-letter blanks.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import p, proj, load_items
from render import clue_sentence


def tts_text(it):
    return it['display'][0].upper() + it['display'][1:] + '.'


def visual_blanks(it):
    visual = it.get('answer_display', it['display'])
    return '   '.join(word if len(word) == 1 or not any(ch.isalpha() for ch in word)
                      else word[0] + ' ' + ' '.join('_' for _ in word[1:])
                      for word in visual.split())


items = load_items()
rows, warn = [], []
for it in items:
    kind = 'phrase' if len(it['display'].split()) > 1 else 'word'
    visual = it.get('answer_display', it['display'])
    clue, spans = clue_sentence(it['sentence'], it['highlight'], it['display'])
    if not spans:
        warn.append(f"#{it['n']} {it['display']}: no highlight found in the sentence. Fix items.json 'highlight'.")
    esc = lambda x: x.replace('_', '\\_')
    rows.append(f"| {it['n']} | {kind} | {it['headword']} | **{visual}** | **{it['display']}** | `{tts_text(it)}` | {esc(visual_blanks(it))} | {esc(clue)} |")

out = p('output', 'review_list.md')
os.makedirs(os.path.dirname(out), exist_ok=True)
txt = (f"# {proj('title')}: items for approval before recording\n\n"
       "Miss K says each item once, with a falling tone. Visual ellipses are silent; check visual wording separately from speech.\n\n"
       "| # | Type | Headword (DOCX) | On-screen answer | Miss K says | TTS text | Blanks | Clue sentence (thinking screen) |\n"
       "|---|---|---|---|---|---|---|---|\n" + '\n'.join(rows) + '\n')
if warn:
    txt += '\n## To fix before approval\n\n' + '\n'.join('- ' + w for w in warn) + '\n'
with open(out, 'w') as handle:
    handle.write(txt)
print(txt)
print('wrote', out)
