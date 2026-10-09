import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('photo_importer', ROOT / 'scripts' / 'import_photos.py')
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)


class PhotoImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / 'photos'
        for name in importer.SECTIONS:
            (self.source / name).mkdir(parents=True)
        self.album = self.source / 'Wandering on Earth' / '意大利'
        self.album.mkdir()
        self.content = self.root / 'content'

    def tearDown(self):
        self.temp.cleanup()

    def photo(self, name):
        path = self.album / name
        exif = Image.Exif()
        exif[274] = 6
        exif[270] = 'private metadata'
        Image.new('RGB', (120, 80), '#668899').save(path, exif=exif)
        return path

    def managed(self):
        return self.content / 'wandering' / importer.slug(self.album.name)

    def snapshot(self):
        return {str(p.relative_to(self.content)): p.read_bytes() for p in self.content.rglob('*') if p.is_file()}

    def test_orientation_private_metadata_order_cache_and_deletion(self):
        one, two = self.photo('2.jpg'), self.photo('10.jpg')
        originals = {p: p.read_bytes() for p in [one, two]}
        self.assertEqual(importer.import_photos(self.source, self.content), (2, 2))
        marker = importer.read(self.managed() / importer.MARKER)
        self.assertEqual(list(marker['photos']), ['2.jpg', '10.jpg'])
        self.assertNotIn(str(self.root), json.dumps(marker))
        meta = importer.read(self.managed() / 'album.json')
        self.assertEqual(meta['title'], '意大利')
        for item in marker['photos'].values():
            with Image.open(self.managed() / item['file']) as image:
                self.assertEqual(image.size, (80, 120))
                self.assertFalse(image.getexif())
        self.assertEqual(importer.import_photos(self.source, self.content), (2, 0))
        for p, data in originals.items():
            self.assertEqual(p.read_bytes(), data)
        one.unlink()
        self.assertEqual(importer.import_photos(self.source, self.content), (1, 0))
        self.assertEqual(len(list(self.managed().glob('*.jpg'))), 1)

    def test_corrupt_addition_preserves_last_import_and_manual_album(self):
        self.photo('1.jpg')
        importer.import_photos(self.source, self.content)
        snapshot = self.snapshot()
        (self.album / '2.jpg').write_bytes(b'partial upload')
        with self.assertRaises(ValueError):
            importer.import_photos(self.source, self.content)
        self.assertEqual(self.snapshot(), snapshot)
        (self.album / '2.jpg').unlink()
        marker = self.managed() / importer.MARKER
        marker.unlink()
        snapshot = self.snapshot()
        with self.assertRaises(ValueError):
            importer.import_photos(self.source, self.content)
        self.assertEqual(self.snapshot(), snapshot)

    def test_album_delete_only_managed_data_and_missing_root_is_safe(self):
        self.photo('1.jpg')
        importer.import_photos(self.source, self.content)
        manual = self.content / 'portrait' / 'manual'
        manual.mkdir(parents=True)
        (manual / 'keep.txt').write_text('keep')
        for p in self.album.iterdir():
            p.unlink()
        self.album.rmdir()
        importer.import_photos(self.source, self.content)
        self.assertFalse(self.managed().exists())
        self.assertTrue((manual / 'keep.txt').exists())
        snapshot = self.snapshot()
        (self.source / 'Work').rmdir()
        with self.assertRaises(ValueError):
            importer.import_photos(self.source, self.content)
        self.assertEqual(self.snapshot(), snapshot)


if __name__ == '__main__':
    unittest.main()
