# 08 业务规则 · 5. 返利计算与分账（BR-CALC）

返回 [README](README.md)（使用规则、术语表、规则索引）

## 5. 返利计算与分账（BR-CALC）

本节规定：分佣基数 B、分账公式、比例与上限、舍入、快照时点、调整重算、比价/淘礼金/补贴、每单四段金额。共 27 条（已确认 14、默认假设 4、待决策 3、待验证 6）。

2026-10-01 晚负责人补充决定（docs/changes/20261001-拍板第二批.md §8）：ADD-06 用户只有一个余额（BR-FUND-13），本人、直推、间推份额都入受益人的同一余额，分佣快照仍按角色记录受益人，不再有 account_type；ADD-05 发布规则版本（含开启间推）、正差补差、申诉恢复由超管或被勾选该权限的账号一人完成，须 step-up、写审计，取消「发布人 ≠ 起草人」「第二人审批 / 复核」；ADD-03 各平台预留比例、各等级比例、间推比例开发期用占位值，上线前超管在后台按规则版本填写，之后随时可改、立即生效（按 paid_at 选版本，不回溯），取代「W1 随 ledger-rules.md 一次给出」。本主题中 finance、super 等后台角色名按 ADD-04 读作「超管，或被勾选该操作权限点的后台账号」。

2026-10-01 晚负责人确认 规划/11 §7.3 第 8 项：BR-CALC-21 的算例表来源改为两家模型盲算 + 08 原文对照、负责人确认 5 条代表例，取代「由财务给出」；分账公式、属性与每日校验不变。

2026-10-03 资金规则对齐（docs/changes/20261003-资金规则对齐.md，负责人批准）：BR-CALC-02 写明取值阶段适用于所有按基数判断的规则、联盟给的任何金额先换算再用；BR-CALC-09 补未成年受益人、净额口径与封禁 / 注销受益人取较小值；BR-CALC-13 补没收份额的 FORFEIT 凭证与锁内判定；BR-CALC-15、23 随 R9b 只存档（决-01 A）与整单分路改写；BR-CALC-10 随决-07 A 改写。条目状态不变；旧写法登记在各条细则「取代」。同日评审后修改（变更记录 §13.6；同步修正，不改分佣比例、受益权与应得金额）：BR-CALC-02 补「不同的 N 可得同一个 B，B 相等时平台金额仍按新的 N 重算」，BR-CALC-23 (a) 的分路注随 BR-FUND-09 补基数相等的情形；BR-CALC-13 的 FORFEIT 凭证写明只适用于首次整份没收，延后正差转没收只没收待补记额（BR-FUND-04 ⑫）。

**订单状态写法**：本主题按 BR-FUND-01 的双状态（`platform_status` + `rebate_status`）与迁移编号（P1–P15、R1–R14；P11–P15 为 2026-10-03 资金规则对齐补入）书写（按 C-01 默认处理，已由负责人确认 2026-09-30）。与 规划/04 单一 order_status 的对应：O1→P1；O2→P2 / R2；O3→P3 + R4；O4→P6 + R6（入账前整单失效，rebate_status=VOID）；O5→R7；O6→R5（SETTLE_BATCH_CREDIT）；O7→P4 且 rebate_status 不变（只写 order_settlements）；O8→P4 + 结算补差（BR-CALC-23）；O9→R8（rebate_status=CLAWED_BACK）；O10→R9（部分退款、部分维权）/ R9b（价保等佣金变化）；O11→R3。单一状态 SETTLED = (platform_status=SETTLED, rebate_status=CREDITED 且补差已处理完)。负责人不采纳双状态时，按 BR-FUND-01 的映射表回退到上列 O 编号。

### 5.1 规则一览

