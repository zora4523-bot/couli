# 申诉 Appeal（App 原生，账号申诉）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`Appeal`（auth login，入口 in_app / push）；本规格只管账号申诉（封禁 / 冻结）；订单申诉见 [app-appeal-order.md](app-appeal-order.md)；从哪来：`RiskNotice`、站内信、帮助文章「怎么申诉」；去哪：`RiskNotice`、`AuthManage`（解封后淘宝需重新授权时）、`Home`
- 需求：01 §4.2 `Appeal` 行；F-RISK-04；规则只引编号：BR-ID-31、BR-ID-36（细则「维持后再申诉」）、BR-ID-20（负责人 2026-10-18：只有淘宝要重新授权）、BR-TEXT-23（unbanned `{need_reauth}`、unfrozen）、BR-TEXT-11；验收：AC-S1-60、AC-S1-158、AC-S1-185；任务：APP-12、HM-08
- 可参考的已合并页面：第 2 批订单申诉（原生仓库派发前核对）
- 是否资金或归属页面：否

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 提交（封禁） | Appeal.dc.html（867e969a8ca2） | risk.state=banned、没有处理中的申诉 | 本地输入；submitAppeal（target_type=account） |
| 提交（冻结） | AppealFrozen.dc.html（c16f5816f4c9） | risk.state=frozen | 同上 |
| 处理中（封禁 / 冻结） | AppealProgress-v2.dc.html（4ad2437f61ab）、AppealProgressFrozen-v2.dc.html（9e94939c1429） | 有处理中的申诉 | listAppeals（status、created_at）；同一时间只能有一条，再提交返回原申诉 |
| 结果：已解除（封禁） | AppealResultLifted-v2.dc.html（251aa4ccf1d4） | 申诉撤销封禁 | listAppeals（closed_at）；淘宝绑定为 invalid 时才显示需重新完成淘宝授权一句（listUnionBindings） |
| 结果：提现已恢复（冻结） | AppealResultLiftedFrozen-v2.dc.html（9cb0634a9e66） | 申诉解除冻结 | listAppeals |
| 结果：维持（封禁 / 冻结） | AppealResultUpheld-v2.dc.html（e083d8b577ba）、AppealResultUpheldFrozen-v2.dc.html（367dba9c465f） | 申诉被维持 | listAppeals；可马上再申诉（不设前提），同一处罚次数用尽后不显示（见 [app-risk-notice.md](app-risk-notice.md) `RiskNoticeStates` ②） |
| 深色（提交 / 进度） | AppealDark.dc.html（62a4eda4ba26）、AppealProgressDark.dc.html（89b821ca3740） | 系统深色 | 同上；输入框占位用次文字令牌 |
| 提交失败 | 不适用（无画板） | 20001 / 50001 | 轻提示，保留输入 |

画板上的原因、时间与申诉内容为样例；时间写法 YYYY-MM-DD HH:mm（BR-TEXT-11，同第 2 批订单申诉）。

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 提交页 | 原因摘要 + 多行输入 + 【提交申诉】 | risk.reason_category | 空输入置灰；不显示处理时限（BR-TEXT-23 细则）；提示进度在「账号状态」页看 |
| 进度 / 结果 | 时间线（提交、处理中、结果）+ 结果卡 +「接下来可以」 | appeals[] | 结果卡的出口按处罚类型 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 结果与状态说明 | BR-TEXT-23 模板（unbanned、unfrozen、申诉结果） |
| 错误 | BR-TEXT-14 表 A `error.20001`、`error.30701`、`error.50001` |
| 申诉页各句、结果页「接下来可以」各条 | 08 无键，用画板文案，待回写 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| submitAppeal | 【提交申诉】（10006 白名单内） | 20001、30701、10405 |
| listAppeals | 进页、提交后（10006 白名单内） | — |
| getMe | 结果页刷新账号状态 | — |
| listUnionBindings | 封禁解除后判断是否提示淘宝重新授权 | — |

## 5. 权限点与开关

无。

## 6. 稿上没画、实现要做的

时间线读屏顺序；提交后焦点到进度页标题；键盘弹起时提交按钮贴键盘。

## 7. 待定与不一致

- 同一处罚的已申诉次数与第 4 次被拒的码与文案未定（BR-ID-36 已定上限，码由契约线分配），待上游。
- 申诉中原处罚类型的返回见 [app-risk-notice.md](app-risk-notice.md) §7，待上游。
