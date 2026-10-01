# 凑狸品牌接入

2026-10-01。现有第二版 Logo、语义配色和设计令牌作为项目当前采用基线，本次整理接入入口与维护方式，不改变视觉方案。当前仓库是规划、设计素材和品牌展示页仓库；实际消费方是 `design/brand/index.html`，尚无 App 工程。本文中的三端接入位置是规划位置，素材就绪与展示页接入不等于原生资源、商店提交或真机验收完成。

## 1. 入口与唯一来源

从根目录 [brand.config.json](../brand.config.json) 进入品牌配置。它登记名称、素材路径、令牌源、语义别名和展示页输出位置，**不另存一套色值**。中文名为「凑狸」；正式英文名与 Slogan 仍未定，`englishName` / `tagline` 保持 `null`，`couli` 仅作项目标识，不据此确定商店英文名或 Bundle ID。

| 位置 | 职责 | 编辑方式 |
| --- | --- | --- |
| [brand.config.json](../brand.config.json) | 品牌名称、资产与文档入口、语义角色到令牌路径的映射 | 修改路径或映射；金额、状态规则不放这里 |
| [Logo SVG 源文件](../design/logo/source/) | 图形、横版、竖版、单色与反白标志 | 编辑矢量源；尺寸、留白与字体来源见 [Logo 规范](../design/logo/README.md) |
| [Logo PNG 导出](../design/logo/export/) | 位图消费文件 | 从相应 SVG 重新导出，不以改 PNG 替代源文件修改 |
| [design-tokens.json](../design/tokens/design-tokens.json) | 语义颜色、字体、尺寸、状态等令牌的唯一机器数值源 | 修改值或语义时先改这里；版本由 `metadata.version` 标识 |
| [foundations.css](../design/tokens/foundations.css) | H5 可选基础控件样式源，同步时追加进生成 CSS | 手写维护；只消费语义令牌，不再定义另一套品牌色；消费端不必单独加载 |
| [sync-brand.py](../scripts/sync-brand.py) | 根据根配置和令牌源生成 H5 消费文件 | Python 3.9+ 标准库脚本，支持生成与只读漂移检查 |
| [variables.css](../design/tokens/variables.css)、[brand-config.js](../design/brand/brand-config.js) | 生成的 CSS 变量、浏览器品牌配置 | 不直接编辑；通过同步脚本更新 |
| [配色规范](../design/colors/colors.md)、[令牌规范](../design/tokens/README.md) | 使用边界、对比度记录、格式及单位映射 | 解释源数据；与源变动同步，不成为第二套可编辑数值源 |

语义别名用于说明用途，例如主行动、价格、待结算和成功状态；它们指向 JSON 中的令牌路径。组件消费对应的语义名，不把当前颜色名称当成业务状态。

## 2. 当前展示页如何消费

```text
brand.config.json
  ├─ 资产路径、品牌信息与语义映射
  ├─ tokens.source → design-tokens.json
  └─ tokens.foundations → foundations.css
             ↓ scripts/sync-brand.py
  design/brand/brand-config.js + design/tokens/variables.css
             ↓
  design/brand/index.html
```

展示页加载生成的品牌配置和一份 `variables.css`，按根配置引用 Logo、图标与语义颜色；基础控件样式已追加在该 CSS 中，消费同一组变量。配置由本地文件生成，不依赖远程主题服务、运行时联盟数据或生产账号。已有方向示意继续使用虚构商品和订单数据，不代表完整 App 已实现。

在仓库根目录运行：

```sh
python3 scripts/sync-brand.py
python3 scripts/sync-brand.py --check
python3 -m http.server 8765 --bind 127.0.0.1 --directory design
```

