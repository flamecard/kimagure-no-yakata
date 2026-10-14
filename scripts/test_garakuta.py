import importlib.util
import io
import json
import unittest
from unittest.mock import patch
from pathlib import Path
spec = importlib.util.spec_from_file_location('build', Path(__file__).parent / 'build_garakuta.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.item = {'status':'配布準備中', 'release': {'repository':'flamecard/kimagure-no-yakata','tag':'v1','asset':'setup.exe'},'version':'1.0','updated':'2026-10-14','history':['初版．'],'license':'Test license'}
        self.asset = {'name':'setup.exe','size':100,'state':'uploaded','browser_download_url':'https://github.com/flamecard/kimagure-no-yakata/releases/download/v1/setup.exe'}
    def response(self, **changes):
        data = {'draft':False,'prerelease':False,'assets':[self.asset]}
        data.update(changes)
        return io.BytesIO(json.dumps(data).encode())
    def test_pending_has_no_link(self):
        self.item['release'] = None
        self.assertNotIn('href=', build.download(self.item))
    def test_verified_asset_has_link(self):
        with patch.object(build.urllib.request, 'urlopen', return_value=self.response()):
            self.assertIn(self.asset['browser_download_url'], build.download(self.item))
    def test_missing_or_unpublished_assets_rejected(self):
        for changes in [{'assets':[]},{'draft':True},{'prerelease':True}]:
            with patch.object(build.urllib.request, 'urlopen', return_value=self.response(**changes)):
                with self.assertRaises(ValueError): build.download(self.item)
    def test_empty_asset_rejected(self):
        self.asset['size']=0
        with patch.object(build.urllib.request, 'urlopen', return_value=self.response()):
            with self.assertRaises(ValueError): build.download(self.item)
    def test_unknown_license_rejected(self):
        self.item['license']='未定'
        with patch.object(build.urllib.request, 'urlopen', return_value=self.response()):
            with self.assertRaises(ValueError): build.download(self.item)
    def test_punctuation_and_escaping(self):
        self.assertEqual(build.text('<例>，説明．'), '&lt;例&gt;，<br class="punctuation-break">説明．<br class="punctuation-break">')

if __name__ == '__main__': unittest.main()
