import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class V72Contract(unittest.TestCase):
    def test_ads_wizard_metadata(self):
        self.assertIn('name: ads-wizard', (ROOT/'SKILL.md').read_text(encoding='utf8'))
    def test_v67_is_preserved_as_primary(self):
        root=(ROOT/'SKILL.md').read_text(encoding='utf8')
        self.assertIn('V67 creative baseline restored',root)
        self.assertIn('Motion Director 67',root)
    def test_no_asset_hero_requirement(self):
        guide=(ROOT/'references/145-editor-first-soft-geometry-v72.md').read_text(encoding='utf8').lower()
        self.assertIn('contextual icons',guide)
        self.assertIn('icon does not help',guide)
        self.assertIn('still a slide deck',guide)
    def test_example_is_interaction_led(self):
        example=json.loads((ROOT/'examples/editorial-polish-v72.json').read_text(encoding='utf8'))
        self.assertGreaterEqual(len(example['beats']),3)
        self.assertTrue(all(b.get('visual_action') and b.get('seam') and b.get('ui_polish') for b in example['beats']))
        self.assertTrue(all(b['ui_polish']['role'].lower().startswith(('small','optional')) for b in example['beats']))
    def test_original_v67_sfx_and_editor(self):
        self.assertTrue((ROOT/'scripts/sfx_story_audit_v67.py').exists())
        self.assertTrue((ROOT/'starter/sound_design/render.py').exists())
        self.assertTrue((ROOT/'scripts/seam_review_v66.py').exists())
if __name__=='__main__': unittest.main()
