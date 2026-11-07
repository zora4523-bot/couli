# 凑狸 · iOS 界面与交互细则

2026-11-07 · 状态：生效 · 先读[总则](README.md)。本文只写 iOS 怎么落地。工程：`rebate-ios`（SwiftUI，部署目标 iOS 16.0）。API 的确切签名与可用版本以 Apple 官方文档为准；标「以官方文档为准」的，实现前先查。

路径简写（相对 `rebate-ios` 仓库根）：`DS/` = `Packages/DesignSystem/Sources/DesignSystem/Components/`，`F/` = `Packages/Features/Sources/`，`A/` = `App/Sources/`。审计基于提交 `93c3662`（之后 DS-02-iOS-1 已合并 `a2f5bdf`：令牌锁 v0.5.1、深色改读生成物）。

---

## 1. 需求 → 系统组件对照表

| 需求 | 用 | 要点 |
| --- | --- | --- |
| 底栏 | `TabView` 系统标签栏（`.tabItem`；iOS 18 起可用 `Tab`） | 见 §2（D10-826） |
| 顶栏 / 导航 | `NavigationStack` + `.navigationTitle` + `.toolbar`（`ToolbarItem`） | 顶级页可用大标题；不另画 NavBar |
| 返回 | 系统返回键与边缘右滑 | 不用 `navigationBarBackButtonHidden(true)`（会连侧滑一起关）；需要「未保存先确认」时按官方文档的拦截写法，不藏返回键 |
| 半屏 | `.sheet` + `.presentationDetents([.medium, .large])` + `.presentationDragIndicator(.visible)`（iOS 16+） | 统一档位写进薄封装，只传参数；可下滑关闭 |
| 弹窗 / 确认 | `.alert` | 标题、正文、按钮角色（`.destructive`、`.cancel`）用系统 |
| 操作菜单 | `.confirmationDialog` | 「去淘宝 / 复制口令」这类选项 |
| 轻提示 | 系统没有 | 优先就地反馈（按钮状态、行内文字）；必须用时只用一个统一的轻量横幅（L2），少用，不盖系统栏 |
| 列表行 / 设置页 | `List` / `Form` / `Section`（`.listStyle(.insetGrouped)` 等） | 行用 `NavigationLink` 或 `Button`，拿系统高亮与读屏 |
| 开关 | `Toggle` | 品牌色经 `tint` |
| 勾选（协议） | `Toggle` + 自定义 `ToggleStyle`，图标用 SF Symbols `checkmark.circle` / `checkmark.circle.fill` | iOS 没有勾选框控件；这是系统交互语义 + 系统符号，不是自绘控件 |
| 单选 | `Picker`（`.inline` / `.menu`）或 `List` 里带勾的行 | — |
| 分段 | `Picker` + `.pickerStyle(.segmented)` | 订单「自购 / 分享」等 |
| 搜索 | `.searchable` | 搜索页的输入、取消、历史用系统行为 |
| 菜单 | `Menu` | 排序、筛选的下拉 |
| 下拉刷新 | `.refreshable { await … }` | **等数据回来再结束**（async 函数返回才收起） |
| 侧滑操作 | `.swipeActions`（在 `List` 内） | 如删除搜索历史 |
| 长按菜单 | `.contextMenu` | 复制订单号、复制口令 |
| 输入框 | `TextField` / `SecureField` + `.keyboardType` + `.textContentType` | 验证码 `.oneTimeCode`、手机号 `.telephoneNumber`；外框用系统样式或令牌圆角的背景，不丢系统光标与粘贴菜单 |
| 日期 / 选择器 | `DatePicker`、`Picker` | — |
| 转圈 | `ProgressView` | 首屏用骨架，不用整页转圈 |
| 图片 | 统一的「商品图」L2 组件 | 系统 `AsyncImage` 没有磁盘缓存；组件内做占位 + 渐显 + 缓存 + 失败态（缓存方案以项目选型为准） |

---

## 2. 底栏（D10-826，负责人 2026-11-07 明确）

- 用 SwiftUI `TabView` 的**系统标签栏**；删掉外壳里 `VStack { content; TabBar }` 的自绘栏与 `.toolbar(.hidden, for: .tabBar)`（审计时在 `A/Shell/ShellViews.swift:59-89`，自绘件在 `DS/Navigation.swift:81-146`）。
- **Liquid Glass**：用 iOS 26 及以后的 SDK 编译时，iOS 26 起系统自动呈现悬浮的 Liquid Glass 标签栏；iOS 16–25 是系统经典样式（部署目标不变）。为此：
  - 要：内容延伸到标签栏下方（滚动内容透出玻璃）；`if #available(iOS 26, *)` 下加 `.tabBarMinimizeBehavior(.onScrollDown)`；品牌色只用 `.tint`。
  - 不要：在 Info.plist 加 `UIDesignRequiresCompatibility`；用 `.toolbarBackground(…, for: .tabBar)` 设不透明背景；用 `UITabBarAppearance` 覆盖背景材质；在底部另垫实色条或叠自绘栏。
