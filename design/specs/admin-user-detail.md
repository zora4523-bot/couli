# 用户详情 users/{id}（管理后台）

- 核对版本：规划提交 408f6d3（负责人 2026-10-18 后台第 1 批定稿「全部按推荐」，`docs/changes/20261018-后台第1批定稿.md`）；代码主干 16b6f5aa（rebate-platform 远端 main，2026-10-18 核对，后端详情、reveal 已 done；联盟授权、封禁冻结、调等级、改上级、直推名单、编辑会员信息、实名更正、副本导出待契约 / 任务；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（PNG 在 `review-admin/png/`），不入公开仓库；完整 sha256 登记在 [design/README.md](../README.md) 第 15 项「管理后台第 1 批」
- 路由：后台资源 `users/{id}`，六个页签 `?tab=overview|funds|orders|claims|withdrawals|risk`；从哪来：用户查询、一框搜、工作台卡、订单 / 提现详情里的 UID；去哪：调账与核销（调整余额）、余额流水、订单详情、找回审核、提现单详情、风控命中
- 需求：01 F-ADM-04（含 2026-10-18 回写的直推名单、调等级、改上级）；规则只引编号：BR-ID-20 细则（联盟授权）、BR-INV-10、BR-ID-27 / 28、BR-FUND-24 细则「后台入口」；验收：AC-ADM-04（同号规则）、10 AC-S2-59、AC-S2-56（调账）、AC-S1-51-TB（重置授权）、AC-S1-157；任务：05 F1-07c/d、F1-07g
- 可参考的已合并页面：`apps/admin/src/pages/users/**`（若已有详情骨架）；StepUpModal
- 是否资金或归属页面：是（调整余额走调账单；改上级影响归属；联盟授权重置 / 停用）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 概览 | AdmUserDetail.dc.html（617be995aeda） | 打开详情 | adminGetUser · 200 · example |
| 余额与流水 / 订单 / 找回 / 提现 页签 | AdmUserDetailFunds（13bbcdfe3506）/ Orders（99fb8d156049）/ Claims（0bfa17cdabc2）/ Withdrawals（7c60b7911225，空态）/ WithdrawalsList（60717727c39f，有数据） | 切页签 | adminListLedger / adminListOrders / adminListClaims / adminListWithdrawals（带 user_id）· 200 |
| 页签加载中 / 出错 | AdmUserDetailTabStates.dc.html（e1b4965fdc31） | 请求在途 / 失败 | 本地 |
| 风控命中 | AdmUserDetailRisk.dc.html（de99943fd976） | 切页签 | adminListRiskHits（user_id）；画板上的规则编号（R-REG-01、R-ORD-01 / 03、R-WDR-02、R-CLM-01）、处置与阈值均为样例，不是 08 BR-RISK 的取值 |
| 无操作权限 | AdmUserDetailNoPerm.dc.html（3e627744c7b5） | 只有 user.lookup / order.view | 按权限点隐藏六类按钮 |
| 注销处理中 / 已注销 | AdmUserDetailDeleting（d6c327e0c084）/ Deleted（46fe2ba3149c） | `deletion_status ∈ processing / done` | adminGetUser（状态字段） |
| 调等级 | AdmUserLevelChange.dc.html（d000af860f45） | 点【调等级】 | adminChangeUserLevel（step-up 动态码） |
| 改上级（不可改 / 可改） | AdmUserInviterChange（639f2c6e034e）/ ChangeOk（134610f7a9ad） | 点【改上级】；30409 时只显示原因 | adminChangeInviter（30409 / 30401 / 30403） |
| 直推名单 | AdmUserInvitees.dc.html（22b6d035c666） | 点【查看直推名单】 | adminListInvitees · 分页 |
| 调整余额 | AdmUserBalanceAdjust.dc.html（04b54121cb68） | 点【调整余额】 | 同调账单 adminCreateAdjustment（短信档） |
| 联盟授权重置 / 停用 | AdmUserUnionReset（0453f5ec337a）/ AdmUserUnionDisable（13f5bc22b7d6） | 淘宝行【重置授权】；各行【停用返利】 | union-bindings reset / disable / enable |
| 冻结 / 解冻 | AdmUserFreeze（b9037fbe7bb9）/ AdmUserUnfreeze（093f14218510） | 标题行【冻结】【解冻】 | 风控接口（`risk.freeze`） |
| 客服代办入口（实名更正 / 编辑会员信息 / 个人信息副本） | AdmUserRealnameFix（aa337d48e22b）/ AdmUserEdit（4fb9af006f38）/ AdmUserDataExport（a08b538fac72） | 点对应卡 | 对话框本身的规格随各自任务（F-ADM-04 编辑会员信息、BR-ID-06、BR-ID-30），本页只登记入口 |

