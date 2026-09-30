# 08 业务规则 · 7. 提现与打款（BR-WDR）

返回 [README](README.md)（使用规则、术语表、规则索引）

## 7. 提现与打款（BR-WDR）

本节规定：提现入口与鉴权、校验顺序、限额、冻结、状态机与分录、审核打款、审核风险标签、支付宝结果判定、对账与文案。共 29 条（已确认 2、默认假设 21、待决策 4、待验证 2）。

### 7.1 规则一览

| 编号 | 规则 | 状态 | 影响面 |
| --- | --- | --- | --- |
| BR-WDR-01 | **提现入口与鉴权**<br>提现申请 `POST /v1/withdrawals` 与收款账号变更 `PUT /v1/me/payout-account` 只能由原生 App（iOS/Android/鸿蒙）发起，并且必须同时满足以下条件：access_token 有效；请求签名通过（`X-Timestamp` 与服务器时间差 ≤300 秒，`X-Nonce` 10 分钟内未用过，`X-Sign` 校验通过）；带 `Idempotency-Key`；带有效的 `step_up_token`。step_up_token 由短信二次验证签发，5 分钟有效，绑定 user_id + device_id + action。action ∈ {withdraw, payout_account_change}，必须与所调接口一致。token 只能用一次：请求成功（提现单已创建或收款账号已变更）时，在同一事务内把它的 jti 记为已用。`h5_token`（aud=h5）、JSBridge、Agent 工具一律不得调用这两个接口，也不得调用任何写钱包的接口。 | 默认假设 | POST /v1/withdrawals；PUT /v1/me/payout-account；step_up_token 签发与 jti 消费记录；h5_token 作用域；bridge.schema.json；Agent 工具注册表 CI 检查；Withdraw 页；AC-WDR-01 |
| BR-WDR-02 | **收款账号绑定与变更**<br>收款通道只支持支付宝。MVP 只提供绑定和换绑，不提供解绑。绑定或换绑时有以下要求。⓪ 新账号的 alipay_hmac 命中黑名单（BR-ID-31）→ 44001。① `payee_name` 与实名姓名都先规范化，再逐字比较，必须相等，否则返回 30307。规范化步骤：NFKC；去掉首尾空白（含 U+3000、U+00A0）；把 ‘•’‘.’‘．’‘・’ 统一为 ‘·’（U+00B7）。数据库存规范化后的值。② 支付宝登录号加密存储，并计算 HMAC。当前有效绑定上 `(app_id, alipay_hmac)` 唯一（部分唯一索引，WHERE is_current=true）；该账号已被其他会员当前绑定时返回 30308。③ 每次换绑必须带有效 step_up_token（action=payout_account_change）。④ 换绑成功且新 alipay_hmac ≠ 当前绑定时，才计 1 次变更。每个自然月（+08:00）的变更次数 ≤ `withdraw.payout_account_change_per_month`（默认 2）。首次绑定、失败的请求、提交同一个账号都不计次。超出上限返回 30303，且 `data.reason=payout_account_change_limit`。⑤ 提现单创建时快照收款人（规范化姓名、登录号密文、HMAC）；之后换绑不影响已创建的提现单。 | 默认假设 | payout_accounts（alipay_logon_id_cipher、alipay_hmac、payee_name、is_current；部分唯一索引）；payout_account_changes（新表）；withdrawals 收款人快照字段；realname.name 规范化存储；PUT /v1/me/payout-account；配置 withdraw.payout_account_change_per_month；risk_flags：payee_prev_other_user；blocklist 命中校验（44001，BR-ID-31）；绑定收款账号页；AC-WDR-02 |
| BR-WDR-03 | **申请校验顺序与错误码**<br>`POST /v1/withdrawals` 的判断顺序固定，命中第一条即返回：<br>前置（全局中间件）：access_token 与作用域；签名与防重放（10401）；参数格式（amount_fen 为正整数、account_type ∈ {SELF, PROMO}，否则返回 20001，并在 data.fields 列出出错字段）；缺少 Idempotency-Key（20001）。<br>⓪ 幂等查找（BR-WDR-07）：同 key、同请求体、已完成 → 原样返回首次响应；同 key、不同请求体 → 20901；同 key 仍在处理中 → 40901。<br>① `withdraw.enabled=off` 或 `withdraw.account_enabled.<account_type>=off` → 30306（30306 只表示提现开关关闭）。<br>② step-up（BR-WDR-01）→ 10003。<br>③ risk_state=banned，或 appealing 且 prev_risk_state=banned → 10006。<br>③a 命中黑名单（BR-ID-31：手机号 HMAC、身份证 HMAC、收款支付宝 HMAC、设备哈希任一命中）→ 44001。<br>④ 未实名 → 30304。<br>⑤ 未绑收款账号 → 30305。<br>⑥ 收款人姓名 ≠ 实名姓名（规范化后比较）→ 30307。<br>⑦ 会员处于提现冻结（risk_state=frozen 或 appealing 且 prev_risk_state=frozen，或有生效的 withdraw_holds，含账务差异冻结 reason=ledger_mismatch，见 BR-WDR-05）→ 30303 reason=account_frozen。<br>⑧ 任一账户 available_fen &lt;0 → 30302。<br>⑨ 金额不合规 → 30303，本步内按 below_min → not_multiple → above_max → net_too_small 取第一个命中的原因。<br>⑩ 申请账户 available_fen &lt; amount_fen → 30301。<br>⑪ 次数超限 → 30303，本步内按 daily_count → monthly_count → payee_daily_users 取第一个命中的原因。<br>⑫ 未成年（BR-WDR-06）→ 30309，先判 PROMO 禁提，再判月额度。<br>⑬ 近 90 天自购门槛（开启时）→ 30303 reason=self_purchase_required。<br>⑭ 风控命中 → 不拒绝，按 BR-WDR-29 打 risk_flags，进入人工审核。<br>`GET /v1/withdrawals/rules` 复用同一个校验器，只要求 access_token 有效，跳过以下各项：前置中的签名与幂等，⓪、②，以及 ⑨⑩⑫ 中与本次金额有关的比较。其余步骤按原顺序判断，逐账户返回：can_withdraw、首个阻断的 block_code 与 block_reason、max_withdrawable_fen、剩余次数、各项限制值。 | 默认假设 | POST /v1/withdrawals；GET /v1/withdrawals/rules 响应结构；全局鉴权与参数校验中间件；错误码表 规划/04 §7；/v1/dict 的 withdraw_reason 枚举；Withdraw 页错误提示；客服话术：提现失败原因；AC-WDR-03 |
| BR-WDR-04 | **金额与次数限制默认值**<br>提现金额与次数限制全部可配，默认值如下：单笔 amount_fen ≥ `withdraw.min_amount_fen`（默认 100 分，即 ¥1）；amount_fen % `withdraw.amount_step_fen` = 0（默认 100 分，即整元）；amount_fen ≤ `withdraw.max_amount_fen`（默认 500000 分，即 ¥5,000）；每个会员每自然日 ≤ `withdraw.daily_count_per_user`（默认 1）、每自然月 ≤ `withdraw.monthly_count_per_user`（默认 10），均按 SELF+PROMO 两账户合计；同一收款支付宝（按快照 alipay_hmac）每自然日被不同会员使用 ≤ `withdraw.payee_daily_distinct_users`（默认 1）。“0 表示不限”只适用于 daily_count_per_user、monthly_count_per_user、payee_daily_distinct_users。配置保存时校验：min_amount_fen ≥1；amount_step_fen ≥1；min_amount_fen ≤ max_amount_fen ≤ payout.single_cap_fen。计数口径：created_at 落在该自然日或自然月（00:00 +08:00 日切），且状态不属于 {REJECTED, FAILED} 的提现单；比较方式为“已有数 + 本次 ≤ 上限”。并发下计数一致由 BR-WDR-07 的锁保证。 | 默认假设 | 配置 withdraw.min_amount_fen / amount_step_fen / max_amount_fen / daily_count_per_user / monthly_count_per_user / payee_daily_distinct_users / self_purchase_90d.enabled / self_purchase_90d.min_fen 及保存时校验；withdrawals 索引 (user_id, created_at)、(payee_alipay_hmac, created_at)；GET /v1/withdrawals/rules；Withdraw 页金额输入与提示；后台 提现设置；AC-WDR-03 |
| BR-WDR-05 | **提现阻断：负余额与冻结**<br>“提现阻断”指以下任一情况：risk_state ∈ {frozen, banned, appealing}（appealing 按 appeals.prev_risk_state 取 frozen 或 banned 的效果，BR-ID-36）；存在生效的提现冻结记录（withdraw_holds）；SELF 或 PROMO 任一账户 available_fen &lt; 0。<br>申请时（BR-WDR-03）：banned 或 appealing(prev=banned) → 10006；frozen、appealing(prev=frozen) 或有生效冻结 → 30303 reason=account_frozen；任一账户为负 → 30302，data.account 指明为负的账户，作用范围按 BR-FUND-11（默认两个账户都不得申请）。<br>已存在的非终态单按阻断来源分两类处理：<br>(a) 负余额（本款是负余额处理非终态提现单的唯一维护处，BR-FUND-21 只保留编号指向本款）：W2、W4、W8 的守卫在锁定账户行的同一事务内检查“该单所属账户 available_fen ≥ 0”；扣回或负向调整使账户 available 由 ≥0 变为 &lt;0 的事务内写 outbox 事件 account.went_negative，提现模块消费后立即处理（事件只加快处理，守卫是硬约束）。为负账户下 PENDING_REVIEW、APPROVED 且没有任何 kind=transfer 尝试记录的单，由系统执行 W3（reject_reason_code=NEGATIVE_BALANCE，BR-WDR-10），写 WITHDRAW_RETURN，冻结额退回 available 抵扣负数。另一账户（未变负）的 PENDING_REVIEW、APPROVED 单不驳回，置 withdrawals.blocked_reason=NEGATIVE_BALANCE_OTHER：W2 拒绝、EXECUTE 跳过、W8 拒绝；两个账户 available_fen 都 ≥ 0 时自动清空。为负账户下已有转账尝试记录的 APPROVED 单（经 W9 退回）不自动驳回，置 blocked_reason=NEGATIVE_BALANCE 并告警，由财务按 BR-WDR-10 处理；该账户恢复 ≥0 后同样自动清空。PAYING 且尚未发出转账的单在 payout 复核（BR-WDR-13 ③）走 W9（hold_reason=member_blocked），回到 APPROVED 后立即按本款处理；已发出转账的 PAYING 单照常查询与完成。<br>(b) 风控冻结（risk_state ∈ {frozen, banned, appealing}）与 withdraw_holds：不自动改变单据状态。W2 审核通过与 W3 驳回不受影响。EXECUTE（BR-WDR-12）与 W8 手动成功（BR-WDR-16）遇到阻断时拒绝。payout 复核遇到阻断时走 W9，hold_reason=member_blocked。<br>提现冻结只记在 withdraw_holds 表（唯一冻结记录；不使用 users.withdraw_blocked_reason），字段：user_id、reason ∈ {manual, recon_diff, ledger_mismatch, manual_failed_watch}、source_ref、created_by、created_at、hold_until（可空）、released_at、released_by。一条记录在 released_at 为空、且 hold_until 为空或 > now 时生效。多个原因可以叠加，逐条解除。新增和解除都记审计，且与 BR-WDR-07 一样先锁 users 行。不设账户级冻结。R2 与日终校验只追加 withdraw_holds，不改 risk_state。 | 待决策 | account_balances；users.risk_state；withdraw_holds（新表，reason 含 ledger_mismatch）；withdrawals.blocked_reason；事件 account.went_negative 消费者；W2 / W4 / W8 守卫；reject_reason_code NEGATIVE_BALANCE；POST /v1/withdrawals；后台审核列表 blocked 标识；后台批次执行结果；payout 进程复核；后台 冻结/解冻操作；推送「提现未通过」；客服话术：余额为负为何不能提现；AC-WDR-03 |
| BR-WDR-06 | **未成年人提现限制**<br>本条是未成年人提现限额、计数口径与错误码的唯一维护处；年龄计算、满 18 周岁时刻 adult_at（由 realname.birth_date 推导，BR-ID-25）与识别时点只在 BR-ID-26 维护，本条调用同一推导函数。申请时刻 now &lt; adult_at 即为未成年；未满 14 周岁不能实名（BR-ID-26），因此在 ④ 即被拦截（30304）。已实名且未满 18 周岁时：<br>① 不得提 PROMO → 30309，`data.remaining_fen=0`。<br>② SELF：本自然月已申请额 + 本次 amount_fen 必须 ≤ `withdraw.minor_monthly_cap_fen`（默认 20000 分，即 ¥200），否则 30309，`data.remaining_fen` = max(0, 上限 − 本自然月已申请额)。本自然月已申请额 = 该用户 account_type=SELF、created_at 落在当前 +08:00 自然月内、status ∉ {REJECTED, FAILED}（即 PENDING_REVIEW、APPROVED、PAYING、PAID_API、PAID_MANUAL）的提现单 amount_fen 合计。<br>③ 该配置为 0 时，等同于未满 18 周岁一律禁提。<br>④ BR-WDR-03 ⑫ 先判 ①、再判 ②；② 的复核按 BR-WDR-07 在同一事务、同一组锁（users 行 → SELF → PROMO 余额行）内与建单、写 WITHDRAW_FREEZE 一起完成，不另加锁。<br>满 18 周岁时刻起本条限制自动失效，无需人工操作。 | 待决策 | 配置 withdraw.minor_monthly_cap_fen；realname.birth_date（加密，替代 birth_year；adult_at 由其推导）；POST /v1/withdrawals（30309）；GET /v1/withdrawals/rules；Withdraw 页未成年提示；用户协议未成年条款；AC-WDR-03 |
| BR-WDR-07 | **提现单创建、并发锁与幂等**<br>校验通过后，在同一个数据库事务内按固定顺序加锁并复核：① `SELECT … FROM users WHERE id=? FOR UPDATE`；② 按 SELF → PROMO 的顺序，对该会员的两个 account_balances 行 `FOR UPDATE`；③ `pg_advisory_xact_lock(hashtext(app_id\|\|':'\|\|alipay_hmac))`（快照中的收款账号）；④ 在锁内重新执行 BR-WDR-03 的 ⑦⑧⑩⑪⑫；⑤ 计算 fee_fen（BR-WDR-19）、tax_fen（BR-WDR-20），`net_fen = amount_fen − fee_fen − tax_fen`；⑥ 插入提现单（PENDING_REVIEW）；⑦ 写 `WITHDRAW_FREEZE` 凭证（BR-WDR-09）；⑧ 写幂等结果。凡是会修改一个会员余额行或其提现冻结的写操作（包括 BR-FUND 扣回、BR-WDR-05 冻结），都必须先锁 users 行，再按 SELF→PROMO 顺序加锁，避免死锁。<br>幂等沿用 规划/04 的 `idempotency_keys`，唯一键 (app_id, user_id, method, path, key)：<br>- 在签名校验之后、BR-WDR-03 ① 之前查找（⓪）。<br>- 请求体哈希 = sha256(键名排序、无空白的规范化 JSON)。<br>- 同 key、同哈希、已完成 → 原样返回首次响应（包括业务错误）；同 key、不同哈希 → 20901；同 key 的首个请求还没完成 → 40901。<br>- 成功和 3xxxx 业务错误写入幂等结果；1xxxx、2xxxx 不写。缺少 Idempotency-Key → 20001。<br>- `POST /v1/withdrawals` 与 `PUT /v1/me/payout-account` 的幂等记录不按 30 天清理，保留期 ≥ 提现单保留期。<br>`out_biz_no` 在插入提现单时生成，`(app_id, out_biz_no)` 唯一，之后任何代码和 SQL 都不得修改（数据库触发器拒绝对该列的 UPDATE）。 | 默认假设 | withdrawals（out_biz_no 唯一及禁止 UPDATE 的触发器、net_fen、fee_rule_id、tax_rule_version、income_type）；idempotency_keys 保留策略；users 行锁、account_balances 行锁顺序；BR-FUND 扣回的锁顺序；ledger_vouchers / ledger_entries；POST /v1/withdrawals；AC-WDR-04；SM-WDR-W1 |
| BR-WDR-08 | **提现状态机**<br>提现状态只有 7 个：PENDING_REVIEW、APPROVED、REJECTED、PAYING、PAID_API、PAID_MANUAL、FAILED。终态为 REJECTED、PAID_API、PAID_MANUAL、FAILED；进入终态后，状态与金额都不得再改。状态迁移只允许下表 W1–W10。每次迁移用 `UPDATE … WHERE id=? AND status=?` 做比较并交换（CAS）；影响 0 行即视为并发冲突，不写任何分录，后台接口返回 20902（状态已变化，请刷新后重试；`data.resource=withdrawal`）。needs_manual=true 的单只能经 W10 结束。 | 默认假设 | withdrawals.status 枚举、execute_seq、hold_reason、hold_at、blocked_reason；specs/state-machines/withdrawal.yaml；后台 withdrawals / payout-batches 接口；错误码 20902（data.resource=withdrawal）；SM-WDR-W1…W10；AC-WDR-05 |
| BR-WDR-09 | **各状态的资金分录**<br>本条是提现分录模板（记账时点、ledger_type、借贷科目）的唯一维护处；frozen 子户性质、不设在途科目、风控冻结不移动资金、不变量 frozen = Σ 非终态提现单见 BR-FUND-14。<br>用户申请提现后，冻结金额一直留在 `USER_*.frozen`，直到单据进入终态；EXECUTE（W4）时不写任何分录。分录只在以下时点写，并与状态迁移在同一事务内完成：<br>- W1（APPLY，进入 PENDING_REVIEW）：写 WITHDRAW_FREEZE（available −amount，frozen +amount）。<br>- W3（驳回，含系统驳回 NEGATIVE_BALANCE）、W6（通道明确失败）、W10 判 FAILED：写 WITHDRAW_RETURN（frozen −amount，available +amount）。<br>- W5（通道成功 → PAID_API）、W8（手动成功录入并经确认人确认 → PAID_MANUAL，BR-WDR-16）、W10 判 PAID_API：写一张凭证，含 WITHDRAW_PAID（借 USER_\*.frozen net_fen，贷 CASH_ALIPAY）、WITHDRAW_FEE（借 USER_\*.frozen fee_fen，贷 FEE_INCOME）、TAX_WITHHOLD（借 USER_\*.frozen tax_fen，贷 TAX_PAYABLE）。金额为 0 的分录不写，三者合计必须等于 amount_fen。<br>- W2、W4、W7、W9：不写分录。 | 默认假设 | ledger_entries / ledger_vouchers；account_balances.frozen_fen；ledger_invariants.sql；specs/ledger-rules.md；钱包页“冻结中”金额；SM-WDR-W1…W10；AC-WDR-05 |
| BR-WDR-10 | **审核与驳回**<br>MVP 的提现单全部人工审核。APPROVE（W2）与 REJECT（W3）只能由 super 或 finance 角色执行，执行前需持有 5 分钟内有效的后台 step-up token。APPROVE 写 reviewer_id、reviewed_at；会员处于风控冻结或有生效 withdraw_holds 时也可以审核通过，所属账户为负或 blocked_reason 非空时不得审核通过（BR-WDR-05）。REJECT 必须选择原因码 `reject_reason_code`（人工可选：RISK_SUSPECT、ORDER_ABNORMAL、PAYEE_INFO_INVALID、USER_REQUEST、OTHER；系统专用：NEGATIVE_BALANCE），可以填写内部备注；NEGATIVE_BALANCE 只由系统按 BR-WDR-05 (a) 写入（操作人记 system，不需 step-up，记审计），人工不可选；用户只看到原因码对应的文案，看不到内部备注。从 APPROVED 驳回时有两条额外限制：该单存在 result ∈ {pending, success, unknown} 的转账尝试时，拒绝驳回，只能走 BR-WDR-15；存在 result=fail 的转账尝试时，驳回需第二人确认后生效，第二人为 super 或 finance、≠ 驳回人、需 step-up。驳回在同一事务内写 WITHDRAW_RETURN，提交后经 outbox 发通知。MVP 用户不能自行撤销提现；需要撤销时联系客服，由财务以 USER_REQUEST 驳回。 | 默认假设 | withdrawals.reviewer_id、reviewed_at、reject_reason_code、reject_note、reject_confirmed_by、risk_flags；后台 withdrawals 审核接口与页面；通知模板：提现未通过；客服话术：如何撤销提现；AC-ADM-07；SM-WDR-W2、W3 |
| BR-WDR-11 | **职责分离与第二人审批**<br>同一张提现单：执行打款人 executor_id ≠ 审核人 reviewer_id。W8 手动成功：录入人 ≠ reviewer_id，确认人 ≠ 录入人（确认人可以是 reviewer）。W10 由一名 super 和一名 finance 两名不同管理员确认，凭证上传人必须是其中之一。一张 APPROVED 单同一时刻只能属于一个未完成的批次（批次内还有 APPROVED 单即为未完成）。批次中任一单 `amount_fen ≥ payout.second_approval_single_fen`（默认 50000 分，即 ¥500），或批次 `Σ amount_fen ≥ payout.second_approval_batch_fen`（默认 2000000 分，即 ¥20,000）时，执行前必须有第二人批准：批准人为 super 或 finance，≠ 执行人（可以是批次内某单的审核人），需 step-up。批准时锁定成员（withdrawal_id 集合），并保存批准时的 Σ amount_fen；成员有任何增删，批准即失效，需重新批准。批准在批次未完成期间一直有效，经 W9 退回的单可以用原批准重新执行。所有校验都在服务端执行，界面按 ability 隐藏按钮只是辅助；所有操作都写审计日志。 | 默认假设 | withdrawals.reviewer_id、executor_id、manual_entry_by、manual_confirm_by；payout_batches.approver_id、approved_at、approved_member_ids、approved_total_fen；配置 payout.second_approval_single_fen / second_approval_batch_fen；后台 payout-batches 审批与执行；audit_logs；上线检查清单；AC-ADM-07 |
| BR-WDR-12 | **批次执行**<br>批次只是一组 APPROVED 提现单的集合（一张单同一时刻只属于一个未完成批次，见 BR-WDR-11），不影响单据状态。EXECUTE 分三步：<br>① 批次级前置检查，任一不满足则整批拒绝：`payout.enabled=on`；`payout.queue_paused=false`；第二人审批有效（BR-WDR-11）。<br>② 逐单判断：状态仍为 APPROVED；executor ≠ reviewer；会员没有提现阻断（BR-WDR-05）；该单没有任何 kind=transfer 的 payout_attempts 记录。通过的单组成本次可执行集合。<br>③ 对可执行集合做水位检查（BR-WDR-18），不满足则整批拒绝，不迁移任何单。<br>检查通过后，每单以 CAS 迁到 PAYING，写 executor_id、batch_id、executed_at，execute_seq +1。事务提交后经 outbox 为每单投递一个 payout 任务，jobId = `{withdrawal_id}:{execute_seq}`。未通过的单保持 APPROVED，并在结果中列出原因。重复点击执行靠状态 CAS 去重：已经是 PAYING 或终态的单不再投递。 | 默认假设 | payout_batches；withdrawals.executor_id、batch_id、executed_at、execute_seq；payout 队列 jobId；outbox；后台 payout-batches 执行接口与页面；AC-WDR-06；SM-WDR-W4 |
| BR-WDR-13 | **payout 进程与打款前复核**<br>只有 payout 进程能读取支付宝应用私钥（KMS，仅 prod）。该进程没有公网入站；出站只允许访问支付宝网关、PG、Redis；固定 1 个实例，转账队列 concurrency=1。非 prod 环境只能走支付宝沙箱或 dry-run。`PAYOUT_MODE` 默认 dry_run，改为 live 只能由人经生产发布完成。<br>处理每个转账任务的步骤：<br>① 单据状态 ≠ PAYING，或任务的 execute_seq ≠ 单据当前的 execute_seq → 直接结束。<br>② 该单已存在任何 kind=transfer 的尝试记录 → 不转账，转入查询（BR-WDR-14）。<br>③ 在 `pg_advisory_xact_lock('payout_daily')` 内按顺序复核，任一不满足即走 W9 回到 APPROVED，并写 hold_reason：payout_disabled（payout.enabled=off）→ queue_paused → member_blocked（BR-WDR-05）→ single_cap（net_fen > payout.single_cap_fen）→ daily_cap（当日已发出合计 + 本单 net > payout.daily_cap_fen）。这里不复核水位，水位只在 EXECUTE 时检查（BR-WDR-18）。<br>④ 在同一把锁内写 payout_attempts（kind=transfer，result=pending）并提交，之后才发起转账（先记后发）。<br>⑤ 转账请求超时时间为 10 秒。<br>转账任务 attempts=1，队列不得自动重试转账。W9 时清空 executor_id、executed_at，保留 batch_id，写 hold_reason 和 hold_at。hold_reason 完整枚举：payout_disabled、queue_paused、member_blocked、single_cap、daily_cap、payer_side_after_transfer（BR-WDR-17）。 | 默认假设 | payout 进程与部署（ECS、安全组、RAM、KMS、队列 concurrency）；payout_attempts（result 枚举增加 pending）；配置 payout.single_cap_fen / daily_cap_fen、PAYOUT_MODE；withdrawals.hold_reason、hold_at、execute_seq；B2-06 验收用例；SM-WDR-W9 |
| BR-WDR-14 | **打款结果判定与只查不重提**<br>转账或查询的结果按 BR-WDR-28 的清单判定：成功 → W5（PAID_API，记 channel_order_id 与 paid_at）；明确失败 → W6（FAILED）；付款方侧失败 → W9 + 暂停队列（BR-WDR-17）。不在清单内的情况一律视为结果未知，包括：超时、网络错误、HTTP 5xx、SYSTEM_ERROR、未列入清单的码或状态、查询返回“订单不存在”或处理中。结果未知时单据保持 PAYING，以首次转账尝试时间 T 为基准，在 T+1 分、+5 分、+30 分、+2 小时各查询一次，之后每 2 小时查询一次。到 T+24 小时仍未知，则置 needs_manual=true、告警，并停止自动查询；此后只能经 BR-WDR-15（W10）结束。任何情况下，系统都不得自动再次调用转账接口，也不得换新的 out_biz_no 重打。 | 已确认 | payout 进程查询调度；配置 payout.query_schedule；withdrawals.fail_code、channel_order_id、paid_at、needs_manual；W10 处置页【立即查询】；通知模板：提现成功/失败；SM-WDR-W5…W7；AC-WDR-07 |
| BR-WDR-15 | **24 小时未知人工处置**<br>needs_manual=true 的 PAYING 单只能通过 W10 结束。处置人必须上传支付宝侧凭证，可以是查询接口返回的 JSON（处置页【立即查询】的结果），或含该 out_biz_no 的支付宝账务明细或账单行。然后由一名 super 和一名 finance 确认：两人不同，均需 step-up，上传人必须是二者之一。<br>- 凭证显示已成功 → PAID_API，按 BR-WDR-09 记成功分录。<br>- 只有同时满足以下三点才可判 FAILED：距 T 已 ≥24 小时；T 当日及次日的支付宝账单都已下载，且都没有该 out_biz_no；最近一次查询为“订单不存在”。判 FAILED 时写 WITHDRAW_RETURN，并在同一事务内为该会员新增 withdraw_holds（reason=manual_failed_watch，hold_until = 判定时刻 + `withdraw.manual_failed_hold_days` 天，默认 7 天）。<br>needs_manual 单不得转 PAID_MANUAL，也不得重发转账。 | 默认假设 | withdrawals.needs_manual、manual_resolution、resolver_ids、proof_file；withdraw_holds（manual_failed_watch）；配置 withdraw.manual_failed_hold_days；后台 needs_manual 处置页；文件存储（凭证）；audit_logs；SM-WDR-W10 |
| BR-WDR-16 | **手动成功（线下打款）**<br>PAID_MANUAL 只能从 APPROVED 进入（W8），守卫如下：该单不存在 result ∈ {pending, success, unknown} 的转账尝试记录；会员没有提现阻断（BR-WDR-05）；录入人为 super 或 finance，且 ≠ reviewer_id；确认人为 super 或 finance，且 ≠ 录入人（可以是 reviewer）；两人都需 step-up。录入时必填：支付宝流水号（`(app_id, channel_order_id)` 唯一，同一个流水号不得用于两张单）、实付时间、实付金额，实付金额必须 = net_fen。成功后按 BR-WDR-09 写成功分录、更新 tax_ytd、通知用户。手动成功与接口打款的互斥由状态 CAS 保证：EXECUTE 与 MANUAL_PAID 都要求 status=APPROVED，先提交的一方生效。 | 默认假设 | withdrawals.channel_order_id 唯一约束、manual_entry_by、manual_confirm_by；后台 手动成功录入/确认页；R2 对账匹配规则；SM-WDR-W8 |
| BR-WDR-17 | **开关、权限与付款方异常**<br>`withdraw.enabled=off` 或 `withdraw.account_enabled.<account_type>=off` 时，新申请返回 30306，已有单不受影响。<br>`payout.enabled=off` 时：EXECUTE 整批拒绝，APPROVED 单保持原状；已投递但还没发出转账的任务，在复核时走 W9（payout_disabled）；已发出转账的 PAYING 单继续查询，查询不会因开关而暂停。<br>转账返回 payer_side_codes 清单内的码时（BR-WDR-28，验证前清单为空）：该单走 W9 回到 APPROVED，hold_reason=payer_side_after_transfer，不退回用户余额；系统置 `payout.queue_paused=true` 并告警。这类单已有转账记录，在 BR-WDR-22 ④ 验证为“同一 out_biz_no 重提幂等”并经负责人批准之前，不得再次执行（BR-WDR-12），只能走 W8 手动成功，或 W3 驳回（需第二人确认，BR-WDR-10）。<br>权限：<br>- finance 可以直接切换（需 step-up，并告警）的只有三项：withdraw.enabled、payout.enabled、payout.queue_paused。<br>- withdraw.account_enabled.\* 只能由 super step-up 修改（涉及 BR-WDR-20 的税务前提）。<br>- 其余 withdraw.\*、payout.\*、tax.\* 的阈值与清单（包括 second_approval_\*、single_cap_fen、daily_cap_fen、watermark_\*、BR-WDR-28 的三份清单）由 finance 提议、super step-up 后生效；BR-WDR-28 的清单还需负责人确认。 | 默认假设 | 配置 withdraw.enabled、withdraw.account_enabled.SELF / PROMO、payout.enabled、payout.queue_paused；kill-switches 后台与配置变更审批流；payout 进程；告警规则；SM-WDR-W9 |
| BR-WDR-18 | **垫资水位与打款限额**<br>每小时整点计算两个量：企业支付宝可用余额 W（取数时刻记为 t_W；BR-WDR-22 ⑦ 验证前由财务手工录入并记录时间），以及未来 3 日预计提现 P = 近 7 个完整自然日（不含当日，+08:00）提现申请 amount_fen 的日均值 × 3（不含 REJECTED）。W &lt; 1.5P 时告警财务。<br>水位只在 EXECUTE 时检查。以下任一情况都整批拒绝、不迁移任何单，并提示“可用水位不足或数据过期，请拆分批次或刷新”，不做部分执行：<br>① W &lt; P；<br>② t_W 距今超过 2 小时；<br>③ Σ(本次将迁到 PAYING 的单的 net_fen) + Σ(status=PAYING 的单的 net_fen) + Σ(t_W 之后到达 PAID_API / PAID_MANUAL 的单的 net_fen) > W × `payout.watermark_usable_bp` / 10000（默认 9000）。<br>已进入 PAYING 的单不再按水位复核（BR-WDR-13 ③）。<br>payout 进程内的限额：单笔 net_fen ≤ `payout.single_cap_fen`（默认 500000 分）；当日已发出合计 ≤ `payout.daily_cap_fen` = 通道日限额 × 80%。 | 默认假设 | 配置 payout.single_cap_fen / daily_cap_fen / watermark_usable_bp / watermark_\*；watermark 定时任务（每小时）；后台 水位看板与手工录入；EXECUTE 接口；告警规则；AC-WDR-06 |
| BR-WDR-19 | **提现手续费**<br>MVP 所有提现的 `fee_fen = 0`。`fee_rules` 表按“通道 × 账户类型 × 金额区间 × 会员等级 × 活跃度”建全字段，但 MVP 计算器只支持“账户类型 × (比例 ratio_bp 或固定金额 fixed_fen)”，其余维度必须为空，否则保存配置时拒绝。同一账户类型同一时刻只能有 1 条生效规则（effective_from ≤ now &lt; effective_to，区间不得重叠，保存时校验）；ratio_bp 与 fixed_fen 必须恰好一个非空。计算方式：fee_fen = fixed_fen，或 round_half_up(amount_fen × ratio_bp / 10000)，且 0 ≤ fee_fen &lt; amount_fen。手续费在申请时计算，并与 fee_rule_id 一起固化到提现单。 | 默认假设 | fee_rules 表（effective_from、effective_to 与保存校验）；withdrawals.fee_fen、fee_rule_id；后台 费率配置；提现确认页手续费展示 |
| BR-WDR-20 | **税额计算与年度台账**<br>所得类型按账户固定：SELF→SELF_REBATE，PROMO→SERVICE_FEE；INCIDENTAL（活动奖励）放 P1。每类所得的计税方法 `tax.<income_type>.method ∈ {none, flat_rate, cumulative}` 与税率全部配置化，代码中不得硬编码税率。tax_fen 在申请时计算，并与 tax_rule_version 一起固化；四舍五入到分，tax_fen ≥ 0。计税年度取提现单 created_at 的 +08:00 自然年。累计方法下：本次税额 = max(0, 应扣(本年已到账累计收入 + 同年度在途同类申请额 + 本次 amount) − 本年已扣累计 − 同年度在途同类税额)。`tax_ytd(user_id, year, income_type, cum_income_fen, cum_withheld_fen, continuous_months)` 只在 PAID_API / PAID_MANUAL 时累加，year 取该单 created_at 的年份，cum_income 加 amount_fen；驳回与失败不累加。 | 待决策 | 配置 tax.\*、withdraw.account_enabled.PROMO；tax_ytd 表；withdrawals.tax_fen、income_type、tax_rule_version；ledger TAX_WITHHOLD / TAX_PAYABLE；提现确认页“预计到账 = 金额 − 手续费 − 代扣税”；B2-08；开发任务拆解 BF-12 算例验收 |
| BR-WDR-21 | **涉税导出与报送**<br>后台必须提供按自然季度（+08:00，按 paid_at）导出已到账提现的涉税明细，字段：姓名、证件号、所得类型、收入额（amount_fen）、已扣税额（tax_fen）、到账时间、收款账户（脱敏）、out_biz_no。含完整证件号的版本只有 finance 能导出，要求如下：导出前 step-up，并填写用途；文件存放在 OSS exports 私有桶，签名 URL 24 小时过期；文件首行写明导出人与导出时间；每次导出记审计（导出人、行数、用途）。super 只能导出脱敏版，证件号只保留前 6 位和后 4 位。报送时限（开展业务 30 日内报送平台基本信息、每季度终了次月报送）属于外部法规要求，在税务师书面意见确认前只作为上线检查项，不写成已确认的义务。 | 默认假设 | 后台 exports（涉税季度导出，全量 / 脱敏两种）；OSS exports 私有桶与签名 URL；audit_logs；上线检查清单；数据保留策略 |
| BR-WDR-22 | **支付宝通道能力待验证**<br>以下支付宝能力在沙箱实测并留下接口样例之前，不得写成事实，相关配置按保守默认运行：① 企业支付宝能否开通“单笔转账到支付宝账户”，以及 SELF / PROMO 适用的业务场景（默认按“佣金报酬”申请）；② 单笔、单日转账限额；③ 转账是否强制校验收款人姓名，姓名不符时返回什么码；④ 超时后用同一 out_biz_no 再次提交的官方语义（是否幂等返回原单）；⑤ 明确失败码清单、付款方侧失败码清单、查询接口各状态的含义（包括“订单不存在”“处理中”，以及成功后又被退回的状态，如果存在）；⑥ out_biz_no 的长度与字符集；⑦ 企业账户余额查询接口；⑧ 按日下载的账单能否包含 out_biz_no。 | 待验证 | 规划/09 CAP-X-06（支付宝行）；配置 payout.biz_scene.&lt;account_type>、definite_fail_codes、query_status_map、payer_side_codes、single_cap_fen、daily_cap_fen；AlipayChannel 适配器；specs/alipay-error-map.csv；B2-06 |
| BR-WDR-23 | **通道对账对提现的影响**<br>每日 T+1 对前一自然日（+08:00）的支付宝账务明细与提现单做核对：接口打款单按 out_biz_no 匹配，手动成功单按 channel_order_id 匹配；金额用账单金额对比 net_fen。差异处理：<br>① 支付宝成功、内部为 PAYING 且 needs_manual=false → 立即查询；查询返回成功才走 W5。查询结果不是成功 → 置 needs_manual=true，生成差错单并告警，之后按 BR-WDR-15 处理。<br>② 支付宝成功、内部为 PAYING 且 needs_manual=true → 只生成待处置提示并附上账单行，由 BR-WDR-15 的 W10 结束。<br>③ 以下情况生成差错单、告警，并为该会员新增 withdraw_holds（reason=recon_diff，不自动到期）：支付宝成功，而内部为 APPROVED / FAILED / REJECTED 或没有对应单；内部为 PAID_\*，而支付宝没有记录；金额不一致。<br>终态提现单不得修改状态或金额，更正只能经差错单 + 调账（发起人 ≠ 复核人，见 BR-FUND）。 | 默认假设 | recon_channel；差错单；withdraw_holds（recon_diff）；告警规则；B2-07 验收用例 |
| BR-WDR-24 | **提现打款告警**<br>以下情形必须告警（通知财务和负责人）：<br>- 自然日内（按状态迁移时间，+08:00）W6 次数 ÷ (W5 + W6 次数) > 2%，且分母 ≥20；不含 W8、W10。<br>- 按 W5 / W6 迁移时间排序，连续 3 次 W6。<br>- 任一单被置 needs_manual。<br>- 转账同步返回未识别的业务码（BR-WDR-28）。<br>- payout.queue_paused 被置位。<br>- W &lt; 1.5P（告警），或 W &lt; P（暂停）。<br>- EXECUTE 因水位被拒。<br>- 任一单走 W9。<br>- W10 判定 FAILED。<br>- 审核超时（BR-WDR-26）。<br>- R2 出现差异。<br>- 修改 withdraw.\* / payout.\* 的开关或配置。 | 默认假设 | 告警规则配置；可观测看板；规划/02 §13 |
| BR-WDR-25 | **用户侧状态文案**<br>withdrawal_status 到用户状态标题的映射与措辞只在 BR-TEXT-06 维护，资金术语含义只在 BR-TEXT-01 维护，本条不另写。本条只规定：①副文案的分支条件（见细则表：按 withdrawal_status、review_deadline、首次转账尝试后时长、needs_manual、失败类型 W6/W10、失败码是否账号类选择副文案 key）；REJECTED、FAILED 的副文案必须含原因与退回金额，【修改收款账号】入口只对账号类失败码显示（BR-TEXT-08）；②展示字段：提现记录必须展示申请金额 amount、手续费、代扣税、实际到账 net，以及各个时间点。PAYING 分支中的 T 取首次转账尝试时间；还没有尝试记录时取 executed_at。 | 待决策 | /v1/dict withdrawal_status 副文案 key；WithdrawRecords 页；提现详情页；通知模板；客服话术：提现到哪一步了；AC-WDR-08 |
| BR-WDR-26 | **审核时效与结果通知**<br>审核时效承诺为“工作日 24 小时”：只在工作日内计时（配置 workday_calendar，含法定节假日与调休，+08:00，工作日按全天 24 小时计；非工作日提交从下一个工作日 00:00 起算），`review_deadline = created_at + 24 个工作日小时`。“审核结束”指单据进入 PAYING、PAID_MANUAL 或 REJECTED。<br>超时判定：超时检查任务每 5 分钟运行一次，review_deadline 到达后 ≤5 分钟内判定；判定时状态仍 ∈ {PENDING_REVIEW, APPROVED} 即为审核超时，此时 ① 告警财务（BR-WDR-24，不受夜间限制）；② 向用户发 1 次推送 + 站内信（模板 WD_OVERDUE，文案按 BR-TEXT-07；不发短信）。判定时刻落在免打扰时段内的用户通知顺延到该时段结束时刻发送（时段取配置 notify.quiet_hours，定义与维护处见 BR-WATCH-15，本条不另写时段数值；若该配置改为按通知分类配置，本通知取交易/资金类的值）；发送前复查状态仍 ∈ {PENDING_REVIEW, APPROVED}，否则不发。每单只判定一次，用户通知幂等键 `withdrawal_id:OVERDUE`。<br>结果通知在状态迁移事务提交后经 outbox 发出：REJECTED、PAID_API、PAID_MANUAL 发推送 + 站内信；FAILED 发推送 + 站内信 + 短信。同一张单的同一个状态只通知一次，按 withdrawal_id + status 去重。 | 默认假设 | withdrawals.review_deadline；配置 workday_calendar、notify.quiet_hours（BR-WATCH-15）；scheduler 超时检查任务（5 分钟）；notify 模板与 outbox（含 WD_OVERDUE，幂等键 withdrawal_id:OVERDUE）；短信模板：提现失败；验收 AC-S2-20、AC-S2-29；后台 超时待审核列表；GET /v1/withdrawals/{id} |
| BR-WDR-27 | **MVP 不做的提现能力**<br>以下能力 MVP 不实现，相关开关默认关闭，客户端不出现入口：自动到账规则组（金额阈值 ≤X 元、时段、首提不自动、当日入账不自动、次数）；三项提现预警指标（60 天高佣订单占比、60 天失效含维权占比、30 天提现额 / 60 天确认收货返利）用于自动决策（自动转人工、自动拦截或自动到账判定）——MVP 只计算并作为审核标签展示，见 BR-WDR-29；灵工通道 FlexLaborChannel；手续费全矩阵与条件模式；奖励类收益的提现门槛。通道层必须抽象为 PayoutChannel 接口，MVP 只实现 AlipayChannel。 | 已确认 | PayoutChannel 接口；配置 withdraw.auto_payout.\*；规划/05 P1 清单 |
| BR-WDR-28 | **打款结果判定清单**<br>打款结果只能按三份配置清单判定：`payout.definite_fail_codes`（转账同步返回码 → W6）；`payout.query_status_map`（查询返回的状态 → success / fail / unknown，映射为 fail 时走 W6）；`payout.payer_side_codes`（转账同步返回码 → W9 + 暂停队列，见 BR-WDR-17）。<br>BR-WDR-22 ⑤ 验证完成之前：definite_fail_codes 与 payer_side_codes 为空；query_status_map 只把官方文档中的成功状态（暂记为 SUCCESS，待实测）映射为 success，其余状态一律为 unknown；转账同步返回任何非成功的业务码时，该单按结果未知处理（BR-WDR-14），同时系统置 payout.queue_paused=true 并告警。<br>清单每加入一个码或状态，都必须附沙箱或生产的请求/响应样例（存 规划/09 CAP-X-06 证据路径），由 finance 提议、super step-up 后生效，并经负责人确认。<br>成功时 paid_at 取支付宝返回的成交时间；没有返回时，取收到成功响应时的服务器时间（+08:00）。fail_code 在“失败码 → 用户文案”映射表中查不到时，显示“支付宝处理失败”。 | 待验证 | 配置 payout.definite_fail_codes / query_status_map / payer_side_codes；AlipayChannel 适配器；specs/alipay-error-map.csv；失败码 → 用户文案映射表；payout.queue_paused；告警规则；SM-WDR-W5、W6、W9 |
| BR-WDR-29 | **审核风险标签与提现预警指标**<br>风险标签只供审核人参考，不自动驳回、不自动放行、不改变校验结果。计算时点：BR-WDR-03 ⑭（加锁前）按申请时刻 t 计算下列 ①–⑧、⑩，结果（code、实际值、阈值）与计算时刻写入 withdrawals.risk_flags、risk_flags_at，随 W1 同事务插入，之后不自动重算；⑨ 在审核页加载时与 W2 提交前实时检查。窗口一律为 [t − N×24 小时, t]，时刻按 +08:00，金额单位分，比例单位 bp。<br>① first_withdrawal：该会员没有 status ∈ {PAID_API, PAID_MANUAL} 的提现单。<br>② credited_today：t 所在自然日 00:00 至 t，该会员任一账户有 REBATE_CREDIT、SHARE_CREDIT 或 REFERRAL_CREDIT 分录。<br>③ same_device_multi_account：判定口径（login_logs.device_hash、720 小时滑动窗口、按首次登录排序第 3 个及以后的账号才打标）与阈值 `risk.device_login_accounts_limit` 只在 BR-ID-37 维护；本条在 BR-WDR-03 ⑭ 时点调用同一判定函数，命中即写本标签，本条不另设计数口径与配置项。<br>④ invalid_ratio_60d（失效含维权占比）：分母 = 该会员 buy_type=self、已归属、paid_at 在 60 天窗口内的子订单数；分子 = 其中 rebate_status ∈ {VOID, CLAWED_BACK} 或存在 status=SUCCEEDED 的 order_rights 的子订单数；分子 × 10000 / 分母 > `risk.withdraw.invalid_ratio_bp`（默认 3000）且分子 ≥ `risk.withdraw.invalid_min_count`（默认 3）时命中。<br>⑤ high_commission_ratio_60d（高佣订单占比）：分母同 ④；单个子订单佣金率 = 联盟预估佣金 × 10000 / 计佣金额（均取订单同步回传值，向下取整）；分子 = 佣金率 ≥ `risk.withdraw.high_commission_rate_bp`（默认 5000）的子订单数；分母 ≥ `risk.withdraw.min_orders`（默认 5）且分子 × 10000 / 分母 > `risk.withdraw.high_commission_ratio_bp`（默认 5000）时命中。<br>⑥ withdraw_vs_received（30 天提现额 / 60 天确认收货返利）：分子 = 该会员 created_at 在 30 天窗口内、status ∉ {REJECTED, FAILED} 的提现单 amount_fen 合计（含本单）；分母 = 该会员作为受益人（自购、分享、直推）在 received_at 落在 60 天窗口内、rebate_status ∈ {WAITING, CREDITED} 的子订单上的返利份额合计（WAITING 取当前预估份额，CREDITED 取已入账净额）；分母 = 0，或分子 × 10000 / 分母 > `risk.withdraw.withdraw_received_ratio_bp`（默认 10000）时命中。<br>⑦ had_negative：该会员任一账户存在 balance_after_fen &lt; 0 的分录。<br>⑧ recon_diff：该会员存在 reason=recon_diff 的 withdraw_holds 记录（含已解除；未解除的已在 BR-WDR-03 ⑦ 被拒绝申请）。<br>⑨ blacklist_hit：申请之后才登记、且命中该会员手机号、身份证、收款支付宝 HMAC 或设备哈希的黑名单（BR-ID-31）。<br>⑩ payee_prev_other_user：见 BR-WDR-02。<br>任一项计算失败（查询超时或报错）时写 risk_calc_failed 标签，不阻断申请。 | 默认假设 | withdrawals.risk_flags、risk_flags_at；配置 risk.withdraw.invalid_ratio_bp / invalid_min_count / high_commission_rate_bp / high_commission_ratio_bp / min_orders / withdraw_received_ratio_bp（③ 的阈值用 BR-ID-37 的 risk.device_login_accounts_limit）；BR-ID-37 同设备多账号判定函数（login_logs.device_hash，720 小时）；ledger_entries；orders、order_rights、commission_splits 查询索引；blocklist；后台审核列表与详情标签；BR-WDR-03 ⑭；AC-ADM-07 |

