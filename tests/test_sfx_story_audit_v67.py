"""Regression for the scene/SFX plan and the real packaged procedural renderer."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('sfxaudit',ROOT/'scripts/sfx_story_audit_v67.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class SFXStoryTests(unittest.TestCase):
    def test_example_is_auditable_and_renderer_compatible(self):
        plan=json.loads((ROOT/'examples/sfx-story-v67.json').read_text())
        result=module.audit(plan)
        self.assertTrue(result['ok'],result['errors'])
        self.assertGreaterEqual(result['summary']['different_families'],7)
        self.assertGreaterEqual(result['summary']['sound_cues'],15)
        self.assertEqual(result['render_plan']['frames'],738)
        self.assertTrue(all(e['frame']+e['duration_frames']<=738 for e in result['render_plan']['events']))

    def test_missing_audio_intent_requires_reason(self):
        plan={'fps':30,'duration':2,'visual_events':[{'id':'hero','event':'contact','at':1,'visual_change':'button changes','audio_role':'silence'}]}
        result=module.audit(plan)
        self.assertFalse(result['ok'])
        self.assertTrue(any('reason' in e for e in result['errors']))

    def test_pre_lap_is_reviewed_not_blocked(self):
        plan={'fps':30,'duration':2,'visual_events':[{'id':'bridge','event':'bridge','at':1,'visual_change':'shape crosses','audio_role':'prelap','sounds':[{'kind':'sweep','at':1,'duration':.2,'gain_db':-20}]}]}
        result=module.audit(plan)
        self.assertTrue(result['ok'])
        self.assertTrue(any('prelap' in w for w in result['warnings']))

    def test_renderer_preserves_legacy_and_adds_distinct_kinds(self):
        import numpy as np
        spec=importlib.util.spec_from_file_location('mdsfx',ROOT/'starter/sound_design/render.py')
        renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
        self.assertTrue({'click','impact','whoosh','chime','riser','drop'}.issubset(renderer.KINDS))
        self.assertTrue({'snap','paper','brush','tick','rattle','glint','glitch','sweep','pulse'}.issubset(renderer.KINDS))
        samples=[]
        for kind in sorted(renderer.KINDS):
            a=renderer.sound(kind,round(.25*renderer.SR),np.random.default_rng(3))
            self.assertTrue(np.isfinite(a).all(),kind)
            self.assertGreater(np.max(np.abs(a)),.15,kind)
            self.assertLessEqual(np.max(np.abs(a)),1.00001,kind)
            samples.append(a)
        # Not all new kinds are identical: variation must be audible in principle.
        self.assertGreater(np.sqrt(np.mean((samples[0]-samples[1])**2)),.1)

    def test_roundtrip_original_stem(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)
            p=json.loads((ROOT/'examples/sfx-story-v67.json').read_text())
            res=module.audit(p)
            plan=out/'plan.json';wav=out/'sfx.wav'
            plan.write_text(json.dumps(res['render_plan']))
            r=subprocess.run([sys.executable,str(ROOT/'starter/sound_design/render.py'),str(plan),str(wav)],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertTrue(wav.is_file())
            import wave
            with wave.open(str(wav),'rb') as w:
                self.assertEqual(w.getnchannels(),2)
                self.assertEqual(w.getframerate(),48000)
                self.assertAlmostEqual(w.getnframes()/48000,24.6,places=2)

if __name__=='__main__':unittest.main()
