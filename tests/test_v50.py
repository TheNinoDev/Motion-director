import copy,json,math,struct,sys,tempfile,unittest,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'starter/composite_film')]
import preproduction_v50 as p
import production_v50 as prod

def tone(f,hz):
 with wave.open(str(f),'wb') as w:
  w.setparams((1,2,8000,0,'NONE','not compressed'));w.writeframes(b''.join(struct.pack('<h',int(1000*math.sin(2*math.pi*hz*i/8000))) for i in range(24000)))

class V50(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.m=self.root/'brief.json';self.performance=self.root/'performance.json';self.voice=self.root/'voice.wav';self.music=self.root/'music.wav'
  self.d=p.read(ROOT/'templates/preproduction-v50.json');self.perf=p.read(ROOT/'templates/performance-v50.json');self.d['brief'].update(product_name='Fictional test',product_source='Test fixture',focus='Find the correct version',audience='Test audience',language='English',platforms=['test'],use_scope='commercial',voice_route='elevenlabs',music_route='supplied');self.d['script_decision']='delegated';self.d['audio_delivery']={'mode':'agent_acquired','observation':'Fixture only'};p.put(self.performance,self.perf);p.put(self.m,self.d)
 def tearDown(self):self.tmp.cleanup()
 def save(self):p.put(self.m,self.d);p.put(self.performance,self.perf)
 def ready(self):
  tone(self.voice,400);tone(self.music,120)
  for k in ('voice','music'):self.d['audio'][k].update(path=k+'.wav',rights_status='cleared',rights_evidence='Synthetic test fixture; not an actual authorization',audition_observation='Synthetic fixture, validation only')
  self.d['audio']['voice']['scratch']=False # only exercising the gate; not a real speech take
  al={'voice_sha256':p.sha(self.voice),'method':'manual_listen_verified','phrases':[{'text':x['text'],'start':i,'end':i+.8} for i,x in enumerate(self.perf['beats'])]};p.put(self.root/'alignment.json',al);self.save()
 def test_blank_brief(self):
  p.put(self.m,p.read(ROOT/'templates/preproduction-v50.json'));r=p.check(self.m);self.assertEqual(r['stage'],'briefing');self.assertEqual(len(r['questions']),9)
 def test_empty_script(self):
  self.performance.unlink();self.assertEqual(p.check(self.m)['stage'],'write_script')
 def test_no_untagged_expressive(self):
  for b in self.perf['beats']:b['cue']='neutral'
  self.save();self.assertEqual(p.check(self.m)['stage'],'rewrite_script')
 def test_correct_provider(self):
  self.d['brief']['voice_route']='fish';self.save();self.assertEqual(p.check(self.m)['stage'],'rewrite_script')
 def test_tags_separate(self):
  r=p.script_review(self.perf,self.d['brief']);self.assertFalse(r['errors']);self.assertEqual(r['tags'],3);self.assertIn('[curious]',r['tagged']);self.assertNotIn('[',r['clean']);self.assertEqual(r['clean'],self.perf['locked_text'])
 def test_handoff(self):
  self.d['brief']['voice_design']='holographic_new';r=p.script_review(self.perf,self.d['brief']);h=p.handoff(self.d['brief'],self.perf,r);self.assertIn('Project Capricorn',h);self.assertIn('[curious]',h);self.assertIn('Export the original WAV or MP3',h);self.assertIn('No screen recording',h)
 def test_music_selection(self):
  self.d['brief']['music_route']='research';self.save();self.assertEqual(p.check(self.m)['stage'],'music_selection');self.d['music_selection']={'track':'Fixture','version':'test','source_url':'https://example.com','rights_evidence':'fixture','acquisition_steps':'fixture','selection_basis':'fixture','trending':True};self.save();self.assertEqual(p.check(self.m)['stage'],'music_selection')
 def test_handoff_required(self):
  self.d['audio_delivery']={};self.save();self.assertEqual(p.check(self.m)['stage'],'prepare_audio_handoff')
 def test_handoff_stale(self):
  self.d['audio_delivery']={'mode':'user_handoff','observation':'Fixture only','handoff_dir':'handoff'};self.save();self.assertEqual(p.check(self.m)['stage'],'prepare_audio_handoff')
 def test_no_audio(self):self.assertEqual(p.check(self.m)['stage'],'audio_handoff_or_review')
 def test_ready_and_mix(self):
  self.ready();self.assertTrue(p.check(self.m,True)['ready']);out=self.root/'bed.wav';r=p.mix(self.m,out,3.2);self.assertEqual(r['mix_sha256'],p.sha(out));self.assertAlmostEqual(p.probe(out)['duration_seconds'],3.2,places=2)
 def test_stale_alignment(self):
  self.ready();tone(self.voice,600);self.assertEqual(p.check(self.m)['stage'],'alignment')
 def test_scratch_blocked(self):
  self.ready();self.d['audio']['voice']['scratch']=True;self.save();self.assertFalse(p.check(self.m,True)['ready'])
 def test_private_no_release(self):
  self.ready();self.d['brief']['use_scope']='private-preview';self.save();self.assertFalse(p.check(self.m,True)['ready'])
 def test_ad_requires_preproduction(self):
  c=p.read(ROOT/'examples/creative-v49.json');c['mode']='advertisement';cf=self.root/'creative.json';p.put(cf,c)
  with self.assertRaisesRegex(ValueError,'No preproduction'):prod.start(ROOT/'examples/director-v49.json',cf,self.root/'session')
 def test_static_beat_rejected(self):
  plan={'fps':30,'layers':[{'id':'t','kind':'text','active':[0,3],'opacity':[[0,0],[1,1]]}]};creative={'mode':'advertisement','beats':[{'start':0,'end':3,'layer_ids':['t'],'layout':'title','direction':{'subject_layer':'t','operation':'fade','before':'nothing','after':'text','why':'fixture','transition':'cut'}}]};self.assertTrue(prod.coverage(plan,creative)['errors'])
 def test_study_legacy(self):
  w=self.root/'study';r=prod.start(ROOT/'examples/director-v49.json',ROOT/'examples/creative-v49.json',w);self.assertFalse(r['preproduction_locked']);self.assertEqual(prod.next_step(w)['stage'],'preview');self.assertFalse(prod.gate(w)['ready'])
if __name__=='__main__':unittest.main()