- 图标用 SF Symbols（或把凑狸图标做成模板渲染的图片资源）；文字仍取 `ShellDraftTexts` 的文案键。
- **选中只跟随 Router**：`TabView(selection:)` 的绑定 get 读 Router 当前 Tab，set 调 `onSelect` 过守卫；被守卫拦下时 Router 不切，绑定自然回到原值。
- **再点当前 Tab**：回到顶部，已在顶部则回到该 Tab 根页面。SwiftUI 的 `TabView` 不自动做，需要在绑定 set 收到「同一个值」时处理（写法以官方文档为准）。
- 读屏、大字、长按放大交给系统，删掉自写的这部分逻辑；组件目录页的 TabBar 样例改为系统样例。
- **建议（迁移时评估）**：每个 Tab 自己持有一个 `NavigationStack`，使 Tab 内层级导航时标签栏保持可见（HIG）。现在全 App 只有一个 `NavigationStack`、栈底是 Tab 外壳（`A/RootView.swift:144-150`，`Packages/Core/Sources/Router/Router.swift:159`），所以一进二级页标签栏就消失。登录、购买确认等中途流程改为模态呈现。
- 证据：在 iOS 26 以上模拟器截一张悬浮样式截图，连同 iOS 16–25 的经典样式截图进证据。

---

## 3. 触感（统一入口）

在 DesignSystem 放一个统一入口（如 `Haptics`），页面只调它：

| 时刻（总则 §3.2） | iOS 17+ | iOS 16 |
| --- | --- | --- |
| 选择变化 | `.sensoryFeedback(.selection, trigger:)` | `UISelectionFeedbackGenerator` |
| 操作成功 | `.sensoryFeedback(.success, trigger:)` | `UINotificationFeedbackGenerator` `.success` |
| 被拦 / 失败 | `.warning` / `.error` | `UINotificationFeedbackGenerator` `.warning` / `.error` |
| 达到阈值 | `.impact(weight: .light)` | `UIImpactFeedbackGenerator(style: .light)` |

- 要：系统控件（`Toggle`、`.contextMenu`、`Picker` 等）自带的触感不重复加。
- 不要：在滚动、列表加载、普通点击上加触感。

## 4. 动效

- 状态切换用 `withAnimation`：iOS 17+ 优先 `.snappy` / `.smooth`，iOS 16 用 `.spring(response:dampingFraction:)` 或约 0.2–0.3 秒的 `easeInOut`。
- 内容出现 / 消失用 `.transition`（如淡入加轻微位移）；加载到内容用交叉淡化，不硬切（审计：`F/Wallet/WalletScreen.swift:68-84` 硬切）。
- 金额与数字变化用 `.contentTransition(.numericText())`（可用版本以官方文档为准）。
- 骨架：`.redacted(reason: .placeholder)` 或骨架组件 + 微光；`@Environment(\.accessibilityReduceMotion)` 为真时不播微光、位移改淡入。
- 页面转场用系统默认的压栈与模态动画，不自写。

## 5. 按压反馈

- 整卡、整行可点：用 `Button { … } label: { 卡片 }` 加带 `configuration.isPressed` 的 `ButtonStyle`（按下轻微变暗或缩放约 0.97，带动画），或放进 `List` 用 `NavigationLink` 拿系统高亮。
- 不要：`.onTapGesture` 做整卡点击（审计：`F/Orders/OrderCard.swift:37-38`、`F/Search/SearchView+Results.swift:273-275`、`DS/HomeProductCards.swift:129-130`）。
- 品牌按钮：以系统按钮样式为底（如 `.buttonStyle(.borderedProminent)` + `.tint` + `.buttonBorderShape` + `.controlSize`）；必须自定义 `ButtonStyle` 时，按下态要有可见变化并带过渡（审计：`DS/CouliButton.swift:163-190` 按下只换色无过渡；`DS/Foundation.swift:290` 品牌底按钮按下无变化）。

## 6. 品牌主题接入

