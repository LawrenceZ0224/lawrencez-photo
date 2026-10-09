# LawrenceZ 摄影网站

GitHub Pages 项目：LawrenceZ0224/lawrencez-photo。线上地址：https://lawrencez0224.github.io/lawrencez-photo/ 。导航为 Top、Work、Wandering on Earth、Portrait、Profile、Journal。Top 返回白底入口。

## 日常照片管理

用 VS Code 打开 `/Users/lawrencez/Desktop/个人网站/code`。照片放在 code 外的同级文件夹，不必手动编写相册配置：

```text
个人网站/
├── Work/
│   └── 2026/                  每年的非系列作品
├── Wandering on Earth/
│   └── Italy/                 按地点分类，支持中文文件夹名
├── Portrait/
│   └── 主题名称/               按人物或拍摄项目分类
└── code/                      网站代码和自动准备的公开副本
```

照片直接放在年份、地点或主题文件夹内，不要再套一层子文件夹。文件夹名就是页面标题。照片支持 JPG、JPEG、PNG、WebP、TIFF；RAW、HEIC 请先导出成片。只放准备公开的作品，不需要把所有原片放进去。按文件名自然排序，推荐 `001.jpg`、`002.jpg`；第一张默认是相册封面。可在相册内增加 UTF-8 的 `相册介绍.txt` 写介绍。

在 VS Code 的“终端 → 运行任务”选择 **网站：本地预览**，浏览器打开 http://127.0.0.1:8080/ 。预览运行时，增加、移除、替换照片或相册后会自动导入并重新构建；处理完成后刷新浏览器查看。首次大量导入需要等待，终端每 25 张报告进度。照片更新无需网络或代理。

独立的 **网站：导入照片** 任务只准备照片；预览和发布任务会自动导入，不必重复执行。电脑上鼠标移到 Wandering on Earth 展开地点，手机上点击展开，选择地点后进入照片墙。

照片墙采用 1:1 方形缩略图，默认居中裁切。点击缩略图打开白底高清大图，大图保留原比例；左右箭头切换，右上角 × 关闭，支持键盘左右键、Esc 和手机横向滑动。关闭后保留照片墙滚动位置。

## 原文件、公开副本与删除

`scripts/import_photos.py` 只读取 code 同级相册，生成 `content/` 下的网页成片，最长边不超过 3840 像素，不放大小图，矫正方向、转换 sRGB、去除 EXIF。原文件不被修改或删除。处理后的公开副本会随仓库提交；原片、登录信息不应放进 code。照片文件名和相册名也可能出现在公开元数据中。

导入记录 `_photo-import.json` 用于复用未变的公开副本、跟踪增删；不要手动修改它或往自动管理的相册中混入其他照片。中断复制、损坏图片会停止导入，保留上一批成功的内容。缺少三个来源主文件夹时拒绝独立导入，避免误移除内容。预览遇到问题保留上一版网页。

从本地相册移除照片，会在下次成功导入后从当前网站移除；线上更新仍需发布。GitHub 公开仓库历史可能保留已经提交的照片，删除当前页面不等于清除历史。原文件另做独立备份。

## 发布到 GitHub

预览满意后运行 **网站：检查并发布到 GitHub**。流程为准备照片、构建、检查远端状态、测试、提交、推送；GitHub Actions 自动部署。首次使用需完成 GitHub 登录和 Git 作者身份设置。网络或登录失败会保留本地文件。远端有新提交时停止，请先在 VS Code 合并；不强制覆盖远端历史。

GitHub 仓库 Settings → Pages → Source 使用 GitHub Actions。`.github/workflows/pages.yml` 从已提交的 `content/` 构建，无需访问你电脑上的文件夹。推送 main 表示发布。GitHub Pages 上线内容与本地预览是两个不同版本，未推送的修改不会自动出现在网上。

## 个人介绍与随笔

- `content/site.json`：署名、简介、碎碎念、公开邮箱；`profilePhoto` 可填写 `profile/me.jpg` 并放入对应照片。
- `content/journal/article-name.json`：随笔，文件名使用英文、数字、短横线。

```json
{"title":"文章标题","date":"2026-10-09","excerpt":"摘要","body":"正文第一段。\n\n正文第二段。"}
```

没有照片的分类保持空白，不补充示例作品。Work 年份按降序显示。自动相册 `album.json` 可选 `captions` 和 `focus`；focus 的两个数值是裁切中心横、纵百分比，默认 `[50,50]`。日常无需编辑这些配置。

## 开发与验证

环境初始化：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

```sh
.venv/bin/python scripts/preview.py
.venv/bin/python -m unittest discover -s tests -v
```

`build.py` 生成 640、1280 像素宽度的缩略图尺寸和最长边 3840 像素的大图。所有尺寸提供 WebP，小尺寸额外提供 JPEG 作为回退；大图使用 WebP，避免重复保存大文件。根据屏幕选择缩略图尺寸，完整大图使用最大档。已有图片的构建结果通过内容哈希复用；首次全量处理较慢。

`dist/` 是自动输出，不直接修改。成功构建保留 `.previous-build/`，失败保留当前网站。输出为标准静态文件，可迁移托管。未来绑定自有域名后更新 `content/site.json` 的 siteUrl 和 GitHub Pages 设置。
