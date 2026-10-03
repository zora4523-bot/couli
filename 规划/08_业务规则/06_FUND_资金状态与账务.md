# 08 业务规则 · 6. 资金状态与账务（BR-FUND）

返回 [README](README.md)（使用规则、术语表、规则索引）

## 6. 资金状态与账务（BR-FUND）

本节规定：返利状态流转、入账时点与凭证、扣回与补差、负余额、单一余额、流水类型、不变量、月末核对与垫资、收益看板口径。共 25 条（已确认 16、默认假设 6、待决策 1、待验证 2）。

2026-10-03 功能对照补缺第 2 批（docs/changes/20261003-功能对照补缺.md「第 2 批」；「功能对照 G-xx / Q-xx」是该批缺口清单与待确认题的编号，与 规划/10 §6.1 的 G-xx、规划/06 的 Q-xx 不是同一套）：新增 BR-FUND-25「收益看板口径」（待决策，按功能对照 Q-10 默认 A 写，功能对照 G-11）。看板只做展示，不改任何入账、扣回与余额规则；其余条目不变。同日按评审改写「已结算」的聚合方式，写明红冲与重记怎样计入（变更记录 §2.8 第 5 条）。

2026-10-03 资金规则对齐（docs/changes/20261003-资金规则对齐.md，负责人批准：表 ① 同步项按条文草案、表 ② 选择项按保守默认）：联盟给的金额一律先按 BR-CALC-02 换算成分佣基数再用，记 booked_n_fen；日终等式按已入账联盟佣金减待补记额核对、受益人净额不为负；统一加锁顺序、锁后重读受益人状态；P 表补 P11–P15 与事件编码；结算批次补迁移表 SB1–SB9 与受益人补记项（BR-FUND-04 ⑫）；扣回与补差的净额计入恢复与改派凭证；BR-FUND-05、BR-FUND-08 改为已确认。各条在细则「取代」里登记旧写法；写回落点见变更记录 §13。同日评审后修改（变更记录 §13.6；同步修正，不改分佣比例、受益权与应得金额）：受益人补记项按待补记义务（beneficiary_credit_id）只记一次，延后的正差改用 `ADJ:DEFERRED:{beneficiary_credit_id}` 键（BR-FUND-04 ⑫、R5a、R14、BR-FUND-08）；补差在基数相等而联盟佣金不同时只调平台金额，并成对更新 booked_base_fen 与 booked_n_fen，基数为 0 仍记预留的订单同样由 R10 承接（BR-FUND-09、R10）。

本节按 §14.3 的建议（默认处理）改写了 C-01、C-02、C-03、C-06、C-07、C-08、C-09 涉及的条目，C-16、C-17 的默认处理与本节原写法一致；各条细则末尾注明所按的分歧编号与决策人，裁决前按默认处理实现。

2026-09-30 负责人拍板第一批（docs/changes/20260930-拍板第一批.md）：BR-FUND-01 与 C-01、C-06 已确认；BR-FUND-04 入账方向改为跟随联盟月结批量入账（§3），流程参数待决策（§6），本主题其他条目中依赖逐单入账的写法已对齐或在细则末行登记待改。2026-09-30 负责人补充（变更记录 §10 第 1、2 项）：月结账单由系统在月结账单日按联盟接口返回的结算数据自动生成（不由财务上传），后台确认后立即或定时结算；预计结算月份以联盟返回的结算时间为准，未返回时按确认收货月 + 1 推算；本主题中「账单导入」「逐单比对」的写法已随 BR-FUND-04 改写。

2026-10-01 负责人拍板第二批（docs/changes/20261001-拍板第二批.md）：BR-FUND-04 月结入账方向与流程参数按 9-30 默认确认（FUND-01、FUND-07），原登记「待改，未重写」的月结同步项（BR-FUND-09、17、18、20）已改写；已确认的还有 BR-FUND-09 补差审批（FUND-11）、BR-FUND-11 与 BR-FUND-21 负余额提现（FUND-12）、BR-FUND-12 坏账核销含注销负余额（FUND-09）、BR-FUND-17 与 BR-FUND-18 用户口径「预估 / 已结算 / 预计结算月份」（OPS-01）、BR-FUND-20 垫资告警机制、BR-FUND-22 申诉恢复（FUND-14、OPS-07）；补写 BR-FUND-08 注销后扣回记平台坏账（FUND-09）、BR-FUND-13 所得类型（FUND-04）、BR-FUND-14 未成年推广收益不移动资金（FUND-10）；新增 BR-FUND-24 人工调账（FUND-13，代理起草，负责人 2026-10-01 授权按推荐）。BR-FUND-12、BR-FUND-20 的数值（坏账核销天数与门槛、垫资告警线）原定随 FUND-21 一次给出，已由 §8 ADD-03 改为开发期占位、上线前超管在后台填写（见下段）。

2026-10-01 晚负责人补充决定（docs/changes/20261001-拍板第二批.md §8，优先于前述写法）：ADD-06 用户只有一个余额（科目 USER_BALANCE，account_balances 每用户一行），不分 SELF / PROMO，收入来源只由 ledger_type + sub_type 区分，BR-FUND-10、11、13、14、18、19、21、23、24 与分录模板随之改写；ADD-05 资金操作（补差、坏账核销、人工调账、订单恢复、黑名单扣回确认、改派）超管或被勾选该权限的账号一人即可完成，须 step-up、写审计，取代各处「发起人 ≠ 复核人 / 第二人复核」；ADD-07 余额为负不能注销（BR-ID-27，30416），BR-FUND-12、BR-FUND-24 中注销时负余额当即核销的写法取消；ADD-03 经营数值开发期用占位值、上线前超管在后台填写，取代「W1 随 specs/ledger-rules.md 一次给出」。本主题中 finance、ops、super 等后台角色名按 ADD-04 读作「超管，或被勾选该操作权限点的后台账号」（权限点清单见 规划/04 §11）。

2026-10-01 用语同步（docs/adr/0001-技术栈基线.md §3，规划/11 §9.1；00 §8 第 ① 类）：BR-FUND-01、BR-FUND-07 正文与 BR-FUND-16、BR-FUND-19 细则里的事件与队列叫法改为中立说法（「领域事件」「与业务写入同一事务入队」「任务重复投递」）。规则含义、取值与状态均不变。

### 6.1 规则一览

