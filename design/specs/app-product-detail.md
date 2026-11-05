# 商品详情 ProductDetail（App 原生）

- 核对版本：规划提交 0949b0a 加本次回写（负责人 2026-11-04～11-05 逐轮给意见、按 r13 为最后一轮回写的商品详情 v3，`docs/changes/20261105-商品详情v3定稿.md`）；代码主干未核对（派发前核对）
- 画板存放：`couli-runs/design-hifi/project/<文件名>.dc.html`（v3 的 PNG 在 `review-detail/v3/png/`，逐轮意见与字段显隐表在同目录 `README.md`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「商品详情 v3 定稿」；v3 取代第 1 批的 Product-v2、ProductJd、ProductDark、ProductPriceTrend-v2 与 ProductPublic-v2（公开版底栏），这几张不再作实现依据；画板上的商品、店铺（拼多多店「云朵柔」是虚构）、价格、返利、走势均为样例数据
- 路由：`ProductDetail`（auth none；参数 `platform`、`product_key`、`item_ref`；入口 in_app、push、deeplink）；从哪来：首页、搜索、热销榜、收藏夹、AI 卡片、识别弹卡、链接直达（F-PROD-02）；去哪：购买链路（[app-product-buy.md](app-product-buy.md)）、`AgentChat`（【问问 AI】）、`ProductShare`（公开版【分享赚】，[app-product-share.md](app-product-share.md)）、平台店铺页（【进店】外跳）
- 需求：01 F-PROD-05、F-PROD-12（收藏）、F-PROD-14（价格走势）、F-PROD-15（反馈）；验收：10 AC-S1-01-*、AC-S1-141、AC-S1-186、AC-S1-187；任务：05 APP-06 / HM-05、APP-16 / HM-12，新增部分由编排派工
- 可参考的已合并页面：无（派发前按代码主干核对）
- 是否资金或归属页面：否（展示预估；购买与进店的归因在服务端）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 正常 · 淘宝有券（多图） | Product-v3.dc.html（5d06d0a1480e） | 有券、单一金额、≥ 2 张图 | getProduct · 200 · ProductOk（详情专用字段待契约，04 §8.3） |
| 正常 · 拼多多有券（销量、店铺评分） | ProductPdd.dc.html（333b6a50e63b） | 拼多多；销量与评分按平台开关 | 同上 |
| 正常 · 京东无券（单张图） | ProductJd-v2.dc.html（3e7ad1c09aec） | 无券（售价）、只有 1 张图 | 同上（无券字段按 product_card 置空） |
| 价格走势展开（含最常见价） | ProductPriceTrend-v3.dc.html（9f4f94dbe44c） | 展开折叠模块 | getProductPriceTrend · 200（`mode_price_fen` 待契约） |
| 反馈半屏 | ProductFeedbackSheet.dc.html（81d27e7c10e5） | 点反馈入口 | 商品反馈接口（待契约） |
| 深色 | ProductDark-v2.dc.html（cec93f3000a6） | 系统深色（00 D35） | 同浅色 |
| 已收藏 / 收藏夹已满 / 走势暂无记录 | ProductFavorited-v2（4f7de72d9e56）、ProductFavoriteFull（4bcb3a16d770）、ProductPriceTrendEmpty-v2（f225eca45ee2）沿用；背景是旧版详情，按 v3 骨架实现 | 收藏成功；超上限；记录不足 | addFavorite；20001（`20001.favorites_full`）；getProductPriceTrend（no_data） |
| 无返利 | 不适用（无专用画板） | getProduct 返回 `rebate_basis=no_rebate` | 只显示 `no_rebate.notice` 与【搜相似商品】，不显示价格与购买区（BR-PRICE-08） |
| 拿不到金额（amount_unknown） | 不适用 | 不进详情 | —（拼多多直链降级卡没有 product_key，见 §7） |
| 商品失效 | 不适用 | 进页即失效 | 30143；进页即下架 30141 的置灰写法同 app-product-buy「已下架」 |

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 主图 | `ProductGallery` | image、images[]（≤ 9） | 左右滑；≥ 2 张显示页码；图上只浮返回键 |
| 价格区 | `PriceTag`（详情形态） | final_price_fen、coupon_fen、coupon_end_at、is_presale；stale、age_sec、quoted_at | 主价 + 券标签，无券不显示券标签；报价降级时券标签下方显示取价提示（BR-PRICE-11） |
| 标题 | `PlatformBadge`（标题标签）+ 标题 | platform、shop_type、title；sales_text（只拼多多） | 标签与标题同一段文字、两行省略；销量一行为空不显示 |
| 店铺块 | `StoreCard` | shop_name、shop_logo、shop_scores[]、shop_entry | `shop_entry=true` 整块点击 → 店铺转链 → 外跳；头像：拼多多店铺 logo，淘宝、京东平台标识图，天猫通用店铺图标；评分：拼多多三项等级，京东店铺等级原样数字，淘宝不放 |
| 价格走势 | `PriceTrendPanel` | price-trend（含 mode_price_fen） | 默认折叠、展开才请求；拼多多与无券换标题 |
| 反馈 | 走势下方文字入口 + `FeedbackSheet` | link_id、券后价、返利金额、quoted_at | 规则见 F-PROD-15 |
| 底栏 | `BuyBar`：【问问 AI】【收藏】+ 组合胶囊（【分享赚】+ `BuyButton`） | cta、rebate_min_fen | 购买见 app-product-buy；内测期与未满 18 周岁不出【分享赚】 |

