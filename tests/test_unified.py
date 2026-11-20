"""Lightweight runnable regression tests for unified production (no paid APIs)."""
import json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PRODUCTION=ROOT/'starter/unified/production.py'

def basic():
    return {'version':1,'width':160,'height':280,'fps':10,'shots':[
        {'id':'a','engine':'type','frames':10,'content':{'kind':'hero','text':'HEY','chrome':False}},
        {'id':'b','engine':'type','frames':10,'transition_in':{'kind':'dissolve','frames':2},'content':{'kind':'hero','text':'NOW','chrome':False}}]}

def run(*args):return subprocess.run([sys.executable,str(PRODUCTION),*map(str,args)],capture_output=True,text=True)

@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg required')
class UnifiedTests(unittest.TestCase):
    def test_preflight_and_missing_voice(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'plan.json';p.write_text(json.dumps(basic()))
            self.assertEqual(run(p,'--check').returncode,0)
            x=run(p,'--final');self.assertNotEqual(x.returncode,0);self.assertIn('voiceover',x.stderr.lower())

    def test_duplicate_id_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            d=basic();d['shots'][1]['id']='a';p=Path(td)/'plan.json';p.write_text(json.dumps(d))
            x=run(p,'--check');self.assertNotEqual(x.returncode,0);self.assertIn('Duplicate',x.stderr)

    def test_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            d=basic();d['shots'][1]={'id':'b','engine':'clip','frames':10,'src':'../other.mp4'}
            p=Path(td)/'plan.json';p.write_text(json.dumps(d));x=run(p,'--check')
            self.assertNotEqual(x.returncode,0);self.assertIn('outside project',x.stderr)

    def test_transition_and_cache(self):
        with tempfile.TemporaryDirectory() as td:
            t=Path(td);p=t/'plan.json';p.write_text(json.dumps(basic()))
            a=run(p,'--build-dir',t/'build','--preview');self.assertEqual(a.returncode,0,a.stderr+a.stdout)
            d=json.loads((t/'build'/'report.json').read_text());self.assertEqual(d['frames'],18);self.assertFalse(d['has_audio'])
            b=run(p,'--build-dir',t/'build','--preview');self.assertEqual(b.returncode,0,b.stderr+b.stdout)
            d2=json.loads((t/'build'/'report.json').read_text());self.assertEqual(d2['cached_shots'],2)

    def test_real_audio_mix_pipeline_uses_test_tones(self):
        with tempfile.TemporaryDirectory() as td:
            t=Path(td);d=basic();d['audio']={'voice':'voice.wav','music':'music.mp3','music_volume':.1}
            p=t/'plan.json';p.write_text(json.dumps(d))
            for name,frequency,duration in [('voice.wav',260,1.5),('music.mp3',400,0.8)]:
                cmd=['ffmpeg','-v','error','-y','-f','lavfi','-i',f'sine=frequency={frequency}:duration={duration}',t/name]
                subprocess.run([str(x) for x in cmd],check=True)
            x=run(p,'--build-dir',t/'build','--final');self.assertEqual(x.returncode,0,x.stderr+x.stdout)
            report=json.loads((t/'build'/'report.json').read_text());self.assertEqual(report['status'],'technical_export_complete');self.assertTrue(report['has_audio'])

if __name__=='__main__':unittest.main()
