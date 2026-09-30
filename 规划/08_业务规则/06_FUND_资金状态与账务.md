# 08 业务规则 · 6. 资金状态与账务（BR-FUND）

返回 [README](README.md)（使用规则、术语表、规则索引）

## 6. 资金状态与账务（BR-FUND）

本节规定：返利状态流转、入账时点与凭证、扣回与补差、负余额、两账户、流水类型、不变量、月末核对与垫资。共 23 条（已确认 3、默认假设 8、待决策 10、待验证 2）。

本节按 §14.3 的建议（默认处理）改写了 C-01、C-02、C-03、C-06、C-07、C-08、C-09 涉及的条目，C-16、C-17 的默认处理与本节原写法一致；各条细则末尾注明所按的分歧编号与决策人，裁决前按默认处理实现。

### 6.1 规则一览

| 编号 | 规则 | 状态 | 影响面 |
| --- | --- | --- | --- |
| BR-FUND-01 | **订单双状态模型**<br>每个子订单必须维护两个互相独立的状态字段：`platform_status`（平台订单状态，唯一写者 order-sync，只由联盟数据经平台状态映射表驱动，见 BR-FUND-02）与 `rebate_status`（返利状态，唯一写者 settlement）。`hold`、`rights_pending` 的唯一写者也是 settlement：hold 只经后台 hold/unhold 接口或风控引擎调用 R11 迁移；order_rights 只经 settlement 提供的命令写入（order-sync、rights-imports 调用该命令），rights_pending 在 order_rights 写入或变更的同一事务内重算（存在 status ∈ {PROCESSING, WAIT_COMMISSION} 的记录即为 true）。两个状态都只能经 specs/state-machines/\*.yaml 生成的 transition() 以 CAS（UPDATE … WHERE id=:id AND status=:from，row_version+1）迁移；影响 0 行视为并发冲突或非法迁移，重读后按迁移表判断。表外事件：状态与余额均不变；内部调用抛 IllegalTransition，不重试，记日志并告警；后台 API 返回 20902「订单状态已变化，请刷新后重试」（data.resource=order）。订单相关的余额与分录只能在该子订单 rebate_status 迁移（含状态不变的自迁移 R5a、R7、R9、R9b、R10、R14）的同一 PG 事务内变更，不得依赖 outbox 事件完成；提现、坏账核销、人工调账、联盟回款不伴随订单迁移，分别按 BR-WDR-09（账户约束 BR-FUND-14）、BR-FUND-12、BR-FUND-16、BR-FUND-20。用户可见订单状态 display_status 由 (platform_status, rebate_status, hold, rights_pending, 金额) 派生，不入库（BR-FUND-17）。同一子订单的所有处理按 order_key（`{platform}:{sub_order_id}`，BR-FUND-05）用 pg_advisory_xact_lock 串行。 | 待决策 | orders.status 拆为 orders.platform_status、orders.rebate_status、orders.hold、orders.rights_pending；orders.locked、row_version；order_status_history 增加 field 列（platform/rebate）；specs/state-machines/order-platform.yaml、order-rebate.yaml；测试 ID SM-ORD-O&lt;n> → SM-PLT-P&lt;n>、SM-REB-R&lt;n>；order_rights 写入命令（settlement 提供）；错误码 20902（data.resource=order）；GET /v1/orders、GET /v1/orders/{id} 的 status 字段改为派生 display_status；后台订单列表筛选；三端订单页状态展示 |
| BR-FUND-02 | **平台状态映射与可入账事件**<br>platform_status 只能由 specs/order-status-map/&lt;platform>.csv 把平台状态码映射为内部事件后按 BR-FUND-01 的 P 表迁移；映射表之外的状态码必须告警并写入待处理表，不得丢弃、不得猜测。可入账事件由 specs/creditable-events.yaml 定义：taobao、jd、pdd = 确认收货；meituan = 订单完成或核销；P1 平台 vip、douyin = 确认收货，eleme = 订单完成或核销（P1 平台接入时按 规划/09 实测结果确认后才写入该文件，未写入的平台订单不进入 WAITING）。平台返回的无时区时间一律按 +08:00 解析。乱序与去重按 BR-ATTR-01（attr.mtime_ordering.&lt;platform>，默认 false 时只看 content_hash）。received_at 必须取平台返回的收货/完成时间，不得用我方同步时间代替；平台只给出「已结算」而未给出收货时，视为已收货，received_at 取平台结算时间字段，按 P5 迁移到 SETTLED。received_at 一旦写入不再覆盖（包括之后回传的真实收货时间），credit_due_at 不重算；后到的真实收货时间另存 orders.platform_received_at 备查。平台未返回可用时间字段时订单进待处理表，不进入 WAITING。订单接口回传的结算佣金写入 order_settlements（source=API，BR-FUND-09）。 | 待验证 | specs/order-status-map/&lt;platform>.csv；specs/creditable-events.yaml；orders.received_at、platform_received_at、platform_modified_at、settled_at；order_settlements；order_sync 待处理表；规划/09 平台能力验证表；验收用例：确认收货与结算乱序回放、更新时间相等内容不同回放 |
| BR-FUND-03 | **预估返利生成与变更**<br>订单已归因到用户且 platform_status ∈ {PAID, RECEIVED, SETTLED} 时，每个受益人的预估返利（分）= 按该订单唯一一份分佣快照（生成时点按 BR-CALC-10：已归因且 platform_status 首次 ∈ {PAID, RECEIVED, SETTLED} 的同一事务内生成，DEPOSIT_PAID 阶段不生成；等级与上级取 paid_at 时刻，按 BR-CALC-12；生成后不再改）的比例拆分当前基数 B_est 所得份额（拆分与舍入规则见 BR-CALC）；platform_status=DEPOSIT_PAID 或 rebate_status=UNATTRIBUTED 时预估计为 0 且不向用户展示金额。ESTIMATED 与 WAITING 阶段不得写任何分录、不得改变 account_balances。联盟回传的佣金或数量（部分退款、价保、比价降佣）变化时，在订单 upsert 的同一事务内更新 est_commission_fen、refunded_quantity，commission_version+1，预估随之重算。首次入库 B_est=0 的已归因订单为 ESTIMATED，展示「本单无返利」；B_est 由 >0 变为 0 按 BR-FUND-07 处理。 | 默认假设 | orders.est_commission_fen、refunded_quantity、commission_version；commission_splits（生成时点见 BR-CALC-10）；GET /v1/orders 预估金额字段；推送见 BR-TEXT-09；订单页 |
| BR-FUND-04 | **入账时点与入账任务**<br>rebate_status 由 ESTIMATED 进入 WAITING 时必须写 credit_due_at = received_at + wait_days × 24 小时（wait_days 读配置 settle.wait_days.&lt;platform>，默认 15；修改只影响此后进入 WAITING 的订单）。入账任务 settle.credit 每日运行一次，名义时刻 run_at = 当日 00:05:00.000 +08:00（时间一律读注入的 Clock；补跑或重跑仍取该日 run_at，不用实际启动时刻），只处理同时满足以下条件的子订单：rebate_status=WAITING；credit_due_at ≤ run_at；hold=false；rights_pending=false；子订单入账基数（按 BR-FUND-05 取法）≥ settle.daily_min_fen（默认 0 分，即不设门槛），或 settle_commission_fen 已记录；orders.credit_requires_settle=true 且 settle_commission_fen 为空 → 跳过（BR-CALC-15、BR-CALC-25），与门槛分支同样显示 WAITING_SETTLE、不给预计日期（C-27 (e)，默认处理，待财务确认）。**入账开关**：平台开关 credit.enabled.&lt;platform>（BR-CALC-03，默认 off；读取时点与缓存同 settle.auto.enabled）为 off 时，入账任务跳过该平台全部子订单（含 R5a），其余平台照常；R4 照常进 WAITING 并写 credit_due_at；该平台 WAITING 订单 expected_credit_date 返回 null，display_status=CREDITING（BR-FUND-17，「入账核对中」，不显示日期），该平台商品详情与 display_status ∈ {DEPOSIT_PAID, PAID} 的订单不展示「确认收货满 {wait_days} 天后入账」；扣回、补差、失效不受该开关影响。开关由 off 改为 on 后，下一次任务按 credit_due_at 正常处理积压订单，不另设补跑；expected_credit_date 按下式把「开关最近一次打开时刻」并入 max(…)。**单批上限**：每次任务每个平台最多处理 settle.credit.max_orders_per_run 个子订单（默认 5000，默认处理，待财务确认），按 (credit_due_at, order_key) 升序取；超出部分保持 WAITING、由下一次任务优先处理，并告警财务 1 次。门槛按子订单判断，一单中除 held 受益人外的全部受益人同时入账或同时不入账；held 受益人解除后按 BR-FUND-01 R5a 单独入账。任务在处理每个子订单的事务开始前读取 settle.auto.enabled（缓存 ≤10 秒）：为 off 时立即结束本次任务，已提交的订单保持 CREDITED，未处理的保持 WAITING；开关恢复后不自动补跑，下一次任务照常处理所有 credit_due_at ≤ run_at 的订单；有权限者可在后台 step-up 后手动触发一次补跑。用户侧预计入账日 expected_credit_date（+08:00 日期，YYYY-MM-DD）= 首个 run_at ≥ max(credit_due_at, received_synced_at, 最近一次维权关闭或 hold 解除时刻, 该平台 credit.enabled 最近一次由 off 改为 on 的时刻) 的入账任务所在日期，其中 received_synced_at = 本系统写入 rebate_status=WAITING 的事务时刻（取注入的 Clock）；即通常为 credit_due_at 的日期部分，时间部分 > 00:05:00.000 时再加 1 天；维权中或 hold 期间、该平台 credit.enabled=off 期间返回 null（显示售后中 / 核对中，不给日期），解除或开关打开后按上式重算（G-16，默认处理，待负责人确认）。本条是 expected_credit_date 计算的唯一维护处，BR-TEXT-04 只维护其展示格式。用户侧只展示「预计 MM-DD 入账」，不得承诺「15 天到账」「15 天入账」；售后或审核暂停时改用 BR-FUND-17 对应文案。 | 待决策 | orders.credit_due_at、orders.received_synced_at、orders.credit_requires_settle；配置 settle.wait_days.&lt;platform>、settle.daily_min_fen、settle.auto.enabled、credit.enabled.&lt;platform>（BR-CALC-03）、settle.credit.max_orders_per_run；任务 settle.credit 调度与 run_at、后台手动补跑；GET /v1/orders/{id} expected_credit_date；订单页、钱包待入账预计日期；商品详情「入账」文案；客服话术「什么时候入账」；验收用例：时钟注入快进 15 天入账、credit_due_at=00:05:03 边界、收货同步晚于 credit_due_at、任务中途关闭开关、credit.enabled=off 跳过与打开后处理积压、单批上限溢出 |
| BR-FUND-05 | **入账金额与入账凭证**<br>定义 order_key = `{platform}:{sub_order_id}`（如 `taobao:1234567`）；所有资金 uniq_key 与 advisory lock 都必须用 order_key，不得单用 sub_order_id。入账基数 B_credit 必须 = orders.settle_commission_fen（若非空，取值规则见 BR-FUND-09），否则 = 入账时刻 orders.est_commission_fen 最新值；按分佣快照比例重新拆分为各受益人份额与平台留存（平台留存 = B_credit − Σ受益人份额，尾差归平台）。每个份额 >0 的受益人写 1 张凭证，uniq_key=`{order_key}:{user_id}:{role}:CREDIT`；平台留存 >0 写 1 张凭证，uniq_key=`{order_key}:PLATFORM:CREDIT`；B_credit=0 时不写凭证，只迁移状态。同一子订单的全部凭证、account_balances 更新、orders.booked_base_fen=B_credit 与 rebate_status→CREDITED 必须在同一 PG 事务内完成；用户账户按 account_id 升序 SELECT … FOR UPDATE。uniq_key 冲突视为已入账，跳过且结果与首次相同。 | 待决策 | ledger_vouchers.uniq_key 唯一索引；ledger_entries；account_balances；orders.booked_base_fen；任务 settle.credit；事件 order.credited；属性测试：同一 (子订单,受益人,角色) 入账 ≤1 次；跨平台同号子订单各自入账；验收用例（AC-SET-nn，编号待 规划/05 分配）：重放入账只入账 1 次 |
| BR-FUND-06 | **维权中与订单暂停**<br>子订单 rights_pending=true（存在 status ∈ {PROCESSING, WAIT_COMMISSION} 的 order_rights 记录）或 hold=true 时，入账任务必须跳过；二者都不改变 rebate_status。hold 只能对 rebate_status ∈ {ESTIMATED, WAITING} 设置：人工由 ops（风控）或 cs（客服）操作，风控引擎可以系统身份（actor=system:risk）自动 hold；unhold 只能由 ops 或 cs 人工执行（不要求与 hold 为同一人），系统不得自动 unhold；hold、unhold 都必须填原因码并写审计日志。CREDITED 之后不得 hold（改用账户提现冻结）。维权结果：失败 → 关闭记录、金额不变；全额成功 → 入账前按 BR-FUND-07、入账后按 BR-FUND-08；部分成功 → 按 BR-FUND-08 的新基数取值顺序确定 B_new（入账前改预估，入账后部分扣回）；联盟新佣金与应扣佣金都没有时，order_rights 置 WAIT_COMMISSION（仍阻止入账），等联盟回传新佣金后按 R7/R9 处理并关闭。无「处理中」信号的平台只在结果回传时处理。 | 待验证 | orders.hold、orders.rights_pending；order_rights 表（来源、类型、金额、应扣佣金、状态 PROCESSING/WAIT_COMMISSION/SUCCEEDED/FAILED、发生时间、平台维权单号、created_at）；后台订单 hold/unhold 操作与审计；风控引擎 system:risk 身份；/admin/v1/rights-imports；订单页展示文案 |
| BR-FUND-07 | **入账前失效与部分退款**<br>rebate_status ∈ {UNATTRIBUTED, ESTIMATED, WAITING} 时收到 PLATFORM_INVALID、全额维权成功、PUNISH、BLACKLIST_HIT，或 B_est 由 >0 更新为 0 而平台未回传失效，必须迁移到 VOID（终态），记 reason_code（REFUND / RIGHTS / PUNISH / BLACKLIST / COMMISSION_ZERO），不写任何分录，事务内写 outbox 事件 order.invalidated。首次入库即 B_est=0 的订单不适用本条（见 BR-FUND-03）。COMMISSION_ZERO 判定只比较 platform_status ≠ DEPOSIT_PAID 时的 B_est：platform_status=DEPOSIT_PAID 期间 B_est 的任何变化（含 >0 变 0 或变为 null）都不触发本条；进入 PAID（P2）时的 B_est 视为 BR-FUND-03 的「首次 B_est」，为 0 时按「本单无返利」处理、不作废。联盟某次回传佣金字段缺失或为空时不覆盖已有 est_commission_fen（保留上次数值），不触发本条；est_commission_fen 只在从未收到数值时为 null，表示「未知」，不视为 0。部分退款、部分维权、价保、比价降佣只更新 refunded_quantity 与 est_commission_fen，状态不变，不写分录。VOID 后平台再回传有效状态不得自动复活，按 BR-FUND-22 处理。 | 默认假设 | orders.rebate_status、reason_code；事件 order.invalidated；推送「订单已失效」；订单页原因码文案 |
| BR-FUND-08 | **入账后扣回**<br>rebate_status=CREDITED 时发生逆向事件（退款、维权成功、处罚、PLATFORM_INVALID、REFUND_AFTER_SETTLE、INVALID_AFTER_SETTLE、B 由 >0 变 0），必须在同一事务内按受益人写 CLAWBACK 凭证。京东实际佣金由 >0 变 0 的口径待 规划/09 验证，验证前按全额扣回处理并生成差错单人工复核。佣金变化（R9b：价保、比价降佣、联盟佣金调整）不属于逆向事件，不写 CLAWBACK，按 BR-FUND-01 R9b 处理（负差即时写负向 SETTLE_ADJUST，正差进 BR-FUND-09 候选）。新基数 B_new 按以下顺序取第一个可用值：①本次事件自带的联盟新佣金（订单同步回传的 est_commission_fen 或 settle_commission_fen，取本次更新的那个）；②order_rights 记录的应扣佣金，B_new = booked_base_fen − 应扣佣金；③都没有 → 不写扣回，order_rights 置 WAIT_COMMISSION，订单进待处理表并告警。整单失效时 B_new=0。受益人扣回金额 = 该受益人在该子订单上的已入账净额（CREDIT + Σ SETTLE_ADJUST − Σ 已有 CLAWBACK）− 按 B_new 和快照重拆的新应得，≤0 不写。平台留存差额 = 平台已入账净额 − 按 B_new 的新留存，可正可负，≠0 就写：正数 借 COMMISSION_REVENUE / 贷 UNION_RECEIVABLE；负数 借 UNION_RECEIVABLE / 贷 COMMISSION_REVENUE。本次全部凭证对 UNION_RECEIVABLE 的净影响必须 = −(booked_base_fen − B_new)，同事务 booked_base_fen=B_new。B_new=0 → CLAWED_BACK（终态），否则保持 CREDITED。uniq_key：受益人 `{order_key}:{user_id}:{role}:CLAWBACK:{rights_event_id}`，平台 `{order_key}:PLATFORM:CLAWBACK:{rights_event_id}`。rights_event_id 取值：来自维权/处罚接口或导入 → `R{order_rights.id}`；来自订单同步的平台状态变化 → `P{platform_status 迁移后的 row_version}`；来自订单同步的佣金变化 → `C{commission_version}`（同一份联盟数据重放时 commission_version 不变，不生成新键）。扣回只从 available 扣，允许 available 变负（BR-FUND-10），不得扣 frozen。 | 待决策 | ledger_type CLAWBACK 与 sub_type；order_rights（WAIT_COMMISSION）；orders.booked_base_fen；事件 order.clawed_back；推送/站内信「返利已扣回」；订单页已扣回详情（金额、原因、关联流水）；验收用例 AC-SET-nn（编号待 规划/05 分配，对应后端功能规划 §10.1 AC-MONEY-004）；属性测试：扣回 ≤ 已入账；UNION_RECEIVABLE 净影响 = −(B_old − B_new) |
| BR-FUND-09 | **月结补差**<br>R1 联盟对账以联盟结算明细（结算报表或接口）为唯一依据。每个子订单的结算记录存 order_settlements(order_key, seq, source ∈ {API, STATEMENT}, settle_commission_fen, settled_at, content_hash)，每收到一条内容不同的记录 seq+1；orders.settle_commission_fen = 最新 STATEMENT 记录的金额，无 STATEMENT 时取最新 API 记录；API 与明细金额不一致时以明细为准并生成差错单。调度任务每日 02:00 检查各平台上一结算周期的明细是否已全部拉取，拉全后的次日运行 R1；finance 可手动触发。补差只针对 rebate_status=CREDITED 的子订单，逐受益人计算 diff = 按当前 settle_commission_fen 与快照重拆的应得份额 − 已入账净额（平台留存同法），按 settle_commission_fen 与 booked_base_fen 的大小分两路：①负差（settle_commission_fen &lt; booked_base_fen）：在写入该 settle_commission_fen 的同一事务内（订单同步回传结算额，或结算明细入库）立即写 SETTLE_ADJUST 凭证（diff≠0 才写），不等审批；②正差（settle_commission_fen > booked_base_fen）：R1 生成补差候选行（记录生成时的 seq）写入 settle_adjust_batches，须由 finance 发起、另一名 finance 或 super（≠发起人）step-up 复核后才写 SETTLE_ADJUST 凭证；写凭证时必须按 orders.settle_commission_fen 当前值与当前净额重算：diff=0 不写；候选行 seq ≠ 该订单当前 seq 时该行作废，不写；③相等：不补差。价保、比价降佣等佣金下调（结算额写入前的 est_commission_fen 变化）不等月结，按 BR-FUND-01 R9b 即时记账。两路 uniq_key 相同：受益人 `{order_key}:{user_id}:{role}:ADJ:{seq}`、平台 `{order_key}:PLATFORM:ADJ:{seq}`，同事务 booked_base_fen=settle_commission_fen。月结不得产生首次入账：结算明细中 WAITING 的子订单只记录结算额、不生成差错单，由 BR-FUND-04 入账任务按结算额入账（含低于日结门槛的订单）；ESTIMATED、VOID、CLAWED_BACK 或我方无订单的，生成差错单。负向补差允许 available 变负。 | 待决策 | order_settlements 表；settle_adjust_batches 表（只含正差）；orders.settle_commission_fen、booked_base_fen；订单同步与明细入库事务内的负差即时补差；/admin/v1/recon R1、正差补差批次发起与复核页；ledger_type SETTLE_ADJUST；差错单类型；订单页「与预估不同时显示差额原因」；验收用例 F-SET-05 重跑月结、结算修正 A→B→A |
| BR-FUND-10 | **负余额规则**<br>只有 CLAWBACK、负向 SETTLE_ADJUST、负向 ADMIN_ADJUST 可以使 USER_\*.available_fen &lt; 0；其他任何写入（含 WITHDRAW_FREEZE、WITHDRAW_FEE、TAX_WITHHOLD）写入前必须校验结果 ≥0，frozen_fen ≥0 由数据库 CHECK 约束保证。available_fen &lt; 0 时该账户提现申请必须返回 30302；后续入账直接计入该账户，自然抵扣负数，不另写抵扣分录；SELF 与 PROMO 两账户不互抵、不自动划转。 | 已确认 | account_balances CHECK (frozen_fen >= 0)；POST /v1/withdrawals 校验、错误码 30302；GET /v1/wallet/summary negative_fen；钱包页待抵扣提示；验收用例 AC-SET-nn（编号待 规划/05 分配，对应后端功能规划 §10.1 AC-MONEY-004） |
| BR-FUND-11 | **负余额跨账户提现限制**<br>用户任一账户（SELF 或 PROMO）available_fen &lt; 0 时，两个账户都不得提现；两账户仍不互抵、不划转资金。申请时的错误码与已有非终态提现单的处理见 BR-WDR-05。 | 待决策 | 见 BR-WDR-05；钱包页提示文案；客服话术 |
| BR-FUND-12 | **负余额坏账核销**<br>账户 available 由 ≥0 变为 &lt;0 时记 negative_since = 当日会计日（00:00 +08:00 日切），回到 ≥0 时清空。每日 R3 后生成负余额报表；当 当前会计日 − negative_since ≥ ledger.bad_debt_days（默认 90）且 \|available_fen\| ≥ ledger.bad_debt_min_fen（默认 0，待财务）时生成核销候选单；同一账户同时最多 1 张 PENDING 候选单，已存在则不再生成。核销不得自动执行：必须由 finance 发起、另一名 finance 或 super（≠发起人）step-up 后批准。批准时重读 available：&lt;0 → 写 BAD_DEBT_WRITEOFF（借 BAD_DEBT / 贷 USER_\*.available，金额 = −当前 available_fen，不用候选单生成时的金额），使 available=0；≥0 → 候选单置 CANCELLED，不写凭证。凭证 uniq_key=`BADDEBT:{account_id}:{candidate_id}`。核销时给同实名、同设备、同收款账号的关联账户打风控标记。 | 待决策 | account_balances.negative_since；负余额报表、核销候选单（后台，PENDING/APPROVED/CANCELLED）；ledger_type BAD_DEBT_WRITEOFF；配置 ledger.bad_debt_days、ledger.bad_debt_min_fen；风控关联标记与申诉；隐私政策风控条款 |
| BR-FUND-13 | **两个账户与余额性质**<br>每个用户注册时必须创建两个账户：SELF（自购返利，科目 USER_SELF:{uid}）与 PROMO（推广收益 = 分享单 + 直推分佣，科目 USER_PROMO:{uid}），各含 available、frozen 两个子户，初始均为 0。入账账户由订单 pid_scene 与受益人角色决定：self_buy/agent/taolijin/fallback 的买家份额 → SELF；share 的分享者份额与直推分佣 → PROMO。用户余额是平台应付佣金，不是储值：不得提供充值、用户间转账、余额消费、两账户互转接口；钱包模块不得出现 transfer、pay_with_balance 类接口。手续费、门槛按账户分别配置（见 BR-WDR）。 | 已确认 | ledger_accounts；account_balances；GET /v1/wallet/summary 按账户返回；钱包页两账户；契约审查：禁止 transfer/pay_with_balance |
| BR-FUND-14 | **冻结与已提现资金变动**<br>本条只规定账户性质约束与不变量；提现各状态何时写分录、写哪些 ledger_type、借贷科目只在 BR-WDR-09 维护，本条不重复。<br>① frozen 子户只用于提现：只有提现分录（BR-WDR-09）可以增减 USER_\*.frozen，其他业务（入账、扣回、调账、坏账核销、风控）不得写 frozen。<br>② 不设 WITHDRAW_IN_TRANSIT：打款中（PAYING）资金留在 frozen，直到提现单进入终态；该科目不创建、任何凭证不得使用；「已提交支付宝、尚未确认」的金额从 status=PAYING 的提现单汇总。<br>③ 风控冻结（risk_state=frozen）与 withdraw_holds 只禁止提现（BR-WDR-05），不移动资金，不计入 frozen_fen。<br>④ 不变量：每账户 frozen_fen = Σ 该账户非终态提现单（PENDING_REVIEW、APPROVED、PAYING）amount_fen；日终校验与属性测试均覆盖。<br>各状态分录见 BR-WDR-09。 | 默认假设 | ledger_type WITHDRAW_FREEZE/WITHDRAW_RETURN/WITHDRAW_PAID/WITHDRAW_FEE/TAX_WITHHOLD 的记账时点与科目见 BR-WDR-09；科目 WITHDRAW_IN_TRANSIT 从 规划/02 §8.2 科目表删除；钱包冻结中展示；不变量 frozen = Σ 非终态提现 |
| BR-FUND-15 | **流水类型与映射**<br>ledger_entries.ledger_type 只能取以下 13 个值：REBATE_CREDIT、SHARE_CREDIT、REFERRAL_CREDIT、CLAWBACK、SETTLE_ADJUST、WITHDRAW_FREEZE、WITHDRAW_PAID、WITHDRAW_RETURN、WITHDRAW_FEE、TAX_WITHHOLD、REWARD（P1）、ADMIN_ADJUST、BAD_DEBT_WRITEOFF；细分只用 sub_type。契约不得定义间推类流水（D8）。用户「余额流水」只展示该用户 available 子户上的分录，按时间倒序，每条展示：带符号金额、类型名称、sub_type 说明、关联订单或提现单、原因、变动后余额 balance_after_fen；此外每张打款成功的提现单合并显示为 1 条 WITHDRAW_PAID 汇总条目（用户侧名称按 BR-TEXT-19，C-02 默认方案 A 为「提现到账」；显示实际到账金额、税、手续费，不改变可提现余额，不带 balance_after）。balance_after_fen 为该分录所在子户变动后的余额。其他文档的类型名只作映射，不得出现在代码与契约中。 | 默认假设 | contracts/enums/ledger-types、sub-types；ledger_entries.ledger_type、sub_type、balance_after_fen；GET /v1/wallet/ledger（含 WITHDRAW_PAID 汇总条目）；余额流水 H5；后台流水查询与导出 |
| BR-FUND-16 | **复式记账硬约束**<br>每个 uniq_key 对应 1 张凭证（ledger_vouchers，uniq_key 在 (app_id, uniq_key) 上唯一）+ ≥2 条分录；一笔业务可由同一事务内的多张凭证组成（如 BR-FUND-05）。分录 amount_fen 为带符号 bigint（单位分，借为正、贷为负），同一凭证 Σ amount_fen = 0，domain 层校验且日终 SQL 复核。ledger_vouchers、ledger_entries 只插入：应用数据库角色无 UPDATE/DELETE 权限并加防护触发器；更正一律写红冲凭证（uniq_key=`{原 uniq_key}:REVERSE`）再重记。用户账户余额缓存 account_balances 必须在同一事务内 SELECT … FOR UPDATE（多账户按 account_id 升序加锁）后更新，version+1；用户负债账户 available_fen = −Σ 该子户分录 amount_fen。平台科目为热点账户，不维护实时余额缓存，从分录汇总。会计日按 00:00 +08:00 日切，accounting_date 取写入时注入 Clock 的日期。金额计算只能用 packages/money 的整数分运算，不得用浮点。 | 已确认 | ledger_vouchers、ledger_entries、account_balances 表结构与权限；DB 角色与防护触发器；packages/money；AGENTS.md 资金硬规则；属性测试（PR 1 万次、夜间 100 万次）；真实 PG 并发测试 |
| BR-FUND-17 | **资金话术与状态对应**<br>本条只维护两件事：①订单 display_status 必须按细则派生表从上到下取第一个匹配项，文案取字典 key `order_status.<display_status>`，文字以 BR-TEXT-02、BR-TEXT-03 为准；②Agent 与客服回答订单或金额问题时，状态与金额必须来自订单与钱包接口（GET /v1/orders、GET /v1/wallet/summary），不得由模型推断。资金术语（预估返、待入账、已入账、可提现、冻结中、已到账、已提现等）的含义只在 BR-TEXT-01 维护，提现状态文案只在 BR-TEXT-06 维护，禁用词只在 BR-TEXT-13 维护，本条不另写。 | 待决策 | 规划/04 §2.3 用户侧状态映射、§2.4 提现状态文案；display_status 枚举（契约）；dict_items 文案 key；specs/banned-words.yaml（BR-TEXT-13）；推送/站内信模板；钱包页、订单页、提现记录文案；Agent rule_qa、order_query 回复模板；客服话术库；帮助中心文章 |
| BR-FUND-18 | **钱包汇总与资产快照口径**<br>GET /v1/wallet/summary 必须按 SELF、PROMO 分别返回：available_fen（可为负）、withdrawable_fen = max(available_fen,0)、negative_fen = max(−available_fen,0)、frozen_fen、pending_credit_fen（待入账：该用户在该账户对应角色上 rebate_status=WAITING 的份额合计，含维权中、hold 与已过预计入账日未入账的）、pending_credit_paused_fen（其中维权中或 hold 的部分）、next_credit_date、credit_overdue、estimated_fen（rebate_status=ESTIMATED 且 platform_status=PAID 的份额合计，不含 DEPOSIT_PAID、UNATTRIBUTED）、withdrawn_fen（已提现：Σ 该账户 PAID_API/PAID_MANUAL 提现单 amount_fen）、risk_paused_reason（risk_state=frozen 或存在生效 withdraw_holds 时返回用户可见原因 key，否则 null；不影响各金额）。pending_credit_fen、estimated_fen 的份额按 BR-FUND-05 的基数取法计算（settle_commission_fen 非空用它，否则用 est_commission_fen），与入账金额一致。next_credit_date = hold=false 且 rights_pending=false 的 WAITING 订单中最早的 expected_credit_date（BR-FUND-04；低于日结门槛且未结算的订单、所在平台 credit.enabled=off 的订单不计；无此类订单返回 null）；若早于今天（+08:00），返回今天并返回 credit_overdue=true，前端显示「入账核对中」。字段名与 BR-TEXT-01 钱包汇总口径对齐，取值口径以本条为准。余额类取 account_balances 实时值；pending_credit/estimated 取订单与分佣快照的计算值，缓存 ≤60 秒。asset_snapshots 在会计日 D+1 的 00:01:00 +08:00 写入 D 日数据：total_available_positive_fen、total_negative_fen、total_frozen_fen、total_waiting_fen、total_estimated_fen、union_receivable_fen（按平台）；余额类按 accounting_date ≤ D 的分录汇总，waiting/estimated 取快照运行时刻的订单状态。入账任务 settle.credit 必须在当日快照完成后才开始，最晚等到 00:30；超时则告警、照常入账，并把该日快照标记 waiting_comparable=false。 | 默认假设 | GET /v1/wallet/summary 响应 schema（含 pending_credit_fen、pending_credit_paused_fen、next_credit_date、credit_overdue、withdrawn_fen、risk_paused_reason）；asset_snapshots 字段与 waiting_comparable；任务依赖：settle.credit 等待 asset_snapshot；钱包页；后台资产快照报表；R3 用户应付 vs 资产快照 |
| BR-FUND-19 | **账务不变量与日终校验**<br>每日 01:00 +08:00 对会计日 D−1 运行 ledger_invariants.sql，校验：①每个用户账户 余额缓存 = 分录合计，且 期初 + 当日发生额 = 期末（daily_balances）；②每张凭证 Σ amount_fen = 0；③每个 (子订单, 受益人, 角色) 的 CREDIT 凭证 ≤1；④每 (子订单, 受益人, 角色) Σ CLAWBACK ≤ CREDIT + Σ 正向 SETTLE_ADJUST；⑤每个 CREDITED 或 CLAWED_BACK 子订单：该单订单类凭证（CREDIT、CLAWBACK、SETTLE_ADJUST、ADMIN_ADJUST RESTORE）对 UNION_RECEIVABLE 的净额 = booked_base_fen，且 Σ受益人已入账净额 ≤ booked_base_fen；⑥frozen_fen ≥0 且 = Σ 非终态提现单金额；⑦用户账户中每条使 balance_after_fen &lt;0 且较前一条下降的分录，其 ledger_type ∈ {CLAWBACK, SETTLE_ADJUST, ADMIN_ADJUST}；⑧platform_status=INVALID 或存在已成功的 INVALID_AFTER_SETTLE 维权、但 rebate_status 仍为 CREDITED 的子订单数 = 0。账户级差异（①⑥⑦⑧）：告警、生成差错单，并冻结涉及用户两个账户的提现。全局差异（②③④⑤）：告警，系统自动将 settle.auto.enabled 置 off（系统关闭不需 step-up），并冻结差异涉及的所有用户两个账户的提现。冻结方式：为每个涉及用户新增 1 条 withdraw_holds 记录（BR-WDR-05；reason=ledger_mismatch，source_ref=差错单 id，后台显示冻结来源 LEDGER_MISMATCH，不向用户展示），同一差错单对同一用户只新增 1 条；冻结生效期间提现申请返回 30303（data.reason=account_frozen）；与 30302 同时满足时按 BR-WDR-03 校验顺序优先返回 30303(account_frozen)；由 finance 在差错单关闭时 step-up 解除该条记录（写 released_at、released_by），同一用户的其他冻结记录不受影响。settle.auto.enabled 重新打开需有权限者 step-up。每张入账凭证提交后 5 分钟内做证实核对（凭证金额 = 分佣快照按 B_credit 重算的份额），不一致 5 分钟内告警并按账户级冻结该用户提现（同上新增 withdraw_holds）。 | 默认假设 | ledger_invariants.sql；daily_balances 表（新增）；withdraw_holds（reason=ledger_mismatch，BR-WDR-05）；错误码 30303 data.reason=account_frozen；开关 settle.auto.enabled（系统自动关闭）；告警规则；属性测试与并发测试；验收用例 AC-SET-nn（编号待 规划/05 分配，对应后端功能规划 §10.1 AC-MONEY-013） |
| BR-FUND-20 | **垫资敞口与入账开关**<br>已入账未回款 = UNION_RECEIVABLE:{platform} 分录余额（按平台）。联盟回款必须由财务在后台录入或经 R1 确认后写凭证：借 CASH_ALIPAY（或银行科目）/ 贷 UNION_RECEIVABLE:{platform}。每日随资产快照（D+1 00:01，BR-FUND-18）计算各平台与合计的已入账未回款；合计 > ledger.advance_alert_fen 的每一天告警财务 1 次。紧急开关 settle.auto.enabled（默认 on）：人工修改需 step-up 并告警，10 秒内生效；系统按 BR-FUND-19 自动关闭不需 step-up；重新打开一律需有权限者 step-up。开关为 off 时入账任务按 BR-FUND-04 停止，订单保持 WAITING，不影响扣回与补差。 | 待决策 | 看板：已入账未回款（按平台与合计）、负余额总额；配置 ledger.advance_alert_fen；开关 settle.auto.enabled；后台联盟回款录入；R1 差错单 |
| BR-FUND-21 | **负余额时未打款的提现单**<br>负余额对非终态提现单的处理（W2/W4/W8 守卫、事件 account.went_negative、同账户 W3 驳回、另一账户 blocked_reason=NEGATIVE_BALANCE_OTHER、PAYING 单走 W9）只在 BR-WDR-05 (a) 维护，本条不再单独规定；编号保留供 §14.3 C-08、C-21 及外部引用定位。 | 待决策 | 见 BR-WDR-05 (a) |
| BR-FUND-22 | **作废或扣回订单的平台恢复**<br>rebate_status 为 VOID 或 CLAWED_BACK 的子订单不得因平台数据自动复活。仅当其 reason_code ∈ {REFUND, RIGHTS, COMMISSION_ZERO} 或进入原因为 PLATFORM_INVALID / INVALID_AFTER_SETTLE，且平台此后回传非失效状态或佣金恢复为 >0 时，才告警并生成差错单（类型「已作废订单被平台恢复」）；因 PUNISH、BLACKLIST_HIT 作废的订单，platform_status 照常更新，不告警、不生成差错单。差错单只能经 ADMIN_RESTORE 处理：ops 或 finance 发起，另一人（≠发起人）step-up 复核。R12：VOID → 按当前 platform_status 回到 ESTIMATED 或 WAITING（credit_due_at = received_at + wait_days 重算，已过期则由下一次入账任务入账），不写分录。R13：CLAWED_BACK → CREDITED，按当前联盟佣金与分佣快照重算各受益人与平台应得，与当前净额的差额写 ADMIN_ADJUST（sub_type=RESTORE，借 UNION_RECEIVABLE / 贷 USER_\*.available 或 COMMISSION_REVENUE），uniq_key 受益人 `{order_key}:{user_id}:{role}:RESTORE:{差错单 id}`、平台 `{order_key}:PLATFORM:RESTORE:{差错单 id}`，同事务 booked_base_fen=新基数。复核人也可决定不恢复，关闭差错单并记原因。 | 默认假设 | 迁移表 R12、R13（SM-REB-R12/R13）；差错单类型「已作废订单被平台恢复」；ADMIN_ADJUST sub_type RESTORE；后台差错单处理页（发起、复核）；告警规则 |
| BR-FUND-23 | **月末三项核对**<br>每月 1 日 01:30:00 +08:00（名义时刻，读注入的 Clock；须在当日 01:00 的 BR-FUND-19 日终校验完成后开始，最晚等到 03:00，超时告警并照常运行）对上月 M（M 月 1 日 00:00 至 M+1 月 1 日 00:00，+08:00）运行内部对账 R3 的月度核对，按 app_id、分 SELF/PROMO 与合计计算三个数（单位分）：X1 用户累计入账净额 = 截至 M 月末（accounting_date ≤ M 月末日）用户 available 子户上 REBATE_CREDIT、SHARE_CREDIT、REFERRAL_CREDIT、REWARD、CLAWBACK、SETTLE_ADJUST、ADMIN_ADJUST、BAD_DEBT_WRITEOFF 分录对用户余额的影响合计（贷记为正）；X2 用户期末余额 = M 月末日 asset_snapshots 的 total_available_positive_fen − total_negative_fen + total_frozen_fen；X3 用户累计已提现 = 截至 M 月末迁移到 PAID_API/PAID_MANUAL 的提现单 amount_fen 合计（取提现单表，以迁移事务的 Clock 时刻判断归属月份）。必须满足 X1 = X2 + X3，差额 ≠0 分即 P1 告警并生成差错单（类型「月末三项不平」），不自动冻结提现、不改开关（账户级定位与冻结由 BR-FUND-19 负责）。同一报表另列按平台的「上月联盟预估佣金」（paid_at 在 M 内且已归因子订单的 est_commission_fen 当前值合计）、「上月入账基数」（M 内 rebate_status→CREDITED 的子订单 booked_base_fen 合计）、UNION_RECEIVABLE:{platform} 期末余额，只供财务查看，不参与等式。重跑同一月份结果相同，差错单按 (app_id, 月份) 去重。 | 默认假设 | 任务 recon.monthly（依赖 BR-FUND-19 当日完成、BR-FUND-18 月末日快照）；/admin/v1/recon R3 月度报表与导出；差错单类型「月末三项不平」；告警规则；验收用例：构造入账、扣回、提现、核销后三项相等；篡改一笔提现单金额后生成差错单 |