| 编号 | 规则 | 状态 | 影响面 |
| --- | --- | --- | --- |
| BR-FUND-01 | **订单双状态模型**<br>每个子订单必须维护两个互相独立的状态字段：`platform_status`（平台订单状态，唯一写者 order-sync，只由联盟数据经平台状态映射表驱动，见 BR-FUND-02）与 `rebate_status`（返利状态，唯一写者 settlement）。`hold`、`rights_pending` 的唯一写者也是 settlement：hold 只经后台 hold/unhold 接口或风控引擎调用 R11 迁移；order_rights 只经 settlement 提供的命令写入（order-sync、rights-imports 调用该命令），rights_pending 在 order_rights 写入或变更的同一事务内重算（存在 status ∈ {PROCESSING, WAIT_COMMISSION} 的记录即为 true）。两个状态都只能经 specs/state-machines/\*.yaml 生成的 transition() 以 CAS（UPDATE … WHERE id=:id AND status=:from，row_version+1）迁移；影响 0 行视为并发冲突或非法迁移，重读后按迁移表判断。表外事件：状态与余额均不变；内部调用抛 IllegalTransition，不重试，记日志并告警；后台 API 返回 20902「订单状态已变化，请刷新后重试」（data.resource=order）。判定先于写库：先按迁移表判定本次事件，属于表外事件或 P10（倒退）的，本次报文不更新订单的任何列（P10 整条不落库为负责人 2026-10-03 资金规则对齐决-12 选 A）；与当前状态相同不是迁移、不算表外事件（P15），本次报文的其余数据照常处理。订单相关的余额与分录只能在该子订单 rebate_status 迁移（含状态不变的自迁移 R5a、R7、R9、R9b、R10、R14）的同一 PG 事务内变更，不得依赖领域事件（异步任务）完成；提现、坏账核销、人工调账、联盟回款不伴随订单迁移，分别按 BR-WDR-09（账户约束 BR-FUND-14）、BR-FUND-12、BR-FUND-16、BR-FUND-20。用户可见订单状态 display_status 由 (platform_status, rebate_status, hold, rights_pending, 金额) 派生，不入库（BR-FUND-17）。同一子订单的所有处理按 order_key（`{platform}:{sub_order_id}`，BR-FUND-05）用 pg_advisory_xact_lock 串行。 | 已确认 | orders.status 拆为 orders.platform_status、orders.rebate_status、orders.hold、orders.rights_pending；orders.locked、row_version；order_status_history 增加 field 列（platform/rebate）；specs/state-machines/order-platform.yaml、order-rebate.yaml；测试 ID SM-ORD-O&lt;n> → SM-PLT-P&lt;n>、SM-REB-R&lt;n>；order_rights 写入命令（settlement 提供）；错误码 20902（data.resource=order）；GET /v1/orders、GET /v1/orders/{id} 的 status 字段改为派生 display_status；后台订单列表筛选；三端订单页状态展示 |
| BR-FUND-02 | **平台状态映射与可入账事件**<br>platform_status 只能由 specs/order-status-map/&lt;platform>.csv 把平台状态码映射为内部事件后按 BR-FUND-01 的 P 表迁移；映射表之外的状态码必须告警并写入待处理表，不得丢弃、不得猜测；写入待处理表时订单返利状态为 ESTIMATED 或 WAITING 的，由系统以 actor=system:risk 置 hold（原因码 UNMAPPED_STATUS，BR-FUND-06），待处理记录关闭后由人工 unhold（负责人 2026-10-03 资金规则对齐决-05 选 A；开关 order_sync.unmapped_status_hold.enabled，默认 on，off 时只告警、不 hold）；已入账的订单不能 hold，只告警进待处理表，由人工按 BR-FUND-08 处理。平台状态码或接口表示联盟处罚（含审核失败、违规判定）的，映射为内部事件「处罚」（PLATFORM_PUNISH）：platform_status 不变，经 settlement 命令写 order_rights（type=PUNISH，status=SUCCEEDED），返利状态按迁移 R6 或 R8，原因码 PUNISH；不得映射为「失效」。哪些码属于处罚以 规划/09 实测为准，写入 specs/order-status-map/&lt;platform>.csv；实测前这些码不进映射表，出现时按映射表之外的状态码处理。可入账事件由 specs/creditable-events.yaml 定义：taobao、jd、pdd = 确认收货；meituan = 订单完成或核销；P1 平台 vip、douyin = 确认收货，eleme = 订单完成或核销（P1 平台接入时按 规划/09 实测结果确认后才写入该文件，未写入的平台订单不进入 WAITING）。平台返回的无时区时间一律按 +08:00 解析。乱序与去重按 BR-ATTR-01（attr.mtime_ordering.&lt;platform>，默认 false 时只看 content_hash）。received_at 必须取平台返回的收货/完成时间，不得用我方同步时间代替；平台只给出「已结算」而未给出收货时，视为已收货，received_at 取平台结算时间字段，按 P5 迁移到 SETTLED（首次入库即已结算按 P12）。received_at 一旦写入不再覆盖（包括之后回传的真实收货时间），settle_period 不重算（BR-FUND-04）；后到的真实收货时间另存 orders.platform_received_at 备查。平台未返回可用时间字段时订单进待处理表，不进入 WAITING（BR-FUND-01 R4 守卫）。Adapter 只在平台明确处于已结算状态时写 settle_commission_fen 与 order_settlements（source=API，BR-FUND-09）；预估与结算共用同一字段的平台（拼多多），结算前只写 est_commission_fen。哪些原始状态算已结算写在 specs/order-status-map/&lt;platform>.csv；实测前拼多多只认 order_status 5，3（审核成功）不算。 | 待验证 | specs/order-status-map/&lt;platform>.csv（含处罚类码与「已结算」原始码的标注）；specs/creditable-events.yaml；order_rights.type=PUNISH；orders.hold_reason=UNMAPPED_STATUS；配置 order_sync.unmapped_status_hold.enabled；orders.received_at、platform_received_at、platform_modified_at、settled_at；order_settlements；order_sync 待处理表；规划/09 平台能力验证表；验收用例：确认收货与结算乱序回放、更新时间相等内容不同回放 |
| BR-FUND-03 | **预估返利生成与变更**<br>订单已归因到用户且 platform_status ∈ {PAID, RECEIVED, SETTLED} 时，每个受益人的预估返利（分）= 按该订单唯一一份分佣快照（生成时点按 BR-CALC-10：已归因且 platform_status 首次 ∈ {PAID, RECEIVED, SETTLED} 的同一事务内生成，DEPOSIT_PAID 阶段不生成；等级与上级取 paid_at 时刻，按 BR-CALC-12；生成后不再改）的比例拆分当前基数 B_est 所得份额（拆分与舍入规则见 BR-CALC）；platform_status=DEPOSIT_PAID 或 rebate_status=UNATTRIBUTED 时预估计为 0 且不向用户展示金额。ESTIMATED 与 WAITING 阶段不得写任何分录、不得改变 account_balances。联盟回传的佣金或数量（部分退款、价保、比价降佣）变化时，在订单 upsert 的同一事务内更新 est_commission_fen、refunded_quantity，commission_version+1，预估随之重算；B_est 由有效联盟佣金按 BR-CALC-02 换算，settle_commission_fen 非空后预估佣金单独变化只存档、预估不变（BR-CALC-02 取值阶段）。首次入库 B_est=0 的已归因订单为 ESTIMATED，展示「本单无返利」；B_est 由 >0 变为 0 按 BR-FUND-07 处理。 | 默认假设 | orders.est_commission_fen、refunded_quantity、commission_version；commission_splits（生成时点见 BR-CALC-10）；GET /v1/orders 预估金额字段；推送见 BR-TEXT-09；订单页 |
| BR-FUND-04 | **入账时点与入账任务**<br>负责人已定方向（2026-09-30，变更记录 §3）：可提现入账跟随联盟月结，不再按确认收货后固定天数逐单入账；负责人补充（2026-09-30，变更记录 §10）：月结账单由系统在月结账单日按联盟接口返回的结算数据自动生成，不由财务上传，后台人工确认后立即或定时结算；预计结算月份以联盟返回的结算时间为准。流程参数（③–⑪）由负责人 2026-10-01 确认按 9-30 默认（拍板第二批 FUND-01、FUND-07）。<br>① 预估：订单付款并经订单同步入库，即按 BR-FUND-03 生成预估收益（不可提现，不写分录）；order-sync 每日至少轮询一次联盟订单接口，更新平台状态、佣金与联盟结算数据（BR-FUND-02；联盟返回结算佣金时写 settle_commission_fen（BR-CALC-02），返回结算时间时写 union_settled_at）。<br>② 待入账：platform_status 进入 RECEIVED 或 SETTLED 时按 R4 进入 WAITING，同一事务写 received_synced_at（取注入的 Clock）与结算周期 settle_period（YYYY-MM）= received_at 所在自然月（+08:00，取法读配置 settle.period_basis.&lt;platform>，默认 received_at）；settle_period 写入后不因 received_at 回补而重算。<br>③ 月结账单生成：每月月结账单日（读配置 settle.bill_day，默认 24，取值 22–28，各平台同一天，+08:00）当日资产快照完成（BR-FUND-18）后，系统自动为账单月 M（= 上一自然月）生成一份月结账单（bill_id = M），生成期间账单状态为「出账中」。账单范围：credit.enabled.&lt;platform>=on 的平台中，rebate_status=WAITING、settle_period ≤ M，且截至生成开始时刻已有联盟结算数据（settle_commission_fen 非空）的子订单；另列 settle_period=M 而仍无联盟结算数据的子订单供 ④ 判「应结未结」。联盟结算数据的来源读配置 settle.statement_source.&lt;platform> ∈ {api, upload}，默认 api（order-sync 从联盟接口同步）；upload 只作该平台联盟接口不可用时的备用：finance 在账单生成前上传该平台联盟结算明细，逐行写 order_settlements(source=STATEMENT)（BR-FUND-09），视同联盟结算数据，校验规则相同。<br>④ 一致性校验：对账单范围内每个子订单，同时满足以下条件的进入批次候选：\|B_settle − 分佣快照当前版本 base_fen\| ≤ settle.batch.match_tolerance_fen（默认 0 分；B_settle = 联盟结算佣金按 BR-CALC-02 换算的分佣基数，当前版本 = 最大 commission_version，BR-CALC-10；差错单结论为「以联盟为准」的视为一致）；hold=false；rights_pending=false。不一致的生成差错单「账单金额不一致」，不入账；hold 或维权中的记「暂缓」，不生成差错单、不入账；settle_period=M、未 hold、未维权而截至生成开始仍无联盟结算数据的生成差错单「应结未结」，订单保持 WAITING，联盟结算数据到达后进补充批次或下一期账单；联盟结算数据对应我方 ESTIMATED / VOID / CLAWED_BACK 或我方无单（上传备用时）的生成差错单（类型沿用 BR-FUND-09）；rebate_status=CREDITED 的不进批次，按 BR-FUND-09 补差。<br>⑤ 生成批次：候选按 (platform, M) 生成结算批次（状态 DRAFT），每批最多 settle.batch.max_orders 个子订单（默认 5000），超出按 order_key 升序拆为多批；全部批次生成完后账单状态为「已出账」；批次状态迁移见细则「结算批次迁移表」（SB1–SB9）。账单与批次列明各平台子订单数、联盟结算佣金合计、各受益人份额与平台留存合计、差错单数与暂缓数。<br>⑥ 人工确认与结算方式：finance 或 super 在 step-up 后在月结账单上确认（一次确认该账单全部 DRAFT 批次，记录 confirmed_by、confirmed_at；默认单人确认），并选择结算方式：立即结算（默认选中，确认后立即执行）或定时结算（指定 scheduled_at，须晚于确认时刻，且保存时不得落在资产快照的名义时段内（每日 00:00 至 00:30，BR-FUND-18）；到时自动执行，执行时当日快照仍未完成的等快照完成，见 ⑦；执行前可撤销定时，批次回到 DRAFT）；或驳回（批次 CANCELLED，记原因，批内订单保持 WAITING）。未确认的批次不得入账。账单状态由批次状态派生（出账中 / 已出账 / 待结算 / 结算中 / 已结算），不另存一套状态，映射见细则。<br>⑦ 批量入账：批次 CONFIRMED 且到达执行时刻后执行，每个子订单单独一个 PG 事务；事务内按 order_key 加锁重读，仍为 WAITING、hold=false、rights_pending=false，且 order_settlements 的 seq 与校验时一致，才按 BR-FUND-05 以 B_credit（由联盟结算额按 BR-CALC-02 换算，含扣平台预留比例）按分佣快照拆分写入账凭证、写入各受益人可提现余额，并按 R5 迁移到 CREDITED；否则跳过（保持 WAITING，批次明细记原因，进入后续批次）。uniq_key 保证同一批次重放或跨批次重复只入账一次。每个子订单事务开始前读取 settle.auto.enabled 与 credit.enabled.&lt;platform>（缓存 ≤10 秒），任一为 off 立即停止，批次置 PARTIAL，已提交的保持 CREDITED、未处理的保持 WAITING；开关恢复后不自动续跑，由 finance step-up 后手动继续。每日 00:00 至当日资产快照完成（BR-FUND-18）期间不执行批次：定时时刻保存时已按名义时段校验（⑥）；到了执行时刻而当日快照仍未完成（快照延迟）的，等快照完成或超时后执行（SB5）。<br>⑧ 补充批次：差错单处理完毕、hold 解除、维权关闭或联盟结算数据后到的子订单，finance 可对同一月结账单发起补充校验与批次（流程同 ④–⑦，单独确认，同样可选立即或定时），不必等下一期账单。<br>⑨ 平台入账开关 credit.enabled.&lt;platform>（BR-CALC-03，默认 off）为 off 时，该平台不得生成或执行结算批次（月结账单中该平台只保留校验结果），R4 照常进 WAITING 并写 settle_period；扣回、补差、失效不受本条开关与批次影响。某平台的首个月结批次只能在该平台 CAP-\*-08 的 08b（首个月结对账，规划/09）通过后执行：通过前该平台 credit.enabled.&lt;platform> 保持 off（打开条件 = BR-CALC-03 验证证据 + 08b 通过）；账单日早于 08b 通过的（如首个账单日 11-24 早于淘宝、京东 08b 截止 11-27），该平台本期不生成批次，顺延到下一个账单日，或 08b 通过后打开开关、由 finance 对该期账单手动发起补充批次（⑧），照常人工确认（负责人 2026-10-01）。<br>⑩ 一单中除 held 受益人（BR-CALC-13）外的全部受益人同批入账或同时不入账；held 受益人解除后按 BR-FUND-01 R5a 在后续批次（含补充批次）单独入账（按 ⑫ 的受益人补记项）。<br>⑪ 用户侧预计结算月份：WAITING 订单由服务端返回 expected_credit_period（预计结算月份，YYYY-MM，+08:00）：已有 union_settled_at 时 = union_settled_at 所在自然月（以联盟为准）；联盟尚未返回结算时间时 = 确认收货月（settle_period）+ settle.period_offset_months.&lt;platform> 个月（默认 1，即次月结算上月确认收货的订单）；客户端不得自行推算；展示文案只在 BR-TEXT-04 维护；维权中、hold、该平台 credit.enabled=off 时返回 null；当前日期（+08:00）晚于 expected_credit_period 当月的月结账单日 + settle.statement.grace_days（默认 10 天）而本单仍为 WAITING 时，credit_overdue=true，按 BR-FUND-17 显示「入账核对中」。不得向用户承诺具体入账日期或天数。本条是预计结算月份计算的唯一维护处。<br>⑫ 受益人补记项（2026-10-03 资金规则对齐方案 §6.6；默认处理，与 R5a 同待财务确认；待补记义务的身份与键为同日评审后修改，方案 §13.6）：CREDITED 子订单上受益人每出现一次待补记额（暂缓未入账，或正差被延后；待补记额见 BR-FUND-19 ⑤），就是一个待补记义务，分配稳定的 beneficiary_credit_id，在产生它的事务内登记开立事件与归属快照：入账时暂缓（迁移 R5）开首次入账义务，改派重记时新受益人暂缓（迁移 R14）开改派入账义务，其余（正差被延后：BR-FUND-09 正差获批或负差一路、迁移 R13 恢复时受益人冻结或申诉中）开延后差额义务。同一 (子订单, 受益人, 角色) 同时最多一个未完成的义务：已有未完成义务时，新的延后并入它、不另开（金额都在执行时重算）；义务完成（补记、没收，或执行时金额为 0）之后再出现的待补记额开新义务、用新 ID；订单转 CLAWED_BACK（迁移 R8）或改派（迁移 R14）时，同一事务作废该单未完成的义务，之后恢复（R13）或重记产生的待补记额开新义务。月结账单生成任务与补充批次发起时，对 CREDITED 子订单上每个未完成的义务生成补记项（明细引用 beneficiary_credit_id；同一义务被多个批次纳入或重试，都引用同一个 ID，不拿批次明细当业务身份），随该平台的批次一起人工确认、一起执行。补记项不做 ④ 的金额一致性校验（订单已入账，以 booked_base_fen 为准）。执行时在 BR-FUND-16 细则「加锁流程」的锁内重验：订单仍为 CREDITED、rights_pending=false、结算记录 seq 与生成补记项时一致、归属快照未变、该义务仍未完成，否则跳过。受益人状态正常（含注销冷静期）→ 按执行时的 booked_base_fen 与快照比例重算应得，入账金额 = 应得 − 当前净额（净额口径同 BR-FUND-08）；首次入账义务用 CREDIT 键，改派入账义务用迁移 R14 的 REASSIGN_CREDIT 键，延后差额义务用 `{order_key}:{uid}:{role}:ADJ:DEFERRED:{beneficiary_credit_id}` 键（BR-FUND-01 R5a；普通结算调整仍用 BR-FUND-09 的 `ADJ:{seq}`）；凭证与义务完成在同一事务提交，金额为 0 不写凭证、义务同样完成。仍在冻结或账户申诉中 → 明细记 deferred，义务保持未完成，留给后续批次。已封禁、已进入注销处理或已注销、已识别未成年人的推广份额 → 按 BR-CALC-13 没收，写 FORFEIT 凭证（延后差额义务的键为 `{order_key}:PLATFORM:FORFEIT:{uid}:{role}:DEFERRED:{beneficiary_credit_id}`），义务记为没收。补记的金额并入该批次完成后按受益人汇总的「已结算」推送（BR-TEXT-09 现有模板），不新增模板。 | 已确认 | orders.settle_period、orders.received_synced_at、orders.union_settled_at（新增，联盟返回的结算时间）（删除 orders.credit_due_at）；月结账单（bill_id=账单月、生成开始 / 完成时间、账单状态由批次派生、分平台子订单数与联盟结算佣金合计、受益人份额与平台留存合计、差错单数、暂缓数）；结算批次与批次明细（状态 DRAFT/CONFIRMED/EXECUTING/PARTIAL/DONE/CANCELLED，settle_mode（IMMEDIATE/SCHEDULED）、scheduled_at、confirmed_by、confirmed_at，明细结果：入账 / 跳过 / 暂缓；明细类型：子订单 / 受益人补记项（带 user_id、role 与 beneficiary_credit_id，⑫））；待补记义务（beneficiary_credit_id、开立事件、归属快照、状态，⑫）；差错单类型「账单金额不一致」「应结未结」；配置 settle.bill_day、settle.period_offset_months.&lt;platform>、settle.period_basis.&lt;platform>、settle.statement_source.&lt;platform>（默认 api）、settle.batch.match_tolerance_fen、settle.batch.max_orders、settle.statement.grace_days、settle.auto.enabled、credit.enabled.&lt;platform>（BR-CALC-03）（删除 settle.statement_day.&lt;platform>、settle.wait_days.&lt;platform>、settle.daily_min_fen、settle.credit.max_orders_per_run）；删除每日任务 settle.credit，新增月结账单日生成任务；后台月结账单列表与详情（状态、分平台合计、校验结果）、确认（立即 / 定时）/ 撤销定时 / 驳回 / 继续执行、补充批次页、联盟接口不可用时的结算明细上传页；GET /v1/orders/{id} expected_credit_period、credit_overdue；订单页、钱包预计结算月份表达；商品详情入账说明；客服话术「什么时候入账」；验收用例：账单日自动生成账单 → 一致性校验 → 确认（立即 / 定时）→ 批量入账、金额不一致进差错单、应结未结后补充批次、hold 与维权暂缓后补充批次、批次重放只入账一次、执行中关闭开关后手动继续、credit.enabled=off 不生成批次、预计结算月份（有 / 无联盟结算时间）、上传备用 |
| BR-FUND-05 | **入账金额与入账凭证**<br>定义 order_key = `{platform}:{sub_order_id}`（如 `taobao:1234567`）；所有资金 uniq_key 与 advisory lock 都必须用 order_key，不得单用 sub_order_id。入账基数 B_credit 必须按 BR-CALC-02 由 N 计算（含扣除快照中的平台预留比例 reserve_bp），N 取 orders.settle_commission_fen（取值规则见 BR-FUND-09；月结口径下入账时必有结算佣金，BR-FUND-04 ③）；按分佣快照比例重新拆分为各受益人份额与平台留存（平台留存 = B_credit − Σ受益人份额，Σ 含被剥夺与暂缓的受益人，尾差归平台）。每个份额 >0 的受益人写 1 张凭证，uniq_key=`{order_key}:{user_id}:{role}:CREDIT`（被剥夺的受益人不写其凭证，份额按 BR-CALC-13 写平台 FORFEIT 凭证；暂缓的受益人不写凭证，解除后按 BR-FUND-04 ⑫ 补记）；平台凭证金额 = 平台留存 + 预留金额 reserve_fen（BR-CALC-02、BR-CALC-04），>0 写 1 张凭证，uniq_key=`{order_key}:PLATFORM:CREDIT`；份额为 0 的受益人不写凭证，平台凭证金额（留存 + 预留）大于 0 就写，两者都为 0 时不写任何凭证，只迁移状态。同一子订单的全部凭证、account_balances 更新、orders.booked_base_fen=B_credit、orders.booked_n_fen = 入账所依据的联盟结算佣金的正数部分与 rebate_status→CREDITED 必须在同一 PG 事务内完成；加锁顺序与锁后重读受益人状态见 BR-FUND-16 细则「加锁流程」。uniq_key 冲突视为已入账，跳过且结果与首次相同。 | 已确认 | ledger_vouchers.uniq_key 唯一索引；ledger_entries；account_balances；orders.booked_base_fen、booked_n_fen；结算批次执行（BR-FUND-04）；事件 order.credited；属性测试：同一 (子订单,受益人,角色) 入账 ≤1 次；跨平台同号子订单各自入账；验收用例（AC-SET-nn，编号待 规划/05 分配）：重放入账只入账 1 次 |
| BR-FUND-06 | **维权中与订单暂停**<br>子订单 rights_pending=true（存在 status ∈ {PROCESSING, WAIT_COMMISSION} 的 order_rights 记录）或 hold=true 时，月结账单校验记暂缓、批次执行时跳过（BR-FUND-04）；二者都不改变 rebate_status。hold 只能对 rebate_status ∈ {ESTIMATED, WAITING} 设置：人工由 ops（风控）或 cs（客服）操作，风控引擎可以系统身份（actor=system:risk）自动 hold（含 BR-FUND-02 映射表之外的状态码，原因码 UNMAPPED_STATUS）；unhold 只能由 ops 或 cs 人工执行（不要求与 hold 为同一人），系统不得自动 unhold；hold、unhold 都必须填原因码并写审计日志。CREDITED 之后不得 hold（改用账户提现冻结）。维权结果：失败 → 关闭记录、金额不变；全额成功 → 入账前按 BR-FUND-07、入账后按 BR-FUND-08；部分成功 → 按 BR-FUND-08 的新基数取值顺序确定 B_new（入账前改预估，入账后部分扣回）；联盟新佣金与应扣佣金都没有时，order_rights 置 WAIT_COMMISSION（仍阻止入账），等联盟回传新佣金后按 R7/R9 处理并关闭。无「处理中」信号的平台只在结果回传时处理。 | 待验证 | orders.hold、orders.rights_pending；order_rights 表（来源、类型、金额、应扣佣金、状态 PROCESSING/WAIT_COMMISSION/SUCCEEDED/FAILED、发生时间、平台维权单号、created_at）；后台订单 hold/unhold 操作与审计；风控引擎 system:risk 身份；/admin/v1/rights-imports；订单页展示文案 |
| BR-FUND-07 | **入账前失效与部分退款**<br>rebate_status ∈ {UNATTRIBUTED, ESTIMATED, WAITING} 时收到 PLATFORM_INVALID、全额维权成功、PUNISH、BLACKLIST_HIT，或 B_est 由 >0 更新为 0 而平台未回传失效（B_est 指有效联盟佣金按 BR-CALC-02 换算出的基数；settle_commission_fen 已到之后，预估佣金单独变化不触发 COMMISSION_ZERO），必须迁移到 VOID（终态），记 reason_code（REFUND / RIGHTS / PUNISH / BLACKLIST / COMMISSION_ZERO），不写任何分录，同一事务内入队领域事件 order.invalidated。首次入库即 B_est=0 的订单不适用本条（见 BR-FUND-03）。COMMISSION_ZERO 判定只比较 platform_status ≠ DEPOSIT_PAID 时的 B_est：platform_status=DEPOSIT_PAID 期间 B_est 的任何变化（含 >0 变 0 或变为 null）都不触发本条；进入 PAID（P2）时的 B_est 视为 BR-FUND-03 的「首次 B_est」，为 0 时按「本单无返利」处理、不作废。联盟某次回传佣金字段缺失或为空时不覆盖已有 est_commission_fen（保留上次数值），不触发本条；est_commission_fen 只在从未收到数值时为 null，表示「未知」，不视为 0。部分退款、部分维权、价保、比价降佣只更新 refunded_quantity 与 est_commission_fen，状态不变，不写分录。VOID 后平台再回传有效状态不得自动复活，按 BR-FUND-22 处理。 | 默认假设 | orders.rebate_status、reason_code；事件 order.invalidated；推送「订单已失效」；订单页原因码文案 |
| BR-FUND-08 | **入账后扣回**<br>rebate_status=CREDITED 时发生逆向事件（退款、维权成功、处罚、PLATFORM_INVALID、REFUND_AFTER_SETTLE、INVALID_AFTER_SETTLE、有效基数由 >0 变 0（有效联盟佣金按 BR-CALC-02 取值与换算，含结算佣金为负）），必须在同一事务内按受益人写 CLAWBACK 凭证。京东实际佣金由 >0 变 0 的口径待 规划/09 验证，验证前按全额扣回处理并生成差错单人工复核。佣金变化（价保、比价降佣、联盟佣金调整）不属于逆向事件，不写 CLAWBACK：联盟新的结算记录带来的变化按 BR-FUND-09 与迁移 R10 处理（负差即时写负向 SETTLE_ADJUST，正差进 BR-FUND-09 候选；原基数大于 0 而新基数为 0 按本条 R8）；结算记录未变、只有预估佣金变化的按 BR-FUND-01 R9b 只存档并出差错单。先取新的联盟佣金 N_new，按以下顺序取第一个可用值：①本次事件带来的联盟新佣金，指有效联盟佣金（BR-CALC-02）发生变化：结算佣金为空时是预估佣金的新值；结算佣金非空时只认新的结算记录（BR-FUND-09 的 seq 变化），结算佣金非空时单独变化的预估佣金不算；②联盟维权记录（order_rights）给出的应扣佣金：N_new = booked_n_fen − 应扣佣金，小于 0 按 0；③都没有 → 不写扣回，order_rights 置 WAIT_COMMISSION，订单进待处理表并告警，等联盟的新佣金或应扣佣金，不按我方估算先扣（负责人 2026-10-03 资金规则对齐决-03 选 A）。整单失效时 N_new = 0。新基数 B_new 由 N_new 按 BR-CALC-02 用快照 reserve_bp 换算。我方 Adapter 自行估算的佣金（BR-CALC-15 按件估算）只用于入账前的预估，不作为入账后扣回的依据。受益人扣回金额 = 该受益人在该子订单上的已入账净额 − 按 B_new 和快照重拆的新应得（受益人状态规则见 BR-CALC-09），≤0 不写。已入账净额 = 该受益人键下 CREDIT、SETTLE_ADJUST、CLAWBACK、ADMIN_ADJUST（RESTORE，含 BR-FUND-22 ③ 的申诉补发）、REASSIGN_REV、REASSIGN_CREDIT 的代数和；改记平台坏账的扣回计入，归平台的正差不计入（同 BR-FUND-19 ④）。平台已入账净额 = 该子订单全部凭证对 COMMISSION_REVENUE 的贷方净额（含 FORFEIT，以及申诉补发凭证的借方）。平台差额 = 平台已入账净额 − 按 B_new 的新平台应得，可正可负，≠0 就写：正数 借 COMMISSION_REVENUE / 贷 UNION_RECEIVABLE；负数 借 UNION_RECEIVABLE / 贷 COMMISSION_REVENUE；平台已入账净额与新的平台应得都含预留（新平台应得 = 按 B_new 的新留存 + N_new 换算出的预留 reserve_fen，BR-FUND-05）。本次全部凭证对 UNION_RECEIVABLE 的净影响必须 = −(booked_n_fen − N_new 的正数部分) − Σ 待补记额的变化量（变化量 = 本次之后 − 本次之前，待补记额见 BR-FUND-19 ⑤；没有暂缓或延后受益人时即 −(booked_n_fen − N_new 的正数部分)）；同事务 booked_base_fen = B_new、booked_n_fen = N_new 的正数部分。B_new=0 → CLAWED_BACK（终态），否则保持 CREDITED；同一事务作废该子订单未批准的正差候选（BR-FUND-09 ②，决-10 A），转 CLAWED_BACK 时还作废该子订单未完成的待补记义务（BR-FUND-04 ⑫）。uniq_key：受益人 `{order_key}:{user_id}:{role}:CLAWBACK:{rights_event_id}`，平台 `{order_key}:PLATFORM:CLAWBACK:{rights_event_id}`。rights_event_id 取值：来自维权/处罚接口或导入 → `R{order_rights.id}`；来自订单同步的平台状态变化 → `P{platform_status 迁移后的 row_version}`；来自订单同步的佣金变化 → `C{commission_version}`（同一份联盟数据重放时 commission_version 不变，不生成新键）。扣回只从 available 扣，允许 available 变负（BR-FUND-10），不得扣 frozen。受益人已进入注销 processing 或已注销（墓碑用户，BR-ID-28）且该受益人净额大于 0 时（份额入过其账户），该受益人的扣回额不写其账户，改借 BAD_DEBT / 贷 UNION_RECEIVABLE；份额从没入过其账户（入账时已按 BR-CALC-13 没收，净额为 0）的，不写任何分录，没收的份额随平台已入账净额冲回（平台坏账；金额、uniq_key、ledger_type 与 sub_type 不变；拍板第二批 FUND-09）。 | 已确认 | ledger_type CLAWBACK 与 sub_type；order_rights（WAIT_COMMISSION）；orders.booked_base_fen、booked_n_fen；事件 order.clawed_back；推送/站内信「返利已扣回」；订单页已扣回详情（金额、原因、关联流水）；验收用例 AC-SET-nn（编号待 规划/05 分配，对应后端功能规划 §10.1 AC-MONEY-004）；属性测试：受益人净额不为负；UNION_RECEIVABLE 净影响 = −(booked_n_old − N_new 的正数部分) − Σ 待补记额变化量 |
| BR-FUND-09 | **月结补差**<br>R1 联盟对账以联盟结算明细（结算报表或接口）为唯一依据。每个子订单的结算记录存 order_settlements(order_key, seq, source ∈ {API, STATEMENT}, settle_commission_fen, settled_at, content_hash)，每收到一条内容不同的记录 seq+1；orders.settle_commission_fen = 最新 STATEMENT 记录的金额，无 STATEMENT 时取最新 API 记录；API 与明细金额不一致时以明细为准并生成差错单。R1 正差候选随月结账单生成任务（BR-FUND-04 ③，月结账单日当日资产快照完成后）对 CREDITED 子订单运行，finance 可手动触发；负差不等 R1（见 ①）。补差只针对 rebate_status=CREDITED 的子订单。先把 settle_commission_fen 按 BR-CALC-02 用快照 reserve_bp 换算成结算基数 B_settle，逐受益人计算 diff = 按 B_settle 与快照重拆的应得份额 − 已入账净额（口径同 BR-FUND-08；平台同法，平台应得含预留，BR-FUND-05），各受益人差额的去向按 BR-CALC-09 的受益人状态规则；再按 B_settle 与 booked_base_fen 的大小分两路（分路按整单，不按各受益人差额的方向；B_settle 与 booked_base_fen 相等时改比结算佣金的正数部分与 booked_n_fen）：①负差（B_settle &lt; booked_base_fen，或两者相等而结算佣金的正数部分 &lt; booked_n_fen）：在写入该 settle_commission_fen 的同一事务内（订单同步回传结算额，或结算明细入库）立即写 SETTLE_ADJUST 凭证（diff≠0 才写），不等审批；受益人已进入注销 processing 或已注销的，其负差改借 BAD_DEBT / 贷 UNION_RECEIVABLE（同 BR-FUND-08）；②正差（B_settle > booked_base_fen，或两者相等而结算佣金的正数部分 > booked_n_fen）：R1 生成补差候选行（记录生成时的 seq）写入 settle_adjust_batches，须由超管或被勾选补差权限的账号 step-up 批准后才写 SETTLE_ADJUST 凭证（一人可完成，写审计，拍板第二批 §8 ADD-05）；写凭证时必须按 orders.settle_commission_fen 当前值换算的 B_settle 与当前净额重算：diff=0 不写；候选行 seq ≠ 该订单当前 seq 时该行作废，不写；同一条结算记录（seq）只在其写入时刻晚于该子订单最近一次扣回（CLAWBACK）时才生成正差候选，扣回发生时该子订单未批准的正差候选全部作废（作废原因「因扣回作废」，批准接口返回已作废）（负责人 2026-10-03 资金规则对齐决-10 选 A；开关 settle.adjust.void_on_clawback.enabled，默认 on，off 时候选照常生成、由批准人把关）；③B_settle 与 booked_base_fen 相等、结算佣金的正数部分也等于 booked_n_fen：无动作。基数相等而联盟佣金不同时，各受益人应得不变、差额为 0，只调平台的金额（预留与留存按 BR-CALC-02、BR-CALC-04 重算），负差即时、正差进候选审批，与受益人的补差相同；基数为 0 仍记预留的订单（BR-FUND-05）联盟佣金变化而基数仍为 0 的同此（迁移 R10）。同一路里逐受益人按 BR-CALC-09 的状态规则算差额，平台差额随所在一路记账（可正可负，取整所致）。负差一路里：封禁、已注销受益人的新应得取重拆份额与已有净额中较小的一个，多出的部分并入平台差额；冻结、申诉中受益人的正差，以及已解除、等补记的份额，留作待补记额（BR-FUND-04 ⑫ 受益人补记项）；都不进补差候选。正差一路里不出现受益人负差。结算额写入前的预估变化发生在入账前，只重算预估（迁移 R7）；入账后的预估变化见迁移 R9b（只存档并出差错单）。两路 uniq_key 相同：受益人 `{order_key}:{user_id}:{role}:ADJ:{seq}`、平台 `{order_key}:PLATFORM:ADJ:{seq}`，同事务 booked_base_fen = B_settle、booked_n_fen = settle_commission_fen 的正数部分。R1 补差不得产生首次入账：结算明细中 WAITING 的子订单只记录结算额、不生成差错单，由 BR-FUND-04 结算批次比对、人工确认后按结算额入账；ESTIMATED、VOID、CLAWED_BACK 或我方无订单的，生成差错单。负向补差允许 available 变负。 | 已确认 | order_settlements 表；settle_adjust_batches 表（只含正差）；orders.settle_commission_fen、booked_base_fen、booked_n_fen；订单同步与明细入库事务内的负差即时补差；/admin/v1/recon R1、正差补差批次批准页；ledger_type SETTLE_ADJUST；差错单类型；订单页「与预估不同时显示差额原因」；验收用例 F-SET-05 重跑月结、结算修正 A→B→A |
| BR-FUND-10 | **负余额规则**<br>只有 CLAWBACK、负向 SETTLE_ADJUST、负向 ADMIN_ADJUST，以及改派红冲凭证（迁移 R14 的 REASSIGN_REV，BR-ATTR-20）可以使 USER_BALANCE.available_fen &lt; 0；其他红冲（`{原 uniq_key}:REVERSE`）不在此列，红冲入账类凭证时仍须结果 ≥0；其他任何写入（含 WITHDRAW_FREEZE、WITHDRAW_FEE、TAX_WITHHOLD）写入前必须校验结果 ≥0，frozen_fen ≥0 由数据库 CHECK 约束保证。available_fen &lt; 0 时提现申请必须返回 30302（BR-FUND-11），注销申请返回 30416（BR-ID-27，拍板第二批 §8 ADD-07）；后续入账直接计入余额，自然抵扣负数，不另写抵扣分录。 | 已确认 | account_balances CHECK (frozen_fen >= 0)；POST /v1/withdrawals 校验、错误码 30302；POST /v1/me/deletion 30416；GET /v1/wallet/summary negative_fen；钱包页待抵扣提示；验收用例 AC-SET-nn（编号待 规划/05 分配，对应后端功能规划 §10.1 AC-MONEY-004） |
| BR-FUND-11 | **负余额时禁止提现**<br>用户余额 available_fen &lt; 0 时不得提现；未打款的非终态提现单由系统自动驳回、冻结额退回抵扣负数（拍板第二批 §8 ADD-06）。申请时的错误码与已有非终态提现单的处理见 BR-WDR-05 (a)。 | 已确认 | 见 BR-WDR-05；钱包页提示文案；客服话术 |
| BR-FUND-12 | **负余额坏账核销**<br>账户 available 由 ≥0 变为 &lt;0 时记 negative_since = 当日会计日（00:00 +08:00 日切），回到 ≥0 时清空。每日 R3 后生成负余额报表；当 当前会计日 − negative_since ≥ ledger.bad_debt_days（默认 90）且 \|available_fen\| ≥ ledger.bad_debt_min_fen（默认 0；两项数值开发期为占位值，上线前由超管在后台填写，拍板第二批 §8 ADD-03）时生成核销候选单；同一账户同时最多 1 张 PENDING 候选单，已存在则不再生成。核销不得自动执行：须由超管或被勾选核销权限的账号 step-up 后批准，一人可完成，写审计（拍板第二批 §8 ADD-05）。批准时重读 available 与 frozen：该用户 frozen_fen 大于 0（有非终态提现单）时拒绝批准，候选单保持 PENDING，提示先把提现单处理到终态（负责人 2026-10-03 资金规则对齐决-11 选 A；开关 ledger.bad_debt_require_no_frozen.enabled，默认 on，off 时不看 frozen 照常核销）；frozen_fen 为 0 且 available &lt;0 → 写 BAD_DEBT_WRITEOFF（借 BAD_DEBT / 贷 USER_BALANCE.available，金额 = −当前 available_fen，不用候选单生成时的金额），使 available=0；≥0 → 候选单置 CANCELLED，不写凭证。凭证 uniq_key=`BADDEBT:{account_id}:{candidate_id}`。核销时给同实名、同设备、同收款账号的关联账户打风控标记。余额为负的用户不能申请注销（BR-ID-27，30416，拍板第二批 §8 ADD-07），本条只适用于未注销用户；注销 processing 起才到的扣回按 BR-FUND-08 记平台坏账，不再使墓碑用户余额变负（拍板第二批 FUND-09）。 | 已确认 | account_balances.negative_since；负余额报表、核销候选单（后台，PENDING/APPROVED/CANCELLED；有非终态提现单时批准页提示）；ledger_type BAD_DEBT_WRITEOFF；配置 ledger.bad_debt_days、ledger.bad_debt_min_fen、ledger.bad_debt_require_no_frozen.enabled；风控关联标记与申诉；隐私政策风控条款 |
| BR-FUND-13 | **单一余额与余额性质**<br>每个用户只有一个余额：注册时创建 1 个用户账户（科目 USER_BALANCE:{uid}，account_balances 每用户一行），含 available、frozen 两个子户，初始均为 0；不分自购与推广账户（拍板第二批 §8 ADD-06）。该用户作为任一受益角色（本人自购或分享、直推、间推）的份额都入这一个余额；收入来源只由流水 ledger_type + sub_type 区分（BR-FUND-15），用于展示与对账；分佣快照仍按角色记录受益人（BR-CALC-04、BR-CALC-10）。用户余额是平台应付佣金，不是储值：不得提供充值、用户间转账、余额消费接口；钱包模块不得出现 transfer、pay_with_balance 类接口。手续费、门槛与提现限额按用户统一配置，不按收入来源区分（见 BR-WDR）。 | 已确认 | ledger_accounts（每用户 1 个 USER_BALANCE，删除 account_type 维度）；account_balances 每用户一行；GET /v1/wallet/summary 单一余额；钱包页单一余额 + 流水来源；契约审查：禁止 transfer/pay_with_balance |
| BR-FUND-14 | **冻结与已提现资金变动**<br>本条只规定账户性质约束与不变量；提现各状态何时写分录、写哪些 ledger_type、借贷科目只在 BR-WDR-09 维护，本条不重复。<br>① frozen 子户只用于提现：只有提现分录（BR-WDR-09）可以增减 USER_BALANCE.frozen，其他业务（入账、扣回、调账、坏账核销、风控）不得写 frozen。<br>② 不设 WITHDRAW_IN_TRANSIT：打款中（PAYING）资金留在 frozen，直到提现单进入终态；该科目不创建、任何凭证不得使用；「已提交支付宝、尚未确认」的金额从 status=PAYING 的提现单汇总。<br>③ 风控冻结（risk_state=frozen）与 withdraw_holds 只禁止提现（BR-WDR-05），不移动资金，不计入 frozen_fen。<br>④ 不变量：每个用户 frozen_fen = Σ 该用户非终态提现单（PENDING_REVIEW、APPROVED、PAYING）amount_fen；日终校验与属性测试均覆盖。<br>⑤ 未成年人（BR-ID-26）识别前已入账的推广收益留在余额 available，不移动、不写 frozen；未满 18 周岁期间提现整体受 BR-WDR-06 月额度约束，满 18 周岁时刻起不再受限（拍板第二批 FUND-10、§8 ADD-06）。<br>各状态分录见 BR-WDR-09。 | 默认假设 | ledger_type WITHDRAW_FREEZE/WITHDRAW_RETURN/WITHDRAW_PAID/WITHDRAW_FEE/TAX_WITHHOLD 的记账时点与科目见 BR-WDR-09；科目 WITHDRAW_IN_TRANSIT 从 规划/02 §8.2 科目表删除；钱包冻结中展示；不变量 frozen = Σ 非终态提现 |
| BR-FUND-15 | **流水类型与映射**<br>ledger_entries.ledger_type 只能取以下 13 个值：REBATE_CREDIT、SHARE_CREDIT、REFERRAL_CREDIT、CLAWBACK、SETTLE_ADJUST、WITHDRAW_FREEZE、WITHDRAW_PAID、WITHDRAW_RETURN、WITHDRAW_FEE、TAX_WITHHOLD、REWARD（P1）、ADMIN_ADJUST、BAD_DEBT_WRITEOFF；细分只用 sub_type。间推份额不新增流水类型，记 REFERRAL_CREDIT、sub_type=INDIRECT（D8，BR-CALC-05）。红冲与改派重记的分录沿用被更正分录的 ledger_type 与 sub_type，不新增类型（BR-FUND-16、BR-FUND-01 R14）。单一余额下收入来源（自购返利、分享收益、邀请分佣、好友推广奖励等）只由 ledger_type + sub_type 区分（拍板第二批 §8 ADD-06）。用户「余额流水」只展示该用户 available 子户上的分录，按时间倒序，每条展示：带符号金额、类型名称、sub_type 说明、关联订单或提现单、原因、变动后余额 balance_after_fen；此外每张打款成功的提现单合并显示为 1 条 WITHDRAW_PAID 汇总条目（用户侧名称按 BR-TEXT-19，为「提现到账」；显示实际到账金额、税、手续费，不改变可提现余额，不带 balance_after）。balance_after_fen 为该分录所在子户变动后的余额。其他文档的类型名只作映射，不得出现在代码与契约中。 | 默认假设 | contracts/enums/ledger-types、sub-types；ledger_entries.ledger_type、sub_type、balance_after_fen；GET /v1/wallet/ledger（含 WITHDRAW_PAID 汇总条目）；余额流水 H5；后台流水查询与导出 |
| BR-FUND-16 | **复式记账硬约束**<br>每个 uniq_key 对应 1 张凭证（ledger_vouchers，uniq_key 在 (app_id, uniq_key) 上唯一）+ ≥2 条分录；一笔业务可由同一事务内的多张凭证组成（如 BR-FUND-05）。分录 amount_fen 为带符号 bigint（单位分，借为正、贷为负），同一凭证 Σ amount_fen = 0，domain 层校验且日终 SQL 复核。ledger_vouchers、ledger_entries 只插入：应用数据库角色无 UPDATE/DELETE 权限并加防护触发器；更正一律写红冲凭证（uniq_key=`{原 uniq_key}:REVERSE`）再重记。用户账户余额缓存 account_balances 必须在同一事务内 SELECT … FOR UPDATE（多账户按 account_id 升序加锁）后更新，version+1；用户负债账户 available_fen = −Σ 该子户分录 amount_fen。平台科目为热点账户，不维护实时余额缓存，从分录汇总。会计日按 00:00 +08:00 日切，accounting_date 取写入时注入 Clock 的日期。金额计算只能用 packages/money 的整数分运算，不得用浮点。 | 已确认 | ledger_vouchers、ledger_entries、account_balances 表结构与权限；DB 角色与防护触发器；packages/money；AGENTS.md 资金硬规则；属性测试（PR 1 万次、夜间 100 万次）；真实 PG 并发测试 |
| BR-FUND-17 | **资金话术与状态对应**<br>本条只维护两件事：①订单 display_status 必须按细则派生表从上到下取第一个匹配项，文案取字典 key `order_status.<display_status>`，文字以 BR-TEXT-02、BR-TEXT-03 为准；②Agent 与客服回答订单或金额问题时，状态与金额必须来自订单与钱包接口（GET /v1/orders、GET /v1/wallet/summary），不得由模型推断。资金术语（预估返、预估推广收益、已结算、可提现、冻结中、已到账、已提现等）的含义只在 BR-TEXT-01 维护，提现状态文案只在 BR-TEXT-06 维护，禁用词只在 BR-TEXT-13 维护，本条不另写。 | 已确认 | 规划/04 §2.3 用户侧状态映射、§2.4 提现状态文案；display_status 枚举（契约）；dict_items 文案 key；specs/banned-words.yaml（BR-TEXT-13）；推送/站内信模板；钱包页、订单页、提现记录文案；Agent rule_qa、order_query 回复模板；客服话术库；帮助中心文章 |
| BR-FUND-18 | **钱包汇总与资产快照口径**<br>GET /v1/wallet/summary 返回该用户单一余额（BR-FUND-13，拍板第二批 §8 ADD-06）的：available_fen（可为负）、withdrawable_fen = max(available_fen,0)、negative_fen = max(−available_fen,0)、frozen_fen、estimated_total_fen（预估合计：该用户作为任一受益角色在 rebate_status ∈ {ESTIMATED, WAITING} 订单上的份额合计 = estimated_fen + pending_credit_fen，不含 DEPOSIT_PAID、UNATTRIBUTED；用户侧「预估收益」，BR-TEXT-01）、estimated_fen（其中 rebate_status=ESTIMATED 且 platform_status=PAID 的份额合计）、pending_credit_fen（其中 rebate_status=WAITING 的份额合计，含维权中、hold 与 credit_overdue 的；用户侧只作「其中已收货」进度行，不单列「待入账」）、pending_credit_paused_fen（其中维权中或 hold 的部分）、next_credit_period、credit_overdue、withdrawn_fen（已提现：Σ 该用户 PAID_API/PAID_MANUAL 提现单 amount_fen）、risk_paused_reason（risk_state=frozen 或存在生效 withdraw_holds 时返回用户可见原因 key，否则 null；不影响各金额）。各份额按有效联盟佣金（BR-CALC-02：settle_commission_fen 非空时取其值，否则取 est_commission_fen）经 BR-CALC-02 换算的基数计算，与入账金额（BR-FUND-05）一致。next_credit_period = hold=false、rights_pending=false、所在平台 credit.enabled=on 且 credit_overdue=false 的 WAITING 订单中最早的 expected_credit_period（BR-FUND-04 ⑪，YYYY-MM；跨平台取最早月份；无此类订单返回 null）；credit_overdue = 存在 hold=false、rights_pending=false 且 credit_overdue=true 的 WAITING 订单（前端附「入账核对中」）。字段名与 BR-TEXT-01 钱包汇总口径对齐，取值口径以本条为准。余额类取 account_balances 实时值；预估类取订单与分佣快照的计算值，缓存 ≤60 秒。asset_snapshots 在会计日 D+1 的 00:01:00 +08:00 写入 D 日数据：total_available_positive_fen、total_negative_fen、total_frozen_fen、total_waiting_fen、total_estimated_fen、union_receivable_fen（按平台）；余额类按 accounting_date ≤ D 的分录汇总，waiting/estimated 取快照运行时刻的订单状态。结算批次不在每日 00:00 至当日快照完成期间执行，月结账单在账单日快照完成后生成（BR-FUND-04 ③⑦）；快照最晚等到 00:30，超时则告警、批次照常可执行，并把该日快照标记 waiting_comparable=false。 | 已确认 | GET /v1/wallet/summary 响应 schema（含 estimated_total_fen、estimated_fen、pending_credit_fen、pending_credit_paused_fen、next_credit_period、credit_overdue、withdrawn_fen、risk_paused_reason）；asset_snapshots 字段与 waiting_comparable；任务依赖：结算批次与月结账单生成等待 asset_snapshot（BR-FUND-04）；钱包页；后台资产快照报表；R3 用户应付 vs 资产快照 |
| BR-FUND-19 | **账务不变量与日终校验**<br>每日 01:00 +08:00 对会计日 D−1 运行 ledger_invariants.sql，校验：①每个用户账户 余额缓存 = 分录合计，且 期初 + 当日发生额 = 期末（daily_balances）；②每张凭证 Σ amount_fen = 0；③每个 (子订单, 受益人, 角色) 的 CREDIT 凭证 ≤1；④每 (子订单, 受益人, 角色) 的净额 ≥ 0，净额 = 该受益人键下 CREDIT、SETTLE_ADJUST、CLAWBACK、ADMIN_ADJUST RESTORE、REASSIGN_REV、REASSIGN_CREDIT 的代数和（改记平台坏账的扣回计入，归平台的正差不计入）；⑤每个 CREDITED 或 CLAWED_BACK 子订单：该单订单类凭证（CREDIT、FORFEIT、CLAWBACK、SETTLE_ADJUST、ADMIN_ADJUST RESTORE、改派的 REASSIGN_REV 与 REASSIGN_CREDIT）对 UNION_RECEIVABLE 的净额 = booked_n_fen − Σ 待补记额，且 Σ 受益人净额 ≤ booked_base_fen；待补记额 = 暂缓（held）或正差被延后的受益人按 booked_base_fen 与快照比例算出的应得减去其净额，其余受益人为 0；⑥frozen_fen ≥0 且 = Σ 非终态提现单金额；⑦用户账户中每条使 balance_after_fen &lt;0 且较前一条下降的分录，其 ledger_type ∈ {CLAWBACK, SETTLE_ADJUST, ADMIN_ADJUST}，或属于改派红冲凭证（uniq_key 含 `:REASSIGN_REV:`，迁移 R14；红冲沿用原流水类型，按凭证键识别）；⑧platform_status=INVALID 或存在已成功的 INVALID_AFTER_SETTLE 维权、但 rebate_status 仍为 CREDITED 的子订单数 = 0。账户级差异（①⑥⑦⑧）：告警、生成差错单，并冻结涉及用户的提现。全局差异（②③④⑤）：告警，系统自动将 settle.auto.enabled 置 off（系统关闭不需 step-up），并冻结差异涉及的所有用户的提现。冻结方式：为每个涉及用户新增 1 条 withdraw_holds 记录（BR-WDR-05；reason=ledger_mismatch，source_ref=差错单 id，后台显示冻结来源 LEDGER_MISMATCH，不向用户展示），同一差错单对同一用户只新增 1 条；冻结生效期间提现申请返回 30303（data.reason=account_frozen）；与 30302 同时满足时按 BR-WDR-03 校验顺序优先返回 30303(account_frozen)；由 finance 在差错单关闭时 step-up 解除该条记录（写 released_at、released_by），同一用户的其他冻结记录不受影响。settle.auto.enabled 重新打开需有权限者 step-up。每张入账凭证提交后 5 分钟内做证实核对（凭证金额 = 分佣快照按 B_credit 重算的份额），不一致 5 分钟内告警并按账户级冻结该用户提现（同上新增 withdraw_holds）。 | 默认假设 | ledger_invariants.sql；daily_balances 表（新增）；orders.booked_base_fen、booked_n_fen（⑤）；withdraw_holds（reason=ledger_mismatch，BR-WDR-05）；错误码 30303 data.reason=account_frozen；开关 settle.auto.enabled（系统自动关闭）；告警规则；属性测试与并发测试；验收用例 AC-SET-nn（编号待 规划/05 分配，对应后端功能规划 §10.1 AC-MONEY-013） |
| BR-FUND-20 | **垫资敞口与入账开关**<br>已入账未回款 = UNION_RECEIVABLE:{platform} 分录余额（按平台）。联盟回款必须由财务在后台录入或经 R1 确认后写凭证：借 CASH_ALIPAY（或银行科目）/ 贷 UNION_RECEIVABLE:{platform}。每日随资产快照（D+1 00:01，BR-FUND-18）计算各平台与合计的已入账未回款；合计 > ledger.advance_alert_fen 的每一天告警财务 1 次。紧急开关 settle.auto.enabled（默认 on）：人工修改需 step-up 并告警，10 秒内生效；系统按 BR-FUND-19 自动关闭不需 step-up；重新打开一律需有权限者 step-up。开关为 off 时结算批次执行按 BR-FUND-04 ⑦ 停止，订单保持 WAITING，不影响扣回与补差。 | 已确认 | 看板：已入账未回款（按平台与合计）、负余额总额；配置 ledger.advance_alert_fen；开关 settle.auto.enabled；后台联盟回款录入；R1 差错单 |
| BR-FUND-21 | **负余额时未打款的提现单**<br>负余额对非终态提现单的处理（W2/W4/W8 守卫、事件 account.went_negative、未打款单 W3 驳回并抵扣、PAYING 单走 W9）只在 BR-WDR-05 (a) 维护，本条不再单独规定；编号保留供 §14.3 C-08、C-21 及外部引用定位。 | 已确认 | 见 BR-WDR-05 (a) |
| BR-FUND-22 | **作废或扣回订单的平台恢复**<br>rebate_status 为 VOID 或 CLAWED_BACK 的子订单不得因平台数据自动复活。仅当其 reason_code ∈ {REFUND, RIGHTS, COMMISSION_ZERO} 或进入原因为 PLATFORM_INVALID / INVALID_AFTER_SETTLE，且平台此后回传非失效状态或佣金恢复为 >0 时，才告警并生成差错单（类型「已作废订单被平台恢复」）；因 PUNISH、BLACKLIST_HIT 作废的订单，platform_status 照常更新，不告警、不生成差错单。处罚被平台解冻（处罚接口返回解冻、联盟随后照常结算）在 规划/09 实测与负责人再选之前按本条现行做法：不恢复、不补钱；「解冻」是映射表之外的信号，按 BR-FUND-02 进待处理表并告警，留下证据（负责人 2026-10-03 资金规则对齐决-06：实测前 A；实测证实后的做法另交负责人选，见 14）。差错单只能经 ADMIN_RESTORE 处理：超管或被勾选该权限的账号 step-up 后处理，一人可完成，写审计（拍板第二批 §8 ADD-05）。R12：VOID → 按当前 platform_status 回到 ESTIMATED 或 WAITING（WAITING 时 settle_period 按 received_at 取；该周期批次已执行的，进入补充批次或下一周期批次，BR-FUND-04）；user_id 为空（未归因）的回到 UNATTRIBUTED（未归因池，可再被找回或改派，BR-ATTR-16）；不写分录。R13：CLAWED_BACK → CREDITED，按当前有效联盟佣金经 BR-CALC-02 换算出的基数与分佣快照重算各受益人与平台应得（平台应得含预留，BR-FUND-05），与当前净额（口径同 BR-FUND-08）的差额写 ADMIN_ADJUST（sub_type=RESTORE，借 UNION_RECEIVABLE / 贷 USER_BALANCE.available 或 COMMISSION_REVENUE），各受益人差额的去向按 BR-CALC-09 的受益人状态规则，uniq_key 受益人 `{order_key}:{user_id}:{role}:RESTORE:{差错单 id}`、平台 `{order_key}:PLATFORM:RESTORE:{差错单 id}`，同事务 booked_base_fen = 新基数、booked_n_fen = 该联盟佣金的正数部分。处理人也可决定不恢复，关闭差错单并记原因。<br>**申诉恢复**（拍板第二批 FUND-14）：申诉结案为撤销时（BR-ID-36；订单申诉只标记该订单申诉中、不改账户 risk_state，OPS-07），系统自动生成差错单「申诉恢复」，按上述方式处理：订单申诉 → ① 该订单 reason_code=BLACKLIST 的 VOID 按 R12 恢复，② 经 BLACKLIST_CONFIRMED 扣回的 CLAWED_BACK 按 R13 恢复；账户（封禁）申诉 → ③ 该用户在封禁期间因 banned 被 forfeited（BR-CALC-13）、已计入平台留存的份额，按 booked_base_fen 与快照重算该受益人应得，与其已入账净额（口径同 BR-FUND-08）之差写 ADMIN_ADJUST（sub_type=RESTORE，借 COMMISSION_REVENUE / 贷 USER_BALANCE.available），uniq_key 同上；补发后该受益人不再按被剥夺处理，之后的调整按重拆份额算应得（BR-CALC-09 的申诉恢复例外）。PUNISH（联盟处罚）作废的订单不在申诉恢复范围。 | 已确认 | 迁移表 R12、R13（SM-REB-R12/R13）；差错单类型「已作废订单被平台恢复」「申诉恢复」（申诉结案撤销时系统生成，BR-ID-36）；ADMIN_ADJUST sub_type RESTORE；后台差错单处理页（step-up 处理）；告警规则 |
| BR-FUND-23 | **月末三项核对**<br>每月 1 日 01:30:00 +08:00（名义时刻，读注入的 Clock；须在当日 01:00 的 BR-FUND-19 日终校验完成后开始，最晚等到 03:00，超时告警并照常运行）对上月 M（M 月 1 日 00:00 至 M+1 月 1 日 00:00，+08:00）运行内部对账 R3 的月度核对，按 app_id 计算三个数（单位分）：X1 用户累计入账净额 = 截至 M 月末（accounting_date ≤ M 月末日）用户 available 子户上 REBATE_CREDIT、SHARE_CREDIT、REFERRAL_CREDIT、REWARD、CLAWBACK、SETTLE_ADJUST、ADMIN_ADJUST、BAD_DEBT_WRITEOFF 分录对用户余额的影响合计（贷记为正）；X2 用户期末余额 = M 月末日 asset_snapshots 的 total_available_positive_fen − total_negative_fen + total_frozen_fen；X3 用户累计已提现 = 截至 M 月末迁移到 PAID_API/PAID_MANUAL 的提现单 amount_fen 合计（取提现单表，以迁移事务的 Clock 时刻判断归属月份）。必须满足 X1 = X2 + X3，差额 ≠0 分即 P1 告警并生成差错单（类型「月末三项不平」），不自动冻结提现、不改开关（账户级定位与冻结由 BR-FUND-19 负责）。同一报表另列按平台的「上月联盟预估佣金」（paid_at 在 M 内且已归因子订单的 est_commission_fen 当前值合计）、「上月入账基数」（M 内 rebate_status→CREDITED 的子订单 booked_base_fen 合计）、UNION_RECEIVABLE:{platform} 期末余额，只供财务查看，不参与等式。重跑同一月份结果相同，差错单按 (app_id, 月份) 去重。 | 默认假设 | 任务 recon.monthly（依赖 BR-FUND-19 当日完成、BR-FUND-18 月末日快照）；/admin/v1/recon R3 月度报表与导出；差错单类型「月末三项不平」；告警规则；验收用例：构造入账、扣回、提现、核销后三项相等；篡改一笔提现单金额后生成差错单 |
| BR-FUND-24 | **人工调账**<br>人工调整用户余额只能经后台调账单写 ADMIN_ADJUST 凭证（sub_type = 原因码），不得直接改 account_balances 或分录；本条是 ADMIN_ADJUST 原因码与流程的唯一维护处（代理起草，负责人 2026-10-01 授权按推荐）。① 流程：超管或被勾选人工调账权限的账号发起（用户、方向、金额（分，&gt;0）、原因码、关联单据、内部说明），step-up 后批准执行，一人可完成（拍板第二批 §8 ADD-05）；批准时在同一事务内重读余额并写凭证；调账单状态 PENDING → APPROVED / REJECTED / CANCELLED（发起后可先保存待批，可撤回，驳回须填原因）；全程写 audit_logs。RESTORE 只由 BR-FUND-22 差错单生成，按 BR-FUND-22 处理。<br>② 原因码：RESTORE（订单恢复与申诉恢复，BR-FUND-22）、RECON_FIX（对账差错更正，关联 R1/R2/R3 差错单）、PAYOUT_RECOVERY（重复打款或迟到成功的追回，关联提现单与差错单，BR-WDR-15、BR-WDR-23）、ACCOUNT_CLOSED（注销放弃余额转平台收入，关联注销单）、OTHER（须关联客服工单或差错单并写说明）。<br>③ 每张调账单至少关联 1 张单据（差错单、提现单、子订单 order_key、注销单或客服工单）。<br>④ 金额不设单笔上限（负责人 2026-10-01）；批准页展示调账前后 available。<br>⑤ 调减可使 available &lt; 0（BR-FUND-10），之后按 BR-FUND-10、11、12 处理；不得写 frozen（BR-FUND-14 ①）。<br>⑥ 分录：调增 借 平台科目 / 贷 USER_BALANCE.available，调减反之；对方科目默认 RESTORE 按 BR-FUND-22，PAYOUT_RECOVERY 为 CASH_ALIPAY（银行卡通道为对应银行科目），ACCOUNT_CLOSED 为 COMMISSION_REVENUE，RECON_FIX、OTHER 由发起人按差错单与 specs/ledger-rules.md 选定；科目表以 specs/ledger-rules.md 为准。uniq_key=`ADJ:{adjust_id}`；已执行的调账只能另发调账单写红冲凭证 `ADJ:{adjust_id}:REVERSE` 更正（BR-FUND-16）。<br>⑦ 用户可见：余额流水显示 1 条 ADMIN_ADJUST，名称与说明按原因码取字典（BR-TEXT-19），不显示内部说明与操作人；调减另发站内信，含金额与原因类别。<br>⑧ 注销：用户进入注销 processing（BR-ID-28）时，available &gt; 0 的，系统预填 ACCOUNT_CLOSED 调减单（金额在批准时按当时 available 取），按 ① 执行，须在注销 done 前完成，未完成告警；余额为负的用户不能申请注销（BR-ID-27，30416，拍板第二批 §8 ADD-07），不再生成核销候选单；注销用户不发站内信（拍板第二批 FUND-09）。 | 已确认 | 调账单表（adjust_id、user_id、direction、amount_fen、reason_code、ref_type、ref_id、note、status、created_by、reviewed_by、时间；删除 account_type）；ledger_type ADMIN_ADJUST 的 sub_type 枚举（RESTORE、RECON_FIX、PAYOUT_RECOVERY、ACCOUNT_CLOSED、OTHER）；后台调账页（权限点、step-up）；audit_logs；注销处理任务（ACCOUNT_CLOSED 预填）；字典 ledger_type.ADMIN_ADJUST 按原因码的说明（BR-TEXT-19）；站内信模板（余额调减）；specs/ledger-rules.md 科目；验收用例：一人 step-up 完成、未勾选权限的账号被拒、调减至负、红冲、注销放弃余额 |
| BR-FUND-25 | **收益看板口径**<br>GET /v1/earnings/summary（收益看板，M-公开）只返回本人的收益概览，口径只在本条维护；看板只做展示，不参与任何资金计算。期间：今日、昨日、本月、上月，一律按 +08:00 的自然日与自然月。分三栏：① 自购：本人为归属用户且 buy_type=self 的子订单；② 分享：本人为归属用户且 buy_type=share 的子订单；③ 邀请：本人作为直推或间推受益人的邀请分佣。①② 各给四个期间的付款笔数、预估、已结算；③ 只给本月、上月两个期间的预估合计与已结算合计，不给笔数，不给今日、昨日，不按天、按平台或按好友拆分，避免上级借看板推出好友哪天下的单（BR-INV-16、BR-INV-17）。归期：付款笔数与预估按订单 paid_at 归期间；已结算按入账流水的会计日 accounting_date 归期间。计入付款笔数的订单用状态事实列举：已归因到本人、platform_status 到过 PAID 或之后、查询时 rebate_status ∈ {ESTIMATED, WAITING, CREDITED}；只付定金（DEPOSIT_PAID）、未归因、已失效（VOID）、已全额扣回（CLAWED_BACK）的不计；不使用「有效订单」「有效用户」这类会员口径（BR-INV-23）。预估 = 这些订单里 rebate_status ∈ {ESTIMATED, WAITING} 的本人份额合计，份额算法同 BR-FUND-18；已结算 = 期间内本人余额（available 子户）上对应类型分录的代数和，入账记正、红冲记负（① REBATE_CREDIT，② SHARE_CREDIT，③ REFERRAL_CREDIT 含间推）；这三类分录包括首次入账、错误更正的红冲与重记（BR-FUND-16）、已入账订单改归属的红冲与重记（BR-FUND-01 R14），各按自己的会计日归期间，改归属后同一笔收益不会在两个人名下各留一份（细则「已结算怎样聚合」）；不含 SETTLE_ADJUST、CLAWBACK、ADMIN_ADJUST，售后扣回、结算补差与人工调账是否并入、改成净额待财务确认。可选筛选 platform 只作用于 ①②；③ 始终是全部平台合计。开关 earnings.dashboard.enabled（默认 on）关闭后入口隐藏、接口返回 30701；earnings.dashboard.referral_visible（默认 on）关闭后不返回 ③。文案只取 BR-TEXT-01 细则「收益看板文案」。 | 待决策 | GET /v1/earnings/summary 响应 schema 与 platform 参数；页面 Earnings（收益看板，规划/01 §4.2）；配置 earnings.dashboard.enabled、earnings.dashboard.referral_visible；字典 earnings.\*（BR-TEXT-01）；钱包页与「我的」页入口；Agent 与客服口径（不得据看板向上级提供下级订单信息，BR-INV-16）；验收 AC-S2-61 |

