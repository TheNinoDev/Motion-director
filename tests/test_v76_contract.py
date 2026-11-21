"""Mechanical contract checks; not an automated creative-quality judgment."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class V76ContractTests(unittest.TestCase):
    def test_root_and_guides(self):
        s=(ROOT/'SKILL.md').read_text(encoding='utf8')
        self.assertIn('name: ads-wizard',s)
        self.assertIn('Ads Wizard v76',s)
        for path in ['references/156-claude-live-case-v76.md','references/157-editorial-decision-system-v76.md']:
            self.assertTrue((ROOT/path).exists())
    def test_core_and_mascot(self):
        for path in ['starter/sound_design/render.py','scripts/two_frame_finish_v74.py','scripts/scene_ownership_audit_v75.py','assets/branding/ads-wizard-icon.png']:
            self.assertTrue((ROOT/path).is_file())
    def test_true_review_claim(self):
        s=(ROOT/'references/156-claude-live-case-v76.md').read_text(encoding='utf8')
        self.assertIn('FOUR of the nine',s)
        self.assertIn('594 source frames',s)
if __name__=='__main__': unittest.main()