### 6.2 细则

#### BR-FUND-01 细则 · 订单双状态模型

- 状态：待决策
- 默认值：采用双状态（platform_status + rebate_status），取代 规划/04 的单一 order_status；理由：平台事实与资金事实分属不同写者，避免 O7/O8 语义混杂和入账后维权无状态可落，且后端功能规划已按此设计。分佣快照的生成时点按 BR-CALC-10（已归因且 platform_status 首次 ∈ {PAID, RECEIVED, SETTLED}；DEPOSIT_PAID 不生成），快照中的等级与上级按 BR-CALC-12 取 paid_at 时刻，R2、R3 均同（C-06）。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 规划/04 §2.3、§4.1：「order_status 单一状态机：DEPOSIT_PAID→PAID→RECEIVED→CREDITED→SETTLED，终态 INVALID、CLAWED_BACK；平台订单状态和返利状态合在一个状态机里」
  - 规划/01 E09 F-ORD-06：「订单状态机为单一状态机（未拆平台订单状态与返利状态）」
  - PRD v2.1 §9.3：「订单状态含 RIGHTS_PROTECTING、PLATFORM_SETTLED；资金侧 credit_status：ESTIMATED→HOLDING→CREDITED→REVERSED」
- 来源：规划/04 §2.3、§4.1、§7；规划/01 E09 F-ORD-06；PRD修订_后端功能规划 §3.1、§3.2、§1.7；PRD v2.1 §9.3
- 需同步修改的规划文档：6 处（计数仅作记录，落点见 README §0.6）