| 编号 | 规则 | 状态 | 影响面 |
| --- | --- | --- | --- |
| BR-CALC-01 | **金额与比例的数据类型**<br>所有金额必须以整数分存储与运算（PG bigint，字段后缀 _fen，TS 用 bigint）；所有比例必须以整数万分之一存储（字段后缀 _bp，1500 = 15%）。金额运算只能调用 packages/money，分账纯函数只能放在 packages/domain；任何金额路径禁止出现 number 浮点、parseFloat、toFixed、Math.round。对外契约 contracts/openapi.yaml 中所有 \*_fen 字段一律为 integer（int64，单位分），前端按整数处理，只在展示层除以 100 格式化。 | 已确认 | packages/money（mulDivFloor / mulDivCeil）；packages/domain；所有 \*_fen / \*_bp 字段；contracts/openapi.yaml 金额字段为 integer（int64，单位分），见 04 §5；lint 规则 |
| BR-CALC-02 | **分佣基数 B 的定义**<br>分佣基数 B = max(0, floor(N_base × (10000 − reserve_bp) / 10000) − tlj_deduct_fen)。N_base 为联盟口径的推广者收入：已扣平台技术服务费、不含补贴类佣金，单位分（字段映射见 BR-CALC-03、BR-CALC-18）。reserve_bp 为平台预留比例（整数万分之一，0–10000），属于分佣规则版本，每个平台一个值，不按等级、订单类型或个人区分（BR-CALC-06）；快照按 paid_at 选定规则版本（BR-CALC-11）时同时取定该订单平台的 reserve_bp，此后入账与调整重算都用快照中的 reserve_bp。预留金额 reserve_fen = N_base − floor(N_base × (10000 − reserve_bp) / 10000) 归平台，取整尾差归平台；N_base ≤ 0 时先置 0，reserve_fen = 0。tlj_deduct_fen 只在我方淘礼金 normal 模式下非 0（BR-CALC-19），其余为 0。取值阶段：settle_commission_fen 为空时取最新预估收入；一旦 settle_commission_fen 非空，N_base 只取结算收入，之后预估字段的变化只存档，不参与计算；按此取得的 N_base 称有效联盟佣金。本条的取值阶段适用于所有按基数做判断的规则：BR-FUND-03 的预估、BR-FUND-07 与迁移 R6 的基数归零、迁移 R7、BR-FUND-08 的新基数、迁移 R8、R9、R10；联盟给出的任何金额（新佣金、应扣佣金、结算额）都是 N 口径，先按本条换算成 B，再重拆、再与 booked_base_fen 比较；换算含向下取整，不同的 N 可得同一个 B，B 相等而 N 不同时受益人应得不变，平台的预留与留存仍按新的 N 重算（BR-FUND-09）。commission_splits 中 raw_n_fen 存联盟原值（可为负），reserve_bp、reserve_fen 存所用预留比例与预留金额，base_fen 存计算用的 B（≥ 0），platform_retain_fen = base_fen − Σ用户份额 ≥ 0（不含预留，平台合计见 BR-CALC-04）。每单四段金额与平台预估利润见 BR-CALC-27。 | 已确认 | orders.est_commission_fen / settle_commission_fen（语义：已扣技术服务费的推广者收入）；commission_rule_reserves.reserve_bp；commission_splits.raw_n_fen / reserve_bp / reserve_fen / base_fen / platform_retain_fen；后台分佣规则页（各平台预留比例）；商品卡 / Agent 报价（BR-CALC-20）；毛利报表；R1 联盟对账；specs/commission-examples.csv |
| BR-CALC-03 | **各平台 N 的取数字段**<br>每个平台的 UnionAdapter 必须把订单接口中'已扣技术服务费的推广者预估收入 / 结算收入'映射为 N（再按 BR-CALC-18 拆出 n_base_fen 与 subsidy_commission_fen）。映射写在 specs/attribution.md 并附录制报文，还须与联盟后台同一订单的推广者收入逐单核对一致，证据路径记入 09 表对应 CAP。验证通过前：该平台订单只展示预估，不执行月结批次入账（R5 SETTLE_BATCH_CREDIT，含 M3 白名单内测，由 credit.enabled.&lt;platform> 控制，默认 off；该平台首个月结批次另需 08b 首个月结对账通过，BR-FUND-04 ⑨）；convert.enabled.&lt;platform> 不得对公众打开。若平台返回的是未扣服务费的毛收入，Adapter 按 N = gross − ceil(gross × fee_bp / 10000) 扣除（服务费向上取整，N 取保守值）。fee_bp 优先取订单报文中的服务费率字段；报文没有时取配置 union.&lt;platform>.service_fee_bp（按订单类型配置，每个取值附来源，未核实的标'待核实'）；两处都没有，订单进待处理表并告警，不得按 0 处理。 | 待验证 | UnionAdapter.&lt;platform>.toN()；配置 union.&lt;platform>.service_fee_bp、credit.enabled.&lt;platform>；specs/attribution.md；规划/09_平台能力验证/（对应 CAP 的结论，按 09 README §0.4 回填）；订单同步录制 fixture |
| BR-CALC-04 | **分账公式与受益人（通用与自购单）**<br>每个已归因子订单的分账必须按下式计算：本人份额 = floor(B × r_own_bp / 10000)，受益人为订单归属用户；直推份额 = floor(B × r_direct_bp / 10000)，受益人为归属用户在 paid_at 时的直接上级（BR-CALC-12），无上级时为 0；间推份额 = floor(B × r_indirect_bp / 10000)，只在所选规则版本 indirect_enabled=true 时产生，受益人为直推上级在 paid_at 时的上级（BR-CALC-05、BR-CALC-12），缺任一层时为 0；平台留存 = reserve_fen + B − 本人份额 − 直推份额 − 间推份额（reserve_fen 为 BR-CALC-02 的预留金额；B − Σ用户份额 部分记 platform_retain_fen）。r_own_bp、r_direct_bp、r_indirect_bp 按 BR-CALC-06 取与订单 platform、order_type 对应的行。各份额都入对应受益人的单一余额（BR-FUND-13，拍板第二批 §8 ADD-06），来源由流水类型区分；分享单的比例与受益人见 BR-CALC-24。order_type 取 orders.buy_type，由归因流程（BR-ATTR）写入，splitCommission() 不自行判断。 | 已确认 | packages/domain splitCommission()；commission_splits.beneficiaries；ledger REBATE_CREDIT / REFERRAL_CREDIT；订单详情页预估返利；验收用例 AC-SET-待编号（参考文档编号 AC-MONEY-001，规划/ 未定义；编号规则见 13 §13.2） |
| BR-CALC-05 | **间推比例与开关**<br>计酬最多两级（BR-INV-12）。间推（直推上级的上级）由规则版本开关控制：commission_rule_versions.indirect_enabled（默认 false）+ commission_rules.r_indirect_bp（smallint NOT NULL DEFAULT 0，CHECK 0–8000）。indirect_enabled=false 的版本中 r_indirect_bp 必须全为 0，splitCommission() 不产生 indirect 受益人。indirect_enabled=true 时：间推份额 = floor(B × r_indirect_bp / 10000)，r_indirect_bp 取 (platform, 间推受益人在 paid_at 的等级, order_type) 行，入间推受益人的余额，流水 REFERRAL_CREDIT、sub_type=INDIRECT，所得类型同直推；受益人取值见 BR-CALC-12 / BR-INV-13，失效见 BR-CALC-13；间推受益人与归属用户或直推受益人为同一人（异常数据）时间推份额归平台并告警。开启、关闭、改比例只能通过发布新规则版本（BR-CALC-11 按 paid_at 选版本，不回溯快照）；发布 indirect_enabled=true 的版本由超管或被勾选规则发布权限的账号一人 step-up 完成并写审计（拍板第二批 §8 ADD-05），试算报告含间推份额列（BR-CALC-22）。depth ≥ 3 的祖先永不计酬；成为直推或间推受益人不以任何入门费、购买或充值为条件（BR-INV-12、BR-INV-20）。 | 已确认 | commission_rules.r_indirect_bp 与 CHECK；commission_rule_versions.indirect_enabled；packages/domain splitCommission()（indirect 分支）；后台分佣规则页（开关、比例列、step-up 发布）；ledger REFERRAL_CREDIT sub_type=INDIRECT；关系闭包表（MVP 不用于计佣） |
| BR-CALC-06 | **比例配置维度与默认值**<br>commission_rules 每行 = (rule_version_id, platform, level, order_type ∈ {self, share}, r_own_bp, r_direct_bp, r_indirect_bp)，唯一 (rule_version_id, platform, level, order_type)；版本级字段 indirect_enabled 在 commission_rule_versions（BR-CALC-05）；平台预留比例在 commission_rule_reserves，每行 = (rule_version_id, platform, reserve_bp ∈ 0–10000)，唯一 (rule_version_id, platform)（BR-CALC-02）。r_own_bp 用于订单归属用户，按其等级取行；r_direct_bp 用于直接上级，按上级等级取同 platform、同 order_type 的行；r_indirect_bp 用于间推受益人，按其等级取同 platform、同 order_type 的行（等级取值时点见 BR-CALC-12）。发布时版本内必须覆盖配置 commission.platforms × {L1, L2, L3} × {self, share} 的全部组合，缺任一组合则整个版本拒绝发布，不允许回退到其他平台或等级；版本内还必须对 commission.platforms 中每个平台各有一条 reserve_bp，缺任一平台同样拒绝发布，不回退到上一版本的值。比例与预留比例只能通过发布新规则版本调整（BR-CALC-22），按订单 paid_at 选版本、不回溯已生成快照（BR-CALC-11）。订单平台在所选版本中没有对应行时，订单进待处理表并告警，不生成快照。 | 已确认 | commission_rules 表结构、唯一约束与种子数据；commission_rule_reserves（每平台预留比例）；配置 commission.platforms；后台分佣规则页；商品卡 / Agent 报价；specs/commission-examples.csv；等级页展示文案 |
| BR-CALC-07 | **比例合计上限校验**<br>规则发布时必须对每个 (平台, 订单类型) 校验：max_等级(r_own_bp) + max_等级(r_direct_bp) + max_等级(r_indirect_bp) + 活动加成_bp ≤ 8000（indirect_enabled=false 的版本 r_indirect_bp 为 0）；任一单项 &lt; 0 或 > 8000 也拒绝发布。校验不通过返回错误并不生成新版本。 | 已确认 | commission_rules 发布接口；后台分佣规则页校验提示；DB CHECK（单项 0–8000）；验收用例 AC-SET-待编号（参考文档编号 AC-MONEY-014，规划/ 未定义） |
| BR-CALC-08 | **舍入与尾差归属**<br>每个用户份额必须单独按 floor 取整到分（对非负数向下取整）；平台留存 = B − Σ用户份额，承接全部尾差；禁止先按比例算平台份额再倒推用户份额，禁止四舍五入。 | 已确认 | packages/money floor/ceil；packages/domain splitCommission()；specs/ledger-rules.md；属性测试 |
| BR-CALC-09 | **调整按新基数全额重算**<br>任何基数变化（部分退款、价保、结算差额）后，必须用快照比例对新基数 B_new 全额重算每个受益人的应得额，再以'差额 = 新应得 − 已入账（已入账净额，口径同 BR-FUND-08；或原预估）'生成调整；禁止对基数差额 ΔB 直接乘比例取整。受益人状态规则：status=forfeited 的受益人新应得恒为 0，不生成任何调整（经申诉恢复的除外，BR-CALC-13）；受益人 risk_state=banned 时，负向差额照常扣回，正向差额归平台（记 COMMISSION_REVENUE 并写 forfeit_reason）；受益人已注销（deletion_status ∈ {processing, done}）时，正向差额同样归平台，负向差额不写该用户扣回分录，改记平台坏账（BR-ID-28，记账见 BR-FUND-08）；受益人处于 frozen / appealing 时，负向差额照常扣回，正向差额与 BR-CALC-13 的 hold 一样延后，状态解除后再按当时状态处理；已识别未满 18 周岁的受益人：推广份额（share、direct、indirect）的正向差额归平台（forfeit_reason=minor，BR-ID-26 (b)），负向差额照常扣回，自购份额不受影响。归平台的正向差额并入平台凭证，不计入该受益人的净额；改记平台坏账的负向差额沿用该受益人的 uniq_key，计入其净额。封禁或已注销的受益人，新应得取「按新基数重拆的份额」与「其已有净额」中较小的一个。 | 已确认 | settlement 补差任务；CLAWBACK / SETTLE_ADJUST 金额计算；commission_split_amounts；specs/ledger-rules.md；属性测试（多次调整后等于一次性计算） |
| BR-CALC-10 | **分佣快照生成时点与不可变范围**<br>分佣快照必须在子订单首次同时满足'platform_status ∈ {PAID, RECEIVED, SETTLED}'且'已归因到用户'时生成，与触发它的迁移在同一事务写入 commission_splits：入库时已满足 → 入库事务（BR-FUND-01 R2）；已归因但 platform_status=DEPOSIT_PAID → 不生成快照、不计预估（rebate_status=ESTIMATED，预估为 0），在 platform_status 迁到 PAID（P2）的事务内生成；未归因（rebate_status=UNATTRIBUTED）→ 在找回通过或后台改归属（R3）的事务内生成，此时 platform_status 仍为 DEPOSIT_PAID 的，推迟到 P2。未归因订单已为 rebate_status=VOID（对应单一 order_status 的 INVALID；未归因订单不会进入 CLAWED_BACK）时后台改派，按 BR-FUND-01 R3b 只写 user_id、user_basis=admin（BR-ATTR-09）、locked=true；同步重跑用户归属成功的只写 user_id、user_basis=param，不置 locked；都不生成快照、无分录，rebate_status 不变；用户找回不受理 VOID 订单（BR-ATTR-17 ④c，负责人 2026-10-03 资金规则对齐决-07 选 A）。快照一经生成，rule_version_id、order_type、activity_type、rebate_mode、reserve_bp、各受益人的 user_id / role / ratio_bp / level 不可修改（单一余额后受益人不带 account_type，拍板第二批 §8 ADD-06）；受益人状态变化与各版本金额只能追加记录，不得覆盖快照行。 | 默认假设 | commission_splits / commission_split_amounts / commission_split_beneficiary_events 表结构与唯一约束；order-sync 入库流水线；BR-FUND-01 迁移 R2 / R3 / P2（含入库即 RECEIVED 时 R2 同事务进 WAITING）；订单详情页（定金阶段文案、失效找回文案）；SM-REB-R2、SM-REB-R3、SM-PLT-P2 测试 |
| BR-CALC-11 | **规则版本生效时点**<br>每个规则版本必须带 effective_from（ISO 8601 +08:00，须 ≥ 发布时刻，可等于发布时刻即立即生效，BR-CALC-22），且必须严格大于所有已发布且未撤销版本的 effective_from，否则拒绝发布。快照选用'effective_from ≤ paid_at 的已发布、未撤销版本中 effective_from 最大的一个'（边界含等号，比较精度到秒）。未到 effective_from 的已发布版本可以撤销（status=revoked，须 step-up 并写审计，不改内容）；已生效版本不可撤销、不可修改、不可删除，回滚 = 发布一个新版本。规则变更不回溯已生成的快照。联盟返回的无时区时间一律按 +08:00 解析，存 timestamptz。paid_at 为平台付款时间，预售单取尾款付清时间；平台不提供尾款时间时按本条细则的降级顺序取值。找回、改派订单同样按 paid_at 选版本，不按批准时刻，并在订单与快照记 paid_at_source。 | 默认假设 | commission_rules 版本表：effective_from、status（published / revoked）；快照版本选择查询；orders.paid_at / paid_at_source；后台规则发布页（生效时间必填、撤销未生效版本）；近 7 天试算报告 |
| BR-CALC-12 | **等级与上级的取值时点**<br>快照中本人等级与上级等级都取 paid_at 时刻的有效等级：取 level_change_logs 中 effective_at ≤ paid_at 的最后一条（等号取新等级，BR-INV-14）；等级日志缺失时取注册默认等级 L1 并告警，人工核实后如需补差走 ADMIN_ADJUST。直推受益人取 paid_at 时刻有效的上级（relation_change_logs 按 created_at 重放：bound_at ≤ paid_at 且未解除的上级，bound_at / unbound_at 由相邻记录的 created_at 推出，BR-INV-11）；paid_at 时尚无上级 → 直推份额为 0，事后绑定不补。间推受益人（indirect_enabled=true 时）= 直推上级在 paid_at 时刻的上级，同样按 relation_change_logs 重放；任一层在 paid_at 时不存在 → 间推份额归平台，事后绑定不补。 | 默认假设 | level_change_logs（需有 effective_at）；relation_change_logs（bound_at = 该条 created_at，unbound_at = 同一用户下一条记录的 created_at，BR-INV-11；表名见 13 §13.8）；commission_splits.beneficiaries.level；等级变更接口；邀请绑定接口 POST /v1/me/inviter |
| BR-CALC-13 | **受益人失效时份额归平台**<br>受益人失效时其份额归平台留存，不得向上顺延给更上级，也不得转给其他受益人；本条对直推与间推受益人同样适用（直推上级失效时，间推份额仍按间推受益人自身状态判定，不因此上移或下移）。快照生成时判定：受益人不存在或已注销（deletion_status ∈ {processing, done}）→ forfeited，终局不变；risk_state 为 banned、frozen、appealing 的受益人在快照中记 active，不在快照阶段剥夺。入账（月结批次，BR-FUND-04）执行时逐受益人判定（判定在 BR-FUND-16 细则「加锁流程」的锁内进行，用取得锁之后重读的受益人状态）：已注销或 risk_state=banned → 追加 forfeited 事件并写 forfeit_reason，份额计入 COMMISSION_REVENUE，此后不再补发（封禁经申诉撤销的，按 BR-FUND-22「申诉恢复」差错单经有权限者 step-up 处理后补发，一人可完成，拍板第二批 §8 ADD-05）；已被识别为未满 18 周岁 → 其推广份额（分享、直推、间推）同样 forfeited（forfeit_reason=minor，BR-ID-26 (b)），识别前已入账的不扣回；risk_state ∈ {frozen, appealing} → 该受益人入账延后（held），其他受益人照常入账，状态恢复 normal 后在后续月结批次（含补充批次，BR-FUND-04）补入账（订单已 CREDITED 时按 BR-FUND-01 R5a 与 BR-FUND-04 ⑫ 的受益人补记项，金额按执行时的 booked_base_fen 重算），转为 banned 时再判 forfeited；被剥夺的份额，每个受益人写一张平台凭证 `{order_key}:PLATFORM:FORFEIT:{uid}:{role}`（借 UNION_RECEIVABLE / 贷 COMMISSION_REVENUE），金额 = 该受益人按入账基数的应得，凭证带 forfeit_reason（banned、deleted、minor），首次入账（R5）与暂缓转没收（R5a）用同一个键，不另设按原因区分的平台科目（凭证粒度随 BR-FUND-05）；本句指首次整份没收：入账时被剥夺，或暂缓、在本单还没入过账的受益人转没收（入账基数取执行时的 booked_base_fen）；正差被延后的待补记项（BR-FUND-04 ⑫ 的延后差额义务）转没收的，是延后差额没收，只没收当前待补记额、只处置这一笔义务，键与金额见 BR-FUND-04 ⑫，不追加 forfeited 事件，该受益人已入账的部分照常参与之后的扣回与补差（BR-CALC-09）；held 满 30 天仍无风控结论时告警，由人工处理，系统不因超时自动入账或剥夺；appealing 只由账户级申诉产生，订单申诉不改 risk_state（BR-ID-36）；注销冷静期（deletion_status=cooling）不算失效，照常入账（提现限制见 BR-FUND）。订单级风控命中（BLACKLIST_HIT）仍按 BR-FUND-07 整单作废（入账前 R6 → VOID；对应 04 O4），与受益人级 forfeited 分开。受益人级 held 只记在 commission_split_beneficiary_events，不设置订单级 hold 字段（hold 只由人工或风控按 BR-FUND-06 设置）。已入账的份额不因事后封禁而扣回（资金冻结见 BR-FUND-14 与风控 规划/01 E17）。 | 已确认 | splitCommission() 入参 beneficiary_status；settlement 入账任务（hold 与补入账）；commission_split_beneficiary_events；users.risk_state / deletion_status；客服话术（为何上级没拿到分佣、为何返利延后） |
| BR-CALC-14 | **入账时的基数取值**<br>月结批次入账（BR-FUND-04；R5 SETTLE_BATCH_CREDIT，rebate_status WAITING → CREDITED，对应 04 O6）时必须以联盟结算额 orders.settle_commission_fen（月结账单只收已有联盟结算数据的子订单；取值规则见 BR-FUND-09；对应 04 O7）按 BR-CALC-02 计算 B，用快照比例与快照中的 reserve_bp 重算后入账，并写一个新的 commission_split_amounts 版本（与 BR-FUND-05 的 B_credit 同值）；不得以预估收入入账（拍板第二批 FUND-01）。入账后的调整只由结算差额与部分退款 / 价保触发，记账时点与审批见 BR-CALC-23。差额原因码统一为 PRICE_COMPARE、PRICE_PROTECT、SETTLE_DIFF、PART_REFUND。 | 已确认 | settlement 入账任务；commission_split_amounts；订单详情'实返与预估差额'展示；R1 对账 |
| BR-CALC-15 | **部分退款与价保重算**<br>部分退款、价保、维权部分成功导致佣金变化时，新的联盟佣金必须取联盟返回的更新后佣金 N_new，新基数由它按 BR-CALC-02 换算，不得由我方按数量或金额自行推算。是否由我方估算由配置 union.&lt;platform>.partial_refund_updates_commission（boolean，按 09 表验证结果设置，默认 true）决定：为 false 且退款按件计时，Adapter 用 N_new = floor(N × (quantity − refunded_quantity) / quantity) 作为预估（只用于入账前的预估，已 CREDITED 的不据此扣回，BR-FUND-08）；为 false 且按金额退款或价保时，该子订单置 orders.credit_requires_settle=true：rebate_status=WAITING 期间 settle_commission_fen 为空则入账任务跳过（不使用 BR-FUND-06 的 hold 字段），等联盟结算值到达后按 BR-CALC-14 入账，不得沿用原 N 入账；已 CREDITED 的，等结算值按 BR-CALC-23 (a) 处理。只有新 N 与已存值不同时 commission_version 才 +1，更新语句必须带 WHERE commission_version = :expected 乐观锁，冲突时重读后重算。rebate_status ∈ {ESTIMATED, WAITING}（未入账）：只更新预估，不写流水（BR-FUND-01 R7，对应 04 O5）；rebate_status=CREDITED：按 BR-CALC-09 求差——部分退款、部分维权（R9，对应 04 O10）写 CLAWBACK（sub_type=PART_REFUND 等，BR-FUND-08），价保等佣金下调反映在联盟新的结算记录上的按 BR-CALC-23 (a)（迁移 R10），只有预估变化的按 R9b 只存档并出差错单（BR-CALC-23 (b)）。剩余数量为 0 或 N_new = 0 按整单失效处理（入账前 R6 → VOID，入账后 R8 → CLAWED_BACK；对应 04 O4/O9）。 | 待验证 | orders.refunded_quantity / commission_version（乐观锁）/ credit_requires_settle；配置 union.&lt;platform>.partial_refund_updates_commission；BR-FUND-01 迁移 R7 / R9 / R9b；ledger CLAWBACK sub_type=PART_REFUND；BR-FUND-04 入账守卫；订单详情差额原因 PART_REFUND / PRICE_PROTECT；规划/09_平台能力验证/（对应 CAP 的结论，按 09 README §0.4 回填） |
| BR-CALC-16 | **比价订单的计算与展示**<br>比价订单不得使用特殊比例：订单分账一律以联盟返回的（已降佣的）N 按 BR-CALC-04 / BR-CALC-24 计算，订单记 is_price_compare、commission_rate_min_bp、commission_rate_max_bp，实返与预估不同时差额原因码为 PRICE_COMPARE；比价订单的订单列表、订单详情、入账流水三处金额必须一致。下单前报价的比价风险展示只按 BR-PRICE-07（C-22）。 | 待验证 | orders.is_price_compare / commission_rate_min_bp / commission_rate_max_bp；商品卡与详情页比价区间展示见 BR-PRICE-07；订单差额原因 PRICE_COMPARE；验收用例 F-ORD-11 |
| BR-CALC-17 | **自购与分享报价口径（三平台）**<br>下单前报价必须按订单类型分别估算（由 UnionAdapter.quoteN(product, sku, order_type) 输出，见 BR-CALC-20），订单侧 N 一律直接取联盟订单接口返回值，我方不得对订单再乘任何折算系数。拼多多：自购报价 N = floor(分享口径佣金 × self_buy_factor_bp × account_level_factor_bp / 10000 / 10000)，一次乘完再一次 floor（mulDivFloor(x, a×b, 100000000n)）；分享报价 N = floor(分享口径佣金 × account_level_factor_bp / 10000)；转链必须透传 search_id。淘宝：自购与分享分别用 promotion_type=1 / 2 取佣金；新 App 取不到某一口径时，报价取可得口径中的较低值。京东：PLUS 买家可能按 plusCommissionShare 或 0 计佣，报价按非 PLUS 口径并在详情页提示'PLUS 会员购买部分商品可能无返利'。 | 待验证 | UnionAdapter.&lt;platform>.quoteN()；配置中心 union.pdd.\*；商品卡 / Agent 报价；分享面板预估收益；规划/09_平台能力验证/（对应 CAP 的结论，按 09 README §0.4 回填） |
| BR-CALC-18 | **平台补贴与补贴类佣金**<br>平台补贴（平台出资给消费者的优惠）与补贴类佣金（佣金膨胀、超级补贴等单独计的推广者收入）不得计入 B，归平台留存；订单的基础佣金部分照常分账。UnionAdapter 统一输出 n_base_fen（不含补贴类佣金）与 subsidy_commission_fen 两个字段：联盟给的是含补贴的总额 + 补贴明细时，n_base_fen = 总额 − 补贴；分字段返回时直接映射。B 只用 n_base_fen（BR-CALC-02）；R1 对账用 n_base_fen + subsidy_commission_fen 对联盟总额。自购报价不得包含只在分享场景才有的补贴类佣金。联盟未单列补贴类佣金时的处理见 BR-CALC-25。 | 待验证 | UnionAdapter 输出 n_base_fen / subsidy_commission_fen；orders.activity_type / subsidy_commission_fen；商品卡自购 / 分享报价；毛利报表；R1 对账 |
| BR-CALC-19 | **我方淘礼金订单的返利**<br>来自我方淘礼金推广位（pid_scene=taolijin）的订单，默认 rebate_mode=none：本人份额与直推份额都等于 0，全部 N 归平台以抵淘礼金预算。运营可按商品池条目把 rebate_mode 设为 normal，此时 B 按 BR-CALC-02 计算（先扣平台预留，再减 tlj_deduct_fen），再按 BR-CALC-04 分账。tlj_deduct_fen 取我方淘礼金发放记录 tlj_grants 中与该订单 (user_id, item_id) 匹配、状态为已使用、领取时间 ≤ paid_at 的最近一条记录的面额；匹配不到 → 订单进待处理表并告警，按 rebate_mode=none 计算。联盟 N 是否已扣红包由配置 union.taobao.tlj_n_net_of_redpacket 决定（默认 false，待 09 表验证）；为 true 时 tlj_deduct_fen = 0。其他推广者的淘礼金订单不归本 App（见 BR-ATTR）。 | 待决策 | tlj_pool_items.rebate_mode；tlj_grants（匹配键与状态）；配置 union.taobao.tlj_n_net_of_redpacket；splitCommission() 输入 activity_type；淘礼金卡片'预估返利'展示（默认不展示）；04 §2.2 pid_scene 表 |
| BR-CALC-20 | **报价预估与计算函数一致**<br>商品卡、商品详情、Agent 查返利、分享面板、订单预估、入账、补差必须调用同一个 splitCommission() 纯函数。报价计算只在本条维护（BR-PRICE-06 只引用）：报价 = splitCommission(B_quote) 中的本人份额，B_quote 按 BR-CALC-02 由 N_quote 扣除平台预留得出：B_quote = floor(N_quote × (10000 − reserve_bp) / 10000)，reserve_bp 取报价时刻生效规则版本中该平台的值（报价不含淘礼金扣除）。N_quote 由各平台 UnionAdapter.quoteN(product, sku, order_type) 输出，定义为'按报价时刻的券后价（final_price_fen）与该订单类型对应的推广者收入率算出、已扣技术服务费、不含补贴类佣金（淘宝佣金膨胀等，BR-CALC-18）、淘礼金与平台补贴的预估推广者收入'；全部整数运算、每次乘除后向下取整：gross = floor(final_price_fen × rate_bp / 10000)，fee = floor(gross × tech_fee_bp[platform] / 10000)，N_quote = gross − fee；rate_bp 由 Adapter 把平台佣金率字段按十进制字符串解析（不用浮点），各平台自购 / 分享口径差异在 Adapter 内换算（BR-CALC-17），计佣层不感知平台差异。字段口径未经 09 表 CAP-TB-04、CAP-JD-04、CAP-PDD-04 验证前，报价一律取可得口径中的较低值。报价使用报价时刻生效的规则版本（比例与预留比例）、查看者等级（未登录用注册默认等级 L1）与调用方传入的 order_type（各展示对象取值见 BR-PRICE-06）。报价不持久化。展示（标签、零值、区间、口径说明文案、金额格式）只按 BR-PRICE-06 / 07 / 08 / 17，本条不规定展示。 | 待验证 | UnionAdapter.&lt;platform>.quoteN()；GET /v1/products/{product_key} 预估返利；Agent rebate_quote 卡片；分享面板预估收益；packages/domain quoteRebate() / splitCommission()；配置 tech_fee_bp[platform]；specs/commission-examples.csv；验收：同输入时展示报价 = 入账预估 |
| BR-CALC-21 | **分账不变量与算例测试**<br>splitCommission() 必须以 fast-check 属性测试断言：每份 ≥ 0；Σ用户份额 ≤ B；平台留存 = B − Σ用户份额；相同输入输出相同；对全程 active 的受益人，多次调整后的份额 = floor(B_final × r)；forfeited 受益人份额恒为 0。specs/commission-examples.csv 必须在 W1 由财务给出 ≥ 20 例并全部作为参数化测试通过（算例表的来源已改为两家模型盲算 + 08 原文对照，负责人确认 5 条代表例，取代「由财务给出」：规划/11 §7.3 第 8 项，负责人 2026-10-01 确认）。生产每日 01:00 +08:00 校验前一自然日（+08:00）内快照或金额版本有变化的订单：每单 Σ当前应得额 ≤ base_fen；违例时告警，并冻结该订单全部受益人的提现，直至人工解除。 | 已确认 | packages/domain 测试；specs/commission-examples.csv；ledger_invariants.sql；每日 01:00 校验任务；CI 必过检查 |
| BR-CALC-22 | **规则发布与回滚流程**<br>修改 commission_rules 必须：超管或被勾选规则发布权限的账号起草（草稿记录 base_version_id）→ 系统校验 BR-CALC-06 完整性（含每个平台的 reserve_bp）与 BR-CALC-07 上限 → 用试算样本生成差异报告（含各平台预留比例与预留金额列） → 经 step-up 发布 → 在 effective_from 生效。起草与发布可为同一人（拍板第二批 §8 ADD-05）；发布时当前最新已发布版本 ≠ base_version_id 则拒绝，须基于新版本重新试算；上调、下调任一比例（含平台 reserve_bp）都只要求 effective_from ≥ 发布时刻，可设为发布时刻立即生效，对之后付款的订单生效（BR-CALC-11；2026-10-01 负责人确认，取消「下调提前 24 小时」）。已发布版本不可编辑；回滚通过发布新版本实现，未生效版本可按 BR-CALC-11 撤销。所有操作写审计日志。各平台预留比例与各等级比例开发期为占位值，上线前由超管在后台发布首个正式版本（拍板第二批 §8 ADD-03）。 | 已确认 | /admin/v1 commission-rules 接口（drafter_id、publisher_id 只记录，不做互斥校验；base_version_id）；后台分佣规则页；audit-logs；验收用例 AC-SET-待编号（参考文档编号 AC-MONEY-014，规划/ 未定义） |
| BR-CALC-23 | **入账后调整的记账时点与审批**<br>订单入账后（rebate_status=CREDITED）只在两类事件发生时生成调整，且只对差额 ≠ 0 的受益人生成调整行：(a) 联盟结算额写入或变更（orders.settle_commission_fen 按 BR-FUND-09 更新；对应 04 O8）——差额 &lt; 0 的受益人在该次更新的同一事务内立即记负向 SETTLE_ADJUST，不等审批；差额 > 0 的受益人生成补差候选（写入 BR-FUND-09 的 settle_adjust_batches），由超管或被勾选补差权限的账号 step-up 批准后记账（一人可完成，拍板第二批 §8 ADD-05），驳回则不记账并保留候选与驳回理由（分路按 BR-FUND-09 的整单比较：结算基数与 booked_base_fen 比大小，相等时比结算佣金与 booked_n_fen，此时受益人差额为 0、只调平台金额；按受益人状态规则 BR-CALC-09 处理后，同一次结算额变化里不会同时出现要立即扣的受益人负差和要审批的受益人正差）。rebate_status 始终保持 CREDITED（新基数大于 0，或新旧基数都为 0 时；原基数大于 0 而新基数为 0，含结算佣金为负，按迁移 R8 → CLAWED_BACK）；该单正差候选全部处理完（批准或驳回）之前记为补差未完成（对应单一 order_status 的 CREDITED），处理完后对应单一 order_status 的 SETTLED。(b) 部分退款 / 部分维权（BR-FUND-01 R9，对应 04 O10）——负向调整自动记账，不需审批，写 CLAWBACK（BR-FUND-08）。佣金下调（价保、比价降佣、联盟佣金调整）分两种：联盟下调的是结算佣金（新的结算记录）→ 按 (a)，即迁移 R10；结算记录未变、只有预估佣金变化 → 按 BR-FUND-01 R9b 只存档 est_commission_fen、不记账，生成差错单「入账后预估佣金变化」由人工核对（2026-10-03 资金规则对齐决-01 选 A）。月结口径下首次入账即按联盟结算额（BR-CALC-14），(a) 只在入账后联盟结算额再变化时出现。 | 已确认 | settlement 补差任务；settle_adjust_batches 表（BR-FUND-09）与后台批准页；BR-FUND-01 R9 / R9b / R10；ledger SETTLE_ADJUST / CLAWBACK；订单详情差额展示 |
| BR-CALC-24 | **分享单的分账**<br>分享单（order_type=share）只按订单归属用户（分享者）分账：分享者份额 = floor(B × r_own_bp / 10000)，r_own_bp 取 BR-CALC-06 中 (platform, 分享者等级, share) 行；直推份额 = floor(B × r_direct_bp / 10000)，受益人为分享者在 paid_at 时的直接上级，r_direct_bp 取 (platform, 上级等级, share) 行；所选版本 indirect_enabled=true 时，间推份额 = floor(B × r_indirect_bp / 10000)，受益人为分享者上级的上级，r_indirect_bp 取 (platform, 间推受益人等级, share) 行（BR-CALC-05）；各份额入对应受益人的单一余额（BR-FUND-13）。实际购买者即使也是本 App 用户，也不产生自购份额（每个子订单只有一个归属用户，见 BR-ATTR）。分享者经自己的分享链接下单时按哪种 buy_type 计算由 BR-ATTR 决定；决定之前这类订单按 self 计算（流水 REBATE_CREDIT）。 | 已确认 | packages/domain splitCommission()（share 分支）；commission_splits.beneficiaries；ledger SHARE_CREDIT / REFERRAL_CREDIT；分享面板预估收益；orders.buy_type（BR-ATTR） |
| BR-CALC-25 | **联盟未单列补贴类佣金时的处理**<br>某平台订单接口未把补贴类佣金与基础佣金分开返回（BR-CALC-18 无法拆出 subsidy_commission_fen）时，补贴部分是否分给用户由财务决定。决定前：N 整体计入 B，订单照常展示预估，但该平台订单在 settle_commission_fen 为空时不执行月结批次入账（R5 SETTLE_BATCH_CREDIT），等联盟结算值到达后再按 BR-CALC-14 入账（入库时置 orders.credit_requires_settle=true，判定同 BR-CALC-15，不使用 hold 字段）；并在 09 表记录该平台'补贴类佣金未单列'。 | 待决策 | 配置 union.&lt;platform>.subsidy_itemized；orders.credit_requires_settle；settlement 入账任务（结算前不入账分支，需并入 BR-FUND-04 入账守卫）；订单详情入账时间文案；规划/09_平台能力验证/（对应 CAP 的结论，按 09 README §0.4 回填） |
| BR-CALC-26 | **联盟报文金额与比例的换算**<br>联盟报文中的元金额必须按十进制字符串解析为分，禁止 parseFloat 与 Number 运算：小数不超过 2 位时精确换算；超过 2 位时按 floor 取整到分，原字符串保存在 raw_payload 供对账。报文字段为 JSON number 时，必须用保留数字原文的 JSON 解析（如 JSON.parse reviver 的 context.source 或 lossless-json）取得字面值字符串再解析，不得先转成 JS number。百分比字符串（如 '20.00' 表示 20%）同样按十进制字符串换算为 bp，超过 2 位小数时 floor；字段单位（百分比还是万分比）以 09 表验证结论为准。转换函数放在 packages/money：yuanStrToFen()、pctStrToBp()；非法格式（空串、非数字、科学计数法无法精确解析）抛错，订单进待处理表，不得按 0 处理。 | 默认假设 | packages/money yuanStrToFen() / pctStrToBp()；UnionAdapter 报文解析；orders.raw_payload；lint 规则（Adapter 目录同样禁止 parseFloat） |
| BR-CALC-27 | **每单四段金额与平台预估利润**<br>每个已生成分佣快照的子订单，必须在快照生成时（BR-CALC-10）以及此后每写入一个 commission_split_amounts 新版本时，在同一事务按该版本落四段金额（整数分）：① 联盟佣金总额 n_total_fen = n_base_fen + subsidy_commission_fen（BR-CALC-03 / BR-CALC-18 输出，已扣技术服务费，可为负）；② 基数前扣除 pre_base_deduct_fen = n_total_fen − base_fen（含补贴类佣金、平台预留 reserve_fen、淘礼金扣除 tlj_deduct_fen、负 N 置 0 的部分，见 BR-CALC-02）；③ 分佣基数 base_fen（B）；④ 平台预估利润 platform_est_profit_fen = n_total_fen − 该版本 Σ用户份额 amount_fen（forfeited 为 0，held 仍计入） − tlj_redpacket_fen。tlj_redpacket_fen = 我方淘礼金订单（pid_scene=taolijin）按 BR-CALC-19 的匹配键在 tlj_grants 中匹配到的红包面额，不论 rebate_mode；union.taobao.tlj_n_net_of_redpacket=true 或非我方淘礼金订单为 0；我方淘礼金订单匹配不到时 tlj_redpacket_fen 与 platform_est_profit_fen 记 null，报表显示'待核'，不得按 0 计算。四段金额只用于毛利报表、经营看板与 R1 对账，不参与分账，不向用户展示。 | 待决策 | commission_split_totals（新增，唯一 (order_id, commission_version)，只追加）；orders 冗余当前版本四段金额；毛利报表与经营看板「平台预估利润」；R1 联盟对账；specs/commission-examples.csv |

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

