# AI 助手 AgentChat · 查订单与查收益（App 原生）

- 核对版本：规划提交 32a9765（负责人 2026-10-21 定稿 App 内高保真第 2 批，`docs/changes/20261021-App内高保真第2批定稿.md`）；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-money/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 2 批定稿」
- 路由：`AgentChat`（native，auth none，参数可选 `context`，入口 in_app / push）；本规格只管查订单（`order_status`、`claim_draft`、`handoff`、`auth_required`）与查收益（`earnings_summary`）两类回答，页面外壳、找货与页面引导卡见第 1 批与第 3 批规格；去哪：`OrderDetail`（查看订单）、`Login` / `BindPhone`、`Wallet` / `WithdrawRecords`（收益卡按钮）、`FindOrder`（找回记录）、企业微信客服
- 需求：01 F-AGENT-06、F-AGENT-21；规则只引编号：BR-AI-01（主体过滤、prefill_claim、细则「收益查询」）、BR-AI-04、BR-AI-07（explain_order 判定、条数上限）、BR-AI-19、BR-TEXT-22、BR-TEXT-16、BR-ATTR-17（找回第二因子）、BR-TEXT-02 细则「订单的检索范围与分享单的投影」；验收：AC-AGENT-06 / 21（同号）、10 AC-S1-106、AC-S1-148、AC-S1-149、AC-S1-150、AC-S1-151、AC-S1-152、AC-S1-156；任务：05 APP-10 / HM-08（契约 CT-08）
- 可参考的已合并页面：无（原生仓库不在本次核对范围；流样例 `contracts/fixtures/agent-streams/normal-earnings.ndjson`、`normal-earnings-history.ndjson`）
- 是否资金或归属页面：是（只读展示订单与收益；找回提交为用户点击的写操作）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 查订单进度 | AgentOrderAnswer-v2.dc.html（9ded17321bfb） | 已绑手机本人问订单；文本为服务端模板句，结论只在卡上；张数上限按 BR-AI-07 | sendAgentMessage · `order_status` 卡（无命名流样例） |
| 要先登录、要先绑手机 | AgentOrderNeedLogin.dc.html（fa0f2c4a8d96）、AgentOrderNeedPhone.dc.html（c821e4bbea7a） | 游客；已登录未绑手机（问收益同版式换文本） | `auth_required`（reason=login / bind_phone，resume_link_id 为空） |
| 按订单号查不到 | AgentOrderNotFound.dc.html（9f9df0dc89e9） | explain_order 返回 NOT_TRACKED（几种情形卡与文本相同） | `claim_draft` 卡；提交走 createOrderClaim |
| 0 笔订单 | AgentOrderEmpty.dc.html（66a26bead3e4） | list_my_orders 0 笔 | `handoff` 卡 |
| 查收益 | AgentEarningsCard.dc.html（3e83207f3de9） | 已绑手机本人问余额、预估、提现进度 | sendAgentMessage · `earnings_summary`（流样例 normal-earnings） |
| 历史对话里的收益卡 | AgentEarningsHistory.dc.html（4932706c6e6e） | 重新打开之前的对话；不显示任何金额 | listAgentSessionMessages（流样例 normal-earnings-history） |
| 深色 | AgentOrderAnswerDark.dc.html（34438e4dc694）、AgentEarningsCardDark.dc.html（ddfa7ca2462b） | 系统深色（00 D35） | 同查订单、查收益 |
| 收益查询失败、按单号查询超限 | 不适用（无画板；只有文本，不出卡） | — | `agent.earnings.unavailable`、`agent.order.lookup_limited` |

画板上的订单、金额与时点（10-12 10:03）为样例；顶部「使用模型」一行沿用第 1 批写法（第 7 节）。

## 2. 组件

