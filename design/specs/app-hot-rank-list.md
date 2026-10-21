# 热销榜 HotRankList（App 原生）

- 核对版本：规划提交 b8b7dac（负责人 2026-10-21 定稿，`docs/changes/20261021-App内高保真第1批定稿.md`）；代码主干 67d7a4df（2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>.dc.html`（PNG 在 `review-shop/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 1 批定稿」
- 路由：`HotRankList`（画板名 `RankList`，路由不沿用该名：`RankList` 是已删除的团队排行页；无需登录；入口 in_app、push、deeplink；M-公开）；从哪来：公开版首页金刚区；去哪：`ProductDetail`、购买链路
- 需求：01 F-PROD-13；验收：AC-PROD-13（同号规则）；任务：05 APP-16 / HM-12
- 可参考的已合并页面：无（派发前按代码主干核对）
- 是否资金或归属页面：否

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 淘宝 | RankList-v2.dc.html（0099337ee1fb） | 默认 | `GET /v1/rank/hot`（04 §6.3；契约未落，见 §7） |
| 切到京东 | RankListPlatform-v2.dc.html（d0e021320135） | 切平台 | 同上，`platform` |
| 加载中 | RankListLoading-v2.dc.html（bc1a1a82ada6） | 请求在途 | 本地：骨架 |
| 类目暂无数据 | RankListEmpty-v2.dc.html（8fc9097faf34） | items 为空 | 同上，items 置空 |
| 榜单暂不可用 | RankListError.dc.html（690aa3e84abb） | 取榜失败 | 50304（`50304.rank_unavailable`） |
| 深色 | RankListDark.dc.html（91793e840611） | 系统深色（00 D35） | 同浅色 |

画板上的商品、销量、价格、返利均为样例数据。

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 平台切换 | Tab + `PlatformBadge`（20px 官方图标） | `platform` | 切换重新请求 |
| 类目横滑 | 横滑标签 | `categories[]` | 切换带 `category` |
| 榜单 | `ProductCard`、名次、销量文字、`RebateTag`、`BuyButton`、`DisclaimerFooter` | `items[]`（`rank`、`sales_text`、`product_card`） | 卡片 → `ProductDetail`；购买见 app-product-buy |
| 榜单说明 | 文本 | `notice_key` | — |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 榜单说明 / 销量 | `rank.notice`、`rank.sales.tb`、`rank.sales.neutral` |
| 出错 | BR-TEXT-14 表 B `50304.rank_unavailable` |
| 口径 | `price_basis`、`price_basis.general` |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| `GET /v1/rank/hot`（契约未分配 operationId） | 进页、切平台、切类目、翻页、重试 | 50304 |

## 6. 稿上没画、实现要做的

用词守 BR-TEXT-13（不用「高佣」「收益榜」等榜单类词）；名次读屏读「第 N 名」。

## 7. 待定与不一致

- 待上游（契约）：`GET /v1/rank/hot` 与路由 `HotRankList` 尚未进 `openapi.yaml` / `routes.json`。