- 状态：已确认（拍板第二批 TRADE-02：以负责人 2026-10-01 决定为准，先扣平台预留再按等级分账，机制见 docs/changes/20261001-平台预留比例.md；各平台 reserve_bp 开发期为占位值，上线前由超管在后台填写，拍板第二批 §8 ADD-03，取代 FUND-21「W1 随 ledger-rules.md 一次给出」）
- 默认值：B = max(0, floor(N_base × (10000 − reserve_bp) / 10000) − tlj_deduct_fen)；种子版本各平台 reserve_bp = 0，上线前由负责人在后台按平台填写（例：淘宝 1300）
- 决策人：负责人（机制）；超管在后台填写（各平台取值）
- 依赖平台能力：无
- 取代：
  - 规划/08 BR-CALC-02 拍板第一批写法（2026-09-30 负责人同意默认，变更记录 20260930 §2）：「分佣基数 B = max(0, N_base − tlj_deduct_fen)……不再扣除任何平台预留」；原默认值：「不设 reserve_bp；平台留存靠 BR-CALC-07 的 8000 上限保证」（2026-10-01 负责人改为先扣预留，拍板第二批 TRADE-02 确认以 10-01 为准）
  - PRD修订_后端功能规划 §2.6 / §0.4 B10：「B = N − floor(N × reserve_bp[platform] / 10000)，预留淘宝 15%、京拼唯 10%、抖音 15%、美团饿了么 2%；约束 r_buyer+r_l1+r_l2 ≤ 10000」
  - 参考_花卷云功能查漏底稿 §2 分佣基数：「实际计算佣金 = 联盟预估佣金 × (1 − 平台预留%)」
  - 返利 App PRD v2.1 §11.3：「净佣金 = 结算佣金 × (1 − 平台技术服务费率)（由我方自行乘费率）」
  - 本条正文 2026-10-03 前只写「取值阶段：…之后预估字段的变化只存档，不参与计算」，没有写明它适用于哪些按基数判断的规则（BR-FUND-08 ① 曾取「本次更新的那个字段」、BR-FUND-03 与 BR-FUND-07 曾取预估最新值；补「本条的取值阶段适用于所有按基数做判断的规则」与「联盟给出的任何金额都是 N 口径」两句）（2026-10-03 资金规则对齐（负责人批准），方案 §1、§2，同-01、同-02）
  - 本条正文 2026-10-03 写回时只写「…先按本条换算成 B，再重拆、再与 booked_base_fen 比较。」（没有写换算不是一一对应；BR-FUND-09 据此只比较 B，基数相等而联盟佣金不同时漏调平台金额）（2026-10-03 资金规则对齐评审后修改，同步修正，方案 §13.6 第 2 条）
