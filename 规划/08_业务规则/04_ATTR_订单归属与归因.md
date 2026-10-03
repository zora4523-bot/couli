# 08 业务规则 · 4. 订单归属与归因（BR-ATTR）

返回 [README](README.md)（使用规则、术语表、规则索引）

## 4. 订单归属与归因（BR-ATTR）

本节规定：订单归到 App 与用户（推广位白名单、relation_id/归因参数）、自购分享判定、时间窗口、来源回填、未归因池与找回、流水线黑名单、外跳路径与未安装降级、花卷云侧过滤与 AF-07 双向验证。共 29 条（已确认 6、默认假设 16、待决策 1、待验证 6）。

2026-10-01 晚负责人补充决定（docs/changes/20261001-拍板第二批.md §8）：ADD-01 用户淘宝授权一次绑定、永久有效，不提供用户自助换绑，绑定只在注销时释放、释放后冷却 30 天，C-05 结案（BR-ATTR-07 改为已确认；后台「重置授权」用于错绑纠正，保留，BR-ID-20）；ADD-02 站长联盟授权到期管理见 BR-ID-24，过期期间不影响已绑定用户的归属记录；ADD-08 过期或失效期间淘宝未绑定用户不能下单、不提供无返利购买，因此不产生可作找回证据的 no_rebate 记录，也没有找回（BR-ID-24、BR-ATTR-18）；ADD-05 已归属订单改归属与黑名单扣回确认由超管或被勾选该权限的账号一人 step-up 完成（BR-ATTR-20 改为已确认）；ADD-06 用户只有一个余额，buy_type 只决定流水类型（REBATE_CREDIT / SHARE_CREDIT），不再映射 SELF / PROMO 账户。本主题中 super 等后台角色名按 ADD-04 读作「超管，或被勾选该操作权限点的后台账号」。

订单状态一律按 BR-FUND-01 的双状态书写：`platform_status`（平台订单状态）+ `rebate_status`（返利状态）。与 规划/04 单一 order_status 的对应见 BR-FUND-01 细则「与单一 order_status 的映射」（例如 PAID ↔ (PAID, ESTIMATED)，INVALID ↔ (任意, VOID)）；本主题前稿引用的 04 §4.1 迁移编号对应为：O2 ↔ P2（付款，含预售付尾款），O11 ↔ R3（未归因订单找回通过 / 管理员变更）。按 C-01 默认处理，已由负责人确认 2026-09-30。

2026-10-03 实现方案调整（docs/changes/20261003-淘宝转链改客户端百川.md；00 §8 第 ① 类）：淘宝链接 API（万能转链按链接转换等）为邀请制、新 App 首版拿不到（09 CAP-TB-06、2_TB §2.5），淘宝改由客户端百川 SDK 按服务端下发的 pid + relation_id 完成淘客转链；京东、拼多多仍在服务端转链。改动只在 BR-ATTR-05（淘宝 open 下发客户端打开指令）与 BR-ATTR-27（淘宝路径矩阵）两处的「2026-10-03」说明；归因身份仍只由服务端构造，订单归属判定（推广位白名单 + relation_id）、自购分享判定、时间窗口、找回证据均不变，条目状态不变。

2026-10-01 用语同步（docs/adr/0001-技术栈基线.md §3，规划/11 §9.1；00 §8 第 ① 类）：BR-ATTR-01、BR-ATTR-20、BR-ATTR-22 及 BR-ATTR-22 细则的实现措辞改为中立说法（领域事件写作「与业务写入同一事务入队」，迁移不再点名具体库）；BR-ATTR-22 实现约定补 order_keys.attr_at（ADR-0001 §4.2）。规则含义、取值与状态均不变。

2026-10-03 功能对照补缺第 1 批（docs/changes/20261003-功能对照补缺.md；缺口编号写作「功能对照 G-xx」，待确认题写作「功能对照 Q-xx」，与 规划/10 §6.1 的 G-xx、规划/06 的 Q-xx 不是同一套编号）：新增 BR-ATTR-29「第三方页容器内的平台页面与商品链接」（G-02，待决策，按 Q-02 默认 A 写）；BR-ATTR-05 细则补「App 内打开链接的入口」（G-03，按 Q-03 默认 A 写，open 的归属规则不变）；BR-ATTR-08、BR-ATTR-11 细则各加一句指针。原有条目的状态与归属判定都不变。

### 4.1 规则一览

