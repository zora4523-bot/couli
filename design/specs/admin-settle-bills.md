# 月结账单 settle-bills（管理后台）

- 核对版本：规划提交 8c91f67（负责人 2026-10-18 后台第 2 批定稿「全部按推荐」，`docs/changes/20261018-后台第2批定稿.md`）；代码主干 2fdbf110（rebate-platform 远端 main，2026-10-18 核对，尚无后台财务契约；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（PNG 在 `review-admin/png/`），不入公开仓库；完整 sha256 登记在 [design/README.md](../README.md) 第 15 项「管理后台第 2 批」
- 路由：后台资源 `settle-bills`（菜单「资金 / 月结账单」）、`settle-bills/{month}`（详情）、批次明细 `settle-batches/{id}`；从哪来：侧栏、工作台「待确认月结」卡；去哪：差错单列表（[admin-recon.md](admin-recon.md)）、订单详情、紧急开关页（结算总开关）
- 需求：01 F-ADM-08（月结部分）；规则只引编号：BR-FUND-04（③–⑫ 流程、月结账单状态、结算批次迁移表 SB1–SB10、补充批次、上传备用）、BR-FUND-05（入账金额）、BR-FUND-09（结算记录版本）、BR-FUND-01 R5a / BR-CALC-13（受益人补记项）、BR-FUND-20（入账开关）；验收：AC-ADM-08（同号规则）、10 AC-S2-01-TB、AC-S2-03、AC-S2-11、AC-S2-51、AC-S2-57、AC-S2-59、AC-S1-157；任务：05 F1-08d
- 可参考的已合并页面：`apps/admin/src/pages/admins/**`；配置中心页的 Card 写法
- 是否资金或归属页面：是（确认即批量入账）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 列表 | AdmSettleBills.dc.html（790b1a57eab4） | 持 `settle.bill` 或 `fund.view` | adminListSettleBills · 200 · example |
| 详情（已出账） | AdmSettleBillDetail.dc.html（d412d70cbc76） | 存在待确认批次 | adminGetSettleBill · 200 |
| 确认结算对话框 | AdmSettleBillConfirm.dc.html（e6cdc11cf925） | 点【确认立即执行】【定时执行】 | adminConfirmSettleBatches |
| 详情（结算中 / 部分完成）+ 批次明细 | AdmSettleBillRunning.dc.html（004bf542cad9） | 批次 EXECUTING / PARTIAL（结算总开关关闭时） | adminGetSettleBill + adminListSettleBatchItems |
| 发起补充批次 | AdmSettleSupplementLaunch.dc.html（114405a5fa50） | 点【发起补充批次】 | adminPreviewSupplementBatch（预校验）→ adminCreateSupplementBatch |
| 补充批次已生成 | AdmSettleSupplementCreated.dc.html（a59522351031） | 生成成功 | 成功 Alert + 刷新详情 |
| 补充批次无可纳入数据 | AdmSettleSupplementEmpty.dc.html（a4cb3eda1808） | 预校验结果为空 | 预校验返回空；不生成空批次 |
| 上传结算明细（校验未通过） | AdmSettleStatementUpload.dc.html（afbb1e226bbd） | 「上传」来源平台点【上传结算明细】 | 本地逐行校验 + adminValidateSettleStatement |
| 上传结算明细（可导入） | AdmSettleStatementUploadReady.dc.html（862b8a4ed35d） | 全部行通过 | adminImportSettleStatement |
| 结算明细已导入 | AdmSettleStatementUploaded.dc.html（09d7d44e27b4） | 导入成功 | 成功 Alert；来源表状态「已上传」 |
| 空 / 加载中 / 出错 | 不适用（无画板；按三态写法） | — | 本地 |
| 无权限 | 不适用 | 无 `settle.bill` 且无 `fund.view` | 菜单隐藏；10403 |

画板上的账单月、子订单数、金额、批次号、差错单数、平台名与「财务小狸」均为样例；平台只以文字标识。

