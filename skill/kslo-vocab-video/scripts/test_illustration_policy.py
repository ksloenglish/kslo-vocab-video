#!/usr/bin/env python3
"""Regression tests use synthetic manifest fixtures, not approved real illustrations."""
from pathlib import Path
from unittest.mock import patch
import contextlib
import copy
import io
import json
import os
import tempfile
import unittest
from PIL import Image
import check_illustrations as gate
import image_revision
import init_project


class CoStarGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / 'illus').mkdir()
        (self.root / 'work').mkdir()
        image = self.root / 'illus/01_test.png'
        Image.new('RGB', (1920, 1080), 'white').save(image)
        self.item = dict(n=1, slug='test', creature_family='test otter', creature_signature='petal ears',
                         creature_role='craft tutor', human_creature_interaction='offers a bead to the learner',
                         creature_scale_plan='same depth, readable face', style_reference_files=['test-reference.png'],
                         image_prompt='A human and ORIGINAL co-star support the vocabulary meaning.')
        self.entry = dict(sha256=gate.sha(image), **{f: True for f in gate.CHECKS + gate.COSTAR_CHECKS},
                          **{f: 'Synthetic test evidence only.' for f in gate.COSTAR_EVIDENCE},
                          unresolved_issues=[], device_kinds=[], laptop_lid_check='not_applicable',
                          device_structure_evidence='No devices in this synthetic fixture.')
        self.config = dict(illustration_policy=gate.COSTAR_POLICY)
        self.save()

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        (self.root / 'items.json').write_text(json.dumps([self.item]))
        (self.root / 'project.json').write_text(json.dumps(self.config))
        (self.root / 'work/illustration_review.json').write_text(json.dumps({'1': self.entry}))

    def test_complete_manifest_passes(self):
        self.assertEqual(gate.check(self.root), 1)

    def test_complete_costar_plan_is_equivalent_to_support_prompt(self):
        self.item['image_prompt'] = 'A human and ORIGINAL co-star illustrate the vocabulary meaning.'
        self.save()
        self.assertEqual(gate.check(self.root), 1)
        for field in gate.COSTAR_PLANS:
            with self.subTest(field=field):
                self.item[field] = ''
                self.save()
                with self.assertRaisesRegex(ValueError, field):
                    gate.check(self.root)
                self.item[field] = 'restored synthetic plan'

    def test_each_costar_check_blocks_false_or_missing(self):
        baseline = copy.deepcopy(self.entry)
        for field in gate.COSTAR_CHECKS:
            for value in (False, None):
                with self.subTest(field=field, value=value):
                    self.entry = copy.deepcopy(baseline)
                    self.entry[field] = value
                    self.save()
                    with self.assertRaisesRegex(ValueError, field):
                        gate.check(self.root)

    def test_missing_evidence_and_plans_block(self):
        for target, fields in ((self.entry, gate.COSTAR_EVIDENCE), (self.item, gate.COSTAR_PLANS)):
            for field in fields:
                original = target[field]
                target[field] = ''
                self.save()
                with self.assertRaisesRegex(ValueError, field):
                    gate.check(self.root)
                target[field] = original

    def test_empty_references_block(self):
        self.item['style_reference_files'] = []
        self.save()
        with self.assertRaisesRegex(ValueError, 'style_reference_files'):
            gate.check(self.root)

    def test_stale_hash_blocks(self):
        self.entry['sha256'] = 'old'
        self.save()
        with self.assertRaisesRegex(ValueError, 'stale'):
            gate.check(self.root)

    def test_laptop_structure_checks_remain(self):
        self.entry.update(device_kinds=['laptop'], laptop_lid_check='pass', device_structure_evidence='Looks fine.')
        self.save()
        with self.assertRaisesRegex(ValueError, 'keyboard, hinge'):
            gate.check(self.root)

    def test_legacy_reviews_remain_compatible(self):
        self.config = {}
        for field in gate.COSTAR_CHECKS + gate.COSTAR_EVIDENCE:
            self.entry.pop(field)
        for field in gate.COSTAR_PLANS:
            self.item.pop(field)
        self.save()
        self.assertEqual(gate.check(self.root), 1)

    def test_selective_replacement_enforces_costar_policy(self):
        self.config = {}
        self.item['illustration_policy'] = gate.COSTAR_POLICY
        self.entry['prominent_creature'] = False
        self.save()
        with self.assertRaisesRegex(ValueError, 'prominent_creature'):
            gate.check(self.root)

    def test_new_project_cannot_downgrade_an_item(self):
        self.item['illustration_policy'] = ''
        self.save()
        with self.assertRaisesRegex(ValueError, 'downgrade'):
            gate.check(self.root)

    def test_unknown_policy_blocks(self):
        self.config['illustration_policy'] = 'typo'
        self.save()
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            gate.check(self.root)

    def test_template_never_preapproves_images(self):
        with contextlib.redirect_stdout(io.StringIO()):
            gate.template(self.root)
        entry = json.loads((self.root / 'work/illustration_review_template.json').read_text())['1']
        self.assertTrue(all(entry[f] is False for f in gate.CHECKS + gate.COSTAR_CHECKS))
        self.assertTrue(all(entry[f] == '' for f in gate.COSTAR_EVIDENCE))

    def test_initialiser_defaults_and_no_overwrite(self):
        assets = self.root / 'assets_repo'
        (assets / 'library').mkdir(parents=True)
        (assets / 'library/library.json').write_text('{"clips": {}}')
        source = self.root / 'items.csv'
        source.write_text('headword,pos,definition,zh,sentence\ncraft,noun,a skill,技藝,I enjoy this craft.\n')
        project = self.root / 'new_project'
        argv = ['init_project.py', str(project), '--csv', str(source), '--unit', '3']
        with patch.dict(os.environ, {'KSLO_ASSETS': str(assets)}), patch('sys.argv', argv):
            with contextlib.redirect_stdout(io.StringIO()):
                init_project.main()
                config = json.loads((project / 'project.json').read_text())
                self.assertEqual(config['illustration_policy'], gate.COSTAR_POLICY)
                item = json.loads((project / 'items.json').read_text())[0]
                self.assertTrue(all(field in item for field in gate.COSTAR_PLANS))
                self.assertIn('style_reference_files', item)
                before = (project / 'project.json').read_bytes()
                init_project.main()
                self.assertEqual(before, (project / 'project.json').read_bytes())


class ImageRevisionContentTests(unittest.TestCase):
    def test_visual_metadata_may_change_but_text_content_may_not(self):
        item = dict(headword='self-disciplined', definition='able to control oneself',
                    sentence='She is self-disciplined.', zh='自律', audio_text='self-disciplined',
                    image_prompt='old illustration prompt', creature_family='otter', creature_signature='round ears',
                    creature_role='models routines', human_creature_interaction='studies beside the learner',
                    creature_scale_plan='same depth', style_reference_files=['old-reference.png'],
                    image_prompt_previous='earlier prompt')
        edited = copy.deepcopy(item)
        for field in image_revision.IMAGE_FIELDS:
            edited[field] = ['new-reference.png'] if field == 'style_reference_files' else f'new {field}'
        self.assertEqual(image_revision.content([item]), image_revision.content([edited]))
        edited['definition'] = 'a changed protected definition'
        self.assertNotEqual(image_revision.content([item]), image_revision.content([edited]))


if __name__ == '__main__':
    unittest.main(verbosity=2)
