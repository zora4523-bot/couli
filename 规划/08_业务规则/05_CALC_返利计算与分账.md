# 08 业务规则 · 5. 返利计算与分账（BR-CALC）

返回 [README](README.md)（使用规则、术语表、规则索引）

## 5. 返利计算与分账（BR-CALC）

本节规定：分佣基数 B、分账公式、比例与上限、舍入、快照时点、调整重算、比价/淘礼金/补贴、每单四段金额。共 27 条（已确认 4、默认假设 7、待决策 10、待验证 6）。

**订单状态写法**：本主题按 BR-FUND-01 的双状态（`platform_status` + `rebate_status`）与迁移编号（P1–P10、R1–R14）书写（按 C-01 默认处理，待负责人确认）。与 规划/04 单一 order_status 的对应：O1→P1；O2→P2 / R2；O3→P3 + R4；O4→P6 + R6（入账前整单失效，rebate_status=VOID）；O5→R7；O6→R5（CREDIT_DUE）；O7→P4 且 rebate_status 不变（只写 order_settlements）；O8→P4 + 结算补差（BR-CALC-23）；O9→R8（rebate_status=CLAWED_BACK）；O10→R9（部分退款、部分维权）/ R9b（价保等佣金变化）；O11→R3。单一状态 SETTLED = (platform_status=SETTLED, rebate_status=CREDITED 且补差已处理完)。负责人不采纳双状态时，按 BR-FUND-01 的映射表回退到上列 O 编号。

### 5.1 规则一览

