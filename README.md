# LawrenceZ 摄影网站

GitHub Pages 项目：LawrenceZ0224/lawrencez-photo。线上地址：https://lawrencez0224.github.io/lawrencez-photo/ 。导航为 Top、Portfolio、Wandering on Earth、Portrait、Profile、Journal。Top 返回白底入口，ENTER SITE 进入 Portfolio；Work 已从导航移除，原有内容保留。

## 日常照片管理

用 VS Code 打开“个人网站”中的 `code` 文件夹（当前位置：`/Users/lawrencez/Downloads/同步空间/个人网站/code`）。照片放在 code 外的同级文件夹，不必手动编写相册配置：

```text
个人网站/
├── Work/
│   └── 2026/                  每年的非系列作品
├── Wandering on Earth/
│   └── Italy/                 按地点分类，支持中文文件夹名
├── Portrait/
│   └── 主题名称/               按人物或拍摄项目分类
├── Film/
│   └── Autumn in BUPT 2025/   胶片作品集
├── Profile/                  个人照片
└── code/                      网站代码和自动准备的公开副本
```

照片直接放在年份、地点或主题文件夹内，不要再套一层子文件夹。文件夹名就是相册名称；旅行相册的大标题统一为 Wandering on Earth，下方保留地点名称与当前地点高亮。照片支持 JPG、JPEG、PNG、WebP、TIFF；RAW、HEIC 请先导出成片。只放准备公开的作品，不需要把所有原片放进去。按文件名自然排序，推荐 `001.jpg`、`002.jpg`；第一张默认是相册封面。可在相册内增加 UTF-8 的 `相册介绍.txt` 写介绍。

在 VS Code 的“终端 → 运行任务”选择 **网站：本地预览**，浏览器打开 http://127.0.0.1:8080/ 。预览运行时，增加、移除、替换照片或相册后会自动导入并重新构建；处理完成后刷新浏览器查看。首次大量导入需要等待，终端每 25 张报告进度。照片更新无需网络或代理。

独立的 **网站：导入照片** 任务只准备照片；预览和发布任务会自动导入，不必重复执行。电脑上鼠标移到 Wandering on Earth 展开地点。手机端点击右上角三横线，打开独立白底全屏导航；栏目居中排列，当前栏目以蓝色标记。点击 Wandering on Earth 展开地点，选择地点后进入照片墙。右上角 × 关闭导航并保留原来的浏览位置，也支持 Esc 关闭。

照片墙采用 1:1 方形缩略图，默认居中裁切。点击缩略图打开白底高清大图，大图保留原比例；左右箭头切换，右上角 × 关闭，支持键盘左右键、Esc 和手机横向滑动。关闭后保留照片墙滚动位置。

## Portfolio 与作品集目录

导航中的 Portfolio 打开 `/portfolio/`。顶部为居中的 Photoset 大图；下方左右两栏依次为 Portrait / Wandering on Earth、Film / Landscape。手机端按同样顺序改为单栏。Photoset、Portrait、Film 卡片分别进入对应页面，Wandering on Earth 卡片直接打开 Singapore 照片墙；Landscape 仍保留空白位置，不跳转。

封面在 `content/site.json` 的 `portfolioCovers` 中指定：Photoset 使用 `Portrait/wsy/01.jpg`，Portrait 使用 `Portrait/anqi/01.jpg`，Wandering on Earth 使用 `Wandering on Earth/Italy/IMG_20250325_183512-77.jpg`。Film 使用 `Film/Autumn in BUPT 2025/03.JPG`。`album` 是 content 下的相册路径，`source` 填原照片文件名，`focus` 控制本页裁切位置。封面复用已有公开图片，不重复复制原片，也不改变原有人像作品集封面；导入后按原文件名追踪。移除指定照片前应先更换封面设置，避免构建中断。

Photoset 与 Film 目录在电脑上每行显示三个作品集，封面下方显示作品名称；窄屏自动变为两栏或单栏。Photoset 复用现有人像作品集，顺序仍为 wsy、anqi；目前以 Series 01、Series 02 显示，避免暴露文件夹名称，可在对应 `album.json` 添加 `catalogTitle` 指定正式作品名称。

Film 第一个作品集是 Autumn in BUPT 2025，目录封面使用 `01.JPG`（在其 `album.json` 设置 `coverSource`）。点击进入后显示原比例大图、左右箭头与底部 1:1 缩略图。点击缩略图、键盘左右键或手机横滑均可切换；当前缩略图保持清晰，其余淡化；点击缩略图或左右切换时，缩略图条在半秒内平滑移动，让当前照片居中（首尾照片也能居中）。手机支持手指横向滑动缩略图条，滚动缩略图条不会改变整页位置。连续点击会从当前位置转向最新选择，开启系统减少动态效果时直接定位。不自动播放。后续在 Film 下新建作品集文件夹即可自动导入。Film 为可选来源目录，缺失整个 Film 目录时保留已导入内容。