### 7.2 细则

#### BR-WDR-01 细则 · 提现入口与鉴权

- 状态：默认假设
- 默认值：已确认部分：只限原生 App、签名、幂等、step-up 5 分钟且绑定 action（来源 规划/02 §12.1、04 §6.4）。本条新增：绑定 device_id；一次性使用，只在成功时消费。
- 决策人：负责人
- 依赖平台能力：无
- 取代：无
- 来源：规划/04 §6.1、§6.4；规划/03 §1、§5.3；规划/02 §12.1、§12.2；规划/01 F-ACC-07、F-AGENT-10、F-RISK-01；PRD v2.1 §6 鉴权
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 校验失败的返回：签名或重放 → 10401；step-up 缺少、过期、action 不符、user_id 或 device_id 不符、jti 已用 → 10003；用 h5_token 调用 → 越权 10403（令牌作用域不含提现，见 BR-ID-32）；缺少 Idempotency-Key → 20001。
- 何时消费 token：只有请求成功才消费。返回 3xxxx 业务错误（如金额低于下限），或签名、网络失败时不消费；用户在 5 分钟内改金额重试，不必重新收短信。同一 Idempotency-Key 的重放在幂等查找处（BR-WDR-03 ⓪）直接返回首次结果，不再校验 token。
- H5 钱包页和流水页只读；H5 上的【提现】按钮只能跳到原生 `Withdraw` 页。
- Agent 工具注册表中出现 withdraw、payout-account 或 wallet 写接口时，CI 失败（F-AGENT-10 的 grep 检查）。
- 例：用户 10:00:00 完成短信验证，拿到 step_up_token（action=withdraw）。10:05:01 提交提现 → 10003，需重新验证；10:04:59 提交 → 通过这一项。
- 例：10:00 验证（action=payout_account_change）后换绑成功，10:02 用同一个 token 提现 → 10003（action 不符，且 token 已用）。
- 边界：有效期为签发时刻 + 300 秒，`now < exp` 即有效。

