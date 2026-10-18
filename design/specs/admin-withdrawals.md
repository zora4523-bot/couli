# 提现审核列表与自动到账设置 withdrawals（管理后台）

- 核对版本：规划提交 8c91f67（负责人 2026-10-18 后台第 2 批定稿「全部按推荐」，`docs/changes/20261018-后台第2批定稿.md`）；代码主干 2fdbf110（rebate-platform 远端 main，2026-10-18 核对，尚无后台财务契约；派发前再核对一次，对不上的写进第 7 节）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（PNG 在 `review-admin/png/`），不入公开仓库；完整 sha256 登记在 [design/README.md](../README.md) 第 15 项「管理后台第 2 批」
- 路由：后台资源 `withdrawals`（菜单「资金 / 提现审核」），页面内四个页签：审核列表（本规格）、打款队列与结果待确认（[admin-payouts.md](admin-payouts.md)）、自动到账设置（本规格 §2 末段）；从哪来：侧栏、工作台「待审提现」卡（带状态筛选）、一框搜命中提现单号；去哪：提现单详情（[admin-withdrawal-detail.md](admin-withdrawal-detail.md)）、用户详情、导出记录、紧急开关页
- 需求：01 F-ADM-07、F-ADM-12（自动到账设置）；规则只引编号：BR-WDR-08（展示状态映射）、BR-WDR-10（审核与驳回、批量审核）、BR-WDR-11（权限与批次归属）、BR-WDR-12（批次执行、【批量自动打款】、一键组批）、BR-WDR-16（【批量手动打款】）、BR-WDR-29（风险标签）、BR-WDR-30（自动到账判定与设置）；验收：AC-ADM-07（同号规则）、10 AC-S2-20、AC-S2-53、AC-S2-102、AC-S2-28、AC-S2-59、AC-S1-157；任务：05 F1-08a（列表、批量审核、一键组批）、F1-08c（批量手动打款）、F1-10（自动到账设置随配置中心）
- 可参考的已合并页面：`apps/admin/src/pages/admins/**`（列表 + 对话框写法）
- 是否资金或归属页面：是（审核、批量打款、线下补录都改变提现单状态）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 列表正常 | AdmWithdrawList.dc.html（2ac7d0122ace） | 持 `withdraw.review` 或 `fund.view` 进入 | adminListWithdrawals · 200 · example |
| 筛选已改未应用 | AdmWithdrawListFilterDraft.dc.html（cfb0cfabf00f） | 改了筛选控件、未点【查询】 | 本地：表单脏状态 |
| 筛选已应用 | AdmWithdrawListFilterApplied.dc.html（21ba428a5b45） | 点【查询】后 | 同上接口，带新参数；已选项清空 |
| 批量通过确认 | AdmWithdrawBatchApprove.dc.html（f9a4adb6ad1f） | 勾选后点【批量通过】 | adminBatchApproveWithdrawals（预览为本地按状态分组） |
| 批量手动打款 | AdmWithdrawManualBatch.dc.html（126414a8fdf8） | 勾选后点【批量手动打款】 | 模板下载 / 导入预览本地校验；提交 adminBatchManualPaid |
| 自动到账设置 | AdmWithdrawAutoSettings.dc.html（de60f79a4925） | 页签「自动到账设置」 | adminGetAutoPayoutSettings · 200；保存 adminUpdateAutoPayoutSettings |
| 1280 窄窗 | AdmAdaptWithdrawList1280.dc.html（244e9dbabce1） | 视口 ≤ 1280 | 本地 |
| 720 宽（200% 缩放） | AdmAdaptWithdrawList720.dc.html（33388a9511fa） | 视口 < 1280 或 200% 字号 | 本地 |
| 空 / 加载中 / 出错 | 不适用（无画板；按 AdmUsersStates 的三态写法） | 无结果 / 在途 / 失败 | 同上置空 / 本地 |
| 无权限 | 不适用 | 无 `withdraw.review` 且无 `fund.view` | 菜单隐藏；10403 |

画板上的提现单号、UID、金额、风险标签、操作人「财务小狸」、自动到账阈值与前置检查状态均为样例数据；手机号、姓名只以脱敏样式出现。

## 2. 组件（03 §9.1 antd；二次验证按 03 §9.2 StepUpModal）

