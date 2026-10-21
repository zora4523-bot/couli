# 平台授权说明半屏 AuthSheet（App 原生）

- 核对版本：规划提交 b8b7dac（负责人 2026-10-21 定稿，`docs/changes/20261021-App内高保真第1批定稿.md`）；代码主干 67d7a4df（2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>.dc.html`（PNG 在 `review-shop/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 1 批定稿」
- 路由：`AuthSheet`（auth login；参数 `platform`；入口 in_app）；从哪来：点购买时 openLink 返回 30101 / 30102 / 30111；去哪：平台授权（按 `auth_methods` 或 `auth_jump`），回来后进「正在确认授权结果」，关闭后进「关闭授权说明后的提示」（两者见 [app-product-buy.md](app-product-buy.md)）
- 需求：01 F-LINK-03、F-LINK-04；规则只引编号：BR-ID-17（授权方式）、BR-ID-18、BR-ID-22；验收：AC-LINK-03、AC-LINK-04（同号规则）；任务：05 APP-06 / HM-05
- 可参考的已合并页面：无（派发前按代码主干核对）
- 是否资金或归属页面：是（授权决定订单能否归属本人）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 淘宝授权说明半屏 | ProductAuthSheet-v2.dc.html（ac41612bb7ea） | openLink 返回 30101 / 30102（不带 auth_unavailable） | `data.auth_url`、`data.state`、`data.auth_methods`；说明文案取 `config.auth_tips[platform]` |
| 拼多多授权 | 不另出画板（同一版式换拼多多图标与文案，C1-14 S2） | 30111 | `data.auth_jump` |
| 深色 | ProductAuthSheetDark.dc.html（410ac1a82aea） | 系统深色（00 D35） | 同浅色 |

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 半屏 | `AuthSheet`（标题前 32px 平台官方图标，授权是平台标识的用途之一） | auth_tips、auth_methods | 主按钮按 `auth_methods` 顺序执行（两种方式都实现，BR-ID-17 细则）；关闭 → 「关闭授权说明后的提示」 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 说明正文 | `config.auth_tips[platform]`（后台下发） |
| 错误 | BR-TEXT-14 表 A 30101、30102、30111 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getUnionAuthUrl | 需要重新取授权链接时 | 30101、30102、30153、50301 |
| bindUnion | 授权回调后 | 20001、30101、30102、30104、30151、30153、10405 |

## 6. 稿上没画、实现要做的

半屏打开时读屏焦点落在标题；大字号与矮屏按适配稿 `AdaptShortAuthSheet`（证据稿，不在本批）。

## 7. 待定与不一致

- 无。
