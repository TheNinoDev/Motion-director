import unittest,copy,json,tempfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'starter/composite_film')]
from director_v37 import build,diagnosis,MACROS
from review_ledger import create,check,digest
from compositor import val
class V37(unittest.TestCase):
 def spec(self):
  return {'version':1,'duration':3,'layers':[{'id':'a','kind':'rect','w':160,'h':100},{'id':'b','kind':'text','text':'Hi','x':360,'y':500},{'id':'g','kind':'glass_object','geometry':'torus','w':200,'h':200},{'id':'s','kind':'object3d','geometry':'rounded_box','w':200,'h':200},{'id':'p','kind':'path','w':100,'h':100,'points':[[0,0],[100,100]],'stroke':2}],'macros':[]}
 def test_all_recipes(self):
  move={'from':[300,500],'to':[360,640]};angles={'angles_from':[0,0],'angles_to':[35,-15]};scale={'scale_from':1,'scale_to':1.3}
  cases={'masked_arrival':('a',dict(at=[360,640],offset=[60,0])),'focus_pull':('a',dict(**move,**scale)),'object_turn':('s',dict(**move,**angles)),'elastic_land':('s',dict(**move,preset='jelly_soft')),'shape_unfold':('s',dict(**{'from':0,'to':1},**angles)),'glass_travel':('g',dict(**move,**angles)),'orbit_reveal':('a',dict(center=[360,640],radius=[50,80],degrees=[0,180])),'exit_match':('a',dict(**move,**scale)),'stagger_reveal':(None,dict(layers=['a','b'],offset=[0,60])),'path_draw':('p',{'from':0,'to':1})}
  self.assertEqual(set(cases),set(MACROS))
  for name,(layer,kw) in cases.items():
   with self.subTest(recipe=name):
    spec=self.spec();m=dict(recipe=name,start=0,end=2,**kw)
    if layer:m['layer']=layer
    spec['macros']=[m];p,expanded,_=build(spec,ROOT);self.assertGreater(len(expanded['actions']),0);self.assertNotIn('macros',expanded)
 def test_example(self):
  p,s,_=build(json.loads((ROOT/'examples/director-v37.json').read_text()),ROOT/'examples');self.assertEqual(len(s['actions']),19);self.assertEqual(val(p['layers'][4]['x'],2.5),380)
 def test_no_mutation(self):
  s=self.spec();before=copy.deepcopy(s);build(s,ROOT);self.assertEqual(s,before)
 def test_invalid_option(self):
  s=self.spec();s['macros']=[dict(recipe='path_draw',layer='p',start=0,end=1,**{'from':0,'to':1},misspelt=1)]
  with self.assertRaisesRegex(ValueError,'unknown'):build(s,ROOT)
 def test_solid_mask_rejected(self):
  s=self.spec();s['macros']=[dict(recipe='masked_arrival',layer='g',start=0,end=1,at=[360,640],offset=[0,30])]
  with self.assertRaisesRegex(ValueError,'flat'):build(s,ROOT)
 def test_conflict(self):
  s=self.spec();m=dict(recipe='focus_pull',layer='a',start=0,end=2,**{'from':[0,0],'to':[5,5]},scale_from=1,scale_to=2);s['macros']=[m,m]
  with self.assertRaisesRegex(ValueError,'overlapping'):build(s,ROOT)
 def test_diagnostics(self):
  s=self.spec();s['layers'][1]['active']=[0,.2];s['layers'][1]['y']=1200;p,_,_=build(s,ROOT);codes={i['code'] for i in diagnosis(p)};self.assertIn('brief_text',codes);self.assertIn('text_anchor',codes)
 def test_review(self):
  with tempfile.TemporaryDirectory() as d:
   base=Path(d);plan=base/'plan.json';p,_,_=build(self.spec(),ROOT);plan.write_text(json.dumps(p));ledger=create(plan);r=check(plan,ledger,base);self.assertFalse(r['record_complete']);self.assertTrue(r['pending']);ledger['items'].pop();self.assertTrue(check(plan,ledger,base)['errors']);plan.write_text(json.dumps(p,indent=2));self.assertIn('plan changed; regenerate checklist',check(plan,ledger,base)['errors'])
 def test_evidence_mismatch(self):
  with tempfile.TemporaryDirectory() as d:
   base=Path(d);plan=base/'plan.json';p,_,_=build(self.spec(),ROOT);plan.write_text(json.dumps(p));ledger=create(plan);x=ledger['items'][0];x.update(status='reviewed',evidence='missing.png',sha256='bad',observation='Test',decision='keep');self.assertTrue(check(plan,ledger,base)['errors'])
 def test_playback_requires_video(self):
  with tempfile.TemporaryDirectory() as d:
   base=Path(d);plan=base/'plan.json';p,_,_=build(self.spec(),ROOT);plan.write_text(json.dumps(p));ledger=create(plan);x=ledger['items'][-1];x.update(status='reviewed',evidence='still.png',sha256='bad',observation='Test',decision='keep');self.assertTrue(check(plan,ledger,base)['errors'])
if __name__=='__main__':unittest.main()
