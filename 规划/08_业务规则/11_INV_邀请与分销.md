# 08 业务规则 · 11. 邀请与分销（BR-INV）

返回 [README](README.md)（使用规则、术语表、规则索引）

## 11. 邀请与分销（BR-INV）

本节规定：邀请码、绑定渠道与校验、禁止关系、改上级、计酬层级、直推与间推受益人、等级、下级可见范围、开关与 P1 奖励、P1 会员口径。共 23 条（已确认 3、默认假设 12、待决策 8）。

订单状态统一按 BR-FUND-01 双状态书写（platform_status + rebate_status，C-01 默认处理）。与 规划/04 单一 order_status 的对照：O2「首次入库已归因」≈ rebate_status R2；O11「找回 / 后台改归属」≈ R3；INVALID ≈ rebate_status=VOID；CLAWED_BACK 同名；确认收货 = platform_status 首次到 RECEIVED（或经 P5 补写）。若负责人不采纳双状态，按 BR-FUND-01 的映射表回退。

### 11.1 规则一览

| 编号 | 规则 | 状态 | 影响面 |
| --- | --- | --- | --- |
| BR-INV-01 | **邀请码生成与格式**<br>每个用户必须在账号创建的同一事务内由服务端生成 1 个邀请码，终身不变。字符集固定为 32 个字符 `23456789ABCDEFGHJKLMNPQRSTUVWXYZ`（去掉 0/O/1/I），长度等于 6，用 CSPRNG 均匀随机生成；(app_id, invite_code) 必须唯一。每个账号最多生成 5 个候选码（含首次）：每个候选码先按敏感词库（场景=invite_code，不区分大小写的子串匹配）过滤，再用 `INSERT … ON CONFLICT (app_id, invite_code) DO NOTHING` 或在 SAVEPOINT 内写入；唯一冲突或命中敏感词各计 1 次。5 个候选全部失败时回滚整个注册事务，注册接口返回 50001 并告警。已注销账号的邀请码不得回收或再分配。新 App 码空间与优券汇独立，不导入、不互认。用户自定义邀请码为 P1。 | 已确认 | users.invite_code（唯一 (app_id, invite_code)）；注册 / 落地页注册事务；敏感词库场景 invite_code；后台用户查询（按邀请码搜索）；错误码 50001；验收用例 AC-INV-01 |
| BR-INV-02 | **邀请码输入校验与错误码**<br>【规范化】服务端对邀请码依次执行：Unicode NFKC 规范化 → 删除全部 Unicode 空白字符（含 \\s、U+3000）及零宽字符 U+200B–U+200D、U+FEFF → 转大写。规范化后为空字符串的：register 渠道视为未携带 invite_code（响应不含 invite_bind），backfill 与 landing 渠道返回 30401。不做 O→0 等纠错映射。<br>【邀请人不可用判定】定义唯一判定函数 `inviter_unavailable(u)` = u.risk_state ∈ {banned, appealing, frozen} OR u 存在 deletion_status ∈ {cooling, processing, done} 的注销单 OR u.phone_hmac IS NULL OR (u.realname_status=verified 且按 BR-INV-19 在判定时刻未满 18 周岁)；以调用时刻的状态为准。绑定校验（30401）、邀请页展示（BR-INV-18）、后台改上级（BR-INV-10）必须调用同一个函数，不得各自实现；快照与入账时直推受益人的有效性不调用本函数，按 BR-CALC-13（BR-INV-13）。<br>【校验顺序】backfill 与 register 渠道固定为：身份级别 phone（10005，仅 backfill）→ 开关 growth.invite_bind.enabled（关则 30408）→ 频控（42901）→ 本人已有上级或已用过自助绑定（30402）→ 补填期限（30404，仅 backfill）→ 补填条件：订单、找回申请或下级（30409，仅 backfill）→ 规范化后格式校验：长度≠6 或含字符集外字符（30401，不查库）→ 邀请人存在且 inviter_unavailable=false（否则 30401）→ 关系冲突（30403，BR-INV-08）。每一步命中即返回，不执行后续步骤。landing 渠道顺序见 BR-INV-05，后台改上级顺序见 BR-INV-10。<br>【文案】邀请人不存在或不可用一律返回 30401，文案统一为“邀请码无效”，不得暴露具体原因。<br>【频控】计数对象 = 三个渠道返回的全部 30401（含格式错误与空码）；计数键 = phone_hmac（三渠道共用），landing 渠道另按 IP 单独计数。当日（+08:00 自然日）同一键累计 30401 ≥5 次后，该键当日后续绑定请求在频控这一步返回 42901，Retry-After = 距次日 00:00 +08:00 的秒数。register 渠道命中时照常建号，invite_bind={failed, 42901}。 | 默认假设 | POST /v1/me/inviter；POST /v1/auth/login/sms（invite_code）；POST /v1/invites/landing-register；inviter_unavailable 公共判定函数（packages/domain）；错误码表 04 §7（30408、30409 由本主题占用，C-03）；客户端 / H5 错误提示文案；客服话术（邀请码无效）；验收用例 AC-INV-\* |
| BR-INV-03 | **绑定渠道与先到先得**<br>MVP 自助绑定渠道只有 3 个，source 取值固定：`landing`（邀请落地页手机号注册，服务端直接绑定，BR-INV-05）、`register`（App 内新建账号时携带 invite_code，BR-INV-06）、`backfill`（“我的”补填，BR-INV-07）。每个账号自助绑定成功最多 1 次，关系取最先成功的一次，后到的任何渠道都不得覆盖（补填返回 30402，登录携带的 invite_code 被忽略）。绑定写库必须用条件更新 `WHERE parent_id IS NULL AND self_bind_used = false`，并以 Idempotency-Key 去重；成功时同事务写 self_bind_used=true、parent_bind_source、parent_bound_at、relation_change_logs。绑定需要被邀请人为 phone 级别（落地页天然满足）。Agent / AI 工具不得注册任何绑定上级接口（见 BR-AI）。 | 待决策 | users.parent_id、users.self_bind_used、users.parent_bind_source、users.parent_bound_at；relation_change_logs；POST /v1/invites/landing-register、POST /v1/auth/login/sms、POST /v1/me/inviter；Agent 工具注册表 CI 检查；验收用例 AC-INV-\* |
| BR-INV-04 | **剪贴板邀请口令不进MVP**<br>MVP 不得在 App 启动时自动识别剪贴板中的邀请码/邀请口令用于绑定；注册页与补填页的邀请码输入框可提供“粘贴”按钮（用户点击后才读剪贴板，走 `clipboard.read` L2 手势规则）。粘贴抽取规则（三端一致）：对剪贴板文本做 NFKC 规范化并转大写，用正则 `(?<![0-9A-Z])[2-9A-HJ-NP-Z]{6}(?![0-9A-Z])` 取第一个匹配填入输入框；没有匹配时不填入，提示“未识别到邀请码”；不自动提交。提交后服务端仍按 BR-INV-02 校验。App 自己写入剪贴板的邀请码按 03 的 hash 规则不被商品剪贴板识别误判为商品。 | 待决策 | 注册页 / 补填页 UI（三端 + H5）；03 剪贴板识别规则；clipboard.read 桥方法；验收用例 |
| BR-INV-05 | **落地页注册绑定**<br>落地页只用两个接口：发码 `POST /v1/landing/sms-codes`（免签名、人机验证 44003 与发码频控见 BR-ID-32），注册并绑定 `POST /v1/invites/landing-register`（BR-ID-32 所称 `POST /v1/landing/login` 即本接口，路径按 13 保留规划写法；none 级别，Idempotency-Key 必填）。landing-register 入参 phone、sms_code、invite_code、agreed（协议勾选）、channel（可选渠道码），不再收 captcha_token（人机验证已在发码时完成）。落地页必须展示《用户协议》《隐私政策》勾选框（默认不勾），未勾选不得提交。校验顺序固定为：agreed=true（否则 10004）→ 开关（30408）→ 频控：同 IP 或同 phone_hmac 当日 30401 ≥5 次（42901）→ 邀请码规范化与格式（30401）→ 邀请人存在且 inviter_unavailable=false（30401）→ 短信验证码校验并核销（20002 / 20003，BR-ID-05）→ 手机号是否已注册（是则 `already_registered`）→ 同 IP 注册上限（BR-ID-32）→ 44001、不建号 → 建号并绑定。邀请码失败时不核销短信验证码；“已注册”判定必须在短信验证码校验通过之后。存在 phone_hmac 相同且注销状态不为 done 的账号（含 cooling、processing）时，不得修改任何关系，返回 `already_registered`；只存在已 done 的注销账号时视为新手机号。新号必须在同一事务内：创建用户（register_method=h5_landing，registered_channel 按 BR-ID-04 取渠道码）、写 parent_id=邀请人、parent_bind_source=landing、parent_bound_at、self_bind_used=true、relation_change_logs 一条、consent_records（agreement 与 privacy 各一条，version=当前版本，channel=h5_landing，accepted=true）。落地页不采集设备 ID，同设备校验延后到首次 App 登录（BR-INV-09）。落地页 `/i/{code}` 对有效码与无效码返回相同页面结构，不显示邀请人昵称或任何个人信息。 | 默认假设 | POST /v1/landing/sms-codes（人机验证，44003）；POST /v1/invites/landing-register 请求（agreed）与响应（result=already_registered、44001）；配置 landing.ip_register_limit；H5 invite-landing 页面（协议勾选框、统一页面结构）；users.register_method、users.registered_channel、users.phone_hmac 唯一约束；注销留存表（phone_hmac，留存见 BR-ID-30 ⑩）；consent_records（channel=h5_landing）；relation_change_logs；验收用例 AC-INV-02 |
| BR-INV-06 | **注册页填写邀请码**<br>POST /v1/auth/login/sms 携带 invite_code 时：若手机号对应账号已存在，必须忽略 invite_code 且不报错；若本次请求新建账号，绑定在建号事务内用 SAVEPOINT 执行，绑定校验失败或写库异常时只回滚到 savepoint，账号照常提交，绑定失败不得阻止注册。响应仅在请求携带规范化后非空的 invite_code 时包含 `invite_bind`：{result: bound \| failed \| ignored_existing_user, code?: 30401 \| 30403 \| 30408 \| 42901 \| 50001}，其中 50001 表示绑定内部错误。failed 时 self_bind_used 保持 false，可在期限内补填。注册页绑定同样执行 BR-INV-08 的同设备校验（设备 ID 取请求签名中的 device_id）。config.invite.required 在 MVP 必须为 false。 | 默认假设 | POST /v1/auth/login/sms 响应结构；App 注册页提示文案；config.invite.required；验收用例 |
| BR-INV-07 | **补填条件与期限**<br>POST /v1/me/inviter（phone 级别 + 请求签名 + Idempotency-Key）仅在同时满足以下条件时绑定成功，按 BR-INV-02 顺序校验：(a) parent_id IS NULL 且 self_bind_used=false，否则 30402；(b) 服务端当前时间 &lt; users.created_at + config.invite.backfill_hours（默认 168 小时，精确到秒，等于边界时刻即拒绝），否则 30404；(c) 本人为归属用户的订单数 = 0（orders.user_id=本人，任何 platform_status / rebate_status，含 rebate_status=VOID 或 CLAWED_BACK，自购与分享单都算），本人没有任何状态的找回申请（claim_status 任意值），且直属下级数 = 0（users.parent_id=本人，任何状态），否则 30409；(d) 通过 BR-INV-02 的邀请人校验与 BR-INV-08。成功只允许 1 次。补填成功前已付款、之后才入库或找回的订单，按 BR-INV-13 的付款时间规则不写直推受益人。 | 待决策 | POST /v1/me/inviter；/v1/config.invite.backfill_hours；“我的”页补填入口显隐；orders、order_claims、users 计数查询；错误码 30404、30409；客服话术（为什么不能补填）；验收用例 AC-INV-\* |
| BR-INV-08 | **禁止绑定的关系**<br>以下情形必须返回 30403（文案“不能绑定该邀请人”）：① 邀请人 = 被邀请人；② 邀请人是被邀请人的任意深度下级（从邀请人沿 parent_id 向上遍历，遇到被邀请人即命中；遍历上限 1000 层，超限按命中处理并告警）；③ 同设备：被邀请人设备集合 = login_logs 中该用户保留期内全部登录成功记录的 device_id_hash（register、backfill 渠道再并入本次请求签名中 device_id 的 hash；后台改上级不并入操作人设备），邀请人设备集合 = login_logs 中该用户保留期内全部登录成功记录的 device_id_hash，两集合交集非空即命中。login_logs 只记录 sms/wechat/apple/huawei 登录成功事件，不含 token refresh 与 H5 换 token，留存见 BR-ID-30 ⑥；已注销用户按 F-ACC-10 只保留设备哈希（deleted_identities，留存见 BR-ID-30 ⑩、BR-ID-28），用于本校验。本规则适用于 register、backfill、后台改上级；landing 渠道按 BR-INV-09 事后复核。 | 默认假设 | login_logs（新表）、devices；POST /v1/me/inviter、POST /v1/auth/login/sms、后台改上级；risk_hits（记录命中）；隐私政策（登录日志留存期，见 BR-ID-30）；验收用例 |
| BR-INV-09 | **落地页绑定的同设备复核**<br>对 parent_bind_source=landing 且 login_logs 中尚无该用户任何记录的账号，在其首次 App 登录成功（任一登录方式写入第一条 login_logs）的同一事务内执行 BR-INV-08 ③ 校验（被邀请人设备集合 = 本次登录的 device_id_hash）。命中时登录照常成功；parent_id 置 NULL，写 relation_change_logs(source=risk_same_device) 与 risk_hits，self_bind_used 保持 true（不再给自助绑定机会），不通知邀请人也不推送被邀请人；此后 GET /v1/me 的邀请人状态显示“未绑定”，补填返回 30402（文案“已使用过邀请绑定机会”）。未命中则关系保持。首次 App 登录前被邀请人不可能产生订单，因此不影响任何分佣快照。 | 默认假设 | 登录流程（POST /v1/auth/login/\* 成功分支）；users.parent_id；relation_change_logs、risk_hits、login_logs；GET /v1/me 邀请人状态；验收用例 |
| BR-INV-10 | **不可自改绑与后台改上级**<br>用户端不得提供任何改绑或解绑上级的接口。后台改上级（含解绑为无上级）校验顺序固定为：操作人具备“改绑上级”权限且完成二次验证（step-up）并填写原因 → 目标用户直属下级数 = 0、订单数 = 0（任何状态）、无任何状态的找回申请（否则 30409）→ 新上级存在且 inviter_unavailable=false（BR-INV-02，否则 30401；解绑时跳过）→ BR-INV-08 关系冲突（30403；解绑时跳过）。后台改上级不受 BR-INV-07 的 168 小时期限约束，也不受 growth.invite_bind.enabled 约束。成功时同事务将 self_bind_used 置为 true、parent_bind_source=admin、parent_bound_at=操作时间，并写 relation_change_logs(user_id, old_parent_id, new_parent_id, source=admin, operator_id, reason, created_at +08:00)；解绑后用户不再获得自助绑定机会。已生成的分佣快照不得因改绑变化。 | 默认假设 | 后台用户详情“改上级”操作；04 §11 后台角色权限；users.self_bind_used、parent_bind_source、parent_bound_at；relation_change_logs；客服话术（用户要求改上级）；验收用例 |
| BR-INV-11 | **关系存储与注销影响**<br>users.parent_id 是当前上下级关系的唯一权威来源；历史某一时刻的上级（BR-INV-13 按 paid_at 取值）只能由 relation_change_logs 按 created_at 重放得出（某时刻 t 的上级 = created_at ≤ t 的最后一条记录的 new_parent_id，无记录为无上级），因此所有变更必须同事务写 users.parent_id 与 relation_change_logs，source ∈ {landing, register, backfill, admin, risk_same_device, parent_deleted}。M-内测不建、不读闭包表 user_relation_closure（计酬深度最多 2，直推与间推受益人都由 relation_change_logs 按 paid_at 重放得出，BR-INV-12），P1 做关系树视图时再按需建。上级注销到达 done 状态时，其直属下级 parent_id 必须置 NULL（source=parent_deleted），下级不因此获得新的自助绑定机会；注销 cooling/processing 期间关系不变，但按 BR-INV-02 inviter_unavailable=true，其邀请码对新绑定无效；此期间生成的快照中该上级的受益资格按 BR-CALC-13 判定（BR-INV-13）。上级在冷静期撤回注销后，冷静期内已生成的快照不重算。下级注销 done 后其行匿名化，parent_id 保留用于审计，但不计入上级的直邀人数（BR-INV-16）。 | 默认假设 | users.parent_id；relation_change_logs（新表）；user_relation_closure（推迟到 P1）；注销处理任务（04 §4.5）；02 growth 模块表清单 |
| BR-INV-12 | **计酬层级最多两级**<br>每个子订单的分佣受益人最多三类：归属用户（自购返利或推广收益，见 BR-CALC-04、BR-CALC-24）、其直属上级（paid_at 时刻的上级，BR-INV-13；直推分佣，流水 REFERRAL_CREDIT sub_type=DIRECT，入 PROMO 账户）、直属上级的上级（间推，只在所选规则版本 indirect_enabled=true 时产生；流水 REFERRAL_CREDIT sub_type=INDIRECT，入 PROMO，BR-CALC-05）。depth ≥ 3 的祖先不得出现在 commission_splits.beneficiaries，DB 约束与分账纯函数双重保证；间推开关默认关闭，开启、关闭与比例只能按 BR-CALC-05 发布规则版本。份额公式唯一维护处为 BR-CALC-04，本条只约束层级。再增加层级须新的负责人决策。 | 已确认 | commission_rules.r_indirect_bp、commission_rule_versions.indirect_enabled；commission_splits.beneficiaries（role 含 direct / indirect）；packages/domain 分账纯函数；流水 REFERRAL_CREDIT；后台规则配置页；验收用例（算例表） |
| BR-INV-13 | **直推与间推受益人判定**<br>快照生成时点按 BR-CALC-10：子订单首次同时满足 platform_status ∈ {PAID, RECEIVED, SETTLED} 且已归因时（rebate_status R2 入库已归因，或 R3 找回 / 后台改归属；单一 order_status 写法下为 O2、O11），platform_status=DEPOSIT_PAID 时不生成；找回或改归属时 rebate_status 已为 VOID / CLAWED_BACK 的不生成。直推受益人 = 归属用户在订单 paid_at 时刻的上级（BR-CALC-12；由 relation_change_logs 重放，BR-INV-11），不是快照时刻的 users.parent_id；自购单与分享单都适用（分享单的直推受益人是分享者的上级，不是下单人的上级）。(1) paid_at 时刻归属用户没有上级（含绑定前已付款的订单：paid_at &lt; parent_bound_at，含补填前付款、之后才入库或找回的订单）→ 快照不写直推受益人，该份额归平台（COMMISSION_REVENUE）；(2) 有上级时，上级在快照生成时刻与入账时刻的有效性判定（active / forfeited / held、补入账）只按 BR-CALC-13 执行，本条不另列状态；已实名未满 18 周岁上级的处理按 BR-INV-19、BR-ID-26。`inviter_unavailable`（BR-INV-02）只用于绑定校验、邀请页展示与后台改上级，不用于快照与入账判定。受益人有效性口径分歧登记为 14 §14.3 C-30（负责人与财务裁决）。间推受益人（所选规则版本 indirect_enabled=true 时）= 直推受益人在 paid_at 时刻的上级（同样由 relation_change_logs 重放）；paid_at 时刻归属用户无上级或直推上级无上级 → 不写间推受益人，份额归平台；间推受益人有效性同样只按 BR-CALC-13；间推受益人与归属用户或直推受益人为同一人（异常数据）→ 份额归平台并告警（BR-CALC-05）。快照后换绑、解绑、升降级、上级撤回注销均不重算该单。任何情况下份额不得向更上层顺延。 | 待决策 | commission_splits 生成逻辑；rebate_status 迁移 R2、R3（BR-FUND-01）；orders.paid_at、users.parent_bound_at、relation_change_logs 按时点查询；流水 REFERRAL_CREDIT；客服话术（为什么没收到邀请分佣）；验收用例（分佣算例） |
| BR-INV-14 | **等级定义与默认等级**<br>user_level 取值只有 L1、L2、L3；新账号注册时等级 = config `level.default`（默认 L1），游客报价按默认等级。等级只作为 commission_rules 的维度（平台 × 等级 × 订单类型）影响比例：r_self 取 commission_rules(platform=订单平台, level=归属用户在 paid_at 时刻的等级, order_type=订单 buy_type) 的 r_self_bp（分享单为对应分享比例；BR-CALC-06 称 r_own_bp）；r_direct 取 commission_rules(platform=订单平台, level=上级在 paid_at 时刻的等级, order_type=订单 buy_type) 的 r_direct_bp；r_indirect（间推开启时）取 commission_rules(platform=订单平台, level=间推受益人在 paid_at 时刻的等级, order_type=订单 buy_type) 的 r_indirect_bp；「paid_at 时刻的等级」= level_change_logs 中 effective_at ≤ paid_at 的最后一条的 after（等号取新等级；注册时同事务写一条 source=register、before=NULL、after=level.default、effective_at=created_at 的记录；仍缺记录时取 L1 并告警，BR-CALC-12）；各受益人等级都写入 beneficiaries.level。规则发布校验：对每个 platform × order_type，max_level(r_self_bp 或分享比例) + max_level(r_direct_bp) + max_level(r_indirect_bp) + 活动加成上限（如有，归 BR-CALC）≤ 8000，不满足则不能发布；分账纯函数运行时断言各受益份额之和 ≤ B，违反时不写快照并告警。levels 表每级有 status；等级禁用后不得有新升入，已在该等级的用户保持不变。MVP 只允许后台手动调整等级（step-up + 原因），每次变更写 level_change_logs(user_id, before, after, source, operator_id, reason, effective_at, created_at)，MVP 手动调级 effective_at = created_at = 操作提交时刻（+08:00）；用户端等级界面、自动晋升与保级为 P1。等级变更只影响 paid_at ≥ effective_at 的订单，已有快照不重算；商品报价（quoteRebate）按当前等级实时计算。 | 待决策 | users.level；levels、level_change_logs（新表，含 effective_at；即 BR-CALC-12 所称 user_level_logs）；commission_rules 发布校验、commission_splits.beneficiaries.level；packages/domain 分账纯函数（份额和断言）；GET /v1/me（等级字段）；后台用户详情调级操作、规则配置页；BR-CALC-06 比例配置；LevelUpgrade 桥调用返回 unsupported（MVP） |
| BR-INV-15 | **等级晋升条件**<br>晋升只看本人推广订单，不得使用下级人数、团队订单或团队业绩。自动晋升（P1 启用，MVP 不运行）：每日 03:00 +08:00 计算，统计窗口 = 前 30 个完整自然日 [D−30 00:00, D 00:00) +08:00；计数对象 = 本人为归属用户的子订单（自购 + 分享），且确认收货时间 received_at 落在窗口内、计算时刻 rebate_status 不是 VOID / CLAWED_BACK（单一 order_status 写法下即不是 INVALID / CLAWED_BACK）、基数 B > 0；计数 ≥ `level.promote.l3_min_orders`（默认 50）升 L3，≥ `level.promote.l2_min_orders`（默认 10）升 L2；只升不降（保级规则 P1）；目标等级已禁用时不升入。 | 待决策 | 等级晋升定时任务（P1）；配置项 level.promote.\*；level_change_logs；等级界面文案（P1）；财务单位经济模型（高等级比例成本） |
| BR-INV-16 | **上级可见的下级信息**<br>MVP：上级只能通过 GET /v1/invites/me 看到直邀人数 direct_count = COUNT(users WHERE parent_id=本人 AND 该用户不存在 deletion_status=done 的注销单)，处于 cooling/processing 的下级、被封禁或冻结的下级仍计入，实时计算；不得返回下级列表。P1 页面 InvitedFriends：下级列表只允许包含下级昵称（经敏感词处理后的当前昵称）与注册日期（YYYY-MM-DD，+08:00），按注册时间倒序分页；不得返回或展示下级的 UID、手机号（含脱敏形式）、微信号/unionid、头像、等级、订单（任何字段）、订单数、GMV、收益、活跃状态。P1 上线前隐私政策须写明“你的昵称和注册日期将向邀请你的用户展示”。Agent 与客服不得向上级提供上述禁止信息。后台按角色权限可见（手机号脱敏）。 | 默认假设 | GET /v1/invites/me 响应；P1 InvitedFriends 页面与接口；Agent 工具（不得有查询下级的工具）；客服话术（上级询问下级订单）；隐私政策；验收用例 |
| BR-INV-17 | **邀请分佣流水展示**<br>上级的 PROMO 账户中 REFERRAL_CREDIT 及对应 CLAWBACK 分录在用户端只展示：类型名（REFERRAL_CREDIT=“邀请好友购物分佣”，对应 CLAWBACK=“邀请好友购物分佣扣回”）、带符号金额（分→元，保留 2 位小数）、状态（REFERRAL_CREDIT 固定为“已入账”，CLAWBACK 固定为“已扣回”）、时间（分录 created_at，+08:00，精确到分钟）；不得展示下级昵称、商品标题/图片、订单号、订单金额、平台、下单时间。入账前（rebate_status ∈ {ESTIMATED, WAITING}）的直推分佣只以汇总金额计入“预估推广收益”（用户话术与状态对应见 README §1.2、BR-TEXT-01，状态口径见 BR-FUND-01）。 | 默认假设 | GET /v1/wallet 流水接口字段；H5 收益明细页；客服话术；验收用例 |
| BR-INV-18 | **邀请页与落地页内容**<br>GET /v1/invites/me（phone 级别，未绑手机返回 10005）：本人为已识别的未满 18 周岁用户（BR-INV-19）时返回 30413（data.reason=self_minor，客户端文案与入口隐藏按 BR-INV-19）；其余情况返回 200：{can_invite: bool, invite_code, landing_url, poster{template_id, background_url, variables}, direct_count}。当 inviter_unavailable(本人)=true（BR-INV-02）且不属于上述未成年情形时，can_invite=false，invite_code、landing_url、poster 均为 null，direct_count 照常返回；客户端 can_invite=false 时显示“暂不可邀请”，不展示原因。landing_url = `{share_domains 当前可用域名}/i/{invite_code}`，可附加渠道码参数，URL 中不得含 UID、手机号、昵称等个人信息。邀请文案模板变量只有 {nickname}、{invite_code}、{download_url}；海报 M-内测为固定模板 + 后台配置背景图，多模板 P1。后台保存邀请文案模板时必须执行 BR-INV-20 禁用词与广告法绝对化用语检查，不通过不能保存；海报背景图上线前需人工审核并留审核记录（审核人、时间、结论）。规则说明页不得出现“最高返利”“稳赚”及 BR-INV-20 禁用词。 | 默认假设 | GET /v1/invites/me 响应（can_invite、30413）；InviteShare H5 页；invite-landing H5 页；后台邀请文案模板（禁用词检查）与海报背景配置（审核记录）；config.share_domains |
| BR-INV-19 | **未成年人邀请限制**<br>本条是未成年人邀请与分享侧效果（30401、30413、入口隐藏与提示文案）的唯一维护处。年龄、满 N 周岁时刻、「识别」时点（realname verified 时刻）与推广收益入账、识别前已入账推广收益的处理只在 BR-ID-26 维护；提现限制只在 BR-WDR-06 维护。判定时刻 = 绑定校验、邀请或分享接口请求、快照生成或入账的服务端时刻。已识别且在判定时刻未满 18 周岁的用户：inviter_unavailable=true（BR-INV-02），他人用其邀请码绑定返回 30401「邀请码无效」（不带 reason、不透露邀请人年龄）；本人调用 GET /v1/invites/me（BR-INV-18）、POST /v1/shares 及邀请码生成 / 获取接口返回 30413（data.reason=self_minor），客户端隐藏邀请与分享赚入口并提示「未满 18 周岁暂不开放邀请与分享赚」；作为上级时，快照生成时刻未满 18 周岁则不写直推受益人，份额归平台（BR-INV-13）；已生成的直推快照在入账时刻受益人已被识别为未满 18 周岁的，该份额入账时改归平台（BR-ID-26 (b)）；识别前已入账的 REFERRAL_CREDIT 按 BR-ID-26 (c) 处理（待决策，默认冻结至满 18 周岁）。PROMO 余额的提现限制见 BR-WDR-06。已有的下级关系保留，满 18 周岁时刻之后生成的快照恢复正常。未实名用户无法判断年龄，按成年处理。 | 待决策 | 实名信息（年龄推算，BR-ID-26）；BR-INV-02 inviter_unavailable；commission_splits 生成与入账；PROMO 账户冻结；GET /v1/invites/me、POST /v1/shares、邀请码生成 / 获取接口（30413）；错误码 30413（新增）；客户端邀请与分享赚入口隐藏；验收用例（含 2-29 边界、满周岁当日与次日） |
| BR-INV-20 | **分销用语与不做事项**<br>用户端、后台、接口字段、推送与客服话术不得使用“代理、运营商、总代、合伙人、团队业绩、团队奖、分红、下线”等层级或团队计酬用语，等级只称 L1/L2/L3。不得实现：付费升级或付费获得分佣资格、邀请即升级、按发展人数或团队业绩晋升、面向用户的团队业绩/出单/GMV 排行。间推开关开启后，间推份额在余额流水与收益明细中只作为「邀请奖励」类收入逐笔展示（话术按 BR-TEXT 字典），不单列层级、不称「二级」「间推」；「间推」只作内部术语。文案与代码需通过禁用词 CI 检查；后台可配置文案保存时执行同一词库检查（BR-INV-18）。 | 已确认 | 全部 UI 文案与帮助中心；后台菜单命名与可配置文案；CI 禁用词检查；客服话术；规则说明页；余额流水 / 收益明细（间推份额显示） |
| BR-INV-21 | **邀请开关与配置项**<br>紧急开关 growth.invite_bind.enabled（默认 on，10 秒内生效，改动需 step-up 并告警）为 off 时：backfill 返回 30408；register 渠道照常建号但 invite_bind={failed, 30408}；landing-register 返回 30408 且不建号；后台改上级不受影响；已有关系与分佣计算不受影响；关闭期间注册的用户补填期限不顺延。/v1/config.invite 下发 required（MVP 固定 false）与 backfill_hours（默认 168）。频控配置：invite.fail_limit_per_day=5。等级相关配置：level.default=L1、level.promote.l2_min_orders=10、level.promote.l3_min_orders=50、level.promote.window_days=30。 | 默认假设 | 配置中心 growth.invite_bind.enabled、config.invite、invite.fail_limit_per_day、level.\*；三个绑定接口；落地页暂停态 |
| BR-INV-22 | **邀请奖励仅P1**<br>MVP（M-内测、M-公开）不得发放任何新人红包、签到奖励或邀请奖励。P1（W9 起）邀请奖励规则：奖励在被邀请人首单确认收货后才解锁；同设备、同支付宝、同实名各只能领 1 次；设日预算上限，预算扣减与发放同事务原子执行（条件更新 remaining_fen ≥ amount），扣不到即不发、不排队补发；手机号 HMAC 命中未过期注销留存记录（BR-ID-30 ⑩、BR-ID-28）的账号不计为有效新人（F-ACC-10）；同一 device_id 30 天内登录 ≥3 个账号的第 3 个账号起不发奖励（规划/01 E17 风控；08 尚无 BR-RISK 主题）；流水用 REWARD（sub_type=invite），计入 MKT_EXPENSE。“有效新人”口径见 BR-INV-23；奖励金额与预算数值在 P1 规格中定义。 | 默认假设 | 活动引擎（P1）；预算表 remaining_fen（P1）；注销留存表（phone_hmac，留存见 BR-ID-30 ⑩）；流水 REWARD；风控规则；验收用例（P1） |
| BR-INV-23 | **会员口径仅P1（有效、活跃、新用户、有效新人）**<br>MVP（M-内测、M-公开）不得计算、存储、展示或使用任何会员口径标记，任何 MVP 规则不得以其为条件。P1 启用时：每个口径只能由 packages/domain 的纯函数计算（输入 = 用户、订单与流水事实、判定时刻；参数全部读配置中心 member.\*，修改写操作日志），后台任务、活动引擎、报表共用该函数，不得在 SQL 或客户端另写一版；每个口径附决策表 fixture，至少 3 条，覆盖边界值（2/3 笔、窗口首尾时刻）。默认口径（沿用优券汇）：① 有效用户 = login_logs 中存在首条 App 登录成功记录起永久有效。② 活跃用户：每日 00:10 +08:00 重算；窗口 = [D−member.active_days 00:00, D 00:00) +08:00（默认 30 个完整自然日，D 为重算当日）；计数 = 本人为归属用户的子订单（自购 + 分享）中 paid_at 落在窗口内、且重算时刻 platform_status ∈ {PAID, RECEIVED, SETTLED}、rebate_status ∉ {VOID, CLAWED_BACK} 的笔数；≥ member.active_orders（默认 3）即活跃；不得含邀请人数、下级人数或团队业绩条件（BR-INV-15、BR-INV-20）。③ 新用户 = 本人为归属用户、platform_status 曾到达 PAID 或之后状态的子订单数 = 0；首次跟单即去标，订单之后失效也不恢复。④ 有效新人（P1 邀请奖励与「有效邀请」计数共用）= 被邀请人 parent_bind_source ∈ {landing, register, backfill}（后台改上级不计）、已绑手机、首笔 platform_status 到达 RECEIVED 的子订单实付金额（分）≥ member.valid_newcomer_min_paid_fen，且不命中 BR-INV-22 的排除条件；该门槛由财务在 P1 规格给出，给出前有效新人判定不得启用。「首提」「当日入账」「冻结中」属提现主题（BR-WDR-19、BR-WDR-27），本条不定义。 | 待决策 | packages/domain 会员口径纯函数与决策表 fixture（P1）；配置 member.active_days、member.active_orders、member.valid_newcomer_min_paid_fen；每日 00:10 重算任务（P1）；活动引擎与邀请奖励（P1，BR-INV-22）；BR-WDR-19 手续费矩阵活跃度维度（P1）；后台会员查询筛选（P1） |