**platform_status 迁移表**（测试 ID `SM-PLT-P<n>`；平台状态码到事件的映射见 BR-FUND-02）：

| # | 从 | 平台事件 | 到 | 说明 |
|---|---|---|---|---|
| P1 | — | 付定金 | DEPOSIT_PAID | |
| P2 | — / DEPOSIT_PAID | 付款 | PAID | |
| P3 | PAID | 确认收货/完成 | RECEIVED | 写 received_at |
| P4 | RECEIVED | 结算 | SETTLED | 写 settled_at；结算额写 order_settlements（BR-FUND-09） |
| P5 | DEPOSIT_PAID / PAID | 结算（此前未给收货） | SETTLED | 同一事务依次补写 →PAID（如缺）、→RECEIVED、→SETTLED 三条 history；received_at 取结算时间 |
| P6 | DEPOSIT_PAID / PAID / RECEIVED | 失效 | INVALID | |
| P7 | SETTLED | 失效 | 不变 | 写 order_rights(type=INVALID_AFTER_SETTLE, status=SUCCEEDED)，settlement 按 BR-FUND-08 处理 |
| P8 | SETTLED | 维权/处罚 | 不变 | 写 order_rights |
| P9 | INVALID | 平台回传非失效状态 | 平台当前状态 | 记 history 并告警；rebate_status 不自动变化，按 BR-FUND-22 |
| P10 | 任意 | 比当前更早阶段的状态码（倒退） | 不变 | 写待处理表并告警 |

platform_status=SETTLED 只表示联盟订单状态为「结算」，不表示已回款；回款由 BR-FUND-20 的 UNION_RECEIVABLE 核销表示。

**rebate_status 迁移表**（测试 ID `SM-REB-R<n>`）：

