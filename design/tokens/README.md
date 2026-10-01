# 凑狸设计令牌

版本：2026-10-01 / first proposal，供品牌与交互评审及后续实现使用，尚未最终品牌验收。语义依据见 [品牌色](../colors/colors.md)；覆盖规划/03 §10.1 的颜色、六级字号、间距、圆角与阴影，并补充焦点、主按钮状态及触控命中区。

## 文件与主题

- `design-tokens.json`：机器可读的唯一数值源，采用本仓库明确记录的 `couli.tokens.v1` 结构。
- `variables.css`：同一组值的 H5 消费文件；颜色、间距等映射为 CSS 自定义属性，包含可选的 `.couli-button-primary`、`.couli-control`、`.couli-touch-target` 基础样式。
- 当前只交付浅色 UI，`metadata.theme = "light"`、`color-scheme: only light`；深色 UI 为 P1。图标的深色外观版本不代表 App 内已支持深色主题。

代码仓库建立后把 JSON 复制至 `contracts/design-tokens.json`，由三端与 H5 生成各自的资源；本规划仓库没有自动生成器或运行时主题包。调整配色时先修改 JSON，再同步 CSS 与 `colors/colors.md` 的计算记录，不能只改单端值。

## JSON 结构与转换约定

根节点含 `schemaVersion`、`metadata`、`tokens`；令牌叶节点统一为 `{ "type": "…", "value": …, "description": "…" }`。这是内部交换格式，不声明已经完整实现 DTCG 标准，也没有尚不存在的远程 `$schema` 依赖。所有值均已展开，不需要引用解析器。

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

字体遵循系统字体与动态缩放；不要在 H5 设置固定根字号来禁用用户字号偏好。重要数值可采用等宽数字特性，但不能用颜色代替「预估 / 已结算」等语义。间距采用 `0 / 4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48 / 64`；圆角采用 `8 / 12 / 16 / 24 / 999`，分别覆盖小控件、按钮、卡片、较大面板与胶囊形状。

团队采用 44 × 44 的通用逻辑触控目标，iOS 对应 44 × 44 pt；Android / 鸿蒙按本团队方案扩大为 48 × 48 dp / vp。它是团队采用的推荐目标，不宣称为所有平台的硬性最低尺寸。主按钮最小高度为 48，随大字号可继续增高；可见图标即使是 24，触控区域仍需达到目标。不能把相邻控件的扩展命中区做成重叠区域。

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

JSON、CSS 只定义视觉与基础交互，不实现登录、授权、价格计算或购买行为。平台来源使用 `color.source.*` 中性色；此版不引入任何商家品牌色。

## 验收与来源

颜色对比度公式与全部关键组合见 [品牌色 §3](../colors/colors.md#3-对比度实测)。尤其主色 `#C44820` 在暖米白上只有 4.41:1，普通链接与强调文字须使用 `color.text.link` / `color.brand.emphasis`，不能直接复用主色。必要控件边界使用 `color.border.control`；浅分隔线只能装饰。

遵循 [Apple HIG · Color](https://developer.apple.com/design/human-interface-guidelines/color) 和 [Apple HIG · Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) 的语义用色、对比、非颜色线索及适应用户需求原则（核对日期：2026-10-01）。首版已校验 JSON 可解析、JSON 与 CSS 值一致、指定实色组合的对比度；三端 Dynamic Type、屏幕阅读器、触控、焦点、系统强制高对比及实际素材叠加效果，仍需在实现和真机上验证。
