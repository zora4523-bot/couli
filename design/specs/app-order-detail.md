# 订单详情 OrderDetail（App 原生）

- 核对版本：规划提交 32a9765（负责人 2026-10-21 定稿 App 内高保真第 2 批，`docs/changes/20261021-App内高保真第2批定稿.md`）；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-money/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 2 批定稿」
- 路由：`OrderDetail`（native，auth login，参数 `order_id` 必填，入口 in_app / push）；从哪来：订单列表、余额流水、Agent 订单卡【查看订单】、推送；去哪：`ProductDetail`（查看商品）、`FindOrder` / `Appeal`（原因码动作）、`Ledger`（查看流水）、`AgentChat`（问问 AI，带订单 context）、企业微信客服
- 需求：01 F-ORD-07、F-ORD-11、F-ORD-12、F-ORD-16；规则只引编号：BR-TEXT-02（映射表、时间线、未知编码）、BR-TEXT-03（差额行、比价）、BR-TEXT-04、BR-TEXT-05（原因码字典、未知状态下不显示写动作按钮）、BR-FUND-17、BR-ID-36（订单申诉）、BR-TEXT-23（APPEAL_RESULT）、BR-TEXT-24；验收：AC-ORD-07 / 11 / 12 / 16（同号）、10 AC-S1-27、AC-S1-29-TB、AC-S1-48-TB、AC-S1-104、AC-S2-02～06、AC-S2-09、AC-S2-12-TB；任务：05 APP-08 / HM-06
- 可参考的已合并页面：无（原生仓库不在本次核对范围；组件按 03 §10.2）
- 是否资金或归属页面：是（展示返利与归属，不写）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 已收货，等待联盟结算 | OrderDetailEstimated-v2.dc.html（a15fa064d12c） | display_status=WAITING | getOrder · 200 · example |
| 已结算、部分扣回 | OrderDetailSettled-v2.dc.html（d2a89981fd3d）、OrderDetailPartClawed-v2.dc.html（f430a33b1300） | CREDITED、CREDITED_PART_CLAWED | getOrder |
| 已失效（原因直接显示） | OrderDetailNoRebate-v2.dc.html（5e5321b5e441） | INVALID，按 reason | getOrder |
| 已失效·未通过安全校验 | OrderDetailBlacklist-v2.dc.html（b6adbd7d4fd9） | INVALID，reason=BLACKLIST，按钮来自 reason_action | getOrder |
| 预售已付定金 | OrderDetailPresale-v2.dc.html（98880476cb0e） | DEPOSIT_PAID；时间线首节点 deposit_paid | getOrder |
| 售后处理中 | OrderDetailRightsPending-v2.dc.html（8f5501159c79） | RIGHTS_PENDING | getOrder |
| 入账核对中 | OrderDetailReviewing-v2.dc.html（4139226928a5） | REVIEWING；CREDITING（平台入账开关关闭或 credit_overdue） | getOrder |
| 已扣回 | OrderDetailClawedBack-v2.dc.html（35458ec45b74） | CLAWED_BACK | getOrder |
| 分享单（好友买的其他商品） | OrderDetailShare-v2.dc.html（456e329d2c90） | is_other_product=true（无标题、图片、product_key） | getOrder |
| 比价：本单无返利、风险区间 | OrderDetailPriceCompareNoRebate-v2.dc.html（b180e9a84a72）、OrderDetailPriceCompareRisk-v2.dc.html（d93c597bcd6a） | is_price_compare=true，NO_REBATE / PAID | getOrder（区间见第 7 节） |
| 订单申诉：处理中、已通过、维持、次数用完后维持 | OrderDetailAppealPending-v2.dc.html（3cfe115e446f）、OrderDetailAppealRevoked-v2.dc.html（bbc968b9f653）、OrderDetailAppealUpheld-v2.dc.html（97333d4fd0d6）、OrderDetailAppealUpheldFinal.dc.html（0ce8facfc114） | appeal_pending=true；结果与能否再申诉见第 7 节 | getOrder；结果为站内信 APPEAL_RESULT |
| 状态更新中（未知编码） | OrderDetailUnknown.dc.html（1ff2ff17b09d） | display_status 不在本端枚举 | getOrder；只留查看与【刷新】 |
| 原因码与差额行一览（证据稿） | OrderDetailReasonStates.dc.html（f84ac6bc70bb） | 各失效 / 扣回原因、差额行、结算前部分退款 | getOrder |
| 深色 | OrderDetailDark.dc.html（ad0a35f63420） | 系统深色（00 D35） | 同 WAITING |
| 不存在或不可见 | 不适用 | 不是本人、超出可见范围、不存在 | 30701 |

