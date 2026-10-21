# 账号注销 DeleteAccount（App 原生）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`DeleteAccount`（auth login，入口 in_app / push，M-公开，`agent_guide_account: delete`）；从哪来：设置「账号与安全」（公开版）、账号状态页底部出口、强更页「注销账号 / 撤销注销」（受限会话，BR-ID-01 细则）、冷静期内被拦的写操作；去哪：`Withdraw`（去提现）、`Settings`（撤回成功）、联系客服、返回来源页
- 需求：01 §4.2 `DeleteAccount` 行、J9；F-ACC-07、F-ACC-10；规则只引编号：BR-ID-08、BR-ID-10 细则「敏感操作的幂等键」、BR-ID-27（细则）、BR-ID-28、BR-ID-29、BR-ID-31、BR-TEXT-01「待抵扣」、BR-TEXT-11、BR-TEXT-23 DELETION_PROGRESS、03 §10.2 `AgreementCheckRow`；验收：AC-ACC-10（同号规则）、AC-S1-99、AC-S2-46、AC-S2-58、AC-S2-60、AC-S1-158、AC-S1-185；任务：APP-13、HM-10
- 可参考的已合并页面：第 2 批提现待确认与二次验证（原生仓库派发前核对）
- 是否资金或归属页面：是（放弃余额与预估收益）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 说明与条件确认 | DeleteAccount-v2.dc.html（9b74b389e07d） | 未申请 | getDeletion · 200；getMe · balance（available_fen、estimated_total_fen）；勾选后【申请注销】 |
| 有待扣回金额 | DeleteAccountNegative-v2.dc.html（ab5422686c0e） | 进页时余额为负（BR-ID-27 细则） | getMe · balance；【申请注销】置灰；点申请时服务端仍返回 30416 |
| 申请时二次验证 | DeleteAccountStepUp.dc.html（8445746f2573） | 点【申请注销】（已绑手机） | sendSmsCode（purpose=step_up，action=account_deletion）→ stepUp → requestDeletion |
| 未绑手机号的二次验证 | DeleteAccountStepUpOauth.dc.html（b624fff7b3b8） | 账号未绑手机（BR-ID-08） | createOauthAttempt（purpose=step_up）→ 本端支持的第三方重新授权 → stepUp |
| 冷静期中 | DeleteAccountCooling-v2.dc.html（1151e001443d） | getDeletion · status 为冷静期 | apply_at、cooling_until、can_cancel；【撤回注销】调 cancelDeletion |
| 其他结果一览（设计证据） | DeleteAccountStates.dc.html（ccdf48577918） | ① 30412；② 从账号受限页进入（不显示去提现）；③ 冷静期已过撤回得到 10007；④ 20004 identity_mismatch；⑤ 20004；⑥ 本端不支持账号的登录方式 | requestDeletion · 30412；cancelDeletion · 10007；stepUp · 20004 |
| 上一次申请结果未知 | DeleteAccountPendingConfirm-v2.dc.html（d7f4be15ebc3） | 未决键存在 | 本地未决键；【确认】用原键重发 requestDeletion |
| 放弃（二次确认） | DeleteAccountPendingAbandonConfirm-v2.dc.html（d875086763c9） | 点「放弃」 | 本地确认框 |
| 确认请求在途 | DeleteAccountPendingBusy-v2.dc.html（8f9aaf7a52ed） | 请求在途 | 两个动作都置灰 |
| 确认没有结果 | DeleteAccountPendingStill-v2.dc.html（978a75afdafe） | 重发仍无终结结果 | 保持待确认 |
| 已放弃 | DeleteAccountPendingAbandoned-v2.dc.html（8c9782a89589） | abandonIdempotencyKey 得到已作废 | 恢复申请入口，勾选重置 |
| 放弃时已受理 | DeleteAccountPendingCompleted-v2.dc.html（bc9bfc74adf3） | 放弃时得知原申请已成功 | 进冷静期页 |
| 待确认其他结果一览 | DeleteAccountPendingStates.dc.html（817fda267b00） | ① 放弃得到 40901；② 确认得到 20903 | abandonIdempotencyKey · 40901；requestDeletion · 20903 |
| 深色（说明 / 冷静期） | DeleteAccountDark.dc.html（46c626b04b23）、DeleteAccountCoolingDark.dc.html（cf1601c78a36） | 系统深色 | 同上 |
| 被系统撤销 | MessagesDeletionNegative.dc.html（af24fdc4dd84，登记在 [app-messages.md](app-messages.md)） | 冷静期满时余额为负 | 站内信 |

## 2. 组件

资金区（可提现余额、预估收益 +「去提现」，命中区 44）；注销须知列表 +「查看完整《注销须知》」；`AgreementCheckRow`（圆形、默认不勾选、命中区 44）；`StepUpSheet`（标题下一行本次操作摘要）；冷静期时间线（时间写法 BR-TEXT-11）；待确认卡（`pending_confirm.*`）。

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 待确认卡 | BR-TEXT-14 表 C `pending_confirm.title`、`.deletion.desc` / `.action`、`.abandon*`、`.abandon_busy`、`.abandoned`、`.already_done`、`.cannot_confirm` |
| 错误 | 表 A `error.10003`、`.10007`、`.20004`、`.20903`、`.30412`、`.30416`；表 B `error.20004.identity_mismatch` |
| 金额术语 | BR-TEXT-01（「待抵扣」等） |
| 顶部提示、资金区说明、须知六条、负余额说明卡、冷静期各句、二次验证摘要、本端不支持的句子 | 08 无键（须知由法务定稿），用画板文案，待回写 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getDeletion / requestDeletion / cancelDeletion（契约均 planned） | 进页 / 二次验证后 / 【撤回注销】 | requestDeletion：10003、20903、30412、30416；cancelDeletion：10007 |
| sendSmsCode、stepUp、createOauthAttempt | 二次验证 | 20002、20003、20004、50305 |
| abandonIdempotencyKey | 待确认「放弃」 | 40901 |

## 6. 稿上没画、实现要做的

勾选与置灰原因的读屏播报；原幂等键恢复与换账号隔离；封禁用户从账号状态页进入时返回回账号状态页；冷静期内被拦写操作直接跳本页、不弹提示。开关：入口只在公开版（BR-ID-27 细则）；强更受限会话 `deletion_only` 可调 getMe、requestDeletion（契约 x-session-scopes）。画板上的金额、时间与须知条目为样例与版式稿（须知全文待法务定稿）。

## 7. 待定与不一致

- 须知第 6 条「有进行中的提现时不能申请」对封禁用户（提现被人工冻结，不返回 30412，BR-ID-31）不适用，正式文本由法务定稿时处理，待上游。
- 30416 与 cancelled_negative 模板「后续返利抵扣回正」与 BR-TEXT-01「待抵扣」释义不一致，待上游（08 内部同步）。
- BR-ID-08 正文「请先绑定手机号，或在支持该登录方式的设备上操作」无键，待上游（BR-TEXT-14）。
- 余额摘要是否含预估收益：README 待回写项；核对 2026-10-21 契约 `MeBalance` 已有 `estimated_total_fen`，由编排确认后可关。
