import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('audit',ROOT/'scripts/edit_asset_role_audit_v71.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class EditAssetRoleAudit(unittest.TestCase):
    def test_good_example(self):
        plan=json.loads((ROOT/'examples/edit-first-v71/shot-plan.json').read_text(encoding='utf8'))
        report=mod.review(plan)
        self.assertEqual(report['shots_reviewed'],5)
        self.assertEqual(report['warning_count'],0,report['warnings'])
    def test_detects_slide_pair(self):
        shots=[{'id':'a','layout':'title-icon','primary_action':'display',
                'components':[], 'assets':[{'id':'shield','type':'svg-icon','role':'hero'}],
                'handoff':'none'},
               {'id':'b','layout':'icon-hero','primary_action':'hold',
                'components':[], 'assets':[{'id':'lock','type':'svg-icon','role':'standalone'}],
                'handoff':'end'}]
        codes={w['code'] for w in mod.review({'shots':shots})['warnings']}
        self.assertTrue({'standalone-icon','repeated-asset-slides','unplanned-seam','weak-main-action'}.issubset(codes))
    def test_detects_unattached_detail(self):
        shot={'id':'a','layout':'context','primary_action':'Card splits and label resolves','components':[{'id':'button','type':'button'}],
              'assets':[{'id':'key','type':'svg-icon','role':'button-icon','attached_to':'wrong'}],'handoff':'end'}
        self.assertIn('orphan-polish',[w['code'] for w in mod.review({'shots':[shot]})['warnings']])
    def test_allows_no_icons(self):
        shot={'id':'a','layout':'kinetic-typography','primary_action':'Text folds through frame','components':[],'assets':[], 'handoff':'end'}
        self.assertEqual(mod.review({'shots':[shot]})['warning_count'],0)
    def test_rejects_empty(self):
        with self.assertRaises(ValueError):mod.review({'shots':[]})

if __name__=='__main__':unittest.main()
