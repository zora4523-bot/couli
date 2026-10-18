# 余额流水查询与导出记录 ledger / exports（管理后台）

- 核对版本：规划提交 8c91f67（负责人 2026-10-18 后台第 2 批定稿「全部按推荐」，`docs/changes/20261018-后台第2批定稿.md`）；代码主干 2fdbf110（rebate-platform 远端 main，2026-10-18 核对，尚无后台财务契约；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（PNG 在 `review-admin/png/`），不入公开仓库；完整 sha256 登记在 [design/README.md](../README.md) 第 15 项「管理后台第 2 批」
- 路由：后台资源 `ledger`（菜单「资金 / 余额流水」）、`exports`（导出记录，各列表页【导出记录】共用入口，04 §6.6 `exports`）；从哪来：侧栏、用户详情「余额与流水」页签、调账 / 核销成功条【查看凭证】、各列表页【导出记录】；去哪：用户详情、关联单据（提现单、调账单、订单）
- 需求：01 F-ADM-08（余额流水查询与导出）、F-ADM-03（导出任务）；规则只引编号：BR-FUND-13（单一余额与子户）、BR-FUND-14（冻结与已提现变动）、BR-FUND-15（流水类型与映射）、BR-FUND-16（凭证）、BR-TEXT-19（用户侧流水名，仅对照）、BR-ID-34 细则「后台导出任务」（异步、签名链接有效期、重试与取消、脱敏）、BR-ID-30（留存）；验收：AC-ADM-08、10 AC-S2-111、AC-S2-59、AC-S2-33、AC-S1-157；任务：05 F1-08g（流水与导出）、F1-07g（用户详情页签复用）
- 可参考的已合并页面：`apps/admin/src/pages/admins/**`
- 是否资金或归属页面：否（只读查询与导出；导出受 `pii.*` 脱敏）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 流水查询（按 UID 命中） | AdmLedger.dc.html（a569ebb9f83d） | 持 `fund.view` 并填 UID 查询 | adminListLedgerEntries · 200 · example；用户摘要 adminGetUserFundSummary |
| 导出记录 | AdmExportTasks.dc.html（089779a6f3b9） | 任一列表页点【导出记录】 | adminListExports · 200 · example（含排队中 / 生成中 / 已完成 / 失败 / 已过期 / 已取消各一行） |
| 空 / 加载中 / 出错 | 不适用（无画板；按三态写法；未填 UID 时提示先输入） | — | 本地 |
| 无权限 | 不适用 | 无 `fund.view`（流水）/ 无 `export`（导出记录） | 菜单隐藏；10403 |

画板上的 UID、金额、凭证号、订单号、导出任务号、文件名与「query.xiaoli」均为样例。

## 2. 组件（03 §9.1 antd）

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 标题行 | Title + Button【导出当前筛选】（`export`）【导出记录】 | — | 导出创建成功 message「已创建导出任务 EX…，到导出记录下载」（review-log 转开发项） |
| 筛选 | Form：Input UID（必填）、Select（流水类型 `ledger_type`、子类型 `sub_type`、子户 available / frozen）、RangePicker 记账日期、Input 关联单号 +【重置】【查询】 | 查询参数 | 未填 UID 不发请求 |
| 用户摘要 | Card + Statistic：可用余额、冻结中、负余额起始日、已提现累计 + 链接【查看用户详情】 | BR-FUND-18 汇总字段 | — |
| 流水列表 | Table：记账时间、UID、流水类型、子类型、子户、金额（正负）、变动后余额、关联单据（链接）、凭证号 | `ledger_entries`、`ledger_vouchers.uniq_key` | 同一凭证的多条分录相邻显示 |
| 导出记录说明 | Alert：异步生成、链接有效期、重试 / 不可取消 / 账号停用自动取消、可见范围、脱敏（文字按 BR-ID-34 细则，不写死时长） | — | — |
| 导出记录筛选 | Tabs + Badge（全部 / 生成中 / 排队中 / 已完成 / 失败 / 已过期 / 已取消）+ Form：Select 来源页面、RangePicker 发起时间 | `export_status`、来源页面枚举 | — |
| 导出记录列表 | Table：任务号、来源页面 · 导出内容（筛选摘要）、数据（脱敏 / —）、发起（人、时间）、状态（含进度或原因）、文件 / 结果（文件名、行数、有效期）、操作【下载】【重试】【重新导出】 | `exports` | 下载每次写审计；已完成 / 已过期 / 已取消不可重试 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 导出状态 | BR-TEXT-25 `admin_dict.export_status.*`（已有行直接用） |
| 流水类型、子类型后台中文名 | BR-TEXT-25 无行，契约线补（按 BR-FUND-15 的 `ledger_type` / `sub_type` 编码）；画板名为示意；用户侧名另按 BR-TEXT-19，不混用 |
| 子户（可用 / 冻结） | BR-FUND-13；中文名契约线补 |
| 导出来源页面 | 04 §6.6 `exports` 的来源枚举，中文名契约线补 |
| 金额、时间 | BR-TEXT-10、BR-TEXT-11 |
| 错误提示 | BR-TEXT-14（10403、20001、40401） |
| 其余（导出说明、页脚说明） | 08 无键，用画板文案，登记 admin.ledger.* / admin.exports.* |

## 4. 接口（operationId 为暂拟，由 CT-24 `ledger` / `exports` 分配）

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| adminListLedgerEntries | 查询、切页、重试 | 10001、10403、20001（UID 缺失或格式） |
| adminGetUserFundSummary | 查询命中后 | 40401 |
| adminCreateExport | 【导出当前筛选】 | 10403 |
| adminListExports | 进入导出记录、切页签、筛选 | 10403 |
| adminGetExportDownloadUrl | 【下载】 | 已过期 / 已取消（按 `contracts/error-codes.yaml`）；每次写审计 |
| adminRetryExport | 【重试】【重新导出】 | 状态不允许重试 |

## 5. 权限点与开关（04 §11.1）

`fund.view`（单个用户流水）；`export`（导出与导出记录）；`pii.reveal_phone` / `pii.reveal_identity`（未勾选时导出脱敏值）；`audit.view_all`（看全部账号的导出任务，否则只看本人）。本页无写操作，不需二次验证。

## 6. 稿上没画、实现要做的

导出记录中「生成中」行轮询进度；【下载】打开签名链接而不是前端拼接；筛选摘要截断加 Tooltip；金额正负用符号与文字（不只靠颜色）；表格列头有排序的标 `aria-sort`；1280 以下流水表横向滚动，记账时间与金额固定。

## 7. 待定与不一致

- 流水类型、子类型、子户、导出来源页面的后台中文名不在 BR-TEXT-25：契约线补行；画板名为示意。
- 导出链接有效期、重试规则等取值只在 BR-ID-34 细则「后台导出任务」维护；画板说明条写了具体时长，实现从配置或字典取，不写死。
- 导出记录页同时服务第 1 批（用户 / 订单 / 操作日志）与本批页面，本批登记于此；来源页面枚举由契约线随 `exports` 定。