- 来源：docs/changes/20261001-平台预留比例.md；docs/changes/20261001-拍板第二批.md（TRADE-02、FUND-21、§8 ADD-03）；规划/01_需求规划.md §3 分账口径；规划/04_数据模型与契约.md §1 术语表；规划/06_待补信息清单.md Q-B1；PRD修订_后端功能规划 §2.6；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

| 阶段 | N_base 取值 |
|---|---|
| settle_commission_fen 为空（PAID / RECEIVED，预估阶段；月结口径下入账时必有结算值，BR-CALC-14） | 最新联盟预估收入 `est_commission_fen`（扣除补贴类佣金后） |
| settle_commission_fen 非空 | 联盟结算收入 `settle_commission_fen`（扣除补贴类佣金后）；预估字段再变只存档 |

- 结算值本身再变（如结算后维权），按 BR-CALC-15 或 BR-FUND-08（R8，对应 04 O9）处理。
```
N_pos       = max(0, N_base)
after_rsv   = floor(N_pos × (10000 − reserve_bp) / 10000)   // mulDivFloor
reserve_fen = N_pos − after_rsv                               // 归平台，含取整尾差
B           = max(0, after_rsv − tlj_deduct_fen)
```

- 例：联盟返回推广者预估收入 14.52 元、无补贴、非淘礼金，reserve_bp=0 → N_base=1452 → B=1452。
- 例：N_base=1000、淘宝 reserve_bp=1500 → after_rsv=850、reserve_fen=150 → B=850；分账见 BR-CALC-04 例 4。
- 例（尾差）：N_base=1452、reserve_bp=1500 → floor(1452×8500/10000)=floor(1234.2)=1234 → reserve_fen=218，B=1234。
- 例（改预留）：v5 淘宝 reserve_bp=1300，v6 改为 1500、effective_from=2026-10-02T00:00:00+08:00 → paid_at 10-01T23:59:59 的订单按 1300，paid_at 10-02T00:00:00 起按 1500；v5 期间已生成的快照不重算。
- 维度：每个规则版本对 commission.platforms 中每个平台一个 reserve_bp（缺失拒绝发布，BR-CALC-06）；不按等级、订单类型、个人设置。改预留 = 发布新规则版本（BR-CALC-22），按 paid_at 选版本（BR-CALC-11），不回溯。
- 快照生成后，入账（BR-CALC-14）、部分退款与结算调整（BR-CALC-09、BR-CALC-15、BR-CALC-23）按新 N_base 重算 B 时，一律用快照中的 reserve_bp，不取新版本的值。
- 平台最低留存：用户份额合计仍以 B 为基数受 BR-CALC-07 的 8000 上限约束，预留在此之外另归平台。
- 异常：联盟 N 为负（冲正）→ raw_n_fen 记原值，B=0，各受益人新应得为 0；已入账部分按 BR-CALC-09 求差扣回（流水类型 CLAWBACK / SETTLE_ADJUST 见 BR-FUND-08、BR-FUND-09；B 由 >0 变 0 时入账前走 R6 → VOID、入账后走 R8 → CLAWED_BACK，对应 04 O4 / O9）。负值差额只进 R1 对账，不进分账。
- 后端功能规划与花卷云底稿要求的「四段金额」中的平台预留计入 BR-CALC-27 的基数前扣除（pre_base_deduct_fen）。后端功能规划的预留初始值（淘宝 15%、京拼 10% 等）与 ≤ 10000 约束不沿用，取值以后台设置为准，上限以 BR-CALC-07 为准。
- 淘礼金首版不接入（D7，拍板第二批 AI-01），首版 tlj_deduct_fen 恒为 0；接入时按 BR-CALC-19 复核。
- 按 C-01 默认处理（状态名与迁移编号改用 BR-FUND-01），已由负责人确认 2026-09-30。

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
- 来源：docs/changes/20261001-间推二级奖励.md；docs/changes/20261001-平台预留比例.md；规划/01_需求规划.md §3 分账口径；规划/02_系统架构.md §8.3 典型分录；规划/04_数据模型与契约.md §2.2、§2.4；规划/06_待补信息清单.md Q-B1；PRD修订_后端功能规划 §2.6 账户映射；docs/changes/20261001-拍板第二批.md §8 ADD-06
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

```
own      = floor(B × r_own_bp    / 10000)   // 受益人 = 订单归属用户
direct   = floor(B × r_direct_bp / 10000)   // 受益人 = 归属用户 paid_at 时的上级
indirect = enabled ? floor(B × r_indirect_bp / 10000) : 0   // 受益人 = 直推上级 paid_at 时的上级（BR-CALC-05）
platform = reserve_fen + (B − own − direct − indirect)   // reserve_fen 见 BR-CALC-02；括号内记 platform_retain_fen，≥ 0 由 BR-CALC-07 保证
```

| 例 | B | 类型 | 比例（本人/直推/间推） | 本人 | 直推 | 间推 | 平台 |
|---|---|---|---|---|---|---|---|
| 1 | 1234 | self | 5000/1000/0 | 617 | 123 | 0 | 494 |
| 2 | 1234 | self，无上级 | 5000/—/— | 617 | 0 | 0 | 617 |
| 3 | 1 | self | 5000/1000/0 | 0 | 0 | 0 | 1 |
| 4 | N_base=1000，reserve 1500 → B=850 | self | 5000/1000/0 | 425 | 85 | 0 | 340 + 预留 150 = 490 |

- 例 1–3 的 reserve_bp=0（B = N_base）。例 4 中上级为 L2、其 (taobao, L2, self).r_direct_bp=1000，本人 L1 r_own=5000；若本人为 L3 且 r_own=6500 → 本人 floor(850×6500/10000)=552、直推 85、平台 213 + 150 = 363。
- 上表为间推关闭（indirect_enabled=false，间推列恒为 0）的算例；开启时的算例见 BR-CALC-05（例 4 开启 r_indirect=500 → 间推 floor(42.5)=42，平台 298 + 150 = 448）。
- 分享单算例见 BR-CALC-24。
- 角色枚举：`self`、`share`、`direct`、`indirect`；`indirect` 只在所选版本 indirect_enabled=true 时写入（见 BR-CALC-05）。
- 流水类型：self → REBATE_CREDIT；share → SHARE_CREDIT；direct → REFERRAL_CREDIT（sub_type=DIRECT）；indirect → REFERRAL_CREDIT（sub_type=INDIRECT）（见 BR-FUND）；各份额都入受益人的单一余额（BR-FUND-13，拍板第二批 §8 ADD-06；原表「本人 → SELF、直推 → PROMO」取消）。所得类型与税目见 BR-FUND。
- 间推份额按 D8 两级计酬补入（拍板第一批 §3；2026-10-01 改为规则版本开关，docs/changes/20261001-间推二级奖励.md），相关规划文档已随 10-01 变更同步。
- BR-ATTR 定稿前 buy_type 默认：订单能识别出购买者就是归属用户本人（同一 relation_id / special_id）→ self，否则 → share。

#### BR-CALC-05 细则 · 间推比例与开关

- 状态：已确认（两级计酬结构：负责人 2026-09-30，docs/changes/20260930-拍板第一批.md §3 D8；规则版本开关与两级上限：负责人 2026-10-01，docs/changes/20261001-间推二级奖励.md；发布由超管或有权限账号一人 step-up 完成，拍板第二批 §8 ADD-05；间推比例开发期为占位值、上线前超管在后台填写，ADD-03）
- 默认值：indirect_enabled=false（上线默认关闭）；开启时的比例占位 r_indirect_bp = 500（5%），由超管在后台发布规则版本时填写；关闭版本中 r_indirect_bp 存 0，占位值不影响上线
- 决策人：负责人（结构、开启时机）；超管在后台填写（比例数值）
- 依赖平台能力：无
- 取代：
  - 规划/08 BR-CALC-05 原文（2026-09-30，「间推比例固定为 0」）：「r_indirect_bp … CHECK (r_indirect_bp = 0)，后台与 API 不暴露该列，splitCommission() 不读取、不产生 indirect 角色，后台界面不得出现间推配置项。解锁只能在取得书面法律意见后，通过数据库迁移 + 负责人决策完成」
  - 返利 App PRD v2.1 §11.3：「间推 = floor(净佣金 × 间推比例)，MVP 默认 0（可配）」
  - PRD修订_后端功能规划 §2.6：「parent_l2 = 0 写入公式与 beneficiaries」
  - 本条旧默认值（2026-09-30 前）：「间推 = 0 且后台不可开启（D8 默认决策，理由：两层计酬不在监管安全港内）」，旧决策人：法务
  - 拍板第一批写法（2026-09-30）：「间推比例开发默认 0bp，后台可配、随时调整，只对调整后生成分佣快照的订单生效」（无版本开关与第二人审批；2026-10-01 改为规则版本开关 + 第二人审批，按 paid_at 选版本）
  - 本条 2026-10-01 写法：「发布 indirect_enabled=true 的版本须 step-up + 财务角色第二人审批 + 审计」「finance 起草 → 另一名 finance 审批（第二人）→ super 经 step-up 发布」「间推比例数值由负责人 / 财务 W1 随 ledger-rules.md 一次给出」（拍板第二批 §8 ADD-05、ADD-03）
- 来源：docs/changes/20261001-间推二级奖励.md；docs/changes/20260930-拍板第一批.md §3（D8、BR-INV-12、BR-CALC-05 行；「间推比例」行）、§6；docs/changes/20261001-拍板第二批.md（FUND-21、OPS-02、§8 ADD-03、ADD-05）；规划/00_总览与决策.md D8；规划/01_需求规划.md §3；规划/06_待补信息清单.md Q-B1；PRD修订_后端功能规划 §0.4 B6、§2.10

| 情形（开关开启时，均按 paid_at 时刻关系与状态） | 间推处理 | 对齐的直推规定 |
|---|---|---|
| 归属用户无上级，或上级无上级 | 间推份额 0（归平台），事后绑定不补 | BR-CALC-12「paid_at 时尚无上级 → 直推份额为 0，事后绑定不补」 |
| 快照时上上级不存在或已注销 | forfeited，份额归平台，不顺延、不转给他人 | BR-CALC-13 快照时判定 |
| 入账时上上级已注销、banned 或已识别未满 18 周岁 | forfeited，份额计入 COMMISSION_REVENUE | BR-CALC-13 入账时判定 |
| 入账时上上级 frozen / appealing | held，状态解除后在后续月结批次补入账（BR-FUND-01 R5a） | BR-CALC-13 held |
| 上级（中间一级）被封禁、冻结、注销 | 间推受益人独立判定，不因上级状态受影响；上级的份额按 BR-CALC-13 归平台，不转给间推受益人 | BR-CALC-13「不得转给其他受益人」 |
| 调整、补差 | 按 BR-CALC-09 全额重算求差，forfeited 恒 0 | BR-CALC-09 |

- 例（关闭）：A 邀请 B、B 邀请 C，C 自购 B=1000，版本 indirect_enabled=false → C 500、B 100、A 0、平台 400。
- 例（开启，r_indirect=500）：同上 → C 500、B 100、A 50、平台 350；B=1234 → 617 / 123 / 61（floor(61.7)）/ 平台 433。
- 例：开启版本中 C 的上级 B 在 paid_at 时没有上级 → 间推 0，平台多得该份额；A 在 paid_at 之后才成为 B 的上级 → 不补。
- 例（depth 3）：D 邀请 A、A 邀请 B、B 邀请 C，C 自购 → 只计 B（直推）与 A（间推，开关开启时），D 在任何版本都不计酬。
- 例（开关切换不回溯）：v1 indirect_enabled=false；v2 开启、r_indirect=500、effective_from=T → paid_at &lt; T 的订单不产生间推（即使 T 之后才生成快照），paid_at ≥ T 的按 v2 计（BR-CALC-11）；已生成快照不重算。
- 例：异常数据使间推受益人 = C 本人或 = B → 间推份额归平台并告警。
- 发布 indirect_enabled=false 但某行 r_indirect_bp ≠ 0 → 拒绝；r_indirect_bp > 8000 → DB CHECK 失败。跨表约束（版本开关 × 行比例）由发布接口校验，并由属性测试覆盖。
- 发布 indirect_enabled=true 的版本：超管或被勾选规则发布权限的账号起草并经 step-up 发布，一人可完成，写审计（拍板第二批 §8 ADD-05）；试算报告增加间推份额列（BR-CALC-22）。止损 = 发布 indirect_enabled=false 的新版本，对之后付款的订单生效，已生成快照不改（纠正走 BR-CALC-23）。
- depth ≥ 3 的祖先永不进入受益人；splitCommission() 只读取两层，属性测试断言 depth ≤ 2。增加层级须新的负责人决策。
- 中间一级 P 注销（deletion_status=done）后，仍按 paid_at 时刻的 relation_change_logs 重放确定 P 的上级 G（P 注销不切断历史 P→G 关系，例见 BR-CALC-13 细则）；默认处理。
- 推送：跟单与收益推送发给全部受益人，含间推受益人（拍板第二批 OPS-02），模板与时点只在 BR-TEXT-09 维护。
- 不收入门费：用户成为直推或间推受益人不以任何付费、购买、充值为条件；等级 L1–L3 晋升只看本人推广订单，不看下级人数（BR-INV-15）。
- 法律意见（06 Q-F5）由负责人跟进，不作技术闸门。
- 拍板第一批列出的 D8 同步落点（00、01、04、06、13、14、README、10 等）已随 docs/changes/20261001-间推二级奖励.md 同步。

#### BR-CALC-06 细则 · 比例配置维度与默认值

- 状态：已确认（结构：比例按 平台 × 等级 × 订单类型 设置、只按等级不设个人专属比例、每个平台一个预留比例，负责人 2026-10-01 确认，docs/changes/20261001-平台预留比例.md；各项数值开发期为占位值，上线前由超管在后台填写，之后随时可改、立即生效，拍板第二批 §8 ADD-03）
- 默认值：所有平台、所有等级、两种订单类型：r_own 5000、r_direct 1000、r_indirect 0（开关关闭）；各平台 reserve_bp 0；理由：沿用 规划/06 Q-B1 默认，平台留存 40%，满足 BR-CALC-07，且单位经济模型（01 §8.3）尚未定稿
- 决策人：负责人（结构）；超管在后台填写（数值）
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 §2.10：「r_buyer 按等级、平台配置，r_l1 不分平台与订单类型」
  - 本条 2026-10-01 写法：「各项数值由负责人 / 财务 W1 随 ledger-rules.md 一次给出」「默认种子数据（W1 财务签字前按此开发与测试）」（拍板第二批 §8 ADD-03）
  - 本条旧写法（2026-09-30 前）：「commission_rules 每行 = (rule_version_id, platform, level, order_type, r_own_bp, r_direct_bp)」（不含 r_indirect_bp 与平台预留；间推按旧 BR-CALC-05 固定为 0）
