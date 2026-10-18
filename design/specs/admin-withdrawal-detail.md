# 提现单详情与审核 withdrawals/{id}（管理后台）

- 核对版本：规划提交 8c91f67（负责人 2026-10-18 后台第 2 批定稿「全部按推荐」，`docs/changes/20261018-后台第2批定稿.md`）；代码主干 2fdbf110（rebate-platform 远端 main，2026-10-18 核对，尚无后台财务契约；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（PNG 在 `review-admin/png/`），不入公开仓库；完整 sha256 登记在 [design/README.md](../README.md) 第 15 项「管理后台第 2 批」
- 路由：后台资源 `withdrawals/{id}`；从哪来：审核列表【审核】【详情】、打款队列、用户详情提现页签、一框搜、工作台卡；去哪：用户详情、打款记录（[admin-payouts.md](admin-payouts.md)）、自动到账设置
- 需求：01 F-ADM-07；规则只引编号：BR-WDR-05（阻断）、BR-WDR-08（状态机）、BR-WDR-10（审核与驳回）、BR-WDR-16（手动成功）、BR-WDR-26（审核时限展示）、BR-WDR-29（风险标签）、BR-WDR-30（判定结果 `auto_decision`）、BR-WDR-33（微信零钱「等用户确认」）、BR-TEXT-08（驳回原因用户可见文案）；验收：AC-ADM-07、10 AC-S2-20、AC-S2-23、AC-S2-28、AC-S2-53、AC-S2-81、AC-S1-157；任务：05 F1-08a（详情、审核 / 驳回）、F1-08c（手动成功补录）
- 可参考的已合并页面：`apps/admin/src/pages/admins/**`（Descriptions + 对话框）
- 是否资金或归属页面：是

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 待审核（转人工） | AdmWithdrawDetail.dc.html（4e55d52a231d） | `status=PENDING_REVIEW`、`review_mode=manual` | adminGetWithdrawal · 200 · example |
| 驳回对话框 | AdmWithdrawReject.dc.html（ef320b8d193e） | 点【驳回】 | adminRejectWithdrawal |
| 自动到账判定（两张对照） | AdmWithdrawAutoDecision.dc.html（6053736c459a） | 详情「自动到账判定」区展开，或从列表「转人工原因」进入 | `auto_decision`（BR-WDR-30 细则「可追溯」） |
| 已通过待执行 · 银行卡通道未开通 → 手动成功 | AdmWithdrawManualEntry.dc.html（5e6a9684fec9） | `status=APPROVED`，收款方式对应通道关闭，点【手动成功】 | adminManualPaidWithdrawal |
| 微信零钱 · 等用户确认收款 | AdmWithdrawDetailWechat.dc.html（7b7f39d6bb4f） | `status=PAYING`，通道子状态为等用户确认（BR-WDR-33 ⑥） | 同 adminGetWithdrawal；【撤销微信转账】adminCancelWechatTransfer |
| 其他状态（打款中 / 成功 / 驳回 / 失败）、提交中、结果 | 不适用（无画板；同一布局，按钮按状态隐藏） | — | — |
| 加载中 / 出错 / 不存在 | 不适用（Descriptions 骨架；Result + 【重试】；40401） | — | 本地 |
| 无权限 | 不适用 | 无 `withdraw.review` 且无 `fund.view` | 10403 |

画板上的单号、UID、金额、判定实际值、转账记录、确认截止时间均为样例；手机号、收款账号、卡号、姓名只以脱敏样式出现，微信收款标识不显示。