- 品牌色：资源目录的 AccentColor 与根视图 `.tint`，取值来自生成的令牌（浅 / 深两套）。
- 文字：系统文字样式映射到令牌字阶，继续用 `@ScaledMetric`（审计：`Packages/DesignSystem/Sources/DesignSystem/TokenTypography.swift:65-95` 做得好）。
- 深色：跟随系统。正式包现在锁浅色（`App/Info.plist:41-42`，`A/Shell/AppAppearance.swift:10-19`），按 DSX-127 在深色扫描通过后去锁。
- 系统栏（标签栏、导航栏）的材质不覆盖；浮层需要材质时用系统材质（如 `.regularMaterial`），iOS 26 的玻璃效果 API 以官方文档为准。

## 7. 审计发现与迁移优先级（`93c3662`）

| # | 问题 | 证据 | 优先级 | 承接 |
| --- | --- | --- | --- | --- |
| 1 | 底栏自绘，系统标签栏被隐藏 | `A/Shell/ShellViews.swift:63-89`、`DS/Navigation.swift:81-146` | P0 | D10-826 |
| 2 | 20 个页面藏了系统返回键，边缘侧滑一并失效 | 如 `A/Wallet/WalletRouteViews.swift:55-56`、`A/Search/SearchRouteViews.swift:14-15`、`F/Web/WebScreens.swift:86-87`；团队注释见 `F/Me/SettingsScreen.swift:322` | P0 | DS-02-iOS-3 |
| 3 | 单一导航栈，进二级页标签栏消失 | `A/RootView.swift:144-150` | P0（评估） | 随底栏 |
| 4 | 自写弹层引擎：弹窗 19、半屏 9（只 1 个能下滑关闭）、面板 3、轻提示 19；系统 `.alert` / `.confirmationDialog` 为 0；弹层盖不住系统导航栏，页面只好在弹层出现时藏返回键 | `DS/Modals.swift:20-362`、`F/Purchase/PurchaseOverlay.swift:53`、`F/Me/SettingsScreen.swift:99` | P1 | DS-02-iOS-3 |
| 5 | 整卡点击无按压反馈；品牌底按钮按下无变化 | 见 §5 | P1 | L2 冲刺 |
| 6 | 触感为 0 | 全仓无 `UIFeedbackGenerator` / `sensoryFeedback` | P1 | §3 统一入口 |
| 7 | List / Form / Menu / Picker / searchable / contextMenu 为 0；设置行手写；分段、下划线 Tab、验证码格自绘 | `F/Me/MeSupport.swift:95`、`F/Orders/OrdersScreen+Header.swift:108-141`、`F/Search/SearchView+Header.swift:96-118`、`F/Login/CodeCells.swift:84-106` | P1 | 页面翻新 |
| 8 | 状态硬切；图片无缓存、加载完直接出现；骨架无微光 | `F/Wallet/WalletScreen.swift:68-84`、`DS/ProductRemoteImage.swift:37-52` | P2 | L2 冲刺 |
| 9 | 下拉刷新行为不一：订单等结束才收起，钱包与提现记录立即收回，「我的」轮询 | `F/Orders/OrdersScreen.swift:95`、`F/Wallet/WalletScreen.swift:117`、`F/Wallet/WithdrawRecordsScreen.swift:119`、`F/Me/MeTabScreen.swift:121-126` | P2 | 列表页模板 |
| 10 | 正式包锁浅色 | `App/Info.plist:41-42` | P2 | DSX-127 |
| 11 | 登录页是压栈呈现，左上却放关闭 × | `F/Login/LoginView.swift:73-82` | P2 | 改模态 |
| 12 | 数字键盘无「完成」栏；滑动收键盘只在钱包 3 页 | 如 `F/Wallet/WithdrawScreen.swift:173` | P2 | 表单页模板 |
| 13 | 钱包主卡被「我的」和钱包各复制改了一份 | `F/Me/MeHeroCard.swift:9`、`F/Wallet/WalletScreen+Hero.swift:9` | P2 | L2 冲刺（合一） |

## 8. 被锁住的东西与解锁方式

- **视觉测试与测量探针**：`AppTests` 有 126 个视觉测试文件，代码里约 350 处测量探针（`CouliLayoutProbe`）锁着现在的尺寸与位置。某个组件改成系统控件时，同一 PR 删掉该组件的像素 / 位置断言与探针，快照按新实现重出为本端回归基线，PR 正文写明理由；改冻结测试按规划/11 与 approvals #24 走。
- **浅色锁**：DSX-127。
- **守卫与样式检查**：LINT-STYLE-ios 的「禁系统控件直用」与 DSX-60「G1 转为失败」改为「禁自绘系统控件」（总则 §5 第 0 步）；「禁写死样式」照旧。
- **组件目录页**（`A/Debug/Catalog/`）：系统控件的条目改为系统样例；只为 L2 业务组件保留完整的状态矩阵。