| # | 从 | 事件 | 守卫 | 到 | 记账 |
|---|---|---|---|---|---|
| R1 | — | 入库未归因 | — | UNATTRIBUTED | 无 |
| R2 | — | 入库已归因 | — | ESTIMATED（platform_status 已为 RECEIVED/SETTLED 时同事务再按 R4 进 WAITING） | 无；platform_status ≠ DEPOSIT_PAID 时同事务生成分佣快照，DEPOSIT_PAID 时在之后 P2（→PAID）的同一事务内生成（BR-CALC-10） |
| R3 | UNATTRIBUTED | CLAIM_APPROVED / ADMIN_REASSIGN | orders.locked=false（未被其他用户认领或改派） | ESTIMATED；platform_status 已为 RECEIVED/SETTLED 则直接 WAITING（credit_due_at 按原 received_at 计） | 无分录；同事务设置 user_id、user_basis（CLAIM_APPROVED→claim，ADMIN_REASSIGN→admin；BR-ATTR-09），locked=true；platform_status ≠ DEPOSIT_PAID 时同事务生成分佣快照（BR-CALC-10；等级与上级取 paid_at 时刻，BR-CALC-12） |
| R3a | UNATTRIBUTED | SYNC_ATTRIBUTED（同步重跑用户归属成功，BR-ATTR-16） | orders.locked=false | ESTIMATED；platform_status 已为 RECEIVED/SETTLED 则 WAITING（credit_due_at 按原 received_at 计） | 无分录；写 user_id、user_basis=param，不置 locked；platform_status ≠ DEPOSIT_PAID 时同事务按 BR-CALC-10 生成分佣快照 |
| R3b | VOID 且 user_id 为空 | CLAIM_APPROVED / ADMIN_REASSIGN | orders.locked=false | VOID 不变 | 只写 user_id、user_basis、locked=true；不生成快照、无分录 |
| R4 | ESTIMATED | platform_status→RECEIVED 或 SETTLED | — | WAITING | 无（写 credit_due_at） |
| R5 | WAITING | CREDIT_DUE | BR-FUND-04 守卫 | CREDITED | B_credit>0 写入账凭证（BR-FUND-05）；B_credit=0 不写凭证、不推送入账 |
| R5a | CREDITED | BENEFICIARY_RELEASE（受益人 held→active，BR-CALC-13） | 该受益人满足 BR-FUND-04 守卫；在 hold 解除后的下一次 00:05 入账任务处理 | 不变 | 该受益人单独入账，uniq_key 沿用 `{order_key}:{uid}:{role}:CREDIT`（保证只入一次）；转 forfeited 时份额记平台 `{order_key}:PLATFORM:FORFEIT:{uid}:{role}`（默认处理，待财务确认） |
| R6 | UNATTRIBUTED / ESTIMATED / WAITING | 整单失效 / 全额维权 / 处罚 / 黑名单 / B 由 >0 变 0 | B 由 >0 变 0 分支：platform_status ≠ DEPOSIT_PAID，且新 B 非 null（BR-FUND-07） | VOID（终态） | 无（BR-FUND-07） |
| R7 | ESTIMATED / WAITING | 部分退款 / 部分维权 / 佣金变化 | 新 B>0，或原 B 已为 0 | 不变 | 无（重算预估） |
| R8 | CREDITED | 整单失效 / 全额维权 / 处罚 / 结算后退款或失效 / B 由 >0 变 0 / 黑名单人工复核确认（BLACKLIST_CONFIRMED，财务 step-up + 第二人复核；默认处理，待财务确认） | — | CLAWED_BACK（终态） | CLAWBACK（BR-FUND-08） |
| R9 | CREDITED | 部分退款 / 部分维权 | 新 B>0 | 不变 | 部分 CLAWBACK（BR-FUND-08） |
| R9b | CREDITED | 佣金变化（价保、比价降佣、联盟佣金调整；非退款、非维权） | 新 B>0 | 不变 | 更新 est_commission_fen、commission_version+1；新 B &lt; booked_base_fen：同事务写负向 SETTLE_ADJUST（sub_type=PRICE_PROTECT / PRICE_COMPARE / SETTLE_DIFF），uniq_key `{order_key}:{uid}:{role}:ADJ:{sub_type}:v{commission_version}`（平台侧 `{order_key}:PLATFORM:ADJ:{sub_type}:v{commission_version}`），同事务 booked_base_fen=新 B；新 B > booked_base_fen：进 BR-FUND-09 正差候选（C-07；默认处理，待财务确认） |
| R10 | CREDITED | 结算额写入且低于 booked_base_fen（负差，即时）/ 正差补差候选获批 | BR-FUND-09 | 不变；补差后结算佣金=0 且全部受益人与平台净额=0 → CLAWED_BACK | SETTLE_ADJUST（BR-FUND-09） |
| R11 | ESTIMATED / WAITING | HOLD / UNHOLD | BR-FUND-06 的角色 | 不变，hold=true/false | 无 |
| R12 / R13 | VOID / CLAWED_BACK | ADMIN_RESTORE | 见 BR-FUND-22 | 见 BR-FUND-22 | 见 BR-FUND-22 |
| R14 | ESTIMATED / WAITING / CREDITED | ADMIN_REASSIGN（已归属订单改派，BR-ATTR-20） | 双人复核通过 | 不变（自迁移） | 非 CREDITED：无分录，作废旧快照、按新 user_id 生成新快照；CREDITED：同事务先红冲 `{order_key}:{old_uid}:{role}:REASSIGN_REV:{reassign_id}` 再按新快照重记 `{order_key}:{new_uid}:{role}:REASSIGN_CREDIT:{reassign_id}` |

R9 与 R9b 的判定：同一次同步中 refunded_quantity 增加，或存在对应的 order_rights → R9；否则 → R9b。

**与 规划/04 单一 order_status 的映射**：DEPOSIT_PAID→(DEPOSIT_PAID, ESTIMATED 且不计预估)；PAID→(PAID, ESTIMATED)；RECEIVED→(RECEIVED, WAITING)；CREDITED→(RECEIVED 或 SETTLED, CREDITED)；SETTLED→(SETTLED, CREDITED 且已补差)；INVALID→(任意, VOID)；CLAWED_BACK→(任意, CLAWED_BACK)。

**与 规划/04 §4.1 迁移编号 O1–O12 的映射**（其他主题条目中出现的 O 编号按本表换算，规则内容不变；测试 ID SM-ORD-O&lt;n> 改用右列）：

| 04 编号 | 双状态下的迁移 |
|---|---|
| O1 | P1；rebate 按 R1/R2 入库，不计预估、不生成快照 |
| O2 | P2（+ 新入库时 R1/R2）；已归因时同事务生成分佣快照 |
| O3 | P3 + R4（写 received_at、credit_due_at） |
| O4 | 平台失效：P6 + R6；全额维权、处罚、黑名单命中：只 R6，platform_status 不变；CREDITED 命中黑名单不自动扣回，见 BR-ATTR-26 |
| O5 | R7 |
| O6 | R5 |
| O7 | P4，rebate_status=WAITING 不变（结算额写 order_settlements，入账时按结算额，BR-FUND-05） |
| O8 | P4，rebate_status=CREDITED 不变 + R10（补差按 BR-FUND-09） |
| O9 | 平台失效：P6（结算前）或 P7（结算后）+ R8；维权、处罚：P8（结算后写 order_rights）或只写 order_rights（结算前）+ R8 |
| O10 | R9（写 CLAWBACK sub_type=PART_REFUND，不写负向 SETTLE_ADJUST，BR-FUND-08） |
| O11 | R3 |
| O12 | R14（ADMIN_REASSIGN，已归属订单改派，BR-ATTR-20；rebate_status 自迁移，platform_status 不变；CREDITED 时先红冲再重记） |

**为何拆分**：单一状态机下 O7「RECEIVED 收到结算→不变」丢失平台事实；O8 的 SETTLED 同时表示「联盟已结算」和「补差完成」；「入账后、平台结算前的维权」、hold、维权中都需要额外状态。拆分后平台事实与我方资金事实各有唯一写者。

**例**：淘宝子订单 10-01 付款 → (PAID, ESTIMATED)；10-05 10:00 确认收货 → (RECEIVED, WAITING)；10-21 00:05 入账 → (RECEIVED, CREDITED)；此后联盟结算（示意：淘宝「订单结算」状态的出现时点待 规划/09 实测，可能紧随确认收货，与次月 20 日前后的联盟回款不是一回事）→ (SETTLED, CREDITED)；结算后维权成功 → (SETTLED, CLAWED_BACK)。

**异常**：VOID/CLAWED_BACK 后平台再回传有效状态，不自动复活，按 BR-FUND-22 处理。

**并发冲突返回**：后台对订单的 hold/unhold、改派、恢复等写操作 CAS 影响 0 行时返回 20902，data.resource=order（与 BR-ATTR-20 的 order_attribution、BR-WDR-08 的 withdrawal 共用 20902，按 data.resource 区分）。

按 C-01 默认处理（采用双状态，其他条目的单一 order_status 与 O 编号按上方两张映射表换算），待负责人确认；按 C-03 默认处理（20902 补 data.resource=order），待负责人确认；按 C-06 默认处理（快照生成时点按 BR-CALC-10、等级与上级取 paid_at），待负责人确认。

按 C-27 默认处理：(a) R3a、(b) R14、(c) R3b 状态口径代理已补（按 BR-ATTR-16、20 与 BR-CALC-10 现有写法），待负责人确认；(d) R5a、(e) 入账守卫 credit_requires_settle（BR-FUND-04）、(f) CREDITED 命中黑名单只写 blacklist_hit_after_credit 进人工复核、扣回按 R8 BLACKLIST_CONFIRMED、(g) R9b 负差即时记账，待财务确认。

#### BR-FUND-02 细则 · 平台状态映射与可入账事件

- 状态：待验证
- 默认值：四个平台的可入账事件按上表；P1 平台 vip、douyin 按确认收货（来源：PRD修订_后端功能规划 §2.7 可入账事件）、eleme 按完成或核销（后端功能规划 B12 将其列为核销型，§2.7 未列，属推定）；三者均在接入时经 规划/09 实测确认后才写入 creditable-events.yaml；等待期全部 15 天（核销型订单是否不同见 6.3 第 9 条）。
- 决策人：负责人
- 依赖平台能力：taobao/jd/pdd 订单接口：确认收货与结算是否为两个独立状态、各自时间字段是否返回、状态出现顺序；淘宝「订单结算」状态与联盟回款日是否同一时点（决定入账基数多大比例直接取结算额）；京东实际佣金归零能否与部分维权区分；美团核销时间字段（P1，D15）
- 取代：
  - 规划/02 §7.2：「淘宝「确认收货」→PLATFORM_RECEIVED、「结算」→PLATFORM_SETTLED（未说明结算先于或代替收货出现时如何处理）」
- 来源：规划/02 §7.1、§7.2；PRD修订_后端功能规划 §2.7 可入账事件、§3.1；规划/07 §2 08 订单管理
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**各平台待确认的映射（进 规划/09 验证）**：

| 平台 | 需要验证的状态码 | received_at 候选字段 | 维权/失效信号 |
|---|---|---|---|
| taobao | 付款 / 订单成功（确认收货）/ 订单结算 / 失效，以及出现顺序；「订单结算」与联盟回款日是否同一时点 | 确认收货时间、结算时间字段（字段名待实测） | 维权退款接口、处罚订单接口 |
| jd | 有效码 validCode 各值 | 完成时间字段（待实测） | 实际佣金由 >0 变 0（能否与部分维权区分待验证） |
| pdd | order_status 各值 | 收货时间字段（待实测） | 随订单状态 |
| meituan | 完成/核销状态（W7） | 核销时间（待实测） | 随订单状态 |

**例**：淘宝订单若在 10-05 14:30 直接回传「订单结算」且结算时间 = 10-05 14:30，则同一事务写 received_at=2026-10-05T14:30:00+08:00、platform_status=SETTLED（history 补写 RECEIVED、SETTLED 两条）、order_settlements(source=API)，rebate_status 由 ESTIMATED→WAITING。10-06 平台补回真实确认收货时间 10-04 20:00 → 写 platform_received_at，received_at 与 credit_due_at 不变。

**乱序与去重**：只按 BR-ATTR-01（G-12）——配置 attr.mtime_ordering.&lt;platform>（默认 false）：false 时不按更新时间丢弃，只按 content_hash 去重；true 时 platform_modified_at 小于库内值丢弃、相等且 content_hash 不同照常处理。两种配置下状态倒退都按 BR-FUND-01 P10 不迁移、写待处理表并告警。理由：平台更新时间是否单调未经 规划/09 实测，默认不丢弃才不会漏掉退款等逆向更新。

**异常**：状态码未知 → 告警 + 待处理表 + 订单保持原状态；状态倒退 → P10；received_at 缺失 → 待处理表，每日告警汇总。

#### BR-FUND-03 细则 · 预估返利生成与变更

- 状态：默认假设
- 默认值：业务口径沿用 规划/04 O2/O5（已确认；双状态下即 P2/R2 与 R7，见 BR-FUND-01 映射表），状态字段表述依赖 BR-FUND-01 拍板；若不采纳双状态，按 BR-FUND-01 中的 order_status 等价映射执行。推送对象、触发与去重归 BR-TEXT-09 维护（C-25）。
- 决策人：负责人
- 依赖平台能力：无
- 取代：无
- 来源：规划/04 §1 预估佣金、§2.3、§4.1 O1/O2/O5/O11；规划/02 §8.3；PRD v2.1 §9.3；PRD修订_后端功能规划 §3.1
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

**计算**：B_est = 联盟口径推广者预估收入（已扣技术服务费），取 orders.est_commission_fen 最新值；受益人份额 = f(B_est, 快照比例)。

**例**：B_est=1234 分，快照 自购 5000bp、直推 1000bp → 自购预估 617 分、直推预估 123 分（平台 494 分不展示）。买家部分退款 2 件退 1 件，联盟回传 B_est=617 → 自购预估 308 分、直推 61 分，订单页显示新预估与原因码 PART_REFUND。

**推送**：对象、触发、合并与去重只在 BR-TEXT-09 维护（C-25）：自购受益人与 share 单分享者各推自己的份额，直推上级不推 ORDER_TRACKED（J7）；去重键 `{order_key}:{uid}:{role}:TRACKED`。按 C-25 默认处理，待负责人确认。

**边界**：首次入库 B_est=0 的已归因订单（如 0 佣金商品）：ESTIMATED，展示「本单无返利」，不推送；此后照常 R4，到期 B_credit=0 → R5 进 CREDITED、不写凭证、不推送入账，订单页仍显示「本单无返利」（BR-FUND-17）。