#### BR-WDR-02 细则 · 收款账号绑定与变更

- 状态：默认假设
- 默认值：每月变更上限 2 次（规划/06 Q-B3）。不提供解绑、计次口径、姓名规范化为本条新定。
- 决策人：财务
- 依赖平台能力：支付宝转账是否校验收款人姓名（BR-WDR-22 ③）
- 取代：
  - PRD v2.1 §11.6：「每月改收款账号 1 次」
  - PRD v2.1 §11.6：「支付宝账号实名须与平台实名一致（用支付宝接口校验姓名）」
- 来源：规划/01 F-WDR-02；规划/04 §3.2 payout_accounts、§7；规划/06 Q-B3；后端功能规划 §2.1 收款账号；PRD v2.1 §11.6
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 绑定时平台只做本地比对：姓名 = 实名姓名。转账时必传收款人姓名；支付宝是否据此校验、校验失败返回什么码，待 BR-WDR-22 ③ 验证。验证前，姓名不符类的返回按结果未知处理（BR-WDR-14、28），不自动置 FAILED。如果验证结果是支付宝不校验姓名，由负责人决定：在绑定环节加支付宝侧实名核验，或调低首次提现的上限（见 7.3 第 7 条）。
- PRD 所说“绑定时用支付宝接口校验姓名”，在接口能力验证前不做（BR-WDR-22）。
- 登录号先规范化再算 HMAC：去空格；邮箱转小写；手机号只保留数字。具体实现由代理决定，但必须写在 payout_accounts 的迁移说明中。
- 存储：每个会员在 payout_accounts 中只有 1 条当前行（is_current=true）。换绑时旧行置 is_current=false，并写 payout_account_changes（user_id、old_hmac、new_hmac、changed_at）。本月变更次数 = 本月 payout_account_changes 的条数，每月 1 日 00:00 +08:00 起自然重置，不依赖定时任务清零。
- 会员换走的旧账号可以被其他会员绑定。若某 alipay_hmac 近 90 天内曾被其他会员绑定过，允许绑定，但之后的提现单打 risk_flag `payee_prev_other_user`，审核人可见。
- 例：用户 10 月 3 日首次绑定（不计次），10 月 8 日第 1 次变更，10 月 20 日第 2 次变更，10 月 25 日再变更 → 30303（payout_account_change_limit）；11 月 1 日 00:00 起可以再变更。10 月 25 日提交的账号与当前相同 → 不算变更，也不报超限。
- 例：实名为“阿依古丽•买买提”，用户填“阿依古丽·买买提 ”（带全角空格）→ 规范化后相等，通过。
- 1 个身份证最多对应 1 个可提现会员，属于实名规则，见 BR-ID-25（(app_id, id_no_hmac) 在 verified 中唯一）。

