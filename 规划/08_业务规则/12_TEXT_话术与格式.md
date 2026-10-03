# 08 业务规则 · 12. 用户可见话术与格式（BR-TEXT）

返回 [README](README.md)（使用规则、术语表、规则索引）

## 12. 用户可见话术与格式（BR-TEXT）

本节规定：收益术语、订单/提现/流水文案、差额提示、预计结算月份、原因码、通知模板、金额时间格式、禁用词、错误话术、AI 与广告标识、报表金额列口径标注、Agent 固定话术、账号与风控站内信。共 23 条（已确认 10、默认假设 11、待验证 2）。

2026-10-01 晚负责人补充决定（docs/changes/20261001-拍板第二批.md §8）：ADD-06 用户只有一个余额，钱包只显示一组数（可提现余额、待抵扣、冻结中、预估收益、已提现），收入来源（自购返利、分享收益、邀请分佣、好友推广奖励）只在订单、通知与流水中按类型区分（BR-TEXT-01、09、19 已改写）；ADD-07 新增错误码 30416 与注销撤销站内信（BR-TEXT-14、23）；ADD-01 30152 废弃、删除话术行；ADD-02 站长授权过期期间 30101 / 30102 的 data.reason=auth_unavailable 文案（BR-TEXT-14）；ADD-08 该文案改为「淘宝暂时无法下单，请稍后再试」、不给无返利购买按钮（BR-TEXT-14），新增站长告警短信模板 UNION_AUTH_EXPIRING / UNION_AUTH_EXPIRED（BR-TEXT-20）。状态均不变。

订单状态写法：本主题按 BR-FUND-01 双状态书写（platform_status + rebate_status，用户可见状态为服务端按 BR-FUND-17 派生的 display_status）。与 规划/04 单一 order_status 的映射（BR-FUND-01）：DEPOSIT_PAID→(DEPOSIT_PAID, ESTIMATED)，PAID→(PAID, ESTIMATED)，RECEIVED→(RECEIVED, WAITING)，CREDITED→(RECEIVED 或 SETTLED, CREDITED)，SETTLED→(SETTLED, CREDITED 且已补差)，INVALID→(任意, VOID)，CLAWED_BACK→(任意, CLAWED_BACK)；规划/04 的 O1→P1、O2→P2+R2、O3→P3+R4、O4→R6、O5→R7、O6→R5、O7→P4、O8→P4+R10、O9→R8、O10→R9（入账后部分退款改写 CLAWBACK，C-16）、O11→R3。「来源」「取代」中引用的 O 编号是原文档位置，不改。按 C-01 默认处理，已由负责人确认 2026-09-30；不采纳双状态时按上述映射回退。

2026-10-01 用语同步（docs/adr/0001-技术栈基线.md §3，规划/11 §9.1；00 §8 第 ① 类）：BR-TEXT-09 影响面里的事件叫法改为「领域事件」。规则含义、取值与状态均不变。

2026-10-03 功能对照补缺第 1 批（docs/changes/20261003-功能对照补缺.md；「功能对照 G-xx」是该批缺口清单的编号，与 规划/10 §6.1 的 G-xx 不是同一套）：BR-TEXT-14 表 A 新增 20004、50305 两行，表 B 新增 20004.identity_mismatch、30104.credential_invalid，表 C 新增第三方页容器、App 内链接落地页、分享页打开方式与邀请码提醒的文案键。BR-TEXT-14 状态不变。

2026-10-03 功能对照补缺第 2 批（同一变更记录的「第 2 批」，功能对照 G-09～G-21）：逐条改动在各条细则里注「2026-10-03，功能对照 G-xx」，各条状态不变。本批不新增 BR-TEXT 条目。同日按评审补文案键 external_page.download_unsupported，改 10004、claim.guide.window、earnings.metric.credited.hint 等行的说明（变更记录 §2.8）；第 2 轮评审后补 pending_confirm.\* 各键，改表 A 的 10001、10004、10005、30304 行；第 3 轮评审后表 A 加 20903，表 C 加放弃上一笔的各键（pending_confirm.withdraw.abandon、pending_confirm.abandon、pending_confirm.abandon.confirm、pending_confirm.abandoned、pending_confirm.abandon_busy、pending_confirm.already_done）与 pending_confirm.cannot_confirm，删去随本机有效期取消的 pending_confirm.expired（变更记录 §2.8 第 3 轮第 1、2 条）。

2026-10-03 功能对照补缺第 3 批（同一变更记录的「第 3 批」，功能对照 G-22～G-34；同日按评审与编排会话裁定：表 D 加 perm.btn.continue、写明用途键按权限类型映射、权限点标为代理补全的默认假设，BR-TEXT-13 细则补真实数据播报默认不做，变更记录 3.9）：BR-TEXT-13 新增榜单类词「高佣」「收益榜」（G-34，按功能对照 Q-27 默认 A）并补首页公告条不做收益播报的说明（G-33）；BR-TEXT-14 表 A 新增 10405（G-24），表 C 新增未安装微信时的三个键与两个按钮键（G-31）、更新提示的两个按钮键（G-24），新增表 D「隐私与权限文案」（G-25、G-26、G-28，文案由法务定稿）；BR-TEXT-17 细则新增「联盟物料频道」（G-34）。各条状态不变，本批不新增 BR-TEXT 条目。第 2 轮评审后（变更记录 3.10）：表 A 的 10405 行补强更页的次要入口与受限会话，表 C 加强更页的三个次要入口键。第 3 轮评审后（变更记录 3.11）：表 B 加 10403.h5_read_only、10405.no_account；表 A 的 10405 行补 data.min_supported_version 为 null 时的分支。

2026-10-03 功能对照补缺第 4 批（docs/changes/20261003-功能对照补缺.md「第 4 批」，功能对照 G-35～G-65）：逐条改动在各条细则里注「2026-10-03，功能对照 G-xx」，各条状态不变，不新增 BR-TEXT 条目。BR-TEXT-01 细则（不显示累计收益）、BR-TEXT-02 正文影响面与细则（订单分组与查找、订单号显示、查看商品、预售节点与金额）、BR-TEXT-10 细则（金额隐藏）、BR-TEXT-18 细则（累计收益的答复、三个常见问题）、BR-TEXT-20 细则（分享文案不带邀请码）；BR-TEXT-14 表 A 30153 与 50304 两行、表 B 新增 50304.search_disabled、表 C 新增购买加载、百川不可用、授权管理、订单分组与筛选、预售、查看商品、金额隐藏各键；BR-TEXT-22 新增 agent.notice.search_disabled。

### 12.1 规则一览