| 区域 | 组件 | 数据（卡片字段，04 §8.3） | 交互 |
| --- | --- | --- | --- |
| 订单卡 | `PlatformBadge`（14px）+ 标题（好友买的其他商品显示 `order_list.other_product`）+ 状态 + 原因 + 预估返 + 预计结算月份；不放订单号、实付、件数、时间、商品图 | order_id、platform、title、is_other_product、display_status、reason、est_rebate_fen、expected_credit_period | 【查看订单】进 `OrderDetail`，返回回到对话 |
| 登录 / 绑手机卡、找回草稿卡、客服卡 | 同一「图标 + 标题 + 按钮」卡片版式 | reason；platform、order_no、click_times[]；entry、summary | 登录先登记 `pending_action`；客服打开企业微信 |
| 找回草稿卡 | 回显平台、订单号、本人最近打开该平台的时间 + 用户自选「付款日期」+【提交找回】 | 见左 | 用户点了才提交；结果承接同找回页（成功与 30205 打开找回记录，30203 / RISK_BLOCKED / 30206 置灰，30201 / 30202.* / 30204 显示在对应输入下） |
| 收益卡 | 两列 `AmountGrid`（可提现、预估收益 + 最早预计月份或「入账核对中」）+ 最近一笔提现（状态标题 + 申请金额）+「更新于 hh:mm」+ 并排两个次按钮 | as_of、withdrawable_fen、estimated_total_fen、next_credit_period、credit_overdue、latest_withdrawal{title_key, amount_fen} | 【去钱包】【看提现记录】点了才打开、不带参数；本机金额隐藏时显示「****」；不写本机缓存 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 查订单文本 | `order_status.<display_status>.summary`、`order_reason.NOT_TRACKED.summary`、`order_list.summary`、`order_list.empty`、`agent.notice.more_orders`、`agent.order.lookup_limited` |
| 要先登录 / 绑手机 | `agent.need_login`、`agent.need_phone`、`agent.earnings.need_login`、`agent.earnings.need_phone` |
| 收益卡 | `agent.earnings.summary` / `.history` / `.fallback` / `.unavailable` / `.applied_amount` / `.open_wallet` / `.open_records` |
| 找回草稿卡 | `claim.guide.paid_date`、`claim.guide.caution`、`error.302xx`（同找回页） |
| 客服、外壳 | `cs.wechat_unavailable`；`ai_label`、`agent.disclaimer.commission`、`clipboard.paste_hint.agent`（第 1 批外壳） |
| 卡片标题等其余文字 | 08 无键（第 7 节） |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| sendAgentMessage（SSE） | 发出问题 | 30501、10001、10005、10004、30504、20001、30506、30502、50302、42901、50001、50401、10405 |
| listAgentSessionMessages / getCurrentAgentSession | 重新打开对话 | 30501、10001、10005、10004、30504 |
| createOrderClaim | 找回草稿卡【提交找回】 | 20001、30201～30206、10405 |

## 5. 权限点与开关

`agent.tools.get_my_earnings.enabled`（off 时不出收益卡，问收益改出页面引导卡，04 §10.2）；`claims.enabled`（30206）。

## 6. 稿上没画、实现要做的

金额隐藏同时覆盖读屏名称；历史重载、金额隐藏、查询失败分别验收；卡片按钮命中区 ≥ 44；卡片与 fallback_text 的旧客户端回退（03 §7.4）。

## 7. 待定与不一致

- 待上游（契约线，04 §8.3 / 03 §7.4）：找回接口必填付款日期（BR-ATTR-17），`claim_draft` 卡没有付款日期字段，`submit_action` 怎样带上用户选的 paid_date 未定义；`FindOrder` 路由 params 为空对象，「打开找回记录并定位这条申请」无法带上 claim_id。
- 待上游（08 BR-TEXT-14 / BR-TEXT-22 补键）：收益卡「最近一笔提现」；auth_required 卡标题「登录后查订单」「绑定手机号后查订单」；找回草稿卡标题「找回这笔订单」、打开时间一行与「付款日期」输入；客服卡说明句。
- 待上游（编排，BR-TEXT-16）：顶部「使用模型：通义千问（阿里云百炼）」是登记后的示例，登记前应为「内测模型」；两批画板写法一致，稿上改不改由编排定。
- 待上游（契约线）：`agent.earnings.*`、`clipboard.paste_hint.agent` 已在 08，`contracts/texts.default.json` 尚未收录。
