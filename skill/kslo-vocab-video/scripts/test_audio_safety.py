#!/usr/bin/env python3
"""Focused no-media regression tests for the reusable audio safeguards."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


prep = load('prep_items')
extract = load('extract_take')
verify = load('verify_transcription')
revision = load('audio_revision')


class TrimSafetyTests(unittest.TestCase):
    def test_default_trim_bounds_match_legacy(self):
        x = np.zeros(prep.SR * 2)
        x[13000:26000] = .3
        x[31000:34000] = .1
        hop = prep.SR // 100
        energy = np.array([np.sqrt((x[i:i + hop] ** 2).mean()) for i in range(0, len(x) - hop, hop)])
        active = np.where(energy > energy.max() * .02)[0]
        legacy = (max(0, active[0] * hop - int(.02 * prep.SR)),
                  min(len(x), (active[-1] + 1) * hop + int(.06 * prep.SR)))
        start, end, _ = prep.trim_bounds(x)
        self.assertEqual((start, end), legacy)

    def test_quiet_delayed_final_stop_and_tail_are_retained_unfaded(self):
        x = np.zeros(prep.SR)
        x[int(.20 * prep.SR):int(.36 * prep.SR)] = .5       # loud sibilant-like portion
        stop = int(.52 * prep.SR)
        x[stop:stop + int(.01 * prep.SR)] = .008            # weak delayed final stop
        y, info = prep.trim(x, rel=.01, head=.04, tail=.18, details=True)
        faded = prep.edge_fade(y, info['head_available'], info['tail_available'])
        in_clip = stop - info['start']
        self.assertGreater(info['end'], stop + int(.18 * prep.SR) - 2)
        self.assertAlmostEqual(faded[in_clip], x[stop])       # fade is only in the silent tail

    def test_no_activity_is_an_error(self):
        with self.assertRaises(ValueError):
            prep.trim(np.zeros(prep.SR))
        with self.assertRaises(ValueError):
            extract.groups(np.zeros(prep.SR), prep.SR, .18)

    def test_item_trim_override_is_read_from_temporary_project(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'audio' / 'items_raw').mkdir(parents=True)
            (root / 'work').mkdir()
            item = {'n': 19, 'display': 'boost', 'slug': 'boost'}
            (root / 'items.json').write_text(json.dumps([item]))
            (root / 'project.json').write_text(json.dumps({'item_trim': {'19': {'rel': .01, 'head': .04, 'tail': .18}}}))
            x = np.zeros(prep.SR)
            x[int(.20 * prep.SR):int(.36 * prep.SR)] = .5
            x[int(.52 * prep.SR):int(.53 * prep.SR)] = .008
            sf.write(root / 'audio' / 'items_raw' / '19.wav', x, prep.SR)
            env = dict(os.environ, VOCAB_PROJECT=str(root))
            subprocess.run([sys.executable, str(HERE / 'prep_items.py'), '19'], env=env, check=True, capture_output=True, text=True)
            out, sr = sf.read(root / 'audio' / 'items' / '19_boost.wav')
            self.assertEqual(sr, prep.SR)
            self.assertGreater(len(out), int(.50 * prep.SR))  # weak stop + configured .18 s guard survived


class TranscriptSafetyTests(unittest.TestCase):
    def test_authoritative_json_not_repeated_cli_rendering(self):
        data = {'segments': [{'text': 'Boost'}], 'full_text': 'Boost'}
        repeated_terminal_rendering = '[00:00] Boost\n[00:00] Boost'
        self.assertIn('Boost', repeated_terminal_rendering)
        self.assertEqual(verify.check_isolated(data, 'boost')['count'], 1)

    def test_extra_words_duplicates_and_wrong_order_fail(self):
        with self.assertRaises(ValueError):
            verify.check_isolated({'segments': [{'text': 'boost now'}], 'full_text': 'boost now'}, 'boost')
        items = [{'n': 1, 'display': 'alpha'}, {'n': 2, 'display': 'beta'}]
        timeline = [{'kind': 'item', 'item': 1}, {'kind': 'item', 'item': 2}]
        with self.assertRaises(ValueError):
            verify.check_full({'segments': [{'text': 'alpha alpha beta'}], 'full_text': 'alpha alpha beta'}, items, timeline)
        with self.assertRaises(ValueError):
            verify.check_full({'segments': [{'text': 'beta alpha'}], 'full_text': 'beta alpha'}, items, timeline)

    def test_articles_are_rejected_unless_deliberately_enabled(self):
        data = {'segments': [{'text': 'lighten the mood'}], 'full_text': 'lighten the mood'}
        with self.assertRaises(ValueError):
            verify.check_isolated(data, 'lighten mood')
        report = verify.check_isolated(data, 'lighten mood', allow_articles=True)
        self.assertEqual(report['optional_asr_article_normalisation'], 'lighten the mood')


class RevisionSafetyTests(unittest.TestCase):
    def setUp(self):
        self.old = np.full((10000, 1), .1)
        self.fresh = self.old.copy()
        self.fresh[5000:6000] = .2
        self.window = {'n': 1, 'a': 4500, 'b': 6500, 'u': 4000, 'v': 4200, 'start': 4.5, 'end': 6.5}

    def test_pcm_is_sample_perfect_outside_selected_window(self):
        mixed, changed, _ = revision.patch_pcm(self.old, self.fresh, [self.window], sr=1000)
        self.assertTrue(np.array_equal(mixed[~changed], self.old[~changed]))
        self.assertFalse(np.array_equal(mixed[changed], self.old[changed]))

    def test_pcm_overlap_and_clipping_guards(self):
        overlap = dict(self.window, n=2, a=6400, b=8000, u=6100, v=6300)
        with self.assertRaises(ValueError):
            revision.patch_pcm(self.old, self.fresh, [self.window, overlap], sr=1000)
        clipped = self.fresh.copy()
        clipped[5000:6000] = 1.0
        with self.assertRaises(ValueError):
            revision.patch_pcm(self.old, clipped, [self.window], sr=1000)

    def test_protected_project_metadata_changes_fail(self):
        before = {'title': 'S2 Unit', 'output': 'output/v2.mp4', 'item_takes': {'1': '01', '2': '02'}}
        protected = dict(before, title='different', output='output/v3.mp4')
        with self.assertRaises(ValueError):
            revision.verify_project_changes(before, protected, {1}, '/tmp/source.mp4', '/tmp')
        unselected = dict(before, output='output/v3.mp4', item_takes={'1': '01', '2': 'new'})
        with self.assertRaises(ValueError):
            revision.verify_project_changes(before, unselected, {1}, '/tmp/source.mp4', '/tmp')


if __name__ == '__main__':
    unittest.main(verbosity=2)