- 来源：规划/01_需求规划.md §3、§8.3；规划/06_待补信息清单.md Q-B1；docs/changes/20261001-间推二级奖励.md；docs/changes/20261001-平台预留比例.md；docs/changes/20260930-拍板第一批.md §3（D8 行、「间推比例」行）、§5、§6；docs/changes/20261001-拍板第二批.md（FUND-21、§8 ADD-03）；返利 App PRD v2.1 §19.1 D5、§19.2 G1；PRD修订_后端功能规划 §12.1 B11
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

默认种子数据（开发期占位值，按此开发与测试；上线前由超管在后台发布正式版本），commission.platforms = [taobao, jd, pdd]：

| platform | level | order_type | r_own_bp | r_direct_bp | r_indirect_bp |
|---|---|---|---|---|---|
| taobao / jd / pdd | L1、L2、L3 | self | 5000 | 1000 | 0 |
| taobao / jd / pdd | L1、L2、L3 | share | 5000 | 1000 | 0 |

- 种子版本 indirect_enabled=false，r_indirect_bp 全为 0；开启时的占位比例 500 见 BR-CALC-05。
- 种子版本 commission_rule_reserves：taobao / jd / pdd 各一行，reserve_bp 均为 0；上线前由负责人在后台按平台填写新版本（BR-CALC-02）。
- 上述种子值只用于开发与测试；上线取值由超管在后台按 BR-CALC-22 发布规则版本填写，之后随时可改、立即生效（拍板第二批 §8 ADD-03）。

- 同一版本内 3 平台 × 3 等级 × 2 类型 = 18 行比例（每行三项比例都必须有值，r_indirect_bp 可为 0）+ 3 行预留必须齐全。
- 例：(pdd, L2, self) 订单，归属用户 L2 → r_own 取 (pdd, L2, self).r_own_bp=5000；上级 L1 → r_direct 取 (pdd, L1, self).r_direct_bp=1000；间推开启时上上级 L3 → r_indirect 取 (pdd, L3, self).r_indirect_bp。
- 调整：自购、直推、间推比例与平台预留比例都只能通过发布新规则版本调整（BR-CALC-22），可立即生效；按订单 paid_at 选版本（BR-CALC-11），改后付款的订单用新值，已生成快照不回溯。
- 合计上限：发布校验把 r_indirect_bp 计入，见 BR-CALC-07。
- 美团（P1，D15）接入前先把 meituan 加入 commission.platforms，并补齐 6 行比例与 1 行预留，否则新版本发布被拒。

#### BR-CALC-07 细则 · 比例合计上限校验

- 状态：已确认（拍板第二批 FUND-15：负责人 2026-10-01 按当前默认签字，用户份额合计最高 80%；原为待决策，金额口径）
- 默认值：每个 (平台, 订单类型)：max_等级(r_own) + max_等级(r_direct) + max_等级(r_indirect) + 活动加成 ≤ 8000，单项 0–8000（06 Q-B1 默认；间推项按 D8 两级计酬计入，开关关闭的版本 r_indirect 为 0；负责人 2026-10-01 按此签字，拍板第二批 FUND-15）
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 §2.6：「约束 r_buyer_bp + r_l1_bp + r_l2_bp ≤ 10000」
  - 返利 App PRD v2.1 §11.3：「约束 返利 + 分佣 ≤ 净佣金」
  - 本条旧写法（2026-09-30 前）：「max_等级(r_own_bp) + max_等级(r_direct_bp) + 活动加成_bp ≤ 8000」（不含间推）
- 来源：规划/01_需求规划.md §3；规划/06_待补信息清单.md Q-B1；docs/changes/20261001-间推二级奖励.md；docs/changes/20260930-拍板第一批.md §3「间推比例」行（三项合计上限沿用）；docs/changes/20261001-拍板第二批.md（FUND-15）；PRD修订_后端功能规划 §1.6、§10.1 AC-MONEY-014
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 用最大值相加是因为本人、上级、间推受益人可能处于不同等级。
- 例：开启间推，taobao/self 下 max r_own=6500、max r_direct=1000、max r_indirect=500 → 8000，通过；r_indirect 改为 600 → 8100，拒绝（比例仅为算例）。
- 例：taobao/self 下 L3 r_own=6500、L2 r_direct=1500 → 8000，通过；把 5000 误填为 50000 → 单项 > 8000，拒绝（对应后端功能规划 AC-MONEY-014；规划/ 中的 AC-SET 编号待 规划/05 分配）。
- 活动加成在 MVP 恒为 0（奖励活动 P1），P1 加入时计入同一上限。
- 由此平台留存 ≥ B × 20%（舍入尾差另计归平台）。
- 按 D8 两级计酬把间推计入上限（拍板第一批 §3；2026-10-01 间推变更），相关规划文档已随 10-01 变更同步。

#### BR-CALC-08 细则 · 舍入与尾差归属

- 状态：已确认（拍板第二批 FUND-15：负责人 2026-10-01 按当前默认签字，每份向下取整、零头归平台；原为待决策，金额口径）
- 默认值：每份 floor，尾差归平台（06 Q-B1 默认）
- 决策人：财务
- 依赖平台能力：无
- 取代：无
- 来源：规划/01_需求规划.md §3；规划/02_系统架构.md §8.3；规划/06_待补信息清单.md Q-B1；docs/changes/20261001-拍板第二批.md（FUND-15）；返利 App PRD v2.1 §6；开发任务拆解_v1 BF-01
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：B=1235、5000/1000 → 617.5→617、123.5→123、平台 495。
- 例：B=9、5000/1000 → 4、0、5。
- 手续费向上取整属于提现，见 BR-FUND；技术服务费扣除向上取整见 BR-CALC-03。
- 性质：Σ用户份额 ≤ B；每份 ≥ 0；平台留存 ≥ 0。

#### BR-CALC-09 细则 · 调整按新基数全额重算

- 状态：已确认（拍板第二批 FUND-15：负责人 2026-10-01 按当前默认签字，金额变化时按新基数整体重算求差；注销用户的扣回改记平台坏账按拍板第二批 FUND-09）
- 默认值：全额重算求差；forfeited 恒为 0（申诉恢复除外，BR-CALC-13）；封禁或注销后正差归平台；注销后负差记平台坏账（理由：多次调整后每份仍等于 floor(B_final × r)，与对账口径一致；不向已剥夺份额的受益人补发；墓碑账户不再承接扣回）
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - 规划/02_系统架构.md §8.3：「月结补差（结算额比已入账少 100）：按快照比例拆分，借用户与平台收入」
  - 本条旧写法：「受益人已注销或 risk_state=banned 时，负向差额照常扣回」（注销用户改记平台坏账，拍板第二批 FUND-09，与 BR-ID-28 一致）
  - 本条细则末行 2026-10-03 前写法：「同一受益人累计扣回不得超过已入账额（BR-FUND-19 不变量 ④）。」（恢复后再扣回、改派后扣回时不成立，改为净额不为负）（2026-10-03 资金规则对齐（负责人批准），方案 §3，同-05）
  - 本条正文 2026-10-03 前写法：「再以'差额 = 新应得 − 已入账（或原预估）'生成调整」，受益人状态规则只列 forfeited、banned、已注销、frozen / appealing 四种（「已入账」的口径未写明含恢复与改派凭证；没有已识别未成年受益人的调整规则；没有写归平台的正差、改记坏账的负差之后算不算进净额，封禁、注销受益人会被多扣或重复冲坏账）（2026-10-03 资金规则对齐（负责人批准），方案 §6.2、§7.6，同-09、同-26）
- 来源：规划/02_系统架构.md §8.3；docs/changes/20261001-拍板第二批.md（FUND-09、FUND-15）；PRD修订_后端功能规划 §2.7 入账金额、失效与扣回（金额 = 已入账 − 新应得）；docs/changes/20261001-拍板第二批.md §8 ADD-07；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：已入账 B=1235 → 本人 617、直推 123。结算 B_new=1134 → 本人 floor(567)=567、直推 floor(113.4)=113；调整 −50、−10，平台留存由 495 变为 454。
- 错误做法：ΔB=−101，floor(−101×0.5)=−51、floor(−101×0.1)=−11，与全额重算相差 1 分，多次调整后会累积。
- 例（forfeited）：上级快照时已注销（直推 forfeited，0），结算上调 B 1234→1500 → 本人 617→750（+133），直推不生成调整，平台 617→750。
- 例（入账后被封禁）：本人已入账 617，结算上调到 B=1500，本人 risk_state=banned → 应得 750 的正差 133 归平台，本人不补。
- 例（注销后扣回）：直推上级已入账 123，之后进入注销 processing / done；订单部分退款使其应得变为 100 → 不写该用户 CLAWBACK，−23 记平台坏账（BR-ID-28，分录见 BR-FUND）；注销完成时的余额转平台收入（拍板第二批 FUND-09）；余额为负的用户不能注销（BR-ID-27，拍板第二批 §8 ADD-07）。
- 只对差额 ≠ 0 的受益人生成调整行。何时记账、是否审批见 BR-CALC-23。
- 例（2026-10-03 资金规则对齐 E-17；淘宝预留 2000，本人 5000、直推 1000，结算佣金 1000 入账：U1 400、P1 80、平台 520）：(a) U1 入账后被封禁，结算佣金改为 1200（新基数 960）的正差获批 → U1 的 +80 归平台，P1 +16，平台 +184，U1 净额仍 400。(b) 接 (a)，结算佣金再改为 900（新基数 720）→ U1 新应得 min(360, 400) = 360，扣 40（不按 480 扣 120）；P1 −24；平台冲回 236。(c) U1 入账后注销完成，结算佣金改为 900 → U1 的 −40 记平台坏账并计入其净额（360）；再改为 600（新基数 480）→ 只再记坏账 120。(d) P1 入账后被识别为未满 18 周岁，同 (a) 的正差 → P1 的 +16 归平台，P1 不补。
- 例（申诉恢复后，2026-10-03 资金规则对齐 X-01 变体）：预留 0、本人 5000、没有上级，B=1000。U1 入账时封禁，500 归平台；申诉撤销后按 BR-FUND-22 ③ 补发 500；之后结算佣金改为 800 → U1 按重拆份额 400 算应得（不再按被剥夺取 0），扣 100；平台应得 400，冲回 100；UNION_RECEIVABLE 净额 800，不生成补差候选。
- 同一受益人在该子订单上的净额不得为负（BR-FUND-19 不变量 ④，净额口径同 BR-FUND-08）。

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
  - 本条正文与细则表 2026-10-03 前写法：「未归因订单已为 rebate_status=VOID…时找回通过或改派，按 BR-FUND-01 R3b 只写 user_id、user_basis（BR-ATTR-09）、locked=true…」「| 未归因且已 VOID（对应 04 INVALID），找回通过或改派 | R3b：只写 user_id、user_basis、locked=true… |」（找回不受理 VOID 订单，负责人选决-07 A；同步重跑归属成功补入 R3b）（2026-10-03 资金规则对齐（负责人批准），方案 §6.11，同-17、决-07）
- 来源：规划/01_需求规划.md §3；规划/02_系统架构.md §5.2；规划/04_数据模型与契约.md §3.2、§4.1 O1/O2/O11；docs/changes/20261001-平台预留比例.md；PRD修订_后端功能规划 §2.5、§3.1；docs/changes/20261001-拍板第二批.md §8 ADD-06；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：5 处（计数仅作记录，落点见 README §0.6）

| 场景（platform_status / rebate_status） | 快照时点 |
|---|---|
| 首次入库即 PAID 且已归因 | 首次入库事务（R2，对应 04 O2） |
| 预售：先 DEPOSIT_PAID（已归因，rebate_status=ESTIMATED，预估 0），后付尾款 | platform_status 迁到 PAID 的事务（P2，对应 04 O2），定金阶段无快照 |
| 回扫晚到，首次入库已是 RECEIVED / SETTLED 且已归因 | 首次入库事务（R2，同事务按 R4 进 WAITING） |
| 首次入库未归因（UNATTRIBUTED） | 找回通过 / 后台改归属时（R3，对应 04 O11）；platform_status 仍为 DEPOSIT_PAID 时推迟到 P2 |
| 未归因且已 VOID（对应 04 INVALID），后台改派或同步重跑归属成功（找回不受理 VOID，决-07 A） | R3b：改派只写 user_id、user_basis=admin、locked=true；同步归属只写 user_id、user_basis=param；不生成快照，rebate_status 保持 VOID；订单详情显示失效原因 |
| 首次入库即失效（platform_status=INVALID） | 不生成 |

存储：
- `commission_splits`（唯一 order_id = orders.id，只写一次）：rule_version_id、order_type、activity_type、rebate_mode（none/normal，非淘礼金为 null）、paid_at、paid_at_source、raw_n_fen、subsidy_commission_fen、reserve_bp（所选版本该平台的预留比例，不可改）、reserve_fen（生成时值）、tlj_deduct_fen、base_fen、platform_retain_fen（生成时值）、beneficiaries[user_id, role, ratio_bp, level, initial_status, forfeit_reason]、created_at（单一余额后不带 account_type，拍板第二批 §8 ADD-06）。
- `commission_split_amounts(order_id, commission_version, user_id, role, base_fen, amount_fen, created_at)`：唯一 (order_id, commission_version, user_id, role)，只追加不更新；快照生成时写 commission_version=1 的行；当前应得额取最大 commission_version 的行；该版本平台留存 = base_fen − Σamount_fen。
- `commission_split_beneficiary_events(order_id, user_id, role, status ∈ {active, held, forfeited}, reason, created_at)`：只追加；当前状态取最后一条。
- 重放同一订单事件不得重建快照（唯一约束 order_id）。
- 四段金额与平台预估利润随快照与每个金额版本落库，见 BR-CALC-27。
- 「VOID 订单只设 user_id」这一动作不改变 rebate_status，对应 BR-FUND-01 R3b（后台改派或同步重跑归属成功：rebate_status 保持 VOID，只写 user_id、user_basis，改派另置 locked=true，不生成快照、无分录；C-27 (c)）；用户找回不受理 VOID 订单（2026-10-03 资金规则对齐决-07 选 A，原写「找回通过或改派」）。
- BR-ATTR-01（DEPOSIT_PAID 也生成快照、关系与等级取生成时刻）与 BR-FUND-01 R3（比例与用户关系取批准时刻）中与本条、BR-CALC-11、BR-CALC-12 不一致的写法，以本主题为准。
- 按 C-01、C-06 默认处理（状态名改用 BR-FUND-01；生成时点按本条），已由负责人确认 2026-09-30。

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
- 找回、改派订单（R3）同样按 paid_at 选版本；BR-FUND-01 R3「比例取批准时刻」以本条为准。按 C-01、C-06 默认处理，已由负责人确认 2026-09-30。

#### BR-CALC-12 细则 · 等级与上级的取值时点