### 11.2 细则

#### BR-INV-01 细则 · 邀请码生成与格式

- 状态：已确认
- 默认值：长度 6；字符集 32；每账号最多 5 个候选（含首次）；失败返回 50001；注销后不回收
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 参考_花卷云功能查漏底稿 §1 邀请码生成：「纯数字或数字+字母、最少 6 位，连续碰撞自动加位最多 10 位」
- 来源：规划/01 §5 J7、E12 F-INV-01；规划/04 §7 50001；规划/07 §2 自定义邀请码；PRD修订_后端功能规划 §2.10；PRD v2.1 附录 A；参考_花卷云功能查漏底稿 §1
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 码空间 = 32^6 = 1,073,741,824；100 万用户时单次随机碰撞概率约 0.1%，5 个候选足够，**不采用**花卷云“碰撞自动加位到 10 位”的做法（长度恒为 6，便于前端校验与客服口述）。
- PostgreSQL 同一事务内唯一约束冲突会使事务失效，所以必须用 ON CONFLICT 或 SAVEPOINT，不能直接 catch 后重试。
- 例：生成 `K7M2QX`（合法）；`K0M2QX` 含 0，不可能被生成。
- 例：第 1 个候选命中敏感词、第 2 个唯一冲突、第 3 个写入成功 → 注册成功，共用 3 次。
- 注销用户 `users.invite_code` 保留（行被匿名化），查询命中后按 BR-INV-02 返回 30401。
- P1 自定义码：需后台审核 + 敏感词过滤，仍须满足本条字符集；长度规则届时另定。

