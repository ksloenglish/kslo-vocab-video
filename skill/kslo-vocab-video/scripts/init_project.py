#!/usr/bin/env python3
"""Create a new vocab-video project and build items.json from a word list.

usage:
  python3 init_project.py <project_dir> --docx <file.docx> --unit 2 [--level S2]
  python3 init_project.py <project_dir> --csv <file.csv> --unit 2      (columns: headword,pos,definition,zh,sentence)
  add --title "S3 Unit 4 Useful Words and Phrases" to use the teacher's exact video title (default: "<level> Unit <unit>
  Useful Words and Phrases"). Levels other than S2 have no DOCX: ask the teacher for the item list AND the title.

What it does
  1. creates the fixed folder layout and copies brand / Miss K / audio templates from the skill
  2. reads the unit's table IN TABLE ORDER and applies the display rules (see references/presentation_rules.md)
  3. writes items.json + project.json and prints every item, plus an ASK list of cases that need the user's decision
Re-running never overwrites an existing items.json / project.json unless --force is given.
"""
import argparse, csv, json, os, re, shutil, sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(SKILL, 'templates')

POS_SHORT = {'verb': 'v', 'noun': 'n', 'adjective': 'adj', 'adverb': 'adv', 'phrase': 'phr', 'prep': 'prep',
             'preposition': 'prep', 'conjunction': 'conj', 'pronoun': 'pron', 'determiner': 'det',
             'v': 'v', 'n': 'n', 'adj': 'adj', 'adv': 'adv', 'phr': 'phr'}
PLACEHOLDER = r"(sth|sb|sb's|sth's|one's|someone|something|A|B|v-ing|V-ing)"
TRAIL = re.compile(r"(\s+(do\s+sth|sb/sth|sth/sb|sth|sb))+$")


def read_docx(path, unit):
    import docx
    d = docx.Document(path)
    body = d.element.body
    cur, tables = None, {}
    for el in body.iterchildren():
        tag = el.tag.split('}')[-1]
        if tag == 'p':
            txt = ''.join(n.text or '' for n in el.iter() if n.tag.endswith('}t')).strip()
            m = re.match(r'^Unit\s+(\d+)\b', txt)
            if m:
                cur = m.group(1)
        elif tag == 'tbl' and cur is not None and cur not in tables:
            tables[cur] = el
    if str(unit) not in tables:
        sys.exit(f'Unit {unit} not found; units in file: {sorted(tables)}')
    tbl = docx.table.Table(tables[str(unit)], d)
    rows = [[c.text.strip() for c in r.cells] for r in tbl.rows]
    hdr = [h.lower() for h in rows[0]]
    return [dict(headword=r[0], pos=r[1], definition=r[2], zh=r[3], sentence=r[4]) for r in rows[1:] if r[0]], hdr


