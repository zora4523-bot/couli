# 找回审核 claims（管理后台）

- 核对版本：规划提交 408f6d3（负责人 2026-10-18 后台第 1 批定稿「全部按推荐」，`docs/changes/20261018-后台第1批定稿.md`）；代码主干 16b6f5aa（rebate-platform 远端 main，2026-10-18 核对，B1-10a 迁移 todo、无 admin 契约；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（PNG 在 `review-admin/png/`），不入公开仓库；完整 sha256 登记在 [design/README.md](../README.md) 第 15 项「管理后台第 1 批」
- 路由：后台资源 `claims`（菜单「用户与订单 / 找回审核」），审核页 `claims/{id}`；从哪来：侧栏、工作台「待审找回」卡（带状态筛选）、用户详情找回页签；去哪：订单详情、用户详情、导出记录
- 需求：01 F-ADM-06；规则只引编号：BR-ATTR-18（证据视图与审核）、BR-ATTR-20（通过即锁定）；验收：AC-ADM-06（同号规则）、10 AC-S1-26-TB、AC-S1-43、AC-S1-157；任务：05 F1-07f
- 可参考的已合并页面：`apps/admin/src/pages/admins/**`
- 是否资金或归属页面：是（通过即写归属并锁定）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 列表正常 | AdmClaims.dc.html（1c0db82aebe6） | 持 `order.claim` | adminListClaims · 200 · example |
| 列表空 / 加载中 / 出错 | AdmClaimsStates.dc.html（65e5cb768059） | 无结果 / 在途 / 失败 | 同上置空 / 本地 |
| 审核页 | AdmClaimReview.dc.html（6af101e473e5） | 点【审核】 | adminGetClaim · 200；画板上的驳回原因编码为示意，不是 `claim_reject_reason` 的取值 |
| 通过 / 驳回提交中、结果 | 不适用（无画板） | 提交 | adminApproveClaim / adminRejectClaim |
| 无权限 | 不适用 | 无 `order.claim` | 菜单隐藏；10403 |

画板上的找回单号、订单号、UID、证据等级与统计数字均为样例数据。

## 2. 组件（03 §9.1 antd）

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 统计卡 | Statistic ×4（待审核 / 今日新提交 / 今日已通过 / 今日已驳回） | 聚合字段（契约线定） | 本期不实现（F-ADM-06：设计自拟，上线后一月内再定） |
| 筛选卡 | Form：Select（平台、证据等级）、Input（订单号 / 找回单号、用户） | 查询参数 | 查询 / 重置 |
| 状态页签 | Tabs + Badge，一个 `claim_status` 枚举值一个页签，页签名取 `admin_dict.claim_status.*`（画板上的页签名为示意） | `claim_status` 计数 | 切换即筛选 |
| 列表 | Table：找回单号、订单号、平台、用户、付款日期（用户填）、提交时间、证据等级、状态、操作【审核】 | items[] | 进审核页；【一键通过】本期隐藏 |
| 审核页 | 证据视图（用户填写 vs 联盟回传逐项比对）+ 子订单逐个【通过】【驳回】+ 驳回原因 Select（`claim_reject_reason`）+ 说明（通过与驳回都必填、≥ 5 字，按 BR-ATTR-20 ③；通过时提供一键填入「证据核实一致」，2026-10-19）| claim、matches[] | 通过 / 驳回的后果与条件按 BR-ATTR-18、BR-ATTR-20；审核前提示一句（文案登记 admin.claims.*） |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 找回状态中文名 | BR-TEXT-25 `admin_dict.claim_status.*`（已有 6 行） |
| 驳回原因中文名 | BR-TEXT-25 `admin_dict.claim_reject_reason.*`（8 个编码已补，couli #147） |
| 错误、无权限提示 | BR-TEXT-14（10403、20902、20001 按 `contracts/error-codes.yaml`） |
| 其余（页签名、证据视图标签、审核前提示） | 08 无键，用画板文案，登记 admin.claims.* |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| adminListClaims | 进入、筛选、切页签、切页、重试 | 10001、10403、20001 |
| adminGetClaim | 进审核页 | 20001（`data.fields=[claim_id]`，未知 id；后台先例，不用 40401，2026-10-19） |
| adminApproveClaim / adminRejectClaim | 通过 / 驳回 | 20902（`data.resource=claim_item`：另一名客服已先处理该子项，刷新后看结果）、20001（缺说明或驳回缺原因）。订单已被同步或他人归属**不报错**：按 BR-ATTR-20 ② 子项自动结案（申请人本人 → cancelled，否则 → rejected NOT_IN_POOL），提示「订单已被自动归属」（2026-10-19 对齐 08） |

## 5. 权限点与开关（04 §11.2）

`order.claim`（审核，不需二次验证）；`export`。

## 6. 稿上没画、实现要做的

通过后的锁定提示按 BR-ATTR-20（负责人 2026-10-18 第 1 批定稿 ③ 维持，与 #136 一致，不另给撤销入口）；提交中禁用按钮；驳回原因为空不可提交；读屏：行操作名「审核 CL…」。

## 7. 待定与不一致

- 列表【一键通过】与统计卡为设计自拟，本期不做（F-ADM-06、后台缺口审计 §3-21）：实现时隐藏，画板暂留。
- ~~`claim_reject_reason` 编码表未定~~：已补（couli #147，8 个编码）。
- 说明文字的落点（2026-10-19）：写 `claims.reason`（最近一次审核说明，详情页展示）并随每次通过 / 驳回写入审计；子项不加备注列。