### 6.2 细则

#### BR-FUND-01 细则 · 订单双状态模型

- 状态：已确认（负责人 2026-09-30，依据 docs/changes/20260930-拍板第一批.md §2）
- 默认值：采用双状态（platform_status + rebate_status），取代 规划/04 的单一 order_status；理由：平台事实与资金事实分属不同写者，避免 O7/O8 语义混杂和入账后维权无状态可落，且后端功能规划已按此设计。分佣快照的生成时点按 BR-CALC-10（已归因且 platform_status 首次 ∈ {PAID, RECEIVED, SETTLED}；DEPOSIT_PAID 不生成），快照中的等级与上级按 BR-CALC-12 取 paid_at 时刻，R2、R3 均同（C-06）。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 规划/04 §2.3、§4.1：「order_status 单一状态机：DEPOSIT_PAID→PAID→RECEIVED→CREDITED→SETTLED，终态 INVALID、CLAWED_BACK；平台订单状态和返利状态合在一个状态机里」
  - 规划/01 E09 F-ORD-06：「订单状态机为单一状态机（未拆平台订单状态与返利状态）」
  - PRD v2.1 §9.3：「订单状态含 RIGHTS_PROTECTING、PLATFORM_SETTLED；资金侧 credit_status：ESTIMATED→HOLDING→CREDITED→REVERSED」
  - 本条 R10 事件列 2026-10-03 前写法：「结算额写入且低于 booked_base_fen（负差，即时）/ 正差补差候选获批」（拿结算额 N 与基数 B 比）（2026-10-03 资金规则对齐（负责人批准），方案 §1，同-01）
  - 本条 R10 守卫与「到」列 2026-10-03 前写法：「BR-FUND-09」「不变；补差后结算佣金=0 且全部受益人与平台净额=0 → CLAWED_BACK」（结算佣金归零同时符合 R8 与 R10、负的结算佣金停在 CREDITED；改为新基数为 0 一律走 R8 写 CLAWBACK，R10 只处理新基数大于 0）（2026-10-03 资金规则对齐（负责人批准），方案 §2，同-03）
  - 本条 R9b 2026-10-03 前写法：「| R9b | CREDITED | 佣金变化（价保、比价降佣、联盟佣金调整；非退款、非维权） | 新 B>0 | 不变 | 更新 est_commission_fen、commission_version+1；新 B &lt; booked_base_fen：同事务写负向 SETTLE_ADJUST（sub_type=PRICE_PROTECT / PRICE_COMPARE / SETTLE_DIFF），uniq_key `{order_key}:{uid}:{role}:ADJ:{sub_type}:v{commission_version}`（平台侧 `{order_key}:PLATFORM:ADJ:{sub_type}:v{commission_version}`），同事务 booked_base_fen=新 B；新 B > booked_base_fen：进 BR-FUND-09 正差候选（C-07，负责人 2026-10-01 确认，拍板第二批 FUND-11） |」（与 BR-CALC-02「结算佣金非空后预估只存档」冲突；负责人 2026-10-03 选决-01 A：只存档并出差错单）（2026-10-03 资金规则对齐（负责人批准），方案 §2，决-01）
  - 本条「R9 与 R9b 的判定」2026-10-03 前写法：「同一次同步中 refunded_quantity 增加，或存在对应的 order_rights → R9；否则 → R9b。」（未区分新的结算记录，也没有写同一次更新同时命中逆向事件与结算额变化时的先后）（2026-10-03 资金规则对齐（负责人批准），方案 §2，同-04）
  - 本条 R10 记账列 2026-10-03 前写法：「SETTLE_ADJUST（BR-FUND-09）」（未引用 BR-CALC-09 的受益人状态规则）（2026-10-03 资金规则对齐（负责人批准），方案 §6.2，同-09）
  - 本条 R5 记账列 2026-10-03 前写法：「B_credit>0 写入账凭证（BR-FUND-05）；B_credit=0 不写凭证、不推送入账」（基数为 0 而预留大于 0 时平台预留漏记）（2026-10-03 资金规则对齐（负责人批准），方案 §7.3，同-23）
  - 本条 R5a 守卫与记账列 2026-10-03 前写法：「该受益人满足 BR-FUND-04 ⑦ 执行校验；在解除后的下一个结算批次（含补充批次）处理」「该受益人单独入账，uniq_key 沿用 `{order_key}:{uid}:{role}:CREDIT`（保证只入一次）」（⑦ 要求订单仍为 WAITING，R5a 从 CREDITED 出发永远过不了；没有写按哪个基数补、正差被延后的受益人怎么补）；R14 记账列原只写「同事务先红冲…再按新快照重记…」（重记时新受益人暂缓或被剥夺怎么办未写）（2026-10-03 资金规则对齐（负责人批准），方案 §6.6，同-13）
  - 本条 R5a 守卫与记账列 2026-10-03 写回时写法：「（订单为 CREDITED、rights_pending=false、结算记录 seq 未变）」「该受益人单独入账，金额按执行时的 booked_base_fen 与快照比例重算（应得 − 净额）；首次入账 uniq_key 沿用 `{order_key}:{uid}:{role}:CREDIT`（保证只入一次；改派后的新受益人用 R14 的 REASSIGN_CREDIT 键），延后的正差用 `{order_key}:{uid}:{role}:ADJ:{当前 seq}`」；R14 记账列写回时没有作废旧受益人待补记义务、为暂缓的新受益人开义务的写法（同一条结算记录下同一受益人第二次补记——补记后被全额扣回、又经 R13 恢复而再次暂缓——会撞第一次的 `ADJ:{seq}` 键，按「uniq_key 冲突视为已入账」被跳过，少补；补记项没有跨批次稳定的业务身份）（2026-10-03 资金规则对齐评审后修改，同步修正，方案 §13.6 第 1 条）
  - 本条 R10 事件、守卫与记账列 2026-10-03 写回时写法：「结算基数（结算额按 BR-CALC-02 换算）低于 booked_base_fen（负差，即时）/ 正差补差候选获批」「BR-FUND-09；新基数大于 0」「…新基数为 0（含结算佣金为负）不走本迁移，按迁移 R8」，「R9 与 R9b 的判定」写「→ R10（新基数为 0 时 R8）」（N 换算成 B 含向下取整，基数相等而联盟佣金变化时平台金额与 booked_n_fen 没有迁移承接；基数为 0 仍记预留的订单之后联盟佣金变化，既不满足「新基数大于 0」，也不是 R8 的「有效基数由 >0 变 0」）（2026-10-03 资金规则对齐评审后修改，同步修正，方案 §13.6 第 2 条）
  - 本条 P 表 2026-10-03 前只有 P1–P10，P8 写「| P8 | SETTLED | 维权/处罚 | 不变 | 写 order_rights |」，P10 写「| P10 | 任意 | 比当前更早阶段的状态码（倒退） | 不变 | 写待处理表并告警 |」，事件只有中文标签（没有入库首态 — → RECEIVED / SETTLED / INVALID 与 DEPOSIT_PAID → RECEIVED，晚到的订单会被整条拒绝；同状态更新不在表里，按「表外事件一律拒绝」会连金额更新一起丢掉；P10 报文里的金额记不记没有规定；结算前的维权、处罚没有对应行）（2026-10-03 资金规则对齐（负责人批准），方案 §5、§6.8、§8 O-02，同-07、同-15、决-12）
  - 本条 R2 与 R4 2026-10-03 前写法：R2「ESTIMATED（platform_status 已为 RECEIVED/SETTLED 时同事务再按 R4 进 WAITING）」「platform_status ≠ DEPOSIT_PAID 时同事务生成分佣快照」；R4 守卫「—」（首次入库即失效时会按 ≠ DEPOSIT_PAID 生成快照，与 BR-CALC-10 不符；R4 没有写缺平台收货时间不进 WAITING，与 BR-FUND-02 不符）（2026-10-03 资金规则对齐（负责人批准），方案 §5、§6.7，同-07、同-14）
  - 本条 R6、R8 2026-10-03 前写法：R6 事件「B 由 >0 变 0」、守卫「B 由 >0 变 0 分支：platform_status ≠ DEPOSIT_PAID，且新 B 非 null（BR-FUND-07）」；R8 事件「B 由 >0 变 0」、记账「CLAWBACK（BR-FUND-08）」（B 未限定为有效联盟佣金换算出的基数；R8 不写 sub_type 与订单原因码，而 BR-FUND-22 的恢复资格看原因码；VOID、CLAWED_BACK 标「终态」却可经 R12、R13 离开）（2026-10-03 资金规则对齐（负责人批准），方案 §2、§6.4、§8 O-03，同-02、同-11）
  - 本条 R3b 2026-10-03 前写法：「| R3b | VOID 且 user_id 为空 | CLAIM_APPROVED / ADMIN_REASSIGN | orders.locked=false | VOID 不变 | 只写 user_id、user_basis、locked=true；不生成快照、无分录 |」（找回在提交与审核时都拒绝 VOID 订单，CLAIM_APPROVED 走不到；未归因且已 VOID 的订单被同步重新归因时没有迁移可走；负责人选决-07 A：用户找回继续不受理 VOID 订单）（2026-10-03 资金规则对齐（负责人批准），方案 §6.11，同-17、决-07）
- 来源：规划/04 §2.3、§4.1、§7；规划/01 E09 F-ORD-06；PRD修订_后端功能规划 §3.1、§3.2、§1.7；PRD v2.1 §9.3；docs/changes/20261001-拍板第二批.md §8 ADD-05；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：6 处（计数仅作记录，落点见 README §0.6）

**platform_status 迁移表**（测试 ID `SM-PLT-P<n>`；平台状态码到事件的映射见 BR-FUND-02）：

| # | 从 | 平台事件 | 到 | 说明 |
|---|---|---|---|---|
| P1 | — | 付定金（PLATFORM_DEPOSIT_PAID） | DEPOSIT_PAID | |
| P2 | — / DEPOSIT_PAID | 付款（PLATFORM_PAID） | PAID | |
| P3 | PAID | 确认收货/完成（PLATFORM_RECEIVED） | RECEIVED | 写 received_at |
| P4 | RECEIVED | 结算（PLATFORM_SETTLED） | SETTLED | 写 settled_at；结算额写 order_settlements（BR-FUND-09） |
| P5 | DEPOSIT_PAID / PAID | 结算（PLATFORM_SETTLED，此前未给收货） | SETTLED | 同一事务依次补写 →PAID（如缺）、→RECEIVED、→SETTLED 三条 history；received_at 取结算时间 |
| P6 | DEPOSIT_PAID / PAID / RECEIVED | 失效（PLATFORM_INVALID） | INVALID | |
| P7 | SETTLED | 失效（PLATFORM_INVALID） | 不变 | 写 order_rights(type=INVALID_AFTER_SETTLE, status=SUCCEEDED)，settlement 按 BR-FUND-08 处理 |
| P8 | PAID / RECEIVED / SETTLED | 维权/处罚（PLATFORM_RIGHTS / PLATFORM_PUNISH） | 不变 | 写 order_rights（处罚 type=PUNISH，映射见 BR-FUND-02）；结算前同样只写 order_rights |
| P9 | INVALID | 平台回传非失效状态（PLATFORM_PAID / PLATFORM_RECEIVED / PLATFORM_SETTLED） | 平台当前状态 | 记 history 并告警；rebate_status 不自动变化，按 BR-FUND-22 |
| P10 | 任意 | 比当前更早阶段的状态码（倒退；按事件对应的阶段与当前状态比较得出，不是单独的事件） | 不变 | 写待处理表并告警；整条报文不落 orders 的任何列，原始报文留在 union_raw_payloads；待处理表记录与 order_illegal_transition 事件在本次事务内写入并提交（负责人 2026-10-03 资金规则对齐决-12 选 A；开关 order_sync.regression_hold.enabled，默认 on；off 时状态不迁移，报文里的金额、数量、时间、结算记录照常处理） |
| P11 | — | 确认收货/完成（PLATFORM_RECEIVED，首次入库即已收货） | RECEIVED | 同一事务补写 →PAID、→RECEIVED 两条 history；received_at 取平台返回的收货时间。缺该时间时按 P2 落 PAID，收货事件进待处理表，不进 WAITING（BR-FUND-02） |
| P12 | — | 结算（PLATFORM_SETTLED，首次入库即已结算） | SETTLED | 同一事务补写 →PAID、→RECEIVED、→SETTLED 三条 history；received_at 取平台收货时间，缺时取结算时间（同 P5）；结算额写 order_settlements |
| P13 | — | 失效（PLATFORM_INVALID，首次入库即失效，且有付款时间） | INVALID | 入库，供去重、找回判定与展示；返利状态按 R1 或 R2 入库后同一事务按 R6 置 VOID；不生成快照（BR-CALC-10）。两个付款时间都为空的不入库（BR-ATTR-25） |
| P14 | DEPOSIT_PAID | 确认收货/完成（PLATFORM_RECEIVED，此前没见到付款） | RECEIVED | 同一事务补写 →PAID、→RECEIVED；按 P2 的做法在同一事务生成快照（paid_at 取值按 BR-CALC-11）；received_at 同 P11 |
| P15 | 任意 | 与当前状态相同（重复上报，或不同原始码映射到同一状态） | 不变 | 不是迁移：不写 history、不告警、不算表外事件。本次报文的其余数据（佣金、数量、时间、结算记录、维权）照常处理 |

内部事件编码（PLATFORM_*）写入 specs/order-status-map/&lt;platform>.csv 与状态机 yaml；P10 倒退与 P15 同状态由「事件对应的阶段」与当前 platform_status 比较得出，不另设事件（2026-10-03 资金规则对齐方案 §5、§8 O-02）。判定先于写库：先按本表判定本次事件，属于表外事件或 P10 的，不更新订单的任何列；P11–P14 的入库首态与跳级只补 history 与时间字段，能否进 WAITING、能否入账仍按 R4 守卫与 BR-FUND-04 的月结校验。

platform_status=SETTLED 只表示联盟订单状态为「结算」，不表示已回款；回款由 BR-FUND-20 的 UNION_RECEIVABLE 核销表示。

**rebate_status 迁移表**（测试 ID `SM-REB-R<n>`）：

| # | 从 | 事件 | 守卫 | 到 | 记账 |
|---|---|---|---|---|---|
| R1 | — | 入库未归因 | — | UNATTRIBUTED | 无 |
| R2 | — | 入库已归因 | — | ESTIMATED（platform_status 已为 RECEIVED/SETTLED 时同事务再按 R4 进 WAITING；platform_status 为 INVALID（P13）时不生成快照，同一事务按 R6 置 VOID） | 无；platform_status ∈ {PAID, RECEIVED, SETTLED} 时同事务生成分佣快照，DEPOSIT_PAID 时在之后 P2（→PAID）或 P14 的同一事务内生成，INVALID 不生成（BR-CALC-10） |
| R3 | UNATTRIBUTED | CLAIM_APPROVED / ADMIN_REASSIGN | orders.locked=false（未被其他用户认领或改派） | ESTIMATED；platform_status 已为 RECEIVED/SETTLED 则直接 WAITING（settle_period 按原 received_at 取，BR-FUND-04） | 无分录；同事务设置 user_id、user_basis（CLAIM_APPROVED→claim，ADMIN_REASSIGN→admin；BR-ATTR-09），locked=true；platform_status ≠ DEPOSIT_PAID 时同事务生成分佣快照（BR-CALC-10；等级与上级取 paid_at 时刻，BR-CALC-12） |
| R3a | UNATTRIBUTED | SYNC_ATTRIBUTED（同步重跑用户归属成功，BR-ATTR-16） | orders.locked=false | ESTIMATED；platform_status 已为 RECEIVED/SETTLED 则 WAITING（settle_period 按原 received_at 取，BR-FUND-04） | 无分录；写 user_id、user_basis=param，不置 locked；platform_status ≠ DEPOSIT_PAID 时同事务按 BR-CALC-10 生成分佣快照 |
| R3b | VOID 且 user_id 为空 | ADMIN_REASSIGN / SYNC_ATTRIBUTED（同步重跑用户归属成功，BR-ATTR-16） | orders.locked=false | VOID 不变 | ADMIN_REASSIGN：只写 user_id、user_basis=admin、locked=true；SYNC_ATTRIBUTED：只写 user_id、user_basis=param，不置 locked；都不生成快照、无分录。用户找回不受理 VOID 订单（BR-ATTR-17 ④c、BR-ATTR-18），本迁移不含 CLAIM_APPROVED（负责人 2026-10-03 资金规则对齐决-07 选 A） |
| R4 | ESTIMATED | platform_status→RECEIVED 或 SETTLED | received_at 已按 BR-FUND-02 取得（平台返回的收货、完成时间，或 P5、P12 的结算时间）；取不到时不迁移，订单进待处理表 | WAITING | 无（写 received_synced_at、settle_period，BR-FUND-04） |
| R5 | WAITING | SETTLE_BATCH_CREDIT（所在结算批次经人工确认后执行，BR-FUND-04） | BR-FUND-04 ④ 一致性校验通过且 ⑦ 执行校验通过 | CREDITED | 按 BR-FUND-05 写入账凭证：份额为 0 的受益人不写，平台凭证（留存 + 预留）大于 0 就写，全部为 0 时不写凭证、只迁移状态；被剥夺的受益人写平台 FORFEIT 凭证（BR-CALC-13）；B_credit=0 不推送入账 |
| R5a | CREDITED | BENEFICIARY_RELEASE（受益人 held→active，BR-CALC-13；正差被延后的受益人恢复正常同此） | 该受益人的补记项通过 BR-FUND-04 ⑫ 的执行重验（订单为 CREDITED、rights_pending=false、结算记录 seq 未变、归属快照未变、该待补记义务未完成）；BR-FUND-04 ⑦ 的「仍为 WAITING」不适用；在解除后的下一个结算批次（含补充批次）处理 | 不变 | 该受益人按其待补记义务（beneficiary_credit_id，BR-FUND-04 ⑫）单独入账，金额按执行时的 booked_base_fen 与快照比例重算（应得 − 当前净额），凭证与义务完成同事务；首次入账义务 uniq_key 沿用 `{order_key}:{uid}:{role}:CREDIT`（保证只入一次），改派入账义务用 R14 的 REASSIGN_CREDIT 键，延后差额义务用 `{order_key}:{uid}:{role}:ADJ:DEFERRED:{beneficiary_credit_id}`（同一条结算记录下再次补记也不撞键）；转 forfeited 时份额记平台 `{order_key}:PLATFORM:FORFEIT:{uid}:{role}`，延后差额义务为 `{order_key}:PLATFORM:FORFEIT:{uid}:{role}:DEFERRED:{beneficiary_credit_id}`（默认处理，待财务确认） |
| R6 | UNATTRIBUTED / ESTIMATED / WAITING | 整单失效 / 全额维权 / 处罚 / 黑名单 / 有效基数 B_est 由 >0 变 0 | 基数归零分支：platform_status ≠ DEPOSIT_PAID，且新 B_est 非 null；B_est 按 BR-CALC-02 由有效联盟佣金换算，结算佣金已到之后预估单独变化不触发（BR-FUND-07） | VOID（终态） | 无（BR-FUND-07） |
| R7 | ESTIMATED / WAITING | 部分退款 / 部分维权 / 佣金变化 | 新 B>0，或原 B 已为 0 | 不变 | 无（重算预估） |
| R8 | CREDITED | 整单失效 / 全额维权 / 处罚 / 结算后退款或失效 / 有效基数由 >0 变 0（含结算佣金为负，BR-CALC-02） / 黑名单人工复核确认（BLACKLIST_CONFIRMED，超管或有权限账号 step-up 确认，一人可完成，拍板第二批 §8 ADD-05；默认处理，待财务确认） | — | CLAWED_BACK（终态） | CLAWBACK（BR-FUND-08）；sub_type 与订单原因码按 BR-FUND-08 细则「sub_type 与订单原因码」映射，同一事务写 reason_code |
| R9 | CREDITED | 部分退款 / 部分维权 | 新 B>0 | 不变 | 部分 CLAWBACK（BR-FUND-08） |
| R9b | CREDITED | 结算记录未变而预估佣金变化（含变为 0；价保、比价降佣、联盟佣金调整只反映在预估字段时） | — | 不变 | 无分录：只存档 est_commission_fen，不改应得、不改 booked_base_fen 与 booked_n_fen；预估换算出的基数与 booked_base_fen 不同时，生成差错单「入账后预估佣金变化」并告警，同一子订单同一预估值只生成一次（开关 settle.estimate_change_diff.enabled，默认 on；off 时只存档、不生成差错单）。原键 `ADJ:{sub_type}:v{commission_version}` 停用，不复用（2026-10-03 资金规则对齐决-01 选 A） |
| R10 | CREDITED | 结算基数（结算额按 BR-CALC-02 换算）低于 booked_base_fen，或与之相等而结算佣金的正数部分低于 booked_n_fen（负差，即时）/ 正差补差候选获批（含基数相等而结算佣金高于 booked_n_fen） | BR-FUND-09；新基数大于 0，或新旧基数都为 0（BR-FUND-05 基数为 0 仍记预留的订单） | 不变 | SETTLE_ADJUST（BR-FUND-09）；各受益人差额的去向按 BR-CALC-09 的受益人状态规则；基数相等（含新旧基数都为 0）时受益人差额为 0，只调平台金额，同样成对更新 booked_base_fen 与 booked_n_fen；原基数大于 0 而新基数为 0（含结算佣金为负）不走本迁移，按迁移 R8 |
| R11 | ESTIMATED / WAITING | HOLD / UNHOLD | BR-FUND-06 的角色 | 不变，hold=true/false | 无 |
| R12 / R13 | VOID / CLAWED_BACK | ADMIN_RESTORE | 见 BR-FUND-22 | 见 BR-FUND-22 | 见 BR-FUND-22 |
| R14 | ESTIMATED / WAITING / CREDITED | ADMIN_REASSIGN（已归属订单改派，BR-ATTR-20） | 有权限者 step-up 确认（一人可完成，ADD-05） | 不变（自迁移） | 非 CREDITED：无分录，作废旧快照、按新 user_id 生成新快照；CREDITED：同事务先红冲 `{order_key}:{old_uid}:{role}:REASSIGN_REV:{reassign_id}` 再按新快照重记 `{order_key}:{new_uid}:{role}:REASSIGN_CREDIT:{reassign_id}`；重记时在 BR-FUND-16 的锁内逐受益人按 BR-CALC-13 判定：新受益人暂缓的不写凭证，开改派入账义务，按 BR-FUND-04 ⑫ 的补记项入账；被剥夺的写 FORFEIT 凭证；同一事务作废旧受益人未完成的待补记义务（BR-FUND-04 ⑫） |

R9 与 R9b 的判定：同一次同步中 refunded_quantity 增加，或存在对应的 order_rights → R9（新基数为 0 时 R8）；否则有新的结算记录（BR-FUND-09 seq 变化）→ R10（原基数大于 0 而新基数为 0 时 R8；新旧基数都为 0 的仍走 R10，只调平台金额）；否则只有预估佣金变化 → R9b。

同一次更新同时满足逆向事件（R8、R9）与结算额变化（R10）时：先写结算记录，再按逆向事件记 CLAWBACK，差额按新基数与当前净额计算；R10 随后重算，差额为 0 不写（2026-10-03 资金规则对齐，方案 §2 R-27）。例：P0 订单（预留 2000，结算佣金 1000，本人 400、直推 80、平台 520）一次同步同时带来 2 件退 1 件与新的结算记录 500 → 新基数 400、预留 100，只按 CLAWBACK 扣一次：本人 −200、直推 −40、平台 −260，UNION_RECEIVABLE 净额 500；R10 重算差额为 0，不写。

VOID、CLAWED_BACK 是终态：订单同步等自动事件不得让订单离开，只有人工恢复（R12、R13，BR-FUND-22）可以离开；R3b 在 VOID 上只写归属、状态不变（2026-10-03 资金规则对齐方案 §8 O-03；原 R10 的第二种结局「补差后 → CLAWED_BACK」已随同-03 删去）。

**与 规划/04 单一 order_status 的映射**：DEPOSIT_PAID→(DEPOSIT_PAID, ESTIMATED 且不计预估)；PAID→(PAID, ESTIMATED)；RECEIVED→(RECEIVED, WAITING)；CREDITED→(RECEIVED 或 SETTLED, CREDITED)；SETTLED→(SETTLED, CREDITED 且已补差)；INVALID→(任意, VOID)；CLAWED_BACK→(任意, CLAWED_BACK)。

