# 对账任务与差错单 recon（管理后台）

- 核对版本：规划提交 8c91f67（负责人 2026-10-18 后台第 2 批定稿「全部按推荐」，`docs/changes/20261018-后台第2批定稿.md`）；代码主干 2fdbf110（rebate-platform 远端 main，2026-10-18 核对，尚无后台财务契约；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（PNG 在 `review-admin/png/`），不入公开仓库；完整 sha256 登记在 [design/README.md](../README.md) 第 15 项「管理后台第 2 批」
- 路由：后台资源 `recon`（菜单「资金 / 对账与差错」，页签「对账任务」）、`recon-diffs`（页签「差错单」）、`recon-diffs/{id}`（处理抽屉）；从哪来：侧栏、工作台「未关闭差错单」卡、月结账单详情、提现单详情（风险标签「有对账差错」）；去哪：调账页（[admin-adjustments.md](admin-adjustments.md)）、订单详情、提现单详情、支付单收款对账（R4，F1-13）
- 需求：01 F-ADM-08（对账与差错单部分）；规则只引编号：BR-FUND-19（日终校验、余额缓存重算）、BR-FUND-20（联盟回款 R1 确认）、BR-FUND-22（平台恢复 / 申诉恢复差错单，ADMIN_RESTORE）、BR-FUND-23（月末三项核对）、BR-FUND-24（RECON_FIX 调账）、BR-WDR-23（通道对账 R2 与提现冻结）、BR-WDR-05（差错单关闭随单解除冻结）、BR-PAY-07（R4 在支付单页处理）；验收：AC-ADM-08、10 AC-S2-30、AC-S2-48、AC-S2-49、AC-S2-50、AC-S2-93、AC-S2-95、AC-S1-157；任务：05 F1-08e
- 可参考的已合并页面：`apps/admin/src/pages/admins/**`
- 是否资金或归属页面：是（恢复、调账、关闭差错单改变资金与冻结）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 对账任务列表 + 月末三项核对 | AdmRecon.dc.html（894f7d854fa0） | 持 `fund.recon` 或 `fund.view` | adminListReconRuns · 200 · example；adminGetMonthEndCheck |
| 差错单列表 | AdmReconDiffsList.dc.html（4ddb589b0b6a） | 页签「差错单」 | adminListReconDiffs · 200 · example |
| 差错单处理（申诉恢复） | AdmReconDiffs.dc.html（70b1104410e4） | 行操作【处理】，类型为申诉恢复 | adminGetReconDiff；【确认恢复】adminRestoreOrders；【不恢复并关闭】adminCloseReconDiff |
| 其他类型的处理（调账 / 核销 / 关闭） | 不适用（无画板；抽屉同布局，操作区按类型换按钮） | 行操作【处理】 | 调账跳 [admin-adjustments.md](admin-adjustments.md) 新建并带关联单据 |
| 空 / 加载中 / 出错 | 不适用（无画板；按三态写法） | — | 本地 |
| 无权限 | 不适用 | 无 `fund.recon` 且无 `fund.view` | 菜单隐藏；10403 |

画板上的差错单号、申诉单号、订单号、UID、金额与月末三项数字均为样例；平台只以文字标识。

