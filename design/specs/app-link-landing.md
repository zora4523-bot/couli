# App 内链接落地页 LinkLanding（App 原生）

- 核对版本：规划提交 b8b7dac（负责人 2026-10-21 定稿，`docs/changes/20261021-App内高保真第1批定稿.md`）；代码主干 67d7a4df（2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>.dc.html`（PNG 在 `review-shop/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 1 批定稿」
- 路由：`LinkLanding`（auth none；参数 `link_id`；入口 in_app、push、deeplink；M-公开）；从哪来：分享中间页【在 App 中打开】；去哪：购买链路（[app-product-buy.md](app-product-buy.md)，用户点购买才调 open）、首页
- 需求：01 F-SHARE-07；规则只引编号：BR-ATTR-05 细则、BR-ATTR-10、BR-ATTR-11；验收：AC-SHARE-07（同号规则）；任务：05 APP-13 / HM-10
- 可参考的已合并页面：无（派发前按代码主干核对）
- 是否资金或归属页面：是（购买沿用分享者的 link，不提供换成本人链接的入口）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 好友分享的商品 | LinkLanding-v2.dc.html（b0c5fe457563） | 打开者不是分享者 | getLink · 200（不显示返利金额） |
| 本人分享的商品 | LinkLandingOwner-v2.dc.html（15fcdcc7e7b8） | 打开者是分享者 | 同上；提示 `link_landing.owner_hint` |
| 链接已失效 | LinkLandingInvalid.dc.html（993e93c0626f） | link 取不到 | 30144 |

LinkLandingInvalid 为原稿直接沿用。本批没有深色稿，深色按令牌推导。画板上的商品与价格为样例数据。

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 商品卡 | `ProductCard`（大卡）、`PlatformBadge`（14px）、`PriceTag`、`DisclaimerFooter` | getLink 卡片 | 不显示返利金额；`BuyButton` 不拼「预估返」 |
| 购买 | `BuyButton` | link_id | 点了才调 openLink |
| 失效 | `EmptyState` | — | 回首页 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 本人提示 | `link_landing.owner_hint` |
| 失效 | `link_landing.invalid` |
| 口径 | `price_basis`、`price_basis.general` |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getLink | 进页 | 30144 |
| openLink | 点购买 | 见 app-product-buy |

## 7. 待定与不一致

- 无。