| 编号 | 规则 | 状态 | 影响面 |
| --- | --- | --- | --- |
| BR-CALC-01 | **金额与比例的数据类型**<br>所有金额必须以整数分存储与运算（PG bigint，字段后缀 _fen，TS 用 bigint）；所有比例必须以整数万分之一存储（字段后缀 _bp，1500 = 15%）。金额运算只能调用 packages/money，分账纯函数只能放在 packages/domain；任何金额路径禁止出现 number 浮点、parseFloat、toFixed、Math.round。对外契约 contracts/openapi.yaml 中所有 \*_fen 字段一律为 integer（int64，单位分），前端按整数处理，只在展示层除以 100 格式化。 | 已确认 | packages/money（mulDivFloor / mulDivCeil）；packages/domain；所有 \*_fen / \*_bp 字段；contracts/openapi.yaml 金额字段为 integer（int64，单位分），见 04 §5；lint 规则 |
| BR-CALC-02 | **分佣基数 B 的定义**<br>分佣基数 B = max(0, N_base − tlj_deduct_fen)。N_base 为联盟口径的推广者收入：已扣平台技术服务费、不含补贴类佣金，单位分（字段映射见 BR-CALC-03、BR-CALC-18）。tlj_deduct_fen 只在我方淘礼金 normal 模式下非 0（BR-CALC-19），其余为 0。不再扣除任何平台预留。取值阶段：settle_commission_fen 为空时取最新预估收入；一旦 settle_commission_fen 非空，N_base 只取结算收入，之后预估字段的变化只存档，不参与计算。commission_splits 中 raw_n_fen 存联盟原值（可为负），base_fen 存计算用的 B（≥ 0），platform_retain_fen = base_fen − Σ用户份额 ≥ 0。每单四段金额与平台预估利润见 BR-CALC-27。 | 待决策 | orders.est_commission_fen / settle_commission_fen（语义：已扣技术服务费的推广者收入）；commission_splits.raw_n_fen / base_fen / platform_retain_fen；毛利报表；R1 联盟对账；specs/commission-examples.csv |
| BR-CALC-03 | **各平台 N 的取数字段**<br>每个平台的 UnionAdapter 必须把订单接口中'已扣技术服务费的推广者预估收入 / 结算收入'映射为 N（再按 BR-CALC-18 拆出 n_base_fen 与 subsidy_commission_fen）。映射写在 specs/attribution.md 并附录制报文，还须与联盟后台同一订单的推广者收入逐单核对一致，证据路径记入 09 表对应 CAP。验证通过前：该平台订单只展示预估，不执行 CREDIT_DUE 入账（含 M3 白名单内测，由 credit.enabled.&lt;platform> 控制，默认 off）；convert.enabled.&lt;platform> 不得对公众打开。若平台返回的是未扣服务费的毛收入，Adapter 按 N = gross − ceil(gross × fee_bp / 10000) 扣除（服务费向上取整，N 取保守值）。fee_bp 优先取订单报文中的服务费率字段；报文没有时取配置 union.&lt;platform>.service_fee_bp（按订单类型配置，每个取值附来源，未核实的标'待核实'）；两处都没有，订单进待处理表并告警，不得按 0 处理。 | 待验证 | UnionAdapter.&lt;platform>.toN()；配置 union.&lt;platform>.service_fee_bp、credit.enabled.&lt;platform>；specs/attribution.md；规划/09_平台能力验证/（对应 CAP 的结论，按 09 README §0.4 回填）；订单同步录制 fixture |
| BR-CALC-04 | **分账公式与受益人（通用与自购单）**<br>每个已归因子订单的分账必须按下式计算：本人份额 = floor(B × r_own_bp / 10000)，受益人为订单归属用户；直推份额 = floor(B × r_direct_bp / 10000)，受益人为归属用户在 paid_at 时的直接上级（BR-CALC-12），无上级时为 0；平台留存 = B − 本人份额 − 直推份额。r_own_bp 与 r_direct_bp 按 BR-CALC-06 取与订单 platform、order_type 对应的行。自购单（order_type=self）本人份额入 SELF 账户，直推份额入 PROMO；分享单的比例与受益人见 BR-CALC-24。order_type 取 orders.buy_type，由归因流程（BR-ATTR）写入，splitCommission() 不自行判断。 | 已确认 | packages/domain splitCommission()；commission_splits.beneficiaries；ledger REBATE_CREDIT / REFERRAL_CREDIT；订单详情页预估返利；验收用例 AC-SET-待编号（参考文档编号 AC-MONEY-001，规划/ 未定义；编号规则见 13 §13.2） |
| BR-CALC-05 | **间推比例固定为 0**<br>间推（上级的上级）份额必须恒为 0：commission_rules 保留列 r_indirect_bp smallint NOT NULL DEFAULT 0 CHECK (r_indirect_bp = 0)，后台与 API 不暴露该列，splitCommission() 不读取、不产生 indirect 角色，后台界面不得出现间推配置项。解锁只能在取得书面法律意见后，通过数据库迁移 + 负责人决策完成。 | 默认假设 | commission_rules 表结构与 CHECK；packages/domain splitCommission()；后台分佣规则页；关系闭包表（MVP 不用于计佣） |
| BR-CALC-06 | **比例配置维度与默认值**<br>commission_rules 每行 = (rule_version_id, platform, level, order_type ∈ {self, share}, r_own_bp, r_direct_bp)，唯一 (rule_version_id, platform, level, order_type)。r_own_bp 用于订单归属用户，按其等级取行；r_direct_bp 用于直接上级，按上级等级取同 platform、同 order_type 的行（等级取值时点见 BR-CALC-12）。发布时版本内必须覆盖配置 commission.platforms × {L1, L2, L3} × {self, share} 的全部组合，缺任一组合则整个版本拒绝发布，不允许回退到其他平台或等级。订单平台在所选版本中没有对应行时，订单进待处理表并告警，不生成快照。 | 待决策 | commission_rules 表结构、唯一约束与种子数据；配置 commission.platforms；后台分佣规则页；商品卡 / Agent 报价；specs/commission-examples.csv；等级页展示文案 |
| BR-CALC-07 | **比例合计上限校验**<br>规则发布时必须对每个 (平台, 订单类型) 校验：max_等级(r_own_bp) + max_等级(r_direct_bp) + 活动加成_bp ≤ 8000；任一单项 &lt; 0 或 > 8000 也拒绝发布。校验不通过返回错误并不生成新版本。 | 待决策 | commission_rules 发布接口；后台分佣规则页校验提示；DB CHECK（单项 0–8000）；验收用例 AC-SET-待编号（参考文档编号 AC-MONEY-014，规划/ 未定义） |
| BR-CALC-08 | **舍入与尾差归属**<br>每个用户份额必须单独按 floor 取整到分（对非负数向下取整）；平台留存 = B − Σ用户份额，承接全部尾差；禁止先按比例算平台份额再倒推用户份额，禁止四舍五入。 | 待决策 | packages/money floor/ceil；packages/domain splitCommission()；specs/ledger-rules.md；属性测试 |
| BR-CALC-09 | **调整按新基数全额重算**<br>任何基数变化（部分退款、价保、结算差额）后，必须用快照比例对新基数 B_new 全额重算每个受益人的应得额，再以'差额 = 新应得 − 已入账（或原预估）'生成调整；禁止对基数差额 ΔB 直接乘比例取整。受益人状态规则：status=forfeited 的受益人新应得恒为 0，不生成任何调整；受益人已注销或 risk_state=banned 时，负向差额照常扣回，正向差额归平台（记 COMMISSION_REVENUE 并写 forfeit_reason）；受益人处于 frozen / appealing 时，负向差额照常扣回，正向差额与 BR-CALC-13 的 hold 一样延后，状态解除后再按当时状态处理。 | 待决策 | settlement 补差任务；CLAWBACK / SETTLE_ADJUST 金额计算；commission_split_amounts；specs/ledger-rules.md；属性测试（多次调整后等于一次性计算） |
| BR-CALC-10 | **分佣快照生成时点与不可变范围**<br>分佣快照必须在子订单首次同时满足'platform_status ∈ {PAID, RECEIVED, SETTLED}'且'已归因到用户'时生成，与触发它的迁移在同一事务写入 commission_splits：入库时已满足 → 入库事务（BR-FUND-01 R2）；已归因但 platform_status=DEPOSIT_PAID → 不生成快照、不计预估（rebate_status=ESTIMATED，预估为 0），在 platform_status 迁到 PAID（P2）的事务内生成；未归因（rebate_status=UNATTRIBUTED）→ 在找回通过或后台改归属（R3）的事务内生成，此时 platform_status 仍为 DEPOSIT_PAID 的，推迟到 P2。未归因订单已为 rebate_status=VOID（对应单一 order_status 的 INVALID；未归因订单不会进入 CLAWED_BACK）时找回通过或改派，按 BR-FUND-01 R3b 只写 user_id、user_basis（BR-ATTR-09）、locked=true，不生成快照、无分录，rebate_status 不变。快照一经生成，rule_version_id、order_type、activity_type、rebate_mode、各受益人的 user_id / role / account_type / ratio_bp / level 不可修改；受益人状态变化与各版本金额只能追加记录，不得覆盖快照行。 | 默认假设 | commission_splits / commission_split_amounts / commission_split_beneficiary_events 表结构与唯一约束；order-sync 入库流水线；BR-FUND-01 迁移 R2 / R3 / P2（含入库即 RECEIVED 时 R2 同事务进 WAITING）；订单详情页（定金阶段文案、失效找回文案）；SM-REB-R2、SM-REB-R3、SM-PLT-P2 测试 |
| BR-CALC-11 | **规则版本生效时点**<br>每个规则版本必须带 effective_from（ISO 8601 +08:00，须 ≥ 发布时刻，下调比例时见 BR-CALC-22），且必须严格大于所有已发布且未撤销版本的 effective_from，否则拒绝发布。快照选用'effective_from ≤ paid_at 的已发布、未撤销版本中 effective_from 最大的一个'（边界含等号，比较精度到秒）。未到 effective_from 的已发布版本可以撤销（status=revoked，须 step-up 并写审计，不改内容）；已生效版本不可撤销、不可修改、不可删除，回滚 = 发布一个新版本。规则变更不回溯已生成的快照。联盟返回的无时区时间一律按 +08:00 解析，存 timestamptz。paid_at 为平台付款时间，预售单取尾款付清时间；平台不提供尾款时间时按本条细则的降级顺序取值。找回、改派订单同样按 paid_at 选版本，不按批准时刻，并在订单与快照记 paid_at_source。 | 默认假设 | commission_rules 版本表：effective_from、status（published / revoked）；快照版本选择查询；orders.paid_at / paid_at_source；后台规则发布页（生效时间必填、撤销未生效版本）；近 7 天试算报告 |
| BR-CALC-12 | **等级与上级的取值时点**<br>快照中本人等级与上级等级都取 paid_at 时刻的有效等级：取 level_change_logs 中 effective_at ≤ paid_at 的最后一条（等号取新等级，BR-INV-14）；等级日志缺失时取注册默认等级 L1 并告警，人工核实后如需补差走 ADMIN_ADJUST。直推受益人取 paid_at 时刻有效的上级（relation_change_logs 按 created_at 重放：bound_at ≤ paid_at 且未解除的上级，bound_at / unbound_at 由相邻记录的 created_at 推出，BR-INV-11）；paid_at 时尚无上级 → 直推份额为 0，事后绑定不补。 | 默认假设 | level_change_logs（需有 effective_at）；relation_change_logs（bound_at = 该条 created_at，unbound_at = 同一用户下一条记录的 created_at，BR-INV-11；表名见 13 §13.8）；commission_splits.beneficiaries.level；等级变更接口；邀请绑定接口 POST /v1/me/inviter |
| BR-CALC-13 | **受益人失效时份额归平台**<br>受益人失效时其份额归平台留存，不得向上顺延给更上级，也不得转给其他受益人。快照生成时判定：受益人不存在或已注销（deletion_status ∈ {processing, done}）→ forfeited，终局不变；risk_state 为 banned、frozen、appealing 的受益人在快照中记 active，不在快照阶段剥夺。入账任务执行时逐受益人判定：已注销或 risk_state=banned → 追加 forfeited 事件并写 forfeit_reason，份额计入 COMMISSION_REVENUE，此后不再补发；risk_state ∈ {frozen, appealing} → 该受益人入账延后（held），其他受益人照常入账，状态恢复 normal 后由入账任务补入账（订单已 CREDITED 时按 BR-FUND-01 R5a），转为 banned 时再判 forfeited；注销冷静期（deletion_status=cooling）不算失效，照常入账（提现限制见 BR-FUND）。订单级风控命中（BLACKLIST_HIT）仍按 BR-FUND-07 整单作废（入账前 R6 → VOID；对应 04 O4），与受益人级 forfeited 分开。受益人级 held 只记在 commission_split_beneficiary_events，不设置订单级 hold 字段（hold 只由人工或风控按 BR-FUND-06 设置）。已入账的份额不因事后封禁而扣回（资金冻结见 BR-FUND-14 与风控 规划/01 E17）。 | 默认假设 | splitCommission() 入参 beneficiary_status；settlement 入账任务（hold 与补入账）；commission_split_beneficiary_events；users.risk_state / deletion_status；客服话术（为何上级没拿到分佣、为何返利延后） |
| BR-CALC-14 | **入账时的基数取值**<br>入账任务执行 R5（CREDIT_DUE，rebate_status WAITING → CREDITED，对应 04 O6）时必须以订单当时最新 N 按 BR-CALC-02 计算 B：orders.settle_commission_fen 非空（已有 order_settlements 记录，取值规则见 BR-FUND-09；对应 04 O7）则用它，否则用入账时刻最新 est_commission_fen，按快照比例重算后入账，并写一个新的 commission_split_amounts 版本（与 BR-FUND-05 的 B_credit 同值）。入账后的调整只由结算差额与部分退款 / 价保触发，记账时点与审批见 BR-CALC-23。差额原因码统一为 PRICE_COMPARE、PRICE_PROTECT、SETTLE_DIFF、PART_REFUND。 | 已确认 | settlement 入账任务；commission_split_amounts；订单详情'实返与预估差额'展示；R1 对账 |
| BR-CALC-15 | **部分退款与价保重算**<br>部分退款、价保、维权部分成功导致佣金变化时，新基数必须取联盟返回的更新后佣金 N_new，不得由我方按数量或金额自行推算。是否由我方估算由配置 union.&lt;platform>.partial_refund_updates_commission（boolean，按 09 表验证结果设置，默认 true）决定：为 false 且退款按件计时，Adapter 用 N_new = floor(N × (quantity − refunded_quantity) / quantity) 作为预估；为 false 且按金额退款或价保时，该子订单置 orders.credit_requires_settle=true：rebate_status=WAITING 期间 settle_commission_fen 为空则入账任务跳过（不使用 BR-FUND-06 的 hold 字段），等联盟结算值到达后按 BR-CALC-14 入账，不得沿用原 N 入账；已 CREDITED 的，等结算值按 BR-CALC-23 (a) 处理。只有新 N 与已存值不同时 commission_version 才 +1，更新语句必须带 WHERE commission_version = :expected 乐观锁，冲突时重读后重算。rebate_status ∈ {ESTIMATED, WAITING}（未入账）：只更新预估，不写流水（BR-FUND-01 R7，对应 04 O5）；rebate_status=CREDITED：按 BR-CALC-09 求差——部分退款、部分维权（R9，对应 04 O10）写 CLAWBACK（sub_type=PART_REFUND 等，BR-FUND-08），价保（R9b）的负差记账方式见 BR-CALC-23 (b)。剩余数量为 0 或 N_new = 0 按整单失效处理（入账前 R6 → VOID，入账后 R8 → CLAWED_BACK；对应 04 O4/O9）。 | 待验证 | orders.refunded_quantity / commission_version（乐观锁）/ credit_requires_settle；配置 union.&lt;platform>.partial_refund_updates_commission；BR-FUND-01 迁移 R7 / R9 / R9b；ledger CLAWBACK sub_type=PART_REFUND；BR-FUND-04 入账守卫；订单详情差额原因 PART_REFUND / PRICE_PROTECT；规划/09_平台能力验证/（对应 CAP 的结论，按 09 README §0.4 回填） |
| BR-CALC-16 | **比价订单的计算与展示**<br>比价订单不得使用特殊比例：订单分账一律以联盟返回的（已降佣的）N 按 BR-CALC-04 / BR-CALC-24 计算，订单记 is_price_compare、commission_rate_min_bp、commission_rate_max_bp，实返与预估不同时差额原因码为 PRICE_COMPARE；比价订单的订单列表、订单详情、入账流水三处金额必须一致。下单前报价的比价风险展示只按 BR-PRICE-07（C-22）。 | 待验证 | orders.is_price_compare / commission_rate_min_bp / commission_rate_max_bp；商品卡与详情页比价区间展示见 BR-PRICE-07；订单差额原因 PRICE_COMPARE；验收用例 F-ORD-11 |
| BR-CALC-17 | **自购与分享报价口径（三平台）**<br>下单前报价必须按订单类型分别估算（由 UnionAdapter.quoteN(product, sku, order_type) 输出，见 BR-CALC-20），订单侧 N 一律直接取联盟订单接口返回值，我方不得对订单再乘任何折算系数。拼多多：自购报价 N = floor(分享口径佣金 × self_buy_factor_bp × account_level_factor_bp / 10000 / 10000)，一次乘完再一次 floor（mulDivFloor(x, a×b, 100000000n)）；分享报价 N = floor(分享口径佣金 × account_level_factor_bp / 10000)；转链必须透传 search_id。淘宝：自购与分享分别用 promotion_type=1 / 2 取佣金；新 App 取不到某一口径时，报价取可得口径中的较低值。京东：PLUS 买家可能按 plusCommissionShare 或 0 计佣，报价按非 PLUS 口径并在详情页提示'PLUS 会员购买部分商品可能无返利'。 | 待验证 | UnionAdapter.&lt;platform>.quoteN()；配置中心 union.pdd.\*；商品卡 / Agent 报价；分享面板预估收益；规划/09_平台能力验证/（对应 CAP 的结论，按 09 README §0.4 回填） |
| BR-CALC-18 | **平台补贴与补贴类佣金**<br>平台补贴（平台出资给消费者的优惠）与补贴类佣金（佣金膨胀、超级补贴等单独计的推广者收入）不得计入 B，归平台留存；订单的基础佣金部分照常分账。UnionAdapter 统一输出 n_base_fen（不含补贴类佣金）与 subsidy_commission_fen 两个字段：联盟给的是含补贴的总额 + 补贴明细时，n_base_fen = 总额 − 补贴；分字段返回时直接映射。B 只用 n_base_fen（BR-CALC-02）；R1 对账用 n_base_fen + subsidy_commission_fen 对联盟总额。自购报价不得包含只在分享场景才有的补贴类佣金。联盟未单列补贴类佣金时的处理见 BR-CALC-25。 | 待验证 | UnionAdapter 输出 n_base_fen / subsidy_commission_fen；orders.activity_type / subsidy_commission_fen；商品卡自购 / 分享报价；毛利报表；R1 对账 |
| BR-CALC-19 | **我方淘礼金订单的返利**<br>来自我方淘礼金推广位（pid_scene=taolijin）的订单，默认 rebate_mode=none：本人份额与直推份额都等于 0，全部 N 归平台以抵淘礼金预算。运营可按商品池条目把 rebate_mode 设为 normal，此时 B = max(0, N_base − tlj_deduct_fen)，再按 BR-CALC-04 分账。tlj_deduct_fen 取我方淘礼金发放记录 tlj_grants 中与该订单 (user_id, item_id) 匹配、状态为已使用、领取时间 ≤ paid_at 的最近一条记录的面额；匹配不到 → 订单进待处理表并告警，按 rebate_mode=none 计算。联盟 N 是否已扣红包由配置 union.taobao.tlj_n_net_of_redpacket 决定（默认 false，待 09 表验证）；为 true 时 tlj_deduct_fen = 0。其他推广者的淘礼金订单不归本 App（见 BR-ATTR）。 | 待决策 | tlj_pool_items.rebate_mode；tlj_grants（匹配键与状态）；配置 union.taobao.tlj_n_net_of_redpacket；splitCommission() 输入 activity_type；淘礼金卡片'预估返利'展示（默认不展示）；04 §2.2 pid_scene 表 |
| BR-CALC-20 | **报价预估与计算函数一致**<br>商品卡、商品详情、Agent 查返利、分享面板、订单预估、入账、补差必须调用同一个 splitCommission() 纯函数。报价计算只在本条维护（BR-PRICE-06 只引用）：报价 = splitCommission(B_quote) 中的本人份额，B_quote 按 BR-CALC-02 由 N_quote 得出（当前 B_quote = N_quote）。N_quote 由各平台 UnionAdapter.quoteN(product, sku, order_type) 输出，定义为'按报价时刻的券后价（final_price_fen）与该订单类型对应的推广者收入率算出、已扣技术服务费、不含补贴类佣金（淘宝佣金膨胀等，BR-CALC-18）、淘礼金与平台补贴的预估推广者收入'；全部整数运算、每次乘除后向下取整：gross = floor(final_price_fen × rate_bp / 10000)，fee = floor(gross × tech_fee_bp[platform] / 10000)，N_quote = gross − fee；rate_bp 由 Adapter 把平台佣金率字段按十进制字符串解析（不用浮点），各平台自购 / 分享口径差异在 Adapter 内换算（BR-CALC-17），计佣层不感知平台差异。字段口径未经 09 表 CAP-TB-04、CAP-JD-04、CAP-PDD-04 验证前，报价一律取可得口径中的较低值。报价使用报价时刻生效的规则版本、查看者等级（未登录用注册默认等级 L1）与调用方传入的 order_type（各展示对象取值见 BR-PRICE-06）。报价不持久化。展示（标签、零值、区间、口径说明文案、金额格式）只按 BR-PRICE-06 / 07 / 08 / 17，本条不规定展示。 | 待验证 | UnionAdapter.&lt;platform>.quoteN()；GET /v1/products/{product_key} 预估返利；Agent rebate_quote 卡片；分享面板预估收益；packages/domain quoteRebate() / splitCommission()；配置 tech_fee_bp[platform]；specs/commission-examples.csv；验收：同输入时展示报价 = 入账预估 |
| BR-CALC-21 | **分账不变量与算例测试**<br>splitCommission() 必须以 fast-check 属性测试断言：每份 ≥ 0；Σ用户份额 ≤ B；平台留存 = B − Σ用户份额；相同输入输出相同；对全程 active 的受益人，多次调整后的份额 = floor(B_final × r)；forfeited 受益人份额恒为 0。specs/commission-examples.csv 必须在 W1 由财务给出 ≥ 20 例并全部作为参数化测试通过。生产每日 01:00 +08:00 校验前一自然日（+08:00）内快照或金额版本有变化的订单：每单 Σ当前应得额 ≤ base_fen；违例时告警，并冻结该订单全部受益人的提现，直至人工解除。 | 已确认 | packages/domain 测试；specs/commission-examples.csv；ledger_invariants.sql；每日 01:00 校验任务；CI 必过检查 |
| BR-CALC-22 | **规则发布与回滚流程**<br>修改 commission_rules 必须：finance 起草（草稿记录 base_version_id）→ 系统校验 BR-CALC-06 完整性与 BR-CALC-07 上限 → 用试算样本生成差异报告 → super 经 step-up 发布 → 在 effective_from 生效。发布接口校验 publisher_id ≠ drafter_id（super 起草的版本也须由另一名 super 发布）；发布时当前最新已发布版本 ≠ base_version_id 则拒绝，须基于新版本重新试算；下调任一比例时 effective_from ≥ 发布时刻 + 24 小时。已发布版本不可编辑；回滚通过发布新版本实现，未生效版本可按 BR-CALC-11 撤销。所有操作写审计日志。 | 默认假设 | /admin/v1 commission-rules 接口（drafter_id、publisher_id、base_version_id）；后台分佣规则页；audit-logs；验收用例 AC-SET-待编号（参考文档编号 AC-MONEY-014，规划/ 未定义） |
| BR-CALC-23 | **入账后调整的记账时点与审批**<br>订单入账后（rebate_status=CREDITED）只在两类事件发生时生成调整，且只对差额 ≠ 0 的受益人生成调整行：(a) 联盟结算额写入或变更（orders.settle_commission_fen 按 BR-FUND-09 更新；对应 04 O8）——差额 &lt; 0 的受益人在该次更新的同一事务内立即记负向 SETTLE_ADJUST，不等审批；差额 > 0 的受益人生成补差候选（写入 BR-FUND-09 的 settle_adjust_batches），由 finance 发起、另一名 finance 或 super（≠ 发起人）step-up 复核后记账，驳回则不记账并保留候选与驳回理由。rebate_status 始终保持 CREDITED；该单正差候选全部处理完（批准或驳回）之前记为补差未完成（对应单一 order_status 的 CREDITED），处理完后对应单一 order_status 的 SETTLED。(b) 部分退款 / 部分维权（BR-FUND-01 R9）与佣金下调（R9b：价保、比价降佣、联盟佣金调整；对应 04 O10）——负向调整自动记账，不需审批：部分退款、部分维权写 CLAWBACK（BR-FUND-08）；R9b 在新 B &lt; booked_base_fen 时同事务写负向 SETTLE_ADJUST（sub_type=PRICE_PROTECT / PRICE_COMPARE / SETTLE_DIFF，uniq_key 见 BR-FUND-01 R9b）；正向差额此时不记账，进 BR-FUND-09 候选，由 (a) 在结算时处理（C-27 (g) 默认处理，待财务确认）。 | 待决策 | settlement 补差任务；settle_adjust_batches 表（BR-FUND-09）与后台发起 / 复核页；BR-FUND-01 R9 / R9b / R10；ledger SETTLE_ADJUST / CLAWBACK；订单详情差额展示 |
| BR-CALC-24 | **分享单的分账**<br>分享单（order_type=share）只按订单归属用户（分享者）分账：分享者份额 = floor(B × r_own_bp / 10000)，r_own_bp 取 BR-CALC-06 中 (platform, 分享者等级, share) 行，入 PROMO 账户；直推份额 = floor(B × r_direct_bp / 10000)，受益人为分享者在 paid_at 时的直接上级，r_direct_bp 取 (platform, 上级等级, share) 行，入 PROMO。实际购买者即使也是本 App 用户，也不产生自购份额（每个子订单只有一个归属用户，见 BR-ATTR）。分享者经自己的分享链接下单时按哪种 buy_type 计算由 BR-ATTR 决定；决定之前这类订单按 self 计算并记入 SELF 账户。 | 待决策 | packages/domain splitCommission()（share 分支）；commission_splits.beneficiaries；ledger SHARE_CREDIT / REFERRAL_CREDIT；分享面板预估收益；orders.buy_type（BR-ATTR） |
| BR-CALC-25 | **联盟未单列补贴类佣金时的处理**<br>某平台订单接口未把补贴类佣金与基础佣金分开返回（BR-CALC-18 无法拆出 subsidy_commission_fen）时，补贴部分是否分给用户由财务决定。决定前：N 整体计入 B，订单照常展示预估，但该平台订单在 settle_commission_fen 为空时不执行 CREDIT_DUE 入账（R5），等联盟结算值到达后再按 BR-CALC-14 入账（入库时置 orders.credit_requires_settle=true，判定同 BR-CALC-15，不使用 hold 字段）；并在 09 表记录该平台'补贴类佣金未单列'。 | 待决策 | 配置 union.&lt;platform>.subsidy_itemized；orders.credit_requires_settle；settlement 入账任务（结算前不入账分支，需并入 BR-FUND-04 入账守卫）；订单详情入账时间文案；规划/09_平台能力验证/（对应 CAP 的结论，按 09 README §0.4 回填） |
| BR-CALC-26 | **联盟报文金额与比例的换算**<br>联盟报文中的元金额必须按十进制字符串解析为分，禁止 parseFloat 与 Number 运算：小数不超过 2 位时精确换算；超过 2 位时按 floor 取整到分，原字符串保存在 raw_payload 供对账。报文字段为 JSON number 时，必须用保留数字原文的 JSON 解析（如 JSON.parse reviver 的 context.source 或 lossless-json）取得字面值字符串再解析，不得先转成 JS number。百分比字符串（如 '20.00' 表示 20%）同样按十进制字符串换算为 bp，超过 2 位小数时 floor；字段单位（百分比还是万分比）以 09 表验证结论为准。转换函数放在 packages/money：yuanStrToFen()、pctStrToBp()；非法格式（空串、非数字、科学计数法无法精确解析）抛错，订单进待处理表，不得按 0 处理。 | 默认假设 | packages/money yuanStrToFen() / pctStrToBp()；UnionAdapter 报文解析；orders.raw_payload；lint 规则（Adapter 目录同样禁止 parseFloat） |
| BR-CALC-27 | **每单四段金额与平台预估利润**<br>每个已生成分佣快照的子订单，必须在快照生成时（BR-CALC-10）以及此后每写入一个 commission_split_amounts 新版本时，在同一事务按该版本落四段金额（整数分）：① 联盟佣金总额 n_total_fen = n_base_fen + subsidy_commission_fen（BR-CALC-03 / BR-CALC-18 输出，已扣技术服务费，可为负）；② 基数前扣除 pre_base_deduct_fen = n_total_fen − base_fen（含补贴类佣金、淘礼金扣除 tlj_deduct_fen、负 N 置 0 的部分；不设平台预留比例，见 BR-CALC-02）；③ 分佣基数 base_fen（B）；④ 平台预估利润 platform_est_profit_fen = n_total_fen − 该版本 Σ用户份额 amount_fen（forfeited 为 0，held 仍计入） − tlj_redpacket_fen。tlj_redpacket_fen = 我方淘礼金订单（pid_scene=taolijin）按 BR-CALC-19 的匹配键在 tlj_grants 中匹配到的红包面额，不论 rebate_mode；union.taobao.tlj_n_net_of_redpacket=true 或非我方淘礼金订单为 0；我方淘礼金订单匹配不到时 tlj_redpacket_fen 与 platform_est_profit_fen 记 null，报表显示'待核'，不得按 0 计算。四段金额只用于毛利报表、经营看板与 R1 对账，不参与分账，不向用户展示。 | 待决策 | commission_split_totals（新增，唯一 (order_id, commission_version)，只追加）；orders 冗余当前版本四段金额；毛利报表与经营看板「平台预估利润」；R1 联盟对账；specs/commission-examples.csv |