**与 规划/04 §4.1 迁移编号 O1–O12 的映射**（其他主题条目中出现的 O 编号按本表换算，规则内容不变；测试 ID SM-ORD-O&lt;n> 改用右列）：

| 04 编号 | 双状态下的迁移 |
|---|---|
| O1 | P1；rebate 按 R1/R2 入库，不计预估、不生成快照 |
| O2 | P2（+ 新入库时 R1/R2）；已归因时同事务生成分佣快照 |
| O3 | P3 + R4（写 received_at、settle_period） |
| O4 | 平台失效：P6 + R6；全额维权、处罚、黑名单命中：只 R6，platform_status 不变；CREDITED 命中黑名单不自动扣回，见 BR-ATTR-26 |
| O5 | R7 |
| O6 | R5 |
| O7 | P4，rebate_status=WAITING 不变（结算额写 order_settlements，入账时按结算额，BR-FUND-05） |
| O8 | P4，rebate_status=CREDITED 不变 + R10（补差按 BR-FUND-09） |
| O9 | 平台失效：P6（结算前）或 P7（结算后）+ R8；维权、处罚：P8（写 order_rights；2026-10-03 起 P8 含结算前）+ R8 |
| O10 | R9（写 CLAWBACK sub_type=PART_REFUND，不写负向 SETTLE_ADJUST，BR-FUND-08） |
| O11 | R3 |
| O12 | R14（ADMIN_REASSIGN，已归属订单改派，BR-ATTR-20；rebate_status 自迁移，platform_status 不变；CREDITED 时先红冲再重记） |

**为何拆分**：单一状态机下 O7「RECEIVED 收到结算→不变」丢失平台事实；O8 的 SETTLED 同时表示「联盟已结算」和「补差完成」；「入账后、平台结算前的维权」、hold、维权中都需要额外状态。拆分后平台事实与我方资金事实各有唯一写者。

**例**：淘宝子订单 10-01 付款 → (PAID, ESTIMATED)；10-05 10:00 确认收货 → (RECEIVED, WAITING)，settle_period=2026-10；联盟订单状态出现「结算」→ (SETTLED, WAITING)（示意：淘宝「订单结算」状态的出现时点待 规划/09 实测，可能紧随确认收货，与联盟出账、回款不是一回事）；11-24 月结账单日系统按联盟结算数据生成 2026-10 月结账单、一致性校验、人工确认批次后入账 → (SETTLED, CREDITED)（BR-FUND-04）；结算后维权成功 → (SETTLED, CLAWED_BACK)。

**异常**：VOID/CLAWED_BACK 后平台再回传有效状态，不自动复活，按 BR-FUND-22 处理。

**并发冲突返回**：后台对订单的 hold/unhold、改派、恢复等写操作 CAS 影响 0 行时返回 20902，data.resource=order（与 BR-ATTR-20 的 order_attribution、BR-WDR-08 的 withdrawal 共用 20902，按 data.resource 区分）。

按 C-01 默认处理（采用双状态，其他条目的单一 order_status 与 O 编号按上方两张映射表换算），已由负责人确认 2026-09-30；按 C-03 默认处理（20902 补 data.resource=order），待负责人确认；按 C-06 默认处理（快照生成时点按 BR-CALC-10、等级与上级取 paid_at），已由负责人确认 2026-09-30。

按 C-27 默认处理：(a) R3a、(b) R14、(c) R3b 状态口径代理已补（按 BR-ATTR-16、20 与 BR-CALC-10 现有写法），已由负责人确认 2026-09-30；(e) 入账守卫 credit_requires_settle 在月结口径下自然满足（BR-FUND-04 边界；月结由负责人 2026-10-01 确认，拍板第二批 FUND-01），不再待定；(g) R9b 负差即时记账与「结算少了立即扣」同一原则，已由负责人确认 2026-10-01（拍板第二批 FUND-11）；2026-10-03 资金规则对齐决-01 选 A 取代：R9b 改为只存档并出差错单，结算额的下调仍按 R10 负差即时扣；(d) R5a、(f) CREDITED 命中黑名单只写 blacklist_hit_after_credit 进人工复核、扣回按 R8 BLACKLIST_CONFIRMED，待财务确认。

2026-09-30 随 BR-FUND-04 月结口径对齐（变更记录 §3）：R3、R3a、R4 写 settle_period 取代 credit_due_at；R5 事件由 CREDIT_DUE 改为 SETTLE_BATCH_CREDIT；R5a 改为在后续结算批次处理；O3 映射与上方例子同改。双状态模型与迁移表结构不变。同步落点：规划/04 §4 状态机表 4.1 行（order-rebate.yaml R5 事件名、R4 写入字段）；BR-CALC-14、BR-CALC-25 中「CREDIT_DUE」改为 SETTLE_BATCH_CREDIT；05_CALC BR-CALC-13 细则「下一次 00:05 入账任务」。

#### BR-FUND-02 细则 · 平台状态映射与可入账事件

- 状态：待验证
- 默认值：四个平台的可入账事件按上表；P1 平台 vip、douyin 按确认收货（来源：PRD修订_后端功能规划 §2.7 可入账事件）、eleme 按完成或核销（后端功能规划 B12 将其列为核销型，§2.7 未列，属推定）；三者均在接入时经 规划/09 实测确认后才写入 creditable-events.yaml；可入账事件只决定进入 WAITING，入账时点随联盟月结批次（BR-FUND-04），不再设收货后等待期。
- 决策人：负责人
- 依赖平台能力：taobao/jd/pdd 订单接口：确认收货与结算是否为两个独立状态、各自时间字段是否返回、状态出现顺序；淘宝「订单结算」状态与联盟回款日是否同一时点（决定入账基数多大比例直接取结算额）；京东实际佣金归零能否与部分维权区分；美团核销时间字段（P1，D15）
- 取代：
  - 规划/02 §7.2：「淘宝「确认收货」→PLATFORM_RECEIVED、「结算」→PLATFORM_SETTLED（未说明结算先于或代替收货出现时如何处理）」
  - 本条正文 2026-10-03 前写法：「映射表之外的状态码必须告警并写入待处理表，不得丢弃、不得猜测。」「订单接口回传的结算佣金写入 order_settlements（source=API，BR-FUND-09）。」（没有写处罚类平台码映射为「处罚」而不是「失效」，映射为失效会让处罚订单进入可恢复的通道；没有写结算前不写结算佣金，拼多多预估与结算共用一个字段，收货后就当结算佣金会早付；不认识的码出现在未入账订单上时月结照常入账）（2026-10-03 资金规则对齐（负责人批准），方案 §6.8、§6.9，同-15、同-16、决-05）
- 来源：规划/02 §7.1、§7.2；PRD修订_后端功能规划 §2.7 可入账事件、§3.1；规划/07 §2 08 订单管理；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**各平台待确认的映射（进 规划/09 验证）**：

| 平台 | 需要验证的状态码 | received_at 候选字段 | 维权/失效信号 |
|---|---|---|---|
| taobao | 付款 / 订单成功（确认收货）/ 订单结算 / 失效，以及出现顺序；「订单结算」与联盟回款日是否同一时点 | 确认收货时间、结算时间字段（字段名待实测） | 维权退款接口、处罚订单接口 |
| jd | 有效码 validCode 各值 | 完成时间字段（待实测） | 实际佣金由 >0 变 0（能否与部分维权区分待验证） |
| pdd | order_status 各值 | 收货时间字段（待实测） | 随订单状态 |
| meituan | 完成/核销状态（W7） | 核销时间（待实测） | 随订单状态 |

**例**：淘宝订单若在 10-05 14:30 直接回传「订单结算」且结算时间 = 10-05 14:30，则同一事务写 received_at=2026-10-05T14:30:00+08:00、platform_status=SETTLED（history 补写 RECEIVED、SETTLED 两条）、order_settlements(source=API)，rebate_status 由 ESTIMATED→WAITING。10-06 平台补回真实确认收货时间 10-04 20:00 → 写 platform_received_at，received_at 与 settle_period 不变。

**例（缺平台收货时间，2026-10-03 资金规则对齐 E-22）**：淘宝订单 10-08 确认收货，接口没有收货时间 → 不按 R4 进 WAITING（R4 守卫），订单仍为 (PAID, ESTIMATED)，收货事件进待处理表；11-03 出现结算状态、结算时间 11-03 → P5 进 SETTLED、received_at=11-03，同事务按 R4 进 WAITING，settle_period=2026-11，进 12-24 生成的 2026-11 账单。不用我方同步时间代替收货时间。淘宝结算状态的出现时点待 CAP-TB-07、CAP-TB-08 实测，不写成事实。

**乱序与去重**：只按 BR-ATTR-01（G-12）——配置 attr.mtime_ordering.&lt;platform>（默认 false）：false 时不按更新时间丢弃，只按 content_hash 去重；true 时 platform_modified_at 小于库内值丢弃、相等且 content_hash 不同照常处理。两种配置下状态倒退都按 BR-FUND-01 P10 不迁移、写待处理表并告警，整条报文不落 orders 的任何列（决-12 A）。理由：平台更新时间是否单调未经 规划/09 实测，默认不丢弃才不会漏掉退款等逆向更新。

**异常**：状态码未知 → 告警 + 待处理表 + 订单保持原状态，返利状态为 ESTIMATED / WAITING 的同时置 hold（UNMAPPED_STATUS，决-05 A）；状态倒退 → P10（整条不落库，决-12 A）；received_at 缺失 → 待处理表，每日告警汇总。

**例（处罚类状态码，2026-10-03 资金规则对齐 E-23）**：拼多多订单（金额同 P0：预留 2000，结算佣金 1000）已入账；09 实测确认 order_status 10 表示已处罚后，映射为 PLATFORM_PUNISH → 写 order_rights(type=PUNISH)，按 R8 扣回本人 400、直推 80、平台 520，订单 CLAWED_BACK，原因码 PUNISH；之后状态变回 5（已结算）→ platform_status 照常更新，不告警、不出差错单、不恢复（BR-FUND-22）。实测前 10 不在映射表里：出现时告警进待处理表，已入账订单由人工按 BR-FUND-08 处理；未入账订单同时置 hold。

**例（拼多多结算前不写结算佣金，E-24）**：10-08 确认收货（order_status 2），佣金字段 1000 只写 est_commission_fen；11-24 账单日仍未到 5 → 记「应结未结」，不进批次候选；11-28 变为 4（审核失败）→ 未入账，没有资金移动。

#### BR-FUND-03 细则 · 预估返利生成与变更

- 状态：默认假设
- 默认值：业务口径沿用 规划/04 O2/O5（已确认；双状态下即 P2/R2 与 R7，见 BR-FUND-01 映射表），状态字段表述依赖 BR-FUND-01 拍板；若不采纳双状态，按 BR-FUND-01 中的 order_status 等价映射执行。推送对象、触发与去重归 BR-TEXT-09 维护（C-25）。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 本条细则「计算」2026-10-03 前写法：「B_est = 联盟口径推广者预估收入（已扣技术服务费），取 orders.est_commission_fen 最新值」（把 N 当 B，且结算佣金已到之后仍取预估）（2026-10-03 资金规则对齐（负责人批准），方案 §1、§2，同-01、同-02）
- 来源：规划/04 §1 预估佣金、§2.3、§4.1 O1/O2/O5/O11；规划/02 §8.3；PRD v2.1 §9.3；PRD修订_后端功能规划 §3.1；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

**计算**：B_est 由有效联盟佣金（BR-CALC-02：settle_commission_fen 为空时取 est_commission_fen 最新值，非空时只取结算佣金）按 BR-CALC-02 换算（含扣平台预留）；受益人份额 = f(B_est, 快照比例)。

**例**：本例预留比例为 0。B_est=1234 分，快照 自购 5000bp、直推 1000bp → 自购预估 617 分、直推预估 123 分（平台 494 分不展示）。买家部分退款 2 件退 1 件，联盟回传 B_est=617 → 自购预估 308 分、直推 61 分，订单页显示新预估与原因码 PART_REFUND。

**推送**：对象、触发、合并与去重只在 BR-TEXT-09 维护（C-25）：该子订单份额 >0 的全部受益人（订单归属用户、直推上级、间推上级）各推自己的份额，发给上级的只含金额与状态（J7）；去重键 `{order_key}:{uid}:{role}:TRACKED`。C-25 已由负责人决定（拍板第二批 OPS-02：全部受益人都推，入账提醒在月结批次完成后推）。

**边界**：首次入库 B_est=0 的已归因订单（如 0 佣金商品）：ESTIMATED，展示「本单无返利」，不推送；此后照常 R4，随结算批次 B_credit=0 → R5 进 CREDITED、不写凭证、不推送入账，订单页仍显示「本单无返利」（BR-FUND-17）。

**快照时点**：已归因订单首次入库即为 DEPOSIT_PAID 时不生成分佣快照、不计预估；尾款付清（P2）的同一事务内生成快照，快照中的等级与上级取 paid_at 时刻（BR-CALC-10、BR-CALC-12）。例：10-01 20:00 付定金入库 → (DEPOSIT_PAID, ESTIMATED)，无快照；10-11 00:10 付尾款 → 同事务生成快照，等级与上级取 paid_at 时刻（预售单 paid_at 的取值以 BR-CALC-12 为准）。

按 C-06 默认处理（快照生成时点与取值时点以 BR-CALC-10、BR-CALC-12 为准），已由负责人确认 2026-09-30。

#### BR-FUND-04 细则 · 入账时点与入账任务

- 状态：已确认（入账方向由负责人 2026-09-30 确定，账单来源与预计结算月份口径由负责人 2026-09-30 补充确定，依据 docs/changes/20260930-拍板第一批.md §3 D11 / BR-FUND-04 / G-16 / 放量 S2 行、§6「月结结算流程参数」、§10 第 1、2 项；月结入账与下表流程参数默认值由负责人 2026-10-01 确认，依据 docs/changes/20261001-拍板第二批.md FUND-01、FUND-07；首个月结批次须待该平台 08b 通过，负责人 2026-10-01 补充）
- 负责人已定方向：「实际以联盟为准，下单就入账预估；追随联盟统一出账单日，后台人工核查无误后再执行结算；有接口可每天轮询」。落地为：①订单付款并同步入库即生成预估收益（不可提现）；②订单状态每日轮询联盟接口同步；③可提现入账不再按「确认收货满 N 天逐单入账」，改为跟随联盟月结：月结账单日系统按联盟结算数据自动生成月结账单，后台核查无误、人工确认后批量结算，写入可提现余额。
- 负责人已定（2026-09-30 补充，变更记录 §10）：账单来自联盟返回数据，系统自动生成，人工确认后结算（负责人原话「月结肯定是根据联盟返回的账单，然后再分佣结算给用户，为什么是财务上传的？」）；预计结算月份看联盟返回字段，一般是次月结算上月确认收货的订单。参照花卷云（优券汇现用）「月结对账单」与「结算设置」的做法：每月月结账单日（可选 22–28 日，优券汇用 24 日）生成月结账单，账单状态 出账中 → 已出账 → 结算中 → 已结算（另有定时结算未到时刻的「待结算」），后台在账单上选择立即结算或定时结算并确认；只参照流程，字段与编码按 D19 自定。
- 默认值（流程参数；负责人 2026-10-01 确认按下表执行，拍板第二批 FUND-07：账单日 24 日、0 分容差、单人确认、每批 5000 单，其余各项同表）：

| 参数 | 默认 | 理由 |
|---|---|---|
| 月结账单日 settle.bill_day | 每月 24 日（取值 22–28，各平台同一天）；出账日 = 月结账单日，当日资产快照完成后开始生成 | 与花卷云可选范围一致，默认取优券汇现行 24 日；联盟一般在次月 20 日前后完成上月确认收货订单的结算（待 CAP-TB-08、CAP-JD-08、CAP-PDD-08、CAP-MT-08 核实），24 日生成可覆盖多数已结算订单 |
| 账单月与范围 | 账单月 M = 月结账单日所在月的上一自然月；范围为 WAITING、settle_period ≤ M 且已有联盟结算数据的子订单（含以前月份顺延未结的） | 负责人「次月结算上月确认收货的订单」；以前月份因维权、hold、联盟晚结算而未结的订单随后续账单自然带上，不需人工顺延结算周期 |
| 结算周期取法 settle.period_basis.&lt;platform> | received_at 所在自然月（+08:00）；平台先给结算后给收货时 received_at 本就取结算时间（BR-FUND-02） | 联盟一般按确认收货时间归月结算；各平台口径待 CAP-TB-08、CAP-JD-08、CAP-PDD-08、CAP-MT-08 核实后按平台配置 |
| 结算数据来源 settle.statement_source.&lt;platform> | api：order-sync 从联盟订单接口同步结算佣金与结算时间；upload 只在该平台联盟接口不可用（对应 CAP 未判为「支持」或接口持续故障）时由 finance 上传联盟结算明细 | 负责人：账单来自联盟返回数据，不是财务上传；两种来源都作为联盟结算数据参与 ④ 校验，规则相同 |
| 一致性校验容差 settle.batch.match_tolerance_fen | 0 分（联盟结算佣金换算的 B 与分佣快照当前版本 base_fen 须完全一致） | 负责人要求「核查无误」；正常情况下结算数据写入时已按 BR-CALC-02 与 R7 生成新版本，两者相等，不一致说明同步或快照有问题，进差错单由人工判断；入账基数始终由联盟结算额换算（BR-FUND-05、BR-CALC-02），容差只决定是否要人工看 |
| 结算方式 | 确认时选择：立即结算（默认选中）或定时结算（指定 scheduled_at）；每次确认单独选择，不设全局配置 | 参照花卷云「结算设置」弹窗；定时结算便于避开高峰或与财务回款时点对齐 |
| 确认人权限 | finance 或 super，step-up 后单人确认；记录 confirmed_by、confirmed_at；账单与首批批次由系统在月结账单日自动生成，补充批次由 finance 手动发起 | 批次已经过系统逐单校验；资金操作一人可完成（拍板第二批 §8 ADD-05） |
| 批次上限 settle.batch.max_orders | 5000 个子订单（沿用原 settle.credit.max_orders_per_run 的取值） | 控制单次执行时长与单批垫资增量（BR-FUND-20）；超出拆多批，随账单一次确认 |
| 预计结算月份推算 settle.period_offset_months.&lt;platform> | 1（联盟未返回结算时间时，预计结算月份 = 确认收货月 + 1 个月） | 负责人「一般都是次月结算上月确认收货的订单」；联盟返回结算时间后以联盟为准 |
| 逾期宽限 settle.statement.grace_days | 10 天（自 expected_credit_period 当月的月结账单日起算） | 预计结算月份的账单日后 10 天仍未入账，用户侧改显示「入账核对中」，避免长期显示已过时的预计 |
| 补充批次 | 允许，对同一月结账单由 finance 发起，流程同首批 | 差错单、维权 / hold 解除或联盟结算数据后到的订单不必多等一个月 |
| hold / 维权中的子订单 | 记「暂缓」，不生成差错单 | 这类订单与联盟数据并无不一致，只是暂不能入账；解除后进入补充批次或下一期账单 |

- 决策人：负责人（流程参数会同财务）
- 依赖平台能力：CAP-TB-08、CAP-JD-08、CAP-PDD-08、CAP-MT-08（联盟结算佣金与结算时间字段能否经订单接口取得及其语义——是否即联盟向推广者出账结算的时间、结算周期归属口径、联盟结算日、结算数据能否按 sub_order_id 对应我方子订单）；订单每日轮询依赖 CAP-TB-07、CAP-JD-07、CAP-PDD-07
- 取代：
  - 规划/01 §5 J1 步骤 6、规划/04 §2.3 RECEIVED 行：「预计到账日 = 收货日 + 15 天」
  - 规划/04 §2.3 PAID 行、规划/01 F-PROD-05、J1 步骤 1：「「确认收货 15 天后到账」」
  - 规划/06 Q-B2：「日结门槛（低于此预估佣金的子订单等月结）」
  - PRD修订_后端功能规划 §2.7：「每天 00:30 的任务把到期子订单入账」
  - PRD v2.1 §9.3：「维权失败→RECEIVED 恢复观察期剩余天数（暂停计时）」
  - 本条 2026-09-30 前写法：「逐单入账：进入 WAITING 写 credit_due_at = received_at + wait_days × 24 小时（settle.wait_days.&lt;platform>，默认 15）；入账任务 settle.credit 每日 00:05 运行，处理 credit_due_at ≤ run_at 的子订单；日结门槛 settle.daily_min_fen 与 credit_requires_settle 守卫；单批上限 settle.credit.max_orders_per_run；预计入账日 expected_credit_date = 首个 run_at ≥ max(credit_due_at, received_synced_at, 维权关闭或 hold 解除时刻, 开关打开时刻) 的日期」（负责人 2026-09-30 改为跟随联盟月结批量入账）
  - 本条 2026-09-30 前默认值：「满 15×24 小时后的首次 00:05 任务入账，预计入账日一般为收货日+16 天；维权或 hold 期间 credit_due_at 不顺延」
  - 本条 2026-09-30 月结初稿（负责人 2026-09-30 补充取代，变更记录 §10）：「③ 账单导入：联盟对周期 M 出结算账单（出账日读配置 settle.statement_day.&lt;platform>，默认 M 的次月 20 日）后，结算明细经接口拉取或由 finance 在后台上传（settle.statement_source.&lt;platform> ∈ {api, upload}，默认 upload），逐行写 order_settlements(source=STATEMENT)，并登记账单 statement_id = `{platform}:{M}:{导入序号}`；整份导入完成后才能比对」「④ 逐单比对：|账单结算佣金 − 我方同步佣金| ≤ 容差（我方同步佣金 = 最新 source=API 的结算额，无则 est_commission_fen）」「我方 WAITING 且 settle_period=M 但账单无此单的生成差错单「应结未结」，差错单处理可把 settle_period 顺延一个周期」「⑥ 批次须由 finance 或 super 在 step-up 后确认」（按批次确认、无结算方式）
  - 本条 2026-09-30 月结初稿 ⑪：「expected_credit_period（= settle_period，即确认收货月）；预计出账日 + settle.statement.grace_days 仍无该周期已确认批次时 credit_overdue=true」（负责人 2026-09-30 补充：预计结算月份看联盟返回字段，一般次月结算上月确认收货订单）
  - 本条 2026-09-30 月结初稿推送：「批次执行完成后，每用户汇总一条「已结算」推送（同日多批合并）」与 BR-TEXT-09 原「D 日 09:00 日汇总」两种写法（统一为批次完成后推送、免打扰时段顺延，见下方「推送」）
  - 本条 2026-09-30 写法：「本条流程参数为默认处理，待负责人确认（变更记录 §6、§9）」「⑦ … 以 B_credit（= 联盟结算额）按分佣快照拆分」（流程参数由负责人 2026-10-01 确认，拍板第二批 FUND-01、FUND-07；入账基数按 2026-10-01 平台预留比例决定由结算额经 BR-CALC-02 换算，docs/changes/20261001-平台预留比例.md）
  - 本条 ⑩ 与细则「held 受益人」2026-10-03 前只写「held 受益人解除后按 BR-FUND-01 R5a 在后续批次（含补充批次）单独入账」（账单范围与 ④ 校验只针对 WAITING 子订单，批次明细没有受益人维度；没有写补记项由谁生成、要不要校验、明细怎么记、按哪个基数算，正差被延后的受益人由什么触发）（2026-10-03 资金规则对齐（负责人批准），方案 §6.6，同-13）
  - 本条 ⑫ 2026-10-03 写回时写法：「月结账单生成任务与补充批次发起时，对 CREDITED 子订单中待补记额大于 0 的受益人（暂缓未入账，或正差被延后；待补记额见 BR-FUND-19 ⑤）生成补记项」「执行时在 BR-FUND-16 细则「加锁流程」的锁内重验：订单仍为 CREDITED、rights_pending=false、结算记录 seq 与生成时一致，否则跳过」「首次入账用 CREDIT 键（改派后的新受益人用迁移 R14 的 REASSIGN_CREDIT 键），延后的正差用 `{order_key}:{uid}:{role}:ADJ:{当前 seq}` 键（BR-FUND-01 R5a）」「按 BR-CALC-13 没收，写 FORFEIT 凭证。金额为 0 不写凭证。」；细则例 (b)「U1 解冻后补记 +80（键 ADJ:{当前 seq}）」（结算记录身份不等于补记义务身份：R13 恢复可以不产生新的结算 seq 而产生新的待补记义务，同一 seq 下第二次补记撞第一次的键而被跳过，少补；跨批次纳入、重试没有共用的业务身份）（2026-10-03 资金规则对齐评审后修改，同步修正，方案 §13.6 第 1 条）
  - 本条 ⑥ ⑦ 2026-10-03 前写法：「或定时结算（指定 scheduled_at，须晚于确认时刻，且不在每日 00:00 至当日资产快照完成期间；到时自动执行；执行前可撤销定时，批次回到 DRAFT）」「每日 00:00 至当日资产快照完成（BR-FUND-18）期间不执行批次（定时结算时刻落在该时段的，顺延到快照完成后执行）。」（保存定时时快照完成时刻未知，两句重复或矛盾；改为保存按名义时段校验、执行时等快照）；⑤–⑧ 原只有文字、没有迁移表（崩溃后停在 EXECUTING 怎么恢复、哪些状态能取消未定义）（2026-10-03 资金规则对齐（负责人批准），方案 §6.3，同-10、决-02）
- 来源：规划/04 §1、§2.3、§4.1 O6；规划/02 §1 原则 8、§5.2；规划/06 Q-B2；规划/00 §2；PRD修订_后端功能规划 §2.7；规划/01 §5 J1、F-PROD-05；docs/changes/20260930-拍板第一批.md §3；docs/changes/20260930-拍板第一批.md §10（负责人 2026-09-30 补充）；花卷云后台功能明细 09_财务管理 §2 月结对账单、§3.1 结算设置（只参照流程）；docs/changes/20261001-拍板第二批.md FUND-01、FUND-07；docs/changes/20261001-平台预留比例.md；docs/changes/20261001-拍板第二批.md §8 ADD-05；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：6 处（计数仅作记录，落点见 README §0.6）

**流程**（状态机不变，只改 R5 的触发）：订单付款同步入库 → ESTIMATED（预估收益）→ 确认收货同步 → WAITING（写 settle_period）→ 联盟返回结算数据（settle_commission_fen、union_settled_at）→ 月结账单日系统生成账单月 M 的月结账单（出账中）→ 一致性校验 → 生成批次（DRAFT，账单已出账）→ 人工确认并选立即 / 定时结算（CONFIRMED，定时未到为待结算）→ 批量入账（R5，WAITING → CREDITED；账单结算中 → 已结算）。入账后联盟再调整结算额，按 BR-FUND-09 补差；逆向事件按 BR-FUND-08 扣回，均与批次无关。

**月结账单状态**（后台显示；由该账单最近一轮批次（首批或最近一次补充批次）的状态派生，不另存状态；驳回的 CANCELLED 批次不参与派生）：

| 账单状态 | 判定 | 对应批次状态 |
|---|---|---|
| 出账中 | 月结账单日生成任务已开始，校验与批次尚未全部生成 | 批次未生成或生成中 |
| 已出账 | 生成完成，存在未确认批次；本轮批次全部被驳回时也回到此状态（可重新生成或发起补充批次，记审计） | DRAFT |
| 待结算 | 已确认、定时结算，未到 scheduled_at | CONFIRMED（scheduled_at 未到） |
| 结算中 | 已确认且已到执行时刻，尚有批次未完成 | CONFIRMED（已到时刻待启动）/ EXECUTING / PARTIAL |
| 已结算 | 本轮确认的批次全部执行完 | DONE |

**结算批次迁移表**（测试 ID `SM-SB-<n>`；2026-10-03 资金规则对齐方案 §6.3：⑤–⑧ 的表格化，已确认；SB9 为默认处理）：

| # | 从 | 事件 | 守卫 | 到 | 说明 |
|---|---|---|---|---|---|
| SB1 | — | 生成 | 该平台 credit.enabled 为 on，候选非空 | DRAFT | 月结账单生成或补充批次发起 |
| SB2 | DRAFT | 确认 | 有权限者 step-up；定时须晚于确认时刻，且不落在资产快照的名义时段内（时段取值见 BR-FUND-18） | CONFIRMED | 记 confirmed_by、confirmed_at、settle_mode |
| SB3 | CONFIRMED | 撤销定时 | 定时结算且尚未开始执行 | DRAFT | |
| SB4 | DRAFT | 驳回 | step-up，必填原因 | CANCELLED（终态） | 批内订单保持 WAITING |
| SB5 | CONFIRMED | 开始执行 | 已到执行时刻；当日资产快照已完成或已超时（BR-FUND-18）；settle.auto.enabled 与该平台 credit.enabled 都为 on | EXECUTING | 快照没完成就等，不执行 |
| SB6 | EXECUTING | 明细全部处理完 | — | DONE（终态） | |
| SB7 | EXECUTING | 开关被关闭 | — | PARTIAL | 已入账的保持，未处理的保持 WAITING |
| SB8 | PARTIAL | 继续执行 | step-up；两个开关都为 on | EXECUTING | |
| SB9 | EXECUTING | 执行进程中断后被调度重新接管 | 批次仍为 EXECUTING 且没有存活的执行者 | EXECUTING（自迁移） | 从第一条未处理的明细续跑；已入账的靠 uniq_key 跳过 |

表外：已确认的立即结算批次、EXECUTING、PARTIAL、DONE 都不能到 CANCELLED；不新增「取消已确认批次」或「关闭 PARTIAL 批次」的能力，已入账的不回滚，没处理的子订单靠续跑或被后续批次重新纳入（负责人 2026-10-03 资金规则对齐决-02 选 A）。并发冲突返回 20902（data.resource=settle_batch）。一个 WAITING 子订单可以出现在多个批次的明细里，每个批次执行时逐单重验（⑦），已入账的记 skipped；停在 PARTIAL 的批次不妨碍这些子订单进入后续批次。

**例（崩溃续跑，2026-10-03 资金规则对齐 E-18）**：一批 10 个子订单（每单同 P0：本人 400、直推 80、平台 520），执行到第 3 单提交后进程崩溃 → 批次停在 EXECUTING；调度发现没有存活的执行者，按 SB9 从第 4 单续跑，前 3 单 uniq_key 已存在、⑦ 重读也已是 CREDITED，跳过；最终 10 单各入账一次，用户合计 4800、平台 5200，UNION_RECEIVABLE 10000。确认后的立即结算批次调用取消 → 拒绝。

**校验结果**（账单范围内每个子订单只有一种结果）：

| 我方子订单 | 结果 | 订单 |
|---|---|---|
| WAITING，B_settle 与快照 base_fen 之差在容差内，hold=false，rights_pending=false | 进批次候选 | 批次执行后 CREDITED |
| WAITING，差额超出容差 | 差错单「账单金额不一致」 | 保持 WAITING；差错单结论「以联盟为准」后进补充批次 |
| WAITING，hold=true 或 rights_pending=true | 暂缓 | 保持 WAITING；解除后进补充批次或下一期账单 |
| 联盟结算数据对应 ESTIMATED（收货同步缺失）/ VOID / CLAWED_BACK / 我方无单（上传备用时） | 差错单（类型沿用 BR-FUND-09） | 不入账 |
| CREDITED | 不进批次，按 BR-FUND-09 补差 | 不变 |
| WAITING 且 settle_period=M，未 hold、未维权，截至生成开始仍无联盟结算数据 | 差错单「应结未结」 | 保持 WAITING；联盟结算数据到达后进补充批次或下一期账单（settle_period ≤ 账单月即在范围内，不需顺延） |

**例 1（正常，立即结算）**：淘宝子订单 10-01 付款同步 → (PAID, ESTIMATED)，预估收益自购 617 分（不可提现）；10-05 14:30 确认收货，当日同步 → (RECEIVED, WAITING)，settle_period=2026-10，联盟尚未返回结算时间 → expected_credit_period=2026-11（10 月 + 1），订单页按 BR-TEXT-04 展示「预计 11 月结算」。11-20 联盟返回结算佣金 1234 与结算时间 2026-11-20 → expected_credit_period 仍为 2026-11（取联盟）。11-24 快照完成后系统生成 2026-10 月结账单（出账中）；该单 B_settle 1234 = 快照 base_fen 1234 → 进批次 taobao:2026-10 第 1 批 → 账单已出账；11-24 16:00 finance step-up 确认、选立即结算 → 结算中 → 执行，B_credit=1234（种子版本平台预留为 0，B_credit = 结算额，BR-CALC-02）入账 617/123/494（BR-FUND-05）→ (SETTLED, CREDITED)；16:20 全部批次 DONE → 账单已结算，16:20 推送「已结算」。

