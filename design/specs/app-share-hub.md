# 分享赚入口页 ShareHub（App 原生）

- 核对版本：规划提交 b8b7dac（负责人 2026-10-21 定稿，`docs/changes/20261021-App内高保真第1批定稿.md`）；代码主干 67d7a4df（2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>.dc.html`（PNG 在 `review-shop/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 1 批定稿」
- 路由：`ShareHub`（需要登录、已绑手机；入口 in_app、push；M-公开，内测期隐藏，TRADE-21）；从哪来：「我的」宫格【分享赚】；去哪：`ProductShare`（[app-product-share.md](app-product-share.md)）、收藏夹选商品（[app-favorites.md](app-favorites.md)）
- 需求：01 F-SHARE-11；验收：AC-SHARE-11（同号规则）；任务：05 APP-13 / HM-10
- 可参考的已合并页面：无（派发前按代码主干核对）
- 是否资金或归属页面：否（归因在 ProductShare 生成物料时）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 入口页 | ShareHub.dc.html（64d12ff4362a） | 进页 | 本地；规则说明 `share_hub.rule_note` |
| 生成中 | ShareHubConverting.dc.html（19a79a5419c4） | 粘贴后识别中 | parseInput 在途 |
| 识别不到商品 | ShareHubInvalid.dc.html（82e58d6dae3a） | 识别失败 | 30131、30132 |

三张为原稿直接沿用（页面里没有平台标识与口径句）。本批没有深色稿，深色按令牌推导（design/README 第 15 项）。

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 粘贴区 | 输入框 + 【粘贴】（iOS / 鸿蒙系统控件）+ 生成按钮 | 链接或口令 | 识别成功 → `ProductShare` |
| 说明 | 文本 | — | — |
| 收藏夹入口 | 列表入口 | — | 第 3 批 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 标题 / 规则说明 | `share_hub.title`、`share_hub.rule_note` |
| 识别失败 | BR-TEXT-14 表 A 30131、30132 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| parseInput | 粘贴后生成 | 30131、30132、10405 |

## 7. 待定与不一致

- 待上游（契约）：路由 `ShareHub` 尚未进 `routes.json`。
- 页面里「支持淘宝、京东、拼多多」是分享赚入口的说明，不是首页粘贴卡，v1.1 未改。
