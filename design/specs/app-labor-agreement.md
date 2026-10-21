# 劳务协议签署 LaborAgreement（App 原生）

- 核对版本：规划提交 32a9765（负责人 2026-10-21 定稿 App 内高保真第 2 批，`docs/changes/20261021-App内高保真第2批定稿.md`）；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-money/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 2 批定稿」
- 路由：`LaborAgreement`（native，auth realname，入口只有 in_app，params 为空对象、传入参数丢弃并记 `route_params_dropped`，`agent_guide_account` fund）；从哪来：提现页 block_code 10004（consent_type=labor_agreement）；去哪：签署成功回提现页（保留金额、不自动提交）
- 需求：01 F-WDR-13；规则只引编号：BR-WDR-31（含细则「签署组件与签署凭证」：只能原生、H5 / 桥 / Agent 不得代签、每个版本各签一次）、BR-WDR-07 细则「前置步骤的回流」；验收：AC-WDR-13（同号）、10 AC-S2-55；任务：05 APP-09 / HM-08
- 可参考的已合并页面：无（原生仓库不在本次核对范围）
- 是否资金或归属页面：是（提现前置；签署凭证）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 首次签署（未勾选） | LaborAgreement-v2.dc.html（50ac2210482c） | need_sign=true、signed_version 为空 | getLaborAgreement · 200 · needSign |
| 协议改版需重签（v2） | LaborAgreementResign.dc.html（c9170c3e9c59） | need_sign=true 且已签过旧版本；勾选框重新为未选中 | getLaborAgreement（signed_version 低于重签门槛） |
| 已签署 | 不适用（无画板；need_sign=false 时提现页不会引导到本页） | — | getLaborAgreement · 200 · signed |
| 签署失败（网络、超时） | 不适用（无画板） | 界面回到未签署、保留勾选，不显示「已签署」 | 本地 |
| 版本已变 | 不适用 | 签署返回 10004 | 重新拉取全文 |
| 深色 | LaborAgreementDark.dc.html（8b8f12b44a56） | 系统深色（00 D35） | 同首次签署 |

协议正文待法务；画板版本号与正文为占位。

## 2. 组件

| 区域 | 组件 | 数据（接口字段） | 交互 |
| --- | --- | --- | --- |
| 改版提示 | 警告提示条（只在重签时） | signed_version、version | — |
| 协议全文 | 可滚动正文（原生渲染全文地址） | text_url、text_sha256、version | 全文可打开 |
| 勾选 | `AgreementCheckRow`（圆形 18、默认不勾选、命中区 44，03 §10.2） | — | 不沿用旧版本的勾选 |
| 签署 | 主按钮 | version、text_sha256、agreed=true | 成功后再取一次 getLaborAgreement，以服务端记录为准 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 引导与版本不一致 | `error.10004` |
| 校验不过 | `error.20001` |
| 改版提示句 | 08 无键（第 7 节） |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getLaborAgreement | 进页、签署成功后、收到 10004 后 | 30304、10403 |
| signLaborAgreement | 【签署】 | 30304、10403、10004、20001、10405 |

## 5. 权限点与开关

无本页开关；重签门槛由后台发布协议时标记（resign_from_version，F-ADM-14）。

## 6. 稿上没画、实现要做的

长文滚动与大字号；签署按钮防重复提交；读屏能读到版本号与勾选状态。

## 7. 待定与不一致

- 待上游（08 BR-TEXT-14 补键）：重签顶部提示「劳务协议已更新，需要重新阅读并签署后才能提现」为画板措辞，08 只有 `error.10004` 通用句。
- 待上游（法务）：协议正文未定稿。
