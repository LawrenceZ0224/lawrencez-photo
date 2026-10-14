"""Prepare public photo copies from the folders next to code, never alter sources."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import tempfile

from PIL import Image, ImageCms, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = {'Work': 'work', 'Wandering on Earth': 'wandering', 'Portrait': 'portrait'}
FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff'}
MARKER = '_photo-import.json'
VERSION = 'srgb-3840-jpeg94-v2'
# Phone panorama files can legitimately exceed Pillow's default pixel threshold.
Image.MAX_IMAGE_PIXELS = 250_000_000


def natural_key(value):
    return [int(x) if x.isdigit() else x.casefold() for x in re.split(r'(\d+)', str(value))]


def slug(name):
    # Keep routes portable, including when the source folder has a Chinese title.
    if re.fullmatch(r'[a-zA-Z0-9_-]+', name):
        return name.lower()
    stem = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')[:48] or 'album'
    return stem + '-' + hashlib.sha256(name.encode()).hexdigest()[:8]


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def export_photo(source, target):
    with Image.open(source) as original:
        if original.width * original.height > 250_000_000:
            raise ValueError('图片超过 2.5 亿像素，请先导出网页成片。')
        if original.format == 'JPEG':
            original.draft('RGB', (3840, 3840))
        image = ImageOps.exif_transpose(original)
        if original.info.get('icc_profile'):
            image = ImageCms.profileToProfile(image,
                ImageCms.ImageCmsProfile(io.BytesIO(original.info['icc_profile'])),
                ImageCms.createProfile('sRGB'), outputMode='RGB')
        elif image.mode in ('RGBA', 'LA') or 'transparency' in image.info:
            rgba = image.convert('RGBA')
            image = Image.new('RGB', rgba.size, 'white')
            image.paste(rgba, mask=rgba.getchannel('A'))
        else:
            image = image.convert('RGB')
        image.thumbnail((3840, 3840), Image.Resampling.LANCZOS)
        clean = Image.new('RGB', image.size)
        clean.paste(image)
        clean.save(target, quality=94, optimize=True, subsampling=2)


def import_photos(source_root, content):
    source_root, content = Path(source_root), Path(content)
    if not all((source_root / name).is_dir() for name in SECTIONS):
        raise ValueError('照片根目录必须包含 Work、Wandering on Earth、Portrait 三个文件夹；停止导入以免误移除相册。')
    content.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.photo-import-', dir=content.parent))
    plans, seen, total, converted = [], set(), 0, 0
    try:
        for folder_name, section in SECTIONS.items():
            section_root = source_root / folder_name
            for album in sorted(section_root.iterdir(), key=lambda p: natural_key(p.name)):
                if album.name.startswith('.') or not album.is_dir() or album.is_symlink():
                    continue
                relative = f'{folder_name}/{album.name}'
                destination = content / section / slug(album.name)
                if destination in seen:
                    raise ValueError(f'相册名称大小写冲突：{relative}')
                seen.add(destination)
                old = read(destination / MARKER) if (destination / MARKER).exists() else None
                if old and old['source'] != relative:
                    raise ValueError(f'相册路径冲突：{relative}')
                if destination.exists() and not old:
                    extras = [p for p in destination.iterdir() if p.name not in {'album.json', '.gitkeep', '.DS_Store'}]
                    if extras:
                        raise ValueError(f'已有手动管理的相册，停止覆盖：{destination.name}')
                prepared = stage / section / destination.name
                prepared.mkdir(parents=True)
                photos = sorted((p for p in album.iterdir() if p.is_file() and not p.is_symlink()
                                 and not p.name.startswith('.') and p.suffix.lower() in FORMATS), key=lambda p: natural_key(p.name))
                nested = [p for p in album.iterdir() if p.is_dir() and not p.name.startswith('.')]
                if nested:
                    raise ValueError(f'{relative} 中还有子文件夹，请把照片直接放在该相册中。')
                unsupported = [p for p in album.iterdir() if p.is_file() and not p.name.startswith('.')
                               and p.suffix.lower() not in FORMATS and p.name != '相册介绍.txt']
                if unsupported:
                    print(f'{relative}：忽略 {len(unsupported)} 个不支持的文件（支持 JPG/PNG/WebP/TIFF）。', flush=True)
                records = {}
                for n, photo in enumerate(photos, 1):
                    digest = hashlib.sha256(photo.read_bytes() + VERSION.encode()).hexdigest()
                    filename = f'{n:06d}-{digest[:16]}.jpg'
                    target = prepared / filename
                    cached = (old or {}).get('photos', {}).get(photo.name, {})
                    previous = destination / cached.get('file', '_missing')
                    if cached.get('hash') == digest and previous.is_file():
                        shutil.copy2(previous, target)
                    else:
                        try:
                            export_photo(photo, target)
                        except Exception as error:
                            raise ValueError(f'照片暂时无法读取：{relative}/{photo.name}；保留上次导入。') from error
                        converted += 1
                    records[photo.name] = {'file': filename, 'hash': digest}
                    if n % 25 == 0:
                        print(f'{relative}：准备 {n}/{len(photos)} 张', flush=True)
                meta = read(destination / 'album.json') if (destination / 'album.json').exists() else {}
                remap = {(old or {}).get('photos', {}).get(name, {}).get('file'): info['file'] for name, info in records.items()}
                for field in ['captions', 'focus']:
                    meta[field] = {remap[key]: value for key, value in meta.get(field, {}).items() if key is not None and key in remap}
                meta['title'] = album.name
                for field in ['cover', 'mobileCover', 'introCover', 'mobileIntroCover']:
                    # Remember source filenames, so replacing/reordering a photo keeps its cover role.
                    source_name = meta.get(field + 'Source', '')
                    if source_name:
                        if not isinstance(source_name, str) or source_name not in records:
                            raise ValueError(f'{relative}: 指定的封面 {source_name} 不存在，请更新 album.json 中的 {field}Source。')
                        meta[field] = records[source_name]['file']
                    elif field in meta:
                        meta[field] = remap.get(meta[field], '') if meta[field] else ''
                meta.setdefault('cover', '')
                description = album / '相册介绍.txt'
                if description.exists():
                    meta['description'] = description.read_text(encoding='utf-8')
                else:
                    meta.setdefault('description', '')
                (prepared / 'album.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
                marker = {'source': relative, 'version': VERSION, 'photos': records}
                (prepared / MARKER).write_text(json.dumps(marker, ensure_ascii=False, indent=2), encoding='utf-8')
                # Preserve user metadata, only replace files owned by this importer.
                if old:
                    owned = {v['file'] for v in old['photos'].values()} | {MARKER, 'album.json'}
                    for extra in destination.iterdir():
                        if extra.name not in owned:
                            if extra.is_dir():
                                shutil.copytree(extra, prepared / extra.name)
                            else:
                                shutil.copy2(extra, prepared / extra.name)
                plans.append((destination, prepared))
                total += len(photos)
            for destination in (content / section).iterdir() if (content / section).exists() else []:
                if destination.is_dir() and (destination / MARKER).exists() and destination not in seen:
                    old = read(destination / MARKER)
                    owned = {v['file'] for v in old['photos'].values()} | {MARKER, 'album.json', '.DS_Store'}
                    if any(p.name not in owned for p in destination.iterdir()):
                        raise ValueError(f'已删除的相册包含手动添加的文件，停止移除：{destination.name}')
                    plans.append((destination, None))
        # All photos must prepare successfully before replacing any managed album.
        applied = []
        try:
            for i, (destination, prepared) in enumerate(plans):
                destination.parent.mkdir(parents=True, exist_ok=True)
                backup = stage / f'backup-{i}'
                if destination.exists():
                    destination.rename(backup)
                applied.append((destination, backup))
                if prepared:
                    prepared.rename(destination)
        except Exception:
            for destination, backup in reversed(applied):
                if destination.exists():
                    shutil.rmtree(destination)
                if backup.exists():
                    backup.rename(destination)
            raise
        print(f'照片已准备：{total} 张，新增或变更处理 {converted} 张；原文件未修改。', flush=True)
        return total, converted
    finally:
        shutil.rmtree(stage)


def prepare_local():
    source = ROOT.parent
    if all((source / name).is_dir() for name in SECTIONS):
        return import_photos(source, ROOT / 'content')
    print('未发现本地照片目录，使用 content 中已准备的内容。', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=ROOT.parent)
    args = parser.parse_args()
    import_photos(args.source, ROOT / 'content')
