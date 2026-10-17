#!/usr/bin/env python3
"""Words with distinct British and American pronunciations (rule V9).

Miss K keeps her normal voice (Leda, en-GB). Only these words must be said the British way.
  python3 british_words.py            list the project's items that contain such a word
  python3 british_words.py --preview  after recording: join the chosen takes of those items into
                                      output/british_check.mp3 (with a spoken-order list) for the user to approve
The list is not exhaustive: also flag any other item word that you know has a distinct British pronunciation.
"""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# word stem (regex, matched at word start) -> (British pronunciation, respelling to TRY in the TTS text if a take
# sounds American; always confirm by ear with the user)
BRITISH = {
    r'privac':        ('PRIV-uh-see (short i as in "give")', 'privvacy'),
    r'anti(?!c|que)': ('AN-tee (not AN-tie)', 'antee'),           # antisocial, antibiotic, anti-ageing
    r'multi':         ('MUL-tee (not MUL-tie)', 'multee'),
    r'semi':          ('SEM-ee (not SEM-eye)', 'semmee'),
    r'schedul':       ('SHED-yool', 'shedule'),
    r'vitamin':       ('VIT-uh-min (short i)', 'vittamin'),
    r'garage':        ('GA-rahzh / GA-rij (stress on GA)', 'garraj'),
    r'advertisement': ('ad-VER-tis-ment', 'ad-vertissment'),
    r'laborator':     ('luh-BOR-uh-tree', 'laborratry'),
    r'leisure':       ('LEZH-uh (rhymes with "measure")', 'lezher'),
    r'route':         ('ROOT', 'root'),
    r'either':        ('EYE-thuh', 'eyether'),
    r'neither':       ('NYE-thuh', 'nyether'),
    r'tomato':        ('tuh-MAH-toh', 'tomahto'),
    r'controversy':    ('KON-truh-ver-see (stress on KON)', 'KON-troversy'),
    r'alumini?um':    ('al-yuh-MIN-ee-um', 'aluminium'),
    r'yog(h)?(o)?urt':('YOG-urt (short o)', 'yoggurt'),
    r'(mobile|fragile|hostile|futile|fertile|versatile|sterile|missile|docile|juvenile)':
                      ('ends in "-ile" as in "aisle" (MO-bile, FRA-jile)', 'mo-bile / fra-jile'),
    r'herb':          ('with the "h" (HERB)', 'herb'),
    r'data':          ('DAY-tuh', 'dayta'),
    r'process':       ('PROH-ses (long o)', 'proh-sess'),
    r'progress':      ('PROH-gres (noun, long o)', 'proh-gress'),
    r'dynast':        ('DIN-uh-stee (short i)', 'dinnasty'),
    r'patriot':       ('PAT-ree-ut (short a)', 'pattriot'),
    r'clerk':         ('CLARK', 'clark'),
    r'niche':         ('NEESH', 'neesh'),
    r'premier':       ('PREM-ee-uh', 'premmier'),
    r'lieutenant':    ('lef-TEN-ant', 'leftenant'),
    r'adult':         ('AD-ult (stress on AD)', 'AD-ult'),
    r'address':       ('uh-DRESS (stress on DRESS)', 'a-DRESS'),
    r'ballet':        ('BAL-ay (stress on BAL)', 'BAL-ay'),
    r'buffet':        ('BOO-fay (meal)', 'boofay'),
    r'debris':        ('DEB-ree', 'debbree'),
    r'(cigarette|magazine)': ('stress on the last syllable', 'cigarETTE / magaZINE'),
    r'vase':          ('VAHZ', 'vahz'),
    r'basil':         ('BAZ-ul (short a)', 'bazzle'),
    r'oregano':       ('o-ri-GAH-no', 'orri-gahno'),
    r'(can\'t|bath|staff|grass|class|dance|chance|advantage|example|answer|after|half|plant)':
                      ('long "ah" vowel (BAHTH, CAHNT)', ''),
}


def flagged(items):
    out = []
    for it in items:
        hits = []
        for w in re.findall(r"[A-Za-z']+", it['display']):
            for rx, (brit, resp) in BRITISH.items():
                if re.match(rx + r"[a-z']*$", w.lower()):
                    hits.append((w, brit, resp))
                    break
        if hits:
            out.append((it, hits))
    return out


if __name__ == '__main__':
    from config import p, proj, load_items
    items = load_items()
    fl = flagged(items)
    if not fl:
        print('no items with a distinct British pronunciation in the list (check by knowledge too)')
    for it, hits in fl:
        print(f"#{it['n']} {it['display']}: " + '; '.join(f'{w} -> {b}' + (f' (try respelling "{r}")' if r else '')
                                                    for w, b, r in hits))
    if '--preview' in sys.argv and fl:
        takes = proj('item_takes', {}) or {}
        files = []
        for it, _ in fl:
            t = takes.get(str(it['n']), f"{it['n']:02d}")
            f = p('audio', 'items_raw', f'{t}.wav')
            if os.path.exists(f):
                files.append(f)
            else:
                print('missing take', f)
        if files:
            out = p('output', 'british_check.mp3')
            os.makedirs(os.path.dirname(out), exist_ok=True)
            inp, fc = [], ''
            for k, f in enumerate(files):
                inp += ['-i', f]
                fc += f'[{k}:a]aresample=48000,aformat=channel_layouts=mono,apad=pad_dur=0.8[a{k}];'
            fc += ''.join(f'[a{k}]' for k in range(len(files))) + f'concat=n={len(files)}:v=0:a=1[o]'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', *inp, '-filter_complex', fc, '-map', '[o]',
                            '-c:a', 'libmp3lame', '-q:a', '2', out], check=True)
            print('wrote', out, '- items in this order:', ', '.join(it['display'] for it, _ in fl))
