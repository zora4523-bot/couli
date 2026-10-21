# 余额流水 Ledger（App 内 H5）

- 核对版本：规划提交 32a9765（负责人 2026-10-21 定稿 App 内高保真第 2 批，`docs/changes/20261021-App内高保真第2批定稿.md`）；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-money/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 2 批定稿」
- 路由：`Ledger`（h5，`h5_path` /ledger，auth login，入口 in_app / push）；从哪来：钱包「余额流水」、订单详情扣回后的【查看流水】；去哪：行内跳转到 `OrderDetail`（订单类）或 `WithdrawRecords`（提现类），经桥 `nav.open`
- 需求：01 F-WDR-01（余额流水 H5）、F-INV-12（邀请奖励流水）；规则只引编号：BR-FUND-15、BR-TEXT-19（名称、符号、跳转、变动后余额、例 6）、BR-INV-24、BR-FUND-24（ADMIN_ADJUST 原因码）、BR-TEXT-10、BR-TEXT-11；验收：10 AC-S1-23、AC-S2-07、AC-S2-112；任务：05 F1-04（收益明细）、F1-15（REWARD 行）
- 可参考的已合并页面：`apps/h5/src/entries/app/pages/help/**`（H5 三态与 `components/base`）
- 是否资金或归属页面：是（只读展示）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 列表 | Ledger.dc.html（baa5d8ab954a） | 有流水 | listWalletLedger · 200 · example |
| 邀请奖励入账 | LedgerInviteReward.dc.html（ca59251e3f69） | 有 ledger_type REWARD、sub_type invite 的分录（活动开启后才产生） | 同上 |
| 其他流水类型一览（证据稿） | LedgerStates.dc.html（a0e19a192d84） | CLAWBACK、SETTLE_ADJUST、ADMIN_ADJUST（按原因码）、BAD_DEBT_WRITEOFF、WITHDRAW_PAID 明细与代扣个税 | 同上 |
| 空 | LedgerEmpty.dc.html（1a58eb1390d8） | items 为空 | 同上，列表置空 |
| 深色 | LedgerDark.dc.html（58b7b8c060be） | 系统深色（00 D35） | 同列表 |
| 加载、加载更多、出错 | 不适用（无画板；「加载更多」骨架同列表行，README 第 1 节「不另出」） | — | 本地；H5 加载失败 `h5.load_failed` |

画板上的金额、日期、订单尾号与邀请码均为样例。

## 2. 组件

| 区域 | 组件 | 数据（接口字段） | 交互 |
| --- | --- | --- | --- |
| 月份分组 + 流水行 | 列表行（H5 `components/base`） | ledger_type、sub_type、amount_fen、accounting_date、balance_after_fen、masked、link_type / link_id | link 非空才可点；masked=true（邀请分佣）与 REWARD 行不可点、日期只到日（BR-TEXT-19） |
| 变动后余额 | 行内副文字 | balance_after_fen（可为负，带负号）；WITHDRAW_PAID 汇总行为 null 不显示 | — |
| 提现到账汇总行 | 列表行 + 明细 | WITHDRAW_PAID：fee_fen、tax_fen | 点进对应提现单 |
| 金额颜色 | 令牌 | 返利类入账用返利强调色；REWARD、扣回、调账、核销、提现用墨棕（画板设计说明） | — |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 流水名称与说明 | `ledger_type.<CODE>.name` / `.hint`（BR-TEXT-19 表）；间推 `ledger_type.REFERRAL_CREDIT.name_indirect`；邀请奖励 `ledger_type.REWARD.name_invite` / `.hint_invite` |
| ADMIN_ADJUST 按原因码 | `name_<sub_type>` / `hint_<sub_type>`（BR-TEXT-19「ADMIN_ADJUST 原因码文案」；ACCOUNT_CLOSED 对用户不可见） |
| 变动后余额 | `ledger.balance_after` |
| 第二行「订单尾号 xxxx」「打款未成功」「提现未通过」、空态两句 | 08 无键（第 7 节） |
| 金额、日期 | BR-TEXT-10、BR-TEXT-11 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| issueH5Token（桥 `auth.getH5Token`） | 进页取令牌 | 10405 |
| listWalletLedger | 进页、下拉、翻页 | 无业务码（x-error-codes 为空） |

## 5. 权限点与开关

无本页开关；REWARD 行只在邀请奖励活动（`growth.invite_reward.enabled`，BR-INV-24）发放后出现，本页不读开关。

## 6. 稿上没画、实现要做的

加载更多骨架与到底提示；H5 加载失败重试页（F1-01）；行的读屏名称包含名称、金额正负与日期；不靠颜色区分正负；大字号与窄屏。

## 7. 待定与不一致

- 待上游（08 BR-TEXT-19 / BR-TEXT-14 补键）：BAD_DEBT_WRITEOFF 的说明（hint）08 只写「显示 hint」，画板用设计起草的「余额为负的部分已由平台核销」占位；流水第二行与空态两句为原稿写法，无字典键。
- 待上游（契约线）：画板第二行的「订单尾号 4444」、分享单脱敏号「订单 3790****88」与当天的「今天 09:05」，在 listWalletLedger 里没有对应字段（只有 accounting_date 与 link_id）。