不显示：券前价、「有券」标签、预估返后价、正常态取价时间、口径小字（`DisclaimerFooter`，BR-PRICE-03 细则「商品详情页不展示口径说明」）。三平台模块顺序一致，字段没有就整块不显示，平台差异只在口径词（拼多多「拼单」）。开关：`shop.entry.enabled.<platform>`（默认 off）与来源 `shop.entry.source.<platform>`；`detail.sales.enabled.<platform>`、`detail.shop_scores.enabled.<platform>`（默认 off，先拼多多）；`feedback.enabled`（派生 `/v1/config.features.flags.product_feedback`）；内测期按 TRADE-21 不出【分享赚】。

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 主按钮 | `btn.buy.rebate`、`rebate_login_to_view`；点击时变成无返利后 `btn.buy.no_rebate`（08 BR-TEXT-12 细则「购买按钮」）；`btn.buy.rebate_unknown` 不用于详情（§7） |
| 主图与价格区 | `product.gallery.position`、`product.gallery.position.a11y`；`coupon.tag`、`coupon.valid_until`；`tag.presale`、`presale.price_note` |
| 标题与店铺 | `platform.tag.*`；`rank.sales.neutral`（拼多多销量）；`shop.enter`、`shop.name.fallback`、`shop.a11y`、`shop.a11y.enter`、`shop.score.*` |
| 价格走势 | `price_trend.title`、`.title.general`、`.title.pdd*`、`price_trend.source*`、`price_trend.empty`、`price_trend.current`、`price_trend.mode`、`price_trend.mode.note*` |
| 反馈、无返利、收藏 | `feedback.*`；`no_rebate.notice`、`btn.search_similar`；`favorite.add`、`favorite.added`、`favorite.removed`、`error.20001.favorites_full` |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getProduct | 进页、重试 | 30141、30143 |
| getProductPriceTrend | 展开价格走势 | — |
| 店铺转链 `POST /v1/products/{product_key}/shop/open`（待契约） | 点【进店】 | 10001、30101、30102、30111；不能进店的码待契约 |
| 商品反馈 `POST /v1/products/{product_key}/feedback`（待契约） | 点【提交】 | 20001、42901 |
| addFavorite / removeFavorite | 点【收藏】 | 20001、10405 |
| openLink | 点购买（见 app-product-buy） | 同该规格 |

## 6. 稿上没画、实现要做的

报价降级提示、拼多多无券走势标题、京东店铺等级、天猫店头像、无返利提示页没画；走势图另给文字摘要；字号放大或屏窄时底栏改两层、按钮字不截断（03 §10.4）；读屏：主图名称带页码，标题标签与标题读成一句，店铺入口以平台名开头，组合胶囊先读「分享赚」再读购买。

## 7. 待定与不一致

- 待上游：详情专用字段、`mode_price_fen`、店铺转链与商品反馈两个接口、新文案键都还没进契约（04 §6.3、§8.3；`texts.default.json`）；四种平台标签色与图上控件的半透明底未进 `design/tokens`；天猫标识图暂缺（06 Q-E7）；反馈的后台查看页、权限点与反馈记录的留存登记待规划（变更记录 §7），上线前补齐。
- 待 09：拼多多 sales_tip 原样格式与 desc / serv / lgst 取值、京东 shopLevel 满分与 goods.query 权限、多图张数、三平台店铺推广链接能否带上用户归因；验证前对应开关保持关。
- 画板设计说明里留有早轮写法（两行主按钮「领券购买 / 预估返」、「购买 预估返」中间留空格、口径小字三句等），以画面与 README R12、R13 为准：主按钮一行「购买预估返 ¥x」，详情不显示口径小字。
- 画板 Product-v3 设计说明中的「拼多多拿不到金额：购买可返利」示例，以及设计稿 README 0.2 底栏行拼多多列的「购买 可返利」，都不适用于商品详情：amount_unknown 是拼多多直链降级卡（开关 `pdd.direct_convert.enabled`，默认关），没有 product_key，进不了详情（04 §8.3、08 BR-PRICE-08、BR-TEXT-14 `rebate_amount_unknown`）；`btn.buy.rebate_unknown` 只用在这类卡自己的购买按钮上，详情页不实现这个状态（§1「拿不到金额」行）。
