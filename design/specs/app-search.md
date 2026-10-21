# 搜索与结果 Search（App 原生）

- 核对版本：规划提交 b8b7dac（负责人 2026-10-21 定稿，`docs/changes/20261021-App内高保真第1批定稿.md`）；代码主干 67d7a4df（2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>.dc.html`（PNG 在 `review-shop/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 1 批定稿」
- 路由：`Search`（auth none；参数 `q`、`platform`；入口 in_app、push、deeplink）；从哪来：首页搜索框与类目、【搜相似商品】（BR-PRICE-08 细则）、AI 暂不可用的引导；去哪：`ProductDetail`、`AgentChat`（「试试这样搜」）
- 需求：01 F-PROD-01～04、F-PROD-07、F-PROD-08、F-LINK-01；验收：AC-PROD-xx（同号规则）；任务：05 APP-06 / HM-05
- 可参考的已合并页面：无（派发前按代码主干核对）
- 是否资金或归属页面：否

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 输入页 | SearchTyping-v2.dc.html（4ae3fa29b07d） | 聚焦未输入 | 本地搜索历史（F-PROD-03）；热词、直达来自后台配置（见 §7） |
| 结果正常 | Search-v2.dc.html（883c38a8fdc8） | 有结果 | searchProducts · 200 · SearchProductsOk |
| 从类目进入 | SearchCategory-v2.dc.html（022228a8cd6b） | 首页类目入口 | 同上 |
| 价格区间筛选 | SearchFilterPrice-v2.dc.html（fd0c24eeb3e2） | 打开筛选 | 同上，`price_min_fen` / `price_max_fen` |
| 空结果 | SearchEmpty-v2.dc.html（b4c98000f13a） | items 为空 | 同上，items 置空、带 `fallback_items`（F-PROD-04） |
| 口径说明半屏 | SearchDisclaimerNote-v2.dc.html（45ba17491ab6） | 点卡片口径按钮 | 本地 |
| 加载中 | SearchLoading.dc.html（aab428a63c88） | 请求在途 | 本地：骨架 |
| 搜索暂不可用 | SearchError.dc.html（cd2cd5ef2f74） | 联盟失败且无可用缓存 | 50304（`data.platform`） |
| 三家搜索都关闭 | SearchDisabled.dc.html（67bb06995d45） | 三家 `search.enabled.<platform>` 都关 | 50304，`data.reason=search_disabled` |
| 深色 | SearchTypingDark.dc.html（5214684aae5b）、SearchDark.dc.html（3f921e438b1d） | 系统深色（00 D35） | 同浅色 |

画板上的商品、价格、返利、热词均为样例数据。

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 搜索框 | 输入框 + 框内【粘贴】（iOS / 鸿蒙系统控件，有输入时换清除键） | `q` | 粘贴只填入输入框（BR-ID-16 手动粘贴「填入输入框」）；链接或口令点【搜索】走 parseInput 直达详情（F-PROD-02） |
| 平台切换 | Tab + `PlatformBadge`（20px 官方图标） | `platform` | 默认 Tab 按 F-PROD-01；关闭的平台不出 Tab（BR-PROD-10 细则） |
| 排序 / 筛选 | 排序条、价格区间、只看有券 | `sort`、`has_coupon`、价格区间 | 改条件重新请求 |
| 列表 | `ProductCard`（紧凑）、`PlatformBadge`（14px）、`RebateTag`、`BuyButton`、`DisclaimerFooter` | items[] | 卡片 → `ProductDetail`；购买见 app-product-buy |
| 三家都关 | 说明 + 粘贴入口（iOS 写法） | — | 只留返回、说明与粘贴入口 |

## 3. 文案键

占位文字：`search.placeholder`（占位文字待搜索页视觉任务定，D10-119 H-V03，暂沿用首页这一键）；列表口径：`price_basis`、`price_basis.general`（BR-PRICE-03 细则「无券商品与混排列表的口径说明」）；出错 / 关闭：BR-TEXT-14 表 A 50304、表 B `50304.search_disabled`；购买按钮：`btn.buy.*`。

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| searchProducts | 搜索、切 Tab、改排序或筛选、翻页、重试 | 50304、42901 |
| parseInput | 输入链接或口令后点【搜索】 | 30131、30132、10405 |
| getConfig | 启动（`search.enabled.<platform>`、`platform_icons`） | — |

## 5. 开关

`search.enabled.<platform>`（BR-PROD-10 细则「按平台的搜索开关」）。

## 6. 稿上没画、实现要做的

键盘弹起时历史与热词区可滚动；没有输入联想（01 无此项）；大字号、窄屏按 03 §10.4；读屏：平台 Tab 读平台中文名（图标为装饰）。

## 7. 待定与不一致

- 待上游（契约）：搜索热词、关键词直达（F-PROD-03）在契约里还没有下发字段，补齐前输入页「搜索发现」不实现数据，只留历史。
- 待上游（契约）：`texts.default.json` 暂无 `search.placeholder`、`price_basis*` 键。
