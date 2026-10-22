# 订单详情 orders/{id}（管理后台）

- 核对版本：规划提交 408f6d3（负责人 2026-10-18 后台第 1 批定稿「全部按推荐」，`docs/changes/20261018-后台第1批定稿.md`；含 #136：已归属订单不提供改给他人，04 §6.6 `orders/{id}/reassign` 只接受未归因）；代码主干 16b6f5aa（rebate-platform 远端 main，2026-10-18 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（PNG 在 `review-admin/png/`），不入公开仓库；完整 sha256 登记在 [design/README.md](../README.md) 第 15 项「管理后台第 1 批」
- 路由：后台资源 `orders/{id}`；从哪来：订单查询、一框搜、用户详情订单页签、找回审核；去哪：用户详情（UID）、同步记录、对账与差错（恢复流程）
- 需求：01 F-ADM-05；规则只引编号：BR-FUND-01 细则「订单锁定（展示标记）」、BR-ATTR-20（找回通过、未归因订单指派与锁定）、BR-ATTR-31（未归因订单的后台指派，2026-10-21 自 BR-ATTR-20 拆出）、BR-FUND-06（hold）；验收：AC-ADM-05（同号规则）、10 AC-S2-59、AC-S1-157；任务：05 F1-07e
- 可参考的已合并页面：无
- 是否资金或归属页面：是（指定归属、暂停结算）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 正常（已归属 · 预估） | AdmOrderDetail.dc.html（53283883bcc3） | 打开详情 | adminGetOrder · 200 · example |
| 各状态的按钮区 | AdmOrderActionStates.dc.html（3632a1493439） | 设计说明稿：8 种状态一行一种 | — |
| 暂停结算 / 已暂停 / 恢复结算 | AdmOrderSettleHold（243fce26daf1）/ HoldDone（9e51e2ce7c63）/ Resume（8974196755fd） | 点【暂停结算】【恢复结算】 | orders/{id}/hold、unhold；实现用详情内的 Popconfirm / 内嵌表单承载同样字段（F-ADM-05「合并进标记」，Codex 第 1 轮 #10），画板只作字段与后果说明 |
| 指定归属（未归因）：抽屉 / 确认（已付款、已收货）/ 成功 | AdmOrderAssignUnattributed（fa1ac7750b55）/ …Confirm（802e589c64ca）/ …ConfirmReceived（60f77ba3186a）/ …Done（ed47cdb2c6b8） | `user_id` 为空时点【指定归属】 | orders/{id}/reassign（expected_user_id 空、expected_locked）· 20902 时提示已变更 |
| 1280 窄窗 | AdmAdaptOrderDetail1280.dc.html（87dc95eb0801） | 视口 ≤ 1280 | 本地 |
| 加载中 / 出错 / 不存在 | 不适用（无画板） | 在途 / 5xx / 20001（订单不存在） | 本地：Skeleton、Result |
| 无权限 | AdmOrderActionStates 末行 | 无 order.hold / order.assign | 按钮隐藏；服务端 10403 |

画板上的订单号、商品、金额、分佣快照数字与 UID 均为样例数据；「天猫 / 淘宝」只以文字标识来源，无平台商标图形。