#### BR-WDR-03 细则 · 申请校验顺序与错误码

- 状态：默认假设
- 默认值：错误码本身已在 规划/04 §7 确认。以下为本条新定：校验顺序、步内优先级、reason 枚举、前置与 ⓪ 的位置、rules 接口跳过哪些步骤。
- 决策人：代理可自定
- 依赖平台能力：无
- 取代：
  - 后端功能规划 §2.9 申请校验：「失败码 30201–30209 与 GET /v1/withdrawals/precheck」
  - PRD v2.1 §11.5：「申请条件只列实名、余额、最低额、无负余额（未列收款账号与 step-up）」
- 来源：规划/04 §4.2 W1、§5 幂等、§7、§6.4；规划/01 F-WDR-03；后端功能规划 §2.9 申请校验；PRD v2.1 §11.5、§14.4
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- max_withdrawable_fen = can_withdraw ? floor_to_step(min(available_fen, withdraw.max_amount_fen, 未成年本月剩余额度)) : 0。floor_to_step 按 amount_step_fen 向下取整。结果 &lt; min_amount_fen 时，返回 can_withdraw=false、block_code=30303、block_reason=below_min、max_withdrawable_fen=0。次数用尽、被冻结或存在负余额时，can_withdraw=false，max 为 0。
- 鉴权放在开关之前：签名未通过的请求不应得到业务状态信息，这样也与全局中间件的执行顺序一致。
- `data.reason` 为枚举，客户端从 `/v1/dict` 取文案。取值：`account_frozen`、`below_min`、`not_multiple`、`above_max`、`net_too_small`、`daily_count`、`monthly_count`、`payee_daily_users`、`self_purchase_required`、`payout_account_change_limit`。
- ⑦⑧⑩⑪⑫ 在 BR-WDR-07 的锁内再执行一次。先查询、后加锁的做法不够。
- ③a 与 BR-ID-31 对齐：黑名单命中在申请时直接拒绝（44001，提示语可配），不再只作为审核标签；申请之后才登记的黑名单，已有单据由审核人按 BR-WDR-29 的 blacklist_hit 标签处理。
- 30306 只表示开关关闭；账务差异冻结（BR-FUND-19）不再返回 30306，统一记为 withdraw_holds（reason=ledger_mismatch），在 ⑦ 返回 30303 reason=account_frozen，因此自然先于 ⑧ 的 30302。
- 例：用户 SELF 可用 ¥30.50，PROMO 可用 −¥2.00，申请 SELF ¥30 → 在第 ⑧ 步返回 30302，即使 SELF 余额够也一样。
- 例：申请 ¥0.50 且当日已提 1 次 → 30303 below_min（⑨ 在 ⑪ 之前；⑨ 内 below_min 在 not_multiple 之前）。申请 ¥5,000.50 → not_multiple。
- 例：amount_fen=-100 → 20001，不进入 ⑨。
- 例：withdraw.enabled 已关，客户端重放此前成功的同 key 请求 → 返回首次的成功结果（⓪ 在 ① 之前）。
- 后端功能规划中的 30201–30209 编号作废，以 规划/04 §7 的 3030x 为准。映射：30201→30301、30202→30302、30203→30303、30204→30304、30205→30305、30206→30307、30207→30303（daily_count 等）、30208→30306（提现总开关）或 30303 reason=account_frozen（会员禁止提现 withdraw_disabled，本主题记为 withdraw_holds reason=manual）、30209→30309。
- 按 C-03、C-09 默认处理，待负责人（码号分配）、财务（冻结记录方式）确认。⑦ 纳入 appealing(prev=frozen)、③ 的 banned 含 appealing(prev=banned)（BR-WDR-05）：按 C-28 默认处理，待负责人确认。

#### BR-WDR-04 细则 · 金额与次数限制默认值

- 状态：默认假设
- 默认值：最低 ¥1、整元步长、单笔上限 ¥5,000、每人每日 1 次/每月 10 次（两账户合计）、同一支付宝每日 1 个会员、90 天自购门槛关闭。来源：沿用 规划/06 Q-B3；步长沿用后端功能规划（优券汇现行做法）。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - 后端功能规划 §2.9：「同一支付宝账号每天 2 次」
  - PRD v2.1 §11.6：「提现限制初值：每月改收款账号 1 次（其余与规划/06 相同）」
- 来源：规划/06 Q-B3；规划/01 F-WDR-03、J6；规划/02 §8.1 日切；后端功能规划 §2.9；参考_花卷云查漏底稿 §7
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 驳回和打款失败不占次数，保证“打款失败 → 改账号 → 当日重提”走得通（BR-WDR-25 对账号类失败码提示可以改账号重试）。
- 同账号跨会员的规则只数“其他会员”：同一会员当天用同一个支付宝分别提 SELF 和 PROMO，不触发这一条，但受每日次数约束。
- 例（默认值）：会员 10-12 09:00 提 SELF ¥50（审核中），11:00 再提 PROMO ¥20 → 30303 reason=daily_count。如果 09:00 那笔在 10:30 被驳回，11:00 可以提交。
- 例：¥12.50 → 30303 reason=not_multiple；¥5,000 通过；¥5,001 → above_max。
- 近 90 天自购门槛 `withdraw.self_purchase_90d.enabled` 默认 false。开启后，要求存在 buy_type=self、归属于该会员的子订单，其 received_at（确认收货时间）∈ [申请时刻 − 90×24 小时, 申请时刻]，且当前状态满足 BR-FUND-01 的 platform_status ∈ {RECEIVED, SETTLED} 且 rebate_status ∈ {WAITING, CREDITED}（不含 VOID、CLAWED_BACK；部分退款后仍为 WAITING / CREDITED 的计入）；否则返回 30303 reason=self_purchase_required。映射说明：对应 规划/04 单一 order_status 的 RECEIVED、CREDITED、SETTLED（不含 INVALID、CLAWED_BACK），换算按 BR-FUND-01「与 规划/04 单一 order_status 的映射」。
- 门槛金额 `withdraw.self_purchase_90d.min_fen`（默认 0 分，表示只要求存在 1 单）：开启且 >0 时，另要求上述子订单中该会员自购返利份额（入账前取当前预估，入账后取已入账金额，单位分）合计 ≥ 该值，否则同样返回 30303 reason=self_purchase_required。来源：后端功能规划 §2.9 申请校验「或自购收货佣金低于阈值」。
- max_amount_fen 不允许为 0 或超过 payout.single_cap_fen。超过单笔打款上限的单在 payout 复核时只会反复 W9，永远打不出去。
- 按会员等级设置不同限制放到 P1。
- 配置变更由 finance 提议、super step-up 后生效（BR-WDR-17）。
- 按 C-01 默认处理，待负责人确认。

