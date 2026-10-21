# 订单列表 OrderList（App 原生）

- 核对版本：规划提交 32a9765（负责人 2026-10-21 定稿 App 内高保真第 2 批，`docs/changes/20261021-App内高保真第2批定稿.md`）；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-money/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 2 批定稿」；画板名为 `Orders*`
- 路由：`OrderList`（native，auth login，参数可选 `scope`=self / share，入口 in_app / push，`agent_guide`）；从哪来：Tab 或「我的」宫格、钱包「订单」、推送、Agent 引导卡；去哪：`OrderDetail`（order_id）、`FindOrder`（「未跟单？去找回」）
- 需求：01 F-ORD-07、F-ORD-15、F-ORD-09（找回入口）；规则只引编号：BR-TEXT-02 细则「订单列表的状态分组与查找」「订单号的显示」「订单的检索范围与分享单的投影」、BR-ATTR-17（置顶条件）、BR-TEXT-10 细则「金额隐藏」、BR-TEXT-24、BR-ID-30 细则「订单类记录」；验收：AC-ORD-07 / AC-ORD-15（同号）、10 AC-S1-103、AC-S1-73、AC-S1-25、AC-S1-106；任务：05 APP-08 / HM-06
- 可参考的已合并页面：无（原生仓库不在本次核对范围；组件按 03 §10.2）
- 是否资金或归属页面：是（展示归属与返利，不写）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 自购列表 | Orders-v2.dc.html（7f56b9f5ffe0） | scope=self（默认） | listOrders · 200 · example |
| 分享列表 | OrdersShare-v2.dc.html（92b09141ab1d） | scope=share；单号脱敏、不可复制，好友买的其他商品无图无标题 | listOrders（scope=share） |
| 自购为空、分享为空 | OrdersEmpty.dc.html（427293e05b21）、OrdersShareEmpty.dc.html（b3d648e2013f） | items 为空 | 同上，列表置空 |
| 付款月份筛选 | OrdersFilterMonth-v2.dc.html（33fe2f489da0） | 点「月份」 | listOrders（paid_month）；可选月份限于 earliest_visible_date 之后 |
| 平台筛选 | OrdersFilterPlatform-v2.dc.html（2b34babe402c） | 点「平台」，半屏列表项带 20px 官方图标 | listOrders（platform） |
| 搜索结果、无结果 | OrdersSearch-v2.dc.html（b07ddb68814f）、OrdersSearchEmpty.dc.html（ab5b424a11a1） | 输入 q；分享单只按标题 | listOrders（q） |
| 「未跟单？去找回」置顶 | OrdersClaimPinned.dc.html（9b1b9a111971） | claim_entry_pinned=true（只在 scope=self） | listOrders |
| 金额隐藏 | OrdersHidden.dc.html（b7b4ec5fecb5） | 本机偏好开启（与「我的」、钱包共用） | 本地 |
| 断网显示上次数据 | OrdersStale-v2.dc.html（c7933dc74d6e） | 请求失败且有上次数据 | 本地缓存 |
| 深色 | OrdersDark.dc.html（6be77e80f0ea） | 系统深色（00 D35） | 同自购列表 |
| 加载、加载更多、无缓存时出错 | 不适用（无画板；Skeleton / ErrorState） | — | 本地 |

画板上的订单号、商品、金额均为样例；商品图为自绘示意。

## 2. 组件

| 区域 | 组件 | 数据（接口字段） | 交互 |
| --- | --- | --- | --- |
| 顶部 | 自购 / 分享子 Tab + 状态分组 + 平台、月份筛选 + 搜索框 | status_group、platform、paid_month、q | 切换即重查；状态分组成员只按服务端 |
| 订单卡 | 卡片：`PlatformBadge`（14px 官方图标，装饰）+ 标题、商品图、件数、订单号；`AmountGrid`（左实付或已付定金，右返利或推广收益）；状态标签单独一行 | platform、title、image_url、quantity、order_no / masked_order_no、pay_amount_fen、est_rebate_fen 等、display_status | 点卡进 `OrderDetail`；自购单号【复制】（`order_detail.copy.done`），分享单不可复制 |
| 找回入口 | 右上角常驻入口；置顶时为列表首行整行入口、右上角不重复 | claim_entry_pinned | 进 `FindOrder`；`claims.enabled` 关闭时置灰 |
| 查询范围提示 | 列表底部一行 | earliest_visible_date | 设了范围时显示 |
| 待跟单卡 | 第 1 批画板（ProductPendingTrack*），本批不重出 | listPendingTracks | 关闭带 attempt_id（dismissPendingTrack） |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 分组、筛选、搜索框 | `order_status_group.*`、`order_list.filter.platform` / `.filter.month`、`order_list.search.placeholder` / `.placeholder_share` |
| 状态标签 | `order_status.<display_status>.label`；未知编码 `order_status.UNKNOWN` |
| 好友买的其他商品、已付定金、查询范围 | `order_list.other_product`、`order_list.deposit_amount`、`order_list.history_hint` |
| 「未跟单？去找回」 | BR-ATTR-17 原句，键未建（第 7 节） |
| 金额隐藏、断网、复制反馈 | `amount_mask.*`、`net.stale_data`、`order_detail.copy.done` |
| 金额、日期 | BR-TEXT-10、BR-TEXT-11 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| listOrders | 进页、切 Tab / 分组 / 筛选、搜索、翻页 | 无业务码（x-error-codes 为空） |
| listPendingTracks / dismissPendingTrack | 显示 / 关闭待跟单卡（第 1 批规格） | dismiss：20001、10405 |

## 5. 权限点与开关

`claims.enabled`（关闭时找回入口置灰，error.30206）；平台筛选可选项按契约 `platform` 枚举与平台开关（BR-TEXT-24）。

## 6. 稿上没画、实现要做的

加载更多与到底提示；金额隐藏同时覆盖读屏名称（实付、已付定金不隐藏，画板结论）；32 高胶囊与复制按钮命中区 ≥ 44；平台图标不重复播报、筛选项播报选中；大字号与窄屏（适配证据稿 AdaptNarrowOrders、A11yHitOrders 仍为文字来源标签的旧写法，以本批画板为准）。

## 7. 待定与不一致

- 待上游（08 BR-TEXT-14 补键）：「未跟单？去找回」只在 BR-ATTR-17 正文，未登记字典键。
- 待上游（设计文档）：适配与读屏证据稿里的来源标签旧写法，随证据稿更新时改（变更记录待回写清单）。
