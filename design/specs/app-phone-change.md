# 更换手机号（App 原生，`Settings` 子页）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：无独立路由（设置「账号与安全 → 手机号」进入，已绑手机时；未绑走 [app-bind-phone.md](app-bind-phone.md)）；去哪：成功【完成】回 `Settings`；44001 联系客服申诉
- 需求：01 §4.2 `Settings` 行；F-ACC-07、F-ACC-11；规则只引编号：BR-ID-05、BR-ID-06、BR-ID-08 细则「绑定业务摘要」、BR-ID-10 细则「敏感操作的幂等键」、BR-ID-36 细则「被拦截请求申诉」、03 §4.2（不自动恢复的操作、未决键）；验收：AC-ACC-11（同号规则）、AC-S1-158、AC-S1-185；任务：APP-05、APP-12、HM-08
- 可参考的已合并页面：登录 v2 验证码组件、第 2 批提现待确认与二次验证（原生仓库派发前核对）
- 是否资金或归属页面：否（账号安全操作，需二次验证与幂等键）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 第 1 步：当前手机号 | PhoneChange-v2.dc.html（1d1bd865a3e3） | 进页 | getMe（脱敏号码）；【获取验证码】调 sendSmsCode（purpose=step_up，action=phone_change） |
| 第 1 步：验证码 / 验证码错误 | PhoneChangeCode.dc.html（6a3cbdf3dd34）、PhoneChangeCodeError.dc.html（bdd15e1d00e3） | 发码成功 / 20002 | 输满调 stepUp → step_up_token；20002 时格子清空标红 |
| 第 2 步：新手机号 | PhoneChangeNew-v2.dc.html（0c98cf150783） | step_up_token 取得 | 本地；空输入时按钮置灰；sendSmsCode（purpose=bind） |
| 第 2 步：验证码 | PhoneChangeNewCode.dc.html（1987f56addb8） | 发码成功 | 输满调 bindPhone（X-Step-Up-Token、Idempotency-Key） |
| 提交时二次验证 | PhoneChangeStepUp.dc.html（fc17181ebdcf） | bindPhone · 10003（token 过期） | `StepUpSheet` 后沿用原键重发（03 §4.2） |
| 暂不支持自助更换 | PhoneChangeDisabled.dc.html（5197b3edcb8c） | bindPhone · 30414 | 30414 |
| 新号被安全校验拦下 | PhoneChangeNewBlocked-v2.dc.html（e60305593c15） | 44001 | 【知道了】为主、【联系客服申诉】为次 |
| 更换成功 / 放弃时上一次已完成 | PhoneChangeDone.dc.html（3f47cfe39eab）、PhoneChangePendingCompleted.dc.html（691ff3220700） | bindPhone · 200 / 放弃时得知原请求已成功 | 重取 getMe；后者先轻提示 `pending_confirm.already_done` |
| 上一次提交结果未知 | PhoneChangePendingConfirm-v2.dc.html（c1e7e6c0956e） | 未决键存在（BR-ID-10 细则） | 本地未决键；【确认】用原键重发 bindPhone |
| 放弃请求在途 | PhoneChangePendingBusy-v2.dc.html（d44b0aefe596） | abandonIdempotencyKey 在途 | 两个动作都置灰 |
| 确认不了（保持待确认） | PhoneChangePendingStill-v2.dc.html（3e10aa31db84） | 重发仍无终结结果 | 保持待确认 |
| 放弃（二次确认）/ 已放弃 | PhoneChangePendingAbandonConfirm-v2.dc.html（50458ccf9814）、PhoneChangePendingAbandoned-v2.dc.html（ae968e41937f） | 点「放弃」/ abandonIdempotencyKey 得到已作废 | 本地确认框；已作废后回第 1 步并轻提示 |
| 待确认其他结果一览 | PhoneChangePendingStates.dc.html（49c4ff438056） | ① 放弃得到 40901；② 确认得到 20903 | abandonIdempotencyKey · 40901；bindPhone · 20903 |
| 深色 | PhoneChangeCodeDark.dc.html（a84b40775de9） | 系统深色 | 同第 1 步验证码 |

## 2. 组件

步骤条「验证当前手机号 → 验证新手机号」；`CodeInput`（6 格，格高与圆角同登录 v2 r6，输满自动提交）+ 倒计时 + 求助入口；`StepUpSheet`（标题下一行本次操作摘要）；待确认卡（`pending_confirm.*`）+ 下方表单置灰；44001 弹窗。

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 倒计时、求助入口 | BR-TEXT-14 表 C `login.code.countdown`、`login.code.help_entry` |
| 待确认卡 | 表 C `pending_confirm.title`、`.phone_change.desc` / `.action`、`.abandon`、`.abandon.confirm` / `.ok` / `.cancel`、`.abandon_busy`、`.abandoned`、`.already_done`、`.cannot_confirm`、`.retry_later` |
| 被拦 | 表 C `phone_change.risk_blocked.desc`、`cs.appeal_entry`；表 A `error.44001` |
| 错误 | 表 A `error.10003`、`.20002`、`.20003`、`.20903`、`.30411`、`.30414` |
| 步骤名、各说明句、二次验证摘要、成功页说明句 | 08 无键，用画板文案，待回写 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| sendSmsCode | 两步各发码 | 20001、44001、44003、42901、10405 |
| stepUp | 第 1 步输满 | 20001、20002、20003、10405 |
| bindPhone | 第 2 步输满、待确认【确认】 | 10003、20002、20003、20903、30411、30414、44001、10405 |
| abandonIdempotencyKey | 待确认「放弃」 | 20001、40901、10405 |

## 6. 稿上没画、实现要做的

原幂等键恢复、请求在途双按钮禁用、终结与非终结结果分流、换账号隔离（BR-ID-10 细则）；验证码错误与按钮禁用原因的读屏顺序；键盘与安全区遮挡。开关：`account.phone_change_enabled`（服务端，关闭时返回 30414，不下发客户端，见 §7）。样例号码只用脱敏写法（138****5678 当前、139****1234 成功、136****4411 被拦，`sample-data.md` §12）。

## 7. 待定与不一致

- `account.phone_change_enabled` 不下发客户端，30414 只能在第 2 步提交时得到；flow-map §11.2.1「点手机号行直接提示」做不到，待上游（04 / 契约线：发码或二次验证时返回，或下发开关）。
- 换手机号遇到 30411「…可退出后用手机号登录」不贴切，建议加子键；BR-ID-06 未写自助换号成功后其他设备是否退出登录，待上游（08）。
- 跨批：二次验证格子规格（第 2 批 `WithdrawStepUp-v2` 与本页不同）、44001 弹窗按钮主次（第 2 批相反）、待确认卡「提交时间」过去时间写法 BR-TEXT-11 未列，随各批定稿统一，待上游。
