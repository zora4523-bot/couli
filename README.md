# 凑狸

<img src="design/logo/source/logo-horizontal.svg" width="280" alt="凑狸 Logo">

凑狸的规划与设计仓库。当前项目采用第二版「环尾」品牌方案，包含 Logo、语义配色、设计令牌和可交互展示页；正式 App 与后端工程尚未在本仓库建立。

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

当前 UI 采用浅色主题。图标的深色 / 单色构图独立于 UI 主题；系统材质、原生辅助功能和真机验收仍在后续工程阶段完成。中文品牌名为「凑狸」，正式英文名与 Slogan 保持待定。

## 项目文档

- [规划总览与已确认决定](规划/00_总览与决策.md)
- [前端架构与设计系统](规划/03_前端架构.md)
- [品牌与设计素材清单](design/README.md)
- [业务规则索引](规划/08_业务规则/README.md)
- [开发协作规则](规划/11_开发协作与自主推进.md)

有效业务规则以 `规划/` 为准；根目录早期 PRD 与评审文件保留作历史参考。