### 5.2 细则

#### BR-CALC-01 细则 · 金额与比例的数据类型

- 状态：已确认
- 默认值：无（已确认，按规则执行）
- 决策人：负责人
- 依赖平台能力：无
- 取代：无
- 来源：规划/02_系统架构.md §4.2、§16.3；规划/04_数据模型与契约.md §3.2、§5；返利 App PRD v2.1 §6 基本约定；开发任务拆解_v1 BF-01

- 乘除统一写成 `mulDivFloor(amount_fen, ratio_bp, 10000n)`，先乘后除，禁止先把 bp 转成小数。
- `mulDivFloor` 只接受 amount_fen ≥ 0，负数抛 `InvalidAmount`（BigInt 的 `/` 向零截断，`-101n*5000n/10000n = -50n`，不是 floor 的 -51）；负基数由调用方先按 BR-CALC-02 置为 0 再计算。需要向上取整的场景用 `mulDivCeil`，同样只接受非负数。
- 差额（新应得 − 已入账）只用减法求得，不调用 mulDivFloor。
- 例：B=1234、r=5000 → `1234n*5000n/10000n = 617n`；禁止 `1234*0.5`。
- 边界：_bp 取值为 0–10000 的整数；输入非整数或超界，函数抛 `InvalidRatio`，不得静默截断。
- 序列化：服务端把 bigint 转成 JSON integer，值超过 2^53−1 时抛错并告警，不得静默丢精度。
- 联盟报文中元字符串、百分比字符串的换算见 BR-CALC-26。
- CI 用 lint 规则拦截 packages/domain、apps/api/**/settlement 下的浮点运算。

