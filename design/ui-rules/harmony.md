# 凑狸 · 鸿蒙界面与交互细则

2026-11-07 · 状态：生效 · 先读[总则](README.md)。本文只写鸿蒙怎么落地。工程：`rebate-harmony`（ArkTS / ArkUI）。组件与 API 的确切写法、所需 API 版本以华为开发者官方文档为准；标「以官方文档为准」的，实现前先在本项目 SDK 上核对。

路径简写（相对 `rebate-harmony` 仓库根）：`DS/` = `common/designsystem/src/main/ets/`，`E/` = `entry/src/main/ets/`，`F:x/` = `features/x/src/main/ets/`，`CAT` = `entry/src/staging/ets/catalog/CatalogManifest.ets`。审计基于提交 `a819d7a`。

---

## 1. 需求 → ArkUI 组件对照表

| 需求 | 用 | 要点 |
| --- | --- | --- |
| 底栏 | `Tabs`（`barPosition: BarPosition.End`）+ `TabContent().tabBar(…)` | 已是系统 Tabs，保持（D10-824）；用 `BottomTabBarStyle(icon, text)` + 系统符号 `TabBarSymbol`（API 12 起支持，本项目下限 API 20 可直接用；目录里「只接图片资源」不成立，2026-11-07 鸿蒙线核实本机 SDK `tab_content.d.ts:1015`），删自绘 tabBar 构建，背景用系统模糊材质（D10-909）；切换动画用系统默认——`BottomTabBarStyle` 的默认切换本就没有过渡，这是系统默认、不算「设 0」；禁止的是把系统有动画的切换手动改成 0，内容区淡入放到组件冲刺第 2 步。角标：三端底栏目前都不显示角标，`badgeIndex` 删除；以后产品要加未读角标须三端一起加（D10-909 ②） |
| 页面与顶栏 | `Navigation` + `NavDestination` 的**系统标题栏**（`.title()`、`.menus()`） | 不再 `hideTitleBar(true)` 后嵌一个空 `Navigation` 充当标题栏 |
| 返回 | 系统返回手势与标题栏返回 | 只在需要拦截时用 NavDestination 的返回回调 |
| 半屏 | `bindSheet`（高度档位 `detents`） | 已有 13 处；统一参数放薄封装（审计：CouliSheet 统一参数在业务里 0 处使用） |
| 弹窗 / 确认 | 系统 `AlertDialog` / UIContext 的弹窗接口 | 替换 22 处自画面板；具体接口以官方文档为准 |
| 操作菜单 | `ActionSheet` 或 `bindMenu` | — |
| 轻提示 | 系统 Toast（`promptAction.showToast`，或 UIContext 的 PromptAction 接口，以官方文档为准） | 不自画 ToastView |
| 列表行 / 设置页 | `List` + `ListItem`（分组用 `ListItemGroup`，长列表设 `cachedCount`） | 不用 Scroll + Column 拼长列表 |
| 开关 | `Toggle({ type: ToggleType.Switch })` | — |
| 勾选 | `Checkbox`（系统默认外观） | D10-827 ⑥ |
| 单选 | `Radio` | — |
| 分段 | `SegmentButton`（ArkUI 高级组件，以官方文档为准） | — |
| 搜索 | `Search` | 替换 TextInput 拼的搜索框 |
| 菜单 / 长按菜单 | `bindMenu` / `bindContextMenu` | — |
| 下拉刷新 | `Refresh` | 已在用（6 屏）；数据回来再收起 |
| 侧滑操作 | `ListItem` 的 `swipeAction` | — |
| 输入框 | `TextInput` / `TextArea`（`type` 选数字、手机号等） | — |
| 日期 / 选择器 | `DatePicker` / `DatePickerDialog`、`TextPicker` | — |
| 空态 / 错误态 | 系统高级组件 `ExceptionPrompt` 能满足时优先（以官方文档为准）；不满足再用 L2 | 目录里写明不用系统件（`CAT:148`），翻新时复核 |
| 转圈 | `LoadingProgress` | 首屏用骨架 |
| 图标 | `SymbolGlyph($r('sys.symbol.…'))` | 通用图标不用 Path 手画 |
| 图片 | 统一的「商品图」L2 组件：`Image` + `alt` 占位 + 渐显 | 审计：商品图无占位渐显（`DS/components/ProductCard.ets:249-259`） |

---

## 2. 触感（统一入口）

- 在组件库放一个统一入口，内部用 `@kit.SensorServiceKit` 的 `vibrator.startVibration`（预置效果 + `usage: 'touch'`）；需要 `ohos.permission.VIBRATE`。预置效果的 id 与各机型支持情况以官方文档为准，不支持时静默。
- 映射按总则 §3.2：选择变化最轻、成功 / 失败各一种、达到阈值轻撞击；系统控件自带的不重复加。
- 审计：全仓振动接口调用为 0。

## 3. 动效

- 状态切换：`this.getUIContext().animateTo({ duration, curve }, …)` 或属性 `.animation({ … })`；出现 / 消失用 `.transition(TransitionEffect…)`（淡入 + 轻微位移）。
- 曲线：系统默认或 `curves.springMotion()` / `curves.responsiveSpringMotion()`；时长按总则 §3.3。
- 列表到详情的商品图可用 `geometryTransition` / `sharedTransition`（以官方文档为准）。
- 减弱动态：读取系统无障碍设置后关掉位移与微光（读取方式以官方文档为准）。
- 审计：`animateTo`、`transition`、`sharedTransition`、`geometryTransition`、弹簧曲线、`symbolEffect` 全为 0；底部 Tab 设了 `animationDuration(0)`（`DS/components/Navigation.ets:177`），内容靠 Visibility 硬切（`E/shell/AppShell.ets:189`）；自绘开关的圆点直接跳（`F:me/PrivacyAboutCsParts.ets:79`、`F:me/SettingsParts.ets:295`）。

