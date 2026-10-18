# 打款队列、打款记录与结果待确认 payout-batches（管理后台）

- 核对版本：规划提交 8c91f67（负责人 2026-10-18 后台第 2 批定稿「全部按推荐」，`docs/changes/20261018-后台第2批定稿.md`）；代码主干 2fdbf110（rebate-platform 远端 main，2026-10-18 核对，尚无后台财务契约；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（PNG 在 `review-admin/png/`），不入公开仓库；完整 sha256 登记在 [design/README.md](../README.md) 第 15 项「管理后台第 2 批」
- 路由：后台资源 `withdrawals` 的页签「打款队列」「结果待确认」（契约子编号 `payout-batches`、`withdrawals/{id}/attempts`，CT-24）；从哪来：提现审核页签、工作台「打款队列」状态卡、资金看板「待打款」卡；去哪：提现单详情、平台资金台账（[admin-fund-dashboard.md](admin-fund-dashboard.md)）、紧急开关页
- 需求：01 F-ADM-07、F-ADM-26（状态卡）；规则只引编号：BR-WDR-11（执行权限）、BR-WDR-12（批次执行三步）、BR-WDR-13（先记后发、打款前复核）、BR-WDR-14（只查不重提、查询节奏）、BR-WDR-15（未知结果人工处置 W10）、BR-WDR-17（开关、队列暂停、付款方异常）、BR-WDR-18（水位与限额）、BR-WDR-23（通道对账）、BR-WDR-24（告警）、BR-WDR-28（结果判定清单）、BR-WDR-32 / BR-WDR-33（银行卡、微信通道与按通道暂停）、BR-FUND-20（W 录入入台账）；验收：AC-ADM-07、10 AC-S2-24、AC-S2-25、AC-S2-102、AC-S2-103、AC-S2-109、AC-S2-50、AC-S1-157；任务：05 F1-08b
- 可参考的已合并页面：`apps/admin/src/pages/admins/**`；配置中心页的 Card 写法
- 是否资金或归属页面：是（执行打款、处置、核销）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 队列运行中 | AdmPayoutQueue.dc.html（831870049e6e） | `payout.enabled=on`、`payout.queue_paused=false` | adminGetPayoutOverview + adminListPayoutQueue · 200 · example |
| 队列已暂停（付款方余额不足） | AdmPayoutQueuePaused.dc.html（c75be89783f7） | `payout.queue_paused=true`（系统置位，BR-WDR-17） | 同上；批次成员带 `hold_reason` |
| 执行确认 | AdmPayoutExecuteConfirm.dc.html（a990b72f4886） | 勾选待执行单后点【执行所选】 | 本地预览 + adminCreatePayoutBatch 返回逐单结果 |
| 已执行 | AdmPayoutExecuteDone.dc.html（e110d8dea503） | 执行成功 | 成功 Alert + 刷新列表 |
| 结果待确认（W10 处置） | AdmPayoutUnknown.dc.html（df557e7d41f6） | 页签「结果待确认」；`needs_manual=true` 的 PAYING 单 | adminListUnknownPayouts；处置 adminResolveUnknownPayout |
| 打款记录（单笔尝试明细） | AdmPayoutAttempts.dc.html（0ee0eadd1f3f） | 行操作【打款记录】 | adminListPayoutAttempts |
| 录入企业支付宝余额 | AdmPayoutBalanceEntry.dc.html（402d13ce3293） | 点【录入企业支付宝余额】 | adminCreateCashEntry（同一写法用于微信运营账户余额） |
| 录入校验未通过 | AdmPayoutBalanceEntryInvalid.dc.html（7663d65ef357） | 必填为空、取数时间超时效或倒退 | 本地校验 + 20001 |
| 空 / 加载中 / 出错 | 不适用（无画板；按三态写法） | — | 本地 |
| 无权限 | 不适用 | 无 `payout.execute` 且无 `fund.view` | 页签隐藏；10403 |

画板上的 W、P、限额、比例、时效、响应码、状态值、批次号、单号均为样例或占位（支付宝实测前不作为事实，BR-WDR-22、BR-WDR-28）；姓名、账号只以脱敏样式出现。

