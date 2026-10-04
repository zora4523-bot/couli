# 凑狸设计令牌

版本：2026-10-04 / project baseline v0.3.0。2026-10-04 按设计方向第三轮改 App 页面底并新增后台页面底、图片占位、返利强调（`color.rebate.*`）与来源描边令牌（[变更记录](../../docs/changes/20261004-设计方向第三轮.md) §1）；不代表原生或真机验收完成。根配置入口见 [brand.config.json](../../brand.config.json)，完整维护与接入流程见 [品牌接入](../../docs/brand-integration.md)。语义说明见 [品牌色](../colors/colors.md)；覆盖规划/03 §10.1 的颜色、六级字号、间距、圆角与阴影，并补充焦点、主按钮状态及触控命中区。

## 文件与主题

- `design-tokens.json`：机器可读的唯一数值源，采用本仓库明确记录的 `couli.tokens.v1` 结构。
- `variables.css`：自动生成的 H5 消费文件；颜色、间距等映射为 CSS 自定义属性，并追加 `foundations.css` 的基础样式。消费端只需加载这一份 CSS，禁止手改。
- `foundations.css`：手写基础样式源，提供可选的 `.couli-button-primary`、`.couli-control`、`.couli-touch-target`；修改样式后重新生成消费 CSS，不复制品牌色值。
- `../brand/brand-config.js`：由根配置和令牌源生成的浏览器消费配置；与生成 CSS 一起供品牌展示页使用，禁止手改。
- 当前只交付浅色 UI，`metadata.theme = "light"`、`color-scheme: only light`；深色 UI 为 P1。图标的深色外观版本不代表 App 内已支持深色主题。

本仓库已有 `scripts/sync-brand.py`，从根配置定位源文件，生成 CSS 与浏览器配置；它使用 Python 标准库，不是运行时主题服务，也不生成三端原生资源。调整数值先修改 JSON，并同步版本、语义说明及 `colors/colors.md` 中受影响的对比度记录，再在仓库根目录运行：

```sh
python3 scripts/sync-brand.py
python3 scripts/sync-brand.py --check
```

`--check` 只读检查生成物漂移。未来代码仓库的 `contracts/design-tokens.json` 接收固定版本快照，并保留令牌版本与 `SPEC_REF` 的来源关系；各端通过契约版本生成资源，不手工维护第二套数值。具体规划路径、`contract.lock` 与当前已接入范围见 [品牌接入 §4](../../docs/brand-integration.md#4-后续代码工程的接入位置)。

## JSON 结构与转换约定

本版共 87 个令牌叶节点，与 CSS 自定义属性一一对应。根节点含 `schemaVersion`、`metadata`、`tokens`；令牌叶节点统一为 `{ "type": "…", "value": …, "description": "…" }`。这是内部交换格式，不声明已经完整实现 DTCG 标准，也没有尚不存在的远程 `$schema` 依赖。所有值均已展开，不需要引用解析器。

| `type` | `value` 结构 | 平台消费方式 |
| --- | --- | --- |
| `color` | 大写六位十六进制字符串 | 按 sRGB 不透明颜色解析 |
| `dimension` | 数字，另有 `unit: "logical"` | H5 用 px；iOS 用 pt；Android 用 dp；鸿蒙用 vp；布局值不随字号缩放 |
| `fontSize` | 数字，另有 `unit: "logical"` | H5 转 rem（以 16 为基数且保留用户根字号）；iOS 通过 Dynamic Type 缩放 pt 基础值；Android 用 sp；鸿蒙用 fp |
| `lineHeight` | 无单位倍数 | 字号乘此倍数；原生若采用系统文本样式，以可访问性布局为准，不裁切中文字形 |
| `fontWeight` | 数字 | 映射平台字体字重 |
| `fontFamily` | 有序字符串数组 | H5 为字体回退列表；原生使用平台系统字体，不打包 SF 字体 |
| `shadow` | 含 `x/y/blur/spread/color/opacity` 的对象数组 | 尺寸按逻辑单位；CSS 用 rgba；原生采用对应阴影能力，Android 可近似映射 elevation 并视觉复核 |

令牌从 `tokens` 下路径转换为短横线变量名。例如 `color.brand.primary` → `--color-brand-primary`，`color.button.primary.pressed.background` → `--color-button-primary-pressed-background`。文本字号转换为 rem，字重和行高保持无单位，其余尺寸转换为 px。`shadow.none` 的空数组转换为 `none`。

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

颜色对比度公式与全部关键组合见 [品牌色 §3](../colors/colors.md#3-对比度实测)。尤其主色 `#C44820` 在暖米白上只有 4.41:1，普通链接与强调文字须使用 `color.text.link` / `color.brand.emphasis`，不能直接复用主色。必要控件边界使用 `color.border.control`；浅分隔线只能装饰。

遵循 [Apple HIG · Color](https://developer.apple.com/design/human-interface-guidelines/color) 和 [Apple HIG · Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) 的语义用色、对比、非颜色线索及适应用户需求原则（核对日期：2026-10-01）。本版已校验 87 个令牌的 JSON 解析与 CSS 值一致性，以及指定实色组合的对比度；价格 / 白底为 15.28:1，待定状态为 5.33:1，错误状态为 5.64:1。`forced-colors` 中按钮、输入框与焦点线使用系统颜色，但代码回退不能视为已经通过高对比测试。实现必须验证系统强制配色、增强对比、200% 文字放大、灰度与色觉障碍状态辨识；三端 Dynamic Type、屏幕阅读器、触控、焦点及真实素材叠加效果仍需在实现和真机上验证。