## 2. 组件（03 §9.1 antd）

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 标题行 | Title（单号）+ Tag（展示状态，附加态第二行）+ Button 组：【驳回】【审核通过】（`withdraw.review`）、【执行打款】（`payout.execute`）、【手动成功】（`payout.manual_entry`）、【撤销微信转账】（`payout.execute`） | `status`、`review_mode`、`payout_method`、`channel` | 按状态与权限点显示；每个写操作弹 StepUpModal（动态码） |
| 基本信息 | Descriptions：单号、外部业务单号、展示状态、申请时间、审核时限（只对 `review_mode=manual` 显示，BR-WDR-26）、审核方式、审核人与时间、批次 | — | — |
| 金额明细 | Descriptions：申请金额、手续费、代扣个税、实付金额 | `amount_fen`、`fee_fen`、`tax_fen`、`net_fen` | BR-TEXT-10 |
| 自动到账判定 | Card：结论 Tag、规则版本与判定时刻、未满足条件 Tag 列表、⑧ 三项实际值；展开为 ①–⑬ 逐条 Table（条件 / 配置、实际值、结果）+【查看自动到账设置】 | `auto_decision.{result, failed_conditions[], warn_values, rule_version, decided_at}` | 只读；总开关关闭时只显示 disabled 一条 |
| 风险标签 | Tag 列表 + 快照时刻说明 + Button【重新计算】 | `risk_flags[]`（BR-WDR-29） | 重新计算只写新快照，不改状态 |
| 用户 | Descriptions：UID（链接用户详情）、手机号（脱敏 + 【查看】`pii.reveal_phone`）、实名姓名（脱敏）、风控状态、提现冻结、可提现余额、冻结中 | 用户摘要 | 【查看】每次记审计 |
| 收款账号（申请时快照） | Descriptions：收款方式、账号（脱敏 + 【查看】`pii.reveal_identity`）、收款人、打款通道 | 快照字段 | — |
| 转账记录 / 处理记录 | Table（时间、类型、结果）/ Timeline | `payout_attempts[]`、审计摘要 | 打款记录完整视图见 [admin-payouts.md](admin-payouts.md) |
| 驳回对话框 | Modal：说明 + Radio.Group（人工可选原因码，每项下方显示用户可见文案）+ TextArea 内部备注 + StepUpModal | `reject_reason_code`、`reject_note` | 原因必选；USER_REQUEST 用于客服受理撤销（BR-WDR-10）；从 APPROVED 驳回的限制按 BR-WDR-10 |
| 手动成功对话框 | Modal：单号、收款方式、应付金额、Input 通道流水号、DatePicker 实付时间、InputNumber 实付金额 + 校验说明 + StepUpModal | BR-WDR-16 必填项 | 录入即确认，一人可完成；微信零钱单不显示本按钮（BR-WDR-33 ⑧） |
| 微信等用户确认 | Alert（截止时间、到期处理说明）+ 通道子状态行 | 通道子状态、确认截止 | 【撤销微信转账】填原因后 StepUpModal |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 状态、审核方式、转人工原因、风险标签 | BR-TEXT-25 `admin_dict.withdrawal_status.*`、`withdrawals.review_mode.*`、`withdrawals.auto_decision.failed_conditions[].*`、`withdrawals.risk_flags[].code.*` |
| 驳回原因码后台中文名 | BR-TEXT-25 无行，契约线补；对话框里「用户看到」一栏取 BR-TEXT-08 的用户文案字典 |
| 微信通道子状态中文名 | BR-WDR-33 待实测（CAP-X-15）；契约线补，补齐前显示编码 |
| 金额、时间 | BR-TEXT-10、BR-TEXT-11 |
| 错误提示 | BR-TEXT-14（10403、40401、20001、step-up 失效） |
| 其余（区块标题、快照说明、到期处理说明） | 08 无键，用画板文案，登记 admin.withdrawal_detail.* |

## 4. 接口（operationId 为暂拟，由 CT-24 分配）

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| adminGetWithdrawal | 进入、每次写操作后刷新 | 10001、10403、40401 |
| adminApproveWithdrawal / adminRejectWithdrawal | 审核通过 / 驳回 | 状态已变（CAS 失败）、W2 守卫不通过（只按 BR-WDR-10 / BR-WDR-05，风控冻结或有提现冻结记录的会员可以通过）、存在非失败转账尝试不得驳回（BR-WDR-10）；具体码按 `contracts/error-codes.yaml` |
| adminManualPaidWithdrawal | 手动成功 | 流水号重复、金额不等于实付、存在转账尝试（BR-WDR-16 守卫） |
| adminRecalcRiskFlags | 【重新计算】 | 10403 |
| adminCancelWechatTransfer | 【撤销微信转账】 | 状态不是等用户确认；通道结果待实测（BR-WDR-33） |
| adminRevealUser（`users/{id}/reveal`） | 【查看】全量 | 10403；每次写审计 |

## 5. 权限点与开关（04 §11.2）

`withdraw.review`（通过 / 驳回，动态码）；`payout.execute`（执行打款、撤销微信转账，动态码）；`payout.manual_entry`（手动成功，动态码）；`pii.reveal_phone` / `pii.reveal_identity`（查看全量，动态码）；`fund.view`（只读）。一人可完成全部环节（BR-WDR-11）；二次验证每次操作都验（08 §14.7 审计 D 决定前）。

## 6. 稿上没画、实现要做的

按钮随状态隐藏而不是置灰（终态无写操作）；提交中禁用并保留对话框；对话框关闭后焦点回触发按钮（03 §10.5）；判定表 ①–⑬ 用真实表格语义；审核时限超时后不改颜色以外的语义，附带文字；1280 以下 Descriptions 改单列。

## 7. 待定与不一致

- 微信零钱通道的状态值、受理码与撤销结果在 09 CAP-X-15 实测前只作占位（BR-WDR-33 ⑦），画板写「待实测」；不得写成对用户的承诺。
- 画板【手动成功】【录入并确认】标「短信」，以 04 §11.2 `payout.manual_entry` 动态码为准（同 [admin-withdrawals.md](admin-withdrawals.md) §7 ②）。
- 驳回对话框的「用户看到」文案为示意，实现取 BR-TEXT-08 字典；人工可选的原因码集合以 BR-WDR-10 为准，系统专用码不出现在对话框里。
- 状态名同列表（BR-TEXT-25），画板旧名待改。
- 「审核时限」只对转人工的单显示（BR-WDR-26、BR-WDR-25）；自动到账单不显示，画板两张均为转人工样例，无冲突。
