# 人工调账与坏账核销 adjustments（管理后台）

- 核对版本：规划提交 8c91f67（负责人 2026-10-18 后台第 2 批定稿「全部按推荐」，`docs/changes/20261018-后台第2批定稿.md`）；代码主干 2fdbf110（rebate-platform 远端 main，2026-10-18 核对，尚无后台财务契约；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（PNG 在 `review-admin/png/`），不入公开仓库；完整 sha256 登记在 [design/README.md](../README.md) 第 15 项「管理后台第 2 批」；用户详情【调整余额】抽屉 AdmUserBalanceAdjust.dc.html（04b54121cb68）已在第 1 批登记
- 路由：后台资源 `adjustments`（菜单「资金 / 调账与核销」，页签「调账单」）、`bad-debt-writeoffs`（页签「坏账核销」）；从哪来：侧栏、差错单处理【去调账】、用户详情【调整余额】（[admin-user-detail.md](admin-user-detail.md)）；去哪：用户详情、差错单、凭证（余额流水）
- 需求：01 F-ADM-08（调账、坏账核销）、F-ADM-04（调整余额入口）；规则只引编号：BR-FUND-24（①–⑧ 流程与原因码、红冲整笔、后台入口一步提交——负责人 2026-10-18 第 2 批定稿 ② 确认）、BR-FUND-16（凭证唯一键）、BR-FUND-12（坏账核销候选与批准）、BR-FUND-10 / 11（负余额）、BR-ID-28（注销 ACCOUNT_CLOSED 预填单）、BR-ID-34（短信档）、BR-TEXT-19（用户侧流水文案）、BR-TEXT-09 / 23（站内信）；验收：AC-ADM-08、10 AC-S2-56、AC-S2-47、AC-S2-101、AC-S2-106、AC-S2-46、AC-S2-59、AC-S1-157；任务：05 F1-08f
- 可参考的已合并页面：`apps/admin/src/pages/admins/**`（抽屉表单与确认对话框）
- 是否资金或归属页面：是

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 调账单列表 + 新建抽屉 | AdmAdjust.dc.html（0fb0f5ab98e3） | 持 `fund.adjust` 点【新建调账单】 | adminListAdjustments · 200 · example；提交 adminCreateAdjustment（一步提交并生效） |
| 批准待批单 | AdmAdjustApprove.dc.html（52583862069d） | 待批准行点【批准生效】 | adminApproveAdjustment；同对话框【驳回】adminRejectAdjustment |
| 红冲 | AdmAdjustReverse.dc.html（5593542cdec1） | 已生效行点【红冲】 | adminCreateAdjustment（红冲单，关联原单） |
| 红冲已生效 | AdmAdjustReversed.dc.html（cfcb7c1cdff5） | 红冲提交成功 | 成功 Alert；原单标「已红冲」 |
| 坏账核销列表 + 批准 | AdmWriteoff.dc.html（75bc4f7b03d5） | 页签「坏账核销」，待批准行点【批准核销】 | adminListBadDebtWriteoffs；adminApproveBadDebtWriteoff |
| 核销暂不能批准 | AdmWriteoffBlocked.dc.html（5df5525e44c5） | 重读时有未完结提现单（BR-FUND-12、14 §14.6 决-11） | 服务端拒绝；候选单保持待批准 |
| 已核销 | AdmWriteoffDone.dc.html（e4980fc58e34） | 批准成功 | 成功 Alert + 刷新 |
| 空 / 加载中 / 出错 | 不适用（无画板；按三态写法） | — | 本地 |
| 无权限 | 不适用 | 无 `fund.adjust` / `fund.writeoff` 且无 `fund.view` | 菜单隐藏；10403 |

画板上的调账单号、候选单号、UID、金额、天数、阈值均为样例；核销候选阈值为开发期占位，上线前由超管填写（画板已标「样例」）。

