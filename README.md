# 凑狸

<img src="design/logo/source/logo-horizontal.svg" width="280" alt="凑狸 Logo">

凑狸的规划与设计仓库。当前项目采用第二版「环尾」品牌方案，包含 Logo、语义配色、设计令牌和可交互展示页。后端已在独立的 `rebate-platform` 仓库开发；实际完成度以代码主干、工程台账与验收证据为准。

## 品牌入口

根目录的 [brand.config.json](brand.config.json) 是统一配置入口：登记品牌名称、Logo / App 图标路径、令牌来源和颜色语义。实际素材保留在根目录下的 `design/`，每种内容只维护一份源文件。

| 内容 | 项目内位置 | 使用说明 |
| --- | --- | --- |
| 品牌统一配置 | [brand.config.json](brand.config.json) | 文件路径相对仓库根目录；颜色角色引用令牌路径 |
| Logo SVG | [design/logo/source/](design/logo/source/) | 图形、横版、竖版、单色、反白；[使用规范](design/logo/README.md) |
| Logo PNG | [design/logo/export/](design/logo/export/) | 2048px 宽的透明底导出 |
| 系统 App 图标 | [design/app-icon/](design/app-icon/) | 方形底图、透明分层与外观构图；系统接入说明在目录内 |
| 语义配色 | [design/colors/colors.md](design/colors/colors.md) | 主行动、价格、待定、成功、警告、错误的边界与对比度 |
| 设计令牌唯一数值源 | [design/tokens/design-tokens.json](design/tokens/design-tokens.json) | 80 个颜色、字体、间距、圆角、阴影与交互令牌 |
| H5 样式 | [design/tokens/variables.css](design/tokens/variables.css) | 自动生成的 CSS 变量与基础控件样式 |
| 跨端接入指南 | [docs/brand-integration.md](docs/brand-integration.md) | 现有页面用法、修改流程与未来各工程接入位置 |

## 生成、校验与预览

在仓库根目录运行，依赖 Python 3.9+ 标准库，无需安装前端依赖：

```sh
python3 scripts/sync-brand.py
python3 scripts/sync-brand.py --check
python3 -m http.server 8765 --bind 127.0.0.1 --directory design
```

打开 [品牌与交互展示页](http://127.0.0.1:8765/brand/index.html)。也可以直接打开 [design/brand/index.html](design/brand/index.html)；品牌配置通过本地生成的 JavaScript 加载，不需要在线 API。

修改颜色、字号或尺寸时先改令牌 JSON，修改资源选用或颜色角色时改根配置，再运行生成与校验命令。`--check` 只检查，不修改文件；发现资源缺失、无效令牌或生成物漂移时返回非零退出码。基础控件规则维护在 [foundations.css](design/tokens/foundations.css)，会合入生成的 `variables.css`。不要直接编辑生成文件。

展示页的 Logo、下载链接、图标外观、色块和复制色值读取统一配置；页面与交互样式消费同一套 CSS 令牌。历史评审稿与证据保留在 `design/brand/`，不作为当前数值源。

当前 UI 采用浅色主题。图标的深色 / 单色构图独立于 UI 主题；系统材质、原生辅助功能和真机验收仍在后续工程阶段完成。中文品牌名为「凑狸」，英文名为 Couli（2026-10-06），Slogan 待定。

## 规划与任务看板

本机看板：把 `规划/` 里的任务表、待补信息、业务规则、平台能力验证，和代码仓库 `rebate-platform` 的工程台账合在一个页面上看。依赖 Python 3.9+ 标准库，不装别的东西：

```sh
python3 scripts/kanban.py
python3 scripts/kanban.py --check --local
python3 scripts/kanban.py --export ~/Desktop/couli-board.html
```

打开 [http://127.0.0.1:8766/](http://127.0.0.1:8766/)。页面分规划完成度、开发任务看板、待办与未决、平台能力验证、任务清单（可导出 CSV）几页；来源一有变化，页面两三秒内自己更新，不用刷新。

- **读的是两个仓库的远端主干。** 规划文档和工程台账都经 git 读各自的远端 `main`，所以 PR 一合并看板就跟着变，本机检出落后也不影响。默认每 5 分钟把两个仓库的远端 `main` 拉到各自的私有引用 `refs/kanban/main`，不动任何分支、`origin/main` 和工作区文件；`--fetch 0` 关闭拉取，只用本机已有的提交。
- **`--local` 看还没合并的改动。** 加上它，规划文档改读脚本旁边的本机文件，改一个字页面就变；台账仍读远端主干。
- **任务的状态不写在规划里。** 任务清单取自 [规划/05 §3](规划/05_里程碑与任务拆分.md#3-按线任务清单)，状态由台账 `ops/tasks/*.yaml` 和运行目录 `couli-runs` 的在途状态合出来。「现有拆分都已合并」只说明台账里现有的拆分都合并了，整项任务是否完成看验收记录。
- 代码仓库和运行目录默认取本仓库的同级目录 `../rebate-platform`、`../couli-runs`，可用 `--code-repo`、`--runs-dir` 改；找不到时页面会写明读不到台账、开发状态未知。
- `--check` 解析一遍并打印各项计数：整张表、小节或关键列读不到、远端拉取失败时打印 `WARN` 并返回非零（个别列改名有时只表现为数字变化，改表头后对照计数看一眼）；`NOTE` 只是提示（状态文字没能归类、表格某行少了格），不影响退出码。`--check`、`--json`、`--export` 运行前也会先拉取一次，不想联网就加 `--fetch 0`。
- 状态文字按开头的词归类（已定、待确认、进行中等），归不了类的按待办计并列在提示里。有状态列的条目，详情里显示文档原文；所在的表没有状态列的，会标明是看板归纳的。

除 `--export` 指定的文件外，看板不写规划仓库里的任何文件；快照里有本机路径和台账内容，导出到仓库外面。页面样式取 [设计令牌](design/tokens/variables.css)，脚本与页面在 [scripts/kanban.py](scripts/kanban.py)、[scripts/kanban/](scripts/kanban/)。

## 项目文档

- [规划总览与已确认决定](规划/00_总览与决策.md)
- [循序推进的开发顺序](规划/05_里程碑与任务拆分.md#01-按依赖推进与分段验收)
- [2026-10-04 项目阶段核查（版本快照）](docs/research/20261004-项目阶段核查与执行建议.md)
- [开发计划与 Claude Code 接入步骤](规划/05_里程碑与任务拆分.md#310-本批规划的开发接入)
- [花卷云功能整理与收益优先级](docs/research/20261004-花卷云迭代功能收益评估.md)
- [文章方法对照与页面任务做法](docs/research/20261005-文章方法对照.md)
- [前端架构与设计系统](规划/03_前端架构.md)
- [品牌与设计素材清单](design/README.md)
- [业务规则索引](规划/08_业务规则/README.md)
- [开发协作规则](规划/11_开发协作与自主推进.md)

有效业务规则以 `规划/` 为准；根目录早期 PRD 与评审文件保留作历史参考。
