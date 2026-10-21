# 提现申请 Withdraw（App 原生）

- 核对版本：规划提交 32a9765（负责人 2026-10-21 定稿 App 内高保真第 2 批，`docs/changes/20261021-App内高保真第2批定稿.md`）；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-money/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 2 批定稿」
- 路由：`Withdraw`（native，auth realname，入口 in_app / push，params 为空对象、传入参数丢弃并记 `route_params_dropped`，`agent_guide_account` fund）；从哪来：钱包【提现】；去哪：按 block_code 去 `RealName` / `PayoutAccount` / `LaborAgreement` / 核实身份页（完成后回本页、保留金额、不自动提交），提交成功进 `WithdrawRecords`（带 withdrawal_id）并刷新钱包，页底「提现规则」进 `Help`
- 需求：01 F-WDR-03、F-WDR-04、F-WDR-09、F-WDR-15（微信零钱）；规则只引编号：BR-WDR-01、BR-WDR-03、BR-WDR-04 细则、BR-WDR-05 细则、BR-WDR-07 细则「前置步骤的回流」、BR-ID-08 细则「绑定业务摘要」、BR-ID-10 细则「敏感操作的幂等键」、BR-TEXT-07、BR-TEXT-14；验收：AC-WDR-03 / 04 / 09 / 15（同号）、10 AC-S2-20、AC-S2-26、AC-S2-27、AC-S2-53、AC-S2-62、AC-S2-80、AC-S2-81；任务：05 APP-09 / HM-08（微信零钱随 B2-14）
- 可参考的已合并页面：无（原生仓库不在本次核对范围；组件按 03 §10.2）
- 是否资金或归属页面：是（资金写操作：签名、幂等、二次验证）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 正常可提 | Withdraw.dc.html（a3ec02370d99） | can_withdraw=true | getWithdrawRules · 200 · example；getPayoutAccount · 200 · alipay |
| 改金额后计算中、估算未返回 | WithdrawCalculating.dc.html（e9a88c0e068b）、WithdrawEstimateFailed.dc.html（140ef89d5f64） | 金额变化后等新估算；估算失败或迟到被丢弃时隐藏估算行 | getWithdrawRules（amount_fen）；BR-WDR-04 细则「估算响应的归属」 |
| 预计到账说明 | WithdrawNoteNet.dc.html（11c0b7aa3202） | 点「预计到账」说明 | 本地 |
| 未实名引导 | WithdrawRealName.dc.html（9d9752406b6d） | block_code 30304 | getWithdrawRules |
| 时效说明与页内拦截一览（证据稿） | WithdrawPageStates.dc.html（c0ae73615beb） | 自动到账开关两态、微信零钱时效；30301～30309、10004、30303 各 reason | getWithdrawRules；createWithdrawal 对应码 |
| 二次验证 | WithdrawStepUp-v2.dc.html（a4c1a513c313） | 点【提交】，无有效 step_up_token | sendSmsCode（step_up）→ stepUp（action=withdraw） |
| 提交中 | WithdrawSubmitting.dc.html（9530119ea511） | createWithdrawal 在途 | 本地 |
| 被安全校验拦下 | WithdrawBlocked.dc.html（fbb6c6026350） | 44001 | createWithdrawal · 44001（见第 7 节） |
| 微信零钱 | WithdrawWechat.dc.html（1efb6202ac56） | 当前收款方式为微信零钱（通道开启后） | getPayoutAccount |
| 上一笔结果未知（待确认） | WithdrawPendingConfirm.dc.html（763bac6c8891） | 提交结果未知，本机保留原幂等键 | 本地未决记录 |
| 放弃二次确认、放弃请求在途 | WithdrawAbandonConfirm.dc.html（bde016ab1cd2）、WithdrawPendingBusy.dc.html（66b7777490f2） | 点放弃；abandon 请求在途 | 本地 |
| 放弃后仍未决 | WithdrawPendingStill.dc.html（dd30ef7943f0） | abandon 返回 40901 | abandonIdempotencyKey · 40901 |
| 已放弃、放弃时上一笔已受理 | WithdrawAbandoned.dc.html（920130f93ef9）、WithdrawAbandonCompleted-v2.dc.html（0de2354c778f） | outcome=abandoned；outcome=completed（进该单详情） | abandonIdempotencyKey · 200 · abandoned / completed |
| 深色 | WithdrawDark.dc.html（63b4a1de0690）、WithdrawStepUpDark.dc.html（adc11c54ead6） | 系统深色（00 D35） | 同正常、二次验证 |

画板上的金额、次数、收款账号（只用脱敏写法）均为样例。