#### BR-WDR-05 细则 · 提现阻断：负余额与冻结

- 状态：待决策（由默认假设改为待决策：负余额时自动驳回未打款单涉及资金处理，属 §14.3 C-08 待裁决事项）
- 默认值：任一账户为负即两账户都禁提（与 BR-FUND-11 一致，BR-FUND-11 待决策）。规划/01 F-SET-04 只写“负余额期间禁止提现”，没说作用范围，这里取保守口径。负余额引起的阻断按 (a) 自动驳回同账户未打款单、另一账户暂停；风控冻结与 withdraw_holds 引起的阻断不改单据状态、审核照常；冻结只用 withdraw_holds 表记录，账务差异冻结（BR-FUND-19 的 LEDGER_MISMATCH）作为其 reason=ledger_mismatch。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - 本条旧版：「阻断（含负余额）不会自动改变单据状态，W2 审核通过不受影响」（负余额部分改按 (a)）
  - BR-FUND-21 旧正文（负余额时未打款提现单的守卫、事件、驳回、PAYING 处理与例子，2026-09-30 并入 (a) 与本细则，BR-FUND-21 只保留编号）
  - 规划/04 §4.2 W2：「APPROVE 守卫：审核人有权限且已 step-up（未校验账户非负）」（原登记于 BR-FUND-21）
  - 规划/04 §4.2 W4：「EXECUTE 守卫：执行人 ≠ 审核人；超额需第二人审批；企业账户水位充足（未校验账户非负）」（原登记于 BR-FUND-21）
  - BR-FUND-19：「冻结方式：写 users.withdraw_blocked_reason=LEDGER_MISMATCH，提现申请返回 30306」（改为 withdraw_holds reason=ledger_mismatch，申请返回 30303 reason=account_frozen）
  - 本条旧版 reason 值 `invariant_fail`（改名为 ledger_mismatch，含义不变：日终不变量校验或入账证实核对发现差异）
- 来源：规划/01 F-SET-04、F-SET-06；规划/02 §8.4；规划/04 §3.2 users、§4.2 W1、§7；PRD v2.1 §11.7、§14.4；后端功能规划 §2.9；08 §6 BR-FUND-11、BR-FUND-19、BR-FUND-21
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 两账户不互抵（BR-FUND）。但负余额是用户欠平台的钱，如果允许用另一个账户提走，会扩大坏账，所以按会员整体禁提。
- `available_fen = 0` 不算负余额。
- risk_state=frozen 仍表示风控冻结，由风控模块维护，与 withdraw_holds 各自独立判断。
- 例：PROMO 因扣回变成 −¥3.20，SELF 可用 ¥80 → 两个账户申请都返回 30302。PROMO 后续入账补到 ¥0 后恢复。
- 例（同账户）：SELF available=0、frozen=¥10（PENDING_REVIEW 单 ¥10），SELF 订单扣回 ¥3 → available=−¥3 → 系统 W3 驳回该单（NEGATIVE_BALANCE），WITHDRAW_RETURN ¥10 → available=¥7、frozen=0；推送「提现未通过」，原因文案「有订单被扣回，冻结金额已用于抵扣」。
- 例（同账户，部分扣回）：SELF available=0、frozen=¥10，扣回 ¥3 → available=−¥3 → 驳回 → available=¥7；用户可重新申请 ¥7。
- 例（跨账户）：用户申请 SELF ¥50（审核中）后，PROMO 因扣回变为 −¥2。SELF 单置 blocked_reason=NEGATIVE_BALANCE_OTHER，不能审核通过，执行批次时被跳过，结果中列出原因“会员提现阻断：负余额”（BR-WDR-12）；PROMO 入账补到 ≥0 后自动清空，照常审核与执行。如果该单已进入 PAYING 但还没发出转账，payout 进程走 W9 回到 APPROVED，再置 blocked_reason。
- 例（同账户，PAYING 未发出）：SELF available=0、frozen=¥10，单据已 PAYING 但 payout 进程尚未写 kind=transfer 尝试记录，此时扣回 ¥10 → available=−¥10 → payout 复核走 W9 回到 APPROVED（member_blocked）→ 提现模块随即 W3 驳回：WITHDRAW_RETURN ¥10，available=0。若扣回时已写 transfer 尝试记录 → 不拦截，按打款结果完成，available 保持 −¥10。
- 同账户为何驳回而不是暂停：冻结额直接抵扣负数，敞口立即消失，无需维护解除逻辑；跨账户两账户不互抵，驳回退回无法抵扣，所以只阻断。已提交支付宝的单拦截会造成结果未知，所以已发出转账的 PAYING 不拦截。
- 例（风控冻结）：R2 发现该会员有重复打款差错单 → 追加 withdraw_holds（reason=recon_diff）。该会员的单据状态不变，审核人仍可审核通过；APPROVED 单在执行批次时被跳过。
- 解除 manual、recon_diff、ledger_mismatch：由财务在差错单关闭后操作，需 step-up 并记审计（ledger_mismatch 的解除时点与 BR-FUND-19「差错单关闭时 step-up 解除」一致）。manual_failed_watch 到期后自动失效（BR-WDR-15）。
- 后端功能规划 §2.9 的「会员禁止提现 withdraw_disabled（风控或客服设置）」在本主题记为 withdraw_holds reason=manual。
- appealing（申诉中）按申诉前状态取效果（BR-ID-36）：prev_risk_state=banned → 申请返回 10006；prev_risk_state=frozen → 申请返回 30303 reason=account_frozen，已有非终态单按 (b) 处理。与 BR-CALC-13 对 appealing 延后入账一致。
- 按 C-08、C-09 默认处理，待财务确认。appealing 纳入提现阻断按 C-28 默认处理，待负责人确认。

#### BR-WDR-06 细则 · 未成年人提现限制

- 状态：待决策
- 默认值：按 规划/01：14–18 周岁自购返利每月上限 ¥200，推广收益禁提；理由是规划为生效文档。另一选项来自 PRD v2.1 与开发任务拆解 BT-18：未满 18 周岁一律禁提，只需把 minor_monthly_cap_fen 配为 0，代码不变。
- 决策人：法务
- 依赖平台能力：无
- 取代：
  - PRD v2.1 §15 合规：「未满 18 周岁不得提现」
  - 开发任务拆解 BT-18：「实名认证接入后未满 18 岁禁提现」
  - 规划/04 §3.2 realname：「birth_year 字段（按年份判断会把接近 18 岁的未成年人判为成年）」
- 来源：规划/01 §4.3 未成年规则、F-ACC-08；规划/06 Q-B3；规划/04 §3.2 realname、§7 30309、30407；后端功能规划 §12.1 B14；PRD v2.1 §15；开发任务拆解 BT-18
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 例：16 岁用户 10 月已提 SELF ¥150（已到账），再申请 ¥60 → 150+60=210 > 200 → 30309；申请 ¥50 → 通过。
- 例：用户 2008-10-20 出生，2026-10-20 23:59 申请按 17 岁处理；2026-10-21 00:00 起按成年处理。
- 例：用户 2008-02-29 出生，2026 年不是闰年，adult_at = 2026-03-02T00:00+08:00。
- 存储：按 BR-ID-25 存 realname.birth_date（加密），adult_at 由其推导（可存为派生列，或校验时解密计算），不另存明文出生日期；14 周岁判定（BR-ID-26）、邀请限制（BR-INV-19）与本条共用同一 birth_date。adult_at 只供提现校验读取，后台不展示。
- 满周岁口径只在 BR-ID-26 维护（生日次日 00:00，从严），本条的 adult_at 调用同一推导函数。按 C-15 默认处理，待法务确认。
- 例：14–18 用户 10 月已申请 SELF 150 元（APPROVED）+ 已到账 40 元（PAID_API）→ 再申请 20 元 → 150+40+20=210 > 200 → 30309，remaining_fen=1000。
- 例：同一 14–18 用户并发提交 2 笔 SELF 各 150 元 → 两笔都在 BR-WDR-07 的 users 行锁上排队，后到的一笔锁内复核时已申请额为 150 → 只有 1 笔成功，另一笔 30309，remaining_fen=5000。
- 例：14–18 用户 10 月一笔 SELF 100 元被驳回（REJECTED）→ 不计入，本月仍可申请 200 元。
- 限额、计数口径、加锁与 30309 只在本条维护；BR-ID-26 (d) 已改为引用本条。取代 BR-ID-26 (d) 旧写法：「计入状态 PENDING_REVIEW、APPROVED、PAYING、PAID_API、PAID_MANUAL…对该用户 ledger_accounts（account_type=SELF）行 SELECT … FOR UPDATE」（状态集合与本条 ∉ {REJECTED, FAILED} 等价，BR-WDR-08 只有 7 个状态；加锁以 BR-WDR-07 为准）。
- `max_withdrawable_fen`（BR-WDR-03 rules 接口）对未成年人：PROMO 为 0；SELF 取 min(按其他规则算出的值, 本自然月剩余额度)。
- 14–18 岁本来就不开放推广收益（规划/01 §4.3），PROMO 禁提是防御性规则。
- 按 C-15 默认处理，待法务确认。

#### BR-WDR-07 细则 · 提现单创建、并发锁与幂等

- 状态：默认假设
- 默认值：已确认部分：同一事务内锁行、复核、建单、冻结；out_biz_no 固定不变；幂等落 PG（来源 规划/00 §6、02 §5.3、04 §5）。本条新定：先锁 users 行与加锁顺序、advisory lock、业务错误也写幂等、提现类接口的幂等记录不按 30 天清理。
- 决策人：负责人
- 依赖平台能力：out_biz_no 长度与字符集（BR-WDR-22 ⑥）
- 取代：
  - PRD v2.1 原稿（规划/00 §6 所列）：「幂等结果缓存 24 小时」
  - 规划/04 §3.2 idempotency_keys：「保留 30 天（对提现与收款账号接口不再适用）」
  - 后端功能规划 §2.9 创建：「tax_base_fen、tax_withheld_fen 字段名（统一为 tax_fen，计税基数由 amount_fen 与 tax_rule_version 推出）」
- 来源：规划/00 §6；规划/01 F-WDR-04；规划/02 §5.3、§8.1、§8.4；规划/04 §3.2 withdrawals、idempotency_keys、§4.2 W1、§5 幂等；后端功能规划 §2.9 创建；开发任务拆解 BF-06
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

- 客户端规则：用户每点一次【提交】生成一个新 key；只有网络重试复用同一个 key。
- `out_biz_no` 格式由代理决定，但须满足：只含 ASCII 字母和数字，长度 ≤32，全局唯一，不含用户信息，例如 `W20261012A7K3P9Q2M5X8`。支付宝实际允许的长度和字符集以 BR-WDR-22 ⑥ 的验证结果为准。
- 快照字段：`account_type`、`income_type`（SELF→SELF_REBATE，PROMO→SERVICE_FEE）、收款人快照、`fee_rule_id`、`tax_rule_version`。
- 不变量：并发提现不会让 available 变负（规划/02 §8.4 第 6 条）。
- 例：用户 SELF 可用 ¥100，两个请求（不同幂等键）同时各申请 ¥80 → 一个成功（PENDING_REVIEW，available=20，frozen=80），另一个在锁内复核失败，返回 30301。
- 例：同一会员同时提交 SELF ¥50 和 PROMO ¥20（不同 key，daily_count=1）→ 两个事务都要先锁 users 行，因此串行执行；恰好 1 单成功，另一单返回 30303 daily_count。
- 例：同一幂等键因网络重试并发 2 次 → 首个请求未完成时，后到的请求得到 40901；客户端用同一个 key 重放后，拿到与首次相同的 withdrawal_id；只生成 1 张单。
- 例：用户用某个 key 申请得到 30301，之后余额入账，再用同一个 key 重放 → 仍返回 30301（首次结果）。
- 验收：真实 PG（不用 mock）上并发 50 次同键请求 → 只有 1 单；并发 20 个不同键 → 冻结总额 ≤ 原可用余额；并发 SELF 与 PROMO 各 1 单 → 恰好 1 单成功。

#### BR-WDR-08 细则 · 提现状态机

- 状态：默认假设
- 默认值：保留 规划/04 的 APPROVED 中间态；W8 只能从 APPROVED 进入；新增 W9（退回待执行）与 W10（24 小时未知时双人处置）。理由：APPROVED 是“审核人 ≠ 执行人”和批次执行的前提；W8、W9、W10 的设定用于消除重复打款路径。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD v2.1 §11.5：「6 态状态机，审核通过直接 PAYING（无 APPROVED）；状态名 SUCCESS_AUTO / SUCCESS_MANUAL」
  - 后端功能规划 §3.3：「通过后直接 PAYING；状态名 AUTO_SUCCESS / MANUAL_SUCCESS」
  - 规划/02 §5.3 时序图：「→ AUTO_SUCCESS」
  - 规划/04 §4.2 W8：「APPROVED / PAYING（人工确认未打出）→ PAID_MANUAL」
- 来源：规划/04 §2.4、§4.2；规划/01 F-WDR-05；规划/02 §5.3；后端功能规划 §3.3；PRD v2.1 §11.5
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

