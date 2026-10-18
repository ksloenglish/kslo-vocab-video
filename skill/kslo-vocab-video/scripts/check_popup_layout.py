#!/usr/bin/env python3
"""Blocking pop-up text preflight; --stills also renders every used pop-up."""
import argparse
import json
from pathlib import Path
from PIL import ImageDraw
import render
from popup_layout import (BUBBLE_W, BUBBLE_H, BUBBLE_X, BUBBLE_Y, HEAD_RECT,
                          build_popup_text, glyph_sprite, split_line,
                          validate_popup_lines, PopupTextOverflow)

EXPECTED = {
    'pop1': ('Great job!', 'Keep going!'),
    'pop2': ("You're doing really well.", "Let's keep going!"),
    'pop3': ('Nice work!', 'Here come some more.'),
    'pop4': ('Brilliant!', "You're on a roll!"),
    'pop5': ('Keep it up!', "You've got this!"),
    'pop6': ('Almost there!', 'Just a few more to go!'),
}


def check():
    report = validate_popup_lines(render.POP_LINES, render.font)
    for key, line in render.POP_LINES.items():
        headline, subtitle = split_line(line)
        if key in EXPECTED and line == ' '.join(EXPECTED[key]):
            assert (headline, subtitle) == EXPECTED[key]
        layer, placements = build_popup_text(line, render.font)
        assert placements[0]['text'] == headline.upper()
        assert len(placements) == (2 if subtitle else 1)
        if subtitle:
            assert placements[1]['text'] == subtitle
            assert placements[0]['ink_bounds'][3] < placements[1]['ink_bounds'][1]
        outside = layer.getchannel('A').copy()
        draw = ImageDraw.Draw(outside)
        for placement in placements:
            left, top, right, bottom = placement['safe_rect']
            draw.rectangle((left, top, right - 1, bottom - 1), fill=0)
            x0, y0, x1, y1 = placement['ink_bounds']
            assert 64 <= x0 < x1 <= BUBBLE_W - 64
            assert 40 <= y0 < y1 <= BUBBLE_H - 32
            # Sample the complete easing/overshoot range, not only stable holds.
            for step in range(401):
                progress = step / 400
                scale = 0.85 + 0.15 * render.eback(progress)
                cx = BUBBLE_X - 40 + (BUBBLE_W + 120) / 2
                cy = BUBBLE_Y - 40 + (BUBBLE_H + 80) / 2
                gx0 = cx + (40 + x0 - (BUBBLE_W + 120) / 2) * scale
                gx1 = cx + (40 + x1 - (BUBBLE_W + 120) / 2) * scale
                gy0 = cy + (40 + y0 - (BUBBLE_H + 80) / 2) * scale
                gy1 = cy + (40 + y1 - (BUBBLE_H + 80) / 2) * scale
                assert 0 < gx0 < gx1 < render.W
                assert 0 < gy0 < gy1 < render.H
        assert outside.getbbox() is None, f'{key}: glyphs outside safe rectangles'
    # Reproduce the old bug and prove the fitted headline fixes it.
    old = glyph_sprite("YOU'RE DOING REALLY WELL.", render.font('bebas', 128), (12, 28, 62, 255))
    assert old.width > HEAD_RECT[2] - HEAD_RECT[0]
    for line in ["Wonderful effort! You're making excellent progress!",
                 "You've made impressive progress. Keep practising every day!",
                 "W!", "I!", "You're improving! You've got this, keep going!"]:
        build_popup_text(line, render.font)
    for line in ['', 'W' * 300, 'Good job! ' + 'W' * 300]:
        try:
            build_popup_text(line, render.font)
        except PopupTextOverflow:
            pass
        else:
            raise AssertionError('Oversized or empty text was not rejected')
    assert render.POP_MIN_REMAINING == 3
    for count, expected in {5: [], 6: [], 7: [], 8: [5], 12: [5],
                            13: [5, 10], 16: [5, 10], 17: [5, 10],
                            18: [5, 10, 15]}.items():
        assert render.popup_positions(count) == expected
    for count in range(51):
        positions = render.popup_positions(count)
        assert all(done % render.POP_EVERY == 0 and count - done >= 3 for done in positions)
    for kind, items in render.PARTS:
        for done in render.popup_positions(len(items)):
            assert len(items) - done >= 3
    assert [seg['n_done'] for seg in render.SEGMENTS if seg['kind'] == 'popup'] == render.popup_slots()
    bare_assets = render.Assets.__new__(render.Assets)
    for visual in ['assist ... in', 'mistake ... for']:
        layout, _ = bare_assets._blank_layout(visual, render.font('bold', 92))
        assert [payload for kind, _, payload in layout if kind == 't'] == [visual.split()[0][0], '...', visual.split()[-1][0]]
        expected_bars = sum(len(word) - 1 for word in visual.split() if any(ch.isalpha() for ch in word))
        assert sum(kind == 'u' for kind, _, _ in layout) == expected_bars
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stills', action='store_true', help='render entry, overshoot, hold and exit for every used pop-up')
    args = parser.parse_args()
    report = check()
    root = Path(render.R)
    out = root / 'work/popup_qa'
    out.mkdir(parents=True, exist_ok=True)
    report_path = out / 'text_fit_report.json'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    for key, placements in report.items():
        summary = ', '.join(f"{p['role']} {p['font_size']}px, ink {p['ink_bounds']}" for p in placements)
        print(key + ': ' + summary)
    print('PASS: all library lines, punctuation, readable floors, overflow rejection, animation canvas and minimum-three-remaining checks.')
    print('Permitted pop-ups after global items:', render.popup_slots())
    print(report_path)
    if args.stills:
        render.A = render.Assets()
        for seg in render.SEGMENTS:
            if seg['kind'] != 'popup':
                continue
            times = [('entry', 0.35), ('overshoot', 0.60), ('hold', 1.6), ('exit', seg['dur'] - 0.35)]
            for label, local in times:
                g = seg['start'] + local
                path = out / f"seg_{seg['idx']:03d}_{seg['pop']}_{label}.png"
                render.frame_at(g).convert('RGB').save(path)
                print(path)


if __name__ == '__main__':
    main()
