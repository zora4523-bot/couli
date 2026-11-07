# 凑狸 · Android 界面与交互细则

2026-11-07 · 状态：生效 · 先读[总则](README.md)。本文只写 Android 怎么落地。工程：`rebate-android`（Jetpack Compose，Material 3，targetSdk 36）。API 的确切签名、所需库版本以 Android / Material 官方文档为准；标「以官方文档为准」的，实现前先查。

路径写文件名与行号（在仓内唯一）；组件库在 `core/designsystem/src/main/kotlin/com/couli/core/designsystem/`。审计基于提交 `c8eac4a`。

---

## 1. 需求 → Material 3 组件对照表

| 需求 | 用 | 要点 |
| --- | --- | --- |
| 底栏 | `NavigationBar` + `NavigationBarItem` | 见 §2（D10-827，FU-AND-NAV-BAR-android） |
| 页面骨架 | `Scaffold`（`topBar`、`bottomBar`、`snackbarHost`、`contentWindowInsets`） | 系统边距由 Scaffold 统一处理，不在各页零散补 |
| 顶栏 | `TopAppBar` / `CenterAlignedTopAppBar` / `LargeTopAppBar` + `scrollBehavior`（`TopAppBarDefaults` 的滚动行为） | 不在页面里用 Row 自写顶栏 |
| 返回 | 系统返回 + 预测性返回 | 不常开 `BackHandler`；只在需要拦截时启用（如未保存确认）；预测性返回的清单开关与导航库版本要求以官方文档为准 |
| 页面转场 | navigation-compose 的 enter / exit / popEnter / popExit 转场 | 用 Material 运动规范的默认值，不设 0 |
| 半屏 | `ModalBottomSheet` | 已在用（11 处），统一参数放薄封装 |
| 弹窗 / 确认 | `AlertDialog` | 替换自绘内容的 CouliDialog |
| 操作菜单 | `ModalBottomSheet` 列表或 `DropdownMenu` | — |
| 轻提示 | `Snackbar`（经 Scaffold 的 `SnackbarHost`） | D10-827 ⑥；替换顶部自画的 CouliToast |
| 列表行 / 设置页 | `ListItem`（在 `LazyColumn` 内，整行可点） | 开关行用 `ListItem` + trailing `Switch` |
| 开关 | `Switch` | 品牌色经主题 |
| 勾选 | `Checkbox`（M3 方形） | D10-827 ⑥：用系统默认，不画圆形 |
| 单选 | `RadioButton` + `Modifier.selectable` 行 | — |
| 分段 | `SegmentedButton`（单选行）或 `PrimaryTabRow` | 具体组件名与版本以官方文档为准；不仿 iOS 分段 |
| 筛选胶囊 | `FilterChip` | — |
| 搜索 | `SearchBar` / `DockedSearchBar` | 以官方文档为准 |
| 菜单 | `DropdownMenu` | — |
| 下拉刷新 | `PullToRefreshBox`（M3） | 已在用（5 屏）；数据回来再收起 |
| 侧滑操作 | `SwipeToDismissBox` | — |
| 长按菜单 | `combinedClickable(onLongClick = …)` + `DropdownMenu` | 复制订单号等 |
| 输入框 | `OutlinedTextField` / `TextField` + `KeyboardOptions` | 碰资金的输入页另批迁移（冻结用例） |
| 日期 / 选择器 | `DatePicker` / `DatePickerDialog` | — |
| 按钮 | `Button` / `FilledTonalButton` / `OutlinedButton` / `TextButton` / `IconButton` | 品牌样式经主题与 `ButtonDefaults` 参数，不用 Box 重画 |
| 卡片 | `Card` / `ElevatedCard`（`onClick` 重载） | 整卡可点用带 onClick 的卡片，自带涟漪 |
| 转圈 | `CircularProgressIndicator` | 首屏用骨架 |
| 图片 | 统一的「商品图」L2 组件 | 占位 + 渐显 + 缓存 + 失败态；渐显用项目所用图片库的选项（以项目选型为准） |

---

## 2. 底栏（D10-827）