#### BR-INV-02 细则 · 邀请码输入校验与错误码

- 状态：默认假设
- 默认值：NFKC + 删空白/零宽 + 大写；inviter_unavailable 含 banned/appealing/frozen、注销 cooling/processing/done、未绑手机、已实名未满 18；校验顺序如上；30401 频控 5 次/日，键 phone_hmac（landing 另加 IP）；新增 30408、30409
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 错误码表：「30301 邀请码无效、30302 已有上级不可修改（映射为 规划 的 30401、30402）」
- 来源：规划/04 §2.5 risk_state、realname_status、deletion_status；规划/04 §7 错误码 30401–30407、42901；规划/01 §6 身份矩阵与未成年规则；PRD修订_后端功能规划 §2.10、错误码表
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

| 错误码 | 含义 | 可重试 |
| --- | --- | --- |
| 30401 | 邀请码无效（含邀请人不存在或不可用、格式错误） | 否 |
| 30402 | 已绑定上级 / 已用过绑定机会 | 否 |
| 30403 | 不能绑定该邀请人（自己、自己的下级、同设备，见 BR-INV-08） | 否 |
| 30404 | 已超过补填期限 | 否 |
| 30408 | 邀请绑定暂停（新增） | 是 |
| 30409 | 已有订单、找回申请或下级，不能补填（新增） | 否 |
| 42901 | 请求过于频繁（沿用 04 §7，带 Retry-After） | 次日 |