**快照时点**：已归因订单首次入库即为 DEPOSIT_PAID 时不生成分佣快照、不计预估；尾款付清（P2）的同一事务内生成快照，快照中的等级与上级取 paid_at 时刻（BR-CALC-10、BR-CALC-12）。例：10-01 20:00 付定金入库 → (DEPOSIT_PAID, ESTIMATED)，无快照；10-11 00:10 付尾款 → 同事务生成快照，等级与上级取 paid_at 时刻（预售单 paid_at 的取值以 BR-CALC-12 为准）。

按 C-06 默认处理（快照生成时点与取值时点以 BR-CALC-10、BR-CALC-12 为准），待负责人确认。

#### BR-FUND-04 细则 · 入账时点与入账任务

- 状态：待决策
- 默认值：满 15×24 小时后的首次 00:05 任务入账，预计入账日一般为收货日+16 天；维权或 hold 期间 credit_due_at 不顺延，解除后下一次任务入账。理由：严格满足「满 15 天」，避免在平台售后窗口内提前入账导致扣回和负余额；维权结果已明确，无需再观察。替代方案：按自然日（收货日记第 0 天，第 15 天 00:05 入账，实际观察期 14 天 0 时 6 分至 15 天 0 时 5 分）；维权期间顺延维权持续时长。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 规划/01 §5 J1 步骤 6、规划/04 §2.3 RECEIVED 行：「预计到账日 = 收货日 + 15 天」
  - 规划/04 §2.3 PAID 行、规划/01 F-PROD-05、J1 步骤 1：「「确认收货 15 天后到账」」
  - 规划/06 Q-B2：「日结门槛（低于此预估佣金的子订单等月结）」
  - PRD修订_后端功能规划 §2.7：「每天 00:30 的任务把到期子订单入账」
  - PRD v2.1 §9.3：「维权失败→RECEIVED 恢复观察期剩余天数（暂停计时）」
- 来源：规划/04 §1、§2.3、§4.1 O6；规划/02 §1 原则 8、§5.2；规划/06 Q-B2；规划/00 §2；PRD修订_后端功能规划 §2.7；规划/01 §5 J1、F-PROD-05
- 需同步修改的规划文档：6 处（计数仅作记录，落点见 README §0.6）

**例 1**：received_at=2026-10-01T14:30+08:00 → credit_due_at=2026-10-16T14:30 → 10-16 任务不满足（晚于 run_at）→ 2026-10-17 00:05 入账；expected_credit_date=2026-10-17，用户看到「预计 10-17 入账」。

**例 2**：received_at=2026-10-01T00:03+08:00 → credit_due_at=2026-10-16T00:03 ≤ 10-16 00:05:00 → 10-16 入账。

**例 3**：received_at=2026-10-01T00:05:03 → credit_due_at=10-16T00:05:03 > run_at → 10-17 入账，expected_credit_date=10-17（即使 10-16 任务实际 00:05:10 才启动，也不入账）。

**例 4（收货同步晚于到期）**：received_at=2026-10-01T10:00，平台数据延迟，本系统 2026-10-20T15:00 才同步到收货（received_synced_at）→ credit_due_at=10-16T10:00 已过；首个 run_at ≥ 10-20T15:00 为 10-21 00:05 → expected_credit_date=10-21，10-21 入账。

**边界**：credit_due_at 恰等于 run_at → 入账（≤）。任务跨日运行超时：仍以 run_at 判断，凭证 accounting_date 取凭证写入时 Clock 日期。

**维权中 / hold**：到期时存在未关闭维权或 hold → 本次跳过，不顺延 credit_due_at（是否顺延见 6.3 第 4 条），此后每日任务重新判断；期间 expected_credit_date 返回 null（显示售后中 / 核对中，不给日期）；解除后按上式重算，即首个 run_at ≥ max(credit_due_at, received_synced_at, 解除时刻)（例：credit_due_at=10-16T14:03，维权 10-20T09:00 关闭 → 2026-10-21）。只有过了重算后的日期仍未入账才显示「入账核对中」（BR-FUND-18 credit_overdue=true）。按 G-16 默认处理，待负责人确认。received_at 写入后不变（BR-FUND-02），expected_credit_date 也不因平台补回真实收货时间而重算。

**门槛 >0 时**：入账基数 &lt; settle.daily_min_fen 且 settle_commission_fen 未记录的订单保持 WAITING，不展示预计入账日，显示「已收货，等待联盟结算后入账」；settle_commission_fen 记录后（订单同步或 R1 明细，BR-FUND-09），下一次任务按结算额以 REBATE_CREDIT 等入账类型首次入账（不是 SETTLE_ADJUST），不依赖 R1 审批。

**须等结算的订单**：orders.credit_requires_settle=true（BR-CALC-15、BR-CALC-25）且 settle_commission_fen 为空 → 入账任务跳过，保持 WAITING，display_status 与门槛分支相同（WAITING_SETTLE，不显示预计日期）；settle_commission_fen 记录后下一次任务按结算额入账。按 C-27 (e) 默认处理，待财务确认。

**held 受益人**：一单中除 held 受益人（BR-CALC-13）外的全部受益人同时入账；held 受益人解除后按 BR-FUND-01 R5a 在下一次 00:05 任务单独入账，转 forfeited 时份额记平台。按 C-27 (d) 默认处理，待财务确认。

**开关关闭 / 任务延迟**：订单保持 WAITING；预计入账日已过的订单展示「入账核对中」。

**平台入账开关 credit.enabled.&lt;platform>**（BR-CALC-03 默认 off；S1 上线期间三平台均为 off，打开前须有 BR-CALC-03 验证证据，见 规划/05 S2 门槛）：

| 场景 | 入账任务 | 订单 display_status 与日期 | 入账时点文案 |
|---|---|---|---|
| off，ESTIMATED（DEPOSIT_PAID / PAID） | 不涉及 | DEPOSIT_PAID / PAID，expected_credit_date=null | 商品详情与订单页不展示「确认收货满 {wait_days} 天后入账」 |
| off，WAITING（含 credit_due_at 已过） | 跳过该平台全部子订单（含 R5a） | CREDITING「入账核对中」，expected_credit_date=null，不显示日期；hold、维权中按 BR-FUND-17 先匹配 REVIEWING / RIGHTS_PENDING | 同上 |
| off，钱包 | — | 该平台 WAITING 份额仍计入 pending_credit_fen，不参与 next_credit_date（BR-FUND-18） | — |
| off → on | 下一次 00:05 任务按 credit_due_at ≤ run_at 正常处理积压，不另设补跑；受单批上限约束 | expected_credit_date = 首个 run_at ≥ max(credit_due_at, received_synced_at, 维权关闭或 hold 解除时刻, 开关打开时刻) | 恢复展示 |
| on → off（如发现 N 取数错误） | 任务在处理每个子订单的事务开始前读开关（缓存 ≤10 秒），已提交的保持 CREDITED，未处理的保持 WAITING；扣回、补差、失效照常 | 同 off | 同 off |

**单批上限**：每次任务每个平台最多处理 settle.credit.max_orders_per_run 个子订单（默认 5000），按 (credit_due_at, order_key) 升序；超出的订单保持 WAITING，其 expected_credit_date 已早于今天时按 BR-FUND-17 显示 CREDITING「入账核对中」，下一次任务按同一顺序优先处理；发生溢出时告警财务 1 次。默认值理由：开关打开当天可能一次积压整个 S1 期间的订单，上限控制单日垫资增量（BR-FUND-20）与任务时长。按默认处理，上限取值待财务确认。

**例（开关打开）**：淘宝 received_at=10-01T14:30，credit_due_at=10-16T14:30；credit.enabled.taobao 在 11-10 之前为 off → 进入 WAITING 起订单显示「入账核对中」、无日期，10-17 起每日任务跳过；11-10T10:00 打开 → expected_credit_date=11-11，11-11 00:05 入账。若当日该平台到期订单 7000 单 → 按 credit_due_at 升序入账 5000 单，其余 2000 单 11-12 00:05 入账，告警财务。

**推送**：入账后每用户每日汇总一条「¥x 已入账」（B_credit=0 的订单不计入）。

**与 BR-TEXT-04 的分工**：expected_credit_date 的计算（含 received_synced_at、维权关闭或 hold 解除时刻、配置快照、不因 received_at 回补重算）只在本条维护（G-16）；BR-TEXT-04 只维护日期格式与「确认收货满 {wait_days} 天后入账」等展示文案，两者不一致时以本条为准。

按 C-02 默认处理（订单侧用「入账」：预计入账日、已入账、入账核对中），待负责人确认；按 C-17 默认处理（D+1 00:01 资产快照完成后 00:05 入账，BR-FUND-18），待财务确认；按 G-16 默认处理（expected_credit_date 并入维权关闭或 hold 解除时刻，期间返回 null），待负责人确认；按 C-27 (d)(e) 默认处理（held 受益人单独入账、credit_requires_settle 守卫），待财务确认。

#### BR-FUND-05 细则 · 入账金额与入账凭证

- 状态：待决策（原为默认假设；入账基数取法与凭证粒度属金额口径，决策人为财务，按 README §0.3 改为待决策）
- 默认值：每受益人一张凭证 + 平台一张凭证，同一事务提交，uniq_key 以 order_key 开头；理由：与 规划/02 §8.1 的 uniq_key（按受益人）一致，按受益人幂等且流水只涉及一个用户；带平台前缀避免三家子订单号撞号时后到订单被当作已入账跳过。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - 规划/02 §8.3：「订单入账为一张凭证：借 UNION_RECEIVABLE 1234 / 贷 USER_SELF:buyer 617、USER_PROMO:parent 123、COMMISSION_REVENUE 494」
  - 规划/02 §8.1：「uniq_key 以 sub_order_id 开头（不含平台）」
  - PRD v2.1 §11.1：「唯一业务键 (entry_type, biz_id)，如 (CREDIT_REBATE, sub_order_id)」
  - PRD修订_后端功能规划 §2.7：「入账金额取入账时刻订单上最新的联盟口径预估佣金（未考虑已先行结算的情况）」
- 来源：规划/04 §4.1 O6/O7；规划/02 §8.1、§8.3；规划/01 E10 F-SET-02；PRD修订_后端功能规划 §2.7、§2.8 记账规则 2
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

**分录模板**（借为正、贷为负，见 BR-FUND-16）：

| 角色 role | ledger_type | 借 | 贷 |
|---|---|---|---|
| 自购 self | REBATE_CREDIT | UNION_RECEIVABLE:{platform} | USER_SELF:{uid}.available |
| 分享者 share | SHARE_CREDIT | UNION_RECEIVABLE:{platform} | USER_PROMO:{uid}.available |
| 直推上级 parent_direct | REFERRAL_CREDIT（sub_type=DIRECT） | UNION_RECEIVABLE:{platform} | USER_PROMO:{uid}.available |
| 平台 | —（不对用户展示） | UNION_RECEIVABLE:{platform} | COMMISSION_REVENUE |

**booked_base_fen**：该子订单最近一次记账所用基数；入账、扣回（BR-FUND-08）、补差（BR-FUND-09）、恢复（BR-FUND-22）同事务更新，供 BR-FUND-19 ⑤ 校验。

**例**：order_key=taobao:1234567，B_credit=1234，自购 5000bp、直推 1000bp → 凭证 1（`taobao:1234567:42:self:CREDIT`）：借 UNION_RECEIVABLE 617 / 贷 USER_SELF:42 617；凭证 2：借 UNION_RECEIVABLE 123 / 贷 USER_PROMO:parent 123；凭证 3（`taobao:1234567:PLATFORM:CREDIT`）：借 UNION_RECEIVABLE 494 / 贷 COMMISSION_REVENUE 494；booked_base_fen=1234。重放同一任务：3 个 uniq_key 均已存在，余额不变。京东子订单号同为 1234567 时 order_key=jd:1234567，不冲突。

**例（先结算后入账）**：收货后联盟已结算 1100 分，入账时 B_credit=1100 → 550/110/440，此后 R1 差额为 0。

**异常**：受益人已封禁/注销时份额归平台（见 BR-CALC）；任一凭证借贷不平 → 整个事务回滚、告警，订单保持 WAITING。

#### BR-FUND-06 细则 · 维权中与订单暂停

- 状态：待验证
- 默认值：淘宝按维权退款接口的处理中状态设置 rights_pending；京东、拼多多无处理中信号，只做事后扣回。部分成功而佣金未更新时继续阻止入账（WAIT_COMMISSION）。
- 决策人：负责人
- 依赖平台能力：淘宝维权退款接口是否返回「维权处理中」及结束状态、是否返回应扣佣金或新佣金；京东、拼多多是否存在任何售后进行中信号
- 取代：
  - PRD v2.1 §9.3：「RECEIVED 维权发起→RIGHTS_PROTECTING 暂停入账（独立状态）」
- 来源：规划/04 §4.1 O6 守卫「无维权」；规划/02 §7.1；PRD修订_后端功能规划 §2.5、§2.7 订单 hold、§3.2；PRD v2.1 §9.3、§9.5
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**用户展示**：rights_pending=true →「售后处理中，入账暂停」；hold=true →「入账核对中」，不展示内部原因（文字以 BR-TEXT-03 与 README §1.2 为准）。

**例**：received_at=10-01 14:30，credit_due_at=10-16 14:30；10-12 淘宝维权处理中 → 10-17 00:05 跳过；10-20 维权失败关闭 → 10-21 00:05 入账，入账额不变。

**例（部分成功、佣金未更新）**：WAITING 订单 10-15 淘宝维权部分成功，接口只给退款金额、无应扣佣金，联盟佣金未变 → order_rights=WAIT_COMMISSION，继续跳过入账；10-18 联盟回传新佣金 → R7 重算预估并关闭记录，下一次任务入账。

**异常**：order_rights 处于 PROCESSING 或 WAIT_COMMISSION，且 now − created_at ≥ 60×24 小时 → 告警进人工；手工导入的维权/处罚清单（后台 rights-imports）与接口同等处理，按 (platform, sub_order_id, 平台维权单号) 去重。

按 C-02 默认处理（用户展示改用「入账」用词），待负责人确认。

#### BR-FUND-07 细则 · 入账前失效与部分退款

- 状态：默认假设
- 默认值：业务口径沿用 规划/04 O4/O5（已确认），状态字段表述依赖 BR-FUND-01 拍板；B 由 >0 变 0 作废与 reason_code=COMMISSION_ZERO 为本条新增默认值。
- 决策人：负责人
- 依赖平台能力：无
- 取代：无
- 来源：规划/04 §1 扣回、§4.1 O4/O5；规划/01 E10 F-SET-04；PRD修订_后端功能规划 §2.7 失效与扣回、§3.2
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

