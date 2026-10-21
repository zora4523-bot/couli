# 下单须知浮层 JumpTip（App 原生）

- 核对版本：规划提交 b8b7dac（负责人 2026-10-21 定稿，`docs/changes/20261021-App内高保真第1批定稿.md`）；代码主干 67d7a4df（2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>.dc.html`（PNG 在 `review-shop/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 1 批定稿」
- 路由：`JumpTip`（auth login；参数 `platform`；入口 in_app）；从哪来：购买链路首次外跳前（每用户每平台一次，BR-ATTR-21）；去哪：继续外跳（[app-product-buy.md](app-product-buy.md)）
- 需求：01 §4.2 `JumpTip` 行、F-LINK-06、F-LINK-07；验收：AC-LINK-06、AC-LINK-07（同号规则）；任务：05 APP-06 / HM-05
- 可参考的已合并页面：无（派发前按代码主干核对）
- 是否资金或归属页面：否（提示归属注意事项，不改归属）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 下单须知 | ProductJumpTip-v2.dc.html（df823e065236） | 该平台首次外跳前，服务端没有已读记录（BR-ATTR-21） | getTips（`jump_tip` 按平台）；看过后 markTipRead |
| 深色 | ProductJumpTipDark.dc.html（7c89fab4a8a2） | 系统深色（00 D35） | 同浅色 |

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 浮层 | `JumpTip` | platform | 主按钮继续外跳并记已读；按钮文案按画板与 §3 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 须知正文 | BR-TEXT-12 细则「JumpTip」段（正文至少一句；有效天数与丢单两句按 `jump_tip.<platform>.claims_enabled`） |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getTips | 外跳前判断是否展示 | — |
| markTipRead | 点主按钮（body 带 platform） | 20001、10405 |

外跳与 `link_jump` 上报在购买链路。设置页「重新显示下单须知」（resetTip）见 [app-settings.md](app-settings.md)。

## 5. 权限点与开关

`jump_tip.<platform>.claims_enabled`（默认 off；未验证平台不展示有效天数）。

## 6. 稿上没画、实现要做的

浮层打开时读屏焦点落在标题；大字号时正文可滚动、按钮固定在底部。

## 7. 待定与不一致

- 无。