| 编号 | 规则 | 状态 | 影响面 |
| --- | --- | --- | --- |
| BR-ATTR-01 | **归因流水线顺序**<br>每条联盟子订单在同步 upsert 后（首次入库，或 content_hash 变化时）必须按固定顺序执行：① App 归属（BR-ATTR-02，含同步起点过滤；归因时点 attr_at 见 BR-ATTR-25）→ ② 用户归属（BR-ATTR-06/07，只在 user_id 为空时执行）→ ③ 黑名单（BR-ATTR-26）→ ④ buy_type（BR-ATTR-08）→ ⑤ 来源回填（只在本次同步把 user_id 由空写为非空时执行，见 BR-ATTR-15）→ ⑥ 分佣快照（见下）→ ⑦ 状态迁移（platform_status、rebate_status，按 BR-FUND-01）+ 领域事件入队（与状态迁移同一事务）。① 失败：不入库，只计数；② 失败：入库进入未归因池（BR-ATTR-16，rebate_status=UNATTRIBUTED），继续执行 ③④⑦，跳过 ⑤⑥。<br><br>⑥ 分佣快照（生成时点按 BR-CALC-10）：子订单首次同时满足「已归因到用户（user_id 非空）」与「platform_status ∈ {PAID, RECEIVED, SETTLED} 且 rebate_status ∉ {VOID, CLAWED_BACK}」（即单一 order_status 的 PAID/RECEIVED/CREDITED/SETTLED）时，在该次处理的同一事务内生成，只生成一次（commission_splits 以 order_id 唯一）。三种来源（同步归属、找回通过、管理员变更）规则相同。platform_status=DEPOSIT_PAID 时不生成、不计预估；预售单在付尾款（BR-FUND-01 P2）且已归因时生成。找回通过或管理员变更时 rebate_status 已为 VOID 或 CLAWED_BACK → 只写 user_id 与 user_basis，不生成快照。快照中本人等级、上级等级与直推上级取 paid_at 时刻的值（BR-CALC-12；预售单 paid_at 为付尾款时刻），分佣规则版本见 BR-CALC-11；因此入库、找回、改归属的时刻不影响快照结果。未归因订单不生成快照。已归属订单改归属时的快照处理见 BR-ATTR-20。<br><br>user_id 只在三个时点写入：首次归属成功、找回通过、管理员变更（BR-ATTR-20）。已有 user_id 的订单在后续同步中不重跑 ②，也不覆盖 pid、relation_id、sub_union_id、custom_params；新值与库内不同时，写 order_attr_param_changed 事件并发 P2 告警，其余字段照常更新。<br><br>并发：同一子订单的同步处理、找回通过、管理员变更都必须先取 pg_advisory_xact_lock(hash(platform, sub_order_id))，三者用同一把锁，拿到锁后重读订单再写。<br><br>乱序：平台订单更新时间（platform_modified_at）是否可靠、是否单调，由 09 逐平台核实，结果写入配置 attr.mtime_ordering.&lt;platform>（默认 false）。配置为 true 时：新数据的 platform_modified_at &lt; 库内值 → 丢弃，不改任何字段；两者相等且 content_hash 不同 → 照常处理；平台没有返回该字段 → 按 content_hash 处理，并累加 order_sync_no_mtime(platform, date)。配置为 false 时不丢弃，只看 content_hash 是否变化。两种配置下，状态迁移都要经过 BR-FUND-01 迁移表校验（platform_status P1–P10、rebate_status R1–R14（含 R3a、R3b、R5a、R9b））：平台状态倒退（例如 platform_status 由 SETTLED 回到 PAID）按 P10 不迁移、写待处理表并告警；迁移表外的事件一律拒绝。两种情况都记 order_illegal_transition 事件。 | 默认假设 | orders（platform_modified_at、attr_at、platform_status、rebate_status）；order_status_history（field=platform/rebate）；commission_splits（BR-CALC-10）；领域事件任务（同事务入队）；订单同步 worker（05 B1-08）；配置 attr.mtime_ordering.&lt;platform>；事件 order_attr_param_changed、order_illegal_transition；02 §7.3 归因流水线图；BR-FUND-01 P2、P10、R1–R3（原 04 §4.1 O2、O11）；验收用例：乱序、重复同步、未归因重跑、预售快照 |
| BR-ATTR-02 | **App 归属：推广位白名单**<br>一笔订单属于本 App，当且仅当它的推广位命中 union_pids 中 app_id=本 App 的记录，status 为 pending、active、retired 都算。匹配键：淘宝 (platform, union_account_id, site_id, adzone_id)；京东 (platform, union_account_id, positionId)；拼多多 (platform, union_account_id, pid)。淘宝订单 adzone_id 命中、但 site_id 不符时不入库，reason='SITE_MISMATCH'，并发 P1 告警。完全不命中的订单不入库，reason='PID_NOT_OURS'。命中、但 attr_at（BR-ATTR-25）早于 union_accounts.sync_start_at 的订单不入库，reason='BEFORE_SYNC_START'。sync_start_at 取本 App 在该联盟账号下第一个推广位的创建时刻，不取对外上线日。<br><br>丢弃计数：写 order_sync_drop_keys(platform, sub_order_id, reason)（留存见 BR-ID-30 ⑭），同一个键已经存在时不重复计数；第一次写入时，order_sync_drops(platform, date=attr_at 的 +08:00 日期, reason) 加 1。<br><br>推广位 status：pending（已登记、未转链，见 BR-ATTR-28）→ active（可以转链）→ retired（停止新转链，仍留在白名单里）。union_pids 不得物理删除。新增或修改白名单必须由 super 角色操作，做二次验证，并写审计。转链时，推广位必须按 app × platform × pid_scene 从 union_pids 读取 status=active 的记录，不得写死在代码里。 | 默认假设 | union_pids（status: pending/active/retired；淘宝 site_id）；union_accounts.sync_start_at；order_sync_drops、order_sync_drop_keys 表；后台 union-pids 页面（super + step-up）；订单同步 worker；审计日志；验收用例 AF-07 |
| BR-ATTR-03 | **双品牌隔离（原则）**<br>新 App 在淘宝、京东、拼多多各自使用独立的媒体和推广位，任何推广位都不得与优券汇共用；淘礼金推广位也不得与本 App 的其他推广位共用。<br><br>不得调用花卷云 dhcc.oauth.link.\*、dhcc.oauth.order.\* 为新 App 转链或拉单。用户、关系链、余额、积分不跨 App 共享；同一个人可以在两个 App 各注册一次；登录后 app_id 只能从 token 读取。<br><br>本条只管隔离原则（来自已确认决策 D1）。防止同一订单在两个 App 同时返利所依赖的花卷云侧过滤机制、pending → active 关卡与 AF-07 双向验证，依赖未实测的外部行为，拆到 BR-ATTR-28（待验证）维护。 | 已确认 | 所有业务表 app_id；union_pids（独立推广位）；后台推广位新增流程；花卷云侧过滤与放量前置条件见 BR-ATTR-28 |
| BR-ATTR-04 | **共用联盟账号可靠性**<br>MVP 默认新 App 与优券汇共用联盟推广者账号，只新建媒体和推广位。某个平台要对外放量（convert.enabled.&lt;platform>=true），必须先在 W1 真机验证通过该平台对应的条目：淘宝 06 Q-G1——同一淘宝买家在两个媒体备案后 relation_id 是否相同，订单里的 adzone_id 是否总能区分 App；拼多多 06 Q-G7——两个 App 授权后 custom_parameters 是否互相覆盖；京东 06 Q-G6——订单能否原样回传 subUnionId（含 n_ 前缀）。<br><br>判定标准：<br>- 淘宝 06 Q-G1：3 组订单中任意 1 笔 adzone_id 缺失或串位 → 不通过。<br>- 拼多多 06 Q-G7：两个 App 都授权后，3 组订单中任意 1 笔的 custom_parameters 不是下单 App 的值 → 不通过。<br>- 京东 06 Q-G6：按端分别验证（App 原生唤起、H5、scheme、鸿蒙），每端 3 笔。某个端出现任意 1 笔 subUnionId 缺失或被截断 → 该端不通过：该端改为不外跳，或提示用户换端，其他端照常放量。App 原生唤起不通过时，京东整体判为不通过。<br><br>整个平台验证不通过时，该平台改为新开联盟账号（由负责人拍板，代价是高级权限要重新申请）；改完之前该平台不对外放量，其他平台不受影响。 | 待验证 | 06 Q-A4、Q-G1、Q-G6、Q-G7；09 平台能力验证表；配置 convert.enabled.&lt;platform>；京东分端外跳降级配置（contracts/apps.json）；union_accounts |
| BR-ATTR-05 | **归因身份只由服务端注入**<br>UnionIdentity（推广位、relation_id、subUnionId、custom_parameters、sid）只能由 linking 模块根据 token 中的 user_id 和请求的 scene 构造。客户端、Agent 模型、外部入口传入的身份字段一律忽略，Adapter 不接受外部身份。每次转链或出卡都必须登记 link_id，并在 links.identity_snapshot 中固化 {user_id, platform, pid, pid_scene, 归因参数, agent_session_id}。<br><br>POST /v1/links/{link_id}/open 的处理规则：<br>① pid_scene=share 的链接，任何人（包括未登录用户）都可以打开，使用快照里分享者的身份。例外：当前登录用户等于 snapshot.user_id 时，按 BR-ATTR-11 处理（待决策，默认改走自购位）。<br>② 其他链接，快照 user_id 等于当前登录用户，或为空（游客 link）时按当前用户打开；为空时写 links.user_id=当前用户（只写一次），不校验 device_id。<br>③ 登录用户打开别人的非分享链接时，服务端用当前用户身份、按同一 scene 重新登记 link_id 并转链，不得使用原链接主人的身份。当前用户在该平台未授权时，返回 30101（淘宝）或 30111（拼多多）+ auth_url，state 绑定新登记的 link_id。原链接 pid_scene=taolijin 时，不为当前用户创建淘礼金，改按 scene=detail 走自购位重新转链，并提示“该淘礼金仅限原用户使用”。比较基准沿用原 link 的 quoted_final_price_fen（BR-PRICE-12），响应带 new_link_id。<br>④ 未登录用户打开非分享链接 → 返回 10001。<br>⑤ link_id 不存在或不属于本 App → 30144。<br>open 的归属校验只在本条维护；BR-AI-11、BR-PRICE-12 引用本条（G-08）。<br><br>转链结果与有效期：每次 open 都按 identity_snapshot 取转链结果。转链结果最多缓存 15 分钟，缓存键必须包含快照中的 user_id，禁止跨用户复用；缓存未命中时实时转链。<br><br>**2026-10-03 淘宝（实现方案，docs/changes/20261003-淘宝转链改客户端百川.md）**：platform=taobao 时 open 不调用服务端转链接口，改为下发客户端打开指令：服务端照上文 ①–⑤ 做归属校验与授权校验，按 identity_snapshot 构造 UnionIdentity（pid 按 pid_scene 取 active 推广位，relation_id 取快照 user_id 的 active 绑定），写入 jump 的百川步骤，由客户端百川 SDK 完成淘客转链（路径与降级见 BR-ATTR-27 淘宝行）。客户端只原样执行指令，不得替换或补填 pid、relation_id；本条「转链结果」「转链缓存」对淘宝指已下发的打开指令（缓存键、≤15 分钟、按 user_id 隔离不变）。open 照常写 link_log（event=open，result_code=0 表示指令已下发），点击证据口径不变；SDK 是否拉起成功只看 link_jump 上报。京东、拼多多不变。links.expire_at 只表示本次返回给客户端的联盟 URL 可以直接使用的期限：自购和 Agent 链接为登记后 15 分钟；分享链接为登记后 7 天，对应分享文案里的口令或短链（联盟口令、短链的实际有效期待 09 核实）。expire_at 不限制 link_id 被 open：过了 expire_at 仍然可以 open，沿用同一个 link_id，不续期、不新登记，按快照实时转链，link_log 记 expired=true。<br><br>按快照转链前，先校验快照 user_id 的授权：淘宝需要 active 绑定，拼多多需要备案有效，京东不校验。分享链接校验不通过时，返回 30102（淘宝）或 30111（拼多多），H5 中间页统一显示“分享链接已失效，请联系分享者重新分享”。<br><br>淘宝授权回跳用的 state 绑定待继续的 link_id，有效期 10 分钟；回跳时必须校验 link_id 属于当前用户。 | 默认假设 | links.identity_snapshot、expire_at 语义；POST /v1/links/convert；POST /v1/links/{link_id}/open（分享链接可匿名打开）；Agent register_links；转链缓存 Redis 键；错误码 10001、30101、30102、30111、30144；open 响应 new_link_id；links.user_id（游客 link 首次登录回写）；BR-AI-11、BR-PRICE-12（引用本条）；H5 分享中间页失效态；验收用例：跨用户打开链接、分享链接过期后打开 |
| BR-ATTR-06 | **用户归属参数格式**<br>每个用户注册时生成 attr_code：8 位 [0-9a-z] 随机串，在本 App 内唯一（建唯一索引），生成后不再改变。联盟参数里只放 attr_code，不放 user_id。<br><br>转链时，归因参数按以下格式注入：<br>- 淘宝：relation_id 取该用户在本 App + 该联盟账号下 status=active 的绑定。没有绑定时返回 30101 + auth_url，绑定已失效时返回 30102；不得不带 relation_id 转链。例外：open 请求 no_rebate=true（BR-ID-18）时不带 relation_id，也不做绑定校验（用 self_buy 位，BR-ATTR-08）。special_id 在 MVP 只存储、不使用。<br>- 京东：subUnionId = "n_{attr_code}"；attr.click_code.jd=true 时为 "n_{attr_code}_{lk}"（BR-ATTR-15）。no_rebate=true 时不带 subUnionId。用户键方式由开关 attr.jd.user_key_mode ∈ {sub_union_id, private_position, claim_only} 决定，默认 sub_union_id；另两种为 CAP-JD-05 不通过时的降级，见下方“京东降级”。<br>- 拼多多：custom_parameters = {"app":"n","uid":"&lt;attr_code>","sc":"&lt;pid_scene>","lk"?:"&lt;lk>"}，lk 只在 attr.click_code.pdd=true 时出现（BR-ATTR-15）。首次转链前必须完成授权备案，否则返回 30111。no_rebate=true 时不带 custom_parameters.uid 与 lk，也不做备案校验（不带 uid 能否转链待 CAP-PDD-06 核实）。<br><br>京东降级（attr.jd.user_key_mode，由负责人按 CAP-JD-05 结论切换）：<br>- private_position：subUnionId 未获批时，用私域推广位（position.create unionType=3）给每个用户分配 1 个 positionId 作用户键，映射存 user_union_positions(app_id, user_id, platform, union_account_id, position_id, created_at)，唯一 (app_id, platform, position_id) 与 (app_id, user_id, platform)。首次京东转链时分配。私域推广位视同 pid_scene=self_buy、status=active 计入 BR-ATTR-02 京东白名单（匹配键 (platform, union_account_id, positionId) 同时查 union_pids 与 user_union_positions），buy_type 按 BR-ATTR-08 ① 判 self（scene_basis=pid）；该模式下 BR-ATTR-15 ② ③ 不按 pid_scene 过滤（同 fallback 位）；京东分享（scene=share）不可用，京东分享入口隐藏（待负责人确认）。上限每联盟账号 5000 个（来源 09 CAP-JD-05，共用账号时含优券汇已占用数，待实测）。用户键解析：订单 positionId 反查 user_union_positions 得 user_id，不看 subUnionId。已分配数达到上限后，新用户不再分配，这些用户的京东转链改走 claim_required：用 self_buy 位、不带用户键，订单进未归因池，只能经订单找回（BR-ATTR-17）认领，京东商品卡与订单页显示 BR-TEXT-14 claim_required 文案。<br>- claim_only：私域推广位也不可用时，全部京东用户按上述 claim_required 处理，订单只做 App 归属（positionId）。<br>- 京东转链接口（拍板第二批 TRADE-11）：默认 common.get（APP 媒体 + siteId；投放应用须与 siteId 备案一致，否则订单判无效，09 CAP-JD-05）；W1 对 common.get 与 bysubunionid.get（社交媒体）都实测，按 subUnionId 在哪个接口可用（转链可传、订单原样回传）定最终接口，结论写入 09 CAP-JD-05。<br><br>订单入库时的解析规则：<br>- 京东（user_key_mode=sub_union_id）：subUnionId 必须匹配 ^n_([0-9a-z]{8})(?:_([0-9a-z]{1,16}))?$，第二个捕获组是 BR-ATTR-15 的 lk。private_position 模式按上方“京东降级”用 positionId 反查。<br>- 拼多多：custom_parameters 必须能解析为 JSON 对象，app=="n"，uid 是 8 位 [0-9a-z] 字符串；uid 为 JSON number 类型时按解析失败处理；lk 字段可缺省，存在时作为 BR-ATTR-15 的 lk。<br>- 按 attr_code 能反查到本 App 已存在的用户，才算解析成功。<br><br>解析失败或反查不到时，订单进入未归因池，并累加 attr_param_invalid(platform, date)，这个计数只统计京东和拼多多。淘宝 relation_id 为空或找不到绑定时，累加 attr_binding_miss(platform, date)。美团 sid 格式见 4.3 第 4 条。 | 待验证 | users.attr_code（唯一索引）；UnionIdentity 构造（linking 模块，含 no_rebate 例外）；orders.relation_id / sub_union_id / custom_params；union_bindings；user_union_positions（新增，京东降级）；配置 attr.jd.user_key_mode、attr.click_code.&lt;platform>；错误码 30101、30102、30111；订单同步解析；计数 attr_param_invalid、attr_binding_miss；京东转链接口按 CAP-JD-05 实测定（拍板第二批 TRADE-11） |
| BR-ATTR-07 | **淘宝按付款时点绑定归属**<br>淘宝订单的 user_id，取 union_bindings 中同时满足以下条件的那条绑定的 user_id：app_id=本 App；union_account_id=订单所属联盟账号；relation_id=订单上的 relation_id；bound_at ≤ attr_at（BR-ATTR-25）；归属截止时刻 attr_end_at 为空，或 attr_at &lt; attr_end_at。attr_end_at = COALESCE(cooldown_until, released_at)：释放的绑定（注销释放、后台重置授权，BR-ID-20）在释放时写入 cooldown_until = released_at + bind.rebind_cooldown_days（BR-ID-19）；active、invalid、blocked 绑定两者都为空，区间不封闭。所有有 bound_at 的绑定都按这个区间参与判定，不看当前 status，包括已 released 的，这样同步晚到的历史订单也能归属。<br><br>命中多条：user_id 相同时，归属该用户；user_id 不同时，不归属，订单进未归因池，写 attr_binding_conflict 事件并发 P1 告警。找不到绑定：进未归因池，并累加 attr_binding_miss。订单上的 relation_id 原样存入 orders.relation_id；重新授权或绑定释放之后，历史订单不改归属。<br><br>用户淘宝授权一次绑定、永久有效，不提供用户自助换绑，绑定只在注销时释放（拍板第二批 §8 ADD-01）；唯一性、释放后冷却与恢复见 BR-ID-19；冷却天数 bind.rebind_cooldown_days 须 ≥ attr.click_window_days.taobao（BR-ATTR-13；该值核实前下限暂取 30 天），保证释放前点击、冷却期内付款的订单仍落在原绑定区间内。 | 已确认 | union_bindings（bound_at、released_at、cooldown_until）；绑定状态机与错误码 30151（BR-ID-19；30152 随取消换绑废弃）；orders.relation_id；订单同步用户归属步骤；事件 attr_binding_conflict、计数 attr_binding_miss；资损对账：订单归因键与付款时点有效绑定 |
| BR-ATTR-08 | **自购与分享判定**<br>转链请求的 scene 必填；scene 缺失或不在枚举内时，返回 20001，不转链。服务端由 scene 推出 pid_scene：search/detail/home_card/feed/clipboard/h5/push → self_buy；agent → agent；share → share；taolijin → taolijin。fallback（兜底）推广位不用于转链，只作白名单保留位：申请后登记进 union_pids，万一有订单落在兜底位上，按下方 ② ③ 判定 buy_type（拍板第二批 TRADE-19）。no_rebate 购买（BR-ID-18）用 self_buy 位、不带用户参数，也不做绑定或备案校验（BR-ATTR-06 的例外）。<br><br>订单的 buy_type 按以下优先级判定：<br>① 订单推广位在 union_pids 中的 pid_scene 不是 fallback 时，直接取这个值（scene_basis=pid）。<br>② 推广位 pid_scene=fallback 时，读取订单参数中的场景（拼多多 custom_parameters.sc），取值在 {self_buy, agent, share, taolijin} 内时采用（scene_basis=param）。<br>③ 以上都取不到时（包括 sc 缺失、取值非法、sc=fallback），buy_type=self，scene_basis=fallback。<br><br>映射到流水类型（都入订单 user_id 的单一余额 USER_BALANCE，BR-FUND-13，拍板第二批 §8 ADD-06）：share → buy_type=share → SHARE_CREDIT；self_buy/agent/fallback → buy_type=self → REBATE_CREDIT；taolijin → buy_type=self，但默认不生成用户返利分录（快照中用户份额为 0）。淘礼金订单是否叠加返利由负责人按 BR-TLJ 决定，决定之前不入账。<br><br>预留的 scene（与 13 §13.2 一致）：watch_alert 为 MVP 预埋（开关关闭、不对用户展示，BR-WATCH-19，待确认），share_ext、wechat_bot、mcp 为 P1；share_ext、watch_alert、wechat_bot → self_buy；mcp → agent。提醒细分类型 digest、new_arrival、promo_reminder、replenish 不扩 scene：转链时 scene=watch_alert，细分类型记在 sub_scene 或 watch.type（字段由 BR-WATCH 定）。 | 默认假设 | orders.buy_type、scene_basis；union_pids.pid_scene；POST /v1/links/convert scene 枚举与 20001；流水类型 REBATE_CREDIT / SHARE_CREDIT（单一余额 USER_BALANCE）；分佣快照（淘礼金用户份额）；验收 F-ORD-04 |
| BR-ATTR-09 | **归因依据字段拆分**<br>orders.attribution_basis 必须拆成两个字段。scene_basis ∈ {pid, param, fallback}，表示 buy_type 的判定依据。user_basis ∈ {param, claim, admin}，表示 user_id 的来源：param=联盟参数自动归属，claim=找回，admin=后台变更（包括改派已归属订单）；未归因订单的 user_basis 为 NULL。两个字段互不覆盖：找回通过时只写 user_basis=claim，scene_basis 保持不变。 | 默认假设 | orders 表结构；订单详情接口；后台订单列表筛选；报表：兜底判定占比、找回占比 |
| BR-ATTR-10 | **转链者、分享者与购买者**<br>一笔联盟订单只携带一个归因身份：生成这条链接的会员（转链者）。分享链接的转链者就是分享者，购买者的身份不会进入联盟订单。因此分享单的判定是：user_id=分享者，buy_type=share，佣金记入分享者余额（SHARE_CREDIT）；上级分佣按分享者的关系链计算（见 BR-INV）。购买者无论是否本 App 用户，都不能从这笔订单获得返利、积分或首单奖励。<br><br>分享者必须已完成该平台授权，才能生成分享链接（淘宝需要 active 绑定，拼多多需要完成备案），否则返回 30101/30111；分享链接被打开时还会再校验一次（BR-ATTR-05）。<br><br>分享者看到的订单信息只有商品（标题、商品图）、实付金额、件数、状态、脱敏订单号（与订单列表字段一致，按付款时间倒序，拍板第二批 TRADE-06），不得包含购买者的手机号、昵称、收货信息。分享中间页不显示“购买者可得返利”，也不提供把链接换成购买者本人链接的入口。 | 默认假设 | 分享中间页（H5 share-landing）；订单列表（分享单视图）；F-SHARE-05 脱敏；POST /v1/links/convert scene=share；客服话术：好友下单我能拿返利吗 |
| BR-ATTR-11 | **分享者通过自己链接下单**<br>本条优先于 BR-ATTR-05 ①。<br><br>分享者在已登录的 App 内打开自己的分享链接时（open 请求中当前 user_id 等于 snapshot.user_id，且 pid_scene=share），服务端为当前用户新登记一个 link_id（scene=detail，pid_scene=self_buy，identity_snapshot 取当前用户），用新 link_id 走自购位转链，并写 open 日志（link_id=新 id，user_id=opener_user_id=当前用户）；原分享 link_id 不变。订单按自购计（REBATE_CREDIT），不产生推广收益。当前用户淘宝没有 active 绑定时，返回 30101 + auth_url，state 绑定新 link_id；拼多多未备案时返回 30111。<br><br>在 App 外（例如微信中间页）打开时无法识别身份，按分享单处理。事后识别推广自买时，只使用联盟订单接口实际返回、并且已在隐私政策中说明用途的字段做比对，不另外收集购买者信息。可用字段在 09 中逐平台核实；核实之前，App 外的自买不做自动作废，只进人工复核（见 BR-RISK）。 | 已确认 | POST /v1/links/{link_id}/open；links（新登记 link_id）；风控规则（BR-RISK）与人工复核队列；隐私政策；等级晋升统计；验收 F-ORD-04 |
| BR-ATTR-12 | **多次点击、多入口、他人链接**<br>订单的 user_id 和 buy_type 只以联盟回传订单上的推广位和归因参数为准；最终由哪条链接计佣，由联盟按它自己的规则决定。本系统不得根据 link_log、点击先后或用户申诉，改写已归属订单的 user_id 或 buy_type（唯一例外是管理员变更，见 BR-ATTR-20）。<br><br>典型情形的处理：<br>① 同一用户多次点击自己的链接（入口不同）→ buy_type 按回传的推广位判定，source_scene 按 BR-ATTR-15 回填。<br>② 用户先点自己的链接，后点本 App 另一会员的分享链接再下单 → 如果回传的是分享者的参数，订单归分享者，是 share 单；用户提交找回时返回 30204。<br>③ 点了其他推广者或其他 App（包括优券汇）的链接 → 订单不在本 App 推广位上，不入库；找回返回 30201，诊断提示 NOT_TRACKED。<br>④ 用了其他推广者的淘礼金 → 同 ③，诊断提示 OTHER_TLJ。<br>⑤ 从本 App 跳转后，在平台内经 AI 助手引导下单 → 归因是否保留，待 06 Q-G4 核实。 | 默认假设 | 订单同步归属逻辑；找回错误码 30201/30204；JumpTip 文案；客服话术；explain_order（Agent 解释订单） |
| BR-ATTR-13 | **四个时间窗口**<br>以下四个窗口相互独立，不得混用。<br>① 点击有效期 W_click：由联盟决定，本系统不计算，也不据此改动订单。配置项 attr.click_window_days.&lt;platform> 三家均待核实（CAP-TB-05、CAP-JD-05、CAP-PDD-05 与 06 Q-G13；09 U-17），默认值为空（未配置）；核实后只用于 JumpTip 天数句（受 BR-TEXT-12 的 jump_tip.&lt;platform>.claims_enabled 控制）、找回驳回原因，以及 BR-ATTR-07 冷却期的下限。核实前：文案不写具体天数，不用于找回驳回原因，冷却期下限暂取 30 天。<br>② 链接 URL 有效期 W_link（links.expire_at，见 BR-ATTR-05）：返回给客户端的联盟 URL 可以直接使用的期限。自购和 Agent 链接 15 分钟；分享链接 7 天。过期后 link_id 仍然可以 open，按快照实时转链，不新登记、不续期；快照主人的授权已失效时，按 BR-ATTR-05 返回“分享链接已失效”。<br>③ 来源回填窗口 W_backfill：link_log.created_at ∈ [attr_at − 360 小时, attr_at]，两端都是闭区间，配置 attr.backfill_window_hours=360（360 小时是按未核实的“点击有效期 15 天”取的暂定值，待 CAP-*-05 点击有效期结果回写后调整）。<br>④ 找回窗口 W_claim：提交时刻 now ≤ attr_at + 720 小时，只在提交时校验，审核不受这个时限约束。<br><br>所有窗口一律按绝对时长计算，不按自然日；只有“每日次数”类统计按 +08:00 自然日计算。attr_at 见 BR-ATTR-25。 | 默认假设 | 配置 attr.click_window_days.&lt;platform>、attr.backfill_window_hours、claim.window_hours；links.expire_at；JumpTip 文案；POST /v1/links/{link_id}/open；找回校验 |
| BR-ATTR-14 | **link_log 记录与保留**<br>link_logs 的 event 取值为 {convert, precompute, register, open}：<br>- convert：只记用户主动发起的 POST /v1/links/convert（生成分享、按 url 转链），成功、失败都记；点“去购买”走 open，记 open。<br>- precompute：保留取值，不再产生（出卡不预转链，BR-PRICE-12，拍板第二批 TRADE-03）。<br>- register：记 Agent 或提醒出卡时登记 link_id。<br>- open：每次 POST /v1/links/{link_id}/open 都记一条，无论是否命中缓存（cache_hit）、是否已过 expire_at（expired）。<br><br>字段：event、link_id、user_id（归因身份的主人；分享链接被打开时记分享者）、opener_user_id（可空）、client ∈ {ios, android, harmony, h5, web}（服务端根据签名头或 UA 写入）、platform、product_key、raw_item_id、shop_id、scene、pid_scene、spm、pid、relation_id / sub_union_id / custom_params、agent_session_id、agent_message_id、prompt_version、model、quoted_price_fen、cache_hit、expired、result_code、latency_ms、created_at。<br><br>只有 event∈{convert, open} 且 result_code=0 的记录才算点击证据；precompute 和 register 只用于统计和 Agent 追踪。<br><br>保留：表按日分区，按分区删除；被 claim、联盟维权、对账差错单引用的 link_log，在其分区删除前复制到 link_log_evidence 表。两者的留存期见 BR-ID-30 ②（link_logs 留存期不得短于 W_claim + W_backfill，BR-ATTR-13）。 | 默认假设 | link_logs 表结构与分区；link_log_evidence 表；跟单率统计；找回证据计算；Agent 成交归因报表 |
| BR-ATTR-15 | **来源回填**<br>来源回填在订单 user_id 被写入或改写时执行：同步首次归属成功、找回通过、管理员变更（包括改派已归属的订单）。回填按当时的 user_id 重新匹配，覆盖 source_scene、link_id、agent_session_id、source_match 这四个字段；改写的情况下，覆盖前的旧值写入审计。订单已经有 source_match（包括 none）之后，同步更新不再重跑回填。回填不得影响 user_id、buy_type 和任何金额。<br><br>匹配按以下顺序，命中即停：<br>① exact：订单参数中带有 link 短码 lk（京东 subUnionId 后缀、拼多多 custom_parameters.lk、美团 sid），且该 link 属于订单的 user_id → 直接取这个 link。<br>② product：在 link_logs 中找满足以下全部条件的记录：user_id=订单 user_id；platform 相同；product_key 相同；event∈{convert, open}；result_code=0；pid_scene=订单推广位的 pid_scene（订单推广位是 fallback 时不限）；created_at 在 W_backfill 内（以 attr_at 为基准）。取 created_at 最大的一条，相同时取 id 最大的。<br>③ shop：条件同 ②，只是把“product_key 相同”换成“shop_id 相同”。<br>④ none：以上都没有 → 三个来源字段置空，source_match=none。<br><br>lk（link 短码）定义：links 表单独发号的 base36 短码，默认 6 位 [0-9a-z]（36⁶≈21.8 亿），随机生成，冲突重试（最多 3 次，仍冲突报警），存 links.lk（可空），唯一索引 (app_id, lk)（按“业务唯一键以 app_id 开头”约定；exact 匹配另要求 link 属于订单 user_id）。lk 与 link_id、attr_code 无推导关系。只在该平台开关 attr.click_code.&lt;platform>=true 时，于登记 link（convert、register、BR-ATTR-05 ③ 与 BR-ATTR-11 的新登记）时生成并注入联盟参数；开关默认 false，CAP-JD-05、CAP-PDD-05 验证长度与字符集通过后由负责人打开；未打开的平台 links.lk 为空，直接从 ② 开始匹配。no_rebate 购买（BR-ID-18）不下发 lk。 | 默认假设 | orders.source_scene、link_id、agent_session_id、source_match；links.lk（新增，唯一索引 (app_id, lk)）；配置 attr.click_code.&lt;platform>；link_logs 索引 (user_id, platform, product_key, created_at)；审计日志（改派时的来源旧值）；Agent 成交归因报表；跟单成功率统计 |
| BR-ATTR-16 | **未归因池**<br>未归因池里的订单，是通过了 App 归属、但用户归属失败的子订单。入库时 user_id=NULL、user_basis=NULL、locked=false，rebate_status=UNATTRIBUTED（BR-FUND-01 R1）。这类订单的 platform_status 照常迁移（PAID/RECEIVED/SETTLED/INVALID 等；平台失效时 rebate_status 按 R6 置 VOID），但不生成分佣快照，不产生任何用户侧分录。<br><br>每次同步更新都要重跑用户归属（BR-ATTR-01 ②）。归属成功后：写 user_basis=param；rebate_status 由 UNATTRIBUTED 迁到 ESTIMATED（platform_status 已为 RECEIVED/SETTLED 时直接到 WAITING，settle_period 按原 received_at 取，BR-FUND-04 ②），迁移结果与 BR-FUND-01 R3 相同，但事件为同步归属、不置 locked（BR-FUND-01 R3a）；执行来源回填，并按 BR-ATTR-01 ⑥ 的条件生成快照；然后处理该子订单所有未决的找回子项（claim_items 中 decision 为空的）：<br>- 归属到的 user_id 等于申请人 → 子项置为 cancelled，通知申请人“订单已自动跟单”；<br>- 不等于申请人 → 子项置为 rejected（NOT_IN_POOL），通知“该订单已由平台记录归属，找回已关闭”，不透露对方信息。<br>claim 的整体状态按 BR-ATTR-18 由各子项汇总；claim 中还有未决子项时，继续审核。<br><br>未归因订单只能通过找回（提交时 now ≤ attr_at + 720 小时）或管理员变更认领；管理员变更不受找回窗口限制。超过找回窗口仍未认领的订单：rebate_status 保持 UNATTRIBUTED，不生成快照，不入任何用户账户；其佣金的会计处理（是否及何时确认为平台收入）BR-FUND 尚未定义，待财务决策，默认联盟回款核销时整笔计平台留存（4.3 第 3 条）。<br><br>监控：未归因率 = 当日（+08:00，按 orders.created_at）首次入库时 user_id 为 NULL 的订单数 ÷ 当日首次入库的本 App 订单数，按平台统计。每小时计算一次，统计范围为当日 00:00 到计算时刻；分母 ≥20 且比率 >5%（attr.unattributed_rate_alert_bp=500）时告警，同一平台每天最多告警 1 次。 | 已确认 | orders（user_id 可空、user_basis、rebate_status=UNATTRIBUTED）；claim_items（decision 增加 cancelled）；后台未归因订单列表；告警配置 attr.unattributed_rate_alert_bp；站内消息与推送模板；对账（BR-FUND） |
| BR-ATTR-17 | **找回受理与即时校验**<br>入口：订单页常驻“未跟单？去找回”。当用户最近一次外跳距今 ≥30 分钟且 ≤72 小时，并且在那之后没有新订单归属到该用户时，这个入口置顶显示。“外跳”指本人发起、event∈{convert, open}、result_code=0、pid_scene≠share 的 link_log；其中无返利购买（no_rebate=true，BR-ID-18）只有 no_rebate_reason ∈ {auth_declined, auth_failed} 且用户此后已完成该平台授权时才计入置顶条件（拍板第二批 TRADE-09）。<br><br>表单为 H5，接口 POST /v1/orders/claims，入参：platform；order_no（去掉空格后按字符串精确匹配）；paid_date（YYYY-MM-DD，+08:00，作为第二因子；预售单填付定金日期，即 attr_at 的日期）；可选的诊断包。<br><br>同一用户的找回提交按 (app_id, user_id) 加 advisory 锁串行执行，各项计数都在锁内读取。<br><br>校验按以下顺序执行，遇到第一个失败即返回：<br>⓪ 紧急开关 claims.enabled=off → 30206（找回功能暂时关闭；客户端找回入口置灰），不计入当日失败次数。<br>① 当日已被风控禁止 → 30203，data.reason=RISK_BLOCKED。<br>② 当日已创建的找回 ≥5 条 → 30203。<br>③ 匹配订单，限定 orders.app_id = token.app_id：order_no 先匹配 sub_order_id，匹配不到再匹配 parent_order_id（取该父单下的全部子订单）；都匹配不到 → 30201。<br>④ 对匹配到的每个子订单依次校验：<br>a. 付款日期：attr_at 按 +08:00 取日期后不等于 paid_date → 30202，reason=FACTOR_MISMATCH；<br>b. 找回窗口：now > attr_at + 720 小时 → 30202，reason=CLAIM_EXPIRED；<br>c. 订单 rebate_status=VOID（单一 order_status 的 INVALID）→ 30202，reason=ORDER_INVALID；<br>d. 去重：申请人在 claim_items 中已有该 sub_order_id 的记录（任何状态）→ 30205；<br>e. 已有 user_id：属于本人 → 30202，reason=ALREADY_YOURS；属于他人 → 30204，不透露对方信息；<br>f. locked=true → 30204。<br><br>通过全部检查的子订单纳入同一个 claim（写 claim_items），claim 状态为 submitted，随后立即计算证据（BR-ATTR-18）。一个子订单都没通过时，按 sub_order_id 升序，返回第一个子订单的错误码。③④ 的失败计入当日失败次数（BR-ATTR-19）。唯一约束：claim_items(app_id, applicant_user_id, sub_order_id)。 | 默认假设 | POST /v1/orders/claims；claims 表（paid_date、order_no_type）与新表 claim_items；配置 claims.enabled；错误码 30201–30206 及 30202 data.reason 枚举；H5 找回页（含预售日期提示）；订单页入口显示条件；客服话术 |
| BR-ATTR-18 | **找回证据与审核**<br>证据等级按每个子订单（claim_items）、针对申请人本人计算。时间窗为 W_backfill：[attr_at − 360 小时, attr_at]；只看 event∈{convert, open} 且 result_code=0 的 link_log。<br>- strong：同平台、product_key 相同的记录。<br>- weak：没有 strong，但有同平台、shop_id 相同的记录，或同平台的其他记录。<br>- none：以上都没有。<br><br>无返利购买（BR-ID-18，link_logs.no_rebate=true）的记录，只有同时满足以下条件才计入申请人的证据（拍板第二批 TRADE-09）：no_rebate_reason ∈ {auth_declined, auth_failed}；计算证据时申请人在该平台已完成授权（淘宝绑定 active，拼多多备案有效）；attr_at 时该用户在该平台没有未解决的 30151 冲突日志，绑定也不是 blocked。relation_conflict、binding_blocked 的记录永不计入。不满足时该记录按不存在处理；满足时与普通记录一样按 strong / weak 判定。<br><br>claim 的状态按子项中最弱的证据确定：全部为 strong → auto_matched；否则 → manual_review。MVP 阶段所有 claim 都必须由客服确认：auto_matched 在后台置顶，展示命中的 link_log，并提供“一键通过”。<br><br>审核以子订单为单位进行，claim_items 记录 (claim_id, sub_order_id, evidence, decision, reject_reason)，客服可以逐个通过或驳回。claim.status 在全部子项已决后汇总：至少 1 个 approved → approved；否则至少 1 个 rejected → rejected；否则 → cancelled。<br><br>驳回原因码：<br>- 客服可选：NO_EVIDENCE、EXPIRED_CLICK（申请人只有 >360 小时前的同商品记录）、NOT_TRACKED、OTHER_TLJ、FRAUD、OTHER。<br>- 系统专用，客服不可选：NOT_IN_POOL（子订单已被其他 claim 通过、被管理员变更，或被同步自动归属给他人）；ORDER_INVALID（审核时订单 rebate_status 已为 VOID，系统自动驳回）。<br><br>审核通过按 BR-ATTR-20 加锁执行：同一子订单有多个待审子项时，先提交的通过，其余自动 rejected（NOT_IN_POOL）。<br><br>开关 claim.auto_approve_strong 默认 false；P1 开启后，strong 子项直接 approved；开启前必须先评估同商品证据的冒领率。审核结果通过站内消息 + 推送通知申请人。 | 默认假设 | claims.status、claim_items.evidence/decision/reject_reason；后台找回审核页（按子订单审核、证据展示、一键通过、驳回原因码）；配置 claim.auto_approve_strong；站内消息与推送模板；客服话术 |
| BR-ATTR-19 | **找回限流与风控**<br>按用户、按 +08:00 自然日计数，00:00 清零；计数在 BR-ATTR-17 的用户级 advisory 锁内读写。当日已创建的 claim（进入 submitted 的）上限 5 条，第 6 次提交返回 30203。当日即时失败（BR-ATTR-17 ③④ 的失败，包括 30201、30202、30204、30205）次数 ≥10 时，记风控事件 claim_fail_burst，当日剩余时间内的找回请求一律返回 30203，data.reason=RISK_BLOCKED。通过找回获得的订单，不计入首单奖励和新人任务（见 BR-REWARD）。 | 默认假设 | Redis 计数键 claim:{app_id}:{user_id}:{yyyymmdd}；风控事件表；错误码 30203；首单奖励判定（BR-REWARD） |
| BR-ATTR-20 | **找回通过、改归属与锁定**<br>找回子项通过，或管理员变更（后台 orders/{id}/reassign），都必须在同一个事务中完成，步骤如下：<br>① 事务开始先取 pg_advisory_xact_lock(hash(platform, sub_order_id))（与 BR-ATTR-01 同一把锁），再用 SELECT … FOR UPDATE 重读订单。<br>② 复查：找回通过时，如果重读到 user_id 非空，则不写订单、不生成快照，子项按 BR-ATTR-16 处理（等于申请人 → cancelled，否则 → rejected NOT_IN_POOL），并提示客服“订单已被自动归属”。管理员变更时，请求必须携带 expected_user_id、expected_locked；重读值与之不一致 → 返回 20902（状态已变化，请刷新后重试；data.resource=order_attribution），不做任何修改。<br>③ 复查通过后：写 user_id；写 user_basis=claim/admin；locked=true；platform_status 不变；订单原来没有 user_id 时，rebate_status 按 BR-FUND-01 R3 由 UNATTRIBUTED 迁到 ESTIMATED（platform_status 已为 RECEIVED/SETTLED 时直接到 WAITING，settle_period 按原 received_at 取（BR-FUND-04 ②）；已为 VOID 时不变（BR-FUND-01 R3b）），并按 BR-ATTR-01 ⑥ 的条件生成分佣快照；order_status_history 记 field=rebate、source=claim/admin；审计记录原会员、新会员、操作人、原因（必填，≥5 字）；在本事务内入队领域事件 claim.resolved 或 order.reassigned；执行来源回填（BR-ATTR-15）。<br><br>权限：<br>- 未归因订单的管理员变更：运营管理员经二次验证即可操作。<br>- 已归属订单改归属（前稿 O12，无论是否锁定）：由超管或被勾选改归属权限的账号经二次验证发起并确认，一人可完成，写审计（拍板第二批 §8 ADD-05）；确认后才执行上述事务。platform_status、rebate_status 都不变。<br><br>红冲：原快照产生的全部分录（原会员的返利或推广收益、上级分佣、平台留存）按 BR-FUND 全部红冲。同一事务内先红冲，再按新 user_id 生成新快照（等级与上级仍取 paid_at 时刻，BR-CALC-12）和分录；不得在红冲之前给新会员记账。红冲与重记必须作为该子订单 rebate_status 的自迁移执行（BR-FUND-01 要求订单相关分录只随 rebate_status 迁移变更；按 BR-FUND-01 R14）。原会员余额不足时允许出现负余额，按 BR-FUND 的负余额规则追扣或核销。<br><br>锁定之后：用户找回一律返回 30204；只能走上述后台改归属纠错通道。订单已 SETTLED、且原会员相关金额已被提现的，同样只能走这个通道。 | 已确认 | orders.locked、user_basis；BR-FUND-01 rebate_status R3（原 04 §4.1 O11）；已归属订单改归属的 rebate_status 自迁移（前稿 O12，BR-FUND-01 R14）；后台 orders/{id}/reassign（权限点、step-up、expected_user_id/expected_locked）；错误码 20902（data.resource=order_attribution）；审计日志；账务红冲与负余额（BR-FUND）；领域事件 |
| BR-ATTR-21 | **丢单原因码与防呆提示**<br>NOT_TRACKED、EXPIRED_CLICK、OTHER_TLJ 这三个原因码，只能用于找回驳回、explain_order 和诊断展示，不得写入 orders.reason，因为对应的订单不在本 App 推广位上，根本不会入库。RELATION_INVALID 同样不写入 orders.reason（BR-ATTR-07 规定 invalid 绑定仍计入归属，订单不会因此丢失），只用于转链时返回 30102 和授权状态提示。<br><br>JumpTip：每个用户、每个平台首次外跳前展示一次，按 user_id + platform 在服务端记录已读；之后用户可以在设置中重新打开。文案后台可配（key jump_tip.&lt;platform>），包含：在打开的页面直接下单；不要加购后隔天再买；中途不要点其他返利链接，也不要领他人的淘礼金；有效期按 BR-ATTR-13 配置。外跳返回 App 后展示“待跟单”卡。卡片按该次外跳的 link_id 展示，规则如下：<br>① 计算在服务端：外跳时刻 jumped_at 取该 link 本人发起的“外跳”link_log（口径同 BR-ATTR-17：event∈{convert, open}、result_code=0、pid_scene≠share）中最近一条的 created_at；是否显示、是否出找回入口都由服务端按服务端当前时刻计算后下发，客户端不用本机时钟计算。接口：GET /v1/orders/pending-tracks 返回 [{link_id, platform, jumped_at, show_claim_entry, dismissed}]；POST /v1/orders/pending-tracks/{link_id}/dismiss 记录用户手动关闭（写 links.track_dismissed_at，幂等）。<br>② 每个平台只显示最近 1 次外跳的卡（按 jumped_at 取最大，相同取 link_id 最大）；同一用户最多同时 N 张卡，N=已外跳的平台数。<br>③ 消失条件（任一满足，只以本条为准）：该 link 回填到的订单归属到当前用户（orders.link_id=该 link 且 user_id=当前用户，BR-ATTR-15，source_match≠none）；自 jumped_at 起超过 72 小时；用户手动关闭（dismissed=true，客户端不展示）。其他订单归属到该用户不使卡片消失。<br>外跳 ≥30 分钟且 ≤72 小时仍未消失时，show_claim_entry=true，卡片出“未跟单？去找回”入口（BR-ATTR-17）；该 link 为无返利购买时，只有 no_rebate_reason ∈ {auth_declined, auth_failed} 且用户此后已完成该平台授权才 show_claim_entry=true（拍板第二批 TRADE-09）。卡片文案进 BR-TEXT-14，默认标题“订单同步中”，说明“在{platform_name}下单后，订单通常会在一段时间内同步到这里，同步可能有延迟”；CAP-*-07 实测前不写具体分钟数，实测后改为“最长约 {n} 分钟”，n 取配置 order_sync.delay_hint_min.&lt;platform>（G-05）。<br><br>找回页提供“一键上传诊断”，内容为：最近 20 次 link_log、跳转方式、授权状态，以及淘宝、京东、拼多多、美团这几个目标 App 是否可唤起。检测方式：iOS 只查 LSApplicationQueriesSchemes 白名单内的 scheme；Android 只查 queries 中声明的包名；鸿蒙同理；不读取完整应用列表。上传前弹窗逐项展示内容，用户点击同意后才上传；诊断包留存见 BR-ID-30 ④，隐私政策中单列这一用途。<br><br>只有用户点击时才触发外跳；不得做不带跟单参数的直接唤起。 | 默认假设 | 04 §2.3 order_reason 字典；claim_items.reject_reason；JumpTip 组件、配置与已读记录（服务端）；待跟单卡（显示与消失条件、BR-TEXT-14 文案）；GET /v1/orders/pending-tracks、POST /v1/orders/pending-tracks/{link_id}/dismiss（04 §6.4 新增）；links.track_dismissed_at（新增）；10 AC-S1-25、§0.3 时钟；配置 order_sync.delay_hint_min.&lt;platform>（CAP-*-07 实测后填）；H5 找回页诊断上传（同意弹窗）；隐私政策；客服话术 |
| BR-ATTR-22 | **订单唯一键**<br>订单唯一性由不分区的 order_keys 表保证：主键 (platform, sub_order_id)，另有列 order_id、app_id（NOT NULL）、created_at。同步 upsert 时，在同一事务中先插入或读取 order_keys，拿到 order_id，再写分区表 orders。orders 按 attr_at 月分区（attr_at 首次入库后不再改变，见 BR-ATTR-25），主键为 (order_id, attr_at)，分区表上不建业务唯一键。<br><br>order_keys 的主键不以 app_id 开头，是“业务唯一键以 app_id 开头”这条规则的唯一例外；orders.app_id 仍为 NOT NULL。order_keys 冲突时，如果已存的 app_id 与本次计算出的 app_id 不同，不得更新订单，并发 P1 告警。<br><br>各平台 sub_order_id 的构造方式（淘宝 trade_id；京东 orderId+skuId，或订单行 id；拼多多 order_sn）在 09 核实之前为待验证。<br><br>实现约定（拍板第二批 TECH-09；ADR-0001 §4.2）：保留分区；分区表（orders 等）的建表与分区用手写 SQL 迁移，与其他表同一迁移序列，不由工具自动生成；order_keys 另存 attr_at（与 orders.attr_at 同值，写入后不变），按 order_id 查订单时先取它做分区裁剪；需要引用订单的外键一律指向不分区的 order_keys（order_keys.order_id 建唯一约束），不指向分区表 orders。 | 已确认 | order_keys 表（新增；order_id 唯一约束供外键引用；attr_at 供分区裁剪）；orders 分区键与主键；02 §12.3 数据保护例外说明；手写 SQL 迁移脚本（分区表）；订单同步 upsert |
| BR-ATTR-23 | **跟单成功率与跟单率**<br>跟单成功率是 MVP 验收指标，每个平台单独验收。计算方式：测试真实订单中，同时满足 user_id=下单测试账号对应的用户、buy_type 正确、source_match≠none 的笔数，除以测试真实订单总笔数；目标 ≥95%。某平台订单不能派生 product_key（product_key.order_derivable.&lt;platform>=false，BR-PROD-03）且无 lk（attr.click_code.&lt;platform>=false 或该平台无点击级透传，如淘宝，09 U-37）时，source_match 不计入分子，该平台只按 user_id 与 buy_type 正确率考核，≥95% 目标改由负责人按实测重定（依赖 CAP-TB-07、CAP-JD-07、CAP-PDD-07，见细则）。每个平台样本 ≥20 笔；S1 出门样本覆盖 self_buy、agent 两种场景；share 在分享功能（M-公开）上线后另补 ≥20 笔单列统计，不计入 S1 出门；样本覆盖 iOS、Android、鸿蒙、H5 中已上线的端（订单的端取回填到的 link_log.client）。<br><br>跟单率是线上监控指标：<br>- 分子：当日（+08:00，按 attr_at）付款、已入库的本 App 订单数（含未归因）。订单的端取回填到的 link_log.client，没有回填的记为 unknown。<br>- 分母：当日 link_logs 中 event∈{convert, open}、result_code=0 的记录数，按 client 分组。<br>按平台、按端统计；每日 10:00 计算前一日数据（留出同步延迟），比前 7 日均值下降 ≥30% 时告警。 | 默认假设 | 05 分阶段验收（S0/S1）；02 §13 业务告警；link_logs.client；看板：跟单率、截流比例；10 首个完整流程验收用例 |
| BR-ATTR-24 | **淘礼金订单归属**<br>首版按 D7 不接入淘礼金（拍板第二批 AI-01 确认）；以下 A/B/C 归属处理仅在后续接入且能力验证后适用，第三方淘礼金素材一律转链、不提供「复制原口令」（00 D20）首版即适用。用户下单时使用了他人的淘礼金，订单大概率归淘礼金的创建者（淘宝佣金归属优先级待 06 Q-G3 核实）。素材中的淘礼金按接口实测结果分类，不看素材文案：<br>- A 类：解析出的推广位在本 App 白名单内 → 保留，归我方。<br>- B 类：品牌开放，用我方 adzone_id + relation_id 转链后仍带权益 → 保留，归我方；实测通过之前按 unknown 展示（BR-TEXT-15 判定 3′）。<br>- C 类：其他推广者创建 → 一律给出本 App 转链后的商品卡（scene=agent），不提供「复制原口令」（00 D20，负责人 2026-09-30）；不改写用户剪贴板中的原口令；按 BR-TEXT-15 如实提示该淘礼金可能领不到（OTHER_TLJ）。负责人预期转链后淘礼金保留，待 CAP-TB-09 实测。<br>话术不得把未核实的平台规则说成事实，不得承诺返利金额或价格。淘礼金推广位专用，不得与任何其他推广位共用（包括优券汇的）。 | 待验证 | parse_input / 淘礼金判定；Agent explain_order 与话术；Agent 商品卡（C 类给本 App 转链后的商品卡）；union_pids（taolijin 位）；客服话术 |
| BR-ATTR-25 | **归因时点 attr_at**<br>归因时点 attr_at = COALESCE(deposit_paid_at, paid_at)：预售单取付定金的时刻，普通单取付款时刻。attr_at 只在首次入库时确定，写入 orders.attr_at，之后不再修改。<br><br>本主题中凡是涉及“付款时点”的比较，一律用 attr_at 计算：BR-ATTR-02 的 sync_start_at 过滤与丢弃计数日期、BR-ATTR-07 的绑定区间、BR-ATTR-13 的 W_backfill 与 W_claim、BR-ATTR-17 的付款日期因子与找回窗口、BR-ATTR-18 的证据窗口、BR-ATTR-22 的分区键、BR-ATTR-23 的跟单率日期。<br><br>deposit_paid_at 与 paid_at 都为空的订单不入库，记 order_sync_drops reason='NO_PAY_TIME' 并告警；后续同步带上付款时间后照常入库。orders.paid_at 仍按平台原值保存（预售单为付尾款的时刻），用于展示、资金规则（见 BR-FUND）和分佣快照的等级与上级取值（BR-CALC-12）；归属判定不用 paid_at。 | 默认假设 | orders.attr_at（新增，分区键）；订单同步 worker；order_sync_drops reason NO_PAY_TIME；BR-ATTR-02/07/13/17/18/22/23 的时间比较；H5 找回页预售提示 |
| BR-ATTR-26 | **归因流水线黑名单步骤**<br>BR-ATTR-01 ③ 对每条入库或更新的子订单检查 blocklist（BR-ID-31）中的两类名单，命中任一即按下方命中处理（① 尾号维度未启用时除外）：<br>① 订单号尾号黑名单（只适用淘宝）：订单父订单号（trade_parent_id，按字符串）的末 6 位字符，与名单中 dimension=order_no_suffix、platform=taobao、status=active 的值逐字符相等。该维度在 CAP-TB-07（09 U-42）验证通过、且配置 attr.blacklist.order_suffix_void_enabled（默认 false）打开前，命中只写 risk_hits（risk_action=manual_review），不改 rebate_status、用户侧无变化；打开后按下方命中处理。<br>② 渠道黑名单（渠道单）：订单 relation_id 与名单中 dimension=channel、同 union_account_id、status=active 的记录相等，且 start_at ≤ attr_at，end_at 为空或 attr_at &lt; end_at（半开区间，绝对时刻比较）。渠道单由后台导入（01 F-ORD-10）；导入时 start_at=导入时刻，end_at 可空（空=持续生效）。<br><br>命中后的处理：rebate_status ∈ {UNATTRIBUTED, ESTIMATED, WAITING} → 按 BR-FUND-01 R6（BR-FUND-07）置 VOID，reason_code=BLACKLIST，写 risk_hits（risk_action=void_commission）（流水线事件名 BLACKLIST_HIT；用户侧说明与申诉入口见 BR-TEXT-05）；rebate_status=CREDITED → 不自动扣回，写风控事件 blacklist_hit_after_credit 并进人工复核（复核确认后按 BR-FUND-01 R8（BLACKLIST_CONFIRMED）扣回）；rebate_status 已为 VOID 或 CLAWED_BACK → 不处理。黑名单只让订单失效，不改 user_id、buy_type。<br><br>检查时点：只在 BR-ATTR-01 流水线运行时（首次入库，或 content_hash 变化）检查。名单新增后，存量订单在其下一次同步更新时被检查；不做全表回扫。名单统一用 BR-ID-31 的 blocklist，不另建表；名单的新增、停用由运营管理员经二次验证操作，写审计；名单记录不物理删除，停用置 status=inactive；名单维护、申诉与命中记录按 BR-ID-31、BR-ID-36。订单侧黑名单只在本条维护，BR-ID-38 已废弃并指向本条（C-18）。 | 待验证 | blocklist（BR-ID-31；dimension 新增 order_no_suffix、channel，字段 platform、union_account_id、value、start_at、end_at、status）；配置 attr.blacklist.order_suffix_void_enabled；risk_hits；订单同步流水线 ③；orders.reason_code=BLACKLIST；风控事件 blacklist_hit_after_credit；后台名单管理与渠道单导入（F-ORD-10、F-ADM-18）；审计日志；09 U-42、CAP-TB-07 |
| BR-ATTR-27 | **外跳路径与未安装降级**<br>“平台 × 端（iOS、Android、鸿蒙、H5）× 已装/未装”的首选路径（primary）与降级路径（fallbacks）只在本条维护，由服务端在 convert / open 响应中下发 primary、fallbacks，客户端只按顺序执行、不自行拼 scheme；按钮与提示文案进 BR-TEXT-14。默认矩阵见细则（取 09 U-59 与 CAP-TB-11、CAP-JD-11、CAP-PDD-11、CAP-X-04 降级列）。<br><br>路径选择的输入：<br>① 已装状态由客户端上报：convert 与 open 请求体带 installed ∈ {true, false, unknown}。iOS 用 canOpenURL 查 contracts/apps.json 声明的 scheme（在 LSApplicationQueriesSchemes 内）；Android 查 &lt;queries> 中声明的包名；鸿蒙查 querySchemes 声明的 scheme；H5 固定为 unknown；检测失败或未声明时报 unknown。端取请求头 X-Platform，不信任请求体。缺省 installed 按 unknown 处理。<br>② 服务端按 (platform, 端, installed) 查 specs/platform-matrix.csv 下发 primary、fallbacks；installed=unknown 时按“已安装”列下发，并在 fallbacks 末尾追加“未安装”列路径。按钮文案（如“安装淘宝后下单才有返利”）只在 installed=false 时于点击前展示；unknown 时在全部路径失败后展示。<br>③ 放行范围：每条路径在对应 CAP-*-11（鸿蒙另含 CAP-X-04）验证通过前是条件项。非生产环境，以及生产环境的 agent / 内测白名单用户（agent.whitelist_user_ids），按细则“默认矩阵”下发；生产对外用户只下发已验证路径，不得对外承诺“可返利”；某平台某端对外用户没有已验证路径时，该端该平台按下方“全部路径丢归因”处理。某条路径验证丢归因 → 从矩阵删除；某端某平台全部路径丢归因 → 该端隐藏该平台购买按钮并提示（按平台 × 端开关）。只有用户点击时才外跳（BR-ATTR-21）。每次外跳客户端上报 link_jump（路径、是否拉起成功）。 | 待验证 | contracts/apps.json；specs/platform-matrix.csv（键 platform × 端 × installed）；convert / open 请求体 installed（04 §6.3 新增）；请求头 X-Platform；convert / open 响应 primary、fallbacks；03 §4.5 TradeJump（改为按本条执行）；非生产 / 白名单放行默认矩阵；link_jump 上报；BR-TEXT-14 降级文案（取代“口令已复制，打开淘宝即可领券”）；CAP-TB-11、CAP-JD-11、CAP-PDD-11、CAP-X-04；按平台 × 端购买按钮开关 |
| BR-ATTR-28 | **花卷云侧过滤与 AF-07 双向验证**<br>花卷云侧过滤（运营动作）：在花卷云“忽略的 PID / 不入库的 PID”中登记新 App 的推广位。默认做法（待验证）：淘宝填新 App 的媒体级 mm_a_b，京东、拼多多按推广位逐个填写。以下两点是未实测的外部行为，不得当作事实实现或对外承诺：① 淘宝一条媒体级 mm_a_b 能覆盖该媒体下现有和将来的全部推广位；② 京东、拼多多各最多 100 条（来源：花卷云功能查漏底稿 §3，以花卷云后台实际为准）。在 ① 被 AF-07 证实之前，淘宝每新增一个推广位也必须当天在花卷云逐条补填（与京东、拼多多相同）。W0 必须完成花卷云忽略配置并截图留档。<br><br>新增的推广位先处于 pending：计入 BR-ATTR-02 的归属白名单，但不用于转链。填写 hjy_ignore_confirmed_at 和截图路径之后，才能由 super 经二次验证改为 active；淘宝在 ① 证实后，推广位填媒体级配置对应的那条记录。<br><br>每个平台在打开 convert.enabled.&lt;platform> 之前，必须完成 AF-07 双向验证，时限为该平台 convert.enabled.&lt;platform> 打开前（权限已批的平台按 W1 安排；联盟权限获批晚于 W1 的平台顺延至获批后，按 09 README §7.0 处理）：新 App 链接的真实订单在新 App 入库、在花卷云不入库；优券汇链接的真实订单在新 App 不入库（drops 计数加 1）。核对时刻为付款后 T_check = 该平台 CAP-*-07 实测付款到可查询延迟 P95 + 余量（默认 P95 × 2，且不少于 30 分钟）；CAP-*-07 未出结果前，核对截止取付款后 24 小时，期间任一系统查到该笔即可判定。某平台 AF-07 未通过前，该平台 convert.enabled.&lt;platform> 不得打开。 | 待验证 | union_pids（pending → active 关卡、hjy_ignore_confirmed_at）；花卷云后台配置（运营动作）；05 W0/W1 清单；验收用例 AF-07；配置 convert.enabled.&lt;platform>；CAP-TB-05、CAP-JD-05、CAP-PDD-05（U-10）；CAP-TB-07、CAP-JD-07、CAP-PDD-07（U-18） |
| BR-ATTR-29 | **第三方页容器内的平台页面与商品链接**<br>第三方页容器（路由 ExternalPage，容器 ExternalWebView，规划/03 §5.1）里不留「看起来能买、订单却不带用户归因」的入口。<br><br>① 配置侧（活动转链上线前）：后台保存任何可配置的跳转目标或外链（首页卡片与弹窗的跳转、公告条、推送与站内信模板的跳转、帮助 / 规则 / 公告文章里的外链）时，目标是 ExternalPage 且 url 主机命中「平台链接形态表」里联盟平台网页域名（category=union_host）的，拒绝保存，提示改用商品详情跳转或等活动转链上线。开关 external_page.union_host_block 默认 on，关闭须 step-up 并写审计。活动转链（按用户身份为联盟活动页生成推广链接，P1）上线后，联盟活动页只经活动转链入口打开，本项届时改写。<br><br>② 运行侧：ExternalWebView 的每一次主框架导航（含容器打开的第一个 URL、页内点击与重定向的每一跳）都按「平台链接形态表」判定，凡主机命中联盟平台网页域名（category=union_host）的导航一律不在容器里加载，分两种处理：<br>（a）商品页形态（category=product）：客户端取消这次导航，把该 URL（去掉 # 之后的部分）交 POST /v1/inputs/parse 识别。识别成功 → 打开原生 ProductDetail，之后与其他入口进入详情页相同：用户点购买才经 open 转链，scene=detail、pid_scene=self_buy（BR-ATTR-08），不新增 scene 取值，来源记在 spm 的页面段 external_page。识别失败（30131、30132、30141 或 5xxxx）→ 留在当前页并提示（BR-TEXT-14 external_page.product_unresolved）。<br>（b）其他平台页面（会场、店铺、搜索、购物车、结算页等）：客户端取消这次导航，留在当前页并提示（BR-TEXT-14 external_page.union_host_blocked），只给【去搜索】一个去向；不提供「继续访问」，不提供把这个地址交给系统浏览器或平台 App 打开的入口。容器要打开的第一个 URL 就命中时，不进入容器，直接出同一提示。<br>基本模式下，或客户端开关 features.external_page.product_intercept 关闭时，（a）不做识别，按（b）处理；任何情况下都不得变成直接加载平台页面。只上传本地命中的商品页 URL，不上传页面内容与 Cookie；不向第三方页面注入脚本、不改写页面。每次命中记一条埋点（平台、类别与处理结果，不带完整 URL）。<br><br>规则表的取用：客户端依次用 /v1/config.link_patterns 的当前版本、上一次成功拉取的版本、包内内置的规则表快照；内置快照至少含各联盟平台网页的注册域，按整域判定（宁可多拦）。拉取失败不得导致不拦截。<br><br>开关 external_page.union_host_block（默认 on）同时管 ① 与 ②（b）：服务端用它做保存校验，并随 /v1/config.features 下发给客户端；客户端取不到时按 on。只有负责人选定备选 B 并补齐页面提示之后才能关闭。<br><br>平台链接形态表只有一份（platform × category × 模式，category ∈ {product, promo, union_host}）：服务端 parsing 与后台保存校验直接读，客户端取得后只用于本地判定导航去向，商品识别一律以服务端结果为准。promo（推广链接形态）一类供非 https 跳转、外跳与桥方法的规则使用，不在本条。本条覆盖不到的边界见细则「尚未闭合的边界」，在负责人确认前不视为已解决。 | 待决策 | 后台保存校验（pages、notify-templates、articles 等含跳转目标或外链的资源）；配置 external_page.union_host_block（服务端与 /v1/config.features）、features.external_page.product_intercept、/v1/config.link_patterns；specs/link-patterns.yaml 与包内内置快照；ExternalWebView 导航回调（三端）；POST /v1/inputs/parse；ProductDetail；BR-TEXT-14 external_page.product_unresolved、external_page.union_host_blocked；埋点 external_page_union_host；01 §4.2 ExternalPage、F-LINK-11；03 §5.1；07 联盟活动转链行；04 §9 trade.openUnionActivity（P1）；10 AC-S1-70；06「功能对照待确认」Q-02 的边界 |