**例**：10-01 付款预估自购 617 分 → 10-03 买家退款，淘宝回传失效 → (INVALID, VOID)，reason_code=REFUND；钱包预估减少 617，余额与流水不变；推送「订单已失效：订单已退款」。

**例（部分）**：WAITING 中退 1/2 → B_est 1234→617，份额 617→308，credit_due_at 不变。

**例（佣金归零）**：拼多多订单 WAITING，联盟回传佣金 0、状态仍为已收货 → VOID，reason_code=COMMISSION_ZERO，文案「订单已失效：平台取消了本单佣金」。

**边界**：京东实际佣金由 >0 变 0：规划/09 验证前 reason_code=COMMISSION_ZERO；验证确认其表示维权后改取 RIGHTS。

**边界（预售定金）**：淘宝预售单 10-01 付定金入库 (DEPOSIT_PAID, ESTIMATED)，联盟回传佣金 120 分；10-05 回传佣金 0 → 不作废，仍显示「已付定金」（BR-FUND-17 第 6 行）；10-11 付尾款 (PAID) 时佣金 0 → 按首次 B_est=0 显示「本单无返利」，不作废；此后 B_est 由 0 变 >0 按 R7 重算预估。付尾款时佣金 900、之后变 0 → 按本条 VOID，reason_code=COMMISSION_ZERO。

**边界（佣金为空）**：首次入库时联盟未给佣金 → est_commission_fen=null（「未知」，不视为 0），ESTIMATED 显示「已付款，返利待确认」、不展示金额、不显示「本单无返利」；之后收到数值按 R7 重算。已有数值后某次回传佣金缺失 → 保留上次数值，状态不变、不作废。

#### BR-FUND-08 细则 · 入账后扣回

- 状态：待决策（原为默认假设；扣回金额口径与流水类型属金额口径，决策人为财务，按 README §0.3 改为待决策）
- 默认值：入账后的部分退款写 CLAWBACK（sub_type=PART_REFUND），不写负向 SETTLE_ADJUST；佣金调整（R9b）不写 CLAWBACK，负差按 R9b 即时写负向 SETTLE_ADJUST、正差进 BR-FUND-09 候选（C-27 (g)，待财务确认）。理由：按原因区分流水类型——逆向交易一律 CLAWBACK，SETTLE_ADJUST 只表示联盟结算额差异，R1 差额分类和用户流水都更清楚。
- 决策人：财务
- 依赖平台能力：京东实际佣金归零能否与部分维权区分（BR-FUND-02、规划/09）；淘宝维权接口是否返回应扣佣金或新佣金
- 取代：
  - 规划/04 §4.1 O10：「CREDITED 收到 PART_REFUND → 写负向 SETTLE_ADJUST」
  - 规划/07 §2 08 订单管理：「部分退款写调整分录」
  - PRD修订_后端功能规划 §2.7：「idem_key={sub_order_id}:{user_id}:{role}:CLAWBACK:{seq}（seq 来源未定义）」
  - 规划/02 §8.3：「扣回为一张凭证同时借 USER_SELF、USER_PROMO、COMMISSION_REVENUE」
- 来源：规划/04 §1、§4.1 O9/O10；规划/01 E10 F-SET-04；规划/07 §2；PRD修订_后端功能规划 §2.7、§10.1 AC-MONEY-004；PRD v2.1 §11.4
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

**分录**：借 USER_\*:{uid}.available / 贷 UNION_RECEIVABLE:{platform}；ledger_type=CLAWBACK，sub_type ∈ FULL / PART_REFUND / RIGHTS / PUNISH。

**例（后端功能规划 §10.1 AC-MONEY-004；规划/05 编号待分配）**：自购入账 1000 → 提现 1000 已打款（available=0）→ 维权失效，CLAWBACK 1000 → available=−1000；申请提现返回 30302；另一新订单入账 600 → available=−400。

**例（部分）**：已入账 617/123/494（booked=1234），退款 1/2，联盟新 B=617（来源①，键 C{commission_version}）→ 新应得 308/61/248 → CLAWBACK 309、62，平台凭证 246；UNION_RECEIVABLE 净影响 −617；状态保持 CREDITED，booked=617。

**例（舍入使平台留存增加）**：B 10→9，两名受益人各 3300bp：旧份额 3/3、平台 4；新份额 2/2、平台 5 → 受益人各扣 1；平台差额 −1 → 借 UNION_RECEIVABLE 1 / 贷 COMMISSION_REVENUE 1；UNION_RECEIVABLE 净影响 −1+(−1)+1 = −1 = −(10−9)。

**幂等**：同一事件重放 → uniq_key 已存在，跳过；不同事件但重算净额差为 0 → 不写。

**不变量**：每 (子订单,受益人,角色) Σ CLAWBACK ≤ CREDIT + Σ 正向 SETTLE_ADJUST。

按 C-16 默认处理（入账后部分退款写 CLAWBACK sub_type=PART_REFUND，本条原写法不变；BR-TEXT-03 例 3 与第 13 节映射表随之修订），待财务确认。

#### BR-FUND-09 细则 · 月结补差

- 状态：待决策（原为默认假设；补差审批方式属金额口径，且与 BR-CALC-23 存在分歧 C-07，决策人财务）
- 默认值：负差（结算额低于已入账基数）在结算额写入的同一事务内即时记账；正差候选需财务发起、第二人复核后才记账；以结算明细为准。理由：负差延迟期间用户可能提走多入的钱，形成负余额与坏账；正差延迟不产生资损，而联盟结算数据解析或口径错误会批量给用户加钱，人工闸门可防批量资损；与 规划/02 §8.5「调账需第二人复核」一致。R1 首批稳定后可由财务决定改为自动批准小额正差。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - 规划/01 E10 F-SET-05：「月结不产生首次入账（未入账订单除外）」
  - 规划/04 §4.1 O8：「CREDITED 收到 PLATFORM_SETTLED 转 SETTLED，结算额≠已入账额时直接写 SETTLE_ADJUST（无审批）」
  - PRD修订_后端功能规划 §2.7：「按 (batch_id, sub_order_id, user_id, role) 幂等（重建批次会重复补差）」
  - PRD v2.1 §9.3：「RECEIVED 平台结算→PLATFORM_SETTLED，结算佣金与预估差异写 SETTLE_ADJUST（入账前补差）」
- 来源：规划/00 §3.2 D11；规划/01 E10 F-SET-05；规划/04 §1、§4.1 O7/O8；规划/02 §8.5；PRD修订_后端功能规划 §2.7、§0.4 B8；PRD v2.1 §11.4、§11.7；参考_花卷云功能查漏底稿 §7
- 需同步修改的规划文档：4 处（计数仅作记录，落点见 README §0.6）

**分录**：正差 借 UNION_RECEIVABLE / 贷 USER_\*.available；负差 借 USER_\*.available / 贷 UNION_RECEIVABLE；ledger_type=SETTLE_ADJUST，sub_type ∈ SETTLE_DIFF / PRICE_COMPARE / PRICE_PROTECT。价保、比价降佣形成的负差不经本条月结，由 BR-FUND-01 R9b 在订单同步事务内即时写（键 `ADJ:{sub_type}:v{commission_version}`，与本条 `ADJ:{seq}` 不冲突）；正差仍进本条候选。

**例（负差，即时）**：已入账 B=1234（617/123/494），联盟结算 B=1134 写入 → 同一事务应得 567/113/454 → 补差 −50/−10/−40，合计 −100，booked=1134，与 规划/02 §8.3 算例一致。重跑同一结算 → seq 不变、重算 diff=0，不写；只变动 1 次入账 + 1 次补差（F-SET-05 验收）。

**例（正差，复核后）**：结算 B=1300 → R1 生成候选 +33/+7/+26；财务发起、第二人复核后写凭证，booked=1300；复核前余额与 booked 不变。

**例（结算修正 A→B→A）**：seq1=1134 即时补差 −50（567）；seq2=1300 生成正差候选 +83；候选获批 → 650，booked=1300；seq3=1134 → 即时补差 −83（键含 seq3，不与 seq1 冲突），最终净额 567。若 seq3 在 seq2 候选获批前到达：seq2 候选作废，1134 = booked_base_fen，不写。

**边界**：settle_commission_fen = booked_base_fen 时不补差；负差即时补差使 available 变负时按 BR-FUND-10、BR-WDR-05 (a) 处理。

**差错单类型**：结算有、我方 ESTIMATED（收货同步缺失）；结算有、我方 VOID；结算有、我方 CLAWED_BACK；结算有、我方无订单（漏单）；我方 CREDITED、结算无（多单）；API 结算额与明细不一致。

**时点**：各平台结算状态出现时点与回款日待 规划/09 实测，R1 调度按实测结果配置；正差批次未批准前余额不变。补差负向时发站内信并附原因。

按 C-07 默认处理（负差即时记账、双人复核只用于正差），待财务确认。

#### BR-FUND-10 细则 · 负余额规则

- 状态：已确认
- 默认值：无（已确认，按规则执行）
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 §2.7、§2.9：「为负期间申请提现返回 30202」
- 来源：规划/01 E10 F-SET-04；规划/02 §8.3、§8.4；规划/04 §7 错误码 30302；PRD修订_后端功能规划 §2.7 负余额、§2.8 记账规则 5；PRD v2.1 §11.4

**展示**：可提现 = max(available_fen, 0)；待抵扣 = max(−available_fen, 0)，钱包显示「待抵扣 ¥x，后续返利将优先抵扣」。

**例**：SELF available=−400，新入账 REBATE_CREDIT 600 → available=200，可提现 200；PROMO 余额不受影响。

**并发**：提现冻结与扣回并发时，均按 account_id 行锁串行；冻结先提交则扣回照常把 available 扣负，frozen 不动；已冻结未打款的提现单按 BR-WDR-05 (a) 处理。

**错误码映射**：后端功能规划的 30202 在 规划/04 中是「订单不可找回」，本规则统一用 30302「余额为负，暂不能提现」；与账务差异冻结（30303，data.reason=account_frozen，BR-FUND-19）同时满足时按 BR-WDR-03 校验顺序优先返回 30303(account_frozen)。

按 C-03 默认处理（账务差异冻结改用 30303 account_frozen，30306 只表示提现开关关闭），待负责人确认。

#### BR-FUND-11 细则 · 负余额跨账户提现限制

- 状态：待决策
- 默认值：任一账户为负即两账户均禁止提现；理由：规划只写「负余额期间禁止提现」「两账户不互抵」，未说明另一账户能否提现，按资损优先取保守口径。
- 决策人：财务
- 依赖平台能力：无
- 取代：无
- 来源：规划/01 E10 F-SET-04；规划/04 §4.2 W1 守卫「余额非负」；PRD修订_后端功能规划 §2.7 负余额
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

**例**：SELF=−1000，PROMO=5000 → 申请 PROMO 提现 3000 返回 30302（data.account=SELF）；SELF 被后续入账抵平到 ≥0 后，PROMO 可正常提现。

**错误码与已有提现单**：申请返回的错误码（30302）、另一账户已冻结未打款提现单的处理，均见 BR-WDR-05 (a)，本条只维护「两账户都禁提」这一决策。

**不采用该规则时的风险**：用户自购订单入账后退款使 SELF 为负，同时提走 PROMO 余额后不再使用，负余额只能核销为坏账。

按 C-08、C-21 默认处理（另一账户的非终态单按 BR-WDR-05 (a) 记 blocked_reason=NEGATIVE_BALANCE_OTHER），待财务确认。

#### BR-FUND-12 细则 · 负余额坏账核销

- 状态：待决策（原为默认假设；核销最低金额 ledger.bad_debt_min_fen 待财务给出，见 6.3 第 10 条，按 README §0.3 改为待决策）
- 默认值：90 天、金额阈值 0、双人审批；理由：规划/06 Q-B2 默认值；PRD 的「≥阈值进人工追偿清单」阈值未定，暂取 0。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD v2.1 §11.4：「负余额超 90 天且金额 ≥阈值（待确认）进人工追偿清单」
- 来源：规划/01 E10 F-SET-04；规划/06 Q-B2；规划/02 §8.3；规划/04 §2.4；PRD修订_后端功能规划 §2.7 坏账；PRD v2.1 §11.4
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**例**：SELF 于 2026-11-20 被扣至 −800 → negative_since=11-20；至 2027-02-18（第 90 天）仍为 −800 → 生成候选单；批准前入账 500 使余额为 −300 → 批准时核销 300，available=0。若 12-01 入账 800 抵平，negative_since 清空，不生成候选。

**核销后**：后续入账正常计入余额，不追溯追偿；用户标记 risk（风控尚无 BR 主题，以 规划/01 E17 风控为准）。

**个人信息**：关联标记只用于提现风控，处理目的须在隐私政策「风控与反作弊」条款中列明（见 BR-ID-35、BR-ID-12）；标记不向用户展示内部依据，用户可经客服申诉，申诉结果写审计。

**阶段**：负余额报表 M-内测；核销操作在首个候选可能出现前（首笔真实入账日 + 90 天）上线。人工追偿清单与核销候选单合并。

#### BR-FUND-13 细则 · 两个账户与余额性质

- 状态：已确认
- 默认值：无（已确认，按规则执行）
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - PRD v2.1 §11.1：「用户账户 self_rebate、promo_income（命名）」
  - PRD修订_后端功能规划 §2.8：「U_SELF_AVAIL/U_SELF_FROZEN、U_PROMO_AVAIL/U_PROMO_FROZEN（命名）」
- 来源：规划/00 §4、§3.2 D12；规划/04 §2.2、§2.4；规划/02 §8.2；规划/07 §4 #9、§5；PRD v2.1 §11.1；PRD修订_后端功能规划 §2.8

| 账户 | 可入流水 |
|---|---|
| SELF | REBATE_CREDIT、CLAWBACK、SETTLE_ADJUST、提现类、ADMIN_ADJUST、BAD_DEBT_WRITEOFF、REWARD(P1) |
| PROMO | SHARE_CREDIT、REFERRAL_CREDIT、CLAWBACK、SETTLE_ADJUST、提现类、ADMIN_ADJUST、BAD_DEBT_WRITEOFF |

**所得类型**：income_type 不由账户决定，按 (ledger_type, sub_type) 读配置 tax.income_type_map；默认值与税目见提现/税务主题（D12，取得税务师书面意见前为默认假设，决策人财务）。

**例**：用户 A 分享商品给 B，B 下单 → B 是买家不获 SELF（share 订单买家是否计返利见 BR-ATTR），A 的 PROMO 获 SHARE_CREDIT；A 的直推上级获 REFERRAL_CREDIT（DIRECT）到 PROMO。

