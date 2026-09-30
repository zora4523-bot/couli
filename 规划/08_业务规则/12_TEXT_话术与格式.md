# 08 业务规则 · 12. 用户可见话术与格式（BR-TEXT）

返回 [README](README.md)（使用规则、术语表、规则索引）

## 12. 用户可见话术与格式（BR-TEXT）

本节规定：收益术语、订单/提现/流水文案、差额提示、预计入账日、原因码、通知模板、金额时间格式、禁用词、错误话术、AI 与广告标识、报表金额列口径标注。共 21 条（已确认 2、默认假设 14、待决策 3、待验证 2）。

订单状态写法：本主题按 BR-FUND-01 双状态书写（platform_status + rebate_status，用户可见状态为服务端按 BR-FUND-17 派生的 display_status）。与 规划/04 单一 order_status 的映射（BR-FUND-01）：DEPOSIT_PAID→(DEPOSIT_PAID, ESTIMATED)，PAID→(PAID, ESTIMATED)，RECEIVED→(RECEIVED, WAITING)，CREDITED→(RECEIVED 或 SETTLED, CREDITED)，SETTLED→(SETTLED, CREDITED 且已补差)，INVALID→(任意, VOID)，CLAWED_BACK→(任意, CLAWED_BACK)；规划/04 的 O1→P1、O2→P2+R2、O3→P3+R4、O4→R6、O5→R7、O6→R5、O7→P4、O8→P4+R10、O9→R8、O10→R9（入账后部分退款改写 CLAWBACK，C-16）、O11→R3。「来源」「取代」中引用的 O 编号是原文档位置，不改。按 C-01 默认处理，待负责人确认；不采纳双状态时按上述映射回退。

### 12.1 规则一览