#### BR-CALC-02 细则 · 分佣基数 B 的定义

- 状态：待决策（原标默认假设；B 的定义属金额口径、决策人为财务，按 README §0.3 应为待决策）
- 默认值：B = N_base（− 淘礼金 normal 模式的红包扣除），不设 reserve_bp；平台留存靠 BR-CALC-07 的 8000 上限保证。理由：沿用规划/01 §3 口径与 06 Q-B1 默认，财务 W1 随 ledger-rules.md 签字确认
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 §2.6 / §0.4 B10：「B = N − floor(N × reserve_bp[platform] / 10000)，预留淘宝 15%、京拼唯 10%、抖音 15%、美团饿了么 2%；约束 r_buyer+r_l1+r_l2 ≤ 10000」
  - 参考_花卷云功能查漏底稿 §2 分佣基数：「实际计算佣金 = 联盟预估佣金 × (1 − 平台预留%)」
  - 返利 App PRD v2.1 §11.3：「净佣金 = 结算佣金 × (1 − 平台技术服务费率)（由我方自行乘费率）」
- 来源：规划/01_需求规划.md §3 分账口径；规划/04_数据模型与契约.md §1 术语表；规划/06_待补信息清单.md Q-B1；PRD修订_后端功能规划 §2.6
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

| 阶段 | N_base 取值 |
|---|---|
| settle_commission_fen 为空（PAID / RECEIVED / 已入账未结算） | 最新联盟预估收入 `est_commission_fen`（扣除补贴类佣金后） |
| settle_commission_fen 非空 | 联盟结算收入 `settle_commission_fen`（扣除补贴类佣金后）；预估字段再变只存档 |

- 结算值本身再变（如结算后维权），按 BR-CALC-15 或 BR-FUND-08（R8，对应 04 O9）处理。
- 例：联盟返回推广者预估收入 14.52 元、无补贴、非淘礼金 → N_base=1452 → B=1452。
- 平台留存靠 BR-CALC-07 的 8000 上限保证（平台至少留 20%），不再单设 reserve_bp。后端功能规划的 reserve 初始值（淘宝 15%、京拼 10%）如财务仍需要，应折算进各平台的 r_own / r_direct 取值，而不是改公式。
- 异常：联盟 N 为负（冲正）→ raw_n_fen 记原值，B=0，各受益人新应得为 0；已入账部分按 BR-CALC-09 求差扣回（流水类型 CLAWBACK / SETTLE_ADJUST 见 BR-FUND-08、BR-FUND-09；B 由 >0 变 0 时入账前走 R6 → VOID、入账后走 R8 → CLAWED_BACK，对应 04 O4 / O9）。负值差额只进 R1 对账，不进分账。
- 后端功能规划与花卷云底稿要求的「四段金额」（含平台预留）按本条的 B 定义改写，见 BR-CALC-27。
- 按 C-01 默认处理（状态名与迁移编号改用 BR-FUND-01），待负责人确认。

#### BR-CALC-03 细则 · 各平台 N 的取数字段

- 状态：待验证
- 默认值：未验证前按'字段已扣技术服务费'开发，用录制回放测试；credit.enabled.&lt;platform>=off（只展示预估，不入账）；验证结果写入 规划/09_平台能力验证/（对应 CAP 的结论，按 09 README §0.4 回填）
- 决策人：财务
- 依赖平台能力：淘宝/京东/拼多多订单接口：推广者预估收入与结算收入字段是否已扣技术服务费、是否有服务费率字段；淘宝专项服务费 2026 现行费率；拼多多佣金字段是否已含账号等级系数与自购折算
- 取代：无
- 来源：规划/06_待补信息清单.md Q-B1 技术服务费口径；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-04、3_JD_京东.md CAP-JD-04、4_PDD_拼多多.md CAP-PDD-04；PRD修订_后端功能规划 §2.2 平台佣金口径差异
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

待验证的字段（接口名与字段名以联盟文档和录制报文为准）：

| 平台 | 候选预估字段 | 候选结算字段 | 待验证点 |
|---|---|---|---|
| taobao | 付款预估收入（如 pub_share_pre_fee） | 结算预估收入（如 pub_share_fee） | 是否已扣技术服务费（alimama_share_fee 为技术服务费金额，待实测）；专项服务费 2026 现行费率；补贴类收入是否单列（subsidy_fee） |
| jd | 预估佣金（如 estimateFee） | 实际佣金（如 actualFee） | 是否已扣技术服务费 |
| pdd | 佣金金额（如 promotion_amount） | 同字段结算后值 | 是否已含账号等级系数、自购 75% 折算 |

- 例（假设未扣费）：gross=1600、fee_bp=1000 → 服务费 ceil(160)=160 → N=1440；gross=1605、fee_bp=1000 → 服务费 ceil(160.5)=161 → N=1444。
- 元转分与百分比转 bp 按 BR-CALC-26，不得 parseFloat。
- 异常：字段缺失或非数字 → 订单进待处理表并告警，不生成快照，不得按 0 处理。
- 逐单核对：每平台至少用 09 表实验中的真实订单，把 Adapter 输出 N 与联盟后台推广者收入对比，偏差 0 分或可逐单解释才算通过。

#### BR-CALC-04 细则 · 分账公式与受益人（通用与自购单）

- 状态：已确认
- 默认值：无（已确认，按规则执行）
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 §2.6：「platform = N − buyer − parent_l1 − parent_l2（含预留）；算例 N=1452 → B=1235 → platform=712」
- 来源：规划/01_需求规划.md §3 分账口径；规划/02_系统架构.md §8.3 典型分录；规划/04_数据模型与契约.md §2.2、§2.4；规划/06_待补信息清单.md Q-B1；PRD修订_后端功能规划 §2.6 账户映射
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

```
own      = floor(B × r_own_bp    / 10000)   // 受益人 = 订单归属用户
direct   = floor(B × r_direct_bp / 10000)   // 受益人 = 归属用户 paid_at 时的上级
platform = B − own − direct                 // ≥ 0 由 BR-CALC-07 保证
```

| 例 | B | 类型 | 比例 | 本人 | 直推 | 平台 |
|---|---|---|---|---|---|---|
| 1 | 1234 | self | 5000/1000 | 617 → SELF | 123 → PROMO | 494 |
| 2 | 1234 | self，无上级 | 5000/— | 617 | 0 | 617 |
| 3 | 1 | self | 5000/1000 | 0 | 0 | 1 |

- 分享单算例见 BR-CALC-24。
- 角色枚举：`self`、`share`、`direct`；MVP 不写 `indirect`（见 BR-CALC-05）。
- 流水类型：self → REBATE_CREDIT；share → SHARE_CREDIT；direct → REFERRAL_CREDIT（见 BR-FUND）。所得类型与税目见 BR-FUND。
- BR-ATTR 定稿前 buy_type 默认：订单能识别出购买者就是归属用户本人（同一 relation_id / special_id）→ self，否则 → share。

#### BR-CALC-05 细则 · 间推比例固定为 0

- 状态：默认假设
- 默认值：间推 = 0 且后台不可开启（D8 默认决策，理由：两层计酬不在监管安全港内）
- 决策人：法务
- 依赖平台能力：无
- 取代：
  - 返利 App PRD v2.1 §11.3：「间推 = floor(净佣金 × 间推比例)，MVP 默认 0（可配）」
  - PRD修订_后端功能规划 §2.6：「parent_l2 = 0 写入公式与 beneficiaries」
- 来源：规划/00_总览与决策.md D8；规划/01_需求规划.md §3；规划/06_待补信息清单.md Q-B1；PRD修订_后端功能规划 §0.4 B6、§2.10

- 例：A 邀请 B、B 邀请 C，C 自购 B=1000 → C 500、B 100、A 0、平台 400。
- 迁移尝试把 r_indirect_bp 改为非 0 → CHECK 失败，发布被拒（验收用例）。
- 等级 L1–L3 晋升只看本人推广订单，不看下级人数（见 BR-INV 或 01 F-SET）。

#### BR-CALC-06 细则 · 比例配置维度与默认值

- 状态：待决策
- 默认值：所有平台、所有等级、两种订单类型：r_own 5000、r_direct 1000；理由：沿用 规划/06 Q-B1 默认，平台留存 40%，满足 BR-CALC-07，且单位经济模型（01 §8.3）尚未定稿
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 §2.10：「r_buyer 按等级、平台配置，r_l1 不分平台与订单类型」
- 来源：规划/01_需求规划.md §3、§8.3；规划/06_待补信息清单.md Q-B1；返利 App PRD v2.1 §19.1 D5、§19.2 G1；PRD修订_后端功能规划 §12.1 B11
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

默认种子数据（W1 财务签字前按此开发与测试），commission.platforms = [taobao, jd, pdd]：

| platform | level | order_type | r_own_bp | r_direct_bp |
|---|---|---|---|---|
| taobao / jd / pdd | L1、L2、L3 | self | 5000 | 1000 |
| taobao / jd / pdd | L1、L2、L3 | share | 5000 | 1000 |

- 同一版本内 3 平台 × 3 等级 × 2 类型 = 18 行必须齐全。
- 例：(pdd, L2, self) 订单，归属用户 L2 → r_own 取 (pdd, L2, self).r_own_bp=5000；上级 L1 → r_direct 取 (pdd, L1, self).r_direct_bp=1000。
- 美团（W7）接入前先把 meituan 加入 commission.platforms，并补齐 6 行，否则新版本发布被拒。

#### BR-CALC-07 细则 · 比例合计上限校验

- 状态：待决策（原标默认假设；上限决定平台最低留存，属金额口径、决策人为财务，与 BR-CALC-08 同理按 README §0.3 改为待决策）
- 默认值：每个 (平台, 订单类型)：max_等级(r_own) + max_等级(r_direct) + 活动加成 ≤ 8000，单项 0–8000（06 Q-B1 默认；W1 随 ledger-rules.md 由财务签字）
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 §2.6：「约束 r_buyer_bp + r_l1_bp + r_l2_bp ≤ 10000」
  - 返利 App PRD v2.1 §11.3：「约束 返利 + 分佣 ≤ 净佣金」
