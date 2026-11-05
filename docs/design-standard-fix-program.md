# 凑狸设计标准整改计划

2026-11-05 · 状态：生效（执行计划）· 维护：编排会话

这份文档说明设计标准整改**为什么做、守住什么、分几期、每条线做哪些事**。任务的登记与派工状态在 [规划/05 §3.11](../规划/05_里程碑与任务拆分.md#311-设计标准整改2026-11-05)（看板读那里），开工后的拆分与进度以代码仓库台账为准；业务规则的取值只在 [规划/08](../规划/08_业务规则/README.md)，本文不复述，引用处与 08 不一致时以 08 为准。审计报告、画板、抽数与检查脚本放在私有运行目录 couli-runs（`design-audit-20261105/`、`design-hifi/`），本文只给结论和指针，不转贴其中内容。

## 1. 为什么整改

2026-11-05 编排按 13 个维度做了一次设计标准审计，记下 215 条问题，其中 46 条严重，每条都经过反驳核实。结论是：

- **令牌与画板扎实**：令牌唯一源、浅深两套取值、定稿画板与 sha256 登记都已就位。
- **标准没有落到组件和代码**：组件规范还是草稿，没有状态目录、页面模板和动效规则，代码里也没有拦写死样式的检查。
- **跨端已经不一致**：轻提示有四种、错误态有四种，按钮参数三端不同，iOS 有两种导航栏，图标有两套，iOS 还锁着浅色；三端锁定的令牌版本也落后于唯一源。

负责人同日定调「组件按规划统一，这类不用问」，并要求组件改一处就同步到所有用到的地方。P0 当天按 D10-643 派出。

## 2. 整改要守住的标准

整改不是逐条修补，而是把下面七个方面各自落到唯一的依据上。以后新页面和新组件都按这些依据做和验，偏离的要么改回，要么走变更。

| 方面 | 现在的问题 | 整改后以什么为准 | 主要任务 |
| --- | --- | --- | --- |
| 视觉定位 | 品牌个性、插画与品牌 IP 用法、语气只散在画板和对话里；Slogan 未定 | 公开的设计原则文档 `design/principles.md`（个性词各附「要 / 不要」示例）、视觉参考板、负责人选定的 Slogan | DSX-05、DSX-92、DSX-93、DSX-103 |
| 设计语言（令牌） | 三端锁的令牌版本落后，深色值靠手抄表，鸿蒙有旁路副本；布局、动效、层级、图表没有令牌 | 唯一源 `design/tokens/design-tokens.json`；三端与 H5 只锁发布提交并由生成器出全部类别；落后由 CI 告警 | TOKENS-PIPE-android / harmony、DS-02-iOS-1、DSX-02～04、DSX-120～122、CT-11c、TOKENS-LAG |
| 层级 | 关键页规格没有写信息层级，同名「标题」在三端默认字重不同，没有页面模板 | 组件规范的文字角色表；03 的「页面模板」节与页面规格的「0. 信息层级」；PageScaffold 与 layout 令牌 | COMP-SPEC、DSX-11、DSX-15、DSX-54、DSX-66、DSX-76 |
| 组件 | 组件规范未定稿，按钮、胶囊、输入、弹层三端参数不同，页面里私写同类件，图标两套 | 规划仓库 `design/components/`（组件规范 v1.0 与机读表 component-spec.json）；组件库维护常驻任务与差异上限；图标唯一 SVG 源 | COMP-SPEC、COMP-SPEC-2、DSX-118、DSX-119、DS-03、DSX-06、DSX-23、各端迁移单 |
| 动效 | 没有转场目录与动效令牌，减弱动态没有统一入口，轮播与公告节奏各写各的 | 03 的「动效规范」节与 motion 令牌，三端统一入口 | DSX-03、DSX-13、DSX-61、DSX-70、DSX-83 |
| 状态 | 没有状态目录，首次加载、断网、结果未知、字段缺失各端各写，金额缺失有补 0 的 | 契约 `specs/ui-states.yaml` 状态目录与 08 的通用状态键；三端与 H5 的状态组件按目录实现 | DSX-01、UI-STATES、FU-DS-*、DSX-21、DSX-48、CT-09b |
| 验收标准 | 代码没有拦写死样式，视觉验收没有容差和模板，截图基准与无障碍检查不全 | LINT-STYLE（三端与 Web）按基线只减不增；视觉验收规范包；10 的视觉验收用例；截图基准、无障碍守卫与真机冒烟 | LINT-STYLE-*、DSX-09、DSX-14、DSX-50、DSX-86、DSX-62 / 71 / 84、DSX-91、DSX-136 |

深色、商品图、图表与价格走势是贯穿多个方面的专项：iOS 去掉整 App 浅色锁（DSX-127）与 H5 深色修正（H5-DARK）；商品图统一为 ProductImage（DSX-118 与三端 DS-02-*-image）；图表色板与看板规范（DSX-04、DSX-39）；价格走势的图形规则与三端改正（DSX-37、DSX-38、DSX-134、DS-02-android-trend、DS-02-harmony-trend）。

## 3. 分期

整改分期只表示本计划内的先后，与 00 的产品分期 P1 / P2 无关。

| 分期 | 项数 | 内容 | 登记 |
| --- | --- | --- | --- |
| P0 | 27 | 挡住后面所有页面单的基础：组件规范定稿、三端令牌管线与写死样式检查、状态目录、iOS 首页接口与组件库三单、H5 深色修正、详情 v3 的令牌与改稿 | 05 §3.11 |
| P1 | 157 | P0 落地后按线分批派：令牌 v0.6.0 与三端跟锁、页面模板与 PageScaffold、图标一套源、动效、SDUI 按 schema 解码、H5 跟随深色与字号、商品图组件、视觉回归与无障碍检测、图表与价格走势改正、商店截图模板、各页迁移到组件库 | 05 §3.11（与 05 原任务相关的 8 项在原行加指针） |
| P2 | 40 | 公开上架前后视情况排：后台版式令牌、海报与分享素材、读屏用词改取字典、防连点、Lottie 弹窗动效、Slogan 等 | 只在本文；满足立项条件后再登记 05 |

P1 原为 156 项，按 D10-664 ③ 从 CT-22-trend 拆出 CT-22-mode 后为 157 项，全计划共 224 项。派工顺序按 D10-643：各线 P0 插到当前单之后、下一个页面单之前；商品详情 v3 合派排在各线 P0 之后（D10-664）。

## 4. 2026-11-05 晚编排裁定带来的调整

1. **令牌版本顺延。** 详情 v3 回写已用掉 v0.5.0，编排又补到 v0.5.1（couli #276 f088f04，新增 radius.tag、radius.avatar）。本计划原写「v0.5.0」的地方（DSX-02 发布、DSX-120～122 三端跟锁、CT-11c 等）一律改为 **v0.6.0**；原写 DETAIL-V3-WB「v0.4.1」处按实际的 v0.5.0 / v0.5.1 读。TOKENS-PIPE（安卓、鸿蒙）与 DS-02-iOS-1 的令牌锁直接升到 v0.5.1（D10-665）。计划原文引用的 79c554e 是合并前的提交，合并后为 d0aaa76（#274）。
2. **DETAIL-V3-WB 已完成**：v3 回写 couli #274（d0aaa76），令牌 #276（f088f04）。
3. **DSX-117 已完成**：编排以 D10-664 派出商品详情 v3 三端合派，任务书在私有运行目录 couli-runs/DETAIL-V3/。
4. **CT-22-trend 拆单（D10-664 ③）**：最常见价字段 mode_price_fen 拆成 CT-22-mode 单独一单（D10-664 记为 S-05），不依赖 DSX-37，v3 不等走势规则；CT-22-trend 只剩文本键、几何测试向量与拼多多来源键。B1-29-trend 里最常见价的计算即 v3 服务端 S-12，只依赖 CT-22-mode。
5. **D10-643 已派的 P0 记为进行中**：UI-STATES、TOKENS-LAG、TOKENS-PIPE-android、TOKENS-PIPE-harmony、LINT-STYLE-android、LINT-STYLE-harmony、APP-17-ios-apple、FU-X-HOME-PAGE-API-ios、DS-02-iOS-1、DS-02-iOS-2、DS-02-iOS-3、LINT-STYLE-web、H5-DARK。组件规范（COMP-SPEC 一～四）与组件库维护常驻任务 DS-03 是编排自己的 ⑨ ⑩，尚未完成，记为待排；三端 FU-DS 在 UI-STATES 合并后再派。
6. **等负责人的三项**：鸿蒙关怀模式字号封顶（DSX-133，06 Q-A12；DSX-85 按决定实施）、商店截图里的平台标识口径（DSX-35，06 Q-A13，其余部分先做）、Slogan（DSX-93，06 Q-E1）。05 里这几行的「周」列写「等负责人」。
7. **v3 合派的其他相关裁定（D10-664）**：iOS 价格走势 DSX-134 与 iOS 详情 v3 同批派、分开合；安卓、鸿蒙的走势组件先改正，改正前详情里整块不接走势，不另加开关；首页横滑卡先按组件规则落地实底平台标签，DSX-126 改稿出来后再对稿。

## 5. 按线任务清单

每条线先列 P0，再列 P1、P2。「依赖」只列本计划内的任务键；「对应 05 原任务」写本项沿用或补充的 05 任务，标「原行加指针」的不在 05 另建行。各项的完整范围与验收见[附录](#附录-各项范围与验收)。

### 5.1 设计（66 项：P0 9、P1 45、P2 12）

| 编号 | 标题 | 负责线（协同） | 分期 | 依赖 | 验收要点 | 对应 05 原任务 |
| --- | --- | --- | --- | --- | --- | --- |
| COMP-SPEC | 组件规范 v1.0 定稿（一）：框架、基础控件、文字角色与机读规格表 | 设计（协同 iOS、安卓、鸿蒙、前端） | P0 | DETAIL-V3-WB | design/components（v1.0 生效）与 component-spec.json 合入，覆盖清单全部组件并有三端实现名，每个数值只有一个取值 | — |
| COMP-SPEC-2 | 组件规范 v1.0 定稿（二）：反馈与弹层、通用状态、按压与动效归属 | 设计（协同 iOS、安卓、鸿蒙、前端） | P0 | COMP-SPEC | component-spec.json 含反馈、弹层与通用状态各组件行，状态组件、按压与动效归属有书面裁定 | — |
| DSX-118 | 组件规范 v1.0 定稿（三）：商品图 ProductImage（四态、图框、渐显、读屏键） | 设计（协同 iOS、安卓、鸿蒙、前端） | P0 | COMP-SPEC | component-spec.json 有 ProductImage 行（四态、各图框、渐显、读屏），网格图框只有一种写法 | — |
| DSX-119 | 组件规范 v1.0 定稿（四）：首页 8 类 SDUI 卡、订单与资金业务件、tonal 与卡内 40 高按钮裁定 | 设计（协同 iOS、安卓、鸿蒙、前端） | P0 | COMP-SPEC | component-spec.json 含订单与资金业务件、首页 8 类卡各行，tonal 与卡内 40 高按钮有裁定 | — |
| DS-03 | 组件库维护常驻任务：改一处、处处同步，设差异上限，通用状态不得带差异合并 | 设计 | P0 | — | 05 有 DS-03 常驻行并为每个欠账写明承接任务，11 写入同步清单、差异上限与视觉一致性定级 | — |
| DETAIL-V3-WB | 详情 v3 令牌与组件补登：平台实底标签色、图上控件底、标签与头像圆角进令牌（实际 v0.5.0 / v0.5.1） | 设计（协同 iOS、安卓、鸿蒙、前端） | P0 | — | 令牌源含平台标签色、图上控件底、radius.tag / radius.avatar，已有键取值不变，sync-brand --check 通过 | — |
| DSX-117 | v3 合派（D10-641）任务书补充：平台标签令牌、最常见价为空不显示、走势不加开关、详情浮动返回键 | 设计（协同 iOS、安卓、鸿蒙、前端） | P0 | DETAIL-V3-WB、DSX-126 | v3 合派三端与 H5 任务书都含五项补充及对应验收 | — |
| DSX-01 | 08 登记通用状态键与金额缺失展示规则，修正 BR-TEXT-14 影响面 | 设计（协同 后端） | P0 | — | 08 表 C 有 state.* 通用状态键，BR-TEXT-10 有金额缺失展示条文 | — |
| DSX-126 | Main-v3 首页横滑卡平台文字标签改稿（v3 合派前完成） | 设计（协同 iOS、安卓、鸿蒙、前端） | P0 | DETAIL-V3-WB | Main-v3 改稿已登记 sha256 并通过 Codex 审查 | — |
| DSX-02 | 令牌升版（一）：文字角色、组件变体与状态、基础令牌、图框尺寸，统一发布 v0.6.0 | 设计（协同 iOS、安卓、鸿蒙、前端） | P1 | COMP-SPEC、COMP-SPEC-2、DSX-118、DSX-119、DETAIL-V3-WB、DSX-03、DSX-04、DSX-08 | sync-brand --check 通过，metadata.version 为 0.6.0，DSX-03 / DSX-04 的键随本版发布 | — |
| DSX-03 | 令牌升版（二）：布局、动效、叠放层级、反色标题栏，写清阴影各端换算 | 设计（协同 iOS、安卓、鸿蒙、前端） | P1 | COMP-SPEC、COMP-SPEC-2 | 布局、动效、叠放层级、反色标题栏令牌入源（不改版本号），生成的 CSS 带对应变量 | — |
| DSX-04 | 图表规范与色板令牌：color.chart.* 浅深两套，03 §10 加「图表」一节，含 Grafana 看板规范 | 设计 | P1 | — | design-tokens.json 有 color.chart 组，sync-brand --check 通过 | — |
| DSX-05 | 公开设计原则文档：个性词、插画与品牌 IP 用法、品牌语气规则 | 设计 | P1 | COMP-SPEC-2、DSX-08 | design/principles.md 有个性词、插画与品牌 IP、品牌语气各节，每个个性词都有「要 / 不要」示例 | — |
| DSX-06 | 定三端图标口径、导出唯一 SVG 源，补启动页规范 | 设计 | P1 | — | design/icons/tab 下至少 8 个 SVG，清单里其余图标都有文件 | — |
| DSX-07 | 规划仓库设计文档一次清理：过期说法、清单状态、深色图片与标识、分享与海报文档同步 | 设计 | P1 | — | 过期短语检查在 origin/main 上 0 命中，故意加一句「MVP 强制浅色」会报 | — |
| DSX-08 | GUIDE v2 迁入规划仓库 design/guide/：令牌表由令牌源生成、去敏、收齐待同步改动 | 设计 | P1 | COMP-SPEC、COMP-SPEC-2、DETAIL-V3-WB | design/guide/GUIDE.md 在 origin/main，令牌表生成器 --check 无漂移 | — |
| DSX-123 | 画板自检 verify.py v2：颜色与刻度读令牌、深色稿用 dark 值、可点尺寸与对比度、与基线比较 | 设计 | P1 | DSX-08 | 对 WithdrawDark、OrdersDark 报 0 条令牌外颜色 | — |
| DSX-124 | claude.ai「凑狸设计系统」处置：按 v0.4.0 以上令牌重发或标停用 | 设计 | P1 | — | claude.ai 设计系统 README 顶部写明版本 ≥0.4.0 或已停用，并指向规划仓库 design/ | — |
| DSX-09 | 视觉验收规范包：容差表、验收模板、三端并排对照与设计差异台账 | 设计（协同 iOS、安卓、鸿蒙、前端、质量） | P1 | — | visual-acceptance.md 含容差表与验收模板等五节，设计差异台账迁入并带状态列 | — |
| DSX-10 | 适配与无障碍规范 v2 定稿：视口、安全区、大字号让位、系统辅助设置、CAP-X-18、鸿蒙平板 | 设计（协同 鸿蒙、质量、前端） | P1 | — | 规范 §1、§2、§5 里「本轮补充，待确认」「待商量」为 0，剩下的待确认各有 Jev 编号 | — |
| DSX-11 | 03 新增「页面模板」节，规格模板加「0. 信息层级」，11 §2.6 状态更正 | 设计 | P1 | — | 03 有「页面模板」节，5 类页面各有区域表 | — |
| DSX-12 | 03 新增「交互规范」节：承载形式、返回、键盘、吸顶、手势、防连点、加载防闪、触感 | 设计 | P1 | DSX-10 | 03 有「交互规范」节，①–⑧ 各有条文 | — |
| DSX-13 | 03 新增「动效规范」节：转场目录、自绘组件出入场、减弱动态、轮播与公告节奏 | 设计 | P1 | DSX-03、COMP-SPEC-2、DSX-26 | 03 有「动效规范」节，轮播与公告只引用 03 §6.3、不复述数值 | — |
| DSX-14 | 10 视觉验收用例：品牌一致、关键页与定稿一致、通用状态、二级页顶栏、动效，05 QA-11 / QA-12 补验收列 | 设计（协同 质量） | P1 | DSX-06、DSX-09、DSX-13、UI-STATES | 10 有品牌一致、关键页、通用状态、二级页顶栏、动效等视觉验收用例，05 QA-11 / QA-12 验收列补齐 | QA-11、QA-12（原行加指针，不另建行） |
| DSX-15 | 7 个关键页规格补信息层级，重出大字号适配证据稿，钱包规格对齐画板 | 设计 | P1 | DSX-11、DSX-10 | 7 个关键页规格都有「0. 信息层级」，大字号证据稿重出，钱包规格对齐画板 | — |
| W-33 | 已定稿画板按组件规范收口（改稿与普查表）：筛选胶囊、44001 弹窗主次、通用错误态、弹窗标题对齐、勾选框、二次验证格子 | 设计 | P1 | COMP-SPEC、COMP-SPEC-2、DSX-08、DSX-118 | 改过的定稿画板（含 Orders-v2 与三张空态稿）在 design/README 有新 sha256，并过 Codex 对抗审查 | — |
| DSX-125 | 画板组件级检查：标题对齐、勾选框形状、圆角与间距只许令牌或已登记例外（W-33 ⑤ 拆出） | 设计 | P1 | DSX-123、W-33 | verify-boards.py 对全部已定稿画板 0 违规，或只命中已登记的例外 | — |
| DSX-16 | 二级页不显示底栏的规则，补「搜索」Tab 底栏稿 | 设计 | P1 | — | 03 写明二级页不显示底栏，「搜索」Tab 底栏稿已补 | — |
| DSX-17 | 以 routes.json 为主键建页面导航总表，加规格路由行检查，改正 flow-map | 设计 | P1 | — | 以 routes.json 为主键的页面导航总表检查脚本退出码 0，flow-map 改正 | — |
| DSX-18 | 登录 v2 定稿登记与 app-login 规格 | 设计 | P1 | — | design/README 有登录批次的 sha256 表 | — |
| DSX-19 | 补 DataCopy 页画板与规格 | 设计 | P1 | DSX-11 | DataCopy 新稿在 design/README 有 sha256 | — |
| DSX-20 | 08 BR-TEXT-14 表 A 加「呈现」列 | 设计 | P1 | UI-STATES | BR-TEXT-14 表 A 每行都有「呈现」值，脚本检查无空格、无表外取值 | — |
| DSX-21 | 规格补加载 / 加载失败 / 断网三行，加规格检查脚本，设计自检查状态覆盖 | 设计 | P1 | UI-STATES | 规格检查脚本对全部 App 规格退出码 0 | — |
| DSX-22 | 商品卡变体唯一名单（进组件规范）、AI 商品卡布局口径 | 设计（协同 iOS、安卓、鸿蒙） | P1 | COMP-SPEC、DSX-119、DSX-08 | design/components 规范和 component-spec.json 有变体名单，03 §10.2 只有指针 | — |
| DSX-23 | 三端页面私有件收编表 | 设计（协同 iOS、安卓、鸿蒙） | P1 | COMP-SPEC | 表的行数与附带命令在三端当时主干上的命中数一致 | — |
| DSX-24 | 看板加「组件库差异」上限告警，以及同一画板的三端落地状态 | 设计 | P1 | DS-03 | 看板显示组件库差异上限告警与同一画板的三端落地状态 | — |
| DSX-25 | App 内 Web 容器规范：主题和字号传递、标题来源、反色标题栏、setNavBar 色值 | 设计（协同 后端、iOS、安卓、鸿蒙、前端） | P1 | DSX-03 | 03 §8.1 与 brand-integration.md 的主题机制是同一种说法 | — |
| DSX-26 | 首页 SDUI 规则补齐：开放 props 键名、卡片版本规则、视觉参数白名单 | 设计（协同 后端、iOS、安卓、鸿蒙、前端） | P1 | — | 03 §6.3 每个 type 的 props 都是确定键名并标了必填 | — |
| DSX-27 | 首页 SDUI 规格与验收补齐：首页规格同步、后台首页配置规格、AC-HOME、流程图 | 设计（协同 前端、质量） | P1 | DSX-26 | app-home.md 里「section_popup 还没有」「暂无替代文字字段」为 0 | — |
| DSX-28 | 后台内容 CMS 与商品池页面规格 | 设计（协同 前端） | P1 | — | 后台内容 CMS 与商品池两份页面规格已有并登记 sha256 | — |
| DSX-29 | M-内测页面规格补「无障碍」小节 | 设计（协同 质量） | P1 | DSX-09 | M-内测各页面规格都有实质内容的「无障碍」小节 | — |
| DSX-30 | 08 BR-TEXT-14 增「读屏与播报」一节 | 设计（协同 后端） | P1 | — | 08 BR-TEXT-14 有「读屏与播报」一节，键名清单完整 | — |
| DSX-31 | 图片管线定案写进 03：选型、缓存与解码上限、请求策略、首屏预取、清除缓存口径 | 设计 | P1 | — | 一个 PR 改完 03 §3.3、§4.2、§6.2、§12 和 app-settings.md | — |
| DSX-32 | 用 staging 真实主图复核 ImageStress，定长图、低清、白底三条规则的去留 | 设计 | P1 | — | couli-runs 里有复核页和 1 倍 PNG，注明图源和原图尺寸 | — |
| DSX-33 | 运营上传图规格：banner、活动卡、静态弹窗图的尺寸、比例、体积、格式和 https | 设计 | P1 | — | 08 有这条细则，并被 F-ADM-09 引用 | — |
| DSX-34 | 邀请落地页 v2 定稿与规格，定站外品牌头，补邀请页「海报暂不可用」态 | 设计（协同 前端） | P1 | — | 邀请落地页 v2 定稿与规格 h5-invite-landing.md 已有，含「海报暂不可用」态 | — |
| DSX-35 | 商店截图模板与上架素材视觉标准（W7 提审用） | 设计 | P1 | — | 三个商店目录都有截图模板和 description.md，禁用词扫描 0 命中；平台标识口径等负责人 | — |
| DSX-36 | 安卓通知小图标素材（单色剪影），各推送通道图标要求登记待核 | 设计 | P1 | — | notification/ 下有单色剪影图标的 SVG、PNG 和 README | — |
| DSX-37 | 价格走势图形与文案规则：日期横轴、阶梯线、缺失日断开、刻度、跨年、末点标注、失败态、文本键 | 设计 | P1 | DSX-04、UI-STATES、DSX-08 | 规则条目里有几何参数表和 6 组示例（单点、缺失日、跨年、几毛钱的波动、四位数价格、报价与末点不一致） | — |
| DSX-38 | 价格走势补稿：请求失败、加载中、展开深色、200% 字号，与 v3 骨架一致的暂无记录稿 | 设计 | P1 | DSX-37 | 5 张新画板和对应的 1 倍 PNG 已有 | — |
| DSX-39 | 资金看板口径与图表规则：指标定义、金额写法二选一、事件标注与区间上限，锁 G2 版本 | 设计 | P1 | DSX-04 | 08 有指标口径条目，06 有财务确认项 | — |
| DSX-130 | 09 CAP-JD-02 回写京东主图实测（外部阻塞：京东 goods.query 权限） | 设计（协同 运维） | P1 | DSX-44 | 09 CAP-JD-02 有实测日期、样本数和字段结论，引用 evidence 路径 | — |
| DSX-133 | 鸿蒙关怀模式字号封顶：取得负责人决定并回写 03 §10.4、09 CAP-X-18 | 设计（协同 鸿蒙） | P1 | DSX-10 | 03 §10.4 鸿蒙行和 09 CAP-X-18 写明封顶口径和负责人决定日期 | — |
| DSX-132 | 鸿蒙实测结果回写 09：ArkWeb 是否跟随系统字号、减弱动态读取接口 | 设计（协同 鸿蒙） | P1 | HM-03-web、DSX-83 | 09 两处 CAP 有实测日期、设备与结论，引用 PR 里的测试记录 | — |
| DSX-92 | 建视觉参考板，公开参考说明补「外观风格」一节 | 设计 | P2 | DSX-05 | 参考板 README 和截图已有，每个参考都有「学什么 / 不学什么」 | — |
| DSX-93 | 准备 Slogan 候选交负责人选定，并回写品牌配置 | 设计 | P2 | DSX-05 | Slogan 由负责人选定后回写 name.md 与 tagline，sync-brand --check 通过 | — |
| DSX-94 | 后台设计规范与版式令牌：字阶、间距、页面模板、表格密度，admin.* 进唯一源 | 设计（协同 前端） | P2 | — | admin-guidelines.md 已有，并被 03 §9 引用 | — |
| DSX-95 | 「请升级 App」提示页补稿与规格 | 设计 | P2 | DSX-11 | 提示页已登记 sha256，规格已有 | — |
| DSX-96 | 分享中间页与下载引导页 v2 定稿和规格：去旧口径句、补京东拼多多购买按钮、换正式品牌头 | 设计（协同 前端） | P2 | DSX-34 | 分享中间页与下载引导页 v2 定稿登记 sha256，两份规格已有 | — |
| DSX-97 | 03 §4.2「断网显示缓存」按向量口径回写，§9.2 补后台等待上限 | 设计 | P2 | — | 03 §4.2 不再写「请求失败时显示上次成功的数据并标注更新于」 | — |
| DSX-98 | 首页弹窗 Lottie：素材闪烁安全要求，三端播放器与后台上传入口同排 | 设计 | P2 | — | BR-TEXT-26 有闪烁条文 | — |
| DSX-99 | 状态色色觉辨识核对，关闭品牌评审遗留 | 设计（协同 质量） | P2 | — | colors.md 有状态色色觉模拟表 | — |
| DSX-100 | 海报与分享素材规格：二维码、背景图、深色、格式与体积、截断与文案键、微信卡片、出图字体 | 设计 | P2 | — | posters/README 有二维码、背景图、深色、格式与体积、字体五节 | — |
| DSX-101 | 海报出图架构与验收：两层缓存、域名被拦截时的海报兜底、海报验收用例 | 设计 | P2 | — | 02 §11、01 F-SHARE-04、08 11_INV 三处一致 | — |
| DSX-102 | 海报补稿：两张定稿换正式品牌头，补无券、拼多多、缺主图、长昵称变体和生成中、失败态 | 设计 | P2 | DSX-100、DSX-34 | design/README 有更新后的 sha256 | — |
| DSX-131 | 商品图小图取法：CDN 尺寸参数实测登记 09，03 写拼参数规则或 04 登记缩略图字段 | 设计（协同 运维） | P2 | DSX-104 | 09 有 CDN 尺寸参数实测记录，03 或 04 写明小图取法 | — |

### 5.2 后端（23 项：P0 2、P1 14、P2 7）

| 编号 | 标题 | 负责线（协同） | 分期 | 依赖 | 验收要点 | 对应 05 原任务 |
| --- | --- | --- | --- | --- | --- | --- |
| UI-STATES | UI-STATES：状态目录覆盖首次加载、断网缓存、结果未知、字段缺失和加载超时 | 后端 | P0 | DSX-01 | ui-states.yaml 每行都有编号、触发条件、组件 kind、文案键、按钮主次、播报与重试 | — |
| TOKENS-LAG | 令牌锁与契约锁落后告警（三端 + H5） | 后端（协同 前端） | P0 | — | 三端与 H5 的令牌锁或契约锁落后一个版本或 7 天、三端契约锁不一致时 CI 报警（夹具覆盖） | — |
| CT-07e | CT-07e：home-schema 收口——开放 props 定稿、视觉参数与图片约束、版本登记、golden、渲染事件 | 后端（协同 前端） | P1 | DSX-26、DSX-33 | home-schema 开放 props 定稿、视觉参数与图片约束入契约，golden 齐全 | CT-07 |
| F1-09c-check | 首页配置保存校验补齐：禁用词、信息流个数与位置、custom 页 | 后端（协同 前端） | P1 | — | 首页配置保存校验覆盖禁用词、信息流个数与位置和 custom 页，违规时 fields 指向点路径 | F1-09 |
| DSX-40 | 首页渲染健康：计数写库、错误率告警和自动回滚（TECH-29） | 后端（协同 前端、iOS、安卓、鸿蒙） | P1 | CT-07e | 首页渲染与错误计数写库正确，错误率超阈值时告警并自动回滚（集成测试覆盖） | — |
| CT-03-env | 桥契约：app.getEnv 增加主题与字号，新增变化事件 | 后端（协同 前端） | P1 | DSX-25 | schema 有新字段和事件，CT-06 门禁通过 | CT-03 |
| DSX-41 | 契约字典补读屏键：通用 a11y.* 键和商品图读屏名 | 后端（协同 iOS、安卓、鸿蒙） | P1 | DSX-30、DSX-118 | 新键都在 texts.default.json 里，取值与 08 一致 | — |
| CT-09b | error-codes.yaml 和 network-vectors 加 presentation 字段 | 后端 | P1 | DSX-20、UI-STATES | error-codes.yaml 的 108 个码都有 presentation 字段，network-vectors 同步 | CT-09 |
| DSX-42 | 三端共享客户端向量收归唯一源，加跨端 hash 比对 | 后端 | P1 | TOKENS-LAG | 三端共享客户端向量只在 specs/client/ 一处，login、order、clipboard 分叉合并为一版 | — |
| DSX-43 | 契约补文案键：邀请落地页、邀请页海报暂不可用 | 后端 | P1 | DSX-34 | texts.default.json 有这些键，取值与 08 一致 | — |
| DSX-44 | 京东商品图接上：CAP-JD-02 实测 imageInfo 后映射主图和多图（外部阻塞：京东 goods.query 权限） | 后端（协同 运维） | P1 | — | 京东有 imageInfo 时搜索卡出 https 主图与多图，没有时为 null，staging 实测进 evidence | — |
| CT-22-trend | 价格走势契约补齐：文本键、几何测试向量、拼多多来源键（最常见价字段已拆到 CT-22-mode） | 后端 | P1 | DSX-37 | 价格走势文本键、拼多多来源键与几何测试向量入契约，oasdiff 只有新增 | CT-22 |
| CT-22-mode | 最常见价字段契约：ProductPriceTrend 加 mode_price_fen（D10-664 ③ 从 CT-22-trend 拆出） | 后端 | P1 | — | 契约加可为空的 mode_price_fen、形状与 04 §6.3 一致，oasdiff 只有新增 | CT-22 |
| CT-24-funds | CT-24：adminGetFundsReport 契约与 specs/reports/funds.yaml | 后端 | P1 | DSX-39 | adminGetFundsReport 契约与 specs/reports/funds.yaml 合入，oasdiff 只有新增 | CT-24 |
| DSX-45 | packages/money 补坐标轴刻度和读屏金额格式化函数，配测试向量 | 后端（协同 前端） | P1 | DSX-39 | 单测覆盖 0、负数、四位以上金额、分到元的换算 | — |
| B1-29-trend | 价格走势计算：按平台选来源键，服务端算最常见价和显示门槛 | 后端 | P1 | CT-22-trend、CT-22-mode | 按平台选来源键（拼多多用 .pdd 变体），最常见价按 01 F-PROD-14 ⑧ 计算，属性测试与 verify 通过 | B1-29 |
| DSX-103 | 文案检查加品牌语气条目 | 后端 | P2 | DSX-05 | 文案检查加品牌语气条目，违反语气条目的样例让 CI 失败 | — |
| CT-03-upgrade | routes.json 登记「请升级 App」提示页的路由名和文案键 | 后端（协同 iOS、安卓、鸿蒙） | P2 | DSX-95 | routes.json 有该路由，并通过路由一致性检查 | CT-03 |
| CT-03-navbar | 桥契约：ui.setNavBar 的色值参数收口为令牌名 | 后端（协同 iOS、安卓、鸿蒙、前端） | P2 | DSX-25 | ui.setNavBar 的色值参数改为令牌名，CT-06 门禁通过 | CT-03 |
| CT-03-share | 分享与海报契约补齐：poster_status、二维码落地路径、share.open 缩略图约束 | 后端 | P2 | DSX-100 | poster_status、二维码落地路径与缩略图约束入契约，oasdiff 只有新增 | CT-03、CT-22 |
| B1-15-input | 出图输入通道：服务端取同一套令牌、正式 Logo 和随包中文字体，先出样张 | 后端 | P2 | DSX-100 | apps/api 只有一处令牌来源，dependency-cruiser 通过 | B1-15 |
| B1-15-worker | 海报出图 worker：两种模板、两层缓存、写 OSS、回填 poster_url 和状态、限流告警 | 后端（协同 运维） | P2 | B1-15-input、CT-03-share、DSX-102、DSX-101 | 海报出图走两层缓存写 OSS，同一商品第二次进页只合成二维码 | B1-15 |
| DSX-104 | 契约写清商品图字段，评估宽高和小图（缩略图或 CDN 尺寸参数） | 后端（协同 运维） | P2 | DSX-32 | oasdiff 只有新增的可选字段和说明 | — |

### 5.3 前端（H5 与管理后台）（25 项：P0 2、P1 18、P2 5）

| 编号 | 标题 | 负责线（协同） | 分期 | 依赖 | 验收要点 | 对应 05 原任务 |
| --- | --- | --- | --- | --- | --- | --- |
| LINT-STYLE-web | Web LINT-STYLE：H5 与后台禁写死样式，后台主题改读令牌，修正 H5 选中态对比度 | 前端 | P0 | — | pnpm lint 对写死字号、色值与错用品牌色的反例报错，基线入库，后台主题读令牌 | — |
| H5-DARK | H5 遮罩改用 overlay.scrim，轻提示换对角色令牌，加浅深对比度测试 | 前端 | P0 | — | H5 遮罩改用 overlay.scrim，轻提示用角色令牌，浅深对比度测试通过 | — |
| CT-11c | CT-11c：契约令牌快照升到 v0.6.0，H5 接入新令牌类别 | 前端（协同 后端） | P1 | DETAIL-V3-WB、DSX-02、DSX-03、DSX-04 | 契约 design-tokens.json 快照等于 couli 最新版本，H5 接入新令牌类别 | CT-11 |
| DSX-46 | H5 基础件补齐：Button、Chip / Segmented、NoticeBar、Field、Card | 前端（协同 后端） | P1 | COMP-SPEC、COMP-SPEC-2、DSX-02、CT-11c、DSX-119 | H5 base 导出 Button、Chip / Segmented、NoticeBar、Field、Card | — |
| DSX-47 | H5 页面私有的按钮、胶囊、卡片类名迁移到基础件 | 前端 | P1 | DSX-46 | H5 页面私有的按钮、胶囊、卡片常量与原生 button 清零，全部改用 base 组件 | — |
| DSX-48 | H5 状态与反馈组件对齐状态目录：轻提示位置、骨架屏、状态键 | 前端 | P1 | UI-STATES、COMP-SPEC-2、DSX-01、H5-DARK、CT-11c | Toast.tsx 只在站外分支保留底部定位 | — |
| DSX-49 | H5 App 内页面的版心与页面骨架 | 前端 | P1 | CT-11c、DSX-11、LINT-STYLE-web | ≥600 宽视口下，截图内容居中且宽度等于令牌值 | — |
| DSX-50 | H5 与后台截图基准比对（浅 / 深，先只报告） | 前端（协同 设计） | P1 | — | test/spec/frontend 里有截图比对断言，基准图已入库 | — |
| QA-12-web | H5 与后台接入 axe 自动检测和 200% 缩放冒烟 | 前端（协同 质量） | P1 | — | package.json 有 axe 依赖，CI 产物含各页 axe 报告和基线 | QA-11、QA-12（原行加指针，不另建行） |
| DSX-51 | 后台 200% 与窄视口重排（视口分档落地） | 前端（协同 设计） | P1 | — | 浏览器测试在 1280、960、800 宽和 200% 缩放下，除数据表格外没有页面级横向滚动，侧栏可以收起 | — |
| DSX-52 | App 内 H5 跟随宿主主题与字号 | 前端（协同 iOS、安卓、鸿蒙） | P1 | CT-03-env | 浏览器测试：color_scheme=dark 时 html 的 data-theme 为 dark，令牌变量取深色值 | — |
| F1-01-nav | H5 外壳按路由设置原生标题，去掉页面自绘标题 | 前端（协同 iOS、安卓、鸿蒙） | P1 | — | 浏览器测试：每个 app 路由进入后都调用了 ui.setNavBar，且 title 非空 | F1-01 |
| F1-09-qr | 后台首页配置：草稿二维码、弹窗素材上传位、版本错误率列 | 前端（协同 后端） | P1 | — | 浏览器测试：保存草稿后出现二维码，解码以 couli://r/HomePreview?page_key= 开头且带 token | F1-09 |
| F1-09-form | 后台首页配置：由 home-schema 生成属性表单，区块拖拽排序 | 前端（协同 设计、后端） | P1 | CT-07e、DSX-27 | 只用表单新增一个 icon_grid 区块就能保存，生成的 JSON 通过服务端 Ajv | F1-09 |
| F1-09-preview | 后台首页配置：近似预览（可复用的 H5 卡片渲染包）和图片就地校验 | 前端（协同 设计） | P1 | CT-07e、DSX-27、DSX-33 | 编辑后 1 秒内近似预览更新，图片就地校验 | F1-09 |
| DSX-135 | 后台内容 CMS 页面（帮助 / 规则 / 公告 / 协议） | 前端（协同 后端） | P1 | DSX-28 | content 菜单不再渲染 PagePending | F1-10（原行加指针，不另建行） |
| F1-09-pools | 后台商品池管理页 | 前端（协同 后端） | P1 | DSX-28 | pools 菜单不再渲染 PagePending | F1-09 |
| F1-05-landing | 邀请落地页按 v2 定稿实现，替换占位页并补页面标题 | 前端 | P1 | DSX-34、DSX-43 | Playwright 截图：有效码、无效码、已注册，各有浅深两态 | F1-05 |
| F1-05-poster | H5 邀请页海报不可用时显示说明态 | 前端 | P1 | DSX-34、DSX-43 | poster_url 为 null 时显示说明文案，按钮是 aria-disabled，读屏能读到原因 | F1-05 |
| DSX-137 | 资金看板页的图表部分：antd + G2、令牌主题、图表同源、W 过期断线、越线标记、键盘读值 | 前端 | P1 | CT-24-funds、DSX-45、DSX-04、DSX-39、CT-11c | Vitest 断言图、表格、aria-label 数值同源 | F1-08（原行加指针，不另建行） |
| DSX-105 | 后台主题改读生成的 admin 令牌，焦点框统一用 focus.ring | 前端 | P2 | DSX-94、CT-11c | theme.ts 里没有字面 fontSize / controlHeight / borderRadius 数字 | — |
| DSX-106 | 管理后台共享筛选栏，收敛内联数值 | 前端 | P2 | — | pages 里 const FILTER_THEME 为 0 | — |
| DSX-107 | 管理后台统一页面状态组件、弹层动效和「结果未确认」等待上限 | 前端 | P2 | DSX-97 | 逐页设置空 transitionName 的写法为 0 | — |
| DSX-108 | H5 基础控件强制配色回退与减弱动态 | 前端（协同 设计） | P2 | — | apps/h5 和 ui-tokens 里有 forced-colors 规则 | — |
| DSX-138 | 分享中间页与下载引导页按 v2 定稿改版 | 前端 | P2 | DSX-96 | Playwright 截图：浏览器、微信、未拉起 App 三种情况，各有浅深两态 | F1-11（原行加指针，不另建行） |

### 5.4 iOS（36 项：P0 8、P1 23、P2 5）

| 编号 | 标题 | 负责线（协同） | 分期 | 依赖 | 验收要点 | 对应 05 原任务 |
| --- | --- | --- | --- | --- | --- | --- |
| APP-17-ios-apple | iOS「通过 Apple 登录」改用系统官方按钮（解除浅色锁前必须合并） | iOS | P0 | — | Apple 登录改用系统官方按钮，自绘标识与写死字号为 0，浅深快照通过，早于 DSX-127 合并 | APP-17 |
| FU-X-HOME-PAGE-API-ios | iOS 首页 Staging / Release 接真实页面接口，契约锁与安卓、鸿蒙对齐，刷新失败改用 couliToast | iOS（协同 后端） | P0 | — | Release 首页走页面接口，三端 contract.lock 的 rebate_platform 提交一致，刷新失败改用 couliToast | — |
| DS-02-iOS-1 | DS-02-iOS（一）：升令牌锁、生成深色与组件令牌、删手抄表（去浅色锁拆到 DSX-127） | iOS（协同 设计） | P0 | — | 令牌锁直接升到 v0.5.1，深色与组件令牌读生成物，CouliDarkTokens 等手抄表 grep 为 0，Info.plist 浅色锁暂留 | DS-02 |
| DSX-127 | iOS 解除整 App 浅色锁：全部页面深色扫描通过后去锁（DS-02-iOS ④ 拆出） | iOS（协同 设计） | P0 | DS-02-iOS-1、APP-17-ios-apple、LINT-STYLE-ios | 全部页面深色快照入库、对比度扫描 0 失败后去掉整 App 浅色锁 | DS-02 |
| DS-02-iOS-2 | DS-02-iOS（二）：补基础交互组件和目录页（FilterChip、输入框、勾选、开关等） | iOS | P0 | DS-02-iOS-1 | DesignSystem 公开 FilterChip、输入框、勾选、开关等基础交互组件，目录页有浅 / 深 / 200% | DS-02 |
| DS-02-iOS-3 | DS-02-iOS（三）：导航栏和半屏、弹窗改用系统容器，补登录、分享和业务组件 | iOS | P0 | DS-02-iOS-2、COMP-SPEC-2 | 隐藏系统导航栏只剩白名单，半屏与弹窗用系统容器，登录、分享与业务组件补齐 | DS-02 |
| LINT-STYLE-ios | LINT-STYLE（iOS）：SwiftLint 禁写死样式与系统控件直用，改正 4 处用透明度代替状态色 | iOS | P0 | DS-02-iOS-1 | CI 带基线跑 swiftlint --strict，写死样式与系统控件直用的反例失败，4 处透明度代替状态色改正 | — |
| FU-DS-ios | FU-DS（iOS 组件库）：ErrorState、EmptyState、NoticeBar、Toast、Skeleton 按状态目录统一 | iOS | P0 | UI-STATES、COMP-SPEC-2、DSX-01、DS-02-iOS-3 | iOS 组件库公开 ErrorState(kind:) 与 NoticeBar(tone:)，旧的 RetryBanner / NoticeBox 不再公开 | — |
| DSX-120 | iOS 令牌锁升 v0.6.0、锁定组件规范、生成器输出新类别 | iOS（协同 设计） | P1 | DS-02-iOS-1、DSX-02、DSX-03、DSX-04、COMP-SPEC | contract.lock 的 design_tokens 指向 v0.6.0 发布提交并锁定组件规范版本，生成物含新类别、逐值比对通过 | — |
| DSX-140 | iOS CI 接入令牌与契约落后检查，改锁共享客户端向量 | iOS | P1 | TOKENS-LAG、DSX-42、DS-02-iOS-1 | iOS CI 跑 TOKENS-LAG 检查，共享客户端向量的锁与分发清单 sha256 一致 | — |
| DSX-53 | BRAND-02-iOS：品牌图标改用唯一 SVG 源，补启动页图形和品牌页快照 | iOS | P1 | DSX-06、DS-02-iOS-1 | 脚本列出全部 Image(systemName:)，都在「系统控件自带」清单内 | — |
| FU-DS-LINE-HEIGHT-ios | iOS 组件库按规范与新令牌对齐：按钮、字重与行距、半屏标题、搜索胶囊、返利标签、提示条、动效与阴影 | iOS | P1 | DS-02-iOS-1、LINT-STYLE-ios、DSX-120、COMP-SPEC、COMP-SPEC-2、DSX-119 | iOS 组件库按规范与 v0.6.0 令牌对齐，旧尺寸常量 grep 为 0 | — |
| DSX-54 | iOS 组件库 PageScaffold 与 layout 令牌，删模块级限宽常量 | iOS | P1 | DSX-11、DS-02-iOS-3、DSX-120 | iOS 模块级限宽常量 grep 为 0，PageScaffold 读 layout 令牌 | — |
| DSX-55 | iOS 登录页迁移到组件库（含启动页、强更页的品牌位） | iOS | P1 | DS-02-iOS-3 | iOS 登录相关私有件与写死字号为 0，LINT 基线 Login 条目清零，浅深快照重录 | — |
| DSX-56 | iOS 钱包页（钱包 / 提现 / 收款账号 / 记录 / 二次验证）迁移到组件库 | iOS | P1 | DS-02-iOS-3、FU-DS-LINE-HEIGHT-ios | 钱包类页面私有件换成组件库组件，grep 为 0，LINT 基线 Wallet 条目清零 | — |
| DSX-57 | iOS 我的 / 设置页迁移到组件库 | iOS | P1 | DS-02-iOS-3、FU-DS-LINE-HEIGHT-ios | 我的 / 设置页私有件（MeHeroCard 等）grep 为 0，改用组件库 | — |
| DSX-58 | iOS 搜索 / 订单页控件迁移（筛选胶囊、状态胶囊、金额格、订单卡） | iOS | P1 | DS-02-iOS-3、FU-DS-LINE-HEIGHT-ios、W-33、DSX-119 | 搜索 / 订单页私有胶囊与订单卡件 grep 为 0，改用组件库 FilterChip 等 | — |
| DSX-59 | iOS 首页 / 剪贴板控件迁移（浅底按钮、弹层宽、禁用态） | iOS | P1 | DS-02-iOS-3、FU-DS-LINE-HEIGHT-ios、DSX-119 | 首页 / 剪贴板私有浅底按钮与 plain 按钮样式 grep 为 0 | — |
| DSX-60 | iOS 守卫：G1 转为失败，新增 G2 启发式规则 | iOS | P1 | DS-02-iOS-3、LINT-STYLE-ios | G1 为 error 级，反例让 CI 失败 | — |
| FU-DS-ios-pages | FU-DS（iOS 非资金页）：通用状态键、私有提示条、断网态、补缺失的状态行 | iOS | P1 | FU-DS-ios、DSX-21 | iOS 非资金页草稿状态键 grep 为 0，私有提示条换成组件库 | — |
| FU-DS-ios-fund | FU-DS（iOS 资金与金额页）：钱包、提现类状态键，「我的」金额缺失不补 0 | iOS | P1 | FU-DS-ios、DSX-01、DSX-21 | iOS 资金页草稿状态键为 0，「我的」金额缺失按 BR-TEXT-10 展示 | — |
| FU-X-DLG-ios | FU-X-DLG（iOS）：44001 拦截弹窗主次按定稿统一 | iOS | P1 | W-33 | 44001 拦截弹窗四处主次按定稿统一，快照与新画板一致 | — |
| DSX-61 | iOS 动效落地：motion 令牌、减弱动态入口、轮播与公告节奏、首页弹窗转场 | iOS | P1 | DSX-13、DSX-26、DS-02-iOS-3、DSX-120 | DS 有统一入口，轮播和公告都引用它 | — |
| APP-10-ios | APP-10（iOS）：AI 入口开关与「搜索」Tab、AI 卡布局、长按举报可见入口 | iOS | P1 | DSX-16、DSX-22、DSX-12 | AI 入口开关两种取值的底栏快照与稿一致，长按举报有可见入口 | APP-10 |
| DSX-62 | iOS 无障碍守卫与自动审计（含 Web 返回键读屏名） | iOS（协同 质量） | P1 | DS-02-iOS-1 | Web 目录里英文 Back 为 0，单测断言两个容器的返回按钮 label 等于字典值 | — |
| DSX-63 | iOS 大字号快照覆盖与封顶档位统一 | iOS（协同 设计） | P1 | DS-02-iOS-1、DSX-54 | __Snapshots__ 有 Login / Search / Agent 的 font200 基准 | — |
| APP-11-ios-sdui | iOS 首页 SDUI 按契约解码（含渲染上报和弹窗读屏名） | iOS（协同 后端） | P1 | FU-X-HOME-PAGE-API-ios、CT-07e | 单测遍历全部 golden，每份的保留 / 丢弃结果都与期望一致（含反例） | APP-11 |
| APP-04-ios | iOS Web 容器：跟随主题与字号、标题回退、反色标题栏 | iOS（协同 后端、前端） | P1 | DS-02-iOS-1、DSX-25、CT-03-env、DSX-120 | 生成的桥类型含 color_scheme、font_scale | APP-04 |
| DSX-64 | iOS 远程图片收敛为一个加载器：缓存上限、按尺寸解码、统一请求策略、预取 | iOS | P1 | DSX-31、DS-02-iOS-1、FU-X-HOME-PAGE-API-ios | 执行 rg 'AsyncImage\|URLSession.shared.data'（排除测试和 Debug）只命中加载器内部 | — |
| DS-02-ios-image | iOS 商品图收敛为 ProductImage：四态、令牌图框、渐显、缓存命中不闪 | iOS | P1 | DSX-118、DSX-41、DSX-64、DS-02-iOS-3、DSX-120 | 执行 rg 'ProductRemoteImage\|ProductHeroImage' 为 0 | DS-02 |
| DSX-134 | iOS PriceTrendPanel 按共用几何向量和规则实现（与 iOS 详情 v3 同批） | iOS | P1 | DSX-37、DSX-38、CT-22-trend、DS-02-iOS-3、DSX-120、UI-STATES | iOS 走势读共用几何向量全过，mode 为 null 时不显示最常见价，五态 × 浅深 × 200% 快照 | APP-16（原行加指针，不另建行） |
| DSX-109 | iOS 防连点与加载防闪 | iOS | P2 | DSX-12 | iOS 防连点单测（连点两次只推入一次）与加载防闪通过 | — |
| QA-08-ios16 | iOS 16 快照基准与统一快照容差常量 | iOS（协同 质量） | P2 | DSX-09 | __Snapshots__ 有 iOS 16 基准目录 | QA-08（原行加指针，不另建行） |
| APP-11-ios-lottie | iOS 首页弹窗 Lottie 动效 | iOS | P2 | APP-11-ios-sdui、DSX-98 | iOS 首页弹窗 Lottie 的兜底图与动画首帧各有 golden 截图 | APP-11 |
| DSX-110 | iOS 读屏用词改取契约字典 | iOS | P2 | DSX-41 | iOS 草稿读屏键为 0，读屏用词取契约字典 | — |
| APP-13-share-thumb | share.open 微信卡片缩略图压到 ≤32KB（iOS） | iOS | P2 | CT-03-share | 单测：同一组向量图压缩后 ≤32768 字节且是方形 | APP-13（原行加指针，不另建行） |

### 5.5 安卓（29 项：P0 3、P1 22、P2 4）

| 编号 | 标题 | 负责线（协同） | 分期 | 依赖 | 验收要点 | 对应 05 原任务 |
| --- | --- | --- | --- | --- | --- | --- |
| TOKENS-PIPE-android | TOKENS-PIPE（安卓）：升令牌锁，生成深色、组件、阴影，删手抄表和重名常量 | 安卓（协同 设计） | P0 | — | 令牌锁直接升到 v0.5.1，生成器出 dark / component / shadow，手抄深色表与同名不同值常量清除 | — |
| LINT-STYLE-android | LINT-STYLE（安卓）：页面层禁写死样式，系统控件守卫按基线失败 | 安卓 | P0 | — | 页面层写死颜色、尺寸、圆角与系统控件直用的反例都让检查失败，基线只减不增，lint / detekt / test 通过 | — |
| FU-DS-android | FU-DS（安卓组件库）：状态组件统一，Toast 和状态标签按语义绑定图标与颜色 | 安卓（协同 设计） | P0 | UI-STATES、COMP-SPEC-2、DSX-01、TOKENS-PIPE-android | 安卓 ErrorState 带 kind 参数、默认主按钮，Toast 与状态标签按语义绑定图标和颜色 | — |
| DSX-121 | 安卓令牌锁升 v0.6.0、锁定组件规范、生成器输出新类别 | 安卓（协同 设计） | P1 | TOKENS-PIPE-android、DSX-02、DSX-03、DSX-04、COMP-SPEC | contract.lock 的 design_tokens 指向 v0.6.0 发布提交并锁定组件规范版本，生成物含新类别、逐值比对通过 | — |
| DSX-141 | 安卓 CI 接入令牌与契约落后检查，改锁共享客户端向量 | 安卓 | P1 | TOKENS-LAG、DSX-42、TOKENS-PIPE-android | 安卓 CI 跑 TOKENS-LAG 检查，共享客户端向量的锁与分发清单 sha256 一致 | — |
| FU-DS-ANDROID-SYMBOLS | BRAND-02-安卓：CouliIcons 改由唯一 SVG 源生成，接 SplashScreen，加品牌页快照 | 安卓 | P1 | DSX-06、TOKENS-PIPE-android | 清单内的图标全部来自生成文件，手写 path 为 0 | — |
| DSX-65 | 安卓组件库按规范与新令牌对齐：按钮、输入、胶囊、半屏标题、返利标签、Dialog、阴影与字距 | 安卓 | P1 | TOKENS-PIPE-android、LINT-STYLE-android、DSX-121、COMP-SPEC、COMP-SPEC-2、DSX-119 | 参数化测试覆盖按钮、输入、胶囊、Dialog、文字档各行 | — |
| DSX-66 | 安卓组件库 PageScaffold 与 layout 令牌，删模块级限宽和弹层宽常量 | 安卓 | P1 | DSX-11、DSX-121 | 执行 `git grep -n -E 'MAX_WIDTH = [0-9]' -- feature app` 为 0 | — |
| APP-17-android | APP-17（安卓）：登录与绑手机页迁移到组件库，恢复按压反馈（含隐私弹窗、强更页的品牌位） | 安卓 | P1 | DSX-65、LINT-STYLE-android | 登录与绑手机页同名私有件、去掉按压反馈的写法为 0，基线条目清零，浅深快照重录 | APP-17 |
| DSX-67 | 安卓搜索 / 订单页改用组件库：筛选胶囊、搜索框、下划线 | 安卓 | P1 | DSX-65、W-33 | 搜索 / 订单页自写胶囊与搜索框为 0，页面层引用 CouliFilterChip，截图与画板一致 | — |
| DSX-68 | 安卓我的 / 设置 / 换号 / 订单 / 申诉页控件迁移 | 安卓 | P1 | DSX-65、DSX-119 | 我的 / 设置 / 订单等页私有开关与状态胶囊为 0，OrderCard 只在组件库定义 | — |
| DSX-69 | 安卓守卫 G2：自绘开关、方块勾选框、去掉按压反馈 | 安卓 | P1 | LINT-STYLE-android | 三条守卫规则（自绘开关、方块勾选框、去掉按压反馈）各有正例和反例 | — |
| FU-DS-android-pages | FU-DS（安卓非资金页）：删页面轻提示时长常量、私有提示条和草稿状态键 | 安卓 | P1 | FU-DS-android、DSX-21 | 执行 grep 'const val TOAST_(MS\|MILLIS)'，在 feature 和 app/src/main 为 0 | — |
| FU-DS-android-fund | FU-DS（安卓资金与金额页）：钱包 ErrorBar 换组件库，提现类状态键统一，金额缺失不补 0 | 安卓 | P1 | FU-DS-android、DSX-01、DSX-21 | 安卓钱包 ErrorBar 换成组件库 NoticeBar，不再引用 InfoStrip，金额缺失按 BR-TEXT-10 展示 | — |
| FU-X-DLG-android | FU-X-DLG（安卓）：44001 拦截弹窗主次按定稿统一 | 安卓 | P1 | W-33 | 44001 拦截弹窗四处主次按定稿统一，截图与新画板一致 | — |
| DSX-70 | 安卓动效落地：NavHost 显式转场、减弱动态入口、轮播与公告节奏 | 安卓 | P1 | DSX-13、DSX-26、DSX-121 | AppNavHost 有显式转场参数 | — |
| APP-10v-android | APP-10v（安卓）：AI 商品卡 grid 按定稿口径，长按举报补可见入口 | 安卓 | P1 | DSX-22、DSX-12 | Agent 卡截图覆盖 list 和 grid，并与稿一致 | APP-10 |
| DSX-71 | 安卓无障碍守卫与自动检查（含 Web 返回键读屏名、快照显式容差） | 安卓（协同 质量） | P1 | — | 单测断言返回按钮 contentDescription 等于字典值 | — |
| APP-11-android-sdui | 安卓首页 SDUI 按契约解码（含渲染上报和弹窗读屏名） | 安卓（协同 后端） | P1 | CT-07e | 单测遍历全部 golden，结果与期望一致 | APP-11 |
| APP-04-android | 安卓 WebView：跟随主题与字号、标题回退、反色标题栏 | 安卓（协同 后端、前端） | P1 | DSX-25、CT-03-env、DSX-121 | 生成的桥类型含 color_scheme、font_scale | APP-04 |
| DSX-72 | 安卓配置变化不丢状态，补登录页大字号与宽屏快照 | 安卓（协同 设计） | P1 | TOKENS-PIPE-android、DSX-66 | 三个页面的 StateRestorationTester 用例通过 | — |
| DSX-73 | 安卓图片加载下沉到 core：磁盘缓存、按字节内存缓存、按显示尺寸解码，标题栏背景图可用 | 安卓 | P1 | DSX-31 | 执行 rg 'LruCache&lt;String, ImageBitmap>\|CACHE_ENTRIES' 为 0 | — |
| DS-02-android-image | 安卓商品图收敛为 ProductImage：去掉占位字、图框取令牌、渐显不闪，首页角标改正 | 安卓 | P1 | DSX-118、DSX-41、DSX-73、DSX-121 | 执行 rg 'GRID_IMAGE_RATIO\|HERO_RATIO\|image_placeholder'（排除测试）为 0 | DS-02 |
| APP-12-push | 安卓接 MobPush 时用专用通知小图标和品牌强调色 | 安卓 | P1 | DSX-36 | 合并后的清单里默认通知图标指向 ic_stat_couli | APP-12 |
| DS-02-android-trend | 安卓 PriceTrendPanel 改正：去掉「最低 / 最高」，按日期和刻度画阶梯线，补失败态和来源行 | 安卓 | P1 | DSX-37、DSX-38、CT-22-trend、UI-STATES、DSX-121 | 安卓走势去掉「最低 / 最高」，几何向量测试全过，快照含失败态 | DS-02 |
| DSX-128 | share.open 微信卡片缩略图压到 ≤32KB（安卓） | 安卓 | P2 | CT-03-share | 单测：同一组向量图压缩后 ≤32768 字节且是方形 | APP-13（原行加指针，不另建行） |
| DSX-111 | 安卓防连点与加载防闪 | 安卓 | P2 | DSX-12 | 安卓防连点单测（连点两次只导航一次）与加载防闪通过 | — |
| APP-11-android-lottie | 安卓首页弹窗 Lottie 动效 | 安卓 | P2 | APP-11-android-sdui、DSX-98 | 安卓首页弹窗 Lottie 的兜底图与动画首帧各有 golden 截图 | APP-11 |
| DSX-112 | 安卓读屏用词改取契约字典 | 安卓 | P2 | DSX-41 | 安卓草稿读屏键为 0，读屏用词取契约字典 | — |

### 5.6 鸿蒙（40 项：P0 3、P1 30、P2 7）

| 编号 | 标题 | 负责线（协同） | 分期 | 依赖 | 验收要点 | 对应 05 原任务 |
| --- | --- | --- | --- | --- | --- | --- |
| TOKENS-PIPE-harmony | TOKENS-PIPE（鸿蒙）：升令牌锁，一条链路出全部令牌，删旁路副本 | 鸿蒙（协同 设计） | P0 | — | 令牌锁直接升到 v0.5.1，全部令牌出自锁定快照一条链路，旁路副本 design-tokens.v*.json 删除 | — |
| LINT-STYLE-harmony | LINT-STYLE（鸿蒙）：页面层禁写死样式，G1 守卫从只警告改为按基线失败 | 鸿蒙 | P0 | — | lint.py 对写死色值、字号、圆角与系统控件直用的反例失败，基线入库只减不增，主干退出码 0 | — |
| FU-DS-harmony | FU-DS（鸿蒙组件库）：ErrorState、EmptyState、NoticeBar、Toast、Skeleton 按状态目录统一 | 鸿蒙 | P0 | UI-STATES、COMP-SPEC-2、DSX-01、TOKENS-PIPE-harmony | 鸿蒙状态组件按状态目录统一，States.ets 里写死的错误底色与 SECONDARY 清除 | — |
| DSX-122 | 鸿蒙令牌锁升 v0.6.0、锁定组件规范、生成器输出新类别 | 鸿蒙（协同 设计） | P1 | TOKENS-PIPE-harmony、DSX-02、DSX-03、DSX-04、COMP-SPEC | contract.lock 的 design_tokens 指向 v0.6.0 发布提交并锁定组件规范版本，生成物含新类别、逐值比对通过 | — |
| DSX-142 | 鸿蒙 CI 接入令牌与契约落后检查，改锁共享客户端向量 | 鸿蒙 | P1 | TOKENS-LAG、DSX-42、TOKENS-PIPE-harmony | 鸿蒙 CI 跑 TOKENS-LAG 检查，共享客户端向量的锁与分发清单 sha256 一致 | — |
| DSX-74 | BRAND-02-鸿蒙：CouliIcon 改由唯一 SVG 源生成，组件库图标两套归一，核对启动窗 | 鸿蒙 | P1 | DSX-06、TOKENS-PIPE-harmony | 清单内的图标全部来自生成，手写路径为 0 | — |
| DSX-75 | 鸿蒙组件与令牌对齐：提现金额字号、返利标签、阴影、Web 容器加载态、描边 | 鸿蒙 | P1 | LINT-STYLE-harmony、DSX-122 | 提现金额字号、阴影色等写死值 grep 为 0，组件与令牌对齐 | — |
| DSX-76 | 鸿蒙 PageScaffold 与 layout 令牌，合并两个内容限宽常量 | 鸿蒙 | P1 | DSX-11、DSX-122 | 内容最大宽只有一个来源，且来自令牌 | — |
| FU-DS-DIALOG-TITLE-ALIGN | 鸿蒙组件库弹层修正：CouliSheetPanel 撑满整屏，CouliDialog 对齐参数和间距 | 鸿蒙 | P1 | COMP-SPEC-2 | UiTest 断言 FIT_CONTENT 半屏的面板高度等于内容高度 | APP-12 |
| DSX-77 | 鸿蒙半屏页面统一用 CouliSheet.options，删掉私有面板 | 鸿蒙 | P1 | FU-DS-DIALOG-TITLE-ALIGN | 鸿蒙半屏页面都用 CouliSheet.options，私有面板参数 dragBar、maskColor 为 0 | — |
| FU-DS-SWITCH-DESC | 鸿蒙组件库输入与选择修正：验证码统一、开关副标题、胶囊和按钮参数 | 鸿蒙 | P1 | COMP-SPEC、DSX-122、DSX-119 | StepUpPanel.ets 里 focusRing 为 0 | APP-12 |
| DSX-78 | 鸿蒙登录与绑手机页迁移到组件库（含强更页品牌位） | 鸿蒙 | P1 | FU-DS-SWITCH-DESC | 鸿蒙登录页改用组件库件，写死尺寸与系统控件直用为 0，lint 基线 features/auth 清零 | — |
| DSX-79 | 鸿蒙我的 / 设置 / 隐私 / 换号页控件迁移 | 鸿蒙 | P1 | FU-DS-SWITCH-DESC | 鸿蒙我的 / 设置等页没有自绘开关和系统控件直用，字面量基线减半以上，快照重录 | — |
| DSX-80 | 鸿蒙搜索 / 订单 / 首页 / Agent 卡控件迁移 | 鸿蒙 | P1 | FU-DS-SWITCH-DESC、W-33 | 鸿蒙搜索 / 订单 / 首页 / Agent 卡私有胶囊与写死高度常量 grep 为 0 | — |
| DSX-81 | 鸿蒙钱包页控件迁移与字面量清理 | 鸿蒙 | P1 | LINT-STYLE-harmony、FU-DS-SWITCH-DESC | 鸿蒙钱包页系统控件直用与字面量基线清零，浅深快照重录，资金逻辑测试零改动 | — |
| DSX-82 | 鸿蒙守卫 G2：自绘开关和方块勾选框 | 鸿蒙 | P1 | LINT-STYLE-harmony | 两条守卫规则（自绘开关、方块勾选框）各有正例和反例 | — |
| FU-DS-harmony-pages | FU-DS（鸿蒙非资金页）：首次加载改骨架屏、订单详情错误态、私有提示条、草稿键 | 鸿蒙 | P1 | FU-DS-harmony、DSX-21 | features 里 LoadingProgress 只出现在白名单位置 | — |
| FU-DS-harmony-fund | FU-DS（鸿蒙资金与金额页）：钱包首屏骨架、提现状态键、「我的」金额缺失、受限会话转圈 | 鸿蒙 | P1 | FU-DS-harmony、DSX-01、DSX-21 | 鸿蒙钱包首屏是骨架，提现状态键统一，「我的」金额缺失按 BR-TEXT-10 展示 | — |
| FU-X-DLG-harmony | FU-X-DLG（鸿蒙）：44001 拦截弹窗主次按定稿统一 | 鸿蒙 | P1 | W-33 | 44001 拦截弹窗四处主次按定稿统一，截图与新画板一致 | — |
| DSX-83 | 鸿蒙动效落地：先核实减弱动态接口，再做统一入口和轮播公告节奏 | 鸿蒙 | P1 | DSX-13、DSX-26、DSX-122 | 接口实测记录附在 PR（交 DSX-132 回写 09） | — |
| HM-08-agent | HM-08（鸿蒙）：AI 商品卡 grid 按定稿口径，长按举报补可见入口 | 鸿蒙 | P1 | DSX-22、DSX-12 | Agent 卡截图覆盖 list 和 grid，并与稿一致 | HM-08 |
| DSX-84 | 鸿蒙无障碍守卫（含 Web 返回键读屏名） | 鸿蒙（协同 质量） | P1 | — | 设备用例断言两个返回按钮的读屏名等于字典值 | — |
| DSX-85 | 鸿蒙系统字号超 200% 的封顶与 3.2 倍验证（按 DSX-133 的决定实施） | 鸿蒙（协同 设计、质量） | P1 | DSX-133 | configuration.json 与负责人决定一致，设备用例覆盖选定上限且金额与按钮不截断 | — |
| DSX-86 | 鸿蒙截图基准与像素比对管线（浅 / 深、100% / 200%） | 鸿蒙（协同 设计） | P1 | — | 仓库有基准图（或 sha256 清单）和比对脚本 | — |
| DSX-87 | 鸿蒙折叠 / 展开连续性设备用例 | 鸿蒙（协同 质量） | P1 | TOKENS-PIPE-harmony、DSX-76 | 四个页面的折叠 / 展开用例通过并留截图 | — |
| HM-07-sdui | 鸿蒙首页 SDUI 按契约解码（含渲染上报和弹窗读屏名） | 鸿蒙（协同 后端） | P1 | CT-07e | 单测遍历全部 golden，结果与期望一致 | HM-07 |
| HM-03-web | 鸿蒙 ArkWeb：跟随主题与字号、标题回退、反色标题栏 | 鸿蒙（协同 后端、前端） | P1 | DSX-25、CT-03-env、DSX-122 | conformance 页的主题、字号用例在设备上通过 | HM-03 |
| APP-06v-harmony | 鸿蒙补做商品详情视觉对稿（APP-06v 鸿蒙份） | 鸿蒙（协同 设计） | P1 | DETAIL-V3-WB、DSX-117 | 有 compare-harmony.md，逐项都有结论 | APP-06 |
| APP-08v-harmony | 鸿蒙补做订单视觉对稿（APP-08v 鸿蒙份） | 鸿蒙（协同 设计） | P1 | — | NATIVE/APP-08v/compare-harmony.md 已有，逐项都有结论 | APP-08 |
| APP-09v-harmony | 鸿蒙补做钱包提现视觉对稿（APP-09v 鸿蒙份） | 鸿蒙（协同 设计） | P1 | — | compare-harmony.md 已有，逐项都有结论 | APP-09 |
| DSX-88 | 鸿蒙图片缓存与解码配置统一：设上限、按显示尺寸解码、商品图校验 https、预取 | 鸿蒙 | P1 | DSX-31 | Hypium 测试：缓存上限等于 03 §12 的数值、http 商品图映射为空态、首屏会预取、清除后缓存大小下降 | — |
| DS-02-harmony-image | 鸿蒙 9 处直写 Image(url) 收编为统一组件：四态、令牌图框、订单与详情圆角描边、下架去色 | 鸿蒙 | P1 | DSX-118、DSX-41、DSX-88、DSX-122 | 脚本检查这 9 处不再直接用远程地址调用 Image | DS-02 |
| DS-02-harmony-trend | 鸿蒙 PriceTrendPanel 改正：去掉「最低」，按日期和刻度画阶梯线、随容器宽度，补失败态和来源行 | 鸿蒙 | P1 | DSX-37、DSX-38、CT-22-trend、UI-STATES、DSX-122 | 鸿蒙走势去掉「最低 / 最高」、不再写死宽度，几何向量测试全过，截图含失败态 | DS-02 |
| DSX-129 | share.open 微信卡片缩略图压到 ≤32KB（鸿蒙） | 鸿蒙 | P2 | CT-03-share | 单测：同一组向量图压缩后 ≤32768 字节且是方形 | HM-10（原行加指针，不另建行） |
| DSX-113 | 鸿蒙标签组件去重与命名对齐（CouliChip 并入 CouliTag，ON_BRAND 改为 onSolid） | 鸿蒙 | P2 | COMP-SPEC | CouliChip 调用为 0、ON_BRAND 只剩弃用别名，目录页快照无预期外变化 | — |
| DSX-114 | 鸿蒙防连点与加载防闪 | 鸿蒙 | P2 | DSX-12 | 鸿蒙防连点单测（连点两次只推入一次）与加载防闪通过 | — |
| APP-13v-harmony | 鸿蒙补做注销 / 换号 / 绑手机号视觉对稿（APP-13v 鸿蒙份） | 鸿蒙（协同 设计） | P2 | — | NATIVE/APP-13v 下有鸿蒙的 compare，逐项都有结论 | APP-13 |
| DSX-115 | 鸿蒙平板设备类型按判定结果落地 | 鸿蒙（协同 设计） | P2 | DSX-10 | module.json5 与判定一致 | — |
| HM-07-lottie | 鸿蒙首页弹窗 Lottie 动效 | 鸿蒙 | P2 | HM-07-sdui、DSX-98 | 鸿蒙首页弹窗 Lottie 的兜底图与动画首帧各有设备截图 | HM-07 |
| DSX-116 | 鸿蒙读屏用词改取契约字典 | 鸿蒙 | P2 | DSX-41 | 鸿蒙草稿读屏键为 0，读屏用词取契约字典 | — |

### 5.7 质量（5 项：P1 5）

| 编号 | 标题 | 负责线（协同） | 分期 | 依赖 | 验收要点 | 对应 05 原任务 |
| --- | --- | --- | --- | --- | --- | --- |
| DSX-89 | 商品图三端同屏验收：六种真实主图进验收用例，对照模板加图框数值断言 | 质量（协同 设计） | P1 | DS-02-ios-image、DS-02-android-image、DS-02-harmony-image、DSX-32 | 10 有图片用例编号，并写明是否计入 S1 出门 | — |
| DSX-90 | 图表验收清单进 10，挂到相关任务，画板自检加读屏同源检查 | 质量（协同 设计） | P1 | DSX-37、DSX-39 | 10 有图表用例编号并挂到对应任务验收列，画板自检加读屏同源检查 | QA-11、QA-12（原行加指针，不另建行） |
| DSX-91 | 三端组件目录页并排对照（真机） | 质量（协同 设计） | P1 | COMP-SPEC、COMP-SPEC-2、DSX-118、DSX-119、DS-02-iOS-3 | 对照页覆盖 component-spec.json 的全部组件，三端各有浅深两态 | — |
| DSX-136 | 内测前人工真机冒烟一轮（7 个关键页 × 三端截图和录屏） | 质量（协同 设计、iOS、安卓、鸿蒙） | P1 | — | 私有 bucket 有本轮截图和录屏，并逐页与基准对照 | QA-08（原行加指针，不另建行） |
| DSX-139 | QA-11 / QA-12 按端立项入账、读屏清单合并（rebate-platform ops/tasks） | 质量（协同 设计、iOS、安卓、鸿蒙、前端） | P1 | DSX-14 | ops/tasks 有 QA-11、QA-12 各端条目，带执行页面、用例编号与证据位置 | QA-11、QA-12（原行加指针，不另建行） |

## 附录 各项范围与验收

下面是派工用的范围与验收原文（已按第 4 节调整），供开工时核对。写的是要改哪里、怎么验收；其中提到的业务规则以 08 为准，文案以 08 BR-TEXT-14 为准，与 08 不一致时修本附录；提到的平台行为以 09 为准，09 尚未核实的只是待验证的线索，不作为事实或对用户的承诺。「来源」行的 g1-01、A2-03 一类编号指私有审计报告里的条目。

### 设计

<details>
<summary><b>COMP-SPEC</b> · P0 · 组件规范 v1.0 定稿（一）：框架、基础控件、文字角色与机读规格表</summary>

负责线：设计（协同 iOS、安卓、鸿蒙、前端）；依赖：DETAIL-V3-WB；承接：组件规范定稿（D10-643 ⑨）。

**范围**

在已派的 ⑨ 里，把 couli-runs 的 component-inventory.md（v0.1）去掉私有内容，升格为规划仓库唯一的公开组件规范。新建 design/components/README.md（v1.0，带变更记录，登记到 00 §7 和 design/README）和 design/components/component-spec.json。json 是机读表：组件 × 变体 × 尺寸 × 状态 × 属性 → 令牌名或数值，列出 ios / android / harmony / h5 的实现名，带 version 字段，供三端 contract.lock 增加 component_spec 锁定。03 §10.2 的基础控件改成指针，不复述。本单写这些内容：

① 分层，以及「三端必须一致 / 允许各端原生 / 由 SDK 决定」三类。清单 §8 的四个待决问题按推荐结案（负责人 11-05 已定：组件按规划统一，这类不用问）。

② Button：分常规、紧凑两种尺寸，紧凑按钮视觉高 44，命中区按平台扩到 44 / 48，不改视觉；写明 component.control.min-height 说明里「原生按平台目标取较大值」指的是命中区（安卓视觉高被做成 48 的根源在这句）。主按钮形状只留几种变体并写明用途（默认圆角 12、胶囊 999、详情底栏组合胶囊）。次按钮字重 500，另定文字按钮内边距、禁用次按钮外观、加载转圈尺寸。卡内白底按钮统一叫 onSolid。

③ RebateTag 大号定一种圆角和内边距，并裁定 GUIDE §3 与 §7.2 哪种现行。

④ FilterChip 只留一种规格：视觉高 32，命中区 44 / 48，统一字号与选中字重，三态为未选 / 已选（带对勾）/ 禁用，三端都在设计系统层实现。

⑤ 输入：PhoneField「+86」后不加分隔线；CodeInput 圆角 10（负责人 10-19 批准的例外），当前格用 border.active，定数字字号与格高。

⑥ 文字角色表：页面标题、模块标题、半屏标题（22/600）、正文、说明、价格主 / 列表、金额展示，逐项给字号、行高、字重、是否等宽数字，消除同名 title 在三端默认字重不一致的问题。

⑦ §3.1–§3.5 每个组件都写用途、状态矩阵（默认 / 按下 / 禁用 / 加载 / 聚焦 / 错误 / 只读 / 深色）、令牌、命中区、读屏和三端统一名。NavBar、TabBar、TopTabs、FilterChip、PageScaffold 登记进 03 §10.2。另把 d0aaa76（详情 v3 回写）在 03 §10.2 新增或改写的 PlatformBadge 标题标签形态、BuyBar 组合胶囊、StoreCard、ProductGallery、FeedbackSheet 的数值登记进规范（取 v3 定稿画板：标签高 20、内边距 5、12/600、与标题间隔 6；组合胶囊高 48、重叠 24），令牌名用 DETAIL-V3-WB 的 color.platform.tag.*、radius.tag、radius.avatar、overlay.on-image。

⑧ 删掉清单第 38、252 行「MVP 强制浅色」一类已被 00 D35 取代的句子。规范不再手写各端「现状」列，与登录 v2 定稿解绑；只引 BR 编号。变更记录写进 docs/changes/20261105-组件规范定稿.md。规范只定数值、不改令牌源：所有新令牌（含 COMP-SPEC-2 的 component.state.*、DSX-118 的图框）由 DSX-02 在 v0.6.0 一次写入；平台标签色与图上控件底由 DETAIL-V3-WB 在 v0.5.1 写入。商品卡变体的唯一名单由 DSX-22 写进本规范，03 §10.2 只放指针。

来源：g1-01、g2-01、g3-01③、g4-11①。

**验收**

① design/components/README.md（v1.0，状态「生效」）和 component-spec.json 已在 couli origin/main，json 能解析，覆盖清单 §3.1–§3.5 全部组件，每行都有三端实现名；② Button、RebateTag、FilterChip、文字角色、输入各有「变体 × 尺寸 × 状态」数值表，每个值都能在定稿画板里找到出处；PhoneField 分隔线、CodeInput 圆角与当前格色、FilterChip 高与字重、次按钮字重、紧凑按钮视觉高 44 / 命中区 44 或 48、各级默认字重都只有一个取值；③ 03 §10.2 指向 design/components，并登记了 NavBar / TabBar / TopTabs / FilterChip / PageScaffold；④ 执行 `git grep -nF '强制浅色' origin/main -- design/` 只剩「由 D35 取代」一类历史说明；⑤ 清单 §8 四问有裁定和日期；⑥ kanban --check --local 无 WARN，gitleaks 通过。

</details>

<details>
<summary><b>COMP-SPEC-2</b> · P0 · 组件规范 v1.0 定稿（二）：反馈与弹层、通用状态、按压与动效归属</summary>

负责线：设计（协同 iOS、安卓、鸿蒙、前端）；依赖：COMP-SPEC；承接：组件规范定稿（D10-643 ⑨）。

**范围**

在同一份规范和 component-spec.json 里补上以下内容（商品图拆到 DSX-118，首页卡、业务件与 tonal 裁定拆到 DSX-119；规范只定数值，令牌一律由 DSX-02 在 v0.6.0 写入，本单不改 design-tokens.json）：

① Dialog：标题对齐只定一种（或给按场景的表）、元素间距、内边距、按钮行次左主右、宽为屏宽 − 48 并封顶；同时写明哪些场景用系统 AlertDialog / ActionMenu。

② Sheet：高度档、把手、右上关闭、能否下滑或点遮罩关闭；资金与验证类用保护型；遮罩用 overlay.scrim。

③ Toast：App 内一律在页顶并让开导航栏；普通 2 秒、长文 3.5 秒，由组件计时，页面不得传时长；连续提示替换、不排队；按成功 / 信息 / 警告 / 错误绑定图标和颜色；polite 播报；鸿蒙用系统样式，列为允许的原生差异；写明站外 H5 是否例外。

④ 按压：主按钮用 button.primary.pressed，其余用系统按压反馈；带文字的元素不得用 opacity&lt;1 表示按下或禁用（GUIDE:205）。

⑤ ErrorState 的 kind（load_failed / network / maintenance / custom），默认实心主按钮、最大宽 240；EmptyState 定按钮主次和 density；NoticeBar 四种 tone、可带动作。三端参数同名，与 UI-STATES 同口径；03 §10.2 的状态组件行改为引用 specs/ui-states.yaml（原 UI-STATES ④ 的规划仓库部分）。组件名在 NoticeBar 和 InlineNotice 里二选一，避免与 SDUI notice_bar 同名，下游任务以定稿名为准。

⑥ Skeleton：商品卡、订单卡、钱包卡三种；在静态和低幅脉冲里定一种（减弱动态时静止）；只用一个颜色令牌（名称与取值写进规范，由 DSX-02 写入 color.skeleton）。

⑦ 空态图形：MVP 用 96 浅底块加 32 图标，design/README 第 12 项改为「MVP 不做插画、P2 再议」。component.state.*（占位块 96、图标 32、上下留白、按钮最大宽 240）的名称与数值写进规范，令牌由 DSX-02 写入。

⑧ 动效归属：页面转场、系统控件按压、半屏出入场随系统；Toast、Skeleton、Banner、NoticeBar、折叠行等自绘组件随 motion 令牌。

⑨ CouliTag 状态款按语义自动带图标，不能只靠颜色，组件 API 不提供单独改图标色的参数。

来源：g2-02、g3-01、g4-11、g5-01。

**验收**

① component-spec.json 含 Dialog、AlertDialog、ActionMenu、Sheet、Toast、NoticeBar（或定稿名）、Skeleton、ErrorState、EmptyState、CouliTag 状态款各行；Dialog 标题对齐、元素间距和 Toast 时长各只有一个取值或有场景表；② 规范写明 component.state.* 与骨架色的名称和数值，本单 PR 不改 design-tokens.json；③ 组件命名（NoticeBar / InlineNotice）有书面裁定；④ design/README 第 12 项状态已改；⑤ 03 §10.2 状态组件行指向 specs/ui-states.yaml 与 design/components；⑥ kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-118</b> · P0 · 组件规范 v1.0 定稿（三）：商品图 ProductImage（四态、图框、渐显、读屏键）</summary>

负责线：设计（协同 iOS、安卓、鸿蒙、前端）；依赖：COMP-SPEC；承接：组件规范定稿（D10-643 ⑨，COMP-SPEC-2 拆分）。

**范围**

从 COMP-SPEC-2 ⑩ 拆出，只改规划仓库：在 design/components 规范和 component-spec.json 写 ProductImage 条目——加载中、为空、失败都只显示 placeholder 底加 1px border.subtle 描边，不写字；图框名称与数值（列表、网格、横滑、详情、订单、角标内距；网格在「固定高 132」和「157:132 比例」里定一种）写进规范，令牌由 DSX-02 写入 component.image.*；详情主图按 v3 通栏 1:1 cover 加页码；「推广」角标放左上 8、白底描边；网络加载完成才渐显，内存命中直接显示，减弱动态时不渐显；读屏名统一为「商品图片，{标题}」，列表小图不读，键登记到 08 BR-TEXT-14 表 C，card.image_placeholder 和 order_list.image_placeholder 注明作废；目录页只展示在用的 ProductImage。私有稿的清理不在本单：Orders-v2 的「商品图」占位字随 W-33 改稿，GUIDE §6 的 #EFEAE2 随 DSX-08 迁移改，APP-11v brief 的旧图框写法随 DSX-89 改。

来源：g5-01（ProductImage 部分）。

**验收**

① component-spec.json 有 ProductImage 行（四态、各图框、渐显、读屏），网格图框只有一种写法；② 08 表 C 有商品图读屏键，并注明两个占位字键作废；③ 规范写明 component.image.* 的名称和数值，本单 PR 不改 design-tokens.json；④ kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-119</b> · P0 · 组件规范 v1.0 定稿（四）：首页 8 类 SDUI 卡、订单与资金业务件、tonal 与卡内 40 高按钮裁定</summary>

负责线：设计（协同 iOS、安卓、鸿蒙、前端）；依赖：COMP-SPEC；承接：组件规范定稿（D10-643 ⑨，COMP-SPEC-2 拆分）。

**范围**

从 COMP-SPEC-2 ⑪⑫ 拆出，只改规划仓库的 design/components 规范、component-spec.json 和 03 §10.2 指针行：

① 首页 8 类 SDUI 卡各写令牌、状态、浅深两态和 200% 表现。

② 新登记业务件：OrderCard、LedgerRow、RecordRow、PendingTrackCard；状态胶囊并入 CouliTag 状态款，步骤条并入 Timeline。

③ tonal 按钮和卡内 40 高按钮：书面裁定收进 CouliButton 变体还是改稿（组件按规划统一，不问负责人）；裁定结果供 FU-DS-LINE-HEIGHT-ios、DSX-65、FU-DS-SWITCH-DESC、DSX-46 实现，变体数值由 DSX-02 进令牌。

④ 品牌位一律用 CouliLogo / BrandMark；ThirdPartyLoginRow 用 oauth.gap。

来源：g2-02、g4-11、g5-01（首页卡与业务件部分）。

**验收**

① component-spec.json 含 OrderCard、LedgerRow、RecordRow、PendingTrackCard、Timeline、首页 8 类卡各行；② tonal 按钮、卡内 40 高按钮有书面裁定；③ 03 §10.2 中 grep -c -E 'OrderCard|LedgerRow|RecordRow' ≥ 3，且只写指针；④ kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DS-03</b> · P0 · 组件库维护常驻任务：改一处、处处同步，设差异上限，通用状态不得带差异合并</summary>

负责线：设计；依赖：无；承接：组件库维护常驻任务（D10-643 ⑩）。

**范围**

在已派的 ⑩ 里写进 05 和 11，落实负责人 11-05 R8「组件改一处就同步到所有用到的地方」。05 新立常驻任务 DS-03（三端组件库维护，按周清零），登记这些欠账并写明承接任务：FU-DS-LINE-HEIGHT（iOS → FU-DS-LINE-HEIGHT-ios，安卓 → DSX-65，鸿蒙 → DSX-75）、FU-DS-BUTTON-ICON（iOS → FU-DS-LINE-HEIGHT-ios，安卓 → DSX-65，鸿蒙 → FU-DS-SWITCH-DESC）、FU-DS-DIALOG-TITLE-ALIGN、FU-DS-SWITCH-DESC、FU-DS-SWITCH-MARGIN（→ FU-DS-SWITCH-DESC）、FU-DS-ANDROID-SYMBOLS，Android 视觉余项 C3（→ DSX-65）、C4（→ FU-DS-android-pages）、C6（→ DSX-66），以及本计划里的组件库子项。DS-02 行分端写状态：Android b795720、鸿蒙 8134a00 已合，iOS 由 D10-643 派。

11 写入以下规则：

① 同步清单：画板上的组件改动必须同批走「组件规范 → 令牌源 → design/specs → 三端与 H5 组件库 → GUIDE」，缺一步不算完成。

② 页面任务书的「依据摘录」用脚本从定稿 .dc.html 抽出字号、行高、字重、圆角、间距、颜色，逐项对照令牌名写进去，不许按截图估值（APP-06v 的 20/700 就是这样来的）。

③ 令牌升版清单加一项「回扫三端注释与常量」。

④ 页面单可以按 D10-401 直接扩组件库：只加带默认值的参数，默认外观逐像素不变。

⑤ 组件库已有同类组件时，页面私写 Row / Bar / Pill / Chip / Field / Button / Card / Switch 记 S1；与组件库同名的私有函数一律改名或删除。

⑥ 某个控件的页面迁完，就把该控件的守卫从警告转为失败，不等定稿。

⑦ 开放的「组件库差异」上限 20 条，超限先排 DS-03，再开新页面单。

⑧ 同一画板的视觉任务三端同批派，做不到就在看板上标出未跟进的端。

⑨ StateLoadFailed、StateNetworkError、通用空态、首次加载骨架这几类通用状态，不得记为差异后合并；compare 模板固定一节「通用状态」，按定稿 sha256 逐端判定，并列出 FU-DS 合并后的重判清单。

⑩ 评审项加「视觉一致性」：偏离令牌或组件库用法记 S1；同一偏差在两页以上出现时，上升为设计系统层面的决定。同步改 DS-01 / APP-xxv 的评审模板（「纯风格不报」不再覆盖令牌偏离）；首个上升样例是 APP-11v 按钮圆角 12 / 图标 20 对画板 999 / 16。

另在规划仓库 scripts/ 写抽数脚本（画板路径作参数传入，仓库里不放画板内容）：输入 .dc.html，输出「值 → 令牌名 / 令牌外」表；11 的任务书模板加「抽数表」一节。新派页面任务书是否带抽数表，由 DSX-24 的看板检查抽查。变更记录写进 docs/changes/20261105-组件库维护与差异上限.md。

来源：g1-02、g2-03、g3-02、g4-12。

**验收**

① 05 中 grep -c '^| DS-03 ' 为 1，且列出上述 FU-DS 编号；DS-02 行分端写状态；② 11 能 grep 到同步清单、「只加带默认值参数」、差异上限、「组件库已有同类组件」的 S1 口径、通用状态不得带差异合并、视觉一致性定级；③ 抽数脚本在规划仓库 scripts/，对 ProductAuthSheet-v2 跑通并输出 sheet-title 22 / 28.6 / 600；④ 评审模板已改，APP-11v 按钮口径有裁定记录；⑤ 11 写明任务书模板有「抽数表」一节；05 DS-03 行的每个欠账都有承接任务键；⑥ kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DETAIL-V3-WB</b> · P0 · 详情 v3 令牌与组件补登：平台实底标签色、图上控件底、标签与头像圆角进令牌（实际 v0.5.0 / v0.5.1）</summary>

负责线：设计（协同 iOS、安卓、鸿蒙、前端）；依赖：无；承接：详情 v3 定稿回写的令牌部分（d0aaa76 变更记录 §7 第 5 项）；状态（2026-11-05）：已完成（v3 回写 couli #274 d0aaa76，令牌 v0.5.1 #276 f088f04）。

**范围**

外部前置：规划仓库 docs/detail-v3（提交 d0aaa76，负责人 2026-11-05 R2–R13 定稿回写）已合并到 origin/main。分工写明：R2–R13 的规则与规格回写都由 d0aaa76 完成、本单不重复——08 BR-PRICE-03 / 17（R13 详情去掉三句口径小字）、BR-PRICE-09（R9 预估返后不展示）、BR-PRICE-08 / 21（R11 无返利商品不出卡，btn.buy.no_rebate 只留给点击时才变成无返利的卡）、BR-TEXT-12 / 14 表 C（R10 / R12「购买预估返 ¥x」btn.buy.rebate、「购买可返利」btn.buy.rebate_unknown，TRADE-21 按钮文案改定；R7 店铺块 shop.* 与【进店】；反馈 feedback.*；price_trend.current / mode / mode.note* / title.pdd* / source.pdd*）、01 F-PROD-05 字段清单、F-PROD-14 ⑧⑨（最常见价门槛沿用 ③ 的 price_trend.min_distinct_days，与 v3 定稿一致）、F-PROD-15、03 §10.2 的 PlatformBadge 标题标签形态、BuyBar、StoreCard、ProductGallery、FeedbackSheet、PriceTrendPanel，以及 app-product-detail.md 重写。本单只做 d0aaa76 变更记录 §7 第 5 项留下的令牌部分，单独一个 PR，单独升版（只新增键、不改已有值；实际随 v3 回写 #274 升 v0.5.0，#276 补 radius.tag、radius.avatar 为 v0.5.1）：

① 写变更记录 docs/changes/20261105-平台标签色进令牌.md（引负责人 11-05 R6、R7、R8 原话），改写 tokens/README 第 101 行「此版不引入任何商家品牌色」，03 §10.2 PlatformBadge 行里「第三轮为白底描边、中性文字」改为历史说明并指向新令牌，03 §10.1 登记新令牌。

② design-tokens.json 加 color.platform.tag.taobao / tmall / jd / pdd 的 background 和 text（取 v3 定稿值 #D53D00 / #EA0031 / #E02018 / #EB0007 配白字，dark 同值），加 overlay.on-image（rgba(0, 0, 0, 0.55)，即 overlay.scrim 深色值，浅深同值）；新增令牌档 radius.tag=4（负责人 R6 截图样式，不改稿）和 radius.avatar=10（R7 店铺头像）。colors.md 补四色白字和图上控件的对比度。tokens/README 登记第三方标识色例外表（四个平台标签色、微信绿 #07C160、Apple 黑白等），写明只用于平台来源标识。metadata.version 升版（实际 0.5.0，#276 后 0.5.1）。

③ 标签字号 12/600、高 20、内边距 5、与标题间隔 6，组合胶囊高 48、重叠 24 等组件数值由 COMP-SPEC 写进 design/components 并引用本单令牌名；GUIDE §6、§7.1、§7.2 的 v3 同步由 DSX-08 迁移时一并做。

④ 价格走势与最常见价不加任何开关（负责人 2026-10-05 定价格走势「进入近期开发、不做开关隐藏」，最常见价是负责人 2026-11-04 亲自加的；v3 第 11 条已用两个并排数据块、不用比较词、摘要只用 BR-TEXT-13 模板句处理法务顾虑）。d0aaa76 若未在 06 登记「最常见价与当前价并排的表述」，在 06 法务节补一行，只作事后核对，不影响上线。

⑤ 跑 sync-brand.py；变更记录列出受影响的页面（首页、搜索、收藏、热销榜、AI 卡、订单卡、详情），供 DSX-117 写进 v3 合派（D10-641）任务书。DSX-02 的 v0.6.0 在本版之上升版。

来源：g1-03、g2-04、g5-49。

**验收**

① 开工前核对 origin/main 已含 d0aaa76：08 BR-PRICE-03 / 09 / 17 和表 C 的 btn.buy.* 已按 R9–R13 改写、F-PROD-14 ③⑧ 的门槛为 ≥2 个不同日期（本单不改，在 PR 说明里列出核对结果）；② `python3 scripts/sync-brand.py --check` PASS，metadata.version 为 0.5.0（#276 后 0.5.1），新增键都在、已有键取值不变；③ 执行 `git grep -nF -e D53D00 -e EA0031 -e E02018 -e EB0007 origin/main -- design 规划`，只命中 design-tokens.json、生成物、colors.md 和 tokens/README 例外表；④ 四色白字对比度浅深两态都 ≥4.5:1；⑤ tokens/README 不再写「不引入任何商家品牌色」，03 §10.2 PlatformBadge 行指向新令牌；⑥ docs/changes 有变更记录，列出 BR、页面、接口和恢复方式；⑦ 全文没有「受开关控制」一类写法；⑧ kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-117</b> · P0 · v3 合派（D10-641）任务书补充：平台标签令牌、最常见价为空不显示、走势不加开关、详情浮动返回键</summary>

负责线：设计（协同 iOS、安卓、鸿蒙、前端）；依赖：DETAIL-V3-WB、DSX-126；承接：与 D10-641（v3 合派）相关；状态（2026-11-05）：已完成（编排 D10-664 派出，任务书在 couli-runs/DETAIL-V3/）。

**范围**

只改 couli-runs 里三端和 H5 的 v3 合派任务书（编排私有工作目录，直接提交），不改规划仓库。给 D10-641 各端任务书补：

① 平台标题标签取 DETAIL-V3-WB 的 color.platform.tag.* 和 radius.tag，图上返回键、页码底取 overlay.on-image；各端令牌锁先跟到含 v0.5.1 的提交（在 TOKENS-PIPE 的 v0.4.0 之上，随 v3 单一起升），不等 v0.6.0。验收加：代码里 #D53D00、#EA0031、#E02018、#EB0007 四个色值为 0 处。

② 平台标签覆盖 DETAIL-V3-WB 列出的全部页面；首页横滑卡按 DSX-126 改过的 Main-v3 画板，随本次合派落地，不另开首页视觉单。

③ 价格走势折叠行在三平台都显示，不加开关；mode_price_fen 为 null 时「当前」「近 30 天最常见价」两块和统计口径句都不显示，不等后端字段（B1-29-trend 上线前恒为 null）。iOS 的走势由 DSX-134 与 iOS 详情 v3 同批交付。

④ 详情页顶部按 v3：去掉标题、只留浮动返回键，iOS 走 DS-02-iOS-3 的白名单（透明栏加浮动返回键，边缘右滑返回照常可用）。

⑤ 多图只在契约有 images[] 后显示，之前只显示主图且不显示页码（G1-16）。

来源：评审意见第 1、4、6、18 条。

**验收**

① D10-641 三端和 H5 任务书都含上述五项，并写明对应验收（色值 0 处、mode 为 null 不显示、无开关、浮动返回键）；② 编排在 HANDOFF 记下补充时间和任务书路径。

</details>

<details>
<summary><b>DSX-01</b> · P0 · 08 登记通用状态键与金额缺失展示规则，修正 BR-TEXT-14 影响面</summary>

负责线：设计（协同 后端）；依赖：无。

**范围**

与 be 的 UI-STATES 同步，本单先合或同日合：

① BR-TEXT-14 表 C 登记 state.loading、state.load_failed.title / .desc、state.retry、state.empty.default（断网沿用 net.unavailable，原因沿用 error.&lt;code>），注明它们取代的模块草稿键（wallet.load_failed、me.load_failed、withdraw.load_failed、home.loading、order_list.network_error、order.network_error 等），归入「普通」段。

② BR-TEXT-14 影响面里「error-codes.yaml 新增 text_key」一句，改为按 error.&lt;code>[.&lt;reason>] 命名约定取键、不设 text_key 字段。

③ BR-TEXT-10 补客户端金额字段缺失时的展示：不补 0，显示「—」或整块进错误态。按 11 §7.1 由 Jev 判断，变更记录写明置信度。

来源：g3-03。

**验收**

12_TEXT 表 C 能 grep 到上述 state.* 键；grep「新增 text_key」为 0；BR-TEXT-10 有缺失展示条文；kanban --check --local 无新增 WARN；UI-STATES 合并后，脚本比对 08 表 C 与 texts.default.json 的 state.* 零差异。

</details>

<details>
<summary><b>DSX-126</b> · P0 · Main-v3 首页横滑卡平台文字标签改稿（v3 合派前完成）</summary>

负责线：设计（协同 iOS、安卓、鸿蒙、前端）；依赖：DETAIL-V3-WB。

**范围**

从 DSX-22 拆出。按负责人 2026-11-05 R8「列表卡也统一用这种平台标签」和 d0aaa76 的 PlatformBadge 标题标签形态，改 Main-v3 首页横滑卡（及首页网格卡如有）的标题前平台标签：实底文字标签、取 DETAIL-V3-WB 的 color.platform.tag.* 与 radius.tag，与标题同一段文字、折行顶格。只改画板并在 design/README 重登 sha256，过 Codex 对抗审查；必须在 v3 合派（D10-641）任务书补充（DSX-117）之前完成，三端随合派落地，不另开首页视觉单。

来源：g3-19（横滑卡部分）、评审意见第 18 条。

**验收**

Main-v3 改稿已登记 sha256 并通过 Codex 审查；画板里标题前平台标识都是实底文字标签；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-02</b> · P1 · 令牌升版（一）：文字角色、组件变体与状态、基础令牌、图框尺寸，统一发布 v0.6.0</summary>

负责线：设计（协同 iOS、安卓、鸿蒙、前端）；依赖：COMP-SPEC、COMP-SPEC-2、DSX-118、DSX-119、DETAIL-V3-WB、DSX-03、DSX-04、DSX-08。

**范围**

按组件规范（COMP-SPEC、COMP-SPEC-2、DSX-118、DSX-119）定下的数值改 design-tokens.json，所有新令牌在本单一次写入。v0.6.0 在 DETAIL-V3-WB 的 v0.5.1 之上升版，并把 DSX-03、DSX-04 已合入但未改版本号的令牌一起发布：本单是唯一改 metadata.version 的一单，最后合；三端和 H5 只锁本单的合并提交。先扩 scripts/sync-brand.py，让它支持复合文字样式类型。

① 文字角色：text.page-title、section-title、sheet-title、body、caption、price.main、price.list、amount.display，以及各级默认字重。

② 组件变体与状态：

- button.size.regular / compact、button.radius.default / pill / bar；

- color.button.secondary.{default,pressed,disabled} 和 button.text.{pressed,disabled}，都带 dark；

- rebate-tag.large、chip.*、tag.*、验证码格字号和圆角；

- tonal 与卡内 40 高按钮按 DSX-119 的裁定；

- component.state.*（占位块 96、图标 32、上下留白、按钮最大宽 240，取 COMP-SPEC-2 的数值）；

- component.control.min-height 的说明改为明确指命中区。

③ 图框：component.image.list / grid / scroll / hero / order / badge-inset，取值按 DSX-118 的定稿（网格只有一种写法）。

④ 基础补齐：

- 描边宽：border.width.hairline=1 / active=2、icon.stroke=1.75；

- icon.large=32、opacity（禁用、图片上遮罩）、font.numeric、letter-spacing；

- color.skeleton：取 COMP-SPEC-2 定的那一个；

- 画板反复出现的品牌方块尺寸；

- 对话框和弹层宽由 DSX-03 的 dialog.max-width 承担，本单不重复。

⑤ 2 / 6 微间距：纳入刻度或从画板清除，二选一写进 tokens/README，并同步 design/guide/GUIDE.md（DSX-08 迁移后）；verify.py v2（DSX-123）直接读令牌刻度，不另维护白名单。

⑥ colors.md 补新颜色两种主题的对比度；tokens/README 写各端换算；写变更记录；升版并生成。图表色板由 DSX-04 写入、布局与动效令牌由 DSX-03 写入，都随本单的 v0.6.0 一起发布；变更记录合写三单的令牌清单。

来源：g1-17、g2-05、g5-02。

**验收**

① `python3 scripts/sync-brand.py --check` PASS，metadata.version 为 0.6.0，且 DSX-03、DSX-04 的 layout / motion / layer / chart 键都在本版里；上列键（含 component.state.*）都存在，颜色键都带 dark；② variables.css 有 component.image.* 变量；③ tokens/README 给出每个新类别在 H5 / iOS / 安卓 / 鸿蒙的换算；④ colors.md 有 skeleton 两态的对比度；⑤ docs/changes 有变更记录并列出受影响的组件；⑥ TOKENS-LAG 对三端报落后，直到 DSX-120 / DSX-121 / DSX-122 合并。

</details>

<details>
<summary><b>DSX-03</b> · P1 · 令牌升版（二）：布局、动效、叠放层级、反色标题栏，写清阴影各端换算</summary>

负责线：设计（协同 iOS、安卓、鸿蒙、前端）；依赖：COMP-SPEC、COMP-SPEC-2。

**范围**

① sync-brand.py 支持 duration 和 cubicBezier 类型。加 motion.duration.instant / fast / normal / slow、motion.easing.standard / enter / exit、motion.toast.display（与 COMP-SPEC-2 的 Toast 时长一致；现在 H5 和鸿蒙是 2000，安卓首页是 2500）、motion.skeleton.pulse。写明减弱动态时时长取 0 或改为淡入。

② 布局令牌：layout.content.max-width=600、layout.breakpoint.large=600、dialog.max-width、page.gutter=16、card.padding=16 / 12、card.gap=12、底部固定栏内边距。登录或表单如果要更窄的版心，单列 layout.form.max-width 并写明适用页面，否则三端统一 600（取代 iOS 560、安卓 480）。

③ 叠放层级：layer.base / sticky / sheet / dialog / toast。

④ component.navbar.inverse.background / text，浅深两套，用于 ExternalPage 的 nav_style=dark，colors.md 记录两态对比度。

⑤ tokens/README 阴影一行写出各端换算公式（CSS blur → iOS shadowRadius / ArkUI radius / 安卓 elevation），按官方文档核对并注出处。

⑥ 03 §10.1、§10.4 改为引用 layout 令牌，写变更记录。本单只往 design-tokens.json 加键、不改 metadata.version，版本由 DSX-02 统一升到 v0.6.0 发布；三端不跟本单的中间提交。

来源：g1-18、g3-06、g4-18。

**验收**

`python3 scripts/sync-brand.py --check` PASS，metadata.version 未改动，生成的 CSS 带 duration、easing、z-index、layout 变量；jq 能取到 tokens.layout.* 和 tokens.motion.*；转换表有 duration、cubicBezier、shadow 三行，每端公式都带官方文档链接；navbar.inverse 浅深两态 ≥4.5:1；03 §10.4 引用了 layout.content.max-width；docs/changes 有记录。

</details>

<details>
<summary><b>DSX-04</b> · P1 · 图表规范与色板令牌：color.chart.* 浅深两套，03 §10 加「图表」一节，含 Grafana 看板规范</summary>

负责线：设计；依赖：无。

**范围**

design-tokens.json 新增 color.chart.*：series（多系列，带深色，色觉障碍可分）、reference-line、grid、axis、axis-label、annotation、tooltip、focus。实算对比度记进 colors.md，跑 sync-brand。本单只加键、不改 metadata.version，随 DSX-02 的 v0.6.0 一起发布。这就是原审计里「图表多系列色板」和 D10-643 P1「图表色板与走势改正」的色板，三处只做一次。

03 §10 加「图表」一节：

- 线型、线宽、端点、标注、图例；不同系列用虚线或点形区分，不能只靠颜色；

- 价格走势线和「最近记录」标注用价格墨棕色加中性底；GUIDE 里「墨棕或 #A83B1F」的两可写法由 DSX-08 迁移时删掉；鸿蒙和后台现在用的 #C44820 也照此改；

- 后台 G2 主题从 ui-tokens 取同一组令牌。

Grafana 看板规范：时区固定 Asia/Shanghai；金额用 ¥、两位小数、千分位，不用 1.2K；标题带口径编码、截至时刻、刷新方式；浅色主题按令牌改色；每张图配一个表格视图；看板 JSON 入库评审。这些条款同时补进 05 F1-14 原行的验收列（05 原行补验收列，不另立任务，也不给 F1-14 加前置依赖）。

删改 flow-map §22 里两行过时内容。

来源：g5-35（含 g1-17 的图表色板部分）。

**验收**

design-tokens.json 有 color.chart 组，sync-brand --check 通过；colors.md 有浅深两态对比度（非文字 ≥3:1）；metadata.version 未改动；03 §10 有「图表」一节和 Grafana 条款；05 F1-14 行的验收列含时区、金额写法、标题口径编码、表格视图四条；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-05</b> · P1 · 公开设计原则文档：个性词、插画与品牌 IP 用法、品牌语气规则</summary>

负责线：设计；依赖：COMP-SPEC-2、DSX-08。

**范围**

① 新建公开的 design/principles.md，写这些内容：

- 定位怎么落到视觉（新用户和老用户、自购为主推广为辅、AI 和返利各占多少视觉权重）；

- 3–5 个个性词，每个配「要 / 不要」示例；

- 差异化的正向要素和反向禁区；

- 图标、插画、图片、品牌 IP、文案语气、深色各一节。

GUIDE §7（DSX-08 迁移后在 design/guide/GUIDE.md）和清单 §1 里定位与个性相关的段落搬进来，GUIDE 只留指针，不写第三方 App 的界面细节。

② 插画与 IP：MVP 按 COMP-SPEC-2 的结论，用 96 图标占位块、不做插画；P2 插画风格定方向（线宽 1.75、只用令牌色、带深色版）。小狸只出现在 Logo、启动页、关于页等品牌位，还是也能进空态；AI 助手要不要头像。由编排定，必要时用 Jev 判断；如果要外包画师（花钱），另问负责人。

③ 08 新增 BR-TEXT-27「品牌语气」：人称用「你」，不用感叹号和表情，不用网络流行语，一句只说一件事。包内默认文案硬性遵守，运营可改的文案只做提示。08 README 登记索引，principles.md 只引编号。

④ 同步 design/illustrations/README、design/README 第 12 项、06 Q-E6；03 §10、CLAUDE.md 的 design/ 一节、GUIDE 开头都指向 principles.md。

来源：g1-12。

**验收**

design/principles.md 已有上述各节，每个个性词都有「要 / 不要」示例；08 README 索引有 BR-TEXT-27；design/README 第 12 项和 06 Q-E6 写明定论；03 §10 和 CLAUDE.md 有指向；kanban --check --local 无新增 WARN。

</details>

<details>
<summary><b>DSX-06</b> · P1 · 定三端图标口径、导出唯一 SVG 源，补启动页规范</summary>

负责线：设计；依赖：无。

**范围**

① 在 design/icons/README 公开写明三类图标，并逐个列出图标名：

- 品牌脸面：底栏 4 个常态和选中、「我的」宫格、钟表返利、空错态大图标；

- 内容图标：照画板；

- 系统控件自带：返回、关闭、勾选、系统分享等。

前两类三端共用一套凑狸 SVG，第三类用各端系统图标集。写明本清单取代 D10-559 和清单 §1②、待决 2 的冲突说法。安卓 CouliIcons 实际是 1.75 描边的自绘路径；FU-DS-ANDROID-SYMBOLS 按此结案。鸿蒙 SymbolGlyph 和 CouliIcon 的分工也按这张清单。

② 导出唯一源：三端各自补画的图标（钱包、流水、心形、铃铛、星、趋势等）每个只留一种形状，统一为 24 视口、1.75 描边，按类别放进 design/icons/tab、grid 等目录，design/icons/README 是唯一清单；GUIDE §4 由 DSX-08 改为指向它。

③ 启动页：design/splash/README 定图形为原色 logo-mark，浅色底用 canvas，深色底用 #171513，并写各系统的尺寸要求；不含平台商标；brand.config.json 登记 assets。

④ design/README 第 5、10 项改状态。

来源：g1-13。

**验收**

design/icons/tab 下至少 8 个 SVG，清单里其余图标都有文件；脚本检查每个 SVG 的 viewBox 为 0 0 24 24、stroke-width 为 1.75；清单覆盖三端现用的全部图标名；splash/README 写明图形文件和浅深两个底色令牌；sync-brand --check PASS；kanban --check --local 无新增 WARN。

</details>

<details>
<summary><b>DSX-07</b> · P1 · 规划仓库设计文档一次清理：过期说法、清单状态、深色图片与标识、分享与海报文档同步</summary>

负责线：设计；依赖：无。

**范围**

按 ① 类变更直接改。

① 过期说法：

- app-icon/README 第 48 行；brand/index.html 页脚「首版采用浅色 UI」；

- tokens/README 第 71 行改为返利金额和标签用 color.rebate.*，第 64 行与列表卡标题 14/21 对齐；

- design/README 第 5 行「三端工程尚未创建」、第 13 项海报状态（PosterShare-v2、PosterInvite-v2 已定稿）、第 10 项暂写「SVG 源待导出（DSX-06）」；

- 03 §10.1 首段；docs/brand-integration.md 开头和 §4 改成现状（contracts/design-tokens.json、ui-tokens、三端 App 图标都已接入），表里加「服务端出图」消费端；

- 06 Q-E2。

② tokens/README 新增「深色下的图片与标识」一节：商品图不压暗不反色，容器描边用 border.subtle，平台官方图不改色，Logo 用反白版，海报按图片处理。logo/README 补「深色用反白版」。「各端消费」一节列出全部消费方和锁定位置，版本由 TOKENS-LAG 输出，不手写。

③ 分享和海报：

- 08 BR-INV-18 的形状改为只写 poster_url；

- 10 AC-S1-138 ⑥ 改为「没有收益或返利金额」，券后价、券额按 BR-PRICE-17 应该出现；

- 12:930 海报出图超时改为未覆盖；

- app-invite-share.md:39 改为指向 invite.poster.*；

- 06 Q-F5 加一问：邀请落地页在微信里显示 invite.reward.tip，是否触及微信外链规范，作为 BR-INV-24 ① 开启前的法务检查项。不改 D36。

④ 加过期短语检查（新脚本或并入 kanban --check）：「强制浅色」「不表示产品 MVP 启用深色」「首版采用浅色」「金额沿用墨棕或中性」「尚未创建」，带日期的历史条目和「由…取代」说明除外。

来源：g1-14、g5-23。

**验收**

过期短语检查在 origin/main 上 0 命中，故意加一句「MVP 强制浅色」会报；design/README 第 5、10、13 项和 06 Q-E2 与实际一致；tokens/README 有深色图片一节；规划/ 里 grep「poster{template_id」为 0；12 第 930 行不再是 [x]；sync-brand --check PASS；kanban --check --local 无新增 WARN。

</details>

<details>
<summary><b>DSX-08</b> · P1 · GUIDE v2 迁入规划仓库 design/guide/：令牌表由令牌源生成、去敏、收齐待同步改动</summary>

负责线：设计；依赖：COMP-SPEC、COMP-SPEC-2、DETAIL-V3-WB。

**范围**

存放位置定为规划仓库 design/guide/GUIDE.md（公开，走 PR）。原 couli-runs/design-hifi/GUIDE.md 去敏后迁入：第三方 App 的界面观察和竞品截图描述不进公开仓库，留在 couli-runs 的私有附录。迁入当天 couli-runs 原件改为一行指针（编排直接提交）。本单只改规划仓库：

① §2 令牌表改为由 design-tokens.json 生成（含深色值和 T1–T12、v0.5.1 平台标签色），加生成器 --check。

② 骨架底色只留一种，与 COMP-SPEC-2 一致（关闭 design-diffs.md:15），第 25 行 #F6F3ED 改为 #F2EEE6。

③ §3 改为只引组件规范：筛选项高与 chip 32 对齐；返利标签按定论只留一种；补空态、骨架、提示条的完整间距。

④ 收齐其他单留给 GUIDE 的改动：v3 定稿的 §6 详情主图改通栏 cover、§7.1 平台实底文字标签与四种颜色、§7.2 详情骨架与店铺块（DETAIL-V3-WB）；§6 的 #EFEAE2 改为 placeholder 令牌（DSX-118）；删掉「墨棕或 #A83B1F」两可写法，走势图细则指向 03 §10 图表节（DSX-04）；§4 图标改为指向 design/icons/README（DSX-06）。

⑤ 加 §8「深色」指向 tokens/README 新节；design/README 加 GUIDE 的位置和版本指针。

verify.py 拆到 DSX-123，claude.ai 设计系统拆到 DSX-124；三张空态画板的间距改稿随 W-33 一起做。

来源：g1-16、g4-15（GUIDE 部分）。

**验收**

① design/guide/GUIDE.md 在 origin/main，令牌表生成器 --check 无漂移；② GUIDE 里骨架底色只有一种说法，grep #EFEAE2、「墨棕或 #A83B1F」都为 0；③ §6、§7.1、§7.2 与 v3 定稿一致；④ 公开文件里没有第三方 App 的界面细节（按 BR-TEXT-13 与 CLAUDE.md 公开仓库约定自查）；⑤ design/README 有指针；⑥ kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-123</b> · P1 · 画板自检 verify.py v2：颜色与刻度读令牌、深色稿用 dark 值、可点尺寸与对比度、与基线比较</summary>

负责线：设计；依赖：DSX-08。

**范围**

从 DSX-08 ② 拆出。脚本放规划仓库 scripts/verify-boards.py（画板路径作参数传入，仓库里不放画板内容）：

- 颜色白名单改读令牌的 value 和 dark，*Dark 画板用 dark 值（WithdrawDark、OrdersDark 现在误报 15 / 36 条）；

- 跳过 SVG 和商品素材子树再判色；

- 字号、间距、圆角按令牌刻度检查，阴影只许用令牌，并配例外清单；

- 可点元素静态尺寸 ≥44；文字对比度正文 ≥4.5、大字和控件边界 ≥3；

- 结果和基线比较「无新增失败」，基线文件只记画板名和条目、不含画板内容；design/guide/GUIDE.md §5 列为出稿必跑。

来源：g4-15、g4-16（verify 部分）。

**验收**

对 WithdrawDark、OrdersDark 报 0 条令牌外颜色；对变异样例（非令牌色、15px、圆角 10、间距 7、按钮高 40）全部检出；基线入库；脚本有单测；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-124</b> · P1 · claude.ai「凑狸设计系统」处置：按 v0.4.0 以上令牌重发或标停用</summary>

负责线：设计；依赖：无。

**范围**

从 DSX-08 ③ 拆出。claude.ai「凑狸设计系统」停在 v0.2.0：先读已发布版本，再按 v0.4.0 及以上令牌和现行规则重发，或在 README 顶部标「已停用，以 couli 仓库 design/ 为准」。由编排自定，不问负责人；只改 claude.ai 上的设计系统，不改仓库。

来源：g1-16（设计系统部分）。

**验收**

claude.ai 设计系统 README 顶部写明版本 ≥0.4.0 或已停用，并指向规划仓库 design/；编排在 HANDOFF 记下处置结果。

</details>

<details>
<summary><b>DSX-09</b> · P1 · 视觉验收规范包：容差表、验收模板、三端并排对照与设计差异台账</summary>

负责线：设计（协同 iOS、安卓、鸿蒙、前端、质量）；依赖：无。

**范围**

规划仓库新增 docs/templates/visual-acceptance.md：

① 容差表：尺寸和间距 ±1pt / dp / vp；圆角、字号、字重、颜色必须命中令牌；换行和截断零容差；三端快照统一容差（如像素差 ≤0.5% 且感知精度 ≥0.98）。截图门禁口径只在本单写：03 §11（鸿蒙 ≤1%、H5 无阈值、后台「—」）、11 §4.1、03 §9.2「不断言像素」三处统一；写明鸿蒙和 H5 / 后台的像素比对尚未落地（由 DSX-86、DSX-50 承接），先只报告；视觉层门槛（快照全绿、没有未关闭的比对差异）写进 11 §4.1。

② 状态矩阵：浅 / 深 / 200% / 320 / 840（或 ≥600）、读屏顺序、命中区、动效与减弱动态。

③ compare 记录格式改为逐项打勾，并加图框尺寸、比例、圆角、描边的数值断言栏。

④ 视觉任务收尾要交三端并排对照图（同一 fixture、同宽、浅深两态），由编排抽查。

page-spec.md 加「视觉验收」「无障碍」两节。新建统一的设计差异台账，迁入 design-diffs.md 的 24 条和各 compare 里没关闭的差异；画板登记定稿前，该页条目必须已关闭。design/README 或 05 加「页面 × 端 × 是否对齐视觉定稿」矩阵。

来源：g4-13。

**验收**

visual-acceptance.md 含五节；page-spec.md 有「视觉验收」「无障碍」小节；差异台账每条有状态列，design-diffs.md 的 24 条全部迁入；03 §11、03 §9.2、11 §4.1 的截图门禁描述一致，03 §11 写明三端统一快照容差；矩阵表存在；kanban --check --local 无新增 WARN。

</details>

<details>
<summary><b>DSX-10</b> · P1 · 适配与无障碍规范 v2 定稿：视口、安全区、大字号让位、系统辅助设置、CAP-X-18、鸿蒙平板</summary>

负责线：设计（协同 鸿蒙、质量、前端）；依赖：无。

**范围**

把 adaptation-a11y-spec 出成 v2：

① §1、§2、§5、§10 里标「本轮补充，待确认 / 待商量」的条目逐条定，由 Jev 判断，不问负责人：最小设计宽 320、短视口 667、页边距 16、安全区与底部固定栏、状态组件在 200% 和窄屏下的让位顺序（先去插图、再压留白、按钮通栏）。已被 03 和令牌定下的行改为引用（超过 200%、平板与折叠屏、输入描边 border.active、协议行整句一个复选框）；删掉已被「手机锁定竖屏」取代的横屏行；把 03 §10.4 的大屏限宽和 200% 同步回来；§13 补登 10 张 v2 证据稿。规范部分公开到 design/specs/a11y.md（或在 03 §10.5 写明依据的版本和日期），公开部分写进 03 §10.4。§7–§9 的读屏条目不在本任务内。

② 03 §10.4 / §10.5 加「系统辅助设置」一行：减弱动态、粗体与字重放大（含鸿蒙关怀模式字重 1.25 倍）、增强对比、强制配色，写三端和 H5 的做法；改正 colors.md §4 的「H5 基础控件提供 forced-colors」（现在只在设计预览里有）。

③ 按 rebate-private docs-mirror aging-adaptation.md（10-05 取得）回写 09 CAP-X-18 和 03 §10.4 鸿蒙行的事实部分，状态改为「进行中」。超过 200% 的封顶口径只标「待负责人定」，由 DSX-133 承接；本任务按 200% 写。

④ 鸿蒙平板：01 §7.5 和 03 §10.4 的说法不一致，交 Jev 依 20261005 变更记录 §4 判定，再回写两处。

⑤ 抽查 09 其余「未开始」的能力项在 docs-mirror 里是否已有答案。

来源：g3-07、g4-17。

**验收**

规范 §1、§2、§5 里「本轮补充，待确认」「待商量」为 0，剩下的待确认各有 Jev 编号；03 §10.4 能 grep 到 320、667、让位顺序和「系统辅助设置」行；09 CAP-X-18 引用了 docs-mirror 路径和取得日期；colors.md §4 不再声称 H5 已有 forced-colors；01 §7.5 与 03 §10.4 鸿蒙平板口径一致；docs/changes 列出每条 Jev 选项和置信度；kanban --check --local 无新增 WARN。

</details>

<details>
<summary><b>DSX-11</b> · P1 · 03 新增「页面模板」节，规格模板加「0. 信息层级」，11 §2.6 状态更正</summary>

负责线：设计；依赖：无。

**范围**

① 03 §10 新增「页面模板」节（D10-643 P1 预告的「页面模板与 PageScaffold」）。写列表、详情、表单、结果、设置 5 类页面的区域划分（顶栏、可滚动内容列、吸顶区、底部固定操作栏、空态 / 出错 / 加载的位置）和适用页面清单。写明三端 PageScaffold 负责限宽、安全区、底部栏随键盘上移，Feature 模块不得自写骨架。

② docs/templates/page-spec.md 加「0. 信息层级」：主任务；390×844 和 320 宽首屏必须出现的区域；区域优先级和顺序；固定区；200% 字号时先换行或折叠的块。评审清单加「层级与规格一致」。

③ 11 §2.6 改正：模板已用于 69 份规格，写明试行结论。

来源：g3-04。

**验收**

03 有「页面模板」节，5 类页面各有区域表；page-spec.md 有「## 0. 信息层级」；11 里 grep「试行，尚未开始」为 0；kanban --check --local 无新增 WARN。

</details>

<details>
<summary><b>DSX-12</b> · P1 · 03 新增「交互规范」节：承载形式、返回、键盘、吸顶、手势、防连点、加载防闪、触感</summary>

负责线：设计；依赖：DSX-10。

**范围**

先由 Jev 判断适配约定 §3 键盘、§4 半屏与弹窗、§6 返回里的待确认条目，再在 03 新增「交互规范」节：

① 承载形式怎么选：单一确认用 AlertDialog；带链接或长说明用 Dialog；补充说明和短表单用 Sheet；多步骤或需要返回栈用整页；几项去处用 ActionMenu。

② 返回：系统返回先关最上层的半屏或弹窗；有未保存输入的表单页离开时统一处理；分享页按 06 L395 例外。

③ 点遮罩和下滑关闭：普通弹层可关，资金和验证类不可关。

④ 键盘避让，底部按钮栏贴着键盘。

⑤ App 吸顶（搜索页平台 Tab 和排序行、订单状态行），导航栏滚动后的样子（surface 底加下分隔线）。

⑥ 手势清单：每个手势写可见的替代入口和读屏自定义操作。长按举报补可见入口，并给 Agent 结果卡补稿、过 Codex 审查；后台拖动排序必须有上移、下移按钮。

⑦ 防连点：500ms 内只响应一次，导航进行中忽略点击。加载防闪：300ms 内完成不显示，显示后至少停留 400–500ms，按钮内加载除外。

⑧ 触感：MVP 只用系统控件自带的触感。

来源：g3-08。

**验收**

03 有「交互规范」节，①–⑧ 各有条文；适配约定 §3、§4、§6 的待确认为 0 或写明去向；Agent 举报入口补稿登记 sha256 并通过 Codex 审查；kanban --check --local 无新增 WARN。

</details>

<details>
<summary><b>DSX-13</b> · P1 · 03 新增「动效规范」节：转场目录、自绘组件出入场、减弱动态、轮播与公告节奏</summary>

负责线：设计；依赖：DSX-03、COMP-SPEC-2、DSX-26。

**范围**

03 新增「动效规范」节（D10-643 P1 预告的「动效令牌」）：

① 什么时候动，以及禁止项。

② 转场目录：iOS 和鸿蒙用系统推入；安卓在 NavHost 显式配置（共享轴或滑入，时长取 motion 令牌）；模态从底部进入；Tab 切换无动画。

③ 自绘组件的出入场：Toast、Skeleton、Banner、NoticeBar、折叠行、选中态、顶部标签指示条；金额变化默认不动。

④ 全局减弱动态：开启时轮播和滚动公告停止自动播放、改为手动；位移和缩放改为淡入或无动画；Lottie 用兜底图；骨架屏静止。写三端读取入口；鸿蒙的接口在 09 登记为 CAP 待验证，未验证前不写成能力。

⑤ 轮播与公告：取值只在 DSX-26 写进 03 §6.3（公告间隔、autoplay_ms 合法范围、暂停条件）和 04（notice_bar 字段形状），本节只写切换动画并引用 03 §6.3，不复述数值。

⑥ iOS 首页弹窗无转场或淡入，焦点回位放在呈现完成回调里。

⑦ design/README 加「交互与动效规范」交付项，有动效的组件在目录页录屏。

来源：g3-09。

**验收**

03 有「动效规范」节，轮播与公告只引用 03 §6.3、不复述数值；09 有鸿蒙减弱动态的 CAP 条目，状态为待验证；design/README 清单多一行；kanban --check --local 无新增 WARN。

</details>

<details>
<summary><b>DSX-14</b> · P1 · 10 视觉验收用例：品牌一致、关键页与定稿一致、通用状态、二级页顶栏、动效，05 QA-11 / QA-12 补验收列</summary>

负责线：设计（协同 质量）；依赖：DSX-06、DSX-09、DSX-13、UI-STATES；承接：与 05 QA-11、QA-12 相关（原行补验收列）。

**范围**

按 00 §8 第①类直接改：

① 截图容差和门禁口径只在 DSX-09 写，本单引用。

② 03 §10.5 的设计审查通过口径改用 S0–S3；新增 docs/templates/design-review-prompt.md。

③ 10 新增以下用例，编号接在 AC-S1-185 之后：

- 三端品牌一致（主屏图标默认 / 深色 / 着色、启动页浅深、底栏和宫格图标、Logo 浅深，逐项与设计源比对，三端各一张品牌页快照）；

- 7 个关键页 × 三端 × 浅深两态与定稿一致（按 DSX-09 容差）；

- 通用状态三端 + H5 一致；

- 二级页顶栏三端一致；

- QA-11 的字号、方向、大屏用例（补 20261005 变更记录 §4 的遗留）。

④ 05 QA-11 截图清单加通用状态在 200% 和 320 宽下的样子；QA-12 加 WCAG 2.2.2、2.3.1、2.5.7、减弱动态、逐组件按下反馈、转场帧率抽检（05 原行补验收列，不另立任务、不给原行加前置依赖）。rebate-platform ops/tasks 的按端立项归 DSX-139。

⑤ 新 AC 和 AC-S1-185 是否计入内测出门，由编排用 Jev 判定，回写 05 §0 和 10 §2.11，变更记录注明置信度。不改 S1 出门范围本身；要计入出门须另写影响评估。

鸿蒙关怀模式封顶由 DSX-133 定，本单只按 200% 写。

来源：g1-15、g4-14、g3-18。

**验收**

03 §10.5 中「P0 / P1 / P2」为 0，design-review-prompt.md 存在；10 有上述新 AC 编号，并写明是否计入出门；05 QA-11 / QA-12 行的验收列含新增项；截图门禁只引用 DSX-09 写的 03 §11；docs/changes 记录 Jev 置信度；kanban --check --local 无新增 WARN。

</details>

<details>
<summary><b>DSX-15</b> · P1 · 7 个关键页规格补信息层级，重出大字号适配证据稿，钱包规格对齐画板</summary>

负责线：设计；依赖：DSX-11、DSX-10。

**范围**

首页、商品详情、订单列表与详情、钱包、我的、提现、AI 助手空态这几份规格，按 DSX-11 的第 0 节补信息层级。来源：design/key-page-wireframes 分支的 7 页线框、01 §4.2、interaction-patterns、GUIDE §7.2。app-wallet.md 的区域表按定稿 WalletRiskFrozen-v2 改为「冻结中、已提现在狸橙主卡内」。按 DSX-10 的 200% 让位规则，重出落后于定稿的大字号适配证据稿（AdaptLargeTextWallet、AdaptLargeTextOrderDetail 等），并过 Codex 对抗审查。

来源：g3-05。

**验收**

上述规格都有「## 0. 信息层级」；app-wallet.md 与 WalletRiskFrozen-v2 一致；重出的证据稿已登记 sha256，并有 Codex 审查通过记录；DSX-21 的规格检查对这些规格不报错。

</details>

<details>
<summary><b>W-33</b> · P1 · 已定稿画板按组件规范收口（改稿与普查表）：筛选胶囊、44001 弹窗主次、通用错误态、弹窗标题对齐、勾选框、二次验证格子</summary>

负责线：设计；依赖：COMP-SPEC、COMP-SPEC-2、DSX-08、DSX-118；承接：W-33（docs/changes/20261021-App内高保真第3批定稿.md 跨批同步项）。

**范围**

按组件规范普查 design/README 第 15 项登记的已定稿 App 画板，逐项改稿或登记例外：

① FilterChip：改齐 Search-v2、SearchEmpty-v2、Orders-v2、OrdersShare-v2、RankList-v2、Earnings-v2。

② 44001 拦截弹窗只定一种主次（建议能补救的【联系客服申诉】为主，与 30153 一致）。改 WithdrawBlocked、PayoutAccountBlocked、PhoneChangeNewBlocked-v2、LoginCodeBlocked-v2，写进 Dialog 行，删掉规格里的「待上游」。二次验证格子 52/12 和 56/10 统一。

③ SearchError、RankListError、WebPageError 按 StateLoadFailed 的层级改稿，或登记为页内变体。

④ 弹窗标题对齐（现在居中 23 张、靠左 18 张）、勾选框（ProductShare-v2 等 11 张是方块，另两张是圆形）、弹窗元素间距（16 对 12）、验证码格圆角。

⑤ 顺带改：Orders-v2 等画板去掉「商品图」占位字（按 DSX-118）；MessagesEmpty、OrdersEmpty、LedgerEmpty 主列 gap 12 改为 16 + 4（原 DSX-08）。GUIDE §3 只引组件规范的写法以 DSX-08 迁移后的 design/guide 为准。组件级 verify 检查拆到 DSX-125。

⑥ 补完 20261021 回写记录「交编排」里第 1、2 批 #7–#13 的 GUIDE 和清单回写。

⑦ 各批 gen-*.py 和 lib.py 的公共片段收成一份带组件名标记的生成函数库（生成脚本含画板内容，留在 couli-runs）。

改过的画板重新登记 sha256，过 Codex 对抗审查；在第 3 批定稿变更记录里关闭 W-33。

来源：g3-10、g2-07。

**验收**

上述画板（含 Orders-v2 和三张空态稿）在 design/README 有新 sha256；相关规格 grep「待上游」为 0；普查表（画板 × 组件 × 裁定）已落盘，例外清单供 DSX-125 使用；Orders-v2 里「商品图&lt;/div>」为 0；#7–#13 标为完成；W-33 已关闭；Codex 审查无 P0–P2。

</details>

<details>
<summary><b>DSX-125</b> · P1 · 画板组件级检查：标题对齐、勾选框形状、圆角与间距只许令牌或已登记例外（W-33 ⑤ 拆出）</summary>

负责线：设计；依赖：DSX-123、W-33；承接：W-33（拆分）。

**范围**

在 DSX-123 的 scripts/verify-boards.py 上加组件级检查：弹窗标题对齐、勾选框形状、圆角和间距只许用令牌或 W-33 普查表登记的例外；结果与基线比较，只减不增。

来源：g3-10（verify 部分）。

**验收**

verify-boards.py 对全部已定稿画板 0 违规，或只命中已登记的例外；对变异样例（方块勾选框、居中与靠左混用、非令牌圆角）检出；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-16</b> · P1 · 二级页不显示底栏的规则，补「搜索」Tab 底栏稿</summary>

负责线：设计；依赖：无。

**范围**

03 §4.4 写明二级页一律不显示底部 Tab 栏，例外逐个列出；改掉 Search-v2、SearchEmpty-v2 等带底栏的二级页画板。为 agent.entry.visible=false 的情况出「首页 / 搜索 / 订单 / 我的」底栏稿，写清「搜索」Tab 是打开 Search 路由的入口（与安卓 TabShell 一致），还是 Tab 根页面。不等 W-33：本单和 W-33 ① 都改 Search-v2 / SearchEmpty-v2 时，后合的一单在前一单基础上改并重新登记 sha256，能同批就同批出。同步 app-search.md 和 app-home.md，撤掉 APP-06x brief Q15 的「底栏不对照」例外；过 Codex 对抗审查。

来源：g3-11。

**验收**

03 有这条规则；新底栏稿和改过的 Search 组画板已登记 sha256；脚本扫描非 Tab 根路由的画板，都不含 TabBar 部件；Codex 审查通过。

</details>

<details>
<summary><b>DSX-17</b> · P1 · 以 routes.json 为主键建页面导航总表，加规格路由行检查，改正 flow-map</summary>

负责线：设计；依赖：无。

**范围**

① 新增页面导航总表：以 contracts/routes.json 的 51 条路由为主键，列入口、出口、返回目标、是否显示底栏、深链 / 推送是否可达、对应规格、定稿画板。

② 加检查（并入 kanban --check 或独立脚本）：每条路由都有规格和至少一张已登记画板；规格的路由行只写 routes.json 里的路由名，画板名移到第 1 节。

③ 改掉过时的行：app-withdraw-reverify.md L5、app-favorites.md L56，以及 settings、basic-mode、force-update、invite-backfill 四份规格里把画板名当路由名的地方；interaction-patterns.md L74「不新增：收藏」按 01 现行范围改。

④ flow-map 只记跨页流程：改掉与 01 矛盾的三处（L11、L472、L210），补上 AgentConsent、About、Reverify、DataCopy、InviteLink、Launch 的入口行。

来源：g3-12。

**验收**

检查脚本退出码 0，剩下的缺口只有 DSX-18 / DSX-19 / DSX-34 / DSX-95 / DSX-96 已登记的页面；design/specs 里 grep「没有这一页」「尚无 `Favorites`」为 0；flow-map 的三处矛盾已改。

</details>

<details>
<summary><b>DSX-18</b> · P1 · 登录 v2 定稿登记与 app-login 规格</summary>

负责线：设计；依赖：无。

**范围**

review-login/v2（r6，33 张）的 README 仍写「待负责人定：是否定稿」。按新稿统一口径处理：Codex 对抗审查无可见缺陷即通过，由编排核对后自行登记 sha256，登记后在给负责人的汇报里列一行（事后报告，不阻塞）；读屏属性问题转开发验收。审查有可见缺陷就先改稿再登记。登记后按 page-spec 模板（含第 0 节和通用状态三行）写 design/specs/app-login.md，解开安卓 APP-17b 的设计闸门。三端登录页的组件替换（DSX-55、APP-17-android、DSX-78）不等这个闸门。

来源：g3-13。

**验收**

design/README 有登录批次的 sha256 表；design/specs/app-login.md 已有，并通过 DSX-17、DSX-21 的检查；APP-17b 闸门标为已解。

</details>

<details>
<summary><b>DSX-19</b> · P1 · 补 DataCopy 页画板与规格</summary>

负责线：设计；依赖：DSX-11。

**范围**

DataCopy（01 L171，M-内测，10-22 新增）现在没有画板。补画板：列表、无可下载副本、加载失败 / 断网，以及封禁和注销冷静期下也可用的状态；写 design/specs/app-data-copy.md。新稿过 Codex 对抗审查。站外邀请落地页的部分归 DSX-34。

定稿口径（与 DSX-18 统一）：Codex 对抗审查无可见缺陷即通过，编排登记 sha256，登记后在给负责人的汇报里列一行（事后报告，不阻塞）。

来源：g3-14（DataCopy 部分）。

**验收**

DataCopy 新稿在 design/README 有 sha256；规格已有，并通过 DSX-17 检查；Codex 审查通过。

</details>

<details>
<summary><b>DSX-20</b> · P1 · 08 BR-TEXT-14 表 A 加「呈现」列</summary>

负责线：设计；依赖：UI-STATES。

**范围**

表 A 每个码加「呈现」列，取值只能是 page_state / inline_bar / field / toast / dialog / sheet / route / silent，按首屏加载、翻页加载、提交三种场景给默认值，取代「动作」列里的自由写法。用词与 UI-STATES 的组件 kind 一致。

来源：g3-16。

**验收**

表 A 每行都有呈现值，脚本检查没有空格、没有表外取值；kanban --check --local 无新增 WARN。

</details>

<details>
<summary><b>DSX-21</b> · P1 · 规格补加载 / 加载失败 / 断网三行，加规格检查脚本，设计自检查状态覆盖</summary>

负责线：设计；依赖：UI-STATES。

**范围**

App 规格第 1 节固定写三行：加载中、加载失败（无缓存）、断网。每行引用状态目录编号，或写「不适用」加原因。先补这 10 份：app-order-list、app-wallet（去掉「不适用（无画板）」）、app-order-detail、app-product-detail、app-withdraw、app-withdraw-records、app-payout-account、app-risk-notice、app-appeal、app-delete-account。商品失效按钮等缺的键（iOS TODO(N-27)）回写 BR-TEXT-14 表 C。加规格检查：读接口的页面缺这三行就报错。verify.py 和 check-samples.py 增加「每页都有加载 / 失败 / 断网稿，或引用通用状态稿」的检查。

来源：g3-17。

**验收**

规格检查脚本对全部 App 规格退出码 0；上述 10 份规格都有这三行；表 C 有商品失效按钮的键；设计自检对缺状态稿的页面报错。

</details>

<details>
<summary><b>DSX-22</b> · P1 · 商品卡变体唯一名单（进组件规范）、AI 商品卡布局口径</summary>

负责线：设计（协同 iOS、安卓、鸿蒙）；依赖：COMP-SPEC、DSX-119、DSX-08。

**范围**

商品卡变体的唯一名单（列表卡、首页网格卡、首页横滑卡、信息流卡、详情头、分享摘要卡）写进 design/components 规范和 component-spec.json，03 §10.2 只放指向规范的一行，design/guide/GUIDE.md 和各规格统一引用。03 §7.4 删掉契约和画板都没有的「≤3 张时纵向大卡」。AI product_list 的 grid 二选一：出 grid 定稿，或者写明 MVP 只下发 list、客户端收到 grid 按 list 渲染。首页横滑卡的平台标签改稿拆到 DSX-126（v3 合派前完成），三端随 v3 合派（D10-641）落地。

来源：g3-19。

**验收**

design/components 规范和 component-spec.json 有变体名单，03 §10.2 只有指针；03 §7.4 grep「大卡」为 0；AI grid 有定稿，或有「MVP 只用 list」的条文；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-23</b> · P1 · 三端页面私有件收编表</summary>

负责线：设计（协同 iOS、安卓、鸿蒙）；依赖：COMP-SPEC。

**范围**

按页面模块普查三端主干里名字带 Button / Row / Bar / Strip / Pill / Chip / Field / Card / Switch / Divider / Spinner 的私有件：iOS 约 60 个；安卓有 LoginScreen 的 BrandMark / PhoneField / CheckMark / TextLink、BindPhoneField、SearchFilterCapsule、MeSwitch、StatusPill、InfoStrip 等；鸿蒙有 MeSwitchRow、SearchChip、OrderStatusChip、MeSheetPanel、TradeOverlay 面板等。逐项裁定「换组件库 / 扩组件库参数 / 保留并写理由」，并指到迁移任务键或 DS-03；与组件库同名的私有函数单列。表放在 couli-runs/design-hifi/components/adoption.md（私有），附生成命令。

来源：g2-06。

**验收**

表的行数与附带命令在三端当时主干上的命中数一致；每行都有裁定和目标任务键，未指派为 0；DS-03 周检引用这张表里未清项的计数。

</details>

<details>
<summary><b>DSX-24</b> · P1 · 看板加「组件库差异」上限告警，以及同一画板的三端落地状态</summary>

负责线：设计；依赖：DS-03。

**范围**

scripts/kanban.py 加两项：① 统计 DS-03 里开放的「组件库差异」，超过 11 规定的上限时出 WARN；② 每张已定稿画板显示 iOS / 安卓 / 鸿蒙的落地状态（读 design/README 定稿登记、三端台账、couli-runs 在途状态），标出没跟进的端；③ 读 couli-runs 在途的页面任务书，缺「依据摘录」抽数表（DS-03 ②）的出 NOTE。

来源：g2-08。

**验收**

kanban --check --local 无 WARN；本地造一个超上限的样例能触发 WARN；看板上能按画板看到三端落地列；缺抽数表的在途任务书会出 NOTE。

</details>

<details>
<summary><b>DSX-25</b> · P1 · App 内 Web 容器规范：主题和字号传递、标题来源、反色标题栏、setNavBar 色值</summary>

负责线：设计（协同 后端、iOS、安卓、鸿蒙、前端）；依赖：DSX-03。

**范围**

改 03 §5、§8.1、§8.3、§10.4，定一种三端相同的做法：

① 主题：宿主在 document start 写入 html 的 data-theme；app.getEnv 增加 color_scheme，并新增主题变化事件。容器配置写进规范：鸿蒙 darkMode(WebDarkMode.Auto)，安卓夜间用 isLightTheme=false 的主题，iOS 随 DS-02-iOS 解锁。同步改正 brand-integration.md L98。

② 字号：app.getEnv 增加 font_scale 和变化事件，H5 用根字号 CSS 变量放大到 200%，容器不再叠加系统缩放（只放大一次）。03 §10.4 去掉「做法由 APP-04、HM-03 定」。

③ 标题：H5 外壳按路由调用 ui.setNavBar；收到标题之前不显示 URL；document.title 只在非空且不是 URL 时作为回退。

④ nav_style=dark 用 component.navbar.inverse.*，组件里不按主题分支取色，写进 app-external-page.md。

⑤ ui.setNavBar 的色值参数改为令牌名枚举或浅深成对（契约改动在 CT-03-navbar）。

来源：g4-19。

**验收**

03 §8.1 与 brand-integration.md 的主题机制是同一种说法；03 §10.4 的 H5 行不再写「做法由 APP-04、HM-03 定」；app-external-page.md 写明两态配色和对比度要求；03 §8.3 有「不得显示 URL」；kanban --check --local 无新增 WARN。

</details>

<details>
<summary><b>DSX-26</b> · P1 · 首页 SDUI 规则补齐：开放 props 键名、卡片版本规则、视觉参数白名单</summary>

负责线：设计（协同 后端、iOS、安卓、鸿蒙、前端）；依赖：无。

**范围**

改 03 §6、§6.3：

① home-schema.json L3 声明「stay open」的 5 处（icon_grid、product_scroll、activity_entry、notice_bar 展示方式、popup 关闭按钮）写定键名、必填与否和取值，以三端现有写法为起点，icon 和 image 二选一统一。banner 的 height_ratio、autoplay_ms 定为必填或可选；icon_grid 的 rows 截不截断定一种。

② 卡片版本规则：只加可选键不升版，改含义或改必填才升版；契约给每个 type 登记支持版本和各端起始版本。

③ 视觉参数白名单：height_ratio 的取值集合；feed_infinite 每页最多 1 个且放在最后；三端统一夹取规则。

④ 轮播与公告的数值只在本单写一处：03 §6.3 写 banner autoplay_ms 的合法范围（0 或 3000–8000，满足 WCAG 2.2.2）、公告滚动间隔和切换方式、暂停条件（减弱动态、读屏、页面不可见时停止自动播放）；04 写 notice_bar 的 mode（scroll / static）和间隔字段形状。DSX-13 的动效规范和三端动效单都引用这里。

完成后通知 be 关闭 N-35 第①条。

来源：g4-20。

**验收**

03 §6.3 每个 type 的 props 都是确定键名并标了必填；有「卡片版本」小节；白名单有具体数值；03 §6.3 有 autoplay_ms 合法范围、公告间隔和暂停条件，04 有 notice_bar 的 mode 和间隔字段；附对照表，把 APP-11/rule-gaps.md 的相关条目逐条指到新条文。

</details>

<details>
<summary><b>DSX-27</b> · P1 · 首页 SDUI 规格与验收补齐：首页规格同步、后台首页配置规格、AC-HOME、流程图</summary>

负责线：设计（协同 前端、质量）；依赖：DSX-26。

**范围**

① app-home.md 按契约同步（L53、L57 的 popup 替代文字和 section_popup 已经有了）。

② 新增 design/specs/admin-home-config.md：区块拖拽排序、由 schema 生成的属性表单、近似预览、草稿二维码（couli://r/HomePreview?page_key=…&token=…）、popup 的两个上传位。4 张与上线页面不一致的 AdmHomeConfig 旧画板重画或标作废。

③ 10 补 AC-HOME 用例：三级兜底、单卡隔离、未知 type、按端门槛、灰度、回滚、三端 golden 一致。

④ 12 补发布 / 灰度 / 回滚流程图和客户端兜底状态图。

⑤ 03 §13 写明 P1 CustomPage 的 H5 渲染器复用同一套 schema、令牌和卡片组件，并兼作后台近似预览；CustomPage 上线前，后台只编辑 home。

来源：g4-21。

**验收**

app-home.md 里「section_popup 还没有」「暂无替代文字字段」为 0；admin-home-config.md 已有并登记了画板 sha256；10 有 AC-HOME 行；12 有新图并登记到 12 §9；kanban --check --local 无新增 WARN。

</details>

<details>
<summary><b>DSX-28</b> · P1 · 后台内容 CMS 与商品池页面规格</summary>

负责线：设计（协同 前端）；依赖：无。

**范围**

按 11 §2.6 页面规格模板，依据已有画板 AdmContent*、AdmAgreement*、AdmPool*，写两份规格：

- design/specs/admin-content.md：帮助、规则、公告、协议的列表、编辑、发布；Tiptap 节点白名单与 H5 static-renderer 一致；保存时过 BR-TEXT-13 硬拦和 JEV-05 标黄。

- design/specs/admin-pools.md：池列表、入库、标签、上下架，权限为 content.pool。

两份都登记画板 sha256。

来源：g4-22。

**验收**

两份规格已有，并登记了 sha256；引用的接口都在契约里，缺的列入「待定与不一致」；kanban --check --local 无新增 WARN。

</details>

<details>
<summary><b>DSX-29</b> · P1 · M-内测页面规格补「无障碍」小节</summary>

负责线：设计（协同 质量）；依赖：DSX-09。

**范围**

按 DSX-09 的 page-spec「无障碍」小节，先补这些页面：app-withdraw、app-withdraw-records、app-product-buy、app-payout-account、app-real-name、app-settings、app-rules、app-link-landing，以及 6 份资金类后台规格。每份写读屏顺序、图标按钮名称、200% 放不下时怎么排、播报点。分享、收藏、热销榜等 M-公开页随后补。

来源：g4-23。

**验收**

上述规格各有「无障碍」小节，内容不止一句指针；QA-12 清单逐页引用这些小节。

</details>

<details>
<summary><b>DSX-30</b> · P1 · 08 BR-TEXT-14 增「读屏与播报」一节</summary>

负责线：设计（协同 后端）；依赖：无。

**范围**

08 BR-TEXT-14 增加读屏与播报专节：

- 通用图标按钮名称键：a11y.back、a11y.close、a11y.clear、a11y.loading、a11y.unread 等，写明与 web_page.back、external_page.close 的关系；

- 适配规范 §10 草拟的播报句（现在标「待商量」）。

取值只在 08 维护，不与 UI-STATES 的 state.* 键重复。

来源：g4-24。

**验收**

08 有该节，键名清单完整；草拟的播报句全部有键，适配规范 §10 不再标「待商量」；提交说明写明 00 §8 类别。

</details>

<details>
<summary><b>DSX-31</b> · P1 · 图片管线定案写进 03：选型、缓存与解码上限、请求策略、首屏预取、清除缓存口径</summary>

负责线：设计；依赖：无。

**范围**

① 03 §3.3「图片」一行（Kingfisher / Coil 3 / ImageKnife）和代码脱节。二选一写定：改回基线库；或保留自写，另写一份新 ADR 取代这一行，并改 docs/research/20261007:47。这是技术选择，由编排自定。

② 03 §12 写明数值：内存缓存按字节算（如可用内存的 1/8），磁盘缓存上限 100–200MB（按中端参考机实测调整），LRU 淘汰；解码尺寸 = 显示尺寸 × 屏幕密度。

③ 03 §4.2 加「图片请求」：超时、重定向只许跳到 https、可接受的类型和大小上限、不带凭据，以安卓现在的 15 秒、image 类型、5MB 为起点。

④ 03 §6.2 第 5 步保留首屏预取，通过统一加载器的预取接口实现。

⑤ app-settings.md:19 改为「清除后重新计算、照实显示」，缓存大小 = 图片磁盘缓存 + WebView 缓存。

来源：g5-04。

**验收**

一个 PR 改完 03 §3.3、§4.2、§6.2、§12 和 app-settings.md；如果选自写，docs/adr/ 有新 ADR 且 03 指向它；grep「上限数值接入图片库时按设备存储实测后定」和「清除后该行为 0 KB」都为 0；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-32</b> · P1 · 用 staging 真实主图复核 ImageStress，定长图、低清、白底三条规则的去留</summary>

负责线：设计；依赖：无。

**范围**

从 staging 搜索卡的真实主图（淘宝 pict_url / small_images、拼多多 goods_image_url / goods_gallery_urls）里，挑竖图、长图、白底图、场景图、低清图各若干张，放进 ImageStress，按列表、网格、横滑、详情、分享页头图、海报主图六种图框重新渲染。据此裁定 GUIDE §6:176 长图顶部对齐、§6:178 低清 2 倍封顶、§6:179 白底 1:1 优先（服务端是否读 white_image）这三条规则，结论回写 ProductImage 条目；保留的规则立实现单（客户端判断需要 DSX-104 提供的宽高）。真实商品图只放在私有的 couli-runs。

来源：g5-11。

**验收**

couli-runs 里有复核页和 1 倍 PNG，注明图源和原图尺寸；ProductImage 条目里三条规则各有结论；保留的规则有实现单编号。

</details>

<details>
<summary><b>DSX-33</b> · P1 · 运营上传图规格：banner、活动卡、静态弹窗图的尺寸、比例、体积、格式和 https</summary>

负责线：设计；依赖：无。

**范围**

在 08 写清 banner、活动卡、弹窗静态兜底图的建议尺寸、允许的宽高比范围（对应 height_ratio）、体积上限、格式（JPEG / PNG / WebP），以及必须是 https。写在 BR-TEXT-26 弹窗素材细则那一处，或新编号。01 F-ADM-09 和 AdmMediaLibrary 画板里的「图片规格未定」改为指向这一条。

来源：g5-15。

**验收**

08 有这条细则，并被 F-ADM-09 引用；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-34</b> · P1 · 邀请落地页 v2 定稿与规格，定站外品牌头，补邀请页「海报暂不可用」态</summary>

负责线：设计（协同 前端）；依赖：无。

**范围**

InviteLanding* 草稿出 v2 并定稿。品牌头统一用 design/logo 的横版 Logo，不许用 App 图标或文字方块代替；写成通用的「站外品牌头」规格，分享中间页、下载引导页和海报都沿用。

按模板写 design/specs/h5-invite-landing.md：有效码、无效码、已注册、成功几种状态，微信内和普通浏览器两种环境，深色按令牌推导，只用 H5 基础组件和令牌，首屏 JS ≤60KB（gzip）。告知句的位置按 BR-INV-16、F-INV-06。&lt;title>、抬头、按钮、成功页的文案键登记到 BR-TEXT-14 表 C。

InviteShare 补一张「海报暂不可用」说明态画板和对应的键。微信卡片 MVP 只靠页面标题，不承诺自定义卡片。站外邀请落地页补进 design/README 的定稿登记。新稿过 Codex 对抗审查后再登记 sha256。

定稿口径（与 DSX-18 统一）：Codex 对抗审查无可见缺陷即通过，编排登记 sha256，登记后在给负责人的汇报里列一行（事后报告，不阻塞）。

来源：g5-18、g3-14（InviteLanding 部分）、g4-74（邀请落地页部分）。

**验收**

h5-invite-landing.md 已有；design/README 有 InviteLanding-v2* 和 InviteShare「海报暂不可用」态的 sha256；08 表 C 有相关的键；F1-05 任务书引用这份规格；Codex 审查无 P0–P2；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-35</b> · P1 · 商店截图模板与上架素材视觉标准（W7 提审用）</summary>

负责线：设计；依赖：无；状态（2026-11-05）：等负责人（06 Q-A13）。

**范围**

design/store 的三个目录现在只有 .gitkeep，design/README 第 14 项还是「11-22 前待办」。出截图模板画板 6–8 屏（iOS 1320×2868，安卓和鸿蒙 1080×1920），标题条取令牌、以浅色为主；列出要截哪些页（首页、搜索、详情、订单、钱包、AI 等，另加首启隐私弹窗）。只用样例数据，金额一律带「预估」和口径句，不写收益承诺（避开 06 Q-G20 的网赚类判定）。三端各写一份 description.md，过 BR-TEXT-13、20 扫描。截图里的平台标识（淘宝、京东、拼多多 logo）口径等负责人定（D10-643 的待定项）；定之前平台位只写文字来源占位，其余先做。

来源：g5-22。

**验收**

三个目录都有模板 PNG 和 description.md，description 用 banned-words.yaml 扫描 0 命中；design/README 第 14 项写明验收要点；负责人答复后，平台标识口径回写 store/README。

</details>

<details>
<summary><b>DSX-36</b> · P1 · 安卓通知小图标素材（单色剪影），各推送通道图标要求登记待核</summary>

负责线：设计；依赖：无。

**范围**

design/icons 下新增 notification/：从 logo-mark-mono 派生一个 24dp 单色透明底剪影（不能直接用自适应图标的单色层），出 SVG 和各密度 PNG，强调色定为 color.brand.primary；icons/README 加上这一类。华为、小米、OPPO、vivo、荣耀通道和鸿蒙对通知图标、大图的要求，登记为 09 CAP-X-05 的待核项，不写成承诺。

来源：g5-24。

**验收**

notification/ 下有 SVG、PNG 和 README；icons/README 列了这一类；09 CAP-X-05 有待核条目；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-37</b> · P1 · 价格走势图形与文案规则：日期横轴、阶梯线、缺失日断开、刻度、跨年、末点标注、失败态、文本键</summary>

负责线：设计；依赖：DSX-04、UI-STATES、DSX-08。

**范围**

写进组件规范的 PriceTrendPanel 条目；规范还没落地时，先写在 app-product-detail.md 的「价格走势图形规则」一节。

- 横轴按日期，固定 30 天；画阶梯线；缺失日断开，不延续上一个值。

- 纵轴设最小跨度和留白，刻度取 1 / 2 / 5 × 10^n，3–5 档。

- 跨年时日期写 YYYY-MM-DD，或首尾刻度带年份。

- 末点标注写「最近记录 ¥x」；和详情报价不一致时，图上不写「当前」。

- 五种状态：折叠、加载中、暂无记录、请求失败、有记录。请求失败时在行内显示失败和【重试】，不显示旧数据，也不显示成「暂无记录」；失败和重试的文案复用 UI-STATES 的通用键。

- 来源行必须显示；摘要句的字号档统一。

08 表 C 登记 price_trend.summary、chart.a11y、empty.desc、source.line。统一 design/guide/GUIDE.md（DSX-08 迁移后）和 Empty 画板里的空态说明。清单 :161、:189 的「三端未实现」改为「安卓、鸿蒙已实现」。

来源：g5-36。

**验收**

规则条目里有几何参数表和 6 组示例（单点、缺失日、跨年、几毛钱的波动、四位数价格、报价与末点不一致）；08 表 C 有 4 个新键；GUIDE 和画板的空态文案一致；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-38</b> · P1 · 价格走势补稿：请求失败、加载中、展开深色、200% 字号，与 v3 骨架一致的暂无记录稿</summary>

负责线：设计；依赖：DSX-37。

**范围**

按详情 v3 的骨架补以下画板：ProductPriceTrendError、ProductPriceTrendLoading、ProductPriceTrendDark（展开态）、一张 200% 字号稿、ProductPriceTrendEmpty-v3（含拼多多和无券两种标题；现在的 Empty-v2 还写着「预估返后」「领券购买」）。新稿过 Codex 对抗审查，读屏属性方面的问题转给 QA-12。

来源：g5-37。

**验收**

5 张新画板和对应的 1 倍 PNG 已有；Codex 审查无 P0–P2；sha256 追加到 design/README「商品详情 v3 定稿」登记表。

</details>

<details>
<summary><b>DSX-39</b> · P1 · 资金看板口径与图表规则：指标定义、金额写法二选一、事件标注与区间上限，锁 G2 版本</summary>

负责线：设计；依赖：DSX-04。

**范围**

① 08 登记「资金看板指标口径」（放在 BR-WDR-18 或 BR-FUND-20 的细则里）：

- 待打款包含哪些状态，统一卡片和柱图的说法；按 net_fen 还是 amount_fen 计；日终在什么时刻取数；

- W 的日终值取最近一次录入并标 measured_at，过期的日子断线或置灰。

按 BR-TEXT-21 写成默认假设，决策人是财务，确认项登记到 06，不阻塞 F1-08g。BR-TEXT-21 的适用范围扩到汇总卡、图表系列和提示框。

② BR-TEXT-10 在两种写法里定一种：图表和表格统一加 ¥；或者单位写在轴标题或表头、数值不带 ¥、读屏读成「x 元」。AdmReportFunds 画板和适配规范 :257 跟着改。

③ admin-fund-dashboard.md 补充：关键事件由服务端给出；越线的日子改色或加标记点；区间不超过 90 天；超过 31 天时 aria-label 只读摘要；G2 键盘读值的实现说明。

④ 新开一份 ADR（docs/adr/，用 docs/templates/ 的模板）登记 @antv/g2 的版本线；ADR-0001 是锁定基线，原文不改。

来源：g5-43。

**验收**

08 有指标口径条目，06 有财务确认项；BR-TEXT-10 只剩一种写法；admin-fund-dashboard.md 写了事件、区间、读屏三条；新 ADR 有 G2 版本线，ADR-0001 未改动；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-130</b> · P1 · 09 CAP-JD-02 回写京东主图实测（外部阻塞：京东 goods.query 权限）</summary>

负责线：设计（协同 运维）；依赖：DSX-44。

**范围**

【外部阻塞】同 DSX-44。按 DSX-44 的 staging 实测记录回写规划仓库 09 CAP-JD-02（imageInfo 字段、多图张数、https 情况）；上线前仍拿不到图的，在 09 记一笔并写明京东卡显示「为空」态。只改规划仓库。

来源：g5-14（09 部分）。

**验收**

09 CAP-JD-02 有实测日期、样本数和字段结论，引用 evidence 路径；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-133</b> · P1 · 鸿蒙关怀模式字号封顶：取得负责人决定并回写 03 §10.4、09 CAP-X-18</summary>

负责线：设计（协同 鸿蒙）；依赖：DSX-10；承接：与 D10-643 待定项相关；状态（2026-11-05）：等负责人（06 Q-A12）。

**范围**

D10-643 待定项「鸿蒙关怀模式字号封顶」（A：fontSizeMaxScale 降到 2 或 1.75；B：正文跟随到 3.2 倍、密集控件 maxFontScale 封顶）。编排把两种选项和影响面一次列给负责人；决定后回写规划仓库 03 §10.4 鸿蒙行和 09 CAP-X-18（写明口径和决定日期），DSX-85 按此实施，DSX-91、DSX-139 按此补档。只改规划仓库。

来源：g4-50（决定与回写部分）。

**验收**

03 §10.4 鸿蒙行和 09 CAP-X-18 写明封顶口径和负责人决定日期；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-132</b> · P1 · 鸿蒙实测结果回写 09：ArkWeb 是否跟随系统字号、减弱动态读取接口</summary>

负责线：设计（协同 鸿蒙）；依赖：HM-03-web、DSX-83。

**范围**

只改规划仓库：按 HM-03-web 的测试记录回写 09 CAP-X-18（ArkWeb 是否跟随系统字号），按 DSX-83 的接口实测回写 09 对应 CAP（减弱动态 / 动画时长的读取接口）；未验证的不写成能力。

来源：g4-54、g3-61（09 回写部分）。

**验收**

09 两处 CAP 有实测日期、设备与结论，引用 PR 里的测试记录；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-92</b> · P2 · 建视觉参考板，公开参考说明补「外观风格」一节</summary>

负责线：设计；依赖：DSX-05。

**范围**

在 couli-runs 持久目录建「视觉参考板」：每个参考 2–3 张截图（从官方渠道重新观察），写外观层面的「学什么 / 不学什么」，补登第三轮的同类联盟工具。公开的 references/README 加「外观风格参考」一节，只写结论和私有位置指针，不写第三方界面细节。evidence-index.md 的证据路径改到持久目录。现有的反向约束保留。

来源：g1-26。

**验收**

参考板 README 和截图已有，每个参考都有「学什么 / 不学什么」；公开 README 有新节，且不含第三方界面细节；执行 `git grep -nF '/tmp/couli-reference-evidence' origin/main` 为 0。

</details>

<details>
<summary><b>DSX-93</b> · P2 · 准备 Slogan 候选交负责人选定，并回写品牌配置</summary>

负责线：设计；依赖：DSX-05；状态（2026-11-05）：等负责人（06 Q-E1）。

**范围**

Slogan 是负责人提供的品牌内容和对外文案，不交 Jev。设计线准备 2–3 个候选：过 BR-TEXT-13 禁用词检查，与 principles.md 的个性词一致，附商店副标题和海报上的示意，交负责人选。定下后回写 name.md、brand.config.json 的 identity.tagline、06 Q-E1、design/README 第 1 项。

来源：g1-27。

**验收**

name.md 和 tagline 非空；sync-brand --check PASS；06 Q-E1 和 design/README 第 1 项已更新，注明负责人选定日期；kanban --check --local 无新增 WARN。

</details>

<details>
<summary><b>DSX-94</b> · P2 · 后台设计规范与版式令牌：字阶、间距、页面模板、表格密度，admin.* 进唯一源</summary>

负责线：设计（协同 前端）；依赖：无。

**范围**

① 写 design/specs/admin-guidelines.md：字阶 12 / 14 / 16 / 20（28）；间距 4 / 8 / 16 / 24；列表、详情、抽屉、弹窗四种页面模板；表格密度。收拢 03 §9、GUIDE §6、decisions-admin-* 里散落的规则，只引用不复述 08，并作为 Web LINT-STYLE 白名单的依据。

② 把私有 DESIGN-hifi-admin.md「后台版式令牌」的数值加进 design-tokens.json 的 admin.* 分组：按钮高 36、输入框高、菜单项高、圆角 8 / 12、内容区内边距 24、侧栏 220、顶栏 56、表格行高 44 / 52、对话框宽 480 / 640、断点 1280。

③ 核实 theme.ts 的 Input 40、Menu 32 与画板的 36、28 哪个是有意的，统一回写画板或代码。

④ 写明后台按钮圆角 8 是后台例外；写变更记录。

来源：g1-28、g4-73。

**验收**

admin-guidelines.md 已有，并被 03 §9 引用；sync-brand --check PASS 且有 admin.* 分组；tokens/README 写明后台例外；docs/changes 记录 36 / 40、28 / 32 的定论；LINT-STYLE-web 的白名单与规范一致；kanban --check --local 无新增 WARN。

</details>

<details>
<summary><b>DSX-95</b> · P2 · 「请升级 App」提示页补稿与规格</summary>

负责线：设计；依赖：DSX-11。

**范围**

03 §4.4 写的「未知路由或 since 高于当前版本时打开『请升级 App』提示页」，补画板和规格，文案键登记到 BR-TEXT-14 表 C。新稿过 Codex 对抗审查。分享中间页和下载引导页的部分归 DSX-96。

定稿口径（与 DSX-18 统一）：Codex 对抗审查无可见缺陷即通过，编排登记 sha256，登记后在给负责人的汇报里列一行（事后报告，不阻塞）。

来源：g3-15（升级提示页部分）。

**验收**

提示页已登记 sha256，规格已有；08 表 C 有提示页的键；DSX-17 的检查不再报这一页。

</details>

<details>
<summary><b>DSX-96</b> · P2 · 分享中间页与下载引导页 v2 定稿和规格：去旧口径句、补京东拼多多购买按钮、换正式品牌头</summary>

负责线：设计（协同 前端）；依赖：DSX-34。

**范围**

SharePage、SharePageWechat、SharePageNotLaunched 三张去掉含「跨店满减」的旧口径句。按 12 §9.3 L-16，在中间页补京东、拼多多的购买按钮。DownloadGuide 的 96px 方块和 SharePage 的 32px 方块换成 DSX-34 定的站外品牌头。按模板写 h5-share-page.md 和 h5-download-guide.md：微信内和普通浏览器两种状态、深色按令牌推导、只用 H5 基础组件、首屏 JS ≤60KB。&lt;title> 和按钮的文案键登记到 08 表 C。SharePage*、DownloadGuide 补进 design/README 的定稿登记。过 Codex 审查后登记 sha256。实现归 DSX-138。

定稿口径（与 DSX-18 统一）：Codex 对抗审查无可见缺陷即通过，编排登记 sha256，登记后在给负责人的汇报里列一行（事后报告，不阻塞）。

来源：g5-29、g3-15（分享与下载页部分）、g4-74（分享与下载页部分）。

**验收**

两份规格已有；design/README 有 SharePage-v2* 和 DownloadGuide-v2 的 sha256；画板里 grep「跨店满减」为 0；08 表 C 有新键；DSX-138 任务书引用这两份规格；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-97</b> · P2 · 03 §4.2「断网显示缓存」按向量口径回写，§9.2 补后台等待上限</summary>

负责线：设计；依赖：无。

**范围**

03 §4.2 改为「只在网络失败且有缓存时显示旧数据，文案用 net.stale_data」，与 order-vectors G10 一致。03 §9.2 定管理后台 A 类写操作的等待上限，以及什么情况转为「结果未确认」，写进状态目录。

来源：g3-20。

**验收**

03 §4.2 不再写「请求失败时显示上次成功的数据并标注更新于」；03 §9.2 有秒数；kanban --check --local 无新增 WARN。

</details>

<details>
<summary><b>DSX-98</b> · P2 · 首页弹窗 Lottie：素材闪烁安全要求，三端播放器与后台上传入口同排</summary>

负责线：设计；依赖：无。

**范围**

08 BR-TEXT-26 的素材校验加闪烁安全要求（每秒闪烁不超过 3 次，不做大面积红闪），作为后台上传时的人工审核项或预览提示。05 把 APP-11 / HM-07 的 Lottie 子任务和后台上传入口上线绑成一组排期：三端播放器接入前，后台不开放上传入口。

来源：g3-21。

**验收**

BR-TEXT-26 有闪烁条文；05 有绑定排期的说明；三端播放器合并前，apps/admin 里 grep lottie 上传入口为 0。

</details>

<details>
<summary><b>DSX-99</b> · P2 · 状态色色觉辨识核对，关闭品牌评审遗留</summary>

负责线：设计（协同 质量）；依赖：无。

**范围**

在 scripts/ 写一个可以重跑的只读脚本：按 WCAG 相对亮度和 Machado 2009 色觉模拟（CIELAB ΔE76），计算返利、错误、成功、警告、待定这几种状态色两两之间的差异，浅深两套，结果写进 colors.md。ΔE&lt;3 的组合不改品牌色，靠组件的「图标形状 + 文字」区分。关闭品牌评审 claude-round-1.txt:48 和 claude-round-2.txt:67 两条遗留。

来源：g4-72。

**验收**

colors.md 有状态色色觉模拟表；两条遗留有关闭记录；脚本可以重跑，输出与表一致。

</details>

<details>
<summary><b>DSX-100</b> · P2 · 海报与分享素材规格：二维码、背景图、深色、格式与体积、截断与文案键、微信卡片、出图字体</summary>

负责线：设计；依赖：无。

**范围**

posters/README、app-product-share、app-invite-share 补以下内容：

① 二维码：纠错 M（叠在背景上时用 Q）；静区不少于 4 个模块；750 宽海报上边长不小于 192px；邀请海报带 ch=poster。

② 背景图：尺寸；安全区；文字对比度 ≥4.5；体积上限。内测按固定模板 + 包内默认背景；后台配置的时点由 Jev 判定，回写 BR-INV-18 和 F-ADM-09。

③ 深色：海报始终浅色，放在深色页面上时用 border.subtle 承载。

④ 格式：海报出 JPEG，不超过 500KB。04 §9 share.open 的 thumb 不超过 32KB、方形 JPEG，由原生压缩。卡片描述不含收益金额。

⑤ 截断：标题去掉开头的平台名、超过两行截断；昵称超宽省略。登记 share.poster.* 键。

⑥ 推广角标预留位（06 Q-F7）和 AI 隐式标识（BR-ID-15）。

⑦ 出图字体：随包带 Noto Sans SC / 思源黑体（OFL），字重 400 / 600 / 700，等宽数字，写明回退方式；tokens/README 加「服务端出图」消费端。

来源：g5-26。

**验收**

posters/README 有二维码、背景图、深色、格式与体积、字体五节；04 §9 写明 thumb 约束和压缩方；08 表 C 有 share.poster.*；海报一节写了角标位和 AI 标识；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-101</b> · P2 · 海报出图架构与验收：两层缓存、域名被拦截时的海报兜底、海报验收用例</summary>

负责线：设计；依赖：无。

**范围**

① 02 §11 改为两层缓存：与 link 无关的底图按商品、价格、取价日期、模板版本缓存；二维码合成同步做。原因是每次进分享页都会新建 link，原来的缓存基本命中不了。

② 域名被微信拦截时：拦截期间关闭海报入口；旧海报在系统浏览器里扫码时显示说明页；不靠换域名绕开。规则写在 01 F-SHARE-04，09 CAP-X-03 只加一句指针；改正 11_INV:479 的错误指针。如果编排判定这改变了已确认的决定，就按 00 §8 先写影响评估。

③ 10 新增海报验收用例：与定稿画板做像素比对；微信和系统相机各扫一次；体积在上限内；无券、拼多多、长标题各截一张。

来源：g5-27。

**验收**

02 §11、01 F-SHARE-04、08 11_INV 三处一致；08 里 grep「域名切换规则」为 0；10 有海报用例编号；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-102</b> · P2 · 海报补稿：两张定稿换正式品牌头，补无券、拼多多、缺主图、长昵称变体和生成中、失败态</summary>

负责线：设计；依赖：DSX-100、DSX-34。

**范围**

PosterShare-v2 的 32px 文字方块和 PosterInvite-v2 的 48px App 图标，换成站外品牌头。PosterShare 补无券、拼多多（用「拼单」措辞）、缺主图三张；PosterInvite 补一张长昵称（16 个字素）。分享页和邀请页补「海报生成中」「海报生成失败」两种状态。二维码和角标位按 DSX-100 画。过 Codex 对抗审查后重新登记 sha256。

定稿口径（与 DSX-18 统一）：Codex 对抗审查无可见缺陷即通过，编排登记 sha256，登记后在给负责人的汇报里列一行（事后报告，不阻塞）。

来源：g5-28。

**验收**

design/README 有更新后的 sha256；Codex 审查无 P0–P2；画板里没有占位方块，也没有用 App 图标 PNG 做的品牌头。

</details>

<details>
<summary><b>DSX-131</b> · P2 · 商品图小图取法：CDN 尺寸参数实测登记 09，03 写拼参数规则或 04 登记缩略图字段</summary>

负责线：设计（协同 运维）；依赖：DSX-104。

**范围**

从 DSX-104 拆出，只改规划仓库：按 DSX-104 的 staging 实测，把 img.alicdn.com、img.pddpic.com 支持的尺寸参数登记进 09；据此二选一（技术选择，编排自定）：在 03 写客户端按显示尺寸拼参数的规则，或在 04 登记可为空的缩略图字段形状（契约改动另派 CT 子单）。

来源：g5-13（小图部分）。

**验收**

09 有 CDN 实测记录；小图怎么取写在 03 或 04 里，只有一种说法；kanban --check --local 无 WARN。

</details>

### 后端

<details>
<summary><b>UI-STATES</b> · P0 · UI-STATES：状态目录覆盖首次加载、断网缓存、结果未知、字段缺失和加载超时</summary>

负责线：后端；依赖：DSX-01；承接：UI-STATES（D10-643 ⑤）；状态（2026-11-05）：进行中（D10-643 ⑤ 已派）。

**范围**

specs/ui-states.yaml 在 D10-643 ⑤ 已列字段之外，补上这些内容：

① 通用状态行：首次加载用 Skeleton，LoadingProgress 只用于按钮内和等待外部结果；加载失败无缓存（标题「加载失败」+ 原因 + 主按钮【重试】）；断网无缓存；断网有缓存（只在传输失败且有缓存时显示旧数据，用 net.stale_data，与 order-vectors G10 一致）；维护；强更；结果未知（90003 → 待确认）。

② 金额字段缺失不补 0（按 BR-TEXT-10）；所有加载态设超时上限，超时转 ErrorState。

③ 文案键与 08 表 C 一致。

④ 由 yaml 生成三端和 H5 的向量与目录页样例，放在 rebate-platform 的分发产物里；03 §10.2 改为引用 yaml 的那一处由 COMP-SPEC-2 在规划仓库做。

同时承接 CT-09 的状态部分。

来源：g3-22。

**验收**

ui-states.yaml 每行都有编号、触发条件、组件 kind、文案键、按钮主次、播报、重试；CT-06 门禁通过；三端和 H5 的向量文件已在 rebate-platform 生成并进分发清单；texts.default.json 的 state.* 与 08 表 C 零差异。

</details>

<details>
<summary><b>TOKENS-LAG</b> · P0 · 令牌锁与契约锁落后告警（三端 + H5）</summary>

负责线：后端（协同 前端）；依赖：无；承接：令牌落后告警（D10-643 ⑥）；状态（2026-11-05）：进行中（D10-643 ⑥ 已派）。

**范围**

按 D10-643 ⑥ 写一个检查脚本：读 couli origin/main 上 design-tokens.json 的版本和最近变更提交，对比 rebate-platform contracts/design-tokens.json 的 metadata.version，以及三端 contract.lock 的 design_tokens.commit。落后一个版本或超过 7 天就警告，并输出「消费方 → 锁定提交 / 版本 / 落后天数」表，代替在文档里手写版本号。同一检查还比对三端 contract.lock 的 rebate_platform 提交：三端不一致或落后主干超过阈值时也警告（防止再出现 iOS 锁 a7c9f1f、另两端锁 00deded 的分叉）。给 component_spec 锁和共享向量 hash 比对（DSX-42）留扩展点。本单只交付 rebate-platform 里的脚本、夹具和 CI 接入（H5 与后台在同一仓库，一并覆盖）；三端在各自 CI 接同一检查拆到 DSX-140（iOS）、DSX-141（安卓）、DSX-142（鸿蒙）。

来源：g1-10、g2-43、g4-10。

**验收**

① 用夹具验证：锁 18ad5b4、源 49bb4ad 时报落后；落后超过 7 天时报警；三端契约锁不一致时报警；锁与源一致时不报。脚本单测覆盖以上情况；② rebate-platform CI 日志里有四端消费方版本表（三端读远端 contract.lock）；③ rebate-platform CI 有一次运行记录。

</details>

<details>
<summary><b>CT-07e</b> · P1 · CT-07e：home-schema 收口——开放 props 定稿、视觉参数与图片约束、版本登记、golden、渲染事件</summary>

负责线：后端（协同 前端）；依赖：DSX-26、DSX-33；承接：CT-07（续）。

**范围**

按 DSX-26（含轮播与公告数值）、DSX-33 改 contracts/home-schema.json：

① 删掉 L3 的 open 声明，写定 5 类 props 和 banner 字段；每个 type 登记支持版本和各端起始版本。

② 视觉参数加约束：height_ratio 的取值集合或上下限、autoplay_ms 为 0 或 ≥3000；section_notice_bar.props 收口为 mode（scroll / static）加带范围的间隔字段，不再 additionalProperties: true；static_item.image 加 https 的 pattern，与服务端 item-images 同一口径。

③ content 模块的 page-sections-check 在保存和发布时同样校验，不合格返回 20001 并带字段路径。合并前先查 staging 已发布的首页配置有没有越界。

④ 修改 fixtures/home-golden：按新必填补齐 home-full.json 等，补反例（http 地址、比例越界、autoplay_ms=500、公告间隔越界）。

⑤ specs/events.yaml 增加首页渲染成功事件（按 page_version 计）。

⑥ home-schema.json 和 fixtures/home-golden 进入三端 contract.lock 可锁的分发产物（N-35 第①条）。三端解码和 Tracker 生成在 APP-11-ios-sdui、APP-11-android-sdui、HM-07-sdui 各自仓库里做，本单只交付 rebate-platform。

来源：g4-25、g3-24、g5-16。

**验收**

home-schema.json 里「stay open until the plan names them」为 0；契约测试：golden 正例全部通过 Ajv，每个反例按预期失败；保存接口集成测试对越界返回 20001 并带路径；分发清单含 schema 和 golden；新事件生成了 H5 的 Tracker 函数，三端生成器的输入定义已进分发清单；CT-06 门禁（oasdiff、生成物无漂移）通过。

</details>

<details>
<summary><b>F1-09c-check</b> · P1 · 首页配置保存校验补齐：禁用词、信息流个数与位置、custom 页</summary>

负责线：后端（协同 前端）；依赖：无；承接：F1-09c（补丁后缀）。

**范围**

page-sections-check.ts 接入 text-guard：sections 里全部字符串叶子按 BR-TEXT-13（user_visible 范围）查禁用词，命中按点路径返回 20001；接 JEV-05 语义预检，只标黄，服务不可用时静默跳过。补 Ajv 表达不了的规则：feed_infinite 每页最多 1 个且排最后；routes.json 还没有 CustomPage 时拒绝保存 custom:* 页面（或用开关控制）。与 CT-07e 的 schema 校验共用入口。

来源：g4-26。

**验收**

区块标题含「全网最低」或「返现」时返回 20001，fields 指向点路径；两个 feed_infinite 或不在末位时返回 20001；开关关闭时 custom:test 被拒；现有 pages 测试全绿。

</details>

<details>
<summary><b>DSX-40</b> · P1 · 首页渲染健康：计数写库、错误率告警和自动回滚（TECH-29）</summary>

负责线：后端（协同 前端、iOS、安卓、鸿蒙）；依赖：CT-07e。

**范围**

按 01 F-HOME-07 和 04 §6.6：服务端按 page_version 汇总渲染成功事件和 sdui_card_error，写入 render_count / error_count（kysely-page-config-store.ts L3 由只读改为可写）。错误率 >0.5% 且样本 ≥200 时告警，并按同一阈值调用已有的回滚接口做自动回滚，用开关控制，默认先只告警。openapi L16986「stay 0」改为实际口径。三端上报在各自的 SDUI 解码单里，后台错误率列在 F1-09-qr。

来源：g4-27。

**验收**

集成测试：灌 200 次渲染 + 2 次错误后，计数正确并触发告警；开关打开时自动回滚到上一版本并写审计；openapi 里「stay 0」为 0；staging 有一次告警演练记录。

</details>

<details>
<summary><b>CT-03-env</b> · P1 · 桥契约：app.getEnv 增加主题与字号，新增变化事件</summary>

负责线：后端（协同 前端）；依赖：DSX-25；承接：CT-03（bridge.schema.json 续）。

**范围**

按 DSX-25：bridge.schema.json 里 app.getEnv 的结果增加 color_scheme（light / dark）和 font_scale；新增主题变化、字号变化两个事件；conformance 页加主题和字号用例；重新生成 H5 的桥类型；三端桥类型在 APP-04-ios、APP-04-android、HM-03-web 里随各自仓库的契约同步生成。

来源：g4-28。

**验收**

schema 有新字段和事件，CT-06 门禁通过；conformance cases 新增两条用例；H5 生成的桥类型含 color_scheme、font_scale；分发产物里的 bridge.schema.json 已更新。

</details>

<details>
<summary><b>DSX-41</b> · P1 · 契约字典补读屏键：通用 a11y.* 键和商品图读屏名</summary>

负责线：后端（协同 iOS、安卓、鸿蒙）；依赖：DSX-30、DSX-118。

**范围**

按 08，在 contracts/texts.default.json 增加两类键：DSX-30 登记的 a11y.* 键和播报句；DSX-118 登记的商品图读屏名键（只用「商品图片，{标题}」这一种措辞）。在 fund-term-keys.yaml 里归入「普通」段。三端的本地草稿键（card.image_placeholder、order_list.image_placeholder、鸿蒙 product.image）不进契约。不与 state.* 重复。三端下次同步契约时重新生成。

来源：g4-29、g5-03。

**验收**

新键都在 texts.default.json 里，取值与 08 一致；CT-19 未归类检查不报错；banned-words 扫描 0 命中；分发产物里的 texts.default.json 含新键（三端在 DSX-110、DSX-112、DSX-116 同步时生成）；CT-06 门禁通过。

</details>

<details>
<summary><b>CT-09b</b> · P1 · error-codes.yaml 和 network-vectors 加 presentation 字段</summary>

负责线：后端；依赖：DSX-20、UI-STATES；承接：CT-09（续）。

**范围**

error-codes.yaml 每个码加 presentation（首屏、翻页、提交三个场景，取值同 08 表 A「呈现」列）；三端 network-vectors.json 的 effectKinds 加同名字段，生成三端枚举。不新增 text_key，沿用 error.&lt;code> 命名约定。

来源：g3-23。

**验收**

108 个码都有 presentation；与 08 表 A 的比对脚本零差异；H5 生成物能编译，三端枚举的生成器输入已进分发清单（各端下次契约同步时生成）；CT-06 门禁通过，oasdiff 没有未登记的破坏性变更。

</details>

<details>
<summary><b>DSX-42</b> · P1 · 三端共享客户端向量收归唯一源，加跨端 hash 比对</summary>

负责线：后端；依赖：TOKENS-LAG。

**范围**

把三端各自复制的 login、order、clipboard、format、home-sdui、me、oauth-login 和各 *-visual-vectors.json 收进 rebate-platform 的 specs/client/。收之前先逐条合并已经分叉的版本（login 有 125 / 141 例，order 有 263 / 273 例，clipboard 三端各不相同），由对应开发线确认。分发清单登记这些文件的 sha256；TOKENS-LAG 的检查一并比对三端锁定的向量 hash，不一致就警告，什么时候升级为失败由编排定。三端改锁这些文件拆到 DSX-140、DSX-141、DSX-142。

来源：g2-44。

**验收**

specs/client/ 下有上述文件，分叉已合并（login、order、clipboard 各只有一版）；分发清单有每个文件的 sha256；用夹具验证三端锁定 hash 不一致时检查报警。

</details>

<details>
<summary><b>DSX-43</b> · P1 · 契约补文案键：邀请落地页、邀请页海报暂不可用</summary>

负责线：后端；依赖：DSX-34。

**范围**

按 08 表 C，在 contracts/texts.default.json 补上 DSX-34 登记的键：落地页的 &lt;title>、抬头、按钮、成功页，以及 InviteShare 的海报暂不可用。需要时在 fund-term-keys.yaml 里归类。

来源：g5-19。

**验收**

texts.default.json 有这些键，取值与 08 一致；banned-words 扫描 0 命中；CT-06 门禁通过。

</details>

<details>
<summary><b>DSX-44</b> · P1 · 京东商品图接上：CAP-JD-02 实测 imageInfo 后映射主图和多图（外部阻塞：京东 goods.query 权限）</summary>

负责线：后端（协同 运维）；依赖：无。

**范围**

【外部阻塞】开工前提：京东 goods.query 权限（负责人在办，见 HANDOFF 11-04）。权限没到位前，看板上标为被外部阻塞，不派工。权限到位后：ops 在 staging 实测 imageInfo，记录进 evidence；be 在 infra/jd/goods.ts:327 映射 main_image_url 和 image_urls（只收 https、去重、最多 9 张），去掉 registry.ts 里「实测前不映射」的约束和 TODO。09 CAP-JD-02 的回写拆到 DSX-130。上线前仍拿不到图的话，京东卡按 ProductImage 的「为空」态显示。

来源：g5-14。

**验收**

京东回放 fixture 单测：有 imageInfo 时 card.image 是 https 主图、多图不超过 9 张，没有时为 null；registry 约束测试已同步；staging 实测记录和京东搜索卡出图截图进 evidence。

</details>

<details>
<summary><b>CT-22-trend</b> · P1 · 价格走势契约补齐：文本键、几何测试向量、拼多多来源键（最常见价字段已拆到 CT-22-mode）</summary>

负责线：后端；依赖：DSX-37；承接：CT-22（后续子编号）。

**范围**

外部前置：规划仓库 d0aaa76（详情 v3 回写）已合并，08 表 C 已有 price_trend.current / mode / mode.note* / title.pdd* / source.pdd*，04 §6.3 已有 mode_price_fen。

① texts.default.json 补上 DSX-37 和 d0aaa76 登记的 price_trend.* 键（summary、chart.a11y、empty.desc、source.line、current、mode、mode.note 四个变体、title.pdd*、source.pdd*）。

② ProductPriceTrend.source_key 枚举补拼多多变体；最常见价字段 mode_price_fen 按 D10-664 ③ 拆到 CT-22-mode，本单不再加。

③ 新增 specs/price-trend-geometry.vectors.json：输入一组点，输出刻度、路径坐标和断开的段，含 DSX-37 的 6 组示例，三端和服务端共用。

来源：g5-38。

**验收**

oasdiff 只有新增；向量文件进分发清单并有 schema 校验和服务端测试（三端读取测试在 DSX-134、DS-02-android-trend、DS-02-harmony-trend）；texts 与 08 一致；banned-words 扫描 0 命中；CT-06 门禁通过。

</details>

<details>
<summary><b>CT-22-mode</b> · P1 · 最常见价字段契约：ProductPriceTrend 加 mode_price_fen（D10-664 ③ 从 CT-22-trend 拆出）</summary>

负责线：后端；依赖：无；承接：CT-22（后续子编号；D10-664 记为 S-05）。

**范围**

按 D10-664 ③ 从 CT-22-trend ② 拆出，单独一单，不等 DSX-37 的走势规则，v3 详情不必等它之外的走势契约。只在契约里加 04 §6.3 已登记的可为空字段 mode_price_fen（status=no_data 时为 null），不加 04 没有的 mode_days、record_days；取值口径只引用 01 F-PROD-14 ⑧ 与 08 表 C 的 price_trend.mode* 键，不在契约里复述。D10-664 记为 v3 服务端 S-05，台账编号以 task check 为准。

来源：D10-664 ③（拆自 CT-22-trend，原 g5-38）。

**验收**

oasdiff 只有新增；mode_price_fen 可为空，形状与 04 §6.3 一致；三端生成类型含该字段；CT-06 门禁通过。

</details>

<details>
<summary><b>CT-24-funds</b> · P1 · CT-24：adminGetFundsReport 契约与 specs/reports/funds.yaml</summary>

负责线：后端；依赖：DSX-39；承接：CT-24。

**范围**

新增 adminGetFundsReport。响应包括：每日的 W、P 和告警线（带 measured_at 和 stale）；待打款日终序列和口径编码；事件列表（低于告警线、补足、W 过期）。区间参数上限 90 天。新建 specs/reports/funds.yaml（BR-TEXT-21），列头由它生成；后台字典键按 BR-TEXT-25。

来源：g5-44。

**验收**

oasdiff 只有新增；Prism 能启动并返回样例；契约测试断言 funds.yaml 与响应字段一一对应；CT-06 门禁通过。

</details>

<details>
<summary><b>DSX-45</b> · P1 · packages/money 补坐标轴刻度和读屏金额格式化函数，配测试向量</summary>

负责线：后端（协同 前端）；依赖：DSX-39。

**范围**

按 DSX-39 定下的 BR-TEXT-10 写法新增两个函数：坐标轴刻度格式化（整数、千分位）和读屏金额。测试向量与 08 示例一致。后台页面只调后台写法。

来源：g5-45。

**验收**

单测覆盖 0、负数、四位以上金额、分到元的换算；向量与 08 示例一致；pnpm verify 通过。

</details>

<details>
<summary><b>B1-29-trend</b> · P1 · 价格走势计算：按平台选来源键，服务端算最常见价和显示门槛</summary>

负责线：后端；依赖：CT-22-trend、CT-22-mode；承接：B1-29（后续子编号）。

**范围**

compute.ts:90 现在只按有无券选来源键，改为按平台加有无券选，拼多多用 .pdd 变体。计算 mode_price_fen：取与走势同一组每日价（最近 30 个自然日，每天当天最后一次记录），出现天数最多的价，按分比较，并列时取最近出现的价（01 F-PROD-14 ⑧）。显示门槛与走势共用 price_trend.min_distinct_days（取值见 01 F-PROD-14 ③，与 v3 定稿一致），达不到或平台未达 stable_7d 时 status=no_data、mode_price_fen 为 null。不加开关（负责人 2026-10-05 定价格走势不做开关隐藏）。与 v3 合派对齐：客户端在本单上线前按 null 处理。

来源：g5-39。

按 D10-664：最常见价的计算即 v3 服务端 S-12，只依赖 CT-22-mode、不等 CT-22-trend 与 DSX-37；按平台选来源键仍依赖 CT-22-trend。

**验收**

属性测试：并列时取最近出现的价；不同日期数 &lt;2 或未达 stable_7d 时 status=no_data 且 mode_price_fen 为 null；拼多多返回 .pdd；响应里没有用户标识（AC-S1-141）；代码里没有最常见价的开关；pnpm verify 通过。

</details>

<details>
<summary><b>DSX-103</b> · P2 · 文案检查加品牌语气条目</summary>

负责线：后端；依赖：DSX-05。

**范围**

按 DSX-05 定的 BR-TEXT-27 新增一个独立的品牌语气检查，不并进 banned-words.yaml。检查「您」「亲」、全角和半角感叹号、表情符号。CI 对 texts.default.json 等包内默认文案命中即失败；后台运营可改的文案只在语义预检里标黄提示、不拦截（与 03 §9.2 JEV-05 口径一致）。

来源：g1-30。

**验收**

CI 对含「您」或「！」的样例失败；主干 texts.default.json 0 命中；检查规则注明依据 BR-TEXT-27；pnpm verify 通过。

</details>

<details>
<summary><b>CT-03-upgrade</b> · P2 · routes.json 登记「请升级 App」提示页的路由名和文案键</summary>

负责线：后端（协同 iOS、安卓、鸿蒙）；依赖：DSX-95；承接：CT-03（routes.json 续）。

**范围**

contracts/routes.json 加「请升级 App」提示页的路由名，texts.default.json 加对应文案键，本单只改 rebate-platform；三端之后按 DSX-95 的规格各自实现提示页（安卓顺带解掉 AppNavHost 里的 TODO(N-14)），另派。

来源：g3-26。

**验收**

routes.json 有该路由，并通过路由一致性检查；texts 有键；CT-06 门禁通过；分发产物含新路由。

</details>

<details>
<summary><b>CT-03-navbar</b> · P2 · 桥契约：ui.setNavBar 的色值参数收口为令牌名</summary>

负责线：后端（协同 iOS、安卓、鸿蒙、前端）；依赖：DSX-25；承接：CT-03（bridge.schema.json 续）。

**范围**

bridge.schema.json L529–547 的 bg_color、bg_gradient、text_color 现在接受任意 #hex，改为令牌名枚举（surface / brand / inverse）或浅深成对传值。兼容期内旧参数忽略并上报。三端容器在下一次容器补丁里适配。业务 H5 目前还没调用，这是风险预防。

来源：g4-70。

**验收**

CT-06 门禁通过；conformance 用例：传 #hex 会被拒或忽略并上报；H5 的生成类型已更新，分发产物里的 bridge.schema.json 已更新（三端在下一次容器补丁里同步）。

</details>

<details>
<summary><b>CT-03-share</b> · P2 · 分享与海报契约补齐：poster_status、二维码落地路径、share.open 缩略图约束</summary>

负责线：后端；依赖：DSX-100；承接：CT-03、CT-22（后续子编号）。

**范围**

Share 和 MyInvite 加 poster_status（ready / rendering / failed / unavailable）和建议的重取间隔，改写 poster_url 的说明。bridge.schema.json:828–840 给 product_share、invite_landing、download_guide 定下 path_pattern（N-22）。:874–878 share.open 的 thumb 写明约束（不超过 32KB、方形 JPEG、由原生压缩）。

来源：g5-33。

**验收**

oasdiff 只有新增；CT-06 门禁通过；分发产物里三个 path_pattern 都不再是 null；Prism 能启动。

</details>

<details>
<summary><b>B1-15-input</b> · P2 · 出图输入通道：服务端取同一套令牌、正式 Logo 和随包中文字体，先出样张</summary>

负责线：后端；依赖：DSX-100；承接：B1-15。

**范围**

apps/api 通过 @couli/ui-tokens 取颜色、字号、圆角、间距；如果依赖规则不允许直接引用，就用同源生成一份服务端只读快照。logo-mark.svg、logo-horizontal.svg 用快照机制放进来。字体随包，登记 OFL 许可并按常用字集做子集。用 satori + resvg 为两张定稿海报出样张，核实两行截断、等宽数字和中文断行。

来源：g5-31。

**验收**

apps/api 只有一处令牌来源，dependency-cruiser 通过；Logo 和字体快照带来源版本和校验和；样张与画板的像素比对差异在容差内，结果进 evidence；许可证检查通过。

</details>

<details>
<summary><b>B1-15-worker</b> · P2 · 海报出图 worker：两种模板、两层缓存、写 OSS、回填 poster_url 和状态、限流告警</summary>

负责线：后端（协同 运维）；依赖：B1-15-input、CT-03-share、DSX-102、DSX-101；承接：B1-15。

**范围**

给已登记的 poster 队列注册处理器，按定稿模板渲染分享海报和邀请海报：

- 缓存按 DSX-101 拆成两层；二维码参数按 DSX-100；

- 结果写入 OSS media（B1-30b 适配器；生产 bucket 由负责人开，见 06 Q-C21）；

- 回填 POST /v1/shares、GET /v1/invites/me 的 poster_url 和 poster_status，去掉 shares.ts:30、my-invite.ts:24 的「always null」；

- 出图时校验 JPEG 和体积；队列设并发上限，超时告警；k6 加出图场景（QS-15）。

邀请海报仍属 M-内测；内测期间如果本单未上线，由 F1-05-poster 的说明态兜底。本期范围由负责人决定，本单不调整 M-内测范围。

来源：g5-32。

**验收**

同一商品第二次进页只合成二维码；失败时 poster_status=failed；超过体积会重新压缩；渲染结果文本扫描不含收益或返利金额；k6 报告有出图场景；pnpm verify 通过；staging 两个接口都能返回可下载的 JPEG。

</details>

<details>
<summary><b>DSX-104</b> · P2 · 契约写清商品图字段，评估宽高和小图（缩略图或 CDN 尺寸参数）</summary>

负责线：后端（协同 运维）；依赖：DSX-32。

**范围**

ProductCard.image 加说明：平台主图原图、只会是 https、不超过 2048 字符、可以为 null，写明各平台的来源字段，与 item-images.ts 一致。AdminPoolItem.image 补 format: uri。评估给 ProductCard 和分享素材加可为空的 width / height。ops 在 staging 实测 img.alicdn.com、img.pddpic.com 支持的尺寸参数，记录进 evidence；09 登记和小图取法的裁定拆到 DSX-131。是否读 white_image 按 DSX-32 的结论定。本单只改 rebate-platform。

来源：g5-13。

**验收**

oasdiff 只有新增的可选字段和说明；CT-06 门禁通过；CDN 实测记录进 evidence；非 https 主图仍被清成 null（回归测试）。

</details>

### 前端（H5 与管理后台）

<details>
<summary><b>LINT-STYLE-web</b> · P0 · Web LINT-STYLE：H5 与后台禁写死样式，后台主题改读令牌，修正 H5 选中态对比度</summary>

负责线：前端；依赖：无；承接：Web LINT-STYLE（D10-643 ⑧）；状态（2026-11-05）：进行中（D10-643 ⑧ 已派）。

**范围**

按 D10-643 ⑧ 做：

① ESLint 禁止 apps/h5、apps/admin 的 style 对象和 TSX 里出现数字 fontSize / borderRadius / margin / padding 和 hex 色值，同一规则覆盖传给 ui.setNavBar 的色值；禁止 Tailwind 任意值（如 invite-page.tsx:261 的 text-[2rem]，例外写豁免注释）；禁止小字用 text-couli-brand-primary。基线只减不增。

② 后台 theme.ts L80–84 的 14、8、36 改读 packages/ui-tokens；fontSize: 12（67 处）和 token.fontSizeSM（50 处）两种写法统一为令牌。source.test.ts 的扫描范围扩到全部 pages 和 components。

③ 修 PILL_ON（earnings-page.tsx:293–294、:370，claim-form.tsx:268，invite-page.tsx:430）：改为 brand-emphasis 字配 brand-subtle 底（5.62:1）；invite-page.tsx:43 的链接改用 text-couli-text-link。选中胶囊的对比度测试覆盖浅深两态（现在分别是 4.33:1 和 3.02:1）。

后台字号、尺寸改读 admin.* 令牌由 DSX-105 完成。

来源：g2-39、g4-09。

**验收**

① pnpm lint 对反例（text-[13px]、小字用 text-couli-brand-primary、style 里写数字字号或 hex）报错，基线入库；② theme.ts 里 14、8、36 字面量为 0，单测断言主题值等于 ui-tokens；③ source.test.ts 扫描范围含 src/pages/** 和 src/components/**；④ 选中胶囊浅深两态都 ≥4.5:1；⑤ pnpm lint typecheck test 通过。

</details>

<details>
<summary><b>H5-DARK</b> · P0 · H5 遮罩改用 overlay.scrim，轻提示换对角色令牌，加浅深对比度测试</summary>

负责线：前端；依赖：无；承接：H5 组件深色修正（D10-643 ⑦）；状态（2026-11-05）：进行中（D10-643 ⑦ 已派）。

**范围**

按 D10-643 ⑦ 做：

① ModalFrame.tsx:302 的 bg-couli-text-primary/40 改为 bg-couli-overlay-scrim（现在深色下遮罩发白）。

② Toast.tsx:30 不再用 text.primary 当底、text.inverse 当字（深色下 1.16:1），改用 background.surface + text.primary + shadow.floating，修好对比度；位置、时长等外观的后续调整交给 DSX-48。

③ 加「组件前景 / 背景配对 × 浅深两态」对比度断言（文字 ≥4.5、非文字 ≥3），用来拦住引用了错误角色的令牌。

④ H5 组件快照补深色基准。

来源：g1-11。

**验收**

执行 `git grep -nF 'bg-couli-text-primary' -- apps/h5/src/components` 为 0；对比度测试覆盖 Toast 和 ModalFrame，把 Toast 改回 text.primary 底的变异会失败；深色快照基准入库；pnpm verify 通过。

</details>

<details>
<summary><b>CT-11c</b> · P1 · CT-11c：契约令牌快照升到 v0.6.0，H5 接入新令牌类别</summary>

负责线：前端（协同 后端）；依赖：DETAIL-V3-WB、DSX-02、DSX-03、DSX-04；承接：CT-11。

**范围**

照 CT-11a、CT-11b 的做法，在 05 CT-11 下新开 CT-11c。rebate-platform 的 contracts/design-tokens.json 换成 couli v0.6.0 发布提交（DSX-02 合并点，已含 DETAIL-V3-WB 的 v0.5.1 和 DSX-03、DSX-04 的键）的固定快照，并记下来源提交。packages/ui-tokens 生成器支持复合文字样式、duration、cubicBezier、layer、layout、motion、chart（后台 G2 主题取 color.chart.*），生成 CSS 变量、Tailwind 工具类和 theme.gen.ts，供 H5 和后台用。H5 接入三处：Toast.tsx 的 DEFAULT_DURATION_MS 改读 motion.toast.display；base/styles.ts 的 z-50 / z-60 改读 layer；Skeleton.tsx 底色改读 color.skeleton。漂移测试同步更新。改 contracts/ 要占契约槽（全局同时只能 1 个），由 be 协调。

来源：g1-19、g3-25。

**验收**

contracts/design-tokens.json 的 metadata.version 等于 couli 最新版本；ui-tokens 生成物含 layout / motion / layer / chart；漂移测试通过；执行 `git grep -nF -e 'DEFAULT_DURATION_MS = 2000' -e 'z-50' -e 'z-60' -e 'bg-couli-background-placeholder' -- apps/h5/src/components/base` 为 0；pnpm verify 通过；TOKENS-LAG 对 H5 不报落后。

</details>

<details>
<summary><b>DSX-46</b> · P1 · H5 基础件补齐：Button、Chip / Segmented、NoticeBar、Field、Card</summary>

负责线：前端（协同 后端）；依赖：COMP-SPEC、COMP-SPEC-2、DSX-02、CT-11c、DSX-119。

**范围**

在 apps/h5/src/components/base 新增以下组件，取值全部走 ui-tokens：

- Button：variant 为 primary / secondary / text / onSolid（tonal 按 DSX-119 裁定），size 为 standard / compact / full，状态有 disabled / loading，与原生同名同表；

- Chip、Segmented：选中态用 brand-emphasis；

- NoticeBar：四种语气；

- Field：文本和手机号两种；

- Card。

Vitest 按 component-spec.json 的 h5 列断言类名映射；Playwright 做浅深两态截图基准。

来源：g2-40。

**验收**

base/index.ts 导出上述组件；单测覆盖 component-spec.json h5 列的全部行；浅深截图基准入库，对比度测试通过。

</details>

<details>
<summary><b>DSX-47</b> · P1 · H5 页面私有的按钮、胶囊、卡片类名迁移到基础件</summary>

负责线：前端；依赖：DSX-46。

**范围**

把这些页面私有类名和常量换成 base 组件：invite-page.tsx:46–47 的 ACTION_*、messages-page.tsx:42 的 TEXT_BUTTON、earnings-page.tsx 的 PILL_BUTTON / PILL_ON、claim-form.tsx:374 的 disabled 样式、8 个页面各自定义的 CARD 常量。页面里的 38 个 &lt;button 全部改用 Button。eslint 禁止页面再定义按钮、胶囊、卡片的样式常量。

来源：g2-41。

**验收**

执行 `git grep -n -E '(const|export const) (ACTION_PRIMARY|ACTION_SECONDARY|TEXT_BUTTON|PILL_BUTTON|PILL_ON|CARD) =' -- apps/h5/src/entries` 为 0；`git grep -n '<button' -- apps/h5/src/entries` 为 0；页面截图按 PR 说明更新。

</details>

<details>
<summary><b>DSX-48</b> · P1 · H5 状态与反馈组件对齐状态目录：轻提示位置、骨架屏、状态键</summary>

负责线：前端；依赖：UI-STATES、COMP-SPEC-2、DSX-01、H5-DARK、CT-11c。

**范围**

改 apps/h5 的 base 组件：

- Toast：按规范改为 App 内页顶，站外 H5 是否例外按规范；时长由组件定，页面不传 durationMs。

- StateLayout：按状态目录的 kind 决定图标和文案键。

- Skeleton：按 COMP-SPEC-2 的口径，减弱动态时静止。

- earnings-page.tsx 的页内错误标题从 h5.load_failed 改为通用状态键，邀请页等页面同样统一。

本单排在 H5-DARK 之后（改的是同一个文件）。

来源：g3-27。

**验收**

Toast.tsx 只在站外分支保留底部定位；页面层 grep h5.load_failed 只剩容器重试页；Playwright 浅深截图更新，并与 StateLoadFailed 稿并排比对一致。

</details>

<details>
<summary><b>DSX-49</b> · P1 · H5 App 内页面的版心与页面骨架</summary>

负责线：前端；依赖：CT-11c、DSX-11、LINT-STYLE-web。

**范围**

apps/h5 加一个共用的页面骨架：处理安全区，内容最大宽读 layout 令牌并水平居中。App 内 H5 页（流水、收益、找回、消息、公告、邀请、帮助、规则、协议）都改用它。Web LINT-STYLE 加规则，禁止页面写死最大宽。

来源：g3-28。

**验收**

≥600 宽视口下，截图内容居中且宽度等于令牌值；lint 对新增的写死宽度报错。

</details>

<details>
<summary><b>DSX-50</b> · P1 · H5 与后台截图基准比对（浅 / 深，先只报告）</summary>

负责线：前端（协同 设计）；依赖：无。

**范围**

在现有 Vitest 浏览器模式（Playwright Chromium，49 个 *.browser.test.ts）上加截图基准比对：

- H5 关键页（规则、帮助、公告、收益明细、订单找回、消息、邀请）浅深两套；

- 后台关键页（登录、工作台、订单列表、提现审核）浅色一套。

阈值按 11 §4.1 截图差 ≤1%，先只报告；基准入库；容差按 DSX-09。

来源：g4-30。

**验收**

test/spec/frontend 里有截图比对断言，基准图已入库；CI 产物输出每页的差异百分比；变异：改一个按钮圆角后，报告能标出该页。

</details>

<details>
<summary><b>QA-12-web</b> · P1 · H5 与后台接入 axe 自动检测和 200% 缩放冒烟</summary>

负责线：前端（协同 质量）；依赖：无；承接：与 05 QA-12（Web 自动检测部分）、QA-11（H5 与后台 200% 部分）相关。

**范围**

浏览器测试接入 axe-core（vitest-axe 或 @axe-core/playwright）。H5 和后台关键页先只报告，生成违规基线，新增违规即告警。加 200% 缩放冒烟：H5 关键页正文和主要操作不截断、不重叠；后台 200% 下侧栏、筛选和宽表可用（WCAG 1.4.4、1.4.10）。发现的问题登记到 DSX-139 立的 QA-11 / QA-12 清单。

来源：g4-31。

**验收**

package.json 有 axe 依赖，CI 产物含各页 axe 报告和基线；200% 用例在 CI 上运行；新增 axe 违规时 CI 出警告。

</details>

<details>
<summary><b>DSX-51</b> · P1 · 后台 200% 与窄视口重排（视口分档落地）</summary>

负责线：前端（协同 设计）；依赖：无。

**范围**

按适配约定的「后台 · 视口分档」（≥1440 / 1280–1439 / 960–1279 / &lt;960）和 03 §10.4 后台行，在后台外壳和表格组件里落地：侧栏可收起、筛选可换行、宽表固定列。断点集中定义在外壳组件里。

来源：g4-32。

**验收**

浏览器测试在 1280、960、800 宽和 200% 缩放下，除数据表格外没有页面级横向滚动，侧栏可以收起；页面代码里不写断点数字。

</details>

<details>
<summary><b>DSX-52</b> · P1 · App 内 H5 跟随宿主主题与字号</summary>

负责线：前端（协同 iOS、安卓、鸿蒙）；依赖：CT-03-env。

**范围**

H5 shared 层读取 app.getEnv 的 color_scheme 和 font_scale（或宿主写入的 data-theme），并订阅变化事件；根字号 CSS 变量随 font_scale 放大，上限 200%。没有桥（站外、微信）时回退到 prefers-color-scheme 和浏览器默认字号。index.css 里关于 data-theme 的注释与实现保持一致。

来源：g4-33。

**验收**

浏览器测试：color_scheme=dark 时 html 的 data-theme 为 dark，令牌变量取深色值；font_scale=2 时根字号为 2 倍，关键页不截断；无桥环境的回退用例通过。

</details>

<details>
<summary><b>F1-01-nav</b> · P1 · H5 外壳按路由设置原生标题，去掉页面自绘标题</summary>

负责线：前端（协同 iOS、安卓、鸿蒙）；依赖：无；承接：F1-01（补丁后缀）。

**范围**

apps/h5 的 app 入口在路由切换时调用 ui.setNavBar 设置标题（文案取字典键）。entries/app/index.html 的空 title 填上与标题一致的值。help-home.tsx L183 自绘的标题改为 sr-only h1。

来源：g4-34。

**验收**

浏览器测试：每个 app 路由进入后都调用了 ui.setNavBar，且 title 非空；help-home 可见区域没有自绘标题行；非 conformance 代码里的 setNavBar 调用都集中在共用外壳。

</details>

<details>
<summary><b>F1-09-qr</b> · P1 · 后台首页配置：草稿二维码、弹窗素材上传位、版本错误率列</summary>

负责线：前端（协同 后端）；依赖：无；承接：F1-09（补丁后缀）。

**范围**

① 撤掉 home-config.ts L68「二维码待深链定稿」和 EditorView.tsx 头注释里的 no QR code，生成 couli://r/HomePreview?page_key=…&token=… 二维码（token 有效 10 分钟、只读）。

② popup 表单加动画文件和兜底图两个 Upload 位（adminUploadPopupAsset 已实现）。

③ 版本列表加 render_count、error_count 和错误率列（DSX-40 合并后才有数）。

来源：g4-35。

**验收**

浏览器测试：保存草稿后出现二维码，解码以 couli://r/HomePreview?page_key= 开头且带 token；上传位存在，服务端拒绝时显示原因；有错误率列；EditorView.tsx 里「no QR code」为 0。

</details>

<details>
<summary><b>F1-09-form</b> · P1 · 后台首页配置：由 home-schema 生成属性表单，区块拖拽排序</summary>

负责线：前端（协同 设计、后端）；依赖：CT-07e、DSX-27；承接：F1-09（补丁后缀）。

**范围**

左侧区块列表支持拖拽排序；右侧属性表单由收口后的 schema 生成（@rjsf/antd），保留 Monaco JSON 作为高级模式。pool_id 从商品池列表里选（F1-09-pools 合并后接）；union_material 频道下拉只列白名单。

来源：g4-36。

**验收**

只用表单新增一个 icon_grid 区块就能保存，生成的 JSON 通过服务端 Ajv；拖拽改顺序后保存，sections 顺序一致；测试遍历 schema，表单字段与 props 一一对应。

</details>

<details>
<summary><b>F1-09-preview</b> · P1 · 后台首页配置：近似预览（可复用的 H5 卡片渲染包）和图片就地校验</summary>

负责线：前端（协同 设计）；依赖：CT-07e、DSX-27、DSX-33；承接：F1-09（补丁后缀）。

**范围**

后台内嵌 H5 版预览器，按 schema 近似渲染 8 类卡（popup 只显示兜底图，banner 和活动卡按令牌图框裁切），只用令牌和 H5 基础组件。做成独立的卡片渲染包，作为将来 CustomPage H5 渲染器的基础。图片字段加就地校验提示（https、比例、体积，规则取 DSX-33），不合格不能发布。

来源：g4-37、g5-17。

**验收**

编辑后 1 秒内预览更新；用 golden 渲染 8 类卡的截图基准并入 DSX-50 的比对；渲染包不依赖后台代码（dependency-cruiser 校验）；Vitest：http 图片和越界比例会显示字段错误、不能发布；AC-ADM-09、AC-ADM-10 通过。

</details>

<details>
<summary><b>DSX-135</b> · P1 · 后台内容 CMS 页面（帮助 / 规则 / 公告 / 协议）</summary>

负责线：前端（协同 后端）；依赖：DSX-28；承接：与 05 F1-10 相关（只做其中的内容 CMS 界面；配置中心、紧急开关等仍归 F1-10 原行）。

**范围**

按 admin-content.md 做：content 菜单落地成页面，不再渲染 PagePending；用 Tiptap 编辑，输出与 H5 static-renderer 同一白名单的 JSON；保存走 BR-TEXT-13 硬拦和 JEV-05 标黄；协议发布沿用 step-up 和法务确认。

来源：g4-38。

**验收**

content 菜单不再渲染 PagePending；package.json 有 @tiptap/*；冒烟：新建公告并发布后，H5 公告页能看到；白名单外的节点被拒。

</details>

<details>
<summary><b>F1-09-pools</b> · P1 · 后台商品池管理页</summary>

负责线：前端（协同 后端）；依赖：DSX-28；承接：F1-09（商品池）。

**范围**

按 admin-pools.md 做：pools 菜单落地成页面，含池列表、新建、入库、标签、上下架（CT-07d 契约已实现，权限为 content.pool）；首页配置的 pool_id 下拉取这里的池列表。

来源：g4-39。

**验收**

pools 菜单不再渲染 PagePending；冒烟：建池入库后，首页配置里能选到该池；没有权限的账号看不到这个菜单。

</details>

<details>
<summary><b>F1-05-landing</b> · P1 · 邀请落地页按 v2 定稿实现，替换占位页并补页面标题</summary>

负责线：前端；依赖：DSX-34、DSX-43；承接：F1-05。

**范围**

apps/h5 的 landing 入口现在是占位：render.ts 只显示 page_pending，&lt;title> 是空的。按 h5-invite-landing.md 实现 /i/{code}：首屏按 B-6 方案 A，不依赖 React，首屏 JS ≤60KB（gzip）；用正式 Logo；告知句位置按 BR-INV-16；发验证码和注册走 /v1/landing/sms-codes、/v1/invites/landing-register；document.title 取字典键；浅深两态都按令牌；奖励句按 BR-INV-24 的开关显示，默认关闭。

来源：g5-20。

**验收**

Playwright 截图：有效码、无效码、已注册，各有浅深两态；首屏预算检查通过；document.title 非空且等于字典值；AC-INV-02、AC-S1-75 通过；微信深色模式截图进 evidence。

</details>

<details>
<summary><b>F1-05-poster</b> · P1 · H5 邀请页海报不可用时显示说明态</summary>

负责线：前端；依赖：DSX-34、DSX-43；承接：F1-05。

**范围**

invite-page.tsx 在 posterUrl 为 null 时，现在只是 return 并把按钮置灰。改为按画板在预览区显示「海报暂不可用」说明；按钮仍不可点，但读屏能读到原因。poster_url 有值时行为不变，不改接口。

来源：g5-21。

**验收**

poster_url 为 null 时显示说明文案，按钮是 aria-disabled，读屏能读到原因；有值时与现在一致；浅深截图各一张。

</details>

<details>
<summary><b>DSX-137</b> · P1 · 资金看板页的图表部分：antd + G2、令牌主题、图表同源、W 过期断线、越线标记、键盘读值</summary>

负责线：前端；依赖：CT-24-funds、DSX-45、DSX-04、DSX-39、CT-11c；承接：与 05 F1-08g 相关（只做资金看板页的图表部分；流水查询、导出、台账、资产快照仍归 F1-08g 原行，不给原行加前置依赖）。

**范围**

按 03 §9.1 引入 @antv/g2（版本取 DSX-39 新 ADR 的版本线）。页面内容：W 和告警线折线、待打款日终柱、关键事件标注、【以表格查看】切换。图、提示框、aria-label 和表格用同一份数据、同一组格式化函数；主题取 CT-11c 生成的 color.chart.*；W 过期断线或置灰；区间不超过 90 天；支持键盘读值。工作台「预估返利合计」卡标上 ESTIMATED 口径编码。补资金看板的 Playwright 浅深截图基准。

来源：g5-46。

**验收**

Vitest 断言图、表格、aria-label 数值同源；没有 fund.view 权限看不到；截图覆盖浅深、1280 窄窗、200% 缩放；pnpm verify 通过。

</details>

<details>
<summary><b>DSX-105</b> · P2 · 后台主题改读生成的 admin 令牌，焦点框统一用 focus.ring</summary>

负责线：前端；依赖：DSX-94、CT-11c。

**范围**

theme.ts 第 80–99 行的 fontSize、borderRadius、controlHeight、itemHeight 等，改读 ui-tokens 生成的 admin.*。search.css 第 21–23 行的焦点框从 var(--color-brand-primary) 改为 var(--color-focus-ring)。如果决定后台全部沿用 antd 主色作焦点，就在 tokens/README 登记例外，并统一全部控件。

来源：g1-29。

**验收**

theme.ts 里没有字面 fontSize / controlHeight / borderRadius 数字；执行 `git grep -nF 'solid var(--color-brand-primary)' -- apps/admin` 为 0；pnpm verify 通过；后台 Playwright 截图按 DSX-94 的定论核对控件高。

</details>

<details>
<summary><b>DSX-106</b> · P2 · 管理后台共享筛选栏，收敛内联数值</summary>

负责线：前端；依赖：无。

**范围**

apps/admin/src/components 新增 FilterBar，带共享主题（Input / Select / DatePicker 的 controlHeight，Form 的 labelFontSize 12 和 verticalLabelPadding）。audit-logs、claims、orders、users 四个列表页改用它。pages 里 style={{数字}} 写的间距和字号改用 antd token 或共享常量；eslint 以现状为基线，只减不增。

来源：g2-42。

**验收**

pages 里 const FILTER_THEME 为 0；四个页面筛选区的标签字号和控件高一致（Playwright 断言）；内联数字样式的基线只减不增。

</details>

<details>
<summary><b>DSX-107</b> · P2 · 管理后台统一页面状态组件、弹层动效和「结果未确认」等待上限</summary>

负责线：前端；依赖：DSX-97。

**范围**

新增共享的 PageState（loading / empty / failed / forbidden，统一用 antd Result 的一种写法），替换 AdminsPage、ClaimsPage、ClaimReviewPage、OrdersPage、SyncRecords 等页面各自拼的状态。App.tsx 的全局 ConfigProvider 统一弹窗和抽屉动效，去掉 27 个文件里逐页设置空 transitionName 的写法。A 类写操作按 03 §9.2 的等待上限统一转为「结果未确认」。

来源：g3-29。

**验收**

逐页设置空 transitionName 的写法为 0；用 status=warning 表示加载失败的为 0；PageState 有单测；Playwright 冒烟通过。

</details>

<details>
<summary><b>DSX-108</b> · P2 · H5 基础控件强制配色回退与减弱动态</summary>

负责线：前端（协同 设计）；依赖：无。

**范围**

apps/h5 的按钮、输入、勾选、焦点环加 forced-colors 媒体查询的系统颜色回退（参照 foundations.css:69）；Skeleton.tsx:15 以外的动效补 prefers-reduced-motion 处理；与 DSX-10 的「系统辅助设置」一行保持一致。

来源：g4-71。

**验收**

apps/h5 和 ui-tokens 里有 forced-colors 规则；forced-colors: active 模拟下按钮边界和焦点环可见（截图）；reduced-motion 下没有持续动画。

</details>

<details>
<summary><b>DSX-138</b> · P2 · 分享中间页与下载引导页按 v2 定稿改版</summary>

负责线：前端；依赖：DSX-96；承接：与 05 F1-11 相关（按 v2 定稿改版；域名可访问性检测与告警仍归 F1-11 原行）。

**范围**

在 landing 入口按 h5-share-page.md、h5-download-guide.md 实现：首屏预算和 B-6 方案 A 同 F1-05-landing；document.title 取字典键；微信里引导用浏览器打开；浏览器里提供【在 App 中打开】和【复制淘口令】；京东、拼多多的购买按钮按 L-16；浅深两态都做，另截微信深色模式的图。

来源：g5-30。

**验收**

Playwright 截图：浏览器、微信、未拉起 App 三种情况，各有浅深两态；document.title 非空；首屏预算检查通过；AC-SHARE-04、AC-S1-71 通过。

</details>

### iOS

<details>
<summary><b>APP-17-ios-apple</b> · P0 · iOS「通过 Apple 登录」改用系统官方按钮（解除浅色锁前必须合并）</summary>

负责线：iOS；依赖：无；承接：APP-17（iOS 补丁后缀）；状态（2026-11-05）：进行中（D10-643 iOS 顺序已派，须在解浅色锁前合）。

**范围**

LoginView+ThirdParty.swift L155–175 现在自己画了 RoundedRectangle 加 apple.logo：深色下是白字压在 #F2EEE6 上，对比度约 1.16:1，也违背 03 §10.2 和登录 v2 README §6 已定的「用系统按钮」。改为 AuthenticationServices 的 SignInWithAppleButton，样式随系统外观取纯黑或纯白，尺寸与「本机号码一键登录」相同；去掉 L157 写死的 .font(.system(size: 17…))。必须早于 DSX-127（去锁）合并。

来源：g4-03。

**验收**

① 该文件里 apple.logo 自绘和 .font(.system(size: 为 0 处；② 登录页浅深两态快照基准新增，深色下按钮为白色样式的断言通过；③ 合并记录显示本单早于 DSX-127。

</details>

<details>
<summary><b>FU-X-HOME-PAGE-API-ios</b> · P0 · iOS 首页 Staging / Release 接真实页面接口，契约锁与安卓、鸿蒙对齐，刷新失败改用 couliToast</summary>

负责线：iOS（协同 后端）；依赖：无；承接：FU-X-HOME-PAGE-API-ios（D10-643 ①）；状态（2026-11-05）：进行中（D10-643 ① 已派）。

**范围**

按 D10-643 ① 做：

① AppHomeSupport.swift L108「variant == .debug ? debugPort() : nil」导致非 debug 构建只显示包内默认首页。改为 Staging 和 Release 都实现 HomeContractPort，接 getPage 和 listPageSectionItems，跑三端共用的 specs/home-sdui-vectors.json。

② contract.lock 的 rebate_platform 从 a7c9f1f 升到 00deded 或更新，与安卓、鸿蒙同版本。

③ HomeSduiScreen.swift（约 L323–329）自写的底部 overlay 加 3 秒 Task.sleep，改用组件库 couliToast（页顶、组件计时、ToastAnnouncement 播报）。

本机 rebate-ios origin/main 停在 11-02，开工前先按远端主干复核。

来源：g4-01、g3-32。

**验收**

① 三端 contract.lock 的 rebate_platform 提交一致（附比对输出），iOS 快照里有 /v1/pages/{page_key}/sections/{section_id}/items；② 新测试断言 Staging、Release 首页 port 非空，源码中「debugPort() : nil」为 0；③ home-sdui-vectors.json 的哈希与另两端相同，向量单测全过；④ HomeSduiScreen 里没有 .overlay(alignment: .bottom) 提示和 Task.sleep(for: .seconds(3))；⑤ staging 包首页能显示服务端下发的商品池卡（截图进 compare）。

</details>

<details>
<summary><b>DS-02-iOS-1</b> · P0 · DS-02-iOS（一）：升令牌锁、生成深色与组件令牌、删手抄表（去浅色锁拆到 DSX-127）</summary>

负责线：iOS（协同 设计）；依赖：无；承接：DS-02-iOS（D10-643 ②）；状态（2026-11-05）：进行中（D10-643 ② 已派，第一单）。

**范围**

按 D10-643 ② 做（本单含 iOS 的 TOKENS-PIPE）。开工前先按 rebate-ios 远端主干复核现状，本机停在 11-02 的 9a7b870。

① contract.lock 的 design_tokens 从 18ad5b4 直接升到 couli f088f04（v0.5.1，D10-665）；之后跟到 v0.6.0 由 DSX-120 负责。rebate_platform 锁由 FU-X-HOME-PAGE-API-ios 处理。

② 生成器输出 dark、component（v0.4.0 多出的 22 个叶子）、shadow。删掉 TokenColor.swift 第 98–123 行的 CouliDarkTokens 手抄表、CouliGuideMetric、TODO(DS-02-iOS)；TokenColor 不再对 border.active、control.checked、badge.background、button.inverse.* 返回 .clear。TokenComponents.swift 不再用间距算术拼尺寸（如 listImage = s12×2），改读 component.*。

③ CouliButton .inverse 改读 button.inverse.*，深色取值与另两端一致；去掉钱包页的局部写法。SettingsSubPages.swift:129 输入中的描边改用 borderActive。

④ 解除整 App 浅色锁不在本单：拆到 DSX-127，等 APP-17-ios-apple、LINT-STYLE-ios ③ 合并并做完全页面深色扫描后再去锁。本单不改 Info.plist 的 UIUserInterfaceStyle。

⑤ 加「生成物 vs 锁定源」比对测试；关键页浅深两态快照（深色用测试里强制外观）；CI 重跑生成器无漂移。

来源：g1-04、g2-28、g4-02①③、g3-31（远端复核）。

**验收**

① 执行 `git grep -nF -e 'TODO(DS-02-iOS)' -e CouliDarkTokens -e CouliGuideMetric` 为 0；② DesignTokens.swift 的 version ≥ 0.5.1，`git merge-base --is-ancestor f088f04 <锁定提交>` 成立；③ TokenComponents.swift 里用 CouliSpacing 加乘拼出的尺寸为 0；④ 卡内白底按钮深色取值与另两端一致（快照）；⑤ 关键页浅深两态基准入库，生成器重跑后 git diff 为空；⑥ Info.plist 仍保留 UIUserInterfaceStyle（去锁由 DSX-127 做）。

</details>

<details>
<summary><b>DSX-127</b> · P0 · iOS 解除整 App 浅色锁：全部页面深色扫描通过后去锁（DS-02-iOS ④ 拆出）</summary>

负责线：iOS（协同 设计）；依赖：DS-02-iOS-1、APP-17-ios-apple、LINT-STYLE-ios；承接：DS-02-iOS（D10-643 ②，去锁部分）。

**范围**

从 DS-02-iOS-1 ④ 拆出，单独一个 PR，最后合：

① 先对全部页面跑一轮深色快照和对比度扫描（文字 ≥4.5、非文字 ≥3，按令牌配对计算），覆盖 Features 全部路由；扫出的写死颜色和 opacity 状态色在本单或已合的 LINT-STYLE-ios ③、DSX-55 到 DSX-59 里改掉，没改完不去锁。

② 去锁：删掉 Info.plist L41–42 的 UIUserInterfaceStyle=Light，AppAppearance 改为跟随系统；BuildConfigurationTests:19 改为断言该键不存在；verify 增加 Release Info.plist 不含该键的检查。LaunchBackground.colorset 加深色外观 #171513。

③ APP-17-ios-apple（系统 Apple 按钮）和 LINT-STYLE-ios ③ 的 4 处直改必须已在主干。

来源：g4-02④、评审意见第 19 条。

**验收**

① 全部页面深色快照入库，对比度扫描 0 失败（扫描结果附在 PR）；② 执行 `plutil -extract UIUserInterfaceStyle raw App/Info.plist` 报键不存在，BuildConfigurationTests 新断言通过；③ LaunchBackground 有 dark 外观 #171513；④ 系统深色下 Release 包整 App 为深色；⑤ 合并记录显示 APP-17-ios-apple 与 LINT-STYLE-ios 早于本单。

</details>

<details>
<summary><b>DS-02-iOS-2</b> · P0 · DS-02-iOS（二）：补基础交互组件和目录页（FilterChip、输入框、勾选、开关等）</summary>

负责线：iOS；依赖：DS-02-iOS-1；承接：DS-02-iOS（D10-643 ②）；状态（2026-11-05）：进行中（D10-643 ② 已派，第二单）。

**范围**

在 Packages/DesignSystem 补齐以下组件：

- CouliCheckbox（圆形 18）、CouliRadio、CouliSwitch（系统 Toggle 套令牌）、Segmented；

- FilterChip：未选 / 已选（带对勾）/ 禁用，进组件库，替换 SearchComponents.swift:60 和 WithdrawVisualParts.swift:155 的私有实现；

- CouliTextField / TextArea：默认、输入中、错误、禁用四态，错误态为红框 + 图标 + 文字并能读屏报出；

- PhoneField（+86 后不加分隔线）、CodeInput（当前格用 border.active）、SearchField、Divider、CouliIconButton、ListRow、DisclosureRow、Timeline、TopTabs、Loading。

目录页按清单扩充，每个组件做浅色、深色、200% 三档；首页实际用的是 HomeProductCard，没有页面用的 ProductGridCard / ProductCardGrid 合并掉。目录覆盖测试读 component-spec.json（COMP-SPEC 合并前临时用安卓或鸿蒙的 inventory.tsv）。目录页只在 Debug / Staging 编译。

来源：g2-29、g4-02②、g3-31③④。

**验收**

① DesignSystem 的 public 类型里能 grep 到上列全部组件；② Features 下私有 FilterChip、WithdrawQuickChip 的定义为 0；③ 目录覆盖测试 iOS 行全绿；④ 新组件的浅 / 深 / 200% 快照基准入库，FilterChip 三态都有；⑤ 目录页不再引用没有页面使用的商品卡；⑥ Release 制品扫描不含目录页。

</details>

<details>
<summary><b>DS-02-iOS-3</b> · P0 · DS-02-iOS（三）：导航栏和半屏、弹窗改用系统容器，补登录、分享和业务组件</summary>

负责线：iOS；依赖：DS-02-iOS-2、COMP-SPEC-2；承接：DS-02-iOS（D10-643 ②）；状态（2026-11-05）：进行中（D10-643 ② 已派，第三单）。

**范围**

① NavBar 改为系统导航栏封装。订单、钱包、搜索、授权管理等页删掉 .toolbar(.hidden, for: .navigationBar)，改用它，边缘右滑返回要可用；不用系统栏的页面（Tab 根、登录、强更、目录页、商品详情）列白名单。商品详情按 v3 定稿「去掉标题、只留浮动返回键」：导航栏透明或隐藏，返回键浮在通栏主图上（圆底 40、命中区 44、底色 overlay.on-image，即 overlay.scrim 深色值），用 NavigationStack 的返回动作，边缘右滑返回照常可用。

② CouliSheet 改用系统 .sheet 加 presentationDetents 和系统把手；保护型禁止下滑和点遮罩关闭（interactiveDismissDisabled）。CouliDialog 去掉 ZStack 自绘的覆盖层，删掉写死的 easeOut 0.2s 和 300ms 回焦延时；标题对齐和间距按 COMP-SPEC-2。新增 AlertDialog、ActionMenu。

③ 登录组件：AgreementCheckRow、ThirdPartyLoginRow（用微信官方标识）、OAuthButton、LastLoginTag、BrandMark。

④ 业务组件：PriceTrendPanel 外壳、ShareMaterialPicker、ShareCopyEditor（勾选用圆形 CouliCheckbox）。

⑤ 目录页同步补上。

来源：g2-30、g3-31①②。

**验收**

① 执行 grep '.toolbar(.hidden, for: .navigationBar)'，只剩白名单文件（含商品详情）；商品详情快照有浮动返回键、没有标题栏；② DesignSystem 里 .transition(.move(edge: .bottom)) 和 restoreDelayNanos 为 0，单测断言 CouliSheet 走系统 sheet；③ XCUITest 在订单、钱包、详情页边缘右滑返回通过；④ 能 grep 到上列组件，目录覆盖测试 iOS 行全绿；⑤ 浅色、深色、200% 快照基准入库。

</details>

<details>
<summary><b>LINT-STYLE-ios</b> · P0 · LINT-STYLE（iOS）：SwiftLint 禁写死样式与系统控件直用，改正 4 处用透明度代替状态色</summary>

负责线：iOS；依赖：DS-02-iOS-1；承接：LINT-STYLE（D10-643 三端；iOS 份补派）。

**范围**

D10-643 通知的 iOS 段只列了 ① ②，本单按「三端 LINT-STYLE」补进 iOS 队列，排在 DS-02-iOS-1 之后。

① .swiftlint.yml 加 custom_rules，范围是 Packages/Features 和 App/Sources，排除 Debug 和 Generated。拦截这些写法：

- Color(red: / UIColor(red: / Color(hex 和十六进制色；

- .font(.system(size:；

- 数字 cornerRadius、.padding(数字、spacing: 数字、.frame(…: 数字、Feature 层「CGFloat = 数字」（白名单 0、1、2 和命中区扩展）；

- 对令牌色调用 .opacity( 作填充或文字色（白名单只留禁用态和插图）、.opacity(… ? 1 : 0.5) 表达禁用态；

- .buttonStyle(.plain)、Feature 里自定义 ButtonStyle 并在按下时改 opacity、把 onTapGesture 当按钮用。

用 SwiftLint baseline 以现状（约 128–132 处）建基线，只减不增，新增即失败。

② G1 规则（Toggle( / TextField( / SecureField( / TextEditor( / Picker( / .sheet( / .alert( / .confirmationDialog( / .fullScreenCover( / ProgressView()先只警告，由 DSX-60 转为失败。

③ 下面 4 处直接改正，不进基线（DSX-127 去锁前必须已合）：PrivacyCenterScreen.swift:134–136 和 BindPhoneDialogs.swift:69 的 statusWarningText.opacity(0.1) 改 statusWarningBackground（隐私中心提示条现在对比度只有 4.35:1）；ClipboardViews.swift:352 改 statusErrorBackground；WebScreens.swift:190 的 textInverse.opacity(0.8) 改用文字令牌。

来源：g1-09、g2-31、g3-33、g4-04。

**验收**

① CI 带 baseline 跑 swiftlint --strict；反例（新增 .padding(13)、cornerRadius: 10、.font(.system(size: 13))、.opacity(enabled ? 1 : 0.5)、.buttonStyle(.plain)）会让 CI 失败；② 执行 `git grep -nF -e 'opacity(0.1)' -e 'opacity(0.08)' -e 'textInverse.opacity' -- Packages App` 为 0；隐私中心提示条按令牌计算浅色 5.13:1、深色 7.59:1；③ 基线入库，有检查保证只减不增；④ OrdersScreen+Filters 的 0.6 和 14 处 .buttonStyle(.plain) 在基线内；⑤ 主干通过。

</details>

<details>
<summary><b>FU-DS-ios</b> · P0 · FU-DS（iOS 组件库）：ErrorState、EmptyState、NoticeBar、Toast、Skeleton 按状态目录统一</summary>

负责线：iOS；依赖：UI-STATES、COMP-SPEC-2、DSX-01、DS-02-iOS-3；承接：FU-DS（D10-643：UI-STATES 合并后派三端 ErrorState / Toast 统一）。

**范围**

开工前先按远端主干复核证据。在 DesignSystem 里做：

① ErrorState 加 kind（load_failed / network / maintenance / custom），由 kind 决定图标（load_failed 用刷新图标）；按钮默认实心主按钮、最大宽 240；尺寸按 COMP-SPEC-2 定的数值集中定义在组件库一处（v0.6.0 已发布则直接读 component.state.*；否则由 DSX-120 升锁时改读）。

② EmptyState 保留 density，按钮主次参数与另两端同名。

③ RetryBanner 和 NoticeBox 合成 NoticeBar（四种 tone，可带动作）。

④ couliToast 时长由组件决定，连续提示替换；Skeleton 按 COMP-SPEC-2 的口径。

⑤ 目录页展示全部 kind，浅深快照重录。

来源：g3-34。

**验收**

DS 公开 API 有 ErrorState(kind:) 和 NoticeBar(tone:)，RetryBanner / NoticeBox 不再公开；快照重录通过；按 StateLoadFailed / StateNetworkError 定稿 sha256 截图比对记为「一致」；Features 里没有向 couliToast 传时长的调用。

</details>

<details>
<summary><b>DSX-120</b> · P1 · iOS 令牌锁升 v0.6.0、锁定组件规范、生成器输出新类别</summary>

负责线：iOS（协同 设计）；依赖：DS-02-iOS-1、DSX-02、DSX-03、DSX-04、COMP-SPEC；承接：TOKENS-PIPE（iOS 份的 v0.6.0 跟进；原写在 FU-DS-LINE-HEIGHT-ios）。

**范围**

作为三端令牌锁升到 v0.6.0 的唯一一步（iOS），排在 DS-02-iOS-1 之后、读新令牌的各组件单之前：

① contract.lock 的 design_tokens 升到 couli v0.6.0 发布提交（DSX-02 合并点，含 DETAIL-V3-WB 的 v0.5.1 与 DSX-03、DSX-04 的键），快照随之更新；同时锁定 design/components/component-spec.json 的版本（component_spec）。

② 生成器输出 v0.6.0 的新类别：复合文字样式（text.*）、组件变体与状态（button.*、chip.*、tag.*、rebate-tag.large、验证码格、component.state.*、component.image.*）、layout、motion（duration、cubicBezier）、layer、color.chart.*、component.navbar.inverse.*、color.platform.tag.* 与 overlay.on-image（若 v3 合派单还没跟）、border.width、icon.stroke、opacity、letter-spacing。

③ 「生成物 vs 锁定源」逐值比对测试覆盖新类别（含 dark）；FU-DS-ios 已合的话，把其中与 component.state.* 同值的常量改读生成物。

④ 只出生成物和锁，不改组件外观；各组件改读新令牌由下游单做。

来源：评审意见第 13 条。

**验收**

contract.lock 的 design_tokens 指向 v0.6.0 发布提交，component_spec 有锁定版本；生成物的 version 为 0.6.0 且含上列类别；逐值比对测试通过；生成器重跑后 git diff 为空；TOKENS-LAG 对本端不再报 design_tokens 落后；ios-verify 通过。

</details>

<details>
<summary><b>DSX-140</b> · P1 · iOS CI 接入令牌与契约落后检查，改锁共享客户端向量</summary>

负责线：iOS；依赖：TOKENS-LAG、DSX-42、DS-02-iOS-1；承接：与 TOKENS-LAG（D10-643 ⑥）、DSX-42 相关（iOS 接入）。

**范围**

从 TOKENS-LAG、DSX-42 拆出的 iOS 份：① iOS CI 跑 TOKENS-LAG 的同一检查（先警告）；② contract.lock 的 files 表改锁 rebate-platform specs/client/ 下的共享向量（login、order、clipboard、format、home-sdui、me、oauth-login 和 *-visual-vectors），删掉本仓库各自复制、已分叉的版本，测试改读同步来的文件。

来源：g1-10、g2-44（iOS 份）。

**验收**

iOS CI 有一次 TOKENS-LAG 检查的运行记录；contract.lock 锁定的向量 sha256 与 rebate-platform 分发清单一致；仓库里没有向量的私有副本；ios-verify 通过。

</details>

<details>
<summary><b>DSX-53</b> · P1 · BRAND-02-iOS：品牌图标改用唯一 SVG 源，补启动页图形和品牌页快照</summary>

负责线：iOS；依赖：DSX-06、DS-02-iOS-1。

**范围**

品牌脸面和内容类图标改用由 design/icons SVG 生成的 Asset Catalog 矢量资源，替换 Foundation.swift 第 127 行起「暂用 SF Symbols 近似」的写法（底栏、钟表返利、「我的」宫格）；系统控件自带的那类保留 SF Symbols。改正 Foundation.swift:128 指错的 TODO(N-11)。Info.plist 的 UILaunchScreen 加 UIImageName（logo-mark），底色用 LaunchBackground。加品牌页快照（启动页、底栏、关于页 Logo，浅深两态）和图标一致性快照（每个图标 24pt 渲染后与 SVG 参考图比对）。

来源：g1-20。

**验收**

脚本列出全部 Image(systemName:)，都在「系统控件自带」清单内；Foundation.swift 里 TODO(N-11) 为 0；UILaunchScreen 有 UIImageName；快照入库并在 verify 里跑，图标与参考图像素差 ≤1%。

</details>

<details>
<summary><b>FU-DS-LINE-HEIGHT-ios</b> · P1 · iOS 组件库按规范与新令牌对齐：按钮、字重与行距、半屏标题、搜索胶囊、返利标签、提示条、动效与阴影</summary>

负责线：iOS；依赖：DS-02-iOS-1、LINT-STYLE-ios、DSX-120、COMP-SPEC、COMP-SPEC-2、DSX-119；承接：FU-DS-LINE-HEIGHT（iOS 部分并入本单）。

**范围**

作为 DS-03 的子项。v0.6.0 的锁和生成物由 DSX-120 交付，本单只改组件。

① CouliButton：次按钮默认字重 500（CouliButton.swift:51 现在是 semibold）；文字按钮内边距、禁用次按钮外观、加载转圈尺寸按规范改；按 DSX-119 裁定新增 tonal 变体；按钮图标尺寸按画板（FU-DS-BUTTON-ICON iOS 份）。

② 字重与行距：TokenTypography 各级默认字重按规范（:93 现在一律 regular），清掉 7 处没传字重的 .couliFont(.title)；CouliFontMetrics 按 line-height 计算行距（12 号多行应为 18）。

③ 半屏标题：SheetTitleStyle 删掉 prominent 20/700，PurchaseOverlay.swift:104、122 用半屏标题角色 22/600。

④ 搜索胶囊：SearchComponents.swift 改读 chip 令牌（32 高、12 号）。

⑤ 返利标签：PriceRebate.swift:160–164 改读 rebate-tag.large；PriceTag large 档的价格口径词字号与另两端一致（以 v3 为准）。

⑥ NoticeBox 改名为定稿名，保留一版弃用别名。

⑦ 自绘组件动效（Modals.swift:315 等）改读 motion；阴影按换算公式；Feature 层尺寸常量（OrderComponents.swift:72、WithdrawVisualParts.swift:186）改读组件令牌并移出 LINT 基线；CouliContentIcons.swift:80 描边改读 icon.stroke。

内容最大宽交给 DSX-54。参数化测试读 component-spec.json，全量快照重录一次。

来源：g1-23、g2-32。

**验收**

执行 `git grep -nF -e prominentSize -e 'chipHeight = CouliSpacing' -e 'chipHeight: CGFloat = 32' -- Packages App` 为 0；参数化测试覆盖按钮、文字档、提示条各行；12 号多行行距断言为 18；NoticeBox 只剩弃用别名；LINT-STYLE-ios 基线减少；受影响的快照重录，并用 DS-03 的抽数脚本与 ProductAuthSheet-v2、ProductJumpTip-v2、Search 画板逐项核数；DS 目录页显示新变体浅深两态。

</details>

<details>
<summary><b>DSX-54</b> · P1 · iOS 组件库 PageScaffold 与 layout 令牌，删模块级限宽常量</summary>

负责线：iOS；依赖：DSX-11、DS-02-iOS-3、DSX-120。

**范围**

layout 令牌由 DSX-120 生成。DesignSystem 提供 PageScaffold：导航栏 + 限宽居中的内容列 + 随键盘上移的底部固定区 + 安全区；钱包的 WalletPageScaffold 并入。LoginView.swift:17 的 560 和 8 处模块级的 600 改读令牌；弹层宽常量读 dialog 令牌。SwiftLint 加规则：Features 不得写限宽字面量、不得自写骨架，并建基线。

来源：g3-38（另含 g2-32、g4-41 的限宽部分）。

**验收**

执行 `git grep -n -E '(maxContentWidth|maxColumn): CGFloat = (600|560)' -- Packages App` 为 0；PageScaffold 在目录页有浅深和 200% 样例；大屏模拟器截图内容居中，宽度等于令牌值。

</details>

<details>
<summary><b>DSX-55</b> · P1 · iOS 登录页迁移到组件库（含启动页、强更页的品牌位）</summary>

负责线：iOS；依赖：DS-02-iOS-3。

**范围**

① LoginPieces.swift:24 的 CheckBox 换成 AgreementCheckRow。

② CodeCells.swift 换成 CodeInput（当前格用 border.active，字号按规范）。

③ LoginView+ThirdParty 换成 ThirdPartyLoginRow，用微信官方标识替代 SF bubble.left；禁用态改用组件自带的，不再用 opacity（:137、:170）。

④ LoginPieces、ShellViews、UpdatePages 里的「凑狸」方块换成 CouliLogo。

⑤ 手机号输入换成 PhoneField。

只换组件、不动排版，不等登录 v2 的整页视觉闸门。

来源：g2-33。

**验收**

执行 `git grep -n -E 'struct (CheckBox|CodeCells)|bubble[.]left|opacity[(]enabled' -- Packages/Features/Sources/Login` 为 0；Login、Shell、Update 里 .system(size: 为 0；LINT 基线里 Login 的 21 条清零；登录页浅深快照重录，勾选框为圆形。

</details>

<details>
<summary><b>DSX-56</b> · P1 · iOS 钱包页（钱包 / 提现 / 收款账号 / 记录 / 二次验证）迁移到组件库</summary>

负责线：iOS；依赖：DS-02-iOS-3、FU-DS-LINE-HEIGHT-ios。

**范围**

把以下私有件换成组件库的组件：

- 主卡 → WalletHeroCard；WalletStrip、WalletInfoStrip → NoticeBar；

- StepUpCodeCells → CodeInput；RadioMark / CheckMark → CouliRadio / CouliCheckbox；WalletInputField → CouliTextField；

- WithdrawQuickChip → FilterChip；WalletSpinner → Loading；RecordStatusPill → CouliTag 状态款；RecordDivider → Divider；WalletIconButton → CouliIconButton；

- StepUpSheet 直接调用的 .sheet → 保护型半屏。

再清理约 34 处字面量。只换展示组件、不动资金逻辑，按保护路径评审；状态键部分在 FU-DS-ios-fund。

来源：g2-34。

**验收**

上列私有 struct 的 grep 为 0；LINT 基线里 Wallet 的条目清零；钱包、提现关键页浅深快照重录，资金逻辑测试零改动。

</details>

<details>
<summary><b>DSX-57</b> · P1 · iOS 我的 / 设置页迁移到组件库</summary>

负责线：iOS；依赖：DS-02-iOS-3、FU-DS-LINE-HEIGHT-ios。

**范围**

以下私有件换成组件库的组件：MeHeroCard → WalletHeroCard / EntryGrid；MeSupport.swift:342 的提示条和 SettingsNoticeBar → NoticeBar；SettingsDivider → Divider；MeIconButton → CouliIconButton。设置里的开关改用 CouliSwitch。MeRouteViews.swift:43 的系统 .sheet 和自绘半屏统一改用组件库的半屏。

来源：g2-35。

**验收**

执行 `git grep -n -E 'struct (MeHeroCard|SettingsNoticeBar|SettingsDivider|MeIconButton)[^A-Za-z]'` 为 0；WalletHeroCard 在非 Debug 页面有调用；LINT 基线里 Me 的条目清零；快照重录。

</details>

<details>
<summary><b>DSX-58</b> · P1 · iOS 搜索 / 订单页控件迁移（筛选胶囊、状态胶囊、金额格、订单卡）</summary>

负责线：iOS；依赖：DS-02-iOS-3、FU-DS-LINE-HEIGHT-ios、W-33、DSX-119。

**范围**

① 删掉 SearchComponents.swift 的私有 FilterChip，以及 OrderChipLabel、OrderChipButtonStyle（按下时 0.6 透明度），两页都改用组件库 FilterChip；搜索页私有提示条换成 NoticeBar；下划线高 3 改读 tab-indicator.height（2）。

② OrderStatusPill、OrderDetailMutedPill 换成 CouliTag 状态款。

③ OrderListAmounts 换成 AmountGrid（rebateText），深色与另两端一致。

④ 40 高按钮按 DSX-119 的裁定改用变体；OrderCard 下沉到组件库，平台文字标签随 v3 合派同批做。

开工前先按远端主干复核。

来源：g2-36、g3-37。

**验收**

执行 `git grep -n -E 'struct (FilterChip|OrderChipLabel|OrderChipButtonStyle|OrderStatusPill|OrderDetailMutedPill)[^A-Za-z]' -- Packages/Features/Sources` 为 0；Features 里没有 isPressed ? 0.6；订单金额深色取值与另两端一致；LINT 基线里 Search、Orders 的条目清零；快照与 W-33 改齐的画板比对一致。

</details>

<details>
<summary><b>DSX-59</b> · P1 · iOS 首页 / 剪贴板控件迁移（浅底按钮、弹层宽、禁用态）</summary>

负责线：iOS；依赖：DS-02-iOS-3、FU-DS-LINE-HEIGHT-ios、DSX-119。

**范围**

HomeTonalButton 换成组件库的 tonal 变体（DSX-119 裁定、FU-DS-LINE-HEIGHT-ios 实现）；HomeMovingCards.swift:130 的弹层宽 400 改读常量；App/Sources/Clipboard 约 22 处字面量换成令牌；ClipboardCardList.swift:57 用 opacity 表示禁用，改用组件的禁用态；其余页面的 .buttonStyle(.plain) 改用 CouliPlainButtonStyle。

来源：g2-37。

**验收**

执行 `git grep -n -E 'struct HomeTonalButton|buttonStyle[(][.]plain[)]' -- Packages/Features/Sources App/Sources` 为 0；LINT 基线里 Home、Clipboard 的条目清零；浅深快照重录。

</details>

<details>
<summary><b>DSX-60</b> · P1 · iOS 守卫：G1 转为失败，新增 G2 启发式规则</summary>

负责线：iOS；依赖：DS-02-iOS-3、LINT-STYLE-ios。

**范围**

DS-02-iOS（二）（三）合并后，G1（Features 直接调用系统控件）从警告转为失败。新增 G2 规则：拦截页面里用 RoundedRectangle 加 checkmark 拼的勾选框、自绘的开关、把 onTapGesture 当按钮用。以现状为基线；DSX-55 到 DSX-59 合并后基线清零。

来源：g2-38。

**验收**

G1 为 error 级，反例让 CI 失败；G2 三条规则各有正例和反例；迁移任务合并后两份基线都为空。

</details>

<details>
<summary><b>FU-DS-ios-pages</b> · P1 · FU-DS（iOS 非资金页）：通用状态键、私有提示条、断网态、补缺失的状态行</summary>

负责线：iOS；依赖：FU-DS-ios、DSX-21；承接：FU-DS（页面段）。

**范围**

范围是 Home、Search、ProductDetail、Orders、Me（非金额部分）、RiskNotice、Appeal：

- home.loading、me.load_failed、order_list.network_error 等草稿键换成 state.* 和 net.unavailable；

- MeNoticeBar 换成组件库的 NoticeBar；

- 搜索和详情的传输失败改走断网态，不再回落到 error.50001；

- 按规格三行补订单详情、商品详情（含商品失效按钮键）、风险说明、申诉的状态；

- contract.lock 升到含 UI-STATES 的提交；

- SwiftLint 加 G7：Features 不得定义 *NoticeBar / *ErrorBar / *Toast / *ErrorState 视图，并建基线。

来源：g3-35。

**验收**

上述草稿键 grep 为 0；MeNoticeBar 为 0；G7 基线已提交且只减不增；快照和 compare 按状态目录判为「一致」。

</details>

<details>
<summary><b>FU-DS-ios-fund</b> · P1 · FU-DS（iOS 资金与金额页）：钱包、提现类状态键，「我的」金额缺失不补 0</summary>

负责线：iOS；依赖：FU-DS-ios、DSX-01、DSX-21；承接：FU-DS（页面段）。

**范围**

WalletDraftTable 里的 wallet.load_failed、withdraw.load_failed 换成 state.*；Withdraw、WithdrawRecords、PayoutAccount 的加载失败按规格三行和状态目录做；MeView.swift 可提现余额的 ?? 0 按 BR-TEXT-10 的缺失规则改。按资金页评审口径（RV2、保护路径批准）走。

来源：g3-36。

**验收**

上述草稿键为 0；MeView 不再对 withdrawable_fen 用 ?? 0，金额缺失有单测；资金页浅深快照重录。

</details>

<details>
<summary><b>FU-X-DLG-ios</b> · P1 · FU-X-DLG（iOS）：44001 拦截弹窗主次按定稿统一</summary>

负责线：iOS；依赖：W-33；承接：FU-X-DLG（android-visual-backlog-20261103 C1）。

**范围**

提现、收款账号、换手机号、登录验证码四处的 44001 拦截弹窗，按 W-33 的定稿统一主次；二次验证格子也按统一规格。属于敏感写和资金页，单独开小单并做红线证明。

来源：g3-39。

**验收**

四处弹窗快照与新画板一致；UI 测试断言主按钮文字；评审记录含红线证明。

</details>

<details>
<summary><b>DSX-61</b> · P1 · iOS 动效落地：motion 令牌、减弱动态入口、轮播与公告节奏、首页弹窗转场</summary>

负责线：iOS；依赖：DSX-13、DSX-26、DS-02-iOS-3、DSX-120。

**范围**

motion 令牌由 DSX-120 生成，自绘组件的动画只读令牌。DesignSystem 提供读取 accessibilityReduceMotion 的统一入口。HomeMovingCards 的轮播和公告在开启减弱动态或读屏时停止自动播放；间隔按 03 §6.3，取代 HomeJson 写死的 4000 和 max(1, …)。首页弹窗 fullScreenCover 改为无转场或淡入。目录页加减弱动态预览。SwiftLint 禁止 Features 写动效时长字面量。开工前先按远端主干复核。

来源：g3-40。

**验收**

DS 有统一入口，轮播和公告都引用它；HomeJson 里没有写死的 4000；UI 测试在开启减弱动态时断言轮播不自动翻页；首页弹窗录屏为淡入或无转场。

</details>

<details>
<summary><b>APP-10-ios</b> · P1 · APP-10（iOS）：AI 入口开关与「搜索」Tab、AI 卡布局、长按举报可见入口</summary>

负责线：iOS；依赖：DSX-16、DSX-22、DSX-12；承接：APP-10。

**范围**

接 agent.entry.visible：为 false 时，AI 助手 Tab 换成「搜索」，行为与安卓 TabShell 一致，外观按 DSX-16 的底栏稿。AI product_list 按 DSX-22 的口径渲染。长按举报按 DSX-12 补可见入口和读屏自定义操作。

来源：g3-41。

**验收**

开关两种取值的底栏快照与稿一致；UI 测试点「搜索」Tab 能打开 Search；Agent 卡快照覆盖 list（有 grid 的话也覆盖）；读屏能找到举报操作。

</details>

<details>
<summary><b>DSX-62</b> · P1 · iOS 无障碍守卫与自动审计（含 Web 返回键读屏名）</summary>

负责线：iOS（协同 质量）；依赖：DS-02-iOS-1。

**范围**

WebScreens.swift:18–19 的 backLabel 现在是英文 Back（两个容器共用，TODO(N-21)），改为取字典 web_page.back。DesignSystem 提供 accessibilityLabel 为必填参数的 CouliIconButton，Features 里的纯图标按钮都改用它。UITests 对 7 个关键页调用 performAccessibilityAudit()，先只报告，生成基线，只减不增。

来源：g4-40。

**验收**

Web 目录里英文 Back 为 0，单测断言两个容器的返回按钮 label 等于字典值；CouliIconButton 的 label 参数没有默认值；CI 产物含审计结果和基线。

</details>

<details>
<summary><b>DSX-63</b> · P1 · iOS 大字号快照覆盖与封顶档位统一</summary>

负责线：iOS（协同 设计）；依赖：DS-02-iOS-1、DSX-54。

**范围**

补 Login、Search、Agent、BindPhone 的 font200 快照（w320 / w390）。DesignSystem 定义统一的 Dynamic Type 封顶常量（导航类 AX2，约 200%）；HomeNativeHeader.swift:92 和 ShellViews.swift:141–142 现在用 AX3（约 235%，超出 03 口径），改用这个常量；Navigation、Wallet、MeHeroCard、SearchView+Header、WalletScreen+Hero 统一引用。限宽常量由 DSX-54 处理。

来源：g4-41。

**验收**

__Snapshots__ 有 Login / Search / Agent 的 font200 基准；accessibility3 为 0，封顶档位只在 DS 常量处定义；CI 日志证明快照套件实际执行，且失败会阻断合并。

</details>

<details>
<summary><b>APP-11-ios-sdui</b> · P1 · iOS 首页 SDUI 按契约解码（含渲染上报和弹窗读屏名）</summary>

负责线：iOS（协同 后端）；依赖：FU-X-HOME-PAGE-API-ios、CT-07e；承接：APP-11（iOS 补丁后缀）。

**范围**

契约快照同步 home-schema.json 和 home-golden。HomeJson.swift 按契约解码：

- product_grid 的 columns 接受 1 和 2；

- product_scroll / product_grid 接受 union_material；

- icon / image、rows、banner 必填项按契约；

- version 按契约登记的支持范围（现在 L77 写死为 1）；

- 视觉参数统一夹取。

删掉 HomeDecoded.swift 的 TODO(N-35)；上报渲染成功事件；popup.alt 接为弹窗读屏名。

来源：g4-42。

**验收**

单测遍历全部 golden，每份的保留 / 丢弃结果都与期望一致（含反例）；TODO(N-35) 为 0；渲染事件有单测；golden 截图与另两端并排对照（附图）。；解码遇到未知键忽略（单测）；由分发清单生成的 Tracker 含首页渲染成功事件。

</details>

<details>
<summary><b>APP-04-ios</b> · P1 · iOS Web 容器：跟随主题与字号、标题回退、反色标题栏</summary>

负责线：iOS（协同 后端、前端）；依赖：DS-02-iOS-1、DSX-25、CT-03-env、DSX-120；承接：APP-04（iOS 补丁后缀）。

**范围**

BridgeHost 实现 getEnv 的 color_scheme、font_scale 和变化事件，在 document start 注入 data-theme。WKWebView 字号按 DSX-25 的机制处理（WKWebView 默认不跟 Dynamic Type）。nav_style=dark 改用 component.navbar.inverse.*（WebScreens.swift L182、L186）。标题按 setNavBar，收到之前不显示 URL。按 CT-03-env 同步桥契约并重新生成桥类型；navbar.inverse 令牌由 DSX-120 的 v0.6.0 锁提供。

来源：g4-43。

**验收**

生成的桥类型含 color_scheme、font_scale；XCUITest 跑 conformance 页的主题、字号用例通过；深色下 nav_style=dark 对比度 ≥4.5:1（由测试计算）；WebScreens.swift 里「self == .dark ? CouliColor.textPrimary」为 0。

</details>

<details>
<summary><b>DSX-64</b> · P1 · iOS 远程图片收敛为一个加载器：缓存上限、按尺寸解码、统一请求策略、预取</summary>

负责线：iOS；依赖：DSX-31、DS-02-iOS-1、FU-X-HOME-PAGE-API-ios。

**范围**

按 DSX-31 的选型，在 DesignSystem 或 Core 里建唯一的远程图片加载器：

- 显式设置内存和磁盘上限，不再用 URLCache.shared 的默认值；解码缓存按字节计；

- 按显示尺寸 × scale 下采样；

- 请求策略照 03（只收 https、重定向只跳 https、类型和大小有上限、超时）；

- 提供预取接口。

以下三处都改走这个加载器，同一张图只下载、只缓存一次：ProductRemoteImage.swift:39 的 AsyncImage、AppHomeSupport.swift:39–47 的 AppHomeImages、WebScreens.swift:159 的标题栏背景图。首页拿到配置后预取首屏卡片图。MeSystem.swift 的缓存大小和清除要覆盖这个加载器的磁盘缓存。开工前按远端主干复核。

来源：g5-05。

**验收**

执行 rg 'AsyncImage|URLSession.shared.data'（排除测试和 Debug）只命中加载器内部；单测覆盖：容量等于 03 §12 的数值、按字节淘汰、下采样尺寸、拒绝 http 和跳到 http 的重定向、拒绝非 image 类型、首屏会预取、同一 URL 只请求一次；清除缓存后重新计算且包含图片缓存；ios-verify 通过。

</details>

<details>
<summary><b>DS-02-ios-image</b> · P1 · iOS 商品图收敛为 ProductImage：四态、令牌图框、渐显、缓存命中不闪</summary>

负责线：iOS；依赖：DSX-118、DSX-41、DSX-64、DS-02-iOS-3、DSX-120；承接：DS-02（iOS 组件库后续）。

**范围**

在 DesignSystem 里用 ProductImage 取代 ProductRemoteImage。以下位置都改用它：

- 首页网格和横滑（HomeProductCards.swift:109 写死了 132 / 104）；

- 详情主图（ProductDetailParts.swift:16 按 v3 改）；

- 订单图（OrderComponents.swift:175–200：补描边，删掉「商品图」占位字和 minimumScaleFactor）；

- 搜索列表图。

网络加载的图渐显，内存命中直接显示，减弱动态时不渐显。删掉没人调用的 ProductHeroImage，改写 ProductVisualOracleTests。目录页只展示 ProductImage；读屏名改用契约键。

来源：g5-06。

**验收**

执行 rg 'ProductRemoteImage|ProductHeroImage' 为 0；OrderComponents.swift 里没有 minimumScaleFactor；快照覆盖四态 × 网格 / 横滑 / 列表 / 订单 / 详情 × 浅深两态；单测断言缓存命中时第一帧就是图；图框尺寸等于令牌值（±1pt）；ios-verify 通过。

</details>

<details>
<summary><b>DSX-134</b> · P1 · iOS PriceTrendPanel 按共用几何向量和规则实现（与 iOS 详情 v3 同批）</summary>

负责线：iOS；依赖：DSX-37、DSX-38、CT-22-trend、DS-02-iOS-3、DSX-120、UI-STATES；承接：与 05 APP-16 相关（只做 iOS 的价格走势；收藏、热销榜和安卓份不在本单）。

**范围**

iOS 现在不画价格走势。在 DesignSystem 实现 PriceTrendPanel：五种状态；几何读 price-trend-geometry.vectors.json；颜色用 chart 令牌；摘要用 summary 模板；有来源行；读屏用 chart.a11y。用相同参数与另两端的快照对照。价格走势进入近期开发、不加开关（负责人 2026-10-05）；与 v3 合派（D10-641）的 iOS 详情同批派、同批合，详情 v3 的走势折叠行由本单交付；mode_price_fen 为 null 时最常见价两块和口径句不显示。

来源：g5-42。

**验收**

几何向量测试全过（读分发清单里的 price-trend-geometry.vectors.json）；mode 为 null 时不显示最常见价的快照；快照覆盖五态 × 浅深 × 200%；没有「最低」「最高」；三端同参数对照没有差异项；ios-verify 通过。

</details>

<details>
<summary><b>DSX-109</b> · P2 · iOS 防连点与加载防闪</summary>

负责线：iOS；依赖：DSX-12。

**范围**

DesignSystem 给可点区域加默认防连点（500ms 内只响应一次），Router 在导航进行中忽略重复推入。加载指示按 DSX-12：300ms 内完成不显示，显示后至少停留 400–500ms，按钮内加载除外。

来源：g3-42。

**验收**

单测：连点两次只推入一次；加载指示的时序单测覆盖「不显示」和「最短停留」两种情况。

</details>

<details>
<summary><b>QA-08-ios16</b> · P2 · iOS 16 快照基准与统一快照容差常量</summary>

负责线：iOS（协同 质量）；依赖：DSX-09；承接：与 05 QA-08 相关（iOS 16 与 iOS 26 各一套快照）。

**范围**

发版前（或夜间）加一轮 iOS 16 模拟器快照，至少覆盖组件库和 7 个关键页，基准放在单独目录（01 §7.5 和 QA-08 要求两套）。各套件的 precision 和 perceptualPrecision 抽成共用常量，数值按 DSX-09 的容差表。

来源：g4-61。

**验收**

__Snapshots__ 有 iOS 16 基准目录；precision 相关数字只出现在共用常量处；发版流水线有 iOS 16 一轮的运行记录。

</details>

<details>
<summary><b>APP-11-ios-lottie</b> · P2 · iOS 首页弹窗 Lottie 动效</summary>

负责线：iOS；依赖：APP-11-ios-sdui、DSX-98；承接：APP-11（Lottie 跟进，G-V06）。

**范围**

按 03 §6.3 和 BR-TEXT-26 接入 lottie-ios（与 iOS 16 的兼容性按官方文档核对，并补进 03 §6.3），只播放按 sha256 校验过的本地数据；减弱动态时用兜底图；关闭即停播并释放；去掉 HomeMovingCards.swift L112 的「Lottie 不做」；按 03 §3.5 判断是否要登记 SDK 清单。

来源：g4-62。

**验收**

两张 golden 截图（兜底图、动画首帧）；减弱动态和 sha256 不符时用兜底图的单测；「Lottie 不做」为 0。

</details>

<details>
<summary><b>DSX-110</b> · P2 · iOS 读屏用词改取契约字典</summary>

负责线：iOS；依赖：DSX-41。

**范围**

Login、Search、Shell、Trade、Clipboard、Update 等 DraftTexts 里，与 a11y.* 重复的返回、关闭、清除、加载中等键（如 LoginDraftTexts.swift:18–19）删掉，改取契约字典；新增的读屏名只能用字典键。

来源：g4-63。

**验收**

草稿文件里这些读屏键为 0；单测抽查读屏名取自字典。

</details>

<details>
<summary><b>APP-13-share-thumb</b> · P2 · share.open 微信卡片缩略图压到 ≤32KB（iOS）</summary>

负责线：iOS；依赖：CT-03-share；承接：与 05 APP-13 相关（iOS 份）。

**范围**

iOS 在分享单（APP-13）实现 share.open 时一起做，现在 BridgeHost 还是 TODO。三端统一规则：下载 thumb 后裁成方形 JPEG，逐级降质量直到 ≤32KB；title 截到 512 字节以内、description 截到 1KB 以内。读分发清单里三端共用的测试图向量。安卓、鸿蒙份见 DSX-128、DSX-129。

来源：g5-34。

**验收**

单测：同一组向量图压缩后 ≤32768 字节且是方形；过长的 title / desc 被截到上限；真机微信分享卡片带图的截图进 evidence。

</details>

### 安卓

<details>
<summary><b>TOKENS-PIPE-android</b> · P0 · TOKENS-PIPE（安卓）：升令牌锁，生成深色、组件、阴影，删手抄表和重名常量</summary>

负责线：安卓（协同 设计）；依赖：无；承接：TOKENS-PIPE（D10-643 ③，安卓）；状态（2026-11-05）：进行中（D10-643 ③ 已派；令牌锁直接升 v0.5.1，D10-665）。

**范围**

按 D10-643 ③ 做：

① contract.lock 的 design_tokens 从 18ad5b4 直接升到 couli f088f04（v0.5.1，D10-665），同时更新快照；之后跟到 v0.6.0 由 DSX-121 负责。若 LINT-STYLE-android 先合，本单删掉常量时顺手从它的基线里减掉失效条目。

② tools/codegen/gen.py 输出 dark、component（v0.4.0 多出的 22 个叶子）、shadow。删掉 CouliThemeTokens.kt 的手抄深色表（38 个值）、CouliComponentTokens 常量和过时注释「T13 深色提案…未进令牌源」。组件库自己补的颜色改读生成物，源里缺的交 design 进源。

③ Ds02ColorDisciplineTest 去掉对 CouliThemeTokens.kt 的豁免，只允许生成物写色值。

④ 卡片和轻提示阴影改读 shadow.card / floating（CouliFoundation.kt:161、FeedbackComponents.kt:258 现在用 textPrimary，深色下变成浅色光晕）。

⑤ iconSmall 同名不同值：CouliFoundation.kt:60 是 16，CouliThemeTokens.kt:153 是 14。统一为令牌 icon.small=14，迁移调用处，外观不变；CouliSizes 里其他与令牌同名不同值的项也改名对齐。

⑥ 回扫过时注释和常量（如 CouliFoundation.kt:57）。

⑦ ContractConformanceTest 增加「生成物 vs 锁定源」逐值比对，含 dark。

来源：g1-05、g2-09、g4-05。

**验收**

① contract.lock 的 design_tokens ≥ f088f04（v0.5.1，D10-665）；DesignTokens.kt 的 version ≥ 0.5.1，含 dark / component / shadow；② 执行 `git grep -nF -e 'T13 深色提案' -e 'textPrimary.copy(alpha = CouliAlpha.CARD_SHADOW)'` 为 0，CouliThemeTokens.kt 里没有手抄十六进制色；③ 色值纪律测试 Ds02ColorDisciplineTest 的允许名单只含 core/generated，并有一个违反样例被拦；④ 全仓 iconSmall 只有一处定义且值为 14，有单测断言没有同名不同值；⑤ 逐值比对测试覆盖 dark 并通过；⑥ 生成器重跑后 git diff 为空；除深色阴影外，既有快照 0 变化，或差异已在 PR 里登记。

</details>

<details>
<summary><b>LINT-STYLE-android</b> · P0 · LINT-STYLE（安卓）：页面层禁写死样式，系统控件守卫按基线失败</summary>

负责线：安卓；依赖：无；承接：LINT-STYLE（D10-643 ④，安卓）；状态（2026-11-05）：进行中（D10-643 ④ 已派）。

**范围**

按 D10-643 ④ 做：

① build-logic 新增页面样式字面量规则，范围是 feature/*、app、core 页面模块（wallet、clipboard、orders）的 src/main。禁止这些写法：Color(0x…) / Color.Black、N.dp / N.sp（含字面字号 数字.sp）、RoundedCornerShape(N)、Feature 层「数字 const val」当尺寸用（如 PILL_MIN_HEIGHT=22.dp、PHONE_BOX_MIN=52.dp）、具名参数里的魔法数（如 strokeWidth=2.dp）、feature / app 里的 indication = null。Ds02ColorDisciplineTest 的扫描目录扩到 feature 层。

② DesignSystemGuard（G1）名单补上 Button / TextButton / OutlinedButton / IconButton，范围扩到 app 和 core 页面模块，从只警告改为「违规集合 ⊆ 基线」才通过。

③ 与 TOKENS-PIPE-android 并行（D10-643 ③④ 同时派），按现状生成基线（约 146 处字面量、224 个页面数字常量），只减不增，新增即失败；清掉已不存在的陈旧条目，基线外的新增项一次性纳入并在 PR 写明原因；Ds02GuardBaselineTest 改为比对真实代码。

④ 守卫 README 写明 *VisualGuardTest 只是哈希冻结，不管样式。

LoginScreen 里 3 处 indication = null 进基线，由 APP-17-android 清掉。

来源：g1-07、g2-10、g3-43、g4-06。

**验收**

① 每条规则各有反例单测，在 feature/ 新增 12.dp、RoundedCornerShape(8.dp)、Color(0xFF000000)、Switch( / Button(、indication = null 都会让检查失败；② 基线测试断言每条都能在代码里匹配到，条目只减不增；③ DesignSystemGuard 注释不再写「当前只警告」；④ 主干上 ./gradlew lint detekt test 通过。

</details>

<details>
<summary><b>FU-DS-android</b> · P0 · FU-DS（安卓组件库）：状态组件统一，Toast 和状态标签按语义绑定图标与颜色</summary>

负责线：安卓（协同 设计）；依赖：UI-STATES、COMP-SPEC-2、DSX-01、TOKENS-PIPE-android；承接：FU-DS（D10-643：UI-STATES 合并后派，安卓份）。

**范围**

在 core/designsystem 里做：

① ErrorState 加 kind 决定图标（不再固定 alert）；按钮默认实心主按钮（现在 primary 默认是 false）；上下留白 32（现在 space6 是 24）；最大宽 240；尺寸按 COMP-SPEC-2 定的数值集中定义在组件库一处（v0.6.0 已发布则直接读 component.state.*；否则由 DSX-121 升锁时改读）。

② EmptyState 加 density，按钮主次参数与另两端同名。

③ WalletComponents.kt:670 的 InfoStrip 并入 NoticeBar（四种 tone，可带动作），保留一版弃用别名。

④ CouliToast 时长由组件决定，页面不再传；连续提示替换；去掉独立的 iconTint 参数，按语义类型绑定图标和颜色。WalletUi.kt:410、OrderListScreen.kt:759、HomeScreen.kt:258 的错误提示改传错误类型（现在错误三角是成功绿）。

⑤ CouliTag 状态款自动带图标。

⑥ Skeleton 按 COMP-SPEC-2 的口径。

⑦ 目录页加灰度对照截图，Compose 截图基准浅深重录。

来源：g3-44、g4-45。

**验收**

① ErrorState 默认主按钮且有 kind 参数，FeedbackComponents 里没有 space6 上下留白；② InfoStrip 只剩弃用别名；③ feature/** 里传 iconTint 为 0，错误类型 Toast 图标为 statusErrorText 色（快照）；④ CouliTag 状态款不传 icon 也会渲染图标（单测）；⑤ 截图基准（含灰度对照）重录，按定稿比对记为「一致」。

</details>

<details>
<summary><b>DSX-121</b> · P1 · 安卓令牌锁升 v0.6.0、锁定组件规范、生成器输出新类别</summary>

负责线：安卓（协同 设计）；依赖：TOKENS-PIPE-android、DSX-02、DSX-03、DSX-04、COMP-SPEC；承接：TOKENS-PIPE（安卓份的 v0.6.0 跟进；原写在 DSX-65）。

**范围**

作为三端令牌锁升到 v0.6.0 的唯一一步（安卓），排在 TOKENS-PIPE-android 之后、读新令牌的各组件单之前：

① contract.lock 的 design_tokens 升到 couli v0.6.0 发布提交（DSX-02 合并点，含 DETAIL-V3-WB 的 v0.5.1 与 DSX-03、DSX-04 的键），快照随之更新；同时锁定 design/components/component-spec.json 的版本（component_spec）。

② 生成器输出 v0.6.0 的新类别：复合文字样式（text.*）、组件变体与状态（button.*、chip.*、tag.*、rebate-tag.large、验证码格、component.state.*、component.image.*）、layout、motion（duration、cubicBezier）、layer、color.chart.*、component.navbar.inverse.*、color.platform.tag.* 与 overlay.on-image（若 v3 合派单还没跟）、border.width、icon.stroke、opacity、letter-spacing。

③ 「生成物 vs 锁定源」逐值比对测试覆盖新类别（含 dark）；FU-DS-android 已合的话，把其中与 component.state.* 同值的常量改读生成物。

④ 只出生成物和锁，不改组件外观；各组件改读新令牌由下游单做。

来源：评审意见第 13 条。

**验收**

contract.lock 的 design_tokens 指向 v0.6.0 发布提交，component_spec 有锁定版本；生成物的 version 为 0.6.0 且含上列类别；逐值比对测试通过；生成器重跑后 git diff 为空；TOKENS-LAG 对本端不再报 design_tokens 落后；./gradlew lint detekt test 通过。

</details>

<details>
<summary><b>DSX-141</b> · P1 · 安卓 CI 接入令牌与契约落后检查，改锁共享客户端向量</summary>

负责线：安卓；依赖：TOKENS-LAG、DSX-42、TOKENS-PIPE-android；承接：与 TOKENS-LAG（D10-643 ⑥）、DSX-42 相关（安卓接入）。

**范围**

从 TOKENS-LAG、DSX-42 拆出的安卓份：① 安卓 CI 跑 TOKENS-LAG 的同一检查（先警告）；② tools/contracts/sync.sh 和 contract.lock 改锁 rebate-platform specs/client/ 下的共享向量，删掉本仓库已分叉的副本，测试改读同步来的文件。

来源：g1-10、g2-44（安卓份）。

**验收**

安卓 CI 有一次 TOKENS-LAG 检查的运行记录；contract.lock 锁定的向量 sha256 与分发清单一致；仓库里没有向量的私有副本；./gradlew test 通过。

</details>

<details>
<summary><b>FU-DS-ANDROID-SYMBOLS</b> · P1 · BRAND-02-安卓：CouliIcons 改由唯一 SVG 源生成，接 SplashScreen，加品牌页快照</summary>

负责线：安卓；依赖：DSX-06、TOKENS-PIPE-android；承接：FU-DS-ANDROID-SYMBOLS。

**范围**

① CouliIcons.kt 的品牌脸面和内容类图标改由 design/icons SVG 生成，生成文件头注明来源提交；删掉各自补画、与鸿蒙形状不同的路径（钱包第 185–189 行、心形、铃铛、趋势、流水等）；本任务按 DSX-06 的口径结案。

② themes.xml 配 Android 12 SplashScreen：底色浅色 canvas、values-night 用 #171513，图形用 logo-mark。如果需要 core-splashscreen 依赖，先按 11 §2.3 开 deps 任务。

③ 加品牌页快照和图标一致性快照。

来源：g1-21。

**验收**

清单内的图标全部来自生成文件，手写 path 为 0；values 和 values-night 都有 windowSplashScreen* 属性；Android 12 以上模拟器冷启动截图（浅深各一张）显示 logo-mark 和正确底色；快照入库。

</details>

<details>
<summary><b>DSX-65</b> · P1 · 安卓组件库按规范与新令牌对齐：按钮、输入、胶囊、半屏标题、返利标签、Dialog、阴影与字距</summary>

负责线：安卓；依赖：TOKENS-PIPE-android、LINT-STYLE-android、DSX-121、COMP-SPEC、COMP-SPEC-2、DSX-119。

**范围**

作为 DS-03 的子项。v0.6.0 的锁和生成物由 DSX-121 交付，本单只改组件。

① CouliButtons：紧凑按钮视觉高 44，命中区用扩展区做到 48（CouliButtons.kt:86 现在把 defaultMinSize(48) 写在 background 前面，背景被撑到 48），一并了结 F-AND-78 / FU-DS「按钮紧凑高度」。文字按钮内边距（现 8×4）、禁用次按钮外观、加载转圈尺寸按规范改；按 DSX-119 裁定新增 tonal 变体，按钮图标尺寸按画板（FU-DS-BUTTON-ICON 安卓份），HomeNativeHeader.kt:135 改用它；ON_SOLID 改名为 onSolid，保留一版弃用别名。

② CouliInputs：PhoneField 去掉分隔线，CodeInput 圆角按规范。

③ CouliFilterChip：32 高、左右 12、12/18、选中 brand.emphasis 500。

④ 半屏标题：删掉 CouliFoundation.kt:120–123 的 sheetTitle 20/700，TradeUi.kt:486、578 用 22/600。

⑤ PriceComponents.kt:270、278 的大号返利标签改读 rebate-tag.large。

⑥ CouliDialog 的元素间距（:408 现为 12）和标题对齐默认值按规范改。

⑦ 卡片 elevation 按换算规则；字距 2.sp / 1.sp 和 CouliIcons.kt:335 的描边改读令牌；RiskAppealParts 的 PILL_MIN_HEIGHT、PhoneChangeParts 的 PHONE_BOX_MIN 改读组件令牌并移出 LINT 基线。

⑧ 字重与行距（FU-DS-LINE-HEIGHT 安卓份，backlog C5）：先只读核 CouliTypography，12 号多行行距按画板 18，各级默认字重按规范。

⑨ 组件库可选参数（backlog C3）：CouliTextField 多行最小高与顶对齐、clearButtonModifier KDoc、开放焦点回落工具，照 D10-401 只加带默认值的参数。

Toast 时长常量的清理在 FU-DS-android-pages，内容最大宽的清理在 DSX-66。参数化测试读 component-spec.json；目录页浅深快照重录。

来源：g1-24、g2-11、g2-12（Dialog 部分）。

**验收**

参数化测试覆盖按钮、输入、胶囊、Dialog、文字档各行；12 号多行行距断言为 18；紧凑按钮快照视觉高 44、命中区测试为 48；执行 `git grep -nF -e 'PILL_MIN_HEIGHT = ' -e 'PHONE_BOX_MIN = '` 为 0（或只剩引用生成令牌的定义）；ON_SOLID 只剩弃用别名；HomeNativeHeader 不再自绘浅底按钮；LINT 基线行数减少；受影响快照重录，并用抽数脚本与画板核数。

</details>

<details>
<summary><b>DSX-66</b> · P1 · 安卓组件库 PageScaffold 与 layout 令牌，删模块级限宽和弹层宽常量</summary>

负责线：安卓；依赖：DSX-11、DSX-121。

**范围**

layout 令牌由 DSX-121 生成。core/designsystem 提供 PageScaffold：导航栏通栏、不受限宽；内容列限宽居中；底部栏用 imePadding；处理安全区。MeUi 二级页骨架、WalletUi、OrderDetailScreen 改用它。以下常量改读令牌：9 处 CONTENT_MAX_WIDTH / MAX_WIDTH = 600、LoginScreen / BindPhoneScreen 的 480、MeUi 的 ME_MAX_WIDTH、CouliOverlays 的 ALERT_MAX_WIDTH 560、PrivacyPrompt 的 342、TradeUi 的 320、HomeScreen 的 POPUP_MAX_WIDTH 400。lint 加规则：Feature 不得写限宽常量、不得自写骨架，并建基线。底部 Tab 换系统 NavigationBar（backlog C6，DS-02 底部 Tab），颜色读令牌。

来源：g3-48（另含 g1-24、g2-12、g4-48 的限宽部分）。

**验收**

执行 `git grep -n -E 'MAX_WIDTH = [0-9]' -- feature app` 为 0；≥600dp 模拟器截图内容居中、导航栏通栏；PageScaffold 目录页有浅深样例；底部 Tab 用 NavigationBar，截图基准重录。

</details>

<details>
<summary><b>APP-17-android</b> · P1 · APP-17（安卓）：登录与绑手机页迁移到组件库，恢复按压反馈（含隐私弹窗、强更页的品牌位）</summary>

负责线：安卓；依赖：DSX-65、LINT-STYLE-android；承接：APP-17（安卓登录 v2 视觉单 APP-17b 的组件部分）。

**范围**

① LoginScreen.kt 删掉与组件库同名的私有件 BrandMark、PhoneField、CheckMark、TextLink，L446–455 自拼的协议行改用 AgreementCheckRow（圆形 18）。

② BindPhoneField 换成 PhoneField；验证码格换成 CodeInput（当前格用 border.active）。

③ 第三方登录换成 ThirdPartyLoginRow（oauth.gap 32），删掉 OAUTH_GAP = 40。

④ 去掉 L452、L554、L714 的 indication = null，恢复系统水波纹。

⑤ 手机号输入的字号按规范改。

⑥ PrivacyPrompt.kt:386 和 UpdatePages.kt:293 的「凑狸」方块换成 CouliLogo。

只换组件、不动排版，不等登录 v2 的整页视觉闸门（负责人 11-05「组件按规划统一，这类不用问」）；APP-17b 开工时直接沿用。

来源：g2-13、g3-49。

**验收**

执行 `git grep -n -E 'fun (BrandMark|PhoneField|CheckMark|TextLink|BindPhoneField)[(]' -- feature/login` 为 0；feature/login 里 indication = null 为 0；OAUTH_GAP / BRAND_RADIUS / BRAND_TILE_RADIUS 为 0；第三方圆钮有按压测试；LINT 和 G1 基线里 feature/login 的条目清零；登录、绑手机页浅深快照重录，勾选框为圆形。

</details>

<details>
<summary><b>DSX-67</b> · P1 · 安卓搜索 / 订单页改用组件库：筛选胶囊、搜索框、下划线</summary>

负责线：安卓；依赖：DSX-65、W-33。

**范围**

SearchVisualParts.kt:153 的 SearchFilterCapsule 和 OrderListHeader.kt 的自写胶囊都改用 CouliFilterChip；SearchVisualParts.kt:304 的 BasicTextField 换成 SearchField / CouliTextField；UNDERLINE = 2 改读 tab-indicator.height。

来源：g2-14、g3-47。

**验收**

执行 `git grep -n -E 'SearchFilterCapsule|BasicTextField[(]' -- feature/search` 为 0；feature/orders 没有自写胶囊分支；CouliFilterChip 在页面层有引用；G1 / LINT 基线里相应条目清零；两页截图和 search-visual-vectors 与改齐的画板一致。

</details>

<details>
<summary><b>DSX-68</b> · P1 · 安卓我的 / 设置 / 换号 / 订单 / 申诉页控件迁移</summary>

负责线：安卓；依赖：DSX-65、DSX-119。

**范围**

MeSwitch 换成 CouliSwitch；PhoneChangeParts 和 AccountUi 里的 BasicTextField 换成 PhoneField / CouliTextField；两个 StatusPill 换成 CouliTag 状态款；OrderListCard 的 OrderCard 下沉到组件库（平台标签随 v3 合派同批做）；订单详情用 Timeline、CouliDivider、ListRow。

来源：g2-15。

**验收**

执行 `git grep -n -E 'fun (MeSwitch|StatusPill)[(]' -- feature` 为 0；feature/me 里 BasicTextField( 为 0；OrderCard 只在 core/designsystem 定义；PR 写明基线条目的前后数字；快照重录。

</details>

<details>
<summary><b>DSX-69</b> · P1 · 安卓守卫 G2：自绘开关、方块勾选框、去掉按压反馈</summary>

负责线：安卓；依赖：LINT-STYLE-android。

**范围**

在 build-logic 加组件清单 §6 G2 的三条规则：自绘开关形状（52×32 胶囊加圆点）、用圆角方块加勾图标拼的勾选框、indication = null。以现状为基线；APP-17-android 和 DSX-68 合并后基线清零，规则转为不带基线的失败级。

来源：g2-16。

**验收**

三条规则各有正例和反例；反例让检查失败；迁移合并后基线为空。

</details>

<details>
<summary><b>FU-DS-android-pages</b> · P1 · FU-DS（安卓非资金页）：删页面轻提示时长常量、私有提示条和草稿状态键</summary>

负责线：安卓；依赖：FU-DS-android、DSX-21；承接：FU-DS（页面段）。

**范围**

① 删掉 feature 和 app 里的 TOAST_MS / TOAST_MILLIS 常量（HomeScreen、LoginScreen、BindPhoneScreen、AgentScreen、CsSheets、MeUi、OrderListScreen、WalletUi、AuthManage、TradeUi、LoginPages 等约 10 处），改用组件库的 Toast；首页轻提示从 BottomCenter 改到规范位置。

② SearchScreen 的私有 NoticeBar 换成组件库的。

③ order_list.network_error 等草稿键换成 state.* 和 net.unavailable。

④ 按规格三行补 DeleteAccount 等页面的状态；整页加载失败 / 断网改用 DS ErrorState（backlog C4）。

⑤ 锁升到含 UI-STATES 的提交。

⑥ detekt 加 G7：Feature 不得定义 *NoticeBar / *ErrorBar / *Toast，并建基线。

来源：g3-45（另含 g1-24、g2-12 的 Toast 部分）。

**验收**

执行 grep 'const val TOAST_(MS|MILLIS)'，在 feature 和 app/src/main 为 0；SearchScreen 没有 private fun NoticeBar；G7 基线已提交；截图基准更新。

</details>

<details>
<summary><b>FU-DS-android-fund</b> · P1 · FU-DS（安卓资金与金额页）：钱包 ErrorBar 换组件库，提现类状态键统一，金额缺失不补 0</summary>

负责线：安卓；依赖：FU-DS-android、DSX-01、DSX-21；承接：FU-DS（页面段）。

**范围**

WalletUi.kt 的私有 ErrorBar 换成 NoticeBar，原来用 InfoStrip 的地方也改用 NoticeBar；WalletTexts 的 withdraw.load_failed 等换成 state.*；提现、提现记录、收款账号页的加载失败按规格三行做；核对「我的」可提现金额字段缺失时是否补 0，按 BR-TEXT-10 改。按资金页评审口径走。

来源：g3-46。

**验收**

feature/wallet 没有 internal fun ErrorBar，也不再引用 InfoStrip；草稿键为 0；金额缺失有单测；资金页浅深截图基准重录。

</details>

<details>
<summary><b>FU-X-DLG-android</b> · P1 · FU-X-DLG（安卓）：44001 拦截弹窗主次按定稿统一</summary>

负责线：安卓；依赖：W-33；承接：FU-X-DLG（android-visual-backlog-20261103 C1）。

**范围**

提现、收款账号、换手机号、登录验证码四处的 44001 拦截弹窗按 W-33 定稿统一主次，二次验证格子按统一规格。单独开小单并做红线证明。

来源：g3-50。

**验收**

四处截图与新画板一致；UI 测试断言主按钮文字；评审记录含红线证明。

</details>

<details>
<summary><b>DSX-70</b> · P1 · 安卓动效落地：NavHost 显式转场、减弱动态入口、轮播与公告节奏</summary>

负责线：安卓；依赖：DSX-13、DSX-26、DSX-121。

**范围**

motion 令牌由 DSX-121 生成。AppNavHost 显式配置 enter / exit / popEnter / popExit，取代 navigation-compose 2.9.8 默认的淡入。DS 提供读取系统动画时长缩放的统一入口。HomeCards 的轮播和公告在减弱动态、读屏、页面不可见时停止自动播放；间隔按 03 §6.3，取代 NOTICE_SCROLL_MS = 3_000L；轮播加下限。

来源：g3-51。

**验收**

AppNavHost 有显式转场参数；HomeCards 里没有 NOTICE_SCROLL_MS 字面量；动画缩放为 0 时，Robolectric 断言不自动翻页；转场录屏随 QA-12 归档。

</details>

<details>
<summary><b>APP-10v-android</b> · P1 · APP-10v（安卓）：AI 商品卡 grid 按定稿口径，长按举报补可见入口</summary>

负责线：安卓；依赖：DSX-22、DSX-12；承接：APP-10v（android-visual-backlog A4）。

**范围**

AgentCards.kt 的 grid 分支（L664 起）按 DSX-22 的口径改；长按举报在 onLongClickLabel 之外，按 DSX-12 补可见入口。

来源：g3-52。

**验收**

Agent 卡截图覆盖 list 和 grid，并与稿一致；UI 测试能从可见入口打开举报。

</details>

<details>
<summary><b>DSX-71</b> · P1 · 安卓无障碍守卫与自动检查（含 Web 返回键读屏名、快照显式容差）</summary>

负责线：安卓（协同 质量）；依赖：无。

**范围**

WebScreens.kt:82 的 BACK_LABEL_KEY 是 external_page.back，字典里没有这个键，TalkBack 只读「按钮」。改为 web_page.back，并去掉回落空串的写法。CouliIconButton 在 label 为空时，调试构建直接报错。Compose / Robolectric 测试启用 ATF 无障碍检查，先只报告，生成基线。Roborazzi 按 DSX-09 显式配置比较阈值。

来源：g4-44。

**验收**

单测断言返回按钮 contentDescription 等于字典值；源码里 external_page.back 为 0；空 label 调用会抛错；测试日志含 ATF 结果，基线已入库；有 Roborazzi 阈值配置，CI 日志证明快照比较实际执行且失败会阻断合并。

</details>

<details>
<summary><b>APP-11-android-sdui</b> · P1 · 安卓首页 SDUI 按契约解码（含渲染上报和弹窗读屏名）</summary>

负责线：安卓（协同 后端）；依赖：CT-07e；承接：APP-11（Android 补丁后缀）。

**范围**

tools/contracts/sync.sh L113–140 的取文件清单加上 home-schema.json 和 home-golden，contract.lock 记下哈希。HomeJson.kt 按契约改：columns（L262）、product_scroll title（L277）、height_ratio 上限（L248）、icon / image（L404）、版本范围（L210 MAX_VERSION 改读契约），视觉参数统一夹取。加 golden 正反例单测；上报渲染成功事件；popup.alt 接为读屏名。

来源：g4-46。

**验收**

单测遍历全部 golden，结果与期望一致；sync.sh 清单含这两项，contract.lock 记了哈希；渲染事件有单测；golden 截图与另两端并排对照。；解码遇到未知键忽略（单测）；由分发清单生成的 Tracker 含首页渲染成功事件。

</details>

<details>
<summary><b>APP-04-android</b> · P1 · 安卓 WebView：跟随主题与字号、标题回退、反色标题栏</summary>

负责线：安卓（协同 后端、前端）；依赖：DSX-25、CT-03-env、DSX-121；承接：APP-04（Android 补丁后缀）。

**范围**

夜间改用 isLightTheme=false 的主题（themes.xml L8 现在继承 Light 且 forceDarkAllowed=false）。BridgeHost 实现 getEnv 的新字段和变化事件，注入 data-theme。字号只放大一次：核对 textZoom 默认随系统，避免与根字号叠加。WebScreens.kt L463、L473 的 nav_style=dark 改用 navbar.inverse；L242 的标题回退不显示 URL。按 CT-03-env 同步桥契约并重新生成桥类型；navbar.inverse 令牌由 DSX-121 的 v0.6.0 锁提供。

来源：g4-47。

**验收**

生成的桥类型含 color_scheme、font_scale；conformance 页的主题、字号用例通过；深色下 nav_style=dark 对比度 ≥4.5:1；200% 时测试断言只放大一处；pageTitle 是 URL 时标题为空的用例通过。

</details>

<details>
<summary><b>DSX-72</b> · P1 · 安卓配置变化不丢状态，补登录页大字号与宽屏快照</summary>

负责线：安卓（协同 设计）；依赖：TOKENS-PIPE-android、DSX-66。

**范围**

登录、提现、订单列表补 StateRestorationTester 用例，保证已填内容和滚动位置不丢，可照搜索页 SearchScreenReviewR1Test 的写法。登录页补 font200 和 w840 快照，w840 断言内容区宽度等于令牌值。限宽常量由 DSX-66 处理。

来源：g4-48。

**验收**

三个页面的 StateRestorationTester 用例通过；登录页 font200 / w840 快照入基准；w840 内容区宽度等于令牌值。

</details>

<details>
<summary><b>DSX-73</b> · P1 · 安卓图片加载下沉到 core：磁盘缓存、按字节内存缓存、按显示尺寸解码，标题栏背景图可用</summary>

负责线：安卓；依赖：DSX-31。

**范围**

按 DSX-31 的选型，把 AppProductImages.kt 下沉到 core：

- 加磁盘缓存并设上限（release 的 VariantHttpClient 现在没配 cache）；

- 内存缓存改为按字节计，替代按张数计的 LruCache(48)；

- 按目标尺寸 × 密度算采样率，替代 MAX_EDGE=1024；

- 请求策略照 03；

- 提供预取接口，由首页首屏调用。

NavBarState 的 bg_image 改走加载器，不再回 90001，相应断言改为成功。AndroidMeSystem 的缓存大小和清除要包含图片磁盘缓存。

来源：g5-07。

**验收**

执行 rg 'LruCache&lt;String, ImageBitmap>|CACHE_ENTRIES' 为 0；Robolectric 测试覆盖：按字节淘汰、冷启动磁盘命中不发请求、采样尺寸、bg_image 能应用、清除后 cacheBytes 下降；在 Redmi Note 13 5G 上抽测列表滚动内存，结果进 evidence；verify 通过。

</details>

<details>
<summary><b>DS-02-android-image</b> · P1 · 安卓商品图收敛为 ProductImage：去掉占位字、图框取令牌、渐显不闪，首页角标改正</summary>

负责线：安卓；依赖：DSX-118、DSX-41、DSX-73、DSX-121；承接：DS-02（安卓组件库后续）。

**范围**

① ProductThumbnail 去掉 label 参数和 :402 的 Text，四态按规范；:373 produceState 的初值改为同步读内存缓存；加渐显，减弱动态时不渐显。

② GRID_IMAGE_RATIO=1.19 和 HERO_RATIO 改从 component.image 取（详情按 v3）。

③ HomeCards.kt:150 的角标改用 OUTLINE，:237 的 banner 角标从 TopEnd 改到 TopStart。

④ 收编 CouliLists 的 ImagePlaceholder，分享素材占位改用 ProductImage。

⑤ 删掉 SearchDraftTexts.kt:31 和 OrderTexts.kt:122 的占位字键，读屏名改用契约键。

来源：g5-08。

**验收**

执行 rg 'GRID_IMAGE_RATIO|HERO_RATIO|image_placeholder'（排除测试）为 0；单测断言角标是 OUTLINE 且在 TopStart；ds02 快照重录，覆盖四态 × 各尺寸 × 浅深；单测断言缓存命中时第一帧没有占位；verify 通过。

</details>

<details>
<summary><b>APP-12-push</b> · P1 · 安卓接 MobPush 时用专用通知小图标和品牌强调色</summary>

负责线：安卓；依赖：DSX-36；承接：APP-12。

**范围**

把 DSX-36 的剪影做成单色矢量 res/drawable/ic_stat_couli。core/push 接 MobPush 时（现在是 TODO(N-33)），把它设为默认通知小图标；强调色用 brand.primary；渠道名取字典键。不得使用 ic_launcher_*。

来源：g5-25。

**验收**

合并后的清单里默认通知图标指向 ic_stat_couli；单测或 Lint 断言它是单色透明底；本地通知截图（状态栏不是白块）进 evidence。

</details>

<details>
<summary><b>DS-02-android-trend</b> · P1 · 安卓 PriceTrendPanel 改正：去掉「最低 / 最高」，按日期和刻度画阶梯线，补失败态和来源行</summary>

负责线：安卓；依赖：DSX-37、DSX-38、CT-22-trend、UI-STATES、DSX-121；承接：DS-02（安卓组件库后续）。

**范围**

改 CouliBusiness.kt：

- :37 的 KDoc 去掉「最低 / 最高」；

- 组件接收 start_date、current_fen、low_fen 和模板键 price_trend.summary，自己按 BR-TEXT-10 / 11 格式化；

- TrendLine（:81–89）改读共用的几何向量：按日期落点、阶梯线、缺失日断开、刻度和网格；

- 线色改用 chart 令牌；

- 加 Error 态和来源行，摘要字号档按规则统一。

改正 CatalogComponentSample.kt:572 的样例，重录 PriceTrendPanel 基准；加单测断言不含禁用词。

来源：g5-40。

**验收**

在 core/designsystem 和 app/src/debugFeatures 里 rg '最低|最高' 为 0；几何向量测试全过（读分发清单里的向量文件）；快照含 Error 态，覆盖浅深和 200%；verify 通过。

</details>

<details>
<summary><b>DSX-128</b> · P2 · share.open 微信卡片缩略图压到 ≤32KB（安卓）</summary>

负责线：安卓；依赖：CT-03-share；承接：与 05 APP-13 相关（安卓份）。

**范围**

安卓在分享单（APP-13）实现 share.open 时一起做。规则同 APP-13-share-thumb：方形 JPEG、逐级降质量直到 ≤32KB；title ≤512 字节、description ≤1KB；读同一组测试图向量。

来源：g5-34（安卓份）。

**验收**

单测：同一组向量图压缩后 ≤32768 字节且是方形；过长的 title / desc 被截到上限；真机微信分享卡片带图的截图进 evidence。

</details>

<details>
<summary><b>DSX-111</b> · P2 · 安卓防连点与加载防闪</summary>

负责线：安卓；依赖：DSX-12。

**范围**

core/designsystem 的可点区域默认防连点（500ms 内只响应一次），导航进行中忽略重复导航（可结合 launchSingleTop）；加载指示按 DSX-12 的不显示阈值和最短停留做，按钮内加载除外。

来源：g3-53。

**验收**

单测：连点两次只导航一次；加载指示有时序单测。

</details>

<details>
<summary><b>APP-11-android-lottie</b> · P2 · 安卓首页弹窗 Lottie 动效</summary>

负责线：安卓；依赖：APP-11-android-sdui、DSX-98；承接：APP-11（Android，Lottie 跟进）。

**范围**

接入 lottie-android；HomeJson.kt 的 popup() 读 lottie 键，按 sha256 校验缓存；系统动画缩放为 0 时用兜底图；关闭即停播释放；序列化忽略未知键；按 03 §3.5 判断是否登记 SDK 清单。

来源：g4-64。

**验收**

两张 golden 截图；动画缩放为 0 和 sha256 不符时用兜底图的单测；popup 解码读 lottie 的单测。

</details>

<details>
<summary><b>DSX-112</b> · P2 · 安卓读屏用词改取契约字典</summary>

负责线：安卓；依赖：DSX-41。

**范围**

SearchDraftTexts.kt:39、41 等草稿里与 a11y.* 重复的键删掉；29 处 CouliIconButton 的 label 统一取 a11y.* 或页面字典键。

来源：g4-65。

**验收**

草稿文件里这些读屏键为 0；单测抽查读屏名取自字典。

</details>

### 鸿蒙

<details>
<summary><b>TOKENS-PIPE-harmony</b> · P0 · TOKENS-PIPE（鸿蒙）：升令牌锁，一条链路出全部令牌，删旁路副本</summary>

负责线：鸿蒙（协同 设计）；依赖：无；承接：TOKENS-PIPE（D10-643 ③，鸿蒙）；状态（2026-11-05）：进行中（D10-643 ③ 已派；令牌锁直接升 v0.5.1，D10-665）。

**范围**

按 D10-643 ③ 做：

① contract.lock 的 design_tokens 从 18ad5b4 直接升到 couli f088f04（v0.5.1，D10-665），contracts/snapshot 随之更新；之后跟到 v0.6.0 由 DSX-122 负责。若 LINT-STYLE-harmony 先合，本单删掉旁路副本和常量时顺手从它的基线里减掉失效条目。

② 两条链路合一：gen.py 出的 DesignTokens.ets 还是 0.3.0，gen_theme.py 读旁路副本 specs/design-tokens.v0.4.0.json。改为都从锁定快照生成，输出 base / dark 两套 element/color.json、component、shadow。

③ 删掉副本 specs/design-tokens.v0.4.0.json；ds02 夹具需要保留的改为从快照派生。

④ HM-LINT-11 theme-drift 改为对照锁定快照。

来源：g1-06、g2-17、g4-07。

**验收**

① 执行 `git ls-files 'specs/design-tokens.v*.json'` 为空；② 全部生成物的 version 只有一个值，且等于锁定快照的版本；gen_theme.py 头注不再写「contract.lock 仍锁 v0.3.0」；③ 脚本比对 dark/element/color.json 与快照 dark 字段逐项相等；④ 手改 CouliThemeTokens.ets 一个色值时，lint.py 退出码为 1；⑤ 生成器重跑后 git diff 为空。

</details>

<details>
<summary><b>LINT-STYLE-harmony</b> · P0 · LINT-STYLE（鸿蒙）：页面层禁写死样式，G1 守卫从只警告改为按基线失败</summary>

负责线：鸿蒙；依赖：无；承接：LINT-STYLE（D10-643 ④，鸿蒙）；状态（2026-11-05）：进行中（D10-643 ④ 已派）。

**范围**

按 D10-643 ④ 做：

① tools/ci/lint.py 新增页面样式字面量规则，范围是 features/*/src/main 和 entry/src/main。拦截颜色字面量（含八位色值，如 ExternalWebView.ets:580 '#CC000000'、TrustedWebView.ets:1625 '#99000000'），.fontSize(数字或 '24vp')、.borderRadius(N)、.padding / .margin(N)、space: N、.width / .height(N)、iconSize: N，以及用 .opacity(…? 0.5 …) 表达禁用态。与 TOKENS-PIPE-harmony 并行，按现状约 216 处建基线，只减不增，新增即退出码 1。

② [design-system-required]（G1）名单补上 Button / Divider / LoadingProgress / TextInput / bindSheet / openCustomDialog，以现状约 38 处建基线；L37、L84 从「警告、不计入违反」改为新增即违反，不等组件规范定稿。

③ 组件清单 §6 G3「颜色尺寸只用令牌」按以上规则落地。

来源：g1-08、g2-18、g3-54、g4-08。

**验收**

① lint.py 自测含反例：八位色值、数字 fontSize、.borderRadius(12)、Toggle(、'#FFFFFF'、.opacity(this.disabled ? 0.5 : 1) 都会让退出码为 1；② 基线文件已入库，检查条目只减、每条都能匹配到代码；③ 注释不再写「不计入违反」；④ 主干上跑 lint.py 退出码为 0。

</details>

<details>
<summary><b>FU-DS-harmony</b> · P0 · FU-DS（鸿蒙组件库）：ErrorState、EmptyState、NoticeBar、Toast、Skeleton 按状态目录统一</summary>

负责线：鸿蒙；依赖：UI-STATES、COMP-SPEC-2、DSX-01、TOKENS-PIPE-harmony；承接：FU-DS（D10-643：UI-STATES 合并后派，鸿蒙份）。

**范围**

改 common/designsystem 的 components/States.ets：

① ErrorState 去掉红三角和 statusErrorBackground 红底，改由 kind 决定图标、用中性底；按钮默认主按钮、最大宽 240；尺寸按 COMP-SPEC-2 定的数值集中定义在组件库一处（v0.6.0 已发布则直接读 component.state.*；否则由 DSX-122 升锁时改读）。

② EmptyState 去掉写死的 SECONDARY，加按钮主次参数和 density，参数名与另两端一致。

③ Display.ets 的 NoticeBar 补四种 tone 和动作。

④ CouliToast 继续用系统 showToast（页顶），时长由组件决定。

⑤ Skeleton 按 COMP-SPEC-2 的口径。

⑥ 目录页和 hdc 截图基准浅深重录。

来源：g3-55。

**验收**

States.ets 里没有 statusErrorBackground 和写死的 SECONDARY；三端状态组件参数同名；新截图基准入库，像素差 ≤1%；按定稿 sha256 比对一致。

</details>

<details>
<summary><b>DSX-122</b> · P1 · 鸿蒙令牌锁升 v0.6.0、锁定组件规范、生成器输出新类别</summary>

负责线：鸿蒙（协同 设计）；依赖：TOKENS-PIPE-harmony、DSX-02、DSX-03、DSX-04、COMP-SPEC；承接：TOKENS-PIPE（鸿蒙份的 v0.6.0 跟进；原写在 FU-DS-SWITCH-DESC、DSX-75）。

**范围**

作为三端令牌锁升到 v0.6.0 的唯一一步（鸿蒙），排在 TOKENS-PIPE-harmony 之后、读新令牌的各组件单之前：

① contract.lock 的 design_tokens 升到 couli v0.6.0 发布提交（DSX-02 合并点，含 DETAIL-V3-WB 的 v0.5.1 与 DSX-03、DSX-04 的键），快照随之更新；同时锁定 design/components/component-spec.json 的版本（component_spec）。

② 生成器输出 v0.6.0 的新类别：复合文字样式（text.*）、组件变体与状态（button.*、chip.*、tag.*、rebate-tag.large、验证码格、component.state.*、component.image.*）、layout、motion（duration、cubicBezier）、layer、color.chart.*、component.navbar.inverse.*、color.platform.tag.* 与 overlay.on-image（若 v3 合派单还没跟）、border.width、icon.stroke、opacity、letter-spacing。

③ 「生成物 vs 锁定源」逐值比对测试覆盖新类别（含 dark）；FU-DS-harmony 已合的话，把其中与 component.state.* 同值的常量改读生成物。

④ 只出生成物和锁，不改组件外观；各组件改读新令牌由下游单做。

来源：评审意见第 13 条。

**验收**

contract.lock 的 design_tokens 指向 v0.6.0 发布提交，component_spec 有锁定版本；生成物的 version 为 0.6.0 且含上列类别；逐值比对测试通过；生成器重跑后 git diff 为空；TOKENS-LAG 对本端不再报 design_tokens 落后；lint.py 与 hvigor 测试 通过。

</details>

<details>
<summary><b>DSX-142</b> · P1 · 鸿蒙 CI 接入令牌与契约落后检查，改锁共享客户端向量</summary>

负责线：鸿蒙；依赖：TOKENS-LAG、DSX-42、TOKENS-PIPE-harmony；承接：与 TOKENS-LAG（D10-643 ⑥）、DSX-42 相关（鸿蒙接入）。

**范围**

从 TOKENS-LAG、DSX-42 拆出的鸿蒙份：① 鸿蒙 CI 跑 TOKENS-LAG 的同一检查（先警告）；② contract.lock 改锁 rebate-platform specs/client/ 下的共享向量，删掉本仓库已分叉的副本，测试改读同步来的文件。

来源：g1-10、g2-44（鸿蒙份）。

**验收**

鸿蒙 CI 有一次 TOKENS-LAG 检查的运行记录；contract.lock 锁定的向量 sha256 与分发清单一致；仓库里没有向量的私有副本；lint.py 退出码 0。

</details>

<details>
<summary><b>DSX-74</b> · P1 · BRAND-02-鸿蒙：CouliIcon 改由唯一 SVG 源生成，组件库图标两套归一，核对启动窗</summary>

负责线：鸿蒙；依赖：DSX-06、TOKENS-PIPE-harmony。

**范围**

CouliIcon.ets 的品牌脸面和内容类路径改由 design/icons SVG 生成，替换第 18 行说的自绘钱包、流水、铃铛、星、趋势等。Controls / Display / Navigation / Inputs.ets 里的 SymbolGlyph 只留给「系统控件自带」类。module.json5 的 startWindowIcon 换成按规范导出的 logo-mark；start_window_background 的浅深两值改由令牌生成。补品牌页和图标一致性的 hdc 截图基准。

来源：g1-22。

**验收**

清单内的图标全部来自生成，手写路径为 0；脚本检查组件库里 SymbolGlyph 的符号名都在「系统控件自带」清单内；start_window_background 来自生成物；截图基准入库，像素差 ≤1%。

</details>

<details>
<summary><b>DSX-75</b> · P1 · 鸿蒙组件与令牌对齐：提现金额字号、返利标签、阴影、Web 容器加载态、描边</summary>

负责线：鸿蒙；依赖：LINT-STYLE-harmony、DSX-122。

**范围**

新类别的生成由 DSX-122 交付，本单只接入组件。改正以下几处：

- WithdrawView.ets:456 的 .fontSize(24) 改为 heading 28 加半粗（画板是 28/35/600）；

- Price.ets:223 返利标签圆角改读 rebate-tag.large；

- CouliMetrics.ets:132–134 的阴影 radius 按换算公式；

- Web 容器加载态：ExternalWebView.ets:579–580、TrustedWebView.ets:1624–1625 的 #CC000000、#99000000 和 borderRadius(12) 改用遮罩、表面、圆角令牌，并对照画板和 iOS WebScreens.swift:135，定成三端同一规格；

- CouliIcon.ets:139 描边改读 icon.stroke；

- 字重与行距（FU-DS-LINE-HEIGHT 鸿蒙份）：12 号多行行距按画板 18，各级默认字重按规范。

Toast 时长在 FU-DS-harmony，内容最大宽在 DSX-76。

来源：g1-25。

**验收**

执行 `git grep -nF -e 'fontSize(24)' -e '#CC000000' -e '#99000000' -- features common/designsystem` 为 0；LINT 基线行数减少；提现页和 Web 容器加载态截图与画板核数，基准入库。

</details>

<details>
<summary><b>DSX-76</b> · P1 · 鸿蒙 PageScaffold 与 layout 令牌，合并两个内容限宽常量</summary>

负责线：鸿蒙；依赖：DSX-11、DSX-122。

**范围**

layout 令牌由 DSX-122 生成。CouliLayout.maxContentWidth 和 ContentColumn.MAX_WIDTH 两个 600 合成一个，读令牌，删掉 TODO(N-27)。提供 PageScaffold（NavDestination + NavBar + 限宽内容列 + 底部栏避让键盘 + 安全区），现有页面骨架改用它。lint 加规则：features 不得写限宽数字、不得自写骨架，并建基线。

来源：g3-59（另含 g1-25、g4-52 的限宽部分）。

**验收**

内容最大宽只有一个来源，且来自令牌；common/designsystem 里 TODO(N-27) 和 MAX_WIDTH: number = 600 为 0；折叠屏展开态截图内容居中。

</details>

<details>
<summary><b>FU-DS-DIALOG-TITLE-ALIGN</b> · P1 · 鸿蒙组件库弹层修正：CouliSheetPanel 撑满整屏，CouliDialog 对齐参数和间距</summary>

负责线：鸿蒙；依赖：COMP-SPEC-2；承接：FU-DS-DIALOG-TITLE-ALIGN（APP-12w 立，归 DS-03）。

**范围**

作为 DS-03 的子项。修复 CouliSheetPanel 在 SheetSize.FIT_CONTENT 下纵向 Flex 撑满整屏的问题（TradeOverlay.ets:494、MeKit.ets:415 因为这个问题另写了面板）。CouliDialogPanel / Options 加标题对齐参数；默认值和元素间距（Overlays.ets:141 现在是 16）按规范改。目录页加 FIT_CONTENT 半屏样例。参数化测试读 component-spec.json。浅深快照重录。

来源：g2-19。

**验收**

UiTest 断言 FIT_CONTENT 半屏的面板高度等于内容高度；参数化测试断言标题对齐和元素间距；PR 里写明快照重录说明。

</details>

<details>
<summary><b>DSX-77</b> · P1 · 鸿蒙半屏页面统一用 CouliSheet.options，删掉私有面板</summary>

负责线：鸿蒙；依赖：FU-DS-DIALOG-TITLE-ALIGN。

**范围**

11 个文件里的 .bindSheet( 改为 CouliSheet.options(protectedSheet, height, onClose)，资金和验证类用保护型。涉及 ClipboardViews（两处）、RootPage、AgentTabRoot、DeleteAccountView、PhoneChangeView、SettingsView、OrderListView（两处）、SearchView、PayoutAccountView、RealNameView、WithdrawView。删掉 MeSheetPanel 和 TradeOverlay 的私有面板。

来源：g2-20。

**验收**

执行 `git grep -n -E 'dragBar:|maskColor:' -- features entry/src/main` 为 0；脚本断言每处 bindSheet 的选项都来自 CouliSheet.options；G1 基线里 bindSheet 条目清零；快照重录。

</details>

<details>
<summary><b>FU-DS-SWITCH-DESC</b> · P1 · 鸿蒙组件库输入与选择修正：验证码统一、开关副标题、胶囊和按钮参数</summary>

负责线：鸿蒙；依赖：COMP-SPEC、DSX-122、DSX-119；承接：FU-DS-SWITCH-DESC（APP-12w 立，归 DS-03）。

**范围**

作为 DS-03 的子项。v0.6.0 的锁和生成物由 DSX-122 交付，本单只改组件。

- StepUpPanel.ets:270 的当前格从 focusRing 改为 border.active；CodeCells.ets:15 的 MIN_HEIGHT 60 改读 code-cell.height（56），数字字号按规范；

- CouliSwitch 加副标题样式和 accessibilityDescription 两个可选参数（同时了结 FU-DS-SWITCH-MARGIN）；

- FilterChip：32 高、左右 12、选中带描边；

- 文字按钮内边距、加载转圈尺寸按规范改；按 DSX-119 裁定新增 tonal 变体；按钮图标尺寸按画板（FU-DS-BUTTON-ICON 鸿蒙份）。

参数化测试读 component-spec.json；目录页浅深快照重录。

来源：g2-21。

**验收**

StepUpPanel.ets 里 focusRing 为 0；CodeCells.ets 没有字面量 60；参数化测试覆盖按钮、输入、胶囊、开关各行；快照重录。

</details>

<details>
<summary><b>DSX-78</b> · P1 · 鸿蒙登录与绑手机页迁移到组件库（含强更页品牌位）</summary>

负责线：鸿蒙；依赖：FU-DS-SWITCH-DESC。

**范围**

LoginView.ets 的 agreementRow（圆角方块，CHECKBOX = 20）换成 AgreementCheckRow（CheckBoxShape.CIRCLE）；验证码格换成 CodeInput；LoginView 和 BindPhoneView 里 TextInput 换成 PhoneField、Divider() 换成 CouliDivider、LoadingProgress 换成 CouliLoading；Row({ space: 40 }) 换成 ThirdPartyLoginRow；LoginView.ets:197 和 ForceUpdatePage.ets:15 的方块换成 CouliLogo。只换组件、不动排版，不等登录 v2 的闸门。

来源：g2-22。

**验收**

执行 `git grep -n -E 'CHECKBOX: number = 20|space: 40|TextInput[(]|Divider[(][)]|LoadingProgress[(]' -- features/auth` 为 0；LoginView 引用了 AgreementCheckRow、CodeInput、PhoneField、ThirdPartyLoginRow、CouliLogo；lint 两份基线里 features/auth 清零；浅深快照重录。

</details>

<details>
<summary><b>DSX-79</b> · P1 · 鸿蒙我的 / 设置 / 隐私 / 换号页控件迁移</summary>

负责线：鸿蒙；依赖：FU-DS-SWITCH-DESC。

**范围**

features/me 下这些改动：

- 自绘的 52×32 开关（MeSwitchRow、PrivacyAboutCsParts、SettingsParts、NotifyServiceRow）换成 CouliSwitch，并去掉 .opacity(this.disabled ? 0.5 : 1)；

- MeTabView 的余额主卡和宫格换成 WalletHeroCard / EntryGrid；

- TextInput 换成 PhoneField / CouliTextField，Divider() 换成 CouliDivider，LoadingProgress 换成 CouliLoading；

- 8 处 '24vp' 等字面量换成令牌字号。

来源：g2-23。

**验收**

features/me 里没有自绘开关（DSX-82 规则 0 命中），`opacity(this.disabled` 为 0；Divider()、LoadingProgress(、TextInput( 为 0；字面量基线里 features/me 从 63 条降到 31 条以下；快照重录。

</details>

<details>
<summary><b>DSX-80</b> · P1 · 鸿蒙搜索 / 订单 / 首页 / Agent 卡控件迁移</summary>

负责线：鸿蒙；依赖：FU-DS-SWITCH-DESC、W-33。

**范围**

- SearchView 的 SearchChip（CHIP_HEIGHT 36）和 OrderListView 自写的 32 高胶囊都换成组件库 FilterChip；TAB_BAR_HEIGHT 3 改读 tab-indicator.height（2）。

- OrderStatusChip 换成 CouliTag 状态款。

- HomeTabRoot.ets:338–352 内联的浅底按钮换成 tonal 变体。

- AgentCards.ets:134 用 opacity 表示禁用，改用组件的禁用态。

- search、orders、home、agent、web、entry 里的 LoadingProgress、Divider()、TextInput 换成组件库的组件。

来源：g2-24、g3-58。

**验收**

执行 `git grep -n -E 'SearchChip|OrderStatusChip|CHIP_HEIGHT|TAB_BAR_HEIGHT' -- features` 为 0；上述目录里 LoadingProgress(、Divider()、TextInput( 为 0；G1 基线里相应条目清零；两页截图与改齐的画板一致。

</details>

<details>
<summary><b>DSX-81</b> · P1 · 鸿蒙钱包页控件迁移与字面量清理</summary>

负责线：鸿蒙；依赖：LINT-STYLE-harmony、FU-DS-SWITCH-DESC。

**范围**

features/wallet 里：TextInput、Divider()、LoadingProgress 换成组件库的组件；页面层约 36 处尺寸、圆角、字号字面量换成令牌（WithdrawView 的字号由 DSX-75 改）。只换展示、不动资金逻辑，按保护路径评审。

来源：g2-25。

**验收**

features/wallet 里 TextInput(、Divider()、LoadingProgress( 为 0；字面量基线里 features/wallet 清零；浅深快照重录，资金逻辑测试零改动。

</details>

<details>
<summary><b>DSX-82</b> · P1 · 鸿蒙守卫 G2：自绘开关和方块勾选框</summary>

负责线：鸿蒙；依赖：LINT-STYLE-harmony。

**范围**

lint.py 加组件清单 §6 G2 的两条规则：自绘开关、圆角方块加 check 拼成的勾选框。以现状为基线；DSX-78、DSX-79 合并后基线清零。

来源：g2-26。

**验收**

两条规则各有正例和反例；反例退出码为 1；迁移合并后基线为空。

</details>

<details>
<summary><b>FU-DS-harmony-pages</b> · P1 · FU-DS（鸿蒙非资金页）：首次加载改骨架屏、订单详情错误态、私有提示条、草稿键</summary>

负责线：鸿蒙；依赖：FU-DS-harmony、DSX-21；承接：FU-DS（页面段）。

**范围**

- 首次加载的 LoadingProgress 改成 Skeleton，只保留按钮内和等待外部结果两种用法。

- OrderDetailView.ets L543–545 在 EMPTY 阶段用 EmptyState 显示错误，改为 ErrorState 带【重试】。

- MeNoticeBar、PrivacyBasicNotice、CsSafetyStrip、BasicModeNotice 换成组件库的 NoticeBar。

- order.network_error 等草稿键换成 state.* 和 net.unavailable。

- 按规格三行补状态；锁升到含 UI-STATES 的提交。

- lint.py 加 G7（features 不得自定义状态块和提示条），并建基线。

来源：g3-56。

**验收**

features 里 LoadingProgress 只出现在白名单位置；OrderDetailView 不再用 EmptyState 显示错误；私有提示条为 0；G7 基线已提交；hdc 截图更新。

</details>

<details>
<summary><b>FU-DS-harmony-fund</b> · P1 · FU-DS（鸿蒙资金与金额页）：钱包首屏骨架、提现状态键、「我的」金额缺失、受限会话转圈</summary>

负责线：鸿蒙；依赖：FU-DS-harmony、DSX-01、DSX-21；承接：FU-DS（页面段）。

**范围**

WalletView.ets 首次加载的 LoadingProgress 改成 Skeleton；withdraw.load_failed（取值与另两端不同）换成 state.*；MePresentation.ets L174–175 的 ?? 0 按 BR-TEXT-10 改；受限会话下「我的」一直转圈，改为超时后转 ErrorState 并可重试。按资金页评审口径走。

来源：g3-57。

**验收**

WalletView 首屏是骨架；MePresentation 不再对 withdrawable_fen 用 ?? 0；UiTest 覆盖受限会话超时后出现【重试】；资金页截图基准重录。

</details>

<details>
<summary><b>FU-X-DLG-harmony</b> · P1 · FU-X-DLG（鸿蒙）：44001 拦截弹窗主次按定稿统一</summary>

负责线：鸿蒙；依赖：W-33；承接：FU-X-DLG（android-visual-backlog-20261103 C1）。

**范围**

提现、收款账号、换手机号、登录验证码四处的 44001 拦截弹窗按 W-33 定稿统一主次，二次验证格子按统一规格。单独开小单并做红线证明。

来源：g3-60。

**验收**

四处截图与新画板一致；UiTest 断言主按钮文字；评审记录含红线证明。

</details>

<details>
<summary><b>DSX-83</b> · P1 · 鸿蒙动效落地：先核实减弱动态接口，再做统一入口和轮播公告节奏</summary>

负责线：鸿蒙；依赖：DSX-13、DSX-26、DSX-122。

**范围**

motion 令牌由 DSX-122 生成。先按官方文档核实读取「减弱动态 / 动画时长」的接口并留实测记录（09 回写由 DSX-132 做），再在 DS 提供统一入口。HomeCards 的轮播（L164 Math.max(1000, …)）和公告（L708 interval(4000)）按 03 §6.3 的间隔和暂停条件改，开启减弱动态时停止自动播放。

来源：g3-61。

**验收**

接口实测记录附在 PR（交 DSX-132 回写 09）；HomeCards 里没有写死的 4000 和 1000；UiTest 在开启该设置时断言不自动翻页。

</details>

<details>
<summary><b>HM-08-agent</b> · P1 · HM-08（鸿蒙）：AI 商品卡 grid 按定稿口径，长按举报补可见入口</summary>

负责线：鸿蒙；依赖：DSX-22、DSX-12；承接：HM-08。

**范围**

AgentCards.ets 的 grid（R1-13）按 DSX-22 的口径改；长按举报在只给读屏和键盘的透明按钮之外，补一个可见入口。

来源：g3-62。

**验收**

Agent 卡截图覆盖 list 和 grid，并与稿一致；UiTest 能从可见入口打开举报。

</details>

<details>
<summary><b>DSX-84</b> · P1 · 鸿蒙无障碍守卫（含 Web 返回键读屏名）</summary>

负责线：鸿蒙（协同 质量）；依赖：无。

**范围**

TrustedWebView.ets:1407–1413 和 ExternalWebView.ets:422–428 的返回 Button 补 .accessibilityText（取字典 web_page.back）。Controls.ets 的 CouliIconButton 把 accessibilityName 改为 @Require（L403 现在默认空串）。lint.py 新增规则：纯图标 Button 必须有 accessibilityText，或者用 CouliIconButton。设备用例对关键页断言可点控件的 accessibilityText 非空、命中区 ≥48vp。

来源：g4-49。

**验收**

设备用例断言两个返回按钮的读屏名等于字典值；accessibilityName 没有默认值且能编译；新 lint 规则对变异样例报错，基线已入库；命中区用例通过。

</details>

<details>
<summary><b>DSX-85</b> · P1 · 鸿蒙系统字号超 200% 的封顶与 3.2 倍验证（按 DSX-133 的决定实施）</summary>

负责线：鸿蒙（协同 设计、质量）；依赖：DSX-133。

**范围**

按 DSX-133 记下的负责人决定（鸿蒙关怀模式字号封顶）实施，二选一：

A. configuration.json 的 fontSizeMaxScale 从 3.2 降到 2（或按华为建议 1.75，关键组件 maxFontScale 2）；

B. 正文跟随到 3.2 倍，导航栏、底栏、AmountGrid 等密集控件用 maxFontScale 封顶（现在全仓只有两处插画小字这样做）。

补设备用例覆盖选定的上限和关怀模式字重 1.25 倍（现在 Hm07vOverlayUi 最高只测到 2），覆盖金额、购买和提现按钮不截断、不重叠。03 §10.4 鸿蒙行的回写在 DSX-133。

来源：g4-50。

**验收**

configuration.json 与负责人决定一致；设备用例覆盖到选定上限并通过；R1-07-A 更新为已执行。

</details>

<details>
<summary><b>DSX-86</b> · P1 · 鸿蒙截图基准与像素比对管线（浅 / 深、100% / 200%）</summary>

负责线：鸿蒙（协同 设计）；依赖：无。

**范围**

设备步骤用 hdc snapshot_display 出图，首页（含 golden）和 7 个关键页的 100% / 200%、浅 / 深基准入库，或存私有库并在仓库记 sha256。加像素差比对（≤1%，先只报告，稳定后改为失败），替换 check-ui-facilities.cjs:639「截图只模拟保存成功」的做法。

来源：g4-51。

**验收**

仓库有基准图（或 sha256 清单）和比对脚本；verify 输出每张图的像素差报告；变异：改一个颜色令牌后，报告标出差异。

</details>

<details>
<summary><b>DSX-87</b> · P1 · 鸿蒙折叠 / 展开连续性设备用例</summary>

负责线：鸿蒙（协同 质量）；依赖：TOKENS-PIPE-harmony、DSX-76。

**范围**

在折叠屏模拟器或真机上补用例：填表 → 展开 / 折叠 → 断言内容和滚动位置不丢，覆盖登录、提现、搜索、订单列表（全仓 foldStatus、mediaquery 现在都是 0）。Hm07vHomeUi.test.ets:600 的 ≥600vp 判定在折叠屏模拟器上实跑。限宽改读令牌由 DSX-76 处理。

来源：g4-52。

**验收**

四个页面的折叠 / 展开用例通过并留截图；≥600vp 用例在折叠屏模拟器上非退化执行，日志可见。

</details>

<details>
<summary><b>HM-07-sdui</b> · P1 · 鸿蒙首页 SDUI 按契约解码（含渲染上报和弹窗读屏名）</summary>

负责线：鸿蒙（协同 后端）；依赖：CT-07e；承接：HM-07（补丁后缀）。

**范围**

契约快照同步 home-schema.json 和 home-golden。HomeJson.ets：删掉 L5 的 TODO(N-35)；L312 height_ratio 上限、L384 icon / image、L409–411 product_scroll title、版本范围都按契约改；视觉参数统一夹取。加 golden 正反例单测；上报渲染成功事件；popup.alt 接为读屏名。

来源：g4-53。

**验收**

单测遍历全部 golden，结果与期望一致；TODO(N-35) 为 0；渲染事件有单测；golden 截图与另两端并排对照。；解码遇到未知键忽略（单测）；由分发清单生成的 Tracker 含首页渲染成功事件。

</details>

<details>
<summary><b>HM-03-web</b> · P1 · 鸿蒙 ArkWeb：跟随主题与字号、标题回退、反色标题栏</summary>

负责线：鸿蒙（协同 后端、前端）；依赖：DSX-25、CT-03-env、DSX-122；承接：HM-03（补丁后缀）。

**范围**

TrustedWebView.ets L1522–1526 的 Web 组件加 darkMode(WebDarkMode.Auto)，是否还需要 forceDarkAccess 按官方文档核对。BridgeHost 实现 getEnv 的新字段和变化事件，注入 data-theme。文字缩放按 DSX-25 做；ArkWeb 是否跟随系统字号要实测，测试记录附在 PR，由 DSX-132 回写 09 CAP-X-18。ExternalWebView.ets L119–120 在组件里按主题取色，改为 navbar.inverse。L1606 onTitleReceive 的回退不显示 URL。按 CT-03-env 同步桥契约并重新生成桥类型；navbar.inverse 令牌由 DSX-122 的 v0.6.0 锁提供。

来源：g4-54。

**验收**

conformance 页的主题、字号用例在设备上通过；ExternalWebView 里没有按主题分支取色；深色下 nav_style=dark 对比度 ≥4.5:1；生成的桥类型含 color_scheme、font_scale；字号跟随结论附测试记录（交 DSX-132 回写 09）。

</details>

<details>
<summary><b>APP-06v-harmony</b> · P1 · 鸿蒙补做商品详情视觉对稿（APP-06v 鸿蒙份）</summary>

负责线：鸿蒙（协同 设计）；依赖：DETAIL-V3-WB、DSX-117；承接：APP-06v（鸿蒙份）。

**范围**

按同一份任务书和 fixture 补做鸿蒙的对稿，深色按定稿深色稿。v3（d0aaa76）已取代 APP-06v 的画板，直接按 v3 做鸿蒙份；若 D10-641 鸿蒙份已覆盖详情 v3 对稿，本单只补 compare 和三端并排图。收尾按 DSX-09 交三端并排对照图。

来源：g4-55。

**验收**

有 compare-harmony.md，逐项都有结论；浅 / 深 / 200% / 320 / 600 截图齐全；有一张三端并排图。

</details>

<details>
<summary><b>APP-08v-harmony</b> · P1 · 鸿蒙补做订单视觉对稿（APP-08v 鸿蒙份）</summary>

负责线：鸿蒙（协同 设计）；依赖：无；承接：APP-08v（鸿蒙份）。

**范围**

按同一份任务书（订单列表和订单详情，第 2 批定稿）和 fixture 补做，深色按定稿深色稿；收尾交三端并排对照图。

来源：g4-56。

**验收**

NATIVE/APP-08v/compare-harmony.md 已有，逐项都有结论；五档截图齐全；有一张三端并排图。

</details>

<details>
<summary><b>APP-09v-harmony</b> · P1 · 鸿蒙补做钱包提现视觉对稿（APP-09v 鸿蒙份）</summary>

负责线：鸿蒙（协同 设计）；依赖：无；承接：APP-09v（鸿蒙份）。

**范围**

按同一份任务书（钱包、提现、提现记录、二次验证、收款账号、实名、劳务协议）和 fixture 补做，只改视觉、不改资金逻辑；收尾交三端并排对照图。

来源：g4-57。

**验收**

compare-harmony.md 已有，逐项都有结论；五档截图齐全；资金相关执行器零改动（diff 证明）；有一张三端并排图。

</details>

<details>
<summary><b>DSX-88</b> · P1 · 鸿蒙图片缓存与解码配置统一：设上限、按显示尺寸解码、商品图校验 https、预取</summary>

负责线：鸿蒙；依赖：DSX-31。

**范围**

按 DSX-31 的选型，在 entry 启动时统一设置内存缓存和文件缓存的上限（现在全仓都没设），并按显示尺寸解码。ProductCardMapper.ets:171–175 补 https 校验（首页 static_item.image 在解码阶段已经丢掉非 https 地址，现在只差商品卡这一路）。请求策略照 03。提供预取接口，由 HomeTabRoot 首屏调用（现在只预取弹窗图）。AppMe.ets:633–669 的缓存大小和清除要覆盖图片文件缓存。

来源：g5-09。

**验收**

Hypium 测试：缓存上限等于 03 §12 的数值、http 商品图映射为空态、首屏会预取、清除后缓存大小下降；缓存配置只出现在一处；verify 通过。

</details>

<details>
<summary><b>DS-02-harmony-image</b> · P1 · 鸿蒙 9 处直写 Image(url) 收编为统一组件：四态、令牌图框、订单与详情圆角描边、下架去色</summary>

负责线：鸿蒙；依赖：DSX-118、DSX-41、DSX-88、DSX-122；承接：DS-02（鸿蒙组件库后续）。

**范围**

common/designsystem 新建 ProductImage 和通用远程图件，替换以下 9 处自写的 Image / onComplete / onError：HomeCards ×4、HomeTabRoot、HomeTiles、ProductCard、OrderViewKit、ProductDetailView。

- 去掉 imageLabel 文字和 48 号图标占位；

- 网格图 aspectRatio(1) 改从 grid 令牌取；

- 详情主图按 v3，取代 aspectRatio(1.4) 和 HERO_RADIUS=12；

- 订单图改为圆角 8 加描边；

- 商品下架时详情主图去色；

- 加渐显。

ImagePlaceholder 从 staging 目录页撤下；删掉占位字键和本地读屏键，改用契约键。

来源：g5-10。

**验收**

脚本检查这 9 处不再直接用远程地址调用 Image；在 features、common、entry 里 git grep -e imageLabel -e HERO_RADIUS 为 0；截图基准覆盖四态 × 各尺寸 × 浅深，外加一张下架去色图；verify 通过。

</details>

<details>
<summary><b>DS-02-harmony-trend</b> · P1 · 鸿蒙 PriceTrendPanel 改正：去掉「最低」，按日期和刻度画阶梯线、随容器宽度，补失败态和来源行</summary>

负责线：鸿蒙；依赖：DSX-37、DSX-38、CT-22-trend、UI-STATES、DSX-122；承接：DS-02（鸿蒙组件库后续）。

**范围**

Business.ets：

- :59 等距排点改为读共用几何向量：按日期、阶梯线、缺失日断开、刻度网格；

- 去掉 :73 写死的 280 宽，改为随容器自适应；

- :76 的 #C44820 改用 chart 令牌；

- 加 ERROR 态和来源行；摘要由组件按模板键格式化。

staging 样例去掉「最低」，日期改成 MM-DD，金额按 BR-TEXT-10 写。截图基准重拍；单测断言不含禁用词。

来源：g5-41。

**验收**

git grep -e 最低 -e 最高 为 0；Business.ets 里不再写死 280；几何向量测试全过（读分发清单里的向量文件）；截图含 Error 态，覆盖浅深、200% 和宽屏；verify 通过。

</details>

<details>
<summary><b>DSX-129</b> · P2 · share.open 微信卡片缩略图压到 ≤32KB（鸿蒙）</summary>

负责线：鸿蒙；依赖：CT-03-share；承接：与 05 HM-10 相关（鸿蒙份）。

**范围**

鸿蒙在分享单（HM-10）实现 share.open 时一起做。规则同 APP-13-share-thumb：方形 JPEG、逐级降质量直到 ≤32KB；title ≤512 字节、description ≤1KB；读同一组测试图向量。

来源：g5-34（鸿蒙份）。

**验收**

单测：同一组向量图压缩后 ≤32768 字节且是方形；过长的 title / desc 被截到上限；真机微信分享卡片带图的截图进 evidence。

</details>

<details>
<summary><b>DSX-113</b> · P2 · 鸿蒙标签组件去重与命名对齐（CouliChip 并入 CouliTag，ON_BRAND 改为 onSolid）</summary>

负责线：鸿蒙；依赖：COMP-SPEC。

**范围**

作为 DS-03 的子项。Basics.ets:245 的 CouliChip（页面约 14 处引用）和 Display.ets:135 的 CouliTag（页面 0 引用）合并为规范名 CouliTag，CouliChip 保留一版弃用别名；ON_BRAND 改名为 onSolid，保留别名；ProductCard 的变体名按规范改。

来源：g2-27。

**验收**

在 features 和 entry 里 git grep 'CouliChip(' 为 0；ON_BRAND 只剩弃用别名；目录页快照没有预期外变化。

</details>

<details>
<summary><b>DSX-114</b> · P2 · 鸿蒙防连点与加载防闪</summary>

负责线：鸿蒙；依赖：DSX-12。

**范围**

DS 可点区域默认防连点（500ms 内只响应一次），NavPathStack 在导航进行中忽略重复推入；加载指示按 DSX-12 的不显示阈值和最短停留做。

来源：g3-63。

**验收**

单测：连点两次只推入一次；加载指示有时序单测。

</details>

<details>
<summary><b>APP-13v-harmony</b> · P2 · 鸿蒙补做注销 / 换号 / 绑手机号视觉对稿（APP-13v 鸿蒙份）</summary>

负责线：鸿蒙（协同 设计）；依赖：无；承接：APP-13v（鸿蒙份）。

**范围**

按同一份任务书（第 3 批定稿）和 fixture 补做；注销属于 W6 范围，排在 M-内测页之后；收尾交三端并排对照图。

来源：g4-66。

**验收**

NATIVE/APP-13v 下有鸿蒙的 compare，逐项都有结论；五档截图齐全；有一张三端并排图。

</details>

<details>
<summary><b>DSX-115</b> · P2 · 鸿蒙平板设备类型按判定结果落地</summary>

负责线：鸿蒙（协同 设计）；依赖：DSX-10。

**范围**

按 DSX-10 对鸿蒙平板范围的判定处理：在范围内的话，module.json5 的 deviceTypes 加 tablet，按 03 §10.4 平板行做限宽居中，并补平板模拟器用例；不在范围内的话，不改代码，只核对折叠屏内屏上竖屏锁定的实际表现。新增平板上架材料属于对外动作，届时报负责人。

来源：g4-67。

**验收**

module.json5 与判定一致；平板或折叠屏内屏模拟器用例通过并有截图。

</details>

<details>
<summary><b>HM-07-lottie</b> · P2 · 鸿蒙首页弹窗 Lottie 动效</summary>

负责线：鸿蒙；依赖：HM-07-sdui、DSX-98；承接：HM-07（Lottie 跟进）。

**范围**

接入 OpenHarmony 三方库中心仓的 Lottie 移植库（与最低 API 20 的兼容性按官方文档核对，并补进 03 §6.3）；按 sha256 校验后从本地播放；读系统减弱动态设置，开启时用兜底图；关闭即停播释放。

来源：g4-68。

**验收**

两张设备截图；减弱动态和 sha256 不符时用兜底图的用例通过。

</details>

<details>
<summary><b>DSX-116</b> · P2 · 鸿蒙读屏用词改取契约字典</summary>

负责线：鸿蒙；依赖：DSX-41。

**范围**

MeDraftTexts.ets:62–63、OrderDraftTexts.ets:129 等草稿里与 a11y.* 重复的键删掉，改取契约字典。

来源：g4-69。

**验收**

草稿文件里这些读屏键为 0；设备用例抽查读屏名取自字典。

</details>

### 质量

<details>
<summary><b>DSX-89</b> · P1 · 商品图三端同屏验收：六种真实主图进验收用例，对照模板加图框数值断言</summary>

负责线：质量（协同 设计）；依赖：DS-02-ios-image、DS-02-android-image、DS-02-harmony-image、DSX-32。

**范围**

目前没有 qa 专线，由 design（编排）兜底执行。10 新增图片状态用例，覆盖竖图、长图、白底图、低清图、加载失败、地址为空六种情况：三端用 staging 构建、同一组商品，同屏截图对照。compare 模板的数值断言栏按 DSX-09。改正 APP-11v 的两条旧结论：compare-harmony.md:25 把 1:1 记成「一致」，compare-android.md 接受了 1.19；同时改 APP-11v brief 里横滑图「圆角 12」和网格图「1:1 近似」，改为引用 DSX-118 的图框（原 COMP-SPEC-2 ⑩ 的私有稿部分）。真机部分随 DSX-136 一起截图。

来源：g5-12。

**验收**

10 有图片用例编号，并写明是否计入 S1 出门；三端同屏截图进 evidence；对照模板有数值断言栏；两条旧结论已改判；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-90</b> · P1 · 图表验收清单进 10，挂到相关任务，画板自检加读屏同源检查</summary>

负责线：质量（协同 设计）；依赖：DSX-37、DSX-39；承接：与 05 QA-11、QA-12 相关（图表部分，原行补验收列）。

**范围**

目前没有 qa 专线，由 design 兜底执行。10 新增 App 价格走势和后台资金看板两组图表用例：

① 按共用向量断言刻度和几何；

② 标签、提示框、aria-label、表格同源；

③ 浅深两套快照；

④ 200% 字号和 1280 窄窗；

⑤ 空数据、单点、缺失日、请求失败四种数据情况；

⑥ 摘要和标注过禁用词扫描。

这些用例挂到 05 QA-11、QA-12、HM-12、F1-08g 原行的验收列（原行补验收列），以及本计划 DSX-134、DSX-137、DS-02-android-trend、DS-02-harmony-trend 的验收。verify.py 加检查：role=img 的图必须有 aria-label，并有同源的表格或摘要。DS-02/compare-harmony.md:104 的 PriceTrendPanel 改判。

来源：g5-48。

**验收**

10 有图表用例编号；05 对应任务的验收列引用了这些编号；verify 新检查能在现有画板上跑通，并列出不合格清单；kanban --check --local 无 WARN。

</details>

<details>
<summary><b>DSX-91</b> · P1 · 三端组件目录页并排对照（真机）</summary>

负责线：质量（协同 设计）；依赖：COMP-SPEC、COMP-SPEC-2、DSX-118、DSX-119、DS-02-iOS-3。

**范围**

目前没有 qa 专线，由 design（编排）兜底执行。按 component-spec.json 逐个组件截三端目录页（iOS、Android staging 调试面板、鸿蒙真机）的浅色、深色、200% 三档，并排做成对照页；鸿蒙关怀模式的档位等 DSX-133 定封顶后另补，不在本单。每处差异标为「一致 / 允许的原生差异 / 违规」，违规项开到 DS-03 或对应的迁移任务。顺带在真机上核对半屏和对话框的遮罩深浅、圆角、把手。内测发包前跑一轮，之后组件库有改动时抽查。

来源：g2-45。

**验收**

对照页覆盖 component-spec.json 的全部组件，三端各有浅深两态；每处差异都有分类和任务键；违规项在内测发包前清零，或有编排记录的延期理由。

</details>

<details>
<summary><b>DSX-136</b> · P1 · 内测前人工真机冒烟一轮（7 个关键页 × 三端截图和录屏）</summary>

负责线：质量（协同 设计、iOS、安卓、鸿蒙）；依赖：无；承接：与 05 QA-08 相关（夜间真机冒烟基础设施仍归 QA-08 原行；本单是内测前一轮人工冒烟）。

**范围**

目前没有 qa 专线，由 design 兜底执行。内测前至少跑一轮：7 个关键页 × 三端真机截图和录屏，存私有 bucket，与模拟器基准并排抽查。四个仓库都还没有 Maestro 流程，本轮可以人工驱动，同时登记 Maestro / arkxtest 的落地单。一并执行鸿蒙 R1-07-A。仓库外如果已有脚本，把位置回写 05 QA-08。真机需要负责人接设备时提前告知。

来源：g4-60。

**验收**

私有 bucket 有本轮截图和录屏，并逐页与基准对照；R1-07-A 状态已更新；05 QA-08 或台账记录了脚本位置或后续落地单号。

</details>

<details>
<summary><b>DSX-139</b> · P1 · QA-11 / QA-12 按端立项入账、读屏清单合并（rebate-platform ops/tasks）</summary>

负责线：质量（协同 设计、iOS、安卓、鸿蒙、前端）；依赖：DSX-14；承接：与 05 QA-11、QA-12 相关（原行补验收列由 DSX-14 做，本单只立项入账）。

**范围**

目前没有 qa 专线，由 design（编排）兜底。05 QA-11、QA-12 原行的检查项扩充由 DSX-14 以「05 原行补验收列」完成，执行仍归两个原任务（W4–W5，内测发包前跑一轮），本单不重复立执行任务，也不给原行加前置依赖。本单只改 rebate-platform：

① ops/tasks 按端为 QA-11、QA-12 立项（iOS、安卓、鸿蒙、H5 与后台），每条写明执行页面（7 个关键页加钱包、提现、订单页，QA-12 另加登录页和分享页）、10 的新用例编号（DSX-14）、证据位置（私有 bucket、evidence/acceptance/records.csv），以及执行前应已合并的组件单（FU-DS-*-pages、DSX-48、DS-02-iOS-3、DSX-61 / DSX-70 / DSX-83）作为执行前置说明。

② 把 couli-runs 的 qa12-a11y-checklist.md（10-09 后没更新）和 followups.md 里转真机的读屏项（F-HM-05、F-AND-93 等约 21 行）合成一份带状态的清单，放进 QA-12 的 ops/tasks 条目。

③ 鸿蒙超过 200% 的部分按 DSX-133 的口径另记，定之前按 200% 验收。

来源：g4-58、g4-59、g3-30。

**验收**

① ops/tasks 有 QA-11、QA-12 各端条目，每条都有执行页面、用例编号和证据位置；② 合并清单每条有状态和来源行号；③ CT-06 门禁通过。

</details>
