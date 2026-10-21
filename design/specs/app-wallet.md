# 钱包 Wallet（App 原生）

- 核对版本：规划提交 32a9765（负责人 2026-10-21 定稿 App 内高保真第 2 批，`docs/changes/20261021-App内高保真第2批定稿.md`）；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-money/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 2 批定稿」
- 路由：`Wallet`（native，auth login，入口 in_app / push，`agent_guide`）；从哪来：「我的」余额卡与宫格、Agent 引导卡与收益卡【去钱包】、推送；去哪：`Withdraw`、`WithdrawRecords`、`OrderList`、`Ledger`、`Earnings`（公开版）、`RiskNotice`（冻结提示条，第 3 批）
- 需求：01 F-WDR-01、F-WDR-14（入口）；规则只引编号：BR-FUND-18、BR-TEXT-01、BR-TEXT-04、BR-TEXT-10（金额隐藏）、BR-WDR-05 细则「冻结时的【提现】按钮」、BR-WDR-17、BR-TEXT-23；验收：AC-WDR-01（同号）、10 AC-S2-33、AC-S2-27、AC-S2-30；任务：05 APP-09 / HM-08
- 可参考的已合并页面：无（原生仓库不在本次核对范围；组件按 03 §10.2）
- 是否资金或归属页面：是（只读展示，不写资金）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 正常 | Wallet.dc.html（39420611de0a） | 进入页面 | getWalletSummary · 200 · example |
| 有冻结中 | WalletFrozen.dc.html（d683bb4b078e） | frozen_fen > 0 | 同上 |
| 待抵扣，【提现】置灰 | WalletNegative-v2.dc.html（ae0f3613fd5b） | negative_fen > 0 | 同上；置灰说明 `error.30302` |
| 风控冻结，【提现】可点 | WalletRiskFrozen-v2.dc.html（92f868009ea9） | risk_paused_reason 非空 | getWalletSummary；frozen_until 取 getMe（04 §6.1） |
| 风控冻结时点【提现】 | WalletRiskFrozenTap.dc.html（7d3b9c66dda3） | 点【提现】，getWithdrawRules 返回 block_code 30303、block_reason account_frozen | getWithdrawRules · 200；留在本页出轻提示 |
| 其他状态一览（证据稿） | WalletStates.dc.html（ca3762283157） | ① withdraw_enabled=false；② 冻结无期限；③～⑤ next_credit_period 为空、credit_overdue=true、pending_credit_paused_fen > 0 | getWalletSummary；① 文案 `error.30306` |
| 金额隐藏 | WalletHidden.dc.html（ae2774deea9b） | 本机偏好开启（与「我的」、订单页共用） | 本地 |
| 收益看板入口（公开版） | WalletEarningsEntry.dc.html（1e89481e8ebe） | `features.earnings.dashboard.visible` 为真 | getConfig |
| 断网显示上次数据 | WalletStale.dc.html（57a01df4654b） | 请求失败且本机有上次数据 | 本地缓存 |
| 三个问号说明 | WalletNoteEstimate.dc.html（306ddd4a1455）、WalletNoteFrozen.dc.html（d3cb96cbbb60）、WalletNotePaused.dc.html（dbda4217e9ad） | 点「预估收益」「冻结中」「暂缓入账」旁问号 | 本地 |
| 深色 | WalletDark.dc.html（f56890ac6f5c） | 系统深色（00 D35） | 同正常 |
| 加载、无缓存时出错 | 不适用（无画板；按 Skeleton / ErrorState） | — | 本地 |

画板上的金额、月份、冻结原因与到期时间均为样例（`couli-runs/design-hifi/sample-data.md` §12）。

## 2. 组件

| 区域 | 组件 | 数据（接口字段） | 交互 |
| --- | --- | --- | --- |
| 主卡 | `WalletHeroCard` | withdrawable_fen；withdraw_enabled、negative_fen 决定【提现】置灰 | 置灰不可点；可点时先调 getWithdrawRules：account_frozen 留本页出 Toast，其余进 `Withdraw`（该页按 block_code 引导，BR-WDR-07 细则）；「提现记录」进 `WithdrawRecords` |
| 风控提示条 | 顶部提示条 | risk_paused_reason、frozen_until | risk_state=frozen 时可点进 `RiskNotice`；提现冻结记录引起的不可点（第 7 节） |
| 预估区 | `AmountGrid`（两列 + 问号） | estimated_total_fen、pending_credit_fen、pending_credit_paused_fen、next_credit_period、credit_overdue | 问号开说明 `Sheet`；客户端不自行相加（BR-TEXT-01） |
| 冻结中、已提现、待抵扣 | `AmountGrid` | frozen_fen、withdrawn_fen、negative_fen | — |
| 入口行 | 列表行 | — | 订单、余额流水、收益看板（开关） |
| 金额隐藏 | 小眼睛按钮 | 本机偏好 | 隐藏时金额显示「****」，月份照常 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 金额名称（可提现余额、预估收益、其中已收货、暂缓入账、最早预计、冻结中、已提现、待抵扣） | BR-TEXT-01 术语；键未建，建键时用 `wallet.` 前缀（BR-TEXT-12 细则） |
| 问号说明 | `wallet.help.estimated`、`wallet.help.frozen`、`wallet.help.pending_paused` |
| 置灰说明、轻提示 | `error.30302`、`error.30306`、`error.30303.account_frozen` |
| 风控提示条 | BR-TEXT-01 钱包汇总口径的暂停提示（模板以该条为准）+ `risk_reason.<category>`、到期时间附句（BR-TEXT-23 细则）；第二行无键（第 7 节） |
| 金额隐藏、断网 | `amount_mask.hide` / `amount_mask.show`、`net.stale_data` |
| 金额、月份、时间 | BR-TEXT-10、BR-TEXT-04、BR-TEXT-11 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getWalletSummary | 进页、回到前台、下拉刷新、从提现相关页返回 | 无业务码（x-error-codes 为空）；公共码按 `contracts/error-codes.yaml` |
| getWithdrawRules | 点【提现】 | 无业务码；block_code 按 BR-WDR-03 |
| getMe | 有风控暂停时取 frozen_until | — |

## 5. 权限点与开关

`withdraw.enabled`（经 withdraw_enabled 下发）；收益看板入口 `features.earnings.dashboard.visible`（由 `earnings.dashboard.enabled` 派生，04 §10.1）；`credit.enabled.<platform>` 关闭时已收货订单按「入账核对中」、不显示月份（WalletStates ③）。

## 6. 稿上没画、实现要做的

加载骨架与无缓存出错态；金额隐藏同时覆盖读屏名称；问号、小眼睛命中区 ≥ 44；大字号与窄屏（适配证据稿 AdaptLargeTextWallet 未在本批重出）；深色只经令牌切换。

## 7. 待定与不一致

- 待上游（08 BR-TEXT-14 补键）：风控提示条第二行「浏览、购物照常。点这里查看说明或申诉」、WalletStates ④ 月份处「结算进度」标签为画板措辞，无字典键。
- 待上游（08 BR-TEXT-23 / 契约线）：提现冻结记录（withdraw_holds）引起的暂停用什么原因文案未写；risk_paused_reason 只是原因键，客户端据什么区分「可点进 RiskNotice」与「不可点」未定义。
- 待上游（契约线）：`wallet.help.*` 已在 08 表 C，`contracts/texts.default.json` 尚未收录。