- 状态：默认假设
- 默认值：等级与上级都按 paid_at 取值；日志缺失按 L1（理由：与 PRD'等级变更以付款时间为准'一致，结果不受入库或找回延迟影响；缺日志时取当前等级可能多付且不可重放）。备选：上级按快照时 parent_id（找回单按找回时的上级计），需负责人拍板才改
- 决策人：负责人
- 依赖平台能力：无
- 取代：无
- 来源：返利 App PRD v2.1 §11.3；规划/04_数据模型与契约.md §3.2 users.parent_id；docs/changes/20261001-间推二级奖励.md；PRD修订_后端功能规划 §2.10 等级、后台改上级
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 例：用户 10-20T10:00+08:00 由 L1 升 L2；订单 paid_at 10-20T09:59 于 10:03 入库 → 按 L1；paid_at 恰为 10:00:00 → 按 L2。
- 例：用户 10-05 付款，10-12 才绑定邀请码，订单 10-20 经找回生成快照 → 直推 0，新上级不因旧订单获益。
- 例（间推开启）：C 的上级 B 于 10-10 绑定上级 A；C 的订单 paid_at 10-09 → 间推 0（归平台）；paid_at 10-11 → 间推受益人 A，等级取 A 在 10-11 的等级。
- 上级在快照后被改绑（后台改上级仅限无订单用户）不影响已生成快照。
- 游客报价按注册默认等级（见 BR-CALC-20）。
- 找回、改派订单（BR-FUND-01 R3）的等级与上级同样取 paid_at 时刻，不取批准时刻或快照生成时刻；BR-INV-13「排除 paid_at 早于绑定的订单」与本条一致。按 C-06 默认处理，已由负责人确认 2026-09-30。

#### BR-CALC-13 细则 · 受益人失效时份额归平台

- 状态：已确认（拍板第二批 FUND-17：held 满 30 天无结论告警、由人工决定、不自动处理；同批 FUND-10（未成年）、FUND-14（申诉恢复）、OPS-07（订单申诉不改账户状态）已写入）
- 默认值：快照时只剥夺已注销或不存在的受益人；入账时 banned / 已注销 / 已识别未满 18 周岁（推广份额）→ forfeited，frozen / appealing → hold，冷静期照常（理由：永久失效才剥夺，临时风控状态只延后，避免事后证明无辜的用户永久失去返利；先入账后封禁无法扣回，所以冻结期间不入账）
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 本条旧写法：「若风控流程允许 banned 事后解除，已 forfeited 的份额只能经 ADMIN_ADJUST 人工补发（见 BR-FUND），系统不自动补」（拍板第二批 FUND-14 改为申诉恢复差错单）
  - 本条旧未决：「held 状态最长保留多久、风控结论超期未出时如何处理」（拍板第二批 FUND-17 已定）
  - 本条 2026-10-01 写法：「申诉恢复差错单…一人发起、另一人复核后恢复」「识别前已入账的推广收益留在推广账户…按 BR-WDR-06 不可提现」（拍板第二批 §8 ADD-05、ADD-06）
  - 本条正文 2026-10-03 前写法：「入账（月结批次，BR-FUND-04）执行时逐受益人判定：」（没有写判定须在取得锁之后，先读状态后加锁会按旧状态记账）（2026-10-03 资金规则对齐（负责人批准），方案 §4，同-06）
  - 本条正文 2026-10-03 前只写「份额计入 COMMISSION_REVENUE」「状态恢复 normal 后在后续月结批次（含补充批次，BR-FUND-04）补入账（订单已 CREDITED 时按 BR-FUND-01 R5a）」（没有写没收份额的凭证键与粒度，BR-ID-28、BR-ID-26 (b) 另写记入 subject=deleted_user / minor_excluded 的平台账户，生效科目表里没有这两个科目；补入账按哪个基数算未写）（2026-10-03 资金规则对齐（负责人批准），方案 §6.1、§6.6，同-08、同-13）
  - 本条正文 2026-10-03 写回时只写「被剥夺的份额，每个受益人写一张平台凭证 `{order_key}:PLATFORM:FORFEIT:{uid}:{role}`…金额 = 该受益人按入账基数的应得…首次入账（R5）与暂缓转没收（R5a）用同一个键」，没有写适用范围（BR-FUND-04 ⑫ 的延后正差转没收也引用本条，照字面要按整份应得没收、并把已入账的受益人整个改为被剥夺：评审例中应没收待补记的 80，却会写 480，应收联盟变成 1600，已入账的 400 也不再参与之后的扣回）（2026-10-03 资金规则对齐评审后修改，同步修正，方案 §13.6 第 3 条）
- 来源：规划/01_需求规划.md E10 F-SET-03；docs/changes/20261001-间推二级奖励.md；docs/changes/20261001-拍板第二批.md（FUND-10、FUND-14、FUND-17、OPS-07）；规划/04_数据模型与契约.md §2.3 BLACKLIST、§2.5 risk_state / deletion_status、§4.1 O4；PRD修订_后端功能规划 §2.6 受益人失效；docs/changes/20261001-拍板第二批.md §8 ADD-05、ADD-06；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 例：B=1234、r=5000/1000，快照时上级已注销 → 本人 617、直推 forfeited 0、平台 617。
- 例：月结批次执行时本人 risk_state=banned → 本人 617 forfeited，平台 494+617=1111；直推 123 正常入账。
- 例：月结批次执行时本人 risk_state=frozen → 本人 617 held（仍未入账），直推 123 入账；之后恢复 normal → 在下一个月结批次或补充批次补入账 617；若申诉失败转 banned → forfeited，平台 +617。
- 申诉恢复（拍板第二批 FUND-14）：封禁经申诉撤销（BR-ID-36 结案撤销）时，系统为该用户因本次封禁 forfeited 的份额（forfeit_reason=banned）自动生成「申诉恢复」差错单（BR-FUND-22，与风控作废订单的恢复同一入口），由有权限者一人 step-up 处理后恢复（拍板第二批 §8 ADD-05）：受益人追加 active 事件，按 BR-FUND-22 ③ 补发（ADMIN_ADJUST sub_type=RESTORE，借 COMMISSION_REVENUE / 贷该受益人 available，金额与 uniq_key 只按 BR-FUND-22）；不走 BR-FUND-24 人工调账单流程，处理前不入账。注销、未成年导致的 forfeited 不恢复。
- held 时限（拍板第二批 FUND-17）：受益人自首条 held 事件起满 30 天仍未解除时告警（风控与财务），由人工给出风控结论（解冻 → 补入账；转封禁 → forfeited）；超时本身不改变 held，系统不自动入账或剥夺。例：受益人 10-01 起 frozen，10-31 仍未解除 → 告警，份额继续 held。
- 未成年（拍板第二批 FUND-10）：入账时已识别未满 18 周岁的受益人，其推广份额（分享、直推、间推）追加 forfeited（forfeit_reason=minor），记平台（BR-ID-26 (b)）；自购返利照常；识别前已入账的推广收益留在余额中，不扣回、不另设冻结，未满 18 周岁期间提现整体受 BR-WDR-06 月额度约束，满 18 周岁后不再受限（拍板第二批 §8 ADD-06）。
- 申诉中（拍板第二批 OPS-07）：appealing 只由账户级申诉（封禁 / 冻结申诉，BR-ID-36）产生；用户对单笔风控作废订单的申诉只标记该订单申诉中，不改 risk_state，不使该用户其他订单的份额 held。
- 状态变化写 commission_split_beneficiary_events（BR-CALC-10）。
- 例（间推开启，r=5000/1000/500，B=1234）：快照时直推上级 B 已注销 → 直推 forfeited；间推受益人仍按 B 在 paid_at 时刻的上级 A 判定（BR-CALC-12 重放，B 注销不改历史关系），A 有效 → A 61；A 失效 → 间推 forfeited，归平台，不顺延给 A 的上级。
- 间推受益人（BR-CALC-05）适用本条全部判定；「不得向上顺延」指直推受益人失效时其份额不转给间推受益人，间推受益人失效时其份额也不转给更上级，均归平台。
- 规划 01 F-SET-03 已确认'归平台、不顺延'，本条新增判定时点与 hold。
- 例（没收份额的凭证，2026-10-03 资金规则对齐 E-16）：淘宝预留 2000，本人 5000、直推 1000，结算佣金 1000；入账时本人 U1 已进入注销处理 → P1 +80；平台 CREDIT 凭证 520（留存 320 + 预留 200）；另写 `{order_key}:PLATFORM:FORFEIT:U1:self` 400（借 UNION_RECEIVABLE / 贷 COMMISSION_REVENUE，forfeit_reason=deleted），不写 U1 流水；UNION_RECEIVABLE 合计 1000。
- held 解除后按 BR-FUND-01 R5a 入账：订单已 CREDITED 时，在 hold 解除后的下一个月结批次或补充批次（BR-FUND-04 ⑫ 受益人补记项）为该受益人单独入账，金额按执行时的 booked_base_fen 重算（暂缓期间结算额变过的，按变后的基数补），uniq_key 沿用 {order_key}:{uid}:{role}:CREDIT（只入一次）；转 forfeited 时份额记平台（{order_key}:PLATFORM:FORFEIT:{uid}:{role}，首次整份没收）；BR-FUND-04 为「除 held 受益人外同批入账」。已入账受益人正差被延后的部分另按 BR-FUND-04 ⑫ 的延后差额义务补记（键 `ADJ:DEFERRED:{beneficiary_credit_id}`），转没收时只没收待补记额，不把该受益人整个改为被剥夺（2026-10-03 评审后修改）。按 C-27 (d) 处理，补入账时点随月结口径（拍板第二批 FUND-01）。
- 按 C-01 默认处理（订单级失效改用 BR-FUND-01 状态名），已由负责人确认 2026-09-30。

#### BR-CALC-14 细则 · 入账时的基数取值

- 状态：已确认（入账口径随拍板第二批 FUND-01 改为月结批量入账）
- 默认值：无（已确认，按规则执行）
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - 本条旧写法：「settle_commission_fen 为空时用入账时刻最新 est_commission_fen 入账」（逐单满期入账口径；拍板第二批 FUND-01 按 9-30 拍板改为跟随联盟月结后取消）
- 来源：docs/changes/20260930-拍板第一批.md §3 D11、§10；docs/changes/20261001-拍板第二批.md（FUND-01、FUND-11）；规划/04_数据模型与契约.md §2.3、§4.1 O6/O7/O8；规划/02_系统架构.md §8.3；PRD修订_后端功能规划 §2.7 入账金额、月结补差
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 以下两例预留比例为 0（结算额 = 基数）；预留比例不为 0 时先按 BR-CALC-02 换算，例见 BR-FUND-09。
- 例：快照时 N=1234（预估 617/123），联盟月结结算额 1300 → 月结批次按 B=1300 入账 650/130，平台 520。
- 例：已按结算额 1300 入账，之后联盟把该单结算额改为 1200 → 本人 600、直推 120；调整 −50、−10，平台 −40 → 480（记账方式见 BR-CALC-23）。
- 结算额 = 已入账基数 → 不生成调整。
- 订单详情'实返与预估差额'只使用上述 4 个原因码。
- 入账守卫（月结账单范围、一致性校验、hold、rights_pending、开关）见 BR-FUND-04；orders.credit_requires_settle=true 且 settle_commission_fen 为空的订单不入账（BR-CALC-15、BR-CALC-25），月结口径下该条件自然满足。
- 按 C-01 默认处理（O6/O7 改写为 R5 与 settle_commission_fen 非空），已由负责人确认 2026-09-30。

#### BR-CALC-15 细则 · 部分退款与价保重算

- 状态：待验证
- 默认值：以联盟更新后的佣金为准；partial_refund_updates_commission 默认 true；平台不更新时按件退款用数量比例 floor 估算，按金额退款或价保暂停入账等结算
- 决策人：财务
- 依赖平台能力：淘宝/京东/拼多多：部分退款、价保后订单接口是否返回更新后的佣金，是否提供退款数量或退款金额字段
- 取代：
  - 返利 App PRD v2.1 §9.3：「维权成功（部分）按比例调整结算基数（未说明按数量还是金额）」
  - 本条正文 2026-10-03 前写法：「新基数必须取联盟返回的更新后佣金 N_new」（把联盟佣金当基数；改为先取 N_new 再按 BR-CALC-02 换算）（2026-10-03 资金规则对齐（负责人批准），方案 §1，同-01）
  - 本条正文 2026-10-03 前写法：「价保（R9b）的负差记账方式见 BR-CALC-23 (b)。」（R9b 改为只存档）（2026-10-03 资金规则对齐（负责人批准），方案 §2，决-01）
- 来源：规划/04_数据模型与契约.md §2.3、§4.1 O5/O10；PRD修订_后端功能规划 §3.1、§3.2；返利 App PRD v2.1 §9.3；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 例（本例预留比例为 0，N = B）：quantity=3，N=900，已入账 450/90。退 1 件，联盟 N_new=600 → 应得 300/60，写 CLAWBACK（sub_type=PART_REFUND）−150、−30，平台 360→240。
- 例（按件估算）：N=1000、quantity=3、退 1 → floor(1000×2/3)=666。
- 例（按金额退款、平台不更新佣金，rebate_status=WAITING）：数量不变，原 N=1000 → credit_requires_settle=true，订单详情按 WAITING 显示「已收货，等待联盟结算」与预估返（文案以 BR-TEXT-02 为准）；结算值 800 到达 → 进入当期或补充月结批次按 B=800 入账。
- credit_requires_settle 一经置 true 不回退；settle_commission_fen 非空后该守卫自然失效。月结口径（拍板第二批 FUND-01，BR-FUND-04）下入账本就只用联盟结算额，该守卫不再改变入账时点，也不再派生单独的展示状态（BR-FUND-17 第 11 行 WAITING_SETTLE 已停用），订单按 WAITING 等状态展示（BR-TEXT-02）。按 C-27 (e) 默认处理，待财务确认。
- commission_split_amounts 的幂等键 (order_id, commission_version, user_id, role)，order_id 为 orders 表内部主键（不用平台原始 sub_order_id，避免跨平台重号）；扣回凭证 uniq_key 见 BR-FUND-08。
- 京东实际佣金变 0 的判失效规则见 BR-FUND-08。
- 部分退款流水类型按 C-16（CLAWBACK sub_type=PART_REFUND，不再写负向 SETTLE_ADJUST），已由负责人 2026-10-03 确认默认（资金规则对齐决-04）；状态名按 C-01 默认处理，已由负责人确认 2026-09-30。

#### BR-CALC-16 细则 · 比价订单的计算与展示

- 状态：待验证
- 默认值：订单侧按联盟 N 计算；下单前展示见 BR-PRICE-07（按 C-22 默认处理，已由负责人确认 2026-09-30，财务知悉）
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
- 与 BR-PRICE-07 的分歧按 C-22 默认处理，已由负责人确认 2026-09-30（财务知悉）：下单前卡片与详情的比价风险返利展示只按 BR-PRICE-07——区间 [按 rebate.taobao.compare_rate_ratio_bp 折算的下限, 正常佣金率上限]，不另显示保守值，也不改为「不展示金额」；展示字段 rebate_min_fen / rebate_max_fen 由价格主题维护。本条只约束订单侧计算（以联盟已降佣的 N 分账、订单三处一致、差额原因 PRICE_COMPARE）。
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