- 30405–30407 保持 04 §7 的实名含义（身份证已被实名 / 实名核验不通过 / 年龄不满足），本主题不占用。
- 例：输入 ` ｋ７ｍ２ｑｘ​ ` → NFKC 得 `k7m2qx` + 零宽字符 → 删除空白与零宽 → 大写 `K7M2QX` 再查库。
- 例：输入 `K7M2Q` → 30401 且不查库，计入频控。
- 例：已绑上级的用户提交格式错误的码 → 30402（30402 在格式校验之前）。
- 例：补填期限已过且有订单 → 30404（30404 在 30409 之前）。
- 例：同一 phone_hmac 当天第 5 次 30401 后，第 6 次请求返回 42901，次日 00:00 +08:00 解除；开关关闭时先返回 30408。
- risk_state=frozen 仅冻结提现，是否也视为邀请人不可用见 11.3 第 4 条；默认纳入（风控嫌疑期间不产生新的分佣关系）。
- users.status 在 04 §3.2 有字段但未定义取值，本函数不使用它，封禁以 risk_state 为准。
- 码号归属（C-03）：30408、30409 只表示本表含义。BR-ID-25 原用的 30408（今日实名次数用完）改为 30410；BR-ID-26 原用的 30409 拆为：他人用未满 18 周岁用户的码绑定 → 按 inviter_unavailable 返回 30401（不带 reason、不透露年龄），未满 18 周岁本人调用邀请、分享接口 → 30413（data.reason=self_minor）。码号以 规划/04 §7 为准。按 C-03 默认处理，待负责人确认。

#### BR-INV-03 细则 · 绑定渠道与先到先得

