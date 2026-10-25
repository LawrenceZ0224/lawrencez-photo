"""Portrait cover selection must survive photo imports and work on project URLs."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


builder = module('portrait_builder', 'build.py')
importer = module('portrait_importer', 'import_photos.py')


class PortraitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / 'sources'
        self.content = self.root / 'content'
        self.content.mkdir()
        (self.content / 'site.json').write_text(json.dumps({'name': 'Test', 'siteUrl': 'https://example.com'}))
        for name in importer.SECTIONS:
            (self.source / name).mkdir(parents=True)
        self.album = self.source / 'Portrait' / 'anqi'
        self.album.mkdir()
        Image.new('RGB', (80, 120), '#667788').save(self.album / '01.jpg')
        Image.new('RGB', (120, 80), '#887766').save(self.album / '06.jpg')
        importer.import_photos(self.source, self.content)
        self.managed = self.content / 'portrait' / 'anqi'
        self.meta_path = self.managed / 'album.json'
        meta = importer.read(self.meta_path)
        meta.update(coverSource='06.jpg', mobileCoverSource='01.jpg', introCoverSource='01.jpg')
        self.meta_path.write_text(json.dumps(meta))
        importer.import_photos(self.source, self.content)

    def tearDown(self):
        self.temp.cleanup()

    def test_desktop_mobile_covers_survive_insert_and_replace(self):
        before = importer.read(self.meta_path)
        Image.new('RGB', (120, 80), '#112233').save(self.album / '06.jpg')
        Image.new('RGB', (80, 120), '#223344').save(self.album / '00.jpg')
        importer.import_photos(self.source, self.content)
        after = importer.read(self.meta_path)
        records = importer.read(self.managed / importer.MARKER)['photos']
        self.assertNotEqual(before['cover'], after['cover'])
        self.assertEqual(after['cover'], records['06.jpg']['file'])
        self.assertEqual(after['mobileCover'], records['01.jpg']['file'])
        self.assertEqual(after['introCover'], records['01.jpg']['file'])
        snapshot = {p.name: p.read_bytes() for p in self.managed.iterdir()}
        (self.album / '06.jpg').unlink()
        with self.assertRaisesRegex(ValueError, '指定的封面'):
            importer.import_photos(self.source, self.content)
        self.assertEqual(snapshot, {p.name: p.read_bytes() for p in self.managed.iterdir()})

    def test_three_levels_and_responsive_cover_under_project_base(self):
        output = self.root / 'dist'
        builder.build(self.content, output, '/lawrencez-photo')
        index = (output / 'portrait/index.html').read_text()
        cover = (output / 'portrait/01/index.html').read_text()
        photos = (output / 'portrait/01/photos/index.html').read_text()
        self.assertIn('href="/lawrencez-photo/portrait/01/"', index)
        self.assertIn('href="/lawrencez-photo/portrait/01/photos/"', cover)
        self.assertIn('href="/lawrencez-photo/portrait/"', photos)
        self.assertIn('href="/lawrencez-photo/"', cover)  # Top
        self.assertIn('src="/lawrencez-photo/assets/portrait.js"', photos)
        album = json.loads((output / 'manifest.json').read_text())['albums']['portrait'][0]
        self.assertEqual(album['coverPhoto']['file'], importer.read(self.meta_path)['cover'])
        self.assertEqual(album['mobileCoverPhoto']['file'], importer.read(self.meta_path)['mobileCover'])
        self.assertEqual(album['introCoverPhoto']['file'], importer.read(self.meta_path)['introCover'])
        self.assertEqual(album['mobileIntroCoverPhoto']['file'], album['introCoverPhoto']['file'])
        self.assertIn(album['coverPhoto']['full'], index)
        self.assertIn(album['introCoverPhoto']['full'], cover)
        self.assertNotIn(album['coverPhoto']['full'], cover)
        self.assertIn('media="(max-width:700px)"', cover)
        self.assertIn(album['mobileCoverPhoto']['full'], cover)
        self.assertEqual(photos.count('class="portrait-frame"'), 2)
        self.assertLess(photos.index(album['photos'][0]['full']), photos.index(album['photos'][1]['full']))
        self.assertNotIn('data-photo ', photos)  # The photo wall lightbox must not intercept the slideshow.
        self.assertIn('/lawrencez-photo/portrait/01/photos/', (output / 'sitemap.xml').read_text())


if __name__ == '__main__':
    unittest.main()