| 区域 | 组件 | 数据（接口字段） | 交互 |
| --- | --- | --- | --- |
| 标题行 | Typography.Title + Badge「待审 N」+ Button【导出】【导出记录】 | 待审计数（F-ADM-07） | 导出走异步任务（`export`），记录页见 [admin-ledger.md](admin-ledger.md) §2 |
| 页签 | Tabs：审核列表 / 打款队列（Badge）/ 结果待确认（Badge）/ 自动到账设置 | 各页签计数 | 切换路由 |
| 状态页签 | Tabs + Badge：全部 / 待审 / 驳回 / 手动 / 自动 | 按展示状态与 `review_mode` 计数 | 切换即筛选 |
| 筛选卡 | Form：Select（展示状态、审核方式 `review_mode`、收款方式 `payout_method`）、RangePicker（申请时间）、【重置】【查询】；条件改动未应用时 Alert 列出改了哪些、说明结果仍对应旧条件 | 查询参数 | 点【查询】应用并清空已选；受阻原因筛选见 §7 ③ |
| 批量栏 | 已选统计（待执行 / 待审核张数、合计实付）+ Button【批量通过】（`withdraw.review`）【批量手动打款】（`payout.manual_entry`）【批量自动打款】（`payout.execute`） | 已选 items | 三个都弹确认对话框，列出将处理与跳过的单；一次二次验证覆盖本批（BR-WDR-10 细则） |
| 列表 | Table：勾选、提现单号、用户 / 收款（UID + 收款方式）、申请金额、展示状态（第二行放「暂停」「执行受阻」原因）、风险标签、原因 / 执行结果（转人工原因、审核人与时间、批次号、驳回原因码）、申请时间、操作【审核】或【详情】 | items[]：`status`、`review_mode`、`auto_decision.failed_conditions[]`、`risk_flags[]`、`reject_reason_code`、`batch_id` | 行操作进详情；驳回内部备注悬停显示 |
| 批量通过对话框 | Modal + Table（单号、用户、金额、本次处理：将通过 / 跳过及原因）+ 后果说明 + StepUpModal（动态码） | 本地分组 | 只处理 PENDING_REVIEW 单（BR-WDR-10 细则）；通过后不自动打款 |
| 批量手动打款对话框 | Modal：【下载流水号模板】（按勾选预填单号与应付）、Upload 导入、导入预览 Table（单号、收款方式、应付、通道流水号、实付时间、实付金额、校验）、未通过行提示、StepUpModal（动态码） | 导入行 | 未通过校验的行不录入，其余逐单录入并确认（BR-WDR-16 细则） |
| 自动到账设置 | Alert（开启前置检查清单，BR-WDR-30 细则「开启前置检查」）+ Form 分组 ①–⑧「对应花卷云」、⑨⑫「本系统附加」、⑩⑪⑬「固定条件只读」+ 规则版本 + 【恢复默认值】【保存】（`config.business`，动态码） | `withdraw.auto_payout.*`、`rule_version` | ① 总开关只读显示状态 + Button【去紧急开关页】（负责人 2026-10-18 第 2 批定稿 ①：总开关只在紧急开关页改，需 `switch.all`）；保存校验与版本递增按 BR-WDR-30 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 提现状态、审核方式、转人工原因、风险标签中文名 | BR-TEXT-25 `admin_dict.withdrawal_status.*`、`withdrawals.review_mode.*`、`withdrawals.auto_decision.failed_conditions[].*`、`withdrawals.risk_flags[].code.*`（已有行直接用） |
| 展示状态（待审核 / 暂停 / 执行受阻等派生态） | BR-WDR-08 细则映射；中文名由契约线随 CT-24 在 BR-TEXT-25 补行，补齐前显示编码 |
| 驳回原因码中文名 | BR-TEXT-25 无行，契约线补；用户可见文案另按 BR-TEXT-08 |
| 金额 | BR-TEXT-10（后台格式） |
| 错误、无权限提示 | BR-TEXT-14（10403、20001 按 `contracts/error-codes.yaml`） |
| 其余（筛选说明、批量栏说明、设置页各项说明） | 08 无键，用画板文案，登记 couli-runs/F1-frontend/needs.md（admin.withdrawals.*） |