## 2. 组件（03 §9.1 antd）

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 标题行 | Title + Button【手动触发 R1 联盟对账】（`fund.recon`）+ Tabs（对账任务 / 差错单 Badge） | 未关闭差错单计数 | 触发后新增一行「运行中」 |
| R4 提示 | Alert：收款对账（R4）的差错在支付单页处理 + 链接 | — | BR-PAY-07 |
| 任务筛选 | Form：Select（对账任务 R1 / R2 / R3 / 月末三项、对象）、RangePicker（周期）+【重置】【查询】 | 查询参数 | — |
| 任务列表 | Table：对账任务、对象（平台 / 通道 / 全部账户）、周期、运行时刻、状态（已完成 / 有差异 / 等待账单 / 运行中）、核对数、差异数、操作【明细】【差错单】【报表】；手动触发行加标注 | `recon_runs` | 【差错单】带 source + 周期筛选进差错单页签 |
| 月末三项核对 | Card：月份、结论 Tag（已平 / 不平）、X1 / X2 / X3 与差值、只供财务查看的附加行 + Button【导出】【导出记录】 | BR-FUND-23 | 不平时链接到对应差错单 |
| 差错单筛选 | Form：Select（类型 `recon_diff_type`、来源 `recon_diffs.source`、状态 `recon_diff_status`）+ 金额列说明 Alert | 查询参数 | — |
| 差错单列表 | Table：差错单号、类型、来源、周期、关联单据（链接）、我方已记（含说明小字）、对方（含说明）、差额（正负只表示谁大，结论另看）、状态、操作【处理】【详情】 | `recon_diffs` | — |
| 处理抽屉（申诉恢复） | Drawer：差错单摘要（来源、申诉单、用户、生成时间、风控状态、处理权限）+ 恢复范围 Table（子订单、当前状态、恢复方式、补发金额）+ 补发合计、流水类型、用户余额前后 + Button【不恢复并关闭】（必填原因）【确认恢复】（`order.restore`，动态码） | BR-FUND-22 R12 / R13、③ | 处罚作废的订单不在范围（BR-FUND-22） |
| 处理抽屉（其他类型） | 同上摘要 + 按类型的操作：【去调账】（带关联单据，`fund.adjust`）、【核销】（R2 迟到成功 → W11，`payout.execute`）、【已关闭（不处理）】（必填原因，`fund.recon`）、【重算余额缓存】（R3，短信档） | BR-FUND-19、BR-WDR-23、BR-FUND-24 | 关闭时随单解除 `recon_diff` / `ledger_mismatch` 冻结（04 §11.2 `fund.recon`） |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 差错单类型、来源、状态 | BR-TEXT-25 `admin_dict.recon_diff_type.*`、`recon_diffs.source.*`、`recon_diff_status.*`（已有行直接用） |
| 对账任务状态（已完成 / 有差异 / 等待账单 / 运行中）、恢复方式 | BR-TEXT-25 无行，契约线补；补齐前显示编码 |
| 调账原因码（抽屉里的流水类型行） | BR-FUND-24 ②；后台中文名契约线补（见 [admin-adjustments.md](admin-adjustments.md) §3） |
| 金额、时间 | BR-TEXT-10、BR-TEXT-11、BR-TEXT-21 |
| 错误提示 | BR-TEXT-14（10403、20001、step-up 失效、40401） |
| 其余（金额列说明、R4 提示、适用范围说明） | 08 无键，用画板文案，登记 admin.recon.* |

## 4. 接口（operationId 为暂拟，由 CT-24 `recon` / `recon-diffs` / `withdraw-holds` 分配）

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| adminListReconRuns / adminGetReconRun | 进入、筛选、【明细】 | 10001、10403、40401 |
| adminTriggerRecon（R1） | 【手动触发 R1 联盟对账】 | 已有运行中任务；10403 |
| adminGetMonthEndCheck | 进入任务页签 | 10403 |
| adminListReconDiffs / adminGetReconDiff | 切页签、筛选、【处理】 | 10403、40401 |
| adminRestoreOrders（ADMIN_RESTORE） | 【确认恢复】 | platform_status 为失效不得恢复（R12 守卫）；10403 |
| adminCloseReconDiff | 【不恢复并关闭】【已关闭（不处理）】 | 原因为空（20001）；关闭时解除冻结失败按 `contracts/error-codes.yaml` |
| adminRecalcBalanceCache | 【重算余额缓存】 | 短信档 token 缺失被拒（BR-ID-34） |
| adminCreateExport | 月末三项【导出】 | 10403 |

## 5. 权限点与开关（04 §11.2）

`fund.recon`（对账操作与差错单处理、关闭结案必填原因；普通操作不需二次验证，触发余额缓存重算须短信档）；`order.restore`（平台恢复 / 申诉恢复，动态码，一人可完成）；`fund.adjust`（由差错单去调账，短信档，见调账规格）；`payout.execute`（R2 迟到成功核销 W11，动态码）；`fund.view`（只读）；`export`。

## 6. 稿上没画、实现要做的

差错单状态变更后列表与工作台计数刷新；关闭对话框原因必填且提示会解除哪些冻结；恢复范围表只读、补发合计用 `aria-live`；月末三项等式用表格语义；任务列表「运行中」行轮询；1280 以下差错单表横向滚动、关联单据列固定。

## 7. 待定与不一致

- 画板差错单类型名（通道对账差异 / 日终账务差异 / 账单金额不一致 / 已作废订单被平台恢复）与 BR-TEXT-25 `recon_diff_type`（通道对账不一致 / 账实不符 / 月结金额不一致 / 平台恢复）不一致：实现按 BR-TEXT-25，画板待改名（提现线改名同一轮）。
- 「差额 = 对方 − 我方已记」与正负号说明为稿面约定；字段名与计算方向由契约线定，画板只作列说明。
- 画板只画了申诉恢复一种处理流程；调账、核销、关闭、重算的抽屉操作区按本规格 §2 末行与 F1-08e 实现，补画板时核对。
- 「处罚解冻」差错单类型取值待契约线登记（BR-FUND-22 细则「处罚解冻证实之后」），列表筛选项补齐前显示编码。
