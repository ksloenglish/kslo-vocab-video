#!/usr/bin/env python3
"""Create an image-review gallery or enforce its explicit hash approvals.

usage:
  VOCAB_PROJECT=/project python3 review_images.py [--items 1 2]
  VOCAB_PROJECT=/project python3 review_images.py --approve --review-id ID --note 'explicit user approval' [--items 1 2]
  VOCAB_PROJECT=/project python3 review_images.py --check [--items 1 2]

Creating a gallery never approves anything. Run --approve only after an actual
explicit user reply has been observed; this script cannot verify a conversation.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def image_path(root, item):
    return root / 'illus' / f"{item['n']:02d}_{item['slug']}.png"


def require_png(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f'missing or empty PNG: {path}')
    try:
        with Image.open(path) as image:
            if image.format != 'PNG':
                raise ValueError(f'not a PNG: {path}')
            image.verify()
    except (OSError, ValueError) as error:
        raise ValueError(f'unreadable PNG: {path} ({error})') from error


def load_items(root):
    items = json.loads((Path(root) / 'items.json').read_text())
    seen = set()
    for item in items:
        try:
            n = int(item['n'])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f'item has invalid number: {item!r}') from error
        if n in seen:
            raise ValueError(f'duplicate item number in items.json: {n}')
        seen.add(n)
    return items


def parse_numbers(values):
    if values is None:
        return None
    result = []
    for value in values:
        for token in str(value).split(','):
            token = token.strip()
            if not token:
                raise ValueError('empty item number in --items')
            try:
                n = int(token)
            except ValueError as error:
                raise ValueError(f'invalid item number: {token!r}') from error
            if n in result:
                raise ValueError(f'duplicate item number: {n}')
            result.append(n)
    return result


def selected_items(root, numbers=None):
    items = load_items(root)
    if numbers is None:
        return items
    known = {int(item['n']) for item in items}
    unknown = [n for n in numbers if n not in known]
    if unknown:
        raise ValueError('item(s) outside this project: ' + ', '.join(map(str, unknown)))
    wanted = set(numbers)
    return [item for item in items if int(item['n']) in wanted]  # always actual video order


def candidates(root, numbers=None):
    out = []
    for item in selected_items(root, numbers):
        path = image_path(root, item)
        require_png(path)
        out.append(dict(n=int(item['n']), slug=item['slug'], display=item.get('display', item['slug']),
                        path=path, sha256=sha(path)))
    return out


def review_id(entries):
    exact = [dict(n=entry['n'], sha256=entry['sha256']) for entry in entries]
    raw = json.dumps(exact, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return 'img-' + hashlib.sha256(raw).hexdigest()


def state_path(root):
    return Path(root) / 'work' / 'image_approval.json'


def read_state(root):
    path = state_path(root)
    if not path.exists():
        return dict(version=1, approved={})
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or not isinstance(data.get('approved', {}), dict):
        raise ValueError(f'invalid approval manifest: {path}')
    data.setdefault('version', 1)
    data.setdefault('approved', {})
    return data


def write_state(root, data):
    path = state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def font(size):
    for path in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                 '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap(draw, text, face, width):
    words, lines, line = str(text).split(), [], ''
    for word in words or ['']:
        test = (line + ' ' + word).strip()
        if line and draw.textlength(test, font=face) > width:
            lines.append(line)
            line = word
        else:
            line = test
    if line:
        lines.append(line)
    return lines


def make_sheets(root, entries):
    out = Path(root) / 'output'
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob('illustration_review_sheet_*.png'):
        old.unlink()
    tile_w, tile_h, gap, margin, header = 780, 510, 20, 30, 82
    sheets = []
    for page, start in enumerate(range(0, len(entries), 6), 1):
        chunk = entries[start:start + 6]
        rows = (len(chunk) + 1) // 2
        sheet = Image.new('RGB', (2 * tile_w + 3 * margin, header + rows * tile_h + (rows + 1) * gap), (13, 25, 52))
        draw = ImageDraw.Draw(sheet)
        title_face, label_face = font(30), font(25)
        draw.text((margin, 25), f'Illustration review — sheet {page}', font=title_face, fill=(255, 210, 92))
        for index, entry in enumerate(chunk):
            col, row = index % 2, index // 2
            x = margin + col * (tile_w + margin)
            y = header + gap + row * (tile_h + gap)
            draw.rounded_rectangle((x, y, x + tile_w, y + tile_h), radius=18, fill=(27, 48, 88), outline=(125, 170, 230), width=2)
            label = f"#{entry['n']}  {entry['display']}"
            lines = wrap(draw, label, label_face, tile_w - 32)[:2]
            label_h = max(42, 30 * len(lines) + 12)
            for line_no, line in enumerate(lines):
                draw.text((x + 16, y + 10 + 30 * line_no), line, font=label_face, fill='white')
            with Image.open(entry['path']) as source:
                source = source.convert('RGB')
                source.thumbnail((tile_w - 28, tile_h - label_h - 28), Image.Resampling.LANCZOS)
                px = x + (tile_w - source.width) // 2
                py = y + label_h + 12 + (tile_h - label_h - 24 - source.height) // 2
                sheet.paste(source, (px, py))
        path = out / f'illustration_review_sheet_{page:02d}.png'
        sheet.save(path, optimize=True)
        sheets.append(path)
    return sheets


def gallery(root, numbers=None):
    root = Path(root)
    entries = candidates(root, numbers)
    if not entries:
        raise ValueError('no items selected for review')
    ident = review_id(entries)
    state = read_state(root)
    state['pending'] = dict(review_id=ident,
                            items=[dict(n=e['n'], sha256=e['sha256']) for e in entries],
                            created_at=datetime.now(timezone.utc).isoformat())
    write_state(root, state)
    sheets = make_sheets(root, entries)
    out = root / 'output'
    project = json.loads((root / 'project.json').read_text()) if (root / 'project.json').exists() else {}
    lines = [f"# {project.get('title', 'Illustration')} — image review", '',
             f"**Review ID:** `{ident}`", '',
             '> Review the source images and their full-resolution PNG links below. Creating this gallery does **not** approve any image. Run `--approve` only after an explicit user approval reply has been observed; the script itself cannot verify a conversation.',
             '', '## Contact sheets', '']
    for page, sheet in enumerate(sheets, 1):
        group = entries[(page - 1) * 6:page * 6]
        lines.append(f"- [Sheet {page} — #{group[0]['n']}–#{group[-1]['n']}]({quote(str(sheet.resolve()), safe='/')})")
    lines += ['', '## Items (actual video order)', '']
    for entry in entries:
        link = quote(str(entry['path'].resolve()), safe='/')
        lines.append(f"{entry['n']}. **{entry['display']}** — [open full-resolution PNG]({link})  ")
        lines.append(f"   SHA-256: `{entry['sha256']}`")
    review = out / 'illustration_review.md'
    review.write_text('\n'.join(lines) + '\n')
    print(f'Wrote {review} ({len(entries)} item(s), {len(sheets)} sheet(s)); pending review ID: {ident}')
    return ident


def pending_entries(state):
    pending = state.get('pending')
    if not isinstance(pending, dict) or not isinstance(pending.get('review_id'), str) or not isinstance(pending.get('items'), list):
        raise ValueError('no pending image review; create a gallery first')
    entries, seen = [], set()
    for entry in pending['items']:
        try:
            n, digest = int(entry['n']), entry['sha256']
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError('invalid pending image review') from error
        if n in seen or not isinstance(digest, str) or len(digest) != 64:
            raise ValueError('invalid or duplicate pending image review item')
        seen.add(n)
        entries.append(dict(n=n, sha256=digest))
    if not entries or review_id(entries) != pending['review_id']:
        raise ValueError('pending review ID does not match its exact ordered hashes; create a new gallery')
    return entries


def approve(root, ident, note, numbers=None):
    root = Path(root)
    if not isinstance(note, str) or not note.strip():
        raise ValueError('--note must be non-empty and record the explicit user approval')
    state = read_state(root)
    pending = pending_entries(state)
    if ident != state['pending']['review_id']:
        raise ValueError('wrong or stale --review-id; use the pending review ID in output/illustration_review.md')
    scope = {entry['n']: entry['sha256'] for entry in pending}
    wanted = [entry['n'] for entry in pending] if numbers is None else numbers
    unknown = [n for n in wanted if n not in scope]
    if unknown:
        raise ValueError('item(s) outside the pending review scope: ' + ', '.join(map(str, unknown)))
    actual = {entry['n']: entry for entry in candidates(root, wanted)}
    for n in wanted:
        if actual[n]['sha256'] != scope[n]:
            raise ValueError(f'#{n}: source image changed after the gallery; create and review a fresh gallery')
        previous = state['approved'].get(str(n), {})
        if previous.get('sha256') == actual[n]['sha256']:
            raise ValueError(f'#{n}: already approved for this image; do not submit duplicate approval')
    now = datetime.now(timezone.utc).isoformat()
    for n in wanted:
        state['approved'][str(n)] = dict(sha256=actual[n]['sha256'], review_id=ident,
                                         note=note.strip(), approved_at=now)
    write_state(root, state)
    print('Recorded explicit approval for item(s): ' + ', '.join(map(str, wanted)))


def check(root, item_numbers=None):
    root = Path(root)
    entries = candidates(root, item_numbers)
    state = read_state(root)
    failures = []
    for entry in entries:
        approved = state['approved'].get(str(entry['n']), {})
        if approved.get('sha256') != entry['sha256']:
            failures.append(f"#{entry['n']} missing, unapproved or stale")
    if failures:
        raise ValueError('image approval required: ' + '; '.join(failures))
    print('Image approval gate PASS: ' + (', '.join(str(e['n']) for e in entries) or 'no changed images'))
    return len(entries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', default=os.environ.get('VOCAB_PROJECT'))
    parser.add_argument('--items', nargs='+', help='item numbers, comma-separated and/or space-separated')
    parser.add_argument('--approve', action='store_true', help='record observed explicit user approval; never use before that reply')
    parser.add_argument('--check', action='store_true', help='fail unless selected actual PNG hashes were explicitly approved')
    parser.add_argument('--review-id')
    parser.add_argument('--note', help='non-empty note recording the explicit user approval')
    args = parser.parse_args()
    if not args.project:
        parser.error('Set VOCAB_PROJECT or pass --project')
    if args.approve and args.check:
        parser.error('choose only one of --approve or --check')
    try:
        numbers = parse_numbers(args.items)
        if args.approve:
            if not args.review_id:
                raise ValueError('--approve requires --review-id from the pending gallery')
            approve(args.project, args.review_id, args.note, numbers)
        elif args.check:
            check(args.project, numbers)
        else:
            if args.review_id or args.note:
                raise ValueError('--review-id and --note are only valid with --approve')
            gallery(args.project, numbers)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        print(f'Image approval FAILED: {error}', file=sys.stderr)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