- 状态：待决策（原标默认假设；默认值本身写有「待负责人确认」，且先到先得决定直推受益人归属，按 README §0.3 属订单归属口径）
- 默认值：三渠道；将 01 的优先级解释为时间先后、先成功者锁定；失败不消耗机会；理由：落地页在服务端完成绑定，按时间先后不需要跨渠道比较，也不会出现后到渠道改写已有关系
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 §2.10 绑定上级：「优先级第②项“首次启动识别剪贴板邀请口令”（MVP 不采用，见 BR-INV-04）」
- 来源：规划/01 §5 J7、E12 F-INV-02；规划/04 §6.1、§6.4；规划/02 Agent 工具白名单；PRD修订_后端功能规划 §2.10
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 将 01 F-INV-02 的“优先级 落地页 > 注册页 > 补填”解释为**时间先后**：落地页注册时已绑定，之后用同一手机号在 App 登录携带 invite_code 会被忽略；注册页绑定成功后补填入口返回 30402。
- 失败的尝试不消耗机会；只有写库成功才置 `self_bind_used=true`。
- 微信 / Apple / 华为登录新建的账号没有邀请码输入框，需先绑手机，再在补填期限内走 backfill。
- 例：用户 U 在 10-01 10:00 经落地页注册（parent=A），10-01 10:05 在 App 用同号登录并带 invite_code=B 的码 → 登录成功，parent 仍为 A，`invite_bind.result=ignored_existing_user`。
- 并发：同一用户两个请求同时补填不同码，只有一条条件更新成功，另一条返回 30402。

#### BR-INV-04 细则 · 剪贴板邀请口令不进MVP

- 状态：待决策
- 默认值：MVP 不做自动识别，仅提供用户点击的“粘贴”按钮，按统一正则取第一个匹配；理由：落地页已覆盖锁粉，自动读剪贴板有隐私审核风险
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 §2.10：「② 首次启动识别剪贴板邀请口令（用户点击触发读取）」
- 来源：PRD修订_后端功能规划 §2.10；规划/03 剪贴板实现要点、§5.3 L2；规划/01 E12 F-INV-02

- 理由：落地页注册已在服务端完成绑定，不依赖安装归因；启动读剪贴板会触发 iOS 粘贴提示、增加隐私审核风险，且与 03 的商品剪贴板识别规则冲突。
- 例：用户从微信复制“邀请码 K7M2QX”，在注册页点“粘贴”→ 抽取 `K7M2QX` 填入 → 用户点提交 → 服务端校验。
- 例：剪贴板为“￥AB12CD￥ 邀请码 K7M2QX”→ 取第一个匹配。`AB12CD` 含 1 不匹配，因此填入 `K7M2QX`。
- 例：剪贴板为商品链接、无 6 位候选 → 不填入，提示“未识别到邀请码”。
- 若负责人决定 P1 做“首次启动剪贴板邀请口令”，需另行定义口令格式、与商品口令的区分、有效期。

#### BR-INV-05 细则 · 落地页注册绑定

- 状态：默认假设
- 默认值：发码人机验证与同 IP 注册上限取 BR-ID-32（本条只定其在校验顺序中的位置）；已注册（含注销中）手机号不改关系；已 done 注销的手机号视为新号；邀请码无效不建号且不核销短信码；已注册判定在短信码之后；协议勾选必填
- 决策人：代理可自定
- 依赖平台能力：无
- 取代：
  - 本条旧写法：「landing-register 入参带 captcha_token 每次校验；IP 限流阈值见 BR-RISK，超限 42901；registered_channel=invite_landing；consent channel=invite_landing」（与 BR-ID-32 两套接口与阈值，按 BR-ID-32 合并：发码接口、人机验证、IP 注册上限与 consent channel 取 BR-ID-32 / BR-ID-04，绑定语义与校验顺序保留本条）
- 来源：规划/01 §5 J7 步骤 2、E12 F-INV-02、F-ACC-10、F-PRIV-01、F-PRIV-05；规划/04 §3.2 users、consent_records；§6.4；§7 10004、42901；规划/03 H5 landing；PRD修订_后端功能规划 §2.1 注册来源、§2.12 同 IP 注册；08 BR-ID-04、BR-ID-05、BR-ID-32
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 流程：好友微信内打开 `{share_domain}/i/K7M2QX` → 勾选协议 → 输入手机号 → 完成人机验证并发码（landing/sms-codes）→ 输入验证码提交（landing-register）→ 注册并绑定 → 引导下载 → App 内同号登录，`GET /v1/me` 可见已有上级（本人只看到“已绑定”，见 11.3 第 5 条）。
- 落地页发码人机验证、同 IP 注册上限的计数口径、窗口边界与例子只在 BR-ID-32 维护，本条不重复；同设备注册上限（BR-ID-05）不适用于落地页（不采集设备，改由 BR-INV-09 首次 App 登录时复核）。
- 例：13800000000 首次注册，邀请人 A 正常 → 创建 U，U.parent_id=A；同一号码再次提交且短信码正确 → `already_registered`，不改 U。
- 例：手机号已注册但邀请码无效 → 30401（邀请码校验在前），短信码不核销，不暴露手机号是否注册。
- 例：该号 2026-06 注销并已 done，2026-10 在落地页注册 → 按新号建号并绑定；新号不能领新人奖励（F-ACC-10，BR-INV-22）。
- 页面提示：already_registered →“该手机号已注册，请打开 App；符合条件可在 App 内补填邀请码”；30408 →“邀请活动暂停，可直接下载 App 注册”，不创建账号；44001 →“注册人数过多，请稍后再试或下载 App 注册”。
- 注销 done 时 users.phone_hmac 移入注销留存表（deleted_identities；留存见 BR-ID-30 ⑩、BR-ID-28，用于防重复领奖），不再占用 users 的唯一约束；该处理归注销主题，此处只写依赖。

#### BR-INV-06 细则 · 注册页填写邀请码

- 状态：默认假设
- 默认值：SAVEPOINT 内绑定；绑定失败不阻止注册；老用户忽略邀请码；仅携带非空码时返回 invite_bind
- 决策人：代理可自定
- 依赖平台能力：无
- 取代：无
- 来源：规划/04 §6.1、§7、§10.1；规划/01 E12 F-INV-02
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 客户端对 result=failed 提示“邀请码未生效：{原因}，注册 7 天内可在“我的”补填”；42901 提示“尝试次数过多，请明天再试”。
- 例：新号注册携带自己同设备另一账号 A 的码 → 账号创建成功，invite_bind={failed, 30403}，self_bind_used 仍为 false，可在期限内用其他人的码补填。
- 例：老用户登录携带任意码 → invite_bind.result=ignored_existing_user。
- 例：invite_code 为全角空格 → 视为未携带，响应无 invite_bind。
- 例：绑定写库时数据库异常 → 回滚到 savepoint，账号创建成功，invite_bind={failed, 50001}，告警。

#### BR-INV-07 细则 · 补填条件与期限

- 状态：待决策（原标默认假设；默认值本身写有「待负责人确认」，补填条件决定直推受益人归属，按 README §0.3 属订单归属口径）
- 默认值：168 小时（不含边界）；无订单（含失效）、无任何找回申请、无下级；成功 1 次；01 的“7 天、无订单、无下级”已定，精确边界与订单/找回口径为代理细化；理由：失效单与找回申请也计入，防止先下单再挑上级
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 参考_花卷云功能查漏底稿 §1、§16 #24：「补填仅限已登录、无上级、无订单、无粉丝（未给期限）」
  - 规划/04 §10.1：「补填期限随 config.invite 下发（具体值没定义）」
- 来源：规划/01 §5 J7 步骤 3、E12 F-INV-02；规划/04 §2.5 claim_status、§3.2 orders.paid_at、§6.4、§7、§10.1；PRD修订_后端功能规划 §2.10；参考_花卷云功能查漏底稿 §1
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 期限起点是账号创建时间，不是绑手机时间；微信登录后第 5 天才绑手机，补填窗口只剩约 2 天。
- 例：created_at=2026-10-01T10:00:00+08:00 → 2026-10-08T09:59:59+08:00 可补填；2026-10-08T10:00:00+08:00 返回 30404。
- 例：注册第 2 天已有 1 笔已失效订单 → 30409（失效单也算，防止先下单再挑上级）。
- 例：用户提交过找回申请（submitted，订单仍在未归因池）→ 30409。
- 例：用户 10-02 付款，联盟同步延迟，10-03 补填 A 成功，10-04 订单入库 → 订单 paid_at &lt; parent_bound_at，快照不写 A，份额归平台（BR-INV-13）。
- 只转链未下单的用户仍可补填（不以 link_logs 为条件）。
- 期限随 `/v1/config.invite.backfill_hours` 下发，客户端据此隐藏补填入口，服务端以自身时钟为准。
- 订单状态按 BR-FUND-01 双状态书写：「任何状态」指任意 platform_status 与任意 rebate_status（单一 order_status 写法下即含 INVALID、CLAWED_BACK）；rebate_status=UNATTRIBUTED 的订单 user_id 为空，不属于本人，不计入。按 C-01 默认处理，待负责人确认。

#### BR-INV-08 细则 · 禁止绑定的关系

- 状态：默认假设
- 默认值：三种情形沿用 01；同设备窗口 = login_logs 留存期（BR-ID-30 ⑥）；只比较登录成功记录
- 决策人：负责人
- 依赖平台能力：无
- 取代：无
- 来源：规划/01 §5 J7 步骤 4、E12 F-INV-03、F-ACC-10、§7.6；规划/04 §3.2（无 login_logs 表）、§7 30403；PRD修订_后端功能规划 §2.10
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

- 例：A 与 U 在 60 天前曾在同一台 iPhone（device_id=d1）登录过，U 补填 A 的码 → 30403。
- 例：A 与 U 同设备登录发生在 200 天前（已超出 login_logs 留存期，BR-ID-30 ⑥）→ 不命中。
- 例：后台想把 U 的上级改为 V（V 是 U 的下级）→ 按 BR-INV-10 顺序先因 U 有下级返回 30409；② 的成环检查作为兜底。
- 设备 ID 重置后生成的新 device_id 视为不同设备，重置识别与同设备多账号归 规划/01 E17 风控（08 尚无 BR-RISK 主题）、BR-ID-05 同设备注册上限与 02 设备注册。
- 同设备窗口 = login_logs 留存期（BR-ID-30 ⑥；受最小必要与 01 §7.6 留存约束，不能取“全部历史”）；若负责人要求与 BR-ID-05 同设备注册上限的 30×24 小时口径统一，改本条即可（11.3 第 9 条）。