随后打开 [本地品牌展示页](http://127.0.0.1:8765/brand/index.html)。`--check` 只核对源与生成物是否一致，不写文件，也不代替视觉和无障碍检查。浏览器直接打开 HTML 时同样使用已生成的本地配置；不要求浏览器自行读取仓库根 JSON。

## 3. 修改与校验流程

1. **选择唯一源**：更换素材路径或名称改根配置；改名称时同步令牌文件的 `metadata.name`，校验器会拒绝两者不一致。改变令牌值改 `design-tokens.json`；改变标志轮廓改 SVG 源文件。不要直接改生成 CSS / JS 来修正展示效果。
2. **同步说明和导出**：令牌变化时维护版本及相关描述，并更新配色规范中的受影响对比度记录。Logo 变化时重新导出对应 PNG；若背景或图形色变化，按素材规范同步 SVG / PNG。同步脚本不代替矢量编辑或位图导出。
3. **生成消费文件**：运行 `python3 scripts/sync-brand.py`，查看生成物差异；再运行 `python3 scripts/sync-brand.py --check` 检查漂移。
4. **查看实际效果**：在展示页检查 Logo 比例、色块、按钮与状态标签，并按 [令牌验收说明](../design/tokens/README.md#验收与来源) 检查文字放大、键盘焦点和非颜色线索。改变素材时另查小尺寸与不同背景；改文档不能代替这些检查。
5. **记录采用版本**：代码工程后续接入时固定采用的源版本，按工程的契约发布流程更新消费方；不让各端从浮动文件自行取值。

品牌配置只控制视觉和资产引用。业务文案、金额口径、订单归属、授权与资金状态继续引用 `规划/08_业务规则/`；本次接入不增加 MVP 能力。

## 4. 后续代码工程的接入位置

以下均来自 [前端架构 §2、§3.4、§8、§10](../规划/03_前端架构.md)，是**规划位置，当前未创建**。

| 工程位置 | 后续接入方式 |
| --- | --- |
| `rebate-platform/contracts/design-tokens.json` | 接收当前令牌源的固定版本快照，不手工维护另一套数值；保留令牌版本与规划仓库 `SPEC_REF` 的来源关系 |
| `rebate-platform/tools/codegen/` | 按契约生成流程产出各端令牌资源；接入生成物漂移检查 |
| `rebate-platform/packages/ui-tokens` | 输出 H5 / 后台消费的 CSS 变量与 Tailwind 预设，供 `apps/h5` 等工程使用 |
| `rebate-ios/Packages/DesignSystem/` | 将固定契约版本映射到 SwiftUI 颜色、文本样式、间距和组件；字号响应 Dynamic Type |
| `rebate-android/core/designsystem/` | 将同版令牌映射到 Compose 主题、尺寸与字体单位，并核对字号缩放 |
| `rebate-harmony/common/designsystem/` | 将同版令牌映射到 ArkUI 资源与常量，并核对字号缩放 |

原生工程按现有 `contract.lock` 锁定契约版本；契约发布与 `SPEC_REF` 的规则见前端架构 §2 及 [开发协作 §5](../规划/11_开发协作与自主推进.md)。本仓库同步脚本目前只生成品牌展示页所需的 CSS / JS，不声称已实现 Swift、Kotlin、ArkTS 或 Tailwind 生成器。

资产也按固定版本随各端构建交付；Logo SVG 的路径引用不等于平台工程已能直接加载该格式。具体资源转换、密度、缓存与打包在真实工程中实现和验证，不在此创建空工程冒充接入。

## 5. Logo、系统图标与主题边界

Logo 用于页面和品牌传播，系统 App 图标有独立的背景、留白、图层和平台资源要求。使用 [Logo 规范](../design/logo/README.md) 选择横版、竖版或图形；系统启动器使用 [App 图标规范](../design/app-icon/README.md) 中的对应素材，不能把横版 Logo 当作系统图标，也不能将展示页的模拟圆角写回提交源文件。

MVP UI 仍只采用浅色主题；App 图标的 dark / tinted 构图独立于 UI 主题。分层源素材和 Icon Composer 导入记录不代表已交付 `.icon` 文件、三端工程资源、系统材质效果或真机验收。当前完成与待验证范围以 App 图标规范为准。

## 6. 语义和可访问性

实际令牌值以 JSON 唯一源为准；语义使用说明与对比度计算记录见 [配色规范](../design/colors/colors.md)，单位、字号和基础控件约定见 [令牌规范](../design/tokens/README.md)。接入时特别保留：

- 主色用于主要行动；普通小字或链接使用文字语义令牌，不能直接复用主按钮底色。
- 价格通过文字层级突出；预估和等待使用待定语义，只有已结算 / 已完成使用成功语义；错误同时给出原因与可执行的恢复入口。
- 状态保留可读文字与图形线索，颜色不是唯一信息；焦点环、状态徽标和装饰分隔线各有用途。
- 控件保持足够的命中区；字体响应用户缩放，禁用态使用真实禁用行为；强制颜色样式只是回退，不等于已通过系统测试。
- 工程接入后继续验证大字号、读屏、键盘 / 辅助输入、对比与真实素材叠加，以及各平台真机效果。展示页检查不代替这些验收。
