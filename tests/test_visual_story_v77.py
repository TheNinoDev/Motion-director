import importlib.util, tempfile, unittest
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
class TestEditorialV77(unittest.TestCase):
    def test_guidance_is_explicit(self):
        root=(ROOT/"SKILL.md").read_text()
        self.assertIn("FINAL VETO",root)
        self.assertIn("visual_story_inspection_v77.py",root)
        self.assertIn("headline",root.lower())
    def test_instructions_have_specific_timecoded_evidence(self):
        case=(ROOT/"references/158-v77-current-film-autopsy.md").read_text()
        self.assertIn("3–8s",case)
        self.assertIn("21–24s",case)
    def test_editorial_tool_is_present(self):
        self.assertTrue((ROOT/"scripts/visual_story_inspection_v77.py").is_file())
if __name__=="__main__": unittest.main()
