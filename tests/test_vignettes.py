"""The flat Vignettes source imports safely and opens one Film-style reader."""
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


builder = module('vignettes_builder', 'build.py')
importer = module('vignettes_importer', 'import_photos.py')


class VignettesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / 'sources'
        for name in [*importer.REQUIRED_SECTIONS, 'Vignettes']:
            (self.source / name).mkdir(parents=True)
        self.vignettes = self.source / 'Vignettes'
        self.content = self.root / 'content'
        self.managed = self.content / 'vignettes' / 'main'
        self.managed.mkdir(parents=True)
        self.meta_path = self.managed / 'album.json'
        self.meta_path.write_text(json.dumps({'coverSource': 'Into the Mist.jpg'}))
        config = {'name': 'Test Photographer', 'siteUrl': 'https://example.com',
                  'portfolioCovers': {'vignettes': {
                      'album': 'vignettes/main', 'source': 'Into the Mist.jpg'}}}
        (self.content / 'site.json').write_text(json.dumps(config))
        Image.new('RGB', (120, 80), '#778899').save(self.vignettes / 'Into the Mist.jpg')
        Image.new('RGB', (80, 120), '#3366aa').save(self.vignettes / 'Fly into the Blue.jpg')

    def tearDown(self):
        self.temp.cleanup()

    def snapshot(self):
        return {str(p.relative_to(self.content)): p.read_bytes()
                for p in self.content.rglob('*') if p.is_file()}

    def test_flat_import_cover_cache_and_originals(self):
        originals = {p.name: p.read_bytes() for p in self.vignettes.iterdir()}
        self.assertEqual(importer.import_photos(self.source, self.content), (2, 2))
        record = importer.read(self.managed / importer.MARKER)
        self.assertEqual(record['source'], 'Vignettes')
        self.assertEqual(set(record['photos']), set(originals))
        self.assertEqual(len(list(self.managed.glob('*.jpg'))), 2)
        meta = importer.read(self.meta_path)
        self.assertEqual(meta['title'], 'Vignettes')
        self.assertEqual(meta['cover'], record['photos']['Into the Mist.jpg']['file'])
        for name, photo in record['photos'].items():
            self.assertEqual(meta['captions'][photo['file']], Path(name).stem)
        self.assertEqual(importer.import_photos(self.source, self.content), (2, 0))
        self.assertEqual(originals, {p.name: p.read_bytes() for p in self.vignettes.iterdir()})

    def test_missing_optional_folder_preserves_published_content(self):
        importer.import_photos(self.source, self.content)
        before = self.snapshot()
        self.vignettes.rename(self.root / 'temporarily-unavailable-vignettes')
        self.assertEqual(importer.import_photos(self.source, self.content), (0, 0))
        self.assertEqual(self.snapshot(), before)

    def test_corrupt_and_nested_additions_preserve_last_import(self):
        importer.import_photos(self.source, self.content)
        before = self.snapshot()
        corrupt = self.vignettes / 'Broken.jpg'
        corrupt.write_bytes(b'incomplete image copy')
        with self.assertRaisesRegex(ValueError, '照片暂时无法读取'):
            importer.import_photos(self.source, self.content)
        self.assertEqual(self.snapshot(), before)
        corrupt.unlink()
        (self.vignettes / 'Nested album').mkdir()
        with self.assertRaisesRegex(ValueError, '子文件夹'):
            importer.import_photos(self.source, self.content)
        self.assertEqual(self.snapshot(), before)

    def test_project_base_cover_and_single_gallery(self):
        importer.import_photos(self.source, self.content)
        output = self.root / 'dist'
        builder.build(self.content, output, '/lawrencez-photo')
        portfolio = (output / 'portfolio' / 'index.html').read_text()
        reader = (output / 'vignettes' / 'index.html').read_text()
        manifest = json.loads((output / 'manifest.json').read_text())
        album = manifest['albums']['vignettes'][0]
        records = importer.read(self.managed / importer.MARKER)['photos']
        self.assertEqual(album['path'], 'vignettes/')
        self.assertEqual(album['sourcePath'], 'vignettes/main/')
        self.assertEqual(album['photos'][0]['file'], records['Into the Mist.jpg']['file'])
        self.assertEqual(album['coverPhoto']['file'], album['photos'][0]['file'])
        card = re.search(r'<article[^>]*aria-labelledby="portfolio-vignettes">(.*?)</article>',
                         portfolio).group(1)
        self.assertIn('href="/lawrencez-photo/vignettes/"', card)
        self.assertIn(album['photos'][0]['full'], card)
        self.assertNotIn(album['photos'][1]['full'], card)
        self.assertNotIn('Landscape', portfolio)
        self.assertNotIn('portfolio-landscape', portfolio)
        self.assertIn('class="film-reader"', reader)
        self.assertIn('src="/lawrencez-photo/assets/film.js"', reader)
        self.assertIn('href="/lawrencez-photo/assets/site.css"', reader)
        self.assertIn('class="film-return" href="/lawrencez-photo/portfolio/">← Portfolio', reader)
        self.assertEqual(reader.count('class="film-frame"'), 2)
        self.assertEqual(reader.count('data-film-thumb="'), 2)
        first_frame = re.search(r'<figure class="film-frame" data-film-frame>(.*?)</figure>',
                                reader).group(1)
        self.assertIn(album['photos'][0]['full'], first_frame)
        self.assertIn('alt="Into the Mist"', first_frame)
        self.assertIn('data-film-count aria-live="polite">01 / 02', reader)
        for control in ['data-film-prev', 'data-film-next', 'data-film-status', 'data-film-retry']:
            self.assertIn(control, reader)
        self.assertNotIn('data-photo ', reader)
        self.assertFalse((output / 'vignettes' / 'main').exists())
        sitemap = (output / 'sitemap.xml').read_text()
        self.assertIn('https://example.com/lawrencez-photo/vignettes/', sitemap)
        self.assertNotIn('/vignettes/main/', sitemap)


if __name__ == '__main__':
    unittest.main()