- 来源：规划/01_需求规划.md §3；规划/06_待补信息清单.md Q-B1；PRD修订_后端功能规划 §1.6、§10.1 AC-MONEY-014
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 用最大值相加是因为本人与上级可能处于不同等级。
- 例：taobao/self 下 L3 r_own=6500、L2 r_direct=1500 → 8000，通过；把 5000 误填为 50000 → 单项 > 8000，拒绝（对应后端功能规划 AC-MONEY-014；规划/ 中的 AC-SET 编号待 规划/05 分配）。
- 活动加成在 MVP 恒为 0（奖励活动 P1），P1 加入时计入同一上限。
- 由此平台留存 ≥ B × 20%（舍入尾差另计归平台）。

#### BR-CALC-08 细则 · 舍入与尾差归属

- 状态：待决策（原标默认假设；舍入方向与尾差归属属金额口径、决策人为财务，按 README §0.3 应为待决策）
- 默认值：每份 floor，尾差归平台（06 Q-B1 默认；W1 随 ledger-rules.md 由财务签字）
- 决策人：财务
- 依赖平台能力：无
- 取代：无
- 来源：规划/01_需求规划.md §3；规划/02_系统架构.md §8.3；规划/06_待补信息清单.md Q-B1；返利 App PRD v2.1 §6；开发任务拆解_v1 BF-01
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：B=1235、5000/1000 → 617.5→617、123.5→123、平台 495。
- 例：B=9、5000/1000 → 4、0、5。
- 手续费向上取整属于提现，见 BR-FUND；技术服务费扣除向上取整见 BR-CALC-03。
- 性质：Σ用户份额 ≤ B；每份 ≥ 0；平台留存 ≥ 0。

#### BR-CALC-09 细则 · 调整按新基数全额重算

- 状态：待决策（原标默认假设；调整算法与正差归属属金额口径、决策人为财务，按 README §0.3 应为待决策）
- 默认值：全额重算求差；forfeited 恒为 0；封禁或注销后正差归平台（理由：多次调整后每份仍等于 floor(B_final × r)，与对账口径一致；不向已剥夺份额的受益人补发）
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - 规划/02_系统架构.md §8.3：「月结补差（结算额比已入账少 100）：按快照比例拆分，借用户与平台收入」
- 来源：规划/02_系统架构.md §8.3；PRD修订_后端功能规划 §2.7 入账金额、失效与扣回（金额 = 已入账 − 新应得）
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：已入账 B=1235 → 本人 617、直推 123。结算 B_new=1134 → 本人 floor(567)=567、直推 floor(113.4)=113；调整 −50、−10，平台留存由 495 变为 454。
- 错误做法：ΔB=−101，floor(−101×0.5)=−51、floor(−101×0.1)=−11，与全额重算相差 1 分，多次调整后会累积。
- 例（forfeited）：上级快照时已注销（直推 forfeited，0），结算上调 B 1234→1500 → 本人 617→750（+133），直推不生成调整，平台 617→750。
- 例（入账后被封禁）：本人已入账 617，结算上调到 B=1500，本人 risk_state=banned → 应得 750 的正差 133 归平台，本人不补。
- 只对差额 ≠ 0 的受益人生成调整行。何时记账、是否审批见 BR-CALC-23。
- 同一受益人累计扣回不得超过已入账额（BR-FUND-19 不变量 ④）。

#### BR-CALC-10 细则 · 分佣快照生成时点与不可变范围

- 状态：默认假设
- 默认值：按'platform_status 首次处于 PAID 及之后且已归因'生成（理由：消解 02 §5.2'首次入库'与 04 O2'PLATFORM_PAID'的冲突，并覆盖预售与找回）
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 规划/01_需求规划.md §3、规划/02_系统架构.md §5.2：「订单首次入库时写分佣快照」
  - 规划/04_数据模型与契约.md §3.2：「commission_splits 首次入库时生成，不可修改（未含 account_type、状态、平台留存）」
  - 规划/04_数据模型与契约.md §4.1 O2：「PLATFORM_PAID → PAID，副作用：生成分佣快照（无'已归因'条件）」
  - PRD修订_后端功能规划 §2.5 第 6 步：「订单首次入库且已归因时写快照并落四段金额（N、预留、B、平台利润）」
- 来源：规划/01_需求规划.md §3；规划/02_系统架构.md §5.2；规划/04_数据模型与契约.md §3.2、§4.1 O1/O2/O11；PRD修订_后端功能规划 §2.5、§3.1
- 需同步修改的规划文档：5 处（计数仅作记录，落点见 README §0.6）

| 场景（platform_status / rebate_status） | 快照时点 |
|---|---|
| 首次入库即 PAID 且已归因 | 首次入库事务（R2，对应 04 O2） |
| 预售：先 DEPOSIT_PAID（已归因，rebate_status=ESTIMATED，预估 0），后付尾款 | platform_status 迁到 PAID 的事务（P2，对应 04 O2），定金阶段无快照 |
| 回扫晚到，首次入库已是 RECEIVED / SETTLED 且已归因 | 首次入库事务（R2，同事务按 R4 进 WAITING） |
| 首次入库未归因（UNATTRIBUTED） | 找回通过 / 后台改归属时（R3，对应 04 O11）；platform_status 仍为 DEPOSIT_PAID 时推迟到 P2 |
| 未归因且已 VOID（对应 04 INVALID），找回通过或改派 | R3b：只写 user_id、user_basis、locked=true，不生成快照，rebate_status 保持 VOID；订单详情显示失效原因 |
| 首次入库即失效（platform_status=INVALID） | 不生成 |

存储：
- `commission_splits`（唯一 order_id = orders.id，只写一次）：rule_version_id、order_type、activity_type、rebate_mode（none/normal，非淘礼金为 null）、paid_at、paid_at_source、raw_n_fen、subsidy_commission_fen、tlj_deduct_fen、base_fen、platform_retain_fen（生成时值）、beneficiaries[user_id, role, account_type, ratio_bp, level, initial_status, forfeit_reason]、created_at。
- `commission_split_amounts(order_id, commission_version, user_id, role, base_fen, amount_fen, created_at)`：唯一 (order_id, commission_version, user_id, role)，只追加不更新；快照生成时写 commission_version=1 的行；当前应得额取最大 commission_version 的行；该版本平台留存 = base_fen − Σamount_fen。
- `commission_split_beneficiary_events(order_id, user_id, role, status ∈ {active, held, forfeited}, reason, created_at)`：只追加；当前状态取最后一条。
- 重放同一订单事件不得重建快照（唯一约束 order_id）。
- 四段金额与平台预估利润随快照与每个金额版本落库，见 BR-CALC-27。
- 「VOID 订单找回通过只设 user_id」这一动作不改变 rebate_status，对应 BR-FUND-01 R3b（找回通过或改派：rebate_status 保持 VOID，只写 user_id、user_basis、locked=true，不生成快照、无分录；C-27 (c)）。
- BR-ATTR-01（DEPOSIT_PAID 也生成快照、关系与等级取生成时刻）与 BR-FUND-01 R3（比例与用户关系取批准时刻）中与本条、BR-CALC-11、BR-CALC-12 不一致的写法，以本主题为准。
- 按 C-01、C-06 默认处理（状态名改用 BR-FUND-01；生成时点按本条），待负责人确认。

#### BR-CALC-11 细则 · 规则版本生效时点

- 状态：默认假设
- 默认值：按 paid_at 选版本；effective_from 严格递增；未生效版本可撤销；预售尾款时间拿不到时按 platform_modified → observed 降级（理由：与入库延迟、回扫时机无关，可重放；与后端功能规划 F-69 一致）
- 决策人：财务
- 依赖平台能力：淘宝/京东/拼多多订单接口：预售单尾款付清时间字段是否提供（09 表订单同步项，如 CAP-TB-07）
- 取代：
  - 返利 App PRD v2.1 §11.3：「比例按下单时刻的规则版本快照计算」
  - 规划/01_需求规划.md §3：「订单首次入库时把规则版本写入快照（未定义按哪个时间选版本）」
- 来源：规划/01_需求规划.md §3；规划/04_数据模型与契约.md §11；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-07；PRD修订_后端功能规划 §2.6 快照、§2.10、§1.6
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

- 例：v2 effective_from 2026-10-01T00:00:00+08:00，v3 effective_from 2026-11-01T00:00:00+08:00。paid_at 2026-10-31T23:59:59+08:00 → v2；paid_at 2026-11-01T00:00:00+08:00 → v3。
- 例：v3（11-01 生效）已发布未生效，再发布 v4 effective_from 10-25 → 拒绝；须先撤销 v3，或把 v4 设在 11-01 之后。
- 例：预售定金 10-21 付、尾款 11-11T00:05+08:00 付 → 用 11-11 时有效的版本。
- 预售 paid_at 取值顺序：① 订单接口的尾款付清时间字段（paid_at_source=platform）；② 付款时间字段仍为定金时间时，取我方首次收到的、使 platform_status 迁到 PAID（BR-FUND-01 P2，对应 04 PLATFORM_PAID）的那条数据 raw_payload 中的平台更新时间，如淘宝 modified_time（paid_at_source=platform_modified）；③ 以上都没有，取本系统首次观测到该子订单 platform_status 进入 PAID 的时间（paid_at_source=observed）。取定后写入快照，重放不重算。
- 回扫晚到的订单仍按 paid_at 选版本，结果与入库时间无关，保证重放幂等。
- paid_at 早于第一个版本 → 用第一个版本并告警。
- 找回、改派订单（R3）同样按 paid_at 选版本；BR-FUND-01 R3「比例取批准时刻」以本条为准。按 C-01、C-06 默认处理，待负责人确认。

#### BR-CALC-12 细则 · 等级与上级的取值时点

- 状态：默认假设
- 默认值：等级与上级都按 paid_at 取值；日志缺失按 L1（理由：与 PRD'等级变更以付款时间为准'一致，结果不受入库或找回延迟影响；缺日志时取当前等级可能多付且不可重放）。备选：上级按快照时 parent_id（找回单按找回时的上级计），需负责人拍板才改
- 决策人：负责人
- 依赖平台能力：无
- 取代：无
- 来源：返利 App PRD v2.1 §11.3；规划/04_数据模型与契约.md §3.2 users.parent_id；PRD修订_后端功能规划 §2.10 等级、后台改上级
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 例：用户 10-20T10:00+08:00 由 L1 升 L2；订单 paid_at 10-20T09:59 于 10:03 入库 → 按 L1；paid_at 恰为 10:00:00 → 按 L2。
- 例：用户 10-05 付款，10-12 才绑定邀请码，订单 10-20 经找回生成快照 → 直推 0，新上级不因旧订单获益。
- 上级在快照后被改绑（后台改上级仅限无订单用户）不影响已生成快照。
- 游客报价按注册默认等级（见 BR-CALC-20）。
- 找回、改派订单（BR-FUND-01 R3）的等级与上级同样取 paid_at 时刻，不取批准时刻或快照生成时刻；BR-INV-13「排除 paid_at 早于绑定的订单」与本条一致。按 C-06 默认处理，待负责人确认。

