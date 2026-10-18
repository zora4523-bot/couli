# 凑狸设计令牌

版本：2026-10-18 / project baseline v0.4.0。2026-10-04 按设计方向第三轮改 App 页面底并新增后台页面底、图片占位、返利强调（`color.rebate.*`）与来源描边令牌（[变更记录](../../docs/changes/20261004-设计方向第三轮.md) §1）；2026-10-18 按规划/00 D35 给每个颜色与阴影令牌补深色取值，并新增组件令牌 T1–T12（[变更记录](../../docs/changes/20261018-深色令牌进唯一源.md)）；不代表原生或真机验收完成。根配置入口见 [brand.config.json](../../brand.config.json)，完整维护与接入流程见 [品牌接入](../../docs/brand-integration.md)。语义说明见 [品牌色](../colors/colors.md)；覆盖规划/03 §10.1 的颜色、六级字号、间距、圆角与阴影，并补充焦点、主按钮状态及触控命中区。

## 文件与主题

- `design-tokens.json`：机器可读的唯一数值源，采用本仓库明确记录的 `couli.tokens.v1` 结构。
- `variables.css`：自动生成的 H5 消费文件；颜色、间距等映射为 CSS 自定义属性，并追加 `foundations.css` 的基础样式。消费端只需加载这一份 CSS，禁止手改。
- `foundations.css`：手写基础样式源，提供可选的 `.couli-button-primary`、`.couli-control`、`.couli-touch-target`；修改样式后重新生成消费 CSS，不复制品牌色值。
- `../brand/brand-config.js`：由根配置和令牌源生成的浏览器消费配置；与生成 CSS 一起供品牌展示页使用，禁止手改。
- 令牌源有**浅 / 深两套取值**（规划/00 D35，2026-10-18；规划/03 §10.1）：`metadata.theme = "light"` 是基准主题，`metadata.modes = ["light", "dark"]`，`metadata.darkThemePhase = "MVP"`。每个颜色叶节点的 `value` 是浅色值、`dark` 是深色值；阴影 `shadow.card` / `shadow.floating` 同样带 `dark`（`shadow.none` 两态都是空数组、不带 `dark`）；尺寸、字号等不随主题变化、没有 `dark`。消费方读不到 `dark` 时回退 `value`。语义令牌名只有一套，组件只引用令牌名、不判断主题；取值与消费方式见下文「浅 / 深两套取值与各端消费」。图标的深色外观版本与 UI 主题是两回事。

本仓库已有 `scripts/sync-brand.py`，从根配置定位源文件，生成 CSS 与浏览器配置；它使用 Python 标准库，不是运行时主题服务，也不生成三端原生资源。调整数值先修改 JSON，并同步版本、语义说明及 `colors/colors.md` 中受影响的对比度记录，再在仓库根目录运行：

```sh
python3 scripts/sync-brand.py
python3 scripts/sync-brand.py --check
```

