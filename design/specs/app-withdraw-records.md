# 提现记录 WithdrawRecords（App 原生）

- 核对版本：规划提交 32a9765（负责人 2026-10-21 定稿 App 内高保真第 2 批，`docs/changes/20261021-App内高保真第2批定稿.md`）；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-money/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 2 批定稿」
- 路由：`WithdrawRecords`（native，auth login，可选参数 `withdrawal_id`：定位本人这张单并展开详情，不是本人的按不存在处理，入口 in_app / push，`agent_guide`）；从哪来：钱包「提现记录」、提交提现成功、提现类站内信与推送、Agent 引导卡与收益卡【看提现记录】；去哪：`PayoutAccount`（账号类失败【修改收款账号】）、微信（【去微信确认收款】）、企业微信客服
- 需求：01 F-WDR-05、F-WDR-09、F-WDR-15；规则只引编号：BR-WDR-08、BR-WDR-25（用户侧状态表与分支）、BR-TEXT-06、BR-TEXT-07、BR-TEXT-08、BR-WDR-26、BR-WDR-32、BR-WDR-33、BR-TEXT-12 细则「未知编码」；验收：AC-WDR-05 / 09 / 15（同号）、10 AC-S2-20、AC-S2-80、AC-S2-81；任务：05 APP-09 / HM-08（微信零钱随 B2-14）
- 可参考的已合并页面：无（原生仓库不在本次核对范围）
- 是否资金或归属页面：是（只读展示提现结果）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 列表 | WithdrawRecords-v2.dc.html（cf01250a9203） | 有记录；收起行的「未通过」「打款未成功」都带原因 | listWithdrawals · 200 · example |
| 审核中详情（提交成功后） | WithdrawRecordsPending-v2.dc.html（54c438899928） | PENDING_REVIEW、review_mode=manual、未到审核期限 | getWithdrawal · 200 · example |
| 审核超时 | WithdrawRecordsReviewOverdue-v2.dc.html（7f5a7afbd5fa） | 人工审核已过审核期限 | 同上 |
| 自动判定中、自动到账等待 | WithdrawRecordsAutoDeciding-v2.dc.html（bd02a3bebdfa）、WithdrawRecordsAutoWaiting-v2.dc.html（e6fdc88d7fa1） | review_mode 未定或 auto | 同上 |
| 支付宝处理中、到账延迟 | WithdrawRecordsPaying-v2.dc.html（358b5b21a0b5）、WithdrawRecordsDelayed-v2.dc.html（667784386893） | PAYING 未超过 BR-WDR-25 的时限；超过时限或转人工核实 | 同上 |
| 已到账详情 | WithdrawRecordsPaid-v2.dc.html（c0b9ef897858） | PAID_API / PAID_MANUAL；交易流水号可复制 | getWithdrawal（channel_order_id） |
| 打款未成功（账号类） | WithdrawRecordsFailed-v2.dc.html（54118c4372a1） | FAILED，fail_action 为修改收款账号 | 同上 |
| 微信零钱待确认、超时 | WithdrawRecordsWechatConfirm-v2.dc.html（5ce143522bb8）、WithdrawRecordsWechatTimeout-v2.dc.html（1370a40a1c78） | 微信零钱单等用户确认收款；过确认截止后撤销 | 同上（通道开启后） |
| 空 | WithdrawRecordsEmpty.dc.html（466c0c5432b7） | items 为空 | 同上，列表置空 |
| 状态一览、其他结果一览（证据稿） | WithdrawRecordsStates-v2.dc.html（772af712d717）、WithdrawRecordsMore.dc.html（d4c9e8f21e97） | ①～⑰ 各状态分支；代扣个税、线下转账、扣回驳回、人工驳回原因、未知状态 | 同上 |
| 深色 | WithdrawRecordsDark.dc.html（df8977f3cae2） | 系统深色（00 D35） | 同已到账详情 |
| 单号不是本人或不存在 | 不适用 | 带 withdrawal_id 打开 | getWithdrawal · 30701 → 只显示列表 |

画板上的金额、时间、流水号与收款账号（只用脱敏写法）均为样例。

## 2. 组件

| 区域 | 组件 | 数据（接口字段） | 交互 |
| --- | --- | --- | --- |
| 月份分组 + 记录行 | 列表行：金额、状态标签、时间 · 渠道 + 脱敏账号、副文案 | status、review_mode、amount_fen、payout_channel_name、masked_account、reason_code、fail_action、created_at | 点行展开详情；未知状态标题「处理中」、不显示任何写操作 |
| 详情 | 字段表：申请金额、手续费、代扣个税（为 0 不写）、实际 / 预计到账、收款账号、申请时间、到账时间、交易流水号 | fee_fen、tax_fen、net_fen、channel_order_id | 流水号【复制】 |
| 操作 | 按状态只出现画板上的按钮：联系客服（撤销走客服）、修改收款账号（只对账号类失败）、去微信确认收款 | fail_action | 「已到账」只对应 PAID_API / PAID_MANUAL（BR-WDR-08 细则） |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 状态标题与副文案 | `withdrawal_status.<CODE>.label` / `.hint`（BR-TEXT-06；副文案分支按 BR-WDR-25 表）；未知 `withdrawal_status.UNKNOWN` |
| 驳回、失败原因 | `withdraw_reject_reason.<CODE>`、`withdraw_fail_reason.<CODE>`（BR-TEXT-08） |
| 时效 | BR-TEXT-07（`withdraw.sla_text` / `.sla_text_auto`） |
| 到账金额、流水号 | `withdraw_detail.net.expected` / `.net.actual`、`withdraw_detail.trade_no` / `.copy` / `.copied` |
| 金额、时间 | BR-TEXT-10、BR-TEXT-11 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| listWithdrawals | 进页、下拉、翻页 | 无业务码 |
| getWithdrawal | 带 withdrawal_id 进页、展开详情、从微信返回立即查一次 | 30701 |

## 5. 权限点与开关

微信零钱相关状态随 `payout.channel_enabled.wechat` 与收款方式开放（BR-WDR-33）；银行卡通道关闭期间银行卡单按 PAID_MANUAL 显示（BR-WDR-32）。

## 6. 稿上没画、实现要做的

「加载更多」骨架（README 第 1 节不另出）；状态变化只播报一次；复制与按钮命中区 ≥ 44；大字号与窄屏。

## 7. 待定与不一致

- 待上游（契约线）：BR-WDR-25 副文案分支要用的 review_deadline、首次转账尝试后时长、needs_manual、channel_state、confirm_deadline、hold_days，以及详情里的到账时间（paid_at），在 Withdrawal 形状里都没有（只有 status、review_mode、reason_code、fail_action、created_at、channel_order_id）；由服务端下发副文案键还是这些字段未定。
- 待上游（08）：BR-TEXT-08 兜底句写「已退回余额」、BR-WDR-25 分支表写「已退回可提现余额」（本批按后者）；`withdraw_reject_reason.USER_REQUEST` 原句含「金额已退回余额」，与「{原因}；¥x 已退回可提现余额」拼接后重复；BR-TEXT-06 PAID_MANUAL 在银行卡线下转账时 payout_channel_name 取什么未列（画板写「银行卡」）；BR-WDR-32 未写通道未开通期间要不要提示「银行卡到账会慢一些」（画板不加）。
- 待上游（08 BR-ID-33）：微信零钱的脱敏显示格式未定。