画板上的 UID、昵称、脱敏手机号 / 身份证、收款账号、余额、上级与直推数均为样例数据，不对应真实用户；平台名只以文字出现，无平台商标图形。

## 2. 组件（03 §9.1 antd）

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 标题行 | Title + UID + Tag（risk_state）+ 按钮组（加入黑名单 / 冻结 / 封禁） | user_id、risk_state、frozen_until | 按权限点显示；注销中 / 已注销不显示按钮 |
| 页签 | Tabs（六个） | — | 切换只换下方内容 |
| 基本信息 | Descriptions（4 列）+ 【查看】（pii.reveal_*）+ 等级旁【调等级】 | 昵称、phone_masked、实名、身份证脱敏、收款账号、邀请码、level、状态、注册方式 / 渠道 / 时间 | 【查看】每次 step-up 并审计 |
| 联盟授权 | Table：平台 / 状态 / 绑定标识 / 授权时间 / 冷却到期 / 操作 | union_bindings[]（淘宝、拼多多、京东各一行） | 淘宝【重置授权】【停用返利】；京东 / 拼多多只有【停用返利】/【恢复返利】；blocked 不显示重置 |
| 上级与直推 | Card + Descriptions +【改上级】【查看直推名单】 | parent_id、bind_source、parent_bound_at、invitee_count | 改上级对话框；直推名单抽屉 |
| 余额 | Card + Statistic +【调整余额】【查看流水】 | available_fen、frozen_fen、negative_since、withdraw_block | 调整余额打开调账抽屉（UID 固定） |
| 风控与名单 | Card | risk_state、hits_30d、blacklist、appeal | 【查看命中记录】切到风控页签 |
| 客服代办 | 三张卡（实名更正 / 编辑会员信息 / 个人信息副本） | — | 各自对话框 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 风控状态、申诉状态、提现状态、找回状态、流水类型中文名 | BR-TEXT-25 `admin_dict.risk_state.*`、`admin_dict.appeal_status.*`、`admin_dict.withdrawal_status.*`、`admin_dict.claim_status.*`、`admin_dict.ledger_type.*` |
| 错误、step-up、无权限提示 | BR-TEXT-14（10003、10403.admin_permission_denied、30409 等按 `contracts/error-codes.yaml`） |
| 其余（卡标题、按钮、对话框说明） | 08 无键，用画板文案，登记 admin.user_detail.* |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| adminGetUser | 进入、操作后刷新 | 10001、10403、40401 |
| adminRevealUser | 【查看】 | 10003（step-up）、10403 |
| adminListLedger / Orders / Claims / Withdrawals / RiskHits | 切页签、切页 | 10403（fund.view 等） |
| adminListInvitees | 直推名单 | 10403 |
| adminChangeUserLevel | 调等级提交 | 10003、20001 |
| adminChangeInviter | 改上级提交 | 30409、30401、30403、10003 |
| adminCreateAdjustment | 调整余额提交 | 10003（短信档）、20001、30416 |
| union-bindings reset / disable / enable | 联盟授权操作 | 10003、20001（非淘宝调 reset，`data.fields=[platform]`） |

## 5. 权限点与开关（04 §11.1 / §11.2）

`user.lookup` / `user.list`（看）；`pii.reveal_phone`、`pii.reveal_identity`（查看，动态码）；`fund.view`（余额、流水、提现页签）；`user.level`、`user.inviter`（动态码）；`fund.adjust`（短信）；`union.binding_reset`（只淘宝）、`union.binding_disable`；`risk.freeze`、`risk.ban`、`risk.blocklist`；`user.realname_fix`、`user.phone_change`、`user.data_export`。短信档按钮在账号未登记验证手机号时置灰并提示（BR-ID-34 细则）。

## 6. 稿上没画、实现要做的

页签内列表的空态按 AdmUserDetailTabStates 的写法；调账抽屉与「调账与核销」页共用组件，只多「UID 固定」与返回页签；改上级在 30409 时按钮仍可点、对话框只给说明；对话框关闭后焦点回触发按钮；读屏：联盟表 `aria-label=联盟授权`，行操作名带平台。

## 7. 待定与不一致

- 调账抽屉原稿余额与概览余额为不同时点的样例，实现以接口为准。
- 直推名单字段按 04 §6.6 `users/{id}/invitees`（不含会员口径字段，BR-INV-23 本期不展示）。
- 注销中 / 已注销保留哪些字段按 BR-ID-28，稿只示意。
- 调等级的升降级条件在 08 BR-INV，稿不显示；接口与错误码待契约线。
- 京东 / 拼多多停用 / 恢复返利的完成态未另画，复用 AdmUserUnionDisable 确认稿，平台分支文案由实现按 BR-ID-20 取（Codex 第 1 轮 #27）。
