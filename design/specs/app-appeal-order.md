# 订单申诉 Appeal（订单申诉部分，App 原生）

- 核对版本：规划提交 32a9765（负责人 2026-10-21 定稿 App 内高保真第 2 批，`docs/changes/20261021-App内高保真第2批定稿.md`）；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-money/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 2 批定稿」
- 路由：`Appeal`（native，auth login，入口 in_app / push）；本规格只管 target_type=order 的提交与进度，账户申诉（封禁 / 冻结）在第 3 批规格；从哪来：订单详情 BLACKLIST 原因的【去申诉】、维持后的【再次申诉】、APPEAL_RESULT 站内信；去哪：回 `OrderDetail`、企业微信客服
- 需求：01 F-ORD-12、F-RISK-04；规则只引编号：BR-ID-36（谁能申诉、同一对象只有一条处理中、维持后再申诉与次数）、BR-ATTR-26、BR-TEXT-23 细则（不显示处理时限、APPEAL_RESULT）、BR-TEXT-11；验收：AC-ORD-12（同号）、10 AC-S1-48-TB；任务：05 APP-12（申诉页）与 APP-08（订单详情入口）/ HM-08、HM-06
- 可参考的已合并页面：无（原生仓库不在本次核对范围）
- 是否资金或归属页面：否（只标记该订单申诉中，不改账户状态、不改返利）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 提交 | AppealOrder.dc.html（7cca26488329） | 从订单详情进入，该订单无处理中的申诉 | getOrder（申诉对象摘要：订单号、状态、原因） |
| 处理中 | AppealProgressOrder-v2.dc.html（a3f271827ce7） | 提交成功后，或该订单已有处理中的申诉 | listAppeals · 200 · example（target_type=order 的那条） |
| 提交中、校验不过 | 不适用（无画板） | 提交在途；说明为空等 | 本地；20001 |
| 结果（已通过 / 维持） | 不在本页出稿：显示在订单详情（OrderDetailAppealRevoked-v2 等，见 `app-order-detail.md`）与站内信 | 结案后 | APPEAL_RESULT |
| 深色 | 无深色稿（按令牌推导，00 D35） | — | — |

画板上的订单号、时间与申诉说明为样例。

## 2. 组件

| 区域 | 组件 | 数据（接口字段） | 交互 |
| --- | --- | --- | --- |
| 申诉对象 | 只读信息行（类型、订单号、当前状态、原因） | order_no、display_status、reason | — |
| 申诉说明 | 多行输入 | content | 必填与长度按契约 `SubmitAppealRequest` |
| 提示 | 说明文字 | — | 不显示处理时限或截止时刻（BR-TEXT-23 细则） |
| 提交 | 主按钮【提交申诉】 | target_type=order、target_id=order_id | 成功后显示处理中；重复提交返回原申诉、不新建（BR-ID-36） |
| 进度 | 时间线（已提交 → 处理中 → 处理结果） | created_at、status、closed_at | 时间格式按 BR-TEXT-11；「联系客服」打开企业微信客服（`/v1/config.kf`） |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 原因 | `order_reason.BLACKLIST.title`（BR-TEXT-05） |
| 页面说明句、进度说明句 | 08 无键（画板措辞，第 7 节） |
| 提交失败 | `error.20001`、`error.30701`、`error.10405` |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getOrder | 进页取申诉对象摘要 | 30701 |
| submitAppeal | 【提交申诉】（target_type=order） | 20001、30701、10405 |
| listAppeals | 进页判断有无处理中的申诉、看进度 | 无业务码 |

## 5. 权限点与开关

无本页开关；能否申诉由服务端按 BR-ID-36 判定（订单级，不看账户 risk_state）。

## 6. 稿上没画、实现要做的

提交中按钮态与失败重试；输入框键盘弹起与字数提示；子页面结果回传给订单详情（BR-ID-10 细则「子页面结果回传」）；读屏顺序与错误提示关联输入框。

## 7. 待定与不一致

- 待上游（08 BR-TEXT-14 补键）：AppealOrder、AppealProgressOrder-v2 的说明句为画板措辞，无字典键。
- 待上游（契约线）：同一订单申诉次数用完后再提交时 submitAppeal 的返回码未列入 x-error-codes（BR-ID-36 细则「维持后再申诉」）。
- 待上游（契约线）：`Appeal` 路由同时承载账户申诉与订单申诉，`routes.json` 的 params 为空对象，从订单详情进入时怎样带上是哪一笔订单（target_type、order_id）未定义。
