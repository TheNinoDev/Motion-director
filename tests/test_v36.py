import unittest,sys,json,copy,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'starter/composite_film')]
from motion_workbench import compile_spec,audit,OPS
from agent_revision import revise
from compositor import Engine,val
class V36(unittest.TestCase):
 def spec(self):return {'version':1,'duration':3,'layers':[{'id':'a','kind':'rect','w':200,'h':200},{'id':'b','kind':'ellipse','w':200,'h':200},{'id':'solid','kind':'object3d','w':200,'h':200,'geometry':'ellipsoid'},{'id':'path','kind':'path','w':200,'h':200,'points':[[0,0],[100,100]],'stroke':2}], 'actions':[],'cues':{'mid':1}}
 def action(self,op,l='a',**kw):return dict(op=op,layer=l,start=0,end=1,**kw)
 def test_example(self):
  p,n=compile_spec(json.loads((ROOT/'examples/workbench-v36.json').read_text()),ROOT/'examples');self.assertEqual(len(p['layers']),10);self.assertFalse(audit(p));self.assertEqual(len(p['layers'][4]['softbody']['events']),2)
 def test_all_actions(self):
  configs={'fade':('a',{'from':0,'to':1}),'slide':('a',{'from':[0,0],'to':[10,20]}),'zoom':('a',{'from':1,'to':2}),'turn':('a',{'from':0,'to':90}),'tilt':('a',{'from':[0,0],'to':[10,20]}),'reveal':('a',{'from':0,'to':1}),'wipe':('a',{'from':0,'to':1,'mask':'iris'}),'trace':('path',{'from':0,'to':1}),'morph':('solid',{'from':0,'to':1}),'light_sweep':('solid',{'from':0,'to':1}),'pulse':('a',{'from':1,'amount':1.2}),'orbit':('a',{'center':[360,640],'radius':[50,20],'degrees':[0,180]}),'elastic':('solid',{'preset':'jelly_soft','strength':.5}),'handoff':('a',{'target':'b'}),'curve':('a',{'points':[[0,0],[20,0],[20,30],[40,30]]}),'stretch':('a',{'from':[1,1],'to':[1.2,.8]}),'bend':('solid',{'from':0,'to':.4}),'twist':('solid',{'from':0,'to':.7}),'refraction':('solid',{'from':1.4,'to':1.6}),'roughness':('solid',{'from':.2,'to':.4})}
  self.assertEqual(set(configs),set(OPS))
  for op,(l,kw) in configs.items():
   with self.subTest(op=op):
    s=self.spec();s['actions']=[self.action(op,l,**kw)];p,n=compile_spec(s,ROOT);self.assertFalse(audit(p))
 def test_typo(self):
  s=self.spec();s['layers'][0]['rotat']=20
  with self.assertRaisesRegex(ValueError,'rotat'):compile_spec(s,ROOT)
 def test_bad_action(self):
  s=self.spec();s['actions']=[self.action('fade',**{'from':0,'to':2})]
  with self.assertRaises(ValueError):compile_spec(s,ROOT)
 def test_incompatible(self):
  s=self.spec();s['actions']=[self.action('morph',**{'from':0,'to':1})]
  with self.assertRaisesRegex(ValueError,'unsupported'):compile_spec(s,ROOT)
 def test_authored_collision(self):
  s=self.spec();s['layers'][0]['scale']=[[0,1],[1,2]];s['actions']=[self.action('zoom',**{'from':1,'to':2})]
  with self.assertRaisesRegex(ValueError,'authored track'):compile_spec(s,ROOT)
 def test_overlap(self):
  s=self.spec();s['actions']=[self.action('zoom',**{'from':1,'to':2}),dict(op='zoom',layer='a',start=.5,end=2,**{'from':2,'to':3})]
  with self.assertRaisesRegex(ValueError,'overlapping'):compile_spec(s,ROOT)
 def test_gap(self):
  s=self.spec();s['actions']=[self.action('zoom',**{'from':1,'to':2}),dict(op='zoom',layer='a',start=2,end=3,**{'from':2,'to':3})];p,_=compile_spec(s,ROOT);self.assertEqual(val(p['layers'][0]['scale'],1.5),2)
 def test_wrong_anchor(self):
  s=self.spec();s['layers'][1]['x']=500;s['actions']=[self.action('handoff',target='b')]
  with self.assertRaisesRegex(ValueError,'anchors'):compile_spec(s,ROOT)
 def test_revise(self):
  p,_=compile_spec(self.spec(),ROOT);before=copy.deepcopy(p);out,r=revise(p,{'reason':'size','changes':[{'layer':'a','set':{'w':300}}]},ROOT);self.assertEqual(p,before);self.assertEqual(out['layers'][1:],p['layers'][1:]);self.assertEqual(out['layers'][0]['w'],300);self.assertEqual(r[0]['changed'],['w'])
 def test_protected(self):
  p,_=compile_spec(self.spec(),ROOT)
  for field in ('active','src','kind','unknown'):
   with self.assertRaises(ValueError):revise(p,{'reason':'bad','changes':[{'layer':'a','set':{field:0}}]},ROOT)
 def test_route_paths(self):
  from agent_route import ROUTES,route
  for task in ROUTES:
   r=route(task,ROOT/'work');self.assertTrue(all(Path(x).is_file() for x in [r['read_first']]+r['only_needed_guides']))
 def test_dimension(self):
  s=self.spec();s['layers'][0]['w']=-2
  with self.assertRaisesRegex(ValueError,'dimension'):compile_spec(s,ROOT)
 def test_completed_anchor(self):
  s=self.spec();s['actions']=[self.action('handoff',target='b'),dict(op='slide',layer='b',start=.1,end=.9,**{'from':[360,640],'to':[560,640]})]
  with self.assertRaisesRegex(ValueError,'anchors'):compile_spec(s,ROOT)
 def test_frame(self):
  s=self.spec();s['width']=180;s['layers']=s['layers'][:2];s['actions']=[self.action('handoff',target='b')];p,_=compile_spec(s,ROOT);e=Engine(p,ROOT);self.assertEqual(e.frame(.5).shape,(320,180,3));self.assertNotEqual(e.frame(0).tobytes(),e.frame(1.5).tobytes())
if __name__=='__main__':unittest.main()
