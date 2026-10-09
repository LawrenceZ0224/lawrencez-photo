"""Explicitly publish reviewed local changes to the existing GitHub repository."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

from build import ROOT, build
from import_photos import prepare_local


def git(*args, capture=False):
    result = subprocess.run(['git', *args], cwd=ROOT, check=True, text=True,
                            capture_output=capture, timeout=45,
                            env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'})
    return result.stdout.strip() if capture else ''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--message', default='更新摄影网站')
    args = parser.parse_args()
    try:
        if Path(git('rev-parse', '--show-toplevel', capture=True)).resolve() != ROOT:
            raise RuntimeError('请在克隆下来的网站仓库内发布。')
        if git('branch', '--show-current', capture=True) != 'main':
            raise RuntimeError('请先切换到 main 分支。')
        prepare_local()
        build(ROOT / 'content', ROOT / 'dist')
        # Never force push or silently replace the current remote history.
        git('fetch', 'origin', 'main')
        if git('rev-list', '--count', 'HEAD..origin/main', capture=True) != '0':
            raise RuntimeError('GitHub 有更新。请先在 VS Code 获取并合并远端更新，再发布。')
        subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], cwd=ROOT, check=True, timeout=120)
        if git('status', '--porcelain', capture=True):
            # Git requests local identity configuration instead of inventing an email.
            git('var', 'GIT_AUTHOR_IDENT', capture=True)
            git('add', '-A')
            git('commit', '-m', args.message)
        git('push', 'origin', 'main')
        print('已同步到 GitHub。请在 Actions 查看自动部署结果。')
    except (RuntimeError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        print(f'发布未完成：{error}\n本地文件已保留。首次使用请在 VS Code 完成 GitHub 登录及 Git 作者身份设置。', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