#### BR-CALC-13 细则 · 受益人失效时份额归平台

- 状态：默认假设
- 默认值：快照时只剥夺已注销或不存在的受益人；入账时 banned / 已注销 → forfeited，frozen / appealing → hold，冷静期照常（理由：永久失效才剥夺，临时风控状态只延后，避免事后证明无辜的用户永久失去返利；先入账后封禁无法扣回，所以冻结期间不入账）
- 决策人：负责人
- 依赖平台能力：无
- 取代：无
- 来源：规划/01_需求规划.md E10 F-SET-03；规划/04_数据模型与契约.md §2.3 BLACKLIST、§2.5 risk_state / deletion_status、§4.1 O4；PRD修订_后端功能规划 §2.6 受益人失效
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 例：B=1234、r=5000/1000，快照时上级已注销 → 本人 617、直推 forfeited 0、平台 617。
- 例：入账日本人 risk_state=banned → 本人 617 forfeited，平台 494+617=1111；直推 123 正常入账。
- 例：入账日本人 risk_state=frozen → 本人 617 held（仍在待结算），直推 123 入账；3 天后恢复 normal → 补入账 617；若申诉失败转 banned → forfeited，平台 +617。
- 若风控流程允许 banned 事后解除，已 forfeited 的份额只能经 ADMIN_ADJUST 人工补发（见 BR-FUND），系统不自动补。
- 状态变化写 commission_split_beneficiary_events（BR-CALC-10）。
- 规划 01 F-SET-03 已确认'归平台、不顺延'，本条新增判定时点与 hold。
- held 解除后按 BR-FUND-01 R5a 入账：订单已 CREDITED 时，在 hold 解除后的下一次 00:05 入账任务为该受益人单独入账，uniq_key 沿用 {order_key}:{uid}:{role}:CREDIT（只入一次）；转 forfeited 时份额记平台（{order_key}:PLATFORM:FORFEIT:{uid}:{role}）；BR-FUND-04 改为「除 held 受益人外同时入账」。按 C-27 (d) 默认处理，待财务确认。
- 按 C-01 默认处理（订单级失效改用 BR-FUND-01 状态名），待负责人确认。

#### BR-CALC-14 细则 · 入账时的基数取值

- 状态：已确认
- 默认值：无（已确认，按规则执行）
- 决策人：财务
- 依赖平台能力：无
- 取代：无
- 来源：规划/04_数据模型与契约.md §2.3、§4.1 O6/O7/O8；规划/02_系统架构.md §8.3；PRD修订_后端功能规划 §2.7 入账金额、月结补差
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：快照时 N=1234（617/123），收货前联盟预估更新为 1300 → 入账 650/130，平台 520。
- 例：入账基数 1300，次月结算 1200 → 本人 600、直推 120；调整 −50、−10，平台 −40 → 480（记账方式见 BR-CALC-23）。
- 结算额 = 已入账基数 → 不生成调整。
- 订单详情'实返与预估差额'只使用上述 4 个原因码。
- 入账守卫（等待期、hold、rights_pending、日结门槛、开关）见 BR-FUND-04；orders.credit_requires_settle=true 且 settle_commission_fen 为空的订单不入账（BR-CALC-15、BR-CALC-25）。
- 按 C-01 默认处理（O6/O7 改写为 R5 与 settle_commission_fen 非空），待负责人确认。

#### BR-CALC-15 细则 · 部分退款与价保重算

- 状态：待验证
- 默认值：以联盟更新后的佣金为准；partial_refund_updates_commission 默认 true；平台不更新时按件退款用数量比例 floor 估算，按金额退款或价保暂停入账等结算
- 决策人：财务
- 依赖平台能力：淘宝/京东/拼多多：部分退款、价保后订单接口是否返回更新后的佣金，是否提供退款数量或退款金额字段
- 取代：
  - 返利 App PRD v2.1 §9.3：「维权成功（部分）按比例调整结算基数（未说明按数量还是金额）」
- 来源：规划/04_数据模型与契约.md §2.3、§4.1 O5/O10；PRD修订_后端功能规划 §3.1、§3.2；返利 App PRD v2.1 §9.3
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 例：quantity=3，N=900，已入账 450/90。退 1 件，联盟 N_new=600 → 应得 300/60，写 CLAWBACK（sub_type=PART_REFUND）−150、−30，平台 360→240。
- 例（按件估算）：N=1000、quantity=3、退 1 → floor(1000×2/3)=666。
- 例（按金额退款、平台不更新佣金，rebate_status=WAITING）：数量不变，原 N=1000 → credit_requires_settle=true，到期不入账，订单详情显示'部分退款，返利待联盟结算后确认'（文案以 BR-TEXT 为准）；结算值 800 到达 → 下一次入账任务按 B=800 入账。
- credit_requires_settle 一经置 true 不回退；settle_commission_fen 非空后该守卫自然失效。入账守卫见 BR-FUND-04（已并入 credit_requires_settle 守卫；跳过期间 display_status=WAITING_SETTLE，不显示预计日期）。按 C-27 (e) 默认处理，待财务确认。
- commission_split_amounts 的幂等键 (order_id, commission_version, user_id, role)，order_id 为 orders 表内部主键（不用平台原始 sub_order_id，避免跨平台重号）；扣回凭证 uniq_key 见 BR-FUND-08。
- 京东实际佣金变 0 的判失效规则见 BR-FUND-08。
- 部分退款流水类型按 C-16 默认处理（CLAWBACK sub_type=PART_REFUND，不再写负向 SETTLE_ADJUST），状态名按 C-01 默认处理，待财务、负责人确认。

#### BR-CALC-16 细则 · 比价订单的计算与展示

- 状态：待验证
- 默认值：订单侧按联盟 N 计算；下单前展示见 BR-PRICE-07（按 C-22 默认处理，待负责人确认，财务知悉）
- 决策人：财务
- 依赖平台能力：淘宝联盟：比价订单判定口径（06 Q-G2）；biz_scene_id=2 时 commission_rate 返回比价后佣金率还是区间、是否仍有 min/max 字段；订单接口 flow_source 等比价标识（CAP-TB-04）
- 取代：
  - 本条原写法（按 C-22 删除）：「下单前报价按 biz_scene_id=2 预判或 min/max 字段展示区间 [floor(N_min×r), floor(N_max×r)]；取不到时展示保守值 floor(N_min × r)；都取不到时不展示金额，只展示'返利以实际结算为准'」
- 来源：规划/01_需求规划.md E09 F-ORD-11、F-PROD-05；规划/06_待补信息清单.md Q-B1、Q-D2、Q-G2；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-04；返利 App PRD v2.1 §11.3；PRD修订_后端功能规划 §2.5、§3.2
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 下单前商品卡与详情的比价区间算例见 BR-PRICE-07 细则（金额格式按 BR-TEXT-10，如「预估返 ¥1.5–¥5 · 以结算为准」）。
- 例：订单同步到 is_price_compare=true、N=300 → 订单列表、订单详情、入账流水三处均显示 150（验收：至少 1 笔比价订单三处一致）。
- 何种场景构成比价（粘贴链接、Agent 推荐后转链）、flow_source 字段含义待联盟 06 Q-G2 答复。
- 报价展示文案与价格口径见 BR-PRICE。
- 与 BR-PRICE-07 的分歧按 C-22 默认处理，待负责人确认（财务知悉）：下单前卡片与详情的比价风险返利展示只按 BR-PRICE-07——区间 [按 rebate.taobao.compare_rate_ratio_bp 折算的下限, 正常佣金率上限]，不另显示保守值，也不改为「不展示金额」；展示字段 rebate_min_fen / rebate_max_fen 由价格主题维护。本条只约束订单侧计算（以联盟已降佣的 N 分账、订单三处一致、差额原因 PRICE_COMPARE）。
- compare_rate_ratio_bp=5000 为占位值：CAP-TB-04 实测与 06 Q-D2 数据到位前，只能在 App 内以「预估返 ¥a–¥b · 以结算为准」展示，不得用于运营素材、客服承诺或对外宣传（C-22）。
#### BR-CALC-17 细则 · 自购与分享报价口径（三平台）

- 状态：待验证
- 默认值：拼多多报价自购系数 7500、账号等级系数 10000；淘宝缺某口径时取较低值；京东按非 PLUS 口径加提示；订单侧不折算
- 决策人：财务
- 依赖平台能力：拼多多：自购类订单是否按分享口径 75% 计佣、商品接口佣金率是哪种口径、订单 promotion_amount 是否已含账号等级系数与自购折算（CAP-PDD-04）；淘宝：promotion_type=1/2 佣金差异及新 App 是否可用 promotion_type=2（CAP-TB-04）；京东：PLUS 佣金口径（CAP-JD-04）
- 取代：
  - 参考_花卷云功能查漏底稿 §2、§16 #7/#8：「拼多多自购统一按 75% 分佣；账号等级 V0×80%、V1×90% 影响可分佣金额（作为事实陈述）」
- 来源：规划/01_需求规划.md §3；规划/06_待补信息清单.md Q-B1；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-04、3_JD_京东.md CAP-JD-04、4_PDD_拼多多.md CAP-PDD-04；PRD修订_后端功能规划 §2.2；参考_花卷云功能查漏底稿 §2、§3
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 配置：`union.pdd.self_buy_factor_bp` 默认 7500（来源为花卷云底稿，待核实）；`union.pdd.account_level_factor_bp` 默认 10000（待核实，V0 可能为 8000）。
- 例（拼多多）：分享口径佣金 400，因子 7500 × 10000 → 自购 N=floor(400×75000000/100000000)=300 → 本人预估 150；分享 N=400 → 分享者预估 200。
- 例（因子均非 10000）：佣金 333、7500 × 8000 → floor(333×60000000/100000000)=floor(199.8)=199（分步 floor 会得 floor(floor(249.75)×0.8)=199，本例相同，但规则只允许一次 floor）。
- 订单侧：联盟返回 promotion_amount=300 → N=300，不再折算。
- 规划/01 §3 把'拼多多官方对自购类按 75%'写成事实，应标为待核实。

#### BR-CALC-18 细则 · 平台补贴与补贴类佣金

- 状态：待验证
- 默认值：补贴类收入单列时拆出 subsidy_commission_fen，不计入 B
- 决策人：财务
- 依赖平台能力：淘宝/京东/拼多多订单接口是否把补贴类佣金与基础佣金分字段返回，或以总额 + 明细返回；淘宝补贴类佣金是否只在分享场景产生
- 取代：
  - PRD修订_后端功能规划 §2.6 活动单：「活动单（淘礼金、补贴等）不计入 B，返利按活动配置（默认不返）」