## 2. 组件（03 §9.1 antd）

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 标题行 | Title + Badge + Button【录入企业支付宝余额】（`fund.cash_entry`）【暂停队列】/【解除暂停】（`switch.payout` 或 `switch.all`） | `payout.queue_paused` | 解除暂停弹 StepUpModal（动态码）；解除后执行仍过水位检查 |
| 状态卡 | Row × 4 Card + Statistic：企业支付宝可用余额 W（录入人、时间、时效）、垫资水位 P（告警线 / 拒绝线）、今日已发出 / 单日限额、队列状态 | BR-WDR-18 的 W、P、限额；`payout.enabled`、`payout.queue_paused` | 数值只读；阈值取配置，不在前端写死 |
| 通道卡 | Card × 3（企业支付宝 / 银行卡 / 微信零钱）：开通与暂停状态、触发单、【解除通道暂停】（动态码）、微信运营账户余额【录入运营账户余额】 | `payout.channel_enabled.<channel>`、`payout.channel_paused.<channel>` | 通道暂停与队列暂停分开解除（BR-WDR-33 ①） |
| 已暂停说明 | Alert：暂停时刻、触发批次与单、已发出 / 未发出的分段说明、用户侧不提示余额不足 | 系统置位记录 | 决定 ③：不加用户通知（BR-WDR-26 维持） |
| 队列 | Tabs（全部 / 打款中 / 待执行）+ 批量栏【执行所选】（`payout.execute`）+ Table：单号 / 用户、实付金额、状态、来源（人工审核 / 自动 / 执行受阻 / 退回 + 批次号）、商户转账单号 `out_biz_no`、最近一次尝试、下次查询、操作【打款记录】【详情】 | `payout_batches`、`withdrawals.{batch_id, executor_id, execute_seq}`、`payout_attempts` | 打款中的单不可勾选、不可重新执行（BR-WDR-14） |
| 执行确认对话框 | Modal：将执行清单 Table + 「执行前检查」清单（开关与队列、W 时效、可用额度、限额）+ 后果说明 + StepUpModal | 本地预览；服务端再查一次（BR-WDR-12 ①–③） | 任一不过整批不执行，原因在响应 |
| 已暂停批次表 | Table：序号、单号 / out_biz_no、实付、状态、停住原因 `hold_reason`、最近尝试、下次查询、操作；折叠相同原因的区段 | 批次成员明细 | 已发出转账的单（含付款方侧失败）不能重新执行，只能走 W9 / W10 / W11 的处置路径，行操作【查询通道结果】【手动成功】【驳回】按 BR-WDR-08、BR-WDR-15、BR-WDR-17 的条件显示；【重新执行】只对未发出转账的单（`hold_reason=queue_paused`，无 kind=transfer 尝试记录），且须解除暂停并重新通过 BR-WDR-12 ①–③ |
| 结果待确认 | Table（单号 / 用户、实付、out_biz_no、首次转账 T、转入时间、最近一次查询、凭证数、状态、操作）+ 处置 Drawer：单据摘要、【立即查询】、凭证列表、Upload 上传支付宝侧凭证、Radio 判定成功 / 失败（失败项列出条件是否满足）、TextArea 处置说明、StepUpModal | `needs_manual`、凭证 | 立即查询只存凭证不改状态；判失败后的冻结与后续核对按 BR-WDR-15 细则 |
| 打款记录抽屉 | Drawer：单据摘要（out_biz_no、实付、收款、来源、`execute_seq`、首次转账 T、转人工处置时点、用户侧显示）+ 尝试记录 Table（时间、类型、响应码 / 状态、结果、耗时）+ 「先记后发」说明 | `payout_attempts[]` | 转账与查询记录的条数与节奏按 BR-WDR-13、BR-WDR-14，前端只按记录渲染 |
| 余额录入对话框 | Modal：账户、当前 W、用途、InputNumber 可用余额、DatePicker 取数时间、TextArea 备注 + 校验说明 + StepUpModal | BR-WDR-18 W、BR-FUND-20 台账 | 取数时间晚于现在或早于上次不能保存；录入写台账历史 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 提现状态、审核方式 | BR-TEXT-25 `admin_dict.withdrawal_status.*`、`withdrawals.review_mode.*` |
| 批次类型 `payout_batches.kind`、成员结果、`hold_reason`、尝试类型与结果、通道子状态、处置判定 | BR-TEXT-25 无行；契约线随 CT-24 补行，补齐前显示编码（支付宝状态值待 09 实测） |
| 用户侧显示（抽屉里的「用户侧显示」行） | BR-TEXT-06、BR-TEXT-07 |
| 金额、时间 | BR-TEXT-10、BR-TEXT-11 |
| 错误提示 | BR-TEXT-14（10403、20001、整批拒绝原因） |
| 其余（卡片说明、检查清单文案、先记后发说明） | 08 无键，用画板文案，登记 admin.payouts.* |