- 保留 `TabBar(...)` 签名，内部换成 `NavigationBar` / `NavigationBarItem`（审计时自绘在 `NavigationComponents.kt:255-315`）。
- 配色只经 `NavigationBarItemDefaults.colors` 取主题色；选中只在 Router 放行后写入，被守卫拦下不变（与 iOS D10-826 同义）。
- 去掉 TabShell 底部垫色条，底栏的系统边距铺到屏底（edge-to-edge 已开，`MainActivity.kt:104`）。
- 读屏不播「第几个、共几个」、200% 字号下底栏文字被裁：**接受系统行为**（D10-827 ①②）。
- Tab 切换内容用淡入过渡，不直接换内容（审计：`TabShell.kt:103-105`）。

## 3. 触感（统一入口）

在组件库放一个统一入口，页面只调它：

| 时刻（总则 §3.2） | 写法 |
| --- | --- |
| 选择变化 | `LocalHapticFeedback.current.performHapticFeedback(…)` 的选择 / 分段类型，或 `LocalView.current.performHapticFeedback(HapticFeedbackConstants.CLOCK_TICK)` |
| 操作成功 | `HapticFeedbackConstants.CONFIRM`（API 30+） |
| 被拦 / 失败 | `HapticFeedbackConstants.REJECT`（API 30+） |
| 达到阈值 / 长按 | `HapticFeedbackType.LongPress` 或 `HapticFeedbackConstants.LONG_PRESS` |

- Compose `HapticFeedbackType` 可用的类型随 compose-ui 版本增加，以官方文档为准；低版本系统没有的常量要降级。
- 不要：在滚动、列表加载、普通点击上加触感；系统 `Switch`、长按菜单自带的不重复加。

## 4. 动效

- 状态与内容：`AnimatedVisibility`、`AnimatedContent`、`Crossfade`、`animate*AsState`、`Modifier.animateContentSize()`、列表项 `Modifier.animateItem()`。
- 时长与缓动用 Material 运动规范的默认值（M3 的运动令牌与 MotionScheme 以官方文档为准）。
- 金额与数字变化：`AnimatedContent` 做数字滚动或淡入替换。
- 减弱动态：系统「移除动画」开启（动画时长缩放为 0）时跳过位移与微光（读取方式以官方文档为准）。
- 审计：全仓 `androidx.compose.animation` 导入为 0；折叠展开硬切（`CouliLists.kt:439-445`）；导航框架没配转场（`AppNavHost.kt:108`）。

## 5. 按压反馈

- 可点元素用带 indication 的 `clickable`（默认涟漪）或 M3 组件的 `onClick` 重载（`Card`、`ListItem` 所在行、`Button` 系列）。
- 不要：`indication = null`（审计：`LoginScreen.kt:452`、`:554`、`:714`）；用 Box 加 `clickable` 自己模拟按钮按下态（审计：`CouliButtons.kt:83-98`、`:309-321`）。

## 6. 品牌主题接入

- `CouliTheme` 包 `MaterialTheme`：
  - 色彩：全部色彩角色取令牌，**恢复 surfaceContainer 系列的色调层级与 `surfaceTint`**（审计：`CouliTheme.kt:95`、`:105-111` 把层级压平了）。不用动态取色（品牌色固定）。
  - 字体：**补齐 M3 全部 15 个字体角色**（审计：只映射了 8 个，`CouliTheme.kt:137-147`），字阶取令牌。
  - 形状：`shapes` 取令牌圆角（审计：没传，用的是默认值）。
- 页面读 `MaterialTheme`（审计：页面里读 `MaterialTheme` 为 0、直接读 `CouliColors` 822 处），迁移页面时逐步改。
- 深色：跟随系统（已做，`CouliTheme.kt:25`）；深色色值进令牌唯一源（审计：仍是提案，`CouliThemeTokens.kt:12-17`）。
- 层级：优先用 M3 色调层级表达层次，阴影只取令牌（审计：卡片一档阴影 2dp、透明度 0.06，`CouliFoundation.kt:80-81`、`:148-171`）。

## 7. 审计发现与迁移优先级（`c8eac4a`）

