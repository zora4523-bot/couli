# 凑狸 Logo · 环尾

2026-10-01 第二版设计（按 Claude Code 评审修订），已按本轮要求作为当前项目的品牌基线采用。品牌中文名沿用已确认的「凑狸」；资源统一入口见根目录 [brand.config.json](../../brand.config.json)，页面与跨端接入见 [接入指南](../../docs/brand-integration.md)。

![品牌概览](../brand/brand-overview.png)

短吻、双耳和卷尾构成一个小狸形象；一道宽尾纹给连续圆环增加辨识点。轮廓仍隐含拼音首字母 C，表达把需求、优惠与商品凑到一起。图形由两个实色闭合子路径组成，不依赖眼睛、胡须或小字。动物种类的识别属于待用户观察验证的设计假设，不声称人人都能认出具体物种。

品牌色为狸橙 `#C44820`，字标用墨棕 `#28251F`。没有使用电商平台商标、系统符号或 Apple 商标。Apple 指南应用在图形的简洁性、缩小识别和 App 图标制作流程上，并不意味着 Apple 对本设计作过认证；对应制作说明见 [App 图标](../app-icon/README.md)。

## 文件

| 用途 | SVG 源文件 | PNG |
| --- | --- | --- |
| 主图形 | [logo-mark.svg](source/logo-mark.svg) | [透明底](export/logo-mark.png) |
| 横向组合 | [logo-horizontal.svg](source/logo-horizontal.svg) | [透明底](export/logo-horizontal.png) |
| 竖向组合 | [logo-vertical.svg](source/logo-vertical.svg) | [透明底](export/logo-vertical.png) |
| 单色 | [logo-mark-mono.svg](source/logo-mark-mono.svg) | [透明底](export/logo-mark-mono.png) |
| 反白 | [图形](source/logo-mark-inverse.svg)、[横版](source/logo-horizontal-inverse.svg)、[竖版](source/logo-vertical-inverse.svg) | `export/` 下对应 `*-inverse.png` |

PNG 导出宽度均为 2048 px。SVG 图形与中文字标均为路径，无字体依赖、位图、外部资源或脚本；反白文件在白底预览时不可见，应放深色背景。

## 使用规则（本项目自定）

- 图形建议最小显示 24 × 24 pt/CSS px，指完整 SVG 画布（原始 viewBox 为 256 × 256）映射后的尺寸，不是有色轮廓包围盒；下方 16/24/32/48 对照也沿用这个口径。示例 App 标题使用 30px 画布，高于此建议值；横版至少宽 112 pt/CSS px；竖版至少宽 80 pt/CSS px。更小空间使用图形，不放文字组合。
- 四周至少留出图形实际高度的 1/4；源文件画布的内边距不代替排版留白。
- 保持等比缩放，使用平涂原色、墨棕单色或反白。不要拉伸、描边、旋转、添加表情或把促销文字叠在图形上。
- 品牌图形允许透明底；App 图标的提交底图必须按对应系统规格制作。展示页圆角仅模拟系统裁切，不应写回图标源文件。
- 动画可作为后续交互细节，当前交付的主标为静态；系统开启减少动态效果时保留静态标志。

## 字体与编辑

中文字标取自 **Noto Sans CJK SC Bold**，已转成轮廓路径，仅包含「凑狸」两字。字距为字体字号的 6%；第二版将横版文字缩至 114/256 画布单位并缩小图文间距，以减轻粗黑字标对圆润图形的压迫感。字形本身未作结构改写，避免用装饰损害中文识读。字体来源：[Noto CJK 官方仓库](https://github.com/notofonts/noto-cjk/tree/main/Sans)，许可：[SIL Open Font License 1.1](https://github.com/notofonts/noto-cjk/blob/main/Sans/LICENSE)。未打包整套字体。常规界面文字仍使用系统字体并支持动态字号。

导出示例（安装了 librsvg 时）：`rsvg-convert -w 2048 source/logo-horizontal.svg -o export/logo-horizontal.png`。也可在支持 SVG 的矢量编辑器中等比导出透明 PNG。

品牌展示标题「聪明找好物，优惠看得清。」是本次提案文案，不修改 [名称与 Slogan](../brand/name.md) 中 Slogan 的待定状态；英文名已定为 Couli（2026-10-06），`COULI` 是它的大写字标写法。

## 本轮对照

[三个方案与小尺寸对照](../brand/logo-comparison.png)：A 为短吻完整尾，B 为短吻加一道宽尾纹（本轮选择），C 增加面部留白。B 在减少细节的同时保留尾纹；C 的面部孔洞在 16 px 较拥挤，因此未选。24 px 仍是建议最小使用尺寸，16 px 仅用于压力检查。第一版 SVG 归档于 `_archive/v1-20261001/`，可从 Git 恢复其余导出稿。