## 4. 接口（operationId 为暂拟，子编号由契约线随 CT-24 分配）

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| adminListWithdrawals | 进入、筛选、切页签、切页、重试 | 10001、10403、20001 |
| adminBatchApproveWithdrawals | 批量通过确认 | 10403、step-up 失效（BR-ID-34）；逐单结果在响应里（不通过的条件只按 BR-WDR-10 与 BR-WDR-05 的 W2 守卫；风控冻结或有提现冻结记录的会员可以通过） |
| adminBatchManualPaid | 批量手动打款确认 | 同上；流水号重复、金额不等于应付逐单返回（BR-WDR-16） |
| adminCreatePayoutBatch | 批量自动打款确认（对勾选 APPROVED 单建 kind=manual 批次并 EXECUTE，BR-WDR-12） | 整批拒绝的原因（开关、队列暂停、水位）与逐单结果在响应里 |
| adminGetAutoPayoutSettings / adminUpdateAutoPayoutSettings | 进入设置页 / 保存 | 20001（保存校验，BR-WDR-30）、10403 |
| adminCreateExport | 【导出】 | 10403 |

## 5. 权限点与开关（04 §11.1 / §11.2 / §10.2）

`withdraw.review`（审核、驳回、批量通过，动态码）；`payout.execute`（批量自动打款，动态码）；`payout.manual_entry`（批量手动打款，动态码）；`config.business`（保存自动到账设置，动态码）；`switch.all`（改 `withdraw.auto_payout.enabled`，只在紧急开关页，本页只放入口）；`fund.view`（只读进入）；`export`。开关：批量自动打款的整批前置只有 `payout.enabled`、`payout.queue_paused`（BR-WDR-12 ①），`payout.channel_enabled.<channel>` 逐单判断（②）；`withdraw.auto_payout.enabled` 只影响判定（BR-WDR-30），不参与 EXECUTE；本页只显示结果。服务端校验为准，前端按权限点隐藏按钮。

## 6. 稿上没画、实现要做的

状态名一律取 BR-TEXT-25（见 §7 ①）；批量操作提交中禁用三个按钮，完成后清空已选并刷新计数；筛选修改后未应用的提示在点【查询】或【重置】时消失；表格列宽固定、容器内横向滚动，勾选与单号固定左侧、操作列固定右侧（1280 稿）；低于 1280 侧栏收成抽屉，每行加【展开】竖排次级信息（720 稿）；读屏：行操作名「审核 W…」「查看 W… 详情」，批量栏统计用 `aria-live`；金额千分位两位小数；设置页只读项用 `aria-readonly`。

## 7. 待定与不一致

- ① 画板列表的状态名为旧名（等待审核 / 自动成功 · 系统自动 / 手动成功 / 审核驳回），与 BR-TEXT-25 `withdrawal_status`（待审核 / 接口打款成功 / 线下打款成功 / 已驳回）不一致：实现按 BR-TEXT-25；提现线画板整批改名另立一轮（`review-admin/review-log.md`「后续另立一轮」），不阻塞实现。
- ② 【批量手动打款】与【录入并确认】按钮的档位在部分画板仍标「短信」（AdmWithdrawBatchApprove、AdmWithdrawManualBatch、AdmAdaptWithdrawList720）：以 04 §11.2 `payout.manual_entry` 动态码为准（2026-10-06 Jev 判断），不改规划。
- ③ F-ADM-07 2026-10-18 新增的「按受阻原因筛选 → 一键组批」本轮未画（review-log 第 1 轮 #25）：实现按 F-ADM-07 与 BR-WDR-12，受阻原因作为筛选项放筛选卡，一键组批复用【批量自动打款】的确认对话框；补画板时按本规格 §2 核对。
- ④ 自动到账设置页的金额、次数、前置检查「未满足」状态为 BR-WDR-30 默认值与 09 现状的示意；配置项合法范围按 08 §14.7 第 3 行由契约线登记。总开关能否开启仍须 BR-WDR-30 细则「开启前置检查」全部通过并经负责人确认，本页不提供开关。
- ⑥ 批量通过对话框画板写「余额为负、冻结 / 封禁、收款账号命中黑名单的单不会通过」，与 BR-WDR-10（风控冻结或有 withdraw_holds 时也可以审核通过；不得通过的只有 W2 守卫所列）不完全一致：实现与响应文案按 BR-WDR-10 / BR-WDR-05，画板待改。
- ⑤ 列表「展示状态」的派生逻辑与字段名（BR-WDR-08 细则映射、`execute_blocked`）由 CT-24 子契约 `withdrawals` 定；定前列表按 `status` + `auto_decision` 本地派生，不自定新枚举。