## 4. 按压反馈

- 系统 `Button` 自带按压效果。自建的可点区域加 `stateStyles({ pressed: …, normal: … })` 或按压效果属性（如 `clickEffect`，以官方文档为准）。
- 不要：在 Row / Column 上只挂 `onClick`（审计：业务代码 119 个 `onClick` 多数无按压反馈，如 `F:me/MeKit.ets:190-225`、`F:me/SettingsParts.ets:24-74`、`F:orders/OrderListView.ets:392-418`）。

## 5. 品牌主题接入与沉浸

- 主题：`CustomTheme` + `ThemeControl.setDefaultTheme` / `WithTheme`，取值来自令牌。审计时覆盖了系统全部 51 个颜色角色（`DS/CouliColors.ets:126-131`）——复核：品牌相关角色取令牌，系统材质与中性层级角色是否保留系统默认，按官方文档与设计确认后定。
- 深色：跟随系统（已完整，base 与 dark 各 46 色一一对应）。
- 字号：fp 跟随系统，做得好（`AppScope/resources/base/profile/configuration.json:3-4`）；`maxFontScale(1)` 的 4 处逐个复核。
- 沉浸：窗口全屏布局 + `expandSafeArea` 让内容延伸到状态栏与导航条区域，标题栏与底栏用系统材质（窗口与安全区接口以官方文档为准）；审计：窗口未开沉浸，只有外部网页开了全屏（`F:web/ExternalWebView.ets:199`）；弹窗最大高度按顶部 48vp 估安全区（`DS/components/Overlays.ets:359-366`）。

## 6. 审计发现与迁移优先级（`a819d7a`）

| # | 问题 | 证据 | 优先级 | 承接 |
| --- | --- | --- | --- | --- |
| 1 | 标题栏不是系统的：22 个 NavDestination 里 21 个 `hideTitleBar(true)`；NavBar 在页面顶部嵌空 Navigation 当标题栏；5 页手绘头部与 Path 返回图标 | `DS/components/Navigation.ets:67-83`；`F:search/SearchView.ets:633-660`、`F:auth/LoginView.ets:644` 等 | P0 | 页面模板 |
| 2 | 购买流程是自画遮罩加假半屏，不能拖拽关闭、没有系统转场 | `E/trade/TradeOverlay.ets:495-500`、`:639-660` | P0 | 改 `bindSheet` |
| 3 | 关闭回弹：「我的」二级页、登录、绑手机 `EdgeEffect.None`；26 处关滚动条 | `F:me/MeKit.ets:127`、`F:auth/LoginView.ets:1069`、`F:auth/BindPhoneView.ets:1095` | P0（改动小） | 守卫拦 `EdgeEffect.None` |
| 4 | 弹窗 22 处自画面板，系统确认框 0；隐私、权限、更新提示是根页面 Stack 覆盖层 | `DS/components/Overlays.ets:60-254`、`E/pages/RootPage.ets:338-344` | P1 | 改系统弹窗 |
| 5 | 按压态、触感、动画都为 0；Tab 切换时长 0、内容硬切 | 见 §2–§4 | P1 | 统一入口 |
| 6 | 生产页面自绘开关、分段、搜索框、半屏把手 | `F:me/PrivacyAboutCsParts.ets:44-83`、`F:me/SettingsParts.ets:266-299`、`F:orders/OrderListView.ets:392-418`、`F:search/SearchView.ets:640`、`F:me/MeKit.ets:433` | P1 | 页面翻新 |
| 7 | 约 20 屏是 Scroll + Column，没有 swipeAction、吸顶分组、cachedCount | 业务代码 34 处 Scroll | P2 | 列表页模板 |
| 8 | 骨架无微光且只 3 页在用，其余页加载转圈；商品图无占位渐显 | `DS/components/ProductCard.ets:723-735`、`F:wallet/WalletView.ets:299`、`F:orders/OrderDetailView.ets:538` | P2 | L2 冲刺 |
| 9 | 通用图标用 Path 自绘（业务 79 处），SymbolGlyph 15 处 | `DS/components/CouliIcon.ets:65-94` | P2 | 图标统一 |
| 10 | 目录与生产不一致：AgentConsentSheet 标 bindSheet、生产是居中自定义弹窗；AuthSheet、JumpTip 生产是页面内自绘弹层 | `CAT:202-205`、`F:agent/AgentConsentDialog.ets:165-172`、`E/trade/TradeOverlay.ets:495-500` | P2 | 目录改正 |
| 11 | 组件库 27 个系统控件封装里 20 个只在目录出现；各 feature 另有约 60 个本地自绘组件 | — | P2 | 页面翻新时收口 |

## 7. 被锁住的东西与解锁方式

- **目录标记**：`CAT` 的 KIND 标记按实际实现改正，系统控件的条目改为系统样例，只为 L2 业务组件保留完整状态矩阵。
- **样式检查**：LINT-STYLE-harmony 按总则 §5 第 0 步定口径（禁写死样式保留；禁自绘系统控件；新增拦 `EdgeEffect.None` 与 `hideTitleBar(true)` 的规则，确需的走白名单）。
- **截图比对**（03 §11 的 hdc 截图，像素差 ≤1%）：只作本端回归基线；换系统组件按批次重出。
- **BottomTabBarStyle 的 Symbol 支持**：已核实支持（2026-11-07，API 12 起有 `TabBarSymbol`），底栏切到 `BottomTabBarStyle`，见 §1 底栏行（D10-909）。