画板上的订单号、商品、金额与日期均为样例；证据稿金额不进 sample-data 主时间线。

## 2. 组件

| 区域 | 组件 | 数据（接口字段） | 交互 |
| --- | --- | --- | --- |
| 状态区 | 标题 + 说明 + `AmountGrid`（返利或推广收益 / 实付或已付定金） | display_status、est_rebate_fen、actual_fen、clawback_fen、pay_amount_fen、expected_credit_period | 未知编码不显示金额 |
| 原因区「为什么没返利？」 | 原因标题与说明 + 按钮 | reason、reason_action | 按钮只来自 reason_action（去找回、重新授权、去申诉、联系客服）；未知状态一律不显示写动作 |
| 差额行 | 单行 | 见第 7 节 | 比价单附「查看说明」（`help_links.price_compare`） |
| 商品区 | `PlatformBadge`（14px 官方图标）+ 商品图、标题、件数、订单号 | title、image_url、quantity、order_no / masked_order_no、product_key | 【查看商品】只在 product_key 非空；自购单号可复制 |
| 时间线 | 时间线 | timeline[]（未发生节点 at 为空） | 结算后不显示预计月份 |
| 底部 | 【问问 AI】 | order_id | 打开 `AgentChat` 并带订单 context |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 状态标题与说明 | `order_status.<display_status>.label` / `.hint`；未知 `order_status.UNKNOWN` |
| 原因与按钮 | `order_reason.<CODE>.title` / `.desc` / `.action`、`order_reason_sub.<SUB>.desc` |
| 时间线 | `order_timeline.deposit_paid` / `.final_paid`；其余节点键未建（BR-TEXT-12 细则） |
| 比价、查看商品、复制、定金、其他商品 | `order.price_compare.hint`、`no_rebate.price_compare.help`、`order_detail.view_product`、`order_detail.copy.done`、`order_list.deposit_amount`、`order_list.other_product` |
| 申诉结果说明 | BR-TEXT-23 APPEAL_RESULT 各结果原文；【再次申诉】【查看流水】【刷新】无键 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getOrder | 进页、【刷新】、从申诉页或找回页返回 | 30701 |

## 5. 权限点与开关

`credit.enabled.<platform>` 关闭时已收货单按 CREDITING 显示、不写「确认收货后随联盟月度结算入账」（BR-TEXT-04）；`help_links.price_compare` 未配置时不显示「查看说明」。

## 6. 稿上没画、实现要做的

首次遇到未知编码按 03 §4.7 上报一次；读屏顺序（状态 → 金额 → 原因 → 按钮）；金额隐藏同订单列表（实付与定金不隐藏）；大字号（AdaptLargeTextOrderDetail 仍为文字来源标签的旧写法，以本批为准）。

## 7. 待定与不一致

- 待上游（契约线）：getOrder 没有画板所需的几项字段——比价风险的返利区间（PriceCompareRisk）、差额行与首次预估之差用哪两个字段算未写明（现有 est_rebate_fen、actual_fen、clawback_fen、reason）、PUNISH 子原因 `order_reason_sub`、申诉结果与时间及「还能否再申诉」（只有 appeal_pending）。
- 待上游（契约线 / 08 BR-TEXT-14）：申诉次数用完后再提交的返回码与提示文案未分配（BR-ID-36 细则「维持后再申诉」）。
- 待上游（设计文档）：适配证据稿旧写法随证据稿更新时改。
