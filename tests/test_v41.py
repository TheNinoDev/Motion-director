import copy,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'starter/composite_film')]
from director_v41 import build,expand,layout_instances
from scene_audit_v41 import audit,repair,world
from production_v41 import start,next_step
from production_v40 import gate
from agent_session import sha
from compositor import val,validate
class V41(unittest.TestCase):
 def spec(self):return json.loads((ROOT/'examples/director-v41.json').read_text())
 def plan(self):return build(self.spec(),ROOT/'examples')[0]
 def test_instances_and_local_clock(self):
  p,e,_=build(self.spec(),ROOT/'examples');by={x['id']:x for x in p['layers']};self.assertEqual(len(e['component_map']),4);self.assertEqual(by['first__value']['text'],'Focus');self.assertEqual(by['second__value']['text'],'Build');self.assertAlmostEqual(by['third__base']['opacity'][0][0],.38);self.assertEqual(by['third__base']['parent'],'third');self.assertAlmostEqual(val(by['first']['y'],.12),490)
 def test_grid_centers_incomplete_row(self):
  a=layout_instances([dict(layout='grid',component='c',center=[0,0],columns=2,spacing=[10,20],items=[{'id':x} for x in 'abc'])]);self.assertEqual([(x['x'],x['y']) for x in a],[(-5,-10),(5,-10),(0,10)])
 def test_radial_and_arc(self):
  common=dict(component='c',center=[5,7],radius=[2,4],angle=0,items=[{'id':x} for x in 'abcd']);a=layout_instances([dict(layout='radial',**common)]);self.assertAlmostEqual(a[1]['y'],11);self.assertAlmostEqual(a[2]['x'],3);b=layout_instances([dict(layout='arc',spread=180,**common)]);self.assertAlmostEqual(b[0]['y'],3);self.assertAlmostEqual(b[-1]['y'],11)
 def test_reference_isolation(self):
  s=self.spec();s['components']['card']['layers'][1]['matte']='base';p,_,_=build(s,ROOT/'examples');by={x['id']:x for x in p['layers']};self.assertEqual(by['second__stripe']['matte'],'second__base')
 def test_reject_malformed(self):
  s=self.spec();s['instance_layouts'][0]['items'][0]['overrides']['value']['active']=[0,1];self.assertRaises(ValueError,expand,s)
  s=self.spec();s['instance_layouts'][0]['items'][1]['id']='first';self.assertRaises(ValueError,expand,s)
  s=self.spec();s['components']['card']['layers'][0]['opacity']=[[0,0],[5,1]];self.assertRaises(ValueError,expand,s)
 def test_parent_transform(self):
  p=self.plan();by={l['id']:l for l in p['layers']};M,op=world(by['first__stripe'],by,1.2);self.assertAlmostEqual(M[0,2],360-.93*187);self.assertAlmostEqual(M[1,2],val(by['first']['y'],1.2));self.assertGreater(op,.95)
 def test_parent_repair(self):
  p=self.plan();by={l['id']:l for l in p['layers']};by['first']['active'][0]=.7;r=audit(p);q=next(x for x in r['repairs'] if x['id']=='extend:first');self.assertAlmostEqual(q['after'][0],.12);self.assertTrue(any(x['parent_hidden_frames'] for x in r['layers'] if x['layer'].startswith('first__')))
  with tempfile.TemporaryDirectory() as d:
   a=Path(d)/'p.json';b=Path(d)/'r.json';a.write_text(json.dumps(p));old=sha(a);self.assertRaises(ValueError,repair,a,b,['extend:first'],'bad');res=repair(a,b,['extend:first'],old);self.assertEqual(sha(a),old);self.assertFalse(any(x['id']=='extend:first' for x in res['remaining']));self.assertRaises(FileExistsError,repair,a,b,['extend:first'],old)
 def test_offscreen(self):
  p=self.plan();by={l['id']:l for l in p['layers']};by['first']['x']=5000;r=audit(p);self.assertGreater(next(x for x in r['layers'] if x['layer']=='first__base')['offscreen_bounds_frames'],0)
 def test_production_next(self):
  with tempfile.TemporaryDirectory() as d:
   w=Path(d)/'session';r=start(ROOT/'examples/director-v41.json',ROOT/'examples/creative-v41.json',w);self.assertTrue((w/'scene-audit.json').exists());self.assertEqual(next_step(w)['stage'],'preview');self.assertFalse(gate(w)['ready']);(w/'preview').mkdir();self.assertEqual(next_step(w)['stage'],'blocked')
if __name__=='__main__':unittest.main()