**例 2（金额不一致）**：同上，联盟结算佣金 1100（B_settle=1100），但分佣快照当前版本 base_fen 仍为 1234（结算数据写入时未生成新版本）、容差 0 → 差错单「账单金额不一致」，不入账；财务核实后结论「以联盟为准」→ 补充批次按 B_credit=1100 入账 550/110/440。

**例 3（维权暂缓）**：账单范围含该单，但 11-18 起淘宝维权处理中（rights_pending=true）→ 暂缓，期间预计结算月份返回 null，订单显示售后中；12-02 维权失败关闭 → finance 发起补充批次入账，入账额仍为联盟结算额；若维权成功则按 BR-FUND-07 作废，不入账。

**例 4（应结未结）**：10-31 23:50 确认收货，settle_period=2026-10；11-24 生成 2026-10 账单时联盟尚未返回该单结算数据 → 差错单「应结未结」，订单保持 WAITING；12-02 联盟返回结算时间 2026-12-02 → expected_credit_period=2026-12；12-24 生成 2026-11 账单时（settle_period 2026-10 ≤ 2026-11）该单在范围内，校验通过后随该账单结算；财务也可在 12-02 后对 2026-10 账单发起补充批次提前结算。

**例 5（定时结算与执行中关闭开关）**：11-24 18:00 finance 确认 2026-10 账单、选定时结算 11-25 10:00 → 账单待结算；11-25 10:00 开始执行 → 结算中；执行到第 3000 单时 settle.auto.enabled 被置 off → 立即停止，批次 PARTIAL，3000 单已 CREDITED，其余保持 WAITING；开关重新打开后 finance step-up 继续执行，已入账的 3000 单 uniq_key 已存在，不会重复入账。

**边界**：联盟结算佣金为 0 且快照 base_fen 为 0 → 进批次，B_credit=0 只迁移状态、不写凭证（BR-FUND-05）。订单佣金变化（价保、部分退款）在 WAITING 期间照常按 BR-FUND-03、R7 更新预估；校验时以分佣快照当前版本为准。原日结门槛 settle.daily_min_fen 与 credit_requires_settle 守卫（BR-CALC-15、BR-CALC-25）在本口径下自然满足：只有已有联盟结算数据的订单进入账单，入账基数一律由联盟结算额换算，不存在「未结算先入账」的订单。联盟结算时间晚于当月月结账单日开始生成的时刻时，该单进入下一期账单或补充批次，expected_credit_period 仍按联盟结算时间所在月返回，可能早于实际结算月，逾期按 ⑪ 与宽限天数处理（见 6.3 第 19 条）。

**维权中 / hold**：校验与执行时 rights_pending=true 或 hold=true 的子订单都不入账（BR-FUND-06），不改变 rebate_status；期间预计结算月份返回 null（显示售后中 / 核对中）；解除后进入补充批次或下一期账单，预计结算月份按 ⑪ 重新返回。

**held 受益人与补记项**（⑫）：一单中除 held 受益人（BR-CALC-13）外的全部受益人同批入账；held 受益人解除后按 BR-FUND-01 R5a 在后续批次（含补充批次）以受益人补记项单独入账，金额按执行时的 booked_base_fen 重算，转 forfeited 时份额记平台（FORFEIT 凭证）；正差被延后的受益人同样经补记项补记。每一次待补记义务有自己的 beneficiary_credit_id，跨批次纳入、重试、并发执行都按它只记一次；延后的正差用 `ADJ:DEFERRED:{beneficiary_credit_id}` 键，同一条结算记录下再次补记也不撞键（2026-10-03 评审后修改）。按 C-27 (d) 默认处理，待财务确认。

**例（受益人补记项，2026-10-03 资金规则对齐 E-21）**：(a) 淘宝预留 2000，本人 5000、直推 1000；入账时 U1 冻结（暂缓），P1 +80、平台 +520；暂缓期间结算佣金改为 900 → P1 −8、平台 −52，U1 应得变 360；U1 解冻后下一个账单日生成补记项，执行时按 booked_base_fen 720 补 U1 +360（不按入账当天的 800 补 400），UNION_RECEIVABLE 900。(b) P0 入账后 U1 才被冻结，冻结期间结算佣金改为 1200 的正差获批：P1 +16、平台 +104，U1 的 +80 延后 → UNION_RECEIVABLE 1120；U1 解冻后补记 +80（键 ADJ:DEFERRED:{beneficiary_credit_id}），UNION_RECEIVABLE 1200；若 U1 转为封禁，这 80 写 FORFEIT 记平台，同样 1200。(c) 预留 0、本人 5000、没有上级，已入账 U1 500、平台 500；后台改派给冻结中的 U2（R14）→ 红冲 U1 500、平台 500，按新快照重记只写平台 500，U2 的 500 待补记；U2 解冻后补记 500（REASSIGN_CREDIT 键），UNION_RECEIVABLE 1000。补记项执行时订单已被扣回为 CLAWED_BACK → 跳过，不补钱。(d) 同一条结算记录下第二次补记（2026-10-03 评审后修改；预留 0、本人 5000、没有上级）：seq1 结算佣金 1000 入账 U1 500、平台 500；seq2 结算佣金 1200 时 U1 冻结，正差获批 → 平台 +100，U1 的 +100 开延后差额义务 D1，UNION_RECEIVABLE 1100 = 1200 − 100；U1 解冻后补记 +100（键 `…:U1:self:ADJ:DEFERRED:D1`），D1 完成，U1 净额 600，UNION_RECEIVABLE 1200；全额维权扣回 U1 −600、平台 −600，UNION_RECEIVABLE 0，订单 CLAWED_BACK，结算记录仍是 seq2；平台恢复有效后人工 R13 恢复，此时 U1 又冻结 → 平台 +600，U1 的 600 开新义务 D2，UNION_RECEIVABLE 600 = 1200 − 600；U1 再次解冻 → 补记 +600（键 `…:U1:self:ADJ:DEFERRED:D2`，与 D1 的键不同，不会被当作已入账跳过），U1 净额 600，UNION_RECEIVABLE 1200 = booked_n_fen 1200 − 0。各步凭证借贷相等。同一义务同时被补充批次与下一期账单的批次纳入时，两条明细引用同一 beneficiary_credit_id，先取得锁的一批写凭证并完成义务，另一批重验见义务已完成，记 skipped；批次续跑或任务重复投递同理只记一次。

**平台入账开关 credit.enabled.&lt;platform>**（BR-CALC-03 默认 off；打开前须有 BR-CALC-03 验证证据，且该平台 08b 首个月结对账已通过（见下方「首个月结批次」），见 规划/05 S2 门槛）：

| 场景 | 结算批次 | 订单 display_status 与预计结算月份 | 入账说明文案 |
|---|---|---|---|
| off，ESTIMATED（DEPOSIT_PAID / PAID） | 不涉及 | DEPOSIT_PAID / PAID，expected_credit_period=null | 商品详情与订单页不展示入账说明 |
| off，WAITING | 该平台不生成、不执行批次（含 R5a）；月结账单中该平台只保留校验结果 | CREDITING「入账核对中」，expected_credit_period=null；hold、维权中按 BR-FUND-17 先匹配 REVIEWING / RIGHTS_PENDING | 同上 |
| off，钱包 | — | 该平台 WAITING 份额仍计入 pending_credit_fen，不参与预计结算月份（BR-FUND-18） | — |
| off → on | 对当期已生成的月结账单重新校验、生成补充批次，照常人工确认后执行 | 恢复按 ⑪ 返回预计结算月份 | 恢复展示 |
| on → off（如发现 N 取数错误） | 执行中的批次在下一个子订单事务前停止，置 PARTIAL；扣回、补差、失效照常 | 同 off | 同 off |

**首个月结批次**（负责人 2026-10-01：首个账单日 11-24 早于淘宝、京东 08b 对账截止 11-27 时的先后）：某平台 CAP-\*-08 的 08b（首个月结对账，规划/09 README）通过前，该平台 credit.enabled.&lt;platform> 保持 off，账单日照常生成月结账单、该平台只保留校验结果，不生成批次（⑨）；08b 通过后打开开关，finance 可对当期账单手动发起补充批次（⑧，即上表 off → on），也可等下一个账单日随新账单入账（settle_period ≤ 账单月的订单都在范围内，不需顺延结算周期）；两种方式都照常人工确认。开关 off 期间该平台 WAITING 订单按上表显示「入账核对中」、不显示预计结算月份。拼多多、美团的 08b 截止为实测结算日 + 7 天，处理相同。例：11-24 生成 2026-10 账单时淘宝、京东 08b 都未通过 → 两平台不生成批次；11-26 淘宝 08b 通过 → 打开 credit.enabled.taobao，finance 发起 2026-10 账单淘宝补充批次并确认结算；京东 08b 到 12-24 仍未通过 → 京东继续不入账，08b 通过后按同样方式处理。本主题及其他条目中以 11-24 账单日为例的入账示例，均假定该平台 08b 已通过。

**推送**：结算批次执行完成后推送（本轮确认的批次全部 DONE，或因开关停止置 PARTIAL 时对已入账部分），每用户汇总一条「已结算」推送（B_credit=0 的订单不计入）；完成时刻落在免打扰时段（notify.quiet_hours，BR-WATCH-15，当前默认 [22:00, 08:00)）时顺延到免打扰结束后发送。模板、对象、合并与去重只在 BR-TEXT-09 维护，两处写法一致。受益人补记项（⑫）补记的金额并入该批次完成后按受益人汇总的「已结算」推送，不新增模板。

**与 BR-TEXT-04 的分工**：expected_credit_period、credit_overdue 的计算（联盟结算时间优先、推算偏移、维权 / hold / 开关期间返回 null、逾期判断）只在本条维护；BR-TEXT-04 只维护「预计 {月份} 结算」等展示文案与格式，两者不一致时以本条为准。

C-02 已由负责人改定（变更记录 §3；拍板第二批 OPS-01 再次确认）：结算前一律「预估」，结算批次核对入账后用「已结算」，用户侧文字以 BR-TEXT-01 为准；C-17（D+1 00:01 资产快照 → 00:05 入账）中的 00:05 每日入账任务随本口径取消，只保留「批次不在 00:00 至当日快照完成期间执行」与「月结账单在账单日快照完成后生成」（BR-FUND-18），随 ③⑦ 由负责人 2026-10-01 确认（拍板第二批 FUND-07）；G-16（expected_credit_date 并入维权关闭或 hold 解除时刻）随本口径改为 expected_credit_period，原算法作废；按 C-27 (d) 默认处理（held 受益人单独入账），待财务确认；C-27 (e)（credit_requires_settle 守卫）在本口径下自然满足，见上方边界。

2026-10-01 拍板第二批：FUND-01 选「按 9-30 拍板：跟联盟月结，账单日出账、人工确认后批量入账」，FUND-07 选 9-30 稿默认（见上表）；FUND-16（逐单入账时按满 15×24 小时、维权不顺延）只在保留逐单入账时适用，FUND-01 已选月结，不生效（6.3 第 3、4 条）；FUND-17（受益人冻结满 30 天仍无结论告警、人工决定）落在 BR-CALC-13，本条 ⑩ 与 R5a 的 held 处理不变。
- 同步落点（2026-09-30 月结口径，逐项核对过引用处）：规划/00 §3.2 D11 行「逐单入账」改为月结批次口径，§4 范围裁决表「资金」行、§6 主要变化表「月结账单、会员月账单、分平台对账单 MVP」行的「逐单入账」同改；规划/01 §3 资金流图「确认收货满 wait_days → 逐单入账」、§5 J1 步骤 1「确认收货满 {wait_days} 天后入账」与步骤 6「到期入账」、E04 F-PROD-05 入账说明、E10 F-SET-02「逐单入账（D11）」与 F-SET-05 验收「T+15 入账」；规划/02 §1 原则 8「满 15 天」、§5.2 时序「资产快照 → settle.credit 入账」与「取 WAITING 且到期」、§8.5 R3 行「入账任务之后」；规划/03 §7.4 order_status 卡片 expected_credit_date；规划/04 §1 术语表「入账」行、§3.2 orders（删 credit_due_at、wait_days_snapshot，expected_credit_date 改为 expected_credit_period，增 settle_period）与新增结算账单、批次表、差错单类型，§4 状态机表 4.1 行入账守卫（R5 触发），§6.4 GET /v1/orders/{order_id} 与 §8.3 order_status 卡片 expected_credit_date → expected_credit_period，§10.1 服务端配置键删 settle.wait_days.&lt;platform>、增本条配置；规划/05 §3.3 B2-04「入账任务（快照 → 入账 → 日终校验）」、§4.1 入账闭环说明（「W2 末下单，最早 W5 末入账」按月结口径重估）；规划/06「08 待决策与分歧」表 B12 行（settle.wait_days.&lt;platform>）、Q-B2「入账等待期」行；规划/07 §1 资金行与 §2「结算设置」行的「逐单入账」；规划/09 CAP-TB-08、CAP-JD-08、CAP-PDD-08、CAP-MT-08 补结算账单获取方式、出账日、周期归属口径；规划/10 AC-S2-01-TB「收货满 15 天自动入账」、AC-S2-02、AC-S2-03（credit_due_at）、AC-S2-32 压缩时钟流程、G-16 行；规划/08：BR-TEXT-04 需改（预计入账表达、删 wait_days_snapshot 与「确认收货满 {wait_days} 天后入账」）、BR-TEXT-01（结算前统一为「预估」，已收货待结算时附「其中已收货」子行，已按负责人决定改写）、BR-TEXT-02 映射表 PAID / WAITING / WAITING_SETTLE / CREDITING 行与时间线、BR-TEXT-09 例 2「00:05 入账任务」、BR-TEXT-11 纯日期字段示例、12_TEXT 未决问题第 2、3 条；BR-CALC-14「入账任务执行 R5（CREDIT_DUE）」、BR-CALC-15 与 BR-CALC-25 的 credit_requires_settle 入账守卫（改为自然满足）、BR-CALC-23 (a) 适用范围（只剩批次入账后的结算额变更）、05_CALC 中 R5a「下一次 00:05 入账任务」与「收货 +15 天时尚未结算」例；BR-AI-06 与 08_AI 数据来源表 expected_credit_date；README §0.3 默认假设 × 平台能力表 BR-TEXT-04 行、§1.2「预计 MM-DD 入账」行；13 命名对照 D11 行、WAITING 行「settle.wait_days」、asset_snapshots 行「先于 00:05 入账」；14 §14.2 BR-FUND-04 行、§14.3 C-17 行、客服问答第 10 条。2026-09-30 补充（变更记录 §10：账单来自联盟数据、预计结算月份、推送时点；已 grep 核对）：规划/00 §3.2 D11 行「联盟出账单后后台逐单核对」改为「月结账单日按联盟结算数据自动生成月结账单，人工确认后立即或定时结算」；规划/01 E10 F-SET-02「逐单入账（D11）」改为月结账单口径；规划/04 §3.2 orders 增 union_settled_at，原「结算账单登记（statement_id）」改为月结账单（bill_id=账单月，状态由批次派生），结算批次增 settle_mode、scheduled_at，§6.4 GET /v1/orders/{order_id} 与 §8.3 order_status 卡片 expected_credit_period 含义改为预计结算月份，§10.1 配置键增 settle.bill_day、settle.period_offset_months.&lt;platform>，删 settle.statement_day.&lt;platform>，settle.statement_source.&lt;platform> 默认改 api；规划/07 §2「结算设置（日结门槛、确认收货天数、月结账单日、重复月结）」行对照结果改为月结账单日 settle.bill_day + 立即 / 定时结算；规划/09 CAP-TB-08、CAP-JD-08、CAP-PDD-08、CAP-MT-08 补「联盟结算佣金与结算时间字段能否经订单接口取得、结算时间的语义（是否即联盟向推广者结算的时间）」；规划/10 AC-S2-01-TB / -JD / -PDD、AC-S2-32 补账单日自动生成、立即 / 定时结算、推送免打扰顺延，AC-S2-02 改为预计结算月份（有 / 无联盟结算时间两种）；08 README §0.3「默认假设 × 平台能力」表 BR-TEXT-04 行（依赖部分补联盟结算时间字段）、§1.2「预计 MM-DD 入账」行改为「预计 {月份} 结算」；08 13 命名对照 D11 行；08 14 §14.1 BR-FUND-04 行、§14.2 BR-TEXT-04、BR-TEXT-09 行、§14.4 第 10 项；08 15 BR-TEXT-04 行（依赖平台能力补联盟结算时间字段）；本主题 BR-FUND-09 R1 调度与月结账单生成合并、BR-FUND-18 钱包预计结算月份字段；12_TEXT BR-TEXT-01、02、03、04、09、18 已随本次同步改写（已同步 2026-09-30）

#### BR-FUND-05 细则 · 入账金额与入账凭证

- 状态：已确认（负责人 2026-10-03 资金规则对齐（兼财务口径）：入账基数取法已由拍板第二批 FUND-01 月结口径与 docs/changes/20261001-平台预留比例.md 确定，由联盟结算佣金按 BR-CALC-02 换算；凭证粒度（每个受益人一张、平台一张，被剥夺的受益人每人一张平台 FORFEIT 凭证）按决-04 确认默认。原为待决策：入账基数取法与凭证粒度属金额口径，决策人为财务；更早为默认假设）
- 默认值：每受益人一张凭证 + 平台一张凭证，同一事务提交，uniq_key 以 order_key 开头；理由：与 规划/02 §8.1 的 uniq_key（按受益人）一致，按受益人幂等且流水只涉及一个用户；带平台前缀避免三家子订单号撞号时后到订单被当作已入账跳过。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - 规划/02 §8.3：「订单入账为一张凭证：借 UNION_RECEIVABLE 1234 / 贷 USER_SELF:buyer 617、USER_PROMO:parent 123、COMMISSION_REVENUE 494」
  - 规划/02 §8.1：「uniq_key 以 sub_order_id 开头（不含平台）」
  - PRD v2.1 §11.1：「唯一业务键 (entry_type, biz_id)，如 (CREDIT_REBATE, sub_order_id)」
  - PRD修订_后端功能规划 §2.7：「入账金额取入账时刻订单上最新的联盟口径预估佣金（未考虑已先行结算的情况）」
  - 本条 2026-10-01 前写法：「入账基数 B_credit 必须 = orders.settle_commission_fen（若非空），否则 = 入账时刻 orders.est_commission_fen 最新值」（按 2026-10-01 平台预留比例决定改为由 N 经 BR-CALC-02 换算，docs/changes/20261001-平台预留比例.md）
  - 本条分录模板 2026-10-01 写法：「自购 → USER_SELF:{uid}.available；分享者、直推、间推 → USER_PROMO:{uid}.available」（单一余额，拍板第二批 §8 ADD-06）
  - 本条正文 2026-10-03 前写法：「N 取 orders.settle_commission_fen（若非空，取值规则见 BR-FUND-09），否则取入账时刻 orders.est_commission_fen 最新值」（月结口径下入账时必有结算佣金，「否则取预估」删去）（2026-10-03 资金规则对齐（负责人批准），方案 §2，同-02）
  - 本条正文 2026-10-03 前写法：「平台留存 >0 写 1 张凭证」与细则「平台留存另含预留部分」（平台凭证含预留的写法从细则提到正文，并补同事务写 booked_n_fen）（2026-10-03 资金规则对齐（负责人批准），方案 §1，同-01）
  - 本条正文 2026-10-03 前写法：「用户账户按 account_id 升序 SELECT … FOR UPDATE。」（只有余额行，没有 users 行与锁后重读；统一改由 BR-FUND-16 细则「加锁流程」规定）（2026-10-03 资金规则对齐（负责人批准），方案 §4，同-06）
  - 本条正文 2026-10-03 前写法：「B_credit=0 时不写凭证，只迁移状态。」（写于没有平台预留的时候；预留比例不为 0 时会出现基数为 0 而联盟佣金与预留大于 0，照字面预留不进账，联盟回款时 UNION_RECEIVABLE 倒挂）（2026-10-03 资金规则对齐（负责人批准），方案 §7.3，同-23）
  - 本条正文 2026-10-03 前写法：「平台留存 = B_credit − Σ受益人份额，尾差归平台」「每个份额 >0 的受益人写 1 张凭证」（没有写被剥夺、暂缓的受益人怎么记；随 BR-CALC-13 的 FORFEIT 凭证与 BR-FUND-04 ⑫ 补记项写明）（2026-10-03 资金规则对齐（负责人批准），方案 §6.1、§6.6，同-08、同-13）
  - 本条状态 2026-10-03 前为「待决策（…入账基数取法与凭证粒度属金额口径，决策人为财务…）」（入账基数取法已定、凭证粒度经决-04 确认默认，改为已确认）（2026-10-03 资金规则对齐（负责人批准），方案 §6.5，同-12、决-04）
- 来源：规划/04 §4.1 O6/O7；规划/02 §8.1、§8.3；规划/01 E10 F-SET-02；PRD修订_后端功能规划 §2.7、§2.8 记账规则 2；docs/changes/20261001-平台预留比例.md；docs/changes/20261001-拍板第二批.md §8 ADD-06；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

**分录模板**（借为正、贷为负，见 BR-FUND-16）：

| 角色 role | ledger_type | 借 | 贷 |
|---|---|---|---|
| 自购 self | REBATE_CREDIT | UNION_RECEIVABLE:{platform} | USER_BALANCE:{uid}.available |
| 分享者 share | SHARE_CREDIT | UNION_RECEIVABLE:{platform} | USER_BALANCE:{uid}.available |
| 直推上级 parent_direct | REFERRAL_CREDIT（sub_type=DIRECT） | UNION_RECEIVABLE:{platform} | USER_BALANCE:{uid}.available |
| 间推上级 parent_indirect（role=indirect，仅 indirect_enabled=true 的版本） | REFERRAL_CREDIT（sub_type=INDIRECT） | UNION_RECEIVABLE:{platform} | USER_BALANCE:{uid}.available |
| 平台 | —（不对用户展示） | UNION_RECEIVABLE:{platform} | COMMISSION_REVENUE |

**booked_base_fen**：该子订单最近一次记账所用基数；入账、扣回（BR-FUND-08）、补差（BR-FUND-09）、恢复（BR-FUND-22）同事务更新，供 BR-FUND-19 ⑤ 校验。**booked_n_fen**：同一次记账所依据的联盟佣金（正数部分），与 booked_base_fen 成对更新，供 BR-FUND-19 ⑤ 校验（2026-10-03 资金规则对齐）。

**例**：order_key=taobao:1234567，B_credit=1234，自购 5000bp、直推 1000bp → 凭证 1（`taobao:1234567:42:self:CREDIT`）：借 UNION_RECEIVABLE 617 / 贷 USER_BALANCE:42 617；凭证 2：借 UNION_RECEIVABLE 123 / 贷 USER_BALANCE:parent 123；凭证 3（`taobao:1234567:PLATFORM:CREDIT`）：借 UNION_RECEIVABLE 494 / 贷 COMMISSION_REVENUE 494；booked_base_fen=1234。重放同一批次：3 个 uniq_key 均已存在，余额不变。京东子订单号同为 1234567 时 order_key=jd:1234567，不冲突。

**例（先结算后入账）**：收货后联盟已结算 1100 分，入账时 B_credit=1100 → 550/110/440，此后 R1 差额为 0。

**平台预留**：各例按种子版本（各平台 reserve_bp=0，B_credit = N）。reserve_bp 非 0 时 B_credit 先按 BR-CALC-02 扣预留再拆分，如淘宝预留 1500bp、N=1100 → B_credit=floor(1100×8500/10000)=935、reserve_fen=165；平台凭证金额 = 平台留存 + 165（正文）；booked_base_fen=935、booked_n_fen=1100。

**例（基数为 0 仍记预留，2026-10-03 资金规则对齐 E-34）**：某平台预留比例 10000，联盟结算佣金 1000 → B_credit=0、reserve_fen=1000：受益人份额都为 0，不写用户凭证；平台凭证 1000 照写（借 UNION_RECEIVABLE 1000 / 贷 COMMISSION_REVENUE 1000）；订单 CREDITED，booked_base_fen=0、booked_n_fen=1000，用户侧显示「本单无返利」（BR-FUND-17 第 3 行）。预留 2000、联盟佣金 1 → floor(1×8000/10000)=0，平台凭证 1。

**异常**：受益人已封禁/注销时份额归平台（见 BR-CALC）；任一凭证借贷不平 → 整个事务回滚、告警，订单保持 WAITING。

#### BR-FUND-06 细则 · 维权中与订单暂停

- 状态：待验证
- 默认值：淘宝按维权退款接口的处理中状态设置 rights_pending；京东、拼多多无处理中信号，只做事后扣回。部分成功而佣金未更新时继续阻止入账（WAIT_COMMISSION）。
- 决策人：负责人
- 依赖平台能力：淘宝维权退款接口是否返回「维权处理中」及结束状态、是否返回应扣佣金或新佣金；京东、拼多多是否存在任何售后进行中信号
- 取代：
  - PRD v2.1 §9.3：「RECEIVED 维权发起→RIGHTS_PROTECTING 暂停入账（独立状态）」
  - 本条正文 2026-10-03 前写法：「风控引擎可以系统身份（actor=system:risk）自动 hold」（未列 BR-FUND-02 映射表之外状态码的自动 hold）（2026-10-03 资金规则对齐（负责人批准），方案 §6.8，决-05）
- 来源：规划/04 §4.1 O6 守卫「无维权」；规划/02 §7.1；PRD修订_后端功能规划 §2.5、§2.7 订单 hold、§3.2；PRD v2.1 §9.3、§9.5；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**用户展示**：rights_pending=true →「售后处理中，入账暂停」；hold=true →「入账核对中」，不展示内部原因（文字以 BR-TEXT-03 与 README §1.2 为准）。

**例**：received_at=10-01 14:30，settle_period=2026-10；11-18 淘宝维权处理中 → 11-24 生成的 2026-10 月结账单校验记暂缓、不入账；12-02 维权失败关闭 → 进入补充批次，人工确认后入账，入账额不变（BR-FUND-04 例 3）。

**例（部分成功、佣金未更新）**：WAITING 订单 10-15 淘宝维权部分成功，接口只给退款金额、无应扣佣金，联盟佣金未变 → order_rights=WAIT_COMMISSION，继续跳过入账；10-18 联盟回传新佣金 → R7 重算预估并关闭记录，随后续结算批次入账。

**异常**：order_rights 处于 PROCESSING 或 WAIT_COMMISSION，且 now − created_at ≥ 60×24 小时 → 告警进人工；手工导入的维权/处罚清单（后台 rights-imports）与接口同等处理，按 (platform, sub_order_id, 平台维权单号) 去重。

C-02 已由负责人决定（拍板第一批 §3；拍板第二批 OPS-01：结算前叫预估、结算后叫已结算），「入账」只作动作词（BR-TEXT-01），本条展示文字以 BR-TEXT-03 为准。

#### BR-FUND-07 细则 · 入账前失效与部分退款

- 状态：默认假设
- 默认值：业务口径沿用 规划/04 O4/O5（已确认），状态字段表述依赖 BR-FUND-01 拍板；B 由 >0 变 0 作废与 reason_code=COMMISSION_ZERO 为本条新增默认值。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 本条正文 2026-10-03 前写法：「或 B_est 由 >0 更新为 0 而平台未回传失效」（未说 B_est 用哪个佣金字段；按 BR-CALC-02 限定为有效联盟佣金换算出的基数，结算佣金已到之后预估单独变 0 不作废）（2026-10-03 资金规则对齐（负责人批准），方案 §2，同-02）
- 来源：规划/04 §1 扣回、§4.1 O4/O5；规划/01 E10 F-SET-04；PRD修订_后端功能规划 §2.7 失效与扣回、§3.2；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

**例**：10-01 付款预估自购 617 分 → 10-03 买家退款，淘宝回传失效 → (INVALID, VOID)，reason_code=REFUND；钱包预估减少 617，余额与流水不变；推送「订单已失效：订单已退款」。

**例（部分）**：WAITING 中退 1/2 → B_est 1234→617，份额 617→308，settle_period 不变。

**例（佣金归零）**：拼多多订单 WAITING、尚无结算佣金，联盟回传佣金 0、状态仍为已收货 → VOID，reason_code=COMMISSION_ZERO，文案「订单已失效：平台取消了本单佣金」。

**例（结算佣金已到后只变预估，2026-10-03 资金规则对齐 E-07 第二问）**：订单 WAITING，settle_commission_fen=1000 已到、月结批次尚未执行；联盟只把预估佣金改为 0，没有退款、维权或处罚 → 只存档 est_commission_fen，不作废、不迁移，照常随月结批次按结算佣金入账。

**边界**：京东实际佣金由 >0 变 0：规划/09 验证前 reason_code=COMMISSION_ZERO；验证确认其表示维权后改取 RIGHTS。

**边界（预售定金）**：淘宝预售单 10-01 付定金入库 (DEPOSIT_PAID, ESTIMATED)，联盟回传佣金 120 分；10-05 回传佣金 0 → 不作废，仍显示「已付定金」（BR-FUND-17 第 6 行）；10-11 付尾款 (PAID) 时佣金 0 → 按首次 B_est=0 显示「本单无返利」，不作废；此后 B_est 由 0 变 >0 按 R7 重算预估。付尾款时佣金 900、之后变 0 → 按本条 VOID，reason_code=COMMISSION_ZERO。

**边界（佣金为空）**：首次入库时联盟未给佣金 → est_commission_fen=null（「未知」，不视为 0），ESTIMATED 显示「已付款，返利待确认」、不展示金额、不显示「本单无返利」；之后收到数值按 R7 重算。已有数值后某次回传佣金缺失 → 保留上次数值，状态不变、不作废。

#### BR-FUND-08 细则 · 入账后扣回