#### BR-INV-09 细则 · 落地页绑定的同设备复核

- 状态：默认假设
- 默认值：首次 App 登录成功同事务复核；命中即解除关系且不再给绑定机会；登录不受影响
- 决策人：负责人
- 依赖平台能力：无
- 取代：无
- 来源：规划/04 §6.4 landing-register 用人机验证替代设备签名；规划/01 E12 F-INV-03
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 挂载点是登录成功，不是 POST /v1/devices（设备注册为 none 级别、发生在登录前、与用户无关）。
- 例：A 用自己的手机打开落地页帮小号 U 注册（landing 不采集设备），随后 U 在 A 的同一台手机上首次登录 App → 登录成功，关系解除，U 以后下单直推份额归平台。
- 若 U 先在另一台设备首次登录、之后才在 A 的设备登录：复核只在首次登录执行，后续同设备登录交由 规划/01 E17 风控的同设备多账号规则处理（08 尚无 BR-RISK 主题）。

#### BR-INV-10 细则 · 不可自改绑与后台改上级

- 状态：默认假设
- 默认值：无下级 + 无订单 + 无找回申请 + 新上级可用 + step-up + 日志；成功后 self_bind_used=true；不受期限与开关约束
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 规划/01 E12 F-INV-03：「后台改绑需二次验证并记日志（未给前置条件）」
- 来源：规划/01 E12 F-INV-03；PRD修订_后端功能规划 §2.10 后台改上级、表 relation_change_logs；参考_花卷云功能查漏底稿 §16 #24
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 例：U 注册第 3 天，无订单、无找回、无下级，客服核实 U 本想填 B 的码却误填 A → 运营主管 step-up 后改为 B，日志记录 A→B，self_bind_used=true。
- 例：U 从未自助绑定，后台设上级 B 后又解绑 → U 不能再走 backfill（30402），防止用“后台解绑 + 自助补填”绕过只绑 1 次。
- 例：U 已有 1 笔订单 → 后台改上级按钮置灰，接口返回 30409。
- 改绑前已付款、之后入库的订单按 BR-INV-13 付款时间规则不写新上级，而是写 paid_at 时刻的上级（原上级；其快照、入账时的有效性按 BR-CALC-13；改绑前无上级则不写）。按 C-06 默认处理，待负责人确认。
- 例：U 的上级 A 于 10-05 10:00 被后台改为 B；U 10-05 09:30 付款的订单 10-06 入库 → 直推受益人 A；10-05 10:30 付款的订单 → B。
- 条件采纳后端功能规划：有订单或下级后改绑会让历史/未来分佣受益人与用户认知不一致，并可能被用于转移下级。

#### BR-INV-11 细则 · 关系存储与注销影响

- 状态：默认假设
- 默认值：parent_id 权威 + 变更日志；闭包表 P1；注销中上级的受益资格按 BR-CALC-13，撤回不重算
- 决策人：代理可自定
- 依赖平台能力：无
- 取代：
  - 规划/01 E12 F-INV-04；规划/02 growth 模块；规划/04 §3.2：「关系树 parent_id + 闭包表 M-内测」
- 来源：规划/01 E12 F-INV-04、F-ACC-10；规划/02 模块表 growth；规划/04 §2.5 deletion_status、§3.2、§4.5；PRD修订_后端功能规划 §2.10 关系存储
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

- 闭包表改 P1 的理由：D8 计酬深度最多 2，按 paid_at 重放 relation_change_logs 两次即可得到直推与间推受益人；补填与后台改绑都要求“无下级”，成环只需沿 parent_id 向上遍历即可判定（BR-INV-08），闭包表只增加维护成本。
- 例：A 于 10-10 申请注销（cooling 至 10-17），10-17 进入 processing，10-20 done → 10-20 起 A 的直属下级 U、V 的 parent_id=NULL；U 在 10-14 付款、10-15 生成快照的订单，快照时 A 处于 cooling，按 BR-CALC-13 记 A 为 active；该单入账时 A 已进入 processing 或 done → forfeited，份额归平台（BR-INV-13）。
- 例：A 在冷静期撤回注销 → 关系全程未变；冷静期内生成的快照已按 BR-CALC-13 记 A 为 active，不重算，入账照常。
- relation_change_logs 同时承担 BR-CALC-12 所称「user_relation_logs（bound_at / unbound_at）」：bound_at = 该条 created_at，unbound_at = 同一用户下一条记录的 created_at；表名统一见 13。按 C-06 默认处理，待负责人确认。

#### BR-INV-12 细则 · 计酬层级最多两级

- 状态：已确认（负责人 2026-10-01 确认 D8 新口径；间推比例取值仍待财务，见 BR-CALC-05）
- 默认值：无（已确认，按规则执行）；间推开关默认关闭
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 本条旧写法（2026-09-30，「计酬层级只到直推」）：「间推比例必须等于 0：commission_rules 的间推比例字段加数据库 CHECK (= 0)，后台不提供输入项；depth ≥2 的祖先不得出现在 commission_splits.beneficiaries……在取得分销模式书面法律意见（06 Q-F5）且负责人另行决策并发布迁移之前，不得开启间推」
  - PRD v2.1 §2、§15：「计酬不超过两层；MVP 间推默认 0（可配）」
- 来源：docs/changes/20261001-间推二级奖励.md；规划/00 §3.2 D8；规划/01 §3 分账口径、E12 F-INV-04；规划/02 §8.3；规划/06 Q-B1、Q-F5；PRD修订_后端功能规划 §2.10 分佣规则 r_l2 CHECK=0；PRD v2.1 §15

- 例：B=1234 分，r_self=5000、r_direct=1000 → 自购 617、直推 floor(123.4)=123、平台 494。
- 例：C→B→A（C 邀请 B，B 邀请 A），A 自购 B=1234 → 间推关闭：B 得 123，C 得 0 且不出现在快照；间推开启（r_indirect=500）：B 得 123，C 得 61。
- 例：D→C→B→A，A 自购 → D 是 depth 3，任何版本都不进入受益人。
- r_direct 默认值与比例配置归 BR-CALC-06 维护，跨等级比例上限的发布校验口径见 BR-INV-14。
- 依据 D8（负责人 2026-10-01 确认）；06 Q-F5 书面法律意见由负责人跟进，不作技术闸门。

#### BR-INV-13 细则 · 直推与间推受益人判定

- 状态：待决策
- 默认值：分享单也给分享者的上级直推分佣（理由：PROMO 账户口径已含直推，与自购单一致）；备选仅自购单给直推；上级按 paid_at 时刻取值（理由：结果可重放，不受入库与找回延迟影响）；绑定前付款时份额归平台；上级有效性按 BR-CALC-13（C-30）；待负责人确认
- 决策人：负责人
- 依赖平台能力：各平台订单 paid_at 字段准确性（09 订单归属链路，待实测）
- 取代：
  - 本条旧写法：「直推受益人 = 分佣快照生成时刻（订单首次入库 O2，或找回/后台归属 O11）归属用户的 users.parent_id，另排除 paid_at &lt; parent_bound_at」（按 C-06 改为 paid_at 时刻的上级；排除条件保留并并入 (1)）
- 来源：docs/changes/20261001-间推二级奖励.md（间推受益人）；规划/01 §3 快照、F-SET-03、§6 未成年规则；规划/02 §8.3；规划/04 §3.2 orders.paid_at、commission_splits、状态机 O2/O11；08 BR-FUND-01、BR-CALC-10、BR-CALC-12
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：A 邀请 U；U 于 10-05 自购，订单 10-05 首次入库，B=1000，r_self=5000、r_direct=1000 → U 500、A 100、平台 400。
- 例：A 在 10-04 被封禁，U 10-05 下单 → 按 BR-CALC-13 快照记 A 为 active；入账时 A 仍为 banned → forfeited，U 500、平台 500。A 若为 frozen → 该份额 held，解冻后补入账（BR-FUND-01 R5a）。
- 例：U 是分享者，外部好友 X 通过 U 的分享链接下单（buy_type=share）→ U 得推广收益，U 的上级 A 得直推分佣（本条待决策项）。
- 例：U 10-02 付款，10-03 补填 A，10-04 订单入库 → paid_at &lt; parent_bound_at，不写 A。
- 例（间推开启）：Z 邀请 A、A 邀请 U；U 10-05 自购 → 直推 A、间推 Z；若 A 10-06 才绑定 Z → 间推不写，归平台；Z 已注销 → 按 BR-CALC-13 forfeited，不顺延给 Z 的上级。
- 例：A 10-10 申请注销、10-12 撤回；U 10-11、10-13 入库的订单都写 A（cooling 不算失效，BR-CALC-13）。
- 例：U 的定金单 10-01 付定金（platform_status=DEPOSIT_PAID，不生成快照），10-11 付尾款（→PAID）时生成快照；直推受益人与等级取值时刻见 11.3 第 10 条（默认 deposit_paid_at）。
- 例：U 的订单 10-05 付款、10-06 已失效（rebate_status=VOID），10-08 找回通过 → 只设置 user_id 与 user_basis=claim（BR-FUND-01 R3b），不生成快照，无直推份额。
- paid_at 取联盟订单付款时间，时区 +08:00；各平台 paid_at 是否可靠需在 09 验证（待实测；预售单以 deposit_paid_at 还是尾款时间为准见 11.3 第 10 条）。
- 状态名按 BR-FUND-01 双状态书写（O2 ≈ R2、O11 ≈ R3，映射见本主题开头）。按 C-01 默认处理，待负责人确认。
- 快照生成时点按 BR-CALC-10、上级取 paid_at 时刻按 BR-CALC-12，绑定前付款不写的排除条件保留。按 C-06 默认处理，待负责人确认。
- 上级有效性改为只引用 BR-CALC-13：原 (2)「快照生成时刻 inviter_unavailable(该上级)=true（含封禁、申诉、冻结、注销 cooling/processing/done、已实名未满 18）→ 不写直推受益人」与 BR-CALC-13（banned/frozen/appealing 快照记 active、入账时判 forfeited 或 held，cooling 不算失效）结论相反，已删去；分歧登记 14 §14.3 C-30，待负责人与财务裁决。