def read_csv(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        return [dict(headword=r['headword'].strip(), pos=r['pos'].strip(), definition=r['definition'].strip(),
                     zh=r['zh'].strip(), sentence=r['sentence'].strip()) for r in csv.DictReader(f)], None


def pos_short(pos):
    m = re.search(r'\(([a-z]+)\.?\)', pos.lower())
    key = m.group(1) if m else pos.lower().split()[0].rstrip('.') if pos.strip() else ''
    return POS_SHORT.get(key)


BE = r"(?:be|is|are|was|were|been|being|am|'s|'re|'m)"


def word_rx(w):
    if w.lower() == 'be':
        return BE
    if w.lower() in ('my', 'your', 'his', 'her', 'their', 'our', 'its', "one's"):
        return r"(?:my|your|his|her|their|our|its|one's)"
    if len(w) <= 2:
        return re.escape(w)
    stem = re.escape(w[:-1]) if w.endswith('e') else re.escape(w)
    return stem + r"[a-z]{0,4}"           # inflections: -s -es -ed -d -ing -ied ...


def guess_highlight(display, sentence):
    """Return (substring_of_sentence or None, exact?)"""
    i = sentence.lower().find(display.lower())
    if i >= 0:
        j = i + len(display)
        while j < len(sentence) and sentence[j].isalpha():   # 'feature' in 'features' -> whole word
            j += 1
        return sentence[i:j], j == i + len(display)
    words = [w for w in display.split() if w.lower() != 'a']
    rx = r'\b' + r'\s+'.join(word_rx(w) for w in words) + r'\b'
    m = re.search(rx, sentence, flags=re.I)
    return (m.group(0), False) if m else (None, False)


def display_form(head):
    """Apply the confirmed rules; return (display, asks[])"""
    asks = []
    disp = TRAIL.sub('', head).strip()
    if disp != head:
        pass                                   # trailing sth / sb / sb/sth / do sth stripped (confirmed rule)
    toks = disp.split()
    if any(re.fullmatch(PLACEHOLDER, t) for t in toks) or re.search(r"\b(sb|sth)'s\b", disp):
        asks.append('placeholder (sb/sth/A/B/v-ing/one\'s) inside the phrase: how should it be shown and said?')
    if any('-' in t for t in toks):
        asks.append('hyphenated word: show blanks for each part (t _ _ - t _ _) or treat as one word?')
    if re.search(r"[()/\[\]]", disp):
        asks.append('brackets or slash in the headword: which form should be shown and said?')
    if any("'" in t for t in toks) and not asks:
        asks.append('apostrophe in the headword: confirm the display form.')
    return disp, asks


def blanks_text(display):
    """Text form for review only; the renderer draws the bars itself (first letter + one bar per missing letter)."""
    out = []
    for w in display.split():
        out.append(w if len(w) == 1 else w[0] + ' ' + ' '.join('_' * 1 for _ in w[1:]))
    return '   '.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project'); ap.add_argument('--docx'); ap.add_argument('--csv')
    ap.add_argument('--unit', required=True); ap.add_argument('--level', default='S2')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--title', help="the teacher's exact video title")
    a = ap.parse_args()
    P = os.path.abspath(a.project)
    for d in ('assets/fonts', 'illus', 'audio/vo', 'audio/items_raw', 'audio/items', 'audio/refs', 'audio/aligned',
              'clips/keyed', 'work/ca', 'work/segs', 'work/test', 'output'):
        os.makedirs(os.path.join(P, d), exist_ok=True)
    # missk_neutral.webp is lossless; expanded to the PNG the pipeline uses (badge, any new Seedance keyframe).
    from PIL import Image
    d = os.path.join(P, 'assets/missk_neutral.png')
    if not os.path.exists(d):
        Image.open(os.path.join(T, 'missk/missk_neutral.webp')).convert('RGB').save(d)
    cp = [('brand/logo_white.png', 'assets/logo_white.png')]
    cp += [(f'audio/{f}', f'audio/{f}') for f in os.listdir(os.path.join(T, 'audio'))]
    cp += [(f'fonts/{f}', f'assets/fonts/{f}') for f in os.listdir(os.path.join(T, 'fonts'))]
    for s, d in cp:
        if not os.path.exists(os.path.join(P, d)):
            shutil.copy2(os.path.join(T, s), os.path.join(P, d))
    # reusable Miss K library (clips + lip-aligned voice) lives in the ksloenglish GitHub repo, not in the skill
    L = os.path.expanduser(os.environ.get('KSLO_ASSETS', '~/kslo-vocab-video')) + '/library'
    if not os.path.exists(os.path.join(L, 'library.json')):
        sys.exit(f'Miss K library not found at {L}.\nRun: bash {os.path.dirname(os.path.abspath(__file__))}/fetch_assets.sh')
    lib = json.load(open(os.path.join(L, 'library.json')))
    for nm in lib['clips']:
        for s_, d_ in ((f'clips/missk_{nm}.mp4', f'clips/missk_{nm}.mp4'), (f'aligned/{nm}.wav', f'audio/aligned/{nm}.wav')):
            if os.path.exists(os.path.join(L, s_)) and not os.path.exists(os.path.join(P, d_)):
                shutil.copy2(os.path.join(L, s_), os.path.join(P, d_))
    json.dump({nm: dict(dur=v['dur']) for nm, v in lib['clips'].items()}, open(os.path.join(P, 'work', 'clip_speech.json'), 'w'), indent=1)
    shutil.copy2(os.path.join(L, 'library.json'), os.path.join(P, 'work', 'library.json'))
    if os.path.exists(os.path.join(L, 'stab.json')) and not os.path.exists(os.path.join(P, 'clips/keyed/stab.json')):
        shutil.copy2(os.path.join(L, 'stab.json'), os.path.join(P, 'clips/keyed/stab.json'))

    rows, _ = read_docx(a.docx, a.unit) if a.docx else read_csv(a.csv)
    items, asks, checks = [], [], []
    # VIDEO ORDER (user rule): all phrases first, then all words; table order kept within each group
    rows = [r for r in rows if len(display_form(r['headword'])[0].split()) > 1] + \
           [r for r in rows if len(display_form(r['headword'])[0].split()) <= 1]
    for i, r in enumerate(rows):
        n = i + 1
        disp, ak = display_form(r['headword'])
        is_phrase = len(disp.split()) > 1
        ps = pos_short(r['pos'])
        if ps is None:
            ak.append(f'unknown part of speech "{r["pos"]}": which short label?')
        if ('phr' == ps) != is_phrase and ps is not None:
            ak.append(f'POS "{r["pos"]}" vs {"multi" if is_phrase else "single"}-word display: "What\'s the word?" or "What\'s the phrase?"')
        hl, exact = guess_highlight(disp, r['sentence'])
        if not exact:
            checks.append(f'#{n} {disp}: highlight guess = {hl!r} (inflected/changed in sentence) - verify')
        for q in ak:
            asks.append(f'#{n} "{r["headword"]}": {q}')
        items.append(dict(n=n, headword=r['headword'], display=disp, is_phrase=is_phrase,
                          question="What's the phrase?" if is_phrase else "What's the word?",
                          blanks=blanks_text(disp), pos=r['pos'], pos_short=ps or '?', definition=r['definition'],
                          zh=r['zh'], sentence=r['sentence'], highlight=[hl] if hl else [],
                          slug=re.sub(r'[^a-z]+', '_', disp.lower()).strip('_'), image_prompt='',
                          creature_family='', creature_signature='', creature_role='',
                          human_creature_interaction='', creature_scale_plan='', style_reference_files=[], ask=ak))
    kinds = ''.join('P' if it['is_phrase'] else 'W' for it in items)
    nw = kinds.count('W')
    title = (a.title or f'{a.level} Unit {a.unit} Useful Words and Phrases').strip()
    m = re.match(rf'^({re.escape(a.level)}\s+Unit\s+\S+)\s+(.+)$', title, flags=re.I)
    header = f'{m.group(1)}  \u00b7  {m.group(2)}' if m else title
    if a.title and not re.search(r'useful words and phrases', title, flags=re.I):
        print('NOTE custom title: set project.json title_lines (big opening text) and kicker to match it, '
              'then show the user an opening mockup (W1).')
    proj = dict(level=a.level, unit=str(a.unit),
                title=title,
                header_title=header,
                kicker=f'{a.level}  \u00b7  UNIT {a.unit}',
                title_lines=['USEFUL WORDS', 'AND PHRASES'],
                subtitle='Vocabulary revision for K S Lo students',
                conclusion_l1="You've revised all {total} words",
                conclusion_l2=f'and phrases from Unit {a.unit}.',
                output='output/' + re.sub(r'[^A-Za-z0-9]+', '_', title).strip('_') + '.mp4',
                item_gain_extra_db={}, nostretch=[], item_takes={},
                illustration_policy='unit1_costars_v1',
                illustration_style='Unit 1-style anime; clear human participant and different prominent adorable ORIGINAL pocket-monster-style meaning-bearing co-star in every image; not a tiny decorative pet; no franchise characters or card UI.',
                n_words=nw, n_phrases=len(items) - nw)
    for fn, obj in (('items.json', items), ('project.json', proj)):
        f = os.path.join(P, fn)
        if os.path.exists(f) and not a.force:
            print(f'kept existing {fn} (use --force to overwrite)')
        else:
            json.dump(obj, open(f, 'w'), ensure_ascii=False, indent=1)
    print(f'project: {P}\n{len(items)} items: {nw} words, {len(items) - nw} phrases  order={kinds}\n')
    print('ILLUSTRATIONS: read /pokemon-vocab-cards Section 3 and references/illustration_style.md; inspect Unit 1 anchors, plan prominent meaning-bearing human-creature co-stars and approve three pilots before bulk generation. Fill creature family/signature/role/interaction/scale/references; inspect actual images AND final-size cards before check_illustrations.py.')
    for it in items:
        print(f'{it["n"]:2d} {it["headword"]:34s} -> {it["display"]:28s} | {it["blanks"]:44s} | {it["pos_short"]:4s} | {it["question"]}')
    if checks:
        print('\nCHECK highlights:'); print('\n'.join('  ' + c for c in checks))
    print('\nASK THE USER before continuing:' if asks else '\nNo ASK cases.')
    print('\n'.join('  ' + q for q in asks))


if __name__ == '__main__':
    main()