| 编号 | 规则 | 状态 | 影响面 |
| --- | --- | --- | --- |
| BR-TEXT-01 | **收益术语唯一含义**<br>用户可见文案与客服话术中，下列词只能按本表含义使用（后台与报表口径编码见 BR-TEXT-21）。**结算前一律称「预估」**：「预估返 / 预估返利」指自购返利从商品卡下单前估算、订单付款直到联盟结算并经后台核对入账前的全部阶段（订单 rebate_status ∈ {ESTIMATED, WAITING}，BR-FUND-01；含已收货等待联盟结算、售后中、核对中）；「预估推广收益」指分享单与邀请分佣（直推、间推）同阶段金额；「预估收益」是钱包中全部来源（自购、分享、邀请）结算前的合计（用户只有一个余额，拍板第二批 §8 ADD-06）；三者均不可提现；用户侧不再单列「待入账」金额或状态，不使用「待结算」「结算中」。**联盟结算并经后台核对、按月结批次计入可提现余额后（BR-FUND-04）才用确定表达**：订单侧「已结算」（rebate_status=CREDITED，含部分扣回、已补差），已结算金额自购称「实返」、分享与邀请分佣称「推广收益」，都计入同一可提现余额。「可提现」（钱包标题「可提现余额」）等于 withdrawable_fen = max(available_fen, 0)，available_fen &lt; 0 时负数部分显示为「待抵扣」（negative_fen，BR-FUND-18）；「冻结中」等于 frozen_fen（审核中与打款中提现单的金额）；「已到账」只指提现 withdrawal_status ∈ {PAID_API, PAID_MANUAL}；「已提现」等于已到账提现单申请金额 amount_fen 的累计。「入账」只作动作词（结算金额计入可提现余额，如「售后处理中，入账暂停」、流水「自购返利入账」），不作订单状态名。用户可见文案不得出现「返利到账」「佣金」（含推广佣金、比价佣金、确认收货佣金、结算佣金）。口径与花卷云「预估佣金 / 结算佣金；结算状态 未结 / 已结 / 已失效」一致（对照见细则）。按负责人决定（C-02，变更记录 §3），取代原方案 A。 | 已确认 | dict_items（order_status.&lt;display_status>、withdrawal_status、ledger_type 文案）；GET /v1/wallet/summary 字段按 BR-FUND-18（withdrawable_fen、negative_fen、frozen_fen、estimated_total_fen（预估合计）、estimated_fen、pending_credit_fen、pending_credit_paused_fen、next_credit_period（预计结算月份）、credit_overdue、withdrawn_fen、risk_paused_reason；订单预计结算月份 expected_credit_period 见 BR-FUND-04 ⑪），本条只定文案；Wallet、OrderList、OrderDetail、ProductDetail 页面；推送模板 ORDER_TRACKED / CREDITED；客服话术库；docs/glossary.md；Agent explain_order 话术；specs/banned-words.yaml（BR-TEXT-13：「预估收益」「已结算」移出用户侧禁用词） |
| BR-TEXT-02 | **订单状态用户文案映射**<br>订单列表与详情的状态文案必须由服务端返回的 display_status（子订单粒度；由 BR-FUND-01 的 platform_status、rebate_status 与 hold、rights_pending、金额按 BR-FUND-17 派生表从上到下取第一个匹配项，本条不另定派生顺序）按下表一一映射，文案取自 /v1/dict 的 order_status.&lt;display_status>；rebate_status=UNATTRIBUTED（未归因池，user_id 为空）的订单不得出现在任何用户接口；buy_type=share 的订单只出现在分享者的 scope=share 列表，金额前缀用「预估推广收益 / 推广收益」；直推分佣（REFERRAL）订单不得以订单形式出现在邀请人的任何列表或详情，只在余额流水按 BR-TEXT-19 显示；详情页按钮 = 状态固有按钮 + reason.action 按钮（BR-TEXT-05），最多 2 个，有 reason.action 时它为主按钮；未知状态编码必须显示 order_status.UNKNOWN 文案，不得显示编码原文。 | 默认假设 | dict_items.order_status（按 display_status 编码）；GET /v1/orders、GET /v1/orders/{order_id}（display_status、reason、reason_action、est_rebate_fen、actual_fen、clawback_fen、expected_credit_period、credit_overdue（BR-FUND-04 ⑪，取代 expected_credit_date）、timeline、is_other_product）；Agent order_status 卡片；OrderList、OrderDetail 页面；验收用例 F-ORD-07（每状态 fixture + 三端截图；share 跨商品；按钮组合）；客服话术库；订单列表的状态分组与查找参数（status_group、platform、q、paid_month）、订单号显示格式（order_no / masked_order_no）、详情的 product_key 与「查看商品」、预售单的定金节点与金额（细则，2026-10-03 功能对照 G-60～G-63） |
| BR-TEXT-03 | **订单差额与异常提示**<br>订单金额与首次预估不同、部分退款、维权中、入账延迟、比价风险时，必须在状态文案下按本表叠加提示；差额 = 当前金额 − initial_est_fen（该用户角色在分佣快照生成时（BR-CALC-10）的金额，单位分；首次预估为区间时取上限 rebate_max_fen；找回单以批准时生成的快照为准，BR-FUND-01 R3）；差额行只在 rebate_status=CREDITED（display_status ∈ {CREDITED, CREDITED_PART_CLAWED}）且 \|差额\| ≥ 1 分时显示；rebate_status ∈ {ESTIMATED, WAITING} 只在部分退款时显示「预估返 ¥{initial} → ¥{current}」，其他预估波动不显示差额；维权中、hold、入账延迟由 display_status（RIGHTS_PENDING、REVIEWING、CREDITING）表达，提示文案按本条；差额原因取该子订单最近一次写入的 diff 类 reason_code，无记录时用 SETTLE_DIFF；同时满足多项时按本条优先级；风控 hold 原因不得向用户透出。 | 默认假设 | orders / commission_splits（initial_est_fen、diff_reason_code、refunded_quantity_at_credit）；GET /v1/orders/{order_id}（diff_fen、diff_reason、display_status）；OrderDetail 页面；客服话术库；验收用例：部分退款（入账前 / 后）、比价区间、结算补差、维权中、hold 超期、维权与超期同时满足 fixture |
| BR-TEXT-04 | **预计结算月份口径**<br>入账跟随联盟月结（月结账单日按联盟返回的结算数据生成月结账单、后台确认后批量结算入可提现余额，BR-FUND-04），用户侧不再按「收货日 + wait_days」给出预计入账日期，不得承诺具体入账日期或天数。已收货订单（display_status=WAITING）展示**预计结算月份**「预计 {credit_period} 结算」，不显示确认收货月（例：10 月确认收货、联盟一般次月结算 → 「预计 11 月结算」）：credit_period 取服务端返回的 expected_credit_period（YYYY-MM，预计结算月份；取值、何时为 null 与逾期判断 credit_overdue 只由 BR-FUND-04 ⑪ 维护，本条不写算法），客户端只格式化（同年「11 月」，跨年「2027 年 1 月」）、不得推算；字段为 null 时不显示月份；RIGHTS_PENDING、REVIEWING、CREDITING 不展示月份；商品详情与 display_status=PAID 的订单只显示「确认收货后随联盟月度结算入账」，不得写具体天数或日期（不得出现「15 天」「满 N 天」），入账开关 credit.enabled.&lt;platform>=off 时不展示（BR-FUND-04）；平台未返回可用收货时间的订单不进 WAITING（BR-FUND-02，G-14）。 | 已确认 | GET /v1/orders/{order_id} expected_credit_period、credit_overdue（BR-FUND-04 ⑪，取代 expected_credit_date 的用户侧展示）；Agent order_status 卡片；GET /v1/wallet/summary 预计结算月份（BR-FUND-18）；ProductDetail「确认收货后随联盟月度结算入账」文案（texts，无变量）；验收用例：显示的是结算月份而非收货月（10 月收货 →「预计 11 月结算」）、各 display_status 是否展示月份、字段为 null 时不显示、跨年格式、入账开关关闭时不展示入账时点文案、文案不出现天数与日期（周期取法与逾期用例归 BR-FUND-04）；客服话术 |
| BR-TEXT-05 | **原因码字典与文案**<br>订单 reason 只能取下表编码（规划/ 命名为准），每个编码必须在 dict_items 配置 kind（void / diff / claim）、title、desc、claimable、action；rebate_status ∈ {VOID, CLAWED_BACK}（display_status INVALID、CLAWED_BACK）的订单只能带 void 类原因，金额变化必须带 diff 类原因；claim 类编码（NOT_TRACKED、RELATION_INVALID）不得写入已归因订单的 orders.reason，只用于 explain_order、找回页查询结果；action 取值枚举 CLAIM（找回页）、REAUTH（AuthSheet）、CONTACT_CS（客服会话页）、APPEAL（申诉页），以数组存储，当前每个编码最多 1 个；reason_sub 存在时用 order_reason_sub.&lt;SUB>.desc 替换 desc，显示为「{title}：{sub.desc}」；其他文档的旧编码在同步 / 导入时映射到本表，不得新增同义编码；用户可见文案不得出现「佣金」；每个编码必须有 fixture 与截图。 | 默认假设 | contracts/enums/order_reason.json、contracts/enums/reason_action.json；dict_items.order_reason（kind、title、desc、claimable、action）、dict_items.order_reason_sub；orders.reason、orders.reason_sub；维权导入 rights-imports 映射；OrderDetail、Agent explain_order、找回页；客服话术库；验收用例：每编码 fixture + 截图；claim 类编码不出现在已归因订单 |
| BR-TEXT-06 | **提现状态用户文案**<br>提现记录状态文案必须由 withdrawal_status 按下表映射：PENDING_REVIEW 与 APPROVED 均显示「审核中」；PAYING 显示「打款中」（含结果未知期间）；PAID_API 与 PAID_MANUAL 均显示「已到账」；REJECTED 显示「未通过」且附「余额已退回」与原因；FAILED 显示「打款未成功」且附「余额已退回」与原因，【修改收款账号】入口只对账号类失败码显示（BR-TEXT-08）；「已到账」金额显示 net_fen = amount_fen − fee_fen − tax_fen，由服务端返回；PAID_API 与 PAID_MANUAL 的收款渠道名都取该单 payout_channel_name（支付宝或银行卡，BR-WDR-32；PAID_MANUAL 取人工补录记录），不得固定写「支付宝」。 | 默认假设 | dict_items.withdrawal_status；GET /v1/withdrawals、GET /v1/withdrawals/{id}（net_fen、fee_fen、tax_fen、payout_channel_name、masked_account、fail_action）；Withdraw、WithdrawRecord 页面；推送 WD_SUCCESS / WD_REJECTED / WD_FAILED；客服话术库 |
| BR-TEXT-07 | **提现时效与超时进度**<br>提现时效文案按单据审核方式区分（拍板第二批 OPS-17）：withdrawals.review_mode=auto（自动到账规则组判为自动，BR-WDR-30）的单显示「预计几分钟内到账」；review_mode=manual 或尚未判定的审核中单（PENDING_REVIEW、APPROVED）显示「人工审核，工作日 24 小时内处理，节假日顺延」，「处理」指审核结束（口径见 BR-WDR-26）。提现页提交前不预判单据走向：自动到账总开关（BR-WDR-30，默认关）关闭时只显示人工审核文案，开启后显示「符合条件的提现几分钟内自动到账，其余人工审核，工作日 24 小时内处理」。审核超时的进度推送与站内信使用模板 WD_OVERDUE（只用于 manual 单），文案见细则。超时的触发与去重见 BR-WDR-26（deadline 计算、触发状态、检查间隔、夜间顺延、发送前复查、幂等键均只在该条维护）。 | 已确认 | config: withdraw.sla_text、withdraw.sla_text_auto（新增）；withdrawals.review_mode；推送 / 站内信模板 WD_OVERDUE（新增）；Withdraw 页面；客服话术；验收 AC-S2-20、AC-S2-29 |
| BR-TEXT-08 | **提现驳回与失败原因**<br>REJECTED 的用户原因必须取自字典 withdraw_reject_reason 的编码文案，审核人可另填内部备注 reject_note 但不得展示给用户；FAILED 的用户原因必须由支付宝错误码经映射表 withdraw_fail_reason 转成用户文案，未命中映射时显示兜底文案；withdraw_fail_reason 映射表只决定展示文案，不决定状态：只有 payout 服务维护的明确失败码白名单才能触发 W6→FAILED 与 WITHDRAW_RETURN，白名单以外的码（含 SYSTEM_ERROR、超时、未收录码）一律保持 PAYING，按 W7 查询，24 小时仍未知转人工，禁止置 FAILED 或退回余额；【修改收款账号】入口只对账号类失败码（PAYEE_\*）显示；原因文案不得包含风控规则细节。 | 默认假设 | dict_items.withdraw_reject_reason、withdraw_fail_reason；payout 服务明确失败码白名单（代码常量 + 测试）；withdrawals.reject_reason（改存编码）、withdrawals.fail_code、新增 reject_note（内部）；后台提现审核页（原因下拉）；WithdrawRecord 页面；推送 WD_REJECTED / WD_FAILED、失败短信；验收用例：白名单外错误码不退回余额 |
| BR-TEXT-09 | **交易通知文案模板**<br>交易类通知必须使用下表模板（notify-templates 可改措辞，变量与含义不得改），标题与首句按 BR-TEXT-20 校验；所有金额变量均为 BR-TEXT-10 格式化后的字符串（已含 ¥ 与负号），模板中不得再写 ¥ 或 -；自购与推广（分享、邀请）收入分别使用各自模板，推广用「推广收益」不用「返利」（按收入来源区分，单一余额，拍板第二批 §8 ADD-06）；术语按 BR-TEXT-01（结算前「预估」，结算后「已结算」）。**推送对象**：跟单与收益类通知（ORDER_TRACKED、ORDER_INVALID、CREDITED、CLAWBACK）发给该子订单全部份额 > 0 的受益人：订单归属用户（自购本人或 share 单分享者）、直推上级、间推上级（C-25 负责人决定，拍板第二批 OPS-02 确认；间推上级只在规则版本 indirect_enabled 开启时存在，docs/changes/20261001-间推二级奖励.md；角色与份额见 BR-CALC-04、BR-CALC-05、BR-CALC-24）；发给直推、间推上级的通知只含金额与状态，不含商品标题、图片、SKU、下级昵称、手机号、订单号等任何订单明细或个人信息，也不带失效或扣回原因（同 BR-TEXT-19、BR-TEXT-18 的 J7 隐私要求）。触发：ORDER_TRACKED 在子订单已归因到用户（BR-FUND-01 R2）且 platform_status 首次 ∈ {PAID, RECEIVED, SETTLED} 时触发（含 DEPOSIT_PAID→PAID（P2）、同步即为 PAID、结算先到时补写的 P5），B_est=0（display_status=NO_REBATE）不触发（BR-FUND-17「跟单成功」条件），该受益人份额为 0 时不发给该受益人，每个 (子订单, 受益人, 角色) 最多 1 次，幂等键 {order_key}:{uid}:{role}:TRACKED（order_key 见 BR-FUND-05）；合并窗口为固定窗口，时长取 notify.tracked_merge_window_seconds（当前默认 10 秒，允许 0–60；负责人 2026-10-03 决定跟单通知越快越好、订单同步回来就通知、最好 1 分钟内，取代原 5 分钟窗口，docs/changes/20261003-拍板第三批.md §1）：自用户第 1 个待推事件时刻 t0 起一个窗口，窗口结束时发送（单笔同样只等这一个窗口），窗口内同类事件合并，按自购、分享（share）、邀请（直推 + 间推）三类分别成条，窗口结束后到达的事件开启新窗口；CREDITED 在结算批次完成后发送（BR-FUND-04：同一月结账单一次确认（首批或补充批次）的批次全部执行完，或因开关停止置 PARTIAL 时对已入账部分），统计这次执行写入的 REBATE_CREDIT / SHARE_CREDIT / REFERRAL_CREDIT（含间推流水，类型名以 BR-FUND-15 为准）流水（SETTLE_ADJUST 不计），每用户汇总 1 条，0 笔不发；完成时刻落在免打扰时段（notify.quiet_hours，BR-WATCH-15，当前默认 [22:00, 08:00)）时顺延到免打扰结束后发送，发送时仍按完成时的统计；幂等键 user_id:CREDITED:{settle_run_id}:{part}（settle_run_id 为该次确认的执行编号，part 为第几次执行完成：正常为 1，PARTIAL 后手动继续执行完为 2，依此类推）；找回通过的订单（BR-FUND-01 R3）不发 ORDER_TRACKED，只发 CLAIM_RESULT（上级仍按本条收到邀请类 ORDER_TRACKED）；platform_status=DEPOSIT_PAID 不推送；频控与免打扰见细则（引用 BR-WATCH-15）。**通知分类**（拍板第二批 OPS-16）：本条全部模板与提现类 WD_\* 均属「服务」类：站内信总是写入；推送按用户的「服务」类开关发送，关闭后只写站内信；MVP 通知设置只显示「服务」一个开关。 | 已确认 | messages.yaml / notify-templates（模板标 category=service）；通知设置页（MVP 只显示服务开关）；（新增 ORDER_TRACKED / ORDER_INVALID / CLAWBACK 的邀请类模板）；领域事件 order.created / order.status_changed / order.credited / order.clawed_back / withdrawal.changed / claim.resolved 消费者（按受益人扇出）；推送与站内消息；短信模板（BR-TEXT-20）；验收用例：预售单跟单推送、合并窗口边界（窗口内合并、窗口外另发）、自购 / 分享 / 邀请分条、直推与间推上级各收 1 次且不含商品与下级信息、上级份额为 0 不推、结算批次完成即推、完成时刻在免打扰时段顺延到结束、PARTIAL 与继续执行各推 1 次、找回单不重复推送、金额变量无重复符号 |
| BR-TEXT-10 | **金额格式化**<br>接口金额一律为整数分（_fen），前端用整数运算格式化，不得用浮点：展示为可选负号 + 「¥」 + 元，最多两位小数并去掉末尾 0 与多余小数点；不加千分位；负数用 ASCII「-」置于「¥」前；流水正数加「+」；返利区间在 min &lt; max 时用「–」（U+2013，前后无空格）连接两端，min = max 时显示单值，min = max = 0 时显示「暂无返利」（列表隐藏返利标签）；返利、价格金额由服务端计算，客户端不得自行乘佣金率；服务端渲染推送、短信时使用同一格式化函数，模板变量为格式化后的字符串。 | 已确认 | specs/client-behavior.md 测试向量；PriceTag、RebateTag 组件（iOS / Android / 鸿蒙 / H5）；推送、短信模板渲染（服务端同一格式化函数）；后台金额列 |
| BR-TEXT-11 | **时间与日期格式化**<br>服务端时间字段一律 ISO 8601 带 +08:00，纯日期字段（如价格历史 start_date；订单预计入账为年月字段 expected_credit_period，格式见 BR-TEXT-04）用 YYYY-MM-DD 字符串；客户端展示一律按 Asia/Shanghai 时区换算，不随设备时区变化，使用 24 小时制；列表中的过去时间：与当前日期（+08:00，以服务端校准后的时钟为准）同一天「今天 HH:mm」，前一天「昨天 HH:mm」，同一年「MM-DD」，其他「YYYY-MM-DD」；未来时间：同年「MM-DD HH:mm」，跨年「YYYY-MM-DD HH:mm」，不用「明天」等相对词；纯日期字段：与今天同年显示「MM-DD」，否则「YYYY-MM-DD」，不使用「今天 / 明天」；订单时间线与提现记录详情精确到分钟「YYYY-MM-DD HH:mm」。 | 默认假设 | specs/client-behavior.md 测试向量；三端与 H5 时间格式化工具；OrderList、OrderDetail、WithdrawRecord、消息列表 |
| BR-TEXT-12 | **文案来源与字典机制**<br>业务文案取值顺序必须为：/v1/config.texts[key] → /v1/dict[enum][code] → 包内默认（由同一份 contracts/texts.default.json 生成）；接口枚举字段只返回编码；客户端业务页面不得硬编码中文业务文案（lint 规则拦截）；文案变量用 {name} 占位，变量值为 null、未提供或空字符串视为缺失（0 不算缺失），缺失时回落到该 key 的包内默认，包内默认仍含该缺失变量时整条文案不渲染（元素隐藏）并上报埋点 text_var_missing（key、变量名），不得显示「{」原文；字典带版本号，客户端按版本缓存，启动时及 config 中 dict_version 变化时刷新；服务端生成的推送、短信、Agent 话术必须读同一字典。 | 已确认 | GET /v1/dict、GET /v1/config（texts、dict_version、jump_tip、jump_tip.&lt;platform>.claims_enabled）；dict_items、config_items；contracts/texts.default.json（新增）；三端与 H5 文案加载模块、lint 规则、埋点 text_var_missing；JumpTip 已读记录按 BR-ATTR-21（服务端按 user_id + platform）；后台字典 / 文案编辑页 |
| BR-TEXT-13 | **禁用词与合规表述**<br>以下词不得出现在任何用户可见文案（字典、config.texts、推送、短信、分享模板、SDUI 页面、规则文章、商品池自定义标题、Agent 固定话术、应用商店描述）：全网最低、历史最低、最低价、最便宜、最高返利、稳赚、必返、返利最高、最高返、原价（价格与返利类，BR-PRICE-18 只列词、清单在本条维护）；高佣、收益榜（榜单类，2026-10-03 新补，见细则「榜单类词」）；返利到账、佣金、待结算、结算中、返现、充值、备付金（资金类，含 BR-FUND-17 用户侧禁用词；「预估收益」「已结算」按 C-02 负责人决定为用户侧术语，不再禁用，含义见 BR-TEXT-01）；「比价」只允许出现在 allow_keys 所列字段；规则类文案中的数值（入账天数、提现门槛、次数）必须由配置变量渲染；不得展示任何虚拟数据。本条是禁用词清单与匹配规则的唯一维护处，其他条目只引用。匹配顺序：先按字段位置判断白名单（白名单用原文匹配并整体剔除命中片段），再对剩余文本做 NFKC 归一、去空白与标点、英文转小写后的子串匹配。校验在 CI（扫描仓库文案与模板）和后台保存时同时执行，命中即失败；后台、报表字段不校验资金类词（佣金、待结算、结算中、返现、充值、备付金）与榜单类词（高佣、收益榜），仍校验价格与返利类词。「佣金」另有一处用户侧例外：Agent 佣金披露文案 agent.disclaimer.commission（BR-AI-10，拍板第二批 AI-17）。后台保存时另做语义预检，只标黄提示、不拦截（JEV-05，见细则）。 | 已确认 | CI 文案扫描脚本（specs/banned-words.yaml，含 scope 与 allow_keys）；后台保存校验（dict_items、config_items、notify-templates、share 模板、pages、articles、pool-items）与语义预检提示（Jev，BR-AI-14）；价格历史组件（BR-PRICE / Watch）；Agent 固定话术；应用商店描述 |
| BR-TEXT-14 | **错误与降级话术**<br>客户端对错误码与降级场景的提示必须使用细则表文案（经字典 error.&lt;code> 下发，带 data.reason 的码另有子键 error.&lt;code>.&lt;reason>，可改措辞不可改动作）；13 §13.11 已分配的每个码（废弃码与 9xxxx 除外）在本条都有 error.&lt;code> 行，reason 子键未命中时回落到 error.&lt;code>；44001 显示字典 risk_msg.&lt;code> 文案，服务端只下发风控提示编码不下发自由文本，未命中时显示「操作未通过安全校验」；服务端 msg 只作后备，内容必须与该码包内默认一致，只在字典与包内默认都没有该键时显示（如旧版本客户端遇到新码），msg 也为空时显示「操作未完成，请稍后再试」；其他 5xxxx 通用错误态必须附 trace_id 后 6 位（不足 6 位显示全部）；50301 按 data.reason 区分「维护中」与「即将开放」；42901 按 Retry-After 禁用按钮，无 Retry-After 时禁用 5 秒；转链熔断时按钮必须置为禁用态「稍后再试」；已废弃的错误码（如 30142，BR-PRICE-14）不得保留话术行，码号以 08 §13.11 为准（04 §7 与之逐行一致）；外跳与未安装降级路径以 BR-ATTR-27 为准，本条只维护按钮与提示文案（含待跟单卡、平台能力降级、剪贴板提示条文案；剪贴板读取时机与方式只按 BR-ID-16）。隐私首启、基本模式、撤回同意与系统权限用途的文案键见细则表 D（2026-10-03 新补，包内默认文案由法务定稿）。 | 默认假设 | contracts/error-codes.yaml（新增 text_key、reason 枚举）；dict_items.error（含 error.&lt;code>.&lt;reason> 子键）、dict_items.risk_msg；50301 data.reason（新增，maintenance / not_launched）；ErrorActionMapper（三端与 H5）；BuyButton、Agent 对话页；客服话术（trace id 查询） |
| BR-TEXT-15 | **淘礼金卡片如实话术**<br>首版按 D7 仅使用 unknown 和关闭分支；其余分支后续接入且验证后启用（拍板第二批 AI-01：首版不接入淘礼金，只提示「暂无淘礼金活动」，保留扩展位置）。淘礼金相关卡片必须按判定结果使用下表文案，结论只能是表中 6 种判定之一；素材淘礼金 A/B/C 判定能力在 规划/09 淘宝项验证通过（有接口样例）前，所有素材淘礼金一律按 unknown 处理，B 类能否同时享受我方返利未证实前也按 unknown 展示；tlj_kind=third_party 或 unknown 的卡片不得出现「淘礼金」标签或按钮，不得暗中替换口令；剩余份数必须取接口实时值，查询失败时不显示「剩余 N 份」、按钮保持可点、领取结果以淘宝页面为准，remain=0 按「已领完」处理；{amount} 按 BR-TEXT-10 面额格式（550 → 5.5 元）；池内无匹配或 tlj.enabled=off 时只出 notice agent.notice.tlj_none「暂无淘礼金活动」，不出淘礼金卡，也不出替代的有券商品卡（BR-AI-17；C-24 默认处理，已由负责人确认 2026-09-30）；素材淘礼金（含 tlj_kind=third_party）一律转链，不提供「复制原口令」（D20）。 | 待验证 | Agent rebate_quote / product_card（tlj、cta.text_key）；dict / texts：tlj.\*；商品卡、淘礼金页；config：tlj.kind_detection.enabled（默认 off）（原 tlj.copy_original_tpwd.enabled 按 D20 不再建立）；客服话术 |
| BR-TEXT-16 | **AI 生成内容标识**<br>Agent 对话页必须在每轮 AI 回复区显示统一标识，文案唯一取 texts.ai_label，默认「内容由 AI 生成，仅供参考」；SSE meta.ai_label 必须与该值相同（服务端从同一配置读取），客户端以 meta.ai_label 为准、缺失时用包内默认；tool.status 的 display_text 只描述动作（如「正在搜索淘宝」），不得包含用户输入原文或工具参数；金额、链接、口令只能出现在卡片中，text.delta 出站过滤与 trace 记录按 BR-AI-06；Agent 页顶部与「关于」页公示模型名称与登记编号，公示文案唯一取 config.agent.filing_text（含登记编号；agent.filing_no 只作后台保存校验用，不直接展示，BR-AI-12），未取得时为空且 Agent 入口只对内部测试名单开放（D16、BR-AI-12），不得显示占位或虚构编号。助手对用户的名称唯一取 texts.agent.name，默认「凑狸 AI 助手」（拍板第二批 AI-22），口吻要求见 BR-TEXT-22。BR-AI-06 的 meta.ai_label 按本条取值，不另定（AI-24）。本条是 AI 标识文案、助手名称与配置键的唯一维护处，合规义务见 BR-ID-15。 | 已确认 | SSE meta.ai_label；config.texts.ai_label、config.texts.agent.name、config.agent.filing_text、config.agent.model_label；AiLabel 组件、Agent 页顶部与关于页；Agent tool.status display_text 模板；OutputGuard（BR-AI-06） |
| BR-TEXT-17 | **广告推广标识**<br>product_card.ad_label 字段必须保留，客户端遇到非 null 值必须在卡片角标原样展示，不在客户端判断业务条件；法务定性前按保守默认：首页商品池卡片（运营手选、商家付费或置顶的商品位）、首页活动 Banner 与分享海报返回 ad_label=「推广」（Banner 用 SDUI 卡片的同名字段）；联盟物料信息流、金刚区等其他首页模块、搜索自然结果与 Agent 按相关性排序的卡片返回 null（拍板第二批 OPS-24）；联盟物料信息流返回 null，以该数据源只用不按佣金排序的频道为前提（见细则「联盟物料频道」，2026-10-03 新补）；法务定性后按结论改服务端下发规则并写入本条。 | 已确认 | product_card.ad_label；ProductCard 组件；SDUI 首页运营位；分享海报；config：ad_label 场景规则 |
| BR-TEXT-18 | **客服话术一致性**<br>客服话术库、FAQ、帮助中心、Agent 规则答疑（search_rules）与 explain_order 输出中涉及订单、返利、推广收益、提现状态和原因的表述，必须使用 BR-TEXT-01 术语并引用字典 key 渲染，不得另写同义说法；后台订单与提现详情必须同时显示「内部编码 + 用户看到的文案」；客服不得承诺字典与服务端 expected_credit_period（BR-TEXT-04）以外的入账或到账时间，不得使用 BR-TEXT-13 禁用词，不得向邀请人透露下级的订单信息（J7）；字典或原因码文案变更时，话术库对应条目必须在同一次发布内更新（发布检查项）。 | 默认假设 | 客服话术库（后台 articles 或独立表）；帮助中心 H5；Agent search_rules 规则库、explain_order；后台订单详情、提现详情页；发布检查清单 |
| BR-TEXT-19 | **余额流水用户文案**<br>余额流水的类型名称必须按下表由 ledger_type 映射（字典 ledger_type.&lt;CODE>.name；CLAWBACK 的 sub_type=PART_REFUND 用 ledger_type.CLAWBACK.name_part_refund）；金额按 BR-TEXT-10 带符号显示，符号表示对可用余额的影响；列表范围按 BR-FUND-15：只展示 available 子户分录与每张打款成功提现单的 1 条 WITHDRAW_PAID 汇总条目；WITHDRAW_FEE、TAX_WITHHOLD 不单独成行，只作汇总条目明细（「代扣个税 {tax}」「手续费 {fee}」）；跳转：自购与 share 单的 REBATE_CREDIT / SHARE_CREDIT / CLAWBACK / SETTLE_ADJUST 跳转关联子订单，WITHDRAW_\* 跳转提现单；REFERRAL_CREDIT（sub_type=DIRECT 与 INDIRECT）以及受益角色为 referrer（direct / indirect）的 CLAWBACK / SETTLE_ADJUST 只显示「邀请好友订单」与金额、日期精确到日，不可跳转，不展示下级昵称、层级与任何订单信息（J7）；sub_type=INDIRECT 的名称用 ledger_type.REFERRAL_CREDIT.name_indirect（BR-CALC-05、BR-INV-20，「间推」只作内部术语）；ADMIN_ADJUST 的名称与说明按 sub_type（原因码，BR-FUND-24 ②）取 ledger_type.ADMIN_ADJUST.name_&lt;sub_type>、hint_&lt;sub_type>，调减另发站内信 BALANCE_ADJUSTED（模板见细则；注销用户不发，BR-FUND-24 ⑦⑧）；ADMIN_ADJUST、BAD_DEBT_WRITEOFF 无关联单据时不显示跳转，显示 hint 说明。邀请分佣流水（REFERRAL_CREDIT 直推与间推，及 referrer 角色的 CLAWBACK / SETTLE_ADJUST）的名称、说明与日期精度只在本条维护，BR-INV-17 只引用（拍板第二批 OPS-18）。 | 默认假设 | dict_items.ledger_type（name、hint；ADMIN_ADJUST 按 sub_type 的 name_&lt;sub_type>、hint_&lt;sub_type>）；GET /v1/wallet/ledger（link_type、link_id、masked 标记）；notify-templates BALANCE_ADJUSTED（新增，站内信，category=service）；余额流水 H5；客服话术 |
| BR-TEXT-20 | **推送短信分享渠道约束**<br>推送、短信、分享的标题与首句不得以平台名称开头（正则 ^[【\\[]?(淘宝\|天猫\|京东\|拼多多\|美团\|阿里\|支付宝) 命中即拒），标题任何位置不得出现「官方」；校验在模板保存时与渲染后各做一次：商品标题变量（#标题#、title_short）渲染前去掉开头匹配 ^[【\\[]?(淘宝\|天猫\|京东\|拼多多\|美团\|阿里\|支付宝)[】\\]]? 的前缀并删除「官方」二字，模板不得以 #标题# 开头作为推送标题，渲染后仍命中则不发送并记录 template_render_blocked；App 图标、名称、启动页不得含平台商标；分享文案模板只允许变量 #标题# #券后价# #口令# #链接#，后台可配且过 BR-TEXT-13 校验；微信好友 / 群默认「文案 + 短链」，朋友圈默认海报；短信签名与模板长度、敏感词以短信服务商审核规则为准。 | 待验证 | notify-templates、短信模板；share 模板配置（F-SHARE-02/03）；推送标题与商品标题变量清洗函数；应用商店物料与启动页；后台模板保存校验、埋点 template_render_blocked；站长告警短信模板 UNION_AUTH_EXPIRING / UNION_AUTH_EXPIRED（BR-ID-24，拍板第二批 §8 ADD-08） |
| BR-TEXT-21 | **报表金额列口径与刷新标注**<br>后台页面与报表（含导出文件表头）中每个收益类金额列必须同时标明三项：口径编码（只能取 ESTIMATED 预估收益、WAITING 待入账、CREDITED 已入账、WITHDRAWN 已提现、UNION_SETTLED 联盟结算佣金、UNION_RECEIVED 联盟已回款之一，定义见细则）、数据截至时刻（+08:00，精确到分钟，显示格式按 BR-TEXT-11）、刷新方式（「实时」或实际刷新周期）；不得使用「确认收货佣金」「结算佣金」「预估结算」「未结算」「已返现」等未定义叫法；不同口径的金额不得在同一单元格相加，需要合计时分列展示；同一报表的口径编码与刷新方式由报表定义文件声明，列头由其生成，不手写。 | 默认假设 | 后台报表页与导出表头组件；报表定义文件（specs/reports/\*.yaml，新增 metric_basis、refresh 字段）；docs/glossary.md；后台资产快照报表、佣金对账报表、运营日报 |
| BR-TEXT-22 | **Agent 固定话术**<br>Agent 的拒答、需登录、出错与降级、notice、suggestions、条件标记与订单 / 规则模板文本（BR-AI-01、BR-AI-07、BR-AI-08、BR-AI-14、BR-AI-17、BR-AI-18、BR-AI-24）只能取本条细则表的字典键，经 BR-TEXT-12 字典下发，可改措辞、不可改用途与变量；口吻（拍板第二批 AI-22）：以「凑狸 AI 助手」自称（texts.agent.name，BR-TEXT-16），简短口语，每条不超过 2 句，不用表情符号；不写金额、日期原值、链接与 BR-TEXT-13 禁用词（「佣金」只在 agent.disclaimer.commission 例外）。模型生成的说明文字同样按此口吻写入系统提示，出站过滤仍按 BR-AI-06。order_status.&lt;display_status>.summary 与 order_reason.&lt;CODE>.summary 的包内默认按细则拼法给出，单独配置的以细则表为准。 | 默认假设 | dict_items / config.texts（agent.\*、order_list.\*、\*.summary）；contracts/texts.default.json；CardAssembler、OutputGuard 模板替换；系统提示词口吻段；CI 禁用词扫描；Agent 评测集话术用例 |
| BR-TEXT-23 | **账号与风控站内信**<br>风控状态变更、申诉结果、注销进度三类通知只发站内信，不发推送与短信（拍板第二批 OPS-15），必须使用细则表模板（notify-templates 可改措辞，变量与含义不得改）；内容只写原因类别（字典 risk_reason.&lt;category>），不得写风控规则、命中维度、举报来源或他人信息。封禁说明页与钱包「提现已暂停」提示显示原因类别、冻结到期时间（有期限时）与申诉入口（拍板第二批 OPS-12），文案取同一字典。触发与状态规则只在 BR-ID-27、BR-ID-31、BR-ID-36 维护。 | 已确认 | notify-templates（新增 RISK_STATE_CHANGED、APPEAL_RESULT、DELETION_PROGRESS，category=service、渠道只站内）；dict risk_reason.&lt;category>；封禁说明页；钱包提现暂停提示；GET /v1/me 风控字段（原因类别、frozen_until）；申诉接口查询结果 |

### 12.2 细则

#### BR-TEXT-01 细则 · 收益术语唯一含义

- 状态：已确认（负责人 2026-09-30，依据 docs/changes/20260930-拍板第一批.md §3 C-02、BR-TEXT-01 行；入账方式随同表 D11 行改为联盟月结批次；2026-10-01 拍板第二批 OPS-01 再次确认按 9-30 决定执行：结算前叫预估、结算后叫已结算、显示结算月份；2026-10-01 晚 §8 ADD-06 单一余额：钱包只显示一组数）
- 默认值：无（已确认，按规则执行）。负责人决定：结算前一律称「预估」（预估收益 / 预估返利），联盟结算并经后台核对入账后才用确定表达（已结算、可提现），参考花卷云字段口径。落地为：订单侧确定表达用「已结算」，提现侧保留「已到账」；「入账」只作动作词；「返利到账」「佣金」用户侧禁用；分享与邀请收入用「推广收益」前缀；钱包为单一余额（ADD-06），各金额取 BR-FUND-18 字段；已提现按申请额累计。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 本条原默认方案 A（C-02）：「订单侧「已入账 / 已收货，等待入账 / 预计入账日 / 确认收货满 N 天后入账」，提现保留「已到账」；「预估返」只指 ESTIMATED、WAITING 的预估，「待入账」只指 WAITING；「预估收益」「已结算」用户侧禁用」（负责人选「要改」，按变更记录 §3 C-02 行取代；提现侧「已到账」原义不变）
  - 本条原术语表「待入账：已确认收货、等待观察期满（rebate_status=WAITING）」「已入账：已写入该账户可用余额」（逐单观察期满入账改为跟随联盟月结批次入账，变更记录 §3 D11 行）
  - 本条 2026-09-30 月结初稿中依赖收货月的示例与进度行：「预计随淘宝 10 月联盟结算后入账」「预计随 {平台} {月份} 联盟结算后入账」（月份为确认收货月）（负责人 2026-09-30 补充，变更记录 §10：显示预计结算月份，一般为确认收货次月）
  - 规划/04 §2.3 用户侧状态映射：「CREDITED / SETTLED 显示「已到账」；RECEIVED「已收货，等待到账」」
  - 规划/01 §5 J4、J6 与 F-MSG-02：「已收货等待到账 → 已到账；钱包「待到账」；通知「已到账（每日汇总）」」
  - 规划/01 §5 J6 第 1 步、F-WDR-01：「冻结中（附原因）——风控冻结不再计入冻结中，改为顶部「提现已暂停」提示」
  - 规划/04 §4.2 W4/W5/W6：「冻结 → 在途 → 出金（在途不是独立余额字段，属 frozen_fen）」
  - 规划/02 §5.2：「order.credited → 推送「已到账」」
  - PRD修订_后端功能规划 2.16：「预估收益 → 待入账 → 已入账 → 已提现（作为报表口径保留，用户侧不用「预估收益」）」
  - 参考_花卷云功能查漏底稿 §12：「预估（付款）→预估结算→确认收货→已返现，另有未结算」
  - PRD v2.1 §9.3：「credit_status：ESTIMATED → HOLDING → CREDITED → REVERSED」
  - 本条 2026-10-01 写法：「「预估推广收益」指 PROMO 账户…；「预估收益」只作不区分账户时的合计称呼」「钱包汇总口径 SELF / PROMO 每账户分别返回；SELF 显示「预估返」，PROMO 显示「预估推广收益」」（单一余额，拍板第二批 §8 ADD-06）
- 来源：规划/04 §1 术语表、§2.3、§2.4、§3.2 account_balances、§4.2 W4–W8；规划/01 §1、§5 J4/J6/J7、F-WDR-01、F-WDR-09、F-MSG-02；规划/02 §5.2；PRD修订_后端功能规划 2.16、3.2；PRD v2.1 §9.3；参考_花卷云功能查漏底稿 §12、§16 #33；README §1.2；docs/changes/20260930-拍板第一批.md §3（C-02、BR-TEXT-01 行；D11、BR-FUND-04 行）；docs/changes/20260930-拍板第一批.md §10（负责人 2026-09-30 补充）；docs/changes/20261001-拍板第二批.md（OPS-01、§8 ADD-06）
- 需同步修改的规划文档：6 处（计数仅作记录，落点见 README §0.6）

**术语对照表（唯一口径）**：资金术语含义只在本表维护。BR-FUND-17 只维护 display_status 派生条件与「状态和金额只取接口」，BR-WDR-25 只维护提现副文案分支，README §1.2 为索引；三处与本表不一致时以本表为准。

| 用户词 | 唯一含义 | 内部状态 / 字段 | 后台·报表词 | 能否提现 |
| --- | --- | --- | --- | --- |
| 预估返 ¥x（标签）/ 预估返利（字段名） | 自购返利在结算前的估计值。下单前：按当前佣金率与用户比例估算（来源见 BR-PRICE）；下单后：从付款到联盟结算并经后台核对入账前的全部阶段（含已收货等待联盟结算、售后中、核对中），按当前基数 B_est × 分佣快照比例（BR-FUND-03） | 商品卡 rebate_min_fen/rebate_max_fen；订单 rebate_status ESTIMATED、WAITING | 预估收益（ESTIMATED、WAITING 两个口径编码，BR-TEXT-21） | 否 |
| 预估推广收益 | 分享单与邀请分佣（直推、间推）在结算前的估计值，阶段同上 | 受益角色 share / direct / indirect；rebate_status ESTIMATED、WAITING | 推广收益（预估） | 否 |
| 预估收益 | 钱包中全部来源（自购、分享、邀请）结算前的合计，单一余额下钱包只显示这一个预估数（ADD-06），不是独立状态 | estimated_total_fen（BR-FUND-18），取服务端返回的合计值，客户端不相加 | 预估收益 | 否 |
| 已结算 | 联盟出账后经后台核对、按月结批次计入可提现余额（BR-FUND-04）；订单侧唯一的确定表达 | rebate_status=CREDITED（platform_status 为 RECEIVED 或 SETTLED）；流水 REBATE_CREDIT / SHARE_CREDIT / REFERRAL_CREDIT | 已入账（CREDITED） | 是（计入可提现） |
| 实返 ¥y | 自购订单已结算且未被扣回的金额（含结算补差、减去部分扣回） | actual_fen（BR-TEXT-02） | 实返 | — |
| 推广收益 | 分享单与邀请分佣已结算金额 | 受益角色 share / direct / indirect；CREDITED；流水 SHARE_CREDIT / REFERRAL_CREDIT | 推广收益 | 是 |
| 可提现（钱包标题「可提现余额」） | withdrawable_fen = max(available_fen, 0)；available_fen &lt; 0 时可提现显示 ¥0，另显示「待抵扣 ¥{negative}」并禁止提现（BR-FUND-18、BR-WDR-05） | account_balances.available_fen | 可提现余额 | — |
| 待抵扣 | 余额为负时需由后续结算入账抵扣的金额 | negative_fen = max(−available_fen, 0) | 负余额 | 否 |
| 冻结中 | 提现单处于 PENDING_REVIEW / APPROVED / PAYING 的金额（PAYING 为冻结内的在途，不另设余额字段） | frozen_fen | 冻结 | 否 |
| 已到账 | **仅提现**：支付宝确认成功或人工补录流水号 | PAID_API / PAID_MANUAL；流水 WITHDRAW_PAID「提现到账」 | 已提现 | — |
| 已提现 | Σ 已到账提现单 amount_fen（申请额，含代扣税费） | withdrawals.amount_fen | 已提现 | — |
| 实际到账 | 单笔提现打入收款账户的金额 | net_fen = amount_fen − fee_fen − tax_fen | 实付 | — |
| 跟单成功 | 订单已同步入库且归到该用户（user_id 非空）、platform_status 首次 ∈ {PAID, RECEIVED, SETTLED} 且 B_est > 0 | BR-FUND-01 R2；BR-FUND-17 | 已归因 | 否 |
| 已失效 | 结算前失效，预估作废，余额未变 | rebate_status=VOID（display_status=INVALID） | 失效 | — |
| 已扣回 | 结算后失效，余额已被扣减（可致负） | rebate_status=CLAWED_BACK；流水 CLAWBACK。部分扣回时 rebate_status 仍为 CREDITED，display_status=CREDITED_PART_CLAWED | 扣回 | — |

**「入账」「已入账」「已到账」与原方案 A 的关系**（C-02 负责人选「要改」，新口径取代方案 A）：
- 原方案 A 订单侧「已入账」「待入账」「已收货，等待入账」「确认收货满 N 天后入账」作废：订单结算后的状态词改为「已结算」，结算前一律用「预估」；「待入账」不再作为用户侧金额或状态名。
- 「入账」保留为动作词，只描述「已结算金额计入可提现余额」这一动作（如「售后处理中，入账暂停」、流水名「自购返利入账」），不得单独作状态名；「已入账」不再出现在用户侧状态、金额名与推送标题中，后台与报表仍用 CREDITED「已入账」口径（BR-TEXT-21）。
- 提现侧「已到账」沿用原方案 A 的含义（仅指 PAID_API / PAID_MANUAL），不改为「提现成功」；「返利到账」仍禁用，避免订单与提现同词异义。
- 不设「待结算」「结算中」中间态名：负责人要求结算前一律称「预估」，已收货订单只用说明性短语「已收货，等待联盟结算」（BR-TEXT-02）与「预计 {月份} 结算」（BR-TEXT-04，月份为预计结算月份）表达进度，金额仍叫「预估返」；这两个词继续列在 BR-TEXT-13 禁用词中。

**花卷云口径对照**（只作对照，字段与编码按 D19 不沿用）：预估佣金 ↔ 预估返 / 预估推广收益 / 预估收益（用户侧不出现「佣金」）；结算佣金 ↔ 已结算金额（实返 / 推广收益）；结算状态「未结」↔ 结算前（ESTIMATED、WAITING，用户侧「预估」），「已结」↔ 已结算（CREDITED），「已失效」↔ 已失效（VOID）或已扣回（CLAWED_BACK）。

**钱包汇总口径**（`GET /v1/wallet/summary`，单一余额（拍板第二批 §8 ADD-06）；字段定义与计算只由 BR-FUND-18 维护，本条只定文案）：钱包只显示一组数——可提现余额、待抵扣（为负时）、冻结中、预估收益、已提现；不分「自购返利 / 推广收益」两栏，收入来源在余额流水按类型显示（BR-TEXT-19）。
- 可提现余额 ¥{withdrawable_fen}；negative_fen > 0 时另显示「待抵扣 ¥{negative_fen}」，提现按钮置灰（BR-WDR-05）。冻结中 ¥{frozen_fen}。
- 风控冻结（risk_state=frozen）与提现冻结记录（withdraw_holds，BR-WDR-05）不改变余额、不计入冻结中，只在钱包顶部显示「提现已暂停：{reason}」；reason 取字典 risk_msg.&lt;code> 文案（BR-TEXT-14），不得写风控规则细节；下发字段由 BR-WDR-05 定义。
- 预估：显示「预估收益 ¥{estimated_total_fen}」；预估合计 estimated_total_fen = 该用户全部受益角色结算前份额（BR-FUND-18：estimated_fen + pending_credit_fen，不含定金阶段与未归因订单），由服务端返回合计值，客户端不相加；注「按联盟最新预估计算，以联盟结算金额为准」。
- 预估下附进度行（只作说明，不是独立状态）：「其中已收货 ¥{pending_credit_fen}」；服务端返回 next_credit_period 时附「预计 {月份} 结算」（取值按 BR-FUND-18 与 BR-FUND-04 ⑪），credit_overdue=true 时附「入账核对中」，未返回时不显示月份；pending_credit_paused_fen > 0 时另附「其中 ¥{pending_credit_paused_fen} 暂缓入账」，不说明是维权还是 hold。保留「其中已收货」分项的理由：告诉用户哪部分会进入下一次联盟月结，金额名仍为「预估」。
- 已提现 ¥{withdrawn_fen}（BR-FUND-18：Σ 该用户 PAID_API / PAID_MANUAL 提现单 amount_fen）；提现记录中逐单展示「实际到账 {net}」。
- 不显示累计收益（2026-10-03，功能对照 G-37；按功能对照 Q-11 默认 B，负责人 2026-10-03 未回答、按现状，`docs/changes/20261003-拍板第三批.md` §4）：钱包不显示「累计已到账收益」「累计收益」「历史总收益」一类的累计总额，也不为此加字段（BR-FUND-18 不变）。用户问到时客服按 BR-TEXT-18 细则的统一答复回答。负责人改选显示时，口径要另写进 08 资金主题（只计返利、分享、邀请分佣的入账以及售后扣回与结算补差，不计坏账核销；人工调账计不计由负责人定），再加字段与词条，不能直接拿后台月末核对的累计入账净额（BR-FUND-23 的 X1，含坏账核销）当用户收益。

例：用户 A 有 3 笔自购订单：(PAID, ESTIMATED) 预估 ¥2.5、(RECEIVED, WAITING) 预估 ¥4（淘宝订单 10 月确认收货，联盟尚未返回结算时间，expected_credit_period=2026-11）、(RECEIVED, CREDITED) ¥6；无提现。接口返回 withdrawable_fen=600、estimated_total_fen=650、pending_credit_fen=400、estimated_fen=250、next_credit_period=2026-11、withdrawn_fen=0 → 钱包显示「可提现余额 ¥6｜预估收益 ¥6.5（其中已收货 ¥4，预计 11 月结算）｜已提现 ¥0」。用户问「返利到账了吗」，客服回答：「¥6 已结算，可提现；另有预估收益 ¥6.5，其中已收货的 ¥4 预计 11 月结算，¥2.5 待确认收货」。

**收益看板文案**（2026-10-03，功能对照 G-11；统计口径只在 BR-FUND-25 维护，待决策、按功能对照 Q-10 默认，本条只定文案键，经字典下发，可改措辞、不可改含义）：

| 键 | 默认文案 | 用处 |
| --- | --- | --- |
| earnings.title | 收益看板 | 页面标题与入口文字 |
| earnings.section.self / .share / .referral | 自购返利 / 分享推广收益 / 邀请推广收益 | 三栏标题；不出现「团队」「下线」「二级」等词（BR-INV-20） |
| earnings.period.today / .yesterday / .this_month / .last_month | 今日 / 昨日 / 本月 / 上月 | 期间；邀请栏只有本月、上月 |
| earnings.metric.paid_count.name / .hint | 付款笔数 / 按付款时间统计，不含已失效和已扣回的订单 | 自购、分享两栏 |
| earnings.metric.est.name_self / .name_promo / .hint | 预估返 / 预估推广收益 / 结算前的估计值，以联盟结算金额为准 | 自购栏用 name_self，分享与邀请栏用 name_promo |
| earnings.metric.credited.name / .hint | 已结算 / 按入账日期统计；订单归属被更正时在更正当天冲减，之后的扣回与调整见余额流水 | 三栏；金额可为负数，按 BR-TEXT-10 带符号显示（BR-FUND-25 细则「已结算怎样聚合」） |
| earnings.referral.note | 邀请推广收益只显示本月与上月的合计 | 邀请栏下方说明 |
| earnings.referral.platform_note | 不分平台 | 带平台筛选时显示在邀请栏 |

金额按 BR-TEXT-10 格式化；笔数为 0、金额为 0 时照常显示 0 与「¥0」，不隐藏栏目。看板不显示任何好友的昵称、订单或笔数（BR-INV-16、BR-INV-17）。

**后台 / 报表专用词**：「联盟结算佣金」（联盟月结付给平台的钱）只在后台与报表出现，BR-TEXT-13 按字段范围校验；「预估收益」用户侧与报表均可用，报表中须带口径编码（BR-TEXT-21）。

**负责人决定（C-02，变更记录 §3）**：用预估，结算后才用确定的表达，参考花卷云字段。原待决策的方案 A（订单侧「入账」、提现侧「到账」）与方案 B（订单侧「已到账」、提现改「提现成功」）均不再作为候选；本条按上述新口径取代方案 A，文案经 /v1/dict 下发。

**合稿修订**：钱包字段名以 BR-FUND-18 为准（数据口径归资金主题）：estimated_total_fen、pending_credit_fen、pending_credit_paused_fen、next_credit_period、credit_overdue、estimated_fen、withdrawn_fen、risk_paused_reason（next_credit_date 随月结改为 next_credit_period，新增预估合计 estimated_total_fen，拍板第二批 FUND-01）；本条曾用的 waiting_fen、waiting_paused_fen、next_due_date、due_overdue 已改名，含义不变；BR-FUND-18 已有 withdrawn_fen，钱包首页恢复展示「已提现」（C-19，代理已定）；「可提现」原写「等于 available_fen，可为负」，改为 withdrawable_fen 与「待抵扣」分列，与 BR-FUND-17、BR-FUND-18 一致；「预估中」原写「PAID 订单 rebate_min_fen 取下限」，改为 BR-FUND-18 的 estimated_fen，2026-09-30 随 C-02 再改为「预估返 / 预估推广收益」合计（含原「待入账」部分）。按 C-01 默认处理，已由负责人确认 2026-09-30；C-02 按负责人决定（变更记录 §3），取代方案 A。

需同步修改的规划文档（2026-09-30 C-02 改写；2026-10-01 已随拍板第二批同步）：08 README §1.2 用户话术索引（「已收货，等待入账 / 待入账」「预计 MM-DD 入账」「已入账」行改为本表口径，末段禁用词示例删去「预估收益」「已结算」）；规划/04 §1 术语表「预估返、待入账、已入账、已到账…」行（改为「预估返、预估推广收益、已结算、已到账…」）；规划/04 §6.4 `GET /v1/wallet/summary` 预估合计与预计入账周期字段（随 BR-FUND-18）、`GET /v1/earnings/summary`「预估、待入账、已入账」改为「预估、已结算」；规划/01 §4.1 底部 Tab「我的」行「待入账（BR-FUND-18）」、§4.2 Wallet 页清单「待入账」、§5 J1 第 6 步「预计入账日 → 到期入账 → 推送返利已入账」、J4 订单页文案行、J6 第 1 步钱包、F-WDR-01「待入账」、F-MSG-02「已入账（每日汇总）」；规划/10 AC-S2-33 钱包断言文案；08 §14 C-02 行与 §14.4 第 7 项（改为按负责人决定，取代方案 A）及 §14 BR-FUND-17、BR-WDR-25 行中「C-02 默认方案 A」表述；BR-FUND-17 派生表示意文案（WAITING、CREDITED）与 BR-FUND-18 钱包字段（预估合计、预计入账周期）。

#### BR-TEXT-02 细则 · 订单状态用户文案映射

- 状态：默认假设
- 默认值：状态粒度与文案沿用 规划/04 §2.3（已定），状态名按 BR-FUND-01 双状态换算，用户可见状态取 BR-FUND-17 派生的 display_status（派生顺序归资金主题，本条只定文案）；订单侧用词随 BR-TEXT-01（C-02 负责人决定：结算前称「预估」，结算后称「已结算」，2026-09-30 取代原方案 A 的「到账→入账」）；share 单用「推广收益」前缀、直推分佣不进订单列表（J7）、按钮合并规则、未知编码「状态更新中」、share 跨商品隐去标题为本条新补默认。
- 决策人：负责人
- 依赖平台能力：share 单是否会归入非分享商品（跨商品归因）取决于各平台推广位归因规则（规划/09 订单归属项，待实测）；预售单定金阶段的付款金额与定金时间取决于各平台订单字段（CAP-TB-07、CAP-JD-07、CAP-PDD-07，2026-10-03 功能对照 G-63）
- 取代：
  - PRD修订_后端功能规划 3.2：「按 union_status + rebate_status 组合映射（PAID+ESTIMATED 等）」（双状态按 BR-FUND-01 采纳，字段名以 platform_status + rebate_status 为准；本条改为按派生的 display_status 映射文案）
  - 本条原方案 A 文案（2026-09-30 随 C-02、D11 取代）：PAID hint「确认收货满 {wait_days} 天后入账」；WAITING「已收货，等待入账」+「预计 {expected_credit_date} 入账」；CREDITED「已入账」；CREDITED_PART_CLAWED「已入账（部分扣回 {z}）」；RIGHTS_PENDING hint「售后结束后重新计算入账日」；时间线「预计入账 {expected_credit_date} → 入账 {credited_at}」
  - 本条映射表原 WAITING_SETTLE 行：「WAITING，入账基数低于 settle.daily_min_fen 且结算额未记录 → 已收货，等待联盟结算后入账」（月结口径下停用，BR-FUND-17 第 11 行；拍板第二批 FUND-01）
  - 本条 2026-09-30 月结初稿文案：WAITING hint「预计随 {platform_name} {credit_period} 联盟结算后入账」、时间线「预计随 {platform_name} {credit_period} 联盟结算」（credit_period 为确认收货月）（负责人 2026-09-30 补充，变更记录 §10：改为预计结算月份「预计 {credit_period} 结算」）
  - PRD v2.1 §9.3：「PRESALE_DEPOSIT、RIGHTS_PROTECTING、PLATFORM_SETTLED 状态名」（分别映射 platform_status=DEPOSIT_PAID、display_status=RIGHTS_PENDING、platform_status=SETTLED；原映射「DEPOSIT_PAID、RECEIVED+维权提示、SETTLED」按 C-01 改写）
- 来源：规划/04 §2.3、§4.1、§8.3；规划/01 §5 J4、J7 第 5 条、J8、F-ORD-07；PRD修订_后端功能规划 2.5、3.2；PRD v2.1 §9.3；docs/changes/20260930-拍板第一批.md §3（C-02、D11 行）；docs/changes/20260930-拍板第一批.md §10（负责人 2026-09-30 补充）；docs/changes/20261001-拍板第二批.md（OPS-01、AI-02）
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**映射表**（C-02 负责人决定后的文案，术语见 BR-TEXT-01）

| display_status（BR-FUND-17 派生） | 对应双状态（BR-FUND-01） | 状态文案 | 金额行（自购） | 附加说明（字典 hint） | 状态固有按钮 |
| --- | --- | --- | --- | --- | --- |
| DEPOSIT_PAID | (DEPOSIT_PAID, ESTIMATED) | 已付定金 | 不显示金额 | 尾款付清后计算返利 | — |
| PAID | (PAID, ESTIMATED) | 已付款，返利待确认 | 预估返 ¥x 或 ¥a–¥b | 确认收货后随联盟月度结算入账（BR-TEXT-04）；比价风险提示按 BR-TEXT-03 | — |
| WAITING | (RECEIVED 或 SETTLED, WAITING) | 已收货，等待联盟结算 | 预估返 ¥x | 预计 {credit_period} 结算（BR-TEXT-04；credit_period 为预计结算月份，expected_credit_period 为 null 时不显示） | — |
| CREDITING | WAITING，该平台 credit.enabled=off 或 credit_overdue=true（BR-FUND-17 第 10、12 行，BR-FUND-04 ⑪；原按 expected_credit_date 早于今天） | 入账核对中 | 预估返 ¥x | 如有疑问请联系客服（BR-TEXT-03） | — |
| RIGHTS_PENDING | ESTIMATED 或 WAITING，rights_pending=true | 售后处理中，入账暂停 | 预估返 ¥x | 售后结束后随联盟结算入账（BR-TEXT-03） | — |
| REVIEWING | ESTIMATED 或 WAITING，hold=true | 入账核对中 | 预估返 ¥x | 如有疑问请联系客服；不显示 hold 原因与预计结算月份（BR-TEXT-03） | — |
| NO_REBATE | ESTIMATED / WAITING 且 B_est=0，或 CREDITED 且无入账凭证（B_credit=0） | 本单无返利 | 不显示金额 | —（被平台判为比价订单时显示比价说明，BR-TEXT-03「比价无返利」，2026-10-03） | — |
| CREDITED | (RECEIVED 或 SETTLED, CREDITED)，无 CLAWBACK | 已结算 | 实返 ¥y（含结算补差） | 差额行（BR-TEXT-03） | 去提现 |
| CREDITED_PART_CLAWED | CREDITED 且存在 CLAWBACK（部分扣回，含入账后部分退款） | 已结算（部分扣回 {z}） | 实返 ¥y | 差额行（BR-TEXT-03） | 去提现 |
| INVALID | (任意, VOID) | 已失效 | 返利 ¥0 | 原因标题 + 说明（BR-TEXT-05，仅 void 类） | —（按钮只来自 reason.action，如 BLACKLIST→去申诉，PUNISH/OTHER→联系客服） |
| CLAWED_BACK | (任意, CLAWED_BACK) | 已扣回 | 扣回 -¥z | 原因 + 「已从余额扣除」 | 查看流水 |
| 未知编码 | — | 状态更新中 | 不显示 | 请稍后查看 | — |

各行的判定条件与先后顺序只由 BR-FUND-17 派生表维护，上表「对应双状态」列仅供阅读；两处不一致时以 BR-FUND-17 为准，本表只维护文案列。原 规划/04 的 RECEIVED 行对应 WAITING、CREDITED 与 SETTLED 两行合并为 CREDITED（平台是否已结算不影响用户文案）。用户侧「已结算」指我方月结批次核对入账（rebate_status=CREDITED，BR-TEXT-01），不是 platform_status=SETTLED；平台已结算、我方尚未核对入账的订单仍按其 display_status 显示「预估返」。WAITING、CREDITING 的派生条件（原按 expected_credit_date）随 BR-FUND-04 月结改写由 BR-FUND-17 调整，本表只维护文案。

**金额字段**（服务端计算，客户端不推算，单位分）：
- 预估：est_rebate_fen 或 rebate_min_fen / rebate_max_fen。
- 实返 y = actual_fen = credited_fen + Σ 该子订单本账户 SETTLE_ADJUST 流水金额（带符号）− Σ 该子订单本账户 CLAWBACK 流水金额绝对值（display_status ∈ {CREDITED, CREDITED_PART_CLAWED} 时展示）。
- 扣回 z = clawback_fen = Σ 该子订单本账户 CLAWBACK 流水金额绝对值（含 sub_type=PART_REFUND 的部分扣回，BR-FUND-08）。

**share 单（分享者视角）**：状态文案同上；金额行「预估推广收益 ¥x」/「推广收益 ¥y」；不展示买家信息。子订单 product_key 与分享时 link_id 登记的商品不一致时，标题显示「好友购买的其他商品」，不展示标题、图片、SKU（平台是否存在跨商品归因见 规划/09，待实测）。

**时间线**（详情页）：付款 {paid_at} → 收货 {received_at} → 预计 {credit_period} 结算（BR-TEXT-04，credit_period 为预计结算月份；expected_credit_period 为 null 时该节点只显示「联盟结算」）→ 已结算 {credited_at}；display_status 为 INVALID / CLAWED_BACK 时追加「失效 / 扣回 {time}」节点，CREDITED_PART_CLAWED 追加「部分扣回 {time}」节点；未发生的节点置灰；时间格式见 BR-TEXT-11。预售单（2026-10-03，功能对照 G-63）在最前面加「付定金 {deposit_paid_at}」节点，原「付款」节点改称「付尾款 {paid_at}」，其余不变；deposit_paid_at 取平台返回的定金支付时间（与 BR-ATTR-25 预售单 attr_at 同一来源），平台不返回时该节点只显示「付定金」、不带时间。非预售单没有这个节点。返利金额仍按上表 DEPOSIT_PAID 行不显示。

**预售单的付款金额**（2026-10-03，功能对照 G-63；默认写法，定稿等 CAP-TB-07、CAP-JD-07、CAP-PDD-07 的预售序列实测）：display_status=DEPOSIT_PAID 时，订单接口的实付金额字段 pay_amount_fen 取已付定金金额，列表与详情显示「已付定金 {amount}」（键 `order_list.deposit_amount`）；尾款付清后取实付总额，按普通订单显示。平台不返回定金金额时为 null，不显示金额，不把预售总价当成已付。实测发现平台在定金阶段返回的是别的口径时，按实测改本段与 规划/04 §6.4 的说明。

**订单号的显示**（2026-10-03，功能对照 G-61；自购单完整、分享单脱敏按负责人 2026-10-03 已定，`docs/changes/20261003-拍板第三批.md` §2，本段只补格式）：
- 本人自购单（scope=self）：显示完整订单号 `order_no`，可复制；取用户在平台订单页看到的那个编号（有父单号的平台取父单号，否则取子单号），各平台的取值字段登记在 `specs/union/<platform>.md`。
- 分享单（scope=share）：只显示 `masked_order_no`，不可复制（不给复制按钮，长按也不出复制菜单）。脱敏在服务端完成，分享单的接口响应里不出现完整单号。格式按字符计（含「-」）：长度 ≥ 10 时保留前 4 位与末 2 位，中间不论多少位都换成 4 个「*」；长度 < 10 时只保留末 2 位，前面换成 4 个「*」。例：`3712345678901234567` → `3712****67`；`251003-123456789012345` → `2510****45`；`12345678` → `****78`。
- 为什么末尾只留 2 位：部分平台的订单号尾号可能对应买家账号（BR-ATTR-26 的淘宝订单号尾号维度，待 CAP-TB-07、09 U-42 验证），分享单的下单人是别人，多露尾号可能让分享者把几笔订单关联到同一个买家；保留前 4 位与末 2 位已够分享者与客服对照是哪一笔。
- 发给上级的通知与流水不含任何订单号（BR-TEXT-09、BR-TEXT-19）；任何接口都不向邀请人返回好友的订单号。

**订单列表的状态分组与查找**（2026-10-03，功能对照 G-60）：订单列表（自购、分享两个子 Tab 各自）顶部有状态分组 Tab，默认「全部」；另有平台筛选、按月份筛选与搜索框。分组由服务端按 display_status 归组，客户端只传分组名：

| status_group | 分组名（字典 order_status_group.&lt;group>） | 包含的 display_status |
| --- | --- | --- |
| all | 全部 | 全部，含未知编码 |
| estimating | 预估中 | DEPOSIT_PAID、PAID、WAITING、CREDITING、RIGHTS_PENDING、REVIEWING |
| credited | 已结算 | CREDITED、CREDITED_PART_CLAWED |
| no_rebate | 无返利 | NO_REBATE、INVALID、CLAWED_BACK |

- 分组名不用「待结算」「结算中」（BR-TEXT-13），「已结算」与 BR-TEXT-01 同义；「无返利」指这笔订单没有或不再有返利（含结算前失效与结算后扣回，各单的状态文案仍按上表映射）。未知编码只出现在「全部」。
- 平台筛选：单选一个平台，只作用于当前子 Tab。
- 按月份：按付款时间（+08:00）的年月筛选；只能选可查范围以内的月份（BR-ID-30 细则「订单类记录」的 earliest_visible_date）。
- 搜索：自购单里，输入内容与某笔订单的父单号或子单号完全相同时按单号精确命中，否则按标题包含匹配；分享单只按标题匹配，不按单号匹配（分享单只给脱敏号，BR-ATTR-10），标题已隐去的「好友购买的其他商品」（is_other_product=true）不参与标题匹配。搜索只在本人的订单里进行，不返回其他用户的订单。
- 筛选条件可以叠加；切换子 Tab 时分组回到「全部」，其余条件清空。

**详情页的「查看商品」**（2026-10-03，功能对照 G-62）：订单详情的商品信息区可以点击（入口文字 `order_detail.view_product`「查看商品」），打开该商品的原生详情页（ProductDetail），之后与其他入口进入详情页相同：显示当前价格与预估返利，用户点购买才经 open 转链，是一次新的点击与新的归因（BR-ATTR-05、BR-ATTR-08），不沿用这笔订单的任何链接或归因。
- 显示条件：订单接口返回的 product_key 不为空；本人自购单，或商品与分享时一致的分享单（is_other_product=false）。分享单的实购商品与分享商品不一致（is_other_product=true）时不显示，避免露出好友买了什么；直推、间推分佣的订单本来就不出现在订单列表（上文）。
- 不占详情页底部「最多 2 个按钮」的名额，也不改变按钮规则。
- 商品已下架或信息失效时按详情页现有规则处理（BR-PRICE-14、BR-PROD-05），不在订单页预先判断。

例：子订单 (PAID, ESTIMATED)，预估区间 320–450 分 → 列表「已付款，返利待确认｜预估返 ¥3.2–¥4.5」；10 月收货后 (RECEIVED, WAITING)、预估 450 分、联盟尚未返回结算时间、expected_credit_period=2026-11 → 「已收货，等待联盟结算｜预估返 ¥4.5｜预计 11 月结算」；月结批次核对入账后 → 「已结算｜实返 ¥4.5」。(SETTLED, CLAWED_BACK) + PUNISH → 按钮「联系客服」（主）+「查看流水」。

**边界**：部分退款不改变 rebate_status（BR-FUND-01 R7 / R9），入账前只改金额与差额行，入账后写 CLAWBACK（sub_type=PART_REFUND）使 display_status 变为 CREDITED_PART_CLAWED；hold、维权中不是 rebate_status，而是 display_status 的派生条件（REVIEWING、RIGHTS_PENDING），提示文案按 BR-TEXT-03。

按 C-01 默认处理，已由负责人确认 2026-09-30；入账后部分退款按 C-16 默认处理，待财务确认。

需同步修改的规划文档（2026-09-30 C-02 / D11 改写，未同步）：规划/01 §5 J4「已收货，等待入账（附预计入账日）→ 已入账」改为「已收货，等待联盟结算（附预计入账周期）→ 已结算」；规划/04 §2.3 `display_status` 行说明「订单侧一律「入账」口径，BR-TEXT-01 方案 A」改为按 BR-TEXT-01 C-02 口径；/v1/dict 字典键 order_status.PAID（hint）、.WAITING、.CREDITED、.CREDITED_PART_CLAWED、.RIGHTS_PENDING（hint）文案（契约建立时写入 contracts/texts.default.json）；规划/04 §6.4 `GET /v1/orders/{order_id}` 与 §8.3 `order_status` 卡片的 `expected_credit_date` 字段（改为 expected_credit_period、credit_overdue，BR-FUND-04 ⑪）；规划/03 §7.4 order_status 卡片「预计入账日（expected_credit_date）」；规划/10 §3.4 状态覆盖表 WAITING、CREDITED 行对应用例与 AC-S2-01-TB / -JD、AC-S2-09、AC-S2-12-TB 中的文案断言。。2026-09-30 补充（变更记录 §10，预计结算月份）：/v1/dict order_status.WAITING hint 与时间线节点文案改为「预计 {credit_period} 结算」；规划/01 §5 J4「附预计入账日」改为「附预计结算月份」；规划/10 AC-S2-01-TB / -JD、AC-S2-12-TB 中 WAITING 文案断言改为「预计 11 月结算」一类（已 grep 核对上述位置仍为旧写法）

#### BR-TEXT-03 细则 · 订单差额与异常提示

- 状态：默认假设
- 默认值：差额基准 = 首次分佣快照金额，区间取上限；阈值 1 分；入账前只对部分退款显示变化；原因取最近一次 diff 类 reason_code；hold 对用户只说「入账核对中」。理由：01 J4 与 04 §2.3 要求显示差额原因但未定基准与阈值；取上限使用户看到的最高金额与实返之差都有原因说明，减少客诉。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 本条原文案（2026-09-30 随 C-02、D11 取代）：维权中 hint「售后结束后重新计算入账日」、「隐藏预计入账日」；例 3「已入账（部分扣回 ¥4）」
- 来源：规划/01 §5 J4；规划/04 §2.3、§4.1 O5/O7/O10/O11；PRD修订_后端功能规划 2.6（入账金额、失效与扣回）、3.2；PRD v2.1 §9.3 RIGHTS_PROTECTING；docs/changes/20260930-拍板第一批.md §3（C-02、D11 行）
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

| 情形 | 判定（服务端） | 提示 |
| --- | --- | --- |
| 部分退款（入账前） | rebate_status ∈ {ESTIMATED, WAITING} 且 refunded_quantity > 0 | 叠加「部分退款，返利按剩余金额计算：预估返 ¥{initial} → ¥{current}」 |
| 实返 ≠ 首次预估（含入账后部分退款） | rebate_status=CREDITED 且 abs(diff) ≥ 1 | 叠加「比预估少 ¥2.1：{reason.title}」或「比预估多 ¥0.5：{reason.title}」；存在 sub_type=PART_REFUND 的 CLAWBACK（入账后 refunded_quantity 大于入账时快照 refunded_quantity_at_credit）时原因取 PART_REFUND |
| 维权中 | display_status=RIGHTS_PENDING（rights_pending=true，BR-FUND-06） | 状态文案「售后处理中，入账暂停」+ hint「售后结束后随联盟结算入账」，隐藏预计入账周期 |
| hold | display_status=REVIEWING（hold=true，BR-FUND-06） | 状态文案「入账核对中」+ hint「如有疑问请联系客服」，不显示 hold 原因与预计入账周期 |
| 入账延迟 | display_status=CREDITING（WAITING 且 credit_overdue=true，BR-FUND-04 ⑪；派生条件见 BR-FUND-17） | 状态文案「入账核对中」+ hint「如有疑问请联系客服」 |
| 比价风险 | display_status=PAID 且 rebate_basis=price_compare_risk | 金额显示区间 ¥a–¥b，hint「如被判定为比价订单，返利按较低金额计算」 |
| 比价无返利（2026-10-03，功能对照 G-09） | display_status=NO_REBATE 且 orders.is_price_compare=true | 状态文案仍为「本单无返利」，hint 用 order.price_compare.hint「这笔订单被平台判为比价订单，没有返利」 |

**优先级**：
1. hold、维权中、入账延迟是互斥的 display_status，按 BR-FUND-17 派生顺序只取一个（hold → 维权中 → 入账延迟）；hold 与维权同时存在时显示「入账核对中」。
2. 入账后部分退款与实返 ≠ 首次预估不分两行，只显示差额行，原因 PART_REFUND。
3. 比价风险只在 display_status=PAID，可与部分退款（入账前）同时显示，部分退款行在上。
4. diff 由多次调整叠加时只显示净差额与最近一个原因；diff = 0 不显示。

**比价说明入口**（2026-10-03，功能对照 G-09）：下列三处在行尾加文字入口「查看说明」，打开 /v1/config.help_links.price_compare 配置的帮助文章（规划/04 §10.1）；没有配置时不显示入口，不影响其余文案。① 差额行的原因为 PRICE_COMPARE；② 比价风险 hint；③ 比价无返利 hint。「查看说明」不占详情页的按钮位（BR-TEXT-02 的「最多 2 个按钮」不变）。is_price_compare 的判定字段按 BR-CALC-16（淘宝待 CAP-TB-04，拼多多待 CAP-PDD-04）；字段没有验证通过的平台该值为空，③ 不出现。帮助文章只解释「什么是比价订单、为什么返利会变少或没有」，不写等待时长之类的规避办法，不出现 BR-TEXT-13 的其他禁用词。

例 1：首次预估 520 分，入账时联盟按比价规则给出 310 分 → diff = -210 → 详情「实返 ¥3.1｜比预估少 ¥2.1：比价订单」。
例 2：PAID 区间 320–450 分（initial_est_fen=450），最终入账 320 分 → 「实返 ¥3.2｜比预估少 ¥1.3：比价订单」。
例 3：入账 800 分后买家退 1 件（共 2 件），写 CLAWBACK（sub_type=PART_REFUND）400 分（BR-FUND-08）→ display_status=CREDITED_PART_CLAWED →「已结算（部分扣回 ¥4）｜实返 ¥4｜比预估少 ¥4：部分退款」。

合稿修订：维权中、入账延迟原为本条自定的叠加提示（hold 只在过期后以「入账核对中」出现），现改为 BR-FUND-17 派生的 display_status，hold 在入账前任何阶段即显示「入账核对中」；例 3 原写负向 SETTLE_ADJUST，改为 CLAWBACK。按 C-01 默认处理，已由负责人确认 2026-09-30；按 C-16 默认处理，待财务确认。

需同步修改的规划文档（2026-09-30 C-02 / D11 改写，未同步）：规划/10 AC-S2-03（维权中 hint 断言「售后结束后随联盟结算入账」）、AC-S2-09（「已结算（部分扣回 ¥4）」）；规划/01 §5 J4 差额与异常行无文案复述，不需改。

#### BR-TEXT-04 细则 · 预计结算月份口径

- 状态：已确认（拍板第二批 OPS-01、AI-02：按 9-30 决定显示预计结算月份，订单页、钱包与 Agent 订单卡同一口径，不写天数）
- 默认值：入账时点对用户只表达为预计结算月份「预计 {月份} 结算」，月份取服务端返回的 expected_credit_period（预计结算月份，按 BR-FUND-04 ⑪ 计算，唯一维护处；负责人 2026-09-30 补充：看联盟返回字段，一般次月结算上月确认收货的订单，变更记录 §10），本条只定展示，不显示确认收货月；不给具体日期、不写天数；拿不到收货时间的订单不进 WAITING（BR-FUND-02；G-14，负责人 2026-09-30 确认，变更记录 §2）；expected_credit_period 返回 null 的情形见 BR-FUND-04 ⑪。理由：负责人把入账改为跟随联盟月结、后台人工核对后批量结算（变更记录 §3 D11 行），按收货日推算的日期已不成立；各平台出账日与核对耗时未定（变更记录 §6「月结结算流程参数」），只给月份可避免对外承诺具体日期。
- 决策人：负责人
- 依赖平台能力：各平台订单接口是否返回联盟结算时间及其语义（是否即联盟向推广者结算的月份，决定预计结算月份以联盟为准的部分）、联盟结算周期与结算日、结算覆盖的订单范围（按确认收货月份还是其他口径），以及京东、拼多多订单接口是否返回确认收货时间（规划/09 订单同步与结算项，待实测）；淘宝收货时间字段同样待接口样例确认
- 取代：
  - 本条原口径（2026-09-30 随 D11、BR-FUND-04 月结改写取代）：「expected_credit_date 由服务端计算，以 YYYY-MM-DD 返回，页面「预计 {expected_credit_date} 入账」；wait_days_snapshot 在进入 WAITING 时写入；商品详情与 PAID 订单显示「确认收货满 {wait_days} 天后入账」」
  - 本条 2026-09-30 月结初稿：「已收货订单展示「预计随 {platform_name} {credit_period} 联盟结算后入账」，credit_period = 该单结算周期 settle_period（确认收货月）；{月份} 表示联盟结算周期（账期），不是出账或入账发生的月份」（负责人 2026-09-30 补充，变更记录 §10：显示预计结算月份，不显示收货月）
  - 规划/04 §2.3、规划/01 §5 J1 第 6 步：「预计到账日 = 收货日 + 15 天」
  - PRD修订_后端功能规划 3.2：「预计到账日 = credit_due_at」
  - PRD v2.1 §9.3：「预计入账日（收货日 + 观察期）」
- 来源：规划/04 §2.3、§4.1 O3/O6；规划/02 §5.2；规划/00 D11；PRD修订_后端功能规划 2.6、3.2；docs/changes/20260930-拍板第一批.md §3（D11、BR-FUND-04、G-16 行；C-02 行）；docs/changes/20260930-拍板第一批.md §10（负责人 2026-09-30 补充）；docs/changes/20261001-拍板第二批.md（OPS-01、AI-02）
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

- 预计结算月份的取值（联盟返回结算时间时以联盟为准、未返回时的推算）、月结账单日、后台核对与批量结算的时点、维权或 hold 期间返回 null、逾期判断 credit_overdue、入账开关打开后的处理只在 BR-FUND-04 ⑪ 维护，本条不复述、不写算法；wait_days 不再用于用户侧文案。{月份} 表示预计结算月份（预计完成结算、计入可提现余额的月份），不是确认收货月份。

展示：

| 项 | 规则 |
| --- | --- |
| 月份格式 | expected_credit_period 为 YYYY-MM 字符串（+08:00 口径）；与今天同年显示「{M} 月」，否则「{YYYY} 年 {M} 月」；客户端只格式化，不推算、不改写 |
| 文案 | 订单：「预计 {credit_period} 结算」（不带平台名，订单卡片已显示平台）；钱包预估进度行同一文案（BR-TEXT-01），多平台时的取法按 BR-FUND-18 |
| 显示月份的 display_status | 仅 WAITING 且月份非 null |
| 不显示月份的 display_status | DEPOSIT_PAID、PAID、RIGHTS_PENDING、REVIEWING、CREDITING（「入账核对中」，BR-TEXT-03），以及结算后各状态；credit_overdue=true 时不得把月份自动改写为下个月（由 BR-FUND-17 派生为 CREDITING「入账核对中」） |
| 入账时点文案 | 商品详情与 display_status=PAID 的订单显示「确认收货后随联盟月度结算入账」，不含天数与日期变量；credit.enabled.&lt;platform>=off 时不展示（BR-FUND-04 开关表） |
| 禁止 | 不得出现「15 天」「满 N 天」「预计 MM-DD 入账」等具体天数或日期承诺；客服与 Agent 同样只说月份（BR-TEXT-18） |

例：淘宝订单 2026-10-08 确认收货，联盟尚未返回结算时间，服务端按 BR-FUND-04 ⑪ 返回 expected_credit_period=2026-11 → 订单「已收货，等待联盟结算｜预估返 ¥4.5｜预计 11 月结算」（不显示「10 月」）；联盟返回结算时间后月份以服务端返回为准，客户端不自行改写；月结账单核对入账后显示「已结算｜实返 ¥4.5」。若 credit_overdue=true（BR-FUND-04 ⑪）→ display_status=CREDITING，显示「入账核对中」，不显示月份。跨年：2026-12 确认收货 → 服务端返回 2027-01 → 「预计 2027 年 1 月结算」。

边界：expected_credit_period 何时返回 null（ESTIMATED、维权中 / hold、credit.enabled.&lt;platform>=off 等）及解除后的恢复见 BR-FUND-04 ⑪；本条只按上表决定是否展示（G-16 随 D11 改为 expected_credit_period，原算法作废，见 BR-FUND-04）。

按 C-01 默认处理，已由负责人确认 2026-09-30。合稿修订：原细则中的 run_at 00:05、00:01～00:30 快照等待与四个计算例已删，以 BR-FUND-04 为准（原复述缺 credit.enabled.&lt;platform>=off 分支）；入账时刻 C-17 只在 BR-FUND-04、BR-FUND-18 维护。2026-09-30 按 D11 月结改写：删去「预计 {expected_credit_date} 入账」与「确认收货满 {wait_days} 天后入账」，改为按 expected_credit_period 展示月份。

需同步修改的规划文档（2026-09-30 D11 / C-02 改写，未同步）：08 README §0.3「默认假设 × 平台能力」表 BR-TEXT-04 行（依赖部分改为「联盟出账周期、结算账单覆盖范围与确认收货时间」）、§1.2「预计 MM-DD 入账」行；规划/01 §1 定位表「按订单给出原因码和预计入账日」、§4.2 OrderDetail「预计入账日」、§5 J1 第 1 步「确认收货满 {wait_days} 天后入账」与第 6 步「确认收货 → 预计入账日 → 到期入账」、J4「附预计入账日」、F-AGENT-06「explain_order（原因码 + 预计入账日）」；规划/04 §2.3 display_status 行「文案、预计入账日见 BR-TEXT-02、BR-TEXT-04」、§6.4 `GET /v1/orders/{order_id}`「预计入账日 expected_credit_date」、§8.3 `order_status` 卡片 `expected_credit_date`（均改为 expected_credit_period、credit_overdue，BR-FUND-04 ⑪）；规划/03 §7.4 order_status 卡片「预计入账日（expected_credit_date）」；规划/10 AC-S2-01-TB / -JD（「收货满 15 天自动入账」整条随 BR-FUND-04 改写）、AC-S2-02（预计入账日算法与 wait_days 配置变更断言）、AC-S2-03 ②（expected_credit_date=2026-10-21）、AC-S2-33（next_credit_date 断言）、§6 G-14、G-16 行。。2026-09-30 补充（变更记录 §10，预计结算月份；已 grep 核对以下位置仍为旧写法）：08 README §0.3 表 BR-TEXT-04 行依赖部分补「联盟结算时间字段及语义」、§1.2「预计 MM-DD 入账」行改为「预计 {月份} 结算」；08 15 BR-TEXT-04 行（依赖平台能力补联盟结算时间）；08 14 §14.2 BR-TEXT-04 行；08_AI 数据来源表 expected_credit_date → expected_credit_period（预计结算月份）（2026-10-01 已同步，拍板第二批 AI-02）；规划/01 §1 定位表与 §4.2 OrderDetail「预计入账日」改为「预计结算月份」；规划/03 §7.4、规划/04 §6.4 与 §8.3 expected_credit_period 含义注明「预计结算月份」；规划/10 AC-S2-02 改为断言结算月份（10 月收货 →「预计 11 月结算」；有联盟结算时间时取联盟）

#### BR-TEXT-05 细则 · 原因码字典与文案

- 状态：默认假设
- 默认值：以 规划/04 §2.3 的 12 个编码为底，新增 PRICE_PROTECT、SETTLE_DIFF、COMMISSION_ZERO（BR-FUND-07）与 kind、action（枚举数组）、reason_sub 字段；claim 类编码只用于解释与找回；NOT_TRACKED、BLACKLIST、REFUND 标题改为不武断、不泄露风控的措辞；RIGHTS、PRICE_COMPARE 说明去掉「佣金」。
- 决策人：负责人
- 依赖平台能力：EXPIRED_CLICK 能否判定依赖各平台订单接口是否返回点击时间 / 失效原因（规划/09 订单归属项，待实测）；PUNISH 子原因依赖联盟处罚 / 维权数据导入字段（待实测）
- 取代：
  - 规划/04 §2.3 原因码：「NOT_TRACKED「不是通过本 App 链接下单」、BLACKLIST「账号或订单命中风控规则」、REFUND「订单已退款」」
  - PRD修订_后端功能规划 3.2：「reason_code 分失效或扣回 / 差额两组（编码并入本表）」
  - PRD v2.1 §9.3：「REFUNDED、CANCELLED、RISK_INVALID、PRICE_COMPARE_DOWNGRADED、ORDER_ATTR_OTHER_TLJ、NOT_FILED、CART_ORDER_UNTRACKED、RIGHTS_SUCCESS、PUNISHED」
- 来源：规划/04 §2.3；规划/01 F-ORD-07；PRD修订_后端功能规划 2.5、3.2；PRD v2.1 §9.3、§10.6.1
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

| 编码 | kind | 标题（默认） | 说明（默认） | 可找回 | action |
| --- | --- | --- | --- | --- | --- |
| REFUND | void | 订单已退款或取消 | 退款或取消后平台不再支付返利 | 否 | [] |
| PART_REFUND | diff | 部分退款 | 返利按剩余金额计算 | 否 | [] |
| RIGHTS | void | 发起售后维权，返利取消 | 售后成功后平台不再支付这笔返利 | 否 | [] |
| PUNISH | void | 订单被联盟判定违规 | 按 reason_sub 细分说明（见下） | 否 | [CONTACT_CS] |
| PRICE_COMPARE | diff | 比价订单 | 联盟按比价订单规则计算，返利相应降低 | 否 | [] |
| PRICE_PROTECT | diff | 商家价保退差 | 返利按价保后实付金额重新计算 | 否 | [] |
| SETTLE_DIFF | diff | 结算金额调整 | 联盟结算金额与预估不同，已按结算金额调整 | 否 | [] |
| NOT_TRACKED | claim | 未找到这笔订单的返利记录 | 可能不是通过本 App 链接下单，或下单前点过其他返利链接 | 是 | [CLAIM] |
| EXPIRED_CLICK | void | 下单时链接已过期 | 点击链接超过 {click_valid_days} 天才下单 | 否 | [] |
| RELATION_INVALID | claim | 淘宝授权未完成或已失效 | 重新授权后可提交找回 | 是 | [REAUTH]（授权成功后找回页再显示「去找回」） |
| OTHER_TLJ | void | 订单归其他推广者 | 下单时使用了其他推广者的淘礼金 | 否 | [] |
| BLACKLIST | void | 订单未通过安全校验 | 如有疑问可提交申诉 | 否 | [APPEAL] |
| PRESALE_UNPAID | void | 预售尾款未付 | 尾款未付，订单未成交 | 否 | [] |
| COMMISSION_ZERO | void | 返利已取消 | 平台将这笔订单的返利调整为 0，平台未说明原因 | 否 | [CONTACT_CS] |
| OTHER | void | 其他原因 | 可联系客服查询 | 否 | [CONTACT_CS] |

**PUNISH 子原因**（维权 / 处罚导入时写入 orders.reason_sub，字典 key order_reason_sub.&lt;SUB>.desc，不暴露联盟术语）：VIOLATION_PROMO「平台判定为违规推广订单」、SHOP_TK「平台判定为无效推广订单」、FAKE_TRADE「平台判定为异常交易」。「结算后退款」映射 REFUND（CLAWED_BACK）。

**旧编码映射**：PRD v2.1 REFUNDED/CANCELLED→REFUND；RISK_INVALID→BLACKLIST；PRICE_COMPARE_DOWNGRADED→PRICE_COMPARE；ORDER_ATTR_OTHER_TLJ→OTHER_TLJ；RIGHTS_SUCCESS→RIGHTS；PUNISHED→PUNISH；NOT_FILED→RELATION_INVALID、CART_ORDER_UNTRACKED→NOT_TRACKED（这两个只用于 explain_order / 找回查询，不写入已归因订单）。

**找回驳回原因**：CLAIM_RESULT 的驳回原因不用本表，取字典 claim_reject_reason.&lt;CODE>.title（编码表归 BR-ATTR）。

例：订单 CLAWED_BACK、reason=PUNISH、reason_sub=FAKE_TRADE → 详情「已扣回｜扣回 -¥3.2｜订单被联盟判定违规：平台判定为异常交易」+ 按钮「联系客服」（主）+「查看流水」。用户在找回页输入订单号，系统查到该单未归因且原因为 NOT_TRACKED → 显示标题与说明 + 「去找回」。

边界：title/desc 中的变量（如 {click_valid_days}）来自配置，缺失时按 BR-TEXT-12 处理；BLACKLIST 不得向用户说明命中哪条风控规则。

合稿补入：COMMISSION_ZERO 是 BR-FUND-07 定义的 VOID 原因（B_est 由 >0 变 0 而平台未回传失效），原表缺失；本表编码与 BR-FUND-07 的 reason_code 清单（REFUND / RIGHTS / PUNISH / BLACKLIST / COMMISSION_ZERO）一一对应，BR-FUND-08 CLAWBACK 的 sub_type（FULL / PART_REFUND / RIGHTS / PUNISH）不是原因码，不在本表。「失效 / 扣回」状态名按 BR-FUND-01（VOID、CLAWED_BACK）；按 C-01 默认处理，已由负责人确认 2026-09-30。

#### BR-TEXT-06 细则 · 提现状态用户文案

- 状态：默认假设
- 默认值：状态映射沿用 规划/04 §2.4（已定）；PAID_\* 措辞随 BR-TEXT-01；扣税展示随 D12（默认决策、待税务师意见）；net_fen 由服务端返回；PAID_MANUAL 按实际渠道展示。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 2.9、3.3：「AUTO_SUCCESS / MANUAL_SUCCESS（以 规划/ 的 PAID_API / PAID_MANUAL 为准）」
  - 规划/04 §2.4：「FAILED 用户文案「打款失败」改为「打款未成功」」
- 来源：规划/04 §2.4、§3.2 withdrawals、§4.2 W5–W8；规划/01 §5 J6、F-WDR-09；规划/00 D12；PRD修订_后端功能规划 2.9、3.3
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

| withdrawal_status | 文案 | 附加信息 |
| --- | --- | --- |
| PENDING_REVIEW | 审核中 | 人工审核时效（BR-TEXT-07）；{amount} 已冻结；副文案按 BR-WDR-25 分支 |
| APPROVED | 审核中 | 同上（不暴露批次） |
| PAYING | 打款中 | 副文案按 BR-WDR-25 分支（显示收款账户 {masked_account}） |
| PAID_API | 已到账 | 「已转入{payout_channel_name} {masked_account}，到账 {net}」；有扣税时「已代扣个税 {tax}」 |
| PAID_MANUAL | 已到账 | 「已通过{payout_channel_name}转入 {masked_account}，到账 {net}」；扣税同上 |
| REJECTED | 未通过 | 驳回原因（BR-TEXT-08）+ 退回金额，措辞按 BR-WDR-25 |
| FAILED | 打款未成功 | 失败原因（BR-TEXT-08）+ 退回金额，措辞按 BR-WDR-25；账号类失败码加【修改收款账号】 |
| 未知编码 | 处理中 | — |

例：申请 1000 分，fee 0、tax 0 → 成功后「已到账｜已转入支付宝 138****5678，到账 ¥10」。申请 1000 分、代扣 80 分 → 「到账 ¥9.2，已代扣个税 ¥0.8」。

边界：PAYING 超 24 小时转人工后用户侧仍显示「打款中」；人工确认结果后按终态显示。流水 WITHDRAW_PAID 名称为「提现到账」（BR-TEXT-19）。扣税展示随 规划/00 D12 税务口径；税率表到位前 tax_fen 记 0、照常累计（拍板第二批 FUND-04，BR-WDR-20），tax_fen=0 时不显示「已代扣个税」。银行卡通道（BR-WDR-32，开关默认关）未开通期间的线下转账按 PAID_MANUAL 显示（拍板第二批 FUND-03）。

提现状态标题（withdrawal_status → 用户状态）只在本条维护：BR-WDR-25 不再列状态标题，只维护非 PAID_\* 状态的副文案分支条件与展示字段，上表「附加信息」列中 PENDING_REVIEW、APPROVED、PAYING、REJECTED、FAILED 行的副文案措辞与分支以 BR-WDR-25 细则表为准，本表只列要素；PAID_\* 行的副文案在本条维护。BR-FUND-17 不再写提现文案。C-02 按负责人决定（变更记录 §3），取代方案 A：新口径只改订单侧用词（结算前「预估」、结算后「已结算」），提现侧 PAID_\* 仍为「已到账」、FAILED 仍为「打款未成功」。

#### BR-TEXT-07 细则 · 提现时效与超时进度

- 状态：已确认（拍板第二批 OPS-17：自动到账的单显示「预计几分钟内到账」，转人工的才显示 24 小时）
- 默认值：自动到账单「预计几分钟内到账」；人工审核单「人工审核，工作日 24 小时内处理，节假日顺延」；提现页通用说明按自动到账总开关二选一；超时推送模板 WD_OVERDUE 文案见下。时限计算、触发状态、检查间隔、夜间顺延、发送前复查与去重见 BR-WDR-26。理由：01 J6 文案已定；触发逻辑只在 BR-WDR-26 维护一处。
- 决策人：运营
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 2.9 用户侧状态：「审核中=PENDING_REVIEW（工作日 24 小时内完成）」
  - 本条旧版：「处理时限 deadline = 申请时刻起累计 24 个工作小时…超时检查任务每 5 分钟运行…判定时状态仍 ∈ {PENDING_REVIEW, APPROVED} 时推送 1 次进度通知（幂等键 withdrawal_id:OVERDUE），判定时刻在 22:00–08:00 的推送延至 08:00 发送，发送前复查」（与 BR-WDR-26 旧版重复维护且状态集合、幂等键不一致；触发逻辑并入 BR-WDR-26，取值沿用本条旧版）
  - 本条 2026-10-01 前写法：「提现页与审核中状态必须展示「人工审核，工作日 24 小时内处理，节假日顺延」」（拍板第一批 D10 改为 MVP 自动到账后，按拍板第二批 OPS-17 区分自动与人工）
- 来源：规划/01 §5 J6 第 4 步；PRD修订_后端功能规划 2.9；docs/changes/20260930-拍板第一批.md §3 D10、§9 第 14 项；docs/changes/20261001-拍板第二批.md（OPS-17）
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 展示位置：提现页、提现记录中 PENDING_REVIEW 与 APPROVED（用户侧均为「审核中」）的单据；review_mode=auto 的单在 PAYING 前同样显示「预计几分钟内到账」，打款结果按 BR-TEXT-06。
- 「处理」对用户的含义：审核结束（口径见 BR-WDR-26）；不含打款到账时长。
- 超时推送模板 WD_OVERDUE 文案：「你的提现 {amount} 仍在审核中，我们会尽快处理，结果会第一时间通知你」。站内 + 推送，不发短信。何时发、发几次见 BR-WDR-26。
- 超时后列表副文案见 BR-WDR-25 用户侧状态表。

例：申请 ¥10，超时判定成立 → 推送与站内信「你的提现 ¥10 仍在审核中，我们会尽快处理，结果会第一时间通知你」。触发时刻的例子见 BR-WDR-26 细则。

#### BR-TEXT-08 细则 · 提现驳回与失败原因

- 状态：默认假设
- 默认值：驳回用编码化原因 + 内部备注分离；失败文案按支付宝码映射；状态只由明确失败白名单决定，白名单外一律按未知处理。理由：防止审核人自由文本泄露风控信息；防止把未知结果当失败退回余额导致重复打款（F-WDR-06、W6/W7）。
- 决策人：财务
- 依赖平台能力：支付宝 alipay.fund.trans.uni.transfer / alipay.fund.trans.common.query 的业务失败码清单与「明确失败」判定（待沙箱实测，规划/09）
- 取代：本条旧编码 INFO_MISMATCH→PAYEE_INFO_INVALID、ACCOUNT_RISK→RISK_SUSPECT、RULE_NOT_MET 废弃（该情形在申请时已由 BR-WDR-03 拦截）（G-03）
- 来源：规划/04 §2.4、§3.2 withdrawals、§4.2 W6/W7；规划/01 F-WDR-06、F-WDR-09；PRD修订_后端功能规划 2.9 payout-worker 规则
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**驳回原因（默认）**：编码以 BR-WDR-10 为准，本条只维护文案（字典 withdraw_reject_reason）。

| 编码 | 用户文案 | 使用方 |
| --- | --- | --- |
| RISK_SUSPECT | 账户存在异常，需要核实，请联系客服 | 人工可选 |
| ORDER_ABNORMAL | 部分订单状态待核实，请稍后重新申请 | 人工可选 |
| PAYEE_INFO_INVALID | 收款信息有误，请核对后重新申请 | 人工可选 |
| USER_REQUEST | 已按你的要求取消本次提现，金额已退回余额 | 人工可选 |
| OTHER | 其他原因，请联系客服 | 人工可选 |
| NEGATIVE_BALANCE | 有订单被扣回，冻结金额已用于抵扣 | 系统专用（与 BR-FUND-21 推送一致） |

编码统一为代理已定；ORDER_ABNORMAL、USER_REQUEST 为新增对外文案，默认处理，待财务确认（G-03）。

**失败原因映射（示例，支付宝错误码名称待沙箱核实）**：
| 支付宝错误码（待核实） | 是否在明确失败白名单 | 用户文案 | 修改收款账号 |
| --- | --- | --- | --- |
| PAYEE_NOT_EXIST | 待实测确认 | 收款支付宝账号不存在 | 显示 |
| PAYEE_USER_INFO_ERROR | 待实测确认 | 收款账号姓名与实名信息不一致 | 显示 |
| PAYEE_ACCOUNT_STATUS_ERROR | 待实测确认 | 收款支付宝账号状态异常 | 显示 |
| 白名单内但未命中文案映射 | 是 | 打款未成功，{amount} 已退回余额，如有疑问请联系客服 | 不显示 |
| SYSTEM_ERROR / 超时 / 未收录码 | 否 | 不进入 FAILED，用户侧仍「打款中」 | — |

例：打款返回 PAYEE_USER_INFO_ERROR（白名单内）→ FAILED，记录显示「打款未成功｜收款账号姓名与实名信息不一致｜¥10 已退回余额｜修改收款账号」。返回 SYSTEM_ERROR → 保持 PAYING，1 分、5 分、30 分、2 小时查询，不退回余额。

边界：同一提现单 fail_code 只记最终结果；文案映射表后台可配，变更过禁用词校验（BR-TEXT-13）；明确失败码白名单不在后台可配范围，变更走代码评审。

#### BR-TEXT-09 细则 · 交易通知文案模板

- 状态：已确认（拍板第二批 OPS-02：按 9-30 决定，全部受益人都推、月结批次完成后推；OPS-16：交易与提现消息归「服务」类；模板措辞运营可在 notify-templates 改，变量与含义不变；拍板第三批 2026-10-03：跟单通知越快越好，合并窗口由 5 分钟缩短为 notify.tracked_merge_window_seconds，不改为日汇总）
- 默认值：推送对象按负责人决定（C-25：有收益的都要推送，变更记录 §3）为该子订单全部受益人（归属用户、直推上级、间推上级）；模板措辞随 BR-TEXT-01（C-02 负责人决定）；上级通知只给金额与状态；ORDER_TRACKED 按 platform_status 首次进入 PAID 及之后状态触发、本单无返利不推；合并窗口 notify.tracked_merge_window_seconds（当前默认 10 秒，负责人 2026-10-03），自购 / 分享 / 邀请三类分条；CREDITED 在结算批次完成后每用户汇总 1 条，完成时刻在免打扰时段则顺延到免打扰结束（负责人 2026-09-30 补充后统一口径，与 BR-FUND-04 一致）；DEPOSIT_PAID 不推；找回单本人只发 CLAIM_RESULT。理由：规划/ 只定了通知清单与频控，未定模板、窗口、发送时刻与找回单是否重复推送；上级模板措辞与「邀请」合并分类为代理按 C-25 补的默认，运营可在 notify-templates 改措辞。
- 决策人：运营（推送对象：负责人，C-25 已定）
- 依赖平台能力：无
- 取代：
  - 本条 2026-10-03 前的合并窗口：「合并窗口为固定窗口，自用户第 1 个待推事件时刻 t0 起 5 分钟，在 t0+5min 发送（单笔也延迟到 t0+5min）…t0+5min 之后到达的事件开启新窗口」（负责人 2026-10-03 决定跟单通知越快越好、订单同步回来就通知、最好 1 分钟内，docs/changes/20261003-拍板第三批.md §1）
  - 本条原口径（C-25 默认方案，负责人选「要改」，2026-09-30 按变更记录 §3 取代）：「直推上级不发 ORDER_TRACKED（J7）；直推分佣不发 ORDER_TRACKED；自购受益人与 share 单分享者各推自己的份额，直推上级不推；窗口内同账户类型事件合并，SELF 与 PROMO 分别成条」
  - 本条原方案 A 模板（2026-09-30 随 C-02 取代）：CREDITED「有 {n} 笔返利已入账，共 {sum}，可提现」等「已入账」措辞；「D 日 09:00 入账任务未完成则在任务完成后发送」（随 D11 改为月结结算批次）
  - 本条 2026-09-30 前 CREDITED 发送时点：「CREDITED 日汇总于 D 日 09:00(+08:00) 发送，统计 [D-1 09:00, D 09:00) 内写入的流水，D 日 09:00 有月结结算批次正在执行时在该批次完成后发送，每用户每日 1 条，幂等键 user_id:CREDITED:D」（与 BR-FUND-04「批次执行完成后推送」两种写法并存；2026-09-30 统一为结算批次完成后推送、免打扰时段顺延，变更记录 §9 第 4 项、§10）
  - 规划/02 §5.2：「order.credited → 推送「已到账」（每日汇总）」
  - PRD修订_后端功能规划 2.14：「ORDER_TRACKED 由 order.attributed 触发（以 规划/ 事件名为准，触发条件按本条「首次进入 PAID」）」
  - 本条 2026-10-01 写法：「SELF 与 PROMO 账户分别使用各自模板」「按 SELF、分享、邀请三类分别成条」及模板变体名 SELF / PROMO（单一余额后按收入来源命名，拍板第二批 §8 ADD-06；模板内容不变）
- 来源：规划/01 §5 J1 第 5–6 步、J7 第 5 条、F-MSG-02、F-MSG-04；规划/04 §4.1 O2；PRD修订_后端功能规划 2.14；PRD v2.1 §6、§9.3；docs/changes/20260930-拍板第一批.md §3（C-25 行；D8、BR-INV-12、BR-CALC-05 行；C-02 行；D11 行）；docs/changes/20260930-拍板第一批.md §10（负责人 2026-09-30 补充）；docs/changes/20261001-间推二级奖励.md；docs/changes/20261001-拍板第二批.md（OPS-02、OPS-16）；docs/changes/20261001-拍板第二批.md §8 ADD-06
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 被邀请人知情（2026-10-03，功能对照 G-16）：发给直推、间推上级的通知在订单同步后很快发出（合并窗口见正文），上级能据此大致知道好友的下单时间；通知时效与推送对象不因此改变（拍板第三批 §1：不做日汇总）。对被邀请人的告知内容与位置见 BR-INV-16 细则「对被邀请人的告知」，告知句 invite.notice_inviter 见 BR-TEXT-14 表 C。

| code | 渠道 | 模板 |
| --- | --- | --- |
| ORDER_TRACKED 自购 1 笔 | 推送 + 站内 | 跟单成功：{title_short}，预估返 {rebate} |
| ORDER_TRACKED 自购 合并 n≥2 | 同上 | {n} 笔订单跟单成功，预估返共 {rebate_sum} |
| ORDER_TRACKED 分享（share 单，发给分享者）1 笔 | 同上 | 有好友通过你的分享下单，预估推广收益 {rebate} |
| ORDER_TRACKED 分享 合并 n≥2 | 同上 | 有 {n} 笔好友订单来自你的分享，预估推广收益共 {rebate_sum} |
| ORDER_TRACKED 邀请（发给直推上级）1 笔 | 同上 | 你邀请的好友下单了，预估推广收益 {rebate} |
| ORDER_TRACKED 邀请（发给间推上级）1 笔 | 同上 | 你的好友邀请的用户下单了，预估推广收益 {rebate} |
| ORDER_TRACKED 邀请 合并 n≥2（直推、间推可混合） | 同上 | 有 {n} 笔邀请订单跟单成功，预估推广收益共 {rebate_sum} |
| ORDER_INVALID 自购 | 站内 | 订单已失效：{reason.title} |
| ORDER_INVALID 分享（share 单） | 站内 | 一笔分享订单已失效，不再计算推广收益：{reason.title} |
| ORDER_INVALID 邀请（直推、间推上级） | 站内 | 一笔邀请订单已失效，不再计算推广收益（不带原因，J7） |
| CREDITED 仅自购 | 推送 + 站内 | 有 {n} 笔返利已结算，共 {sum}，已计入可提现余额 |
| CREDITED 仅推广（分享与邀请合计） | 推送 + 站内 | 有 {m} 笔推广收益已结算，共 {promo_sum}，已计入可提现余额 |
| CREDITED 两者都有 | 推送 + 站内 | 有 {n} 笔返利已结算，共 {sum}；推广收益已结算 {promo_sum}，均已计入可提现余额 |
| CLAWBACK 自购 | 推送 + 站内 | 订单返利已扣回 {amount}：{reason.title} |
| CLAWBACK 分享（share 单） | 推送 + 站内 | 一笔分享订单的推广收益已扣回 {amount}：{reason.title} |
| CLAWBACK 邀请（直推、间推分佣） | 推送 + 站内 | 一笔邀请订单的推广收益已扣回 {amount}（不带原因，J7） |
| WD_SUCCESS | 推送 + 站内 | 提现已到账：{net} 已转入{payout_channel_name} |
| WD_REJECTED | 推送 + 站内 | 提现未通过：{reason}，{amount} 已退回余额 |
| WD_FAILED | 推送 + 站内 + 短信 | 提现打款未成功：{reason}，{amount} 已退回余额；账号类失败码追加「，可修改收款账号后重试」 |
| CLAIM_RESULT | 站内 | 订单找回成功，预估返 {rebate} / 订单找回未通过：{reason}（claim_reject_reason.&lt;CODE>.title，BR-ATTR 维护） |

- {amount} 在 CLAWBACK 中为负值格式（如 -¥3.2）；{rebate} 为区间时按 BR-TEXT-10 格式化；合并求和对下限、上限分别求和：两单 ¥1–¥2 与 ¥3 → 「预估返共 ¥4–¥5」。
- title_short = 商品标题先按 BR-TEXT-20 去平台前缀与「官方」，再按 Unicode 扩展字素簇取前 12 个 + 「…」；原标题 ≤12 个字素时不加「…」。邀请类模板不得使用 title_short 及任何商品、下级变量，模板保存校验只允许 {rebate}、{rebate_sum}、{amount}、{n}。
- 上级隐私：直推、间推上级收到的通知只含金额与状态，点击跳转钱包余额流水（BR-TEXT-19，不可跳订单），不跳订单详情；客服对上级的答复同样不透露下级订单（BR-TEXT-18）。
- 频控与免打扰：通知分类、频控初值与免打扰时段见 BR-WATCH-15（已确认）；跟单、收益与提现类属「服务」类（OPS-16，用户可关推送、站内信照写），不受营销类 22:00–08:00 限制（CREDITED 例外：完成时刻在免打扰时段 notify.quiet_hours 内的顺延到时段结束，同 BR-WDR-26 WD_OVERDUE 的顺延做法），也不计入 BR-WATCH-15 的订阅类每日推送上限；条数由本条合并窗口（notify.tracked_merge_window_seconds）与 (子订单, 受益人, 角色) 去重控制（上级下线多时是否另设每日上限见 12.3 未决问题）。

例 1（窗口取默认 10 秒）：用户 14:00:10、14:00:15 两单跟单 → t0=14:00:10，14:00:20 推 1 条「2 笔订单跟单成功，预估返共 ¥7.3」；14:03:40 第三单 → 新窗口，14:03:50 推「跟单成功：…」。
例 2（假定该平台 08b 已通过，BR-FUND-04 ⑨）：11-24 16:00 finance 确认 2026-10 月结账单并立即结算，16:20 全部批次执行完，用户写入 2 笔 REBATE_CREDIT（¥4.5、¥6）→ 16:20 推「有 2 笔返利已结算，共 ¥10.5，已计入可提现余额」；11-26 11:00 补充批次完成、补入 1 笔 → 11:00 另推 1 条。定时结算 11-25 22:30 执行完 → 顺延到 11-26 08:00 推送。

营销类 22:00–08:00 不发；交易类不受限，但 CREDITED 完成时刻在免打扰时段的顺延到时段结束、WD_OVERDUE 的发送时刻按 BR-WDR-26。

例 3：京东子订单同步时平台已回传「完成」、已归因，B_est=0 → display_status=NO_REBATE，不发 ORDER_TRACKED；同一子订单后续 B_est 变为 >0 也不补发（BR-FUND-03：预估金额后续变化不推送）。

例 4（间推开关开启）：C 的直推上级为 B、间推上级为 A；C 自购一单 14:00:10 跟单，份额 C ¥4、B ¥0.8、A ¥0.3 → 14:05:10 C 收「跟单成功：{title_short}，预估返 ¥4」，B 收「你邀请的好友下单了，预估推广收益 ¥0.8」，A 收「你的好友邀请的用户下单了，预估推广收益 ¥0.3」；B、A 的通知不含商品标题与 C 的昵称。若间推比例为 0（A 份额 0）或规则版本 indirect_enabled 关闭（无间推受益人）→ A 不收推送。

例 5（OPS-16）：用户在通知设置关闭「服务」类推送 → 跟单、结算、提现到账等只写站内信，不发推送；WD_FAILED 短信不受该开关影响（BR-TEXT-20）。

触发条件中的状态名按 BR-FUND-01（原写「首次进入 PAID（O2）」）；按 C-01 默认处理，已由负责人确认 2026-09-30。

ORDER_TRACKED 的推送对象、触发、合并与去重只在本条维护（BR-FUND-03 引用本条）：该子订单全部份额 > 0 的受益人各推自己的份额——归属用户（自购本人或 share 单分享者）、直推上级、间推上级；幂等键由原 order_id:TRACKED 改为 {order_key}:{uid}:{role}:TRACKED（order_key 定义见 BR-FUND-05）。C-25 按负责人决定（变更记录 §3：有收益的都要推送），取代原「直推上级不推」默认。

需同步修改的规划文档（2026-09-30 C-25 / C-02 / D11 改写，未同步）：08 §14 C-25 行（改为按负责人决定、推给全部受益人）、C-02 行；BR-FUND-03 推送引用处（原「删去直推上级」说明）；规划/01 §5 J7（补「上级收到跟单与收益通知，只含金额与状态」一句并引用本条）、F-MSG-02「已入账（每日汇总）」改为「已结算（每日汇总）」并注明推送对象含直推、间推上级；规划/01 §5 J1 第 6 步「推送返利已入账」；规划/02 §5.2 时序图「order.credited → 推送 CREDITED 模板」（无文案复述，按受益人扇出时核对）；规划/04 §2.5 `notify_template.code` 行（邀请类模板变体，code 不变）；规划/10 AC-S1-24（补直推、间推上级各收 1 条且不含商品与下级信息、上级份额 0 不推的断言）。。2026-09-30 补充（CREDITED 推送时点统一为结算批次完成后推送、免打扰顺延；已 grep 核对以下位置仍为旧写法）：规划/01 F-MSG-02「已入账（每日汇总）」改为「已结算（结算批次完成后推送）」；规划/02 §5.2 时序图「推送 CREDITED 模板（每日汇总，BR-TEXT-09）」删「每日汇总」；08 14 §14.2 BR-TEXT-09 行；规划/10 AC-S2 月结用例补推送时点与免打扰顺延断言。2026-10-01 拍板第二批 OPS-16 同步：规划/01 F-MSG-04 通知设置 MVP 只显示「服务」开关，交易与提现消息归服务类、可关推送不关站内信；规划/04 §2.5 notify_template 增加 category；规划/05 B1-12 验收「关闭某分类后不再推送」改为「关闭服务类后只写站内信」

#### BR-TEXT-10 细则 · 金额格式化

- 状态：已确认
- 默认值：无（已确认，按规则执行）
- 决策人：代理可自定
- 依赖平台能力：无
- 取代：无
- 来源：规划/03 §10.2、§10.3；规划/04 §5 金额与比例
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

| 输入（分） | 输出 |
| --- | --- |
| 990 | ¥9.9 |
| 1000 | ¥10 |
| 1 | ¥0.01 |
| 0 | ¥0 |
| 123456 | ¥1234.56 |
| -150 | -¥1.5 |
| 流水 +600 | +¥6 |
| 区间 320 / 450 | ¥3.2–¥4.5 |
| 区间 450 / 450 | ¥4.5 |
| 区间 0 / 0 | 暂无返利 |
| 面额格式 550（淘礼金，BR-TEXT-15） | 5.5 元 |

算法：yuan = abs(fen) div 100，cent = abs(fen) mod 100；cent = 0 → 「¥{yuan}」；cent mod 10 = 0 → 「¥{yuan}.{cent/10}」；否则 「¥{yuan}.{两位 cent}」。面额格式 = 同一算法去掉「¥」后接「元」。

- RebateTag：「预估返 ¥x」或「预估返 ¥a–¥b」。
- 推送合并求和对区间取下限 / 上限分别求和（BR-TEXT-09）；钱包「预估中」显示 BR-FUND-18 estimated_fen 单值（BR-TEXT-01）。
- 比例（_bp）只在后台显示：bp/100 + 「%」并去末尾 0（1250 → 12.5%）。
- 三端与 H5、服务端共用 specs/client-behavior.md 中的同一组测试向量（上表）。
- 金额隐藏（2026-10-03，功能对照 G-64；可选功能，UI 稿采用时实现）：「我的」、钱包、订单列表与详情这几个原生页的金额区有一个隐藏开关（小眼睛，无障碍标签取 BR-TEXT-14 表 C `amount_mask.hide` / `amount_mask.show`）。打开后，余额、待抵扣、冻结中、已提现、预估收益与其中各分项、订单的预估返、实返、推广收益、扣回金额都显示为固定的「****」，不显示「¥」、位数与正负号；实付金额是否一起隐藏由 UI 稿定。开关是本机偏好，存在本机、不上传，换账号沿用、卸载即清；不改接口与计算，推送、站内信、H5 页面（如收益看板）不受影响。

#### BR-TEXT-11 细则 · 时间与日期格式化

- 状态：默认假设
- 默认值：「昨天」附带 HH:mm；固定 Asia/Shanghai；未来时间与纯日期不用相对词。理由：规划/03 §10.3 示例「昨天」未写是否带时间，且未定设备时区、未来时间与纯日期的处理。
- 决策人：代理可自定
- 依赖平台能力：无
- 取代：
  - 规划/03 §10.3：「列表「今天 14:03 / 昨天 / 09-27 / 2025-12-31」」
  - 本条原纯日期示例「预计 09-29 入账」「预计 10-17 入账」「预计 2027-01-02 入账」（2026-09-30 随 D11 取代）
- 来源：规划/03 §10.3；规划/04 §5 时间；docs/changes/20260930-拍板第一批.md §3（D11 行）
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

例（now = 2026-09-29T10:00+08:00）：
| 输入 | 列表 / 文案 | 时间线 |
| --- | --- | --- |
| 2026-09-29T09:05:33+08:00 | 今天 09:05 | 2026-09-29 09:05 |
| 2026-09-28T23:59+08:00 | 昨天 23:59 | 2026-09-28 23:59 |
| 2026-09-27T14:03+08:00 | 09-27 | 2026-09-27 14:03 |
| 2025-12-31T08:00+08:00 | 2025-12-31 | 2025-12-31 08:00 |
| 未来 2026-09-30T08:00+08:00 | 09-30 08:00 | — |
| 未来 2027-01-02T08:00+08:00 | 2027-01-02 08:00 | — |
| 日期 2026-09-29 | 09-29 | — |
| 日期 2026-10-17 | 10-17 | — |
| 日期 2027-01-02 | 2027-01-02 | — |

纯日期示例原写「预计 09-29 入账」等，2026-09-30 随 D11 月结口径删去（订单预计入账改为年月 expected_credit_period，展示与格式只在 BR-TEXT-04 维护，不得出现「预计 MM-DD 入账」）；本表只保留日期格式本身。

边界：
- 设备在 UTC 时区，服务端时间 2026-09-28T23:30+08:00 仍显示「昨天 23:30」。
- 客户端时钟与服务端相差 >5 分钟时，用响应头 Date 校准相对时间基准。

#### BR-TEXT-12 细则 · 文案来源与字典机制

- 状态：已确认
- 默认值：无（已确认，按规则执行）
- 决策人：代理可自定
- 依赖平台能力：JumpTip 中有效天数与「后点击覆盖」两句依赖各平台点击有效期与归因覆盖规则（BR-ATTR、规划/09，待实测）
- 取代：无
- 来源：规划/03 §4.5、§10.3；规划/04 §5、§10.1；规划/01 F-CFG-02、F-CFG-06；PRD修订_后端功能规划 2.13；PRD v2.1 §6
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- key 命名：`order_status.<display_status>.label|hint`（CODE 为 BR-FUND-17 派生的 display_status）、`order_reason.<CODE>.title|desc|action`、`order_reason_sub.<SUB>.desc`、`claim_reject_reason.<CODE>.title`、`withdrawal_status.<CODE>.label|hint`、`withdraw_reject_reason.<CODE>`、`withdraw_fail_reason.<CODE>`、`ledger_type.<CODE>.name|hint`、`error.<code>`、`risk_msg.<code>`、`tlj.*`、`btn.buy.coupon`（领券购买）、`btn.buy`（去购买）、`btn.buy.no_rebate`（去购买（无返利））、`tag.rebate`（预估返）、`tag.presale`（预售）、`presale.price_note`、`auth_tips.<platform>`、`jump_tip`、`ai_label`、`pending_track_card.title|desc`（BR-TEXT-14，G-05）、`clipboard.prompt`（BR-TEXT-14，G-20）、`clipboard.invite_prompt`（BR-TEXT-14，OPS-06）、`agent.*` 与 `*.summary`（BR-TEXT-22）、`risk_reason.<category>` 与账号类站内信模板（BR-TEXT-23）、`privacy.*` 与 `perm.<type>.*`（BR-TEXT-14 表 D，2026-10-03）、`app_update.*` 与 `cs.*`（BR-TEXT-14 表 C，2026-10-03）。
- 购买按钮（拍板第二批 TRADE-21）：服务端在卡片 cta.text_key 下发，客户端不判断：有券（coupon_fen > 0）→ `btn.buy.coupon`「领券购买」；无券 → `btn.buy`「去购买」；用户选择或只能无返利购买时 → `btn.buy.no_rebate`「去购买（无返利）」。错误弹窗里的次按钮仍为「仍去购买（无返利）」（BR-TEXT-14）。淘礼金卡按钮按 BR-TEXT-15。
- 预售（拍板第二批 TRADE-10）：预售商品卡与详情显示标签 `tag.presale`「预售」，价格按定金 + 尾款总价显示（口径见 BR-PRICE），价格旁附 `presale.price_note`「定金与尾款以下单页为准」。
- 未知编码：显示 `<enum>.UNKNOWN`（订单「状态更新中」、提现「处理中」）。
- 后台修改字典或 texts：保存前过禁用词校验（BR-TEXT-13）与变量校验（模板变量必须与包内默认一致），发布时 dict_version +1，写审计。

**JumpTip**：
- 展示次数与已读记录按 BR-ATTR-21（每用户每平台首次外跳前 1 次，服务端记已读）。（G-13 默认处理，待运营确认；原「前 3 次、设备本地计数、不分平台、prefs.jump_tip_off」已删除。）
- 正文至少含「在打开的商品页直接下单」。「点击后 {click_valid_days} 天内下单有效」与「中途点其他返利链接可能导致丢单」两句，在对应平台的 规划/09 归因项验证通过后，按平台开关 jump_tip.&lt;platform>.claims_enabled（默认 off）启用；未验证平台不展示有效天数。

例：config.texts 未配置 order_reason.EXPIRED_CLICK.desc，字典值为「点击链接超过 {click_valid_days} 天才下单」，接口未下发 click_valid_days（null）→ 变量缺失，回落包内默认；包内默认同样含该变量 → desc 隐藏、只显示 title，并上报 text_var_missing（key=order_reason.EXPIRED_CLICK.desc，变量 click_valid_days）。变量值为 0（如 {n}=0）→ 正常渲染。（原例用 order_status.RECEIVED.hint 与维权中的 null；双状态下维权中是独立的 display_status=RIGHTS_PENDING，WAITING 订单不存在 expected_credit_date 为 null 的分支（BR-FUND-02，G-14），故换例。）

#### BR-TEXT-13 细则 · 禁用词与合规表述

- 状态：已确认（拍板第二批 TRADE-18：价格与返利类词按当前默认上线，法务意见出来后只改字典与 specs/banned-words.yaml；AI-17：佣金披露文案开例外；JEV-05：语义预检只标黄提示。原为待决策：默认值含待法务确认的词与降价模板）
- 默认值：F-PRIV-09 原清单（全网最低、历史最低、最便宜、最高返利、稳赚、必返）已定；新增「最低价」「返利到账」「佣金」与「比价」字段白名单为默认；「返利最高」「最高返」「原价」（BR-PRICE-18 提出，待法务确认）与「待结算」「结算中」「返现」「充值」「备付金」（资金类用户侧禁用词，原列于 BR-FUND-17，现只在本条维护）确认前默认启用；降价白名单模板待法务确认，确认前使用不含「最低」的中性表述。理由：宁可多拦，误伤只需改写文案，漏拦有广告法风险；清单只在本条维护，避免三处各列一份。
- 决策人：法务
- 依赖平台能力：无
- 取代：
  - 规划/01 F-PRIV-09：「禁用词：全网最低、历史最低、最便宜、最高返利、稳赚、必返（本条补入新增词、字段白名单与归一化规则）」
  - 本条原资金类清单中的「预估收益」「已结算」（2026-09-30 按 C-02 负责人决定移出：结算前称「预估收益 / 预估返利」、结算后称「已结算」为用户侧术语，BR-TEXT-01；变更记录 §3 C-02 行）；「待结算」「结算中」保留禁用，理由见 BR-TEXT-01 细则
- 来源：规划/01 §1、F-PRIV-09、F-SHARE-02；规划/06 Q-F4；PRD v2.1 §10.14、§10.19、§15；参考_花卷云功能查漏底稿 §17；docs/changes/20260930-拍板第一批.md §3（C-02 行）；docs/changes/20261001-拍板第二批.md（TRADE-18、AI-17、JEV-05）
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 禁用词表 specs/banned-words.yaml：每个词列出 scope（user_visible）与 allow_keys（dict key 通配），CI 与后台按 key 判定。
- 一处维护：BR-PRICE-18 只列价格与返利类用词及改写方式，资金术语含义只在 BR-TEXT-01 维护（BR-FUND-17 不再列词）；各处提到的禁用词以本条清单为准，新增词只改本条与 specs/banned-words.yaml。「结算补差」「结算金额调整」等字典文案不含上述资金类词（子串不命中），无需白名单。
- 「比价」allow_keys：order_reason.PRICE_COMPARE.title|desc、rebate_basis=price_compare_risk 的订单状态 hint（order_status.PAID.hint 的比价变体），以及渲染了上述字段的推送 / 站内信（ORDER_INVALID、CLAWBACK）；2026-10-03 增补（功能对照 G-09）：下单前的比价无返利文案 no_rebate.price_compare、no_rebate.price_compare.confirm（BR-TEXT-14 表 C），订单比价说明 order.price_compare.hint（BR-TEXT-03），以及 /v1/config.help_links.price_compare 指向的那一篇帮助文章的标题与正文（按文章 ID 放行，只这一篇）。卖点、广告位、分享标题、应用商店描述命中。卖点统一表述为「找货 + 返利透明 + 丢单兜底」。
- 归一化例：「全 网 最 低！」→ 命中「全网最低」。
- **降价表述（待法务确认）**：规划/01 §1 已写明「最低价」有《广告法》与《互联网平台价格行为规则》风险。法务确认前价格历史组件只用「自 {start_date} 以来我们记录到的价格：当前 {current}，曾为 {low}」，不出现「最低」二字，无白名单；法务同意后才启用白名单模板，正则（原文匹配）`^自 ?\d{4}-\d{2}-\d{2} ?以来我们观察到的最低价`，start_date 固定 YYYY-MM-DD 完整格式，不适用 BR-TEXT-11 相对格式。组件本身归 BR-PRICE / Watch。
- 虚拟数据：虚拟原价、虚拟剩余名额、佣金头条播报、手填浏览数一律不做；淘礼金剩余份数必须来自接口实时值。首页公告条只展示公告 CMS 的内容，收益播报、成交播报、商品弹幕、写死的成团数同样不做（规划/07 §2、§5，规划/03 §6.3；2026-10-03 功能对照 G-33，07 原写「头条播报 P1」已按本条更正）。用真实数据做同类播报不属于虚拟数据，但同样默认不做；要做须负责人决定并先过隐私评估（2026-10-03 按编排会话裁定，待负责人确认，规划/06「功能对照待确认」）。
- 榜单类词（2026-10-03，功能对照 G-34；按功能对照 Q-27 默认 A 写，待负责人确认，规划/06「功能对照待确认」）：「高佣」「收益榜」在用户侧禁用。这两个词说的是按平台能拿多少佣金排序，出现在用户界面等于告诉用户这个榜不是按商品卖得好不好排的。「热销」「热推」「销量榜」不禁。后台与报表字段不校验这两个词（BR-WDR-29 的风险标签名里有「高佣」）。首页物料流与榜单可以选用哪些联盟频道，见 BR-TEXT-17 细则「联盟物料频道」。
- 后台命中返回 20001（data.fields 指出字段与命中词）。Agent 生成内容的禁用词处理见 BR-AI。
- 「佣金」例外（AI-17）：allow_keys 含 agent.disclaimer.commission（「推荐商品含推广链接，购买后本平台可能获得佣金」，BR-AI-10），只按原文整体匹配剔除；其他用户可见位置出现「佣金」仍命中。
- 语义预检（JEV-05，W4 随后台配置中心上线）：运营在后台保存文案（dict、texts、notify-templates、share 模板、pages、articles、商品池自定义标题）时，在禁用词校验之外调用 Jev 判断是否有变相说法（如「史低」「躺着也能返」暗示全网最低或稳赚、团队与层级说法、冒充平台官方）；命中只标黄提示，不拦截保存、不返回错误码；Jev 关闭、超时或不可用时静默跳过。只发送运营文案，不含用户个人信息（BR-AI-14）。禁用词硬拦截仍只按本条词表。
- 需同步（2026-09-30 C-02，未同步）：08 README §1.2 末段「用户侧禁用词（「返利到账」「佣金」「预估收益」「已结算」「返现」等）」删去「预估收益」「已结算」；specs/banned-words.yaml 建立时按本条现清单；规划/01 F-PRIV-09 只列原 6 个词，不需改。

例：运营在分享模板写「#标题# 全网最低价 #券后价#」→ 保存返回 20001「命中禁用词：全网最低、最低价」。字典 order_reason.PRICE_COMPARE.desc 含「比价」→ 通过；首页 banner 标题「比价神器」→ 命中。

#### BR-TEXT-14 细则 · 错误与降级话术

- 状态：默认假设（原标已确认；与 BR-PRICE-14 在 30142 上冲突（C-03），不满足「无争议」，删行后待 C-03 确认）
- 默认值：下表文案与动作为代理补全的默认值（依据 规划/03 §4.2、规划/04 §7）；码号以 08 §13.11 为准（04 §7 与之逐行一致）；30142 已废弃（BR-PRICE-14），券失效的提示与处理按 BR-PRICE-14，本表不再列 30142；表外码按本条通用规则兜底。
- 决策人：代理可自定（码号分配按 C-03，由负责人确认）
- 依赖平台能力：无
- 取代：
  - 规划/03 §4.2：「30131 显示「暂不支持该平台」；50301「该平台维护中」」
  - PRD修订_后端功能规划 7 降级表：「Agent 搜索故障「××平台暂时查不到」」
- 来源：规划/03 §4.2、§7.2；规划/04 §7；规划/02 §14；PRD v2.1 §10.5、§10.9；PRD修订_后端功能规划 2.12、7；PRD修订_双品牌与Agent找货 3.5、3.9；docs/changes/20261001-拍板第二批.md §8 ADD-01、ADD-02、ADD-07；拍板第二批 §8 ADD-08（30101 / 30102 auth_unavailable 文案与按钮）
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**表 A · 错误码文案**（键 error.&lt;code>；码值、含义、可重试以 13 §13.11 为准，本表只维护文案与按钮；「—」表示静默处理、不弹提示；变量缺失按 BR-TEXT-12 回落，带变量的行另给「包内默认」，保证变量缺失时仍有提示）

| 码 | 文案（字典默认） | 包内默认（变量缺失时） | 动作 |
| --- | --- | --- | --- |
| 10001 | 请先登录 | 同左 | 跳 Login，成功后恢复 pending_action；提现等四个需要二次验证的操作不自动恢复，登录后回到发起页，该次提交结果未知时进入待确认状态（表 C pending_confirm.\*，BR-ID-10 细则） |
| 10002 | — | — | 单飞刷新后重放；刷新失败按 10404 |
| 10003 | 为保障资金安全，请先完成短信验证 | 同左 | 弹短信验证，拿到 step_up_token 后重放 |
| 10004 | 请先阅读并同意相关授权 | 同左 | 按 data.consent_type 弹对应同意组件（组件内文案见 BR-ID-11、BR-ID-12、BR-ID-14；labor_agreement 弹劳务协议签署页，BR-WDR-31）。原请求是提现申请等需要二次验证的操作时（BR-ID-10 细则「不适用的动作」），不论哪种同意类型，同意或签署后回到发起页（提现回到 Withdraw、保留已输入金额），由用户重新点【提交】，不自动重放（BR-WDR-07 细则，2026-10-03 功能对照 G-12）；该次提交结果未知时回到发起页进入待确认状态（表 C pending_confirm.\*，BR-ID-10 细则） |
| 10005 | 请先绑定手机号 | 同左 | 跳 BindPhone，完成后恢复 pending_action；提现等四个需要二次验证的操作同 10001 |
| 10006 | 账号已被限制使用 | 同左 | 封禁说明页（原因类别 + 申诉入口，文案见 BR-TEXT-23） |
| 10007 | 账号注销处理中 | 同左 | data.stage=冷静期时跳注销进度页（可撤回），不弹本提示 |
| 10401 | 请求已失效，请重试 | 同左 | 不自动重放，上报埋点 |
| 10402 | — | — | 重新注册设备后重放 1 次；仍失败按「其他 5xxxx」 |
| 10403 | 请在 App 内操作 | 同左 | 不跳登录 |
| 10404 | 登录已过期，请重新登录 | 同左 | 清会话，跳 Login |
| 10405（新增，2026-10-03 功能对照 G-24；13 §13.11 登记） | 当前版本过低，请更新后继续使用 | 同左 | 进入 ForceUpdate 全屏拦截页（规划/03 §4.1）：标题与说明优先用版本检查接口返回的 update_title、update_notes，本文案作兜底；按钮（app_update.go_store）跳应用商店，另有「隐私政策」与「注销账号」（冷静期内为「撤销注销」）两个次要入口（表 C）；本机版本不低于 data.min_supported_version（或它为 null）而会话是受限作用域时，不进入强更页、不显示本文案（版本并不低），先刷新令牌，由用户重新操作（BR-ID-01 细则「受限会话」，第 2 轮评审后补；null 只出现在最低版本配置删除之前签发的受限令牌上，这一分支为第 3 轮评审后补）；不重放原请求；结果未知的那几类提交升级后仍是待确认，由用户确认或放弃上一笔（BR-ID-01 细则「最低支持版本的接口层拦截」、BR-ID-10 细则） |
| 20001 | 填写内容有误，请检查 | 同左 | data.fields 所列字段旁标红 |
| 20002 | 验证码错误，请重新输入 | 同左 | — |
| 20003 | 验证码已失效，请重新获取 | 同左 | — |
| 20004（新增，2026-10-03 功能对照 G-04；13 §13.11 登记） | 授权未完成，请重新授权 | 同左 | 第三方登录或第三方重新授权的凭证或授权尝试无效、已过期或已使用（BR-ID-04、BR-ID-08），对外不区分具体原因；回到登录页或二次验证面板，由用户重新发起第三方授权，不自动重放；data.reason=identity_mismatch 取表 B 子键 |
| 20901 | 请求内容有变化，请重新提交 | 同左 | 生成新幂等键，由用户重新提交 |
| 20902 | 状态已变化，请刷新后重试 | 同左 | 刷新详情 |
| 20903（新增，2026-10-03 第 2 批第 3 轮评审后；13 §13.11 登记） | 上一次提交已放弃，没有被处理 | 同左 | 结束该键的待确认状态，恢复提交入口，由用户重新提交（新幂等键）；不重放（BR-ID-10 细则「敏感操作的幂等键」） |
| 30101 | 购买前需完成淘宝授权，用于识别你的订单 | 同左 | AuthSheet |
| 30102 | 淘宝授权已失效，请重新授权 | 同左 | AuthSheet |
| 30103 | 当前淘宝账号暂不能获得返利，请联系客服 | 同左 | 【仍去购买（无返利）】【联系客服】 |
| 30104 | 授权已过期，请重新发起 | 同左 | 重新获取 auth_url 后发起授权（BR-ID-17） |
| 30111 | 购买前需完成拼多多授权 | 同左 | AuthSheet |
| 30121 | 京东这个商品暂不支持返利 | 同左 | 【仍去购买（无返利）】（BR-PRICE-08） |
| 30131 | 暂不支持这个链接或平台 | 同左 | — |
| 30132 | 这个口令暂时识别不了 | 同左 | 按钮「用商品名搜索」：预填口令文本中「」内或首行商品名，提取不到则搜索框留空 |
| 30141 | 商品已下架 | 同左 | 不外跳，卡片置灰（availability=off_shelf）；Agent 场景追加「换一批」（BR-PRICE-14） |
| 30143 | 商品信息已失效，请重新搜索 | 同左 | 跳搜索（BR-PROD-05） |
| 30144 | 购买链接已失效，正在重新获取 | 同左 | 重新请求转链（BR-ATTR-05）；App 内链接落地页（LinkLanding）不用本文案，显示表 C 的 link_landing.invalid 空态（2026-10-03） |
| 30151 | 这个淘宝账号暂时无法绑定到当前账号，本次购买无法获得返利 | 同左 | 【仍去购买（无返利）】【联系客服】；不透露对方账号与冷却原因（BR-ID-18、BR-ID-19） |
| 30153 | 该平台返利已被停用，请联系客服 | 同左 | 【仍去购买（无返利）】【联系客服】（BR-ID-17、BR-ID-18）；授权管理页只给【联系客服】（BR-ID-17 细则「授权管理页」，2026-10-03 功能对照 G-58） |
| 30201 | 没有找到这笔订单，请核对订单号；刚下单的订单可能还未同步，请稍后再试 | 同左 | — |
| 30202 | 这笔订单暂不能找回 | 同左 | 按 data.reason 取表 B 子键 |
| 30203 | 今日找回次数已用完，请明天再试 | 同左 | 按 data.reason 取表 B 子键 |
| 30204 | 这笔订单已被认领，无法找回 | 同左 | 不透露认领方信息 |
| 30205 | 你已提交过这笔订单的找回 | 同左 | 跳找回记录 |
| 30206 | 找回功能暂时关闭，请稍后再试 | 同左 | 找回入口置灰 |
| 30301 | 可提现余额不足 | 同左 | — |
| 30302 | 账户有待抵扣金额，抵扣完成前暂不能提现 | 同左 | 展示负余额说明（「待抵扣」口径见 BR-TEXT-01） |
| 30303 | 暂不满足提现条件 | 同左 | 按 data.reason 取表 B 子键 |
| 30304 | 请先完成实名认证 | 同左 | 跳 RealName；实名完成后回到发起页（从提现发起的回 Withdraw，从收款账号页发起的回收款账号页），由用户重新提交，不自动提交（BR-ID-10 细则「不适用的动作」、BR-WDR-07 细则） |
| 30305 | 请先绑定收款账号 | 同左 | 跳 PayoutAccount（支付宝或银行卡，BR-WDR-02、拍板第二批 FUND-03）；完成后回到 Withdraw，由用户重新提交（BR-WDR-07 细则） |
| 30306 | 提现功能暂时关闭，请稍后再试 | 同左 | 提现按钮置灰 |
| 30307 | 收款账号姓名与实名姓名不一致，请修改收款账号 | 同左 | 跳 PayoutAccount |
| 30308 | 该收款账号已被其他实名用户绑定，请更换账号 | 同左 | 跳 PayoutAccount；不透露对方信息 |
| 30309 | 未成年人提现受限 | 同左 | 展示未成年提现规则（BR-WDR-06） |
| 30401 | 邀请码无效 | 同左 | — |
| 30402 | 已绑定邀请人，不能重复绑定 | 同左 | — |
| 30403 | 不能绑定该邀请人 | 同左 | — |
| 30404 | 已超过补填邀请码的期限 | 同左 | — |
| 30405 | 该身份证已被其他账号实名 | 同左 | 不透露对方账号 |
| 30406 | 实名核验未通过，请核对姓名与身份证号 | 同左 | — |
| 30407 | 年龄不满足实名要求 | 同左 | — |
| 30408 | 邀请活动暂停 | 同左 | 落地页引导直接下载注册 |
| 30409 | 已有订单、找回申请或邀请记录，不能补填或修改邀请人 | 同左 | — |
| 30410 | 今日实名次数已用完，请明天再试 | 同左 | 不暴露身份证是否已被占用 |
| 30411 | 该手机号已注册，可退出后用手机号登录 | 同左 | data.reason=mergeable 时按表 B 30411.mergeable 处理（BR-ID-06） |
| 30412 | 有进行中的提现，提现完成后再申请注销 | 同左 | — |
| 30413 | 未满 18 周岁，暂不开放邀请与分享 | 同左 | 隐藏邀请与分享赚入口 |
| 30414 | 暂不支持自助更换手机号，请联系客服 | 同左 | — |
| 30415（新增，代理自定、负责人 2026-10-01 接受；13 §13.11 登记） | 本月昵称修改次数已用完，下月可再修改 | 同左 | —（BR-ID-39） |
| 30416（新增，拍板第二批 §8 ADD-07；13 §13.11 登记） | 账户有待扣回金额 {amount}，抵扣回正后才能注销 | 账户有待扣回金额，抵扣回正后才能注销 | {amount} 取 data.amount_fen，按 BR-TEXT-10 格式化；注销页展示该提示与【联系客服】，不进入冷静期（BR-ID-27） |
| 30501 | AI 助手暂未开放 | 同左 | 入口隐藏或置灰 |
| 30502 | 今日 AI 次数已用完，明天恢复，可以先用搜索找货 | 同左 | 跳搜索 |
| 30503 | 暂不支持这类内容 | 同左 | — |
| 30504 | 这个对话已结束，请新建对话 | 同左 | 新建会话 |
| 30505 | — | — | 刷新会话消息 |
| 30506 | 上一条还在回复中 | 同左 | 发送按钮保持禁用至当前 run 结束 |
| 30601 | 你已领取过该淘礼金 | 同左 | — |
| 30602 | 淘礼金已领完 | 同左 | 按钮置灰，给普通购买入口（BR-PRICE-14） |
| 30603 | 活动未开始或已结束 | 同左 | — |
| 30604 | 暂不满足领取条件 | 同左 | — |
| 30701 | 内容不存在或已下线 | 同左 | 显示空态 |
| 30801（P1） | 当前已达到目标价，可直接购买或调低目标价 | 同左 | — |
| 30802（P1） | 提醒数量已达上限，请先删除旧提醒 | 同左 | 列表显示已设数量 |
| 30803（P1） | 这个商品已有提醒 | 同左 | 跳到已有提醒（修改目标价） |
| 30804（P1） | 这个商品有已过期的提醒，可续期 | 同左 | 跳到已有提醒（续期） |
| 30805（P1） | 暂时无法获取价格，请稍后再试 | 同左 | — |
| 30806（P1） | 该平台提醒暂停服务 | 同左 | — |
| 40901 | 正在处理，请稍候 | 同左 | 保持加载态，稍后查询结果 |
| 42901 | 操作太频繁，请稍后再试 | 同左 | 按 Retry-After 禁用按钮，缺省 5 秒 |
| 44001 | risk_msg.&lt;code>；默认「操作未通过安全校验」 | 操作未通过安全校验 | 给申诉入口 |
| 44002 | 设备环境异常，暂不能操作 | 同左 | — |
| 44003 | — | — | 拉起人机验证组件，通过后重放 |
| 50001 | 出了点问题，请稍后再试（{trace6}） | 出了点问题，请稍后再试 | 重试 |
| 50301 | 按 data.reason 取表 B 子键；无 reason 时「{platform_name}维护中，请稍后再试」 | 该平台维护中，请稍后再试 | 见表 B |
| 50302 | AI 暂不可用，可以先用搜索找货 | 同左 | 只在无模型降级的关键词搜索也失败时返回（BR-AI-14，拍板第二批 AI-05）；跳搜索页并预填 data.fallback 中的关键词 |
| 50303 | 暂时无法确认价格，请稍后再试 | 同左 | 不外跳返利链接；主按钮「稍后再试」，次按钮「仍去购买（无返利）」（BR-PRICE-13、BR-PRICE-08） |
| 50304（新增，代理自定、负责人 2026-10-01 接受；13 §13.11 登记） | {platform_name}搜索暂不可用，请稍后再试 | 搜索暂不可用，请稍后再试 | 搜索无可用缓存时返回（BR-PROD-07，拍板第二批 TRADE-12）；搜索页显示空态与重试按钮，不改读商品池冒充搜索结果；data.reason=search_disabled 时按表 B 子键（2026-10-03 功能对照 G-47） |
| 50305（新增，2026-10-03 功能对照 G-04；13 §13.11 登记） | {provider_name}登录暂时不可用，请稍后再试或改用其他登录方式 | 该登录方式暂时不可用，请稍后再试或改用其他登录方式 | 第三方登录服务超时或故障（BR-ID-04）；provider_name 取 微信 / Apple / 华为账号（data.provider）；登录页保留其他登录方式，不自动重试 |
| 50401 | 出了点问题，请稍后再试（{trace6}） | 出了点问题，请稍后再试 | 重试 |
| 其他 5xxxx | 出了点问题，请稍后再试（{trace6}） | 出了点问题，请稍后再试 | 重试 |
| 表外码（字典与包内默认都没有该键） | 服务端 msg；msg 为空时「操作未完成，请稍后再试」 | 同左 | — |

**表 B · data.reason 子键**（键 error.&lt;code>.&lt;reason>；reason 未收录时用表 A 的 error.&lt;code>；reason 枚举以来源条目为准，新增 reason 必须同时在本表加行）

| 码.reason | 文案（字典默认） | 包内默认（变量缺失时） | 动作 / 变量来源 |
| --- | --- | --- | --- |
| 10403.h5_read_only（2026-10-03 第 3 批第 3 轮评审后） | 暂时无法操作，请稍后再试 | 同左 | 强更检查结果未知时 H5 拿到的只读令牌调用了写接口（BR-ID-32 细则「只读作用域」）；不拉起登录，H5 SDK 丢弃内存里的令牌，这次请求不自动重发（规划/03 §5.4） |
| 10405.no_account（2026-10-03 第 3 批第 3 轮评审后） | 这个账号还没有注册，请先更新 App 再注册 | 同左 | 客户端版本过低时登录，手机号或第三方账号没有对应的已有账号（受限登录只登录已有账号，BR-ID-01 细则「受限会话」）；没有建号；提示后回到 ForceUpdate，由用户去更新 |
| 20001.nickname_sensitive | 昵称含不允许使用的内容，请修改 | 同左 | BR-ID-39 |
| 20001.phone_invalid | 请输入 11 位中国大陆手机号 | 同左 | 手机号规范化不通过（BR-ID-05 细则「手机号规范化」，2026-10-03 功能对照 G-19）；手机号输入框旁提示，不发短信 |
| 20004.identity_mismatch | 请使用本账号已绑定的{provider_name}验证 | 请使用本账号已绑定的登录方式验证 | 二次验证时重新授权得到的第三方账号不是本账号绑定的那一个（BR-ID-08）；provider_name 取 微信 / Apple / 华为账号 |
| 30101.auth_unavailable | 淘宝暂时无法下单，请稍后再试 | 同左 | 站长授权过期或失效期间、淘宝绑定非 active 的用户（BR-ID-24，拍板第二批 §8 ADD-02、ADD-08）；不拉起 AuthSheet、不外跳，只给【知道了】，不提供【仍去购买（无返利）】 |
| 30102.auth_unavailable | 淘宝暂时无法下单，请稍后再试 | 同左 | 同上 |
| 30104.credential_invalid | 授权未完成，请重新授权 | 同左 | 淘宝授权凭证（授权码或 SDK 换得的访问令牌）无效、已过期、已使用或不能用于备案（BR-ID-17 细则「授权方式」）；客户端重新获取 auth_url，按新下发的 auth_methods 执行，没有可换的方式时按 BR-ID-18 的授权失败处理 |
| 30202.FACTOR_MISMATCH | 付款日期与订单不符，请核对后重新填写（预售订单填付定金日期） | 同左 | BR-ATTR-17 ④a |
| 30202.CLAIM_EXPIRED | 已超过找回期限，无法提交 | 同左 | BR-ATTR-17 ④b |
| 30202.ORDER_INVALID | 这笔订单已失效，无法找回 | 同左 | BR-ATTR-17 ④c |
| 30202.ALREADY_YOURS | 这笔订单已在你的订单列表中 | 同左 | BR-ATTR-17 ④e |
| 30203.RISK_BLOCKED | 今日暂时无法提交找回，请明天再试 | 同左 | 不透露风控原因（BR-ATTR-19） |
| 30303.account_frozen | 提现已暂停，如有疑问请联系客服 | 同左 | 不透露冻结来源（BR-WDR-05） |
| 30303.below_min | 单笔最低提现 {min_amount} | 提现金额低于单笔最低金额 | 变量取 GET /v1/withdrawals/rules 的限制值（对应 withdraw.min_amount_fen），按 BR-TEXT-10 格式化 |
| 30303.not_multiple | 提现金额需为 {amount_step} 的整数倍 | 提现金额不符合整数倍要求 | 同上（withdraw.amount_step_fen） |
| 30303.above_max | 单笔最多提现 {max_amount} | 超过单笔最高提现金额 | 同上（withdraw.max_amount_fen） |
| 30303.net_too_small | 扣除税费后实际到账金额过低，请提高提现金额 | 同左 | BR-WDR-03 ⑨ |
| 30303.daily_count | 今日提现次数已用完（每日 {daily_count} 次），请明天再试 | 今日提现次数已用完，请明天再试 | 同上（withdraw.daily_count_per_user，每人每日，拍板第二批 §8 ADD-06） |
| 30303.monthly_count | 本月提现次数已用完（每月 {monthly_count} 次） | 本月提现次数已用完 | 同上（withdraw.monthly_count_per_user） |
| 30303.payee_daily_users | 该收款账号今日暂不能再收款，请明天再试 | 同左 | 不透露其他会员信息 |
| 30303.self_purchase_required | 需有近期已确认收货的自购订单才能提现 | 同左 | BR-WDR-04（天数与门槛不写入文案，BR-TEXT-13） |
| 30303.payout_account_change_limit | 本月收款账号变更次数已用完，下月可再变更 | 同左 | BR-WDR-02 |
| 30303.payout_account_verify_limit | 今日收款账号核验次数已用完，请明天再试 | 同左 | BR-WDR-02 细则「核验次数上限」（2026-10-03 功能对照 G-13）；不透露核验结果，不说明次数 |
| 30411.mergeable | 该手机号已注册。可将当前{provider_name}登录并入该手机号账号，并入后当前账号停用 | 该手机号已注册，可将当前登录方式并入该手机号账号 | 按钮【并入】【取消】；【并入】凭 data.merge_ticket 调并号接口（BR-ID-06，拍板第二批 OPS-04）；provider_name 取 微信 / Apple / 华为账号 |
| 50301.maintenance | {platform_name}维护中，请稍后再试 | 该平台维护中，请稍后再试 | 购买按钮置灰「稍后再试」；Toast 显示文案 |
| 50301.not_launched | {platform_name}返利即将开放 | 该平台返利即将开放 | 卡片购买按钮置灰并显示该文案（即 platform_coming_soon），不弹 Toast |
| 50304.search_disabled | {platform_name}暂不提供搜索，可以粘贴商品链接查返利 | 该平台暂不提供搜索，可以粘贴商品链接查返利 | 该平台搜索开关关闭（BR-PROD-10 细则「按平台的搜索开关」，2026-10-03 功能对照 G-47）；不显示重试按钮，给【粘贴链接查返利】；三家都关闭时搜索页用同一句（{platform_name} 缺省按包内默认）；Agent 用 BR-TEXT-22 的 agent.notice.search_disabled |

**表 C · 降级场景文案**（非错误码）

| 场景 | 文案 | 动作 |
| --- | --- | --- |
| Agent 单平台搜索失败 | {platform_name}暂时查不到 | 其他平台结果照常展示 |
| Agent SSE 断线 | 连接中断 | 重试按钮 |
| 淘宝未安装（H5 未验证归因时） | 安装淘宝后下单才有返利，口令已复制 | 复制口令 |
| 京东/拼多多未安装或鸿蒙降级到网页 | 将通过浏览器打开{platform_name} | — |
| 鸿蒙淘宝降级 H5 | 鸿蒙版可能影响返利跟踪，如未显示订单可申请找回 | — |
| 某端全部路径丢归因 | 本设备暂不支持{platform_name}返利 | 隐藏购买按钮 |
| 淘宝客户端 SDK 不可用 jump.taobao_sdk_unavailable | 暂时无法打开淘宝，请稍后再试 | 百川初始化重试后仍失败、且本次没有可执行的后续步骤时显示；不外跳，不给无返利购买（BR-ATTR-27 淘宝行说明，2026-10-03 功能对照 G-50） |
| 待跟单卡（pending_track_card） | 订单同步中｜在{platform_name}下单后，订单通常会在一段时间内同步到这里，同步可能有延迟（CAP-\*-07 实测后改为「最长约 {n} 分钟」，n 取 order_sync.delay_hint_min.&lt;platform>） | 找回入口「未跟单？去找回」的出现条件按 BR-ATTR-17、BR-ATTR-21 |
| platform_coming_soon（= error.50301.not_launched，表 B） | {platform_name}返利即将开放 | 卡片按钮；只在 50301 data.reason=not_launched 时出现 |
| platform_no_rebate | {platform_name}暂不支持返利 | — |
| claim_required（用户键不可用平台，订单页与商品卡） | {platform_name}返利需下单后提交订单号认领 | 走找回 |
| no_rebate_hint | 当前不计返利 | — |
| pdd.parse_failed（拼多多链接识别不到商品，CAP-PDD-01） | 暂时无法识别这个拼多多链接 | 按钮「用商品名搜索」（预填规则同 30132），不自动列候选卡（拍板第二批 TRADE-07） |
| rebate_amount_unknown（rebate_basis=amount_unknown，取值与判定见 04 §8.3、BR-PRICE-08） | 可返利，金额以订单为准 | 替代 RebateTag；不显示「预估返」「预估返后」任何金额；购买经 links/open 转链并带用户归因参数（拍板第二批 TRADE-08） |
| rebate_login_to_view（rebate_basis=login_required，BR-AI-11，拍板第二批 AI-03） | 登录查看返利 | 替代 RebateTag，卡片按钮同文案；点击走登录，登录后按 BR-ATTR-05 处理；只在开关 agent.guest_login_to_view.&lt;platform> 开启的平台出现 |
| spec_min_price_note（商品级价格对应规格无法确定，BR-PROD-04） | 规格以下单页为准 | 价格旁显示；确知为最低规格价或联盟返回区间时价格写「¥x 起」（BR-PROD-04） |
| 剪贴板识别提示条 clipboard.prompt | 检测到商品链接，查返利？ | 出现条件、读取时机与方式只按 BR-ID-16 |
| 剪贴板邀请提示条 clipboard.invite_prompt | 检测到好友邀请码 {invite_code}，绑定为邀请人？ | 出现条件按 BR-INV-04（商品优先；含落地页链接或「邀请码」字样才提示，拍板第二批 OPS-06），读取方式只按 BR-ID-16；点击后进入绑定确认，不直接绑定 |
| 购买请求超时 buy.timeout | 网络不稳定，请重试 | 重试沿用同一幂等键，不自动外跳（超时时长与重试规则归 规划/03 §4.2，拍板第二批 TRADE-22） |
| 购买请求进行中 buy.opening / buy.opening.cancel | 正在打开{platform_name}｜取消 | 点击购买、open 请求发出后的加载层；只写平台名，不显示金额，不出现返利与券相加的合计（BR-PRICE-05）；点【取消】、离开页面或 App 进入后台后，之后到达的响应只更新卡片、不外跳，用户再点购买才外跳（规划/03 §4.5，2026-10-03 功能对照 G-46）；包内默认：正在打开｜取消 |
| 显示上次数据 net.stale_data | 网络不可用，以下为 {time} 的数据 | 订单、钱包页请求失败时显示缓存数据并附本提示；{time} 按 BR-TEXT-11（拍板第二批 TECH-20，代理起草） |
| H5 加载失败 h5.load_failed | 页面加载失败，请重试 | 重试按钮（TECH-20，代理起草） |
| 第三方页容器里的平台商品无法识别 external_page.product_unresolved | 该商品暂无法查返利 | 留在当前页，不在容器里继续打开这个商品页（BR-ATTR-29，2026-10-03 功能对照 G-02） |
| 第三方页容器里拦下的平台页面 external_page.union_host_blocked | 这个页面暂不支持在这里打开，可以在 App 内搜索商品 | 按钮只有【去搜索】；不提供「继续访问」，也不提供交给浏览器或平台 App 打开的入口；原页面保持不动；内嵌框架被拦下时同一页面只提示一次（BR-ATTR-29 ②（b），2026-10-03） |
| 第三方页容器不处理下载 external_page.download_blocked | 这里不能下载，请在浏览器中打开后下载 | 容器取消下载请求后提示一次；只在当前页有系统浏览器出口时用，配合标题栏【在浏览器打开】（规划/03 §5.1，2026-10-03 功能对照 G-21） |
| 第三方页容器不处理下载（无浏览器出口）external_page.download_unsupported | 这里不支持下载 | 当前页没有系统浏览器出口时（平台页面、推广链接，BR-ATTR-29 细则）用这一句，不提浏览器（2026-10-03 评审补） |
| 第三方页容器标题栏 external_page.open_in_browser | 在浏览器打开 | 用系统浏览器打开当前页面地址，只在用户点击时触发；当前页命中平台链接形态表任一类别时不显示（BR-ATTR-29 细则「容器内的非 https 跳转、下载与系统浏览器出口」，规划/03 §5.1） |
| 上一次提交待确认·标题 pending_confirm.title | 上一次提交的结果还没有确认 | 提现申请、收款账号变更、换手机号、申请注销四个操作的发起页进入待确认状态时显示；此时新的提交入口置灰（BR-ID-10 细则「敏感操作的幂等键」，2026-10-03 第 2 轮评审补） |
| 待确认·提现 pending_confirm.withdraw.desc / .action | 上一笔提现 {amount} 还没有收到结果，收款账号 {payout_account}，请先确认 / 确认上一笔提现 | {amount} 取本机未决记录，按 BR-TEXT-10 格式化；{payout_account} 取服务端当前绑定的收款账号（脱敏，BR-TEXT-06）；包内默认：上一笔提现还没有收到结果，请先确认。点击后用原幂等键重发（BR-WDR-07 细则「前置步骤的回流」） |
| 待确认·收款账号 pending_confirm.payout_account.desc / .action | 上一次提交的收款账号 {payout_account} 还没有收到结果，请先确认 / 确认上一次提交 | {payout_account} 取本机未决记录的脱敏摘要；包内默认：上一次提交还没有收到结果，请先确认 |
| 待确认·换手机号 pending_confirm.phone_change.desc / .action | 上一次提交的新手机号 {phone} 还没有收到结果，请先确认 / 确认上一次提交 | {phone} 为脱敏后的新手机号；包内默认同上 |
| 待确认·注销 pending_confirm.deletion.desc / .action | 上一次提交的注销申请还没有收到结果，请先确认 / 确认上一次提交 | — |
| 待确认·暂时确认不了 pending_confirm.retry_later | 暂时无法确认，请稍后再试 | 确认或放弃时得到 42901、5xxxx 或没有响应，确认时得到 40901，保持待确认状态（第 3 轮评审后补放弃） |
| 待确认·按原内容确认不了 pending_confirm.cannot_confirm | 按上一次的内容暂时确认不了，可以稍后再试，或放弃后重新提交 | 确认时得到 20903 以外的 2xxxx（例如收款方式已关闭的 20001、换手机号验证码已失效的 20003），键不结束，保持待确认状态，不在表单字段旁标红（BR-ID-10 细则「敏感操作的幂等键」，2026-10-03 第 3 轮评审补） |
| 待确认·放弃按钮 pending_confirm.withdraw.abandon / pending_confirm.abandon | 放弃上一笔提现 / 放弃上一次提交 | 前者用于 Withdraw，后者用于收款账号、换手机号、注销三个发起页；与确认按钮并列，都由用户点击（第 3 轮评审补） |
| 待确认·放弃二次确认 pending_confirm.abandon.confirm / .ok / .cancel | 放弃后，上一次提交如果还没有被处理，以后也不会再被处理；如果已经处理完，会显示处理结果 / 确定放弃 / 再想想 | 点放弃按钮后弹出；点【确定放弃】才调作废接口（第 3 轮评审补） |
| 待确认·已放弃 pending_confirm.abandoned | 上一次提交已放弃，可以重新提交 | 作废接口返回已作废后显示，同时删除未决记录、恢复提交入口；确认得到 20903 时用表 A 的 error.20903（第 3 轮评审补） |
| 待确认·放弃时正在处理 pending_confirm.abandon_busy | 上一次提交正在处理，暂时不能放弃，请稍后再试 | 作废接口返回 40901 时显示，保持待确认状态（第 3 轮评审补） |
| 待确认·放弃时已处理完 pending_confirm.already_done | 上一次提交已经处理完成 | 作废接口返回原结果（outcome=completed）时显示，随后按原结果展示（提现单、换绑结果或原结果的错误文案），删除未决记录、恢复提交入口（第 3 轮评审补） |
| App 内链接落地页·分享者本人提示 link_landing.owner_hint | 这是你分享的商品，自己购买按自购返利计算 | 只在 `GET /v1/links/{link_id}` 返回 viewer_is_sharer=true 时显示；不显示金额（BR-ATTR-11，2026-10-03 功能对照 G-03） |
| App 内链接落地页·链接失效 link_landing.invalid | 链接已失效 | 30144 时显示空态与按钮【去搜索】，不自动重试（BR-ATTR-05 细则） |
| 分享中间页按钮 share_page.open_in_app | 在 App 中打开 | App 外浏览器里显示；微信内不显示；`open_in_app_url` 为 null 时不显示；文案不得带返利、红包等利益表述（BR-ATTR-05 细则，规划/09 CAP-X-03） |
| 分享中间页·微信内引导 share_page.open_in_browser_hint | 请点右上角，选择在浏览器打开 | 只在微信内显示，代替【在 App 中打开】与【复制淘口令】（规划/03 §8.3） |
| 分享中间页按钮 share_page.copy_tpwd | 复制淘口令 | 只在接口响应带 `tpwd_ticket` 时显示（微信内不显示）；点击时才取口令并写入剪贴板，成功后提示「已复制淘口令」（share_page.copy_tpwd.done）（BR-ATTR-10 细则，2026-10-03） |
| 下载引导页按钮 download_guide.download / download_guide.reopen | 下载 App｜已安装，重新打开 | 非分享链接的深链没有拉起 App 时显示的静态页；【已安装，重新打开】重新访问原深链；页面不展示任何链接内容（BR-ATTR-05 细则，2026-10-03） |
| 第三方新号绑手机引导 invite.bind_phone_guide.title / .body | 绑定手机号｜绑定手机号后，可在期限内填写邀请码。已用手机号注册过的，绑定同一个手机号、符合条件时可把当前登录方式并入原账号 | 按钮【去绑定】【暂不】；出现条件按 BR-INV-03 细则（2026-10-03 功能对照 G-05）；并号条件只按 BR-ID-06，文案不写天数（BR-TEXT-13） |
| 第三方新号绑手机引导·购买前版本 invite.bind_phone_guide.body_before_buy | 绑定手机号后，可在期限内填写邀请码。已用手机号注册过的，绑定同一个手机号、符合条件时可把当前登录方式并入原账号。下单后将不能再填写邀请码，也不能并入原账号 | 登录由点击购买触发时用这一版，按钮同上；【暂不】后继续本次购买（BR-INV-03 细则） |
| 首次购买前邀请码提示 invite.before_buy_tip | 下单后将不能再填写邀请码。有邀请码可以先填写 | 按钮【先填邀请码】【继续购买】；每个账号一次，服务端记已读（BR-INV-03 细则） |
| 对被邀请人的告知 invite.notice_inviter | 绑定后，你订单带来的收益金额和状态会通知邀请你的人，不含商品信息 | 邀请落地页（协议勾选框上方）、App 内注册页邀请码输入框下方、补填页、剪贴板邀请口令的绑定确认页；只作告知，不加勾选框（BR-INV-16 细则「对被邀请人的告知」、BR-INV-18，2026-10-03 功能对照 G-16） |
| 授权管理页 auth_manage.title / .status.authorized / .status.unauthorized / .action.authorize | 授权管理｜已授权｜未授权｜去授权 | 只有这两种状态文案，不显示账号名、昵称、头像与授权时间；blocked 时不给【去授权】，改显示 error.30153 与【联系客服】（BR-ID-17 细则「授权管理页」，2026-10-03 功能对照 G-58） |
| 授权管理页说明 auth_manage.rebind_note | 暂不支持自助更换授权的淘宝账号，需要时请联系客服 | 页面底部固定显示（BR-ID-19） |
| 登录页求助入口 login.help_entry | 登录遇到问题 | 登录页文字入口，打开 help_links.login_help 的帮助文章，未配置时打开帮助中心首页；无需登录（BR-ID-02 细则「未登录时的隐私入口」，2026-10-03 功能对照 G-18） |
| 微信登录拉不起 login.wechat_unavailable | 未安装微信，请使用其他方式登录 | 检测为未安装时不显示微信登录按钮；本提示只在检测结果未知、点击后拉不起微信时出现，登录页保留其他登录方式（BR-ID-04 细则「未安装微信时」，2026-10-03 功能对照 G-31） |
| 微信分享不可用 share.wechat_unavailable | 未安装微信，可以复制后分享 | 未安装时分享面板不列微信渠道，保留复制、保存海报与系统分享；H5 指定微信渠道而本机没有微信时提示一次（BR-ID-04 细则） |
| 客服入口·未安装微信 cs.wechat_unavailable | 未安装微信，无法直接打开客服。可以复制客服链接，在装有微信的设备上打开 | 按钮【复制客服链接】【去帮助中心】；不直接打开客服链接（BR-ID-04 细则） |
| 客服入口·未安装微信的按钮 cs.copy_link / cs.go_help | 复制客服链接｜去帮助中心 | 只在上一行的提示里出现；复制的是 /v1/config kf 里的客服链接 |
| 更新提示的按钮 app_update.go_store / app_update.later | 去更新｜暂不更新 | 【去更新】跳应用商店，是强更页（ForceUpdate）唯一的按钮，强更页另有下一行的次要入口（第 2 轮评审后改）；【暂不更新】只出现在可关闭的更新提示里，记录方式见 规划/03 §4.1（2026-10-03 功能对照 G-24）。标题与说明取版本检查接口的 update_title、update_notes，没有时用 error.10405 |
| 强更页的次要入口 app_update.privacy_policy / app_update.delete_account / app_update.cancel_deletion | 隐私政策｜注销账号｜撤销注销 | 只在强更页出现，样式弱于【去更新】。「隐私政策」打开隐私中心（强更状态下只显示协议、两份清单与【撤回同意】）；「注销账号」进入注销流程，账号在冷静期内时这一项显示「撤销注销」，未登录时先显示「注销账号」、登录后按注销进度进入申请或撤销；完成或取消后回到强更页（规划/03 §4.1，BR-ID-01 细则「受限会话」；2026-10-03 第 3 批第 2 轮评审后补） |
| 比价无返利弹窗 no_rebate.price_compare.confirm | 这件商品这次被判为比价，没有返利 | 只在 open 响应 no_rebate_cause=price_compare 时出现，代替「该商品当前暂无返利，继续购买？」；按钮【看看相似商品】（no_rebate.price_compare.similar）【仍去购买（无返利）】，可关闭；不显示任何返利金额，不写「过几小时再买」之类的建议（BR-PRICE-08 细则「无返利原因」，2026-10-03 功能对照 G-09；开关默认关） |
| 比价无返利卡片原因行 no_rebate.price_compare | 这次被判为比价，没有返利 | 卡片按 open 响应换成无返利态后显示在返利位置，旁边保留文字入口【看看相似商品】；其他无返利情形仍显示「暂无返利」 |
| 相似商品入口 no_rebate.price_compare.similar | 看看相似商品 | 进入搜索页，平台同原商品，搜索词取卡片标题，去掉原商品（BR-PRICE-08 细则） |
| 订单列表查询范围提示 order_list.history_hint | 只显示 {date} 之后的订单，更早的订单请联系客服 | 包内默认：更早的订单请联系客服。只在服务端返回 earliest_visible_date 时显示在列表底部；{date} 按 BR-TEXT-11 的纯日期格式；默认配置不限制范围，此时不显示（BR-ID-30 细则「订单类记录」，2026-10-03 功能对照 G-14） |
| 订单列表状态分组 order_status_group.all / .estimating / .credited / .no_rebate | 全部｜预估中｜已结算｜无返利 | 订单列表自购、分享子 Tab 下的分组 Tab，成员只按 BR-TEXT-02 细则「订单列表的状态分组与查找」；不得改成「待结算」「结算中」（BR-TEXT-13）（2026-10-03 功能对照 G-60） |
| 订单列表筛选与搜索 order_list.filter.platform / .filter.month / .search.placeholder | 平台｜月份｜搜订单号或商品名 | 分享子 Tab 的搜索框提示改用 order_list.search.placeholder_share「搜商品名」（分享单不按单号搜）（2026-10-03 功能对照 G-60） |
| 预售单定金金额 order_list.deposit_amount | 已付定金 {amount} | display_status=DEPOSIT_PAID 且 pay_amount_fen 不为 null 时代替实付金额显示；{amount} 按 BR-TEXT-10（BR-TEXT-02 细则「预售单的付款金额」，2026-10-03 功能对照 G-63） |
| 预售单时间线 order_timeline.deposit_paid / order_timeline.final_paid | 付定金 {time}｜付尾款 {time} | 只用于预售单；没有定金时间时 order_timeline.deposit_paid 只显示「付定金」（BR-TEXT-02 细则「时间线」） |
| 订单详情查看商品 order_detail.view_product | 查看商品 | 订单详情商品信息区的入口，显示条件见 BR-TEXT-02 细则「详情页的「查看商品」」（2026-10-03 功能对照 G-62） |
| 金额隐藏开关 amount_mask.hide / amount_mask.show | 隐藏金额｜显示金额 | 「我的」、钱包、订单页金额区小眼睛按钮的无障碍标签；隐藏时金额统一显示「****」（BR-TEXT-10 细则「金额隐藏」，2026-10-03 功能对照 G-64） |
| 找回指引入口 claim.guide.entry | 订单号在哪里找？ | 找回表单订单号输入框下方；打开 help_links.claim_guide.&lt;platform> 的帮助文章，未配置时不显示（BR-ATTR-17 细则「找回页的填写指引」，2026-10-03 功能对照 G-15） |
| 找回指引·订单号 claim.guide.order_no | 请填写{platform_name}订单详情页显示的订单编号，整串填写；主订单号、子订单号都可以 | 包内默认：请填写订单详情页显示的订单编号，整串填写。选定平台后显示 |
| 找回指引·付款日期 claim.guide.paid_date | 请填写付款成功的日期；预售订单填付定金的日期 | 付款日期输入框下方 |
| 找回指引·期限 claim.guide.window | 付款后 {claim_window_days} 天内可以申请找回 | {claim_window_days} 取 `/v1/config` 的 `claim.window_days`（服务端由 claim.window_hours 向下取整到天派生，BR-ATTR-17 细则「找回页的填写指引」）；为 null 时整句不显示（BR-TEXT-12），不写死天数（BR-TEXT-13）；帮助文章里不写期限数字 |
| 找回指引·核对提示 claim.guide.caution | 填错会占用今天的找回次数，请核对后再提交 | 提交按钮上方；不写具体次数 |

**表 D · 隐私与权限文案**（2026-10-03，功能对照 G-25、G-26、G-28；键名与用途由本表定，包内默认文案由法务定稿，规划/06 Q-F14。「要点或占位措辞」一列里的成句文字是代理起草的占位措辞，供开发与内测包使用，法务定稿后替换；占位稿不得用于提审与公开版本）

| 键 | 用在哪里 | 要点或占位措辞 | 说明 |
| --- | --- | --- | --- |
| privacy.first_launch.title / .summary | 首启隐私弹窗的标题与摘要 | 要点：收集哪些个人信息、各自的用途；接入了哪些第三方 SDK；用户可以查阅、撤回同意、注销；《隐私政策》《用户协议》链接。全文由法务提供 | 按钮固定为【同意】【不同意】（BR-ID-11；键见下文 privacy.btn.\*）；同意前显示，只能取包内默认或已缓存的配置 |
| privacy.second_notice.body | 点【不同意】后的二次说明 | 要点：不同意时只能用基本模式浏览，不能登录、不能获得返利；之后可以随时开启完整功能。全文由法务提供 | 按钮【同意】【仍不同意】；Android、鸿蒙可另给【退出 App】，iOS 不提供（BR-ID-11；键见 privacy.btn.\*） |
| privacy.btn.agree / .disagree / .still_disagree / .exit_app | 首启弹窗与二次说明的按钮 | 同意｜不同意｜仍不同意｜退出 App | 按钮的含义与出现位置按 BR-ID-11，不因文案调整而改变；.exit_app 只在 Android、鸿蒙出现 |
| privacy.basic_mode.notice / .enable | 基本模式页的说明与按钮 | 当前为基本模式，只能浏览。开启完整功能后可以登录、查返利｜开启完整功能 | 点按钮重新展示首启弹窗（BR-ID-02、BR-ID-11） |
| privacy.withdraw.confirm.title / .body | 隐私中心【撤回同意】的确认框 | 撤回同意｜撤回后本机会退出登录并进入基本模式，只能浏览。账号和数据不会删除；要删除请使用账号注销 | 按钮【确认撤回】【取消】（键 privacy.withdraw.confirm.ok / .cancel）；规则见 BR-ID-13 |
| perm.push.card_hint / perm.push.cta | 待跟单卡里的通知说明行与按钮 | 开启通知，跟单成功、返利结算和提现到账时会及时提醒你｜开启通知 | 出现条件与时机见 BR-ID-13 细则「通知权限的申请时机」（功能对照 G-25；按功能对照 Q-21 默认 A，待负责人确认）；不写「开启后才有返利」之类的话，不承诺通知的具体时限。card_hint 同时是通知权限的用途说明键：权限申请组件申请 push 时（含经桥方法申请）取这一句，不另设 perm.push.purpose（规划/03 §4.9 的映射） |
| perm.push.guide_bar | 「我的」页的通知引导条 | 通知没有开启，跟单和提现到账的消息可能收不到。去开启 | 可关闭；点击跳到系统里本 App 的通知设置（BR-ID-13 细则） |
| perm.push.denied_forever | 通知权限已被拒绝、系统不再询问时的引导 | 通知权限已关闭，可以在系统设置中开启 | 配【去设置】 |
| perm.photos.purpose | 保存图片前的用途说明 | 用于把商品海报、邀请海报保存到你的相册 | photos 类型的用途说明键（规划/03 §4.9 的映射）；只申请写入相册，不读取相册里的内容（BR-ID-13） |
| perm.btn.continue | iOS、鸿蒙权限说明页上的按钮 | 继续 | 点后立刻弹系统授权框；不写「允许」「同意」这类冒充系统选项的字样；Android 用顶部浮层，不需要这个按钮（规划/03 §4.9；2026-10-03 评审后补） |
| perm.photos.system_purpose | 写进系统权限声明的用途说明（iOS 的相册写入用途说明） | 用于把你选择保存的海报图片存入相册 | 构建时由生成器从 contracts/texts.default.json 写入工程，不随配置下发；与权限清单 specs/system-permissions.yaml 的条目一一对应（规划/03 §4.9，功能对照 G-28）。SDK 带进来、需要补用途说明的权限按同样方式加键，写这个 SDK 的真实用途 |
| perm.photos.denied_forever | 相册权限已被永久拒绝时的引导 | 没有相册权限，无法保存图片。可以在系统设置中开启 | 配【去设置】 |
| perm.go_settings | 权限引导里的按钮 | 去设置 | 跳到系统里本 App 的设置页 |

- 包内默认必须齐全：首启弹窗在同意之前显示，那时不能依赖网络。
- 改这些键的文案按协议类内容管理：后台归 `content.agreement` 权限点（规划/04 §11.2），保存时填法务确认人并写审计；只有普通配置权限的账号改不了。这一归属是代理补全的默认假设，待负责人确认（规划/06「功能对照待确认」）。
- 文案同样过 BR-TEXT-13 校验；系统权限怎样申请、被拒后怎样处理见 BR-ID-13 与 规划/03 §4.9，本表只管文案。

例：京东转链开关关闭（原因 maintenance）→ 接口返回 50301、data.reason=maintenance → Toast「京东维护中，请稍后再试」，卡片按钮变灰显示「稍后再试」。拼多多因备案互斥或权限未批保持关闭（原因 not_launched）→ 50301、data.reason=not_launched → 不弹 Toast，卡片按钮置灰显示「拼多多返利即将开放」。trace_id 以 …c3d4e5 结尾 → 显示「（c3d4e5）」；trace_id=abc → 显示「（abc）」。30416 且 data.amount_fen=500 →「账户有待扣回金额 ¥5，抵扣回正后才能注销」。30303 reason=below_min、rules 返回最低 100 分 →「单笔最低提现 ¥1」；rules 未返回该值 →「提现金额低于单笔最低金额」。

- 50301 的 data.reason（新增，默认处理，待负责人确认）：maintenance = 维护或熔断（运营临时关闭、转链熔断）；not_launched = 该平台权限未批、验证未通过或备案互斥等尚未放量的关闭。服务端按配置 convert.off_reason.&lt;platform> ∈ {maintenance, not_launched}（新增，默认 maintenance）填写，熔断触发的关闭一律 maintenance；50301 仍只用于 convert.enabled.&lt;platform> 关闭（BR-PRICE-13）。需同步：13 §13.11 与 规划/04 §7 的 50301 行加 data.reason，04 §10.2 加 convert.off_reason.&lt;platform>，10 AC-S1-28-PDD 断言 reason=not_launched 与「即将开放」文案（AC-S1-15 保持 maintenance）。
- 文案来源一律为字典 error.&lt;code> / error.&lt;code>.&lt;reason>（BR-TEXT-12）；13 §13.11「客户端动作」列中「显示服务端 msg」的码，文案同样取本表 error.&lt;code>，需同步把该列改为「取 error.&lt;code>」。服务端返回的 msg 由同一份 contracts/texts.default.json 生成，与包内默认一致，只在客户端没有该键时显示。
- 规则正文中已写的提示句（BR-ID-17 的 30104、30153，BR-PRICE-13 的 50303 按钮，BR-PROD-05 的 30143 等）以本表为文案唯一维护处，措辞不一致时以本表为准，来源条目只保留判定与动作。

- risk_msg 字典后台可编辑，保存过 BR-TEXT-13 校验，不得写风控规则细节。
- 错误码编号以 08 §13.11 为准（04 §7 与之逐行一致）；后端功能规划 30201–30209 的映射见 BR-WDR-03 细则（非逐号对应，如 30206→30307、30207→30303）。
- 30142 原行「这个券已领完｜展示当前价」已删除：码值废弃后不回收、不复用；客户端收到 30142（旧版本服务端）按表 A「表外码」行处理（显示服务端 msg）。
- 44001 在本表只指风控拦截；更换手机号开关关闭改用 30414（BR-ID-06），不走 risk_msg。
- 30152 随取消用户自助换绑废弃（拍板第二批 §8 ADD-01），原行「暂不能换绑，{available_at} 后可再次换绑」已删除；客户端收到 30152（旧版本服务端）按表 A「表外码」行处理。
- 外跳与未安装降级（G-04）：路径（平台 × 端 × 已装/未装的首选与降级）以 BR-ATTR-27 为准，本表只维护按钮与提示文案；每条路径在对应 CAP-\*-11 验证通过前是条件项，不得对外承诺；只有点击时才外跳（BR-ATTR-21）。「淘宝未安装」原文案「口令已复制，打开淘宝即可领券」已取代（09 A-27：未安装时该提示无法继续）；CAP-TB-11 证实 H5 下单保留归因时改为系统浏览器打开 H5，不出该提示。默认处理，待负责人确认。
- 待跟单卡（G-05）：显示与消失条件只按 BR-ATTR-21，找回入口出现条件只按 BR-ATTR-17，本表不复述时长；CAP-\*-07 实测前同步延迟不写具体分钟数。默认处理，待运营（BR-ATTR-21 决策人）确认。
- 平台能力降级文案（G-06，代理已定）：platform_coming_soon、platform_no_rebate、claim_required、no_rebate_hint 沿用 规划/09 CAP-TB-05、CAP-TB-07、CAP-JD-05、CAP-MT-05「不支持时怎么办」列原措辞；pdd.parse_failed、rebate_amount_unknown、spec_min_price_note 取自 CAP-PDD-01 降级列，其中「多规格商品显示最低规格价，以拼多多下单页所选规格为准」统一为 BR-PROD-04 写法「规格以下单页为准」+「¥x 起」。只换维护位置；09 该列只描述行为，以键名引用本表（需同步：09 CAP-PDD-01 降级列改引用这三个键）。platform_coming_soon 只由 50301 data.reason=not_launched 触发（见上）。
- rebate_amount_unknown（已确认，拍板第二批 TRADE-08：启用「可返利，金额以订单为准」，经 links/open 转链带用户参数，不显示金额）：卡片状态「可返利但金额未知」对应 rebate_basis=amount_unknown（rebate_min_fen、rebate_max_fen 为 null）；本表只维护文案，判定条件只在 BR-PRICE-08 维护。需同步：04 §8.3 rebate_basis 取值加 amount_unknown，BR-PRICE-08 补判定条件（如 CAP-PDD-01 拿不到 goods_sign、经 zs.unit.url.gen 转链成功），BR-PRICE-21 三态补该取值的归属。
- pdd.parse_failed（TRADE-07）：与 30132 / AC-S1-08 统一为「报错 + 用商品名搜索」，京东无权限、拼多多识别失败都不自动列候选卡；原写「按 CAP-PDD-01 用文案标题检索并列出候选卡」作废。
- 购买按钮文案按 BR-TEXT-12 细则（TRADE-21）；本表各错误码动作中的「仍去购买（无返利）」只用于错误弹窗次按钮。
- 剪贴板提示条（G-20）：读取时机与方式（iOS detectPatterns + UIPasteControl、Android 开关、鸿蒙 PasteButton、上传条件）只按 BR-ID-16；本表只维护 clipboard.prompt 文案。

2026-10-03 功能对照补缺第 1 批新增（代理按 13 §13.11 的分配规则取号，已同步 13 §13.11 与 规划/04 §7）：20004「第三方授权凭证无效」、50305「第三方登录服务暂不可用」，子键 20004.identity_mismatch、30104.credential_invalid；表 C 新增的文案为代理起草的默认措辞，可在字典中改，不改用途。

2026-10-03 功能对照补缺第 3 批新增（docs/changes/20261003-功能对照补缺.md「第 3 批」；代理按 13 §13.11 的分配规则取号，已同步 13 §13.11 与 规划/04 §7）：10405「客户端版本低于最低支持版本」（功能对照 G-24）。表 C 新增未安装微信时登录、分享、客服的三个文案键与客服提示里的两个按钮键（功能对照 G-31）、更新提示的两个按钮键（功能对照 G-24），为代理起草的默认措辞，可在字典中改，不改用途。新增表 D「隐私与权限文案」（功能对照 G-26），键名与用途已定，文案由法务定稿（规划/06 Q-F14）。第 2 轮评审后表 C 加强更页的三个次要入口键（app_update.privacy_policy、app_update.delete_account、app_update.cancel_deletion），为代理起草的默认措辞，可在字典中改，不改用途。第 3 轮评审后表 B 加子键 10403.h5_read_only、10405.no_account（没有新增码，已同步 13 §13.11 与 规划/04 §7），同样是代理起草的默认措辞。

按 C-03 默认处理，待负责人确认。新增码 30415、50304 与 20001.nickname_sensitive、30411.mergeable 子键（2026-10-01 拍板第二批 OPS-13、TRADE-12、OPS-04），以及 30416（§8 ADD-07）与 30101 / 30102 的 auth_unavailable 子键（§8 ADD-02；文案与按钮按 §8 ADD-08 改为「淘宝暂时无法下单，请稍后再试」、只给【知道了】）需同步 13 §13.11 与 规划/04 §7；码号与枚举改名（admin_unbind → admin_disable 等）由代理自定，负责人 2026-10-01 接受。

#### BR-TEXT-15 细则 · 淘礼金卡片如实话术

**范围（D7）**：首版保留判定 3′（素材 unknown）、4 中的 unknown 无返利分支及 6（未接入 / 关闭）；判定 1、2、3、5 留待后续接入且对应能力验证后启用。未接入、查询失败或口令失效均不能单独证明“已领完”。

- 状态：待验证
- 默认值：能力未验证前所有素材淘礼金按 unknown 展示（无标签、「去购买」、「可能领不到」）；A/B/C 区分文案在后续纳入接入范围且 规划/09 淘宝项有接口样例后启用；素材淘礼金一律转链，不提供「复制原口令」（D20，负责人 2026-09-30 确认）。
- 决策人：负责人
- 依赖平台能力：素材淘礼金 A/B/C 判定依赖淘宝口令解析能否返回淘礼金创建方；B 类（brand_open）经我方推广位下单能否同时领到淘礼金并归因给我方；我方池淘礼金依赖淘礼金创建权限与剩余份数查询接口（均为 规划/09 淘宝项，待实测）
- 取代：
  - 本条原写「「复制原口令（领淘礼金、无返利）」按钮由后台开关 tlj.copy_original_tpwd.enabled 控制，默认关（修订① D8，默认假设，负责人确认）」及未决问题中「D20 待确认」的表述（2026-09-30 按 D20 负责人决定取代：不提供复制原口令，一律转链）
- 来源：规划/01 §1、§5 J2；规划/04 §2.5 tlj_kind、§8.3；PRD v2.1 §10.6、§10.6.1、§10.11；PRD修订_双品牌与Agent找货 3.6、3.6.1；规划/00 D20；docs/changes/20260930-拍板第一批.md §3（D20 行）；docs/changes/20261001-拍板第二批.md（AI-01：首版不接入淘礼金，只提示「暂无淘礼金活动」，保留扩展位置）
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

| 判定 | 标签 | 按钮 | 说明文案 |
| --- | --- | --- | --- |
| 1 我方池淘礼金 | 淘礼金 | 领 {amount}淘礼金 | 剩余 {remain} 份（查询失败不显示） |
| 2 素材 A（ours）/ B（brand_open），验证通过后启用 | 淘礼金 | 领淘礼金并购买 | — |
| 3 素材 C（third_party），验证通过后启用 | 无 | 去购买 | 这条素材里的淘礼金是第三方发的，通过本 App 购买领不到它；本 App 预估返 {rebate} |
| 3′ unknown（验证前所有素材） | 无 | 去购买 | 这条素材里的淘礼金通过本 App 购买可能领不到；本 App 预估返 {rebate} |
| 4 C / unknown 且无返利 | 无 | 去购买 | 同上前半句；该商品暂无返利 |
| 5 可靠接口已确认领完（remain=0；后续接入） | 无 | — | 这个淘礼金已领完，以下是同款有券商品 |
| 6 池内无结果或 tlj.enabled=off | 无 | — | 只出 notice agent.notice.tlj_none「暂无淘礼金活动」，不出替代商品卡（BR-AI-17，C-24 默认，已确认） |

- 判定 6（C-24）：按 BR-AI-17（已确认），本条只维护 agent.notice.tlj_none 的文案；按 C-24 默认处理，已由负责人确认 2026-09-30。若负责人改为「继续出有券商品」，只改本条判定 6 与 Agent 编排。
- D20 结论（负责人 2026-09-30，变更记录 §3 D20 行；即修订① D8，与 规划/00 D8 分销决策编号冲突，已在 00 登记为 D20）：第三方（C 类，tlj_kind=third_party）淘礼金素材一律转链，不提供「复制原口令（领淘礼金、无返利）」按钮，也不设控制该按钮的后台开关（原 tlj.copy_original_tpwd.enabled 不再建立）；unknown 素材同样只转链。负责人预期转链后淘礼金参数保留（用户经我方转链下单仍能领到该淘礼金），该预期待 06 Q-G3、CAP-TB-09 实测确认；**实测前话术不变**，判定 3、3′、4 仍按上表如实告知「领不到 / 可能领不到」，不得写成能领到。
- 待验证后续（D20）：若 CAP-TB-09 实测证实转链后仍保留第三方淘礼金（且订单归我方、返利可计），判定 3 的话术（「通过本 App 购买领不到它」）需改写，判定 3′、4 与 C 类的标签、按钮一并复核；改写走 00 §8 变更流程，并登记到 15 待验证汇总。实测证实不保留时维持现话术。

例：验证前，用户粘贴含 5 元淘礼金的素材，商品预估返 180 分 → 卡片无淘礼金标签，说明「这条素材里的淘礼金通过本 App 购买可能领不到；本 App 预估返 ¥1.8」，按钮「去购买」。我方池淘礼金面额 550 分、剩余查询超时 → 按钮「领 5.5 元淘礼金」，不显示剩余份数。

需同步修改的规划文档（2026-09-30 D20，未同步）：08 §15 待验证汇总登记「D20 转链后是否保留第三方淘礼金 → 判定 3 话术改写」（依赖 CAP-TB-09、06 Q-G3）；规划/09 2_TB CAP-TB-09 通过标准补「第三方淘礼金素材经我方转链后淘礼金是否保留」；规划/10 AC-S1-38-TB、AC-S1-53-TB 补「卡片不出现复制原口令按钮」断言；规划/00 D20 已写明结论，不需改。

#### BR-TEXT-16 细则 · AI 生成内容标识

- 状态：已确认（拍板第二批 AI-24：标识按本条统一；AI-22：助手名称与口吻；AI-06：登记前只对内部测试名单开放。标识的法定措辞若法务另有意见，按 00 §8 改本条）
- 默认值：标识两处统一为「内容由 AI 生成，仅供参考」，由同一配置下发；text.delta 出站过滤按 BR-AI-06；登记前 model_label「内测模型」、filing_text 为空、入口只对内部测试名单开放；助手名称「凑狸 AI 助手」。理由：规划/03 §10.2 与 04 §8.2 措辞不同；D16 与 F-PRIV-07 要求登记前不对公众开放并公示登记编号。
- 决策人：法务
- 依赖平台能力：无
- 取代：
  - 规划/04 §8.2：「meta.ai_label「内容由 AI 生成」」
  - 规划/03 §10.2：「AiLabel「内容由 AI 生成，仅供参考」（两处并存）」
  - 规划/01 F-PRIV-07：「每条回复「内容由 AI 生成」（措辞改取 texts.ai_label）」
  - 08 BR-ID-15 原文：「显式展示「内容由 AI 生成」…登记编号（取配置 agent.filing_no）」（文案与配置键统一到本条；BR-ID-15 只保留合规义务）
  - 08 BR-AI-06 细则原写：「meta.ai_label 固定为“内容由 AI 生成”」（拍板第二批 AI-24 按本条统一）
  - 规划/01 Tab 名称「AI 助手」作为助手名称的写法（AI-22：助手名称为「凑狸 AI 助手」）
- 来源：规划/03 §10.2、§7.5；规划/04 §8.2；规划/00 D16；规划/01 F-PRIV-07；PRD v2.1 §10.13；docs/changes/20261001-拍板第二批.md（AI-06、AI-22、AI-24）
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 例：meta = {ai_label: 「内容由 AI 生成，仅供参考」}；用户搜「伊利纯牛奶 250ml」→ tool.status display_text 为「正在搜索淘宝」，不是「正在搜索伊利纯牛奶 250ml」。
- 出站过滤（G-15，代理已定）：只按 BR-AI-06（已确认）——金额类命中替换为「见卡片」（相邻合并）；URL、scheme、口令、短链删除命中的连续非空白串；trace 记 output_filtered=true 与命中类型。本条不另定过滤规则与埋点，只维护 AI 标识与公示文案。
- model_label：登记前显示「内测模型」，登记后取登记名称，不写供应商品牌宣传语。
- 助手名称（AI-22）：Agent 页顶标题、AgentConsent 说明与固定话术中的自称统一取 texts.agent.name「凑狸 AI 助手」；底部 Tab 标签是否用简称由 规划/01 页面清单定，文字仍从字典取（需同步 01）。
- AgentConsent 单独同意（F-PRIV-07）未完成时不展示对话。
- PlatformBadge 仅作来源说明（文字 + 小图标），不作品牌宣传。
- 标识的法定要求（显式标识位置与措辞）以法务意见为准。

#### BR-TEXT-17 细则 · 广告推广标识

- 状态：已确认（负责人 2026-09-30，依据 docs/changes/20260930-拍板第一批.md §2；范围按拍板第二批 OPS-24 细化）
- 默认值：法务定性前：首页商品池卡、活动 Banner 与分享海报显示「推广」，联盟信息流、搜索自然结果与 Agent 相关性卡片不显示；客户端实现「非 null 即展示」。理由：《互联网广告管理办法》要求付费推广内容可识别，定性前应保守；字段已在 规划/04 §8.3 预留，开关在服务端。
- 决策人：法务
- 依赖平台能力：规则主体不依赖平台；细则「联盟物料频道」的白名单要等 规划/09 CAP-TB-10、CAP-JD-10、CAP-PDD-10 逐个记录各频道的排序依据后才能填全（2026-10-03）
- 取代：本条原范围「首页运营位（运营手选、商家付费或置顶）与分享海报」（信息流、Banner 未写；拍板第二批 OPS-24 定为商品池卡与活动 Banner 标推广、联盟信息流不标）
- 来源：规划/04 §8.3；规划/00 D3；PRD v2.1 §10.13、§15；规划/03 §7（首页卡片注册表）；docs/changes/20261001-拍板第二批.md（OPS-24）；docs/changes/20261003-功能对照补缺.md「第 3 批」（功能对照 G-34）
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 待定内容：标识措辞（「广告」/「推广」）、范围（首页运营位、搜索结果、Agent 卡片、分享海报）、是否按付费置顶与自然结果区分。
- ad_label 下发规则只在本条维护；Agent 卡片的佣金披露文案与“付费位不得参与 Agent 排序”见 BR-AI-10。
- 法务结论是 W8 公开上架（规划/00 D3）前的阻塞项，需在 W5 白名单内测前给出。
- 例：默认阶段，服务端对首页商品池卡片与活动 Banner 返回 ad_label=「推广」，首页联盟物料信息流与搜索结果返回 null；法务若定为首页运营位用「广告」→ 只改服务端配置，不发版。
- **联盟物料频道**（2026-10-03，功能对照 G-34；按功能对照 Q-27 默认 A 写，待负责人确认，规划/06「功能对照待确认」；docs/changes/20261003-功能对照补缺.md「第 3 批」）：联盟物料信息流不标「推广」，前提是它的排序与平台能拿多少佣金无关。
  - 适用范围：首页 `feed_infinite`、`product_scroll`、`product_grid` 的 `union_material` 数据源；P1 的榜单页、品牌页立项时同样适用。
  - 可选频道：只用按销量、热度或「猜你喜欢」这类方式排序的频道。可选频道登记在频道白名单 `specs/material-channels.yaml`（平台、频道标识、排序依据、是否可选）；后台的数据源选项只列白名单内可选的频道，服务端保存首页配置时再校验一次，不在白名单的返回 20001。
  - 取数时再查一次：服务端每次为数据源取物料之前都核对白名单，频道不在白名单或已标为不可选的，不取这个数据源，对应区块按没有数据处理（首页的空态与兜底规则不变）并告警。白名单变更时，后台列出仍引用被移出频道的已发布配置，由运营改配置；保存时的校验管不到之后的白名单变更，所以取数时这一道不能省。
  - 不进白名单：平台文档写明按佣金或收益排序、或带佣金权重的频道与排序参数（各平台的高佣榜、收益榜一类）。排序依据说不清的频道，在 规划/09 CAP-TB-10、CAP-JD-10、CAP-PDD-10 逐个记下「是否含佣金权重」之前也不进白名单。
  - 本系统在物料的合并与混排层不加佣金或返利权重（Agent 的同类要求见 BR-AI-09）。
  - 确实要用按佣金排序的频道时：须负责人决定（功能对照 Q-27 改选 B，或逐个频道放行）；放行的数据源，其卡片一律下发 ad_label=「推广」，并在模块标题处说明排序依据，说明文案由法务定稿后写入本条。在此之前白名单里没有这类频道，后台选不到。
  - 用户侧文案不出现「高佣」「收益榜」（BR-TEXT-13 细则「榜单类词」）。
  - 例：运营想在首页加一个按收益排序的榜单模块 → 后台频道下拉里没有这个频道，直接调后台接口保存也被拒（20001）；改选「实时热销」一类的频道 → 可以保存，卡片 ad_label=null。
  - 需同步修改的规划文档（2026-10-03）：规划/01 F-HOME-03；规划/03 §6.3；规划/04 §6.6；规划/07 §3 榜单页行；规划/09 CAP-TB-10、CAP-JD-10、CAP-PDD-10；规划/10 AC-S1-90（已同步 2026-10-03）。

#### BR-TEXT-18 细则 · 客服话术一致性

- 状态：默认假设
- 默认值：话术库引用字典 key、后台双列显示编码与用户文案、字典变更同发布更新话术、不向邀请人透露下级订单。理由：PRD v2.1 §10.6.1 只要求 OTHER_TLJ「客服话术同步更新」，未形成通用机制。
- 决策人：运营
- 依赖平台能力：无
- 取代：本条原写「客服不得承诺字典与 expected_credit_date 以外的入账或到账时间」及例「预计 10-17 入账」（2026-09-30 随 C-02、D11 月结口径改写）
- 来源：PRD v2.1 §10.6.1 第五步；规划/01 §5 J7 第 5 条、F-AGENT-06、F-AGENT-07；规划/06 Q-F4；README §1.2；docs/changes/20260930-拍板第一批.md §3（C-02、D11 行）
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 话术库条目结构：{场景, 引用 dict key 列表, 标准回复模板, 可执行动作（找回 / 重新授权 / 申诉 / 转财务）}。
- 例：用户问「我的返利怎么还没到」，订单 (RECEIVED, WAITING)、display_status=WAITING、expected_credit_period=2026-11 → 标准回复「这笔订单已收货，预估返 ¥4.5，预计 11 月结算，结算后可在钱包提现」（2026-09-30 随 C-02、D11 改写，原「预计 10-17 入账」；同日按负责人补充改为预计结算月份，原「预计随淘宝 10 月联盟结算后入账」，变更记录 §10）。订单 display_status=INVALID、reason=OTHER_TLJ → 「下单时使用了其他推广者的淘礼金，订单归对方，这笔没有返利」。
- 例：邀请人问「我邀请的好友买了什么」→ 「为保护好友隐私，只能看到推广收益金额，看不到好友的订单」。
- 面向有返利经验用户的常见问题（2026-10-03，功能对照 G-65；D25：同时面向返利新用户与已有返利经验的用户）：帮助中心与客服话术库各放一组，措辞按本条引用字典键，不写死流水名称，不用「团队」「下线」「粉丝」等词（BR-INV-20），也不提其他 App：
  - 「为什么看不到我邀请的好友买了什么？」→ 为保护好友隐私，只显示好友带来的推广收益，不显示好友的订单、商品和下单时间（BR-INV-16）。
  - 「邀请带来的收益在哪里看？」→ 结算前计入钱包的「预估收益」合计，不逐笔列出；结算后在余额流水里逐笔显示，名称取 ledger_type.REFERRAL_CREDIT.name（间推开启时另有 ledger_type.REFERRAL_CREDIT.name_indirect），日期只到日（BR-INV-17、BR-TEXT-19）；收益看板上线后另可看本月、上月的合计（BR-FUND-25）。
  - 「订单里的「分享」是什么？」→ 别人通过你分享的商品链接下的单，收益记在你名下（预估推广收益 / 推广收益）；下单的人这单拿不到返利；你只看到商品、实付、件数、状态和脱敏订单号（BR-ATTR-10、BR-TEXT-02）。
- 例（2026-10-03，功能对照 G-37）：用户问「我一共拿到过多少返利」→「钱包不提供累计收益合计。已结算的每一笔都在余额流水里，可以按时间查看；提现成功的总额是钱包里的「已提现」」（收益看板上线后另加一句「本月、上月的已结算金额可以在收益看板看」，BR-FUND-25）。不说「到账收益」：「已到账」只指提现（BR-TEXT-01）。
- BLACKLIST 与 hold：客服后台可见内部原因，但对用户只说字典文案并引导申诉。
- 验收：抽取话术库全部条目跑禁用词扫描与 dict key 存在性校验。
- 话术库按 display_status（BR-FUND-17）建场景，不按单一 order_status；按 C-01 默认处理，已由负责人确认 2026-09-30。

#### BR-TEXT-19 细则 · 余额流水用户文案

- 状态：默认假设
- 默认值：税费从冻结扣除，不单独成行，只作 WITHDRAW_PAID 汇总条目明细（BR-FUND-15，C-26 默认，待财务确认）；直推分佣流水不可跳转且不展示下级信息；无关联单据的调账显示说明。理由：与后端功能规划分录（税费借记冻结子账户）一致；J7 规定上级看不到下级订单。税务口径待 D12 税务师意见。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 分录表：「TAX_WITHHELD 借 U_\*_FROZEN（映射为 规划/ 的 TAX_WITHHOLD，口径一致）」
  - 本条 2026-10-01 写法：站内信 BALANCE_ADJUSTED「你的{account_name}余额调减…」，{account_name} 取「自购返利账户」或「推广收益账户」（单一余额，拍板第二批 §8 ADD-06）
- 来源：规划/04 §2.4 流水类型、§3.2 withdrawals；规划/01 §5 J7 第 5 条、F-WDR-01；规划/00 D12；docs/changes/20261001-间推二级奖励.md（INDIRECT 名称）；PRD修订_后端功能规划 资金分录；docs/changes/20261001-拍板第二批.md（OPS-18、FUND-13）；docs/changes/20261001-拍板第二批.md §8 ADD-06
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

| ledger_type | 名称 | 符号（可用余额视角） | 跳转 |
| --- | --- | --- | --- |
| REBATE_CREDIT | 自购返利入账 | + | 子订单 |
| SHARE_CREDIT | 分享收益入账 | + | share 子订单 |
| REFERRAL_CREDIT | 邀请分佣入账（显示「邀请好友订单」）；sub_type=INDIRECT 显示「好友推广奖励」（2026-10-01 负责人确认，key ledger_type.REFERRAL_CREDIT.name_indirect） | + | 不跳转 |
| CLAWBACK | 订单扣回（sub_type=PART_REFUND 时显示「部分退款扣回」） | - | 子订单；referrer 角色不跳转 |
| SETTLE_ADJUST | 结算补差（只表示联盟结算额差异，sub_type SETTLE_DIFF / PRICE_COMPARE / PRICE_PROTECT；入账后部分退款不用此类型） | ± | 子订单；referrer 角色不跳转 |
| WITHDRAW_FREEZE | 提现冻结 | - | 提现单 |
| WITHDRAW_FEE | 提现手续费 | 不单独成行（WITHDRAW_PAID 汇总条目明细） | 提现单 |
| TAX_WITHHOLD | 代扣个税 | 不单独成行（WITHDRAW_PAID 汇总条目明细） | 提现单 |
| WITHDRAW_PAID | 提现到账 | 0（列表显示「{net} 已转入{payout_channel_name}」，展开明细含申请额、代扣个税、手续费） | 提现单 |
| WITHDRAW_RETURN | 提现退回 | + | 提现单 |
| ADMIN_ADJUST | 按原因码取名称（见下方「ADMIN_ADJUST 原因码文案」；OTHER 为「人工调账」） | ± | 有关联单据时跳转，否则显示 hint |
| BAD_DEBT_WRITEOFF | 负余额核销 | + | 显示 hint |

例 1：提现 1000 分、无税费成功 → 「提现冻结 -¥10」「提现到账 ¥10 已转入支付宝」。
例 2：提现 1000 分、代扣 80 分成功 → 「提现冻结 -¥10」「提现到账 ¥9.2 已转入支付宝」（明细：申请 ¥10，代扣个税 ¥0.8，手续费 ¥0）。
例 3：驳回 → 「提现冻结 -¥10」「提现退回 +¥10」。
例 4：下级订单入账给上级 150 分 → 「邀请分佣入账｜邀请好友订单｜+¥1.5｜10-17」，不可点击。
例 4b（间推开关开启）：间推份额 61 分 → 「好友推广奖励｜邀请好友订单｜+¥0.61｜10-17」，不可点击，不显示层级或「二级」「间推」字样。名称与 P1 邀请奖励（REWARD sub_type=invite，BR-INV-22）区分。
例 5：自购订单入账 800 分后退 1 件（共 2 件）→ 流水「部分退款扣回｜-¥4」，点击跳转该子订单（BR-FUND-08）。

**ADMIN_ADJUST 原因码文案**（原因码含义与调账流程只在 BR-FUND-24 维护；文案为代理起草，负责人 2026-10-01 授权按推荐（拍板第二批 FUND-13），运营可改措辞，变量与含义不得改）

| sub_type | 名称 name_&lt;sub_type> | 说明 hint_&lt;sub_type> |
| --- | --- | --- |
| RESTORE | 订单恢复补发 | 订单经核实恢复，补发对应金额 |
| RECON_FIX | 结算核对更正 | 按联盟结算核对结果更正 |
| PAYOUT_RECOVERY | 重复到账追回 | 追回重复或异常到账的提现金额 |
| ACCOUNT_CLOSED | 注销放弃余额 | 注销时放弃的余额（注销后用户不可见，只供客服与对账） |
| OTHER | 人工调账 | 如有疑问请联系客服 |

站内信 BALANCE_ADJUSTED（只在调减时发送，只发站内信，category=service；注销用户不发，BR-FUND-24 ⑦⑧）：「你的余额调减 {amount}，原因：{adjust_reason}。如有疑问，请联系客服。」（单一余额，拍板第二批 §8 ADD-06）；{amount} 为调整金额绝对值，按 BR-TEXT-10 格式化（含 ¥）；{adjust_reason} 取上表名称；不写内部说明、操作人与关联单据号。调增不另发站内信。

例 6：财务以 RECON_FIX 调减 120 分（关联子订单）→ 流水「结算核对更正｜-¥1.2」，点击跳转该子订单；站内信「你的余额调减 ¥1.2，原因：结算核对更正。如有疑问，请联系客服。」

上级视角的名称、说明与日期粒度只在本条维护（拍板第二批 OPS-18：「邀请分佣入账」+ 说明「邀请好友订单」、日期只到日，更难反推好友下单时间）；BR-INV-17 原写「邀请好友购物分佣」、时间到分钟，已改为引用本条。

入账后部分退款写 CLAWBACK（sub_type=PART_REFUND），不写负向 SETTLE_ADJUST；按 C-16 默认处理，待财务确认。名称「部分退款扣回」的字典 key 为 ledger_type.CLAWBACK.name_part_refund。

列表范围按 BR-FUND-15：用户余额流水只展示 available 子户分录，外加每张打款成功提现单 1 条 WITHDRAW_PAID 汇总条目（名称「提现到账」，含实际到账、代扣个税、手续费明细，不改可提现余额、不带 balance_after）；WITHDRAW_FEE、TAX_WITHHOLD 不单独成行，名称键保留供汇总条目明细使用；本条只维护名称与明细文案。按 C-26 默认处理，待财务确认。

#### BR-TEXT-20 细则 · 推送短信分享渠道约束

- 状态：待验证
- 默认值：首部平台名与「官方」规则按本条执行（保存时 + 渲染后）；短信字数上限暂按 68 字设计模板，实测后更新。
- 决策人：运营
- 依赖平台能力：阿里云短信签名与模板审核规则（签名字数、单条计费长度、驳回词）；各手机厂商交易类消息分类申请条件（规划/09 待实测）
- 取代：无
- 来源：规划/01 F-PRIV-08、F-SHARE-02、F-SHARE-03；PRD修订_后端功能规划 2.14；参考_花卷云功能查漏底稿 §9；拍板第二批 §8 ADD-08（站长告警短信）
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：分享模板「【淘宝】#标题# 券后 #券后价#」→ 保存拒绝；改为「#标题# 券后 #券后价#，复制 #口令# 打开淘宝」通过。
- 例：商品标题「【天猫】伊利官方旗舰店纯牛奶」→ 渲染用「伊利旗舰店纯牛奶」。
- 商品分享文案不带邀请码与下载地址（2026-10-03，功能对照 G-41；按功能对照 Q-17 默认 A 写，待负责人确认）：分享模板的变量白名单维持 #标题# #券后价# #口令# #链接# 四个，不加 #邀请码#、#下载地址#。理由：买的人从分享单拿不到返利（BR-ATTR-10），文案里带邀请码和下载地址，容易被读成「下载就能返利」；《微信外部链接内容管理规范》2.3.1 条禁止以利益诱导下载或跳转外部 App（规划/09 CAP-X-03）。邀请码与下载地址只用于邀请文案（BR-INV-18 的 {invite_code}、{download_url}）。负责人改选 B（做成可选项、默认关闭）时：只加这两个变量，做成模板级开关、默认关闭，保存时同样过 BR-TEXT-13 与 BR-INV-20 校验，不得出现「下载即可返利」一类对购买者的承诺，微信好友与群渠道是否开放 #下载地址# 按 CAP-X-03 的结论定；展示收益金额或店铺的变量一律不引入。
- 短信（待验证）：签名 ≤8 字、签名 + 模板 ≤68 字按 1 条计费，「红包」「下载」等词易被驳回——来源为花卷云查漏底稿，需在阿里云短信控制台实际报备验证。
- 交易类推送挂厂商消息分类（小米通知类别、OPPO「个人账号与资产变化」、华为「帐号动态」）——同为待验证。
- WD_FAILED 短信示例：「【{签名}】你的提现打款未成功，¥10 已退回余额，请在 App 内查看原因。」须实测字数与审核结果。
- 站长告警短信（BR-ID-24，拍板第二批 §8 ADD-08）：发给后台配置的站长手机号（union.auth_alert_phones，可多个），不发用户，不受用户通知开关与免打扰约束；何时发、发几次只按 BR-ID-24。

| code | 触发（见 BR-ID-24） | 模板 |
| --- | --- | --- |
| UNION_AUTH_EXPIRING | 到期前 union.auth_alert_days 各节点（默认 14、7、1 天） | 【凑狸】你的{platform_name}联盟授权将于{expires_at}到期，请登录后台重新授权，过期后新用户将无法下单。 |
| UNION_AUTH_EXPIRED | 到期，或探测 / 调用检测到授权失效 | 【凑狸】你的{platform_name}联盟授权已过期或失效，新用户暂时无法下单，请尽快登录后台重新授权。 |

- 变量：{platform_name} 取平台中文名（淘宝 / 京东 / 拼多多）；{expires_at} 按 BR-TEXT-11 未来时间写法「YYYY-MM-DD HH:mm」。首句以「你的」开头，避开本条「不得以平台名称开头」；按上文 68 字核对，含签名约 55 字与 42 字。
- 短信签名「凑狸」与这两条模板在阿里云短信的报备由负责人办理；审核要求改措辞时只改文字，变量与触发不变。

#### BR-TEXT-21 细则 · 报表金额列口径与刷新标注

- 状态：默认假设
- 默认值：口径编码 6 个（见下表）；每列列头格式「{列名}（{口径编码}）｜截至 {as_of}｜{刷新方式}」，as_of 按 BR-TEXT-11 显示为 YYYY-MM-DD HH:mm（+08:00），导出文件表头同样写入；实时计算列标「实时」，缓存或快照列标实际周期；联盟侧数据（UNION_SETTLED、UNION_RECEIVED）的刷新周期在 规划/09 实测前标「待核实」。理由：花卷云查漏底稿指出收益口径多级且叫法混用（「确认收货佣金」「结算佣金」「未结算」），运营与财务对数时因口径与刷新时点不一致产生误判；BR-TEXT-01 已统一用户侧术语，本条补齐后台与报表侧。
- 决策人：财务
- 依赖平台能力：各联盟结算明细与回款数据的可取得频率（规划/09 订单同步与结算项，待实测）；实测前 UNION_SETTLED、UNION_RECEIVED 的刷新方式标「待核实」，不得标具体周期
- 取代：
  - 参考_花卷云功能查漏底稿 §12：「预估（付款）→预估结算→确认收货→已返现，另有未结算；统一「确认收货佣金」「结算佣金」叫法」
  - PRD修订_后端功能规划 2.16：「预估收益 → 待入账 → 已入账 → 已提现；禁止并用确认收货佣金、结算佣金」（本条沿用并补刷新标注）
- 来源：参考_花卷云功能查漏底稿 §12、§16 #33；PRD修订_后端功能规划 2.16；BR-TEXT-01；BR-FUND-18（快照与缓存周期）
- 需同步修改的规划文档：规划/01 后台报表相关功能的列头说明（未同步，登记于 README §0.6）

| 口径编码 | 显示名 | 定义（单位分） | 数据来源与时点 |
| --- | --- | --- | --- |
| ESTIMATED | 预估收益 | rebate_status=ESTIMATED 且 platform_status≠DEPOSIT_PAID 的受益人份额合计（与 BR-FUND-18 estimated_fen 同口径） | 订单与分佣快照计算值；报表取值时刻即 as_of |
| WAITING | 待入账 | rebate_status=WAITING 的受益人份额合计（含维权中与 hold） | 同上；日报取 asset_snapshots.total_waiting_fen（D+1 00:01 写入 D 日） |
| CREDITED | 已入账 | REBATE_CREDIT、SHARE_CREDIT、REFERRAL_CREDIT 流水合计，另列 CLAWBACK、SETTLE_ADJUST 净额，不合并进本列 | 分录，按 accounting_date 汇总 |
| WITHDRAWN | 已提现 | PAID_API、PAID_MANUAL 提现单 amount_fen 合计（含代扣税费；实付另列 net_fen） | 提现单，按成功时刻 |
| UNION_SETTLED | 联盟结算佣金 | 联盟结算明细中的结算额（order_settlements） | 联盟结算明细导入时刻（待核实） |
| UNION_RECEIVED | 联盟已回款 | UNION_RECEIVABLE 核销金额（BR-FUND-20） | 回款录入时刻 |

花卷云旧叫法对照：预估（付款）→ ESTIMATED；确认收货 → WAITING；已返现 → CREDITED；预估结算、未结算 → 无对应口径，不得使用，需要时分列 ESTIMATED 与 WAITING；确认收货佣金、结算佣金 → 分别按 WAITING、UNION_SETTLED 命名。

例：运营日报 10-17 09:00 打开，两列列头分别为「自购预估收益（ESTIMATED）｜截至 2026-10-17 09:00｜实时」与「自购待入账（WAITING）｜截至 2026-10-17 00:00｜每日 00:01 快照」；不得出现「未结算合计」一列把两者相加。

边界：
- 同一报表内 as_of 不同的列（快照列与实时列）各自标注，不得在表头共用一个「数据截至」。
- 快照标记 waiting_comparable=false（BR-FUND-18，入账任务未等到快照完成）的日期，WAITING 列在该日数值旁标「口径未对齐」。
- 本条只约束后台与报表；用户可见文案仍按 BR-TEXT-01，用户侧不得出现口径编码。
- 报表中的「预估收益」「联盟结算佣金」不受 BR-TEXT-13 资金类词校验（后台字段豁免），价格与返利类禁用词仍校验。

#### BR-TEXT-22 细则 · Agent 固定话术

- 状态：默认假设（代理起草，负责人 2026-10-01 授权按推荐；已按 BR-TEXT-13 自查禁用词，交负责人过目后改为已确认，拍板第二批 AI-21、AI-22）
- 默认值：下表；口吻为简短口语、不用表情，每条不超过 2 句
- 决策人：负责人（上线后措辞可由运营在字典中改）
- 依赖平台能力：无
- 取代：
  - BR-AI-07 原写「summary 逐码维护在 BR-TEXT-05、BR-TEXT-02 映射表的 summary 列」（改为在本条集中维护，不给映射表加列）
  - BR-AI 各条细则中给出的示例文字（以本表为准，BR-AI 只保留键名与用途）
- 来源：BR-AI-01、BR-AI-05、BR-AI-07、BR-AI-08、BR-AI-10、BR-AI-14、BR-AI-17、BR-AI-18、BR-AI-24；规划/01 E07；docs/changes/20261001-拍板第二批.md（AI-05、AI-07、AI-13、AI-15、AI-17、AI-21、AI-22）
- 需同步修改的规划文档：contracts/texts.default.json 建立时按本表写入；规划/03 §7 Agent 对话页不得硬编码上述文字

**固定话术表**（键 → 默认文案；变量按 BR-TEXT-12 处理）

| 键 | 用途（规则） | 默认文案 |
| --- | --- | --- |
| agent.name | 助手名称（BR-TEXT-16） | 凑狸 AI 助手 |
| agent.welcome | 新对话首屏 | 我是凑狸 AI 助手。说说想买什么，我帮你找货、查返利。 |
| agent.need_login | 游客问订单（BR-AI-01） | 登录后才能查你的订单，点下方按钮登录。 |
| agent.need_phone | 未绑手机问订单（BR-AI-01） | 绑定手机号后才能查订单，点下方按钮去绑定。 |
| agent.refuse.out_of_scope | 意图白名单外（BR-AI-18） | 这个问题我答不了。我可以帮你找货、查返利、查订单，或者解答返利规则。 |
| agent.refuse.advice | 问诊、用药、法律、投资建议（BR-AI-18，AI-15） | 这类问题请咨询医生、律师等专业人士。想买相关商品的话，直接告诉我商品名。 |
| agent.refuse.unsafe | 输入审核命中（BR-AI-18） | 这条内容没法处理，换个说法试试。 |
| agent.refuse.safety_unavailable | 输入审核超时（BR-AI-18） | 暂时处理不了这条消息，请稍后再发一次。 |
| agent.refuse.output_blocked | 输出审核命中、替换后结束（BR-AI-18） | 部分内容无法显示，商品信息以卡片为准。 |
| agent.refuse.safety_timeout | 输出审核再超时（BR-AI-18） | 说明文字暂时无法显示，商品信息以卡片为准。 |
| agent.refuse.prohibited | 禁售（BR-AI-18） | 这类商品不在可推荐范围内。 |
| agent.degraded | 无模型降级出卡（BR-AI-14，AI-05） | 先按关键词为你找到这些商品，详情见卡片。 |
| agent.degraded.empty | 无模型降级、关键词搜索无结果（BR-AI-14） | 没找到相关商品，换个关键词试试。 |
| agent.timeout | 单轮到时结束（BR-AI-14） | 这次回复超时了，可以再问一次。 |
| agent.rule.found | 规则命中（BR-AI-07） | 规则见下方卡片。 |
| agent.rule.not_found | 规则未命中（BR-AI-07） | 没有找到相关规则，可以联系客服确认。 |
| agent.order.lookup_limited | 按订单号查询超限（BR-AI-07） | 查询次数较多，请到订单页查看或稍后再试。 |
| order_list.summary | 多笔订单（BR-AI-07） | 找到 {n} 笔订单，详情见卡片。 |
| order_list.empty | 0 笔订单（BR-AI-07） | 没有找到符合条件的订单，可到订单页查看，或提交找回。 |
| agent.notice.link_limit | 链接超过 3 个（BR-AI-01） | 一次最多识别 3 个链接。 |
| agent.notice.ordinal_default | 指代追问后仍无法解析（BR-AI-01） | 已按第 1 个商品处理。 |
| agent.notice.price_unrecognized | 价格条件追问后仍无法解析（BR-AI-08） | 未识别价格条件，已按其他条件查找。 |
| agent.notice.relaxed_spec | 放宽规格（BR-AI-08） | 已放宽规格条件。 |
| agent.notice.relaxed_price | 放宽价格（BR-AI-08） | 已放宽价格条件。 |
| agent.notice.no_result | 两次放宽仍无结果（BR-AI-08） | 没有找到符合条件的商品。 |
| agent.notice.no_cheaper | 再便宜点无结果（BR-AI-05，同 BR-PRICE-15） | 没有找到比当前结果更便宜的商品。 |
| agent.notice.more_orders | 订单超过本次上限（BR-AI-07） | 更多订单请到订单页查看。 |
| agent.notice.tlj_taobao_only | 非淘宝平台问淘礼金（BR-AI-17） | 淘礼金仅支持淘宝。 |
| agent.notice.search_disabled | 用户只要某个搜索开关已关闭的平台的商品（BR-PROD-10 细则「按平台的搜索开关」，2026-10-03 功能对照 G-47） | {platform_name}暂不提供搜索，可以把商品链接发给我查返利。 |
| agent.notice.title_based | 比较或适用性问题（BR-AI-18，AI-07） | 以上只根据商品标题判断，具体以商品详情为准。 |
| agent.suggest.no_result.1–3 | 无结果建议（BR-AI-08） | 去掉价格条件再找｜只搜{q_short}｜换个平台看看 |
| agent.disclaimer.commission | 佣金披露（BR-AI-10，BR-TEXT-13 例外） | 推荐商品含推广链接，购买后本平台可能获得佣金。 |
| agent.match.matched | 卡片条件标记（BR-AI-24） | 符合条件 |
| agent.match.title_shows | 规格经代码匹配（BR-AI-24） | 标题显示为{spec} |
| agent.match.relaxed | 放宽后入选（BR-AI-24） | 已放宽条件 |
| agent.match.spec_unconfirmed | 规格未确认（BR-AI-24） | 规格待确认 |
| order_status.PAID.summary | T5（BR-AI-07） | 订单已跟踪到，确认收货后随联盟月度结算，详情见卡片。 |
| order_status.WAITING.summary | T5 | 已收货，等待联盟结算，预计结算月份见卡片。 |
| order_status.CREDITED.summary | T5 | 这笔返利已结算，可以去钱包提现，详情见卡片。 |

- agent.notice.tlj_none「暂无淘礼金活动」只在 BR-TEXT-15 判定 6 维护，本表不重复。
- 其余 order_status.&lt;display_status>.summary 与全部 order_reason.&lt;CODE>.summary 的包内默认 = 「{BR-TEXT-02 状态文案或 BR-TEXT-05 标题}，详情见卡片。」（即 BR-AI-07 的兜底拼法，例：order_reason.REFUND.summary =「订单已退款或取消，详情见卡片。」，AC-S1-44 ② 断言不变）；需要单独措辞时在上表加行。
- 自查：上表不含 BR-TEXT-13 禁用词（「佣金」只出现在 agent.disclaimer.commission 例外键），不含金额与日期变量；summary 只说状态，不说「已返」「没返」类结论以外的推断（BR-AI-07）。
- 例：游客问「我昨天的订单返了吗」→ auth_required(login) 卡 + 「登录后才能查你的订单，点下方按钮登录。」。
- 例：模型与备用模型都超时 → 关键词出卡 + 「先按关键词为你找到这些商品，详情见卡片。」，不出现错误提示。

#### BR-TEXT-23 细则 · 账号与风控站内信

- 状态：已确认（拍板第二批 OPS-15：补风控状态变更、申诉结果、注销进度模板，只发站内信；OPS-12：说明页显示原因类别与申诉入口。模板与类别文字为代理起草，运营可改措辞）
- 默认值：下表
- 决策人：负责人（措辞：运营）
- 依赖平台能力：无
- 取代：无（规划/04 notify_template.code 原只有交易与提现类）
- 来源：BR-ID-27、BR-ID-31、BR-ID-36；规划/01 F-RISK-04、F-MSG；规划/04 §2.5；docs/changes/20261001-拍板第二批.md（OPS-12、OPS-15）；docs/changes/20261001-拍板第二批.md §8 ADD-07
- 需同步修改的规划文档：规划/04 §2.5 notify_template.code 增加 RISK_STATE_CHANGED、APPEAL_RESULT、DELETION_PROGRESS；规划/01 §4.2 页面清单补封禁说明页、申诉页；GET /v1/me 返回原因类别与 frozen_until（04 §6.1）

**原因类别**（字典 risk_reason.&lt;category>；后台封禁、冻结与订单风控作废时必选一项，内部原因与规则编号只在后台可见）

| category | 用户文案 |
| --- | --- |
| malicious_rights | 异常售后维权 |
| fraud_invite | 异常邀请行为 |
| abnormal_trade | 异常交易 |
| account_security | 账户安全核验 |
| other | 违反用户协议 |

**模板**（均为站内信，category=service，不受推送开关影响）

| code / 变体 | 触发（规则） | 模板 |
| --- | --- | --- |
| RISK_STATE_CHANGED frozen | risk_state 变为 frozen、未设到期（BR-ID-36） | 你的账户提现已暂停，原因：{reason_category}。如有疑问，可在帮助中心提交申诉。 |
| RISK_STATE_CHANGED frozen_until | risk_state 变为 frozen 且设了到期时间 | 你的账户提现已暂停至 {frozen_until}，原因：{reason_category}。如有疑问，可在帮助中心提交申诉。 |
| RISK_STATE_CHANGED unfrozen | frozen 到期或人工解除 → normal | 你的账户提现已恢复。 |
| RISK_STATE_CHANGED banned | risk_state 变为 banned（BR-ID-31） | 你的账号已被限制使用，原因：{reason_category}。可在说明页提交申诉。 |
| RISK_STATE_CHANGED unbanned | 解封（BR-ID-31、BR-ID-36） | 你的账号限制已解除，购物前需重新完成平台授权。 |
| APPEAL_RESULT account_revoked | 账户申诉撤销（BR-ID-36） | 你的申诉已通过，相关限制已解除。 |
| APPEAL_RESULT order_revoked | 订单申诉撤销（BR-ID-36） | 你对一笔订单的申诉已通过，返利将在复核后恢复。 |
| APPEAL_RESULT upheld | 申诉维持 | 你的申诉已处理，维持原处理结果。如有疑问请联系客服。 |
| DELETION_PROGRESS requested | 注销申请进入冷静期（BR-ID-27） | 注销申请已提交，{cancel_deadline} 前可在「设置 → 账号与安全」撤回。 |
| DELETION_PROGRESS cancelled | 撤回注销（BR-ID-27） | 已撤回注销申请，账号恢复正常使用。 |
| DELETION_PROGRESS cancelled_negative | 冷静期满时余额为负，系统撤销注销（BR-ID-27，拍板第二批 §8 ADD-07，代理补全） | 你的账户有待扣回金额 {amount}，注销申请已撤销。后续返利抵扣回正后可重新申请，如有疑问请联系客服。 |

- {frozen_until}、{cancel_deadline} 按 BR-TEXT-11 未来时间格式；{reason_category} 取上表文案；{amount} 按 BR-TEXT-10 格式化（待扣回金额）。
- 封禁期间用户只能调 10006 白名单接口（BR-ID-31），banned 通知在解封后可见；封禁说明页显示「账号已被限制使用」、原因类别与【申诉】入口，申诉进度与结果在说明页经申诉接口查看。冻结只影响提现，钱包顶部提示按 BR-TEXT-01（「提现已暂停：{reason}」）；risk_state=frozen 时 {reason} 显示本条原因类别文案，有到期时间时附「，预计 {frozen_until} 恢复」。
- 注销进入 processing 后账号不能登录（BR-ID-27），不再发 DELETION_PROGRESS；进度只在注销进度页查询。
- 例：风控冻结用户并设 frozen_until=2026-11-30 00:00、类别 abnormal_trade → 站内信「你的账户提现已暂停至 11-30 00:00，原因：异常交易。如有疑问，可在帮助中心提交申诉。」；到期恢复后另发「你的账户提现已恢复。」。

### 12.3 本主题未决问题

1. 已关闭（C-02，负责人 2026-09-30，变更记录 §3）：原「BR-TEXT-01 方案 A/B（订单侧用「入账」还是继续用「到账」）」；负责人决定结算前一律称「预估」、结算后用「已结算」，取代方案 A，提现侧保留「已到账」（BR-TEXT-01）。
2. 入账时刻：D11 改为跟随联盟月结批次后，原 C-17「00:01 快照 → 00:05 每日入账」随 BR-FUND-04 改写，批次时点只在 BR-FUND-04、BR-FUND-18 维护（待财务确认）；BR-TEXT-04 不含时刻与算法，时刻变更不改本主题；CREDITED 推送时点按 BR-TEXT-09（2026-09-30 统一为结算批次完成后推送、免打扰时段顺延，与 BR-FUND-04 一致）。
3. 入账改为跟随联盟月结（D11，变更记录 §3），wait_days 不再用于用户侧文案；各平台联盟出账周期与出账日、结算账单覆盖的订单范围、京东与拼多多是否返回确认收货时间需在 规划/09 核实，结算周期取法与 expected_credit_period 只在 BR-FUND-04 ⑪ 维护（BR-TEXT-04；月结流程参数为变更记录 §6 遗留项）。2026-09-30 负责人补充（变更记录 §10）：用户侧显示预计结算月份（联盟返回结算时间时以联盟为准，否则确认收货月 + 1），不再显示收货月；联盟「结算时间」字段语义未实测，若实为确认收货时间，显示月份会早于实际结算月份（见 BR-FUND 6.3 第 19 条）。
4. EXPIRED_CLICK 能否判定、click_valid_days 每平台取值、后点击是否覆盖归因（BR-ATTR、规划/09）；决定 JumpTip 两句承诺何时启用。
5. 支付宝转账业务失败码清单与「明确失败」白名单（BR-TEXT-08）需沙箱实测；白名单确定前所有失败码按未知处理。
6. 代扣个税、手续费的展示与分录（BR-TEXT-06、BR-TEXT-19）随 规划/00 D12 税务师意见确认。
7. 「最低价」降价白名单模板是否合规需法务确认（BR-TEXT-13）；确认前价格历史用不含「最低」的中性表述。按拍板第二批 TRADE-18，其余价格与返利类禁用词按当前默认上线，法务意见出来后只改字典。
8. ad_label 措辞与范围（BR-TEXT-17）已由负责人按保守默认确认（2026-09-30，变更记录 §2，决策人含法务由负责人确认），范围按拍板第二批 OPS-24 细化；AI 标识措辞与位置（BR-TEXT-16）已按拍板第二批 AI-24 统一，法务另有意见时按 00 §8 修改。
9. 淘礼金 A/B/C 判定、B 类能否同时返利、我方池淘礼金剩余份数接口（BR-TEXT-15）待 规划/09 淘宝项实测。 D20 已定：素材淘礼金一律转链、不提供复制原口令；转链后是否保留第三方淘礼金待 CAP-TB-09 / 06 Q-G3 实测，证实保留时改写判定 3 话术（BR-TEXT-15）。
10. share 单是否存在跨商品归因（好友经分享进店后买其他商品）待 规划/09 实测（BR-TEXT-02）。
11. 2026–2027 年法定节假日与调休日历的录入责任人与时间（BR-WDR-26 workday_calendar）。
12. 修订① 的 D8（C 类素材是否给「复制原口令」）与 规划/00 的 D8（分销计酬）编号冲突，需在文档登记表中重新编号。
13. PUNISH 子原因对用户透出粒度需负责人与运营确认（BR-TEXT-05 默认用不含联盟术语的概括文案）。
14. 找回驳回原因字典 claim_reject_reason 的编码表由 BR-ATTR 给出（BR-TEXT-09 CLAIM_RESULT 引用）。
15. 订单状态按 C-01 改用 BR-FUND-01 双状态与 BR-FUND-17 派生的 display_status（BR-TEXT-01/02/03/04/05/09/18），已由负责人确认 2026-09-30；不采纳时按本主题开头的映射回退。
16. 已关闭：BR-FUND-17 已删去术语表，派生表文案列改为「示意」并声明以 BR-TEXT-02 为准，只保留派生条件与「状态和金额只取接口」；现派生表示意文案已用「入账核对中」「售后处理中，入账暂停」「已收货，等待联盟结算后入账」。原记录：BR-FUND-17 文案列与本主题不一致、未列入 §14.3：REVIEWING「返利审核中」对本主题「入账核对中」（本主题不透露 hold）；RIGHTS_PENDING「返利暂缓到账」、CREDITING「到账处理中」、WAITING_SETTLE「等待联盟结算后到账」对方案 A 的「入账」；BR-FUND-04 推送「¥x 已到账」对 BR-TEXT-09「已入账」。建议随 C-02 一并裁决，文案以本主题为准（BR-FUND-17 只保留派生条件）。
17. 已关闭（C-25，负责人 2026-09-30 决定，变更记录 §3：有收益的都要推送）：ORDER_TRACKED 的对象、触发、合并与去重只在 BR-TEXT-09 维护；跟单与收益通知发给该子订单全部份额 > 0 的受益人（归属用户、直推上级、间推上级），上级通知只含金额与状态（J7 隐私）；去重键 {order_key}:{uid}:{role}:TRACKED（BR-FUND-05）；BR-FUND-03 推送段引用 BR-TEXT-09。取代原默认「直推上级不推」。
18. 已关闭（C-19）：withdrawn_fen 由 BR-FUND-18 提供，钱包首页展示已提现（BR-TEXT-01）。
19. BR-TEXT-21 中 UNION_SETTLED、UNION_RECEIVED 的刷新周期取决于各联盟结算明细可取得频率（规划/09 待实测）。
20. BR-TEXT-14 新增 50301 data.reason（maintenance / not_launched）与配置 convert.off_reason.&lt;platform>，需同步 13 §13.11、规划/04 §7 与 §10.2、10 AC-S1-28-PDD；新增 rebate_basis=amount_unknown 需同步 04 §8.3、BR-PRICE-08、BR-PRICE-21（启用已由拍板第二批 TRADE-08 确认）；13 §13.11「显示服务端 msg」改为「取 error.&lt;code>」。50301 data.reason 为默认处理，待负责人确认。
21. 上级（直推、间推）跟单与收益通知属交易类，不计入 BR-WATCH-15 订阅类每日推送上限；下线较多的上级每日可能收到较多「邀请」类推送。已关闭（负责人 2026-10-03，docs/changes/20261003-拍板第三批.md §1）：不改为日汇总，跟单通知越快越好，合并窗口缩短为 notify.tracked_merge_window_seconds（BR-TEXT-09）；邀请类每日上限不设，之后如有打扰投诉由运营再提。
22. 用户侧「已结算」与 platform_status=SETTLED（联盟已结算）不同：联盟已结算、我方尚未核对入账期间用户仍看到「预估返」。WAITING、CREDITING 的派生条件（改按 BR-FUND-04 ⑪ credit_overdue）与钱包预计结算月份字段已随 BR-FUND-04 月结改写同步：BR-FUND-17 第 10、12 行，BR-FUND-18 next_credit_period、estimated_total_fen（拍板第二批 FUND-01；BR-TEXT-01、BR-TEXT-02、BR-TEXT-04 已按此改）。
23. Agent 固定话术（BR-TEXT-22）为代理起草（拍板第二批 AI-21），待负责人过目后改为已确认；新增码 30415、50304 由代理自定、负责人 2026-10-01 接受，规划/04 §7 已登记，待 13 §13.11 登记。

---