### 4.2 细则

#### BR-ATTR-01 细则 · 归因流水线顺序

- 状态：默认假设
- 默认值：未归因订单每次更新都重跑用户归属；已归属订单不重跑，也不覆盖归因参数；快照按 BR-CALC-10 在首次「已归因且 platform_status 已到 PAID 及之后（非定金、未作废）」时生成，等级与上级取 paid_at 时刻（BR-CALC-12）；按更新时间丢弃旧数据的逻辑，只在平台核实后按平台开启
- 决策人：负责人
- 依赖平台能力：各平台订单更新时间字段是否总会返回、是否单调递增（09 核实）
- 取代：
  - 02_系统架构.md §7.3：「流水线没有说明未归因订单在后续同步中是否重跑、已归属订单是否会被改写；“分佣快照（首次入库时）”→ 首次同时满足已归因与已付款（非定金）时（BR-CALC-10）」
  - 04_数据模型与契约.md §4.1 O2：「PLATFORM_PAID 时生成分佣快照（无“已归因”条件）→ 按本条 ⑥：已归因才生成，对应 BR-FUND-01 P2 与 R2/R3」
  - 01_需求规划.md §3 分账口径：「快照：订单首次入库时 → 首次同时满足已归因与已付款（非定金）时」
  - 本主题前稿 BR-ATTR-01 ⑥：「user_id 首次由空变非空时生成、DEPOSIT_PAID 也生成、关系链与等级取生成时刻 → 按 C-06 改为 BR-CALC-10 时点 + BR-CALC-12 paid_at 取值」