`--check` 只读检查生成物漂移。未来代码仓库的 `contracts/design-tokens.json` 接收固定版本快照，并保留令牌版本与 `SPEC_REF` 的来源关系；各端通过契约版本生成资源，不手工维护第二套数值。具体规划路径、`contract.lock` 与当前已接入范围见 [品牌接入 §4](../../docs/brand-integration.md#4-后续代码工程的接入位置)。

## JSON 结构与转换约定

本版共 109 个令牌叶节点（v0.3.0 的 87 个 + 2026-10-18 新增 22 个），与 CSS 自定义属性一一对应；其中 46 个（44 个颜色 + 2 个阴影）带深色值。根节点含 `schemaVersion`、`metadata`、`tokens`；令牌叶节点统一为 `{ "type": "…", "value": …, "description": "…" }`，颜色与阴影叶节点另有 `"dark": …`（结构与 `value` 相同）。这是内部交换格式，不声明已经完整实现 DTCG 标准，也没有尚不存在的远程 `$schema` 依赖。所有值均已展开，不需要引用解析器。

| `type` | `value` 结构 | 平台消费方式 |
| --- | --- | --- |
| `color` | 大写六位十六进制字符串 `#RRGGBB`；带透明度的遮罩类用八位 `#RRGGBBAA`（末两位为透明度，目前只有 `color.overlay.scrim`） | 六位按 sRGB 不透明颜色解析；八位 CSS 输出为 `rgba()`，iOS 按 RGBA 读取；Android `colors.xml` 与鸿蒙 `color.json` 的八位格式都是 `#AARRGGBB`，生成时须换位（浅 `#28251F66` → `#6628251F`，深 `#0000008C` → `#8C000000`），直接照抄会变成接近全透明 |
| `number` | 无单位数字 | 倍数或比例，原样使用（目前只有 `component.checkbox.max-scale`） |
| `dimension` | 数字，另有 `unit: "logical"` | H5 用 px；iOS 用 pt；Android 用 dp；鸿蒙用 vp；布局值不随字号缩放 |
| `fontSize` | 数字，另有 `unit: "logical"` | H5 转 rem（以 16 为基数且保留用户根字号）；iOS 通过 Dynamic Type 缩放 pt 基础值；Android 用 sp；鸿蒙用 fp |
| `lineHeight` | 无单位倍数 | 字号乘此倍数；原生若采用系统文本样式，以可访问性布局为准，不裁切中文字形 |
| `fontWeight` | 数字 | 映射平台字体字重 |
| `fontFamily` | 有序字符串数组 | H5 为字体回退列表；原生使用平台系统字体，不打包 SF 字体 |
| `shadow` | 含 `x/y/blur/spread/color/opacity` 的对象数组 | 尺寸按逻辑单位；CSS 用 rgba；原生采用对应阴影能力，Android 可近似映射 elevation 并视觉复核 |

令牌从 `tokens` 下路径转换为短横线变量名。例如 `color.brand.primary` → `--color-brand-primary`，`color.button.primary.pressed.background` → `--color-button-primary-pressed-background`。文本字号转换为 rem，字重和行高保持无单位，其余尺寸转换为 px。`shadow.none` 的空数组转换为 `none`。

## 浅 / 深两套取值与各端消费

两套取值都只在 `design-tokens.json` 里维护：浅色在 `value`，深色在 `dark`；没有第二个文件，也没有「深色令牌表」。深色取值 2026-10-18 按组件库画板的深色提案进源（提案与对比度计算在 couli-runs `design-hifi/components/tokens/`，不入本仓库），全部组合按下文「验收与来源」的对比度要求复核过，没有需要调整的项。原则：狸橙主色、按下态、实底与其上的白字在两种主题下**同值**（白字 4.89:1），强调文字 / 链接 / 返利文字换成更亮的橙（`#F0956B` / `#F29A6E`）以在深底上达到正文对比度；页面底、卡片底、分组底、占位底是四级由深到浅的暖灰（`#171513` → `#24211E` → `#2F2B27` → `#36312C`），App 与管理后台页面底在深色下同值；状态色（待定、成功、警告、错误）文字提亮、浅底压暗，语义与图形线索不变；卡内白底按钮（`color.button.inverse.*`）在深色下仍是白底深橙字。

| 消费端 | 接法（由规划/05 DS-02 实现，本仓库只定义取值） |
| --- | --- |
| H5 / 管理后台（CSS） | 只加载一份 `variables.css`：`:root` 是浅色值；`@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }` 与 `:root[data-theme="dark"]` 是两个**同值**的深色块，只覆盖带 `dark` 的令牌，并把 `color-scheme` 设为 `dark`。页面默认跟随系统；App 内 H5 由宿主在 `<html>` 上写 `data-theme="dark"` / `"light"` 与原生保持同一主题，站外 H5 不写该属性。页面不要再写 `color-scheme: only light` |
| iOS（Asset Catalog） | 每个颜色令牌一个 Color Set，`Any Appearance` 填 `value`、`Dark` 填 `dark`；SwiftUI 用 `Color("color-text-primary")` 之类的令牌名取色，系统切换外观时自动换值，不在视图里判断 `colorScheme`。阴影两套用 `shadow.*.dark` 对应 |
| Android（资源目录） | `values/colors.xml` 放 `value`、`values-night/colors.xml` 放同名的 `dark`；Compose 主题按 `isSystemInDarkTheme()` 选 `lightColorScheme` / `darkColorScheme`，两套都从令牌生成，并把 M3 的 `surfaceContainer*`、`secondaryContainer`、`scrim` 等映射补齐（组件清单 §7）。八位十六进制换成 `#AARRGGBB` |
| 鸿蒙（资源目录） | `resources/base/element/color.json` 放 `value`、`resources/dark/element/color.json` 放同名的 `dark`；ArkUI 用 `$r('app.color.color_text_primary')` 引用，系统深色时自动命中 `dark` 目录；八位十六进制同样换成 `#AARRGGBB`；系统组件的品牌色经 `ThemeControl.setDefaultTheme` 按令牌映射 |
| 代码仓库契约 | `contracts/design-tokens.json` 接收本文件的固定版本快照（含 `dark` 字段），各端生成器从同一快照产出上述资源，不手工维护第二套数值（规划/03 §10.1） |

组件验收用两态截图（规划/03 §10.2「两态交付」）；深色下关键页的可读性与对比度按规划/10 AC-S1-185 验收。

## 字体、节奏与触控

| 字号令牌 | 基础字号 | 行高倍数 | 场景 |
| --- | ---: | ---: | --- |
| `font.size.caption` | 12 | 1.5 | 非核心补充信息；不用于主要价格与操作 |
| `font.size.footnote` | 14 | 1.5 | 次要标签、说明 |
| `font.size.body` | 17 | 1.5 | 正文、主按钮 |
| `font.size.title` | 22 | 1.3 | 模块标题 |
| `font.size.heading` | 28 | 1.25 | 页面标题 |
| `font.size.display` | 34 | 1.2 | 少量品牌展示、核心数字 |

字体遵循系统字体与动态缩放；不要在 H5 设置固定根字号来禁用用户字号偏好。商品标题与正文使用 17 级，次要标签和说明使用 14 级，12 级只作非核心补充信息；避免展示页另写 11 px 字号。重要数值可采用等宽数字特性，但不能用颜色代替「预估 / 已结算」等语义。间距采用 `0 / 4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48 / 64`；圆角采用 `8 / 12 / 16 / 24 / 999`，分别覆盖小控件、按钮、卡片、较大面板与胶囊形状。

团队采用 44 × 44 的通用逻辑触控目标，iOS 对应 44 × 44 pt；Android / 鸿蒙按本团队方案扩大为 48 × 48 dp / vp。它是团队采用的推荐目标，不宣称为所有平台的硬性最低尺寸。主按钮最小高度为 48，随大字号可继续增高；可见图标即使是 24，触控区域仍需达到目标。不能把相邻控件的扩展命中区做成重叠区域。

## 金额与状态语义

- 主按钮使用狸橙；价格使用 `color.price.text` 墨棕，以字号和字重突出，不借用警示色。
- 预估返利和等待结算使用 `color.status.pending.*` 中性色，配钟表图形与明确状态词；金额沿用墨棕或中性文字，不配绿色对勾。
- 仅已结算或已完成使用 `color.status.success.*`，配完成对勾与明确状态词。业务文字与口径以 BR-TEXT-01、BR-TEXT-04、BR-FUND-04 为准。
- 错误使用 `color.status.error.*` 莓红，配警示图形、原因与恢复操作；不得只把原文变红。
- `color.brand.secondary` 保留为品牌辅助色；不要用它绕开业务状态约束。焦点环以控件外轮廓传递焦点，不能与状态徽标混用。

这些图形是状态语义的组成部分：原生选用对应平台图标；H5 使用同一套 SVG 图标。屏幕阅读器应读出状态文字，重复表达同一含义的图标设为装饰，不能只读出“钟表”或“对勾”。

## H5 接入示例

```html
<link rel="stylesheet" href="./variables.css">
<button class="couli-button-primary" type="button">继续</button>
```

```css
.product-card {
  background: var(--color-background-surface);
  color: var(--color-text-primary);
  padding: var(--space-4);
  border-radius: var(--radius-card);
}
.brand-link {
  color: var(--color-text-link);
  text-decoration: underline;
  text-underline-offset: 0.16em;
}
```

`.couli-button-primary` 提供正常、按下、禁用和 `:focus-visible`。原生 `<button disabled>` 可直接禁用；若自定义控件使用 `aria-disabled="true"`，仍须在业务代码中阻止激活，CSS 不会替它禁用行为。加载态应保留尺寸、可读文字与忙碌语义；具体文案由页面规则决定。

JSON、CSS 只定义视觉与基础交互，不实现登录、授权、价格计算或购买行为。平台来源使用 `color.source.*`（白底、浅描边、中性文字）；此版不引入任何商家品牌色。返利金额与其标签用 `color.rebate.*`，价格仍用 `color.price.text`，状态标签仍用 `color.status.*`。

## 验收与来源

颜色对比度公式与全部关键组合（浅色与深色各一张表）见 [品牌色 §3](../colors/colors.md#3-对比度实测)。尤其主色 `#C44820` 在暖米白上只有 4.41:1、在深色页面底上只有 3.72:1，两种主题下普通链接与强调文字都须使用 `color.text.link` / `color.brand.emphasis`，不能直接复用主色。必要控件边界使用 `color.border.control`；浅分隔线只能装饰。

遵循 [Apple HIG · Color](https://developer.apple.com/design/human-interface-guidelines/color) 和 [Apple HIG · Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) 的语义用色、对比、非颜色线索及适应用户需求原则（核对日期：2026-10-01）。本版已校验 109 个令牌的 JSON 解析与 CSS 值一致性（`--check` 同时核对两个深色块与 JSON 的 `dark` 一致），以及指定实色组合的对比度：浅色价格 / 白底为 15.28:1，待定状态为 5.33:1，错误状态为 5.64:1；深色主文字 / 卡片底为 13.84:1，待定状态为 6.28:1，错误状态为 6.72:1，禁用文字为 4.64:1，控件边界 / 卡片底为 4.25:1。`forced-colors` 中按钮、输入框与焦点线使用系统颜色，但代码回退不能视为已经通过高对比测试。实现必须验证系统强制配色、增强对比、200% 文字放大、灰度与色觉障碍状态辨识；三端 Dynamic Type、屏幕阅读器、触控、焦点及真实素材叠加效果仍需在实现和真机上验证。
