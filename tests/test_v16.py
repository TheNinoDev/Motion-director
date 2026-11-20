import importlib.util,sys,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
FONT=next((str(p) for p in map(Path,['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','C:/Windows/Fonts/arialbd.ttf','/System/Library/Fonts/Supplemental/Arial Bold.ttf']) if p.exists()),None)
def load(name,rel):
    s=importlib.util.spec_from_file_location(name,ROOT/rel);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
r=load('layer16','starter/layer_motion/render.py');o=load('optical16','starter/layer_motion/optical.py');c=load('compile16','starter/polish/compile.py');a=load('audio16','starter/polish/audio_reactive.py')
class TestOptics(unittest.TestCase):
    def test_all_eight_effects_render_and_move(self):
        for k in sorted(o.KINDS):
            with self.subTest(kind=k):
                d=dict(kind=k,id='fx',size=[600,600],count=24);z=o.Optical(d,.3,(220,230,250,255));x=z.sample(.2,0);y=z.sample(.8,15);self.assertEqual(x.shape,(180,180,4));self.assertGreater(x[:,:,3].max(),0);self.assertFalse(np.array_equal(x,y));self.assertTrue(np.array_equal(y,z.sample(.8,15)))
    @unittest.skipUnless(FONT,'font unavailable')
    def test_each_style_and_compositing(self):
        for style in c.STYLES:
            d=c.build('FORM','Too many tabs?','One place','Discover',str(ROOT/'examples/assets/v15-workspace.png'),style=style,width=180,height=320,frames=(30,30,30,30));self.assertEqual(len(d['shots']),4)
            for s in d['shots']:
                scene=r.Scene(180,320,dict(s['content'],frames=s['frames']),FONT);x=scene.render_frame(15);self.assertEqual(x.shape,(320,180,3));self.assertGreater(x.std(),5)
    def test_bad_effect_parameters(self):
        for key,v in [('count',999),('speed',float('nan')),('distortion',-1)]:
            l=dict(id='f',kind='orbit',size=[300,300],**{key:v})
            with self.assertRaises(ValueError):r.validate(dict(frames=20,layers=[l]))
    @unittest.skipUnless(FONT,'font unavailable')
    def test_pitch_distortion_feather(self):
        l=dict(id='f',kind='rect',size=[450,450],color='#d2f777',distortion=18,feather=8,pitch=[[0,0],[20,45]],reveal=[[0,.25],[20,1]],reveal_axis='radial');s=r.Scene(180,320,dict(frames=21,layers=[l]),FONT);self.assertFalse(np.array_equal(s.render_frame(0),s.render_frame(20)))
    def test_audio_bake_uses_overlap_offset(self):
        d=c.build('FORM','HOOK','Benefit','CTA','image.png',frames=(30,30,30,30));env=np.linspace(0,1,116);b=a.bake(d,env,'end','echo','glow',.05,.15);v=b['shots'][-1]['content']['layers'][0]['glow'];self.assertAlmostEqual(v[0][1],.05+.15*env[86],places=5);self.assertAlmostEqual(v[-1][1],.2,places=5)
        with self.assertRaises(ValueError):a.bake(d,env,'end','brand','glow',.05,.1)
if __name__=='__main__':unittest.main()