- 状态：已确认（负责人 2026-10-03 资金规则对齐（兼财务口径）。已确认的部分：扣回金额按 BR-CALC-09 整体重算求净差（拍板第二批 FUND-15），净额含恢复与改派凭证（方案 §7.6）；注销后扣回记平台坏账，限份额入过其账户（FUND-09、方案 §7.2）；联盟给的金额先按 BR-CALC-02 换算再用（方案 §1）；决-04 确认默认：凭证粒度（每受益人一张、平台一张）与入账后部分退款写 CLAWBACK（C-16）；决-03 选 A：联盟没给新佣金也没给应扣佣金时挂起（③）；决-10 选 A：应扣佣金从 booked_n_fen 里减，扣回之后早于扣回的结算记录不再生成正差候选（BR-FUND-09 ②）。sub_type 与订单原因码的映射是代理按方案 §6.4 补的编码映射。京东佣金归零口径、淘宝维权接口字段仍待 规划/09 验证（15 §15.2）。原为待决策：扣回金额口径与流水类型属金额口径，决策人为财务；更早为默认假设）
- 默认值：入账后的部分退款写 CLAWBACK（sub_type=PART_REFUND），不写负向 SETTLE_ADJUST；佣金调整不写 CLAWBACK：联盟结算额的变化按 BR-FUND-09 / R10（负差即时写负向 SETTLE_ADJUST、正差进候选），只有预估变化的按 R9b 只存档并出差错单（2026-10-03 资金规则对齐决-01 A，取代 C-27 (g) 的 R9b 负差即时记账）。理由：按原因区分流水类型——逆向交易一律 CLAWBACK，SETTLE_ADJUST 只表示联盟结算额差异，R1 差额分类和用户流水都更清楚。
- 决策人：财务
- 依赖平台能力：京东实际佣金归零能否与部分维权区分（BR-FUND-02、规划/09）；淘宝维权接口是否返回应扣佣金或新佣金
- 取代：
  - 规划/04 §4.1 O10：「CREDITED 收到 PART_REFUND → 写负向 SETTLE_ADJUST」
  - 规划/07 §2 08 订单管理：「部分退款写调整分录」
  - PRD修订_后端功能规划 §2.7：「idem_key={sub_order_id}:{user_id}:{role}:CLAWBACK:{seq}（seq 来源未定义）」
  - 规划/02 §8.3：「扣回为一张凭证同时借 USER_SELF、USER_PROMO、COMMISSION_REVENUE」
  - 本条正文 2026-10-03 前写法：「B 由 >0 变 0」（逆向事件列举；改为有效基数由 >0 变 0）（2026-10-03 资金规则对齐（负责人批准），方案 §2，同-02）
  - 本条正文与默认值 2026-10-03 前写法：「佣金变化（R9b：价保、比价降佣、联盟佣金调整）不属于逆向事件，不写 CLAWBACK，按 BR-FUND-01 R9b 处理（负差即时写负向 SETTLE_ADJUST，正差进 BR-FUND-09 候选）。」「佣金调整（R9b）不写 CLAWBACK，负差按 R9b 即时写负向 SETTLE_ADJUST、正差进 BR-FUND-09 候选（C-27 (g)，负责人 2026-10-01 确认，拍板第二批 FUND-11）」（随 R9b 改为只存档，结算额变化归 R10）（2026-10-03 资金规则对齐（负责人批准），方案 §2，决-01）
  - 本条正文 2026-10-03 前写法：「新基数 B_new 按以下顺序取第一个可用值：①本次事件自带的联盟新佣金（订单同步回传的 est_commission_fen 或 settle_commission_fen，取本次更新的那个）；②order_rights 记录的应扣佣金，B_new = booked_base_fen − 应扣佣金；③都没有 → 不写扣回，order_rights 置 WAIT_COMMISSION，订单进待处理表并告警。整单失效时 B_new=0。」（把联盟佣金 N 当分佣基数 B 用、拿 B 减 N；预留比例不为 0 时少扣或错摊）（2026-10-03 资金规则对齐（负责人批准），方案 §1、§2，同-01、同-02）
  - 本条正文 2026-10-03 前写法：「平台留存差额 = 平台已入账净额 − 按 B_new 的新留存」「本次全部凭证对 UNION_RECEIVABLE 的净影响必须 = −(booked_base_fen − B_new)，同事务 booked_base_fen=B_new」（未含预留，预留不为 0 时两句互相矛盾）（2026-10-03 资金规则对齐（负责人批准），方案 §1，同-01）
  - 本条细则「不变量」与影响面 2026-10-03 前写法：「每 (子订单,受益人,角色) Σ CLAWBACK ≤ CREDIT + Σ 正向 SETTLE_ADJUST。」「属性测试：扣回 ≤ 已入账」（恢复后再扣回、改派后扣回时不成立，改为净额不为负）（2026-10-03 资金规则对齐（负责人批准），方案 §3，同-05）
  - 本条正文 2026-10-03 前写法：「受益人扣回金额 = 该受益人在该子订单上的已入账净额（CREDIT + Σ SETTLE_ADJUST − Σ 已有 CLAWBACK）− 按 B_new 和快照重拆的新应得，≤0 不写。」（净额不含恢复 RESTORE 与改派凭证：恢复或申诉补发之后再扣回，恢复的钱扣不回来，结算下调时还会再补一次；平台已入账净额未写明含没收与申诉补发）（2026-10-03 资金规则对齐（负责人批准），方案 §7.6，同-26）
  - 本条正文 2026-10-03 前写法：「受益人已进入注销 processing 或已注销（墓碑用户，BR-ID-28）时，该受益人的扣回额不写其账户，改借 BAD_DEBT / 贷 UNION_RECEIVABLE」（没有限定份额入过其账户；BR-ID-28 细则末例据此把入账前已没收、净额为 0 的份额也记了坏账）（2026-10-03 资金规则对齐（负责人批准），方案 §7.2，同-22）
  - 本条细则「分录」2026-10-03 前只列「sub_type ∈ FULL / PART_REFUND / RIGHTS / PUNISH」（各逆向事件记哪个 sub_type、部分维权记 RIGHTS 还是 PART_REFUND、CLAWED_BACK 写不写订单原因码都没有写）（2026-10-03 资金规则对齐（负责人批准），方案 §6.4，同-11）
  - 本条状态 2026-10-03 前为「待决策（…扣回金额口径与流水类型属金额口径，决策人为财务…）」，正文 ③ 原写「③都没有 → 不写扣回，order_rights 置 WAIT_COMMISSION，订单进待处理表并告警。」（已定与待定的部分没有分开；凭证粒度、C-16、③ 挂起与 R-21 的基准经决-03、决-04、决-10 定下，改为已确认）（2026-10-03 资金规则对齐（负责人批准），方案 §6.5、§7.1，同-12、决-03、决-04、决-10）
  - 本条正文 2026-10-03 写回时只写「同一事务作废该子订单未批准的正差候选（BR-FUND-09 ②，决-10 A）」（转 CLAWED_BACK 时未完成的待补记义务不作废，之后 R13 恢复产生的待补记额会沿用扣回前的义务身份，扣回前生成的补记项在恢复后还能执行）（2026-10-03 资金规则对齐评审后修改，同步修正，方案 §13.6 第 1 条）
  - 本条正文 2026-10-03 写回时写法：「新基数为 0 按本条 R8」（基数为 0 仍记预留的订单，之后结算佣金变化时新旧基数都为 0，由迁移 R10 只调平台金额，见 BR-FUND-09）（2026-10-03 资金规则对齐评审后修改，同步修正，方案 §13.6 第 2 条）
- 来源：规划/04 §1、§4.1 O9/O10；规划/01 E10 F-SET-04；规划/07 §2；PRD修订_后端功能规划 §2.7、§10.1 AC-MONEY-004；PRD v2.1 §11.4；BR-ID-28；docs/changes/20261001-拍板第二批.md FUND-09；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

**分录**：借 USER_BALANCE:{uid}.available / 贷 UNION_RECEIVABLE:{platform}；ledger_type=CLAWBACK，sub_type ∈ FULL / PART_REFUND / RIGHTS / PUNISH。

**sub_type 与订单原因码**（2026-10-03 资金规则对齐方案 §6.4；编码映射，不改金额、幂等键与恢复资格）：

| 逆向事件 | 迁移 | CLAWBACK sub_type | 订单原因码 |
| --- | --- | --- | --- |
| 处罚（处罚接口，或映射为处罚的平台码，BR-FUND-02） | R8 | PUNISH | PUNISH |
| 维权成功，全额 | R8 | RIGHTS | RIGHTS |
| 维权成功，部分 | R9 | RIGHTS | 不改；差额原因 PART_REFUND |
| 平台失效、结算后失效或整单退款 | R8 | FULL | REFUND |
| 黑名单人工复核确认 | R8 | FULL | BLACKLIST |
| 有效基数由正变零，没有失效、维权、处罚 | R8 | FULL | COMMISSION_ZERO |
| 部分退款（退款数量增加，没有维权记录） | R9 | PART_REFUND | 不改；差额原因 PART_REFUND |

取法：先按来源（处罚取 PUNISH，维权记录取 RIGHTS）；其余新基数为 0 取 FULL，否则取 PART_REFUND。迁移 R8 在同一事务写订单原因码（reason_code），取值集合同 BR-FUND-07。恢复资格（BR-FUND-22）只看订单原因码，不看 sub_type；用户流水名称按 sub_type 取（BR-TEXT-19）。例（E-19）：P0 部分维权、应扣佣金 250 → 本人 −100、直推 −20、平台 −130，sub_type=RIGHTS，订单原因码不改；记 RIGHTS 还是 PART_REFUND，金额、幂等键与净额都相同，只差流水名称与对账分类。

**例（后端功能规划 §10.1 AC-MONEY-004；规划/05 编号待分配）**：自购入账 1000 → 提现 1000 已打款（available=0）→ 维权失效，CLAWBACK 1000 → available=−1000；申请提现返回 30302；另一新订单入账 600 → available=−400。

**例（部分）**：本例预留比例为 0（N = B）。已入账 617/123/494（booked=1234），退款 1/2，联盟新 B=617（来源①，键 C{commission_version}）→ 新应得 308/61/248 → CLAWBACK 309、62，平台凭证 246；UNION_RECEIVABLE 净影响 −617；状态保持 CREDITED，booked=617。

**例（舍入使平台留存增加）**：本例预留比例为 0。B 10→9，两名受益人各 3300bp：旧份额 3/3、平台 4；新份额 2/2、平台 5 → 受益人各扣 1；平台差额 −1 → 借 UNION_RECEIVABLE 1 / 贷 COMMISSION_REVENUE 1；UNION_RECEIVABLE 净影响 −1+(−1)+1 = −1 = −(10−9)。

**例（预留比例不为 0，2026-10-03 资金规则对齐 E-01、E-03）**：淘宝 reserve_bp=2000，本人 5000、直推 1000。入账时联盟结算佣金 1000 → B=800、预留 200，本人 400、直推 80、平台 320+200=520，booked_base_fen=800、booked_n_fen=1000。① 部分退款，联盟回传新结算佣金 600 → B_new=floor(600×8000/10000)=480、预留 120 → 本人 240（扣 160）、直推 48（扣 32）、平台 192+120=312（冲回 208）；UNION_RECEIVABLE 净影响 −400 = −(1000−600)；booked_base_fen=480、booked_n_fen=600。② 若改为维权记录只给出应扣佣金 250、没有新佣金 → N_new=1000−250=750，B_new=600、预留 150 → 本人 300（扣 100）、直推 60（扣 20）、平台 240+150=390（冲回 130）；净影响 −250。

**例（恢复过的钱计入净额，2026-10-03 资金规则对齐 X-01、E-11）**：本例预留比例为 0，本人 5000、没有上级。B=1000，U1 应得 500：首次入账时 U1 封禁，500 归平台（平台凭证 1000 = 留存 500 + 没收 500）；之后封禁申诉撤销，按 BR-FUND-22 ③ 补发（借 COMMISSION_REVENUE 500 / 贷 U1 余额 500）；联盟随后把结算佣金改为 0 → 按 R8：U1 已入账净额 500（含补发）扣 500；平台已入账净额 1000 − 500 = 500，冲回 500；UNION_RECEIVABLE 净额 0，订单 CLAWED_BACK。净额若不计补发，U1 不扣、留着 500，而 UNION_RECEIVABLE 停在 500。另一单（P0，预留 2000）：入账 → 全额扣回 → R13 恢复 → 再次全额扣回，第二次按计入恢复的净额扣本人 400、直推 80，平台冲回 520，UNION_RECEIVABLE 净额 0。

**幂等**：同一事件重放 → uniq_key 已存在，跳过；不同事件但重算净额差为 0 → 不写。

**不变量**：每 (子订单, 受益人, 角色) 的净额不为负（净额口径同 BR-FUND-19 ④）。

**注销后扣回（拍板第二批 FUND-09）**：用户 42 的订单 11-24 随月结批次入账自购 617；12-01 用户进入注销 processing（申请时余额 ≥ 0，BR-ID-27），余额按 BR-FUND-24 以 ACCOUNT_CLOSED 转平台收入；12-05 该单全额维权成功 → 受益人扣回凭证 `taobao:1234567:42:self:CLAWBACK:R{id}` 写 借 BAD_DEBT 617 / 贷 UNION_RECEIVABLE 617，不写墓碑用户账户，余额不变负；平台留存差额照常。

C-16 已由负责人 2026-10-03 确认默认（资金规则对齐决-04）：入账后部分退款写 CLAWBACK sub_type=PART_REFUND，本条原写法不变；BR-TEXT-03 例 3 与第 13 节映射表随之修订。

#### BR-FUND-09 细则 · 月结补差

- 状态：已确认（负责人 2026-10-01，依据 docs/changes/20261001-拍板第二批.md FUND-11：少了立即扣，多了人工批准再补；正差批准由 §8 ADD-05 改为超管或有权限账号一人 step-up 完成；原为待决策，补差审批方式与 BR-CALC-23 存在分歧 C-07）
- 默认值：负差（结算额低于已入账基数）在结算额写入的同一事务内即时记账；正差候选须人工 step-up 批准后才记账（一人可完成，ADD-05）；以结算明细为准。理由：负差延迟期间用户可能提走多入的钱，形成负余额与坏账；正差延迟不产生资损，而联盟结算数据解析或口径错误会批量给用户加钱，人工闸门可防批量资损。R1 首批稳定后可由财务决定改为自动批准小额正差。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - 规划/01 E10 F-SET-05：「月结不产生首次入账（未入账订单除外）」
  - 规划/04 §4.1 O8：「CREDITED 收到 PLATFORM_SETTLED 转 SETTLED，结算额≠已入账额时直接写 SETTLE_ADJUST（无审批）」
  - PRD修订_后端功能规划 §2.7：「按 (batch_id, sub_order_id, user_id, role) 幂等（重建批次会重复补差）」
  - PRD v2.1 §9.3：「RECEIVED 平台结算→PLATFORM_SETTLED，结算佣金与预估差异写 SETTLE_ADJUST（入账前补差）」
  - 本条 2026-09-30 写法：「调度任务每日 02:00 检查各平台上一结算周期的明细是否已全部拉取，拉全后的次日运行 R1」（随 BR-FUND-04 月结账单生成合并，2026-10-01）
  - 本条 2026-10-01 写法：「须由 finance 发起、另一名 finance 或 super（≠发起人）step-up 复核后才写 SETTLE_ADJUST 凭证」及默认值「与 规划/02 §8.5「调账需第二人复核」一致」（拍板第二批 §8 ADD-05 改为一人 step-up 批准）
  - 本条正文 2026-10-03 前写法：「逐受益人计算 diff = 按当前 settle_commission_fen 与快照重拆的应得份额 − 已入账净额（平台留存同法），按 settle_commission_fen 与 booked_base_fen 的大小分两路：①负差（settle_commission_fen &lt; booked_base_fen）…②正差（settle_commission_fen > booked_base_fen）…写凭证时必须按 orders.settle_commission_fen 当前值与当前净额重算」「同事务 booked_base_fen=settle_commission_fen」；细则边界「settle_commission_fen = booked_base_fen 时不补差」（拿联盟佣金 N 与扣过预留的基数 B 比大小、把 N 写进 B 的字段；预留比例不为 0 时每单都会被判成正差）（2026-10-03 资金规则对齐（负责人批准），方案 §1，同-01）
  - 本条正文与细则 2026-10-03 前写法：「价保、比价降佣等佣金下调（结算额写入前的 est_commission_fen 变化）不等月结，按 BR-FUND-01 R9b 即时记账。」「价保、比价降佣形成的负差不经本条月结，由 BR-FUND-01 R9b 在订单同步事务内即时写（键 `ADJ:{sub_type}:v{commission_version}`，与本条 `ADJ:{seq}` 不冲突）；正差仍进本条候选。」（R9b 改为只存档并出差错单）（2026-10-03 资金规则对齐（负责人批准），方案 §2，决-01）
  - 本条正文 2026-10-03 前写法：「逐受益人计算 diff = 按当前 settle_commission_fen 与快照重拆的应得份额 − 已入账净额（平台留存同法），按 settle_commission_fen 与 booked_base_fen 的大小分两路：①负差（settle_commission_fen &lt; booked_base_fen）：在写入该 settle_commission_fen 的同一事务内（订单同步回传结算额，或结算明细入库）立即写 SETTLE_ADJUST 凭证（diff≠0 才写），不等审批；」（没有引用 BR-CALC-09 的受益人状态规则：封禁受益人的正差、注销受益人的负差去向未写；「已入账净额」未写明含恢复与改派凭证；分路按整单还是按各受益人差额的方向未写，与 BR-CALC-23 (a) 的逐受益人写法不一致）（2026-10-03 资金规则对齐（负责人批准），方案 §6.2、§7.6、§7.7，同-09、同-26、同-27）
  - 本条正文 ② 2026-10-03 前写法：「写凭证时必须按 orders.settle_commission_fen 当前值与当前净额重算：diff=0 不写；候选行 seq ≠ 该订单当前 seq 时该行作废，不写；」（没有考虑按应扣佣金扣回之后联盟结算记录还停在旧值的情形，下一次比对会把刚扣的钱生成正差候选补回去；负责人选决-10 A）（2026-10-03 资金规则对齐（负责人批准），方案 §7.1，决-10）
  - 本条正文 ③ 与细则「边界」2026-10-03 写回时写法：「③相等：不补差。」「B_settle（结算额按 BR-CALC-02 换算）= booked_base_fen 时不补差」；分路一句只写「按 B_settle 与 booked_base_fen 的大小分两路」（N 换算成 B 含向下取整，不是一一对应：基数相等而联盟佣金不同时平台的预留已变，却既不调平台金额、也不更新 booked_n_fen，日终用旧 booked_n_fen 校验照样通过；预留 5000 时结算佣金由 1001 改为 1000，基数仍为 500，平台少冲回 1 分；基数为 0 仍记预留的订单结算佣金由 1000 改为 600，留下 400 分虚增的应收联盟）（2026-10-03 资金规则对齐评审后修改，同步修正，方案 §13.6 第 2 条）
- 来源：规划/00 §3.2 D11；规划/01 E10 F-SET-05；规划/04 §1、§4.1 O7/O8；规划/02 §8.5；PRD修订_后端功能规划 §2.7、§0.4 B8；PRD v2.1 §11.4、§11.7；参考_花卷云功能查漏底稿 §7；docs/changes/20261001-拍板第二批.md FUND-11、§8 ADD-05；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：4 处（计数仅作记录，落点见 README §0.6）

**分录**：正差 借 UNION_RECEIVABLE / 贷 USER_BALANCE.available；负差 借 USER_BALANCE.available / 贷 UNION_RECEIVABLE；ledger_type=SETTLE_ADJUST，sub_type 默认 SETTLE_DIFF，Adapter 能识别原因时写 PRICE_PROTECT、PRICE_COMPARE（BR-FUND-15）。价保、比价降佣反映在联盟新的结算记录上时按本条处理；结算记录未变、只有预估佣金变化的按 BR-FUND-01 R9b 只存档并出差错单，原 R9b 键 `ADJ:{sub_type}:v{commission_version}` 停用、不复用。

以下三例预留比例为 0（结算额 = 结算基数）。

**例（负差，即时）**：已入账 B=1234（617/123/494），联盟结算 B=1134 写入 → 同一事务应得 567/113/454 → 补差 −50/−10/−40，合计 −100，booked=1134，与 规划/02 §8.3 算例一致。重跑同一结算 → seq 不变、重算 diff=0，不写；只变动 1 次入账 + 1 次补差（F-SET-05 验收）。

**例（正差，批准后）**：结算 B=1300 → R1 生成候选 +33/+7/+26；财务 step-up 批准后写凭证，booked=1300；批准前余额与 booked 不变。

**例（结算修正 A→B→A）**：seq1=1134 即时补差 −50（567）；seq2=1300 生成正差候选 +83；候选获批 → 650，booked=1300；seq3=1134 → 即时补差 −83（键含 seq3，不与 seq1 冲突），最终净额 567。若 seq3 在 seq2 候选获批前到达：seq2 候选作废，1134 = booked_base_fen，不写。

**例（预留比例不为 0，2026-10-03 资金规则对齐 E-04、E-05）**：淘宝 reserve_bp=2000，本人 5000、直推 1000；入账时结算佣金 1000 → booked_base_fen=800、booked_n_fen=1000（本人 400、直推 80、平台 320+200=520）。联盟数据不变时，账单日比对 B_settle=floor(1000×8000/10000)=800 = booked_base_fen、结算佣金 1000 = booked_n_fen，不生成候选。联盟把结算佣金改为 900 → B_settle=720 &lt; 800，负差即时：本人 −40、直推 −8、平台 288+180=468（−52），合计 −100，booked_base_fen=720、booked_n_fen=900。

**例（整单分路与受益人状态，2026-10-03 资金规则对齐 X-05、E-17）**：本例预留比例为 0，本人 5000、没有上级。① 入账 B=1000：U1 500、平台 500。② U1 被封禁；结算佣金升到 1200，正差候选获批：U1 的 +100 按 BR-CALC-09 归平台，U1 净额 500、平台 700，booked_base_fen=1200。③ 结算佣金降到 1100 → 整单负差一路，同一事务：U1 新应得 = min(重拆 550, 净额 500) = 500，差额 0，不写；平台应得 1100 − 500 = 600，冲回 100；UNION_RECEIVABLE 净额 1100，不生成补差候选。若 U1 在 ③ 时是冻结（不是封禁），U1 重拆份额比净额多的 50 记为待补记额，解冻后随 BR-FUND-04 ⑫ 补记项入账，同样不进候选。注销受益人（P0：本人 400 入账后注销完成）遇结算佣金改为 900：本人 −40 不写其账户，借 BAD_DEBT 40 / 贷 UNION_RECEIVABLE 40，并计入其净额（360）；之后再改为 600 时只再记坏账 120，不重复冲已记的 40。

**例（扣回之后的旧结算记录，2026-10-03 资金规则对齐 E-32）**：P0（预留 2000）入账后维权记录给出应扣佣金 250 → N_new = 1000 − 250 = 750，扣回后本人 300、直推 60、平台 390，booked_base_fen=600、booked_n_fen=750；联盟订单上的结算佣金仍是 1000、没有新记录 → 账单日比对时这条结算记录早于扣回，不生成候选（否则会把刚扣的 100、20、130 原样补回）；联盟之后出新的结算记录 750 → 与已入账相等，不补；更高 → 正常生成候选，由批准人对着维权记录决定。扣回前已有一条结算 1200 的未批准候选 → 扣回时作废，批准接口返回已作废。

**例（基数相等而联盟佣金变化，2026-10-03 评审后修改）**：某平台预留 5000，本人 5000、直推 1000。入账时结算佣金 1001 → B=floor(1001×5000/10000)=500、预留 501：本人 250、直推 50、平台 200+501=701，合计 1001；booked_base_fen=500、booked_n_fen=1001。联盟新结算记录 1000 → B_settle 仍为 500、预留 500：受益人差额为 0，不写凭证；平台应得 700，按负差一路同一事务冲回 1（借 COMMISSION_REVENUE 1 / 贷 UNION_RECEIVABLE 1，键 `{order_key}:PLATFORM:ADJ:{seq}`）；booked_base_fen=500、booked_n_fen=1000，UNION_RECEIVABLE 1000。反过来由 1000 改为 1001 → 生成只有平台 +1 的正差候选，批准后写（借 UNION_RECEIVABLE 1 / 贷 COMMISSION_REVENUE 1）。另一单预留 10000，结算佣金 1000 入账：B=0，平台 1000（BR-FUND-05）；新结算记录 600 → B 仍为 0：按迁移 R10 同一事务冲回平台 400（借 COMMISSION_REVENUE 400 / 贷 UNION_RECEIVABLE 400），booked_base_fen=0、booked_n_fen=600，UNION_RECEIVABLE 600，订单保持 CREDITED。

**边界**：B_settle（结算额按 BR-CALC-02 换算）= booked_base_fen 且结算佣金的正数部分 = booked_n_fen 时不补差；基数相等而联盟佣金不同时只调平台金额（正文 ③）；负差即时补差使 available 变负时按 BR-FUND-10、BR-WDR-05 (a) 处理。

**差错单类型**：结算有、我方 ESTIMATED（收货同步缺失）；结算有、我方 VOID；结算有、我方 CLAWED_BACK；结算有、我方无订单（漏单）；我方 CREDITED、结算无（多单）；API 结算额与明细不一致。月结账单校验另有「账单金额不一致」「应结未结」两类（BR-FUND-04 ④）。

**时点**：各平台结算状态出现时点与回款日待 规划/09 实测，R1 调度按实测结果配置；正差批次未批准前余额不变。补差负向时发站内信并附原因。

C-07 已由负责人决定（拍板第二批 FUND-11），与本条默认一致：负差即时记账、人工批准只用于正差（批准一人可完成，§8 ADD-05）。

- 随 BR-FUND-04 月结口径调整（变更记录 §3；2026-09-30 负责人补充，变更记录 §10：月结账单由系统在月结账单日按联盟接口返回的结算数据自动生成，结算明细上传只作接口不可用时的备用）：联盟结算数据（source=API 为主，STATEMENT 为上传备用）写入后同时驱动 BR-FUND-04 月结账单首次入账批次（WAITING）与本条 R1 补差（CREDITED），「每日 02:00 检查明细是否拉全、拉全后次日运行 R1」的调度需与 BR-FUND-04 ③ 月结账单日生成合并；差错单类型需补 BR-FUND-04 的「账单金额不一致」「应结未结」；「取代」中 规划/01 F-SET-05「月结不产生首次入账」的表述需按新口径复核（首次入账现随月结账单批次发生，本条 R1 仍不产生首次入账）。2026-10-01 已改写：R1 调度并入月结账单生成（规则正文），差错单类型已补上述两类；规划/01 F-SET-05 的改述见本主题同步清单。

#### BR-FUND-10 细则 · 负余额规则

- 状态：已确认
- 默认值：无（已确认，按规则执行）
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 §2.7、§2.9：「为负期间申请提现返回 30202」
  - 本条 2026-10-01 写法：「available_fen < 0 时该账户提现申请必须返回 30302；后续入账直接计入该账户…；SELF 与 PROMO 两账户不互抵、不自动划转」（单一余额，拍板第二批 §8 ADD-06；余额为负不能注销，ADD-07）
  - 本条正文 2026-10-03 前写法：「只有 CLAWBACK、负向 SETTLE_ADJUST、负向 ADMIN_ADJUST 可以使 USER_BALANCE.available_fen &lt; 0」（BR-ATTR-20 明写改派时原会员可以负余额，而改派红冲沿用原入账的流水类型，不在白名单里，原会员已提现时改派做不了；只补改派红冲，其他红冲不列入）（2026-10-03 资金规则对齐（负责人批准），方案 §7.5，同-24）
- 来源：规划/01 E10 F-SET-04；规划/02 §8.3、§8.4；规划/04 §7 错误码 30302；PRD修订_后端功能规划 §2.7 负余额、§2.8 记账规则 5；PRD v2.1 §11.4；docs/changes/20261001-拍板第二批.md §8 ADD-06、ADD-07；docs/changes/20261003-资金规则对齐.md

**展示**：可提现 = max(available_fen, 0)；待抵扣 = max(−available_fen, 0)，钱包显示「待抵扣 ¥x，后续返利将优先抵扣」。

**例**：available=−400，新入账 REBATE_CREDIT 600 → available=200，可提现 200；为负期间申请注销返回 30416（data.amount_fen=400）。

**例（改派红冲允许变负，2026-10-03 资金规则对齐 E-36）**：P0（预留 2000）入账后 U1 已提现 400（available 0），P1 余额 80；后台把订单改派给没有上级的 U2（R14）→ 红冲 U1 −400（available −400）、P1 −80、平台 −520；按新快照重记 U2 +400、平台 +600（留存 320 + 无上级留平台的 80 + 预留 200）；UNION_RECEIVABLE 不变；U1 之后按负余额规则处理，日终 ⑦ 不报差异。改派以外的红冲（如更正一张入账凭证）会使余额变负时仍被拒绝。

**并发**：提现冻结与扣回并发时，均按 account_id 行锁串行；冻结先提交则扣回照常把 available 扣负，frozen 不动；已冻结未打款的提现单按 BR-WDR-05 (a) 处理。

**错误码映射**：后端功能规划的 30202 在 规划/04 中是「订单不可找回」，本规则统一用 30302「余额为负，暂不能提现」；与账务差异冻结（30303，data.reason=account_frozen，BR-FUND-19）同时满足时按 BR-WDR-03 校验顺序优先返回 30303(account_frozen)。

按 C-03 默认处理（账务差异冻结改用 30303 account_frozen，30306 只表示提现开关关闭），待负责人确认。

#### BR-FUND-11 细则 · 负余额时禁止提现

- 状态：已确认（负责人 2026-10-01，依据 docs/changes/20261001-拍板第二批.md §8 ADD-06：用户只有一个余额，余额为负时不能提现，未打款的提现单自动驳回并抵扣；此前 FUND-12「两户都禁提」随单一余额失去对象；原为待决策）
- 默认值：余额为负即禁止提现；未打款的非终态提现单自动驳回、冻结额退回抵扣（BR-WDR-05 (a)）。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 本条 2026-10-01 写法（标题「负余额跨账户提现限制」）：「用户任一账户（SELF 或 PROMO）available_fen < 0 时，两个账户都不得提现；两账户仍不互抵、不划转资金」（单一余额，ADD-06）
- 来源：规划/01 E10 F-SET-04；规划/04 §4.2 W1 守卫「余额非负」；PRD修订_后端功能规划 §2.7 负余额；docs/changes/20261001-拍板第二批.md FUND-12、§8 ADD-06
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

**例**：available=−1000 → 申请提现 3000 返回 30302；后续入账抵平到 ≥0 后可正常提现。

**错误码与已有提现单**：申请返回的错误码（30302）、未打款提现单的驳回与抵扣，均见 BR-WDR-05 (a)，本条只维护「余额为负禁提」这一决策。

C-08、C-21 已由负责人决定（拍板第二批 FUND-12）；单一余额后「另一账户」的情形不再存在（§8 ADD-06），BR-WDR-05 (a) 不再使用 blocked_reason=NEGATIVE_BALANCE_OTHER。

#### BR-FUND-12 细则 · 负余额坏账核销

- 状态：已确认（规则机制：负责人 2026-10-01，依据 docs/changes/20261001-拍板第二批.md FUND-09；§8 ADD-05 改为超管或有权限账号一人 step-up 批准，ADD-07 取消注销时的负余额核销（余额为负不能注销），ADD-03 数值 ledger.bad_debt_days、ledger.bad_debt_min_fen 开发期用占位值、上线前超管在后台填写；原为待决策）
- 默认值：90 天、金额阈值 0（占位值）、一人 step-up 批准；理由：规划/06 Q-B2 默认值；PRD 的「≥阈值进人工追偿清单」阈值未定，暂取 0。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD v2.1 §11.4：「负余额超 90 天且金额 ≥阈值（待确认）进人工追偿清单」
  - BR-ID-28 旧写法：「注销时余额为负的，负额以 BAD_DEBT_WRITEOFF 核销」（未经两人审批；按 FUND-09 改为当即生成候选单、两人审批）
  - 本条 2026-10-01 写法：「必须由 finance 发起、另一名 finance 或 super（≠发起人）step-up 后批准」「用户注销进入 processing 时 available < 0 的账户当即生成核销候选单，不受 bad_debt_days 与 bad_debt_min_fen 限制，仍按本条两人审批」「数值由负责人、财务在 W1 随 specs/ledger-rules.md 给出」（拍板第二批 §8 ADD-05、ADD-07、ADD-03）
  - 本条正文 2026-10-03 前写法：「批准时重读 available：&lt;0 → 写 BAD_DEBT_WRITEOFF（…金额 = −当前 available_fen…）」（没有看冻结中的提现金额：用户还有一张卡住的提现单时先核销、之后再驳回或付出这张单，平台会记坏账又付钱；负责人选决-11 A）（2026-10-03 资金规则对齐（负责人批准），方案 §7.4，决-11）
- 来源：规划/01 E10 F-SET-04；规划/06 Q-B2；规划/02 §8.3；规划/04 §2.4；PRD修订_后端功能规划 §2.7 坏账；PRD v2.1 §11.4；BR-ID-28；docs/changes/20261001-拍板第二批.md FUND-09、FUND-21、§8 ADD-03、ADD-05、ADD-07；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**例**：用户余额于 2026-11-20 被扣至 −800 → negative_since=11-20；至 2027-02-18（第 90 天）仍为 −800 → 生成候选单；批准前入账 500 使余额为 −300 → 批准时核销 300，available=0。若 12-01 入账 800 抵平，negative_since 清空，不生成候选。

**例（注销）**：用户 12-01 申请注销时 available=−300 → 返回 30416「账户有待扣回金额，暂不能注销」，不生成核销候选单；后续返利入账抵扣回正后才能申请（BR-ID-27，ADD-07）。未申请注销的负余额用户按上例满 90 天后核销，财务甲 step-up 批准即执行。

**例（有卡住的提现单，2026-10-03 资金规则对齐 E-35）**：available −1000，frozen 1000（一张 APPROVED 单，有一次付款方侧失败的转账尝试，只标了 blocked）；满 90 天生成候选单 → 批准时 frozen 1000 > 0，拒绝，候选单保持 PENDING，提示先处理提现单；财务驳回该单（查询确认没有到账后，BR-WDR-17）→ 退回 1000，available 0 → 候选单在下次批准时按 available ≥0 置 CANCELLED，没有坏账，也没有打款。

**核销后**：后续入账正常计入余额，不追溯追偿；用户标记 risk（风控尚无 BR 主题，以 规划/01 E17 风控为准）。

**个人信息**：关联标记只用于提现风控，处理目的须在隐私政策「风控与反作弊」条款中列明（见 BR-ID-35、BR-ID-12）；标记不向用户展示内部依据，用户可经客服申诉，申诉结果写审计。

**阶段**：负余额报表 M-内测；核销操作在首个候选可能出现前（首笔真实入账日 + 90 天）上线。人工追偿清单与核销候选单合并。

#### BR-FUND-13 细则 · 单一余额与余额性质