## 2. 组件

| 区域 | 组件 | 数据（接口字段） | 交互 |
| --- | --- | --- | --- |
| 页头 | 余额行 + 剩余次数 | withdrawable_fen、daily_remaining、monthly_remaining | — |
| 金额输入 | 金额框 +【全部提现】+ 快捷档位 | max_withdrawable_fen、quick_amounts_fen | 【全部提现】填服务端上限；档位只显示下发值 |
| 估算行 | 单行（「计算中…」/ 隐藏） | est_fee_fen、est_tax_fen、est_net_fen | 只显示与账号、页面实例、请求序号、金额都对得上的最新一次 |
| 收款账号行、时效句 | 只写文字（支付宝 / 微信官方图标未入库） | payout_method、masked_account；时效句按自动到账总开关二选一（BR-TEXT-07） | 点行进 `PayoutAccount` |
| 提交 | 主按钮 + `StepUpSheet` | Idempotency-Key、X-Step-Up-Token | 结果未知时不换键，进待确认（BR-ID-10 细则） |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 页头、上限、全部提现、估算、计算中、规则入口 | `withdraw.balance_line`、`withdraw.remaining_counts`、`withdraw.max_line`、`withdraw.all`、`withdraw.estimate` / `.estimate.net_only`、`withdraw.estimate.calculating`、`withdraw.rules_link`（`help_links.withdraw_rules`） |
| 时效句 | `config.texts` 的 `withdraw.sla_text` / `withdraw.sla_text_auto`（BR-TEXT-07） |
| 拦截与金额提示 | `error.30301`～`error.30309`、`error.30303.<reason>`、`error.10004`、`error.10005` |
| 二次验证 | 标题 `error.10003`；倒计时 `login.code.countdown`；`error.20002` / `20003` |
| 被拦下 | `error.44001`（`risk_msg.<code>`）、`withdraw.risk_blocked.desc`、`cs.appeal_entry` |
| 待确认一族 | `pending_confirm.title`、`pending_confirm.withdraw.*`、`pending_confirm.abandon.*`、`.abandoned`、`.abandon_busy`、`.already_done`、`.retry_later`、`.cannot_confirm`、`error.20903` |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getWithdrawRules | 每次进页、从前置页回来、金额变化 | 无业务码；block_code 按 BR-WDR-03 |
| getPayoutAccount | 进页 | 30304 |
| sendSmsCode / stepUp | 二次验证 | 20001、44001、44003、42901 / 20001～20004、50305、10405 |
| createWithdrawal | 【提交】、待确认时【确认】（原键重发） | 10003、10004、10005、20903、30301～30307、30309、10405 |
| abandonIdempotencyKey | 待确认时放弃（action=withdraw） | 20001、40901、10405 |

## 5. 权限点与开关

`withdraw.enabled`（30306）；`withdraw.auto_payout.enabled` 决定时效句二选一；微信零钱随 `payout.channel_enabled.wechat` 与收款方式开放（BR-WDR-33）。

## 6. 稿上没画、实现要做的

「手续费 / 税费」问号（01 Wallet 行，`wallet.help.fee_tax`）本批稿上未画；键盘弹起、窄屏、大字号与焦点（AdaptKeyboardWithdraw、AdaptNarrowWithdraw、AdaptLargeTextWithdraw、A11yFocusWithdraw 为既有证据稿；A11yFocusStepUp、AdaptShortStepUp 的二次验证标题是旧文案，以本批为准）。

## 7. 待定与不一致

- 待上游（契约线）：createWithdrawal 的 x-error-codes 没有 44001（BR-WDR-03 ③a，WithdrawBlocked 画的就是它）；getWithdrawRules 没有最低额、步长、单笔上限、按收款方式上限等限制值（BR-WDR-03 末句），页内提示的变量从哪取未定；stepUp 请求没有绑定业务摘要字段（BR-ID-08 细则「绑定业务摘要」试行），二次验证标题下的「提现 ¥10 · 收款账号…」依赖它；旧号加验码（BR-WDR-03 ③b）未分配（见 `app-withdraw-reverify.md`）。
- 待上游（08 BR-TEXT-14 补键）：「预计到账」说明正文、微信零钱单笔上限句、引导按钮【去绑定收款账号】【去签署劳务协议】【查看提现规则】为画板措辞；表 B 缺 `30303.payee_daily_count`。
- 待上游（契约线）：`withdraw.risk_blocked.desc`、`cs.appeal_entry`、`login.code.countdown` 已在 08，`contracts/texts.default.json` 尚未收录。
