"""Local preview, rebuilding automatically as content and source files change."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import time

from build import ROOT, build
from import_photos import prepare_local, SECTIONS


def fingerprint():
    paths = list((ROOT / 'scripts').glob('*.py'))
    for name in SECTIONS:
        folder = ROOT.parent / name
        if folder.exists():
            paths.append(folder)
            paths.extend(p for p in folder.rglob('*') if not p.name.startswith('.'))
    for name in ['content', 'assets']:
        paths.extend(p for p in (ROOT / name).rglob('*') if p.is_file())
    return tuple(sorted((str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in paths))


def watch(stop):
    previous = fingerprint()
    while not stop.wait(1):
        try:
            current = fingerprint()
            if current != previous:
                time.sleep(.3)
                previous = fingerprint()
                prepare_local()
                build(ROOT / 'content', ROOT / 'dist')
                previous = fingerprint()
                print('预览已更新，请刷新浏览器。', flush=True)
        except Exception as error:
            print(f'暂未更新，保留上次成功预览：{error}', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    prepare_local()
    build(ROOT / 'content', ROOT / 'dist')
    server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(SimpleHTTPRequestHandler, directory=str(ROOT / 'dist')))
    stop = threading.Event()
    threading.Thread(target=watch, args=(stop,), daemon=True).start()
    print(f'本地预览：http://127.0.0.1:{args.port}/（修改后自动构建，刷新即可查看；Ctrl+C结束）', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        server.server_close()


if __name__ == '__main__':
    main()
