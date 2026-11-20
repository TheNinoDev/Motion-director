import unittest,importlib.util,json,tempfile,subprocess,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('editorial22',ROOT/'starter/editorial/render.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
FONT=next((str(p) for p in (Path('/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),Path('C:/Windows/Fonts/arialbd.ttf')) if p.is_file()),None)
SRC=str(ROOT/'examples/assets/v15-workspace.png')
class EditorialTest(unittest.TestCase):
 def test_validation(self):
  for c in [dict(kind='invalid'),dict(kind='wall',lines=[]),dict(kind='fold',src='missing'),dict(kind='signature',brand=''),dict(kind='wall',lines=['x'],density=13),dict(kind='wall',lines=['x'],progress=[[0,0],[0,1]]),dict(kind='wall',lines=['x'],samples=0),dict(kind='macro',src=SRC,crop=[.8,.1,.4,.5]),dict(kind='fold',src=SRC,bend=9)]:
   with self.assertRaises(ValueError):m.validate(dict(frames=20,**c))
 def test_interpolation(self):
  self.assertAlmostEqual(m.tr(dict(progress=[[0,0],[1,1,'out']]),'progress',.5,0),.875)
 @unittest.skipUnless(FONT,'no installed font')
 def test_every_kind(self):
  for kind in m.KINDS:
   with self.subTest(kind=kind):
    c=dict(kind=kind,frames=30,src=SRC,crop=[.05,.28,.51,.55],crop2=[.54,.28,.95,.55],text='Make room.',lines=['GOOD WORK.','IN VIEW.'],label='CONCEPT',sub='More space.',brand='F / FORM',repeat='WORK / ',grain=0)
    sh=m.Editorial(180,320,c,FONT);frames=[sh.frame(i) for i in (0,7,16,29)];self.assertEqual(frames[-1].shape,(320,180,3));self.assertGreater(frames[-1].std(),8);self.assertTrue(np.array_equal(sh.frame(16),frames[2]));self.assertFalse(np.array_equal(frames[0],frames[-1]))
 @unittest.skipUnless(FONT,'no installed font')
 def test_reveal_options(self):
  for style in ('slice','glyph','wipe','none'):
   sh=m.Editorial(180,320,dict(kind='poster',frames=30,lines=['A','B','C','D'],layout='right',reveal=style,samples=2,grain=0),FONT);self.assertGreater(sh.frame(29).std(),8)
 def test_preset_and_controller(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'plan.json';subprocess.run([sys.executable,str(ROOT/'starter/editorial/preset.py'),'--hook','Work','--tension','buried','--reveal','Found','--proof','Selected work','--brand','FORM','--cta','See it','--screenshot',SRC,'--crop','.05','.28','.51','.55','--crop2','.54','.28','.95','.55','--frames','10','11','12','13','14','--out',str(p)],check=True,capture_output=True);d=json.loads(p.read_text());self.assertEqual(sum(s['frames'] for s in d['shots']),60);subprocess.run([sys.executable,str(ROOT/'starter/unified/production.py'),str(p),'--check'],check=True,capture_output=True)
if __name__=='__main__':unittest.main()