- 状态：已确认（负责人 2026-10-01 改为单一余额，依据 docs/changes/20261001-拍板第二批.md §8 ADD-06）
- 默认值：无（已确认，按规则执行）
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - PRD v2.1 §11.1：「用户账户 self_rebate、promo_income（命名）」
  - PRD修订_后端功能规划 §2.8：「U_SELF_AVAIL/U_SELF_FROZEN、U_PROMO_AVAIL/U_PROMO_FROZEN（命名）」
  - 本条 2026-10-01 写法（标题「两个账户与余额性质」）：「每个用户注册时必须创建两个账户：SELF（自购返利，科目 USER_SELF:{uid}）与 PROMO（推广收益 = 分享单 + 直推分佣，科目 USER_PROMO:{uid}）…入账账户由订单 pid_scene 与受益人角色决定…不得提供…两账户互转接口…手续费、门槛按账户分别配置」（ADD-06）
- 来源：规划/00 §4、§3.2 D12；规划/04 §2.2、§2.4；规划/02 §8.2；规划/07 §4 #9、§5；PRD v2.1 §11.1；PRD修订_后端功能规划 §2.8；docs/changes/20261001-拍板第二批.md §8 ADD-06
- 需同步修改的规划文档：规划/04 ledger_accounts、account_balances、wallet 接口（删除 account_type）；规划/02 §8.2 科目表；规划/01 钱包页；规划/10 钱包与提现用例（随 ADD-06 同步）

USER_BALANCE 可入流水：REBATE_CREDIT、SHARE_CREDIT、REFERRAL_CREDIT、CLAWBACK、SETTLE_ADJUST、提现类、ADMIN_ADJUST、BAD_DEBT_WRITEOFF、REWARD(P1)。

**所得类型**：income_type 不由收入来源决定，按 (ledger_type, sub_type) 读配置 tax.income_type_map；佣金类流水（REBATE_CREDIT、SHARE_CREDIT、REFERRAL_CREDIT 各 sub_type）一律映射 SERVICE_FEE（劳务报酬），全部提现合并累计计税（负责人 2026-09-30 补充，2026-10-01 拍板第二批 FUND-04 确认，与 ADD-06 一致）；税率与计算只在 BR-WDR-20 维护。

**例**：用户 A 分享商品给 B，B 下单 → B 是买家不获返利（share 订单买家是否计返利见 BR-ATTR），A 的余额获 SHARE_CREDIT；A 的直推上级的余额获 REFERRAL_CREDIT（DIRECT）。A 自购一单 → A 的同一余额获 REBATE_CREDIT；钱包只显示一个可提现余额，流水按类型显示来源。

科目名称以 ledger_accounts 唯一键 (app_id, owner_type, owner_id, subject) 为准。

#### BR-FUND-14 细则 · 冻结与已提现资金变动

- 状态：默认假设
- 默认值：打款中资金保留在 frozen，去掉 frozen→WITHDRAW_IN_TRANSIT 这一步；理由：用户看到的「冻结中」直接等于 frozen_fen，打款在途金额可由提现单状态查询，R2 对账不依赖在途科目。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - 规划/02 §8.3：「进入打款：借 USER_\*.frozen / 贷 WITHDRAW_IN_TRANSIT；打款成功：借 WITHDRAW_IN_TRANSIT / 贷 CASH_ALIPAY；打款失败/驳回借方含 WITHDRAW_IN_TRANSIT」
  - 规划/04 §4.2 W4、W5、W6：「冻结 → 在途；在途 → 出金；在途 → 可用」
  - PRD修订_后端功能规划 §2.8：「FREEZE 的 sub_type 含 risk（风控冻结移动资金）」
  - 本条 2026-10-01 写法：「④ 每账户 frozen_fen = Σ 该账户非终态提现单」「⑤ …留在 PROMO available…禁提由 BR-WDR-06 ① 执行」（单一余额，拍板第二批 §8 ADD-06）
- 来源：规划/04 §2.4、§4.2；规划/02 §8.2、§8.3；规划/01 §5 J6、F-WDR-01；PRD修订_后端功能规划 §2.8、§3.3；BR-ID-26；docs/changes/20261001-拍板第二批.md FUND-10、§8 ADD-06
- 需同步修改的规划文档：5 处（计数仅作记录，落点见 README §0.6）

**例**：available=5000，有一张 PENDING_REVIEW 提现单 3000、一张 PAYING 提现单 1000 → frozen_fen 必须 = 4000（冻结中 ¥40）；该会员随后被风控冻结 → available、frozen 均不变，只是不能再申请与执行提现。各步的分录与含税费的例子见 BR-WDR-09。

**已提现金额** = Σ 终态 PAID_API/PAID_MANUAL 提现单 amount_fen；到手金额 = amount − fee − tax。

**冻结中（附原因）**：原因 = 对应提现单状态文案（审核中/打款中）；风控冻结以账户横幅单独提示，不计入冻结中金额。提现规则数值、审核、打款流程见 BR-WDR。

**未成年推广收益（⑤，拍板第二批 FUND-10、§8 ADD-06）**：BR-ID-26 (c) 原写「冻结至满 18 周岁」，与 ① 冲突（frozen 只放提现单）；负责人 2026-10-01 定为留在余额不动，单一余额后不再区分推广账户。例：16 岁用户 9-20 实名识别前已入账推广收益 ¥30 → available 不变、frozen 不变；未满 18 周岁期间该用户全部提现合计受每月 ¥200 上限约束（BR-WDR-06）；满 18 周岁时刻起不再受限，不需解冻任务，也不写流水。

#### BR-FUND-15 细则 · 流水类型与映射

- 状态：默认假设
- 默认值：采用 规划/04 §2.4 的 13 种命名（用户已确认命名以 规划 为准）；类型集合与科目写入 specs/ledger-rules.md（代理按本主题起草，财务确认前按本条执行）。单一余额下用户流水的来源即 ledger_type + sub_type（拍板第二批 §8 ADD-06）。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD v2.1 §11.2：「流水类型 15 种（CREDIT_SELF_REBATE…ADMIN_ADJUST_OUT，含 CREDIT_INDIRECT_COMMISSION）」
  - PRD修订_后端功能规划 §2.8：「entry_type 15 类（INVITE_L1_CREDIT、INVITE_L2_CREDIT、FREEZE、UNFREEZE、TAX_WITHHELD、ACTIVITY_REWARD、BAD_DEBT_WRITE_OFF、OPENING_BALANCE 等）」
  - 本条旧写法（2026-09-30）：「契约不得定义间推类流水（D8）」「REFERRAL_CREDIT：DIRECT（只此一值）」
  - 本条 2026-10-01 前写法：「ADMIN_ADJUST：调账原因码（含 RESTORE，见 BR-FUND-22；必填原因与操作人）」（原因码与流程改由 BR-FUND-24 维护）
  - 本条正文 2026-10-03 前没有写红冲与改派重记用哪个流水类型（随 BR-FUND-10、BR-FUND-19 ⑦ 的改派红冲白名单写明沿用原类型；BR-FUND-25 细则已按此假设）（2026-10-03 资金规则对齐（负责人批准），方案 §7.5，同-24）
- 来源：规划/04 §2.4；规划/00 §6、§3.2 D8；docs/changes/20261001-间推二级奖励.md；PRD v2.1 §11.2；PRD修订_后端功能规划 §2.8；开发任务拆解 H-06；参考_花卷云功能查漏底稿 §7；docs/changes/20261001-拍板第二批.md FUND-13；docs/changes/20261001-拍板第二批.md §8 ADD-06；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**sub_type 值域**：CLAWBACK：FULL / PART_REFUND / RIGHTS / PUNISH；SETTLE_ADJUST：SETTLE_DIFF / PRICE_COMPARE / PRICE_PROTECT（默认 SETTLE_DIFF，Adapter 能识别原因时写 PRICE_PROTECT、PRICE_COMPARE；R9b 不再写 SETTLE_ADJUST，2026-10-03 资金规则对齐方案 §2）；REFERRAL_CREDIT：DIRECT / INDIRECT（INDIRECT 只在间推开关开启的规则版本下产生，BR-CALC-05）；REWARD：newbie / checkin / invite；ADMIN_ADJUST：调账原因码，值域与流程只在 BR-FUND-24 维护（含 RESTORE，见 BR-FUND-22；ACCOUNT_CLOSED，注销放弃余额）。

**用户侧名称**：各 ledger_type 的用户侧名称只在 BR-TEXT-19（字典 ledger_type.&lt;CODE>.name）维护；WITHDRAW_PAID 为「提现到账」（C-02 已由负责人决定，拍板第一批 §3、拍板第二批 OPS-01）。

**映射表**：

| PRD v2.1（15 种） | 后端功能规划 | 规划 ledger_type |
|---|---|---|
| CREDIT_SELF_REBATE | REBATE_CREDIT | REBATE_CREDIT |
| CREDIT_SHARE_REBATE | SHARE_CREDIT | SHARE_CREDIT |
| CREDIT_DIRECT_COMMISSION | INVITE_L1_CREDIT | REFERRAL_CREDIT(DIRECT) |
| CREDIT_INDIRECT_COMMISSION | INVITE_L2_CREDIT | REFERRAL_CREDIT(INDIRECT)（D8 2026-10-01 修订；不新增类型） |
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

C-02 已由负责人决定（拍板第二批 OPS-01）：提现侧用「到账」，WITHDRAW_PAID 汇总条目名称随 BR-TEXT-19。

#### BR-FUND-16 细则 · 复式记账硬约束

- 状态：已确认
- 默认值：无（已确认，按规则执行）
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 §2.8 记账规则 1：「分录 direction（借/贷）+ amount_fen > 0（与 规划 带符号口径不同，以 规划 为准）」
  - 本条细则「加锁流程」2026-10-03 前写法：「一锁（FOR UPDATE 用户账户行）→ 二判（uniq_key 是否存在、余额是否满足 BR-FUND-10）→ 三写（凭证、分录含 balance_after_fen、余额缓存）→ 四提交。」（没有 users 行，也没有多受益人的加锁顺序与「取得锁之后重读受益人状态」，入账与注销、封禁并发时会按旧状态记账，交叉受益人的订单可能互相等待）（2026-10-03 资金规则对齐（负责人批准），方案 §4，同-06）
- 来源：规划/02 §1 原则 3/8、§8.1、§11；规划/00 §3.2 D11；规划/01 E10 F-SET-01；规划/05 §3.3、§7；PRD修订_后端功能规划 §1.7、§2.8 记账规则 1–6；PRD v2.1 §11.1；开发任务拆解 BF-02、QA-01/02；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

**加锁流程**（2026-10-03 资金规则对齐方案 §4）：订单相关的记账事务（迁移 R5、R5a、R8、R9、R10、R13、R14）按固定顺序加锁：

1. `pg_advisory_xact_lock(order_key)`（BR-FUND-01）；
2. 本事务要读其状态或要写其余额的全部用户，按 user_id 升序对 users 行 `SELECT … FOR UPDATE`（BR-WDR-07）；
3. 这些用户的 account_balances 行按 account_id 升序 `FOR UPDATE`；
4. 取得 2、3 之后重读每个受益人的状态（注销状态、风控状态、是否已识别未满 18 周岁），按重读结果决定入其账户、暂缓、归平台还是改记坏账；取得锁之前读到的状态只能用来预筛，不得用来记账；
5. 判幂等键（uniq_key 是否存在）与余额（是否满足 BR-FUND-10），写凭证、分录（含 balance_after_fen）、余额缓存和订单字段，提交。

平台科目不加锁（本条正文）。提现类事务的顺序不变：users 行 → 余额行 → 收款账号 advisory 锁（BR-WDR-07），自动到账判定再取 `auto_payout_daily`（BR-WDR-30）。改变受益人状态的事务（风控冻结、封禁、解冻、账户申诉立案与结案、注销进入 processing、实名核验结果写入）必须先对该 users 行 `FOR UPDATE`，再写状态。

例：订单 X 的受益人是（U1 本人、U2 上级），订单 Y 是（U2 本人、U1 上级）；两个事务都按 user_id 升序先锁 U1 再锁 U2，不会互相等待。入账与注销并发：批次读到 U7 正常 → 注销任务先锁 U7、置为注销处理中并提交 → 批次事务取得 U7 的锁后重读到注销处理中，U7 的份额按 BR-CALC-13 归平台，不写其余额。

**例**：REBATE_CREDIT 617：分录① UNION_RECEIVABLE:taobao +617；分录② USER_BALANCE:42.available −617；Σ=0；USER_BALANCE:42.available_fen 从 1000 变 1617，分录② balance_after_fen=1617。

**错误更正例**：误调账 +500（ADMIN_ADJUST，uniq_key=ADJ:9001）→ 红冲凭证 −500（uniq_key=ADJ:9001:REVERSE）→ 重记正确的 +50。

**强一致**：余额、分录、rebate_status、提现状态只在同一 PG 事务内变更；领域事件（与业务写入同一事务入队的任务）只驱动推送、风控、看板、trace。

**分工**：凭证粒度、科目、红冲规则写在 specs/ledger-rules.md（代理按本主题起草，财务确认）；锁顺序按上方「加锁流程」（2026-10-03 按本条授权统一）；缓存策略等其他实现细节代理可自定。

#### BR-FUND-17 细则 · 资金话术与状态对应

- 状态：已确认（负责人 2026-10-01，依据 docs/changes/20261001-拍板第二批.md OPS-01：结算前叫预估、结算后叫已结算、显示预计结算月份；派生条件按 FUND-01 月结口径改写；原为待决策，「返利到账」与 BR-TEXT-01、BR-WDR-25 存在分歧 C-02）
- 默认值：display_status 派生顺序如下表；术语用词按 BR-TEXT-01（C-02 由负责人决定：结算前一律「预估」，联盟结算并经月结批次入账后「已结算」），用词只改 BR-TEXT-01、02、06 与 /v1/dict 字典，不改本条派生条件。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 规划/00 §2：「「确认收货 15 天后返利入账」（承诺了固定天数，时点见 BR-FUND-04）」
  - 规划/04 §2.3 CREDITED 行：「用户文案「已到账」（订单侧改为「已入账」）」
  - 本条 2026-09-30 派生表第 11–13 行：「WAITING 且结算未记录，且（低于日结门槛，或 credit_requires_settle=true）→ WAITING_SETTLE」「WAITING 且 expected_credit_date 早于今天 → CREDITING」「WAITING → 已收货，预计 MM-DD 入账」（随 BR-FUND-04 月结口径改写，2026-10-01）
  - 本条 2026-09-30 默认值：「术语用词按 C-02 默认（BR-TEXT-01 方案 A）」（负责人改定为预估 / 已结算口径）
  - 本条派生表第 3 行 2026-10-03 前写法：「CREDITED 且无 CREDIT 凭证（B_credit=0）」（对入账时份额暂缓、尚无 CREDIT 凭证的受益人会误判成「本单无返利」；基数为 0 时平台凭证照写，按凭证判断也不准）（2026-10-03 资金规则对齐（负责人批准），方案 §6.6、§7.3，同-13、同-23）
- 来源：规划/04 §2.3、§2.4；规划/01 §5 J1、J6；PRD修订_后端功能规划 §2.16、§3.2 用户侧展示映射；PRD v2.1 §11.1 术语；README §1.2；BR-TEXT-01；docs/changes/20261001-拍板第二批.md OPS-01、FUND-01；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：5 处（计数仅作记录，落点见 README §0.6）

用户术语与资金状态、字段的对应只在 BR-TEXT-01 术语对照表维护（钱包金额字段见 BR-FUND-18），提现状态文案只在 BR-TEXT-06 维护，README §1.2 为索引；本条不再列术语表（原表已删，内容均已在 BR-TEXT-01 覆盖）。

**订单 display_status 派生表**（从上到下取第一个匹配项；「文案（示意）」列按 BR-TEXT-01 口径示意，便于阅读，正式文字以 BR-TEXT-02、BR-TEXT-03、BR-TEXT-04 与字典为准，两处不一致时以 BR-TEXT-02 为准，本条只维护条件与顺序；第 11 行停用但保留行号，供其他条目按行号引用）：

| # | 条件 | display_status | 文案（示意） |
|---|---|---|---|
| 0 | rebate=UNATTRIBUTED | 不返回 | — |
| 1 | VOID | INVALID | 已失效（附原因） |
| 2 | CLAWED_BACK | CLAWED_BACK | 已扣回 |
| 3 | CREDITED 且 booked_base_fen = 0 | NO_REBATE | 本单无返利 |
| 4 | CREDITED 且存在 CLAWBACK | CREDITED_PART_CLAWED | 已结算（部分扣回 ¥x） |
| 5 | CREDITED | CREDITED | 已结算（有补差时显示差额与原因，BR-TEXT-03） |
| 6 | ESTIMATED 且 platform=DEPOSIT_PAID（不看 B_est，也不看 hold） | DEPOSIT_PAID | 已付定金 |
| 7 | ESTIMATED/WAITING 且 B_est=0（B_est 为 null 不匹配） | NO_REBATE | 本单无返利 |
| 8 | hold=true | REVIEWING | 入账核对中 |
| 9 | rights_pending=true | RIGHTS_PENDING | 售后处理中，入账暂停 |
| 10 | WAITING 且该平台 credit.enabled=off（BR-CALC-03、BR-FUND-04） | CREDITING | 入账核对中（不显示月份） |
| 11 | （停用）月结口径下不再派生：只有已有联盟结算数据的子订单进入结算批次，入账基数一律由结算额换算（BR-FUND-04 边界） | WAITING_SETTLE（不进契约） | — |
| 12 | WAITING 且 credit_overdue=true（BR-FUND-04 ⑪） | CREDITING | 入账核对中（不显示月份） |
| 13 | WAITING | WAITING | 已收货，等待联盟结算（预计 {月份} 结算，BR-TEXT-04） |
| 14 | ESTIMATED | PAID | 已付款，返利待确认 |

**查看者本人份额暂缓**（2026-10-03 资金规则对齐方案 §6.6）：订单已 CREDITED（匹配第 4、5 行）而查看者本人在该单的份额处于暂缓、尚未入账（held，BR-CALC-13；之后按 BR-FUND-04 ⑫ 补记）时，对该查看者按 REVIEWING「入账核对中」展示，不显示「已结算」；其他受益人照常按第 4、5 行。文案归 BR-TEXT-02。

**B_est 为空**：orders.est_commission_fen 为 null（从未收到联盟佣金数值，如 DEPOSIT_PAID 阶段未给佣金；已有数值后缺失不覆盖，见 BR-FUND-07）表示「未知」，不视为 0：不匹配第 7 行，不触发 BR-FUND-07 的 COMMISSION_ZERO，不向用户展示金额（ESTIMATED 按第 14 行「已付款，返利待确认」、WAITING 按第 10、12、13 行）；WAITING 且入账基数（BR-FUND-05）为 null 时结算批次跳过该单并告警，不按 0 入账。第 6 行先于第 7 行，保证付定金阶段 B_est=0 或 null 时显示「已付定金」而非「本单无返利」（BR-ATTR-01 例、10 AC-S1-24 ②、AC-S2-12-TB）。

**CREDITING 的两种来源**：第 10 行（平台入账开关 off）与第 12 行（预计结算月份的账单日 + 宽限天数已过仍未入账，credit_overdue=true）共用 display_status=CREDITING 与字典 key `order_status.CREDITING`，不新增枚举；两者都不显示月份（第 10 行 expected_credit_period=null；第 12 行按 BR-TEXT-04 不展示已过期的月份）。BR-TEXT-02 该行的「对应双状态」说明应同步补上第 10 行条件（判定以本表为准）。

**例**：客服或 Agent 被问「我的返利到账了吗？」—先调订单接口取 display_status：得到 WAITING（expected_credit_period=2026-11）时按字典 `order_status.WAITING` 渲染（「已收货，等待联盟结算｜预估返 ¥x｜预计 11 月结算」）；得到 CREDITED 时按 `order_status.CREDITED` 渲染（「已结算」）；不得在接口返回前凭对话内容推断状态或金额。用词按 BR-TEXT-01，提现问题按 BR-TEXT-06。

术语与禁用词按 C-02 负责人决定（拍板第二批 OPS-01；术语见 BR-TEXT-01，禁用词归 BR-TEXT-13）；本条派生条件与 C-02 无关。

- 随 BR-FUND-04 月结口径调整（变更记录 §3；2026-10-01 已改写）：第 11 行 WAITING_SETTLE 停用（行号保留，枚举不进契约、不建字典 key）；第 12 行改按 BR-FUND-04 ⑪ 的 credit_overdue；第 13 行按 expected_credit_period 展示（文案 BR-TEXT-04）；「例」同改。需同步：08 12_TEXT BR-TEXT-02 映射表与 BR-TEXT-04「不显示月份」列表删去 WAITING_SETTLE；规划/04 display_status 枚举删去 WAITING_SETTLE。

#### BR-FUND-18 细则 · 钱包汇总与资产快照口径

- 状态：已确认（负责人 2026-10-01，依据 docs/changes/20261001-拍板第二批.md OPS-01（结算前统称预估、显示预计结算月份，C-02）与 FUND-07（月结批次与快照时序，C-17）；原为默认假设）
- 默认值：预估合计 = ESTIMATED（已付款）+ WAITING（已收货）份额，WAITING 部分另以 pending_credit_fen 作「其中已收货」进度行；预计结算月份取可计订单 expected_credit_period 的最早值；快照 00:01 写入，结算批次与月结账单都等快照完成。理由：负责人定结算前一律称预估，用户侧不再单列「待入账」（BR-TEXT-01）；快照先于批次保证余额与预估口径时点一致。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 规划/04 §6.4：「两个账户：可提现、待到账、冻结、负余额（待到账口径未定义）」
  - 规划/04 §3.2 asset_snapshots：「total_pending_fen（未区分 WAITING 与 ESTIMATED）」
  - PRD修订_后端功能规划 §2.8：「liability_snapshots 每天 00:15 写入」
  - 本条 2026-09-30 写法：「待入账 = 仅 WAITING（已收货），预估单列 estimated_fen」「next_credit_date = 最早 expected_credit_date；早于今天时返回今天并 credit_overdue=true」「入账任务 settle.credit 必须在当日快照完成后才开始，最晚等到 00:30」（随 BR-FUND-04 月结与 BR-TEXT-01 预估口径改写，2026-10-01）
  - 本条 2026-10-01 写法：「GET /v1/wallet/summary 必须按 SELF、PROMO 分别返回…estimated_total_fen（该用户在该账户对应角色上…）…withdrawn_fen（Σ 该账户…）」（单一余额，拍板第二批 §8 ADD-06）
  - 本条正文 2026-10-03 前写法：「各份额按 BR-FUND-05 的基数取法计算（N 取 settle_commission_fen 非空时的值，否则 est_commission_fen，经 BR-CALC-02 换算）」（BR-FUND-05 入账口径已改为只取结算佣金，预估类份额改为直接引用 BR-CALC-02 的有效联盟佣金，口径不变）（2026-10-03 资金规则对齐（负责人批准），方案 §2，同-02）
- 来源：规划/04 §3.2、§6.4；规划/01 §5 J6、F-WDR-01、F-SET-08；PRD修订_后端功能规划 §2.8 负债日快照；参考_花卷云功能查漏底稿 §7；docs/changes/20261001-拍板第二批.md OPS-01、FUND-07；docs/changes/20261001-拍板第二批.md §8 ADD-06
- 需同步修改的规划文档：4 处（计数仅作记录，落点见 README §0.6）

**例**：用户余额 available=−400，frozen=0，WAITING 两单 308+617（其中 617 维权中，308 的 expected_credit_period=2026-11），ESTIMATED 一单 123，无提现、无冻结 → withdrawable=0，negative=400，estimated_total=1048，estimated=123，pending_credit=925，pending_credit_paused=617，next_credit_period=2026-11，credit_overdue=false，withdrawn=0，risk_paused_reason=null；钱包按 BR-TEXT-01 显示「预估收益 ¥10.48（其中已收货 ¥9.25，预计 11 月结算；其中 ¥6.17 暂缓入账）」。若到 2026-12-05（11 月账单日 11-24 + 宽限 10 天之后）308 那单仍未入账 → 该单 credit_overdue=true，next_credit_period=null，credit_overdue=true，页面附「入账核对中」。

**为何快照先于批次**：若结算批次在 00:00 后、当日快照完成前执行，D+1 入账的订单凭证 accounting_date=D+1，快照时又已不在 WAITING，这批金额既不在 D 日余额也不在 D 日 waiting，R3「用户应付 vs 资产快照」少一截。00:00 至快照完成之间的非记账状态变化（如失效）计入 D 日。

**说明**：withdrawable_fen 只反映余额，是否满足最低额、次数、负余额限制以 GET /v1/withdrawals/rules 为准。钱包页展示可提现、预估（estimated_total_fen，附「其中已收货」与预计结算月份）、冻结中、已提现（文案按 BR-TEXT-01）；estimated_fen、pending_credit_fen 分项供进度行、订单汇总与 Agent 查询使用。

**与 BR-TEXT-01 钱包汇总口径的关系**：字段名已与 BR-TEXT-01 对齐（原 waiting_fen→pending_credit_fen、waiting_paused_fen→pending_credit_paused_fen、next_due_date→next_credit_date、due_overdue→credit_overdue，新增 withdrawn_fen、risk_paused_reason）。2026-10-01 随月结口径：新增 estimated_total_fen（即 BR-TEXT-01 的「预估合计」，原写「字段名待 BR-FUND-18 随月结改写时定」）；next_credit_date 改为 next_credit_period（预计结算月份，多平台取最早）；credit_overdue 的单不计入 next_credit_period，只置 credit_overdue=true。取值口径以本条为准：estimated_fen 按 BR-FUND-05 基数取法 × 快照比例计算（BR-TEXT-01 曾写 rebate_min_fen 合计）。

C-02 已由负责人决定（拍板第二批 OPS-01：用户侧不再单列「待入账」，结算前统称预估）；C-17 随 BR-FUND-04 流程参数确认（拍板第二批 FUND-07：快照 D+1 00:01 写入，结算批次与月结账单等快照完成，最晚 00:30）。

- 随 BR-FUND-04 月结口径调整（变更记录 §3；2026-10-01 已改写）：next_credit_date 改为 next_credit_period，credit_overdue 改引 BR-FUND-04 ⑪，入账任务等快照改为结算批次与月结账单等快照，例同改。需同步：规划/04 §6.4 GET /v1/wallet/summary 响应字段（增 estimated_total_fen，next_credit_date → next_credit_period）；08 12_TEXT BR-TEXT-01 钱包口径字段名；08_AI 数据来源表中的钱包字段。

#### BR-FUND-19 细则 · 账务不变量与日终校验

- 状态：默认假设
- 默认值：账户级差异冻结涉及用户提现；全局差异自动关闭自动入账并冻结涉及用户提现；理由：规划只写「冻结对应账户提现」，PRD 写「冻结自动任务」，按影响范围分两级处理，且全局差异时多入的钱不能被提走。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 §2.8 记账规则 7：「00:10 写 daily_balances 并校验（时间改为与 01:00 校验合并）」
  - PRD v2.1 §11.7：「任何差异冻结自动任务并告警（未分级）」
  - 本条正文 2026-10-03 前写法：「④每 (子订单, 受益人, 角色) Σ CLAWBACK ≤ CREDIT + Σ 正向 SETTLE_ADJUST；⑤每个 CREDITED 或 CLAWED_BACK 子订单：该单订单类凭证（CREDIT、CLAWBACK、SETTLE_ADJUST、ADMIN_ADJUST RESTORE）对 UNION_RECEIVABLE 的净额 = booked_base_fen，且 Σ受益人已入账净额 ≤ booked_base_fen」（预留比例不为 0、有暂缓或延后受益人、扣回 → 恢复 → 再扣回、改派后扣回这几种正常业务下不成立，每天都会触发全局差异）（2026-10-03 资金规则对齐（负责人批准），方案 §3，同-05）
  - 本条正文 ⑦ 2026-10-03 前写法：「⑦用户账户中每条使 balance_after_fen &lt;0 且较前一条下降的分录，其 ledger_type ∈ {CLAWBACK, SETTLE_ADJUST, ADMIN_ADJUST}」（改派红冲沿用原入账类型，按此会报账户级差异；随 BR-FUND-10 补改派红冲）（2026-10-03 资金规则对齐（负责人批准），方案 §7.5，同-24）
- 来源：规划/02 §8.4；规划/01 E10 F-SET-06、§7.2；规划/04 §7 错误码 30306；PRD修订_后端功能规划 §1.6、§2.8、§10.1 AC-MONEY-013；PRD v2.1 §11.7；开发任务拆解 BF-10、QA-01/02；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**例**：01:00 发现 USER_BALANCE:42 缓存 5000、分录合计 4900 → P1 告警，生成差错单 E1，为用户 42 新增 withdraw_holds（reason=ledger_mismatch，source_ref=E1），提现申请返回 30303（data.reason=account_frozen）；财务调账、关闭 E1 时 step-up 解除该条记录。

**全局例**：发现 taobao:1234567 的 (用户 42, self) 有 2 张 CREDIT 凭证 → settle.auto.enabled=off，停止自动入账，用户 42 新增 withdraw_holds，提现返回 30303(account_frozen)；值班人工处理后由有权限者 step-up 重新打开开关，差错单关闭时解除冻结记录。

**与 30302 同时满足**：用户 42 同时有生效冻结记录且 available=−100 → 返回 30303(account_frozen)（BR-WDR-03 ⑦ 在 ⑧ 之前）；冻结解除后再申请 → 30302。

**⑧ 例**：订单 platform_status=INVALID 但 rebate_status=CREDITED（扣回事件丢失）→ 冻结该单全部受益人提现，差错单进人工，按 BR-FUND-08 补扣。

**④⑤ 例（2026-10-03 资金规则对齐 E-10、E-11）**：P0 订单（淘宝 reserve_bp=2000，结算佣金 1000，本人 U1 5000、直推 P1 1000）。① 入账无暂缓：U1 +400、P1 +80、平台 +520，UNION_RECEIVABLE 净额 1000 = booked_n_fen 1000 − 0，通过。② 另一单入账时 U1 被冻结（暂缓）：P1 +80、平台 +520，U1 的 400 不写凭证 → 净额 600 = 1000 − 400，通过；③ 暂缓期间结算佣金改为 900：P1 −8、平台 −52 → 净额 540 = 900 − 360（U1 应得变 360），通过；④ U1 解冻后补记 +360 → 净额 900 = 900 − 0，通过。另一单：入账 → 全额维权扣回 → 人工恢复（R13）→ 再次全额扣回，U1 的净额 400 − 400 + 400 − 400 = 0，④ 通过；按旧写法「Σ CLAWBACK 800 > CREDIT 400」会报全局差异。

**口径说明**：计入应收的联盟佣金是否含补贴类佣金，随 BR-CALC-18（待验证）与 specs/ledger-rules.md 定；⑤ 只要求 booked_n_fen 与平台凭证用同一口径。

**测试**：以上不变量作为属性测试，PR 跑 1 万次、夜间 100 万次；真实 PG 并发测试覆盖并发提现、并发入账、任务重复投递。

按 C-03 默认处理（错误码 30306 改为 30303 data.reason=account_frozen），待负责人确认；按 C-09 默认处理（冻结只记在 withdraw_holds，不另设 users.withdraw_blocked_reason），待财务确认。

#### BR-FUND-20 细则 · 垫资敞口与入账开关

- 状态：已确认（规则机制：负责人 2026-10-01；告警阈值 ledger.advance_alert_fen 开发期为占位值，上线前由超管在后台填写，之后可随时修改、立即生效，依据 docs/changes/20261001-拍板第二批.md §8 ADD-03（取代 FUND-21）；原为待决策）
- 默认值：告警阈值由超管在后台填写，未填写前只展示看板不告警；按合计告警、平台分项只展示；开关默认 on。
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 §2.8：「「月末差额进平台资金台账」写法删除，只有差错单关闭时才按核销凭证入账（本条沿用）」
  - 本条 2026-09-30 写法：「垫资周期：收货后约 15 天入账，联盟回款约次月 20 日前后，平台最长垫付约 50 天」「开关为 off 时入账任务按 BR-FUND-04 停止」（随 BR-FUND-04 月结口径改写，2026-10-01）
  - 本条 2026-10-01 写法：「告警阈值 ledger.advance_alert_fen 由负责人、财务在 W1 随 specs/ledger-rules.md 一次给出」（拍板第二批 §8 ADD-03）
- 来源：规划/01 §3 垫付营运资金；规划/02 §8.3、§8.5、§1 原则 8；规划/04 §10.2；PRD v2.1 §11.4；PRD修订_后端功能规划 §2.8；开发任务拆解 BF-11；docs/changes/20261001-拍板第二批.md FUND-01、FUND-21、§8 ADD-03
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**垫资周期**：入账随月结账单批次发生（BR-FUND-04），入账时联盟已对该单结算；已入账未回款主要是联盟结算到联盟回款之间的时差，回款日待 规划/09 核实。敞口远小于原逐单入账口径。