科目名称以 ledger_accounts 唯一键 (app_id, owner_type, owner_id, account_type) 为准。

#### BR-FUND-14 细则 · 冻结与已提现资金变动

- 状态：默认假设
- 默认值：打款中资金保留在 frozen，去掉 frozen→WITHDRAW_IN_TRANSIT 这一步；理由：用户看到的「冻结中」直接等于 frozen_fen，打款在途金额可由提现单状态查询，R2 对账不依赖在途科目。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - 规划/02 §8.3：「进入打款：借 USER_\*.frozen / 贷 WITHDRAW_IN_TRANSIT；打款成功：借 WITHDRAW_IN_TRANSIT / 贷 CASH_ALIPAY；打款失败/驳回借方含 WITHDRAW_IN_TRANSIT」
  - 规划/04 §4.2 W4、W5、W6：「冻结 → 在途；在途 → 出金；在途 → 可用」
  - PRD修订_后端功能规划 §2.8：「FREEZE 的 sub_type 含 risk（风控冻结移动资金）」
- 来源：规划/04 §2.4、§4.2；规划/02 §8.2、§8.3；规划/01 §5 J6、F-WDR-01；PRD修订_后端功能规划 §2.8、§3.3
- 需同步修改的规划文档：5 处（计数仅作记录，落点见 README §0.6）

**例**：PROMO available=5000，有一张 PENDING_REVIEW 提现单 3000、一张 PAYING 提现单 1000 → frozen_fen 必须 = 4000（冻结中 ¥40）；该会员随后被风控冻结 → available、frozen 均不变，只是不能再申请与执行提现。各步的分录与含税费的例子见 BR-WDR-09。

**已提现金额** = Σ 终态 PAID_API/PAID_MANUAL 提现单 amount_fen；到手金额 = amount − fee − tax。

**冻结中（附原因）**：原因 = 对应提现单状态文案（审核中/打款中）；风控冻结以账户横幅单独提示，不计入冻结中金额。提现规则数值、审核、打款流程见 BR-WDR。

#### BR-FUND-15 细则 · 流水类型与映射

- 状态：默认假设
- 默认值：采用 规划/04 §2.4 的 13 种命名（用户已确认命名以 规划 为准）；类型集合与科目仍需财务在 specs/ledger-rules.md 签字。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD v2.1 §11.2：「流水类型 15 种（CREDIT_SELF_REBATE…ADMIN_ADJUST_OUT，含 CREDIT_INDIRECT_COMMISSION）」
  - PRD修订_后端功能规划 §2.8：「entry_type 15 类（INVITE_L1_CREDIT、INVITE_L2_CREDIT、FREEZE、UNFREEZE、TAX_WITHHELD、ACTIVITY_REWARD、BAD_DEBT_WRITE_OFF、OPENING_BALANCE 等）」
- 来源：规划/04 §2.4；规划/00 §6、§3.2 D8；PRD v2.1 §11.2；PRD修订_后端功能规划 §2.8；开发任务拆解 H-06；参考_花卷云功能查漏底稿 §7
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**sub_type 值域**：CLAWBACK：FULL / PART_REFUND / RIGHTS / PUNISH；SETTLE_ADJUST：SETTLE_DIFF / PRICE_COMPARE / PRICE_PROTECT；REFERRAL_CREDIT：DIRECT（只此一值）；REWARD：newbie / checkin / invite；ADMIN_ADJUST：调账原因码（含 RESTORE，见 BR-FUND-22；必填原因与操作人）。

**用户侧名称**：各 ledger_type 的用户侧名称只在 BR-TEXT-19（字典 ledger_type.&lt;CODE>.name）维护；按 C-02 默认方案 A，WITHDRAW_PAID 为「提现到账」，若负责人改选方案 B 则为「提现成功」，只改字典。

**映射表**：

| PRD v2.1（15 种） | 后端功能规划 | 规划 ledger_type |
|---|---|---|
| CREDIT_SELF_REBATE | REBATE_CREDIT | REBATE_CREDIT |
| CREDIT_SHARE_REBATE | SHARE_CREDIT | SHARE_CREDIT |
| CREDIT_DIRECT_COMMISSION | INVITE_L1_CREDIT | REFERRAL_CREDIT(DIRECT) |
| CREDIT_INDIRECT_COMMISSION | INVITE_L2_CREDIT | 不使用（D8：只做直推一层，契约不定义间推类型） |
| CLAWBACK_REBATE / CLAWBACK_COMMISSION | CLAWBACK | CLAWBACK |
| SETTLE_ADJUST | SETTLE_ADJUST | SETTLE_ADJUST |
| WITHDRAW_FREEZE | FREEZE | WITHDRAW_FREEZE |
| WITHDRAW_UNFREEZE | UNFREEZE | WITHDRAW_RETURN |
| WITHDRAW_PAYOUT | WITHDRAW_PAID | WITHDRAW_PAID |
| WITHDRAW_FEE | WITHDRAW_FEE | WITHDRAW_FEE |
| TAX_WITHHOLD | TAX_WITHHELD | TAX_WITHHOLD |
| REWARD | ACTIVITY_REWARD | REWARD |
| ADMIN_ADJUST_IN / _OUT | ADMIN_ADJUST | ADMIN_ADJUST(±) |
| — | BAD_DEBT_WRITE_OFF | BAD_DEBT_WRITEOFF |
| — | OPENING_BALANCE | 不使用（D1 不迁移） |

**例**：流水一条「订单扣回（部分退款） −¥3.09 · 订单 2026…1234 · 余额 ¥12.00」；提现 ¥100 → 流水「提现冻结 −¥100.00 · 余额 ¥20.00」，打款成功后另一条「提现到账 ¥100.00（实际到账 ¥97.00，税 ¥2.00，手续费 ¥1.00）」。平台留存凭证不在用户流水出现。

按 C-02 默认处理（提现侧用「到账」，WITHDRAW_PAID 汇总条目名称随 BR-TEXT-19），待负责人确认。

#### BR-FUND-16 细则 · 复式记账硬约束

- 状态：已确认
- 默认值：无（已确认，按规则执行）
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 §2.8 记账规则 1：「分录 direction（借/贷）+ amount_fen > 0（与 规划 带符号口径不同，以 规划 为准）」
- 来源：规划/02 §1 原则 3/8、§8.1、§11；规划/00 §3.2 D11；规划/01 E10 F-SET-01；规划/05 §3.3、§7；PRD修订_后端功能规划 §1.7、§2.8 记账规则 1–6；PRD v2.1 §11.1；开发任务拆解 BF-02、QA-01/02
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

**加锁流程**：一锁（FOR UPDATE 用户账户行）→ 二判（uniq_key 是否存在、余额是否满足 BR-FUND-10）→ 三写（凭证、分录含 balance_after_fen、余额缓存）→ 四提交。

**例**：REBATE_CREDIT 617：分录① UNION_RECEIVABLE:taobao +617；分录② USER_SELF:42.available −617；Σ=0；USER_SELF:42.available_fen 从 1000 变 1617，分录② balance_after_fen=1617。

**错误更正例**：误调账 +500（ADMIN_ADJUST，uniq_key=ADJ:9001）→ 红冲凭证 −500（uniq_key=ADJ:9001:REVERSE）→ 重记正确的 +50。

**强一致**：余额、分录、rebate_status、提现状态只在同一 PG 事务内变更；outbox 事件只驱动推送、风控、看板、trace。

**分工**：凭证粒度、科目、红冲规则由财务在 specs/ledger-rules.md 签字；锁顺序、缓存策略等实现细节代理可自定。

#### BR-FUND-17 细则 · 资金话术与状态对应

- 状态：待决策（原为默认假设；「返利到账」指哪个状态须由 08 唯一定义（现为 BR-TEXT-01，README §1.2 为索引），与 BR-TEXT-01、BR-WDR-25 存在分歧 C-02，决策人改为负责人）
- 默认值：display_status 派生顺序如下表；术语用词按 C-02 默认（BR-TEXT-01 方案 A），方案 A/B 的内容与理由只在 BR-TEXT-01 维护。两方案下派生条件与 display_status 枚举不变，C-02 拍板只改 BR-TEXT-01、02、06 与 /v1/dict 字典，不改本条。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 规划/00 §2：「「确认收货 15 天后返利入账」（承诺了固定天数，时点见 BR-FUND-04）」
  - 规划/04 §2.3 CREDITED 行：「用户文案「已到账」（订单侧改为「已入账」）」
- 来源：规划/04 §2.3、§2.4；规划/01 §5 J1、J6；PRD修订_后端功能规划 §2.16、§3.2 用户侧展示映射；PRD v2.1 §11.1 术语；README §1.2；BR-TEXT-01
- 需同步修改的规划文档：5 处（计数仅作记录，落点见 README §0.6）

用户术语与资金状态、字段的对应只在 BR-TEXT-01 术语对照表维护（钱包金额字段见 BR-FUND-18），提现状态文案只在 BR-TEXT-06 维护，README §1.2 为索引；本条不再列术语表（原表已删，内容均已在 BR-TEXT-01 覆盖）。

**订单 display_status 派生表**（从上到下取第一个匹配项；「文案（示意）」列为方案 A 示意，便于阅读，正式文字以 BR-TEXT-02、BR-TEXT-03 与字典为准，两处不一致时以 BR-TEXT-02 为准，本条只维护条件与顺序）：

| # | 条件 | display_status | 文案（示意） |
|---|---|---|---|
| 0 | rebate=UNATTRIBUTED | 不返回 | — |
| 1 | VOID | INVALID | 已失效（附原因） |
| 2 | CLAWED_BACK | CLAWED_BACK | 已扣回 |
| 3 | CREDITED 且无 CREDIT 凭证（B_credit=0） | NO_REBATE | 本单无返利 |
| 4 | CREDITED 且存在 CLAWBACK | CREDITED_PART_CLAWED | 已入账（部分扣回 ¥x） |
| 5 | CREDITED | CREDITED | 已入账（有补差时显示差额与原因，BR-TEXT-03） |
| 6 | ESTIMATED 且 platform=DEPOSIT_PAID（不看 B_est，也不看 hold） | DEPOSIT_PAID | 已付定金 |
| 7 | ESTIMATED/WAITING 且 B_est=0（B_est 为 null 不匹配） | NO_REBATE | 本单无返利 |
| 8 | hold=true | REVIEWING | 入账核对中 |
| 9 | rights_pending=true | RIGHTS_PENDING | 售后处理中，入账暂停 |
| 10 | WAITING 且该平台 credit.enabled=off（BR-CALC-03、BR-FUND-04） | CREDITING | 入账核对中（不显示日期） |
| 11 | WAITING 且结算未记录，且（低于日结门槛，或 orders.credit_requires_settle=true（BR-CALC-15、BR-CALC-25；C-27 (e)）） | WAITING_SETTLE | 已收货，等待联盟结算后入账 |
| 12 | WAITING 且 expected_credit_date 早于今天（+08:00） | CREDITING | 入账核对中 |
| 13 | WAITING | WAITING | 已收货，预计 MM-DD 入账 |
| 14 | ESTIMATED | PAID | 已付款，返利待确认 |

**B_est 为空**：orders.est_commission_fen 为 null（从未收到联盟佣金数值，如 DEPOSIT_PAID 阶段未给佣金；已有数值后缺失不覆盖，见 BR-FUND-07）表示「未知」，不视为 0：不匹配第 7 行，不触发 BR-FUND-07 的 COMMISSION_ZERO，不向用户展示金额（ESTIMATED 按第 14 行「已付款，返利待确认」、WAITING 按第 10–13 行）；WAITING 且入账基数（BR-FUND-05）为 null 时入账任务跳过该单并告警，不按 0 入账。第 6 行先于第 7 行，保证付定金阶段 B_est=0 或 null 时显示「已付定金」而非「本单无返利」（BR-ATTR-01 例、10 AC-S1-24 ②、AC-S2-12-TB）。

**CREDITING 的两种来源**：第 10 行（平台入账开关 off）与第 12 行（预计入账日已过）共用 display_status=CREDITING 与字典 key `order_status.CREDITING`，不新增枚举；两者都不显示日期（第 10 行 expected_credit_date=null；第 12 行按 BR-TEXT-02 不展示已过期的日期）。BR-TEXT-02 该行的「对应双状态」说明应同步补上第 10 行条件（判定以本表为准）。

**例**：客服或 Agent 被问「我的返利到账了吗？」—先调订单接口取 display_status：得到 WAITING（expected_credit_date=2026-10-17）时按字典 `order_status.WAITING` 渲染；得到 CREDITED 时按 `order_status.CREDITED` 渲染；不得在接口返回前凭对话内容推断状态或金额。用词按 BR-TEXT-01，提现问题按 BR-TEXT-06。

术语与禁用词按 C-02 默认处理（BR-TEXT-01 方案 A；禁用词归 BR-TEXT-13），待负责人确认；本条派生条件与 C-02 无关。

#### BR-FUND-18 细则 · 钱包汇总与资产快照口径

- 状态：默认假设
- 默认值：待入账 = 仅 WAITING（已收货），预估（已付款未收货）单列 estimated_fen；快照 00:01 写入且先于入账任务。理由：只有已收货订单才有预计入账日，J6 要求待入账附预计日期；快照先于入账保证余额与待入账口径时点一致。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 规划/04 §6.4：「两个账户：可提现、待到账、冻结、负余额（待到账口径未定义）」
  - 规划/04 §3.2 asset_snapshots：「total_pending_fen（未区分 WAITING 与 ESTIMATED）」
  - PRD修订_后端功能规划 §2.8：「liability_snapshots 每天 00:15 写入」
- 来源：规划/04 §3.2、§6.4；规划/01 §5 J6、F-WDR-01、F-SET-08；PRD修订_后端功能规划 §2.8 负债日快照；参考_花卷云功能查漏底稿 §7
- 需同步修改的规划文档：4 处（计数仅作记录，落点见 README §0.6）

**例**：用户 SELF：available=−400，frozen=0，WAITING 两单 308+617（其中 617 维权中，308 的 expected_credit_date=10-17），ESTIMATED 一单 123，无提现、无冻结 → withdrawable=0，negative=400，pending_credit=925，pending_credit_paused=617，next_credit_date=10-17，credit_overdue=false，estimated=123，withdrawn=0，risk_paused_reason=null。若今天是 10-18 且 308 那单仍未入账 → next_credit_date=10-18，credit_overdue=true，页面显示「入账核对中」。

**为何快照先于入账**：若 00:05 先入账，D+1 入账的订单凭证 accounting_date=D+1，快照时又已不在 WAITING，这批金额既不在 D 日余额也不在 D 日待入账，R3「用户应付 vs 资产快照」每天少一截。00:00 至快照完成之间的非记账状态变化（如失效）计入 D 日。

