# 订单找回 FindOrder（App 内 H5）

- 核对版本：规划提交 32a9765（负责人 2026-10-21 定稿 App 内高保真第 2 批，`docs/changes/20261021-App内高保真第2批定稿.md`）；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-money/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 2 批定稿」
- 路由：`FindOrder`（h5，`h5_path` /find-order，auth login，入口 in_app / push）；从哪来：订单页「未跟单？去找回」、订单详情原因码【去找回】、待跟单卡（第 1 批）；去哪：`Help`（「订单号在哪里找？」按平台的指引文章）
- 需求：01 F-ORD-09；规则只引编号：BR-ATTR-17（校验顺序、填写指引、⓪ 开关）、BR-ATTR-18、BR-ATTR-19（次数与风控）、BR-ATTR-30（审核结果）、BR-ATTR-16（已自动跟单）、BR-TEXT-14 表 A 30201～30206 与表 B、BR-TEXT-11、BR-TEXT-24；验收：AC-ORD-09（同号）、10 AC-S1-26-TB、AC-S1-43、AC-S1-74、AC-S1-106；任务：05 F1-04
- 可参考的已合并页面：`apps/h5/src/entries/app/pages/help/**`（H5 三态）、`apps/h5/src/components/platform/PlatformBadge.tsx`
- 是否资金或归属页面：是（提交归属申请；写操作经桥签名）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 填写表单 | FindOrder-v2.dc.html（e7e3559e3f05） | 默认页签「申请找回」 | getConfig（`claim.window_days`、`help_links.claim_guide.<platform>`） |
| 没找到可找回的订单 | FindOrderNotFound-v2.dc.html（1b64c39c8994） | 提交返回 30201（含分享单、不存在的单号） | createOrderClaim · 30201 |
| 其他提交结果一览（证据稿） | FindOrderErrors.dc.html（926a3ea2ec59） | ①～④ 30202 各 reason；⑤ 30204；⑥ 30205；⑦ 30203；⑧ 30203.RISK_BLOCKED；⑨ 30206 | createOrderClaim 对应码 |
| 找回记录 | FindOrderRecords-v2.dc.html（44cbb7bf2cb2） | 「找回记录」页签；提交成功后定位到新记录 | listOrderClaims · 200 · example |
| 找回记录为空 | FindOrderRecordsEmpty.dc.html（e62f4bacad8a） | items 为空 | 同上，列表置空 |
| 深色 | FindOrderDark.dc.html（782182a3b4bf）、FindOrderRecordsDark.dc.html（3dcf8b722120） | 系统深色（00 D35） | 同表单、记录 |
| 提交中、加载、出错 | 不适用（无画板） | — | 本地；`h5.load_failed` |

画板上的订单号、日期与驳回原因为样例。

## 2. 组件

| 区域 | 组件 | 数据（接口字段） | 交互 |
| --- | --- | --- | --- |
| 页签 | 「申请找回」「找回记录」 | — | 30205 与成功都切到记录并定位 |
| 下单平台 | 32 高胶囊 + 16px 官方平台图标（装饰，读屏读平台中文名） | platform | 切平台换填写提示 |
| 订单号、付款日期 | 输入框 + 日期选择 + 填写提示 | order_no、paid_date | 30202.FACTOR_MISMATCH 标在日期框下，其余按证据稿标在订单号框下 |
| 指引入口 | 文字链「订单号在哪里找？」 | `help_links.claim_guide.<platform>` | 未配置时不显示 |
| 提交 | 主按钮 | — | 30203、30203.RISK_BLOCKED、30206 当天置灰、不写具体次数 |
| 记录列表 | 列表行：`PlatformBadge`（14px）+ 状态标签 + 订单号 + 付款日期 + 说明句 | status、items[]（子订单决定与驳回原因）、created_at | 按子订单显示；不透露认领方 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 填写提示、期限、核对提示、指引入口 | `claim.guide.order_no`、`claim.guide.paid_date`、`claim.guide.window`、`claim.guide.caution`、`claim.guide.entry` |
| 提交结果 | `error.30201`～`error.30206`、`error.30202.<reason>`、`error.30203.RISK_BLOCKED` |
| 记录为空 | `claim.records.empty` |
| 记录：已找回说明 | CLAIM_RESULT 原文（BR-TEXT-09）；驳回原因 `claim_reject_reason.<CODE>.title`（用户侧文字未给，第 7 节） |
| 记录：状态标签与其余说明句、底注 | 08 无键（第 7 节） |
| 日期 | BR-TEXT-11 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| issueH5Token（桥 `auth.getH5Token`） | 进页 | 10405 |
| getConfig（桥 `app.getConfig`） | 进页取期限与指引链接 | — |
| createOrderClaim（桥 `net.signedRequest`，`signed_paths`） | 【提交】 | 20001、30201～30206、10405 |
| listOrderClaims | 进「找回记录」、提交成功后 | 无业务码 |

## 5. 权限点与开关

`claims.enabled`（关闭返回 30206，提交与订单页入口一并置灰，已提交的照常审核）。

## 6. 稿上没画、实现要做的

键盘弹起时提交按钮可见（适配证据稿 AdaptKeyboardFindOrder、AdaptNarrowFindOrder 仍为文字来源标签的旧写法，以本批为准）；错误提示与输入框关联；胶囊命中区 ≥ 44、播报选中；三平台指引正文上线前人工对照真机（05 F1-04）。

## 7. 待定与不一致

- 待上游（08 BR-TEXT-14 / BR-TEXT-25 补键）：找回记录的状态标签（审核中、已自动跟单、已找回、未通过）、说明句、底注「只显示你本人提交的找回申请」无键；`claim_reject_reason.<CODE>.title` 只有后台名称，画板 NO_EVIDENCE 用设计占位「没有找到这笔订单经凑狸下单的记录」。
- 待上游（契约线）：`claim.records.empty` 已在 08 表 C，`contracts/texts.default.json` 尚未收录。
