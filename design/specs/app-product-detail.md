# 商品详情 ProductDetail（App 原生）

- 核对版本：规划提交 b8b7dac（负责人 2026-10-21 定稿，`docs/changes/20261021-App内高保真第1批定稿.md`）；代码主干 67d7a4df（2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>.dc.html`（PNG 在 `review-shop/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 1 批定稿」
- 路由：`ProductDetail`（auth none；参数 `platform`、`product_key`、`item_ref`；入口 in_app、push、deeplink）；从哪来：首页、搜索、热销榜、AI 卡片、识别弹卡、链接直达（F-PROD-02）；去哪：购买链路（[app-product-buy.md](app-product-buy.md)）、`AgentChat`（【问问 AI】）、`ProductShare`（公开版【分享赚】，[app-product-share.md](app-product-share.md)）
- 需求：01 F-PROD-05、F-PROD-07、F-PROD-12（收藏）、F-PROD-14（价格走势）；验收：AC-PROD-xx（同号规则）；任务：05 APP-06 / HM-05、APP-16 / HM-12（收藏、价格走势）
- 可参考的已合并页面：无（派发前按代码主干核对）
- 是否资金或归属页面：否（展示预估；购买与归属在购买链路）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 正常（淘宝有券，比价区间） | Product-v2.dc.html（332e5a6255c4） | 有券 | getProduct · 200 · ProductOk |
| 正常（京东无券，单一金额） | ProductJd.dc.html（772b02da48b3） | 无券、`rebate_basis` 单值 | getProduct · 200（契约只有 ProductOk 一个示例，无券字段按 product_card 置空） |
| 公开版（底栏多【分享赚】） | ProductPublic-v2.dc.html（5910e23441e6） | M-公开（内测期隐藏，TRADE-21） | 同上 |
| 已收藏 | ProductFavorited-v2.dc.html（4f7de72d9e56） | 收藏成功 | addFavorite |
| 收藏夹已满 | ProductFavoriteFull.dc.html（4bcb3a16d770） | 超上限 | 20001（`20001.favorites_full`） |
| 价格走势展开 | ProductPriceTrend-v2.dc.html（fb121836d240） | 展开折叠模块 | getProductPriceTrend · 200 |
| 价格走势暂无记录 | ProductPriceTrendEmpty-v2.dc.html（f225eca45ee2） | 记录天数不足 | 同上（空） |
| 商品失效 | 不适用（无专用画板） | 进页即失效 | 30143；进页即下架 30141 的置灰写法同 app-product-buy「已下架」 |
| 深色 | ProductDark.dc.html（25dbc178d1bf） | 系统深色（00 D35） | 同浅色 |

画板上的商品、店铺、价格、返利、走势均为样例数据。

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 主图 / 标题 / 店铺 | 图片轮播、标题、`PlatformBadge`（14px 官方图标） | product | — |
| 价格区 | `PriceTag`、`RebateTag`（紧挨价格大数字下） | final_price_fen、券、rebate_* | 单一金额时主按钮拼「· 预估返 ¥x」 |
| 口径块 | `DisclaimerFooter`（详情页常驻全文） | — | — |
| 价格走势 | `PriceTrendPanel`（默认折叠、展开才请求） | price-trend | 无券用无券标题 |
| 底栏 | 【问问 AI】【收藏】小图标、【分享赚】（公开版）、`BuyButton` | cta | 收藏未登录走登录并恢复（APP-16）；购买见 app-product-buy |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 购买按钮 | `btn.buy`、`btn.buy.coupon`、`btn.buy.no_rebate`、`btn.buy.rebate_suffix` |
| 口径 | `price_basis`、`price_basis.general`（拼多多按 BR-PRICE-04） |
| 价格走势 | `price_trend.title`、`price_trend.title.general`、`price_trend.source*`、`price_trend.empty` |
| 收藏 | `favorite.add`、`favorite.added`、`favorite.removed`、`error.20001.favorites_full` |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getProduct | 进页、重试 | 30141、30143 |
| getProductPriceTrend | 展开价格走势 | — |
| addFavorite / removeFavorite | 点【收藏】 | 20001、10405 |
| openLink | 点购买（见 app-product-buy） | 同该规格 |

## 6. 稿上没画、实现要做的

价格走势图另给文字摘要供读屏；大字号时底栏按钮不换行截断（03 §10.4）；返利标签读屏读完整句。

## 7. 待定与不一致

- 无。设计自定：京东无券详情 ProductJd 取 ProductJumpBrowser 底稿去掉加载卡，作「无券 + 单一金额」样例。
