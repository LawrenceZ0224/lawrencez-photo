"""Attach the existing remote history without replacing local working files."""
import subprocess
import sys

from build import ROOT
from publish import git

REMOTE = 'https://github.com/LawrenceZ0224/lawrencez-photo.git'


def main():
    try:
        if not (ROOT / '.git').exists():
            git('init', '-b', 'main')
            git('remote', 'add', 'origin', REMOTE)
        elif git('remote', 'get-url', 'origin', capture=True) != REMOTE:
            raise RuntimeError('当前目录已连接其他仓库，停止以保护现有配置。')
        git('fetch', 'origin', 'main')
        head = subprocess.run(['git', 'rev-parse', '--verify', 'HEAD'], cwd=ROOT,
                              capture_output=True, timeout=10)
        if head.returncode:
            # The initial index adopts remote history; local files stay intact.
            git('reset', '--mixed', 'origin/main')
            git('branch', '--set-upstream-to=origin/main', 'main')
        print('仓库已连接。本地文件保留，请在 VS Code 源代码管理中查看差异后发布。')
        return 0
    except (RuntimeError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        print(f'连接未完成：{error}\n本地文件保留。请接通 GitHub 网络后重试。', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