#### BR-INV-14 细则 · 等级定义与默认等级

- 状态：待决策
- 默认值：默认 L1；MVP 仅后台手动调级；r_direct 默认按上级在 paid_at 时刻的等级（理由：与上级自身等级激励一致；取值时刻按 BR-CALC-12），备选按归属用户等级；跨等级最大组合 ≤ 8000 发布校验；待负责人/财务确认
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - PRD v2.1 §2：「P1 等级分佣界面（未说明 MVP 等级如何变化）」
  - 规划/01 §3 分账口径：「r_self + r_direct ≤ 8000（未说明跨等级组合如何校验）」
- 来源：规划/00 §3.2 D8、§4；docs/changes/20261001-间推二级奖励.md（r_indirect 取值与上限）；规划/01 §3、E12 F-INV-05/07；规划/04 §2.5、§3.2；PRD修订_后端功能规划 §2.10 等级
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

- 例：U 在 10-10 12:00:00 被后台从 L1 调到 L2；paid_at=10-10 11:59:59 的订单即使 10-11 才入库，仍按 L1 比例；paid_at=10-10 12:00:00（等于生效时刻）及以后的按 L2。
- 例：taobao × self 下 r_self 为 L1 5000 / L2 5500 / L3 6000，r_direct 为 L1 1000 / L2 1500 / L3 2500 → 6000 + 2500 = 8500 > 8000，发布被拒（逐行校验会漏掉 L3 自购 + L3 上级的组合）。
- 例：L3 被禁用后，自动晋升任务（P1）最多升到 L2；已是 L3 的用户保持 L3。
- r_direct 按上级等级还是按归属用户等级取值属于金额口径，待负责人/财务确认。
- 等级取值时刻由「快照时等级」改为「paid_at 时刻等级」（BR-CALC-12），与 BR-INV-13 上级取值时刻一致。按 C-06 默认处理，待负责人确认。

#### BR-INV-15 细则 · 等级晋升条件

- 状态：待决策
- 默认值：L1 默认；近 30 个完整自然日本人子订单（确认收货、未失效、B>0）≥10 → L2、≥50 → L3；只升不降；理由：沿用 06 Q-B1 默认，改用确认收货口径防刷
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 参考_花卷云功能查漏底稿 §17：「拉人头晋升（不做）」
- 来源：规划/06 Q-B1 等级 L1–L3 晋升条件；规划/00 §3.2 D8；规划/01 E12 F-INV-05；PRD修订_后端功能规划 §2.10 等级（自动升级 P1）
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：D=2026-11-01，窗口为 10-02 00:00 至 10-31 23:59:59；该窗口确认收货且未失效的本人子订单 12 笔 → 升 L2；其中 1 笔 11-02 退款扣回不影响已升等级。
- 例：窗口内 60 笔，其中 15 笔 rebate_status=VOID → 有效 45 笔 → L2，不升 L3。
- 状态名按 BR-FUND-01 双状态书写（INVALID ≈ VOID）。按 C-01 默认处理，待负责人确认。
- 按确认收货而非付款计数，防止“下单后退款刷等级”。
- 自购是否计入：默认计入（“本人推广订单” = 本人链接产生的订单）；若负责人只认分享单，改计数口径即可。

#### BR-INV-16 细则 · 上级可见的下级信息

- 状态：默认假设
- 默认值：MVP 仅直邀人数（排除注销 done）；P1 昵称 + 注册日期，需隐私政策告知
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 参考_花卷云功能查漏底稿 §2：「团队订单隐私脱敏且不可点（本系统不展示任何团队订单）」
  - 规划/01 §5 J7 第 5 步：「上级只能看到下级的昵称和注册时间（MVP 改为只看直邀人数）」
- 来源：规划/01 §4 页面清单、§5 J7 步骤 5、E12 F-INV-07；规划/00 §4 分销；规划/04 §6.4；PRD修订_后端功能规划 §2.10 团队页/下级隐私；参考_花卷云功能查漏底稿 §2
- 需同步修改的规划文档：4 处（计数仅作记录，落点见 README §0.6）

- 例：A 有 3 个直属下级，其中 1 个注销已 done、1 个在冷静期 → direct_count=2。
- 例：P1 页面一行显示“小王 2026-10-03”，点击无详情页。
- 01 J7 第 5 步（上级看昵称与注册时间）与 F-INV-07（团队页只显示直邀人数，P1）互相矛盾；本条裁决：MVP 只给直邀人数（邀请页），昵称 + 注册日期列表放 P1。
- 页面名 TeamFans 含“团队”语义，按 BR-INV-20 改为 InvitedFriends。
- 下级是否能看到自己上级的信息未定义，见 11.3 第 5 条。

#### BR-INV-17 细则 · 邀请分佣流水展示

- 状态：默认假设
- 默认值：单条展示；状态由分录类型推出；时间 = 分录 created_at 精确到分钟；不含任何下级或订单字段
- 决策人：负责人
- 依赖平台能力：无
- 取代：无
- 来源：规划/01 §5 J7 步骤 5；规划/04 §2.4 REFERRAL_CREDIT、ledger_entries；PRD修订_后端功能规划 §2.10 下级隐私
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- ledger_entries 只插入、没有状态字段，REFERRAL_CREDIT 在入账时才生成，所以“状态”由分录类型推出，不另存。
- 例：U 买了一件 99 元商品，A 的收益明细出现“邀请好友购物分佣 +1.23 元 已入账 2026-10-25 10:00”，看不到是谁、买了什么。
- 扣回显示“邀请好友购物分佣扣回 −1.23 元 已扣回 2026-11-02 09:14”。
- 单条流水金额仍可能让上级推测下级有消费，这是分佣本身不可避免的；如需进一步弱化可改为按日汇总（未采用）。
- 取代本条旧写法「预估中的直推分佣计入“待到账”」：按 README §1.2 与 BR-TEXT-01 方案 A，入账前的推广收益称「预估推广收益」，订单侧用「入账」、不用「到账」。按 C-02 默认处理，待负责人确认。

#### BR-INV-18 细则 · 邀请页与落地页内容

- 状态：默认假设
- 默认值：200 + can_invite（本人已识别未满 18 周岁时 30413）；固定模板海报；三变量文案；文案保存时禁用词检查、背景图人工审核
- 决策人：运营
- 依赖平台能力：无
- 取代：无
- 来源：规划/01 §5 J7 步骤 1、E12 F-INV-06；规划/04 §6.4；规划/07 §2 02/03；规划/06 Q-F4
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：A 正常 → can_invite=true，landing_url=`https://s.example.cn/i/K7M2QX?ch=poster`（域名为占位，实际取 config.share_domains）。
- 例：A 被封禁 → {can_invite:false, invite_code:null, landing_url:null, poster:null, direct_count:5}。
- 例：运营在文案模板中写“全网最高返利”→ 保存被拒，提示命中绝对化用语。
- 例：A 已实名、未满 18 周岁 → 30413（data.reason=self_minor）；A 被封禁 → 200 且 can_invite=false，不说明原因。未成年情形按 BR-INV-19 明示原因（提示「未满 18 周岁暂不开放邀请与分享赚」），其他不可用情形不展示原因。
- 取代本条旧写法「恒返回 200，未成年本人也只返回 can_invite=false」：与 BR-INV-19 及错误码 30413（self_minor）对齐。
- 分享域名被封时换域名，已发出的旧海报二维码失效由 规划/01 E13 分享的域名切换规则处理（08 尚无 BR-SHARE 主题）。

#### BR-INV-19 细则 · 未成年人邀请限制

- 状态：待决策
- 默认值：已识别未满 18 周岁不可邀请（他人绑定 30401、本人邀请页 30413）、不受益直推分佣；识别后未入账直推份额归平台；识别前已入账 REFERRAL_CREDIT 按 BR-ID-26 (c) 默认冻结至满 18 周岁；满周岁时刻口径按 BR-ID-26（C-15 默认处理，待法务确认）；01 §6 未成年规则本身待法务确认
- 决策人：法务
- 依赖平台能力：无
- 取代：
  - 本条旧写法：「当日 ≥ 出生日期加 18 年的同月同日即满 18 周岁；2 月 29 日出生者平年按 3 月 1 日计；邀请页 can_invite=false；已入账 REFERRAL_CREDIT 冻结、由法务决定退回或保留」（年龄口径与已入账处理改为引用 BR-ID-26，避免两处维护；邀请页按 30413 对齐）
  - BR-ID-26 (a) 旧写法：「他人用其邀请码绑定时按 BR-INV-02 的 inviter_unavailable 返回 30401…其本人调用 POST /v1/shares、GET /v1/invites/me 及邀请码生成/获取接口返回新增码 30413…」（内容并入本条，BR-ID-26 (a) 改为引用本条）
- 来源：规划/01 §6 未成年规则（待法务确认）、F-ACC-08；规划/04 §2.5 realname_status；08 BR-ID-26

