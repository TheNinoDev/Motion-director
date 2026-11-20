import importlib.util,sys,json,tempfile,unittest,subprocess,shutil
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
FONT=next((str(p) for p in map(Path,['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','C:/Windows/Fonts/arialbd.ttf','/System/Library/Fonts/Supplemental/Arial Bold.ttf']) if p.exists()),None)
def load(name,rel):
    spec=importlib.util.spec_from_file_location(name,ROOT/rel);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
r=load('layer15','starter/layer_motion/render.py');fx=load('effects15','starter/layer_motion/effects.py');c=load('choreo15','starter/choreography/compile.py');s=load('sfx15','starter/sound_design/render.py')
@unittest.skipUnless(FONT,'system font required')
class EffectsTests(unittest.TestCase):
    def test_sdf_morph_endpoint_shapes_and_midpoint(self):
        a=dict(kind='morph',id='shape',size=[400,400],color='#ffffff',**{'from':'circle','to':'square'})
        dy=fx.Dynamic(a,.5,FONT,(255,255,255,255));x,y,z=[dy.sample(t)[:,:,3] for t in (0,.5,1)]
        self.assertTrue((x>127).any() and (x==0).any());self.assertGreater((z>127).sum(),(x>127).sum());self.assertFalse(np.array_equal(x,y));self.assertFalse(np.array_equal(y,z))
    def test_swarm_is_deterministic_and_animated(self):
        a=dict(kind='swarm',id='cloud',size=[400,400],**{'from':'grid','to':'text'},text='FORM',count=160,seed=3)
        d=fx.Dynamic(a,.5,FONT,(60,255,200,255));d2=fx.Dynamic(a,.5,FONT,(60,255,200,255));self.assertTrue(np.array_equal(d.sample(.5),d2.sample(.5)));self.assertFalse(np.array_equal(d.sample(0),d.sample(1)))
    def test_shutter_integrates_linear_not_gamma(self):
        def unit(f):return np.full((3,3,3),255 if f>=1 else 0,np.uint8)
        out=fx.shutter(unit,1,3,2,1);self.assertTrue(np.all(np.abs(out.astype(float)-188)<=1));self.assertTrue(np.all(fx.shutter(unit,1,3,1,1)==255))
    def test_dynamic_layers_render_with_subframe_shutter(self):
        l=dict(kind='morph',id='a',size=[450,450],**{'from':'star','to':'text'},text='A',progress=[[0,0],[9,1]],x=[[0,310],[9,770]])
        sc=r.Scene(180,320,dict(frames=10,samples=3,shutter=.8,layers=[l]),FONT);a=sc.render_frame(0);b=sc.render_frame(9);self.assertEqual(a.shape,(320,180,3));self.assertFalse(np.array_equal(a,b))
        bad=dict(l,**{'to':'not-shape'});
        with self.assertRaises(ValueError):r.validate(dict(frames=10,layers=[bad]))
    def test_compiler_rescales_keyframes_and_validates(self):
        d=c.build('FORM','Your work','One space','Discover','image.png',frames=(51,63,90),width=180,height=320)
        self.assertEqual(sum(x['frames'] for x in d['shots'])-6,198);self.assertEqual(len(d['shots']),3)
        with self.assertRaises(ValueError):c.build('FORM','a','b','c','a.png',frames=(10,20,30))
    def test_layout_review_and_conservative_repair(self):
        m=load('layout15','scripts/layout_geometry.py');d={'version':1,'width':180,'height':320,'fps':30,'shots':[{'id':'static','engine':'layers','frames':30,'content':{'layers':[{'id':'overflow','kind':'text','text':'VERY WIDE','font_size':100,'x':1000,'y':800,'size':[750,180]}]}}]}
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'plan.json';p.write_text(json.dumps(d));rep,fix=m.inspect(p,True);self.assertEqual(len(rep['issues']),1);self.assertEqual(len(rep['repairs']),1);p.write_text(json.dumps(fix));after,_=m.inspect(p);self.assertFalse(after['issues'])
class AudioTests(unittest.TestCase):
    def test_sfx_is_sample_accurate(self):
        plan={'fps':30,'frames':30,'events':[{'frame':10,'kind':'click','duration_frames':4,'pan':.4}]};a=s.render(plan);self.assertEqual(a.shape,(48000,2));self.assertFalse(a[:16000].any());self.assertTrue(a[16000:22400].any());self.assertFalse(a[22400:].any());self.assertTrue(np.array_equal(a,s.render(plan)))
    def test_all_sfx_kinds_are_finite(self):
        for kind in s.KINDS:
            a=s.render({'fps':30,'frames':30,'events':[{'frame':0,'kind':kind,'duration_frames':20}]});self.assertTrue(np.isfinite(a).all());self.assertGreater(np.max(np.abs(a)),0);self.assertLessEqual(np.max(np.abs(a)),.75)
    def test_out_of_range_cue(self):
        with self.assertRaises(ValueError):s.render({'fps':30,'frames':30,'events':[{'frame':29,'kind':'impact','duration_frames':4}]})
@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'ffmpeg required')
class IntegrationTests(unittest.TestCase):
    def test_new_transition_and_sfx_preview(self):
        with tempfile.TemporaryDirectory() as td:
            t=Path(td);d={'version':1,'width':180,'height':320,'fps':15,'audio':{'sfx':'sfx.wav'},'shots':[{'id':'one','frames':10,'engine':'type','content':{'kind':'hero','text':'ONE','chrome':False}},{'id':'two','frames':10,'engine':'type','transition_in':{'kind':'circleclose','frames':3},'content':{'kind':'hero','text':'TWO','chrome':False}}]}
            s.write({'fps':15,'frames':17,'events':[{'frame':7,'duration_frames':5,'kind':'whoosh'}]},t/'sfx.wav');p=t/'project.json';p.write_text(json.dumps(d));cmd=[sys.executable,str(ROOT/'starter/unified/production.py'),str(p),'--preview','--build-dir',str(t/'build')];a=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(a.returncode,0,a.stdout+a.stderr);report=json.loads((t/'build'/'report.json').read_text());self.assertEqual(report['frames'],17);self.assertTrue(report['has_audio']);self.assertEqual(report['status'],'PREVIEW_ONLY')
if __name__=='__main__':unittest.main()