**例**：11-24 月结批次入账 2026-10 账单合计 1,200,000 分、12-20 淘宝回款 1,150,000 分 → UNION_RECEIVABLE:taobao 余额 50,000 分，差额进 R1 差错单，不直接记损益。阈值 1,000,000 分时：11-24 至 12-19 每天合计 1,200,000 → 每天告警 1 次；12-21 回落到 50,000 → 不告警。

企业支付宝水位 W/P 与暂停打款规则见 BR-WDR-18、BR-WDR-17。

- 随 BR-FUND-04 月结口径调整（变更记录 §3；2026-10-01 已改写）：垫资周期、例与开关为 off 时的停止点已按月结批次改写（见规则正文与上文）。

#### BR-FUND-21 细则 · 负余额时未打款的提现单

- 状态：已确认（负责人 2026-10-01，依据 docs/changes/20261001-拍板第二批.md FUND-12：未打款单自动驳回抵扣，C-08、C-21 随之结案；§8 ADD-06 单一余额后不再有「另一账户」挂起；原为待决策，决策人财务）
- 规则正文：负余额对非终态提现单的全部处理——W2/W4/W8 守卫、事件 account.went_negative 的写入与消费、未打款单 W3 驳回（NEGATIVE_BALANCE）并退回冻结额抵扣负数、PAYING 单经 W9 回到 APPROVED 后的处理——只在 BR-WDR-05 (a) 维护，默认值、取代项、例子与理由一并见 BR-WDR-05 细则。本条不再单独规定，编号保留供 C-08、C-21 与 规划/00–07、10、BR-TEXT-08 的既有引用定位。
- 2026-09-30 修订：原正文与 BR-WDR-05 (a) 重复维护同一套细则，合并到 BR-WDR-05 (a)；原例子（部分扣回、跨账户、PAYING 未发出）与「同账户为何驳回而不是暂停」已并入 BR-WDR-05 细则。

#### BR-FUND-22 细则 · 作废或扣回订单的平台恢复

- 状态：已确认（负责人 2026-10-01，依据 docs/changes/20261001-拍板第二批.md FUND-14：申诉撤销时系统自动生成「申诉恢复」差错单，人工处理后恢复并补发；§8 ADD-05 改为超管或有权限账号一人 step-up 处理；原为默认假设）
- 默认值：平台恢复只经人工处理（一人 step-up，写审计），不自动复活；处罚/黑名单作废不告警；申诉撤销时系统自动生成「申诉恢复」差错单，处理方式相同。理由：终态自动复活会与已发推送、已扣回余额冲突；恢复涉及资金，须有权限者 step-up 并留审计。
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - BR-ID-36 旧写法：「撤销 → … 作废的订单由后台按 BR-FUND-22 恢复」（本条原只为平台恢复生成差错单，申诉成功的订单没有入口；改为申诉撤销时系统自动生成「申诉恢复」差错单）
  - BR-CALC-13 旧写法：「已注销或 risk_state=banned → … 份额计入 COMMISSION_REVENUE，此后不再补发」（封禁经申诉撤销的，按本条 ③ 补发）
  - 本条 2026-10-01 写法：「ops 或 finance 发起，另一人（≠发起人）step-up 复核」「R12 守卫：发起人 ≠ 复核人」（拍板第二批 §8 ADD-05）
  - 本条 R13 2026-10-03 前写法：「按当前联盟佣金与分佣快照重算各受益人与平台应得…同事务 booked_base_fen=新基数」（没说先换算）（2026-10-03 资金规则对齐（负责人批准），方案 §1，同-01）
  - 本条 R13 与 ③ 2026-10-03 前写法：「与当前净额的差额写 ADMIN_ADJUST（sub_type=RESTORE…）」「与其已入账净额之差写 ADMIN_ADJUST（sub_type=RESTORE，借 COMMISSION_REVENUE / 贷 USER_BALANCE.available），uniq_key 同上。」（净额口径未写明含已有的 RESTORE，同一份额遇到第二张差错单会再补一次；R13 未引用 BR-CALC-09 的受益人状态规则；③ 未写补发后之后的调整怎么算应得）（2026-10-03 资金规则对齐（负责人批准），方案 §6.2、§7.6，同-09、同-26）
  - 本条 R12 2026-10-03 前写法：「R12：VOID → 按当前 platform_status 回到 ESTIMATED 或 WAITING（…），不写分录。」表中「到」列「ESTIMATED 或 WAITING」（未归因的 VOID 订单恢复后该回到 UNATTRIBUTED，原写法没有）（2026-10-03 资金规则对齐（负责人批准），方案 §6.11，同-17）
  - 本条正文 2026-10-03 前没有写处罚被平台解冻之后怎么办（外部资料称淘宝处罚订单可在冻结与解冻之间切换，未实测；负责人选决-06 实测前 A：不恢复、留证据，实测证实后的选项另议）（2026-10-03 资金规则对齐（负责人批准），方案 §6.10，决-06）
- 来源：规划/04 §4.1 O4、O9；规划/02 §8.5；PRD修订_后端功能规划 §3.2；BR-ID-36；docs/changes/20261001-拍板第二批.md FUND-14、OPS-07、§8 ADD-05；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

| # | 从 | 事件 | 守卫 | 到 | 记账 |
|---|---|---|---|---|---|
| R12 | VOID | ADMIN_RESTORE | 差错单存在；操作人有权限且 step-up；platform_status ≠ INVALID | ESTIMATED 或 WAITING；user_id 为空的回到 UNATTRIBUTED | 无 |
| R13 | CLAWED_BACK | ADMIN_RESTORE | 同上 | CREDITED | ADMIN_ADJUST(RESTORE) |

**例（R12）**：10-03 退款失效 → VOID(REFUND)；10-06 淘宝回传「订单成功」（买家撤销退款）→ P9 platform_status=RECEIVED，告警，差错单；10-07 运营 step-up 恢复 → WAITING，settle_period 按 received_at 取，随结算批次入账（BR-FUND-04）。

**例（R13）**：本例预留比例为 0。已入账 617/123/494 后全额扣回 → CLAWED_BACK；联盟恢复佣金 1234 → 差错单；处理恢复 → ADMIN_ADJUST +617/+123/+494，booked_base_fen=booked_n_fen=1234，状态 CREDITED。

**例（不告警）**：黑名单命中作废的订单，平台照常推进到 RECEIVED → 只更新 platform_status。

**例（申诉恢复）**：订单 taobao:5550001 因渠道黑名单 10-03 作废（VOID，BLACKLIST），用户 10-04 对该订单申诉（只标记该订单申诉中，账户 risk_state 不变，OPS-07），10-06 结案撤销 → 系统生成差错单「申诉恢复」→ 运营 step-up 处理 → R12 回到 WAITING，随结算批次入账。直推上级 U 在 11-24 批次入账时为 banned，其份额 123 计入平台留存；12-01 U 的封禁申诉撤销 → 差错单「申诉恢复」→ 处理后写 ADMIN_ADJUST(RESTORE)：借 COMMISSION_REVENUE 123 / 贷 USER_BALANCE:U 123。

#### BR-FUND-23 细则 · 月末三项核对

- 状态：默认假设
- 默认值：每月 1 日 01:30 对上月运行；等式 X1 = X2 + X3，差额 ≥1 分即告警并生成差错单，不自动冻结；「上月联盟预估佣金」等只列示。理由：花卷云底稿把「负债日快照 + 月末三项对平」列为易漏项；BR-FUND-19 的日终校验按账户比对分录与余额缓存，本条用提现单表与资产快照这两个独立来源做总量核对，能发现分录与业务单据之间的偏差；定位与冻结已由 BR-FUND-19 负责，本条不重复冻结。积分余额（花卷云第三项口径之一）属 P1 积分功能，MVP 无积分账户，不纳入；积分上线时另行新增条目。
- 决策人：财务
- 依赖平台能力：无
- 取代：无
- 来源：参考_花卷云功能查漏底稿 §7「负债日快照」、§16 #20；规划/02 §8.4 R3 内部对账（分录合计 vs 余额；用户应付合计 vs 资产快照）；规划/01 F-ADM-08；docs/changes/20261001-拍板第二批.md §8 ADD-06
- 需同步修改的规划文档：规划/02 §8.4 R3 行补「月度三项核对（BR-FUND-23）」；规划/04 §3.2 差错单类型补「月末三项不平」（部分落实，登记于 README §0.6）

**计算**（单位分；「对用户余额的影响」贷记用户为正、借记为负）：

| 项 | 口径 | 数据来源 |
|---|---|---|
| X1 用户累计入账净额 | accounting_date ≤ M 月末日的用户 available 子户分录中，ledger_type ∈ {REBATE_CREDIT, SHARE_CREDIT, REFERRAL_CREDIT, REWARD, CLAWBACK, SETTLE_ADJUST, ADMIN_ADJUST, BAD_DEBT_WRITEOFF} 的影响合计；不含 WITHDRAW_FREEZE、WITHDRAW_RETURN | ledger_entries |
| X2 用户期末余额 | M 月末日 asset_snapshots：total_available_positive_fen − total_negative_fen + total_frozen_fen | asset_snapshots（BR-FUND-18） |
| X3 用户累计已提现 | 截至 M 月末迁移到 PAID_API/PAID_MANUAL 的提现单 amount_fen 合计（含税与手续费） | withdrawals |

**例**：上线至 10-31 累计：入账 1,000,000，扣回 −30,000，补差 −5,000，核销 +800 → X1=965,800；10-31 快照 available 正数合计 700,000、负数合计 1,200、frozen 50,000 → X2=748,800；已到账提现单合计 217,000 → X3=217,000；748,800 + 217,000 = 965,800，相等。若某提现单被误改 amount_fen 为 21,000（实际分录 WITHDRAW_PAID+FEE+TAX=20,000），X3 多 1,000 → 差额 −1,000，告警并生成差错单。

**边界**：月末日快照被标记 waiting_comparable=false 不影响本条（只用余额类字段）；月末日快照缺失时本条不运行，告警并在快照补写后由 finance 手动触发；单一余额后不再分账户核对（拍板第二批 §8 ADD-06，原写「分 SELF/PROMO 与合计」）；上线日所在月份之前的月份不运行，上线当月按上线日至月末的数据照常核对（X1、X3 均从 0 起算，D1 不迁移数据）。

#### BR-FUND-24 细则 · 人工调账

- 状态：已确认（负责人 2026-10-01，依据 docs/changes/20261001-拍板第二批.md FUND-13：二次验证、必填原因码与关联单据、不设上限；§8 ADD-05 改为超管或有权限账号一人可完成（取代 FUND-13「财务发起 + 另一人复核」），ADD-06 单一余额，ADD-07 余额为负不能注销；原因码集合、对方科目、负余额、用户可见与注销处理为代理起草，负责人 2026-10-01 授权按推荐；ACCOUNT_CLOSED 依据同批 FUND-09）
- 默认值：见规则正文 ①–⑧。理由：调账直接改变用户负债，强制关联单据，使每笔调账都能追溯到差错单或业务事件；不设上限、一人可完成按负责人决定，风险由权限点、step-up 与审计日志控制。
- 决策人：负责人（流程）；财务（科目，specs/ledger-rules.md）
- 依赖平台能力：无
- 取代：
  - 08 13_命名与编码对照 ADMIN_ADJUST 行：「财务发起、第二人复核」（只写在命名对照表，08 无独立规则；规则改在本条维护）
  - 规划/02 §8.5：「调账需第二人复核」（原因码、关联单据、用户可见推给尚未编写的 specs/ledger-rules.md）
  - BR-FUND-15 旧写法：「ADMIN_ADJUST：调账原因码（含 RESTORE，见 BR-FUND-22；必填原因与操作人）」
  - BR-ID-28 旧写法：「资金：余额与未结算收益按放弃处理（分录见 BR-FUND）」（未定放弃用哪种流水与科目；按 FUND-09 改为 ⑧ ACCOUNT_CLOSED 调账转平台收入）
  - 本条 2026-10-01 写法：「① finance 发起（用户、账户 SELF/PROMO…），另一名 finance 或 super（≠发起人）复核；发起与复核都需 step-up」「⑥ 科目表以财务在 specs/ledger-rules.md 签字为准」「⑧ …available < 0 的按 BR-FUND-12 核销」（拍板第二批 §8 ADD-05、ADD-06、ADD-07）
- 来源：规划/02 §8.5；08 13_命名与编码对照；BR-FUND-10、12、15、16、22；BR-WDR-15、23；BR-ID-27、28；docs/changes/20261001-拍板第二批.md FUND-09、FUND-13、§8 ADD-05、ADD-06、ADD-07
- 需同步修改的规划文档：规划/04（调账单表、ADMIN_ADJUST sub_type 枚举、后台调账接口、§11 权限行）；规划/01 后台调账页；08 12_TEXT BR-TEXT-19（ADMIN_ADJUST 按原因码的说明）与站内信模板；08 10_ID BR-ID-28（注销余额处理引用本条 ⑧）；08 13 ADMIN_ADJUST 行

**例（追回重复打款）**：R2 发现提现单 W2026… 迟到成功、重复出款 ¥100（BR-WDR-23）→ 财务甲发起调账单：用户 42、调减 10000 分、PAYOUT_RECOVERY、关联该提现单与差错单 E9 → 甲 step-up 批准 → 写 ADMIN_ADJUST（借 USER_BALANCE:42.available 10000 / 贷 CASH_ALIPAY 10000），available 由 3000 变 −7000；用户流水显示 1 条调减及按原因码的说明，并收到站内信；之后按 BR-FUND-10、11 处理负余额。

**例（无权限）**：未被勾选人工调账权限的客服账号发起调账 → 拒绝并写审计。

**例（红冲）**：调账单 9001 误调 +500 → 另发调账单 9002（关联 9001）写 `ADJ:9001:REVERSE` −500，再发 9003 记正确的 +50（BR-FUND-16）。

**例（注销）**：用户 12-01 进入 processing，available=2000 → 系统预填 ACCOUNT_CLOSED 调减单；12-02 财务甲 step-up 批准时仍为 2000 → 借 USER_BALANCE.available 2000 / 贷 COMMISSION_REVENUE 2000。若该用户申请注销时 available=−300 → 申请返回 30416，不进入冷静期，也不生成核销候选单（BR-ID-27，ADD-07）。

**用户侧**：流水名称、按原因码的说明与站内信措辞只在 BR-TEXT-19 与通知模板维护；原因码中文名示意：RESTORE「订单恢复」、RECON_FIX「对账更正」、PAYOUT_RECOVERY「重复到账追回」、OTHER「余额调整」（ACCOUNT_CLOSED 只用于已注销用户，不对外展示）。

#### BR-FUND-25 细则 · 收益看板口径

- 状态：待决策（默认）。2026-10-03 新增（功能对照 G-11）；按功能对照 Q-10 的默认 A 写，负责人尚未回答，登记在 规划/06「功能对照待确认」。
- 默认值：进 M-公开；自购与分享两栏给今日、昨日、本月、上月的付款笔数、预估、已结算；邀请栏只给本月、上月的金额合计，不给笔数、不按天拆；付款笔数与预估按付款日归期，已结算按入账日归期；已结算取入账类分录的代数和（含更正与改归属的红冲、重记），不并入之后的售后扣回、结算补差与人工调账。理由：规划/04 早已登记该接口为 M-公开，但没有口径，开发只能猜；邀请分佣若按天给笔数，上级能反推出好友的下单日期，与 BR-INV-17「日期只到日、不可跳转」的初衷不符。
- 决策人：负责人（是否进 M-公开、邀请栏展示范围）；财务（已结算是否改为扣除扣回后的净额）
- 依赖平台能力：无
- 取代：
  - 规划/04 §6.4 原写：「收益看板：今日 / 昨日 / 本月 / 上月的付款笔数、预估、已结算，自购与推广分开；金额口径同 BR-FUND-18」（「推广」未区分本人分享单与邀请分佣，按天给笔数；口径改由本条定义）
  - 08 13 §13.9 `GET /v1/earnings/summary` 行的同一句描述
- 来源：规划/04 §6.4；08 13 §13.9；PRD修订_后端功能规划（GET /v1/earnings/summary）；BR-FUND-18；BR-INV-16、BR-INV-17、BR-INV-20、BR-INV-23；BR-TEXT-01；docs/research/20261003-功能对照缺口清单.md G-11、docs/research/20261003-功能对照待确认问题.md Q-10
- 需同步修改的规划文档：规划/00 §4 资金行；规划/01 §4.2（Earnings）、F-WDR-14；规划/04 §6.4、§10.1；规划/05 B2-13、F1-12；规划/10 AC-S2-61；08 13 §13.9；BR-TEXT-01 细则（已同步 2026-10-03）

**期间**（+08:00）：今日 = [当日 00:00, 次日 00:00)；昨日 = 前一个自然日；本月 = [本月 1 日 00:00, 下月 1 日 00:00)；上月同理。服务端用注入时钟计算，响应带 as_of（统计截至时刻），客户端不自行换算期间。

**三栏与字段**（形状见 规划/04 §6.4）：

| 栏 | 范围 | 期间 | 付款笔数 | 预估 | 已结算 |
| --- | --- | --- | --- | --- | --- |
| ① 自购 | 本人为归属用户、buy_type=self 的子订单 | 今日、昨日、本月、上月 | 有 | 本人份额（role=self） | REBATE_CREDIT |
| ② 分享 | 本人为归属用户、buy_type=share 的子订单（本人的分享单） | 今日、昨日、本月、上月 | 有 | 本人份额（role=share） | SHARE_CREDIT |
| ③ 邀请 | 本人为 direct 或 indirect 受益人的邀请分佣（间推只在规则版本开启时存在，BR-CALC-05） | 只有本月、上月 | 不返回 | 两种角色的份额合计 | REFERRAL_CREDIT（DIRECT + INDIRECT）合计 |

- 付款笔数按子订单计（一个子订单一笔，BR-ATTR-22）；含「本单无返利」的订单（它们也在订单列表里）。
- 看板是查询时刻的事实，不是历史快照：订单后来失效，它所在期间的笔数与预估随之减少；找回通过的订单按其 paid_at 归到原付款期间；后台改归属后按新归属用户统计。
- 已结算怎样聚合（2026-10-03 评审后改写；原写法「已结算只增不减」与红冲、改归属不能同时成立，作废）：
  - 取数范围：本人 USER_BALANCE 的 available 子户上、ledger_type 属于该栏类型（① REBATE_CREDIT，② SHARE_CREDIT，③ REFERRAL_CREDIT）、会计日 accounting_date 落在期间内的分录。平台科目和别人子户上的分录不取。
  - 符号：按「入账为正」取值，即 −amount_fen（用户负债账户贷记为负，BR-FUND-16）。首次入账与重记是正数，红冲是负数。
  - 计入的三种分录：首次入账（BR-FUND-05）；红冲，即错误更正凭证（uniq_key 以 :REVERSE 结尾，BR-FUND-16）和已入账订单改归属时冲回原受益人的凭证（REASSIGN_REV，BR-FUND-01 R14）落在本人子户上的分录；重记，即更正后重新记的入账和改归属后记给新受益人的入账（REASSIGN_CREDIT）。红冲与重记沿用被更正分录的 ledger_type 与 sub_type（BR-FUND-15 的 13 个类型里没有单独的更正类型）；specs/ledger-rules.md 起草时按此写明，由财务确认。
  - 期间：三种分录都按各自的会计日归期间，不回改原入账所在期间的数。某个期间只有红冲、没有足够的入账相抵时，该期间的已结算是负数，接口如实返回，页面按带符号金额显示（BR-TEXT-10）。
  - 不计入：SETTLE_ADJUST（结算补差，含负差）、CLAWBACK（售后扣回）、ADMIN_ADJUST（人工调账）以及提现、税费等其余类型。前三种是否并入已结算、让它变成净额，属资金口径，由财务定（本主题未决问题第 22 项）；确定前它们只在余额流水逐笔显示（BR-TEXT-19），页面在已结算旁按字典给一句说明。
  - 可核对的性质（做成测试断言）：任一期间，全体用户某一栏的已结算之和 = 该期间各用户 available 子户上该类型分录的 −Σ amount_fen。改归属时原受益人的入账与红冲相抵为 0，只剩新受益人的重记，同一笔收益不会被统计两次。
  - 付款笔数与预估不看分录：它们按查询时刻订单的当前归属计算（上一条），改归属后只算在新归属用户名下。
- 例（已入账订单改归属）：订单 S 归 A，A 的自购份额 520 于 2026-10-24 入账。2026-11-12 后台把 S 改归 B（R14）：同一事务红冲 A 的 520，再按新快照给 B 重记（这里也是 520），两张凭证的会计日都是 11-12。→ A：10 月已结算仍含这 520，11 月已结算因红冲减 520（当月没有别的入账时显示 −¥5.20），两个月相加为 0。B：11 月已结算加 520。全体用户 10 月、11 月两期合计仍是 520。付款笔数：S 只算在 B 名下，按 S 的付款日归期。
- 预估取 BR-FUND-18 的份额算法，四个期间之和不等于钱包的「预估收益」（钱包不限付款期间），页面不把两者并排比较。
- ③ 不分直推与间推，不显示层级（BR-INV-20）；间推开关关闭时 ③ 只有直推。③ 的两个数都是合计，不提供展开、明细或跳转；逐笔的已结算分佣仍只在余额流水按 BR-TEXT-19 显示（日期到日）。
- platform 筛选：只过滤 ①②；带筛选时 ③ 原样返回全部平台合计，页面在该栏标注「不分平台」（文案见 BR-TEXT-01）。
- 缓存：≤60 秒，按 user_id 隔离（同 BR-FUND-18 预估类）。
- 不得出现的内容：其他用户的昵称、手机号、订单与笔数；排行、与他人比较；「团队」「下线」等用语（BR-INV-20）；「佣金」「返现」等禁用词（BR-TEXT-13）。

**例**：现在是 2026-11-12 10:00。用户 A 本月自购 3 笔：11-02 付款的一笔已确认收货、等待月结（WAITING），份额 269；11-10 付款的一笔还没收货（ESTIMATED），份额 135；11-11 付款的一笔在 11-12 09:00 退款失效。A 邀请的好友本月付款 2 笔，A 的直推份额合计 54。→ ① 本月：付款笔数 2、预估 404、已结算 0；① 昨日：付款笔数 0（11-11 那笔已失效，不计）；③ 本月：预估 54、已结算 0，没有笔数。11-24 的月结批次把 A 在 10 月付款的两笔入账，共 520 → ① 本月已结算 520（按入账日归本月），这两笔的付款笔数仍算在上月。

**负责人改选时**：选 B（推到 P1）→ earnings.dashboard.enabled 置 off，规划/00 §4 该行改 P1，页面入口隐藏；想让邀请栏显示更多（笔数、按天）→ 属放宽上级可见范围，须先改 BR-INV-16、BR-INV-17 并写影响评估（规划/00 §8）。

### 6.3 本主题未决问题

1. 【已由负责人确认 2026-09-30，变更记录 §2】BR-FUND-01：是否采用 platform_status + rebate_status 双状态模型取代 规划/04 单一 order_status（默认采用），需负责人拍板。
2. 【已由负责人确认 2026-09-30（C-06），变更记录 §2】BR-FUND-01 R2/R3、BR-FUND-03：分佣快照生成时点与等级、上级取值时点，现按 C-06 默认（生成时点按 BR-CALC-10，等级与上级取 paid_at，BR-CALC-12；原默认「找回单取批准时刻」已撤回），需负责人确认。
3. 【已被取代：负责人 2026-09-30 改为跟随联盟月结批量入账，变更记录 §3；见本节第 18 条】BR-FUND-04：预计入账日按「满 15×24 小时后首个 00:05 入账日」（约收货日+16 天）还是按自然日「收货日+15 天」（实际观察期不足 15 天），需负责人拍板。 拍板第二批 FUND-16 选当前默认（满 15×24 小时、维权不顺延），该选择只在保留逐单入账时适用；FUND-01 已选月结，不生效。
4. 【已被取代：月结口径下无 credit_due_at，维权 / hold 期间暂缓、解除后进补充批次或下一周期批次，见 BR-FUND-04】BR-FUND-04：维权或 hold 期间 credit_due_at 是否顺延（默认不顺延，理由：维权结果已明确；替代：顺延维权持续时长），需负责人拍板；expected_credit_date 在维权 / hold 期间返回 null、解除后按 max(credit_due_at, received_synced_at, 解除时刻) 重算（G-16 默认），需负责人确认。 拍板第二批 FUND-16 同上，不生效。
5. 【已被取代：拍板第二批 §8 ADD-06 改为单一余额，余额为负即禁提（BR-FUND-11）；此前 FUND-12 按默认两账户都禁提】BR-FUND-11：一个账户为负时，另一账户是否仍可提现（默认两账户都禁提），需财务拍板。
6. 【已由负责人确认 2026-10-01，拍板第二批 FUND-12：未打款单自动驳回并退回抵扣（默认）；§8 ADD-06 后不再区分同账户 / 另一账户】BR-FUND-21（规则正文在 BR-WDR-05 (a)）：账户变负时同账户未打款提现单自动驳回（默认）还是暂停待回正，需财务拍板（对应 C-08）。
7. 淘宝/京东/拼多多订单接口中「确认收货」与「结算」是否为独立状态、各自时间字段名与出现顺序；淘宝「订单结算」状态出现时点与联盟回款日是否同一时点（BR-FUND-02），需进 规划/09 实测并附接口样例。
8. 各平台是否提供「维权处理中」信号、淘宝维权接口是否返回应扣佣金（BR-FUND-06、BR-FUND-08）；京东「实际佣金归零」能否与部分维权区分。
9. 【已被取代：月结口径下不设收货后等待期，核销型订单同样随联盟账单批次入账】核销型订单（美团、饿了么，均 P1，D15）入账等待期是否不同于 15 天（后端功能规划 B12，W1），默认同为 15 天。
10. 【已由拍板第二批 §8 ADD-03 改定：经营数值开发期用占位值、上线前由超管在后台填写，不再单独签字（取代 FUND-21）；BR-FUND-12、BR-FUND-20 机制已确认；科目表与凭证粒度写入 specs/ledger-rules.md，由财务确认】财务需给出：已入账未回款告警阈值 ledger.advance_alert_fen、坏账核销最低金额 ledger.bad_debt_min_fen、specs/ledger-rules.md 的科目表、凭证粒度与流水类型签字（W1 周三前）。
11. 淘宝、京东、拼多多联盟实际结算/回款日（「次月 20 日前后」）待核实，影响 R1 调度与垫资测算；月结口径下同时决定 BR-FUND-04 月结账单日 settle.bill_day（默认 24 日，须晚于各平台联盟结算日）与结算周期取法（见第 18 条）。（2026-09-30 负责人补充：出账日 = 月结账单日，原 settle.statement_day.&lt;platform> 删除。）
12. 【已由负责人确认 2026-10-01，拍板第二批 OPS-01：结算前叫预估、结算后叫已结算、显示预计结算月份；用词只在 BR-TEXT-01 维护，本主题示意文字已按此改写】本主题用户文案（BR-FUND-04、06、15、17、18 中的示意文字）的用词随 C-02 与 BR-TEXT-01 方案 A/B，需负责人拍板；拍板后只改 BR-TEXT-01、02、06 与字典，本主题派生条件与字段不变。
13. 【已由负责人确认 2026-10-01，拍板第二批 FUND-11：负差即时扣、正差人工批准再补（默认）；§8 ADD-05 改为一人 step-up 批准】BR-FUND-09：结算负差即时记账、正差双人复核（默认，C-07）还是所有补差都双人复核，需财务拍板。
14. BR-FUND-19：账务差异冻结记入 withdraw_holds（reason=ledger_mismatch）并返回 30303(account_frozen)（默认，C-03、C-09），需负责人（错误码）与财务（冻结记录方式）确认。
15. 【已由负责人确认 2026-10-03，资金规则对齐决-03 选 A（联盟没给数时挂起）、决-04 确认默认（凭证粒度、C-16）；BR-FUND-05、BR-FUND-08 改为已确认】BR-FUND-05、BR-FUND-08：入账基数取法、凭证粒度与扣回流水类型（CLAWBACK vs 负向 SETTLE_ADJUST，C-16）已由默认假设改为待决策，需财务确认（写入 specs/ledger-rules.md）。（2026-10-01：入账基数取法随 FUND-01 月结与平台预留比例决定已定，由联盟结算额按 BR-CALC-02 换算；仍待财务确认的是凭证粒度与 C-16，确认前按默认实现，不阻塞开发。）
16. 【已由负责人确认 2026-10-01：展示随 OPS-01（CREDITING「入账核对中」，不显示月份），单批上限 5000 随 FUND-07】BR-FUND-04、BR-FUND-17：credit.enabled.&lt;platform>=off 期间 WAITING 订单显示 CREDITING「入账核对中」、不给日期，商品详情与未收货订单不展示入账时点文案（默认，复用 CREDITING 枚举，不新增 CREDIT_PAUSED）；开关打开后积压订单由下一次任务处理，单批上限 settle.credit.max_orders_per_run 默认 5000，需负责人确认展示、财务确认上限取值。（2026-09-30 月结口径：开关打开后对已导入账单重新比对生成批次，单批上限改为 settle.batch.max_orders，默认仍 5000，见第 18 条。）
17. BR-FUND-07、BR-FUND-17：DEPOSIT_PAID 阶段佣金变化不触发 COMMISSION_ZERO、付尾款时 B_est=0 按「本单无返利」不作废、佣金缺失不覆盖已有值（默认处理），需负责人确认。
18. 【已由负责人确认 2026-10-01，拍板第二批 FUND-01、FUND-07：按下列默认】BR-FUND-04 月结流程参数（变更记录 §6「月结结算流程参数」、§9 第 1 项，默认处理，待负责人、财务确认）：月结账单日（默认 24 日，取值 22–28）、结算周期取法（默认 received_at 所在自然月）、一致性校验容差（默认 0 分）、确认人权限（默认 finance 或 super 单人 step-up 确认，替代：超阈值第二人复核）、批次上限（默认 5000）、逾期宽限（默认 10 天）、预计结算月份推算偏移（默认 1 个月）、允许补充批次、hold / 维权中的子订单记暂缓而非差错单。已由负责人 2026-09-30 补充确定（变更记录 §10），不再待定：账单来自联盟接口返回的结算数据、系统在账单日自动生成（人工上传只作接口不可用时的备用），人工确认后立即或定时结算；预计结算月份以联盟返回的结算时间为准。
19. BR-FUND-04 ⑪ 预计结算月份取「联盟返回的结算时间所在月」，依赖该字段的语义（2026-09-30 负责人补充）：若某平台接口的「结算时间」实为确认收货时间或联盟内部记账时间（与向推广者出账结算的月份不同），或联盟结算时间晚于当月月结账单日，展示月份会早于我方实际结算月份，并可能提前触发 credit_overdue「入账核对中」。需 CAP-TB-08、CAP-JD-08、CAP-PDD-08、CAP-MT-08 实测字段语义；候选处理（待负责人确认，未采用）：预计结算月份取 max(联盟结算时间所在月, 确认收货月 + settle.period_offset_months)，或联盟结算时间晚于当月账单日时顺延一个月。
20. 月结账单状态：负责人补充中列出 出账中 → 已出账 → 结算中 → 已结算 四个状态，花卷云另有「待结算」；本条按五个状态（含定时结算未到时刻的「待结算」）由批次状态派生（BR-FUND-04 细则），是否保留「待结算」需负责人确认；这些是后台账单状态用词，不出现在用户侧；BR-TEXT-13 禁用「待结算」「结算中」只约束用户可见文案，二者不冲突。
21. 代理按拍板第二批补全、负责人 2026-10-01 授权按推荐的写法，财务确认 specs/ledger-rules.md 时一并核对：BR-FUND-24 的原因码集合与各原因码对方科目（ACCOUNT_CLOSED 记 COMMISSION_REVENUE、PAYOUT_RECOVERY 记 CASH_ALIPAY）；BR-FUND-08 注销后扣回借 BAD_DEBT 的分录（FUND-09）；BR-FUND-22 ③ 封禁申诉撤销后补发 forfeited 份额（FUND-14）。原列「BR-FUND-12 注销时负余额当即生成核销候选单」已由 §8 ADD-07 取消（余额为负不能注销）。
22. BR-FUND-25 收益看板（2026-10-03，功能对照 G-11）：是否进 M-公开、邀请栏只给本月与上月合计，按功能对照 Q-10 默认 A 写，待负责人确认；「已结算」取入账类分录的代数和（含更正与改归属的红冲、重记，各按自己的会计日归期）、不并入售后扣回、结算补差与人工调账，是代理起草的默认；是否改为净额需财务确认（改净额时须同时定扣回归入哪个期间），红冲是否改为回改原入账期间也一并由财务确认。

---
