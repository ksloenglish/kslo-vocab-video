#!/usr/bin/env python3
"""Synthetic regression tests for review_images.py; no video rendering or project media."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

SCRIPTS = Path(__file__).resolve().parent
REVIEW = SCRIPTS / 'review_images.py'
sys.path.insert(0, str(SCRIPTS))
from image_revision import changed_image_numbers


class ImageApprovalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'illus').mkdir()
        (self.root / 'work').mkdir()
        self.items = []

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, n, display=None, colour=None):
        slug = f'item_{n}'
        self.items.append(dict(n=n, slug=slug, display=display or f'Item {n}'))
        Image.new('RGB', (640, 360), colour or (n * 19 % 255, n * 41 % 255, n * 61 % 255)).save(
            self.root / 'illus' / f'{n:02d}_{slug}.png')

    def save(self):
        (self.root / 'items.json').write_text(json.dumps(self.items))
        (self.root / 'project.json').write_text(json.dumps({'title': 'Synthetic image review'}))

    def command(self, *args, ok=True):
        env = dict(os.environ, VOCAB_PROJECT=str(self.root))
        result = subprocess.run([sys.executable, str(REVIEW), *args], env=env, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if ok and result.returncode:
            self.fail(f'command failed: {args}\nstdout={result.stdout}\nstderr={result.stderr}')
        if not ok:
            self.assertNotEqual(result.returncode, 0, f'command unexpectedly passed: {args}')
        return result

    def gallery_id(self, *args):
        self.command(*args)
        return json.loads((self.root / 'work' / 'image_approval.json').read_text())['pending']['review_id']

    def approve(self, ident, *items):
        args = ['--approve', '--review-id', ident, '--note', 'explicit user approval']
        if items:
            args += ['--items', *map(str, items)]
        self.command(*args)

    def test_complete_missing_and_stale_approvals(self):
        for n in (1, 2, 3): self.add(n)
        self.save()
        ident = self.gallery_id()
        self.command('--check', ok=False)  # complete gallery alone is never approval
        self.approve(ident)
        self.command('--check')
        Image.new('RGB', (640, 360), (255, 1, 2)).save(self.root / 'illus' / '02_item_2.png')
        self.command('--check', ok=False)  # hash mutation makes its approval stale
        (self.root / 'illus' / '03_item_3.png').unlink()
        self.command('--check', ok=False)  # an actual PNG must still exist

    def test_hash_mutation_after_gallery_cannot_be_approved(self):
        self.add(1); self.save()
        ident = self.gallery_id()
        Image.new('RGB', (640, 360), (1, 2, 3)).save(self.root / 'illus' / '01_item_1.png')
        self.command('--approve', '--review-id', ident, '--note', 'explicit user approval', ok=False)

    def test_partial_approvals_preserve_accepted_hashes(self):
        for n in (1, 2, 3): self.add(n)
        self.save()
        first = self.gallery_id()
        self.approve(first, 1)
        first_hash = json.loads((self.root / 'work' / 'image_approval.json').read_text())['approved']['1']['sha256']
        Image.new('RGB', (640, 360), (4, 5, 6)).save(self.root / 'illus' / '02_item_2.png')
        second = self.gallery_id('--items', '2')
        self.approve(second, 2)
        state = json.loads((self.root / 'work' / 'image_approval.json').read_text())
        self.assertEqual(state['approved']['1']['sha256'], first_hash)
        self.command('--check', '--items', '1')
        self.command('--check', '--items', '2')
        self.command('--check', ok=False)  # still blocks assembly because #3 was never accepted

    def test_note_review_id_duplicate_and_scope_requirements(self):
        self.add(1); self.add(2); self.save()
        ident = self.gallery_id('--items', '1')
        self.command('--approve', '--note', 'explicit user approval', '--items', '1', ok=False)
        self.command('--approve', '--review-id', ident, '--note', '   ', '--items', '1', ok=False)
        self.command('--approve', '--review-id', 'img-wrong', '--note', 'explicit user approval', '--items', '1', ok=False)
        self.command('--approve', '--review-id', ident, '--note', 'explicit user approval', '--items', '1', '1', ok=False)
        self.command('--approve', '--review-id', ident, '--note', 'explicit user approval', '--items', '2', ok=False)

    def test_paginated_gallery_is_actual_order_and_has_individual_png_links(self):
        # Deliberately non-numeric order mirrors the renderer's ordered items.json contract.
        for n in (9, 2, 7, 1, 8, 3, 6): self.add(n, f'Display {n}')
        self.save()
        self.gallery_id()
        text = (self.root / 'output' / 'illustration_review.md').read_text()
        self.assertTrue((self.root / 'output' / 'illustration_review_sheet_01.png').is_file())
        self.assertTrue((self.root / 'output' / 'illustration_review_sheet_02.png').is_file())
        positions = [text.index(f'**Display {n}**') for n in (9, 2, 7, 1, 8, 3, 6)]
        self.assertEqual(positions, sorted(positions))
        for n in (9, 2, 7, 1, 8, 3, 6):
            self.assertIn(str(self.root / 'illus' / f'{n:02d}_item_{n}.png'), text)
        self.assertIn(str(self.root / 'output' / 'illustration_review_sheet_01.png'), text)

    def test_changed_set_gate_does_not_require_untouched_legacy_approvals(self):
        self.add(1); self.add(2); self.save()
        baseline = {'image_files': {
            'illus/01_item_1.png': __import__('hashlib').sha256((self.root / 'illus' / '01_item_1.png').read_bytes()).hexdigest(),
            'illus/02_item_2.png': __import__('hashlib').sha256((self.root / 'illus' / '02_item_2.png').read_bytes()).hexdigest(),
        }}
        Image.new('RGB', (640, 360), (211, 31, 51)).save(self.root / 'illus' / '02_item_2.png')
        self.assertEqual(changed_image_numbers(self.root, baseline), [2])
        ident = self.gallery_id('--items', '2')
        self.approve(ident, 2)
        self.command('--check', '--items', '2')  # source-MP4 changed-set equivalent
        self.command('--check', ok=False)        # #1 remains legacy/unapproved, but is not in changed set


if __name__ == '__main__':
    unittest.main(verbosity=2)