## 4. 接口（operationId 为暂拟，由 CT-24 分配）

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| adminGetPayoutOverview | 进入、执行 / 录入 / 解除后刷新 | 10001、10403 |
| adminListPayoutQueue / adminListUnknownPayouts | 切页签、筛选、切页 | 10403 |
| adminCreatePayoutBatch | 【执行所选】确认 | 整批拒绝（`payout.enabled`、`queue_paused`、水位、W 时效）与逐单未通过原因在响应（BR-WDR-12） |
| adminUpdateSwitch（`payout.queue_paused`、`payout.channel_paused.<channel>`） | 解除暂停 | 10403；step-up 失效 |
| adminQueryPayoutResult | 【立即查询】【查询通道结果】 | 通道错误按 BR-WDR-28 记录为凭证 |
| adminResolveUnknownPayout | 处置判定 | 凭证缺失、条件不满足（BR-WDR-15） |
| adminListPayoutAttempts | 【打款记录】 | 40401 |
| adminCreateCashEntry | 余额录入 | 20001（取数时间校验）、10403 |

## 5. 权限点与开关（04 §11.2 / §10.2）

`payout.execute`（执行、W10 处置、W11 核销、撤销微信转账，动态码；可为本单审核人，ADD-05）；`switch.payout` 或 `switch.all`（解除 `payout.queue_paused` / `payout.channel_paused.<channel>`，动态码）；`fund.cash_entry`（录入 W 与微信运营账户余额，动态码）；`fund.view`（只读）。开关：`payout.enabled`、`payout.queue_paused`、`payout.channel_enabled.<channel>`、`payout.channel_paused.<channel>`，本页显示状态，修改只有暂停 / 解除两项，其余在紧急开关页。

## 6. 稿上没画、实现要做的

状态卡阈值与时效文字从配置与接口取，不写死；暂停态下【执行所选】禁用并说明原因；执行中按钮禁用、完成后 message 并刷新；处置抽屉的条件清单用列表语义并逐项标「满足 / 未满足」；Upload 限制文件类型（JSON / CSV / 账单截图），成功后出现在凭证列表；折叠区段键盘可展开；1280 以下状态卡 2 列、通道卡纵排。

## 7. 待定与不一致

- 支付宝转账与查询的响应码、状态值、受理码（含微信 WAIT_USER_CONFIRM 等）在 09 CAP 实测前均为占位（BR-WDR-22、BR-WDR-28、BR-WDR-33 ⑦）；画板写「待实测 / 待验证」，实现用编码显示，不得写成事实。
- `payout_batches.kind`、`hold_reason`、尝试结果、通道子状态的后台中文名不在 BR-TEXT-25：契约线补行（随 CT-24 `payout-batches`），画板名为示意。
- 画板【解除暂停】标「短信」：以 04 §11.2 `switch.payout` / `switch.all` 动态码为准（2026-10-06 Jev 判断）。
- 已暂停批次表的「W9 退回」行操作与微信零钱卡的在途口径由 BR-WDR-08 / BR-WDR-33 与 B2-14 定；画板只作字段说明。
- 决定 ③（负责人 2026-10-18）：打款延迟不另加主动通知，用户侧仍只按 BR-WDR-26 超时一次通知；画板「用户侧不提示余额不足」与之一致。
