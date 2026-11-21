import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('rehearsal',ROOT/'scripts/film_rehearsal_v73.py')
MOD=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(MOD)


class FilmRehearsalTests(unittest.TestCase):
    def test_valid_spans(self):
        shots=MOD.validate_plan({'shots':[{'start':0,'end':2},{'start':2,'end':4}]},4)
        self.assertEqual(len(shots),2)
    def test_gap_rejected(self):
        with self.assertRaisesRegex(ValueError,'gap'):MOD.validate_plan({'shots':[{'start':0,'end':1},{'start':2,'end':3}]},3)
    def test_overlap_rejected(self):
        with self.assertRaisesRegex(ValueError,'overlap'):MOD.validate_plan({'shots':[{'start':0,'end':2},{'start':1.4,'end':3}]},3)
    def test_outside_duration(self):
        with self.assertRaisesRegex(ValueError,'invalid'):MOD.validate_plan({'shots':[{'start':0,'end':9}]},5)
    def test_empty_rejected(self):
        with self.assertRaisesRegex(ValueError,'at least one'):MOD.validate_plan({'shots':[]},5)
    def test_contact_sheet_uses_actual_video(self):
        from unittest.mock import patch
        from PIL import Image
        with tempfile.TemporaryDirectory() as d:
            with patch.object(MOD,'get_frame',return_value=Image.new('RGB',(100,180),'white')) as grab:
                output=Path(d)/'sheet.jpg'
                MOD.build_sheet('fake.mp4',[1,2,3],['a','b','c'],output,cols=3,width=100)
                self.assertTrue(output.is_file());self.assertEqual(grab.call_count,3)

if __name__=='__main__':unittest.main()