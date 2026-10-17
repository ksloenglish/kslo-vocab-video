#!/usr/bin/env python3
"""Write output/youtube.md: a YouTube title and description for the project's video.

Rules (user): never mention AI, Manus, "generated" or how the video was made; address K S Lo students;
keep the K S Lo English branding. YouTube chapters must start at 0:00, be >= 3 and each >= 10 s, so items
(8.6 s) are listed WITHOUT timestamps - only Welcome / Part 1 / Part 2 / Wrap-up are chapters.
Review the text, then paste it into YouTube Studio.

usage: python3 youtube_text.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timeline import SEGMENTS, ITEMS, PARTS, TOTAL
from config import p, proj


def ts(t):
    t = int(t)
    return f'{t // 60}:{t % 60:02d}'


lvl, unit = proj('level', 'S2'), proj('unit', '')
title = f'{proj("title")} | Vocabulary Revision with Miss K | K S Lo English'
seg = {s['kind']: s for s in SEGMENTS if s['kind'] != 'item'}
chapters = [(0, 'Welcome'), (seg['part']['start'], f'Part 1: {PARTS[0][0].title()}')]
if 'transition' in seg:
    chapters.append((seg['transition']['start'], f'Part 2: {PARTS[1][0].title()}'))
chapters.append((seg['conclusion']['start'], 'Wrap-up'))
lists = '\n'.join(f"{k.title()} ({len(its)})\n" + ', '.join(i['headword'] for i in its) for k, its in PARTS)

desc = f"""Revise the useful words and phrases from {lvl} Unit {unit} with Miss K, your virtual English tutor!

Look at each picture, use the first letters to guess the word or phrase, and say it aloud before the 3-second countdown ends. Then check your answer: Miss K says it for you, and you'll see its part of speech, Chinese meaning, definition and an example sentence.

Made for {lvl} students of HKMA K S Lo College. Great for quick revision before a dictation, quiz or test.

Chapters
""" + '\n'.join(f'{ts(t)} {n}' for t, n in chapters) + f"""

""" + lists.replace('\n' + PARTS[-1][0].title(), '\n\n' + PARTS[-1][0].title()) + f"""

How to revise with this video
1. Say each answer aloud before the countdown ends.
2. Pause the video if you need more time.
3. Watch again and see how many more you can get right.
4. Use each word or phrase in a sentence of your own.

Keep up the great work, K S Lo students!

#KSLoEnglish #{lvl}English #EnglishVocabulary #VocabularyRevision #LearnEnglish
"""
banned = ['ai ', 'a.i.', 'artificial', 'manus', 'generated', 'machine']
low = (title + ' ' + desc).lower()
assert not any(b in low for b in banned), 'banned wording in YouTube text'
os.makedirs(p('output'), exist_ok=True)
out = p('output', 'youtube.md')
open(out, 'w').write(f'# YouTube title\n\n{title}\n\n# YouTube description\n\n```\n{desc}```\n')
print(open(out).read())
print('title length', len(title), '(YouTube max 100); video length', ts(TOTAL))
