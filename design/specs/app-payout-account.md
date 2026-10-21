# 收款账号 PayoutAccount（App 原生）

- 核对版本：规划提交 32a9765（负责人 2026-10-21 定稿 App 内高保真第 2 批，`docs/changes/20261021-App内高保真第2批定稿.md`）；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-money/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 2 批定稿」
- 路由：`PayoutAccount`（native，auth realname，入口 in_app / push，params 为空对象、传入参数丢弃并记 `route_params_dropped`，`agent_guide_account` fund）；从哪来：提现页 block_code 30305 与收款账号行、提现记录账号类失败【修改收款账号】；去哪：保存成功回发起页（保留金额、不自动提交）
- 需求：01 F-WDR-02、F-WDR-12、F-WDR-15；规则只引编号：BR-WDR-02（含细则：规范化、核验次数、唯一）、BR-WDR-32、BR-WDR-33 ②、BR-ID-08 细则「绑定业务摘要」、BR-ID-10 细则「敏感操作的幂等键」、BR-ID-33 细则「收款账号的脱敏格式」、BR-WDR-07 细则「前置步骤的回流」；验收：AC-WDR-02 / 12 / 15（同号）、10 AC-S2-21、AC-S2-54、AC-S2-81；任务：05 APP-09 / HM-08（后端 B1-13；微信零钱随 B2-14）
- 可参考的已合并页面：无（原生仓库不在本次核对范围）
- 是否资金或归属页面：是（资金写操作：签名、幂等、二次验证）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 未绑定（支付宝） | PayoutAccount.dc.html（7fc83faf1ae6） | 没有当前收款账号 | getPayoutAccount · 200 · unbound |
| 绑定银行卡 | PayoutAccountBank-v2.dc.html（9506fc56ee0d） | 选银行卡；卡号只用脱敏样例；三要素核验随 CAP-X-08，说明句不提前承诺 | 本地表单 |
| 已绑定（支付宝、银行卡） | PayoutAccountBound.dc.html（41867ffd379d）、PayoutAccountBoundBank.dc.html（e7a6b2cac56a） | 有当前账号；显示脱敏账号与本月剩余变更次数 | getPayoutAccount · 200 · alipay（银行卡无命名示例） |
| 未通过安全校验 | PayoutAccountBlocked.dc.html（39392aaf7eea） | 保存返回 44001 | savePayoutAccount · 44001 |
| 保存失败一览（证据稿） | PayoutAccountErrors.dc.html（589ccce611a3） | ① 30303.payout_account_change_limit；② 30303.payout_account_verify_limit；③ 30307；④ 30308；⑤ 40901 | savePayoutAccount 对应码 |
| 上一次变更结果未知（待确认） | PayoutAccountPendingConfirm.dc.html（0344664380d1） | 保存结果未知，本机保留原幂等键 | 本地未决记录 |
| 确认请求在途、放弃二次确认 | PayoutAccountPendingBusy.dc.html（a0ffffe9b289）、PayoutAccountPendingAbandonConfirm.dc.html（8068ad5c7642） | 原键重发在途；点放弃 | 本地 |
| 放弃时仍在处理、已放弃、已完成 | PayoutAccountPendingStill.dc.html（8fef2ccfad07）、PayoutAccountPendingAbandoned.dc.html（780035f86c64）、PayoutAccountPendingCompleted.dc.html（14a515de9036） | abandon 返回 40901；outcome=abandoned；outcome=completed（显示新账号） | abandonIdempotencyKey · 40901 / 200 · abandoned / completed |
| 微信零钱：未绑定、授权中、授权未完成、已绑定 | PayoutAccountWechat-v2.dc.html（7632e45b64ca）、PayoutAccountWechatAuthorizing-v2.dc.html（f62b0c0aeb54）、PayoutAccountWechatAuthFailed-v2.dc.html（6e9cb55a018b）、PayoutAccountWechatBound.dc.html（59579a90afc6） | 收款方式含微信零钱（通道开启后）：先短信二次验证、再微信授权、回来保存 | createOauthAttempt（purpose=payout_bind）；保存形状见第 7 节 |
| 深色 | PayoutAccountBoundDark.dc.html（0ab4dcdb2671） | 系统深色（00 D35） | 同已绑定 |