| # | 从 | 事件 | 守卫 | 到 |
|---|---|---|---|---|
| W1 | — | APPLY | BR-WDR-03 全部通过 | PENDING_REVIEW |
| W2 | PENDING_REVIEW | APPROVE | BR-WDR-10；所属账户 available_fen ≥ 0 且 blocked_reason 为空（BR-WDR-05 (a)）；风控冻结与 withdraw_holds 不影响审核通过 | APPROVED |
| W3 | PENDING_REVIEW / APPROVED | REJECT | 必填原因码；从 APPROVED 驳回时不得有 pending/success/unknown 转账尝试，有 fail 尝试需第二人确认（BR-WDR-10）；系统驳回 NEGATIVE_BALANCE 只针对没有任何转账尝试的单（BR-WDR-05 (a)） | REJECTED |
| W4 | APPROVED | EXECUTE | BR-WDR-11、12（含该单没有任何转账尝试、所属账户 available_fen ≥ 0、blocked_reason 为空）；execute_seq +1 | PAYING |
| W5 | PAYING 且 needs_manual=false | CHANNEL_SUCCESS | BR-WDR-14、28 | PAID_API |
| W6 | PAYING 且 needs_manual=false | CHANNEL_FAIL | BR-WDR-14、28 | FAILED |
| W7 | PAYING | CHANNEL_UNKNOWN | — | PAYING（排入查询；T+24h 置 needs_manual 并停止自动查询） |
| W8 | APPROVED | MANUAL_PAID | BR-WDR-16 | PAID_MANUAL |
| W9 | PAYING | HOLD | 发出转账前复核未过（BR-WDR-13 ③），或转账返回付款方侧码（BR-WDR-17、28） | APPROVED（写 hold_reason、hold_at；清空 executor_id、executed_at） |
| W10 | PAYING 且 needs_manual=true | MANUAL_RESOLVE | BR-WDR-15 | PAID_API / FAILED |

- 每条迁移对应的分录见 BR-WDR-09；测试 ID 为 `SM-WDR-W1…W10`。
- 例：财务 A 点“驳回”，执行人 B 同时执行批次，两边都以 status=APPROVED 为条件 → 只有先提交的一方生效，另一方得到 20902（data.resource=withdrawal）。
- 并发冲突码：原写 30310，改用与订单同义的 20902，以 `data.resource` 区分 order / order_attribution / withdrawal；30310 不再分配。
- W2、W3、W4、W8 守卫中与负余额有关的部分（所属账户 available_fen ≥ 0、blocked_reason、系统驳回）来自 BR-WDR-05 (a)。
- 状态机定义写入 `specs/state-machines/withdrawal.yaml`。属性测试需覆盖：任意事件序列下，frozen 合计 = 非终态单金额合计。
- 按 C-03（并发冲突码，待负责人确认）、C-08（负余额守卫，待财务确认）默认处理。

#### BR-WDR-09 细则 · 各状态的资金分录

- 状态：默认假设
- 默认值：冻结金额留在用户 frozen 子户直到终态，不经过在途科目。理由：这与三处现有写法一致——规划/04 §2.4 的流水类型定义（WITHDRAW_PAID = 冻结减少，WITHDRAW_RETURN = 冻结转回可用）、后端功能规划、PRD v2.1；只需改 规划/02 §8.3 一处，并且能得到可校验的不变量 frozen = 非终态单合计。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - 规划/02 §8.3：「进入打款：借 USER_\*.frozen 贷 WITHDRAW_IN_TRANSIT；打款成功：借 WITHDRAW_IN_TRANSIT 贷 CASH_ALIPAY」
  - 规划/04 §4.2 W4–W6：「冻结 → 在途；在途 → 出金；在途 → 可用」
  - PRD v2.1 §11.5：「WITHDRAW_UNFREEZE / WITHDRAW_PAYOUT 流水名」
  - 后端功能规划 §2.9：「UNFREEZE、TAX_WITHHELD 流水名」
- 来源：规划/04 §2.4、§4.2；规划/02 §8.2、§8.3、§8.4；后端功能规划 §2.9 payout-worker 规则 3；PRD v2.1 §11.5
- 需同步修改的规划文档：4 处（计数仅作记录，落点见 README §0.6）

- 每条分录的 `uniq_key = wd:{withdrawal_id}:{FREEZE|RETURN|PAID|FEE|TAX}`，重放时不会重复记账。
- 不变量 frozen_fen = Σ 非终态提现单 amount_fen、不使用 `WITHDRAW_IN_TRANSIT` 科目：见 BR-FUND-14，本条分录模板必须使该不变量在任意迁移后成立。
- 例：PROMO available=5000，申请 ¥30 → W1 后 available 2000、frozen 3000；W5 成功，fee 0、tax 0 → 只写 WITHDRAW_PAID 3000 一条用户分录（贷 CASH_ALIPAY 3000），frozen=0，已提现累计 +3000；若 W6 明确失败 → 写 WITHDRAW_RETURN 3000，available 回到 5000。
- 例：申请 ¥100，fee ¥1，tax ¥2 → W5（或 W8、W10 判 PAID_API）写一张凭证：用户 frozen 三条借方分录 WITHDRAW_PAID 9700、WITHDRAW_FEE 100、TAX_WITHHOLD 200，合计 10000；对方 贷 CASH_ALIPAY 9700、FEE_INCOME 100、TAX_PAYABLE 200。
- 科目表与舍入以 BR-FUND（BR-FUND-13、BR-FUND-15）与 specs/ledger-rules.md 为准；提现的记账时点、ledger_type 与借贷科目只在本条维护。

#### BR-WDR-10 细则 · 审核与驳回

- 状态：默认假设
- 默认值：本条新定：原因码枚举、用户不能自撤、有转账尝试时的驳回限制。已在 规划/04 §11 确认：审核角色与 step-up。
- 决策人：财务
- 依赖平台能力：无
- 取代：无
- 来源：规划/04 §4.2 W2、W3、§11；规划/01 F-ADM-07、F-RISK-03；规划/02 §12.5；后端功能规划 §2.9 审核
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 审核列表必须展示风控标签 `risk_flags`（定义、窗口与阈值见 BR-WDR-29）：首次提现、当日有入账、同设备多账号（口径见 BR-ID-37）、命中黑名单、近 60 天失效（含维权）占比高、近 60 天高佣订单占比高、30 天提现额与 60 天确认收货返利之比高、有过负余额、R2 差异、payee_prev_other_user。这些标签都不会自动驳回；blocked_reason 非空的单另以“暂停”标识展示。
- 各编码的用户文案只在 BR-TEXT-08 维护（字典 withdraw_reject_reason）；NEGATIVE_BALANCE 的文案与 BR-WDR-05 (a) 的推送一致。旧编码 INFO_MISMATCH、ACCOUNT_RISK、RULE_NOT_MET 废弃，编码以本条为准（G-03）。ORDER_ABNORMAL、USER_REQUEST 的对外文案为新增，按 G-03 默认处理，待财务确认。
- 批量审核：界面可以多选，一次 step-up 覆盖本次操作；服务端逐单做 W2 的 CAS，部分失败时逐单返回结果。
- 例：用户申请 ¥200，财务以 PAYEE_INFO_INVALID 驳回 → 状态 REJECTED，available +20000，推送“提现未通过：收款信息有误，¥200.00 已退回可提现余额”。
- 例：某单转账返回付款方侧码后经 W9 回到 APPROVED（有 result=fail 的尝试），财务甲驳回 → 进入待确认，财务乙确认后才变为 REJECTED 并退回余额。
- APPROVED 的单在 EXECUTE 之前仍可驳回；进入 PAYING 后不可驳回。
- 按 C-08 默认处理，待财务确认。

#### BR-WDR-11 细则 · 职责分离与第二人审批

- 状态：默认假设
- 默认值：A=¥500、B=¥20,000（规划/06 Q-B3）；super 与 finance 都能审核和执行（规划/04 §11）。批准锁定成员、批准人可以是审核人为本条新定。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD v2.1 §13.2：「财务审核与财务出纳分成两个角色；超管不可审核或打款」
  - 后端功能规划 §12.1 B13：「A、B 待拍板」
- 来源：规划/04 §4.2 W4、§11；规划/02 §12.5；规划/01 F-WDR-07、F-ADM-07；规划/06 Q-B3；后端功能规划 §2.9 审核、§3.3；PRD v2.1 §13.2
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 角色按 规划/04 §11：super 和 finance 都能审核和执行，但同一张单的审核与执行不能是同一人。
- 阈值用 amount_fen 比较（含手续费与税，偏保守），用批准时锁定成员的合计计算。边界含等号：单笔恰好 ¥500 也需要第二人审批。
- 批准人可以是审核人、W8 确认人可以是审核人：这是为了让 MVP 的两人团队能运转。团队 ≥3 人后是否收紧，由财务决定（见 7.3 第 8 条）。
- 例：批次 30 单，合计 ¥19,999.00，最大单 ¥499.00 → 不需要第二人。再加入一单 ¥1.00，合计 ¥20,000.00 → 需要第二人；已有的批准随之失效。
- 例：财务甲审核了单 X，又把 X 放进自己执行的批次 → X 被跳过，返回“执行人不能是审核人”；批次其余单照常执行。
- 运营前提：内测前至少有 1 名 super 和 1 名 finance，且是两个不同的自然人；否则无法完成 W10 与手动成功。写入上线检查项。

#### BR-WDR-12 细则 · 批次执行

- 状态：默认假设
- 默认值：已确认部分：批次内逐单独立、不整批重跑、只投递 APPROVED 单（规划/02 §5.3 硬规则、规划/01 F-WDR-07）。本条新定：jobId 带 execute_seq、有转账记录即拒绝执行、批次级检查。各守卫的阈值和口径，按所引用条目的状态执行。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 后端功能规划 §2.9 payout-worker 规则 1：「transfer 任务 jobId=out_biz_no」
  - 规划/02 §5.3 时序图：「每单一个任务 jobId = withdrawal_id」
- 来源：规划/04 §4.2 W4；规划/02 §5.3；规划/01 F-WDR-07；后端功能规划 §2.9 审核
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 不整批重跑：一个批次 50 单中 3 单失败，对这 3 单各自处理（用户改账号后重提，或人工处理），不把 50 单重新执行。
- 为什么 jobId 带 execute_seq：队列按 jobId 去重，已完成或已失败的同 jobId 任务还留在队列里时，新任务会被静默丢弃。如果 jobId 只用 withdrawal_id，经 W9 退回后再执行的单会卡在 PAYING。payout 进程收到 execute_seq 与单据当前值不一致的旧任务时直接结束（BR-WDR-13 ①）。
- 已有转账记录的单被拒绝，原因为“已有转账记录，只能手动成功（BR-WDR-16）或驳回（BR-WDR-10）”。要取消这一限制，须等 BR-WDR-22 ④ 验证“同一 out_biz_no 重提幂等”，并经负责人批准。
- 例：批次 10 单，其中 1 单会员被冻结、1 单审核人 = 执行人 → 8 单进入 PAYING，2 单留在 APPROVED，结果页显示 2 条原因。
- 验收：一张单经 W9 回到 APPROVED 后再次执行 → 生成新任务（execute_seq=2），并被 payout 进程处理。

#### BR-WDR-13 细则 · payout 进程与打款前复核

- 状态：默认假设
- 默认值：已确认部分：规划/02 §5.3 硬规则（转账不重试、out_biz_no 不变）与“固定 1 个实例”（02 §3.1）。本条新定：先记后发、10 秒超时、concurrency=1、复核顺序、hold_reason 枚举、W9、不在进程内复核水位。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 规划/02 §5.3 时序图：「payout 进程再校验单笔上限、单日总额、企业账户水位（水位改为只在 EXECUTE 检查）」
- 来源：规划/02 §2、§3.1、§5.3、§12.6、§12.7；规划/04 §3.2 payout_attempts；规划/05 §3.3 B2-06；后端功能规划 §2.9 payout-worker 规则 1、4、5；PRD v2.1 §4.2 A7、§14.2
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

- 先记后发的作用：进程在“请求已发出、响应未收到”时崩溃，重启后看到 pending 记录，只会走查询，不会再转一次。
- 转账参数：out_biz_no；金额 = net_fen/100，保留 2 位小数；收款人登录号与姓名取提现单快照；业务场景按 account_type 读配置（BR-WDR-22）。
- 每次调用 payout_attempts 都要记录：kind、请求摘要（登录号脱敏）、响应 code/sub_code、result（pending/success/fail/unknown）、耗时、时间。
- “当日已发出”= 当日 transfer 尝试中 result ∈ {pending, success, unknown} 的 net 合计。未知也算已占额度，口径偏保守。
- 例：daily_cap=¥50,000，当日已发出 ¥49,800，本单 net ¥300 → 不转账，W9 回 APPROVED，hold_reason=daily_cap，告警财务。
- 例：单子进入 PAYING 后会员 PROMO 因扣回变负 → ③ 命中 member_blocked，W9。
- 验收：模拟转账超时 3 次（进程崩溃重启 3 次）后查询成功 → 支付宝沙箱侧该 out_biz_no 只有 1 笔。

#### BR-WDR-14 细则 · 打款结果判定与只查不重提

- 状态：已确认
- 默认值：来自 规划/02 §5.3：查询时点前 4 次、24 小时转人工、转账不重试。本条补充：2 小时后每 2 小时查询一次；needs_manual 后停止自动查询。判定清单见 BR-WDR-28（待验证）。
- 决策人：负责人
- 依赖平台能力：判定清单与查询状态语义见 BR-WDR-28、BR-WDR-22 ⑤（06 Q-G8 待验证）
- 取代：
  - PRD v2.1 §11.5：「查询每 5 分钟一次持续 24 小时」
- 来源：规划/02 §5.3 硬规则；规划/04 §4.2 W5–W7；规划/01 F-WDR-06；后端功能规划 §2.9 payout-worker 规则 2；PRD v2.1 §11.5、§14.2
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 查询调用本身失败时可以重试：每个查询时点最多 3 次，间隔 10 秒，不计入转账次数。
- “订单不存在”不自动判失败，因为超时的请求可能还在支付宝排队。
- needs_manual 之后：W10 处置页提供【立即查询】按钮，查询结果只存为凭证，不自动迁移状态。R2 每日对账仍覆盖这类单（BR-WDR-23）。
- 例：T=10:00:00 转账超时；10:01 查询为处理中；10:05 查询成功 → W5，在 10:05 这次事务里写分录并通知用户。
- 例：从 T 起 24 小时内每次查询都是“订单不存在” → 次日 10:00 置 needs_manual=true，转 BR-WDR-15，不再自动查询。

#### BR-WDR-15 细则 · 24 小时未知人工处置

- 状态：默认假设
- 默认值：双人 = super + finance、凭证必传，来自后端功能规划 §3.3。本条新增：判失败需两天账单都为空；判失败后冻结 7 天；上传人须是确认人之一。
- 决策人：财务
- 依赖平台能力：支付宝账单下载接口可按日取得含 out_biz_no 的明细（BR-WDR-22 ⑧，06 Q-G8/Q-C20 待验证）
- 取代：无
- 来源：后端功能规划 §3.3；规划/04 §4.2 W7；规划/02 §5.3、§8.5
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 判 FAILED 后冻结 7 天的原因：余额退回后，用户如果马上重提，而支付宝那笔又迟到成功，就会重复出款。这 7 天内，每日 R2 继续核对该 out_biz_no。
- 7 天内 R2 发现迟到成功：按 BR-WDR-23 生成差错单，追加不会自动到期的 recon_diff 冻结；经调账（ADMIN_ADJUST，双人复核）从该用户账户扣回，余额可能为负（BR-FUND）。manual_failed_watch 到期后自动失效，并记审计。
- 例：T=10-12 10:00 转账超时，10-13 10:00 仍未知 → needs_manual。10-13 下午 R2 下载 10-12 账单，发现该 out_biz_no 成功 → 财务甲上传账单行并确认，super 乙确认 → PAID_API。
- 处置期间，用户侧显示“打款中”，副文案为“到账有延迟，我们正在核实”（BR-WDR-25）。