- 例：A 2008-12-01 出生、已实名；2026-10-10 下级 U 的订单生成快照 → A 未满 18，该单直推份额归平台；按 BR-ID-26 口径 A 于 2026-12-02 00:00 +08:00 满 18 周岁，此后生成的快照 A 正常受益。
- 例：2008-02-29 出生者：按 BR-ID-26 在 2026-03-02 00:00 +08:00 满 18 周岁。
- 例：A 未实名，期间累计直推分佣 300 元（已入账）；10-20 首次提现触发实名，推算 16 岁 → 300 元按 BR-ID-26 (c) 默认冻结至满 18 周岁、不可提现；未入账的直推份额入账时归平台。
- 例：16 岁已实名用户 U 的邀请码被好友输入 → 30401「邀请码无效」（与邀请人不存在同一文案）；U 本人打开邀请页或点分享赚 → 30413，客户端隐藏邀请与分享赚入口。
- 满周岁时刻按 BR-ID-26（C-15 默认，待法务确认）。
- 错误码：他人绑定由 30409(inviter_minor) 改为 30401（BR-INV-02 inviter_unavailable，不透露年龄）；本人分享、邀请由 30409(self_minor) 改为 30413（30409 由 BR-INV-07 用于「不能补填」）。按 C-03 默认处理，待负责人确认。
- 实名在首次提现时触发，未实名未成年人在提现前仍可邀请与累计分佣，属已知缺口，由上面的冻结规则兜底。

#### BR-INV-20 细则 · 分销用语与不做事项

- 状态：已确认（D8 于 2026-10-01 经负责人确认，禁止项除「间推收益展示」外不变）
- 默认值：无（已确认，按规则执行）
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 本条旧写法（2026-09-30）：不得实现「间推收益展示」（改为按「邀请奖励」类收入逐笔展示）
  - PRD v2.1 §2 范围表：「P1 团队收益页、排行榜」
- 来源：docs/changes/20261001-间推二级奖励.md；规划/00 §3.2 D8、§4、§5；规划/01 §4 页面清单（TeamFans / RankList）；规划/07 §2 不做清单；PRD v2.1 §15；参考_花卷云功能查漏底稿 §17
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：邀请列表标题用“我邀请的好友”，不用“我的团队”；页面名用 InvitedFriends，不用 TeamFans。
- 例：间推开启后，Z 的余额流水出现一笔「邀请奖励」+0.61，不显示「来自二级好友 U」或层级。
- 这些限制的依据是 D8（负责人 2026-10-01 确认）。解除需负责人决策。

#### BR-INV-21 细则 · 邀请开关与配置项

- 状态：默认假设
- 默认值：growth.invite_bind.enabled=on（生效 ≤10 秒，改动 step-up + 告警）；config.invite.required=false；config.invite.backfill_hours=168；invite.fail_limit_per_day=5（按 +08:00 自然日）；level.default=L1；level.promote.l2_min_orders=10；level.promote.l3_min_orders=50；level.promote.window_days=30（P1 才使用）；landing.ip_register_limit=3（由 BR-ID-32 维护，此处只列依赖）
- 决策人：代理可自定
- 依赖平台能力：无
- 取代：无
- 来源：规划/04 §10.1、§10.2；规划/01 E12 F-INV-02
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：10-10 20:00 关闭开关，20:05 用户补填 → 30408；10-11 09:00 重新打开后可补填（仍受 168 小时限制）。

#### BR-INV-22 细则 · 邀请奖励仅P1

- 状态：默认假设
- 默认值：MVP 不发；P1 首单确认收货后解锁、预算原子扣减、注销留存记录未过期（BR-ID-30 ⑩）时重注册不算有效新人
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 参考_花卷云功能查漏底稿 §1、§8：「会员有效/活跃/新会员/有效新人口径（不在 MVP 采用）」
- 来源：规划/00 §3.2 D9、§4；规划/01 E12 F-INV-08、F-ACC-10；规划/04 §2.4；PRD修订_后端功能规划 §0.4 B2、§2.12

- 例：当日预算剩余 5 元，两笔 3 元奖励并发发放 → 只有一笔条件更新成功，另一笔不发。
- 例：用户注销后 100 天用同号重新注册并被邀请 → 不计为有效新人，邀请人不得奖励。
- 花卷云“有效新人 = 绑手机/微信/备案 + 首单或首次收货金额 ≥X”口径已整理为 BR-INV-23 的默认口径（P1，待决策），不在 MVP 实现。

#### BR-INV-23 细则 · 会员口径仅P1（有效、活跃、新用户、有效新人）

- 状态：待决策（口径用于 P1 奖励与手续费，属金额口径）
- 默认值：MVP 不启用；P1 active_days=30、active_orders=3、每日 00:10 +08:00 重算；有效 = 首次 App 登录成功；新用户 = 无 PAID 及以后状态的本人订单；有效新人金额门槛由财务在 P1 规格给出；理由：沿用优券汇口径，老用户熟悉，迁移后手续费与奖励口径不突变（PRD评审_v2 F-73）
- 决策人：负责人（金额门槛：财务）
- 依赖平台能力：无（订单状态与 paid_at 的可靠性随 BR-FUND-02 在 规划/09 验证）
- 取代：
  - 参考_花卷云功能查漏底稿 §1 会员状态口径：「活跃 = 近 30 天邀请 5 人、近 30 天有 3 笔有效单，所选条件同时满足」（去掉邀请人数条件，BR-INV-20）
  - 参考_花卷云功能查漏底稿 §1：「有效 = 触发任一选定事件（绑手机 / 下载 / 淘宝备案 / 下单 / 收货 / 提现）后永久有效」（固定为首次 App 登录成功）
  - 参考_花卷云功能查漏底稿 §8 有效新人判定：「条件一绑手机 / 绑微信 / 淘宝备案多选，条件二首单金额或首次收货金额 ≥X，两组任意或同时满足」（固定为已绑手机 + 首次确认收货子订单实付 ≥ 门槛）
- 来源：PRD修订_后端功能规划 §2.6 会员口径；PRD评审_v2 F-73；参考_花卷云功能查漏底稿 §1 会员状态口径、§8 有效新人判定

- 例：D=2026-11-01，00:10 重算，窗口 = [2026-10-02 00:00, 2026-11-01 00:00) +08:00；U 在窗口内付款 3 笔且均未失效 → 活跃；其中 1 笔 10-25 变为 rebate_status=VOID → 2 笔，不活跃。
- 例：paid_at=2026-10-01T23:59:59+08:00 的订单不在该窗口内；paid_at=2026-10-02T00:00:00+08:00 在窗口内。
- 例：U 首单 10-05 付款（首次 PAID）、10-06 失效 → 10-05 起不再是新用户，失效不恢复。
- 例：门槛取示例值 2000 分；被邀请人 V 首笔确认收货子订单实付 1800 分 → 不是有效新人；实付 2000 分 → 是（等于门槛即满足）。
- 本条按 R6 只写到 P1 开工前需要的口径；P1 规格需补齐的未知项见 11.3 第 12 条。

### 11.3 本主题未决问题

1. 推广自买单（规划/01 E17 风控，08 尚无 BR-RISK 主题：分享单下单人与推广者同设备/同支付宝/同收货手机号）判定作废推广收益时，推广者上级的直推分佣是否同时作废？默认：同时作废（整单视为违规）。需负责人确认。
2. commission_rules 中 r_direct 按上级等级取值还是按下单归属用户等级取值？BR-INV-14 默认按上级在 paid_at 时刻的等级（已改为待决策），需负责人/财务确认。
3. 分享单是否给分享者的上级直推分佣（BR-INV-13 待决策）？默认给。
4. risk_state=frozen（仅提现冻结）是否也使邀请人不可用、不受益直推分佣？BR-INV-02 默认纳入；若负责人认为 frozen 只影响提现，从 inviter_unavailable 中去掉 frozen，BR-INV-18 自动同步。直推受益人的 frozen 处理不走 inviter_unavailable，按 BR-CALC-13（held，C-30）。
5. 被邀请人能否在 App 内看到自己的上级（昵称或邀请码）？规划 未定义；默认只显示“已绑定邀请人”，不显示对方信息。
6. 晋升阈值（L2 ≥10、L3 ≥50）与各等级 r_self/r_direct 比例的具体取值需财务按单位经济模型确认（06 Q-B1、后端规划 B11），且须满足 BR-INV-14 跨等级最大组合 ≤ 8000。
7. 分销模式书面法律意见（06 Q-F5）由负责人跟进，不作技术闸门；间推开关按 BR-CALC-05 审批流程开启（2026-10-01 更新）。
8. 实名后发现未成年上级时，识别前已入账 REFERRAL_CREDIT 的处理由 BR-ID-26 (c) 统一决定（默认冻结至满 18 周岁，法务与负责人选定）；满 18 周岁时刻按 BR-ID-26（C-15 默认处理，待法务确认）。本主题不另行决定。
9. 同设备判定窗口：BR-INV-08 默认 = login_logs 留存期（BR-ID-30 ⑥）；是否与 BR-ID-05 同设备注册上限的 30×24 小时口径统一，需负责人确认。
10. BR-INV-13 付款时间规则依赖各平台 paid_at 准确（待实测）；预售单以定金付款时间（deposit_paid_at）还是尾款时间作为取上级与等级的 paid_at，需在 09 订单归属验证中确认，默认用 deposit_paid_at（更早者），并须与 BR-CALC-12 的 paid_at 取法一致。
11. 04 §3.2 users.status 字段未定义取值；本主题封禁判定只用 risk_state，需账号主题定义 users.status 或删除该字段。
12. BR-INV-23（P1）开工前需定：有效新人实付金额门槛 member.valid_newcomer_min_paid_fen（财务）；有效新人是否另加「淘宝备案」「绑微信」条件（默认不加）；活跃窗口按 paid_at 还是 received_at 计（默认 paid_at，与 F-73「PAID 及以上状态」一致）。
13. 落地页接口与阈值已按 BR-ID-32 合并（BR-INV-05）：BR-ID-32 的 `POST /v1/landing/login` 与本主题 `POST /v1/invites/landing-register` 指同一接口，路径统一需在 13 与 BR-ID-32 中同步；consent channel 取 h5_landing。

---