适用范围：D7 后续接入，首版不实施（拍板第二批 AI-01 确认首版不接入淘礼金）；以下为接入时需复核的计算草案。

- 状态：待决策
- 默认值：rebate_mode=none：自购返利 0、直推 0（理由：红包已从佣金出，后续接入会消耗我方预算；避免叠加导致单笔亏损）；tlj_n_net_of_redpacket=false
- 决策人：财务
- 依赖平台能力：淘宝：淘礼金订单的推广者收入字段是否已扣除红包面额
- 取代：
  - 规划/04_数据模型与契约.md §2.2：「taolijin → 自购返利（淘礼金商品默认不叠加返利，未定义不叠加是返 0 还是扣面额）」
  - 规划/01 §3、PRD v2.1 §10.6、修订① §3.6：「淘礼金商品默认不叠加自购返利（只提自购，未提直推）」
- 来源：规划/01_需求规划.md §3、E08 F-TLJ-04；规划/04_数据模型与契约.md §2.2；规划/06_待补信息清单.md Q-B1；PRD修订_双品牌与Agent找货 §3.6；PRD修订_后端功能规划 §2.6
- 需同步修改的规划文档：4 处（计数仅作记录，落点见 README §0.6）

- 默认例：N=500、红包 300 → 本人 0、直推 0、平台 500（红包 300 已从预算付出，净 200）。
- normal 例（tlj_n_net_of_redpacket=false，reserve_bp=0）：N=500、红包 300 → B=200 → 本人 100、直推 20、平台 80。淘宝 reserve_bp=1500 时 → floor(500×8500/10000)=425 → B=125 → 本人 62、直推 12、平台 51 + 预留 75。
- normal 例（tlj_n_net_of_redpacket=true）：N=200（联盟已扣）→ tlj_deduct_fen=0 → B=200。
- rebate_mode 与 tlj_deduct_fen 随快照冻结（BR-CALC-10）；商品池改配置不影响已生成快照。

#### BR-CALC-20 细则 · 报价预估与计算函数一致

- 状态：待验证
- 默认值：游客按 L1、卡片按 self 口径报价；口径未验证前取可得口径中的较低值
- 决策人：负责人
- 依赖平台能力：各平台技术服务费率 tech_fee_bp[platform]（待核实）；三家商品接口佣金率字段是否已扣技术服务费、是否含补贴类佣金；淘宝 promotion_type=1/2、京东 PLUS、拼多多自购的报价口径差异（CAP-TB-04、CAP-JD-04、CAP-PDD-04）
- 取代：无
- 来源：docs/changes/20261001-平台预留比例.md；PRD修订_后端功能规划 §2.6 一个函数三处用；参考_花卷云功能查漏底稿 §2 游客佣金展示；规划/04_数据模型与契约.md §5 rebate_quote；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-04、3_JD_京东.md CAP-JD-04、4_PDD_拼多多.md CAP-PDD-04

**公式**（规划/01 §3 分账口径；D8 见规划/00 §3.2）：
```
gross   = floor(final_price_fen × rate_bp / 10000)
fee     = floor(gross × tech_fee_bp[platform] / 10000)
N_quote = gross − fee
B_quote = floor(N_quote × (10000 − reserve_bp[platform]) / 10000)   // BR-CALC-02；reserve_bp 取报价时刻生效版本
本人份额 = floor(B_quote × r_own_bp / 10000)   // r_own_bp 取 commission_rules[platform][level][order_type]（BR-CALC-06；别名 r_self_bp，C-29）
```
- tech_fee_bp[platform] 为配置项，取值待核实；若 CAP-TB-04 / CAP-JD-04 / CAP-PDD-04 实测佣金率字段已扣技术服务费，该平台 tech_fee_bp 配 0，不得重复扣。
- **例**（参数只作示意；淘宝技术服务费率待核实）：final_price_fen=2990，rate 2000bp，tech_fee_bp 1000 → gross=598 → fee=floor(598×1000/10000)=59 → N_quote=539 → reserve_bp 0（种子）→ B_quote=539 → r_own_bp 5000 → floor(539×5000/10000)=269。
- **例**（淘宝 reserve_bp=1500）：同上 N_quote=539 → B_quote=floor(539×8500/10000)=458 → floor(458×5000/10000)=229；订单按同一版本、同一 N 入账时本人份额同为 229。
- 例：游客看 N_quote=1000 的淘宝商品（reserve_bp=0）→ 按 L1 self 5000 → 本人份额 500；登录 L2 用户同商品若 r_own=5500 → 550。
- 例：报价时 v2（5000），用户在 v3（4500）生效后付款 → 快照按 v3，订单预估 450；报价 500 不持久化、不参与订单侧任何计算。预留比例变化同理：报价按报价时刻版本的 reserve_bp，订单按 paid_at 版本。
- 例：B 很小导致本人份额 0，或淘礼金默认模式（BR-CALC-19）→ 本条输出 0；展示按 BR-PRICE-08。
- 金额展示格式、零值、比价区间与口径说明文案只按 BR-PRICE-06 / 07 / 08 / 17（金额格式 BR-TEXT-10）；比价订单的订单侧计算见 BR-CALC-16；三平台自购 / 分享口径见 BR-CALC-17。
- 价格口径、取价时间见 BR-PRICE；AI 金额必须来自该函数输出，见 BR-AI。

#### BR-CALC-21 细则 · 分账不变量与算例测试

- 状态：已确认
- 默认值：无（已确认，按规则执行）
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - 本条原写：「specs/commission-examples.csv 必须在 W1 由财务给出」（规划/11 §7.3 第 8 项，负责人 2026-10-01「全部同意」：两家模型盲算 + 08 原文对照，负责人确认 5 条代表例；做法见 规划/11 §4.2）
- 来源：规划/02_系统架构.md §8.4；返利 App PRD v2.1 §11.3；PRD修订_后端功能规划 §2.6；开发任务拆解_v1 BF-03、C-08

csv 至少覆盖：B=1234 自购（617/123/494）、B=2000 分享（1000/200/800）、B=1、B=0、N 为负、无上级、上级注销（forfeited）、入账时本人 banned、入账时本人 frozen（held）、淘礼金默认、淘礼金 normal、部分退款（按件 / 按金额）、结算下调、结算上调、比价订单、预售、跨版本边界（paid_at = effective_from）、跨等级边界、拼多多自购报价。
- 间推（BR-CALC-05）另加属性：indirect_enabled=false 时无 indirect 受益人；Σ用户份额 ≤ B（含 indirect）；受益人深度 ≤ 2。csv 补：间推关闭 / 开启、上级无上级（间推 0）、上上级注销（forfeited）、上级注销而上上级有效、depth 3 不计酬、开关切换前后按 paid_at 选版本不回溯。
- csv 另补拍板第二批相关例：受益人入账时已识别未满 18 周岁（推广份额 forfeited=minor）、注销后扣回（不写用户分录）、封禁经申诉撤销后的恢复补发。
- 平台预留（BR-CALC-02）另加属性：reserve_fen ≥ 0；B 未被截为 0 时 Σ用户份额 + platform_retain_fen + reserve_fen + tlj_deduct_fen = max(0, N_base)；reserve_bp=0 时 B 与不扣预留的结果相同。csv 补 reserve_bp 非 0（含 N_base=1000、1500 → B=850）与报价 = 入账同值两例。
- 同一 (order_id, 受益人, 角色) 首次入账最多 1 次（BR-FUND-19 不变量 ③）。
- csv 另需覆盖 BR-CALC-27 四段金额算例（普通、补贴、淘礼金 none / normal、负 N）。
- 「冻结该订单全部受益人的提现」的记录方式按 C-09 默认处理：写 withdraw_holds（reason=ledger_mismatch，BR-WDR-05、BR-FUND-19），提现申请按其错误码返回，待财务确认。reason 取值按 C-20 统一（后台显示名 LEDGER_MISMATCH；withdraw_holds 定义只在 BR-WDR-05）。

#### BR-CALC-22 细则 · 规则发布与回滚流程

- 状态：已确认（负责人 2026-10-01：修改可立即生效，按 paid_at 对之后付款的订单生效、不回溯；拍板第二批 §8 ADD-05：超管或有权限账号一人起草并 step-up 发布；ADD-03：比例与预留数值上线前由超管在后台填写；原为默认假设）
- 默认值：沿用后端功能规划 §1.6 流程，保留基准版本校验与试算差异报告；起草与发布可为同一人
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 本条原写法（2026-10-01 前）：「下调任一比例时 effective_from ≥ 发布时刻 + 24 小时」（理由是减少报价刚看到即失效的纠纷）；负责人确认改为立即生效
  - 本条 2026-10-01 写法：「finance 起草 → … → super 经 step-up 发布；发布接口校验 publisher_id ≠ drafter_id（super 起草的版本也须由另一名 super 发布）」「误配风险由第二人发布、试算差异报告与审计控制」「草稿 indirect_enabled=true 时，发布前另需一名非起草人的 finance 审批」（拍板第二批 §8 ADD-05）
- 来源：规划/04_数据模型与契约.md §11；docs/changes/20261001-平台预留比例.md；docs/changes/20261001-拍板第二批.md §8 ADD-03、ADD-05；PRD修订_后端功能规划 §1.6 资金配置、§2.10、§10.1 AC-MONEY-014
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 试算样本 = paid_at ∈ [发布申请时刻 − 7 天, 发布申请时刻) 且已生成快照的订单；报告对比现行版本与草稿的各平台 reserve_bp、预留金额、本人份额、直推份额、间推份额、平台留存合计。
- 草稿 indirect_enabled=true 时同样一人 step-up 发布，试算报告须含间推份额列（BR-CALC-05）；误配风险由 step-up、试算差异报告与审计日志控制。
- 例：财务把 taobao/L1/self 从 5000 改为 4500，试算报告显示近 7 天 1,000 单本人份额合计下降约 10%；同一人 step-up 发布，发布时刻 2026-10-30T10:00+08:00，effective_from=2026-11-01T00:00:00+08:00（也可设为发布时刻，立即生效）。
- 例：负责人把淘宝 reserve_bp 从 1300 改为 1500（其他不变），effective_from 设为发布时刻即立即生效：之后付款的订单按 1500，之前付款的订单仍按 1300（BR-CALC-11）。上调、下调 reserve_bp 规则相同。
- 草稿缺任一平台 reserve_bp、或 reserve_bp 不在 0–10000 → 校验失败，不生成试算、不允许发布。
- effective_from 早于发布时刻 → 拒绝（禁止回溯）。
- 试算报告生成失败 → 不允许发布。

#### BR-CALC-23 细则 · 入账后调整的记账时点与审批

- 状态：已确认（拍板第二批 FUND-11：结算额少了立即扣，多了人工批准后再补；C-07 据此关闭；§8 ADD-05 改为有权限者一人 step-up 批准）
- 默认值：负差（扣回方向）即时记账，正差进批次等人工批准（理由：负差延迟期间用户可能把这部分钱提现走，之后只能形成负余额或坏账；正差延迟不产生资损）
- 决策人：财务
- 依赖平台能力：无
- 取代：
  - 规划/04_数据模型与契约.md §4.1 O8：「CREDITED → SETTLED，结算额 ≠ 已入账额时写 SETTLE_ADJUST（自动记账，无审批）」
  - PRD修订_后端功能规划 §0.4 B8、§2.7 月结补差：「结算补差生成候选，经财务批准后记账（不区分正负）」
  - 本条 2026-10-01 写法：「由 finance 发起、另一名 finance 或 super（≠ 发起人）step-up 复核后记账」（拍板第二批 §8 ADD-05）
  - 本条 (a) 2026-10-03 前写法：「rebate_status 始终保持 CREDITED」（结算佣金变为 0 或负数时与 R8、R10 及 BR-CALC-02 细则「入账后走 R8 → CLAWED_BACK」不一致，补限定）（2026-10-03 资金规则对齐（负责人批准），方案 §2，同-03）
  - 本条 (a) 2026-10-03 前只写「差额 &lt; 0 的受益人在该次更新的同一事务内立即记负向 SETTLE_ADJUST，不等审批；差额 > 0 的受益人生成补差候选…批准后记账」（按每个受益人自己的方向分路，与 BR-FUND-09「按结算额与已入账基数的大小分两路」的整单写法不一致；封禁受益人的正差已归平台后整单下调，会把归平台的部分送进审批或漏记；补注分路依据）（2026-10-03 资金规则对齐（负责人批准），方案 §7.7，同-27）
  - 本条 (a) 2026-10-03 写回时的分路注与状态注：「分路按 BR-FUND-09 的整单比较：结算基数与 booked_base_fen 比大小」「（新基数大于 0 时；新基数为 0，含结算佣金为负，按迁移 R8 → CLAWED_BACK）」（基数相等而联盟佣金不同时没有归属，随 BR-FUND-09 补「相等时比结算佣金与 booked_n_fen、只调平台金额」；新旧基数都为 0 的订单由 R10 只调平台金额，保持 CREDITED）（2026-10-03 资金规则对齐评审后修改，同步修正，方案 §13.6 第 2 条）
  - 本条 (b) 2026-10-03 前写法：「(b) 部分退款 / 部分维权（BR-FUND-01 R9）与佣金下调（R9b：价保、比价降佣、联盟佣金调整；对应 04 O10）——负向调整自动记账，不需审批：部分退款、部分维权写 CLAWBACK（BR-FUND-08）；R9b 在新 B &lt; booked_base_fen 时同事务写负向 SETTLE_ADJUST（sub_type=PRICE_PROTECT / PRICE_COMPARE / SETTLE_DIFF，uniq_key 见 BR-FUND-01 R9b）；正向差额此时不记账，进 BR-FUND-09 候选，由 (a) 在结算时处理（拍板第二批 FUND-11 确认）。」；细则例「入账基数 1300（650/130），之后联盟下调该单佣金为 1250（R9b，sub_type=SETTLE_DIFF）→ 应得 625/125，同事务立即记负向 SETTLE_ADJUST −25、−5（C-27 (g)，拍板第二批 FUND-11 确认；原写法「单纯预估字段变化不生成调整、等结算」已取代）。上调则不记账，进 BR-FUND-09 候选。」「入账 600/120，平台回传价保，联盟新佣金 1100 → 应得 550/110，立即记负向 SETTLE_ADJUST（sub_type=PRICE_PROTECT）−50、−10。」（负责人 2026-10-03 选决-01 A：只有预估变化时只存档并出差错单，佣金下调须反映在联盟新的结算记录上才按 (a) 扣）（2026-10-03 资金规则对齐（负责人批准），方案 §2，决-01）
- 来源：规划/02_系统架构.md §8.3；规划/04_数据模型与契约.md §4.1 O8/O10；docs/changes/20261001-拍板第二批.md（FUND-11、FUND-01）；PRD修订_后端功能规划 §0.4 B8、§2.7；docs/changes/20261001-拍板第二批.md §8 ADD-05；docs/changes/20261003-资金规则对齐.md
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