- 来源：规划/01_需求规划.md §3；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-04；PRD修订_后端功能规划 §2.2、§2.6；参考_花卷云功能查漏底稿 §2
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：淘宝分享单基础收入 800 + 补贴类收入 200 → n_base_fen=800、subsidy_commission_fen=200 → B=800 → 分享者 400、直推 80，平台 320+200=520。
- 例（总额 + 明细）：联盟总额 1000、补贴明细 200 → n_base_fen=800。
- 自购报价：同商品自购场景 N=800 → 本人预估 400（不展示 200 的补贴部分）。
- activity_type=subsidy 的订单仍按基础佣金返（不再默认'不返'）。

#### BR-CALC-19 细则 · 我方淘礼金订单的返利

- 状态：待决策
- 默认值：rebate_mode=none：自购返利 0、直推 0（理由：红包已从佣金出，D7 要求可砍且消耗我方预算；避免叠加导致单笔亏损）；tlj_n_net_of_redpacket=false
- 决策人：财务
- 依赖平台能力：淘宝：淘礼金订单的推广者收入字段是否已扣除红包面额
- 取代：
  - 规划/04_数据模型与契约.md §2.2：「taolijin → 自购返利（淘礼金商品默认不叠加返利，未定义不叠加是返 0 还是扣面额）」
  - 规划/01 §3、PRD v2.1 §10.6、修订① §3.6：「淘礼金商品默认不叠加自购返利（只提自购，未提直推）」
- 来源：规划/01_需求规划.md §3、E08 F-TLJ-04；规划/04_数据模型与契约.md §2.2；规划/06_待补信息清单.md Q-B1；PRD修订_双品牌与Agent找货 §3.6；PRD修订_后端功能规划 §2.6
- 需同步修改的规划文档：4 处（计数仅作记录，落点见 README §0.6）

- 默认例：N=500、红包 300 → 本人 0、直推 0、平台 500（红包 300 已从预算付出，净 200）。
- normal 例（tlj_n_net_of_redpacket=false）：N=500、红包 300 → B=200 → 本人 100、直推 20、平台 80。
- normal 例（tlj_n_net_of_redpacket=true）：N=200（联盟已扣）→ tlj_deduct_fen=0 → B=200。
- rebate_mode 与 tlj_deduct_fen 随快照冻结（BR-CALC-10）；商品池改配置不影响已生成快照。

#### BR-CALC-20 细则 · 报价预估与计算函数一致

- 状态：待验证
- 默认值：游客按 L1、卡片按 self 口径报价；口径未验证前取可得口径中的较低值
- 决策人：负责人
- 依赖平台能力：各平台技术服务费率 tech_fee_bp[platform]（待核实）；三家商品接口佣金率字段是否已扣技术服务费、是否含补贴类佣金；淘宝 promotion_type=1/2、京东 PLUS、拼多多自购的报价口径差异（CAP-TB-04、CAP-JD-04、CAP-PDD-04）
- 取代：无
- 来源：PRD修订_后端功能规划 §2.6 一个函数三处用；参考_花卷云功能查漏底稿 §2 游客佣金展示；规划/04_数据模型与契约.md §5 rebate_quote；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-04、3_JD_京东.md CAP-JD-04、4_PDD_拼多多.md CAP-PDD-04

**公式**（规划/01 §3 分账口径；D8 见规划/00 §3.2）：
```
gross   = floor(final_price_fen × rate_bp / 10000)
fee     = floor(gross × tech_fee_bp[platform] / 10000)
N_quote = gross − fee
B_quote = N_quote                              // 是否扣 reserve_bp 以 BR-CALC-02 为准（当前不扣）
本人份额 = floor(B_quote × r_own_bp / 10000)   // r_own_bp 取 commission_rules[platform][level][order_type]（BR-CALC-06；别名 r_self_bp，C-29）
```
- tech_fee_bp[platform] 为配置项，取值待核实；若 CAP-TB-04 / CAP-JD-04 / CAP-PDD-04 实测佣金率字段已扣技术服务费，该平台 tech_fee_bp 配 0，不得重复扣。
- **例**（参数只作示意；淘宝技术服务费率待核实）：final_price_fen=2990，rate 2000bp，tech_fee_bp 1000 → gross=598 → fee=floor(598×1000/10000)=59 → N_quote=539 → B_quote=539 → r_own_bp 5000 → floor(539×5000/10000)=269。
- **备选口径（仅供 BR-CALC-02 决策对比，不实现）**：B = N − floor(N × 1500/10000) = 539 − 80 = 459 → floor(459×5000/10000)=229。两种口径同输入差 40 分。
- 例：游客看 N_quote=1000 的淘宝商品 → 按 L1 self 5000 → 本人份额 500；登录 L2 用户同商品若 r_own=5500 → 550。
- 例：报价时 v2（5000），用户在 v3（4500）生效后付款 → 快照按 v3，订单预估 450；报价 500 不持久化、不参与订单侧任何计算。
- 例：B 很小导致本人份额 0，或淘礼金默认模式（BR-CALC-19）→ 本条输出 0；展示按 BR-PRICE-08。
- 金额展示格式、零值、比价区间与口径说明文案只按 BR-PRICE-06 / 07 / 08 / 17（金额格式 BR-TEXT-10）；比价订单的订单侧计算见 BR-CALC-16；三平台自购 / 分享口径见 BR-CALC-17。
- 价格口径、取价时间见 BR-PRICE；AI 金额必须来自该函数输出，见 BR-AI。

#### BR-CALC-21 细则 · 分账不变量与算例测试

- 状态：已确认
- 默认值：无（已确认，按规则执行）
- 决策人：财务
- 依赖平台能力：无
- 取代：无
- 来源：规划/02_系统架构.md §8.4；返利 App PRD v2.1 §11.3；PRD修订_后端功能规划 §2.6；开发任务拆解_v1 BF-03、C-08

csv 至少覆盖：B=1234 自购（617/123/494）、B=2000 分享（1000/200/800）、B=1、B=0、N 为负、无上级、上级注销（forfeited）、入账时本人 banned、入账时本人 frozen（held）、淘礼金默认、淘礼金 normal、部分退款（按件 / 按金额）、结算下调、结算上调、比价订单、预售、跨版本边界（paid_at = effective_from）、跨等级边界、拼多多自购报价。
- 同一 (order_id, 受益人, 角色) 首次入账最多 1 次（BR-FUND-19 不变量 ③）。
- csv 另需覆盖 BR-CALC-27 四段金额算例（普通、补贴、淘礼金 none / normal、负 N）。
- 「冻结该订单全部受益人的提现」的记录方式按 C-09 默认处理：写 withdraw_holds（reason=ledger_mismatch，BR-WDR-05、BR-FUND-19），提现申请按其错误码返回，待财务确认。reason 取值按 C-20 统一（后台显示名 LEDGER_MISMATCH；withdraw_holds 定义只在 BR-WDR-05）。

#### BR-CALC-22 细则 · 规则发布与回滚流程

- 状态：默认假设
- 默认值：沿用后端功能规划 §1.6 流程，并加发起人 ≠ 发布人、基准版本校验、下调提前 24 小时（理由：防止比例误配造成资损，减少用户刚看到的报价立即失效引发的纠纷）
- 决策人：财务
- 依赖平台能力：无
- 取代：无
- 来源：规划/04_数据模型与契约.md §11；PRD修订_后端功能规划 §1.6 资金配置、§2.10、§10.1 AC-MONEY-014
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 试算样本 = paid_at ∈ [发布申请时刻 − 7 天, 发布申请时刻) 且已生成快照的订单；报告对比现行版本与草稿的本人份额、直推份额、平台留存合计。
- 例：财务把 taobao/L1/self 从 5000 改为 4500，试算报告显示近 7 天 1,000 单本人份额合计下降约 10%，附在审批单；另一名 super 发布，发布时刻 2026-10-30T10:00+08:00，effective_from=2026-11-01T00:00:00+08:00（满足 ≥ +24 小时）。
- effective_from 早于发布时刻 → 拒绝（禁止回溯）。
- 试算报告生成失败 → 不允许发布。

#### BR-CALC-23 细则 · 入账后调整的记账时点与审批

- 状态：待决策
- 默认值：负差（扣回方向）即时记账，正差进批次等财务批准（理由：负差延迟期间用户可能把这部分钱提现走，之后只能形成负余额或坏账；正差延迟不产生资损）
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - 规划/04_数据模型与契约.md §4.1 O8：「CREDITED → SETTLED，结算额 ≠ 已入账额时写 SETTLE_ADJUST（自动记账，无审批）」
  - PRD修订_后端功能规划 §0.4 B8、§2.7 月结补差：「结算补差生成候选，经财务批准后记账（不区分正负）」
- 来源：规划/02_系统架构.md §8.3；规划/04_数据模型与契约.md §4.1 O8/O10；PRD修订_后端功能规划 §0.4 B8、§2.7
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

- 例：入账 650/130，结算 B=1200 写入 settle_commission_fen → 应得 600/120，差额 −50/−10 → 同一事务立即记负向 SETTLE_ADJUST，补差完成（rebate_status 保持 CREDITED，对应单一 order_status 的 SETTLED）。
- 例：入账 600/120，结算 B=1300 → 应得 650/130，差额 +50/+10 → 生成 2 行候选，补差未完成；finance 发起、另一名 finance 或 super 复核后记账，补差完成。
- 例：入账基数 1300（650/130），尚未结算，联盟预估佣金调整为 1250（R9b，sub_type=SETTLE_DIFF）→ 应得 625/125，同事务立即记负向 SETTLE_ADJUST −25、−5（C-27 (g)，待财务确认；原写法「单纯预估字段变化不生成调整、等结算」已取代）。预估上调则不记账，进 BR-FUND-09 候选。
- 例：入账 600/120，平台回传价保，联盟新佣金 1100 → 应得 550/110，立即记负向 SETTLE_ADJUST（sub_type=PRICE_PROTECT）−50、−10。
- 受益人为 forfeited / banned / frozen 时的处理见 BR-CALC-09。
- 补差候选表统一用 BR-FUND-09 的 settle_adjust_batches（原写 settle_adjustments，02 settlement 模块用名以资金主题为准）。
- 与 BR-FUND-01 R9b、BR-FUND-08、BR-FUND-09 的差异：资金主题把价保列为 R9b「无分录、只由月结补差处理」，且所有补差都经双人复核。按 C-07 默认处理，负差（含价保负差）即时记账、双人复核只用于正差；R9b 已按 C-27 (g) 改为新 B &lt; booked_base_fen 时同事务写负向 SETTLE_ADJUST（sub_type PRICE_PROTECT / PRICE_COMPARE / SETTLE_DIFF），uniq_key 见 BR-FUND-01 R9b（{order_key}:{uid}:{role}:ADJ:{sub_type}:v{commission_version}，平台侧 {order_key}:PLATFORM:ADJ:{sub_type}:v{commission_version}），正差仍进 BR-FUND-09 候选；C-27 (g) 默认处理，待财务确认。
- 按 C-01、C-07 默认处理，待负责人、财务确认。

#### BR-CALC-24 细则 · 分享单的分账

