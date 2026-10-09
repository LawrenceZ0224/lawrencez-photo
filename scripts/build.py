"""Build a portable static photography site from author-owned content folders."""
import hashlib
import html
import io
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from urllib.parse import quote

from PIL import Image, ImageCms, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = [("work", "Work"), ("wandering", "Wandering on Earth"),
            ("portrait", "Portrait"), ("profile", "Profile"), ("journal", "Journal")]
FORMATS = {".jpg", ".jpeg", ".png", ".webp"}
WIDTHS = (640, 1280)


def esc(value):
    return html.escape(str(value), quote=True)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def text_body(text):
    return '<div class="prose">' + ''.join(f'<p>{esc(p)}</p>' for p in text.split('\n\n') if p.strip()) + '</div>'


def natural_key(value):
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', str(value))]


def photo_variants(source, output):
    # Content-derived paths remain stable when files are renamed or re-ordered.
    key = hashlib.sha256(source.read_bytes() + b'pipeline-v3-webp88-jpeg90-3840').hexdigest()[:24]
    folder = output / 'media' / key
    manifest = folder / 'photo.json'
    if manifest.exists():
        return read_json(manifest)
    cached = output.parent / 'dist' / 'media' / key
    if (cached / 'photo.json').exists():
        shutil.copytree(cached, folder, copy_function=os.link)
        return read_json(manifest)
    folder.mkdir(parents=True)
    with Image.open(source) as original:
        image = ImageOps.exif_transpose(original)
        icc = original.info.get('icc_profile')
        if icc:
            image = ImageCms.profileToProfile(image, ImageCms.ImageCmsProfile(io.BytesIO(icc)),
                                             ImageCms.createProfile('sRGB'), outputMode='RGB')
        else:
            if image.mode in ('RGBA', 'LA') or 'transparency' in image.info:
                rgba = image.convert('RGBA')
                image = Image.new('RGB', rgba.size, 'white')
                image.paste(rgba, mask=rgba.getchannel('A'))
            else:
                image = image.convert('RGB')
        variants = []
        # Keep small originals at their native size; never upscale.
        limit = min(image.width, max(1, round(3840 * image.width / max(image.size))))
        for width in sorted({min(w, limit) for w in WIDTHS} | {limit}):
            height = max(1, round(image.height * width / image.width))
            resized = image.resize((width, height), Image.Resampling.LANCZOS)
            # Fresh RGB image strips EXIF, including location metadata.
            clean = Image.new('RGB', resized.size)
            clean.paste(resized)
            webp = f'media/{key}/{width}.webp'
            clean.save(folder / f'{width}.webp', quality=88, method=4)
            jpg = None
            if width <= 1280:
                jpg = f'media/{key}/{width}.jpg'
                clean.save(folder / f'{width}.jpg', quality=90, optimize=True)
            variants.append({'width': width, 'height': height, 'webp': webp, 'jpg': jpg})
        result = {'id': key, 'width': image.width, 'height': image.height, 'variants': variants, 'full': variants[-1]['webp']}
    manifest.write_text(json.dumps(result, ensure_ascii=False), encoding='utf-8')
    return result