- 来源：02_系统架构.md §7.1、§7.3；04_数据模型与契约.md §3.2 orders、§4.1 O2、O11；01_需求规划.md §3 分账口径（快照）；PRD修订_后端功能规划 §2.5、§1.7；BR-FUND-01；BR-CALC-10、BR-CALC-12
- 需同步修改的规划文档：5 处（计数仅作记录，落点见 README §0.6）

**时点**：由订单同步 worker 触发（05 B1-08），不由客户端触发。

**例**：淘宝子订单 S1 在 2026-10-20T12:00+08:00 付款，推广位属于新 App 分享位，relation_id=R9 在付款时点对应用户 A 的绑定：①通过 → ②user_id=A → ③未命中 → ④share → ⑤回填 A 的 share link_log → ⑥生成快照（等级与上级取 10-20T12:00 的值）→ ⑦platform_status=PAID、rebate_status=ESTIMATED（BR-FUND-01 P2、R2）。

**未归因订单重跑**：S2 首次同步时没有 relation_id，进入未归因池（rebate_status=UNATTRIBUTED），不生成快照。10 分钟后同步到的更新带上了 R9，此时重跑 ②，归属 A，user_basis=param，rebate_status→ESTIMATED，执行 ⑤⑥，并按 BR-ATTR-16 处理这个子订单的找回子项。

**预售**：10-15T20:00 付定金时入库并当即归属 A（platform_status=DEPOSIT_PAID，rebate_status=ESTIMATED 且不计预估），此时不生成快照；10-20T09:00 付尾款（P2，platform_status→PAID），此时生成快照，等级与上级取 paid_at=10-20T09:00 的值。如果定金阶段未归因、11-01 找回通过，快照在找回通过时生成，等级与上级仍取 10-20T09:00 的值。

**找回时已作废**：未归因订单 S4 已 rebate_status=VOID，管理员变更给 A → 只写 user_id=A、user_basis=admin，不生成快照（BR-CALC-10）。

**参数变化**：已归属 A 的 S1 在后续同步中带回 relation_id=R7 → 不改 user_id，也不改参数字段；写 order_attr_param_changed，发 P2 告警。

**乱序**（attr.mtime_ordering.taobao=true）：库内 platform_modified_at=10:05，新到一条是 10:03 → 丢弃。新到一条同为 10:05、但 content_hash 不同 → 照常处理。

**状态名映射**：本条按 BR-FUND-01 双状态书写；前稿与 规划/04 的「O2」对应 BR-FUND-01 P2（付款）及同事务的 R2（入库已归因），「O11」对应 R3，「状态机未定义的迁移」对应 P10（倒退）与迁移表外事件。按 C-01、C-06 默认处理，已由负责人确认 2026-09-30。

#### BR-ATTR-02 细则 · App 归属：推广位白名单

- 状态：默认假设
- 默认值：推广位分 pending/active/retired 三种状态，都计入白名单；sync_start_at 取本 App 在该联盟账号下第一个推广位的创建时刻
- 决策人：负责人
- 依赖平台能力：—
- 取代：
  - PRD修订_后端功能规划 §2.2：「表名 promotion_positions、scene 值 tlj → 统一为 union_pids、pid_scene=taolijin」
  - 02_系统架构.md §6.3：「union_pids 字段名 scene → pid_scene」
- 来源：00_总览与决策.md §3.1 D1；01_需求规划.md E09 F-ORD-02、E05 F-LINK-02；02_系统架构.md §6.3、§7.3；PRD修订_后端功能规划 §2.2、§2.5；参考_花卷云功能查漏底稿 §3
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**判定伪代码**：`pid = union_pids.find(app_id, match_key)`；`pid==null → drop(PID_NOT_OURS)`；淘宝 `adzone 命中但 site 不符 → drop(SITE_MISMATCH)`；`attr_at < sync_start_at → drop(BEFORE_SYNC_START)`；其余情况入库，并记 `orders.pid`。

**例**：共用联盟账号下，adzone 1001 属于优券汇，2001 属于新 App 分享位；新 App 第一个推广位在 2026-09-29T00:00+08:00 创建，sync_start_at 就取这个时刻。同步拉到 3 笔订单：1001、2001、2001（付款时间 2026-09-01）。结果：入库 1 笔；drops 表记 PID_NOT_OURS=1、BEFORE_SYNC_START=1。下一轮时间窗口有重叠，又拉到 1001 这一笔 → drop_keys 里已有，不再计数。W0/W1 的 AF-07、06 Q-G1 验证订单付款时间都晚于 09-29，能够入库。

**为什么保留 retired**：用户 10-01 点了自购位 2002 的链接，10-03 这个推广位停用，10-10 付款。如果把 2002 移出白名单，这笔订单会被丢弃，用户丢单。

**告警**：按平台统计，滚动 24 小时内本 App 入库订单数为 0，且同期 link_logs 中 event∈{convert, open}、result_code=0 的记录 ≥50（阈值可配）时告警。

#### BR-ATTR-03 细则 · 双品牌隔离

- 状态：已确认
- 默认值：—
- 决策人：负责人
- 依赖平台能力：—（花卷云侧过滤机制已拆到 BR-ATTR-28）
- 状态变更（2026-09-30）：原条目把花卷云侧过滤（媒体级覆盖、100 条上限、AF-07 付款后 30 分钟核对）与隔离原则一并标为已确认；按 README §0.3，未实测的外部行为不能标已确认，拆出为 BR-ATTR-28（待验证）。本条只保留隔离原则，状态仍为已确认
- 取代：
  - PRD评审（F-29）：「经花卷云降级转链/拉单——作废」
- 来源：00_总览与决策.md §3.1 D1；02_系统架构.md §6.3、§12.3；PRD v2.1 §3.1、§3.2 硬规则 1–4；PRD修订_后端功能规划 §2.2；07_功能对照清单.md §4 #8
- 需同步修改的规划文档：00_总览与决策.md §3.1 D1「影响」列改为「花卷云填'忽略的 PID'（效果待 AF-07 验证，BR-ATTR-28）」；README 规则索引新增 BR-ATTR-28、状态计数待验证 +1；15 §15.1 登记 BR-ATTR-28，§15.2 删去 BR-ATTR-03 行

**权限未批前**：只能用录制回放开发，不得借用花卷云接口过渡。

#### BR-ATTR-04 细则 · 共用联盟账号可靠性

- 状态：待验证
- 默认值：共用联盟账号（保留已有高级权限）；验证不通过的平台单独改为新开账号；京东单个端不通过时只停该端
- 决策人：负责人
- 依赖平台能力：淘宝 06 Q-G1：同一买家两媒体备案后 relation_id 是否相同、adzone_id 能否可靠区分；拼多多 06 Q-G7：两 App 授权后 custom_parameters 是否互相覆盖；京东 06 Q-G6：subUnionId 回传完整性（App 原生、H5、scheme、鸿蒙分别验证）
- 取代：无
- 来源：06_待补信息清单.md Q-A4、Q-G1、Q-G6、Q-G7；PRD v2.1 §3.2 待真机验证、§18；PRD修订_后端功能规划 §12.2 V1；PRD修订_双品牌与Agent找货 §1.2
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

**验证方法**：同一买家账号先在优券汇完成备案并下单 1 笔，再在新 App 备案并下单 1 笔。对比两笔订单的 relation_id、adzone_id（拼多多对比 custom_parameters，京东对比 subUnionId），确认新 App 只入库第二笔。每个平台至少 3 组账号。

**结果**记录在 规划/09 对应行，并附接口响应样例的路径。

#### BR-ATTR-05 细则 · 归因身份只由服务端注入

- 状态：默认假设
- 默认值：按上述 ①–④ 处理；③ 选择“为当前用户重新转链”而不是报错，理由是不丢单，也不会把订单记到链接主人名下；link_id 不设打开期限，expire_at 只管返回的 URL
- 决策人：负责人
- 依赖平台能力：联盟口令、短链的实际有效期（09 核实），决定分享 URL 7 天是否可用
- 取代：
  - 01_需求规划.md E05 F-LINK-10：「分享类链接过期后自动重新转链 → 过期后经 open 按快照重新转链，link_id 不变、不续期」
- 来源：02_系统架构.md §6.1、§9.2；04_数据模型与契约.md §1、§3.2 links、§7；PRD修订_后端功能规划 §1.6、§2.2、§2.4；PRD v2.1 §10.4、§10.5；01_需求规划.md E05 F-LINK-10、E07 F-AGENT-08
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**要防的资损**：订单记到别人名下（后端 §1.6）。

**例**：用户 A 的 Agent 卡片链接 L1（scene=agent）被截图转发，B 在自己的 App 里通过深链打开 L1 → 服务端新登记 L2（user_id=B, scene=agent），用 B 的 relation_id 转链；L1 仍归 A，不受影响。B 的淘宝没有 active 绑定时 → 返回 30101 + auth_url，state 绑定 L2。

**例**：A 的淘礼金链接 L4 被 B 打开 → 为 B 按 scene=detail 走自购位转链，提示“该淘礼金仅限原用户使用”，不消耗淘礼金预算。

**例**：A 分享的 L3（share）被未登录的 C 在微信里打开 → 用 A 的身份和分享位转链，订单归 A（BR-ATTR-10）。10 天后 D 再打开 L3 → 已超过 expire_at，仍是 L3，按 A 的快照实时转链，link_log 记 expired=true。如果此时 A 的淘宝绑定已不是 active → 中间页显示“分享链接已失效”。

**缓存键**：`convert:{app_id}:{snapshot_user_id}:{platform}:{product_key}:{pid_scene}`，TTL ≤900 秒。

**例（游客 link）**：游客在设备 D1 生成 L6（user_id 为空），登录为 U 后在设备 D2 打开 L6 → 按 U 打开，写 L6.user_id=U（只写一次），不比对 device_id。之后 V 登录打开 L6 → 属他人，按 ③ 为 V 新登记 L7，比较基准沿用 L6 的 quoted_final_price_fen，响应带 new_link_id=L7。

**例（无效 link）**：link_id 不存在或属于其他 App → 30144。

**为什么不拒绝换设备或转发的 link**：按当前身份重新转链，订单归属正确、用户可以买；直接拒绝只会让用户买不了。

按 G-08 默认处理（合并 BR-AI-11、BR-PRICE-12 的校验），已由负责人确认 2026-09-30。

**App 内打开链接的入口**（2026-10-03，功能对照 G-03；按功能对照 Q-03 默认 A「做，放进第一版的分享任务」写，待负责人确认；docs/changes/20261003-功能对照补缺.md。open 的归属处理不变）：