#### BR-WDR-16 细则 · 手动成功（线下打款）

- 状态：默认假设
- 默认值：只能从 APPROVED 进入。理由：从 PAYING 进入，可能与已发出但未确认的接口转账重复出款；从 PENDING_REVIEW 进入，会绕过审核与职责分离。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - 规划/04 §4.2 W8：「APPROVED / PAYING（人工确认未打出）→ PAID_MANUAL」
  - 后端功能规划 §2.9、§3.3：「手动成功只允许从 PENDING_REVIEW 进入」
  - PRD v2.1 §11.5：「PENDING_REVIEW 或 PAYING（人工确认未出款）→ SUCCESS_MANUAL」
- 来源：规划/04 §4.2 W8；规划/01 F-WDR-05、F-ADM-07；后端功能规划 §2.9、§3.3；PRD v2.1 §11.5；开发任务拆解 BF-09
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：支付宝接口场景未开通期间，财务线下转账 ¥98.00（net_fen=9800），录入流水号 2026101222001… → 甲录入、乙确认 → PAID_MANUAL。若录入金额为 ¥100.00，与 9800 不等 → 拒绝。
- 例：某单执行后，转账返回付款方余额不足，经 W9 回到 APPROVED（尝试记录 result=fail，属于付款方侧码）→ 允许手动成功。这种情况只会在 BR-WDR-28 验证后、付款方侧码清单不为空时出现。若该单曾超时（result=unknown）→ 不允许手动成功，只能走 BR-WDR-15。
- R2 按流水号核对手动成功单。

#### BR-WDR-17 细则 · 开关、权限与付款方异常

- 状态：默认假设
- 默认值：开关语义沿用 规划/04 §10.2。finance 可直接切换的开关限定为三项；withdraw.account_enabled.\* 与 payer_side_after_transfer 的处理为本条新定。
- 决策人：负责人
- 依赖平台能力：付款方侧失败码（BR-WDR-22 ⑤、BR-WDR-28）
- 取代：
  - 规划/04 §11 紧急开关行：「finance 可改 payout.\*、withdraw.\*（收窄为三个开关，其余阈值须 super 生效）」
- 来源：规划/04 §10.2、§11；规划/02 §14；后端功能规划 §2.9 payout-worker 规则 7
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 例：批次 20 单执行到第 8 单时返回付款方余额不足（假设该码已按 BR-WDR-28 验证并列入清单）→ 第 8 单 W9，hold_reason=payer_side_after_transfer；第 9–20 单在复核时看到 queue_paused，也走 W9（hold_reason=queue_paused）；第 1–7 单已发出，照常查询。财务充值后解除暂停：第 9–20 单没有转账记录，可以重新执行；第 8 单只能手动成功或驳回。
- 付款方侧码验证之前，余额不足类返回按未知处理，并由 BR-WDR-28 的“未识别业务码暂停队列”规则停住后续转账。
- 允许 finance 置位 queue_paused，因为置位是停止出款、属于安全方向；解除也需要 step-up。
- 用户侧：回到 APPROVED 的单仍按 APPROVED 显示（标题见 BR-TEXT-06，副文案见 BR-WDR-25），不单独告知用户平台余额不足。

#### BR-WDR-18 细则 · 垫资水位与打款限额

- 状态：默认假设
- 默认值：单笔上限 ¥5,000（规划/06 Q-B3）；通道日限额验证前 daily_cap = ¥50,000。本条新增：W 过期阈值 2 小时、可用比例 90%、在途扣减口径、水位只在 EXECUTE 检查。
- 决策人：财务
- 依赖平台能力：支付宝企业账户余额查询接口与单日转账限额（BR-WDR-22 ②⑦，06 Q-G8、Q-C20 待验证）
- 取代：无
- 来源：规划/02 §5.3、§8.5、§14；规划/06 Q-B3；后端功能规划 §2.9 payout-worker 规则 4
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 公式：P = round_half_up(Σ_{d=−7..−1} apply_amount_d / 7) × 3。
- ③ 把全部 PAYING 单都算作尚未扣款（其中有些可能已在 t_W 前扣款），会重复扣减，结果偏保守。PAID_MANUAL 计入 ③ 的前提是线下打款也从同一个企业支付宝账户付出，需财务确认。
- 例：近 7 日申请合计 ¥49,000 → 日均 ¥7,000 → P=¥21,000。W=¥30,000 &lt; 1.5P=¥31,500 → 告警；W=¥20,000 &lt; P → 拒绝执行新批次。
- 例：W=¥40,000，P=¥21,000，当前 PAYING 合计 ¥8,000，t_W 后已到账 ¥2,000，本批 ¥27,000 → 37,000 > 36,000（W 的 90%）→ 整批拒绝，提示拆分批次。
- 例：W 于 09:00 取数，11:30 执行批次 → 数据已过去 2.5 小时，拒绝执行。
- 通道日限额未知期间，daily_cap 默认 ¥50,000（内测 ≤500 人，按 B=¥20,000 的 2.5 倍取整）。

#### BR-WDR-19 细则 · 提现手续费

- 状态：默认假设
- 默认值：手续费 0（规划/06 Q-B3、规划/01 F-WDR-08）
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD v2.1 §11.6：「specs/fee-rules.csv 全矩阵手续费规则（MVP 即启用）」
- 来源：规划/01 F-WDR-08；规划/06 Q-B3；后端功能规划 §2.9 费率表；PRD v2.1 §11.6
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例（假设以后给 PROMO 配置比例 100bp，即 1%）：amount ¥123 → fee = round_half_up(12300×100/10000) = 123 分；税为 0 时 net = 12177 分。
- 只要求 net_fen ≥ 1 分，否则返回 30303 reason=net_too_small。
- “活跃”的定义（近 30 天有有效订单）和全矩阵放到 P1。

#### BR-WDR-20 细则 · 税额计算与年度台账

- 状态：待决策
- 默认值：SELF_REBATE：method=none，等税务师意见 06 Q-F6。SERVICE_FEE：按 D12（平台自建累计预扣）用 cumulative，税目与税率表由财务在 M-内测 前依据税务师意见书面给出。在给出之前，`withdraw.account_enabled.PROMO` 默认 off；负责人书面接受 method=none 的风险后才可开启。无论哪种情况，所得类型、tax_ytd、TAX_WITHHOLD 分录都要全部建好。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 后端功能规划 §2.9 创建：「PROMO 按 2025 年第 16 号公告累计预扣、INCIDENTAL 按 20%（作为默认写死的说法；改为配置，外部法规待核实）」
  - PRD v2.1 §11.8：「若由灵工平台代报，推广收益提现须在灵工通道上线后才开放（D12 方案 A 已定 MVP 走企业支付宝）」
- 来源：规划/00 §3.2 D12；规划/01 F-SET-07；规划/04 §2.4；后端功能规划 §2.9 创建、税务落点；PRD v2.1 §11.8；开发任务拆解 BF-12；规划/06 Q-F6
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 在途 = 同一用户、同一计税年度、同类所得、状态 ∈ {PENDING_REVIEW, APPROVED, PAYING} 的单。
- 计税年度用 created_at：保证计算与台账落在同一年度。例如 12 月申请、次年 1 月到账的单，计算和入账都记在申请那一年。涉税导出（BR-WDR-21）仍按 paid_at 分季度。如果税务师要求按支付年度计算，改为统一按 paid_at，并在跨年到账时重算。
- 例（假设 SERVICE_FEE 配为 flat_rate 2000bp，即 20%）：申请 ¥100 → tax 2000 分，net 8000 分；到账后 tax_ytd.cum_income +10000、cum_withheld +2000。
- 例（method=none）：tax_fen=0，但 tax_ytd 照常累加收入，保证日后补算有底数。
- 在途单失败导致后续单多扣时，累计方法会在下一次提现自动冲回（本次税额可以为 0）；年度差额由用户汇算，不单独退税。
- 税务口径依赖税务师书面意见 06 Q-F6：自购返利是否属于应税所得、服务费适用什么税目。“2025 年第 16 号公告”等外部法规引用待核实。

#### BR-WDR-21 细则 · 涉税导出与报送

- 状态：默认假设
- 默认值：季度导出字段如上；只有 finance 可导出全量（与 规划/04 §11“敏感字段全量查看仅 finance”一致）；报送时限待税务师确认
- 决策人：财务
- 依赖平台能力：无
- 取代：无
- 来源：规划/01 F-SET-07；规划/04 §11；后端功能规划 §2.9 税务落点；PRD v2.1 §11.8；规划/06 Q-F6
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：Q4 导出范围 = paid_at ∈ [2026-10-01T00:00+08:00, 2027-01-01T00:00+08:00) 的 PAID_API / PAID_MANUAL 单。
- 用户注销后，涉税记录在去标识之前须保留（规划/01 数据保留，期限由财务确认）。

#### BR-WDR-22 细则 · 支付宝通道能力待验证

- 状态：待验证
- 默认值：验证完成前：转账必传收款人姓名；BR-WDR-28 三份清单为空（只把查询成功状态映射为 success）；未识别业务码按结果未知处理并暂停队列；single_cap_fen=500000 分（¥5,000）；daily_cap_fen=5000000 分（¥50,000）；禁止任何形式的重复提交（含同一 out_biz_no）；企业账户余额 W 由财务手工录入；SELF、PROMO 业务场景按「佣金报酬」申请。
- 决策人：财务
- 依赖平台能力：支付宝 06 Q-G8/Q-C20：场景开通、限额、姓名校验、同一 out_biz_no 重提语义、失败码与查询状态、余额查询、账单下载、沙箱支持
- 取代：
  - 参考_花卷云查漏底稿 §7：「普通转账单笔最高 5000 元（外部限额，未验证）」
  - 后端功能规划 §2.9 payout-worker 规则 6：「必传收款人姓名，由支付宝做姓名校验（写成事实，改为待验证）」
  - 规划/09 CAP-X-06 降级列：「姓名不符：显示“收款人姓名与实名不一致，请修改收款账号”，余额已退回（30307）」
- 来源：规划/06 Q-B3、Q-C20、Q-G8；规划/09 CAP-X-06、§5.2；后端功能规划 §2.9 规则 1、6；PRD v2.1 §11.6；参考_花卷云查漏底稿 §7
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 验证完成前的默认：转账必传收款人姓名；BR-WDR-28 的三份清单为空（只把查询成功状态映射为成功）；转账同步返回未识别的业务码时，按结果未知处理并暂停队列；单笔上限 ¥5,000；daily_cap ¥50,000；④ 未验证前禁止任何形式的重复提交（包括同一 out_biz_no）；W 由财务手工录入。
- 验证产出：每一项留一份接口请求/响应样例，存到 规划/09 CAP-X-06 的证据路径；清单写入配置后，需负责人确认。
- ① 的场景：后端功能规划 §2.9 payout-worker 规则 6 写「推广收益和自购返利走佣金报酬，活动奖励走现金营销」。活动奖励（INCIDENTAL）为 P1；「现金营销」场景是否需要单独签约、能否与「佣金报酬」并存，随 ① 一并验证，结果写入 `payout.biz_scene.<account_type>`，验证前不写成已开通。
- 如果 ④ 验证结果为“同一 out_biz_no 重提幂等”，可以在 P1 评估用“人工触发同号重提”替代部分人工处置，以及放开 BR-WDR-12 对有 fail 尝试记录的单的执行限制，由负责人决定。
- 如果 ⑤ 发现存在“成功后退回”状态，需另行定义该状态对 PAID_API 单的处理，在此之前不得映射。

#### BR-WDR-23 细则 · 通道对账对提现的影响

- 状态：默认假设
- 默认值：有差异即冻结该会员提现，来自 PRD v2.1 §11.7（规划/02 未写）。本条新定：needs_manual 单不自动迁移、金额按 net_fen 核对。
- 决策人：财务
- 依赖平台能力：支付宝按日账单下载（BR-WDR-22 ⑧）
- 取代：无
- 来源：规划/02 §8.5；规划/05 §3.3 B2-07；PRD v2.1 §11.7
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- “内部 PAID_\*、支付宝无记录”：paid_at 靠近日界时，要 paid_at 当日和次日两份账单都没有记录，才算差异。
- 例：out_biz_no W2026… 内部为 FAILED，已退回 ¥100，支付宝账单显示成功 ¥100 → 有重复出款风险：生成差错单，冻结该会员提现（recon_diff）。财务发起 ADMIN_ADJUST −¥100，复核人确认；余额可以为负，按负余额规则处理。
- 例：内部 PAYING（needs_manual=false），账单显示成功，即时查询仍为“处理中” → 置 needs_manual=true，生成差错单，由 W10 凭账单行处置。
- 验收：注入 1 笔重复打款和 1 笔漏单，次日对账全部发现（B2-07）。

#### BR-WDR-24 细则 · 提现打款告警

- 状态：默认假设
- 默认值：比例告警按自然日统计、分母 ≥20、只统计 W5/W6，为本条新增，用于避免小样本误报
- 决策人：代理可自定
- 依赖平台能力：无
- 取代：无
- 来源：规划/02 §13、§8.5；后端功能规划 §2.9 规则 2、7
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：当日 30 笔 W5/W6 迁移中有 1 笔 W6，失败率 3.3% > 2%，分母 30 ≥20 → 告警。当日 10 笔中 1 笔 W6 → 分母不足，不按比例告警；但如果连续 3 次 W6，仍然告警。
- 告警通道与去重窗口（同类告警 30 分钟内合并）见可观测规范。

#### BR-WDR-25 细则 · 用户侧状态文案

- 状态：待决策（由默认假设改为待决策：“到账 / 入账”用词属 §14.3 C-02，需负责人拍板）
- 默认值：状态标题随 BR-TEXT-06、术语随 BR-TEXT-01（C-02 默认方案 A），本条不写；PENDING_REVIEW、APPROVED、PAYING 的副文案分支为本条新定，REJECTED、FAILED 副文案的原因与退回金额要素沿用 规划/01 F-WDR-09。C-02 改选方案 B 时只改 BR-TEXT-01、06 与 /v1/dict 字典，本条分支条件不变。
- 决策人：负责人（原为运营；用词属 C-02，由负责人拍板）
- 依赖平台能力：无
- 取代：
  - 本条旧版：「PAID_API / PAID_MANUAL 显示“已到账支付宝”；FAILED 显示“打款失败”；经 W6 失败的单均附【修改收款账号】」
  - 规划/04 §2.4：「FAILED 用户文案“打款失败”」
