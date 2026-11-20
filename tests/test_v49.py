import unittest,sys,json,tempfile,copy
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'starter/composite_film')]
from director_v49 import build,EXTRA,diagnose,capabilities
from director_v48 import definition,build as old_build
from revision_guard_v49 import capture,diff,guard
from production_v49 import start,next_step,gate
from compositor import val
class V49(unittest.TestCase):
 def setUp(self):self.base=ROOT/'examples';self.s=json.loads((self.base/'director-v49.json').read_text())
 def test_catalog(self):
  for d in EXTRA.values():definition(d)
  self.assertEqual(len(EXTRA),8)
 def test_every_recipe(self):
  for name,r in EXTRA.items():
   with self.subTest(name=name):
    layers=[]
    for slot in r['slots']:
     l=dict(id=slot,kind='rect',x=360,y=640,w=120,h=100,color='#abcdef',opacity=.5,reveal=.2,scale=1)
     if name=='light_answer' and slot=='hero':l=dict(id=slot,kind='text',text='METAL',material='metal',color='#acbdef',light=.4,size=80)
     layers.append(l)
    s=dict(version=1,duration=3,width=720,fps=30,background='#101010',layers=layers,markers=[dict(id='start',time=.2)],sequences=[dict(id='one',recipe=name,marker='start',offset=0,duration=1,bind={v:v for v in r['slots']},params={})])
    p,e,_=build(s,self.base);self.assertEqual(len(e['cue_actions']),len(r['actions']));self.assertEqual(len(e['sound_cues']),len(r['sounds']))
 def test_legacy(self):
  s=json.loads((self.base/'director-v48.json').read_text());self.assertEqual(build(s,self.base),old_build(s,self.base))
 def test_legacy_custom_shadow(self):
  s=json.loads((self.base/'director-v48.json').read_text());s['sequence_library']['press_release']=s['sequence_library'].pop('finish_lines');s['sequences'][-1]['recipe']='press_release';self.assertEqual(build(s,self.base),old_build(s,self.base))
 def test_example(self):
  before=copy.deepcopy(self.s);p,e,_=build(self.s,self.base);self.assertEqual(self.s,before);self.assertEqual(len(e['sequences']),4);self.assertEqual(len(e['sound_cues']),1);self.assertAlmostEqual(val(next(x for x in p['layers'] if x['id']=='panel')['scale'],5.9),1.10)
 def test_diagnose(self):
  self.s['sequences'][0]['duration']=.001;r=diagnose(self.s,self.base);self.assertFalse(r['valid']);self.assertIn('duration',r['repair'].lower())
 def test_compatibility(self):
  r=capabilities(self.s,self.base,'title2');self.assertIn('opacity',r['occupied']);self.assertNotIn('light',r['supported']);self.assertIn('reveal',r['supported'])
 def test_same_path_byte_change(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);s=copy.deepcopy(self.s);f=d/'asset.png';next(x for x in s['layers'] if x['id']=='product')['src']=str(f);src=d/'source.json';src.write_text(json.dumps(s));Image.new('RGB',(20,20),'red').save(f);a=capture(src);Image.new('RGB',(20,20),'blue').save(f);b=capture(src);r=diff(a,b);self.assertEqual(r['layer_changes'],[]);self.assertTrue(r['asset_changes'][0]['bytes_changed']);self.assertEqual(guard(r,[])['unexpected'],['asset:image:product']);self.assertTrue(guard(r,['asset:image:product'])['ready_for_visual_review'])
 def test_protected_changes(self):
  with tempfile.TemporaryDirectory() as d:
   src=Path(d)/'source.json';s=copy.deepcopy(self.s);next(x for x in s['layers'] if x['id']=='product')['src']=str(self.base/'assets/v15-workspace.png');src.write_text(json.dumps(s));a=capture(src);s['layers'][2]['text']='Different';src.write_text(json.dumps(s));r=diff(a,capture(src));self.assertEqual(guard(r,[])['unexpected'],['layer:title:text']);self.assertTrue(guard(r,['layer:title:text'])['ready_for_visual_review'])
 def test_session(self):
  with tempfile.TemporaryDirectory() as d:
   w=Path(d)/'session';start(self.base/'director-v49.json',self.base/'creative-v49.json',w);self.assertEqual(next_step(w)['stage'],'preview');self.assertFalse(gate(w)['ready'])
if __name__=='__main__':unittest.main()