| # | 问题 | 证据 | 优先级 | 承接 |
| --- | --- | --- | --- | --- |
| 1 | 底栏是一行 Row | `NavigationComponents.kt:255-315` | P0 | FU-AND-NAV-BAR-android |
| 2 | G1 守卫方向相反（feature 不得直接用 13 个 M3 控件）；基线已过期；LINT-STYLE 计划还要把 Button 系列加入禁用 | `DesignSystemGuard.kt:6-31`、`tools/ci/design-system-required-baseline.txt` 第 12、14 行；DSX 计划 LINT-STYLE-android | P0 | FU-AND-G1-SYSTEM-CONTROLS |
| 3 | NavBar 默认常开 BackHandler，没有预测性返回；导航无转场 | `NavigationComponents.kt:72`、`AppNavHost.kt:108` | P0 | 页面模板 |
| 4 | 按钮与图标按钮用 Box 重画，页面调用 99 + 21 处 | `CouliButtons.kt:83-98`、`:309-321` | P1 | L2 冲刺（品牌按钮样式） |
| 5 | 弹窗自绘内容 32 处；轻提示自画在页面顶部、延时移除，不是 Snackbar（14 处）；全仓无 Scaffold | `FeedbackComponents.kt:315`（弹窗）、`FeedbackComponents.kt:243-270`（轻提示）、`OrderListScreen.kt:749-763` | P1 | 页面模板 |
| 6 | 自写顶栏 6 处；NavBar 的 scrolled 参数没有页面传，顶栏不随滚动变化 | `LoginScreen.kt:204`、`BindPhoneScreen.kt:1018`、`SearchScreen.kt:264`、`AgentScreen.kt:169`、`OrderListHeader.kt:68`、`WebScreens.kt:609` | P1 | 页面模板 |
| 7 | 动效、触感为 0 | 见 §3、§4 | P1 | 统一入口 |
| 8 | 输入框是 BasicTextField 加自画外框 | `CouliInputs.kt:99`、`:160-171` | P1（碰资金的另批） | 表单页模板 |
| 9 | 页面绕开组件库自画：搜索胶囊、订单仿 iOS 分段、「我的」行与开关、收款单选、登录方形勾选 | `SearchScreen.kt:350`、`:394`、`:473`；`OrderListHeader.kt:197-231`；`MeUi.kt:211`、`:355`；`PayoutAccountScreen.kt:594-610`；`LoginScreen.kt:520-535` | P1–P2 | 页面翻新 |
| 10 | 骨架无微光；商品图从占位硬切 | `FeedbackComponents.kt:204-208`、`ProductCard.kt:392-403` | P2 | L2 冲刺 |
| 11 | 主题：字体角色缺 7 个、色调层级压平、形状未传、页面不读主题 | 见 §6 | P2 | 主题收口 |
| 12 | 组件目录把 Box 版按钮、自绘底栏标为「系统控件」，统计偏乐观 | `app/src/debugFeatures/.../catalog/CatalogRegistry.kt:52-56`、`:133-139` | P2 | 目录改正 |

## 8. 被锁住的东西与解锁方式

- **G1 守卫**（`DesignSystemGuard.kt`，只警告 + 只减不增的基线）：FU-AND-G1-SYSTEM-CONTROLS 改义为「禁止自绘系统已有控件」，系统控件白名单按本文对照表；组件库冻结范围收窄到 L2 业务组件；基线重出（D10-827 ③⑤）。
- **源码契约测试**：`RiskVisualSourceContractTest.kt:67-68` 断言「不再用 M3 OutlinedTextField」，输入框迁移时按 test-change 与 approvals #24 改。
- **快照**：约 1604 张基线；换系统组件按批次一次换值（同批基线只换一次，D10-827 ⑤），只作本端回归基线。
- **LINT-STYLE-android**：按总则 §5 第 0 步先改计划口径再实现——保留禁写死颜色 / 尺寸 / 圆角与禁 `indication = null`，去掉「系统控件直用失败」与把 Button 系列列入禁用。
- **NavBar 的 BackHandler**：迁到 Scaffold + TopAppBar 时去掉常开写法。
