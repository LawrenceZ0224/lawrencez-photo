# LawrenceZ 摄影网站

白底入口、五个栏目、照片墙与本地文件夹内容管理。导航最左侧的 Top 返回白底入口。第五栏暂称 Journal，可修改 `scripts/build.py` 中的栏目名称。

目前只有栏目框架，没有真实作品或个人介绍。所有摄影图片由你提供。网站尚未上传 GitHub 或正式部署。

## 第一次发布到 GitHub Pages

1. 用 GitHub 账号 `LawrenceZ0224` 创建公开仓库，名称填写 `lawrencez-photo`，可勾选 Add a README file，方便之后网页上传。免费账户使用公开仓库发布 Pages。仓库公开意味着代码、加入仓库的成片与历史版本可被访问；本项目的原片不要放进仓库，只放已决定公开的网页成片。
2. 将本项目的**内容**放入仓库根目录。根目录应直接包含 `content/`、`assets/`、`scripts/`、`requirements.txt` 和 `.github/`，而不是再嵌套一层 `photography-site/`。上传时务必包含隐藏的 `.github/workflows/pages.yml`；电脑的显示隐藏文件开关可能需要打开。
3. 在仓库的 **Settings → Pages → Build and deployment → Source** 中选择 **GitHub Actions**。
4. 打开 **Actions → Publish photography website → Run workflow**。完成后在 Pages 设置或部署任务中查看网址。
5. 预期默认网址为 `https://lawrencez0224.github.io/lawrencez-photo/`。这是计划地址，只有成功部署后才可访问。部署配置会自动读取项目路径，保证图片和栏目链接可用。
6. 在 Pages 设置中检查 HTTPS 已启用，再用大陆手机流量和 Wi-Fi 测试入口、照片墙与完整大图。

以后推送到 main 分支会自动测试、构建并发布。若需要预览，先在电脑本地构建并检查；合并到 main 就表示发布。当前流程不在推送 main 后再询问确认。

## 如何整理内容

- `content/site.json`：署名、简介、碎碎念、公开邮箱；`profilePhoto` 可以填写 `profile/me.jpg`，再将照片放入对应位置。
- `content/work/2026/`：2026 年非系列作品，继续增加 `2025/` 等年份文件夹。
- `content/wandering/tokyo/`：地点文件夹示例；相册显示名在 `album.json` 中填写，可以使用中文。文件夹名用英文、数字或短横线。
- `content/portrait/project-name/`：人像主题或项目文件夹。
- `content/journal/article-name.json`：随笔。

每个照片文件夹都要有 `album.json`。复制现有 Work 的模板即可：

```json
{
  "title": "相册显示名",
  "description": "这组照片的介绍，可留空",
  "cover": "001.jpg",
  "captions": {"001.jpg": "照片说明，可不填"},
  "focus": {"001.jpg": [50, 50]}
}
```

照片文件名按 `001.jpg`、`002.jpg` 排序；格式支持 JPG、PNG、WebP。`cover` 留空时使用第一张；`focus` 是缩略图裁切焦点的横、纵百分比，50、50表示居中。完整大图保持照片比例。

随笔格式：

```json
{
  "title": "文章标题",
  "date": "2026-10-09",
  "excerpt": "列表页摘要",
  "body": "正文第一段。\n\n正文第二段。"
}
```

空的人像、旅行和随笔栏目显示整理中，不会生成虚构作品。

## 本地预览

电脑需安装 Python 3.12 或更新版本。首次准备：

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

预览前构建并启动本地预览：

```sh
python scripts/build.py
python -m http.server 8000 --directory dist
```

在浏览器打开 `http://localhost:8000/`。这是纯静态网站，不需要在线数据库或维护应用服务器。照片放大浏览支持键盘左右键、Escape 关闭与手机横向滑动。

## 图片处理与备份

自动生成不超过原图尺寸的640、1280、2560像素宽度，每档提供WebP和JPEG。统一输出sRGB并去除EXIF；原始输入不被改写。网页缩略图按屏幕取图，完整图最大宽度2560。

目前会重新构建全部照片；同一轮构建中内容相同的图片复用输出，尚未实现跨发布的增量转换。几千张照片时再考虑独立图片存储及增量处理。GitHub Pages发布站点上限1GB，月带宽软限制100GB；这是站点容量约束，不代表应把高清原片存进Git仓库。

本地成功构建保留 `.previous-build/` 中的上一版；失败会保留当前 `dist/`。线上撤回则在GitHub把相应内容提交还原到已验证版本后重新部署，不能只恢复网页而漏掉图片。仓库历史不是原片备份；原片另存电脑和独立备份。

## VS Code 本地编辑与发布

将仓库克隆到本地后，使用 VS Code 的“文件 → 打开文件夹”打开仓库根目录。准备好上文的 `.venv` 环境后，通过“终端 → 运行任务”选择：

如果当前文件夹是本地起步代码而非克隆的仓库，先运行 **网站：首次连接 GitHub 仓库**。它获取远端历史并保留本地文件；完成后在 VS Code 源代码管理中检查差异。网络或登录未完成时会停止，代码仍保存在本地。

- **网站：本地预览**：打开 `http://127.0.0.1:8080/`。修改照片、介绍或页面源文件会自动重新构建，刷新浏览器即可查看。
- **网站：检查并发布到 GitHub**：获取远端状态、检查、提交并推送；GitHub Actions 自动更新线上网站。首次发布需要完成 GitHub 登录，并配置 Git 提交署名与邮箱。

发布遇到 GitHub 新提交时会停止，保留本地文件；请先在 VS Code 合并远端更新。无需把密码或访问令牌写入本项目。

## 自有域名

第一版使用github.io地址即可。以后购买域名，在GitHub Pages设置绑定并在注册商配置DNS。无需重新制作网站。`content/site.json`中的`siteUrl`应随正式域名更新。

## 验证与迁移

```sh
python -m unittest discover -s tests -v
```

自动验证图片方向、去除EXIF、不放大小图、项目子路径、构建失败保留旧版本及正文转义。构建后的 `dist/` 是标准静态文件，可以迁移到其他静态托管服务。

官方说明：[Pages基础](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)、[使用限制](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)、[Actions部署](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。