- 入口：路由 `LinkLanding`（规划/01 §4.2），参数只有 link_id；可由深链 `https://<链接子域>/r/LinkLanding?link_id=…`（规划/03 §4.4）进入，分享中间页的【在 App 中打开】用的就是这条深链。
- 页面先调 `GET /v1/links/{link_id}` 取卡片：只读，不登记新 link、不写 link_log、不转链；卡片字段与分享中间页相同，不含返利金额（BR-PRICE-06、BR-ATTR-10）。用户点购买才调 `POST /v1/links/{link_id}/open`，open 的归属处理只按本条 ①–⑤ 与 BR-ATTR-11，本入口不另设规则。
- 分享 link：任何人都可以打开，未登录也可以点购买（①）；页面不显示打开者可得的返利，也不提供把链接换成打开者本人链接的入口（BR-ATTR-10）。
- 分享者本人打开自己的分享 link：`GET /v1/links/{link_id}` 返回 viewer_is_sharer=true，卡片上方显示一句提示（BR-TEXT-14 link_landing.owner_hint）；点购买后按 BR-ATTR-11 由服务端新登记自购 link。
- 非分享 link（例如别人的卡片链接被做成深链转发）：同样先出卡片，点购买时按 ②③④ 处理（未登录 10001；他人的 link 由服务端为当前用户新登记并返回 new_link_id）。
- link 不存在或不属于本 App：`GET /v1/links/{link_id}` 与 open 都返回 30144。本页没有卡片数据可供重新转链，显示空态（BR-TEXT-14 link_landing.invalid），不自动重试。
- 分享中间页（App 外 H5）：`GET /v1/share-pages/{link_id}` 多返回 `open_in_app_url`（即上面的深链；开关 share.open_in_app.enabled 默认 on，关闭时为 null、页面不显示按钮）。微信内不显示这个按钮，改为引导用浏览器打开（BR-TEXT-14 share_page.open_in_browser_hint）；按钮与引导文案不得带返利、红包等利益表述（规划/09 CAP-X-03 记录的微信外链规范）。深链的关联文件只放链接子域，不放分享页域名（规划/02 §3.4）。
- App 没有被拉起时（未安装，或系统没有接管这条深链），链接子域按 link 类型分流（规划/02 §3.4；2026-10-03 按评审补）：分享 link 回到它的分享中间页，页面改为显示下载入口；非分享 link 到下载引导页，link_id 不存在时同样到下载引导页，对外不区分这两种情况。下载引导页是不取任何 link 数据的静态页：匿名访问者只看到应用名称与图标、下载入口和【已安装，重新打开】按钮，看不到商品、价格、返利，也看不到链接主人的任何信息；该页不调用 `GET /v1/share-pages/{link_id}`（它对非分享 link 返回 30144），也不调用 `GET /v1/links/{link_id}`。安装并登录后重新打开同一条深链，仍按上面的规则进 LinkLanding。
- 淘宝：App 外仍按 BR-ATTR-10 细则（负责人 2026-10-03 确认）用预先转好的推广链接与淘口令；在 App 内经本入口打开时，open 按本条「2026-10-03 淘宝」说明下发带分享者身份的打开指令。两条路并存。

**例**：A 分享的 L3，C 在浏览器里的分享页点【在 App 中打开】→ C 的 App 进入 LinkLanding，看到商品、券与券后价（没有返利金额）→ C 点购买 → open 用 A 的身份与分享位 → 订单归 A（BR-ATTR-10）。A 自己点同一个按钮 → 页面提示这是自己分享的商品 → 点购买 → 新登记 L5，走自购位（BR-ATTR-11）。

#### BR-ATTR-06 细则 · 用户归属参数格式

- 状态：待验证
- 默认值：attr_code 为 8 位 [0-9a-z]；京东用 n_{attr_code}（attr.jd.user_key_mode=sub_union_id）；拼多多 JSON 含 app、uid、sc 三个字段，lk 按开关可选；no_rebate 购买不带任何用户参数、不做绑定或备案校验；京东转链接口默认 common.get，W1 两个接口实测后按 subUnionId 可用性定（拍板第二批 TRADE-11）
- 决策人：负责人
- 依赖平台能力：京东 06 Q-G6：subUnionId 长度、字符集（是否接受小写字母），以及 H5/scheme/鸿蒙下单时能否回传；拼多多 06 Q-G7：两 App 授权后 custom_parameters 是否互相覆盖，以及长度上限；CAP-JD-05：subUnionId 是否获批、私域推广位上限与工具商权限（决定 attr.jd.user_key_mode）；CAP-TB-06、CAP-PDD-06：self_buy 位不带 relation_id / uid 能否转链（no_rebate 例外）
- 取代：
  - PRD v2.1 §3.2 / 修订① §1.2：「拼多多 custom_parameters 只有 app、uid——以 规划/04 为准，加 sc」
  - PRD修订_后端功能规划 §2.4：「未备案错误码 30002 → 规划/04 的 30101/30102」
  - 01_需求规划.md E05 F-LINK-04、F-LINK-05：「uid=&lt;user_id>、subUnionId=n_{user_id} → 改用 attr_code」
  - 09_平台能力验证/3_JD_京东.md CAP-JD-05 降级列与“待决策”：「京东降级方案与 common.get / bysubunionid.get 二选一只写在 09」→ 规则在本条维护（attr.jd.user_key_mode、user_union_positions）；接口选择已由拍板第二批 TRADE-11 定（默认 common.get，W1 实测后按 subUnionId 可用性定），09 只保留实验与结论
- 来源：04_数据模型与契约.md §1 术语表、§7；01_需求规划.md E05 F-LINK-04、F-LINK-05、E09 F-ORD-03；PRD v2.1 §3.2、§8.1；PRD修订_后端功能规划 §2.2 备案绑定；09 CAP-JD-05；BR-ID-18、BR-ATTR-08（no_rebate）；docs/changes/20261001-拍板第二批.md（TRADE-11）
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）；另 04_数据模型与契约.md §3.2 新增表 user_union_positions；14 §14.1“京东转链接口 common.get vs bysubunionid.get”改为已定（拍板第二批 TRADE-11）；09 CAP-TB-06 验证项加“self_buy 渠道推广位不带 relation_id 能否转链”，CAP-PDD-06 加“不带 custom_parameters.uid 能否转链”

**例**：用户 attr_code=k3m9x2qa。京东 → subUnionId=`n_k3m9x2qa`；拼多多自购 → `{"app":"n","uid":"k3m9x2qa","sc":"self_buy"}`（44 字节）；attr.click_code.pdd=true 时最长样例 `{"app":"n","uid":"k3m9x2qa","sc":"taolijin","lk":"a1b2c3"}`（58 字节，≤64 字节控制值）。

**no_rebate 例外**：BR-ATTR-08 规定 no_rebate 购买（BR-ID-18）用 self_buy 位、不带用户参数，与本条“淘宝不得不带 relation_id 转链”是例外关系，不是冲突：UnionIdentity 构造时先判 no_rebate，为 true 则跳过绑定 / 备案校验与用户参数注入，不返回 30101、30102、30111。self_buy 位不带 relation_id 能否转链，在 09 CAP-TB-06 验证（需同步在 CAP-TB-06 验证项中加一条“self_buy 渠道推广位不带 relation_id 能否转链”）；拼多多不带 custom_parameters.uid 同理在 CAP-PDD-06 验证。

**京东降级例**：CAP-JD-05 结论为 subUnionId 未获批、工具商权限已批 → 负责人把 attr.jd.user_key_mode 改为 private_position。用户 U 首次京东转链 → position.create 得 positionId=9001，写 user_union_positions(U, jd, 9001)，用 9001 转链；订单回传 positionId=9001 → App 归属命中、反查得 U。第 5001 个需要分配的用户 V → 不再分配，V 的京东转链用 self_buy 位、不带用户键，订单进未归因池，V 在订单页看到 claim_required 文案并提交找回。

**为什么不用 user_id**：分享链接会被发到微信群，URL 里的参数谁都能看到。放 user_id 会暴露内部 ID 和注册规模，也把联盟参数和 ID 生成方式绑死了。

**异常**：京东订单 subUnionId 为空 → 进未归因池（常见于 H5/scheme 下单时参数丢失，待 06 Q-G6 验证）。拼多多 uid=zz000000，但本 App 没有这个 attr_code → 进未归因池并告警（可能是参数被篡改，或与其他 App 串号）。拼多多 uid 为数字 880123 → 解析失败。

**扩展**：京东、拼多多的点击级 link 短码（lk）见 BR-ATTR-15，验证前不下发。

**不做 PID 池**：按场景分推广位（BR-ATTR-08）+ 用户级归因参数识别用户，不做拼多多“每人一个 PID”的 PID 池（来源：PRD修订_后端功能规划 §13.2 #4）。

**与 BR-ID-22 的关系**：BR-ID-22 把联盟参数中的用户标识写成 ext_uid（HMAC-SHA256 截断 16 位 hex，京东 `n_{ext_uid}`，拼多多 uid=ext_uid）。按 C-04 建议默认采用本条的 attr_code：8 位比 16 位短，给 BR-ATTR-15 的 lk 留出长度；两者都不放 user_id 明文。最终以 06 Q-G6/Q-G7 实测的长度上限与字符集为准；实测前拼多多 custom_parameters 总长按 ≤64 字节控制（BR-ID-22，待核实）。按 C-04 默认处理，已由负责人确认 2026-09-30。

#### BR-ATTR-07 细则 · 淘宝按付款时点绑定归属

- 状态：已确认（负责人 2026-10-01，依据 docs/changes/20261001-拍板第二批.md §8 ADD-01：用户淘宝授权一次绑定、永久有效，不提供用户自助换绑，绑定只在注销时释放、释放后冷却 30 天，C-05 结案；原为待决策）
- 负责人意见（2026-09-30，docs/changes/20260930-拍板第一批.md §3）：遵循淘宝联盟官方开发文档实践；官方文档核对（09 V-06）后按文档定稿
- 状态变更：默认假设 → 待决策（2026-09-30，C-05）→ 已确认（2026-10-01，ADD-01）
- 默认值：按 attr_at 落在 [bound_at, COALESCE(cooldown_until, released_at)) 内的绑定归属；绑定释放（注销释放、后台重置授权）后 relation_id 冷却 30 天，冷却期内继续按区间归属原用户、不可被他人占用；冷却用 released + cooldown_until 表达，不新增 cooling 状态。理由：保留前稿“冷却期内旧链接订单仍归原用户”的效果，少一个状态值
- 决策人：负责人
- 依赖平台能力：淘宝点击有效期（09 核实），决定冷却期下限
- 取代：
  - PRD修订_后端功能规划 §2.2：「relation_id 冲突错误码 30003 → 30151；换绑每 90 天最多 1 次 → 30 天间隔与 30 天冷却（BR-ID-19）」
  - PRD v2.1 §8.3：「旧 relation_id 失效后订单按原用户归属截至换绑时刻——并入本条的归属区间规则（截至冷却结束）」
  - 04_数据模型与契约.md §4 绑定状态机：「换绑冷却 30 天后 → released（冷却期内状态未定义）→ 换绑成功即 released，冷却由 cooldown_until 表达（BR-ID-19）」
  - 本主题前稿 BR-ATTR-07：「解绑或换绑时旧绑定立即进入 cooling（新增状态），released_at=unbound_at+30 天，每小时扫描改 released；30152=名下已有 cooling 绑定 → 按 C-05 并入 BR-ID-19：新授权成功才替换，released_at=换绑时刻，cooldown_until=+30 天，归属截止取 cooldown_until；30152 按 BR-ID-19（距 activated_at 不足 30 天）」
  - 本条 2026-10-01 写法：「被换绑替换的绑定取 cooldown_until（由 BR-ID-19 在换绑成功时写入）；注销释放的绑定取 released_at（BR-ID-20 规定其 cooldown_until=released_at）」「换绑、冷却与恢复见 BR-ID-19」（拍板第二批 §8 ADD-01：取消用户自助换绑，释放后统一冷却）
- 来源：04_数据模型与契约.md §1、§2 union_binding_status、§3.2 union_bindings、§4 绑定状态机；01_需求规划.md F-ACC-10（注销置 blocked）；PRD修订_后端功能规划 §2.2、§2.5 第 4 步、§1.6；PRD v2.1 §8.3；参考_花卷云功能查漏底稿 §3、§16 #5；BR-ID-19、BR-ID-20；08 §14.3 C-05；docs/changes/20261001-拍板第二批.md §8 ADD-01
- 需同步修改的规划文档：4 处（计数仅作记录，落点见 README §0.6）

**时间比较**：统一存 timestamptz，比较用绝对时刻；展示时用 +08:00。区间左闭右开：attr_at = bound_at 归新绑定，attr_at = cooldown_until 不归旧绑定。

**例**：A 在 2026-10-01T10:00+08:00 绑定 R；A 反映错把家人的淘宝号授权给了自己，10-06T00:00 客服在后台「重置授权」（BR-ID-20）→ R 那条 released_at=10-06T00:00、cooldown_until=11-05T00:00；A 下次购买重新授权得到 R2 → 新行 active（bound_at=该时刻）。
- 10-10 付款、订单带 R（A 点过的旧链接）→ A（attr_at &lt; cooldown_until）
- 10-20 B 备案得到 R → 30151（R 冷却中，不透露原因）
- 11-06T09:00 B 绑定 R（冷却已结束）
- 付款 2026-11-04T23:59:59 → A
- 付款 2026-11-05T12:00 → 找不到绑定，进未归因池
- 付款 2026-11-06T09:00:00 → B（bound_at ≤ attr_at，边界含等号）
- 11-10 才同步到一笔 attr_at=10-03 的订单 → 命中 A 已 released 的那条绑定的区间 → A
- 用户不能自助换绑：A 在 App 内没有「更换淘宝账号」入口；A 用另一个淘宝账号重新授权时按 BR-ID-19、BR-ID-21 处理（不替换已有绑定）。

**为什么冷却 30 天**：淘宝点击有效期没有来源（09 U-17，待 CAP-TB-05 与 06 Q-G13 核实），BR-ATTR-13 规定核实前冷却期下限暂取 30 天；30 天的用意是覆盖旧链接的有效期，使 A 旧链接带来的订单不会在 B 绑定之后付款时落到 B 名下。平台核实后，如果点击有效期超过 30 天，必须同步调大冷却期。

**注销用户**：见 4.3 第 2 条（BR-ID-20）。

C-05 已由负责人决定（拍板第二批 §8 ADD-01）：一次绑定永久有效，不提供用户自助换绑，绑定只在注销时释放（释放后冷却 30 天）；后台「重置授权」（拍板第二批 OPS-11）保留，用于错绑纠正。

#### BR-ATTR-08 细则 · 自购与分享判定

- 状态：默认假设
- 默认值：按上表映射；淘礼金订单用户份额默认为 0；fallback 位不用于转链，只作白名单保留位（拍板第二批 TRADE-19 已确认）
- 决策人：负责人
- 依赖平台能力：—
- 取代：
  - 02_系统架构.md §7.3：「反查不到记 self_buy（pid_scene 值）→ 统一为 buy_type=self、scene_basis=fallback」
  - PRD修订_后端功能规划 §2.4：「scene 值 self_buy、h5_activity → 规划/04 的 scene 枚举（detail/h5 等）」
  - PRD v2.1 §10.18、§10.21：「link_log.scene 预留值未给出 pid_scene 映射——在本条补齐」
  - 本主题前稿 BR-ATTR-08：「P1 scene 含 digest、new_arrival、promo_reminder、replenish → 按 13 §13.2 不扩 scene，改记 sub_scene 或 watch.type」
  - 本条 2026-10-01 写法：「映射到入账账户：share → USER_PROMO；self_buy/agent/fallback → USER_SELF」（单一余额，拍板第二批 §8 ADD-06）
- 来源：04_数据模型与契约.md §2.2、§7；02_系统架构.md §6.3、§7.3；01_需求规划.md §3 分账口径、E09 F-ORD-04、J8；13 §13.2 scene 新增（P1）行；PRD v2.1 §8.2、§9.2、§10.21；PRD修订_后端功能规划 §2.5 第 4 步；docs/changes/20261001-拍板第二批.md（TRADE-19）；docs/changes/20261001-拍板第二批.md §8 ADD-06
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

| pid_scene | buy_type | 流水类型（入单一余额，BR-FUND-13） |
|---|---|---|
| self_buy | self | REBATE_CREDIT |
| agent | self | REBATE_CREDIT |
| taolijin | self | 默认不入账用户返利（用户份额 0，见 BR-TLJ/BR-FUND） |
| share | share | SHARE_CREDIT（分享者） |
| fallback | self | REBATE_CREDIT |

**为什么淘礼金默认不返利**：淘礼金已经从佣金里补贴过用户（记 MKT_EXPENSE），再按自购返利入账会重复补贴，导致预算超发。这与 01 分账口径“淘礼金商品默认不叠加自购返利”一致。

**例**：拼多多订单 pid=P-fallback，custom_parameters.sc=share → buy_type=share，scene_basis=param。sc 缺失 → buy_type=self，scene_basis=fallback。

**例**：淘宝订单 adzone 属于 Agent 位 → buy_type=self，scene_basis=pid，记 REBATE_CREDIT；source_scene=agent 由回填得出（BR-ATTR-15）。

**例（P1）**：摘要提醒里的商品被点击 → 转链 scene=watch_alert、pid_scene=self_buy，细分类型 digest 记在 sub_scene 或 watch.type，不作为 scene 取值。BR-WATCH 中把 digest 等写成 scene 的地方以 13 §13.2 与本条为准。

**第三方页容器回流**（2026-10-03，功能对照 G-02）：用户在 ExternalPage 里点到平台商品页、被转回本 App 商品详情后的购买，scene=detail、pid_scene=self_buy，不新增 scene 取值，来源只记在 spm（BR-ATTR-29）。

**no_rebate 购买**：用户在 BR-ID-18 选【仍去购买（无返利）】→ 用该平台 pid_scene=self_buy 的推广位转链，不带 relation_id、attr_code、sid 等任何用户参数；订单只做 App 归属、进未归因池，按 BR-ID-18 的找回证据规则处理。负责人若改为专用 fallback 位，只改推广位选择。按 G-07 默认处理，已由负责人确认 2026-09-30。

#### BR-ATTR-09 细则 · 归因依据字段拆分

- 状态：默认假设
- 默认值：拆成 scene_basis + user_basis
- 决策人：代理可自定
- 依赖平台能力：—
- 取代：
  - 04_数据模型与契约.md §2.3：「attribution_basis：pid/param/fallback/claim/admin 单字段」
- 来源：04_数据模型与契约.md §2.3、§4.1 O11
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

**原问题**：04 的 attribution_basis 把“场景依据”（pid/param/fallback）和“用户依据”（claim/admin）放在同一个字段里。找回通过后写成 claim，原来的 fallback 标记就丢了，“兜底判定为自购”的统计会失真。

**例**：订单 buy_type 按 fallback 判为 self，之后通过找回归属 → scene_basis=fallback、user_basis=claim。

#### BR-ATTR-10 细则 · 转链者、分享者与购买者

- 淘宝分享实现（负责人 2026-10-03 确认，docs/changes/20261003-淘宝转链改客户端百川.md §6-1）：分享时在 App 内用分享者身份转成我方推广链接并生成淘口令，分享内容带淘口令或推广链接；H5 分享中间页提供「复制淘口令」。取不到推广链接或口令时不生成淘宝分享，不以原链接代替。归属规则本身不变。

- 状态：默认假设
- 默认值：购买者不获得返利；中间页不引导购买者改用自己的链接。理由：联盟订单只能带一个身份；引导改链会直接拿走分享者的收益，损害分享积极性
- 决策人：负责人
- 依赖平台能力：—
- 取代：
  - 04_数据模型与契约.md §2.2 注：「分享单里的购买者自己能不能拿返利没有定义——本条定为不能」
- 来源：01_需求规划.md §2、J8、E13 F-SHARE-05；04_数据模型与契约.md §2.2；PRD v2.1 §9.2；docs/changes/20261001-拍板第二批.md（TRADE-06）
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

**例**：A 分享商品 X（券后价 9900 分，联盟佣金率 1000bp，预估佣金 990 分），B 在微信打开中间页后下单 → 订单 user_id=A，buy_type=share；A 的推广收益按 BR-FUND 的分成比例从 990 分中计算；B 在本 App 看不到这笔订单。

**如果 B 想自己拿返利**：B 必须在本 App 里自己搜索或粘贴商品转链（scene=clipboard 等），用的是 B 自己的链接。如果 B 点了 A 的链接之后又点了自己的链接，最终归属由联盟决定（BR-ATTR-12）。

**分享链接过期**：见 BR-ATTR-05、BR-ATTR-13（link_id 不变，按 A 的快照实时转链）。

