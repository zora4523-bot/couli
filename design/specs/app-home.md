# 首页 Home（App 原生）

- 核对版本：规划提交 b8b7dac（负责人 2026-10-21「全部定稿吧 先开发 后面在微调」，`docs/changes/20261021-App内高保真第1批定稿.md`）；代码主干 67d7a4df（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>.dc.html`（1 倍 PNG 在 `review-shop/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 1 批定稿」
- 路由：`Home`（auth none；入口 in_app、push、deeplink）；从哪来：启动、底栏；去哪：`Search`、`AgentChat`、`ProductDetail`、`HotRankList`（公开版金刚区）、`Login`（游客价值卡）、卡片 action 指向的路由
- 需求：01 F-HOME-01～09、F-CLIP-01～06；验收：AC-HOME-xx、AC-CLIP-xx（同号规则）；任务：05 APP-11 / HM-07（SDUI、popup）、APP-07 / HM-05（剪贴板、`PasteButton`）
- 可参考的已合并页面：无（派发前按代码主干核对）
- 是否资金或归属页面：否（识别卡上的购买走 [app-product-buy.md](app-product-buy.md)）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 已登录（内测版 / 公开版） | Main-v3.dc.html（2ab2d11a402a）、MainRankEntry-v3.dc.html（a9488b8617ae） | 已登录；公开版金刚区配置了热销榜入口 | getPage（page_key=home）· 200；卡片形状 `contracts/home-schema.json` |
| 游客 | HomeGuest-v3.dc.html（2e75bc1fbdf9） | 未登录 | 同上；「订单没显示怎么办」卡按 condition.login 只对已登录下发（03 §6.1）；顶部价值卡见 §7 |
| 首页弹窗（Lottie / 静态兜底） | MainPopup-v3.dc.html（09e41d992abc）、MainPopupStatic.dc.html（e260d467f340） | 配置有 popup 卡且命中人群、次数、时段（F-HOME-08）；兜底图在动效加载失败、网速慢、系统减弱动态效果时（BR-TEXT-26） | popup 卡；动效字段见 §7 |
| 剪贴板首次用途说明（2026-10-30 停用，不实现） | HomeClipboardConsent-v3.dc.html（8f6ee27ab7ae） | 未看过用途说明时首次点【粘贴】或开启自动识别（BR-ID-16 细则「首次用途说明弹层」） | recordConsent（BR-ID-12） |
| 识别到商品弹卡 | HomeClipboardCard-v3.dc.html（87ca6a98d539） | 自动识别或手动粘贴得到商品（BR-ID-16） | parseInput · 200 · ParseInputOk |
| 识别其他结果 ①～⑥ | HomeClipboardResults-v3.dc.html（8a1e3eb16be4） | ① 识别不了 ② 已下架 ③ 暂无返利 ④ 查不到价格 ⑤ 网络失败 ⑥ 线报素材 | ① 30132 ② availability=off_shelf ③ rebate_basis=no_rebate、不带 tlj、no_rebate_cause 为空 ④ 查不到价格结果（BR-PRICE-01 / 10）⑤ 本地 ⑥ F-CLIP-04 |
| 识别到邀请码提示条 | HomeClipboardInvite-v3.dc.html（39453277db9c） | 未命中商品、命中邀请口令（BR-INV-04 ③；游客或可补填的已登录用户，稿画游客） | 本地识别；点【绑定】的去向按 BR-INV-04 细则，已登录确认后调 bindInviter |
| 深色 | MainDark-v3.dc.html（d208bbdc84a5）、HomeClipboardCardDark-v3.dc.html（a6c2e00b4343）、MainPopupDark.dc.html（467782a4c301） | 系统深色（00 D35） | 同浅色 |