| 编号 | 规则 | 状态 | 影响面 |
| --- | --- | --- | --- |
| BR-TEXT-01 | **收益术语唯一含义**<br>用户可见文案、客服话术、后台与报表中，下列词只能按本表含义使用：「预估返」只指尚未入账的自购返利估计值（商品卡：下单前估算；订单：rebate_status ∈ {ESTIMATED, WAITING} 的当前预估，BR-FUND-01），不可提现；「待入账」只指 rebate_status=WAITING 的返利；「已入账」只指 rebate_status=CREDITED（含部分扣回、已补差），金额已写入该账户可用余额；「可提现」等于 withdrawable_fen = max(available_fen, 0)，available_fen &lt; 0 时负数部分显示为「待抵扣」（negative_fen，BR-FUND-18）；「冻结中」等于 frozen_fen（审核中与打款中提现单的金额）；「已到账」只指提现 withdrawal_status ∈ {PAID_API, PAID_MANUAL}；「已提现」等于已到账提现单申请金额 amount_fen 的累计。PROMO 账户（分享单、直推分佣）用户侧金额一律用「推广收益」前缀（入账前「预估推广收益」），自购一律用「预估返 / 实返 / 返利」，不得混用。用户可见文案不得出现「返利到账」「佣金」（含推广佣金、比价佣金、确认收货佣金、结算佣金）与报表词「预估收益」。订单侧一律用「入账」，提现侧一律用「到账」（默认方案 A，待负责人拍板）。 | 待决策 | dict_items（order_status.&lt;display_status>、withdrawal_status、ledger_type 文案）；GET /v1/wallet/summary 字段按 BR-FUND-18（withdrawable_fen、negative_fen、frozen_fen、pending_credit_fen、pending_credit_paused_fen、next_credit_date、credit_overdue、estimated_fen、withdrawn_fen、risk_paused_reason），本条只定文案；Wallet、OrderList、OrderDetail、ProductDetail 页面；推送模板 ORDER_TRACKED / CREDITED；客服话术库；docs/glossary.md；报表与后台列名；Agent explain_order 话术；specs/banned-words.yaml（BR-TEXT-13） |
| BR-TEXT-02 | **订单状态用户文案映射**<br>订单列表与详情的状态文案必须由服务端返回的 display_status（子订单粒度；由 BR-FUND-01 的 platform_status、rebate_status 与 hold、rights_pending、金额按 BR-FUND-17 派生表从上到下取第一个匹配项，本条不另定派生顺序）按下表一一映射，文案取自 /v1/dict 的 order_status.&lt;display_status>；rebate_status=UNATTRIBUTED（未归因池，user_id 为空）的订单不得出现在任何用户接口；buy_type=share 的订单只出现在分享者的 scope=share 列表，金额前缀用「预估推广收益 / 推广收益」；直推分佣（REFERRAL）订单不得以订单形式出现在邀请人的任何列表或详情，只在余额流水按 BR-TEXT-19 显示；详情页按钮 = 状态固有按钮 + reason.action 按钮（BR-TEXT-05），最多 2 个，有 reason.action 时它为主按钮；未知状态编码必须显示 order_status.UNKNOWN 文案，不得显示编码原文。 | 默认假设 | dict_items.order_status（按 display_status 编码）；GET /v1/orders、GET /v1/orders/{order_id}（display_status、reason、reason_action、est_rebate_fen、actual_fen、clawback_fen、expected_credit_date、timeline、is_other_product）；Agent order_status 卡片；OrderList、OrderDetail 页面；验收用例 F-ORD-07（每状态 fixture + 三端截图；share 跨商品；按钮组合）；客服话术库 |
| BR-TEXT-03 | **订单差额与异常提示**<br>订单金额与首次预估不同、部分退款、维权中、入账延迟、比价风险时，必须在状态文案下按本表叠加提示；差额 = 当前金额 − initial_est_fen（该用户角色在分佣快照生成时（BR-CALC-10）的金额，单位分；首次预估为区间时取上限 rebate_max_fen；找回单以批准时生成的快照为准，BR-FUND-01 R3）；差额行只在 rebate_status=CREDITED（display_status ∈ {CREDITED, CREDITED_PART_CLAWED}）且 \|差额\| ≥ 1 分时显示；rebate_status ∈ {ESTIMATED, WAITING} 只在部分退款时显示「预估返 ¥{initial} → ¥{current}」，其他预估波动不显示差额；维权中、hold、入账延迟由 display_status（RIGHTS_PENDING、REVIEWING、CREDITING）表达，提示文案按本条；差额原因取该子订单最近一次写入的 diff 类 reason_code，无记录时用 SETTLE_DIFF；同时满足多项时按本条优先级；风控 hold 原因不得向用户透出。 | 默认假设 | orders / commission_splits（initial_est_fen、diff_reason_code、refunded_quantity_at_credit）；GET /v1/orders/{order_id}（diff_fen、diff_reason、display_status）；OrderDetail 页面；客服话术库；验收用例：部分退款（入账前 / 后）、比价区间、结算补差、维权中、hold 超期、维权与超期同时满足 fixture |
| BR-TEXT-04 | **预计入账日口径**<br>expected_credit_date 必须由服务端计算并以 +08:00 日期字符串（YYYY-MM-DD）返回，客户端不得自行推算；credit_due_at 与 expected_credit_date 的算法（含同步时刻、维权关闭或 hold 解除后的重算）只由 BR-FUND-04 维护，本条只定展示（G-16）；wait_days_snapshot 在 rebate_status 进入 WAITING 时按 settle.wait_days.&lt;platform> 写入，后续配置变更不影响已进入 WAITING 的订单；平台未返回可用收货时间的订单不进 WAITING（BR-FUND-02），不会因缺收货时间出现 expected_credit_date=null（G-14）；何时返回 null（含 credit.enabled.&lt;platform>=off）见 BR-FUND-04；只有 display_status=WAITING 且日期非 null 时展示日期，RIGHTS_PENDING、REVIEWING、WAITING_SETTLE、CREDITING 不展示；商品详情与 display_status=PAID 的订单只显示「确认收货满 {wait_days} 天后入账」，不得写死「15」，入账开关关闭时不展示（BR-FUND-04）。 | 默认假设 | orders.credit_due_at、orders.expected_credit_date、orders.wait_days_snapshot、orders.received_synced_at；GET /v1/orders/{order_id}、Agent order_status 卡片 expected_credit_date；ProductDetail「确认收货满 N 天后入账」文案（texts 变量 wait_days）；验收用例：各 display_status 是否展示日期、配置变更、入账开关关闭时不展示入账时点文案（收货时刻在任务前 / 后、延迟同步等算法用例归 BR-FUND-04）；客服话术 |
| BR-TEXT-05 | **原因码字典与文案**<br>订单 reason 只能取下表编码（规划/ 命名为准），每个编码必须在 dict_items 配置 kind（void / diff / claim）、title、desc、claimable、action；rebate_status ∈ {VOID, CLAWED_BACK}（display_status INVALID、CLAWED_BACK）的订单只能带 void 类原因，金额变化必须带 diff 类原因；claim 类编码（NOT_TRACKED、RELATION_INVALID）不得写入已归因订单的 orders.reason，只用于 explain_order、找回页查询结果；action 取值枚举 CLAIM（找回页）、REAUTH（AuthSheet）、CONTACT_CS（客服会话页）、APPEAL（申诉页），以数组存储，当前每个编码最多 1 个；reason_sub 存在时用 order_reason_sub.&lt;SUB>.desc 替换 desc，显示为「{title}：{sub.desc}」；其他文档的旧编码在同步 / 导入时映射到本表，不得新增同义编码；用户可见文案不得出现「佣金」；每个编码必须有 fixture 与截图。 | 默认假设 | contracts/enums/order_reason.json、contracts/enums/reason_action.json；dict_items.order_reason（kind、title、desc、claimable、action）、dict_items.order_reason_sub；orders.reason、orders.reason_sub；维权导入 rights-imports 映射；OrderDetail、Agent explain_order、找回页；客服话术库；验收用例：每编码 fixture + 截图；claim 类编码不出现在已归因订单 |
| BR-TEXT-06 | **提现状态用户文案**<br>提现记录状态文案必须由 withdrawal_status 按下表映射：PENDING_REVIEW 与 APPROVED 均显示「审核中」；PAYING 显示「打款中」（含结果未知期间）；PAID_API 与 PAID_MANUAL 均显示「已到账」；REJECTED 显示「未通过」且附「余额已退回」与原因；FAILED 显示「打款未成功」且附「余额已退回」与原因，【修改收款账号】入口只对账号类失败码显示（BR-TEXT-08）；「已到账」金额显示 net_fen = amount_fen − fee_fen − tax_fen，由服务端返回；PAID_MANUAL 的收款渠道名取人工补录记录的 payout_channel，不得固定写「支付宝」。 | 默认假设 | dict_items.withdrawal_status；GET /v1/withdrawals、GET /v1/withdrawals/{id}（net_fen、fee_fen、tax_fen、payout_channel_name、masked_account、fail_action）；Withdraw、WithdrawRecord 页面；推送 WD_SUCCESS / WD_REJECTED / WD_FAILED；客服话术库 |
| BR-TEXT-07 | **提现时效与超时进度**<br>提现页与审核中状态（PENDING_REVIEW、APPROVED）必须展示「人工审核，工作日 24 小时内处理，节假日顺延」；「处理」指审核结束（口径见 BR-WDR-26）。审核超时的进度推送与站内信使用模板 WD_OVERDUE，文案见细则。超时的触发与去重见 BR-WDR-26（deadline 计算、触发状态、检查间隔、夜间顺延、发送前复查、幂等键均只在该条维护）。 | 默认假设 | config: withdraw.sla_text；推送 / 站内信模板 WD_OVERDUE（新增）；Withdraw 页面；客服话术；验收 AC-S2-20、AC-S2-29 |
| BR-TEXT-08 | **提现驳回与失败原因**<br>REJECTED 的用户原因必须取自字典 withdraw_reject_reason 的编码文案，审核人可另填内部备注 reject_note 但不得展示给用户；FAILED 的用户原因必须由支付宝错误码经映射表 withdraw_fail_reason 转成用户文案，未命中映射时显示兜底文案；withdraw_fail_reason 映射表只决定展示文案，不决定状态：只有 payout 服务维护的明确失败码白名单才能触发 W6→FAILED 与 WITHDRAW_RETURN，白名单以外的码（含 SYSTEM_ERROR、超时、未收录码）一律保持 PAYING，按 W7 查询，24 小时仍未知转人工，禁止置 FAILED 或退回余额；【修改收款账号】入口只对账号类失败码（PAYEE_\*）显示；原因文案不得包含风控规则细节。 | 默认假设 | dict_items.withdraw_reject_reason、withdraw_fail_reason；payout 服务明确失败码白名单（代码常量 + 测试）；withdrawals.reject_reason（改存编码）、withdrawals.fail_code、新增 reject_note（内部）；后台提现审核页（原因下拉）；WithdrawRecord 页面；推送 WD_REJECTED / WD_FAILED、失败短信；验收用例：白名单外错误码不退回余额 |
| BR-TEXT-09 | **交易通知文案模板**<br>交易类通知必须使用下表模板（notify-templates 可改措辞，变量与含义不得改），标题与首句按 BR-TEXT-20 校验；所有金额变量均为 BR-TEXT-10 格式化后的字符串（已含 ¥ 与负号），模板中不得再写 ¥ 或 -；SELF 与 PROMO 账户分别使用各自模板，PROMO 用「推广收益」不用「返利」。触发：ORDER_TRACKED 在子订单已归因到用户（BR-FUND-01 R2）且 platform_status 首次 ∈ {PAID, RECEIVED, SETTLED} 时触发（含 DEPOSIT_PAID→PAID（P2）、同步即为 PAID、结算先到时补写的 P5），B_est=0（display_status=NO_REBATE）不触发（BR-FUND-17「跟单成功」条件），每个 (子订单, 受益人, 角色) 最多 1 次，幂等键 {order_key}:{uid}:{role}:TRACKED（order_key 见 BR-FUND-05）；直推上级不发 ORDER_TRACKED（J7）；合并窗口为固定窗口，自用户第 1 个待推事件时刻 t0 起 5 分钟，在 t0+5min 发送（单笔也延迟到 t0+5min），窗口内同账户类型事件合并，SELF 与 PROMO 分别成条，t0+5min 之后到达的事件开启新窗口；直推分佣不发 ORDER_TRACKED；CREDITED 日汇总于 D 日 09:00(+08:00) 发送，统计 [D-1 09:00, D 09:00) 内写入的 REBATE_CREDIT / SHARE_CREDIT / REFERRAL_CREDIT 流水（按 created_at，SETTLE_ADJUST 不计），0 笔不发，D 日 09:00 入账任务未完成则在任务完成后发送，每用户每日 1 条，幂等键 user_id:CREDITED:D；找回通过的订单（BR-FUND-01 R3）不发 ORDER_TRACKED，只发 CLAIM_RESULT；platform_status=DEPOSIT_PAID 不推送。 | 默认假设 | messages.yaml / notify-templates；outbox 事件 order.created / order.status_changed / order.credited / order.clawed_back / withdrawal.changed / claim.resolved 消费者；推送与站内消息；短信模板（BR-TEXT-20）；验收用例：预售单跟单推送、5 分钟窗口边界、SELF/PROMO 分条、日汇总窗口、任务延迟、找回单不重复推送、金额变量无重复符号 |
| BR-TEXT-10 | **金额格式化**<br>接口金额一律为整数分（_fen），前端用整数运算格式化，不得用浮点：展示为可选负号 + 「¥」 + 元，最多两位小数并去掉末尾 0 与多余小数点；不加千分位；负数用 ASCII「-」置于「¥」前；流水正数加「+」；返利区间在 min &lt; max 时用「–」（U+2013，前后无空格）连接两端，min = max 时显示单值，min = max = 0 时显示「暂无返利」（列表隐藏返利标签）；返利、价格金额由服务端计算，客户端不得自行乘佣金率；服务端渲染推送、短信时使用同一格式化函数，模板变量为格式化后的字符串。 | 已确认 | specs/client-behavior.md 测试向量；PriceTag、RebateTag 组件（iOS / Android / 鸿蒙 / H5）；推送、短信模板渲染（服务端同一格式化函数）；后台金额列 |
| BR-TEXT-11 | **时间与日期格式化**<br>服务端时间字段一律 ISO 8601 带 +08:00，纯日期字段（如 expected_credit_date）用 YYYY-MM-DD 字符串；客户端展示一律按 Asia/Shanghai 时区换算，不随设备时区变化，使用 24 小时制；列表中的过去时间：与当前日期（+08:00，以服务端校准后的时钟为准）同一天「今天 HH:mm」，前一天「昨天 HH:mm」，同一年「MM-DD」，其他「YYYY-MM-DD」；未来时间：同年「MM-DD HH:mm」，跨年「YYYY-MM-DD HH:mm」，不用「明天」等相对词；纯日期字段：与今天同年显示「MM-DD」，否则「YYYY-MM-DD」，不使用「今天 / 明天」；订单时间线与提现记录详情精确到分钟「YYYY-MM-DD HH:mm」。 | 默认假设 | specs/client-behavior.md 测试向量；三端与 H5 时间格式化工具；OrderList、OrderDetail、WithdrawRecord、消息列表 |
| BR-TEXT-12 | **文案来源与字典机制**<br>业务文案取值顺序必须为：/v1/config.texts[key] → /v1/dict[enum][code] → 包内默认（由同一份 contracts/texts.default.json 生成）；接口枚举字段只返回编码；客户端业务页面不得硬编码中文业务文案（lint 规则拦截）；文案变量用 {name} 占位，变量值为 null、未提供或空字符串视为缺失（0 不算缺失），缺失时回落到该 key 的包内默认，包内默认仍含该缺失变量时整条文案不渲染（元素隐藏）并上报埋点 text_var_missing（key、变量名），不得显示「{」原文；字典带版本号，客户端按版本缓存，启动时及 config 中 dict_version 变化时刷新；服务端生成的推送、短信、Agent 话术必须读同一字典。 | 已确认 | GET /v1/dict、GET /v1/config（texts、dict_version、jump_tip、jump_tip.&lt;platform>.claims_enabled）；dict_items、config_items；contracts/texts.default.json（新增）；三端与 H5 文案加载模块、lint 规则、埋点 text_var_missing；JumpTip 已读记录按 BR-ATTR-21（服务端按 user_id + platform）；后台字典 / 文案编辑页 |
| BR-TEXT-13 | **禁用词与合规表述**<br>以下词不得出现在任何用户可见文案（字典、config.texts、推送、短信、分享模板、SDUI 页面、规则文章、商品池自定义标题、Agent 固定话术、应用商店描述）：全网最低、历史最低、最低价、最便宜、最高返利、稳赚、必返、返利最高、最高返、原价（价格与返利类，BR-PRICE-18 只列词、清单在本条维护）；返利到账、佣金、预估收益、已结算、待结算、结算中、返现、充值、备付金（资金类，含 BR-FUND-17 用户侧禁用词）；「比价」只允许出现在 allow_keys 所列字段；规则类文案中的数值（入账天数、提现门槛、次数）必须由配置变量渲染；不得展示任何虚拟数据。本条是禁用词清单与匹配规则的唯一维护处，其他条目只引用。匹配顺序：先按字段位置判断白名单（白名单用原文匹配并整体剔除命中片段），再对剩余文本做 NFKC 归一、去空白与标点、英文转小写后的子串匹配。校验在 CI（扫描仓库文案与模板）和后台保存时同时执行，命中即失败；后台、报表字段不校验资金类词（佣金、预估收益、已结算、待结算、结算中、返现、充值、备付金），仍校验价格与返利类词。 | 待决策 | CI 文案扫描脚本（specs/banned-words.yaml，含 scope 与 allow_keys）；后台保存校验（dict_items、config_items、notify-templates、share 模板、pages、articles、pool-items）；价格历史组件（BR-PRICE / Watch）；Agent 固定话术；应用商店描述 |
| BR-TEXT-14 | **错误与降级话术**<br>客户端对错误码与降级场景的提示必须使用细则表文案（经字典 error.&lt;code> 下发，带 data.reason 的码另有子键 error.&lt;code>.&lt;reason>，可改措辞不可改动作）；13 §13.11 已分配的每个码（废弃码与 9xxxx 除外）在本条都有 error.&lt;code> 行，reason 子键未命中时回落到 error.&lt;code>；44001 显示字典 risk_msg.&lt;code> 文案，服务端只下发风控提示编码不下发自由文本，未命中时显示「操作未通过安全校验」；服务端 msg 只作后备，内容必须与该码包内默认一致，只在字典与包内默认都没有该键时显示（如旧版本客户端遇到新码），msg 也为空时显示「操作未完成，请稍后再试」；其他 5xxxx 通用错误态必须附 trace_id 后 6 位（不足 6 位显示全部）；50301 按 data.reason 区分「维护中」与「即将开放」；42901 按 Retry-After 禁用按钮，无 Retry-After 时禁用 5 秒；转链熔断时按钮必须置为禁用态「稍后再试」；已废弃的错误码（如 30142，BR-PRICE-14）不得保留话术行，码号以 08 §13.11 为准（04 §7 与之逐行一致）；外跳与未安装降级路径以 BR-ATTR-27 为准，本条只维护按钮与提示文案（含待跟单卡、平台能力降级、剪贴板提示条文案；剪贴板读取时机与方式只按 BR-ID-16）。 | 默认假设 | contracts/error-codes.yaml（新增 text_key、reason 枚举）；dict_items.error（含 error.&lt;code>.&lt;reason> 子键）、dict_items.risk_msg；50301 data.reason（新增，maintenance / not_launched）；ErrorActionMapper（三端与 H5）；BuyButton、Agent 对话页；客服话术（trace id 查询） |
| BR-TEXT-15 | **淘礼金卡片如实话术**<br>首版按 D7 仅使用 unknown 和关闭分支；其余分支后续接入且验证后启用。淘礼金相关卡片必须按判定结果使用下表文案，结论只能是表中 6 种判定之一；素材淘礼金 A/B/C 判定能力在 规划/09 淘宝项验证通过（有接口样例）前，所有素材淘礼金一律按 unknown 处理，B 类能否同时享受我方返利未证实前也按 unknown 展示；tlj_kind=third_party 或 unknown 的卡片不得出现「淘礼金」标签或按钮，不得暗中替换口令；剩余份数必须取接口实时值，查询失败时不显示「剩余 N 份」、按钮保持可点、领取结果以淘宝页面为准，remain=0 按「已领完」处理；{amount} 按 BR-TEXT-10 面额格式（550 → 5.5 元）；池内无匹配或 tlj.enabled=off 时只出 notice agent.notice.tlj_none「暂无淘礼金活动」，不出淘礼金卡，也不出替代的有券商品卡（BR-AI-17；C-24 默认处理，待负责人确认）。 | 待验证 | Agent rebate_quote / product_card（tlj、cta.text_key）；dict / texts：tlj.\*；商品卡、淘礼金页；config：tlj.copy_original_tpwd.enabled（默认 off）、tlj.kind_detection.enabled（默认 off）；客服话术 |
| BR-TEXT-16 | **AI 生成内容标识**<br>Agent 对话页必须在每轮 AI 回复区显示统一标识，文案唯一取 texts.ai_label，默认「内容由 AI 生成，仅供参考」；SSE meta.ai_label 必须与该值相同（服务端从同一配置读取），客户端以 meta.ai_label 为准、缺失时用包内默认；tool.status 的 display_text 只描述动作（如「正在搜索淘宝」），不得包含用户输入原文或工具参数；金额、链接、口令只能出现在卡片中，text.delta 出站过滤与 trace 记录按 BR-AI-06；Agent 页顶部与「关于」页公示模型名称与登记编号，公示文案唯一取 config.agent.filing_text（含登记编号；agent.filing_no 只作后台保存校验用，不直接展示，BR-AI-12），未取得时为空且 Agent 入口只对员工白名单开放（D16、BR-AI-12），不得显示占位或虚构编号。本条是 AI 标识文案与配置键的唯一维护处，合规义务见 BR-ID-15。 | 默认假设 | SSE meta.ai_label；config.texts.ai_label、config.agent.filing_text、config.agent.model_label；AiLabel 组件、Agent 页顶部与关于页；Agent tool.status display_text 模板；OutputGuard（BR-AI-06） |
| BR-TEXT-17 | **广告推广标识**<br>product_card.ad_label 字段必须保留，客户端遇到非 null 值必须在卡片角标原样展示，不在客户端判断业务条件；法务定性前按保守默认：首页运营位（运营手选、商家付费或置顶）与分享海报返回 ad_label=「推广」，搜索自然结果与 Agent 按相关性排序的卡片返回 null；法务定性后按结论改服务端下发规则并写入本条。 | 待决策 | product_card.ad_label；ProductCard 组件；SDUI 首页运营位；分享海报；config：ad_label 场景规则 |
| BR-TEXT-18 | **客服话术一致性**<br>客服话术库、FAQ、帮助中心、Agent 规则答疑（search_rules）与 explain_order 输出中涉及订单、返利、推广收益、提现状态和原因的表述，必须使用 BR-TEXT-01 术语并引用字典 key 渲染，不得另写同义说法；后台订单与提现详情必须同时显示「内部编码 + 用户看到的文案」；客服不得承诺字典与 expected_credit_date 以外的入账或到账时间，不得使用 BR-TEXT-13 禁用词，不得向邀请人透露下级的订单信息（J7）；字典或原因码文案变更时，话术库对应条目必须在同一次发布内更新（发布检查项）。 | 默认假设 | 客服话术库（后台 articles 或独立表）；帮助中心 H5；Agent search_rules 规则库、explain_order；后台订单详情、提现详情页；发布检查清单 |
| BR-TEXT-19 | **余额流水用户文案**<br>余额流水的类型名称必须按下表由 ledger_type 映射（字典 ledger_type.&lt;CODE>.name；CLAWBACK 的 sub_type=PART_REFUND 用 ledger_type.CLAWBACK.name_part_refund）；金额按 BR-TEXT-10 带符号显示，符号表示对可用余额的影响；列表范围按 BR-FUND-15：只展示 available 子户分录与每张打款成功提现单的 1 条 WITHDRAW_PAID 汇总条目；WITHDRAW_FEE、TAX_WITHHOLD 不单独成行，只作汇总条目明细（「代扣个税 {tax}」「手续费 {fee}」）；跳转：自购与 share 单的 REBATE_CREDIT / SHARE_CREDIT / CLAWBACK / SETTLE_ADJUST 跳转关联子订单，WITHDRAW_\* 跳转提现单；REFERRAL_CREDIT（sub_type=DIRECT 与 INDIRECT）以及受益角色为 referrer（direct / indirect）的 CLAWBACK / SETTLE_ADJUST 只显示「邀请好友订单」与金额、日期精确到日，不可跳转，不展示下级昵称、层级与任何订单信息（J7）；sub_type=INDIRECT 的名称用 ledger_type.REFERRAL_CREDIT.name_indirect（BR-CALC-05、BR-INV-20，「间推」只作内部术语）；ADMIN_ADJUST、BAD_DEBT_WRITEOFF 无关联单据时不显示跳转，显示 ledger_type.&lt;CODE>.hint 说明。 | 默认假设 | dict_items.ledger_type（name、hint）；GET /v1/wallet/ledger（link_type、link_id、masked 标记）；余额流水 H5；客服话术 |
| BR-TEXT-20 | **推送短信分享渠道约束**<br>推送、短信、分享的标题与首句不得以平台名称开头（正则 ^[【\\[]?(淘宝\|天猫\|京东\|拼多多\|美团\|阿里\|支付宝) 命中即拒），标题任何位置不得出现「官方」；校验在模板保存时与渲染后各做一次：商品标题变量（#标题#、title_short）渲染前去掉开头匹配 ^[【\\[]?(淘宝\|天猫\|京东\|拼多多\|美团\|阿里\|支付宝)[】\\]]? 的前缀并删除「官方」二字，模板不得以 #标题# 开头作为推送标题，渲染后仍命中则不发送并记录 template_render_blocked；App 图标、名称、启动页不得含平台商标；分享文案模板只允许变量 #标题# #券后价# #口令# #链接#，后台可配且过 BR-TEXT-13 校验；微信好友 / 群默认「文案 + 短链」，朋友圈默认海报；短信签名与模板长度、敏感词以短信服务商审核规则为准。 | 待验证 | notify-templates、短信模板；share 模板配置（F-SHARE-02/03）；推送标题与商品标题变量清洗函数；应用商店物料与启动页；后台模板保存校验、埋点 template_render_blocked |
| BR-TEXT-21 | **报表金额列口径与刷新标注**<br>后台页面与报表（含导出文件表头）中每个收益类金额列必须同时标明三项：口径编码（只能取 ESTIMATED 预估收益、WAITING 待入账、CREDITED 已入账、WITHDRAWN 已提现、UNION_SETTLED 联盟结算佣金、UNION_RECEIVED 联盟已回款之一，定义见细则）、数据截至时刻（+08:00，精确到分钟，显示格式按 BR-TEXT-11）、刷新方式（「实时」或实际刷新周期）；不得使用「确认收货佣金」「结算佣金」「预估结算」「未结算」「已返现」等未定义叫法；不同口径的金额不得在同一单元格相加，需要合计时分列展示；同一报表的口径编码与刷新方式由报表定义文件声明，列头由其生成，不手写。 | 默认假设 | 后台报表页与导出表头组件；报表定义文件（specs/reports/\*.yaml，新增 metric_basis、refresh 字段）；docs/glossary.md；后台资产快照报表、佣金对账报表、运营日报 |

### 12.2 细则

#### BR-TEXT-01 细则 · 收益术语唯一含义

- 状态：待决策
- 默认值：方案 A：订单侧用「入账」，提现侧用「已到账」；「返利到账」「佣金」「预估收益」用户侧禁用；PROMO 用「推广收益」前缀；钱包各金额取 BR-FUND-18 字段（预估中 = estimated_fen 单值）；已提现按申请额累计。理由：与 规划/04 术语表、后端功能规划 2.16 一致，消除「已到账」同词异义；文案走字典，可逆。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 规划/04 §2.3 用户侧状态映射：「CREDITED / SETTLED 显示「已到账」；RECEIVED「已收货，等待到账」」
  - 规划/01 §5 J4、J6 与 F-MSG-02：「已收货等待到账 → 已到账；钱包「待到账」；通知「已到账（每日汇总）」」
  - 规划/01 §5 J6 第 1 步、F-WDR-01：「冻结中（附原因）——风控冻结不再计入冻结中，改为顶部「提现已暂停」提示」
  - 规划/04 §4.2 W4/W5/W6：「冻结 → 在途 → 出金（在途不是独立余额字段，属 frozen_fen）」
  - 规划/02 §5.2：「order.credited → 推送「已到账」」
  - PRD修订_后端功能规划 2.16：「预估收益 → 待入账 → 已入账 → 已提现（作为报表口径保留，用户侧不用「预估收益」）」
  - 参考_花卷云功能查漏底稿 §12：「预估（付款）→预估结算→确认收货→已返现，另有未结算」
  - PRD v2.1 §9.3：「credit_status：ESTIMATED → HOLDING → CREDITED → REVERSED」
- 来源：规划/04 §1 术语表、§2.3、§2.4、§3.2 account_balances、§4.2 W4–W8；规划/01 §1、§5 J4/J6/J7、F-WDR-01、F-WDR-09、F-MSG-02；规划/02 §5.2；PRD修订_后端功能规划 2.16、3.2；PRD v2.1 §9.3；参考_花卷云功能查漏底稿 §12、§16 #33；README §1.2
- 需同步修改的规划文档：6 处（计数仅作记录，落点见 README §0.6）

**术语对照表（唯一口径）**：资金术语含义只在本表维护。BR-FUND-17 只维护 display_status 派生条件与「状态和金额只取接口」，BR-WDR-25 只维护提现副文案分支，README §1.2 为索引；三处与本表不一致时以本表为准。C-02 改选方案 B 时改本表、BR-TEXT-02、BR-TEXT-06 与字典。

| 用户词 | 唯一含义 | 内部状态 / 字段 | 后台·报表词 | 能否提现 |
| --- | --- | --- | --- | --- |
| 预估返 ¥x（标签）/ 预估返利（字段名） | 下单前：按当前佣金率与用户比例估算（来源见 BR-PRICE）；下单后：rebate_status ∈ {ESTIMATED, WAITING} 的订单按当前基数 B_est × 分佣快照比例（BR-FUND-03；入账前均为估计值） | 商品卡 rebate_min_fen/rebate_max_fen；订单 rebate_status ESTIMATED、WAITING | 预估收益（ESTIMATED） | 否 |
| 待入账 | 已确认收货、等待观察期满 | rebate_status=WAITING | 待入账（WAITING） | 否 |
| 已入账 | 已写入该账户可用余额 | rebate_status=CREDITED（platform_status 为 RECEIVED 或 SETTLED）；流水 REBATE_CREDIT / SHARE_CREDIT / REFERRAL_CREDIT | 已入账 | 是（计入可提现） |
| 实返 ¥y | 自购订单已入账且未被扣回的金额（含结算补差、减去部分扣回） | actual_fen（BR-TEXT-02） | 实返 | — |
| 预估推广收益 / 推广收益 | PROMO 账户金额：入账前 / 入账后 | account_type=PROMO | 推广收益 | 入账后是 |
| 可提现 | withdrawable_fen = max(available_fen, 0)；available_fen &lt; 0 时可提现显示 ¥0，另显示「待抵扣 ¥{negative}」并禁止提现（BR-FUND-18、BR-WDR-05） | account_balances.available_fen | 可提现余额 | — |
| 待抵扣 | 余额为负时需由后续入账抵扣的金额 | negative_fen = max(−available_fen, 0) | 负余额 | 否 |
| 冻结中 | 提现单处于 PENDING_REVIEW / APPROVED / PAYING 的金额（PAYING 为冻结内的在途，不另设余额字段） | frozen_fen | 冻结 | 否 |
| 已到账 | **仅提现**：支付宝确认成功或人工补录流水号 | PAID_API / PAID_MANUAL；流水 WITHDRAW_PAID「提现到账」 | 已提现 | — |
| 已提现 | Σ 已到账提现单 amount_fen（申请额，含代扣税费） | withdrawals.amount_fen | 已提现 | — |
| 实际到账 | 单笔提现打入收款账户的金额 | net_fen = amount_fen − fee_fen − tax_fen | 实付 | — |
| 跟单成功 | 订单已同步入库且归到该用户（user_id 非空）、platform_status 首次 ∈ {PAID, RECEIVED, SETTLED} 且 B_est > 0 | BR-FUND-01 R2；BR-FUND-17 | 已归因 | 否 |
| 已失效 | 入账前失效，预估作废，余额未变 | rebate_status=VOID（display_status=INVALID） | 失效 | — |
| 已扣回 | 入账后失效，余额已被扣减（可致负） | rebate_status=CLAWED_BACK；流水 CLAWBACK。部分扣回时 rebate_status 仍为 CREDITED，display_status=CREDITED_PART_CLAWED | 扣回 | — |

**钱包汇总口径**（`GET /v1/wallet/summary`，SELF / PROMO 每账户分别返回；字段定义与计算只由 BR-FUND-18 维护，本条只定文案）：
- 可提现 ¥{withdrawable_fen}；negative_fen > 0 时另显示「待抵扣 ¥{negative_fen}」，提现按钮置灰（BR-WDR-05）。冻结中 ¥{frozen_fen}。
- 风控冻结（risk_state=frozen）与提现冻结记录（withdraw_holds，BR-WDR-05）不改变余额、不计入冻结中，只在钱包顶部显示「提现已暂停：{reason}」；reason 取字典 risk_msg.&lt;code> 文案（BR-TEXT-14），不得写风控规则细节；下发字段由 BR-WDR-05 定义。
- 待入账 ¥{pending_credit_fen}（含维权中与 hold 的部分）：next_credit_date 非空且 credit_overdue=false 时附「预计 {next_credit_date} 入账」；credit_overdue=true 时附「入账核对中」；next_credit_date 为 null 时不显示日期；pending_credit_paused_fen > 0 时另附「其中 ¥{pending_credit_paused_fen} 暂缓入账」，不说明是维权还是 hold。
- 预估中 ¥{estimated_fen}（单值，不含定金阶段与未归因订单），注「按联盟最新预估计算，以实际入账为准」。
- 已提现 ¥{withdrawn_fen}（BR-FUND-18：Σ 本账户 PAID_API / PAID_MANUAL 提现单 amount_fen）；提现记录中逐单展示「实际到账 {net}」。

例：用户 A 自购账户有 3 单：(PAID, ESTIMATED) 预估 ¥2.5、(RECEIVED, WAITING) 预估 ¥4（预计入账日 10-17）、(RECEIVED, CREDITED) ¥6；无提现。接口返回 withdrawable_fen=600、pending_credit_fen=400、next_credit_date=2026-10-17、credit_overdue=false、estimated_fen=250、withdrawn_fen=0 → 钱包显示「可提现 ¥6｜待入账 ¥4（预计 10-17 入账）｜预估中 ¥2.5｜已提现 ¥0」。用户问「返利到账了吗」，客服回答：「¥6 已入账可提现，¥4 预计 10-17 入账，¥2.5 待确认收货」。

**后台 / 报表专用词**：「预估收益」「联盟结算佣金」（联盟月结付给平台的钱）只在后台与报表出现，BR-TEXT-13 按字段范围校验。

**待决策（负责人）**：
- 方案 A（默认）：订单侧「已入账 / 已收货，等待入账 / 预计入账日 / 确认收货满 N 天后入账」，提现保留「已到账」。理由：与 04 术语表「入账」、后端功能规划 2.16 一致；改动只在订单侧字典文案。
- 方案 B：订单侧保留「已到账」，提现改「提现成功」。
两方案状态含义不变，文案经 /v1/dict 下发，切换只改字典，不改代码。

**合稿修订**：钱包字段名以 BR-FUND-18 为准（数据口径归资金主题）：pending_credit_fen、pending_credit_paused_fen、next_credit_date、credit_overdue、estimated_fen、withdrawn_fen、risk_paused_reason；本条曾用的 waiting_fen、waiting_paused_fen、next_due_date、due_overdue 已改名，含义不变；BR-FUND-18 已有 withdrawn_fen，钱包首页恢复展示「已提现」（C-19，代理已定）；「可提现」原写「等于 available_fen，可为负」，改为 withdrawable_fen 与「待抵扣」分列，与 BR-FUND-17、BR-FUND-18 一致；「预估中」原写「PAID 订单 rebate_min_fen 取下限」，改为 BR-FUND-18 的 estimated_fen。按 C-01 默认处理，待负责人确认；按 C-02 默认处理（方案 A），待负责人确认。

#### BR-TEXT-02 细则 · 订单状态用户文案映射

- 状态：默认假设
- 默认值：状态粒度与文案沿用 规划/04 §2.3（已定），状态名按 BR-FUND-01 双状态换算，用户可见状态取 BR-FUND-17 派生的 display_status（派生顺序归资金主题，本条只定文案）；「到账→入账」随 BR-TEXT-01 方案 A；share 单用「推广收益」前缀、直推分佣不进订单列表（J7）、按钮合并规则、未知编码「状态更新中」、share 跨商品隐去标题为本条新补默认。
- 决策人：负责人
- 依赖平台能力：share 单是否会归入非分享商品（跨商品归因）取决于各平台推广位归因规则（规划/09 订单归属项，待实测）
- 取代：
  - PRD修订_后端功能规划 3.2：「按 union_status + rebate_status 组合映射（PAID+ESTIMATED 等）」（双状态按 BR-FUND-01 采纳，字段名以 platform_status + rebate_status 为准；本条改为按派生的 display_status 映射文案）
  - PRD v2.1 §9.3：「PRESALE_DEPOSIT、RIGHTS_PROTECTING、PLATFORM_SETTLED 状态名」（分别映射 platform_status=DEPOSIT_PAID、display_status=RIGHTS_PENDING、platform_status=SETTLED；原映射「DEPOSIT_PAID、RECEIVED+维权提示、SETTLED」按 C-01 改写）
- 来源：规划/04 §2.3、§4.1、§8.3；规划/01 §5 J4、J7 第 5 条、J8、F-ORD-07；PRD修订_后端功能规划 2.5、3.2；PRD v2.1 §9.3
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**映射表**（方案 A 文案，见 BR-TEXT-01）

| display_status（BR-FUND-17 派生） | 对应双状态（BR-FUND-01） | 状态文案 | 金额行（自购） | 附加说明（字典 hint） | 状态固有按钮 |
| --- | --- | --- | --- | --- | --- |
| DEPOSIT_PAID | (DEPOSIT_PAID, ESTIMATED) | 已付定金 | 不显示金额 | 尾款付清后计算返利 | — |
| PAID | (PAID, ESTIMATED) | 已付款，返利待确认 | 预估返 ¥x 或 ¥a–¥b | 确认收货满 {wait_days} 天后入账；比价风险提示按 BR-TEXT-03 | — |
| WAITING | (RECEIVED 或 SETTLED, WAITING) | 已收货，等待入账 | 预估返 ¥x | 预计 {expected_credit_date} 入账（BR-TEXT-04） | — |
| WAITING_SETTLE | WAITING，入账基数低于 settle.daily_min_fen 且结算额未记录（门槛默认 0，即默认不出现） | 已收货，等待联盟结算后入账 | 预估返 ¥x | 不显示预计入账日（BR-FUND-04） | — |
| CREDITING | WAITING，expected_credit_date 早于今天（+08:00） | 入账核对中 | 预估返 ¥x | 如有疑问请联系客服（BR-TEXT-03） | — |
| RIGHTS_PENDING | ESTIMATED 或 WAITING，rights_pending=true | 售后处理中，入账暂停 | 预估返 ¥x | 售后结束后重新计算入账日（BR-TEXT-03） | — |
| REVIEWING | ESTIMATED 或 WAITING，hold=true | 入账核对中 | 预估返 ¥x | 如有疑问请联系客服；不显示 hold 原因与预计入账日（BR-TEXT-03） | — |
| NO_REBATE | ESTIMATED / WAITING 且 B_est=0，或 CREDITED 且无入账凭证（B_credit=0） | 本单无返利 | 不显示金额 | — | — |
| CREDITED | (RECEIVED 或 SETTLED, CREDITED)，无 CLAWBACK | 已入账 | 实返 ¥y（含结算补差） | 差额行（BR-TEXT-03） | 去提现 |
| CREDITED_PART_CLAWED | CREDITED 且存在 CLAWBACK（部分扣回，含入账后部分退款） | 已入账（部分扣回 {z}） | 实返 ¥y | 差额行（BR-TEXT-03） | 去提现 |
| INVALID | (任意, VOID) | 已失效 | 返利 ¥0 | 原因标题 + 说明（BR-TEXT-05，仅 void 类） | —（按钮只来自 reason.action，如 BLACKLIST→去申诉，PUNISH/OTHER→联系客服） |
| CLAWED_BACK | (任意, CLAWED_BACK) | 已扣回 | 扣回 -¥z | 原因 + 「已从余额扣除」 | 查看流水 |
| 未知编码 | — | 状态更新中 | 不显示 | 请稍后查看 | — |

各行的判定条件与先后顺序只由 BR-FUND-17 派生表维护，上表「对应双状态」列仅供阅读；两处不一致时以 BR-FUND-17 为准，本表只维护文案列。原 规划/04 的 RECEIVED 行对应 WAITING、CREDITED 与 SETTLED 两行合并为 CREDITED（平台是否已结算不影响用户文案）。

**金额字段**（服务端计算，客户端不推算，单位分）：
- 预估：est_rebate_fen 或 rebate_min_fen / rebate_max_fen。
- 实返 y = actual_fen = credited_fen + Σ 该子订单本账户 SETTLE_ADJUST 流水金额（带符号）− Σ 该子订单本账户 CLAWBACK 流水金额绝对值（display_status ∈ {CREDITED, CREDITED_PART_CLAWED} 时展示）。
- 扣回 z = clawback_fen = Σ 该子订单本账户 CLAWBACK 流水金额绝对值（含 sub_type=PART_REFUND 的部分扣回，BR-FUND-08）。

**share 单（分享者视角）**：状态文案同上；金额行「预估推广收益 ¥x」/「推广收益 ¥y」；不展示买家信息。子订单 product_key 与分享时 link_id 登记的商品不一致时，标题显示「好友购买的其他商品」，不展示标题、图片、SKU（平台是否存在跨商品归因见 规划/09，待实测）。

**时间线**（详情页）：付款 {paid_at} → 收货 {received_at} → 预计入账 {expected_credit_date} → 入账 {credited_at}；display_status 为 INVALID / CLAWED_BACK 时追加「失效 / 扣回 {time}」节点，CREDITED_PART_CLAWED 追加「部分扣回 {time}」节点；未发生的节点置灰；时间格式见 BR-TEXT-11。

例：子订单 (PAID, ESTIMATED)，预估区间 320–450 分 → 列表「已付款，返利待确认｜预估返 ¥3.2–¥4.5」；收货后 (RECEIVED, WAITING)、预估 450 分、expected_credit_date=2026-10-17 → 「已收货，等待入账｜预估返 ¥4.5｜预计 10-17 入账」。(SETTLED, CLAWED_BACK) + PUNISH → 按钮「联系客服」（主）+「查看流水」。

**边界**：部分退款不改变 rebate_status（BR-FUND-01 R7 / R9），入账前只改金额与差额行，入账后写 CLAWBACK（sub_type=PART_REFUND）使 display_status 变为 CREDITED_PART_CLAWED；hold、维权中不是 rebate_status，而是 display_status 的派生条件（REVIEWING、RIGHTS_PENDING），提示文案按 BR-TEXT-03。

按 C-01 默认处理，待负责人确认；入账后部分退款按 C-16 默认处理，待财务确认。

#### BR-TEXT-03 细则 · 订单差额与异常提示

- 状态：默认假设
- 默认值：差额基准 = 首次分佣快照金额，区间取上限；阈值 1 分；入账前只对部分退款显示变化；原因取最近一次 diff 类 reason_code；hold 对用户只说「入账核对中」。理由：01 J4 与 04 §2.3 要求显示差额原因但未定基准与阈值；取上限使用户看到的最高金额与实返之差都有原因说明，减少客诉。
- 决策人：负责人
- 依赖平台能力：无
- 取代：无
- 来源：规划/01 §5 J4；规划/04 §2.3、§4.1 O5/O7/O10/O11；PRD修订_后端功能规划 2.6（入账金额、失效与扣回）、3.2；PRD v2.1 §9.3 RIGHTS_PROTECTING
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

| 情形 | 判定（服务端） | 提示 |
| --- | --- | --- |
| 部分退款（入账前） | rebate_status ∈ {ESTIMATED, WAITING} 且 refunded_quantity > 0 | 叠加「部分退款，返利按剩余金额计算：预估返 ¥{initial} → ¥{current}」 |
| 实返 ≠ 首次预估（含入账后部分退款） | rebate_status=CREDITED 且 abs(diff) ≥ 1 | 叠加「比预估少 ¥2.1：{reason.title}」或「比预估多 ¥0.5：{reason.title}」；存在 sub_type=PART_REFUND 的 CLAWBACK（入账后 refunded_quantity 大于入账时快照 refunded_quantity_at_credit）时原因取 PART_REFUND |
| 维权中 | display_status=RIGHTS_PENDING（rights_pending=true，BR-FUND-06） | 状态文案「售后处理中，入账暂停」+ hint「售后结束后重新计算入账日」，隐藏预计入账日 |
| hold | display_status=REVIEWING（hold=true，BR-FUND-06） | 状态文案「入账核对中」+ hint「如有疑问请联系客服」，不显示 hold 原因与预计入账日 |
| 入账延迟 | display_status=CREDITING（WAITING 且 today(+08:00) > expected_credit_date） | 状态文案「入账核对中」+ hint「如有疑问请联系客服」 |
| 比价风险 | display_status=PAID 且 rebate_basis=price_compare_risk | 金额显示区间 ¥a–¥b，hint「如被判定为比价订单，返利按较低金额计算」 |

**优先级**：
1. hold、维权中、入账延迟是互斥的 display_status，按 BR-FUND-17 派生顺序只取一个（hold → 维权中 → 入账延迟）；hold 与维权同时存在时显示「入账核对中」。
2. 入账后部分退款与实返 ≠ 首次预估不分两行，只显示差额行，原因 PART_REFUND。
3. 比价风险只在 display_status=PAID，可与部分退款（入账前）同时显示，部分退款行在上。
4. diff 由多次调整叠加时只显示净差额与最近一个原因；diff = 0 不显示。

例 1：首次预估 520 分，入账时联盟按比价规则给出 310 分 → diff = -210 → 详情「实返 ¥3.1｜比预估少 ¥2.1：比价订单」。
例 2：PAID 区间 320–450 分（initial_est_fen=450），最终入账 320 分 → 「实返 ¥3.2｜比预估少 ¥1.3：比价订单」。
例 3：入账 800 分后买家退 1 件（共 2 件），写 CLAWBACK（sub_type=PART_REFUND）400 分（BR-FUND-08）→ display_status=CREDITED_PART_CLAWED →「已入账（部分扣回 ¥4）｜实返 ¥4｜比预估少 ¥4：部分退款」。

合稿修订：维权中、入账延迟原为本条自定的叠加提示（hold 只在过期后以「入账核对中」出现），现改为 BR-FUND-17 派生的 display_status，hold 在入账前任何阶段即显示「入账核对中」；例 3 原写负向 SETTLE_ADJUST，改为 CLAWBACK。按 C-01 默认处理，待负责人确认；按 C-16 默认处理，待财务确认。

#### BR-TEXT-04 细则 · 预计入账日口径

- 状态：默认假设
- 默认值：预计入账日由服务端计算，算法（含同步时刻、维权关闭或 hold 解除时刻）按 BR-FUND-04（唯一维护处），本条只定展示；wait_days 收货时快照；拿不到收货时间的订单不进 WAITING（BR-FUND-02），不因缺收货时间返回 null（G-14 默认处理，待负责人确认）；其余返回 null 的情形见 BR-FUND-04。理由：「收货日 + 15 天」在收货时刻晚于任务时刻时比实际早 1 天；配置变更与延迟同步都会让已展示日期失真。
- 决策人：负责人
- 依赖平台能力：京东、拼多多订单接口是否返回确认收货时间，以及三家可入账事件与观察期定义（规划/09 订单同步项，待实测）；淘宝收货时间字段同样待接口样例确认
- 取代：
  - 规划/04 §2.3、规划/01 §5 J1 第 6 步：「预计到账日 = 收货日 + 15 天」
  - PRD修订_后端功能规划 3.2：「预计到账日 = credit_due_at」
  - PRD v2.1 §9.3：「预计入账日（收货日 + 观察期）」
- 来源：规划/04 §2.3、§4.1 O3/O6；规划/02 §5.2；规划/00 D11；PRD修订_后端功能规划 2.6、3.2
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

- wait_days 按平台配置 settle.wait_days.&lt;platform>，默认 15（D11；后端功能规划 2.6 允许按平台配置）；进入 WAITING 时写入 orders.wait_days_snapshot。
- 入账任务时刻、快照等待、credit_due_at 与 expected_credit_date 的计算及算例（收货时刻在任务前 / 后、恰等于 run_at、延迟同步、维权或 hold 解除、入账开关打开）只在 BR-FUND-04（例 1–4 及各分支）维护，本条不复述。

展示：

| 项 | 规则 |
| --- | --- |
| 日期格式 | 接口返回 +08:00 日期字符串 YYYY-MM-DD；页面「预计 {expected_credit_date} 入账」（BR-TEXT-03 WAITING 行），按 BR-TEXT-11 纯日期字段格式化（同年 MM-DD，否则 YYYY-MM-DD）；客户端只格式化，不推算、不改写 |
| 显示日期的 display_status | 仅 WAITING 且 expected_credit_date 非 null |
| 不显示日期的 display_status | DEPOSIT_PAID、PAID、RIGHTS_PENDING、REVIEWING、WAITING_SETTLE、CREDITING（「入账核对中」，BR-TEXT-03），以及入账后各状态；过期未入账不得把日期自动改写为今天 |
| 入账时点文案 | 商品详情与 display_status=PAID 的订单显示「确认收货满 {wait_days} 天后入账」，wait_days 取当前 settle.wait_days.&lt;platform>（PAID 尚无快照），不得写死「15」；credit.enabled.&lt;platform>=off 时不展示（BR-FUND-04 开关表） |
| 钱包 next_credit_date | 过期处理按 BR-FUND-18（返回今天 + credit_overdue=true，文案「入账核对中」，BR-TEXT-01） |

例（配置变更，属快照口径）：订单 10-01 收货时 wait_days=15 写入快照；10-05 运营改为 10 → 该订单仍按 15 天，商品详情新文案显示「确认收货满 10 天后入账」。

边界：expected_credit_date 何时返回 null（ESTIMATED、WAITING_SETTLE、维权中 / hold、credit.enabled.&lt;platform>=off 等）及解除后的重算见 BR-FUND-04；本条只按上表决定是否展示（G-16 默认处理，待负责人确认）。

按 C-01 默认处理，待负责人确认。合稿修订：原细则中的 run_at 00:05、00:01～00:30 快照等待与四个计算例已删，以 BR-FUND-04 为准（原复述缺 credit.enabled.&lt;platform>=off 分支）；入账时刻 C-17 只在 BR-FUND-04、BR-FUND-18 维护。

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

合稿补入：COMMISSION_ZERO 是 BR-FUND-07 定义的 VOID 原因（B_est 由 >0 变 0 而平台未回传失效），原表缺失；本表编码与 BR-FUND-07 的 reason_code 清单（REFUND / RIGHTS / PUNISH / BLACKLIST / COMMISSION_ZERO）一一对应，BR-FUND-08 CLAWBACK 的 sub_type（FULL / PART_REFUND / RIGHTS / PUNISH）不是原因码，不在本表。「失效 / 扣回」状态名按 BR-FUND-01（VOID、CLAWED_BACK）；按 C-01 默认处理，待负责人确认。

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
| PAID_API | 已到账 | 「已转入支付宝 {masked_account}，到账 {net}」；有扣税时「已代扣个税 {tax}」 |
| PAID_MANUAL | 已到账 | 「已通过{payout_channel_name}转入 {masked_account}，到账 {net}」；扣税同上 |
| REJECTED | 未通过 | 驳回原因（BR-TEXT-08）+ 退回金额，措辞按 BR-WDR-25 |
| FAILED | 打款未成功 | 失败原因（BR-TEXT-08）+ 退回金额，措辞按 BR-WDR-25；账号类失败码加【修改收款账号】 |
| 未知编码 | 处理中 | — |

例：申请 1000 分，fee 0、tax 0 → 成功后「已到账｜已转入支付宝 138****5678，到账 ¥10」。申请 1000 分、代扣 80 分 → 「到账 ¥9.2，已代扣个税 ¥0.8」。

边界：PAYING 超 24 小时转人工后用户侧仍显示「打款中」；人工确认结果后按终态显示。流水 WITHDRAW_PAID 名称为「提现到账」（BR-TEXT-19）。若 BR-TEXT-01 选方案 B，PAID_\* 改为「提现成功」。扣税展示随 规划/00 D12 税务口径。

提现状态标题（withdrawal_status → 用户状态）只在本条维护：BR-WDR-25 不再列状态标题，只维护非 PAID_\* 状态的副文案分支条件与展示字段，上表「附加信息」列中 PENDING_REVIEW、APPROVED、PAYING、REJECTED、FAILED 行的副文案措辞与分支以 BR-WDR-25 细则表为准，本表只列要素；PAID_\* 行的副文案在本条维护。BR-FUND-17 不再写提现文案。按 C-02 默认处理（方案 A：PAID_\* 为「已到账」，FAILED 为「打款未成功」），待负责人确认。

#### BR-TEXT-07 细则 · 提现时效与超时进度

- 状态：默认假设
- 默认值：时效说明文案「人工审核，工作日 24 小时内处理，节假日顺延」；超时推送模板 WD_OVERDUE 文案见下。时限计算、触发状态、检查间隔、夜间顺延、发送前复查与去重见 BR-WDR-26。理由：01 J6 文案已定；触发逻辑只在 BR-WDR-26 维护一处。
- 决策人：运营
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 2.9 用户侧状态：「审核中=PENDING_REVIEW（工作日 24 小时内完成）」
  - 本条旧版：「处理时限 deadline = 申请时刻起累计 24 个工作小时…超时检查任务每 5 分钟运行…判定时状态仍 ∈ {PENDING_REVIEW, APPROVED} 时推送 1 次进度通知（幂等键 withdrawal_id:OVERDUE），判定时刻在 22:00–08:00 的推送延至 08:00 发送，发送前复查」（与 BR-WDR-26 旧版重复维护且状态集合、幂等键不一致；触发逻辑并入 BR-WDR-26，取值沿用本条旧版）
- 来源：规划/01 §5 J6 第 4 步；PRD修订_后端功能规划 2.9
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 展示位置：提现页、提现记录中 PENDING_REVIEW 与 APPROVED（用户侧均为「审核中」）的单据。
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

- 状态：默认假设
- 默认值：模板措辞随 BR-TEXT-01 方案 A；ORDER_TRACKED 按 platform_status 首次进入 PAID 及之后状态触发、本单无返利不推；5 分钟固定窗口；CREDITED 每日 09:00 汇总前 24 小时流水；直推分佣不推跟单；DEPOSIT_PAID 不推；找回单只发 CLAIM_RESULT。理由：规划/ 只定了通知清单与频控，未定模板、窗口、发送时刻与找回单是否重复推送。
- 决策人：运营
- 依赖平台能力：无
- 取代：
  - 规划/02 §5.2：「order.credited → 推送「已到账」（每日汇总）」
  - PRD修订_后端功能规划 2.14：「ORDER_TRACKED 由 order.attributed 触发（以 规划/ 事件名为准，触发条件按本条「首次进入 PAID」）」
- 来源：规划/01 §5 J1 第 5–6 步、J7 第 5 条、F-MSG-02、F-MSG-04；规划/04 §4.1 O2；PRD修订_后端功能规划 2.14；PRD v2.1 §6、§9.3
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

| code | 渠道 | 模板（方案 A） |
| --- | --- | --- |
| ORDER_TRACKED SELF 1 笔 | 推送 + 站内 | 跟单成功：{title_short}，预估返 {rebate} |
| ORDER_TRACKED SELF 合并 n≥2 | 同上 | {n} 笔订单跟单成功，预估返共 {rebate_sum} |
| ORDER_TRACKED PROMO（share 单，发给分享者）1 笔 | 同上 | 有好友通过你的分享下单，预估推广收益 {rebate} |
| ORDER_TRACKED PROMO 合并 n≥2 | 同上 | 有 {n} 笔好友订单来自你的分享，预估推广收益共 {rebate_sum} |
| ORDER_INVALID SELF | 站内 | 订单已失效：{reason.title} |
| ORDER_INVALID PROMO（share 单） | 站内 | 一笔分享订单已失效，不再计算推广收益：{reason.title} |
| CREDITED 仅 SELF | 推送 + 站内 | 有 {n} 笔返利已入账，共 {sum}，可提现 |
| CREDITED 仅 PROMO | 推送 + 站内 | 有 {m} 笔推广收益已入账，共 {promo_sum}，可提现 |
| CREDITED 两者都有 | 推送 + 站内 | 有 {n} 笔返利已入账，共 {sum}；推广收益已入账 {promo_sum}，可提现 |
| CLAWBACK SELF | 推送 + 站内 | 订单返利已扣回 {amount}：{reason.title} |
| CLAWBACK PROMO（share 单） | 推送 + 站内 | 一笔分享订单的推广收益已扣回 {amount}：{reason.title} |
| CLAWBACK PROMO（直推分佣） | 推送 + 站内 | 一笔邀请好友订单的推广收益已扣回 {amount}（不带原因，J7） |
| WD_SUCCESS | 推送 + 站内 | 提现已到账：{net} 已转入{payout_channel_name} |
| WD_REJECTED | 推送 + 站内 | 提现未通过：{reason}，{amount} 已退回余额 |
| WD_FAILED | 推送 + 站内 + 短信 | 提现打款未成功：{reason}，{amount} 已退回余额；账号类失败码追加「，可修改收款账号后重试」 |
| CLAIM_RESULT | 站内 | 订单找回成功，预估返 {rebate} / 订单找回未通过：{reason}（claim_reject_reason.&lt;CODE>.title，BR-ATTR 维护） |

- {amount} 在 CLAWBACK 中为负值格式（如 -¥3.2）；{rebate} 为区间时按 BR-TEXT-10 格式化；合并求和对下限、上限分别求和：两单 ¥1–¥2 与 ¥3 → 「预估返共 ¥4–¥5」。
- title_short = 商品标题先按 BR-TEXT-20 去平台前缀与「官方」，再按 Unicode 扩展字素簇取前 12 个 + 「…」；原标题 ≤12 个字素时不加「…」。

例 1：用户 14:00:10、14:03:40 两单跟单 → t0=14:00:10，14:05:10 推 1 条「2 笔订单跟单成功，预估返共 ¥7.3」；14:06:00 第三单 → 新窗口，14:11:00 推「跟单成功：…」。
例 2：D=10-17，00:05 入账任务写入 2 笔 REBATE_CREDIT（¥4.5、¥6）→ 10-17 09:00 推「有 2 笔返利已入账，共 ¥10.5，可提现」；10-17 11:00 人工补入 1 笔 → 计入 10-18 09:00 的汇总。

营销类 22:00–08:00 不发；交易类不受限，但 CREDITED 固定 09:00、WD_OVERDUE 的发送时刻按 BR-WDR-26。

例 3：京东子订单同步时平台已回传「完成」、已归因，B_est=0 → display_status=NO_REBATE，不发 ORDER_TRACKED；同一子订单后续 B_est 变为 >0 也不补发（BR-FUND-03：预估金额后续变化不推送）。

触发条件中的状态名按 BR-FUND-01（原写「首次进入 PAID（O2）」）；按 C-01 默认处理，待负责人确认。

ORDER_TRACKED 的推送对象、触发、合并与去重只在本条维护（BR-FUND-03 引用本条）：自购受益人与 share 单分享者各推自己的份额，直推上级不推；幂等键由原 order_id:TRACKED 改为 {order_key}:{uid}:{role}:TRACKED（order_key 定义见 BR-FUND-05）。按 C-25 默认处理，待负责人确认。

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

#### BR-TEXT-11 细则 · 时间与日期格式化

- 状态：默认假设
- 默认值：「昨天」附带 HH:mm；固定 Asia/Shanghai；未来时间与纯日期不用相对词。理由：规划/03 §10.3 示例「昨天」未写是否带时间，且未定设备时区、未来时间与纯日期的处理。
- 决策人：代理可自定
- 依赖平台能力：无
- 取代：
  - 规划/03 §10.3：「列表「今天 14:03 / 昨天 / 09-27 / 2025-12-31」」
- 来源：规划/03 §10.3；规划/04 §5 时间
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
| 日期 2026-09-29 | 预计 09-29 入账 | — |
| 日期 2026-10-17 | 预计 10-17 入账 | — |
| 日期 2027-01-02 | 预计 2027-01-02 入账 | — |

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

- key 命名：`order_status.<display_status>.label|hint`（CODE 为 BR-FUND-17 派生的 display_status）、`order_reason.<CODE>.title|desc|action`、`order_reason_sub.<SUB>.desc`、`claim_reject_reason.<CODE>.title`、`withdrawal_status.<CODE>.label|hint`、`withdraw_reject_reason.<CODE>`、`withdraw_fail_reason.<CODE>`、`ledger_type.<CODE>.name|hint`、`error.<code>`、`risk_msg.<code>`、`tlj.*`、`btn.buy`（去购买）、`tag.rebate`（预估返）、`auth_tips.<platform>`、`jump_tip`、`ai_label`、`pending_track_card.title|desc`（BR-TEXT-14，G-05）、`clipboard.prompt`（BR-TEXT-14，G-20）。
- 未知编码：显示 `<enum>.UNKNOWN`（订单「状态更新中」、提现「处理中」）。
- 后台修改字典或 texts：保存前过禁用词校验（BR-TEXT-13）与变量校验（模板变量必须与包内默认一致），发布时 dict_version +1，写审计。

**JumpTip**：
- 展示次数与已读记录按 BR-ATTR-21（每用户每平台首次外跳前 1 次，服务端记已读）。（G-13 默认处理，待运营确认；原「前 3 次、设备本地计数、不分平台、prefs.jump_tip_off」已删除。）
- 正文至少含「在打开的商品页直接下单」。「点击后 {click_valid_days} 天内下单有效」与「中途点其他返利链接可能导致丢单」两句，在对应平台的 规划/09 归因项验证通过后，按平台开关 jump_tip.&lt;platform>.claims_enabled（默认 off）启用；未验证平台不展示有效天数。

例：config.texts 未配置 order_reason.EXPIRED_CLICK.desc，字典值为「点击链接超过 {click_valid_days} 天才下单」，接口未下发 click_valid_days（null）→ 变量缺失，回落包内默认；包内默认同样含该变量 → desc 隐藏、只显示 title，并上报 text_var_missing（key=order_reason.EXPIRED_CLICK.desc，变量 click_valid_days）。变量值为 0（如 {n}=0）→ 正常渲染。（原例用 order_status.RECEIVED.hint 与维权中的 null；双状态下维权中是独立的 display_status=RIGHTS_PENDING，WAITING 订单不存在 expected_credit_date 为 null 的分支（BR-FUND-02，G-14），故换例。）

#### BR-TEXT-13 细则 · 禁用词与合规表述

- 状态：待决策（原标默认假设；默认值含待法务确认的词与降价模板，属合规定性，按 README §0.3 改为待决策）
- 默认值：F-PRIV-09 原清单（全网最低、历史最低、最便宜、最高返利、稳赚、必返）已定；新增「最低价」「返利到账」「佣金」「预估收益」与「比价」字段白名单为默认；「返利最高」「最高返」「原价」（BR-PRICE-18 提出，待法务确认）与「已结算」「待结算」「结算中」「返现」「充值」「备付金」（资金类用户侧禁用词，原列于 BR-FUND-17，现只在本条维护）确认前默认启用；降价白名单模板待法务确认，确认前使用不含「最低」的中性表述。理由：宁可多拦，误伤只需改写文案，漏拦有广告法风险；清单只在本条维护，避免三处各列一份。
- 决策人：法务
- 依赖平台能力：无
- 取代：
  - 规划/01 F-PRIV-09：「禁用词：全网最低、历史最低、最便宜、最高返利、稳赚、必返（本条补入新增词、字段白名单与归一化规则）」
- 来源：规划/01 §1、F-PRIV-09、F-SHARE-02；规划/06 Q-F4；PRD v2.1 §10.14、§10.19、§15；参考_花卷云功能查漏底稿 §17
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 禁用词表 specs/banned-words.yaml：每个词列出 scope（user_visible）与 allow_keys（dict key 通配），CI 与后台按 key 判定。
- 一处维护：BR-PRICE-18 只列价格与返利类用词及改写方式，资金术语含义只在 BR-TEXT-01 维护（BR-FUND-17 不再列词）；各处提到的禁用词以本条清单为准，新增词只改本条与 specs/banned-words.yaml。「结算补差」「结算金额调整」等字典文案不含上述资金类词（子串不命中），无需白名单。
- 「比价」allow_keys：order_reason.PRICE_COMPARE.title|desc、rebate_basis=price_compare_risk 的订单状态 hint（order_status.PAID.hint 的比价变体），以及渲染了上述字段的推送 / 站内信（ORDER_INVALID、CLAWBACK）；卖点、广告位、分享标题、应用商店描述命中。卖点统一表述为「找货 + 返利透明 + 丢单兜底」。
- 归一化例：「全 网 最 低！」→ 命中「全网最低」。
- **降价表述（待法务确认）**：规划/01 §1 已写明「最低价」有《广告法》与《互联网平台价格行为规则》风险。法务确认前价格历史组件只用「自 {start_date} 以来我们记录到的价格：当前 {current}，曾为 {low}」，不出现「最低」二字，无白名单；法务同意后才启用白名单模板，正则（原文匹配）`^自 ?\d{4}-\d{2}-\d{2} ?以来我们观察到的最低价`，start_date 固定 YYYY-MM-DD 完整格式，不适用 BR-TEXT-11 相对格式。组件本身归 BR-PRICE / Watch。
- 虚拟数据：虚拟原价、虚拟剩余名额、佣金头条播报、手填浏览数一律不做；淘礼金剩余份数必须来自接口实时值。
- 后台命中返回 20001（data.fields 指出字段与命中词）。Agent 生成内容的禁用词处理见 BR-AI。

例：运营在分享模板写「#标题# 全网最低价 #券后价#」→ 保存返回 20001「命中禁用词：全网最低、最低价」。字典 order_reason.PRICE_COMPARE.desc 含「比价」→ 通过；首页 banner 标题「比价神器」→ 命中。

#### BR-TEXT-14 细则 · 错误与降级话术

- 状态：默认假设（原标已确认；与 BR-PRICE-14 在 30142 上冲突（C-03），不满足「无争议」，删行后待 C-03 确认）
- 默认值：下表文案与动作为代理补全的默认值（依据 规划/03 §4.2、规划/04 §7）；码号以 08 §13.11 为准（04 §7 与之逐行一致）；30142 已废弃（BR-PRICE-14），券失效的提示与处理按 BR-PRICE-14，本表不再列 30142；表外码按本条通用规则兜底。
- 决策人：代理可自定（码号分配按 C-03，由负责人确认）
- 依赖平台能力：无
- 取代：
  - 规划/03 §4.2：「30131 显示「暂不支持该平台」；50301「该平台维护中」」
  - PRD修订_后端功能规划 7 降级表：「Agent 搜索故障「××平台暂时查不到」」
- 来源：规划/03 §4.2、§7.2；规划/04 §7；规划/02 §14；PRD v2.1 §10.5、§10.9；PRD修订_后端功能规划 2.12、7；PRD修订_双品牌与Agent找货 3.5、3.9
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**表 A · 错误码文案**（键 error.&lt;code>；码值、含义、可重试以 13 §13.11 为准，本表只维护文案与按钮；「—」表示静默处理、不弹提示；变量缺失按 BR-TEXT-12 回落，带变量的行另给「包内默认」，保证变量缺失时仍有提示）

| 码 | 文案（字典默认） | 包内默认（变量缺失时） | 动作 |
| --- | --- | --- | --- |
| 10001 | 请先登录 | 同左 | 跳 Login，成功后恢复 pending_action |
| 10002 | — | — | 单飞刷新后重放；刷新失败按 10404 |
| 10003 | 为保障资金安全，请先完成短信验证 | 同左 | 弹短信验证，拿到 step_up_token 后重放 |
| 10004 | 请先阅读并同意相关授权 | 同左 | 按 data.consent_type 弹对应同意组件（组件内文案见 BR-ID-11、BR-ID-12、BR-ID-14） |
| 10005 | 请先绑定手机号 | 同左 | 跳 BindPhone，完成后恢复 pending_action |
| 10006 | 账号已被限制使用 | 同左 | 封禁说明页 + 申诉入口 |
| 10007 | 账号注销处理中 | 同左 | data.stage=冷静期时跳注销进度页（可撤回），不弹本提示 |
| 10401 | 请求已失效，请重试 | 同左 | 不自动重放，上报埋点 |
| 10402 | — | — | 重新注册设备后重放 1 次；仍失败按「其他 5xxxx」 |
| 10403 | 请在 App 内操作 | 同左 | 不跳登录 |
| 10404 | 登录已过期，请重新登录 | 同左 | 清会话，跳 Login |
| 20001 | 填写内容有误，请检查 | 同左 | data.fields 所列字段旁标红 |
| 20002 | 验证码错误，请重新输入 | 同左 | — |
| 20003 | 验证码已失效，请重新获取 | 同左 | — |
| 20901 | 请求内容有变化，请重新提交 | 同左 | 生成新幂等键，由用户重新提交 |
| 20902 | 状态已变化，请刷新后重试 | 同左 | 刷新详情 |
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
| 30144 | 购买链接已失效，正在重新获取 | 同左 | 重新请求转链（BR-ATTR-05） |
| 30151 | 这个淘宝账号暂时无法绑定到当前账号，本次购买无法获得返利 | 同左 | 【仍去购买（无返利）】【联系客服】；不透露对方账号与冷却原因（BR-ID-18、BR-ID-19） |
| 30152 | 暂不能换绑，{available_at} 后可再次换绑 | 暂不能换绑，请稍后再试 | available_at 取 data.available_at，按 BR-TEXT-11 未来时间格式（同年「MM-DD HH:mm」，跨年「YYYY-MM-DD HH:mm」） |
| 30153 | 该平台返利已被停用，请联系客服 | 同左 | 【仍去购买（无返利）】【联系客服】（BR-ID-17、BR-ID-18） |
| 30201 | 没有找到这笔订单，请核对订单号；刚下单的订单可能还未同步，请稍后再试 | 同左 | — |
| 30202 | 这笔订单暂不能找回 | 同左 | 按 data.reason 取表 B 子键 |
| 30203 | 今日找回次数已用完，请明天再试 | 同左 | 按 data.reason 取表 B 子键 |
| 30204 | 这笔订单已被认领，无法找回 | 同左 | 不透露认领方信息 |
| 30205 | 你已提交过这笔订单的找回 | 同左 | 跳找回记录 |
| 30206 | 找回功能暂时关闭，请稍后再试 | 同左 | 找回入口置灰 |
| 30301 | 可提现余额不足 | 同左 | — |
| 30302 | 账户有待抵扣金额，抵扣完成前暂不能提现 | 同左 | 展示负余额说明（「待抵扣」口径见 BR-TEXT-01） |
| 30303 | 暂不满足提现条件 | 同左 | 按 data.reason 取表 B 子键 |
| 30304 | 请先完成实名认证 | 同左 | 跳 RealName |
| 30305 | 请先绑定收款支付宝账号 | 同左 | 跳 PayoutAccount |
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
| 30411 | 该手机号已注册，可退出后用手机号登录 | 同左 | — |
| 30412 | 有进行中的提现，提现完成后再申请注销 | 同左 | — |
| 30413 | 未满 18 周岁，暂不开放邀请与分享 | 同左 | 隐藏邀请与分享赚入口 |
| 30414 | 暂不支持自助更换手机号，请联系客服 | 同左 | — |
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
| 50302 | AI 暂不可用，可以先用搜索找货 | 同左 | 跳搜索 |
| 50303 | 暂时无法确认价格，请稍后再试 | 同左 | 不外跳返利链接；主按钮「稍后再试」，次按钮「仍去购买（无返利）」（BR-PRICE-13、BR-PRICE-08） |
| 50401 | 出了点问题，请稍后再试（{trace6}） | 出了点问题，请稍后再试 | 重试 |
| 其他 5xxxx | 出了点问题，请稍后再试（{trace6}） | 出了点问题，请稍后再试 | 重试 |
| 表外码（字典与包内默认都没有该键） | 服务端 msg；msg 为空时「操作未完成，请稍后再试」 | 同左 | — |

**表 B · data.reason 子键**（键 error.&lt;code>.&lt;reason>；reason 未收录时用表 A 的 error.&lt;code>；reason 枚举以来源条目为准，新增 reason 必须同时在本表加行）

| 码.reason | 文案（字典默认） | 包内默认（变量缺失时） | 动作 / 变量来源 |
| --- | --- | --- | --- |
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
| 30303.daily_count | 今日提现次数已用完（每日 {daily_count} 次），请明天再试 | 今日提现次数已用完，请明天再试 | 同上（withdraw.daily_count_per_user） |
| 30303.monthly_count | 本月提现次数已用完（每月 {monthly_count} 次） | 本月提现次数已用完 | 同上（withdraw.monthly_count_per_user） |
| 30303.payee_daily_users | 该收款账号今日暂不能再收款，请明天再试 | 同左 | 不透露其他会员信息 |
| 30303.self_purchase_required | 需有近期已确认收货的自购订单才能提现 | 同左 | BR-WDR-04（天数与门槛不写入文案，BR-TEXT-13） |
| 30303.payout_account_change_limit | 本月收款账号变更次数已用完，下月可再变更 | 同左 | BR-WDR-02 |
| 50301.maintenance | {platform_name}维护中，请稍后再试 | 该平台维护中，请稍后再试 | 购买按钮置灰「稍后再试」；Toast 显示文案 |
| 50301.not_launched | {platform_name}返利即将开放 | 该平台返利即将开放 | 卡片购买按钮置灰并显示该文案（即 platform_coming_soon），不弹 Toast |

**表 C · 降级场景文案**（非错误码）

| 场景 | 文案 | 动作 |
| --- | --- | --- |
| Agent 单平台搜索失败 | {platform_name}暂时查不到 | 其他平台结果照常展示 |
| Agent SSE 断线 | 连接中断 | 重试按钮 |
| 淘宝未安装（H5 未验证归因时） | 安装淘宝后下单才有返利，口令已复制 | 复制口令 |
| 京东/拼多多未安装或鸿蒙降级到网页 | 将通过浏览器打开{platform_name} | — |
| 鸿蒙淘宝降级 H5 | 鸿蒙版可能影响返利跟踪，如未显示订单可申请找回 | — |
| 某端全部路径丢归因 | 本设备暂不支持{platform_name}返利 | 隐藏购买按钮 |
| 待跟单卡（pending_track_card） | 订单同步中｜在{platform_name}下单后，订单通常会在一段时间内同步到这里，同步可能有延迟（CAP-\*-07 实测后改为「最长约 {n} 分钟」，n 取 order_sync.delay_hint_min.&lt;platform>） | 找回入口「未跟单？去找回」的出现条件按 BR-ATTR-17、BR-ATTR-21 |
| platform_coming_soon（= error.50301.not_launched，表 B） | {platform_name}返利即将开放 | 卡片按钮；只在 50301 data.reason=not_launched 时出现 |
| platform_no_rebate | {platform_name}暂不支持返利 | — |
| claim_required（用户键不可用平台，订单页与商品卡） | {platform_name}返利需下单后提交订单号认领 | 走找回 |
| no_rebate_hint | 当前不计返利 | — |
| pdd.parse_failed（拼多多链接识别不到商品，CAP-PDD-01） | 暂时无法识别这个拼多多链接 | 按 CAP-PDD-01 用文案标题检索并列出候选卡 |
| rebate_amount_unknown（rebate_basis=amount_unknown，取值与判定见 04 §8.3、BR-PRICE-08） | 可返利，金额以订单为准 | 替代 RebateTag；不显示「预估返」「预估返后」任何金额 |
| spec_min_price_note（商品级价格对应规格无法确定，BR-PROD-04） | 规格以下单页为准 | 价格旁显示；确知为最低规格价或联盟返回区间时价格写「¥x 起」（BR-PROD-04） |
| 剪贴板识别提示条 clipboard.prompt | 检测到商品链接，查返利？ | 出现条件、读取时机与方式只按 BR-ID-16 |

例：京东转链开关关闭（原因 maintenance）→ 接口返回 50301、data.reason=maintenance → Toast「京东维护中，请稍后再试」，卡片按钮变灰显示「稍后再试」。拼多多因备案互斥或权限未批保持关闭（原因 not_launched）→ 50301、data.reason=not_launched → 不弹 Toast，卡片按钮置灰显示「拼多多返利即将开放」。trace_id 以 …c3d4e5 结尾 → 显示「（c3d4e5）」；trace_id=abc → 显示「（abc）」。30152 且 data.available_at=2026-11-05T00:00+08:00（now 为 2026 年）→「暂不能换绑，11-05 00:00 后可再次换绑」。30303 reason=below_min、rules 返回最低 100 分 →「单笔最低提现 ¥1」；rules 未返回该值 →「提现金额低于单笔最低金额」。

- 50301 的 data.reason（新增，默认处理，待负责人确认）：maintenance = 维护或熔断（运营临时关闭、转链熔断）；not_launched = 该平台权限未批、验证未通过或备案互斥等尚未放量的关闭。服务端按配置 convert.off_reason.&lt;platform> ∈ {maintenance, not_launched}（新增，默认 maintenance）填写，熔断触发的关闭一律 maintenance；50301 仍只用于 convert.enabled.&lt;platform> 关闭（BR-PRICE-13）。需同步：13 §13.11 与 规划/04 §7 的 50301 行加 data.reason，04 §10.2 加 convert.off_reason.&lt;platform>，10 AC-S1-28-PDD 断言 reason=not_launched 与「即将开放」文案（AC-S1-15 保持 maintenance）。
- 文案来源一律为字典 error.&lt;code> / error.&lt;code>.&lt;reason>（BR-TEXT-12）；13 §13.11「客户端动作」列中「显示服务端 msg」的码，文案同样取本表 error.&lt;code>，需同步把该列改为「取 error.&lt;code>」。服务端返回的 msg 由同一份 contracts/texts.default.json 生成，与包内默认一致，只在客户端没有该键时显示。
- 规则正文中已写的提示句（BR-ID-17 的 30104、30153，BR-PRICE-13 的 50303 按钮，BR-PROD-05 的 30143 等）以本表为文案唯一维护处，措辞不一致时以本表为准，来源条目只保留判定与动作。

- risk_msg 字典后台可编辑，保存过 BR-TEXT-13 校验，不得写风控规则细节。
- 错误码编号以 08 §13.11 为准（04 §7 与之逐行一致）；后端功能规划 30201–30209 的映射见 BR-WDR-03 细则（非逐号对应，如 30206→30307、30207→30303）。
- 30142 原行「这个券已领完｜展示当前价」已删除：码值废弃后不回收、不复用；客户端收到 30142（旧版本服务端）按表 A「表外码」行处理（显示服务端 msg）。
- 44001 在本表只指风控拦截；更换手机号开关关闭改用 30414（BR-ID-06），不走 risk_msg。
- 外跳与未安装降级（G-04）：路径（平台 × 端 × 已装/未装的首选与降级）以 BR-ATTR-27 为准，本表只维护按钮与提示文案；每条路径在对应 CAP-\*-11 验证通过前是条件项，不得对外承诺；只有点击时才外跳（BR-ATTR-21）。「淘宝未安装」原文案「口令已复制，打开淘宝即可领券」已取代（09 A-27：未安装时该提示无法继续）；CAP-TB-11 证实 H5 下单保留归因时改为系统浏览器打开 H5，不出该提示。默认处理，待负责人确认。
- 待跟单卡（G-05）：显示与消失条件只按 BR-ATTR-21，找回入口出现条件只按 BR-ATTR-17，本表不复述时长；CAP-\*-07 实测前同步延迟不写具体分钟数。默认处理，待运营（BR-ATTR-21 决策人）确认。
- 平台能力降级文案（G-06，代理已定）：platform_coming_soon、platform_no_rebate、claim_required、no_rebate_hint 沿用 规划/09 CAP-TB-05、CAP-TB-07、CAP-JD-05、CAP-MT-05「不支持时怎么办」列原措辞；pdd.parse_failed、rebate_amount_unknown、spec_min_price_note 取自 CAP-PDD-01 降级列，其中「多规格商品显示最低规格价，以拼多多下单页所选规格为准」统一为 BR-PROD-04 写法「规格以下单页为准」+「¥x 起」。只换维护位置；09 该列只描述行为，以键名引用本表（需同步：09 CAP-PDD-01 降级列改引用这三个键）。platform_coming_soon 只由 50301 data.reason=not_launched 触发（见上）。
- rebate_amount_unknown（默认处理，待负责人确认）：卡片状态「可返利但金额未知」对应 rebate_basis=amount_unknown（rebate_min_fen、rebate_max_fen 为 null）；本表只维护文案。需同步：04 §8.3 rebate_basis 取值加 amount_unknown，BR-PRICE-08 补判定条件（如 CAP-PDD-01 拿不到 goods_sign、经 zs.unit.url.gen 转链成功），BR-PRICE-21 三态补该取值的归属。同步前服务端不得返回该取值，拼多多此类链接按 BR-PRICE-08 无返利态处理。
- 剪贴板提示条（G-20）：读取时机与方式（iOS detectPatterns + UIPasteControl、Android 开关、鸿蒙 PasteButton、上传条件）只按 BR-ID-16；本表只维护 clipboard.prompt 文案。

按 C-03 默认处理，待负责人确认。

#### BR-TEXT-15 细则 · 淘礼金卡片如实话术

**范围（D7）**：首版保留判定 3′（素材 unknown）、4 中的 unknown 无返利分支及 6（未接入 / 关闭）；判定 1、2、3、5 留待后续接入且对应能力验证后启用。未接入、查询失败或口令失效均不能单独证明“已领完”。

- 状态：待验证
- 默认值：能力未验证前所有素材淘礼金按 unknown 展示（无标签、「去购买」、「可能领不到」）；A/B/C 区分文案在后续纳入接入范围且 规划/09 淘宝项有接口样例后启用；复制原口令开关默认关。
- 决策人：负责人
- 依赖平台能力：素材淘礼金 A/B/C 判定依赖淘宝口令解析能否返回淘礼金创建方；B 类（brand_open）经我方推广位下单能否同时领到淘礼金并归因给我方；我方池淘礼金依赖淘礼金创建权限与剩余份数查询接口（均为 规划/09 淘宝项，待实测）
- 取代：无
- 来源：规划/01 §1、§5 J2；规划/04 §2.5 tlj_kind、§8.3；PRD v2.1 §10.6、§10.6.1、§10.11；PRD修订_双品牌与Agent找货 3.6、3.6.1
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

| 判定 | 标签 | 按钮 | 说明文案 |
| --- | --- | --- | --- |
| 1 我方池淘礼金 | 淘礼金 | 领 {amount}淘礼金 | 剩余 {remain} 份（查询失败不显示） |
| 2 素材 A（ours）/ B（brand_open），验证通过后启用 | 淘礼金 | 领淘礼金并购买 | — |
| 3 素材 C（third_party），验证通过后启用 | 无 | 去购买 | 这条素材里的淘礼金是第三方发的，通过本 App 购买领不到它；本 App 预估返 {rebate} |
| 3′ unknown（验证前所有素材） | 无 | 去购买 | 这条素材里的淘礼金通过本 App 购买可能领不到；本 App 预估返 {rebate} |
| 4 C / unknown 且无返利 | 无 | 去购买 | 同上前半句；该商品暂无返利 |
| 5 可靠接口已确认领完（remain=0；后续接入） | 无 | — | 这个淘礼金已领完，以下是同款有券商品 |
| 6 池内无结果或 tlj.enabled=off | 无 | — | 只出 notice agent.notice.tlj_none「暂无淘礼金活动」，不出替代商品卡（BR-AI-17，C-24 默认） |

- 判定 6（C-24）：按 BR-AI-17（已确认），本条只维护 agent.notice.tlj_none 的文案；默认处理，待负责人确认。若负责人改为「继续出有券商品」，只改本条判定 6 与 Agent 编排。
- 「复制原口令（领淘礼金、无返利）」按钮由后台开关 tlj.copy_original_tpwd.enabled 控制，默认关（修订① D8，默认假设，负责人确认；与 规划/00 D8 分销决策编号冲突，登记时改名）。

例：验证前，用户粘贴含 5 元淘礼金的素材，商品预估返 180 分 → 卡片无淘礼金标签，说明「这条素材里的淘礼金通过本 App 购买可能领不到；本 App 预估返 ¥1.8」，按钮「去购买」。我方池淘礼金面额 550 分、剩余查询超时 → 按钮「领 5.5 元淘礼金」，不显示剩余份数。

#### BR-TEXT-16 细则 · AI 生成内容标识

- 状态：默认假设
- 默认值：标识两处统一为「内容由 AI 生成，仅供参考」，由同一配置下发；text.delta 出站过滤按 BR-AI-06；登记前 model_label「内测模型」、filing_text 为空、入口白名单。理由：规划/03 §10.2 与 04 §8.2 措辞不同；D16 与 F-PRIV-07 要求登记前不对公众开放并公示登记编号。
- 决策人：法务
- 依赖平台能力：无
- 取代：
  - 规划/04 §8.2：「meta.ai_label「内容由 AI 生成」」
  - 规划/03 §10.2：「AiLabel「内容由 AI 生成，仅供参考」（两处并存）」
  - 规划/01 F-PRIV-07：「每条回复「内容由 AI 生成」（措辞改取 texts.ai_label）」
  - 08 BR-ID-15 原文：「显式展示「内容由 AI 生成」…登记编号（取配置 agent.filing_no）」（文案与配置键统一到本条；BR-ID-15 只保留合规义务）
- 来源：规划/03 §10.2、§7.5；规划/04 §8.2；规划/00 D16；规划/01 F-PRIV-07；PRD v2.1 §10.13
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 例：meta = {ai_label: 「内容由 AI 生成，仅供参考」}；用户搜「伊利纯牛奶 250ml」→ tool.status display_text 为「正在搜索淘宝」，不是「正在搜索伊利纯牛奶 250ml」。
- 出站过滤（G-15，代理已定）：只按 BR-AI-06（已确认）——金额类命中替换为「见卡片」（相邻合并）；URL、scheme、口令、短链删除命中的连续非空白串；trace 记 output_filtered=true 与命中类型。本条不另定过滤规则与埋点，只维护 AI 标识与公示文案。
- model_label：登记前显示「内测模型」，登记后取登记名称，不写供应商品牌宣传语。
- AgentConsent 单独同意（F-PRIV-07）未完成时不展示对话。
- PlatformBadge 仅作来源说明（文字 + 小图标），不作品牌宣传。
- 标识的法定要求（显式标识位置与措辞）以法务意见为准。

#### BR-TEXT-17 细则 · 广告推广标识

- 状态：待决策
- 默认值：法务定性前：首页运营位与分享海报显示「推广」，搜索自然结果与 Agent 相关性卡片不显示；客户端实现「非 null 即展示」。理由：《互联网广告管理办法》要求付费推广内容可识别，定性前应保守；字段已在 规划/04 §8.3 预留，开关在服务端。
- 决策人：法务
- 依赖平台能力：无
- 取代：无
- 来源：规划/04 §8.3；规划/00 D3；PRD v2.1 §10.13、§15
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 待定内容：标识措辞（「广告」/「推广」）、范围（首页运营位、搜索结果、Agent 卡片、分享海报）、是否按付费置顶与自然结果区分。
- ad_label 下发规则只在本条维护；Agent 卡片的佣金披露文案与“付费位不得参与 Agent 排序”见 BR-AI-10。
- 法务结论是 W8 公开上架（规划/00 D3）前的阻塞项，需在 W5 白名单内测前给出。
- 例：默认阶段，服务端对 scene=home_card 的卡片返回 ad_label=「推广」，搜索结果返回 null；法务若定为首页运营位用「广告」→ 只改服务端配置，不发版。

#### BR-TEXT-18 细则 · 客服话术一致性

- 状态：默认假设
- 默认值：话术库引用字典 key、后台双列显示编码与用户文案、字典变更同发布更新话术、不向邀请人透露下级订单。理由：PRD v2.1 §10.6.1 只要求 OTHER_TLJ「客服话术同步更新」，未形成通用机制。
- 决策人：运营
- 依赖平台能力：无
- 取代：无
- 来源：PRD v2.1 §10.6.1 第五步；规划/01 §5 J7 第 5 条、F-AGENT-06、F-AGENT-07；规划/06 Q-F4；README §1.2
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 话术库条目结构：{场景, 引用 dict key 列表, 标准回复模板, 可执行动作（找回 / 重新授权 / 申诉 / 转财务）}。
- 例：用户问「我的返利怎么还没到」，订单 (RECEIVED, WAITING)、display_status=WAITING、expected_credit_date=2026-10-17 → 标准回复「这笔订单已收货，预估返 ¥4.5，预计 10-17 入账，入账后可在钱包提现」。订单 display_status=INVALID、reason=OTHER_TLJ → 「下单时使用了其他推广者的淘礼金，订单归对方，这笔没有返利」。
- 例：邀请人问「我邀请的好友买了什么」→ 「为保护好友隐私，只能看到推广收益金额，看不到好友的订单」。
- BLACKLIST 与 hold：客服后台可见内部原因，但对用户只说字典文案并引导申诉。
- 验收：抽取话术库全部条目跑禁用词扫描与 dict key 存在性校验。
- 话术库按 display_status（BR-FUND-17）建场景，不按单一 order_status；按 C-01 默认处理，待负责人确认。

#### BR-TEXT-19 细则 · 余额流水用户文案

- 状态：默认假设
- 默认值：税费从冻结扣除，不单独成行，只作 WITHDRAW_PAID 汇总条目明细（BR-FUND-15，C-26 默认，待财务确认）；直推分佣流水不可跳转且不展示下级信息；无关联单据的调账显示说明。理由：与后端功能规划分录（税费借记冻结子账户）一致；J7 规定上级看不到下级订单。税务口径待 D12 税务师意见。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 分录表：「TAX_WITHHELD 借 U_\*_FROZEN（映射为 规划/ 的 TAX_WITHHOLD，口径一致）」
- 来源：规划/04 §2.4 流水类型、§3.2 withdrawals；规划/01 §5 J7 第 5 条、F-WDR-01；规划/00 D12；docs/changes/20261001-间推二级奖励.md（INDIRECT 名称）；PRD修订_后端功能规划 资金分录
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

| ledger_type | 名称 | 符号（可用余额视角） | 跳转 |
| --- | --- | --- | --- |
| REBATE_CREDIT | 自购返利入账 | + | 子订单 |
| SHARE_CREDIT | 分享收益入账 | + | share 子订单 |
| REFERRAL_CREDIT | 邀请分佣入账（显示「邀请好友订单」）；sub_type=INDIRECT 显示「邀请奖励」（默认，文案待定，key ledger_type.REFERRAL_CREDIT.name_indirect） | + | 不跳转 |
| CLAWBACK | 订单扣回（sub_type=PART_REFUND 时显示「部分退款扣回」） | - | 子订单；referrer 角色不跳转 |
| SETTLE_ADJUST | 结算补差（只表示联盟结算额差异，sub_type SETTLE_DIFF / PRICE_COMPARE / PRICE_PROTECT；入账后部分退款不用此类型） | ± | 子订单；referrer 角色不跳转 |
| WITHDRAW_FREEZE | 提现冻结 | - | 提现单 |
| WITHDRAW_FEE | 提现手续费 | 不单独成行（WITHDRAW_PAID 汇总条目明细） | 提现单 |
| TAX_WITHHOLD | 代扣个税 | 不单独成行（WITHDRAW_PAID 汇总条目明细） | 提现单 |
| WITHDRAW_PAID | 提现到账 | 0（列表显示「{net} 已转入{payout_channel_name}」，展开明细含申请额、代扣个税、手续费） | 提现单 |
| WITHDRAW_RETURN | 提现退回 | + | 提现单 |
| ADMIN_ADJUST | 人工调账 | ± | 有关联单据时跳转，否则显示 hint |
| BAD_DEBT_WRITEOFF | 负余额核销 | + | 显示 hint |

例 1：提现 1000 分、无税费成功 → 「提现冻结 -¥10」「提现到账 ¥10 已转入支付宝」。
例 2：提现 1000 分、代扣 80 分成功 → 「提现冻结 -¥10」「提现到账 ¥9.2 已转入支付宝」（明细：申请 ¥10，代扣个税 ¥0.8，手续费 ¥0）。
例 3：驳回 → 「提现冻结 -¥10」「提现退回 +¥10」。
例 4：下级订单入账给上级 150 分 → 「邀请分佣入账｜邀请好友订单｜+¥1.5｜10-17」，不可点击。
例 4b（间推开关开启）：间推份额 61 分 → 「邀请奖励｜邀请好友订单｜+¥0.61｜10-17」，不可点击，不显示层级或「二级」「间推」字样。「邀请奖励」与 P1 REWARD sub_type=invite（BR-INV-22）同名，定稿文案时须区分，改名只改字典。
例 5：自购订单入账 800 分后退 1 件（共 2 件）→ 流水「部分退款扣回｜-¥4」，点击跳转该子订单（BR-FUND-08）。

入账后部分退款写 CLAWBACK（sub_type=PART_REFUND），不写负向 SETTLE_ADJUST；按 C-16 默认处理，待财务确认。名称「部分退款扣回」的字典 key 为 ledger_type.CLAWBACK.name_part_refund。

列表范围按 BR-FUND-15：用户余额流水只展示 available 子户分录，外加每张打款成功提现单 1 条 WITHDRAW_PAID 汇总条目（名称「提现到账」，含实际到账、代扣个税、手续费明细，不改可提现余额、不带 balance_after）；WITHDRAW_FEE、TAX_WITHHOLD 不单独成行，名称键保留供汇总条目明细使用；本条只维护名称与明细文案。按 C-26 默认处理，待财务确认。

#### BR-TEXT-20 细则 · 推送短信分享渠道约束

- 状态：待验证
- 默认值：首部平台名与「官方」规则按本条执行（保存时 + 渲染后）；短信字数上限暂按 68 字设计模板，实测后更新。
- 决策人：运营
- 依赖平台能力：阿里云短信签名与模板审核规则（签名字数、单条计费长度、驳回词）；各手机厂商交易类消息分类申请条件（规划/09 待实测）
- 取代：无
- 来源：规划/01 F-PRIV-08、F-SHARE-02、F-SHARE-03；PRD修订_后端功能规划 2.14；参考_花卷云功能查漏底稿 §9
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：分享模板「【淘宝】#标题# 券后 #券后价#」→ 保存拒绝；改为「#标题# 券后 #券后价#，复制 #口令# 打开淘宝」通过。
- 例：商品标题「【天猫】伊利官方旗舰店纯牛奶」→ 渲染用「伊利旗舰店纯牛奶」。
- 短信（待验证）：签名 ≤8 字、签名 + 模板 ≤68 字按 1 条计费，「红包」「下载」等词易被驳回——来源为花卷云查漏底稿，需在阿里云短信控制台实际报备验证。
- 交易类推送挂厂商消息分类（小米通知类别、OPPO「个人账号与资产变化」、华为「帐号动态」）——同为待验证。
- WD_FAILED 短信示例：「【{签名}】你的提现打款未成功，¥10 已退回余额，请在 App 内查看原因。」须实测字数与审核结果。

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

### 12.3 本主题未决问题

1. BR-TEXT-01 方案 A/B（订单侧用「入账」还是继续用「到账」）需负责人拍板；默认方案 A，代码按字典实现，切换不改代码。
2. 每日入账任务运行时刻：已按 C-17 默认处理为 00:01 快照 → 00:05 入账，只在 BR-FUND-04、BR-FUND-18 维护，待财务确认；BR-TEXT-04 不含时刻与算法，时刻变更不改本主题。
3. wait_days 是否三平台都为 15 天；京东、拼多多是否返回确认收货时间、可入账事件与观察期需在 规划/09 核实（BR-TEXT-04）。
4. EXPIRED_CLICK 能否判定、click_valid_days 每平台取值、后点击是否覆盖归因（BR-ATTR、规划/09）；决定 JumpTip 两句承诺何时启用。
5. 支付宝转账业务失败码清单与「明确失败」白名单（BR-TEXT-08）需沙箱实测；白名单确定前所有失败码按未知处理。
6. 代扣个税、手续费的展示与分录（BR-TEXT-06、BR-TEXT-19）随 规划/00 D12 税务师意见确认。
7. 「最低价」降价白名单模板是否合规需法务确认（BR-TEXT-13）；确认前价格历史用不含「最低」的中性表述。
8. ad_label 措辞与范围（BR-TEXT-17）需法务在 W5 内测前定性；AI 标识措辞与位置（BR-TEXT-16）待法务确认。
9. 淘礼金 A/B/C 判定、B 类能否同时返利、我方池淘礼金剩余份数接口（BR-TEXT-15）待 规划/09 淘宝项实测。
10. share 单是否存在跨商品归因（好友经分享进店后买其他商品）待 规划/09 实测（BR-TEXT-02）。
11. 2026–2027 年法定节假日与调休日历的录入责任人与时间（BR-WDR-26 workday_calendar）。
12. 修订① 的 D8（C 类素材是否给「复制原口令」）与 规划/00 的 D8（分销计酬）编号冲突，需在文档登记表中重新编号。
13. PUNISH 子原因对用户透出粒度需负责人与运营确认（BR-TEXT-05 默认用不含联盟术语的概括文案）。
14. 找回驳回原因字典 claim_reject_reason 的编码表由 BR-ATTR 给出（BR-TEXT-09 CLAIM_RESULT 引用）。
15. 订单状态按 C-01 改用 BR-FUND-01 双状态与 BR-FUND-17 派生的 display_status（BR-TEXT-01/02/03/04/05/09/18），待负责人确认；不采纳时按本主题开头的映射回退。
16. 已关闭：BR-FUND-17 已删去术语表，派生表文案列改为「示意」并声明以 BR-TEXT-02 为准，只保留派生条件与「状态和金额只取接口」；现派生表示意文案已用「入账核对中」「售后处理中，入账暂停」「已收货，等待联盟结算后入账」。原记录：BR-FUND-17 文案列与本主题不一致、未列入 §14.3：REVIEWING「返利审核中」对本主题「入账核对中」（本主题不透露 hold）；RIGHTS_PENDING「返利暂缓到账」、CREDITING「到账处理中」、WAITING_SETTLE「等待联盟结算后到账」对方案 A 的「入账」；BR-FUND-04 推送「¥x 已到账」对 BR-TEXT-09「已入账」。建议随 C-02 一并裁决，文案以本主题为准（BR-FUND-17 只保留派生条件）。
17. 已关闭（C-25 默认，待负责人确认）：ORDER_TRACKED 的对象、触发、合并与去重只在 BR-TEXT-09 维护；自购受益人与 share 单分享者各推自己的份额，直推上级不推（J7）；去重键改用 {order_key}:{uid}:{role}:TRACKED（BR-FUND-05）；BR-FUND-03 删去推送段、改为引用 BR-TEXT-09。
18. 已关闭（C-19）：withdrawn_fen 由 BR-FUND-18 提供，钱包首页展示已提现（BR-TEXT-01）。
19. BR-TEXT-21 中 UNION_SETTLED、UNION_RECEIVED 的刷新周期取决于各联盟结算明细可取得频率（规划/09 待实测）。
20. BR-TEXT-14 新增 50301 data.reason（maintenance / not_launched）与配置 convert.off_reason.&lt;platform>，需同步 13 §13.11、规划/04 §7 与 §10.2、10 AC-S1-28-PDD；新增 rebate_basis=amount_unknown 需同步 04 §8.3、BR-PRICE-08、BR-PRICE-21；13 §13.11「显示服务端 msg」改为「取 error.&lt;code>」。均为默认处理，待负责人确认。

---