- 以下各例预留比例为 0（结算额 = 基数）；预留比例不为 0 时先按 BR-CALC-02 换算，例见 BR-FUND-09。
- 例：按结算额 1300 入账 650/130，之后联盟把结算额改为 1200 写入 settle_commission_fen → 应得 600/120，差额 −50/−10 → 同一事务立即记负向 SETTLE_ADJUST，补差完成（rebate_status 保持 CREDITED，对应单一 order_status 的 SETTLED）。
- 例：按结算额 1200 入账 600/120，之后联盟把结算额改为 1300 → 应得 650/130，差额 +50/+10 → 生成 2 行候选，补差未完成；财务 step-up 批准后记账，补差完成。
- 例：入账基数 1300（650/130），之后联盟新的结算记录把该单结算佣金下调为 1250 → 按 (a)：应得 625/125，同事务立即记负向 SETTLE_ADJUST −25、−5（sub_type 默认 SETTLE_DIFF）。上调则不记账，进 BR-FUND-09 候选。
- 例：入账 600/120，平台回传价保，联盟新的结算记录 1100 → 按 (a)：应得 550/110，立即记负向 SETTLE_ADJUST −50、−10（Adapter 识别出价保时 sub_type=PRICE_PROTECT）。
- 例（只有预估变化，决-01 A）：入账 600/120（结算佣金 1200），联盟只把预估佣金改为 1100、结算记录未变 → 不记账、余额不变，生成 1 张差错单「入账后预估佣金变化」，同一预估值重放不重复生成；联盟随后真的出了 1100 的结算记录时再按 (a) 扣。
- 受益人为 forfeited / banned / frozen 时的处理见 BR-CALC-09。
- 补差候选表统一用 BR-FUND-09 的 settle_adjust_batches（原写 settle_adjustments，02 settlement 模块用名以资金主题为准）。
- 与 BR-FUND-01 R9b、BR-FUND-08、BR-FUND-09 的差异：资金主题原把价保列为 R9b「无分录、只由月结补差处理」，且所有补差都经人工批准。按 C-07（拍板第二批 FUND-11 确认），负差（含价保负差）即时记账、人工批准只用于正差（一人可完成，§8 ADD-05）；R9b 已按 C-27 (g) 改为新 B &lt; booked_base_fen 时同事务写负向 SETTLE_ADJUST（sub_type PRICE_PROTECT / PRICE_COMPARE / SETTLE_DIFF），uniq_key 见 BR-FUND-01 R9b（{order_key}:{uid}:{role}:ADJ:{sub_type}:v{commission_version}，平台侧 {order_key}:PLATFORM:ADJ:{sub_type}:v{commission_version}），正差仍进 BR-FUND-09 候选；C-27 (g) 已由拍板第二批 FUND-11 确认。2026-10-03 资金规则对齐决-01 选 A：R9b 改为只存档并出差错单，本段所述 R9b 写负向 SETTLE_ADJUST 与 `ADJ:{sub_type}:v{commission_version}` 键已停用；结算额的下调仍即时记账（R10）。
- 按 C-01 默认处理，已由负责人确认 2026-09-30；C-07 已由拍板第二批 FUND-11 确认。
- 月结口径（拍板第二批 FUND-01）：首次入账即按联盟结算额（BR-CALC-14），(a) 只在入账后联盟结算额再变化时出现，正差候选比逐单入账时少。

#### BR-CALC-24 细则 · 分享单的分账

- 状态：已确认（负责人 2026-09-30，依据 docs/changes/20260930-拍板第一批.md §2；间推部分按 2026-10-01 规则版本开关执行，BR-CALC-05）
- 默认值：沿用 06 Q-B1 分享收益 5000；直推计给分享者上级；间推（开关开启时）计给分享者上级的上级（D8，BR-CALC-05）；分享者经自己链接自购按 self 计；各份额入受益人的单一余额（拍板第二批 §8 ADD-06）
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 规划/01_需求规划.md §3：「分享单给分享者的份额公式与直推受益人未写」
  - 本条旧默认值（2026-09-30 前）：「直推按一层计给分享者上级（D8 默认）」
- 来源：规划/00_总览与决策.md D8；docs/changes/20260930-拍板第一批.md §2、§3 D8 行；docs/changes/20261001-间推二级奖励.md；规划/01_需求规划.md §3；规划/04_数据模型与契约.md §2.2 buy_type；规划/06_待补信息清单.md Q-B1 分享收益比例；docs/changes/20261001-拍板第二批.md §8 ADD-06
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

| 例 | B | 比例（分享者/直推/间推） | 分享者 | 分享者上级 | 分享者上级的上级 | 平台 |
|---|---|---|---|---|---|---|
| 1 | 2000 | 5000/1000/0 | 1000 | 200 | 0 | 800 |
| 2 | 2000，分享者无上级 | 5000/—/— | 1000 | 0 | 0 | 1000 |
| 3 | 2000（间推开启，比例仅为算例） | 5000/1000/500 | 1000 | 200 | 100 | 700 |

- 例：A 分享给 App 用户 B，B 通过 A 的链接购买 → 订单归属 A（share），B 不得分账。
- 例：A 用自己的分享链接下单，BR-ATTR 定稿前 → 按 self，A 得 r_own(self) 份额（REBATE_CREDIT）。
- 流水类型：分享者 SHARE_CREDIT，上级 REFERRAL_CREDIT（DIRECT），上级的上级 REFERRAL_CREDIT（INDIRECT）；税目见 BR-FUND。

#### BR-CALC-25 细则 · 联盟未单列补贴类佣金时的处理

- 状态：待决策
- 默认值：未单列时 N 整体计入 B，但入账推迟到联盟结算后（理由：补贴佣金常带条件、事后可能被追回，结算后入账可降低扣回与坏账风险；是否把补贴分给用户属于金额口径，需财务 W1 确认）
- 决策人：财务
- 依赖平台能力：淘宝/京东/拼多多订单接口是否单列补贴类佣金（CAP-TB-04、CAP-JD-04、CAP-PDD-04）
- 取代：无
- 来源：规划/01_需求规划.md §3；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-04；PRD修订_后端功能规划 §2.2
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：淘宝订单 pub_share_pre_fee=1000，接口无补贴明细 → 预估按 B=1000 展示 500；联盟结算前不进月结账单；结算值 950 到达 → 月结批次按 B=950 入账 475/95。
- 判定'未单列'以 09 表验证结论为准，按平台配置 union.&lt;platform>.subsidy_itemized（boolean，默认 true）；为 false 时本条生效。
- 生效方式：subsidy_itemized=false 的平台，订单入库时置 orders.credit_requires_settle=true；settle_commission_fen 为空时不入账（不设 hold，不影响 BR-FUND-06 的 hold 语义）。该守卫已并入 BR-FUND-04 的入账条件（C-27 (e)，默认处理，待财务确认）。
- 月结口径（拍板第二批 FUND-01）下所有订单都在联盟结算后入账，「结算后入账」自然满足；本条只余「补贴部分是否分给用户」待财务决定。

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
- 默认值：四段 = 联盟佣金总额、基数前扣除（含平台预留金额）、B、平台预估利润；利润扣除我方淘礼金红包面额（理由：沿用后端功能规划与花卷云底稿「每单落四段金额」的需求，按本主题 B 的定义（BR-CALC-02 先扣预留）改写；利润扣红包面额使淘礼金 none / normal 两种模式口径一致，与 BR-CALC-19「净 200」算例一致；利润口径属金额口径，需财务确认）
- 决策人：财务
- 依赖平台能力：无（n_base_fen、subsidy_commission_fen 的取数依赖见 BR-CALC-03、BR-CALC-18；tlj_n_net_of_redpacket 依赖见 BR-CALC-19）
- 取代：
  - 参考_花卷云功能查漏底稿 §2 分佣基数、§16 #1：「每单落库四个金额：预估佣金、平台预留、实际计算佣金、平台预估利润；实际计算佣金 = 联盟预估佣金 × (1 − 平台预留%)」
  - PRD修订_后端功能规划 §2.5 第 6 步：「订单首次入库且已归因时落四个金额：联盟预估佣金 N、平台预留、可分配基数 B、平台预估利润」
- 来源：docs/changes/20261001-平台预留比例.md；参考_花卷云功能查漏底稿 §2、§16 #1；PRD修订_后端功能规划 §2.5 第 6 步、§13.2 易漏项 #1、经营看板（平台预估利润）

| 字段（整数分） | 定义 | 时点 |
|---|---|---|
| n_total_fen | n_base_fen + subsidy_commission_fen（已扣技术服务费，可为负） | 快照生成时与每个新 commission_version |
| pre_base_deduct_fen | n_total_fen − base_fen（含该版本 reserve_fen，按快照 reserve_bp 计算） | 同上 |
| base_fen | B（BR-CALC-02） | 同上 |
| platform_est_profit_fen | n_total_fen − Σ该版本用户份额 − tlj_redpacket_fen；可为负 | 同上 |

- 存储：`commission_split_totals(order_id, commission_version, n_total_fen, pre_base_deduct_fen, base_fen, user_share_total_fen, tlj_redpacket_fen, platform_est_profit_fen, created_at)`，唯一 (order_id, commission_version)，只追加；orders 冗余当前版本值供报表查询。
- 例（普通单）：n_base 1234、补贴 0、reserve_bp 0、5000/1000 → ① 1234 ② 0 ③ 1234，用户 617+123=740，④ 494。
- 例（平台预留）：n_base 1000、补贴 0、reserve_bp 1500、5000/1000 → ① 1000 ② 150 ③ 850，用户 425+85=510，④ 490。
- 例（补贴，BR-CALC-18）：n_base 800、补贴 200 → ① 1000 ② 200 ③ 800，用户 400+80，④ 520。
- 例（我方淘礼金 none，BR-CALC-19）：N=500、红包 300 → ① 500 ② 0 ③ 500，用户 0，④ 500−0−300=200。
- 例（我方淘礼金 normal，tlj_n_net_of_redpacket=false）：N=500、红包 300 → ① 500 ② 300 ③ 200，用户 100+20，④ 500−120−300=80。
- 例（负 N 冲正）：n_total −320 → ① −320 ② −320 ③ 0，用户 0，④ −320。
- 边界：held 受益人份额计入 Σ用户份额（仍是应付）；forfeited 为 0。四段金额不进用户接口、不进用户可见文案。
- 我方淘礼金订单匹配不到红包记录 → tlj_redpacket_fen、platform_est_profit_fen 为 null，报表标'待核'并告警（与 BR-CALC-19 的待处理表同一告警）。

### 5.3 本主题未决问题

1. 已解决（拍板第二批 FUND-11）：BR-CALC-23 结算负差即时记账、正差人工批准后记账（§8 ADD-05：一人 step-up 批准）；序号保留。
2. BR-CALC-25：联盟未单列补贴类佣金时，补贴部分是否分给用户，需财务决定
3. BR-CALC-02 / 05 / 06 数值：各平台 reserve_bp、L1–L3 的 r_own / r_direct / r_indirect（间推开启时的占位 500）以及单位经济模型终值（PRD v2.1 §19.1 D5、§19.2 G1；后端规划 §12.1 B11；规划侧见 06 Q-B1、01 §8.3），开发期用占位值，上线前由超管在后台填写，之后随时可改、立即生效（拍板第二批 §8 ADD-03，取代 FUND-21）；结构已确认
4. BR-CALC-19：我方淘礼金订单是否给本人或上级分佣（默认都为 0），需财务确认；首版不接入淘礼金（拍板第二批 AI-01），接入前再定
5. BR-CALC-12：直推受益人按 paid_at 时的上级（默认）还是按快照时 parent_id【C-06 已由负责人确认 2026-09-30：按 paid_at】
6. BR-CALC-24 / BR-ATTR：分享者经自己的分享链接下单按 self 还是 share（默认 self），影响比例与流水类型（单一余额后不再影响账户，税目统一 SERVICE_FEE），需 BR-ATTR 定稿（BR-CALC-24 已由负责人确认 2026-09-30，含「BR-ATTR 定稿前按 self」的默认；BR-ATTR 侧仍待定稿）
7. 已解决（拍板第二批 FUND-17）：BR-CALC-13 held 满 30 天仍无风控结论时告警，由人工决定，系统不自动处理；序号保留。
8. 【已由负责人确认 2026-10-03，资金规则对齐决-04 确认默认】部分退款负向调整的流水类型：已列入 §14.3 C-16，默认按 BR-FUND-08 写 CLAWBACK（sub_type=PART_REFUND），BR-CALC-15、BR-CALC-23 已按此改写，待财务确认
9. BR-CALC-11：三家订单接口能否拿到预售尾款付清时间，需在 09 表订单同步项验证
10. 活动加成（P1 新人红包、邀请奖励）的计算口径与是否占用 8000 上限之外的预算，P1 前再定
11. 已解决：BR-CALC-02（2026-10-01 改为先扣平台预留，拍板第二批 TRADE-02 确认）、BR-CALC-24（2026-09-30 确认）、BR-CALC-07 / 08 / 09（拍板第二批 FUND-15 按当前默认签字）、BR-CALC-22（§8 ADD-05）均为已确认；各数值见第 3 项；序号保留。
12. BR-CALC-27：平台预估利润是否扣除我方淘礼金红包面额、四段金额是否需要按版本留历史（默认扣除、按版本只追加），需财务确认
13. 【已由 §14.3 C-22 处理：默认处理，已由负责人确认 2026-09-30（财务知悉）】BR-CALC-16 与 BR-PRICE-07 的淘宝比价区间下限算法、拿不到 min/max 时的展示：下单前展示只按 BR-PRICE-07，BR-CALC-16 只保留订单侧计算；compare_rate_ratio_bp=5000 为占位值，数据到位前只在 App 内展示
14. 【已由 §14.3 C-27 处理：(g) 已由拍板第二批 FUND-11 确认；(e) 默认处理，待财务确认，月结口径下该守卫自然满足】跨主题分歧：BR-CALC-15 / BR-CALC-25 新增的 orders.credit_requires_settle 入账守卫未在 BR-FUND-04 的入账条件中；BR-CALC-23 (b) 价保负差即时记账与 BR-FUND-01 R9b「无分录、只由月结补差」不一致（按 C-07 默认以本主题为准）；处理结果：credit_requires_settle 守卫在月结口径下自然满足（BR-FUND-04 边界；WAITING_SETTLE 展示状态已停用，BR-FUND-17 第 11 行）；价保、比价降佣等负差按 BR-FUND-01 R9b 即时写负向 SETTLE_ADJUST（uniq_key {order_key}:{uid}:{role}:ADJ:{sub_type}:v{commission_version}），正差仍进 BR-FUND-09 候选
15. 【已由 §14.3 C-27 处理：(c) 代理已补；(d) held 补入账改为后续月结批次（拍板第二批 FUND-01），uniq_key 不变】跨主题缺口：BR-CALC-13 受益人级 held 在订单 CREDITED 后补入账所用的迁移与凭证 uniq_key，BR-FUND-01 / BR-FUND-05 未定义（BR-FUND-04 写「一单的全部受益人同时入账」）；BR-CALC-10 中 VOID 未归因订单找回通过只设 user_id 的事件，BR-FUND-01 迁移表未列出；处理结果：held 解除后按 BR-FUND-01 R5a 入账（uniq_key 沿用 {order_key}:{uid}:{role}:CREDIT），VOID 未归因订单找回 / 改派按 R3b（rebate_status 保持 VOID，只写 user_id、user_basis、locked=true）

---
