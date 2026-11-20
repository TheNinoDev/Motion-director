import json,sys,unittest,tempfile,copy,wave
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'starter/composite_film'))
from compositor import Engine,validate,val
from recipes import resample,morph_path,bezier
from music_cues import analyze,snap
from mix_picture import mix_picture

class TestV27(unittest.TestCase):
 def plan(self,layers):return dict(width=180,height=320,fps=30,duration=2,background='#000000',layers=layers)
 def box(self,id,**kw):return dict(kind='rect',id=id,active=[0,2],x=360,y=640,w=200,h=200,color='#ff0000',**kw)
 def test_tracks(self):
  self.assertEqual(val([[0,0],[1,10,'linear']],.4),4);self.assertEqual(val([[0,0],[1,10,'out']],1),10)
 def test_duplicate(self):
  with self.assertRaises(ValueError):validate(self.plan([self.box('x'),self.box('x')]),ROOT)
 def test_bad_track(self):
  l=self.box('bad');l['x']=[[1,1],[0,0]]
  with self.assertRaises(ValueError):validate(self.plan([l]),ROOT)
 def test_parent(self):
  l=self.box('child',parent='root');l['x']=0;l['y']=0
  p=self.plan([dict(id='root',kind='group',active=[0,2],x=[[0,180],[2,540,'linear']],y=640),l]);e=Engine(validate(p,ROOT),ROOT);self.assertGreater(e.frame(.1)[160,45,0],200);self.assertGreater(e.frame(1.9)[160,135,0],200)
 def test_matte(self):
  m=dict(id='matte',kind='ellipse',active=[0,2],x=360,y=640,w=100,h=100,color='#ffffff',matte_only=True);p=self.plan([m,self.box('box',matte='matte')]);e=Engine(validate(p,ROOT),ROOT);f=e.frame(.5);self.assertGreater(f[160,90,0],200);self.assertEqual(f[160,110,0],0)
 def test_invert(self):
  m=dict(id='matte',kind='ellipse',active=[0,2],x=360,y=640,w=100,h=100,color='#ffffff',matte_only=True);p=self.plan([m,self.box('box',matte='matte',matte_mode='alpha_invert')]);e=Engine(validate(p,ROOT),ROOT);f=e.frame(.5);self.assertEqual(f[160,90,0],0);self.assertGreater(f[160,110,0],200)
 def test_morph(self):
  l=morph_path('path',[0,2],[(0,[[0,300],[720,300]]),(2,[[0,900],[720,900]])]);e=Engine(validate(self.plan([l]),ROOT),ROOT);self.assertGreater(np.abs(e.frame(.1).astype(float)-e.frame(1.9)).sum(),1000)
 def test_curve(self):
  p=bezier([0,0],[0,10],[10,10],[10,0]);self.assertEqual(p[0],[0,0]);self.assertEqual(p[-1],[10,0]);self.assertEqual(len(resample(p,30)),30)
 def test_shutter(self):
  l=self.box('moving');l['x']=[[0,100],[2,620,'linear']];p=self.plan([l]);p['shutter_windows']=[[0,2]];e=Engine(validate(p,ROOT),ROOT);f=e.render_frame(1,2);self.assertEqual(f.shape,(320,180,3));self.assertTrue(f.max()>0)
 def test_music_and_sfx(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'bed.wav';x=np.zeros((96000,2),np.int16);x[24000:24500]=15000;x[72000:72500]=-15000
   with wave.open(str(f),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(x.tobytes())
   a=analyze(f);self.assertTrue(len(a['cues'])>=1);self.assertEqual(snap(0,[],.1),0)
   out=Path(d)/'out.wav';events=mix_picture(f,{'fps':30,'duration':2,'sound_events':[{'time':.5,'kind':'click','gain_db':-20}]},out);self.assertEqual(events[0]['frame'],15);self.assertTrue(out.exists())
 def test_demo_matte_plan(self):
  f=ROOT/'starter/composite_film/technique-demo.json';p=validate(json.loads(f.read_text()),f.parent);p['width']=180;p['height']=320;e=Engine(p,f.parent);self.assertGreater(e.frame(.9).max(),0)
if __name__=='__main__':unittest.main()
