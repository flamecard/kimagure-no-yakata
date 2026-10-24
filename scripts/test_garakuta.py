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
    def test_portable_release_and_digest(self):
        self.item['release'].update(asset='KomaCut.zip', sha256='a'*64)
        self.item.update(launch_executable='KomaCut.exe',download_note='初回準備が必要．')
        self.asset.update(name='KomaCut.zip',digest='sha256:'+'a'*64)
        with patch.object(build.urllib.request, 'urlopen', return_value=self.response()):
            result=build.download(self.item)
            self.assertIn('Windows用ZIP',result)
            self.assertIn('KomaCut.exe',result)
            self.assertNotIn('インストーラー',result)
        self.asset['digest']='sha256:'+'b'*64
        with patch.object(build.urllib.request, 'urlopen', return_value=self.response()):
            with self.assertRaises(ValueError): build.download(self.item)
    def test_portable_requires_safe_launch_name(self):
        self.item['release']['asset']='KomaCut.zip'
        self.asset['name']='KomaCut.zip'
        self.item['launch_executable']='../escape.exe'
        with patch.object(build.urllib.request, 'urlopen', return_value=self.response()):
            with self.assertRaises(ValueError): build.download(self.item)
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
