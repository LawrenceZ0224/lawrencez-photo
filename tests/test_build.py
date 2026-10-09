import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('site_builder', ROOT / 'scripts' / 'build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class PublishingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.content = self.root / 'content'
        self.content.mkdir()
        (self.content / 'site.json').write_text(json.dumps({'name': 'Test Photographer', 'siteUrl': 'https://example.com'}))
        for section in ['work', 'wandering', 'portrait', 'journal']:
            (self.content / section).mkdir()
        album = self.content / 'work' / '2026'
        album.mkdir()
        (album / 'album.json').write_text(json.dumps({'title': '2026', 'cover': ''}))
        self.output = self.root / 'dist'

    def tearDown(self):
        self.temp.cleanup()

    def add_photo(self):
        source = self.content / 'work' / '2026' / '001.jpg'
        exif = Image.Exif()
        exif[274] = 6
        Image.new('RGB', (120, 80), '#778899').save(source, exif=exif)
        return source

    def test_project_subpath_and_each_navigation_page(self):
        self.add_photo()
        builder.build(self.content, self.output, '/lawrencez-photo')
        for section, label in builder.SECTIONS:
            page = self.output / section / 'index.html'
            self.assertTrue(page.exists())
            self.assertIn('/lawrencez-photo/assets/site.css', page.read_text())
            self.assertIn(f'/lawrencez-photo/{section}/', page.read_text())
        self.assertIn('/lawrencez-photo/work/', (self.output / 'index.html').read_text())

    def test_photo_orientation_metadata_and_no_upscaling(self):
        source = self.add_photo()
        original = source.read_bytes()
        builder.build(self.content, self.output)
        manifest = json.loads((self.output / 'manifest.json').read_text())
        photo = manifest['albums']['work'][0]['photos'][0]
        self.assertEqual((photo['width'], photo['height']), (80, 120))
        self.assertEqual([v['width'] for v in photo['variants']], [80])
        for suffix in ['jpg', 'webp']:
            with Image.open(self.output / photo['variants'][0][suffix]) as image:
                self.assertEqual(image.size, (80, 120))
                self.assertFalse(image.getexif())
        self.assertEqual(source.read_bytes(), original)

    def test_invalid_cover_keeps_previous_site(self):
        builder.build(self.content, self.output)
        old_page = (self.output / 'index.html').read_bytes()
        meta_path = self.content / 'work' / '2026' / 'album.json'
        meta = json.loads(meta_path.read_text())
        meta['cover'] = 'missing.jpg'
        meta_path.write_text(json.dumps(meta))
        with self.assertRaises(ValueError):
            builder.build(self.content, self.output)
        self.assertEqual((self.output / 'index.html').read_bytes(), old_page)

    def test_plain_text_is_escaped_and_previous_release_preserved(self):
        post = {'title': '测试文章', 'date': '2026-10-09', 'body': '<script>alert(1)</script>\n\n第二段'}
        (self.content / 'journal' / 'test.json').write_text(json.dumps(post))
        builder.build(self.content, self.output)
        builder.build(self.content, self.output)
        article = (self.output / 'journal' / 'test' / 'index.html').read_text()
        self.assertIn('&lt;script&gt;', article)
        self.assertNotIn('<script>alert(1)</script>', article)
        self.assertTrue((self.root / '.previous-build' / 'index.html').exists())


if __name__ == '__main__':
    unittest.main()