- 状态：待决策（原标默认假设；分享单比例与「经自己分享链接下单按 self 还是 share」涉及金额口径与订单归属，按 README §0.3 应为待决策）
- 默认值：沿用 06 Q-B1 分享收益 5000；直推按一层计给分享者上级（D8 默认）；分享者经自己链接自购按 self 记 SELF
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 规划/01_需求规划.md §3：「分享单给分享者的份额公式与直推受益人未写」
- 来源：规划/00_总览与决策.md D8；规划/01_需求规划.md §3；规划/04_数据模型与契约.md §2.2 buy_type；规划/06_待补信息清单.md Q-B1 分享收益比例
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

| 例 | B | 比例 | 分享者 | 分享者上级 | 平台 |
|---|---|---|---|---|---|
| 1 | 2000 | 5000/1000 | 1000 → PROMO | 200 → PROMO | 800 |
| 2 | 2000，分享者无上级 | 5000/— | 1000 | 0 | 1000 |

- 例：A 分享给 App 用户 B，B 通过 A 的链接购买 → 订单归属 A（share），B 不得分账。
- 例：A 用自己的分享链接下单，BR-ATTR 定稿前 → 按 self，A 得 r_own(self) 份额入 SELF。
- 流水类型：分享者 SHARE_CREDIT，上级 REFERRAL_CREDIT；税目见 BR-FUND。

#### BR-CALC-25 细则 · 联盟未单列补贴类佣金时的处理

- 状态：待决策
- 默认值：未单列时 N 整体计入 B，但入账推迟到联盟结算后（理由：补贴佣金常带条件、事后可能被追回，结算后入账可降低扣回与坏账风险；是否把补贴分给用户属于金额口径，需财务 W1 确认）
- 决策人：财务
- 依赖平台能力：淘宝/京东/拼多多订单接口是否单列补贴类佣金（CAP-TB-04、CAP-JD-04、CAP-PDD-04）
- 取代：无
- 来源：规划/01_需求规划.md §3；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-04；PRD修订_后端功能规划 §2.2
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：淘宝订单 pub_share_pre_fee=1000，接口无补贴明细 → 预估按 B=1000 展示 500；收货 +15 天时尚未结算 → 不入账；结算值 950 到达 → 按 B=950 入账 475/95。
- 判定'未单列'以 09 表验证结论为准，按平台配置 union.&lt;platform>.subsidy_itemized（boolean，默认 true）；为 false 时本条生效。
- 生效方式：subsidy_itemized=false 的平台，订单入库时置 orders.credit_requires_settle=true；入账任务在 settle_commission_fen 为空时跳过该单（不设 hold，不影响 BR-FUND-06 的 hold 语义）。该守卫已并入 BR-FUND-04 的入账条件（C-27 (e)，默认处理，待财务确认）。

#### BR-CALC-26 细则 · 联盟报文金额与比例的换算

- 状态：默认假设
- 默认值：精确解析，超过 2 位小数按 floor（理由：与 BR-CALC-08 向平台保守取整一致；原文保留可对账）
- 决策人：财务
- 依赖平台能力：三家订单与商品接口金额、佣金率字段的实际格式与单位（CAP-TB-04 未知项：commission_rate 单位）
- 取代：无
- 来源：规划/02_系统架构.md §4.2；规划/04_数据模型与契约.md §5 金额整数分；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-04 未知项

- 例：'14.52' → 1452；'14.5' → 1450；'14.526' → 1452（floor，原文存 raw_payload）；'-3.20' → -320（负数原样保留供 raw_n_fen，计算前按 BR-CALC-02 处理）。
- 例：'20.00' → 2000 bp；'12.345' → 1234 bp。
- 例：JSON 原文 `"estimateFee": 0.1` → 字面值 '0.1' → 10，不得经过 0.1 的二进制浮点。

#### BR-CALC-27 细则 · 每单四段金额与平台预估利润

- 状态：待决策
- 默认值：四段 = 联盟佣金总额、基数前扣除（不设平台预留比例）、B、平台预估利润；利润扣除我方淘礼金红包面额（理由：沿用后端功能规划与花卷云底稿「每单落四段金额」的需求，但按本主题 B 的定义（BR-CALC-02 不扣预留）改写；利润扣红包面额使淘礼金 none / normal 两种模式口径一致，与 BR-CALC-19「净 200」算例一致；利润口径属金额口径，需财务确认）
- 决策人：财务
- 依赖平台能力：无（n_base_fen、subsidy_commission_fen 的取数依赖见 BR-CALC-03、BR-CALC-18；tlj_n_net_of_redpacket 依赖见 BR-CALC-19）
- 取代：
  - 参考_花卷云功能查漏底稿 §2 分佣基数、§16 #1：「每单落库四个金额：预估佣金、平台预留、实际计算佣金、平台预估利润；实际计算佣金 = 联盟预估佣金 × (1 − 平台预留%)」
  - PRD修订_后端功能规划 §2.5 第 6 步：「订单首次入库且已归因时落四个金额：联盟预估佣金 N、平台预留、可分配基数 B、平台预估利润」
- 来源：参考_花卷云功能查漏底稿 §2、§16 #1；PRD修订_后端功能规划 §2.5 第 6 步、§13.2 易漏项 #1、经营看板（平台预估利润）

| 字段（整数分） | 定义 | 时点 |
|---|---|---|
| n_total_fen | n_base_fen + subsidy_commission_fen（已扣技术服务费，可为负） | 快照生成时与每个新 commission_version |
| pre_base_deduct_fen | n_total_fen − base_fen | 同上 |
| base_fen | B（BR-CALC-02） | 同上 |
| platform_est_profit_fen | n_total_fen − Σ该版本用户份额 − tlj_redpacket_fen；可为负 | 同上 |

- 存储：`commission_split_totals(order_id, commission_version, n_total_fen, pre_base_deduct_fen, base_fen, user_share_total_fen, tlj_redpacket_fen, platform_est_profit_fen, created_at)`，唯一 (order_id, commission_version)，只追加；orders 冗余当前版本值供报表查询。
- 例（普通单）：n_base 1234、补贴 0、5000/1000 → ① 1234 ② 0 ③ 1234，用户 617+123=740，④ 494。
- 例（补贴，BR-CALC-18）：n_base 800、补贴 200 → ① 1000 ② 200 ③ 800，用户 400+80，④ 520。
- 例（我方淘礼金 none，BR-CALC-19）：N=500、红包 300 → ① 500 ② 0 ③ 500，用户 0，④ 500−0−300=200。
- 例（我方淘礼金 normal，tlj_n_net_of_redpacket=false）：N=500、红包 300 → ① 500 ② 300 ③ 200，用户 100+20，④ 500−120−300=80。
- 例（负 N 冲正）：n_total −320 → ① −320 ② −320 ③ 0，用户 0，④ −320。
- 边界：held 受益人份额计入 Σ用户份额（仍是应付）；forfeited 为 0。四段金额不进用户接口、不进用户可见文案。
- 我方淘礼金订单匹配不到红包记录 → tlj_redpacket_fen、platform_est_profit_fen 为 null，报表标'待核'并告警（与 BR-CALC-19 的待处理表同一告警）。

### 5.3 本主题未决问题

1. BR-CALC-23：结算正差是否需要财务批准、负差是否即时记账（默认负差即时、正差审批），需财务 W1 决定
2. BR-CALC-25：联盟未单列补贴类佣金时，补贴部分是否分给用户，需财务决定
3. BR-CALC-06：L2、L3 等级的 r_own / r_direct 是否与 L1 不同，以及单位经济模型终值（PRD v2.1 §19.1 D5、§19.2 G1；后端规划 §12.1 B11；规划侧见 06 Q-B1、01 §8.3），需财务 W1 定
4. BR-CALC-19：我方淘礼金订单是否给本人或上级分佣（默认都为 0），需财务确认
5. BR-CALC-12：直推受益人按 paid_at 时的上级（默认）还是按快照时 parent_id，需负责人确认
6. BR-CALC-24 / BR-ATTR：分享者经自己的分享链接下单按 self 还是 share（默认 self，记 SELF），影响账户与税目，需 BR-ATTR 定稿
7. BR-CALC-13：held 状态最长保留多久、风控结论超期未出时如何处理，需与风控规则（BR-FUND、规划/01 E17 风控）一起定
8. 部分退款负向调整的流水类型：已列入 §14.3 C-16，默认按 BR-FUND-08 写 CLAWBACK（sub_type=PART_REFUND），BR-CALC-15、BR-CALC-23 已按此改写，待财务确认
9. BR-CALC-11：三家订单接口能否拿到预售尾款付清时间，需在 09 表订单同步项验证
10. 活动加成（P1 新人红包、邀请奖励）的计算口径与是否占用 8000 上限之外的预算，P1 前再定
11. BR-CALC-02、BR-CALC-07、BR-CALC-08、BR-CALC-09：由默认假设改为待决策（金额口径），默认值不变，需财务 W1 随 specs/ledger-rules.md 签字；BR-CALC-24 同样改为待决策，与第 6 项一起定
12. BR-CALC-27：平台预估利润是否扣除我方淘礼金红包面额、四段金额是否需要按版本留历史（默认扣除、按版本只追加），需财务确认
13. 【已由 §14.3 C-22 处理：默认处理，待负责人确认（财务知悉）】BR-CALC-16 与 BR-PRICE-07 的淘宝比价区间下限算法、拿不到 min/max 时的展示：下单前展示只按 BR-PRICE-07，BR-CALC-16 只保留订单侧计算；compare_rate_ratio_bp=5000 为占位值，数据到位前只在 App 内展示
14. 【已由 §14.3 C-27 处理：(e)(g) 默认处理，待财务确认】跨主题分歧：BR-CALC-15 / BR-CALC-25 新增的 orders.credit_requires_settle 入账守卫未在 BR-FUND-04 的入账条件中；BR-CALC-23 (b) 价保负差即时记账与 BR-FUND-01 R9b「无分录、只由月结补差」不一致（按 C-07 默认以本主题为准）；处理结果：credit_requires_settle 守卫已并入 BR-FUND-04（WAITING_SETTLE，不显示预计日期）；价保、比价降佣等负差按 BR-FUND-01 R9b 即时写负向 SETTLE_ADJUST（uniq_key {order_key}:{uid}:{role}:ADJ:{sub_type}:v{commission_version}），正差仍进 BR-FUND-09 候选
15. 【已由 §14.3 C-27 处理：(c) 代理已补；(d) 默认处理，待财务确认】跨主题缺口：BR-CALC-13 受益人级 held 在订单 CREDITED 后补入账所用的迁移与凭证 uniq_key，BR-FUND-01 / BR-FUND-05 未定义（BR-FUND-04 写「一单的全部受益人同时入账」）；BR-CALC-10 中 VOID 未归因订单找回通过只设 user_id 的事件，BR-FUND-01 迁移表未列出；处理结果：held 解除后按 BR-FUND-01 R5a 入账（uniq_key 沿用 {order_key}:{uid}:{role}:CREDIT），VOID 未归因订单找回 / 改派按 R3b（rebate_status 保持 VOID，只写 user_id、user_basis、locked=true）

---