## 2. 组件（03 §9.1 antd）

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 标题行 | Title + Button【新建调账单】（`fund.adjust`）+ Tabs（调账单 / 坏账核销 Badge） | 待批准计数 | — |
| 调账单筛选 | Form：Select（原因码、状态）+【重置】【查询】 | 查询参数 | — |
| 调账单列表 | Table：调账单号、用户、方向、金额（ACCOUNT_CLOSED 预填单显示「批准时取」）、原因码（中文名 + 编码）、关联单据（链接；OTHER 无单据时显示原因说明）、状态、发起 / 处理人、操作【批准生效】【驳回】【红冲】【详情】 | `admin_adjustments` | 待批准行（只有系统预填单）：批准（短信档）、驳回（必填原因，无二次验证）；已生效行：红冲；画板上的【撤回】随人工待批单取消而不再出现（见 §7） |
| 新建抽屉 | Drawer：Alert「一步完成」说明 + Form：Input UID（带余额摘要）、Radio 方向、InputNumber 金额、Select 原因码（RESTORE 不可选）、关联单据列表 +【添加关联单据】、TextArea 原因说明、预览（余额前后、用户流水显示、站内信说明）+ Button【提交并生效】（短信档 StepUpModal） | BR-FUND-24 ①②③ | 【提交并生效】= 保存 + 批准 + 凭证一步完成（决定 ②）；画板上的【保存待批】本期不渲染（见 §7） |
| 批准对话框 | Modal：单据摘要、关联单据摘要、批准时重读余额前后、后果说明 + Button【驳回】（必填原因）【批准并短信验证】 | BR-FUND-24 ①④⑤ | 只对系统预填单；人员要求与批准后的更正方式按 BR-FUND-24 ① 与细则「红冲只按原单整笔」 |
| 红冲对话框 | Modal：原单摘要、新单预览（方向相反、金额只读等于原单、凭证键）、TextArea 红冲原因（必填）、重读余额前后、后果说明 + Button【提交并短信验证】 | BR-FUND-24 细则「红冲只按原单整笔」、BR-FUND-16 | 可红冲的对象与次数限制按该细则；红冲单同样一步提交，画板上的【保存待批】本期不渲染 |
| 坏账核销列表 | Table：候选单号、用户、负余额起始日、已持续、生成时金额、当前可用余额、冻结中、状态、操作【批准核销】（短信档）或拦截说明 | `bad_debt_writeoff` | — |
| 批准核销对话框 | Modal：候选单摘要、当前余额与冻结、核销金额（按批准时余额）、后果说明（关联账户风控标记）+ StepUpModal（短信档）；拦截态 Alert（有未完结提现单，先处理到终态；候选单保持待批准）+【去处理提现单】 | BR-FUND-12 | 拦截开关配置键以 BR-FUND-12 / 08 §14.6 决-11 为准 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 调账单状态、核销候选状态 | BR-TEXT-25 `admin_dict.admin_adjustments.status.*`、`bad_debt_writeoff.status.*`（已红冲是标记不是状态，BR-TEXT-25 备注） |
| 调账原因码后台中文名 | BR-FUND-24 ② 的编码；后台中文名 BR-TEXT-25 无行，契约线补（画板名为示意）；用户侧流水名与说明只按 BR-TEXT-19 |
| 站内信 | BR-TEXT-09 / BR-TEXT-23 模板（调减发、调增不另发，按模板规则） |
| 金额、时间 | BR-TEXT-10、BR-TEXT-11 |
| 错误提示 | BR-TEXT-14（10403、20001、step-up 档位不符、重复红冲） |
| 其余（一步完成说明、后果说明、拦截说明） | 08 无键，用画板文案，登记 admin.adjustments.* |

## 4. 接口（operationId 为暂拟，由 CT-24 `adjustments` / `bad-debt-writeoffs` 分配）

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| adminListAdjustments / adminGetAdjustment | 进入、筛选、【详情】 | 10001、10403、40401 |
| adminCreateAdjustment | 【提交并生效】、红冲提交（都是一步提交并批准） | 短信档 token 缺失或为动态码档被拒（BR-ID-34）；关联单据为空、RESTORE 不可人工选（20001）；同一原单第二次红冲被拒（码待契约线定，BR-FUND-24 细则） |
| adminApproveAdjustment | 【批准并短信验证】 | 同上；状态已变 |
| adminRejectAdjustment | 驳回系统预填单（必填原因） | 20001；状态已变 |
| adminListBadDebtWriteoffs / adminApproveBadDebtWriteoff | 核销页签 / 批准 | 有未完结提现单被拒（BR-FUND-12）；余额回正时的处理按 BR-FUND-12；短信档 |

## 5. 权限点与开关（04 §11.2）

`fund.adjust`（新建并提交生效、批准系统预填单、红冲，短信档；驳回不需二次验证，BR-FUND-24 细则）；`fund.writeoff`（批准核销，短信档）；`fund.view`（只读）。未登记验证手机号的账号发起时提示先登记（BR-ID-34 细则）。

## 6. 稿上没画、实现要做的

金额输入按后台金额规则（整数分传输，BR-TEXT-10）；原因码为 OTHER 且无关联单据时原因说明必填并提示；提交中禁用提交按钮；成功后 message 含新单号并刷新列表与用户详情余额；已红冲行的【红冲】隐藏并显示链接到红冲单；核销拦截态按钮禁用且说明可聚焦；1280 以下抽屉全宽。

## 7. 待定与不一致

- 决定 ②（负责人 2026-10-18）：人工发起的调账单（含红冲单）一律一步提交并生效，不再提供【保存待批】与【撤回】；待批列表只留系统预填的 ACCOUNT_CLOSED 单（批准或驳回）。写在 BR-FUND-24 正文 ① 与细则「后台入口」。画板 AdmAdjust / AdmAdjustReverse 的【保存待批】按钮、列表里的【撤回】与人工发起的「待批」样例行（ADJ20261008003）为定稿前写法，本期不渲染、不作依据；画板待改。
- 画板状态名「待批」与 BR-TEXT-25「待批准」不一致：实现按 BR-TEXT-25，画板待改。
- 画板核销拦截态写了配置键名与默认值：以 BR-FUND-12 与 08 §14.6 决-11 登记为准，前端不写死。
- 重复红冲的接口拒绝码待契约线定（BR-FUND-24 细则，规划/06「2026-10-05 设计审查待确认」）。
- 调账原因码后台中文名契约线补行后，画板与前端同步取字典。