画板上的商品、价格、返利、邀请码均为样例数据。首页加载兜底无专用画板（三级兜底，F-HOME-04）。

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 顶部原生区 | 搜索框、【问 AI】、常驻粘贴卡、游客价值卡（只对游客） | — | 搜索框 → `Search`；【问 AI】→ `AgentChat`；【登录领返利】→ `Login` |
| 粘贴卡 | iOS UIPasteControl / 鸿蒙 PasteButton（文字图标由系统给，只调底色与圆角）；Android 自绘按钮 | — | 手动粘贴任务（03 §4.6）；2026-10-30 起不再先出用途说明弹层 |
| SDUI 卡片 | 03 §6.3 注册表；`ProductCard`、`PlatformBadge`（14px 官方图标）、`RebateTag`、`DisclaimerFooter` | sections | 卡片 action 按 routes 跳转；商品卡 → `ProductDetail` |
| 弹窗 | `Dialog`：图片 / 动效区 + 关闭按钮 | popup 卡 | 点图片区按 action 跳转；关闭按钮出现即可点 |
| 识别弹卡 | `Sheet` + `ProductCard` + `BuyButton` | parseInput 结果 | 购买见 app-product-buy；【搜相似商品】按 BR-PRICE-08 细则「搜相似商品」 |

## 3. 文案键

粘贴卡：`clipboard.paste_hint`（BR-ID-16「按钮文字」）；用途说明弹层：`clipboard.consent.*`（BR-TEXT-14 表 D）；邀请提示条：`clipboard.invite_prompt`；识别结果：表 A 30132、30141；`btn.buy.*`、`btn.search_similar`；口径 `price_basis`、`price_basis.general`；首页兜底：`home.fallback`；游客价值卡两句：08 未登记（待回写清单第 1 条）。

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getPage | 进页、下拉刷新 | 30701 |
| getConfig | 启动（剪贴板开关、`platform_icons`） | — |
| parseInput | 识别到候选、手动粘贴 | 30131、30132、10405 |
| recordConsent | 用途说明点【开启】 | 20001、10401、10402、10405 |
| bindInviter | 已登录用户确认绑定 | 契约 x-error-codes |

## 6. 开关与开发验收

- 开关：`clipboard.enabled`（按端）；首页配置 condition.login；popup 每日次数与时段（F-HOME-08）；`search.enabled.<platform>`（【搜相似商品】的 Tab 回退）。
- Android 自绘粘贴按钮（画面按 iOS / 鸿蒙系统控件画）：默认卡片标题保留，按钮文字照 BR-ID-16 Android 写法用「粘贴查返利」，标题与按钮的排法待设计下次改稿确认（待回写清单第 12 条）。
- 弹窗读屏名默认「首页弹窗」，契约 popup 暂无替代文字字段；UIPasteControl / PasteButton 的可配置项接入时对照官方文档；`section_popup.lottie` 由契约线 CT-07b 补；大字号、窄屏、读屏顺序按 03 §10.4 / §10.5。

## 7. 待定与不一致

- 待上游（契约）：01 F-HOME-08、BR-TEXT-26 与 04 popup 已有 lottie，`home-schema.json` 的 `section_popup` 还没有；`texts.default.json` 暂无 `clipboard.paste_hint`、`clipboard.consent.*`、`btn.search_similar`、`price_basis*` 等键。
- 待上游（规划）：首页顶部原生区的常驻粘贴卡与游客价值卡，01 §4.2 / F-HOME-02、03 §6 未写（清单第 3、4 条）。
- 待上游（规划）：已下架卡不显示价格与返利是画板做法，BR-PRICE-14 细则只写置灰与【搜相似商品】（清单第 2 条）。
- 画板说明与细则：识别结果卡【搜相似商品】说明末句「回到原卡后原按钮照常可用」按 BR-PRICE-08 细则只指第 1 种——「暂无返利」卡的【去购买（无返利）】照常可用；已下架卡回来后仍只有【搜相似商品】可点。画板不改，下次改稿修正说明（清单第 13 条）。
