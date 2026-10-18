#!/usr/bin/env python3
"""Lightweight renderer regressions; uses a synthetic empty project and no media rendering."""
import importlib
import os
from pathlib import Path
import sys
import tempfile
import unittest
from PIL import ImageFont


class PresentationBlankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        (root / 'items.json').write_text('[{"n": 1, "is_phrase": false}]')
        (root / 'project.json').write_text('{}')
        os.environ['VOCAB_PROJECT'] = str(root)
        for module in ('config', 'timeline', 'render'):
            sys.modules.pop(module, None)
        cls.render = importlib.import_module('render')
        cls.assets = cls.render.Assets.__new__(cls.render.Assets)
        cls.font = ImageFont.load_default(size=24)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def layout(self, text):
        return self.assets._blank_layout(text, self.font)[0]

    def test_hyphenated_words_have_two_initials_and_component_bars(self):
        layout = self.layout('self-disciplined')
        self.assertEqual([(kind, value) for kind, _, value in layout if kind == 't'],
                         [('t', 's'), ('t', '-'), ('t', 'd')])
        self.assertEqual(sum(kind == 'u' for kind, _, _ in layout), 13)  # self: 3; disciplined: 10
        self.assertEqual(self.render.blank_words('self-disciplined'), 's_____-d_____')

    def test_tip_top_and_literal_ellipsis_are_preserved_correctly(self):
        layout = self.layout('tip-top ...')
        self.assertEqual([(kind, value) for kind, _, value in layout if kind == 't'],
                         [('t', 't'), ('t', '-'), ('t', 't'), ('t', '...')])
        self.assertEqual(sum(kind == 'u' for kind, _, _ in layout), 4)
        self.assertEqual(self.render.blank_words('tip-top ...'), 't_____-t_____ ...')

    def test_clue_blanks_are_fixed_and_ordinary_words_keep_existing_behavior(self):
        self.assertEqual(self.render.blank_words('word elephant a I'), 'w_____ e_____ a I')
        layout = self.layout('word a')
        self.assertEqual([(kind, value) for kind, _, value in layout if kind == 't'], [('t', 'w'), ('t', 'a')])
        self.assertEqual(sum(kind == 'u' for kind, _, _ in layout), 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
