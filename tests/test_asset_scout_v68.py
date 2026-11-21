import importlib.util
import tempfile
import unittest
from pathlib import Path

S=Path(__file__).resolve().parents[1]/'scripts'/'asset_scout_v68.py'
spec=importlib.util.spec_from_file_location('asset_scout_v68',S)
a=importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
ROOT=Path(__file__).resolve().parents[1]

class TestAssetScoutV68(unittest.TestCase):
    def test_original_demo_has_real_pictograms(self):
        root=ROOT/'examples/asset-first-v68/illustrations'
        found=a.scan(root)
        self.assertEqual(found['files_scanned'],10)
        self.assertEqual(found['usable_previews'],10)
        self.assertEqual(sum(x['kind']=='svg' for x in found['assets']),5)
    def test_svg_script_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'icon.svg'
            p.write_text('<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>')
            ok,_=a.safe_svg(p)
            self.assertFalse(ok)
    def test_svg_remote_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'icon.svg'
            p.write_text('<svg xmlns="http://www.w3.org/2000/svg"><use href="https://example.org/a"/></svg>')
            ok,_=a.safe_svg(p)
            self.assertFalse(ok)
    def test_site_icon_permission_required(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'icons';p.mkdir();(p/'badge.png').write_bytes(b'png')
            with self.assertRaises(ValueError): a.scan(p,'product-site')
            with self.assertRaises(ValueError): a.scan(p,'product-site',allow_product_icons=True)
            result=a.scan(p,'product-site',allow_product_icons=True,authorization_note='owner granted permission')
            self.assertEqual(len(result['assets']),1)
            self.assertEqual(result['assets'][0]['rights_status'],'needs-independent-verification')
    def test_contact_sheet(self):
        root=ROOT/'examples/asset-first-v68/illustrations'
        info=a.scan(root)
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'sheet.jpg'
            a.sheet(root,info,out)
            self.assertTrue(out.is_file())
            self.assertGreater(out.stat().st_size,10000)

if __name__=='__main__':unittest.main()
