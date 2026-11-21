"""Tests for objective scene-cut sampling. Requires local ffmpeg, Pillow."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

@unittest.skipUnless(shutil.which('ffmpeg'), 'requires ffmpeg')
class TestSeamReview(unittest.TestCase):
    def test_three_solid_color_scenes(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td)
            video=td/'triptych.mp4'
            cmd=['ffmpeg','-hide_banner','-loglevel','error','-y',
                 '-f','lavfi','-i','color=c=red:s=160x284:r=30:d=1',
                 '-f','lavfi','-i','color=c=blue:s=160x284:r=30:d=1',
                 '-f','lavfi','-i','color=c=green:s=160x284:r=30:d=1',
                 '-filter_complex','[0:v][1:v][2:v]concat=n=3:v=1:a=0[out]',
                 '-map','[out]','-pix_fmt','yuv420p','-c:v','libx264',str(video)]
            subprocess.run(cmd,check=True)
            report=td/'report.json'; sheet=td/'sheet.png'
            run=subprocess.run([sys.executable,str(ROOT/'scripts/seam_review_v66.py'),str(video),
                               '--fps','10','--min-diff','8','--top','5','--report',str(report),'--sheet',str(sheet)],
                               capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            r=json.loads(report.read_text())
            times=[x['time_s'] for x in r['seams']]
            self.assertTrue(any(abs(t-1)<.21 for t in times),times)
            self.assertTrue(any(abs(t-2)<.21 for t in times),times)
            self.assertTrue(sheet.is_file() and sheet.stat().st_size>2000)
            explicit=td/'explicit.json'
            run=subprocess.run([sys.executable,str(ROOT/'scripts/seam_review_v66.py'),str(video),
                               '--cuts','1.0,2.0','--report',str(explicit)],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertEqual(len(json.loads(explicit.read_text())['seams']),2)

if __name__=='__main__':unittest.main()