#### BR-ATTR-11 细则 · 分享者通过自己链接下单

- 状态：已确认（负责人 2026-09-30，依据 docs/changes/20260930-拍板第一批.md §2）
- 默认值：App 内自己打开 → 改为自购；App 外打开 → 按分享处理，字段核实前只做人工复核。理由：App 内能准确识别身份，不会误伤；App 外无法识别，只能靠风控
- 决策人：负责人
- 依赖平台能力：联盟订单是否返回可用于比对的买家信息（设备、支付宝、收货手机号），以及隐私政策是否已覆盖这一用途，在 09 中逐平台核实
- 取代：
  - 01_需求规划.md E09 F-ORD-04 验收：「同一会员从详情和分享面板各下一单，分别入两个账户（负责人确认本条后作废）」
  - PRD修订_后端功能规划 §2.12：「推广自买单作废——判定细则移到 BR-RISK，本条只管 App 内改链和数据使用限制」
- 来源：01_需求规划.md E09 F-ORD-04；PRD修订_后端功能规划 §2.12；PRD v2.1 §14.4；06_待补信息清单.md 等级条件
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**理由**：推广订单数计入等级晋升（L2：近 30 天推广订单 ≥10 笔），推广收益与自购返利的比例也可能不同。允许分享者自买，会被用来刷单套利。

**例**：A 在 App 内点自己分享卡片上的“去购买” → 新登记 L5（scene=detail），走自购位，按自购计入 A 的余额（REBATE_CREDIT）；原分享链接 L3 不受影响。A 把分享链接发到微信，自己在微信里打开并下单 → 先按分享单入账；如果联盟返回的字段与 A 一致，进人工复核，由风控决定是否作废推广收益。

**入口**（2026-10-03，功能对照 G-03）：App 内打开分享链接的页面是 `LinkLanding`（BR-ATTR-05 细则「App 内打开链接的入口」）。`GET /v1/links/{link_id}` 的 viewer_is_sharer 只用来显示提示（BR-TEXT-14 link_landing.owner_hint）；是否改走自购位，仍只由 open 时服务端按本条判定。

#### BR-ATTR-12 细则 · 多次点击、多入口、他人链接

- 状态：默认假设
- 默认值：联盟回传参数是唯一依据，系统不改写
- 决策人：负责人
- 依赖平台能力：淘宝 06 Q-G3：佣金归属优先级；淘宝 06 Q-G4：平台内 AI 助手下单是否保留归因；京东、拼多多：多次点击的归属规则（09 逐平台核实）
- 取代：无（02_系统架构.md §7.3 与 PRD v2.1 §9.2 都没有写多次点击、多入口、他人分享链接的处理，本条为补充；02 §7.3 没有相应的注，不需要删除）
- 来源：01_需求规划.md J1 步骤 3；02_系统架构.md §7.3；PRD v2.1 §9.2、§10.6.1；PRD修订_后端功能规划 §12.2 V8；06_待补信息清单.md Q-G3、Q-G4
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

**联盟侧规则（待核实，不作为系统逻辑）**：公开资料显示多为“最后一次点击有效”；淘宝的佣金归属优先级为 预售 > 淘礼金 > 超级红包 > 口令（06 Q-G3）。这些信息只用于客服话术和 JumpTip 文案。

**例**：用户 U 在 10-01 通过 Agent 卡片点击商品 X，10-03 又从搜索页点击 X，10-03 付款。淘宝回传的是自购位 → buy_type=self；回填时取 pid_scene=self_buy 的最近一条（10-03 的 search 记录），source_scene=search。

**客服话术**：“订单归属以平台记录为准；下单前最后点的是谁的链接，订单通常就归谁。”

#### BR-ATTR-13 细则 · 四个时间窗口

- 状态：默认假设
- 默认值：W_click 三家均未配置（待 CAP-*-05、06 Q-G13 核实；核实前冷却期下限暂取 30 天，文案不写天数，不用于找回驳回原因）；W_link 自购和 Agent 15 分钟、分享 7 天；W_backfill 360 小时（暂定值，待点击有效期结果回写）；W_claim 720 小时（只在提交时校验）
- 决策人：负责人
- 依赖平台能力：淘宝、京东、拼多多各自的点击有效期（跟单周期），以及加购后下单是否计佣——在 09 中逐平台核实
- 取代：
  - PRD v2.1 §9.4：「找回范围为付款后 7 至 60 天 → 付款后 ≤30 天（规划/04、06 Q-B4）」
  - 01_需求规划.md J1 步骤 3：「对所有平台都写“点击后 15 天内有效” → 按平台配置，未核实的平台不写天数」
  - 01_需求规划.md E05 F-LINK-10：「分享链接 7 天与 JumpTip 15 天口径冲突 → 两者是不同的窗口，并存；分享链接过期后 link_id 不变」
- 来源：01_需求规划.md J1、J5、E05 F-LINK-10；04_数据模型与契约.md §2.3 EXPIRED_CLICK、§4.3；06_待补信息清单.md Q-B4、Q-G13；PRD修订_后端功能规划 §2.4、§2.5；PRD v2.1 §9.4；09 README U-17、附录 A-24
- 状态变更说明（2026-09-30）：删去“淘宝默认 15 天”与 JumpTip 写“15 天”的写法（三家点击有效期均无来源，09 U-17）；条目状态仍为默认假设
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）；另 14 §14.2 BR-ATTR-13 默认值列改为本条细则默认值；10_ID BR-ID-21 “付款前 15 天内点击”注明「待 CAP-*-05 点击有效期结果回写」

**例**（attr_at=2026-10-20T12:00:00+08:00）：
- link_log 2026-10-05T12:00:00 → 在回填窗口内（刚好 360 小时）；2026-10-05T11:59:59 → 在窗口外
- 找回可以提交到 2026-11-19T12:00:00，到 12:00:01 返回 30202 reason=CLAIM_EXPIRED；11-19T11:00 提交、11-21 客服审核 → 仍可以通过

**分享链接例**：A 在 10-01 生成分享链接 L3，B 在 10-09 打开 → 已超过 7 天，仍是 L3，按 A 的快照实时转链，写 link_log（event=open, expired=true）。

**JumpTip**：天数句按 BR-TEXT-12 的 jump_tip.&lt;platform>.claims_enabled 控制，默认 off；三家在 CAP-*-05 与 06 Q-G13 书面答复前都写“请在打开的页面尽快下单”，不写天数（09 U-17、附录 A-24）。

**依赖同一未核实数值的规则**（点击有效期结果回写时一并复核）：W_backfill 360 小时（本条 ③）；BR-ATTR-18 证据窗口与驳回原因 EXPIRED_CLICK 的“>360 小时”判据（点击有效期核实前，EXPIRED_CLICK 的用户文案不得写具体天数）；BR-ATTR-07 冷却期下限；BR-ID-21 巡检条件“付款前 15 天内点击”——均待 CAP-*-05 点击有效期结果回写。

#### BR-ATTR-14 细则 · link_log 记录与保留

- 状态：默认假设
- 默认值：按日分区，留存见 BR-ID-30 ②；被工单引用的记录在分区删除前复制到 link_log_evidence（留存见 BR-ID-30 ②）；新增 event、pid_scene、opener_user_id、client、cache_hit、expired 字段
- 决策人：代理可自定
- 依赖平台能力：—
- 取代：
  - PRD修订_后端功能规划 §2.4、§8：「按月分区保留 180 天 → 规划/01、04 的 90 天按日分区，另设证据表」
  - 02_系统架构.md §9.2 / 01 E07 F-AGENT-08：「预转链未区分事件类型 → 记为 precompute，不算点击证据」
  - 本条旧写法：「保留 90 天（≥ W_claim 30 天 + W_backfill 15 天）……link_log_evidence 保留到对应工单关闭后 180 天」（天数并入 BR-ID-30 ②）
- 来源：01_需求规划.md E05 F-LINK-08、E07 F-AGENT-08；02_系统架构.md §9.2 转链时机；04_数据模型与契约.md §3.2 link_logs；PRD v2.1 §8.2、§10.20；PRD修订_后端功能规划 §2.4；docs/changes/20261001-拍板第二批.md（TRADE-03）
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**为什么排除 precompute 和 register**：Agent 出卡时会登记、也会预转链，但用户可能根本没点。拿这些当证据，会让找回审核把“看过”误判成“点过”。

**为什么 open 命中缓存也要记**：用户在第二个 Agent 会话里点了同一个商品，如果因为命中缓存而不记，回填会落到旧会话上。

**例**：Agent 给出 5 张卡 → 5 条 register；出卡不预转链（拍板第二批 TRADE-03），没有 precompute；用户点了第 2 张 → 1 条 open（result_code=0，实时转链）。只有这条 open 能用于回填和找回证据。

**分享**：A 生成分享链接 → convert（user_id=A）；C 在微信打开 → open（user_id=A，opener_user_id=null，client=h5）。

#### BR-ATTR-15 细则 · 来源回填

- 状态：默认假设
- 默认值：MVP 先启用 product/shop 匹配；exact 在 CAP-JD-05、CAP-PDD-05（06 Q-G6/Q-G7）核实后按平台开启（配置 attr.click_code.&lt;platform>，布尔，默认 false）；lk 为 links 单独发号的 6 位 base36 短码，唯一索引 (app_id, lk)
- 决策人：代理可自定
- 依赖平台能力：京东 06 Q-G6：subUnionId 长度与字符集；拼多多：custom_parameters 长度上限；淘宝：订单 item_id 与转链 item_id 是否同一口径（商品身份见 BR-PROD）
- 取代：
  - 02_系统架构.md §7.3 / 01 E09 F-ORD-08：「多次点击取最近一条（不区分推广位场景）→ 先按订单推广位的 pid_scene 过滤，再取最近一条」
  - PRD修订_后端功能规划 §2.5：「同店铺匹配仅淘宝 → 三平台都可用（规划/04 §4.3 口径）」
- 来源：01_需求规划.md E09 F-ORD-08；02_系统架构.md §7.3；PRD修订_后端功能规划 §2.4 点击级透传、§2.5 第 5 步；PRD v2.1 §9.2
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**例**：订单 user_id=U，淘宝，product_key=tb:123，推广位 pid_scene=agent，attr_at=10-20T12:00。U 的 link_logs：10-10 search/self_buy/tb:123；10-18 open/agent/tb:123（session S7）；10-19 search/self_buy/tb:123；10-19 precompute/agent/tb:123（session S8）。结果：precompute 不算点击；pid_scene 与订单一致的只有 10-18 那条 → source_scene=agent，agent_session_id=S7，source_match=product。

**为什么过滤 pid_scene**：如果只取“最近一条”，10-19 的 search 会把这笔 Agent 成交记到搜索名下。

**改派例**：管理员把订单从 A 改给 B → 按 B 的 link_logs 重新回填；A 时的 source_scene、link_id 写入审计。

**lk 格式（待验证）**：京东 `n_{attr_code}_{lk}`，如 `n_k3m9x2qa_a1b2c3`（17 字符；京东转链入参上限 80 字符，来源 09 CAP-JD-05，订单侧回传待实测）；拼多多加 `"lk":"<6位>"`，最长样例 `{"app":"n","uid":"k3m9x2qa","sc":"taolijin","lk":"a1b2c3"}` 为 58 字节（sc 取值最长 8 字符），≤ BR-ID-22 的 64 字节控制值（64 字节为后端规划写法，平台实际上限待 CAP-PDD-05 核实）。解析时京东 lk 捕获组接受 1–16 位（BR-ATTR-06），以便将来调长；按 lk 反查不到 link 或 link 不属于订单 user_id → 不算 exact，继续 ②。

**为什么单独发号而不用 link_id 派生**：link_id 是内部主键，派生短码会暴露发号规律与规模（与 attr_code 不放 user_id 同理）；单独发号还能按平台限制调整长度而不动主键。

**需同步修改的规划文档（lk）**：04_数据模型与契约.md §3.2 links 增加 lk 列（可空）与唯一索引 (app_id, lk)。

#### BR-ATTR-16 细则 · 未归因池

- 状态：已确认（负责人 2026-09-30，依据 docs/changes/20260930-拍板第一批.md §2）
- 状态变更：默认假设 → 待决策（2026-09-30）。依据：默认值含待财务确认的金额口径（超窗未认领订单的佣金处理），按 README §0.3 应为待决策
- 默认值：告警阈值 5%、分母至少 20 笔；超窗未认领订单保持 UNATTRIBUTED、不入任何用户账户，联盟回款核销时整笔计平台留存。理由：超窗后已无用户可认领，不计平台收入会让应收长期挂账；收入确认时点由财务定
- 决策人：负责人（超窗佣金的会计处理：财务）
- 依赖平台能力：—
- 取代：无
- 来源：04_数据模型与契约.md §1 未归因池、§4.1 O11；02_系统架构.md §7.3、§13；PRD修订_后端功能规划 §2.5、§3.4；BR-FUND-01 R1、R3、R6
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**常见来源**：淘宝订单没有 relation_id，或 relation_id 找不到对应绑定；京东 H5/scheme 下单时 subUnionId 丢失；拼多多参数解析失败。

**例**：10-20 截至 15:00，京东入库 200 笔，其中 14 笔入库时没有 subUnionId → 未归因率 7%，超过 5%，告警，并按端和跳转方式拆分排查。同一天之后再次超标，不再重复告警。

**找回子项被取消的例**：U 用父单号提交找回，claim 含 S1、S2（submitted）；10 分钟后同步到的 S1 更新带上了参数、自动归属 U → S1 子项 cancelled，通知“订单已自动跟单”；S2 子项继续审核。如果 S1 被自动归属给 V → S1 子项 rejected(NOT_IN_POOL)，通知“该订单已由平台记录归属，找回已关闭”。

**同步归属时的返利状态**：S5 未归因期间平台已确认收货（platform_status=RECEIVED，rebate_status=UNATTRIBUTED，received_at=10-22T10:00）；10-23 同步带回参数、归属 U → rebate_status 直接到 WAITING，settle_period 按 10-22T10:00 的 received_at 取 2026-10（BR-FUND-04 ②），不从归属时刻重算。该迁移即 BR-FUND-01 R3a：写 user_id、user_basis=param，不置 locked，无分录；platform_status≠DEPOSIT_PAID 时同事务生成快照。按 C-27 (a) 默认处理，待负责人确认。

#### BR-ATTR-17 细则 · 找回受理与即时校验

- 状态：默认假设
- 默认值：第二因子为付款日期（预售为定金日期）；支持父单号匹配；按子订单去重
- 决策人：负责人
- 依赖平台能力：三平台订单接口能否返回父单号（淘宝 trade_parent_id 等），在 09 中核实
- 取代：
  - 01_需求规划.md J5 步骤 2：「只提交平台 + 完整订单号、精确匹配子订单 → 增加付款日期第二因子，并支持父单号」
  - PRD v2.1 §9.4：「淘宝另需付款金额或下单时间 → 三平台统一用付款日期」
  - PRD修订_后端功能规划 §2.5：「拒绝原因 NOT_FOUND/NOT_IN_POOL/EXPIRED → 映射到 30201/30204/30202(CLAIM_EXPIRED)」
- 来源：01_需求规划.md J5、E19 F-OBS-05；04_数据模型与契约.md §3.2 claims、§4.3、§7；PRD修订_后端功能规划 §2.5 订单找回、紧急开关 claims.enabled、错误码 30104；13 §13.3 30206；PRD v2.1 §8.5、§9.4；开发任务拆解 BT-14；docs/changes/20261001-拍板第二批.md（TRADE-09）
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

**为什么先校验付款日期**：先校验日期，再检查归属，不知道付款日期的人就无法通过返回码区分“已被他人认领”和“在未归因池中”，从而无法枚举订单归属。

**30201 文案**：“暂未查到该订单。订单一般在付款后 5 分钟内同步，请 30 分钟后再试；如果仍查不到，可能是下单前点了其他链接，或用了他人的淘礼金。”

**例**：U 输入父单号 P1（下有 S1、S2；S1 在未归因池，S2 已归属 U），paid_date=2026-10-20，attr_at=2026-10-20T23:30+08:00 → claim 只包含 S1，S2 不受影响。U 随后又用子单号 S1 提交 → 30205。

**例**：attr_at=2026-10-20T00:10+08:00（UTC 为 10-19），用户填 10-19 → FACTOR_MISMATCH（按 +08:00 取日期）。

**例**：预售单 10-15 付定金、10-20 付尾款，用户应填 10-15；找回页在预售说明里提示“预售单请填写付定金的日期”。

**开关关闭**：客服积压时运营关闭 claims.enabled → 提交返回 30206，不校验订单、不计失败次数；已提交的 claim 照常审核。

**第二因子为什么选日期**：订单截图上能直接看到付款日期，用户填写成本低；同时能防止只拿到订单号的人冒领未归因订单。

#### BR-ATTR-18 细则 · 找回证据与审核

- 状态：默认假设
- 默认值：MVP 全部由客服确认（D14 默认）；strong 自动通过属于 P1；同店铺证据只算 weak；无返利购买记录仅在事后已授权且无冲突时计入（拍板第二批 TRADE-09 已确认）
- 决策人：负责人
- 依赖平台能力：—
- 取代：
  - 01_需求规划.md J5 步骤 3：「满足证据条件（未定义）进待客服确认 → 按 strong/weak/none 定义」
  - PRD修订_后端功能规划 §2.5：「同店铺证据仅淘宝，且可作为自动匹配依据 → 三平台都可用，但只算 weak」
  - PRD修订_后端功能规划 §3.4：「claim 状态 PENDING/APPROVED/REJECTED/CANCELLED → 规划/04 状态名」
- 来源：00_总览与决策.md §3.2 D14；04_数据模型与契约.md §4.3；PRD修订_后端功能规划 §2.5、§3.4、§0.4 B9；PRD v2.1 §9.4；docs/changes/20261001-拍板第二批.md（TRADE-09）
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

**为什么同店铺只算 weak**：大店铺（天猫超市、京东自营）里点过任意一个商品，就能对同店铺别人的未归因订单拿到 strong；P1 开启自动通过后会被直接冒领。

**例**：申请人 U 的订单 attr_at=10-20T12:00，商品 tb:123。U 在 10-12 有 tb:123 的 open（result_code=0）→ strong → auto_matched → 客服一键通过。

**例**：U 只有 10-01 的 tb:123 记录（距付款超过 360 小时）→ none → manual_review；客服可以用 EXPIRED_CLICK 驳回。

**例**：父单 claim 含 S1(strong)、S2(none) → claim 为 manual_review；客服通过 S1、以 NO_EVIDENCE 驳回 S2 → claim.status=approved，S2 的驳回原因记录在 claim_items。

**例（无返利购买，拍板第二批 TRADE-09）**：C 拒绝淘宝授权后点「仍去购买（无返利）」（no_rebate_reason=auth_declined），10-20 付款 tb:123，订单进未归因池；10-23 C 完成授权（active）后提交找回 → 10-20 前那条 no_rebate open 计入证据，同商品 → strong → auto_matched，客服确认。若 C 的淘宝账号当时已被本 App 其他用户绑定（relation_conflict）→ 该记录永不计入，证据为 none，客服以 NO_EVIDENCE 驳回。C 尚未授权就提交 → 该记录不计入，同样 none。

**站长授权过期或失效期间（拍板第二批 §8 ADD-08）**：淘宝未绑定用户点购买只得到 30101 / 30102（data.reason=auth_unavailable），不外跳、没有无返利购买（BR-ID-24），不会产生 no_rebate_reason=auth_failed 的记录，这期间的订单没有找回路径；auth_failed 只指用户自己的授权失败。

**状态映射**：规划/04 的 submitted/auto_matched/manual_review/approved/rejected/cancelled 对应后端规划的 PENDING/APPROVED/REJECTED/CANCELLED。

#### BR-ATTR-19 细则 · 找回限流与风控

- 状态：默认假设
- 默认值：每日 5 条；失败 10 次封当日
- 决策人：运营
- 依赖平台能力：—
- 取代：无
- 来源：01_需求规划.md J5 步骤 4；04_数据模型与契约.md §3.2 claims、§7；06_待补信息清单.md Q-B4；PRD修订_后端功能规划 §2.5、§2.12
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

**例**：U 在 10-20 创建 5 条 claim 后，第 6 次提交 → 30203。另一用户 V 在 10-20 连续输错订单号或付款日期 10 次 → 当天被禁，10-21T00:00+08:00 解除。

**为什么两个计数分开**：“5 条”用来限制审核工作量；“10 次失败”用来识别撞库式冒领。付款日期约有 30 种可能取值，每天 10 次失败的上限让逐日试探在一天内无法完成。

#### BR-ATTR-20 细则 · 找回通过、改归属与锁定