**说明**：withdrawable_fen 只反映余额，是否满足最低额、次数、负余额跨账户限制以 GET /v1/withdrawals/rules 为准。钱包页展示可提现、待入账（附预计日期）、冻结中、已提现（文案按 BR-TEXT-01）；estimated_fen 供订单汇总与 Agent 查询使用。

**与 BR-TEXT-01 钱包汇总口径的关系**：字段名已与 BR-TEXT-01 对齐（原 waiting_fen→pending_credit_fen、waiting_paused_fen→pending_credit_paused_fen、next_due_date→next_credit_date、due_overdue→credit_overdue，新增 withdrawn_fen、risk_paused_reason）。取值口径以本条为准，两处不同的有：estimated_fen 按 BR-FUND-05 基数取法 × 快照比例计算（BR-TEXT-01 写 rebate_min_fen 合计）；预计日已过时 next_credit_date 返回今天并置 credit_overdue=true（BR-TEXT-01 写返回 null）。BR-TEXT-01 已按 C-19 改用本条字段名。

按 C-02 默认处理（用户侧「待入账」「入账核对中」），待负责人确认；按 C-17 默认处理（快照 D+1 00:01 写入，入账任务等快照完成，最晚 00:30），待财务确认。

#### BR-FUND-19 细则 · 账务不变量与日终校验

- 状态：默认假设
- 默认值：账户级差异冻结涉及用户提现；全局差异自动关闭自动入账并冻结涉及用户提现；理由：规划只写「冻结对应账户提现」，PRD 写「冻结自动任务」，按影响范围分两级处理，且全局差异时多入的钱不能被提走。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 §2.8 记账规则 7：「00:10 写 daily_balances 并校验（时间改为与 01:00 校验合并）」
  - PRD v2.1 §11.7：「任何差异冻结自动任务并告警（未分级）」
- 来源：规划/02 §8.4；规划/01 E10 F-SET-06、§7.2；规划/04 §7 错误码 30306；PRD修订_后端功能规划 §1.6、§2.8、§10.1 AC-MONEY-013；PRD v2.1 §11.7；开发任务拆解 BF-10、QA-01/02
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**例**：01:00 发现 USER_PROMO:42 缓存 5000、分录合计 4900 → P1 告警，生成差错单 E1，为用户 42 新增 withdraw_holds（reason=ledger_mismatch，source_ref=E1），SELF、PROMO 提现申请均返回 30303（data.reason=account_frozen）；财务调账复核、关闭 E1 时 step-up 解除该条记录。

**全局例**：发现 taobao:1234567 的 (用户 42, self) 有 2 张 CREDIT 凭证 → settle.auto.enabled=off，停止自动入账，用户 42 新增 withdraw_holds，两账户提现返回 30303(account_frozen)；值班人工处理后由有权限者 step-up 重新打开开关，差错单关闭时解除冻结记录。

**与 30302 同时满足**：用户 42 同时有生效冻结记录且 SELF available=−100 → 返回 30303(account_frozen)（BR-WDR-03 ⑦ 在 ⑧ 之前）；冻结解除后再申请 → 30302。

**⑧ 例**：订单 platform_status=INVALID 但 rebate_status=CREDITED（扣回事件丢失）→ 冻结该单全部受益人提现，差错单进人工，按 BR-FUND-08 补扣。

**测试**：以上不变量作为属性测试，PR 跑 1 万次、夜间 100 万次；真实 PG 并发测试覆盖并发提现、并发入账、BullMQ 重复投递。

按 C-03 默认处理（错误码 30306 改为 30303 data.reason=account_frozen），待负责人确认；按 C-09 默认处理（冻结只记在 withdraw_holds，不另设 users.withdraw_blocked_reason），待财务确认。

#### BR-FUND-20 细则 · 垫资敞口与入账开关

- 状态：待决策（原为默认假设；告警阈值 ledger.advance_alert_fen 待财务给出，见 6.3 第 10 条，按 README §0.3 改为待决策）
- 默认值：告警阈值由财务在 W1 给出，未给出前只展示看板不告警；按合计告警、平台分项只展示；开关默认 on。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 §2.8：「「月末差额进平台资金台账」写法删除，只有差错单关闭时才按核销凭证入账（本条沿用）」
- 来源：规划/01 §3 垫付营运资金；规划/02 §8.3、§8.5、§1 原则 8；规划/04 §10.2；PRD v2.1 §11.4；PRD修订_后端功能规划 §2.8；开发任务拆解 BF-11
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**垫资周期**：收货后约 15 天入账，联盟回款约次月 20 日前后（待核实，见 规划/09），平台最长垫付约 50 天。

**例**：10 月内入账合计 1,200,000 分、11-20 淘宝回款 1,150,000 分 → UNION_RECEIVABLE:taobao 余额 50,000 分，差额进 R1 差错单，不直接记损益。阈值 1,000,000 分时：11-19 合计 1,200,000 → 告警；11-21 回落到 50,000 → 不告警。

企业支付宝水位 W/P 与暂停打款规则见 BR-WDR-18、BR-WDR-17。

#### BR-FUND-21 细则 · 负余额时未打款的提现单

- 状态：待决策（随 §14.3 C-08、C-21，决策人：财务）
- 规则正文：负余额对非终态提现单的全部处理——W2/W4/W8 守卫、事件 account.went_negative 的写入与消费、同账户未打款单 W3 驳回（NEGATIVE_BALANCE）并退回冻结额抵扣负数、另一账户 blocked_reason=NEGATIVE_BALANCE_OTHER、PAYING 单经 W9 回到 APPROVED 后的处理——只在 BR-WDR-05 (a) 维护，默认值、取代项、例子与理由一并见 BR-WDR-05 细则。本条不再单独规定，编号保留供 C-08、C-21 与 规划/00–07、10、BR-TEXT-08 的既有引用定位。
- 2026-09-30 修订：原正文与 BR-WDR-05 (a) 重复维护同一套细则，合并到 BR-WDR-05 (a)；原例子（部分扣回、跨账户、PAYING 未发出）与「同账户为何驳回而不是暂停」已并入 BR-WDR-05 细则。

#### BR-FUND-22 细则 · 作废或扣回订单的平台恢复

- 状态：默认假设
- 默认值：平台恢复只经人工双人复核处理，不自动复活；处罚/黑名单作废不告警。理由：终态自动复活会与已发推送、已扣回余额冲突；恢复涉及资金，需第二人复核。
- 决策人：负责人
- 依赖平台能力：无
- 取代：无
- 来源：规划/04 §4.1 O4、O9；规划/02 §8.5；PRD修订_后端功能规划 §3.2
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

| # | 从 | 事件 | 守卫 | 到 | 记账 |
|---|---|---|---|---|---|
| R12 | VOID | ADMIN_RESTORE | 差错单存在；发起人 ≠ 复核人；step-up；platform_status ≠ INVALID | ESTIMATED 或 WAITING | 无 |
| R13 | CLAWED_BACK | ADMIN_RESTORE | 同上 | CREDITED | ADMIN_ADJUST(RESTORE) |

**例（R12）**：10-03 退款失效 → VOID(REFUND)；10-06 淘宝回传「订单成功」（买家撤销退款）→ P9 platform_status=RECEIVED，告警，差错单；10-07 复核恢复 → WAITING，credit_due_at 按 received_at 计算。

**例（R13）**：已入账 617/123/494 后全额扣回 → CLAWED_BACK；联盟恢复佣金 1234 → 差错单；复核恢复 → ADMIN_ADJUST +617/+123/+494，booked=1234，状态 CREDITED。

**例（不告警）**：黑名单命中作废的订单，平台照常推进到 RECEIVED → 只更新 platform_status。

#### BR-FUND-23 细则 · 月末三项核对

- 状态：默认假设
- 默认值：每月 1 日 01:30 对上月运行；等式 X1 = X2 + X3，差额 ≥1 分即告警并生成差错单，不自动冻结；「上月联盟预估佣金」等只列示。理由：花卷云底稿把「负债日快照 + 月末三项对平」列为易漏项；BR-FUND-19 的日终校验按账户比对分录与余额缓存，本条用提现单表与资产快照这两个独立来源做总量核对，能发现分录与业务单据之间的偏差；定位与冻结已由 BR-FUND-19 负责，本条不重复冻结。积分余额（花卷云第三项口径之一）属 P1 积分功能，MVP 无积分账户，不纳入；积分上线时另行新增条目。
- 决策人：财务
- 依赖平台能力：无
- 取代：无
- 来源：参考_花卷云功能查漏底稿 §7「负债日快照」、§16 #20；规划/02 §8.4 R3 内部对账（分录合计 vs 余额；用户应付合计 vs 资产快照）；规划/01 F-ADM-08
- 需同步修改的规划文档：规划/02 §8.4 R3 行补「月度三项核对（BR-FUND-23）」；规划/04 §3.2 差错单类型补「月末三项不平」（部分落实，登记于 README §0.6）

**计算**（单位分；「对用户余额的影响」贷记用户为正、借记为负）：

| 项 | 口径 | 数据来源 |
|---|---|---|
| X1 用户累计入账净额 | accounting_date ≤ M 月末日的用户 available 子户分录中，ledger_type ∈ {REBATE_CREDIT, SHARE_CREDIT, REFERRAL_CREDIT, REWARD, CLAWBACK, SETTLE_ADJUST, ADMIN_ADJUST, BAD_DEBT_WRITEOFF} 的影响合计；不含 WITHDRAW_FREEZE、WITHDRAW_RETURN | ledger_entries |
| X2 用户期末余额 | M 月末日 asset_snapshots：total_available_positive_fen − total_negative_fen + total_frozen_fen | asset_snapshots（BR-FUND-18） |
| X3 用户累计已提现 | 截至 M 月末迁移到 PAID_API/PAID_MANUAL 的提现单 amount_fen 合计（含税与手续费） | withdrawals |

**例**：上线至 10-31 累计：入账 1,000,000，扣回 −30,000，补差 −5,000，核销 +800 → X1=965,800；10-31 快照 available 正数合计 700,000、负数合计 1,200、frozen 50,000 → X2=748,800；已到账提现单合计 217,000 → X3=217,000；748,800 + 217,000 = 965,800，相等。若某提现单被误改 amount_fen 为 21,000（实际分录 WITHDRAW_PAID+FEE+TAX=20,000），X3 多 1,000 → 差额 −1,000，告警并生成差错单。

**边界**：月末日快照被标记 waiting_comparable=false 不影响本条（只用余额类字段）；月末日快照缺失时本条不运行，告警并在快照补写后由 finance 手动触发；上线日所在月份之前的月份不运行，上线当月按上线日至月末的数据照常核对（X1、X3 均从 0 起算，D1 不迁移数据）。

### 6.3 本主题未决问题

1. BR-FUND-01：是否采用 platform_status + rebate_status 双状态模型取代 规划/04 单一 order_status（默认采用），需负责人拍板。
2. BR-FUND-01 R2/R3、BR-FUND-03：分佣快照生成时点与等级、上级取值时点，现按 C-06 默认（生成时点按 BR-CALC-10，等级与上级取 paid_at，BR-CALC-12；原默认「找回单取批准时刻」已撤回），需负责人确认。
3. BR-FUND-04：预计入账日按「满 15×24 小时后首个 00:05 入账日」（约收货日+16 天）还是按自然日「收货日+15 天」（实际观察期不足 15 天），需负责人拍板。
4. BR-FUND-04：维权或 hold 期间 credit_due_at 是否顺延（默认不顺延，理由：维权结果已明确；替代：顺延维权持续时长），需负责人拍板；expected_credit_date 在维权 / hold 期间返回 null、解除后按 max(credit_due_at, received_synced_at, 解除时刻) 重算（G-16 默认），需负责人确认。
5. BR-FUND-11：一个账户为负时，另一账户是否仍可提现（默认两账户都禁提），需财务拍板。
6. BR-FUND-21（规则正文在 BR-WDR-05 (a)）：账户变负时同账户未打款提现单自动驳回（默认）还是暂停待回正，需财务拍板（对应 C-08）。
7. 淘宝/京东/拼多多订单接口中「确认收货」与「结算」是否为独立状态、各自时间字段名与出现顺序；淘宝「订单结算」状态出现时点与联盟回款日是否同一时点（BR-FUND-02），需进 规划/09 实测并附接口样例。
8. 各平台是否提供「维权处理中」信号、淘宝维权接口是否返回应扣佣金（BR-FUND-06、BR-FUND-08）；京东「实际佣金归零」能否与部分维权区分。
9. 核销型订单（美团、饿了么，均 P1）入账等待期是否不同于 15 天（后端功能规划 B12，W1），默认同为 15 天。
10. 财务需给出：已入账未回款告警阈值 ledger.advance_alert_fen、坏账核销最低金额 ledger.bad_debt_min_fen、specs/ledger-rules.md 的科目表、凭证粒度与流水类型签字（W1 周三前）。
11. 淘宝、京东、拼多多联盟实际结算/回款日（「次月 20 日前后」）待核实，影响 R1 调度与垫资测算。
12. 本主题用户文案（BR-FUND-04、06、15、17、18 中的示意文字）的用词随 C-02 与 BR-TEXT-01 方案 A/B，需负责人拍板；拍板后只改 BR-TEXT-01、02、06 与字典，本主题派生条件与字段不变。
13. BR-FUND-09：结算负差即时记账、正差双人复核（默认，C-07）还是所有补差都双人复核，需财务拍板。
14. BR-FUND-19：账务差异冻结记入 withdraw_holds（reason=ledger_mismatch）并返回 30303(account_frozen)（默认，C-03、C-09），需负责人（错误码）与财务（冻结记录方式）确认。
15. BR-FUND-05、BR-FUND-08：入账基数取法、凭证粒度与扣回流水类型（CLAWBACK vs 负向 SETTLE_ADJUST，C-16）已由默认假设改为待决策，需财务在 specs/ledger-rules.md 签字时一并确认。
16. BR-FUND-04、BR-FUND-17：credit.enabled.&lt;platform>=off 期间 WAITING 订单显示 CREDITING「入账核对中」、不给日期，商品详情与未收货订单不展示入账时点文案（默认，复用 CREDITING 枚举，不新增 CREDIT_PAUSED）；开关打开后积压订单由下一次任务处理，单批上限 settle.credit.max_orders_per_run 默认 5000，需负责人确认展示、财务确认上限取值。
17. BR-FUND-07、BR-FUND-17：DEPOSIT_PAID 阶段佣金变化不触发 COMMISSION_ZERO、付尾款时 B_est=0 按「本单无返利」不作废、佣金缺失不覆盖已有值（默认处理），需负责人确认。

---
