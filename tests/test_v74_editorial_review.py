"""Tests of v74's factual QA coverage and authoring contract, not 'creative quality'."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from two_frame_finish_v74 import analyze, build_pages, diffs
from ensemble_story_audit_v74 import validate


class EditorialReviewTests(unittest.TestCase):
    def test_example_causality_and_handoff(self):
        data=json.loads((ROOT/'examples/ensemble-motion-v74.json').read_text(encoding='utf8'))
        result=validate(data)
        self.assertTrue(result['ok'], result['errors'])
        self.assertEqual(result['scenes'],3)

    def test_rejects_slide_with_no_reaction_or_bridge(self):
        bad={'scenes':[{'id':'intro','start':0,'end':3,'visual_cause':'Text appears and remains static',
            'primary_action':'Static icon appears in the middle',
            'secondary_reaction':'Nothing happens whatsoever',
            'result':'The same finished slide stays static',
            'text_role':'A headline repeats the spoken words',
            'elements':[{'id':'icon','role':'actor'}],
            'handoff':{}}, {'id':'next','start':3,'end':5}]}
        result=validate(bad)
        self.assertFalse(result['ok'])
        self.assertTrue(any('responding element' in x for x in result['errors']))
        self.assertTrue(any('handoff anchor' in x for x in result['errors']))

    def test_2_frame_order_and_count(self):
        x=np.zeros((266,150,3),dtype=np.uint8)
        frames=[(i,np.full_like(x,i,dtype=np.uint8)) for i in [0,2,4,6,8,10]]
        with tempfile.TemporaryDirectory() as d:
            pages=build_pages(frames,12,Path(d),per_page=4,cols=2)
            self.assertEqual(len(pages),2)
            self.assertTrue(all((Path(d)/n).is_file() for n in pages))
            data=diffs(frames,12,2)
            self.assertEqual(data['analyzed_pairs'],5)

    def test_real_ffmpeg_decoding_and_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp);v=path/'test.mp4';width=160;height=284
            frames=[]
            for k in range(12):
                frame=np.zeros((height,width,3),dtype='uint8')
                frame[:,:]=[10+k*4, 30, 50]
                frame[80:180,30+k:60+k,0]=255
                frames.append(frame.tobytes())
            raw=b''.join(frames)
            p=subprocess.run(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
                '-s',f'{width}x{height}','-r','12','-i','-', '-c:v','libx264','-pix_fmt','yuv420p',str(v)],input=raw,capture_output=True)
            self.assertEqual(p.returncode,0,p.stderr.decode())
            report=analyze(v,path/'review',every=2,per_page=4)
            self.assertEqual(report['decoded_source_frames'],12)
            self.assertEqual(report['sampled_frames'],6)
            self.assertEqual(report['expected_sampled_frames'],6)
            self.assertEqual(report['total_pages'],2)
            self.assertEqual(report['last_sampled_source_frame'],10)
            self.assertFalse(report['visual_review_done'])
            self.assertTrue((path/'review/review.json').exists())
            self.assertEqual(len(report['sha256']),64)

    def test_plan_seam_contact_sheet(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp);v=path/'test.mp4'
            p=subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi',
               '-i','testsrc=size=160x284:rate=12:duration=2',
               '-c:v','libx264','-pix_fmt','yuv420p',str(v)],capture_output=True)
            self.assertEqual(p.returncode,0,p.stderr.decode())
            report=analyze(v,path/'out',every=2,plan={'shots':[{'end':1.0},{'end':2.0}]})
            self.assertEqual(len(report['seam_review']['pages']),1)
            self.assertTrue((path/'out/seam-neighborhoods'/report['seam_review']['pages'][0]).is_file())


if __name__=='__main__':unittest.main()