## 人像作品集

Portrait 采用“作品集选择 → 全屏封面 → START 进入组图”的三层浏览。作品集入口使用居中的 VIEW，全屏封面入口使用居中的 START，入口不展示本地文件夹名。电脑使用横幅封面，手机可以单独指定竖幅封面；导航一直可用。只有一组作品时不显示切换作品集的箭头。增加 `Portrait/主题名称/` 文件夹并放入照片，预览、发布时就会自动增加作品集。

作品集按 `content/site.json` 中的 `portraitOrder` 排序，目前为 `["wsy", "anqi"]`：wsy 是第 01 组，anqi 是第 02 组；公开地址分别是 `/portrait/01/`、`/portrait/02/`，详细组图在对应的 `photos/` 下。旧文件夹名称链接自动转到编号地址，不列入站点地图。以后新增且未指定顺序的作品集会按文件夹名排在后面；无需重命名照片文件夹。组图底部只显示照片序号，不显示文件夹名称。

列表封面与第二层全屏引入可以分开设置：

| 作品集 | 电脑列表封面 | 手机列表封面 | 全屏引入（电脑和手机） |
| --- | --- | --- | --- |
| wsy | 04.jpg | 01.jpg | 07.jpg |
| anqi | 06.jpg | 01.jpg | 04.jpg |

全屏引入在手机上使用对应照片的人物裁切位置，详细作品始终保持完整比例。

详细作品按文件名自然顺序排列（anqi 当前 6 张、wsy 当前 8 张），保持完整比例。组图每 4.5 秒淡入切换，可用 Pause / Play 控制；左右箭头、键盘方向键、手机横滑均可切换，手动切换或打开手机导航后停止自动播放。系统启用“减少动态效果”时默认不自动播放。左下角 Portrait 返回作品集选择页。

如需换封面，修改对应 `content/portrait/作品集/album.json`：`coverSource` 为电脑列表封面，`mobileCoverSource` 为手机列表封面，`introCoverSource` 为第二层全屏引入；可选的 `mobileIntroCoverSource` 可进一步单独指定手机引入照片。填写本地相册中的原文件名即可；同名照片替换或排序变化后仍会正确追踪。新建相册默认使用第一张照片；未设置全屏引入时沿用列表封面，指定全屏引入后手机默认也使用该图。删掉指定封面前，请先更换对应设置或清空它；指定的照片不存在时导入会停止，保留上次成功内容。原片文件夹始终只读，封面设置保存在代码仓库中。

## 原文件、公开副本与删除

`scripts/import_photos.py` 只读取 code 同级相册，生成 `content/` 下的网页成片，最长边不超过 3840 像素，不放大小图，矫正方向、转换 sRGB、去除 EXIF。原文件不被修改或删除。处理后的公开副本会随仓库提交；原片、登录信息不应放进 code。照片文件名和相册名也可能出现在公开元数据中。

导入记录 `_photo-import.json` 用于复用未变的公开副本、跟踪增删；不要手动修改它或往自动管理的相册中混入其他照片。中断复制、损坏图片会停止导入，保留上一批成功的内容。Wandering on Earth、Portrait 为必需来源主文件夹，缺少任意一个时拒绝独立导入，避免误移除内容。Work 与 Film 为可选目录，整个目录缺失时保留其已导入内容，并继续导入其他分类。预览遇到问题保留上一版网页。

从本地相册移除照片，会在下次成功导入后从当前网站移除；线上更新仍需发布。GitHub 公开仓库历史可能保留已经提交的照片，删除当前页面不等于清除历史。原文件另做独立备份。

## 发布到 GitHub

预览满意后运行 **网站：检查并发布到 GitHub**。流程为准备照片、构建、核对 1 GB 站点容量、检查远端状态、测试、提交、推送；GitHub Actions 自动部署。第一次上传大量网页图片可能较久，之后只同步变化的内容。首次使用需完成 GitHub 登录和 Git 作者身份设置。网络或登录失败会保留本地文件。远端有新提交时停止，请先在 VS Code 合并；不强制覆盖远端历史。

GitHub 仓库 Settings → Pages → Source 使用 GitHub Actions。`.github/workflows/pages.yml` 从已提交的 `content/` 构建，无需访问你电脑上的文件夹。推送 main 表示发布。GitHub Pages 上线内容与本地预览是两个不同版本，未推送的修改不会自动出现在网上。

## 个人介绍与随笔

- Profile 使用浅灰背景，电脑端左侧原比例照片上下居中、右侧为白色介绍框；手机端先照片、后介绍框。介绍框暂时完全留白。
- `content/site.json`：`profile`、`notes`、`email` 可在之后填写介绍、碎碎念与公开邮箱。`profilePhotoSource` 指定同级 Profile 文件夹中的照片文件名，导入工具自动生成 `content/profile/photo.jpg`，由 `profilePhoto` 引用。替换同名照片后，预览和发布会自动更新，原文件不被修改。
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
