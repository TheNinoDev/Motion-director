import sys,unittest,json,tempfile,copy
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'starter/composite_film'))
from director_v46 import build
from compositor import val
from production_v46 import start,next_step,gate,check_audio
from event_audio_v46 import make,decode,wav
from agent_session import sha

class V46(unittest.TestCase):
 def spec(self):return json.loads((ROOT/'examples/director-v46.json').read_text())
 def compile(self,s=None):return build(s if s is not None else self.spec(),ROOT/'examples')
 def test_cues_and_reactions(self):
  p,e,_=self.compile();self.assertEqual(len(e['sound_cues']),6);self.assertEqual(len(e['event_reactions']),3)
  for c in e['sound_cues']:self.assertLessEqual(abs(c['frame']/p['fps']-e['gesture_events'][c['event']]['time']),.5/p['fps']+1e-8)
  halo=next(x for x in p['layers'] if x['id']=='halo1');t=e['gesture_events'][2]['time'];self.assertAlmostEqual(val(halo['opacity'],t+.24),.8);self.assertAlmostEqual(val(halo['opacity'],t+.48),0)
 def test_retime(self):
  s=self.spec();s['gestures'][0]['steps'][2]['end']=3.7;p,e,_=self.compile(s);a=e['gesture_events'][2]['time'];self.assertGreater(a,3.372);self.assertEqual(e['sound_cues'][2]['frame'],round(a*30));self.assertAlmostEqual(val(next(x for x in p['layers'] if x['id']=='halo1')['opacity'],a+.24),.8)
 def test_identity(self):
  s=self.spec();s['event_reactions'][0]['expect_target']='card2';self.assertRaises(ValueError,self.compile,s)
 def test_collision(self):
  s=self.spec();s['event_reactions'][0]['layer']='card1';s['event_reactions'][0]['values']={'scale':.1};self.assertRaises(ValueError,self.compile,s)
 def test_duration(self):
  s=self.spec();s['event_sounds'][5]['duration']=4;self.assertRaises(ValueError,self.compile,s)
 def test_duplicate(self):
  s=self.spec();s['event_sounds'].append(copy.deepcopy(s['event_sounds'][0]));self.assertRaises(ValueError,self.compile,s)
 def test_immutable(self):
  s=self.spec();b=copy.deepcopy(s);self.compile(s);self.assertEqual(s,b)
 def test_stem_deterministic(self):
  p,e,_=self.compile()
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);a=d/'a';b=d/'b';a.mkdir();b.mkdir();make(p,e['sound_cues'],a);make(p,e['sound_cues'],b);self.assertEqual(sha(a/'event-sfx.wav'),sha(b/'event-sfx.wav'));x=decode(a/'mix-v46.wav');self.assertEqual(x.shape,(432000,2));self.assertGreater(float(np.max(abs(x))),.01);self.assertLess(float(np.max(abs(x))),.9)
 def test_bad_bed(self):
  p,e,_=self.compile()
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);wav(d/'short.wav',np.zeros((4800,2)));self.assertRaises(ValueError,make,p,e['sound_cues'],d,d/'short.wav')
 def test_start_and_integrity(self):
  with tempfile.TemporaryDirectory() as d:
   w=Path(d)/'work';start(ROOT/'examples/director-v46.json',ROOT/'examples/creative-v46.json',w);self.assertEqual(next_step(w)['stage'],'preview');self.assertFalse(gate(w)['ready']);(w/'event-sfx.wav').write_bytes(b'changed');self.assertFalse(check_audio(w)['valid'])
 def test_ad_fx_not_audio_replacement(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);c=json.loads((ROOT/'examples/creative-v46.json').read_text());c['mode']='advertisement';(d/'c.json').write_text(json.dumps(c));self.assertRaisesRegex(ValueError,'actual authorized',start,ROOT/'examples/director-v46.json',d/'c.json',d/'work')
if __name__=='__main__':unittest.main()