- 来源：规划/01 F-WDR-09、J6；规划/04 §2.4；后端功能规划 §2.9 用户侧状态
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

下表只规定每种分支用哪条副文案及其要素；状态标题由 withdrawal_status 按 BR-TEXT-06 映射，本表不列；最终措辞以 /v1/dict 字典为准。

| 分支条件（内部状态） | 副文案 |
|---|---|
| PENDING_REVIEW 且 now &lt; review_deadline | 预计 {review_deadline} 前完成审核 |
| PENDING_REVIEW 且 now ≥ review_deadline | 审核时间较长，我们正在处理，结果会通知你 |
| APPROVED（含 W9 退回） | 处理中，结果会通知你 |
| PAYING（&lt; T+2h） | 支付宝处理中，到账后会通知你 |
| PAYING（≥ T+2h 或 needs_manual） | 到账有延迟，我们正在核实，结果会通知你 |
| PAID_API / PAID_MANUAL | 按 BR-TEXT-06（两种状态分句，不带 {paid_at}；到账时间在记录行按 BR-TEXT-11 显示） |
| REJECTED | {原因文案}；¥{amount} 已退回可提现余额 |
| FAILED（W6，账号类失败码） | {失败原因}；¥{amount} 已退回可提现余额，可修改收款账号后重新提现 |
| FAILED（W6，其他失败码） | {失败原因}；¥{amount} 已退回可提现余额 |
| FAILED（W10） | 支付宝未完成转账；¥{amount} 已退回可提现余额，核实期间 {hold_days} 天内暂不可提现 |

- 在支付宝处理时长实测之前，不写“几分钟内到账”这类时效承诺。
- 账号类失败码的清单随 BR-WDR-28 的 definite_fail_codes 验证结果确定（BR-TEXT-08 维护码到文案的映射）；验证前 definite_fail_codes 为空，不会出现 W6，上表两行 W6 只在验证后生效。
- 客服话术的状态标题按 BR-TEXT-06、副文案按上表；客服后台可以看到内部状态。
- 文案经 `/v1/dict` 下发，客户端按版本缓存。
- 按 C-02 默认处理，待负责人确认。

#### BR-WDR-26 细则 · 审核时效与结果通知

- 状态：默认假设
- 默认值：工作日 24 小时（规划/06 Q-B3）。计时口径、超时状态集合 {PENDING_REVIEW, APPROVED}、检查间隔 5 分钟、每单只通知 1 次、免打扰时段内顺延到时段结束（时段按 notify.quiet_hours，见 BR-WATCH-15，当前默认 [22:00, 08:00)）且发送前复查为本条新定；超时推送用户对应 规划/01 J6 第 4 点。
- 决策人：运营
- 依赖平台能力：无
- 取代：
  - 本条旧版：「超时推送文案“提现审核排队中，我们会尽快处理，余额已冻结保留”」（与 BR-TEXT-07 重复维护且措辞不同，改为引用 BR-TEXT-07）
  - 本条旧版：「到期仍为 PENDING_REVIEW 时…按 withdrawal_id + ‘review_overdue’ 去重」（与 BR-TEXT-07 旧版的状态集合、幂等键不一致；状态集合改为 {PENDING_REVIEW, APPROVED}，因为 APPROVED 尚未进入 PAYING，审核环节未结束；幂等键统一为 withdrawal_id:OVERDUE，与 10 AC-S2-29 一致）
  - BR-TEXT-07 旧版中的超时触发逻辑（deadline 计算、5 分钟检查、状态集合、幂等键、22:00–08:00 顺延与发送前复查）并入本条，BR-TEXT-07 只保留展示文案与推送模板
  - 本条旧版：「判定时刻在 22:00–08:00（+08:00）的用户通知延至当日或次日 08:00 发送」（时段写死，与 notify.quiet_hours 重复维护；改为引用 BR-WATCH-15 的 notify.quiet_hours）
- 来源：规划/06 Q-B3；规划/01 F-MSG-02、J6、指标表；后端功能规划 §2.9 用户侧状态；08 §12 BR-TEXT-07
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 工作日日历：配置项 workday_calendar（含国务院公布的放假与调休），每年 12 月录入次年；未录入的日期按周一至周五为工作日。
- PAYING 的进度不在本时限内（由支付宝结果决定，见 BR-WDR-14）。
- 例：周五 20:00 提交 → 周五剩 4 小时，再加周一 20 小时 → deadline 为周一 20:00；20:05 前判定仍 PENDING_REVIEW 或 APPROVED → 告警财务并通知用户 1 次。
- 例：周三 10:00 提交 → deadline 周四 10:00。
- 例：国庆假期 10-03 提交 → 从第一个工作日 00:00 起算 24 小时。
- 例：周六 15:00 提交（非工作日从下一个工作日 00:00 起计）→ deadline 周二 00:00 → 判定在 00:00–00:05 → 财务告警即时发出，用户通知延至周二 08:00；若周二 07:30 已进入 PAYING → 用户通知不发。
- 例：周三 10:00 提交，周四 09:50 审核通过（APPROVED），到 10:05 判定时仍未执行（未进入 PAYING）→ 按超时处理，告警并通知 1 次；之后该单经 W9 退回 APPROVED 也不再通知。
- 指标：工作日 24 小时处理率 ≥95%（规划/01）。
- 审核超时不会自动通过，也不会自动驳回。

#### BR-WDR-27 细则 · MVP 不做的提现能力

- 状态：已确认
- 默认值：—
- 决策人：负责人
- 依赖平台能力：无
- 取代：无
- 来源：规划/00 §3.2 D10、§4；规划/01 F-WDR-10；后端功能规划 §2.9 通道；PRD v2.1 §2、§14.4；参考_花卷云查漏底稿 §7

- MVP 所有提现都人工审核（D10）。上述预警指标在 MVP 只以 risk_flags 的形式提示审核人（BR-WDR-10、BR-WDR-29），不自动决策。规则一览原写法把三项指标整体列为“不实现”，与本句不一致，已改为“自动决策不实现、打标实现”。
- 例：配置项 `withdraw.auto_payout.enabled` 存在但为 false，接口拒绝把它设为 true（P1 之前不能开启）。

#### BR-WDR-28 细则 · 打款结果判定清单

- 状态：待验证
- 默认值：验证前三份清单为空，只有查询成功状态映射为 success；遇到未识别的业务码即暂停队列（本条新增）
- 决策人：负责人
- 依赖平台能力：支付宝失败码、付款方侧码、查询状态语义（BR-WDR-22 ⑤，06 Q-G8 待验证）
- 取代：
  - 规划/02 §5.3 时序图：「明确失败（姓名不符、账号不存在等）→ FAILED（改为：只有码在已验证清单内才判失败）」
- 来源：规划/02 §5.3；规划/09 CAP-X-06；后端功能规划 §2.9 payout-worker 规则 2、6
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 验证前遇到未识别业务码就暂停队列，原因：余额不足一类的码在识别之前，后续的单会一个接一个同样失败，并全部在 24 小时后落入人工处置。暂停后，尚未发出转账的单在复核时走 W9（queue_paused），没有转账记录，恢复后可以重新执行。代价是某个收款人自身的错误（例如账号不存在）也会暂停整个队列，内测规模下可以接受。
- 例（验证前）：T=10:00 转账同步返回“收款人姓名不符”一类的码 → 保持 PAYING，按 BR-WDR-14 查询；queue_paused=true 并告警；24 小时仍未知 → needs_manual，按 BR-WDR-15 处置。
- 例（假设 BR-WDR-22 验证后已把该码列入 definite_fail_codes）：同样的返回 → W6，写 WITHDRAW_RETURN，推送 + 短信“打款未成功：收款账号实名与你的实名不一致，¥x 已退回”（措辞以 BR-TEXT-06、BR-TEXT-08 为准），不暂停队列。
- 例：查询返回 SUCCESS → W5；查询返回 FAIL（验证前映射为 unknown）→ 继续按节奏查询。

#### BR-WDR-29 细则 · 审核风险标签与提现预警指标

- 状态：默认假设
- 默认值：三项提现预警指标在 MVP 计算并打标、不自动决策（与 BR-WDR-27 一致，后端功能规划 §2.12「全人工期间只打标」）。③ 的口径与阈值以 BR-ID-37 为准（默认第 3 个账号起打标）；④ 的 30% 且 ≥3 单沿用 规划/01 F-RISK-03；⑤ 的 5000bp / 5000bp / 最少 5 单、⑥ 的 10000bp 为本条新定（花卷云只给出“超 X%”，未给值），理由：只作提示，偏宽松以减少审核噪音，内测后按命中率调整。
- 决策人：财务
- 依赖平台能力：无（⑤ 只用订单同步已有的预估佣金与计佣金额，不依赖单独的佣金率字段）
- 取代：
  - BR-WDR-27 旧版规则一览：「三项提现预警指标 MVP 不实现」（改为自动决策不实现、打标实现）
  - BR-WDR-10 旧版：「近 60 天维权失效占比高」等标签只列名称、未定义窗口与阈值
  - 本条旧版 ③：「本次请求的 device_id 在 30 天窗口内登录过的不同 user_id 数（含本人）≥ risk.withdraw.same_device_accounts（默认 3）」（与 BR-ID-37 的键 device_hash、720 小时窗口、只标第 3 个起的账号、配置 risk.device_login_accounts_limit 均不一致；旧写法会把同设备前 2 个账号也打标。改为引用 BR-ID-37，删除 risk.withdraw.same_device_accounts；分歧登记 14 §14.3）
- 来源：参考_花卷云查漏底稿 §7 提现预警、§16 #19；后端功能规划 §2.12 风控（同设备多账号、恶意维权、提现预警）、§2.6 会员口径（首提、当日入账）；规划/01 F-RISK-03；08 §10 BR-ID-31
- 需同步修改的规划文档：2 处（规划/04 §3.2 withdrawals 增加 risk_flags_at 并定义 risk_flags 结构；规划/01 F-RISK-03 补三项预警指标，引用本条），未同步，登记于 README §0.6

- 边界：比较一律用“>”（④⑤⑥）或“≥”（⑤ 的单笔佣金率与最少单数），按上表；③ 的边界按 BR-ID-37；恰好 3000bp 不命中 ④。
- 例（③，口径见 BR-ID-37）：同一 device_hash 在 720 小时内先后登录 A、B、C 三个账号 → A、B 申请提现不打 same_device_multi_account，C 申请时打标。
- 口径：④⑤ 只看自购单（buy_type=self），因为维权与高佣自买由购买者本人造成；⑥ 的分母含自购、分享、直推三类受益份额，因为提现额来自两个账户合计。
- 快照：risk_flags 是申请时刻的快照，审核人看到的值不随之后的订单变化而变；审核详情页可提供【重新计算】按钮（代理可自定），结果另存，不覆盖快照。
- 例：t=2026-10-12 10:00 申请 ¥300。近 60 天自购子订单 10 单，其中 4 单 VOID → 4000bp > 3000bp 且 4 ≥ 3 → invalid_ratio_60d。近 30 天提现（含本单）¥500，近 60 天确认收货的返利份额 ¥320 → 500×10000/320=15625bp > 10000bp → withdraw_vs_received。
- 例：近 60 天自购子订单 4 单且全部佣金率 ≥50% → 分母 4 &lt; 5，不计 ⑤。
- 例：会员首次申请 ¥10，余额来自 70 天前确认收货、已入账的订单，近 60 天没有确认收货订单（分母 0）→ 同时打 first_withdrawal 与 withdraw_vs_received。
- 阈值修改按 BR-WDR-17 的阈值流程：finance 提议、super step-up 后生效，并记审计。

### 7.3 本主题未决问题

1. 每人每日 1 次按 SELF+PROMO 两账户合计计数（BR-WDR-04 默认），这意味着同一天不能分别提两个账户；是否改为按账户分别计数，需财务确认。
2. （已由 BR-ID-27 规定，本条仅留指引）注销申请时存在 PENDING_REVIEW / APPROVED / PAYING 提现单 → 拒绝注销并返回 30412；因封禁被人工冻结的提现不适用 30412，由财务在冷静期内处理到终态。BR-ID-27 为默认假设，改动走 00 变更流程。
3. MVP 是否允许用户自行撤销“审核中”的提现（BR-WDR-10 默认不允许，经客服由财务驳回）。
4. 税务师书面意见（规划/06 Q-F6）到位前，三类所得的计税方法与税率、涉税报送时限都无法定稿（BR-WDR-20、21）。
5. 内测期推广收益是否代扣个税：默认 withdraw.account_enabled.PROMO=off，直到财务给出税目与税率表，或负责人书面接受 method=none 的风险（BR-WDR-20）。
6. 支付宝通道 8 项能力（BR-WDR-22）尚未实测，尤其是同一 out_biz_no 重提的语义与明确失败码清单；验证结果决定 BR-WDR-14/15/17/28 能否放宽人工处置。
7. 如果验证结果是支付宝不校验收款人姓名：是在绑定环节加支付宝侧实名核验，还是调低首次提现上限（负责人，BR-WDR-02）。
8. 第二人批准人可以是审核人、W8 确认人可以是审核人，这是为了让两人团队能运转；团队 ≥3 人后是否要求更多不同的人（财务，BR-WDR-11）。
9. 支付宝账单显示成功、而内部是经 W9 退回的 APPROVED 单（付款方侧码误判）时，没有对应的状态迁移路径（APPROVED → PAID_API）。目前只生成差错单并冻结会员；付款方侧码清单验证前不会出现这种情况，验证后需补定义（BR-WDR-23）。
10. PRD v2.1 §14.4“奖励类首单确认收货后才可提现”随活动奖励放到 P1，P1 设计时需重新定义。
11. 受 §14.3 跨主题分歧影响、已按「建议」列默认处理的条目：C-02（BR-WDR-25，负责人）、C-03（BR-WDR-03、08，负责人）、C-08（BR-WDR-05、08、10，财务）、C-09（BR-WDR-03、05，财务）、C-15（BR-WDR-06，法务；满周岁口径默认取 BR-ID-26 的生日次日 00:00）、C-28（BR-WDR-03、05，负责人）、C-01（BR-WDR-04 细则的状态名，负责人）。裁决结果与默认不同时，按条目中的「按 C-xx 默认处理」标注逐处回改。
12. BR-WDR-29 的 ⑤⑥ 阈值为新定默认值，内测一个月后由财务按命中率与实际驳回率复核。

---