画板上的账号、卡号、姓名只用脱敏或示例写法（「李四」为通用示例名）。

## 2. 组件

| 区域 | 组件 | 数据（接口字段） | 交互 |
| --- | --- | --- | --- |
| 收款方式 | 单选（只写文字，支付宝 / 微信官方图标未入库） | 可选方式见第 7 节 | 切换换表单 |
| 表单 | 支付宝登录号 + 收款人姓名；银行卡卡号 + 户名 | payout_method、logon id / card_no、payee_name | 姓名框下标 30307、账号框下标 30308（不透露对方） |
| 已绑定卡片 | 脱敏账号、开户行、本月还能变更次数 +【更换收款账号】 | masked_account、bank_name、masked_payee_name、change_remaining_this_month | 次数用完时置灰 |
| 保存 | 主按钮 + `StepUpSheet`（action=payout_account_change） | Idempotency-Key、X-Step-Up-Token | 改成另一个账号时摘要对不上返回 10003，重新验证；结果未知进待确认 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 保存失败 | `error.30303.payout_account_change_limit` / `.payout_account_verify_limit`、`error.30307`、`error.30308`、`error.40901`、`error.20001`、`error.20001.phone_invalid` |
| 被拦下 | `error.44001`、`cs.appeal_entry`；说明句无键（第 7 节） |
| 二次验证 | `error.10003`、`login.code.countdown` |
| 待确认一族 | `pending_confirm.title`、`pending_confirm.payout_account.*`、`pending_confirm.abandon*`、`.abandoned`、`.already_done`、`.retry_later`、`.cannot_confirm` |
| 脱敏写法 | BR-ID-33 细则（服务端脱敏） |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getPayoutAccount | 进页、保存成功后 | 30304 |
| sendSmsCode / stepUp | 保存前二次验证（微信零钱在拉起授权前） | 20001、44001、44003、42901 / 20001～20004、50305、10405 |
| createOauthAttempt | 微信零钱授权前（purpose=payout_bind） | 10001、20001、50001、10405 |
| savePayoutAccount | 【保存】、待确认时原键重发 | 30303、30304、30307、30308、10003、20903、10405、20001、44001、40901、50401、50301 |
| abandonIdempotencyKey | 待确认时放弃（action=payout_account_change） | 20001、40901、10405 |

## 5. 权限点与开关

`withdraw.payout_methods`（服务端配置，第 7 节）；银行卡通道 `payout.channel_enabled.bank_card` 关闭期间仍可绑卡，提现走人工 + 线下转账（BR-WDR-32）；微信零钱 `payout.channel_enabled.wechat`。

## 6. 稿上没画、实现要做的

卡号输入分组与键盘类型；登录号、卡号不写日志与埋点；错误提示与输入框关联；子页面结果回传（BR-ID-10 细则）。

## 7. 待定与不一致

- 待上游（契约线）：`withdraw.payout_methods` 不下发客户端（04 §10「服务端业务配置键」），getPayoutAccount 也不带可选方式，收款方式单选显示哪几种无数据来源；savePayoutAccount 只有支付宝、银行卡两种请求形状，微信零钱保存未定义（B2-14）；stepUp 无绑定业务摘要字段（BR-ID-08 细则「绑定业务摘要」试行），PayoutAccountErrors 说明的「换账号返回 10003」依赖它。
- 待上游（08 BR-TEXT-14 补键）：微信零钱步骤说明「先完成短信验证，再去微信授权，授权回来后保存为收款账号」；`payout_account.risk_blocked.desc`，并在 `cs.appeal_entry` 的用处里补收款账号。
- 待上游（08 BR-ID-33）：微信零钱的脱敏显示格式（WithdrawWechat「微信零钱 **三」与 PayoutAccountWechatBound「**三 的微信零钱」两种原稿写法）。
- 待上游（负责人提供素材）：支付宝、微信（微信零钱）官方图标未入 `design/icons/platform/`，入库前只写文字。
