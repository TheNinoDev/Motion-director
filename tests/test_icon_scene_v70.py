import json,sys,unittest,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from icon_scene_audit_v70 import audit
from solar_svg_import_v70 import safe_svg,find,import_one
class TestIconScenes(unittest.TestCase):
 def test_example(self):
  d=json.loads((ROOT/'examples/icon-ensemble-v70/shot-plan.json').read_text())
  self.assertFalse(audit(d)['warnings'])
 def test_repeated_isolated_icons_warn(self):
  shots=[{'id':str(i),'assets':[{'id':'icon','role':'hero'}]} for i in range(3)]
  self.assertTrue(audit({'shots':shots})['warnings'])
 def test_unrelated_actors_warn(self):
  shot={'id':'x','assets':[{'id':'a','role':'hero'},{'id':'b','role':'target'}]}
  self.assertTrue(audit({'shots':[shot]})['warnings'])
 def test_unsafe_svg(self):
  with self.assertRaises(ValueError):safe_svg('<svg><script/></svg>')
 def test_local_import(self):
  with tempfile.TemporaryDirectory() as t:
   src=Path(t)/'icons';(src/'bold').mkdir(parents=True)
   (src/'bold'/'heart.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="currentColor" d="M0 0h24v24H0z"/></svg>')
   self.assertEqual(find(src,'heart'),['bold/heart.svg'])
   self.assertEqual(import_one(src,'bold','heart',Path(t)/'out',size=64)['name'],'heart')
if __name__=='__main__':unittest.main()