## 2. 组件（03 §9.1 antd）

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 下一期卡 | Card：下一期账单月、账单日说明 + Table（平台、结算数据来源、状态、操作【上传结算明细】/【重新上传】） | `settle.bill_day`、`settle.statement_source.<platform>` | 上传只对来源为 upload 的平台显示（`settle.statement_upload`，不需二次验证） |
| 筛选 | Form：Select（账单月、账单状态）+【重置】【查询】 | 查询参数 | — |
| 列表 | Table：账单月、账单状态、生成时间、子订单数、联盟结算佣金、受益人份额、平台留存、差错单、暂缓、操作【查看】 | 账单聚合字段 | 进详情 |
| 详情标题 | Title + Tag（账单状态，BR-FUND-04 细则「月结账单状态」派生）+ Button【驳回】【定时执行】【确认立即执行】（`settle.bill`，动态码）+ 说明 Alert（确认一次覆盖本账单全部待确认批次；驳回后果） | 账单状态、待确认批次数 | 按钮按状态显示；结算总开关关闭时 Alert 说明已停止、可继续 |
| 统计卡 | Statistic × 6：子订单数（口径说明）、已入账 / 待入账、差错单、暂缓、联盟结算佣金、受益人份额、平台留存 | 聚合字段 | 口径文字只读 |
| 一致性校验结果 | Table：平台、范围内子订单、进批次候选、账单金额不一致、应结未结、状态不符、暂缓、说明（入账开关关闭的平台只保留校验） | BR-FUND-04 ④、`credit.enabled.<platform>` | 差错单数链接到差错单列表 |
| 结算批次 | Table：批次号、平台、类型（首批 / 补充）、子订单数（+ 补记项数）、联盟结算佣金、批次状态、结算方式（定时含时刻）、确认人、操作【明细】【继续执行】【撤销定时】+ Button【发起补充批次】 | `settle_batch.status`、`settle_mode`、`scheduled_at` | 继续执行 / 撤销定时按 SB3、SB8（动态码） |
| 批次明细 | Table：子订单 / 补记项、类型、受益人、入账金额、结果、原因；进度文字 | 批次成员 | 只读 |
| 确认结算对话框 | Modal：摘要 + Radio（立即执行 / 定时执行）+ DatePicker 执行时间（校验说明）+ StepUpModal | `settle_mode`、`scheduled_at` | 定时时刻限制按 BR-FUND-04 ⑥⑦ |
| 发起补充批次对话框 | Modal：适用条件说明、范围 Checkbox（按平台；入账开关关闭的平台不可选）、预校验结果 Table（来源 × 平台 × 金额、已在批次中的不重复、受益人补记项）、将生成批次数、后果说明 + StepUpModal【生成补充批次】；空结果态列出未纳入原因与去处理的链接 | BR-FUND-04 ⑧⑫ | 预校验为空时禁用生成 |
| 上传结算明细对话框 | Modal：Select 平台（只列 upload 来源）、Select 账期、【下载模板】、Upload、逐行校验结果 Table（行号、子订单号、结算佣金、结算时间、原因）、【下载未通过的行】、通过 / 未通过计数、【确认导入】 | BR-FUND-04 ③ upload 来源、BR-FUND-09 | 有未通过行整份不导入；重新上传记新结算记录 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 批次状态、结算方式 | BR-TEXT-25 `admin_dict.settle_batch.status.*`、`settle_mode.*` |
| 月结账单状态（出账中 / 已出账 / 待结算 / 结算中 / 已结算） | BR-FUND-04 细则「月结账单状态」派生；BR-TEXT-25 无行，契约线补 |
| 批次明细结果（已入账 / 跳过 / 暂缓 / 未处理）、一致性校验列名 | BR-TEXT-25 无行，契约线补；差错单类型取 `recon_diff_type.*` |
| 金额、时间 | BR-TEXT-10、BR-TEXT-11、BR-TEXT-21（收益类金额列口径编码） |
| 错误提示 | BR-TEXT-14（10403、20001、step-up 失效） |
| 其余（口径说明、适用条件、模板说明） | 08 无键，用画板文案，登记 admin.settle_bills.* |

## 4. 接口（operationId 为暂拟，由 CT-24 `settle-bills` / `settle-batches` 分配）

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| adminListSettleBills / adminGetSettleBill | 进入、筛选、写操作后刷新 | 10001、10403、40401 |
| adminConfirmSettleBatches | 确认立即 / 定时 | 一致性校验未通过不能确认（F1-08d 验收）、定时时刻不合法（20001）、开关关闭（SB 守卫） |
| adminRejectSettleBatches / adminCancelSchedule / adminResumeSettleBatch | 驳回（必填原因）/ 撤销定时 / 继续执行 | 状态不允许（SB3、SB4、SB8 守卫） |
| adminPreviewSupplementBatch / adminCreateSupplementBatch | 发起补充批次（预校验 / 生成） | 无可纳入数据（返回空，不报错）；10403 |
| adminListSettleBatchItems | 【明细】 | 40401 |
| adminValidateSettleStatement / adminImportSettleStatement | 上传校验 / 导入 | 20001（逐行原因）；账单已开始生成后拒绝 |

## 5. 权限点与开关（04 §11.2 / §10.2）

`settle.bill`（确认、撤销定时、驳回、继续执行、补充批次，动态码，单人确认）；`settle.statement_upload`（上传，不需二次验证）；`fund.view`（只读）；`export`。开关：`settle.auto.enabled`（执行中关闭的处理按 BR-FUND-04 ⑦ 与结算批次迁移表，本页只显示并提示去紧急开关页）、`credit.enabled.<platform>`（关闭的平台不生成批次）。

## 6. 稿上没画、实现要做的

确认按钮在存在未通过的一致性校验或无待确认批次时禁用并说明；驳回弹输入原因（必填，无二次验证以外的要求按 SB4 动态码）；定时执行到时自动执行，页面轮询或手动刷新；统计卡口径文字折叠为帮助图标 + Tooltip 且可聚焦；批次表子订单数与补记项数分两段读出；上传对话框的逐行结果表可键盘遍历；1280 以下校验结果表横向滚动。

## 7. 待定与不一致

- 联盟结算明细上传只做后端接口，前端页面延后到 P1（01 F-ADM-08 §4-9、05 F1-08d）：三张上传画板本期不实现，只作接口形状与 P1 参考；来源表的【上传结算明细】按钮本期不渲染。
- 月结账单状态与批次明细结果的后台中文名不在 BR-TEXT-25：契约线补行；画板名为示意。
- 一致性校验结果的列「状态不符」对应差错单类型沿用 BR-FUND-09（BR-FUND-04 细则表），具体 `recon_diff_type` 取值由契约线对齐。
- 画板样例把「确认一次覆盖本账单全部待确认批次」写成固定做法，与 BR-FUND-04「超出拆多批，随账单一次确认」一致；按批次单独确认不提供。
- 补充批次预校验的分类（差错单已处理 / 维权关闭 / hold 解除 / 结算数据后到）为稿面分组，字段由契约线定；不自定枚举。