def build(content, destination, base_path=''):
    base = '/' + base_path.strip('/') if base_path.strip('/') else ''
    def url(path):
        return base + '/' + quote(str(path).lstrip('/'), safe='/')
    config = read_json(content / 'site.json')
    name = config['name']
    if not isinstance(name, str) or not name.strip():
        raise ValueError('site.json 中的摄影署名不能为空')
    pages = []
    previous = destination.parent / '.previous-build'
    stage = Path(tempfile.mkdtemp(prefix='.build-', dir=destination.parent))
    try:
        shutil.copytree(ROOT / 'assets', stage / 'assets')
        albums = {}
        for section, _ in SECTIONS[:3]:
            entries = []
            source = content / section
            for folder in sorted(source.iterdir() if source.exists() else [], key=lambda p: natural_key(p.name), reverse=section == 'work'):
                if not folder.is_dir() or not (folder / 'album.json').exists():
                    continue
                if not re.fullmatch(r'[a-zA-Z0-9_-]+', folder.name):
                    raise ValueError(f'请给相册文件夹使用英文、数字或短横线：{folder.name}')
                meta = read_json(folder / 'album.json')
                if not isinstance(meta.get('title'), str) or not meta['title'].strip():
                    raise ValueError(f'{folder}: 相册标题不能为空')
                photos = []
                for path in sorted(folder.iterdir(), key=lambda p: natural_key(p.name)):
                    if path.suffix.lower() not in FORMATS or path.name.startswith('.'):
                        continue
                    photo = photo_variants(path, stage)
                    photo = {**photo, 'file': path.name,
                             'caption': meta.get('captions', {}).get(path.name, meta['title']),
                             'focus': meta.get('focus', {}).get(path.name, [50, 50])}
                    focus = photo['focus']
                    if (not isinstance(focus, list) or len(focus) != 2 or
                            any(not isinstance(x, (int, float)) or not 0 <= x <= 100 for x in focus)):
                        raise ValueError(f'{path}: 裁切位置需为两个0到100之间的数字')
                    photos.append(photo)
                    if len(photos) % 25 == 0:
                        print(f'{meta["title"]}：已生成 {len(photos)} 张网页图片', flush=True)
                cover_name = meta.get('cover', '')
                if cover_name and cover_name not in [p['file'] for p in photos]:
                    raise ValueError(f'{folder}: 封面 {cover_name} 不存在')
                cover = next((p for p in photos if p['file'] == cover_name), photos[0] if photos else None)
                entries.append({**meta, 'slug': folder.name, 'photos': photos, 'coverPhoto': cover,
                                'path': f'{section}/{folder.name}/'})
            albums[section] = entries

        def picture(photo, full=False):
            variants = photo['variants']
            chosen = next(v for v in reversed(variants) if v['jpg']) if full else variants[0]
            srcset = ', '.join(f'{url(v["webp"])} {v["width"]}w' for v in variants)
            cls = 'profile-image' if full else 'photo'
            focus = photo.get('focus', [50, 50])
            style = f'object-position:{focus[0]}% {focus[1]}%'
            return (f'<picture><source type="image/webp" srcset="{esc(srcset)}" sizes="{("(max-width:700px) 90vw, 720px" if full else "(max-width:700px) 50vw, (max-width:1100px) 25vw, 20vw")}">'
                    f'<img class="{cls}" src="{esc(url(chosen["jpg"]))}" width="{photo["width"]}" height="{photo["height"]}" '
                    f'alt="{esc(photo.get("caption", name))}" style="{style}" loading="lazy" decoding="async"></picture>')

        def document(path, title, body, active='', intro=False, description=''):
            links = f'<a href="{url("")}">Top</a>'
            for slug, label in SECTIONS:
                current = ' aria-current="page"' if slug == active else ''
                if slug == 'wandering':
                    locations = ''.join(f'<a href="{url(a["path"])}">{esc(a["title"])}</a>' for a in albums['wandering'])
                    links += (f'<div class="nav-group"><button class="nav-trigger" type="button" aria-expanded="false" '
                              f'aria-controls="location-menu"{current}>{label}</button>'
                              f'<div class="nav-menu" id="location-menu">{locations or "<span>地点整理中</span>"}</div></div>')
                else:
                    links += f'<a href="{url(slug + "/")}"{current}>{label}</a>'
            header = '' if intro else (
                f'<header><a class="brand" href="{url("work/")}">{esc(name)}</a>'
                '<button class="menu-toggle" type="button" aria-label="打开导航" aria-expanded="false" '
                'aria-controls="mobile-navigation" hidden>'
                '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M4 7H28M4 16H28M4 25H28"/></svg></button>'
                f'<nav id="site-navigation" aria-label="主要栏目">{links}</nav></header>')
            canonical = ''
            if config.get('siteUrl'):
                canonical = f'<link rel="canonical" href="{esc(config["siteUrl"].rstrip("/") + url(path))}">'
            page = ('<!doctype html>\n' + f'<html lang="{esc(config.get("language", "zh-CN"))}"><head><meta charset="utf-8">'
                    '<meta name="viewport" content="width=device-width,initial-scale=1">'
                    f'<title>{esc(title)} · {esc(name)}</title><meta name="description" content="{esc(description or config.get("description", ""))}">'
                    f'{canonical}<link rel="stylesheet" href="{url("assets/site.css")}"></head><body>'
                    f'{header}<main class="{"entry" if intro else ""}">{body}</main>'
                    f'<footer>© {esc(name)}</footer><script src="{url("assets/gallery.js")}" defer></script></body></html>')
            output = stage / path / 'index.html' if path else stage / 'index.html'
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(page, encoding='utf-8')
            pages.append(path)
            return page

        def empty():
            return '<p class="empty">作品整理中</p>'

        def wall(photos):
            if not photos:
                return empty()
            return '<div class="grid">' + ''.join(
                f'<a class="photo-link" data-photo data-caption="{esc(p["caption"])}" href="{url(p["full"])}">{picture(p)}</a>'
                for p in photos) + '</div>'

        def subnav(entries, current=''):
            return '<div class="subnav" aria-label="相册分类">' + ''.join(
                f'<a href="{url(a["path"])}"' + (' aria-current="page"' if a['slug'] == current else '') + f'>{esc(a["title"])}</a>'
                for a in entries) + '</div>'

        intro = f'<div class="entry-inner"><h1 class="entry-name">{esc(name)}</h1><a class="enter-link" href="{url("work/")}">ENTER SITE</a></div>'
        document('', 'Photography', intro, intro=True)
        for section, label in SECTIONS[:3]:
            entries = albums[section]
            if section == 'work':
                latest = next((a for a in entries if a['photos']), entries[0] if entries else None)
                body = '<h1>Work</h1>' + subnav(entries, latest['slug'] if latest else '') + wall(latest['photos'] if latest else [])
            elif section == 'wandering':
                body = f'<h1>{label}</h1>' + subnav(entries)
                if not entries:
                    body += empty()
            else:
                cards = ''.join(f'<a href="{url(a["path"])}">{picture(a["coverPhoto"])}<span class="album-label">{esc(a["title"])}</span></a>'
                                for a in entries if a['coverPhoto'])
                body = f'<h1>{label}</h1>' + (f'<div class="grid">{cards}</div>' if cards else empty())
            document(f'{section}/', label, body, section)
            for album in entries:
                body = f'<h1>{esc(album["title"])}</h1>' + subnav(entries, album['slug'])
                if album.get('description'):
                    body += f'<p class="description">{esc(album["description"])}</p>'
                body += wall(album['photos'])
                document(album['path'], album['title'], body, section, description=album.get('description', ''))

        profile = '<h1>Profile</h1><div class="profile">'
        if config.get('profilePhoto'):
            source = (content / config['profilePhoto']).resolve()
            if content.resolve() not in source.parents:
                raise ValueError('个人照片必须位于content文件夹内')
            profile += picture({**photo_variants(source, stage), 'caption': name}, full=True)
        profile += text_body(config.get('profile', ''))
        if config.get('notes'):
            profile += text_body(config['notes'])
        if config.get('email'):
            profile += f'<p><a href="mailto:{esc(quote(config["email"], safe="@.+-"))}">{esc(config["email"])}</a></p>'
        if not any(config.get(k) for k in ['profilePhoto', 'profile', 'notes', 'email']):
            profile += '<p class="empty">个人介绍整理中</p>'
        document('profile/', 'Profile', profile + '</div>', 'profile')
        posts = []
        for path in sorted((content / 'journal').glob('*.json')):
            meta = read_json(path)
            for required in ['title', 'date', 'body']:
                if not isinstance(meta.get(required), str) or not meta[required].strip():
                    raise ValueError(f'{path}: {required}不能为空')
            if not re.fullmatch(r'[a-zA-Z0-9_-]+', path.stem):
                raise ValueError('随笔文件名请使用英文、数字或短横线')
            post_path = f'journal/{path.stem}/'
            body = f'<article class="post"><h1>{esc(meta["title"])}</h1><time>{esc(meta["date"])}</time>{text_body(meta["body"])}<a class="back" href="{url("journal/")}">返回 Journal</a></article>'
            document(post_path, meta['title'], body, 'journal', description=meta.get('excerpt', ''))
            posts.append({**meta, 'path': post_path})
        listing = ''.join(f'<a class="journal-item" href="{url(p["path"])}"><time>{esc(p["date"])}</time><h2>{esc(p["title"])}</h2><p>{esc(p.get("excerpt", ""))}</p></a>'
                          for p in sorted(posts, key=lambda p: p['date'], reverse=True))
        document('journal/', 'Journal', '<h1>Journal</h1><div class="journal-list">' + (listing or '<p class="empty">随笔整理中</p>') + '</div>', 'journal')
        (stage / 'manifest.json').write_text(json.dumps({'albums': albums, 'posts': posts}, ensure_ascii=False, indent=2), encoding='utf-8')
        (stage / '.nojekyll').touch()
        (stage / '.photography-build').touch()
        not_found = document('404/', '页面未找到', f'<h1>页面未找到</h1><p class="empty"><a href="{url("work/")}">返回作品</a></p>')
        (stage / '404.html').write_text(not_found, encoding='utf-8')
        if config.get('siteUrl'):
            origin = config['siteUrl'].rstrip('/')
            sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            sitemap += ''.join(f'<url><loc>{esc(origin + url(path))}</loc></url>' for path in pages if path != '404/') + '</urlset>'
            (stage / 'sitemap.xml').write_text(sitemap, encoding='utf-8')
            (stage / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {origin}{url("sitemap.xml")}\n', encoding='utf-8')
        old_count = 0
        if (destination / 'manifest.json').exists():
            old = read_json(destination / 'manifest.json')
            old_count = sum(len(a['photos']) for entries in old['albums'].values() for a in entries)
        new_count = sum(len(a['photos']) for entries in albums.values() for a in entries)
        if destination.exists() and not (destination / '.photography-build').exists():
            raise ValueError('输出文件夹不属于本工具，停止以防覆盖其他文件')
        if previous.exists():
            if not (previous / '.photography-build').exists():
                raise ValueError('旧版本文件夹不属于本工具，停止构建')
            shutil.rmtree(previous)
        if destination.exists():
            destination.rename(previous)
        try:
            stage.rename(destination)
        except Exception:
            if previous.exists() and not destination.exists():
                previous.rename(destination)
            raise
        print(f'构建完成：{len(pages)}个页面，{new_count}张照片（上一版{old_count}张）。预览后再发布。')
    finally:
        if stage.exists():
            shutil.rmtree(stage)


if __name__ == '__main__':
    build(ROOT / 'content', ROOT / 'dist', os.environ.get('SITE_BASE_PATH', ''))