- 状态：已确认（负责人 2026-10-01，依据 docs/changes/20261001-拍板第二批.md §8 ADD-05：资金操作一人可完成，须 step-up、写审计；原为默认假设）
- 默认值：已归属订单改归属由超管或被勾选改归属权限的账号经二次验证一人完成并写审计；允许原会员出现负余额，按 BR-FUND 处理
- 决策人：负责人
- 依赖平台能力：—
- 取代：
  - 04_数据模型与契约.md §4.1 O11：「只覆盖未归因订单的 CLAIM_APPROVED/ADMIN_REASSIGN → 补充已归属订单的变更、并发复查与锁定后的纠错」
  - 参考_花卷云功能查漏底稿 §6：「锁定后不能再找回、改归属、重算分佣 → 保留 super + 双人复核的纠错通道」
  - 本主题前稿 BR-ATTR-20：「并发冲突返回 30206 → 20902（data.resource=order_attribution），C-03」
  - 本条 2026-10-01 写法：「由 super 角色经二次验证发起，第二人复核（发起人 ≠ 复核人，与 02 §12.5 调账复核相同）」「只能走“super 发起 + 第二人复核”的纠错通道」（拍板第二批 §8 ADD-05）
- 来源：01_需求规划.md J5 步骤 4、E09 F-ORD-14；02_系统架构.md §12.5；04_数据模型与契约.md §4.1 O11、§7；PRD修订_后端功能规划 §2.5、§3.4；参考_花卷云功能查漏底稿 §6、§16 #14；docs/changes/20261001-拍板第二批.md §8 ADD-05
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

**例**：客服通过 U 对 S1 的找回 → 加锁重读，S1 的 user_id 仍为 NULL → user_id 改为 U，user_basis=claim，locked=true；platform_status 仍为 RECEIVED，rebate_status 由 UNATTRIBUTED 直接到 WAITING（R3，settle_period 按原 received_at 取）；该结算周期的月结账单已出账或批次已执行的，随补充批次或下一期账单按 BR-FUND-01 R5 入账（BR-FUND-04 ③⑧）。

**并发例**：客服点“通过”的同时，同步 worker 按参数把 S1 归给了 V。两边争同一把锁：同步先拿到锁 → 写 V；客服事务随后拿到锁，重读到 user_id=V → 子项 rejected(NOT_IN_POOL)，不生成第二份快照。

**例**：super 把已归属 A 的订单 S2（platform_status=PAID，rebate_status=ESTIMATED）改给 B，原因“A 与 B 为同一人换号，工单 #123”，超管 step-up 确认 → A 的预估分录、A 上级的分佣、平台留存全部红冲，B 生成新快照（B 与 B 上级的等级取 S2 paid_at 时刻），S2 锁定，两个状态都不变。

**并发冲突例**：管理员甲打开 S2 详情时 user_id=A、locked=false，提交改派时带 expected_user_id=A、expected_locked=false；提交前另一笔改派已把 S2 改给 C 并锁定 → 重读 user_id=C、locked=true，与期望不符 → 返回 20902（data.resource=order_attribution），后台提示刷新，不做任何修改。

**已入账订单改派（BR-FUND-01 R14）**：rebate_status 自迁移不变。ESTIMATED/WAITING：作废旧快照、按新 user_id 生成新快照，无分录。CREDITED：同事务先红冲原凭证（uniq_key `{order_key}:{old_uid}:{role}:REASSIGN_REV:{reassign_id}`），再按新快照记账（`{order_key}:{new_uid}:{role}:REASSIGN_CREDIT:{reassign_id}`）。VOID 且 user_id 为空的订单找回通过或改派（R3b）：rebate_status 保持 VOID，只写 user_id、user_basis、locked=true，不生成快照、无分录。按 C-27 (b)(c) 默认处理，待负责人确认。

**错误码**：前稿写 30206（订单归属已变化）；按 C-03 统一为 20902 + data.resource=order_attribution（与订单、提现的并发冲突同码）；30206 改为“找回功能暂时关闭”（BR-ATTR-17 ⓪）。按 C-01、C-03、C-06 默认处理，C-01、C-06 已由负责人确认 2026-09-30（C-03 已处理）。

#### BR-ATTR-21 细则 · 丢单原因码与防呆提示

- 状态：默认假设
- 默认值：三个原因码与 RELATION_INVALID 只用于诊断、驳回和授权提示；JumpTip 按用户 × 平台展示一次；诊断包只检测目标 App 是否可唤起
- 决策人：运营
- 依赖平台能力：—
- 取代：
  - 04_数据模型与契约.md §2.3：「NOT_TRACKED、EXPIRED_CLICK、OTHER_TLJ、RELATION_INVALID 作为订单原因码且“可找回”的标注」
  - 10_首个完整流程验收用例.md AC-S1-25 ④：「订单归属到 U1 后消失（任意订单）」→ 卡片消失只看该 link 回填到的订单归属到本人（本条 ③）；② 的订单页找回入口置顶仍按 BR-ATTR-17（任意新订单归属即不置顶），与卡片消失条件是两件事
  - 10_首个完整流程验收用例.md §0.3：「外跳后时长 08 未规定在哪端计算」→ 服务端计算（本条 ①），验收用 CLOCK_NOW 推进服务端时钟
- 来源：01_需求规划.md J1、J5、E19 F-OBS-05；03_前端架构.md §4.5、§5.6；04_数据模型与契约.md §2.3；PRD v2.1 §8.5；PRD修订_双品牌与Agent找货 §3.6.1 第五步；07_功能对照清单.md §3；docs/changes/20261001-拍板第二批.md（TRADE-09）
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）；另 04 §6.4 新增 GET /v1/orders/pending-tracks 与 POST /v1/orders/pending-tracks/{link_id}/dismiss，§3.2 links 增加 track_dismissed_at；10 AC-S1-25 ④ 改为“该 link 回填到的订单归属到 U1 后消失”，§0.3 改为“服务端计算，用 CLOCK_NOW 推进”

**例**：U 的找回因为“领了他人淘礼金”被驳回 → claim_items.reject_reason=OTHER_TLJ，用户看到“下单时可能使用了其他推广者的淘礼金，订单通常归对方”；orders 表中并没有这笔订单。

**例**：U 第一次跳淘宝前看到 JumpTip，之后跳淘宝不再显示；第一次跳京东前仍会显示京东的 JumpTip。

**UI 测试**：不点击就不外跳（03 §4.5）；诊断上传前的弹窗必须逐项列出内容，拒绝时不上传。

**例（待跟单卡）**：外跳 10:00，10:20 该 link 回填到的订单归属到本人 → 卡片消失。外跳 10:00 一直没有订单 → 10:30 起卡片出“未跟单？去找回”入口；超过 72 小时（3 天后 10:00）卡片消失。

**例（多次外跳）**：U 10:00 跳淘宝（L1）、10:05 跳京东（L2）、10:10 再跳淘宝（L3）→ pending-tracks 返回 L3（淘宝）与 L2（京东）两项，L1 不再返回。10:20 U 另一笔淘宝订单（回填到 L1）归属到 U → L3 卡片不消失；L3 回填到的订单归属后才消失。U 关闭 L2 卡片 → POST …/L2/dismiss，之后 L2 项 dismissed=true、客户端不展示。

按 G-05 默认处理，待运营确认。

#### BR-ATTR-22 细则 · 订单唯一键

- 状态：已确认（负责人 2026-10-01，拍板第二批 TECH-09：保留分区，分区表用手写 SQL 迁移，外键指向不分区的 order_keys）；各平台 sub_order_id 的构造为待验证子项（09 核实）
- 默认值：order_keys(platform, sub_order_id) 全局唯一；orders 按 attr_at 月分区；分区表手写 SQL 迁移；外键指向 order_keys
- 决策人：负责人
- 依赖平台能力：各平台 sub_order_id 的构造方式与唯一性（淘宝 trade_id、京东 orderId+skuId 或订单行 id、拼多多 order_sn），09 核实
- 取代：
  - 04_数据模型与契约.md §3.2 orders：「唯一 (app_id, platform, sub_order_id)；按 paid_at 月分区 → order_keys 全局唯一，orders 按 attr_at 月分区」
- 来源：04_数据模型与契约.md §3.2；02_系统架构.md §12.3；PRD v2.1 §3.2 硬规则 3；PRD修订_双品牌与Agent找货 §1.2 硬规则 3；PRD修订_后端功能规划 §4；docs/changes/20261001-拍板第二批.md（TECH-09）
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

**为什么要有单独的 order_keys**：PostgreSQL 分区表上的唯一约束必须包含分区键，所以在 orders 上建不出 (platform, sub_order_id) 唯一键。如果把付款时间加进唯一键，预售单付尾款后 paid_at 会变，同一个子订单可能在两个分区各写一行，upsert 的 ON CONFLICT 拦不住，导致重复计佣。

**为什么不带 app_id**：同一联盟子订单只能属于一个 App。如果唯一键带 app_id，将来多 App 同库、推广位配置出错时，同一笔订单可能以两行入库，被重复计佣，造成资损。

**例**：S1 已作为 app_id=n 写入 order_keys；错误配置让它又被算成 app_id=m → 冲突，不更新，告警。

**预售例**：S3 在 10-15 付定金入库，attr_at=10-15，落在 10 月分区；11-02 付尾款时更新 paid_at，但 attr_at 不变，行不跨分区移动。

**外键例**（拍板第二批 TECH-09）：commission_splits 等需要引用订单的表，外键写 REFERENCES order_keys(order_id)；orders 分区表的建表写在手写 SQL 迁移里，月分区的预建按 ADR-0001 §4.2 执行；数据访问层的类型由已有表结构生成，不反向生成迁移。

#### BR-ATTR-23 细则 · 跟单成功率与跟单率

- 状态：默认假设
- 默认值：每平台样本 ≥20 笔（S1 出门只含 self_buy、agent；share 另补单列）；跟单率每日 10:00 计算前一日；订单不能派生 product_key 且无 lk 的平台，source_match 不计入分子
- 决策人：负责人
- 依赖平台能力：CAP-TB-07、CAP-JD-07、CAP-PDD-07（订单商品 ID 能否派生 product_key、是否返回 shop_id；U-32、U-37）
- 取代：无
- 来源：PRD v2.1 §1 MVP 成功标准、§8.5；01_需求规划.md E05 F-LINK-08；02_系统架构.md §13；开发任务拆解 BT-12
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**例**：京东测试 20 笔（attr.click_code.jd=true），19 笔归属正确且回填到了 link_log，1 笔进了未归因池 → 95%，达标。

**source_match 能否计入分子（按平台）**：BR-ATTR-15 ① exact 只适用于带 lk 的平台（京东、拼多多、美团，且 attr.click_code.&lt;platform>=true）；② product 要求订单 product_key 非空，而 product_key.order_derivable.&lt;platform> 默认 false（BR-PROD-03），为 false 时订单 product_key=null；③ shop 要求订单返回 shop_id，未验证。三者都不可用的平台（当前默认下的淘宝：无点击级透传 U-37，订单派生默认关闭 U-32），source_match 必然为 none，不计入分子，该平台只按「user_id 正确且 buy_type 正确」的笔数 ÷ 总笔数考核；≥95% 目标改由负责人按 S0/S1 实测重定，重定前 S1 出门对该平台按 10 §0.2 条件项处理。CAP-TB-07 / CAP-JD-07 / CAP-PDD-07 实测确认订单商品 ID 可派生同一 product_key（order_derivable 改为 true）或订单返回 shop_id 后，恢复计入 source_match。

**例（淘宝，order_derivable.taobao=false）**：测试 20 笔，20 笔 user_id 与 buy_type 正确，source_match 全为 none → 按 user_id 与 buy_type 正确率计 100%；source_match 不作为该平台 S1 出门条件。

**S1 出门样本**：只含 self_buy、agent 场景（每平台 ≥20 笔，覆盖已上线的端）；share 场景在分享功能（M-公开）上线后另补 ≥20 笔单列统计，不计入 S1 出门。按 G-10 默认处理，已由负责人确认 2026-09-30。

**注意**：跟单率的分母是点击，不是下单，正常值远低于 100%，只看趋势。平台内 AI 截流（06 Q-G4）会拉低跟单率。未回填（unknown）的订单占比高时，分端数据不可信，需要先排查回填。

#### BR-ATTR-24 细则 · 淘礼金订单归属

- 状态：待验证
- 默认值：首版不接入淘礼金（拍板第二批 AI-01 确认：只提示「暂无淘礼金活动」，保留以后接入的位置）；实测前素材一律按 unknown 展示（BR-TEXT-15 判定 3′），给出本 App 转链后的商品卡，不宣称已判为第三方淘礼金；不改写用户剪贴板中的原口令，不提供「复制原口令」（00 D20）。
- 决策人：负责人
- 依赖平台能力：淘宝 06 Q-G3：佣金归属优先级（预售/淘礼金/超级红包/口令）；品牌开放淘礼金经我方转链后是否保留权益；≥30 条口令实测
- 取代：无
- 来源：PRD v2.1 §10.6.1；PRD修订_双品牌与Agent找货 §3.6.1；06_待补信息清单.md Q-G3；07_功能对照清单.md §4 #8；docs/changes/20261001-拍板第二批.md（AI-01）

**实测（后续接入前）**：从 3–5 个发单群收集 ≥30 条淘礼金口令，逐条转链，确定区分字段，结果做成 fixture；无法区分时保留 unknown，不以未知冒充 C 类。

**例**：用户粘贴一条淘礼金口令，尚无已验证的判定字段 → unknown → 出本 App 普通商品卡，说明权益可能无法保留；文案只引用 BR-TEXT-15 判定 3′。后续接入并验证判定能力后，才可按证据使用 A/B/C 分支，不能仅凭未知来源或字段缺失断言 C 类。

#### BR-ATTR-25 细则 · 归因时点 attr_at

- 状态：默认假设
- 默认值：attr_at = COALESCE(deposit_paid_at, paid_at)，首次入库后不变
- 决策人：负责人
- 依赖平台能力：各平台预售订单是否返回付定金时间字段，付定金阶段的订单是否会同步下来（09 核实）
- 取代：
  - 本主题前稿 BR-ATTR-02/07/13/17/18：「统一用 paid_at 比较，预售单 paid_at 可能为空 → 统一用 attr_at」
- 来源：04_数据模型与契约.md §3.2 orders（is_presale、deposit_paid_at、paid_at）、§4.1；05_里程碑与任务拆分.md（双11 预售 10-15、尾款 10-20）
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**为什么取定金时刻**：预售单的推广归属在付定金、生成订单时就已确定；如果取尾款时刻，绑定区间和回填窗口会整体往后偏移，旧绑定释放后付尾款的订单会被判给错误的人，或进未归因池。

**例**：S3 在 2026-10-15T20:00+08:00 付定金（platform_status=DEPOSIT_PAID，paid_at 为空），11-02 付尾款 → attr_at=10-15T20:00；绑定区间、回填窗口、找回窗口都按 10-15 计算；找回页的付款日期填 10-15。分佣快照在 11-02 付尾款时生成，等级与上级取 11-02 的 paid_at（BR-ATTR-01 ⑥、BR-CALC-12），与归属用的 attr_at 不同。

**例**：普通单 attr_at=paid_at。

#### BR-ATTR-26 细则 · 归因流水线黑名单步骤

- 状态：待验证
- 默认值：尾号维度（只对淘宝，比对父订单号末 6 位）验证前只记 manual_review、不作废；渠道维度（relation_id + 半开时间区间）命中未入账订单置 VOID(BLACKLIST)；已入账只进人工复核；存量订单下次同步更新时检查
- 决策人：负责人（已入账订单命中后的扣回：财务）
- 依赖平台能力：淘宝订单出参的 trade_parent_id 是否等于买家可见订单号、末 6 位能否用于识别买家（规划/09 U-42、CAP-TB-07，待实测）；京东、拼多多是否有等价字段（未调研，MVP 不启用）
- 取代：
  - 本主题前稿 BR-ATTR-01 ③：「黑名单（见 BR-RISK）」——BR-RISK 主题未建立，名单内容与命中处理无处可查，在本条补齐
  - BR-ID-38（已废弃，C-18）：「订单首次入库时判定一次、不追溯；原因码 BLACKLIST_HIT；维度 taobao_order_suffix」→ 检查时点按本条（首次入库或 content_hash 变化时）；原因码 reason_code=BLACKLIST，BLACKLIST_HIT 只作流水线事件名；维度名 order_no_suffix（platform=taobao）；名单表用 BR-ID-31 blocklist，不另建 risk_blacklists
- 来源：02_系统架构.md §7.3（黑名单：买家订单号后 6 位、渠道黑名单 → INVALID(reason=BLACKLIST)）；01_需求规划.md E09 F-ORD-10（渠道单持续失效到结束时间）、F-ORD-12、E17 F-RISK-03、F-ADM-18；04_数据模型与契约.md §2.3 BLACKLIST、§4.1 O4 BLACKLIST_HIT；PRD修订_后端功能规划 §2.5 维权与处罚（渠道单持续失效、淘宝号黑名单含存量订单）、§13.2 #12、#21；规划/09 README U-42；docs/changes/20261001-拍板第二批.md §8 ADD-05
- 需同步修改的规划文档：规划/01 F-ORD-12、规划/02 §7.3 归因流水线、规划/04 §2.3 BLACKLIST 行改为引用本条（已同步 2026-09-30，见 README §0.6）

**例**：名单有 dimension=order_no_suffix、platform=taobao、value=`123456`。淘宝子订单父单号 `3301987654123456`、rebate_status=ESTIMATED → 末 6 位 `123456` 命中：
- 尾号维度未启用时（CAP-TB-07 未通过或 attr.blacklist.order_suffix_void_enabled=false）：只写 risk_hits（risk_action=manual_review），ESTIMATED 不变，用户侧无变化。
- 启用后：VOID，reason_code=BLACKLIST，写 risk_hits（risk_action=void_commission），订单详情显示原因与申诉入口。
父单号 `3301987654012345` → 不命中。

**例（渠道单）**：2026-10-10T15:00 导入渠道单 relation_id=R8、end_at 为空 → 名单 start_at=10-10T15:00。attr_at=10-10T14:59:59 的订单不命中；attr_at=10-10T15:00:00 的新订单命中（边界含等号）。之后设 end_at=10-31T00:00 → attr_at=10-31T00:00:00 的订单不再命中。

**例（已入账）**：名单新增后，已 CREDITED 的存量订单 S6 因退款触发同步更新 → 命中，不自动扣回，写 blacklist_hit_after_credit，由风控人工处理；复核结论为扣回时由有权限者 step-up 确认（一人可完成，拍板第二批 §8 ADD-05），按 BR-FUND-01 R8（事件 BLACKLIST_CONFIRMED）写 CLAWBACK；同一次更新中的退款仍按 BR-FUND 正常处理。

**为什么不做全表回扫**：名单命中会让订单作废、用户收益消失；全表回扫一次改动大量历史订单，误加名单的影响面不可控。存量订单随正常同步逐步检查，与后端功能规划“存量订单在下一次同步更新时强制失效”一致。

**为什么尾号维度先只记复核**：订单号末 6 位能否识别买家（CAP-TB-07 / U-42）未验证，未验证能力不得据此处置用户资金；验证通过并由负责人打开 attr.blacklist.order_suffix_void_enabled 后才作废。

按 C-18 默认处理（合并 BR-ID-38），已由负责人确认 2026-09-30；已入账命中后的扣回路径按 C-27 (f) 默认处理，待财务确认。

#### BR-ATTR-27 细则 · 外跳路径与未安装降级

- 状态：待验证
- 默认值：按下表矩阵；每条路径在对应 CAP-*-11 验证通过前为条件项，不进 primary、不对外承诺
- 决策人：负责人（路径与文案涉及订单归属与对外文案）
- 依赖平台能力：CAP-TB-11、CAP-JD-11、CAP-PDD-11（各端已装/未装的拉起与归因保持）；CAP-X-04（鸿蒙唤端归因）
- 取代：
  - BR-TEXT-14 / 01 J1 第 4 步：「未安装淘宝复制口令，提示“口令已复制，打开淘宝即可领券”」→ 未安装时用户打不开淘宝（09 A-27），改为本条未安装降级
  - 本条淘宝行原写（2026-09-30）：「已安装：百川 openByUrl(s.click) → taobao:// → Universal Link / App Link → H5」（s.click 由服务端转链产出）→ 改为客户端百川转链（2026-10-03，链接 API 为邀请制，09 2_TB §2.5）
