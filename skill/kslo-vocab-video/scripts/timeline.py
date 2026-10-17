"""Shared timeline (video renderer + audio mixer). All times in seconds.
Layout (format v2): opening (generic intro clip) -> Part 1 card -> Part 1 items -> transition (Part 2) -> Part 2 items
-> conclusion (generic outro clip) -> outro (logo + fade to black).
Part 1 = PHRASES, Part 2 = WORDS (user rule). A unit with only one type has one part and no transition.
Encouragement pop-ups (Miss K slides in, ~4-5 s) follow every 5th item WITHIN a part, except after the last item of a
part. There are no per-item Miss K clips: during the quiz Miss K is a small badge and her answer is voice only.
Clip durations come from work/clip_speech.json (copied from the GitHub library by init_project.py).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import ROOT, R, PROJECT, proj, p, load_items

FPS = 30
ITEMS = load_items()
PHRASES = [i for i in ITEMS if i['is_phrase']]
WORDS = [i for i in ITEMS if not i['is_phrase']]
N_TOTAL = len(ITEMS)
N_PHRASES = len(PHRASES)
N_WORDS = len(WORDS)
# parts in video order: (kind, items)
PARTS = [(k, v) for k, v in (('phrases', PHRASES), ('words', WORDS)) if v]
assert [i['n'] for k, v in PARTS for i in v] == [i['n'] for i in ITEMS], \
    'items.json must list all phrases first, then words (re-run init_project.py)'

# ---- item segment constants (local to item) ----
ITEM_DUR = 8.6
CD_START = 0.6          # countdown "3" starts
CD_END = 3.6            # time is up -> reveal
WORD_AT = 3.75          # Miss K's voice says the answer (speech onset)
INFO_AT = 4.0           # meaning card + sample sentence
EXIT_AT = 8.25          # exit animation start

_cs_f = p('work', 'clip_speech.json')
CLIP_SPEECH = json.load(open(_cs_f)) if os.path.exists(_cs_f) else {}
_iv_f = p('work', 'item_voice.json')
ITEM_VOICE = {int(k): v for k, v in json.load(open(_iv_f)).items()} if os.path.exists(_iv_f) else {}


def _dur(name, default):
    return round(CLIP_SPEECH[name]['dur'], 2) if name in CLIP_SPEECH else default


# ---- special segments ----
OPEN_MK_IN = 5.4        # intro clip starts (local to opening); the centred logo + title lockup plays first
GREET_CLIP = _dur('intro', 15.04)
OPEN_DUR = OPEN_MK_IN + GREET_CLIP
PART1_DUR = 2.4
TRANS_GROW = 0.8        # Miss K slides in before her clip starts (transition / conclusion)
TRANS_CLIP = _dur('transition', 6.04)
TRANS_DUR = TRANS_GROW + TRANS_CLIP + 1.0
CONC_CLIP = _dur('outro', 12.04)
CONC_DUR = TRANS_GROW + CONC_CLIP + 1.0
OUTRO_DUR = 8.0         # ~3 s logo hold, 2 s eased fade to black, 1 s black hold (user request)
VO_LEAD = 0.5
POP_EVERY = 5
POP_TAIL = 0.3          # segment = clip + tail; Miss K slides in during the clip's 0.5 s lead, out at the end
POP_LINES = {           # generic encouragement lines (audio + clip in the library)
    'pop1': 'Great job! Keep going!',
    'pop2': "You're doing really well. Let's keep going!",
    'pop3': 'Nice work! Here come some more.',
    'pop4': "Brilliant! You're on a roll!",
    'pop5': "Keep it up! You've got this!",
    'pop6': 'Almost there! Just a few more to go!',
}


def popup_slots():
    """item numbers after which a pop-up appears"""
    out = []
    for k, its in PARTS:
        for j, it in enumerate(its):
            if (j + 1) % POP_EVERY == 0 and j + 1 < len(its):
                out.append(it['n'])
    return out


def popup_names(nslots):
    """pop1..pop5 in rotation; pop6 ('Almost there') is kept for the last pop-up of the video"""
    if nslots == 0:
        return []
    rot = ['pop1', 'pop2', 'pop3', 'pop4', 'pop5']
    names = [rot[i % len(rot)] for i in range(nslots - 1)]
    return names + ['pop6' if nslots > 1 else 'pop1']


def build():
    segs = []
    t = 0.0

    def add(kind, dur, **kw):
        nonlocal t
        segs.append(dict(kind=kind, start=round(t, 4), dur=dur, **kw))
        t += dur

    slots = popup_slots()
    names = dict(zip(slots, popup_names(len(slots))))
    add('opening', OPEN_DUR)
    for pi, (kind, its) in enumerate(PARTS):
        if pi == 0:
            add('part', PART1_DUR, part=1, ptype=kind)
        else:
            add('transition', TRANS_DUR, part=2, ptype=kind)
        for it in its:
            add('item', ITEM_DUR, item=it['n'])
            if it['n'] in names:
                nm = names[it['n']]
                add('popup', round(_dur(nm, 4.04) + POP_TAIL, 2), pop=nm, n_done=it['n'])
    add('conclusion', CONC_DUR)
    add('outro', OUTRO_DUR)
    for i, s in enumerate(segs):
        s['idx'] = i
        s['f0'] = int(round(s['start'] * FPS))
        s['nf'] = int(round((s['start'] + s['dur']) * FPS)) - s['f0']
    return segs, t


SEGMENTS, TOTAL = build()
N_PART1 = len(PARTS[0][1])


def mk_schedule():
    """Miss K clip schedule (global seconds); the idle clip (sine ping-pong) fills every gap"""
    out = []
    for s in SEGMENTS:
        if s['kind'] == 'opening':
            out.append(dict(name='intro', start=s['start'] + OPEN_MK_IN, dur=GREET_CLIP))
        elif s['kind'] == 'popup':
            out.append(dict(name=s['pop'], start=s['start'], dur=_dur(s['pop'], 4.04)))
        elif s['kind'] == 'transition':
            out.append(dict(name='transition', start=s['start'] + TRANS_GROW, dur=TRANS_CLIP))
        elif s['kind'] == 'conclusion':
            out.append(dict(name='outro', start=s['start'] + TRANS_GROW, dur=CONC_CLIP))
    for a, b in zip(out, out[1:]):
        assert a['start'] + a['dur'] <= b['start'] + 1e-6, ('Miss K clips overlap', a, b)
    return out


MK_SCHED = mk_schedule()


def seg_by_key():
    d = {}
    for s in SEGMENTS:
        k = s['kind'] + (str(s['item']) if s['kind'] == 'item' else str(s['idx']) if s['kind'] == 'popup' else '')
        d[k] = s
    return d


if __name__ == '__main__':
    for s in SEGMENTS:
        print(s['idx'], s['kind'], s.get('item', s.get('pop', s.get('ptype', ''))), s['start'], s['dur'], s['f0'], s['nf'])
    print('TOTAL %.2f s (%.2f min)' % (TOTAL, TOTAL / 60))
    print('parts:', [(k, len(v)) for k, v in PARTS], ' pop-ups after items:', popup_slots())
    missing = [it['n'] for it in ITEMS if it['n'] not in ITEM_VOICE]
    if missing:
        print('items without a prepared voice (run prep_items.py):', missing)