## 2. 组件（03 §9.1 antd）

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 标题行 | Title + 订单号（可复制）+ 平台 + 按钮组【同步此单】【暂停结算 / 恢复结算】【指定归属】 | sub_order_id、platform、user_id、rebate_status、locked、hold | 【指定归属】的显示条件按 BR-ATTR-31，【暂停结算】的可用条件按 BR-FUND-06；置灰时 `aria-describedby` 写原因 |
| 权限说明行 | Typography.Text（12px） | — | 固定文案：order.view / order.hold / order.assign（只对未归因） |
| 状态卡 | Descriptions：平台状态、返利状态、用户侧显示、暂停 / 维权、订单锁定、归属锁定 | platform_status、rebate_status、display_status、hold、rights、locked、attribution_locked | 「已锁定」与「归属已锁定」可同时出现，并列显示 |
| 基本信息 / 归属信息 / 分佣快照 / 状态历史 / 原始报文 | Card + Descriptions + Timeline + 折叠 JSON | 契约字段 | 【查看金额变更记录】【展开全部】 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 平台状态 / 返利状态 / 暂停原因中文名（双列，BR-TEXT-18） | BR-TEXT-25 `admin_dict.platform_status.*`、`admin_dict.rebate_status.*`、`admin_dict.hold_reason.*`（契约线补行） |
| 错误、step-up、无权限提示 | BR-TEXT-14（10003、10403、20902 按 `contracts/error-codes.yaml`） |
| 其余（卡标题、按钮、置灰原因、权限说明行） | 08 无键，用画板文案，登记 admin.order_detail.* |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| adminGetOrder | 进入、操作后刷新 | 10001、10403、20001（`data.fields=[order_id]`：订单不存在，契约不设 404；2026-10-22 由 40401 改） |
| adminHoldOrder / adminUnholdOrder | 暂停 / 恢复提交 | 20902（`data.resource=order`：不在预估 / 待结算（BR-FUND-01 表外事件）；已暂停再暂停、未暂停时恢复（同状态，不算表外事件）；系统因未映射状态暂停（UNMAPPED_STATUS）而待处理记录未关闭时恢复（编排裁定 D10-155，详情的 `unmapped_pending_open` 为 true 时【恢复结算】置灰）；版本已变。暂停后订单被作废的，暂停标记保留、不提供恢复（编排裁定 D10-157）。2026-10-22 由 20001 改）、20001（原因码不合法；暂停时推不出原因码而没选、或所选与推导不符，原因码按所持权限推导、推不出由操作人在 RISK / CS 中选，编排裁定 D10-152 ②；恢复时原因码必填，D10-152 ①）、10403 |
| adminReassignOrder | 指定归属提交（step-up 动态码） | 10003、20902（order_attribution 已变更）、目标用户封禁、注销中或已注销（同一拒绝码，带 `data.reason` 区分；码待契约线，编排裁定 D10-152 ③）、20001（目标用户不存在、原因不合规） |
| adminCreateOrderSync | 【同步此单】 | 10403、20001；站长授权暂停期间另有拒绝码（码待契约线按 08 §13.11 分配，2026-10-22） |

## 5. 权限点与开关（04 §11.1 / §11.2）

`order.view`；`order.hold`；`order.assign`（step-up 档位与适用范围按 04 §11.2 与 BR-ATTR-31；负责人 2026-10-18 #136，第 1 批定稿 ③ 维持）。

## 6. 稿上没画、实现要做的

加载中 / 出错 / 订单不存在（20001）；置灰按钮的原因文字在 1280 不换行到按钮下；状态历史只追加；读屏：按钮名带订单号；抽屉关闭后焦点回【指定归属】。

## 7. 待定与不一致

- 2026-10-22 摘要同步（`docs/changes/20261022-后台风控联盟订单接口形状.md`）：§1、§4、§6 的订单不存在由 40401 改为 20001（契约没有 40401），暂停 / 恢复被拒由 20001 改为 20902（08 BR-FUND-01、BR-FUND-06 细则为准）；adminCreateOrderSync（【同步此单】）由「10403」补为「10403、20001」与站长授权暂停期间的拒绝（码待契约线，couli #176 r1 去掉原写的 50301）；couli #176 r2 起 §4 按编排裁定 D10-152 ①②③、D10-155、D10-157 补写暂停 / 恢复与指定归属的被拒情形；画板不变。
- 封存稿 removed/AdmOrderReassign*（改派）不实现；「作废后误判只能驳回重提找回」已按 #136 处理，负责人 2026-10-18 第 1 批定稿维持；若要给超管留纠错通道需改 BR-ATTR-31（属负责人决定）。
- 目标用户为封禁、注销中或已注销账号时的拒绝码（带 `data.reason` 区分三种）待契约线（编排裁定 D10-152 ③）。