- 来源：01_需求规划.md E05 F-LINK-06；09 README U-59、A-27；09 CAP-TB-11、CAP-JD-11、CAP-PDD-11、CAP-X-04 降级列；09 2_TB §2.5、5_X §5.5（2026-10-03 淘宝行）
- 需同步修改的规划文档：BR-TEXT-14 降级文案行、09 各 CAP-*-11 结论回填 specs/platform-matrix.csv；03_前端架构.md §4.5 删去「iOS 不做“先检测是否安装再跳”，直接 open(url) 按回调降级」与「全部失败时淘宝走“复制口令 + 提示打开淘宝”，其他平台走内置 ExternalPage 打开 H5」两句，改为「已装检测、路径与兜底按 BR-ATTR-27」（LSApplicationQueriesSchemes 只声明 apps.json 生成的 ≤20 条保留）；04_数据模型与契约.md §6.3 convert 与 open 请求体登记 installed（true / false / unknown，缺省 unknown）
- 与 03 的差异（按 08 为准）：03 §4.5 原规定 iOS 不预检测、失败后才降级，服务端因此拿不到“是否已装”，未装时的按钮文案无法在点击前展示；兜底原为“复制口令 + 提示打开淘宝 / 内置 ExternalPage”，与本条“安装提示 / 系统浏览器”不一致。canOpenURL 只查 apps.json 已声明的 scheme，不读取应用列表，与 BR-ATTR-21 诊断包的检测范围相同

| 平台 | 已安装：primary → fallbacks | 未安装 | 鸿蒙 |
| --- | --- | --- | --- |
| 淘宝（2026-10-03 改为客户端百川转链） | 百川打开指令：有我方推广链接时 openByUrl(我方推广链接)，不传 pid 等分佣参数；否则 openByCode(商品详情, item_id) + AlibcTaokeParams(pid, relationId)，由 SDK 转链 → taobao:// → Universal Link / App Link → H5（后三步只在有我方推广链接时下发，打开的都是该链接） | CAP-TB-11 证实 H5 下单保留归因 → 有我方推广链接时系统浏览器打开该链接（或百川 SDK 的 H5 打开方式，以 CAP-TB-11 选定）；否则按钮“安装淘宝后下单才有返利”，有口令时复制口令 | 百川鸿蒙版指令同左；百川不可用 → 有我方推广链接时 H5，并提示“鸿蒙版可能影响返利跟踪，如未显示订单可申请找回”；没有该链接或 H5 也丢归因 → 按 CAP-TB-11 / CAP-X-04 降级列 |
| 京东 | openApp.jdMobile → 通用链接 → u.jd.com 短链 | 系统浏览器打开 u.jd.com，提示“将通过浏览器打开京东” | scheme 不可用 → 系统浏览器打开 u.jd.com |
| 拼多多 | schema_url → mobile_url | mobile_url | schema 不可用 → mobile_url，提示“将打开拼多多网页版下单” |

- 任一平台在某端全部路径丢归因 → 该端隐藏该平台购买按钮，显示“本设备暂不支持{platform_name}返利”（BR-TEXT-14），其他端不受影响。
- **淘宝行说明（2026-10-03，实现方案，docs/changes/20261003-淘宝转链改客户端百川.md）**：
  - pid、relationId 由服务端按 BR-ATTR-05 构造后写进指令，客户端不改不补。百川 5.x 已取消 adzoneId + appkey 方式，只用 pid（09 2_TB §2.5）。
  - 「我方推广链接」只取联盟基础 API（物料搜索升级版等）在带本次快照 user 的 relation_id、并以该 pid_scene 推广位调用时返回的链接（coupon_share_url 优先，其次 click_url），随 link 登记；不跨用户、不跨推广位复用；实际有效期未核实前按 BR-ATTR-13 ② 的 W_link 判定，过期后只下发 openByCode。
  - 任何 s.click / uland 链接（包括我方推广链接）用 openByUrl 打开时都不传 pid（SDK 不支持二次转链，09 5_X §5.5）；用户粘贴的原链接、口令一律不交给百川打开，也不当作返利链接（BR-PRICE-21），只用于解析出 item_id 后走 openByCode。
  - 口令只能由我方推广链接经 `taobao.tbk.tpwd.create` 生成（权限包「淘宝客【公用】淘口令生成」是否自助申请待核）；拿不到时未安装兜底只显示安装提示、不复制口令。
  - App 外 H5（分享中间页）没有百川，只能打开分享链接自带的我方推广链接或口令；淘宝分享链接如何带上分享者 relation_id 见变更记录待负责人确认事项，确认前本条不改分享规则。
  - 本行全部路径在 CAP-TB-11 验证前按上文 ③ 放行范围执行（生产对外用户只下发已验证路径）；openByCode 按 item_id 打开时联盟券能否领取、新版字符串 item_id 能否被百川识别，一并在 CAP-TB-11 验证。
- 验证通过的路径按 CAP-*-11 结论写入 specs/platform-matrix.csv，由 contracts/apps.json 生成三端配置（F-LINK-06）；表中路径顺序为默认值，以实测结论为准。

**例**：iOS 未装淘宝、CAP-TB-11 尚未给出 H5 结论 → 按钮“安装淘宝后下单才有返利”，点击复制口令；不显示“打开淘宝即可领券”。CAP-TB-11 证实 H5 保留归因后 → 改为系统浏览器打开 H5 推广链接。

**例（installed 上报）**：iOS 客户端 canOpenURL("taobao://") 返回 false → open 请求体 installed=false，X-Platform=ios → 服务端取 (taobao, ios, false) 行；H5 中间页打开 → installed=unknown，服务端下发“已安装”列路径，fallbacks 末尾追加“未安装”列路径。

**例（S1 开发与内测）**：CAP-TB-11 尚未开始 → staging 环境与 agent.whitelist_user_ids 内的内测用户按上表默认矩阵下发，用于跑通 AC-S1-18 等用例并产出 CAP-TB-11 证据；生产对外用户在该路径验证通过前不下发该路径。

按 G-04 默认处理，已由负责人确认 2026-09-30。

#### BR-ATTR-28 细则 · 花卷云侧过滤与 AF-07 双向验证

- 状态：待验证
- 默认值：淘宝填媒体级 mm_a_b，但在 AF-07 证实前淘宝新增推广位仍逐条补填；京东、拼多多逐条填写，条数上限以花卷云后台实际为准；新推广位 pending → active 关卡保留；AF-07 核对时刻 = CAP-*-07 实测 P95 × 2（≥30 分钟），实测前核对截止为付款后 24 小时
- 决策人：负责人
- 依赖平台能力：CAP-TB-05、CAP-JD-05、CAP-PDD-05（09 U-10：花卷云“忽略 PID”实际过滤效果，含淘宝媒体级 mm_a_b 是否覆盖将来的推广位、京东和拼多多条数上限）；CAP-TB-07、CAP-JD-07、CAP-PDD-07（09 U-18：付款到可查询延迟 P95）
- 状态变更：2026-09-30 由 BR-ATTR-03（已确认）拆出，新建为待验证
- 取代：
  - BR-ATTR-03 原第 2–4 段（2026-09-30 前）：「淘宝一条媒体级 mm_a_b 即可覆盖全部推广位；京东、拼多多各最多 100 条；AF-07 付款后 30 分钟内核对」→ 均改为待验证，核对时刻按 CAP-*-07 实测 P95 + 余量
  - 本主题前稿：「淘宝按 mm_a_b_c 逐个填写、AF-07 在 W0 09-30 完成 → 淘宝默认按媒体级 mm_a_b 填写（AF-07 证实前仍逐条补填），AF-07 按平台在放量前完成（最迟 W1）」
  - 2026-09-30 前稿：「AF-07 最迟 W1」→ 时限为该平台 convert.enabled.<platform> 打开前；联盟权限获批晚于 W1 的平台顺延（09 README §7.0：淘宝万能转链等为邀约制、获批日未知）
- 来源：00_总览与决策.md §3.1 D1；05_里程碑与任务拆分.md §5 W0；06_待补信息清单.md Q-H5；参考_花卷云功能查漏底稿 §3；09 README U-10、U-18
- 需同步修改的规划文档：README 规则索引与状态计数；15 §15.1；00 D1「影响」列（同 BR-ATTR-03）

**AF-07 验收步骤**（每个平台分别做）：①测试买家账号在新 App 自购位下单 1 笔，在优券汇下单 1 笔；②付款后到 T_check 时核对（T_check 见规则行；CAP-*-07 未出结果前以付款后 24 小时为截止）：新 App orders 表只有第一笔，花卷云只有第二笔；③截图与订单号归档到 05 的验证证据路径。淘宝的 AF-07 同时用来确认媒体级 mm_a_b 过滤确实生效：另在该媒体下新建 1 个未在花卷云逐条登记的推广位（保持 pending，只用 tools/probe 直接调联盟转链，不经 /v1/links/convert），用它下 1 笔，花卷云不入库才算媒体级覆盖成立；成立后才停止淘宝逐条补填。

**例**：CAP-TB-07 实测 P95=4 分钟 → T_check=max(8, 30)=30 分钟；P95=25 分钟 → T_check=50 分钟。

**为什么 AF-07 放到 W1**：测试买家账号（06 Q-H5）在 W1 才能准备好；W0 只完成配置和截图。W1 是权限已批平台的安排，不是硬截止：联盟权限未批的平台无法真实下单，AF-07 顺延至获批后，期间该平台 convert.enabled.&lt;platform> 保持关闭，不影响其他平台。

**异常**：花卷云忽略配置漏填或不生效时，同一笔订单会在两个系统同时返利，造成资损。在 AF-07 证实之前，三家都靠逐条登记 + pending → active 关卡防漏；淘宝媒体级过滤证实后，淘宝新增推广位才可免逐条补填。某平台 AF-07 不通过 → 该平台不放量，由负责人决定是否改为新开联盟账号（同 BR-ATTR-04），其他平台不受影响。

#### BR-ATTR-29 细则 · 第三方页容器内的平台页面与商品链接

- 状态：待决策（功能对照 Q-02：活动转链上线前，首页活动位能不能直接放淘宝、京东、拼多多的官方活动页；本条按默认 A 写，2026-10-03）
- 默认值：A——活动转链上线前不放，后台保存时拦下指向联盟平台网页域名的外链；第三方页容器里凡是去往联盟平台网页域名的导航都不加载：点到平台商品页时转回本 App 的商品详情（点购买才转链），其他平台页面一律拦下并提示。理由：未转链的平台页面里下单，订单不带用户归因（不在本 App 推广位上，或落进未归因池，BR-ATTR-16），用户拿不到返利也无从找回；与「不得做不带跟单参数的直接唤起」（BR-ATTR-21）是同一原则。备选 B：允许放，页面顶部一直显示「在本页直接下单不计返利」（改变对外说法，须负责人选定后另行回写）
- 决策人：负责人
- 依赖平台能力：—（各平台商品页与推广链接的 URL 形态由 parsing 任务按真实样本整理，不属联盟接口能力；P1 活动转链各平台可用的接口与权限待核，淘宝链接 API 为邀请制，规划/09 2_TB §2.5）
- 取代：
  - 规划/01 §4.2 ExternalPage 行：「联盟活动页、商家页」（MVP 不再用于联盟平台页面）
  - 规划/03 §5.1 ExternalWebView 行：「联盟活动页、商家页、任何第三方 URL」「任意 https」
- 来源：docs/research/20261003-功能对照缺口清单.md（G-02）、docs/research/20261003-功能对照待确认问题.md（Q-02）；docs/changes/20261003-功能对照补缺.md；规划/01 §4.2、F-HOME-09；规划/03 §5.1；规划/04 §9 trade.openUnionActivity；规划/07 §3；BR-ATTR-08、BR-ATTR-12、BR-ATTR-16、BR-ATTR-21、BR-PRICE-21
- 需同步修改的规划文档：规划/01 §4.2 ExternalPage 行与 F-LINK-11；规划/03 §4.3、§5.1；规划/04 §6.6 后台保存校验、§10.1 link_patterns 与两个开关；规划/06「功能对照待确认」Q-02 及其边界；规划/07 联盟活动转链行；规划/10 AC-S1-70；BR-TEXT-14 表 C（已同步 2026-10-03）

**平台链接形态表**（`specs/link-patterns.yaml`，由 parsing 任务维护；本条只定类别和各类别的用途，具体域名与路径模式按真实样本整理、随平台变化更新，不写进本条）：

| category | 含义 | 谁用 |
| --- | --- | --- |
| `union_host` | 联盟平台的网页域名（按注册域匹配，含子域）。MVP 覆盖淘宝 / 天猫、京东、拼多多；其他平台接入时加进同一张表 | ① 后台保存校验；② 运行侧判定哪些导航不在容器里加载 |
| `product` | 平台商品详情页的 URL 形态（主机 + 路径模式） | ②（a）哪些被拦下的导航交服务端识别、转回原生商品详情 |
| `promo` | 推广链接形态（联盟短链、推广落地域名） | 非 https 跳转、外跳与桥方法的规则（另见对应条目），本条不用 |

- 匹配只看主机与路径。客户端用的规则表随 /v1/config 下发并带版本；取用顺序：当前版本 → 上一次成功拉取的版本 → 包内内置快照（构建时由 `specs/link-patterns.yaml` 生成）。内置快照至少含各联盟平台网页的注册域，只按整域判定：拿不到商品页形态时，商品页也按「其他平台页面」拦下。任何情况下都有规则可用，拉取失败不得导致不拦截。
- ① 的校验点：保存或发布时由服务端校验，不能只在后台前端校验。被拒时返回 20001，data.fields 指向该跳转字段，后台提示「联盟平台页面要等活动转链上线后才能配置；商品请改用商品详情跳转」（后台文案，不进用户侧字典）。指向这些平台的商品一律配置为 `{route: "ProductDetail", params}`。
- ② 的细节：判定在导航发起时做，重定向的每一跳都判，命中即取消，不等页面加载。（a）同一个 URL 在一次识别完成前不重复请求；识别请求按 `POST /v1/inputs/parse` 的现有规则签名与限流；识别成功后原生详情页压在容器之上，返回即回到原页面。基本模式没有设备签名、不能调识别接口，商品页同样按（b）拦下并提示；基本模式禁止的只是本 App 的购买接口，管不到第三方网页里的下单，所以不能放行。
- ②（b）的提示（BR-TEXT-14 external_page.union_host_blocked）只给【去搜索】；容器的「在浏览器打开」之类入口对被拦下的地址不可用。被拦下后原页面保持不动。
- ② 不区分这次导航是不是用户点击触发的：转回的是本 App 内的原生页面，不是外跳；外跳仍只在用户点击购买时发生（BR-ATTR-21）。
- 开关：external_page.union_host_block（默认 on）同时管 ① 的保存拒绝与 ② 的阻断，只应在负责人选定备选 B 并补齐页面提示之后关闭，关闭须 step-up 并写审计；客户端从 /v1/config.features 取它，取不到按 on。features.external_page.product_intercept=off 只是停掉（a）的识别回流，商品页改按（b）拦下，不会变成放行。
- 例：公告文章里放了一个品牌官网链接 → 可以保存，App 内用 ExternalPage 打开。运营想在首页 banner 放某平台的大促会场链接 → 保存被拒，提示改用商品详情跳转或等活动转链上线。
- 例：用户在品牌官网页里点了一个指向某平台商品详情页的链接 → 容器取消这次跳转 → 识别成功 → 进入本 App 的商品详情，显示券、券后价与预估返利 → 点【领券购买】经 open 转链外跳，订单归该用户。识别返回 30132 → 提示「该商品暂无法查返利」，仍停在官网页。
- 例：品牌官网页里的「去旗舰店」按钮指向某平台的店铺页，或页面自动重定向到平台会场 → 容器取消这次导航 → 提示「这个页面暂不支持在这里打开」并给【去搜索】，官网页保持不动。规则表拉取失败、只有包内快照时结果相同。

**尚未闭合的边界**（2026-10-03，按评审补；接在功能对照 Q-02 下，登记于 规划/06「功能对照待确认」，负责人确认前不视为已解决）：

- 子框架：第三方页面用内嵌框架（iframe）装进来的平台页面不经过主框架导航，本条的判定拦不到。是否检测并处理，待定。
- 规则表之外的域名：平台新启用的域名、第三方短链的落地域名在补进规则表之前拦不住；靠 parsing 任务按样本更新规则表与埋点 external_page_union_host 的回看来发现。
- 平台上不含购买入口的页面（帮助、协议、客服页等）现在也一并拦下。要不要按白名单放行，待定；放行名单属于对默认 A 的放宽，由负责人决定。
- 拉起平台 App 的非 https 跳转（scheme 等）不在本条，按第三方页容器的导航规则处理（规划/03 §5.1，功能对照 G-21）；默认 A 下同样不得成为没有归因的购买入口。
- 品牌官网等非联盟平台页面里的下单与本 App 的返利无关，不拦截、不提示。

### 4.3 本主题未决问题

1. 【已定（拍板第二批 TRADE-19）：兜底位不用于转链，只作白名单保留位，落在兜底位的订单按 BR-ATTR-08 ② ③ 判定 buy_type】fallback（兜底）推广位的用途没有定义：04 §2.2 写“不下发给用户”，06 Q-C16 却要求申请兜底位。哪些订单会落在兜底位上（服务端内部物料？场景推广位缺失时的替补？）需要负责人明确。在此之前，BR-ATTR-08 规定 fallback 位不用于转链；万一有订单落在兜底位上，按 sc 参数或 fallback 规则判定 buy_type
2. 【已定（拍板第二批 §8 ADD-01，C-05 结案）】用户注销后的归属：F-ACC-10 把注销用户的绑定置为 blocked，released_at 为空，relation_id 永远被占用。按 BR-ID-20 处理：注销绑定置 blocked(deletion)，注销 done_at 满 180 天后由每日 04:00 任务置 released，并冷却 bind.rebind_cooldown_days（默认 30 天，ADD-01）；冷却结束前付款、带该 relation_id 的订单按 BR-ATTR-07 区间归到墓碑用户、佣金归平台（BR-ID-28），不得被找回认领（找回返回 30204）；冷却结束后同一淘宝账号可被新用户备案
3. 超过找回窗口仍未认领的未归因订单，佣金的会计处理（平台收入确认时点）需要财务确认；BR-FUND 目前没有对应条目。默认：保持 UNATTRIBUTED，联盟回款核销时整笔计平台留存（BR-ATTR-16）
4. 美团（P1，D15）sid 的格式和长度、是否也使用 attr_code，以及 App 归属键（推广位还是 sid 前缀）尚未定义
5. 淘宝订单接口回传的 item_id 与转链时的 item_id 是否同一口径（加密 ID 差异），会影响 BR-ATTR-15 回填和 BR-ATTR-18 证据的命中率，需要在 09 中实测
6. 用户从本 App 跳转后，在淘宝内经千问等 AI 助手下单，归因是否保留（06 Q-G4/V8），影响找回驳回原因和跟单率口径
7. 各平台付定金阶段的预售订单是否同步、是否返回定金时间（BR-ATTR-25），如果不返回，预售单的归因时点需要改用其他字段
8. 【已由 C-27 处理：① → BR-FUND-01 R3a；② → R14；VOID 且 user_id 为空的找回/改派 → R3b；R3 取值时点随 C-06】BR-FUND-01 的 rebate_status 迁移表缺两项，需在 BR-FUND-01 补齐（本主题按下述结果书写）：① 未归因订单经后续同步按参数归属（user_basis=param）时 UNATTRIBUTED → ESTIMATED / WAITING（R3 只列了 CLAIM_APPROVED、ADMIN_REASSIGN）；② 已归属订单改归属（前稿 O12）的红冲与重记，需要一个 rebate_status 不变的自迁移，承载同事务内的分录变更。另外 BR-FUND-01 R3 写“比例与用户关系取批准时刻”，与 BR-CALC-12（paid_at）不一致，按 C-06 应随之修订
9. 【已由 C-27 (f) 处理：复核确认后由有权限者 step-up 确认（一人可完成，拍板第二批 §8 ADD-05），按 BR-FUND-01 R8（BLACKLIST_CONFIRMED）写 CLAWBACK；与 BR-ID-38 的重复维护已由 C-18 处理（并入 BR-ATTR-26）】已入账（rebate_status=CREDITED）订单命中黑名单（BR-ATTR-26）时是否扣回、按什么流水类型扣回，BR-FUND-01 R8 未列“黑名单”事件；在财务决定前只进人工复核
10. 活动转链上线前，首页活动位能不能直接放淘宝、京东、拼多多的官方活动页（功能对照 Q-02，2026-10-03）：BR-ATTR-29 按默认 A 写（不放、后台保存时拦截；第三方页容器里去往联盟平台网页域名的导航都不加载，商品页转回本 App 商品详情，其他平台页面拦下并提示），待负责人确认；子框架、规则表之外的域名、平台的非购买页面是否放行等边界尚未闭合（细则「尚未闭合的边界」）；P1 活动转链各平台可用的接口与权限待核
11. 分享链接能不能在本 App 内直接打开（功能对照 Q-03，2026-10-03）：BR-ATTR-05 细则按默认 A 写（做 LinkLanding 与分享中间页的【在 App 中打开】），待负责人确认

---
