# 08 业务规则 · 9. 订阅提醒（Watch，P1）（BR-WATCH）

返回 [README](README.md)（使用规则、术语表、规则索引）

## 9. 订阅提醒（Watch，P1）（BR-WATCH）

本节规定：P1 降价提醒全链路规则，其余提醒只列目标。共 29 条（已确认 5、默认假设 17、待决策 1、待验证 6）。

### 9.1 规则一览

| 编号 | 规则 | 状态 | 影响面 |
| --- | --- | --- | --- |
| BR-WATCH-01 | **提醒首版交付目标**<br>P1 的 S3 阶段交付「一个商品的降价提醒」完整用户流程：创建、查询、触发、通知、点击处理。淘宝、京东、拼多多各自独立验收、独立放量，任何一家能力验证未通过都不阻塞其他两家。MVP 不对用户开放任何提醒入口（降价提醒属 P1）。S3 的具体范围（只做目标价模式、其他类型的分期）见 BR-WATCH-26；按平台开关放量与关停见 BR-WATCH-27；MVP 预埋见 BR-WATCH-19。 | 已确认 | 规划/00 §4 范围裁决表；规划/05 阶段 S3 验收 |
| BR-WATCH-02 | **监控对象与商品粒度**<br>一个 price_drop 提醒必须绑定且只绑定一个 (app_id, platform, product_key)；不得跨 app_id、跨平台、跨店铺，不得把不同 product_key 合并监控；判断「同一商品」一律调用 isSameProduct（BR-PROD-01），product_key 入库前先经 resolveProductKey（BR-PROD-02）。S3 不支持指定 SKU（规格/颜色/容量/件数）监控：比较使用联盟接口返回的商品级券后价；确认卡与提醒文案必须写明「按联盟返回的商品券后价监控，不区分规格；多规格商品可能是最低规格价，以下单页所选规格为准」。唯一范围：同一 app_id、user、platform、product_key 下，status ∈ {active, paused, unavailable} 的 price_drop 最多 1 条，由部分唯一索引保证。重复创建返回 30803（HTTP 409，data.reason=watch_duplicate，13 §13.11），响应体带已有 data.watch_id，客户端引导修改目标价。已有同商品 expired 记录且 now − expires_at ≤ watch.renew_grace_days 时，返回 30804（HTTP 409，data.reason=watch_expired_renewable）带该 data.watch_id 并引导续期；超过宽限期可新建。创建在事务内对 user 行加锁（SELECT … FOR UPDATE）后校验唯一性与 watch.max_per_user。product_key 的生成与稳定性见 BR-PROD-02、BR-PROD-03，取联盟原串见 BR-PROD-05。product_key 映射到联盟当前商品 ID 失败时，不得用标题+店铺检索结果自动替换监控对象；watch 置 unavailable（unavailable_reason=item_unresolved），由用户在「我的提醒」重新选择商品（取消后新建）。 | 待验证 | watch.app_id/platform/product_key/sku_key/unavailable_reason；watch 部分唯一索引 (app_id, user_id, platform, product_key) WHERE status IN (active,paused,unavailable) AND type=price_drop；tracked_item 唯一键 (app_id, platform, product_key, sku_key)（BR-PROD-08 ④）；POST /v1/watches（409：30803 watch_duplicate / 30804 watch_expired_renewable）；watch_confirm 卡片文案；规划/09 能力验证表；验收用例 规划/10 AC-S3-30、AC-S3-26 |
| BR-WATCH-03 | **监控价格口径**<br>price_drop 比较的价格必须是按 BR-PRICE-01 由联盟返回数据算出的商品券后价 final_price_fen（整数，单位分，购买 1 件、默认 SKU，= price_fen − coupon_fen；平台自带券后价字段只有进入 BR-PRICE-01 白名单后才可直接采用），且只取自该平台提醒口径接口（watch.query_api_kind.&lt;platform>）不带用户参数的调用（BR-WATCH-06）。本条是提醒监控价格口径的唯一细则，BR-PRICE-19 只指向本条。不得使用预估返后价 est_net_price_fen（券后价 − 预估返利）、素材参考价或券前价 price_fen 作为触发价；不含运费；不含 88VIP/PLUS 会员价、跨店满减、淘金币、淘礼金、平台补贴类不在联盟券后价字段中的优惠、多件优惠。券后价的计算、选券与字段来源以 BR-PRICE-01、BR-PRICE-03 为准，本规则只规定提醒使用其中的 final_price_fen 以及取价接口。预估返利只作为通知与落地页的附加展示，不参与判定。 | 待验证 | price_observation.final_price_fen；watch.target_price_fen 比较逻辑；watch_confirm 卡片「价格口径说明」；提醒文案、客服话术「为什么下单页价格不一样」；规划/09 |
| BR-WATCH-04 | **目标价输入与比较符**<br>目标价 target_price_fen 为整数分：用户输入以元为单位，服务端只能用 packages/domain.parseYuanToFen()（BR-PRICE-01）转换；解析失败（多于 2 位小数如「40.500」「39.999」、非数字、空串、负数）或 target_price_fen &lt; 1 时返回 20001 参数错误（data.fields=[target_price]，data.reason=watch_target_invalid，不另开码，提示「请输入 0.01 以上、最多两位小数的金额」），不做舍入。取值范围 1 ≤ target_price_fen &lt; POST 时服务端实时券后价（BR-WATCH-07）。触发比较符为 ≤：当 final_price_fen ≤ target_price_fen 时条件满足，比较一律用整数分，不得用浮点。Agent 把「低于 X / X 以下 / 不超过 X / X 以内 / 降到 X」统一解析为 target_price_fen = X×100、比较符 ≤，确认卡必须原样显示「券后价 ≤ ¥X 时提醒」（¥X 为 target_price_fen 按 BR-TEXT-10 格式化，如 ¥40、¥40.5）。实时券后价已 ≤ 目标价时必须拒绝创建，返回 30801（data.reason=watch_target_already_met），提示「当前已达到目标价，可直接购买或调低目标价」。错误码为 规划/04 §7 的 5 位数字码，本主题用 20001 与码段 308 提醒的 30801–30806（码表见 13 §13.11，由负责当前接口任务的代理分配），reason 保留为 data.reason 字段。 | 已确认 | watch.target_price_fen；POST /v1/watches 参数校验与错误码；create_watch 工具 schema；watch_confirm 卡片、商品卡设置面板；Agent 评测集提醒类用例；验收用例 规划/10 AC-S3-01、AC-S3-23 |
| BR-WATCH-05 | **观测与价格变更历史分离**<br>必须分开存两类数据，两类数据都以 app_id 为首键、互不跨 app_id（BR-PROD-01、BR-PROD-08 ④）：(1) 观测 price_observation——每次为提醒发起的联盟查询都追加 1 行（成功与失败都写；因配额推迟而未调用接口的不写，BR-WATCH-09），是触发判定、连续确认、数据新鲜度判断的唯一依据；(2) 价格变更历史 price_snapshot——同一 (app_id, product_key, source_kind) 的 (price_fen, coupon_fen, final_price_fen, in_stock) 与该键最新一行不同才插入新行，相同则更新最新行的 last_observed_at 与 observation_count（距上次更新 &lt; price_snapshot.touch_min_interval_minutes 时两者都不更新，observation_count 表示有效触达次数）；失败查询不得写入 price_snapshot。写 price_snapshot 时对 (app_id, product_key, source_kind) 取事务级 advisory lock，再读最新行、比较、插入或更新。判定器不得读取 price_snapshot 做触发判断；「数据是否过期」必须用 tracked_item.last_ok_at（= 最近一次成功观测时间）判断。 | 默认假设 | 新表 price_observation；price_snapshot 字段（first_observed_at、last_observed_at、observation_count、source_kind）；tracked_item 最近观测字段；判定器 WT-06；规划/04 §3.2 表清单；存储容量估算 规划/02 §15 |
| BR-WATCH-06 | **两次确认触发判定**<br>每个平台由配置 watch.query_api_kind.&lt;platform> 指定唯一一个提醒口径接口（拼多多另固定 goods_sign 计划 watch.pdd.goods_sign_plan）；source ∈ {watch_create, watch_update, watch_fetch, watch_confirm, watch_recheck} 的查询都必须调用该接口、使用查询专用推广位（pid_scene=query，BR-PROD-07）、不带用户参数（批量接口传单个商品也可），才送入判定器；用其他接口得到的结果（含 click_quote、MVP 钩子）只写 price_observation 并如实记录 api_kind，不送判定器。只有 armed=true，或 disarmed 且本次价格满足 new_low 阈值（BR-WATCH-12）时，「成功且满足」才进入 pending 并安排确认查询；其他情况只记观测，不改 confirm_state，不安排确认查询。事件必须由两次成功观测确认：两次都满足条件（target_hit：final_price_fen ≤ target_price_fen；new_low：≤ new_low 阈值）且 in_stock ≠ false，两次 observed_at 间隔 ≥ watch.confirm_min_gap_minutes（10），两次之间没有「成功但不满足条件」的观测，第二次在第一次后 watch.confirm_window_hours（6）内。首次满足后在 +watch.confirm_delay_minutes（15）安排确认查询（source=watch_confirm），不得等下一个常规周期；确认查询失败按 watch.confirm_retry_minutes（15、30、60，相对上一次尝试）重试，截止 pending_at + confirm_window_hours；确认查询与重试占用「确认查询与复核」优先级（BR-WATCH-08）。「满足」指都满足条件，不要求价格完全相同。pending 过期在处理下一次观测时惰性判断，不另设扫描任务。判定为纯规则代码，不得调用模型；同一 watch 的判定串行执行（BR-WATCH-11）。 | 待验证 | watch.confirm_state/pending_obs_id/pending_at；调度器确认查询优先级与重试；判定器 WT-06；配置 watch.query_api_kind.&lt;platform>、watch.pdd.goods_sign_plan、watch.confirm_\*；验收用例 规划/10 AC-S3-01、AC-S3-13、AC-S3-03、AC-S3-05、AC-S3-14 |
| BR-WATCH-07 | **检查频率、创建报价与延迟说明**<br>每个 tracked_item 按平台和层级设定常规查询间隔 watch.tier.&lt;platform>.&lt;hot\|default\|cold>.interval_minutes（初值三家相同：120 / 360 / 1440；拼多多、京东以 09 CAP-PDD-13/JD-13 实测为准）；大促模式开启时间隔 ÷ watch.promo_speedup（可配 2–4），任何层级最短 watch.min_interval_minutes（60）。层级每日 04:00（+08:00）重算；热、冷层只统计 source_kind=watch 的 price_snapshot 新行；tracked_item 首次创建时为默认层，created_at 满 14 天后才可能进入冷层。POST /v1/watches（及续期、改目标价）一律在服务端用提醒口径接口重新实时查询（不用卡片或面板上的报价），source=watch_create / watch_update，写 price_observation 并更新 tracked_item 最近观测缓存；查询失败拒绝操作，返回 30805（data.reason=watch_quote_unavailable），提示「暂时无法获取价格，请稍后再试」。tracked_item 新建，或 subscriber_count 从 0 变为 ≥ 1 时，next_fetch_at = now + 当前层级间隔。确认卡、设置面板、「我的提醒」页、提醒附注必须按该商品当前平台与层级显示「约每 X 小时检查一次」（X = ceil(间隔分钟/60)；1440 分钟显示「约每天」），确认卡与面板还必须显示延迟说明「降价后通常 X 小时内通知；22:00–08:00 的提醒次日 08:00 推送；价格以下单页为准」。now − tracked_item.last_observed_at > 1.5 × 当前层级间隔时，「我的提醒」页显示「检查可能延迟」。 | 待验证 | tracked_item.tier/next_fetch_at/created_at；配置 watch.tier.&lt;platform>.\*.interval_minutes、watch.promo_mode、watch.promo_speedup、watch.min_interval_minutes；POST /v1/watches 报价与 30805 watch_quote_unavailable；watch_confirm 卡片、设置面板、我的提醒页、提醒附注文案；客服话术「为什么没及时提醒」；验收用例 规划/10 AC-S3-24 |
| BR-WATCH-08 | **跨用户去重、调度与配额**<br>若 09 CAP-TB-13/JD-13/PDD-13 验证某平台跨用户共享查价成立（不带用户参数的券后价与用户个性化价差可忽略），该平台同一 (app_id, platform, product_key, sku_key) 只能有 1 个 tracked_item，只按它查询一次，结果供全部订阅该商品的提醒共用；不成立的平台按 09 降级列按用户查价，并下调该平台 watch.max_per_user。subscriber_count 统计 status ∈ {active, unavailable} 的提醒：watch 状态迁移时在同一事务内按进出该集合做 ±1，每天 04:00 分层重算时按实际数重新覆盖；为 0 时 next_fetch_at 置 null，停止调度。调度必须用 PG next_fetch_at 索引 + BullMQ worker 批量拉取，不得为每个商品建定时任务；有批量接口的平台必须用批量接口。提醒查询使用独立配额桶（默认联盟日配额的 5%，watch.quota_share_bp=500），优先级从高到低：用户实时操作（在线）> 确认查询与发送前复核 > 热层 > 默认层 > 冷层 > 上新与精选；提醒类查询不得挤占在线配额。配额不足时依次推迟冷层、默认层的 next_fetch_at（不调用接口、不写观测），并告警；确认查询与复核不足时只能推迟，不得跳过复核直接发送。 | 待验证 | tracked_item（subscriber_count、tier、next_fetch_at、last_ok_at）；union 网关配额桶；规划/02 §6.2 治理层配额；规划/09 CAP-TB-13 通过标准 (c)；告警规则；压测 WT-14 |
| BR-WATCH-09 | **查询失败、缺失价格与异常降价**<br>下列任一情况都是失败观测：超时（timeout）、接口错误或无法归类的错误码（error）、平台返回限流（rate_limited）、按 BR-PRICE-01 判为数据异常（price_fen 缺失或 ≤ 0、coupon_fen &lt; 0、coupon_fen ≥ price_fen 即 final_price_fen ≤ 0，记 invalid，同时按 BR-PRICE-01 记 PRICE_ANOMALY）。因我方配额不足而推迟的调度不调用接口、不写 price_observation、不算失败观测（只计入配额监控）。失败观测不得产生任何事件，不得计入两次确认，不得清除 pending，不得写入 price_snapshot；缺失价格不得按 0 分或上次价格填补。平台明确返回「商品不存在/已下架」错误码时记为 fetch_status=not_found、in_stock=false，属于成功观测但不满足 price_drop 条件。unavailable 由每 watch.unavailable_scan_minutes（15）一次的扫描任务判断：watch.status=active，自 tracked_item.last_ok_at 以来失败观测 ≥ watch.unavailable_min_failures（2）次，且 now − coalesce(last_ok_at, watch.created_at) ≥ max(watch.unavailable_after_hours（24）, 2 × 该商品当前层级间隔) 时，置 unavailable（unavailable_reason=fetch_failed），不发任何提醒；之后首次成功观测时自动恢复 active 并清除 pending。异常降价：上一次成功观测 final_price_fen 为 p0、本次为 p1，(p0 − p1) × 10000 ≥ p0 × watch.suspect_drop_bp（7000）时本次观测标记 suspect_drop；参与两次确认的观测任一带 suspect_drop，事件即带 suspect_drop=true，按 BR-WATCH-13 每个通道投递前都必须另发一次实时复核。 | 默认假设 | price_observation.fetch_status/suspect_drop；tracked_item.consecutive_fail_count/first_fail_at/last_ok_at；watch.status=unavailable 及 unavailable_reason；unavailable 扫描任务；我的提醒页状态文案；监控指标 抓取失败率；验收用例 规划/10 AC-S3-06、AC-S3-08、AC-S3-07、AC-S3-09 |
| BR-WATCH-10 | **提醒生命周期**<br>watch.status 取值必须为 active / paused / unavailable / expired / cancelled 五种。创建只发生在用户确认之后（BR-WATCH-18），创建即 active，armed=true，episode_seq=1，expires_at = 创建时刻 + watch.price_drop.ttl_days（60 天）。状态迁移只允许下表所列；每次迁移写 watch_status_log（from、to、actor=user/system/agent_confirmed、reason、at）。发送任何提醒前必须检查 watch 仍为 active 且 condition_version 未变化，否则该事件通道置 suppressed（watch_inactive / condition_changed）。计入每用户上限的状态为 active、paused、unavailable。续期与改目标价必须按 BR-WATCH-07 服务端实时报价，报价失败返回 30805（data.reason=watch_quote_unavailable）且不改动；新目标价须满足 BR-WATCH-04 取值范围。账号提交注销时，全部非终态 watch 置 paused（actor=system，reason=account_closing），不再查询或发送；冷静期内撤销注销时保持 paused，由用户自行恢复；冷静期结束随 F-ACC-10 删除（BR-WATCH-23）。 | 默认假设 | watch.status/condition_version/expires_at/cancelled_at/baseline_final_price_fen/baseline_observed_at；watch_status_log 新表；PATCH /v1/watches/{id}（pause/resume/renew/target）、DELETE /v1/watches/{id}；我的提醒页；retention.purge 任务；F-ACC-10 注销流程；隐私政策；验收用例 规划/10 AC-S3-20、AC-S3-21 |
| BR-WATCH-11 | **触发回合、串行与幂等**<br>每个 watch 在同一 condition_version 下按「回合」触发：创建、改目标价、从 expired 续期时 armed=true、episode_seq=1。两次确认满足 target 条件且 armed 时产生 1 个 target_hit 事件，事件产生即置 disarmed——无论该事件最终 sent 还是 suppressed（任何原因），被抑制的回合不在冷却结束后补发；唯一例外：事件所有通道都因 recheck_failed 或 platform_disabled 被抑制时，判定器把 watch 恢复 armed 并 episode_seq +1。其他情况只有 disarmed→armed 迁移（出现一次「成功但不满足条件」的观测）才使 episode_seq +1；已 armed 时再出现不满足的观测不改变 episode_seq。armed 且确认满足 target 时只生成 target_hit，不同时生成 new_low。dedupe_key：target_hit = {watch_id}:{condition_version}:{episode_seq}:target_hit（不含价格）；new_low = {watch_id}:{condition_version}:new_low:{after_price_fen}；唯一索引冲突视为成功无操作。同一 watch 的判定必须串行：在同一事务内对 watch 行 SELECT … FOR UPDATE，然后读写 confirm_state、armed、episode_seq 与事件表。每个事件每个通道最多 1 条 notification，唯一键 (watch_event_id, channel)；notification 发送状态只能经条件更新 pending→sent 或 pending→suppressed 一次；合并推送的对应关系见 BR-WATCH-15（push_digest）。事件与业务写入在同一事务内写 outbox（规划/02 §11）。重复发送的防护由我方 notification / push_digest 条件更新保证；各推送通道能否按业务 message_id 去重待核实，核实前推送重试只在 send 调用明确返回失败时进行，超时等结果不明时不重试、记 unknown 并告警。 | 默认假设 | watch.armed/episode_seq；watch_event.dedupe_key（唯一索引）、kind、before_price_fen、after_price_fen、status、suppress_reason、suspect_drop；notification 唯一键 (watch_event_id, channel)、delivered_price_fen；判定事务（SELECT … FOR UPDATE）；outbox 事件 watch.triggered；属性测试：抖动不重复提醒、并发判定不重复；验收用例 规划/10 AC-S3-13、AC-S3-11、AC-S3-12 |
| BR-WATCH-12 | **冷却与新低突破**<br>「一次提醒 sent」以事件的第一个 sent 通道为准：last_notified_at = 该通道发送时间，冷却 watch.cooldown_hours（24 小时）从这一刻起算；last_notified_price_fen = 该通道 notification.delivered_price_fen；min_notified_price_fen = 本 condition_version 下所有 sent 通道 delivered_price_fen 的最小值（之后其他通道再发送不改冷却起点，但参与取最小值）。站内信已写入、推送被频控或免打扰抑制时，事件仍算 sent。冷却期内新产生的 target_hit 必须置 suppressed(cooldown)。new_low：watch disarmed（不论是否在冷却期）且 min_notified_price_fen 非空时，两次确认观测都 ≤ 基准价 − max(watch.new_low_min_drop_fen（100）, floor(基准价 × watch.new_low_min_drop_bp（300）/ 10000)) 时生成 new_low，基准价 = min(min_notified_price_fen, 本 condition_version 下 status=pending 事件的 after_price_fen)；min_notified_price_fen 为空时不生成 new_low。new_low 不受回合与冷却限制，sent 后同样更新 last_notified_at、last_notified_price_fen、min_notified_price_fen，冷却重新计 24 小时；冷却内可再次触发 new_low，只受 BR-WATCH-15 每日推送上限约束。改目标价或从 expired 续期时，冷却与 last/min_notified 重置。 | 默认假设 | watch.last_notified_at/last_notified_price_fen/min_notified_price_fen；notification.delivered_price_fen；配置 watch.cooldown_hours、watch.new_low_min_drop_fen、watch.new_low_min_drop_bp；判定器；验收用例 规划/10 AC-S3-13、AC-S3-11、AC-S3-15 |
| BR-WATCH-13 | **发送前复核**<br>每个通道（站内信写入、推送发送）投递前，若该商品最近一次 source ∈ {watch_fetch, watch_confirm, watch_recheck} 的成功观测距当前 > watch.recheck_max_age_minutes（30 分钟），或事件带 suspect_drop（不论最近观测多新），必须实时查询一次（source=watch_recheck）。复核必须使用该平台提醒口径接口（与常规查询同 api_kind、不带用户参数、拼多多同一 goods_sign 计划，BR-WATCH-06）；click_quote 只用于误报统计，不参与判定、新鲜度与复核。复核成功且仍满足事件条件 → 以复核价作为该通道 notification.delivered_price_fen 投递（watch_event.after_price_fen 保持为确认价，不改）；复核成功但不满足 → 该通道 suppressed(stale_alert_suppressed)，复核结果作为普通观测送回判定器；复核失败 → 在 watch.recheck_retry_minutes（+10、+30 分钟）重试，从该通道计划投递时刻起 watch.recheck_give_up_minutes（120 分钟）仍失败则 suppressed(recheck_failed)。计划投递时刻 = 即时投递时为事件产生时刻，免打扰或合并延后时为实际计划发出时刻（如 08:00）。任何情况下不得在未满足新鲜度要求时投递。 | 默认假设 | 通知服务 WT-07/WT-08；watch_event.status/suppress_reason；notification.delivered_price_fen；price_observation source=watch_recheck；监控指标 抑制率；验收用例 规划/10 AC-S3-01、AC-S3-16、AC-S3-18、AC-S3-17 |
| BR-WATCH-14 | **提醒内容与措辞**<br>提醒必须包含：商品短标题、现{price_label}（该通道 delivered_price_fen；price_label 按 BR-PRICE-04：淘宝/京东「券后价」，拼多多「拼单券后价」，无券时「售价」/「拼单价」；标签定义只在 BR-PRICE-04 维护）、用户目标价、被比较价格及其观测日期、预估返利、取价时间、购买按钮，以及固定附注「约每 X 小时检查一次，价格以下单页为准」。被比较价格：target_hit 用 baseline_final_price_fen（创建/改目标价/续期时的实时价）写作「你 MM-DD 设置提醒时为 ¥X」；new_low 用 last_notified_price_fen 写作「上次提醒价 ¥X（MM-DD）」；不得称「原价」，不得省略日期。短标题（模板变量 watch_short_title，与 BR-TEXT-09 交易通知的 title_short 不是同一变量）= 联盟商品标题先按 BR-TEXT-20 去平台名前缀与「官方」，再去掉【】及其中内容，按 Unicode 扩展字素簇取前 watch.short_title_max_chars（20）个，超出加「…」，不超出不加；推送正文超过厂商上限时优先截短标题，金额与目标价完整保留。金额一律用 BR-TEXT-10 的服务端格式化函数（去末尾 0，如 3900 → ¥39、3780 → ¥37.8），日期按 BR-TEXT-11 纯日期规则（同年 MM-DD、跨年 YYYY-MM-DD，不用相对词）。禁用词以 BR-PRICE-18 为准（与 BR-TEXT-13 的合并由这两条维护，本条不另立词表）；本模板的固定文字另外不得出现「最低」「史低」「底价」「全网」「新低」（只约束本模板，不扩大全局词表）；推送标题与首句按 BR-TEXT-20 校验。预估返利取发送时刻的计算结果，口径（含淘宝比价降佣时显示区间或保守值）见 BR-PRICE / BR-CALC，区间格式按 BR-TEXT-10，用词「预估返」按 BR-TEXT-01。 | 默认假设 | notify_templates watch.price_drop.v1；watch.baseline_final_price_fen/baseline_observed_at；禁用词表（BR-PRICE-18）与模板保存校验；BR-TEXT-10 金额格式化函数、BR-TEXT-11 日期格式化、BR-TEXT-20 标题清洗函数；验收用例 规划/10 AC-S3-29 |
| BR-WATCH-15 | **频控、免打扰、合并与通道**<br>降价提醒属「订阅」类通知。站内信必须总是写入（经 BR-WATCH-13 复核通过的）；App 推送仅在用户开启系统推送权限且未关闭「订阅」类时发送（否则该通道 suppressed(push_disabled)）；不得发短信；微信订阅消息为 P1 后续通道。每用户每自然日订阅类推送上限 notify.subscription.daily_push_cap（5）条，按推送实际发出时刻所在的 +08:00 自然日计数，超出该通道 suppressed(daily_push_cap)、只写站内信。合并：用户在 watch.merge_window_minutes（10 分钟）内没有已发出的订阅类推送时，第一条推送立即发送；此后 10 分钟内产生的事件在窗口结束时合并为 1 条摘要推送，摘要计 1 条。免打扰时段为 [22:00, 08:00)（+08:00，notify.quiet_hours）：时段内产生的事件只写站内信，推送在其后第一个 08:00:00 合并为 1 条（推送前按 BR-WATCH-13 复核，全部失效则不推送）。时区一律用 +08:00，不按设备时区。每次推送（单条或合并）新建 1 条 push_digest（id 即推送服务 message_id），用 push_digest_item(push_digest_id, notification_id) 关联各事件的 push notification；摘要发送成功时被合并的 notification 一并条件更新为 sent 并记录 push_digest_id；摘要中复核失效的条目置 suppressed(stale_alert_suppressed)。只有 1 个事件时也走 push_digest，模板用单条模板。 | 已确认 | notification.category；push_digest、push_digest_item 新表；GET/PUT /v1/me/notification-settings；通知服务频控与合并；配置 notify.subscription.daily_push_cap、watch.merge_window_minutes、notify.quiet_hours；MVP 已有 F-MSG-04 行为（订阅类也进免打扰）；验收用例 规划/10 AC-S3-01、AC-S3-18 |
| BR-WATCH-16 | **点击提醒后的展示**<br>提醒发送时必须为每个商品登记 link_id（scene=watch_alert，buy_type=self；pid_scene 由 BR-ATTR-08 按 scene 推导，watch_alert → self_buy）；点击单条提醒进入商品落地页，不得直接外跳；点击合并摘要推送进入「我的提醒」页并高亮本次包含的商品，点某条商品再进入落地页。落地页必须调用只取报价、不转链的接口 GET /v1/links/{link_id}/quote（用提醒口径接口、不带用户参数，写 price_observation source=click_quote，不写 link_logs 打开记录、不消耗转链配额、不返回 jump）；用户点击购买时才调用 POST /v1/links/{link_id}/open 转链，price_changed 的阈值、弹窗与 new_link_id 按 BR-PRICE-13 处理（落地页已按同一价格确认过的，不再重复弹窗，见细则）。notified_price = 用户所点通道的 notification.delivered_price_fen。展示按下表自上而下取第一个命中的行。落地页不得改变 watch 状态（提醒继续有效），并提供「修改目标价」「取消提醒」入口。 | 默认假设 | 规划/04 §2.2 scene 枚举（新增 watch_alert）；规划/04 §6.3 新增 GET /v1/links/{link_id}/quote；links / link_logs.scene；POST /v1/links/{link_id}/open；三端提醒落地页与我的提醒页高亮（WT-11）；客服话术「提醒的价格买不到」；BR-ATTR-08 scene→pid_scene 映射（补 watch_alert 行）；验收用例 规划/10 AC-S3-30、AC-S3-33 |
| BR-WATCH-17 | **数量上限与可调配置**<br>每用户处于 active、paused、unavailable 的提醒合计不得超过 watch.max_per_user（20），超出的创建或续期请求必须返回 30802（data.reason=watch_limit_exceeded）并提示先删除或等待到期；每用户每商品 price_drop 最多 1 个（BR-WATCH-02）；校验在对 user 行加锁的事务内进行。本主题所有阈值（频率、冷却、确认、复核、异常降价、上限、有效期、频控、保留期、告警）必须作为配置项读取，不得写死在代码中；配置修改走 规划/04 §10 配置键流程并记审计。 | 默认假设 | 规划/04 §10 配置键；POST /v1/watches、续期校验；我的提醒页上限提示；验收用例 规划/10 AC-S3-25 |
| BR-WATCH-18 | **创建须用户确认（Agent 与商品卡）**<br>Agent 调用 create_watch 只能生成 watch_confirm 确认卡，不得写库；用户点击确认卡「确认」后由客户端调用 POST /v1/watches（Idempotency-Key = 确认卡 card_id），重复点击只创建 1 个。商品卡「降价提醒」设置面板是非 Agent 的确认界面，面板提交即用户确认；客户端打开面板时生成 UUID 作为 Idempotency-Key，重复提交只创建 1 条。确认卡与设置面板必须展示同一组必示字段：平台、商品标题、价格口径说明（BR-WATCH-02、03）、比较条件「券后价 ≤ ¥X」（格式见 BR-WATCH-04）、当前券后价与取价时间、检查频率与延迟说明（BR-WATCH-07）、通道、有效期截止日。Agent 不得静默创建、修改、暂停、取消提醒；修改与取消同样先出确认卡。Agent 可直接调用 list_watches 读取本人提醒。模型只负责把用户文本转为结构化参数，不得参与查询、判定、价格计算。确认卡有效期 watch.confirm_card_ttl_minutes（30 分钟），过期后点确认返回卡片过期并请用户重新发起；卡片内有效时确认仍以 POST 时服务端实时报价为准（BR-WATCH-07）。AI 权限总则见 BR-AI。 | 默认假设 | Agent 工具 create_watch / list_watches / update_watch / cancel_watch schema；watch_confirm 卡片 schema（规划/04 §8.3）；商品卡设置面板；POST /v1/watches Idempotency-Key；Agent 评测集 ≥80 条提醒类用例；验收用例 规划/10 AC-S3-27 |
| BR-WATCH-19 | **MVP 预埋范围**<br>MVP 只预埋三项，均不对用户展示提醒功能：(1) price_snapshot 价格变更历史——商品详情、查返利/链接识别、转链、搜索的联盟返回在响应后异步写入（BR-WATCH-05 的游程规则，source_kind 按来源区分），写入失败只计数不重试，不得影响接口 P95；price_snapshot 不得含 user_id、device_id、relation_id、subUnionId 等用户标识；只写不带用户级参数（relation_id、按用户分配的推广位/subUnionId、custom_parameters、cPin/xid_buyer、地区、个性化设备标识）的联盟返回，除非 09 CAP-\*-13 已证实价格与该参数无关；拼多多只写搜索/详情通用计划的 goods_sign 结果，并记录 goods_sign_plan。(2) scene 枚举只新增 watch_alert 一个值（13 §13.2「scene 新增（P1）」行；外部入口的 share_ext、wechat_bot、mcp 由该行另行规定，不在本条）；digest、new_arrival、promo_reminder、replenish 不进 scene 枚举，提醒类型的细分以 links.sub_scene 记录（取值 = watch.type，如 price_drop；该列在 P1 随 WT-01 新增，MVP 不建），不扩 scene。(3) 站内信与推送带分类（服务/订阅/营销），通知设置支持按分类关闭。MVP 不建 watch、tracked_item、tracked_query、watch_event、price_observation 表，不注册 create_watch 工具；这些结构在 P1 开工 WT-01 定稿后再迁移。本条是 MVP 范围变更，需负责人确认。 | 已确认 | price_snapshot 表与写入钩子（W2）；规划/04 §2.2 scene；notification.category、/v1/me/notification-settings；规划/05 B1 任务清单；MVP 周验收门 W2 |
| BR-WATCH-20 | **任务表模型为候选方案**<br>「统一 watch 表承载七类订阅任务（target_kind = item/query/event/category）」只是候选技术方案，不得作为业务规则引用。P1 开工时（WT-01）由实现方写 ADR 在两种方案中选定：A 统一 watch 表 + type 专属 condition JSON（按 type 做 CHECK/JSON Schema 校验）；B 按类型分表。无论选哪种，都必须满足 BR-WATCH-02～18 的字段语义（status 五态、unavailable_reason、condition_version、armed/episode_seq、baseline_\*、last/min_notified_\*、dedupe_key、notification.delivered_price_fen、push_digest 等），且 S3 只实现 price_drop 所需字段。 | 默认假设 | WT-01 契约定稿；WT-02 迁移；ADR 目录 |
| BR-WATCH-21 | **有券/到货等提醒（S4）**<br>coupon（有券提醒）、back_in_stock（到货提醒）、淘礼金提醒在 S4 立项前只维护目标、依赖与未知项，不得开发。立项前必须先完成对应平台能力验证并补齐与 BR-WATCH-03～16 同等粒度的规则。硬约束：任何提醒不得创建、预占或发放淘礼金；淘礼金只能在用户点击领取时，按 D7 淘礼金预算与 tlj.enabled 开关实时扣减，预算不足时提醒落地页显示「本期礼金已发完」。 | 待验证 | 规划/00 §4 范围表；规划/09 能力验证表；规划/05 S4；淘礼金预算（D7） |
| BR-WATCH-22 | **大促/精选/复购/上新路线**<br>promo_calendar（P1-b）、digest（P1-c）、replenish（P1-c）、new_arrival（P1-d）只保留目标、依赖、未知项与已知硬约束；硬约束为：Agent 不得无用户确认创建任何主动推荐任务；digest 与 replenish 须用户逐个确认创建，F-PRIV-04「个性化推荐」开关关闭时不生成新任务并立即停止已有任务；digest 每用户最多 3 个、最短间隔 1 天；replenish 只用本 App 历史订单；new_arrival 首次运行只建基线不发提醒；通知分类：digest（精选）、new_arrival（上新）、replenish（复购）按「营销」类，promo_calendar（大促）按「订阅」类（PRD v2.1 §10.19 通知策略）；营销类推送的每日上限、免打扰是否对大促提醒放开，在各类型立项时定（见细则未知项）。 | 默认假设 | 规划/00 §4 范围表；规划/05 后续路线；隐私政策与 F-PRIV-04 个性化推荐开关 |
| BR-WATCH-23 | **数据来源、隐私与合规**<br>提醒使用的价格、券、库存只能来自联盟接口，不得做页面采集；轮询、判定、价格计算不得使用模型。用户的提醒列表属于个人偏好数据：必须写入隐私政策，用户可在「我的提醒」查看全部并删除。用户主动删除（cancelled）：立即对用户不可见并停止一切处理，watch.cancelled_retention_days（7）天内物理删除或去标识（只保留不含 user_id 的聚合统计）；自然到期（expired）：expires_at 起 watch.expired_retention_days（90）天后删除（覆盖 30 天续期宽限）；watch_status_log、watch_event、订阅类站内信与 watch 同期删除。账号注销：提交注销即全部 watch 置 paused、停止查询与推送（BR-WATCH-10）；冷静期结束随 F-ACC-10 删除 watch、watch_status_log、watch_event 与关联站内信。后台按用户查看提醒必须脱敏（手机号、昵称）。营销类推送（精选、上新）需用户单独开启，iOS 须明示同意。保留期与删除方式以法务确认为准。 | 待决策 | 隐私政策文本（规划/06 F 节）；规划/01 F-ACC-10、F-PRIV-08；后台提醒查询页 WT-12；retention.purge；配置 watch.cancelled_retention_days、watch.expired_retention_days |
| BR-WATCH-24 | **监控指标与误报率**<br>误报率按以下口径计算：以 notification 为单位去重，每条 notification 只取首次点击时落地页的实时报价（click_quote，且与提醒口径同 api_kind）；分母 = 7 天滚动窗口（按点击时间）内首次点击且实时报价 fetch_status=ok 并返回价格的 notification 数，off_shelf / not_found 不进分母，单独统计「点击时已下架率」；分子 = 其中实时 final_price_fen > 该 notification.delivered_price_fen（整数分严格大于）的数量；按平台分别计算，样本 &lt; watch.alert.min_samples（50）时不告警。误报率 > 2% 或提醒配额桶使用率 > 90% 必须告警。放量门槛：单平台 7 天内有效样本 ≥ 50 且误报率 &lt; 2% 才可扩大放量，样本不足时维持当前灰度比例。另须上报：有效提醒数与人均数、各层查询量、抓取失败率、确认通过率、事件数与抑制率（按 suppress_reason 分）、各通道送达率与打开率、scene=watch_alert 的点击→下单转化（订单状态口径见细则）、关闭推送率。 | 默认假设 | 规划/02 §13 可观测；后台提醒监控页 WT-12；告警规则 WT-13；P1 放量门槛（BR-WATCH-27） |
| BR-WATCH-25 | **降价提醒验收用例**<br>S3 验收用例只在 规划/10 §4 维护（AC-S3-nn，写入 acceptance/watch.feature；旧编号 WA-nn（= 13 §13.2 AC-WATCH-nn，Epic E21 WATCH）与 AC-S3-nn 的对应见 10 §5.4 与 §4.2「对应」列）；出门条件见 10 §1 S3（三家各跑一次，按平台独立判定）。本主题不再维护用例表；本文其他规则「验收用例」一栏写 AC-S3-nn 只作指向。 | 默认假设 | 规划/10 §1 S3、§4、§5.4；acceptance/watch.feature；规划/05 S3 阶段验收 |
| BR-WATCH-26 | **S3 范围与后续分期**<br>S3 只交付 price_drop 目标价模式（用户给定目标券后价）。以下不进 S3：无目标价降幅模式（PRD v2.1「较上次提醒价下降 ≥5% 且 ≥2 元」）、「自 &lt;开始记录日> 以来观察到的最低价」标签；coupon、back_in_stock、淘礼金提醒延到 S4（BR-WATCH-21）；promo_calendar（P1-b）、digest 与 replenish（P1-c）、new_arrival（P1-d）只写目标、依赖、未知项（BR-WATCH-22）。S4 及以后的类型在 规划/ 中不写实现细节。MVP 预埋范围见 BR-WATCH-19。 | 已确认 | 规划/00 §4 范围裁决表 Agent 行；规划/01 E07 F-AGENT-18；规划/01 新增 Epic E21 WATCH（编号按 13 §13.2，E20 为外部入口 EXT，不用于订阅提醒）；规划/05 阶段 S3/S4 |
| BR-WATCH-27 | **按平台开关的放量与关停**<br>每个平台由 watch.enabled.&lt;platform>（默认 false）独立控制提醒，与 convert.enabled.&lt;platform> 相互独立；convert.enabled.&lt;platform>=false 时该平台提醒也视为关闭。开关为 false 时：不能新建、续期、改目标价（返回 30806，data.reason=watch_platform_disabled），该平台「降价提醒」入口隐藏；已有 watch 状态不变，可暂停、取消；调度器停止查询，判定器不产生事件，未发送事件在投递时置 suppressed(platform_disabled)；「我的提醒」中该平台条目显示「该平台提醒暂停服务」；到期扫描跳过该平台 watch，开关恢复时该平台非终态 watch 的 expires_at 顺延关停时长；开关恢复后清除 pending 并立即安排一次查询。扩大放量须满足 BR-WATCH-24 放量门槛。 | 默认假设 | 配置 watch.enabled.&lt;platform>；调度器、判定器、通知服务；POST/PATCH /v1/watches（30806 watch_platform_disabled）；我的提醒页；watch_platform_switch_log；验收用例 规划/10 AC-S3-35-JD |
| BR-WATCH-28 | **创建入口与前置条件**<br>S3 只有两个创建入口：① 商品卡、商品详情页、提醒落地页上的「降价提醒」按钮，打开设置面板（BR-WATCH-18）；② Agent 对话，create_watch 出确认卡（BR-WATCH-18）。大促日历页、精选设置页、订单详情、下架商品卡等入口属 BR-WATCH-21、22 的未立项类型，S3 不做。「降价提醒」按钮仅在同时满足以下条件时显示：watch.enabled.&lt;platform>=true 且 convert.enabled.&lt;platform>=true（BR-WATCH-27）；商品 product_key 非 null；商品卡 availability 为可购买（下架、无货、price_unavailable 时不显示）；当前券后价 ≥ 2 分（目标价下限 1 分须严格低于当前价，BR-WATCH-04）。身份：创建、改目标价、续期、暂停、恢复、取消、查看「我的提醒」均要求已登录（BR-ID-02 身份等级 member，未绑手机也可用），不要求实名；未登录调用 /v1/watches 返回 10001，客户端按 BR-ID-10 保存 pending_action，登录成功后回到该商品的设置面板，不得自动创建。基本模式下按钮照常显示，点击按 BR-ID-02 重新展示隐私弹窗。Agent：游客或未登录主体表达创建、修改、取消提醒意图时，服务端丢弃模型文本，出 auth_required 卡（reason=login），不出 watch_confirm 卡；create_watch、update_watch、cancel_watch、list_watches 只下发给已登录主体（与 BR-AI 订单类工具的主体过滤同一机制）。系统推送权限不是创建前提：未开启时确认卡与面板的「通道」显示「仅站内信（未开启通知）」并给出去开启入口，再次申请权限的频率按 BR-ID-13。新建 watch 的 app_id 取当前 App。 | 默认假设 | 商品卡、商品详情页、提醒落地页「降价提醒」按钮显示条件；POST/PATCH/DELETE/GET /v1/watches 鉴权（10001）；BR-ID-02 身份能力矩阵（补「订阅提醒」行）；BR-ID-10 pending_action；Agent 工具主体过滤与 auth_required 卡；watch_confirm 卡与设置面板「通道」字段；验收用例 规划/10 AC-S3-28 |
| BR-WATCH-29 | **「我的提醒」页**<br>列表只含当前用户在当前 app_id 下的 price_drop 提醒，状态 ∈ {active, paused, unavailable, expired}；cancelled 一律不显示；expired 显示到按 BR-WATCH-23 删除为止。分两组：「进行中」（active、paused、unavailable，按 created_at 倒序）与「已过期」（expired，按 expires_at 倒序），每组游标分页、每页 20 条。页顶显示「已设 X / N」：X = active + paused + unavailable 条数，N = watch.max_per_user（BR-WATCH-17）。每行显示：平台、短标题（规则同 BR-WATCH-14）、目标价「≤ ¥X」、状态或价格文案、检查频率（BR-WATCH-07）、有效期（到期前 watch.expiry_notice_days 天内显示「N 天后到期」，其余显示「有效至 {expires_at 的日期}」，日期按 BR-TEXT-11 纯日期规则：同年 MM-DD、跨年 YYYY-MM-DD）。状态或价格文案按细则表自上而下取第一个命中的行；可用操作按细则操作表，不在表中的操作不显示。取消与删除都迁移到 cancelled（BR-WATCH-10），须弹二次确认「取消后不再提醒，且无法恢复」，确认后立即从列表消失。页面内的暂停、恢复、改目标价、续期、取消由用户点击即视为确认，不需要 Agent 确认卡；在 Agent 中操作仍按 BR-WATCH-18 先出确认卡。从合并摘要推送进入时（BR-WATCH-16）高亮该摘要 push_digest_item 关联的提醒并滚动到第一条，已取消的条目不显示、不报错。 | 默认假设 | GET /v1/watches（group=active\|expired、cursor）；我的提醒页（iOS / Android / 鸿蒙；H5 是否提供随 P1 范围定）；PATCH /v1/watches/{id}、DELETE /v1/watches/{id}；状态文案字典 watch_status.*；验收用例 规划/10 AC-S3-34、AC-S3-33 |

### 9.2 细则

#### BR-WATCH-01 细则 · 提醒首版交付目标

- 状态：已确认
- 默认值：S3 交付单商品降价提醒全流程；三家按平台独立验收与放量；MVP 不开放提醒入口
- 决策人：负责人
- 依赖平台能力：无
- 取代：无
- 来源：规划/10 §1 S3；规划/00 D24；规划/00_总览与决策.md §4（降价提醒 P1）
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：淘宝在 S3 完成验收并放量；京东 CAP-JD-13 未通过，京东提醒保持关闭，淘宝不受影响。
- 验收以用户结果为准：规划/10 §4 的 S3 用例三家各跑一次，按平台分别判定（BR-WATCH-25）。

#### BR-WATCH-02 细则 · 监控对象与商品粒度

- 状态：待验证
- 默认值：商品级监控，不区分 SKU；同用户同商品非终态 price_drop 最多 1 条；过期宽限期内引导续期
- 决策人：负责人
- 依赖平台能力：三家联盟商品查询接口返回的券后价是商品级还是 SKU 级、多规格时取哪个 SKU（09 CAP-TB-13/JD-13/PDD-13、链路①②）；淘宝/京东动态商品 ID 能否由 product_key 稳定映射（09 CAP-TB-01、CAP-JD-01）
- 取代：
  - 开发任务拆解 v1 WT-03：「1000 个用户盯同一商品只产生 1 个 tracked_item（未定义同商品是否同规格）」
  - 返利 App PRD v2.1 §10.20 表：「tracked_item 以 (platform, item_key) 唯一」
  - 规划/09 CAP-TB-13、CAP-JD-13 不支持时怎么办列：「旧 raw_item_id / itemId 失效：按标题 + 店铺重新检索（检索结果不得自动替换监控对象）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.20 第 1、2、4 条；开发任务拆解_v1_2026-09-29.md WT-03；规划/04_数据模型与契约.md §1 product_key；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-13、3_JD_京东.md CAP-JD-13、4_PDD_拼多多.md CAP-PDD-13
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

- 数据：`watch.app_id`、`watch.platform`、`watch.product_key`、`watch.sku_key`（预留，S3 恒为 null）、`watch.unavailable_reason`（fetch_failed / item_unresolved）。
- 跨用户共享：若 BR-WATCH-08 前提成立，同一 (app_id, platform, product_key, sku_key=null) 只对应 1 个 tracked_item；唯一索引对 sku_key 用 NULLS NOT DISTINCT（或 coalesce(sku_key, '')），否则 null 不参与唯一判断。不同 app_id 的同一商品各自建 tracked_item、各自查价（BR-PROD-01）。
- 例 1：用户 A 对 `tb:123`（伊利纯牛奶 250ml×24）设 ¥40；联盟返回商品级券后价 ¥38，下单页选 250ml×16 规格为 ¥29——只按 ¥38 判定。
- 例 2：A 已有 `tb:123` active 提醒，再建 → 409 watch_duplicate + 已有 watch_id；A 的 `tb:456` 提醒 09-01 到期、09-20 再建 → 409 watch_expired_renewable；10-05（超过 30 天）再建 → 成功。
- 例 3：两个创建请求同时到达 → 行锁串行，第二个得到 watch_duplicate；用户已有 19 条时两个不同商品请求并发 → 第二个得到 watch_limit_exceeded。
- 边界：拼多多价格字段是多规格最低价（09 CAP-PDD-13）；淘宝不传 sku_id 时对应哪个规格未知（09 CAP-TB-13）。若 S0 验证某平台可稳定返回 SKU 级券后价，由负责人决定是否启用 sku_key。
- item_unresolved 不会被后续观测自动恢复（BR-WATCH-10）。

#### BR-WATCH-03 细则 · 监控价格口径

- 状态：待验证
- 默认值：联盟券后价（提醒口径接口、不带用户参数）；不含运费、会员/跨店/多件优惠
- 决策人：负责人
- 依赖平台能力：三家联盟接口是否返回券后价字段及其含义、是否返回运费；满额券门槛字段是否可得；价格是否随用户参数变化（09 链路②、CAP-TB-13/JD-13/PDD-13）；能否以可接受的成本和频率按商品取价（09 链路⑤、CAP-X-10）
- 取代：
  - 返利 App PRD v2.1 §10.19 通用规则：「价格口径：联盟接口的券后价，不含 88VIP 价、跨店满减、淘金币等（未写运费、未写与预估返后价的关系）」
  - BR-PRICE-19 原稿中的监控口径描述（已收拢到本条，BR-PRICE-19 改为指针；其中「查询失败不当 0 元」一句由 BR-WATCH-09 维护）
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.19；规划/01_需求规划.md F-PRIV-08（展示价来自联盟接口）、J2 第 4 条；规划/09_平台能力验证/3_JD_京东.md CAP-JD-13；README §1.3 价格术语；规划/10 §4.1「价格口径」；BR-PRICE-19 原稿
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 公式：触发价 = final_price_fen = price_fen − coupon_fen，一律按 BR-PRICE-01 在服务端自算；平台返回的券后价类字段（如淘宝 final_promotion_price、京东 lowestCouponPrice）只存原始报文，进入 BR-PRICE-01「平台券后价白名单」后才可作为 final_price_fen 来源。
- 选择理由：返利受佣金率变化、淘宝比价降佣影响，用预估返后价触发会因佣金变化产生「降价」误报；券后价是用户在平台下单页能直接核对的数。
- 例：price_fen=4990、coupon_fen=1000 → final_price_fen=3990；目标 4000 → 满足；预估返利 120 分只显示为「预估返 ¥1.2」（金额格式按 BR-TEXT-10）。
- 例：目标 4000，观测 price_fen=4900、final_price_fen=3900，下单页运费 600 → 用 3900 比较，满足；运费不加进去。
- 运费：三家联盟接口是否返回运费待验证；即使返回也不计入触发价，落地页可单独展示「运费以下单页为准」。
- 提醒内容里的价格格式与口径说明按 BR-PRICE-17；点击提醒后的价格复核走 BR-WATCH-16 与 BR-PRICE-13。查询失败、缺失价格的处理只看 BR-WATCH-09。
- 满额券（如满 99 减 20）当 price_fen &lt; 门槛时不可用，此时 final_price_fen = price_fen，由 BR-PRICE 统一判定。
- 京东价格随地区与买家身份（area、cPin、basisPriceType）变化，提醒只用不传这些参数的券后价（09 CAP-JD-13）。

#### BR-WATCH-04 细则 · 目标价输入与比较符

- 状态：已确认（负责人 2026-09-30，依据 docs/changes/20260930-拍板第一批.md §2）
- 默认值：比较符 ≤；实时价已达到目标价则拒绝创建。理由：与 PRD v2.1 WA-01 一致，确认卡显式展示避免歧义；拒绝创建可避免创建即推送
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 开发任务拆解 v1 WT-06：「判定器：目标价/降幅/新低…（比较符 &lt; 或 ≤ 未定义）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.19 任务类型与 WA-01；规划/04_数据模型与契约.md §7 错误码码段；规划/00 D2；规划/10 §4.1
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例 1：目标 ¥40（4000 分），观测 4000 → 满足；4001 → 不满足；3800 → 满足。
- 例 2：Agent 输入「40块5以下提醒我」→ 4050、≤。
- 例 3：输入「39.999」→ watch_target_invalid；「40.500」→ watch_target_invalid（parseYuanToFen 按字符串判断小数位，不去末尾 0，与 BR-PRICE-01 一致）；「40.50」→ 4050；「0」→ watch_target_invalid。Agent 把口语「40块5」先规范为「40.5」再交服务端解析。
- 例 4：POST 时实时券后价 3900，目标 4000 → watch_target_already_met。
- S3 目标价必填：商品卡「降价提醒」按钮打开设置面板（BR-WATCH-18），预填建议目标 = min(floor(当前券后价 × 9500 / 10000 / 100) × 100, floor((当前券后价 − 100) / 100) × 100)（整数运算，结果为整元、至少比当前价低 1 元）；结果 &lt; 100 分时不预填（即当前券后价 &lt; 200 分时不预填）。例：当前 5690 → min(5400, 5500) = 5400（¥54）；当前 250 → min(200, 100) = 100；当前 199 → 不预填。
- 本主题错误码（码表见 13 §13.11，码段 308 提醒，P1；data.reason 保留同名值）：watch_target_invalid → 20001（不另开码，data.fields=[target_price]）；30801 watch_target_already_met；30802 watch_limit_exceeded；30803 watch_duplicate（HTTP 409，带 data.watch_id）；30804 watch_expired_renewable（HTTP 409，带 data.watch_id）；30805 watch_quote_unavailable；30806 watch_platform_disabled。
- 选 ≤ 的理由：PRD v2.1 WA-01 与 §10.19 触发条件均为 ≤；用户说「低于 40」时券后价恰为 4000 分也提醒，比漏提醒的投诉少；确认卡明示比较符消除歧义。

#### BR-WATCH-05 细则 · 观测与价格变更历史分离

- 状态：默认假设
- 默认值：两表分离：price_observation 30 天 + price_snapshot 游程编码 13 个月；advisory lock 串行写
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 返利 App PRD v2.1 §10.20 第 1、4 条：「price_snapshot（item_key、observed_at、price_fen、coupon_fen、final_price_fen、in_stock、source），价格有变化才写（与连续两次观测一致冲突，未定义最近观测）」
  - 开发任务拆解 v1 WX-01：「联盟返回在价格或库存变化时才写新行（未区分变更历史与最近观测）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.20 第 1、4 条、§10.21；开发任务拆解_v1_2026-09-29.md WX-01；规划/10 §4.1「观测与变更历史分离」
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**price_observation**（按日分区，保留 30 天）：id、app_id、platform、product_key、sku_key、observed_at、source（watch_create / watch_update / watch_fetch / watch_confirm / watch_recheck / click_quote）、api_kind、goods_sign_plan（拼多多）、fetch_status（ok / timeout / error / rate_limited / not_found / invalid）、price_fen、coupon_fen、final_price_fen（可空）、in_stock（可空）、suspect_drop（bool）、error_code、raw_payload_id。

**tracked_item 最近观测缓存**：last_observed_at、last_ok_at、last_final_price_fen、last_in_stock、consecutive_fail_count、first_fail_at。

**price_snapshot**（按月分区，保留 13 个月）：app_id、product_key、sku_key、source_kind（search / detail / quote / convert / watch）、price_fen、coupon_fen、final_price_fen、in_stock、first_observed_at、last_observed_at、observation_count。不含任何用户标识（BR-WATCH-19）。

**例**：08:00 观测 4500、14:00 观测 4500、17:00 超时、20:00 观测 3900、20:05 观测 3900、20:15 观测 3900 →
- price_observation 6 行（含 1 行 timeout）；
- price_snapshot（source_kind=watch）2 行：(4500, first 08:00, last 14:00, count 2)、(3900, first 20:00, last 20:15, count 2)（20:05 距 20:00 不足 10 分钟，不计）；
- tracked_item.last_ok_at = 20:15。

用途划分：观测→判定、确认、复核、误报排查；历史→价格走势（P1 以后）、热层判定中的「近 7 天 source_kind=watch 变动次数」（BR-WATCH-07）。

#### BR-WATCH-06 细则 · 两次确认触发判定

- 状态：待验证
- 默认值：每平台单一提醒口径接口；两次成功观测都满足、间隔 ≥10 分钟、窗口 6 小时；确认查询 +15 分钟，失败 +15/+30/+60 分钟重试
- 决策人：负责人
- 依赖平台能力：各平台提醒口径接口与复核/点击报价接口券后价是否一致；价格是否随用户参数变化；拼多多 goods_sign 计划能否固定（09 CAP-TB-13/JD-13/PDD-13）
- 取代：
  - 返利 App PRD v2.1 §10.20 第 5 条：「需连续两次观测一致，以防价格抖动（未定义两次的间隔、来源、是否要求价格相同）」
  - 开发任务拆解 v1 WT-06：「两次观测一致才触发」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.20 第 5 条、WA-01；开发任务拆解_v1_2026-09-29.md WT-06；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-13、3_JD_京东.md CAP-JD-13、4_PDD_拼多多.md CAP-PDD-13
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

每个 watch 的判定状态：confirm_state（none / pending）、pending_obs_id、pending_at。

| 输入 | 当前状态 | 结果 |
|---|---|---|
| 成功且满足（且 armed 或满足 new_low 阈值） | none | 置 pending，安排 +15 分钟确认查询 |
| 成功且满足 | pending，距 pending_at &lt; 10 分钟 | 忽略，保持 pending，不更新 pending_obs_id |
| 成功且满足 | pending，10 分钟 ≤ 距 pending_at ≤ 6 小时 | 产生事件（BR-WATCH-11/12），after=本次价格，状态回 none |
| 成功且满足 | pending，距 pending_at > 6 小时 | 以本次观测替换 pending_obs_id、pending_at，重新安排 +15 分钟确认查询 |
| 成功但不满足 | 任意 | 清除 pending；若 disarmed 则置 armed（BR-WATCH-11） |
| 失败（fetch_status ∉ {ok, not_found}） | 任意 | 不计数、不清除 pending；若为确认查询则按重试表重试 |
| not_found（in_stock=false） | 任意 | 视为成功但不满足 |
| 成功且满足，但 disarmed 且不满足 new_low 阈值 | none | 只记观测 |

- 例：目标 4000。20:00 观测 3900 → pending；20:15 确认查询 3950 → 产生事件，after=3950。
- 反例：20:00 观测 3900 → pending；20:15 观测 4100 → 清除并 armed；20:30 观测 3900 → 重新 pending，不产生事件。
- 例（重试）：20:00 pending；20:15 超时 → 20:30 重试超时 → 21:00 重试 3900 → 产生事件；若到 02:00 仍无成功观测 → 下一次成功观测时惰性清除。
- 例（持续低价）：已 disarmed，价格 30 天都在 3900 → 常规查询照常，无确认查询、无事件。
- 边界：in_stock=null（平台不返回库存）视为可购买，由落地页实时报价兜底（BR-WATCH-16）。
- 初值（候选，接口名、参数与返回字段均待实测核实，未验证前不作为已确认事实）：taobao=taobao.tbk.item.info.upgrade.get，jd=jd.union.open.goods.query（不传 area/cPin），pdd=pdd.ddk.goods.search（goods_sign_list，通用计划）；以 09 CAP-TB-13/JD-13/PDD-13 实测结论为准。

#### BR-WATCH-07 细则 · 检查频率、创建报价与延迟说明

- 状态：待验证
- 默认值：热 2h / 默认 6h / 冷 24h / 大促 ÷2 / 最短 1h（按平台可配）；创建时服务端重新报价，失败拒绝
- 决策人：负责人
- 依赖平台能力：三家联盟接口日配额与 QPS、批量接口单次商品数上限（规划/06 Q-G5 及京东、拼多多对应项；09 CAP-TB-13/JD-13/PDD-13）
- 取代：
  - 返利 App PRD v2.1 §10.20 第 3 条：「热层每 1–2 小时；大促整体 ×2–4（区间未定具体值）」
  - 返利 App PRD v2.1 §10.19：「固定附注「我们约每 X 小时检查一次」（X 未定义取值规则）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.19、§10.20 第 3 条；规划/09_平台能力验证/3_JD_京东.md CAP-JD-13、4_PDD_拼多多.md CAP-PDD-13 降级列；规划/10 §4.1「检查频率与延迟说明」

| 层级 | 条件（初值） | 间隔 | 用户文案 |
|---|---|---|---|
| 热 | subscriber_count ≥ 20，或近 7 天 source_kind=watch 的 price_snapshot 新行 ≥ 3 | 120 分钟 | 约每 2 小时 |
| 默认 | 其他（含创建未满 14 天） | 360 分钟 | 约每 6 小时 |
| 冷 | subscriber_count = 1、created_at 满 14 天且 14 天无 source_kind=watch 新行 | 1440 分钟 | 约每天 |
| 大促 | 运营开关 watch.promo_mode | 上述 ÷ 2，最短 60 分钟 | 按折算后 X |

- 例：默认层商品 10:00 降价，最坏情况 16:00 常规查询命中 → 16:15 确认 → 16:15 站内信与首条推送发出，延迟约 6 小时 15 分钟；若命中在 22:30，则站内信即时写入，推送 08:00 发出。
- 例（创建）：Agent 卡片 14:02 报价 5690，14:20 用户确认 → 服务端 14:20 重新报价 5590，按 5590 校验目标价并作为 baseline；报价超时 → watch_quote_unavailable，无 watch 行。
- 最大延迟（非免打扰）≈ 间隔 + confirm_delay + 队列排队。
- 降级（09）：配额不足时拼多多可设为「订阅人数达阈值的商品按小时，其余每 24 小时」，京东默认层 12 小时，文案随配置自动变化。

#### BR-WATCH-08 细则 · 跨用户去重、调度与配额

- 状态：待验证
- 默认值：共享查价（待 09 验证）；独立提醒配额桶 5%（从商品池刷新 10% 中切出）；实时操作优先于复核
- 决策人：负责人
- 依赖平台能力：跨用户共享查价是否成立（09 CAP-TB-13 (a)、CAP-JD-13、CAP-PDD-13）；淘宝/京东/拼多多日配额、QPS、批量查询上限（规划/06 Q-G5；京东、拼多多需补同类项）
- 取代：
  - 返利 App PRD v2.1 §10.20 第 3 条：「优先级：发送前复核 > 用户实时操作 > 热层 > 默认层 > 冷层 > 上新与精选」
  - PRD修订_后端功能规划 §7 统一 Client 规范：「配额切分在线 60%、订单同步 30%、商品池刷新 10%（未给提醒类定时查询预留配额）」
  - 规划/09 CAP-TB-13 通过标准 (c)：「日调用量 ≤ 配额的 10%（与 02 §6.2 商品池刷新占比一致）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.20 第 2、3 条；PRD修订_后端功能规划_2026-09-29.md §7；规划/02_系统架构.md §6.2 配额；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-13、3_JD_京东.md CAP-JD-13；开发任务拆解_v1_2026-09-29.md WT-03、WT-04
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

- 配额切分默认：P1 开启后由 规划/02 现有「在线 60%、订单同步 30%、商品池刷新 10%」改为「在线 60%、订单同步 30%、商品池刷新 5%、提醒 5%」，06 Q-G5 实测后再调；提醒桶使用率 > 90% 告警。09 CAP-TB-13 通过标准 (c) 同步改为同一数字。
- 容量例：1 万 tracked_item 默认层每日 4 次、每次批量 20 个 → 2,000 次调用/日/平台，需 ≤ 日配额 × 5%（即日配额 ≥ 4 万次）；不满足则按 BR-WATCH-07 降频。
- 与 PRD 不同：PRD 把「发送前复核」排在「用户实时操作」之前，本规则改为实时操作优先，满足 WT-04「实时操作不受影响」，复核改为可推迟。
- 例（计数）：商品有 3 个 active、1 个 paused → subscriber_count=3；active→paused 时 −1，paused→active 时 +1，active→unavailable 不变，cancelled/expired 时 −1。
- 异常：某平台 tracked_item 连续失败不影响其他平台调度。

#### BR-WATCH-09 细则 · 查询失败、缺失价格与异常降价

- 状态：默认假设
- 默认值：扫描判断：≥2 次失败且 ≥ max(24h, 2×层级间隔) 置 unavailable，成功自动恢复；配额推迟不算失败；降幅 ≥70% 强制复核
- 决策人：负责人
- 依赖平台能力：三家联盟接口区分「商品下架/不存在」与「系统错误」的错误码是否可靠（09 链路①⑤）
- 取代：
  - 返利 App PRD v2.1 §10.20 第 5 条：「抓取失败不产生任何事件；连续失败超过 24 小时，把 watch 置为 unavailable（未定义恢复、未定义非法价格）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.19、§10.20 第 5 条；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-13、4_PDD_拼多多.md CAP-PDD-13 降级列；开发任务拆解_v1_2026-09-29.md WT-05；规划/10 §4.1「查询失败不当 0 元」

页面展示：
| 情形 | 「我的提醒」显示 |
|---|---|
| active，最近成功观测有价格 | 「¥45 · 更新于 今天 14:00」 |
| unavailable(fetch_failed) | 「暂时无法获取价格（最近成功 昨天 14:00）」 |
| unavailable(item_unresolved) | 「商品信息已变化，请重新选择商品」 |
| not_found | 「商品已下架或无货」 |

金额按 BR-TEXT-10 格式化，时间按 BR-TEXT-11 列表过去时间规则格式化（今天 HH:mm / 昨天 HH:mm / MM-DD / YYYY-MM-DD）。多个情形同时成立时的取用顺序见 BR-WATCH-29。

- 例 1：14:00 查询超时 → price_observation 写 timeout 行，无事件，watch 仍 active。
- 例 2：联盟返回 price_fen=3900、coupon_fen=3900（算得 final_price_fen=0）→ invalid，计入抓取失败率，不触发「¥0 降价提醒」。
- 例 3（默认层）：09-28 14:00 成功，之后 20:00、02:00、08:00、14:00 均超时 → 09-29 14:00 扫描时满足（4 次失败、24 小时）→ unavailable；09-29 20:00 成功 3900（目标 4000）→ 恢复 active，按 BR-WATCH-06 重新需要两次确认。
- 反例（冷层）：D1 04:00 成功、D2 04:10 成功 → 始终 active；D2 04:10 超时、D3 04:05 成功 → 仍 active（未达 48 小时与 2 次失败）。
- 例 4：p0=4500、p1=1200，(4500−1200)×10000=33,000,000 ≥ 4500×7000=31,500,000 → suspect_drop；确认后每个通道投递前强制实时复核。
- 平台错误码 → not_found 的映射表按平台维护，未列入映射的码一律按 error 处理。

#### BR-WATCH-10 细则 · 提醒生命周期

- 状态：默认假设
- 默认值：五状态；续期不改变非终态状态；expired 30 天内可续（校验上限与实时价）；注销即 paused。保留期与删除范围不在本条维护，只在 BR-WATCH-23（待决策，法务）维护
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 返利 App PRD v2.1 §10.20 第 1 条：「watch.status 仅 active / paused / expired / unavailable（无取消/删除态）」
  - 返利 App PRD v2.1 §10.19：「「我的提醒」页：列表、暂停、修改目标价、删除；到期前 3 天提示续期（未定义迁移条件）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.19、§10.20 第 1 条；开发任务拆解_v1_2026-09-29.md WT-09；规划/01_需求规划.md F-ACC-10；规划/10 §4.1「生命周期」
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

| 从 | 到 | 触发者 | 条件 / 副作用 |
|---|---|---|---|
| — | active | 用户确认（确认卡或设置面板） | POST /v1/watches，Idempotency-Key 见 BR-WATCH-18 |
| active / unavailable | paused | 用户；或系统（account_closing） | 停止判定，清除 pending；subscriber_count 按 BR-WATCH-08 维护 |
| paused | active | 用户 | now &lt; expires_at 且平台开关开启；清除 pending，立即安排一次查询；之后由观测决定是否再进入 unavailable |
| active | unavailable | 系统 | BR-WATCH-09（fetch_failed）或 BR-WATCH-02（item_unresolved） |
| unavailable(fetch_failed) | active | 系统 | 首次成功观测（含改目标价时的实时报价） |
| active/paused/unavailable | expired | 系统 | now ≥ expires_at（每 watch.expiry_scan_minutes=5 扫描；判定时也校验）；平台关停期间不扫描（BR-WATCH-27） |
| 除 cancelled 外任意 | cancelled | 用户，或用户确认的 Agent 取消卡 | 列表立即隐藏；未发送事件投递时 suppressed(watch_inactive) |
| active/paused/unavailable | 原状态（续期） | 用户 | 只延长：expires_at = max(now, expires_at) + 60 天 |
| expired，now − expires_at ≤ watch.renew_grace_days（30） | active（续期） | 用户 | 前提：未超过 watch.max_per_user，实时券后价 > target_price_fen（否则 30802 watch_limit_exceeded / 30801 watch_target_already_met）；expires_at = now + 60 天；condition_version +1，armed=true，episode_seq=1，重置冷却，baseline 与 last/min_notified 按改目标价处理 |
| active/paused/unavailable | 同状态（改目标价） | 用户 | 实时报价（source=watch_update），新目标 &lt; 实时价；condition_version +1，清除 pending，armed=true，episode_seq=1，重置冷却；baseline_final_price_fen = 本次实时价，baseline_observed_at = 本次时间；last_notified_price_fen、min_notified_price_fen 置空 |

- 到期提示：expires_at − watch.expiry_notice_days（3）天发 1 条站内信（订阅类），列表显示「3 天后到期」，不发推送。
- 保留期：cancelled、expired 记录何时删除、哪些关联记录同期删除，只按 BR-WATCH-23 执行（待法务确认）；本条只规定状态迁移。
- 例：09-29 10:00 创建 → expires_at 11-28 10:00；11-25 10:00 收到续期站内信；11-28 10:00 置 expired；12-10 10:00 续期（实时价 4500 > 目标 4000，未超上限）→ active，expires_at = 续期时刻 + 60 天 = 次年 02-08 10:00。
- 例（取消）：23:00 产生事件进入免打扰，23:30 用户取消 → 08:00 合并推送时该事件 suppressed(watch_inactive)，不出现在摘要中。
- 例（注销）：10-01 提交注销 → 全部 watch paused；10-03 撤销注销 → 仍 paused；若未撤销，10-08 冷静期结束同批删除。

#### BR-WATCH-11 细则 · 触发回合、串行与幂等

- 状态：默认假设
- 默认值：回合制；事件产生即 disarmed（recheck_failed/platform_disabled 全抑制除外）；target_hit 键不含价格；按 watch 行锁串行
- 决策人：负责人
- 依赖平台能力：各推送通道（APNs、华为、荣耀、小米、OPPO、vivo、鸿蒙 Push Kit 或聚合服务）是否支持按业务 message_id 去重（待核实）
- 取代：
  - 返利 App PRD v2.1 §10.20 第 1 条：「watch_event：watch_id、kind、before / after 值、created_at、状态（pending / suppressed / sent）（未定义触发幂等键）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.20 第 1 条；PRD修订_后端功能规划_2026-09-29.md §6.1、§6.2；规划/02_系统架构.md §11；规划/10 §4.1「重复执行不重复通知」
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

**suppress_reason 枚举**：cooldown、stale_alert_suppressed、recheck_failed、watch_inactive（paused/expired/cancelled/unavailable）、condition_changed、daily_push_cap（仅 push）、push_disabled（无系统推送权限或关闭订阅类，仅 push）、platform_disabled。

**watch_event.status**：pending → 任一通道 sent 则 sent；所有通道都 suppressed 则 suppressed（suppress_reason 取站内信通道的原因）。

例：目标 4000。
| 时间 | 观测 | 回合状态 | 事件 |
|---|---|---|---|
| D1 20:00/20:15 | 3900/3900 | armed→disarmed，episode 1 | target_hit（dedupe `w1:1:1:target_hit`） |
| D1 20:16 另一 worker 用复核价 3950 再判定 | — | 行锁后读到 disarmed | 无新事件（键也相同） |
| D2 02:15 | 3900 | disarmed | 无，也不安排确认查询 |
| D2 08:15 | 4100 | armed，episode 2 | 无 |
| D2 14:15/14:30 | 3900/3900 | disarmed | target_hit episode 2 → 冷却内 suppressed(cooldown)（BR-WATCH-12），不补发 |

- 同一价格持续低于目标 30 天也只提醒 1 次。
- 例（recheck_failed）：episode 1 事件站内信与推送都 recheck_failed → armed、episode 2，下一次两次确认可再产生 target_hit。
- 推送重试：push.send 明确失败时用同一 notification.id / push_digest.id 重试。

#### BR-WATCH-12 细则 · 冷却与新低突破

- 状态：默认假设
- 默认值：冷却 24 小时从首个 sent 通道起算；new_low 阈值 max(100 分, 3%)；new_low 可突破冷却并重启冷却
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 返利 App PRD v2.1 §10.19 通知策略：「同一提醒冷却 24 小时；创出新低时可突破（未定义新低口径与最小降幅）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.19、§10.20 第 5 条、WA-02；开发任务拆解_v1_2026-09-29.md WT-06

- 例 1（10 AC-S3-13）：目标 4000，24 小时内价格 3900↔4100 来回 5 次 → 第一次 sent，其余 target_hit 均 suppressed(cooldown)。
- 例 2：已 sent 3800（min_notified=3800），阈值 = max(100, 114) = 114。冷却内确认 3750 → 降 50 &lt; 114，不发、不安排确认查询；确认 3680、3685 → 都 ≤ 3686 → new_low sent，min_notified=3680，冷却从发送时刻重计。
- 例 3：min_notified=2000，阈值 = max(100, 60) = 100；确认 1900 → 发。
- 例 4（免打扰）：23:10 target_hit 确认价 3900，站内信 23:10 写入（delivered 3900）→ last_notified_at=23:10、min_notified=3900；08:00 推送复核 3850 发出（delivered 3850）→ 冷却起点仍 23:10，min_notified=3850。
- 例 5：target_hit 23:10 已产生、推送待 08:00，站内信也因复核失败未 sent（min_notified 为空）→ 不生成 new_low。
- 无目标价降幅模式、观察最低价标签的范围决策只在 BR-WATCH-26 维护。

#### BR-WATCH-13 细则 · 发送前复核

- 状态：默认假设
- 默认值：30 分钟新鲜度（只认提醒口径观测）；suspect_drop 强制复核；失败 +10/+30 分钟重试，从计划投递时刻起 2 小时放弃
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 返利 App PRD v2.1 §10.19 WA-01、WA-03：「发送前重新查询价格确认（写成每次发送前都复核）」
  - 返利 App PRD v2.1 §10.20 第 6 条：「快照时间早于 30 分钟的，发送前再查一次（以「快照」为依据，快照变化才写导致无法判断新鲜度）」
  - 规划/09 CAP-TB-13 候选接口：「万能转链（发送前复核 / 点击时实时价，单个，带用户 relation_id）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.19 WA-01/03、§10.20 第 6 条；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-13；开发任务拆解_v1_2026-09-29.md WT-07
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例 1（10 AC-S3-01）：20:00/20:15 确认 3900，20:15 立即投递 → 最近观测 0 分钟，直接发送，delivered=3900。
- 例 2（10 AC-S3-16）：23:10 事件，站内信即时写入；08:00 合并推送前距最近观测 8 小时 → 复核得 4200（目标 4000）→ 推送 suppressed(stale_alert_suppressed)，该商品从摘要中移除；站内信保留，打开时按 BR-WATCH-16 展示当前价。
- 例 3（10 AC-S3-17）：23:10 事件，08:00 复核超时 → 08:10、08:30 重试；10:00 前仍失败 → suppressed(recheck_failed)，计入抑制率（BR-WATCH-11 规定全通道 recheck_failed 时恢复 armed）。
- 例 4：suspect_drop 事件在 20:15 确认，站内信 20:15 投递前仍另发 1 次 watch_recheck。
- 复核优先级见 BR-WATCH-08（低于用户实时操作，可推迟不可跳过）。

#### BR-WATCH-14 细则 · 提醒内容与措辞

- 状态：默认假设
- 默认值：如上模板；被比较价格必须带观测日期；短标题 20 字；禁用词至少 4 个词根
- 决策人：运营（法务审核文案）
- 依赖平台能力：无
- 取代：
  - 返利 App PRD v2.1 §10.19：「提醒内容：商品标题、原券后价→新券后价、预估返利、购买按钮（原券后价未定义取值，无观测日期）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.19 通用规则、WA-06；规划/01_需求规划.md F-PRIV-08；《明码标价和禁止价格欺诈规定》被比较价格要求（条款适用待法务核实）

模板（站内信与推送同源，模板键 watch.price_drop.v1）：
- 标题：「关注的商品已达到你的目标价」
- 正文（target_hit）：「{短标题} 现{price_label} ¥39，已达到你设的 ¥40（你 09-29 设置提醒时为 ¥45）；预估返 ¥1.2」
- 正文（new_low）：「{短标题} 现{price_label} ¥37.8，低于上次提醒价 ¥39（10-02）；预估返 ¥1.15」
- {price_label} 取值按 BR-PRICE-04（本条不另定义），按发送时该通道 delivered_price_fen 对应观测的 coupon_fen 取：淘宝/京东有券「券后价」、无券「售价」；拼多多有券「拼单券后价」、无券「拼单价」。例：淘宝有券 →「伊利纯牛奶… 现券后价 ¥39，已达到你设的 ¥40…」；拼多多有券 →「… 现拼单券后价 ¥39…」；京东无券 →「… 现售价 ¥39…」；拼多多无券 →「… 现拼单价 ¥39…」。
- 跨年例：2026-12-30 设置、2027-01-03 提醒 →「（你 2026-12-30 设置提醒时为 ¥45）」。
- 附注：「约每 6 小时检查一次，价格以下单页为准 · 取价 20:15」
- 按钮：「去看看」（进入落地页，不直接外跳）

合并摘要（BR-WATCH-15）：「3 个关注的商品已达到目标价」+ 列表，每行格式同正文。
例：标题「【官方旗舰】伊利纯牛奶250ml\*24盒 整箱早餐奶 学生营养」→ 按 BR-TEXT-20 删去「官方」得「【旗舰】伊利纯牛奶…」，再去【】及其内容，取前 20 个字素簇（「伊利纯牛奶」5 + 「250ml」5 + 「\*」1 + 「24」2 + 「盒」1 + 空格 1 + 「整箱早餐奶」5 = 20）→ 短标题「伊利纯牛奶250ml\*24盒 整箱早餐奶…」；标题「天猫伊利纯牛奶」→ 去掉「天猫」前缀后为「伊利纯牛奶」，不足 20 个不加「…」。
S4 若启用「观察到的最低价」标签，须先经法务确认与本禁用词表的关系。

#### BR-WATCH-15 细则 · 频控、免打扰、合并与通道

- 状态：已确认（负责人 2026-09-30，依据 docs/changes/20260930-拍板第一批.md §2）
- 默认值：订阅类 5 条/日（按发出时刻计日）；首条立即、后续 10 分钟窗口合并；[22:00, 08:00) 免打扰次日首个 08:00 合并推送；push_digest 承载每次推送
- 决策人：负责人
- 依赖平台能力：华为、荣耀、小米、OPPO、vivo、鸿蒙 Push Kit 对「服务/订阅」类消息的资质要求与每日条数限制（待核实，W0–W2）
- 取代：
  - 返利 App PRD v2.1 §10.19 通知策略：「订阅类 5 条，同一时段的多条合并（未定义时段长度）；免打扰只写营销以外未明确」
  - 规划/01 F-MSG-04：「营销类 22:00–08:00 不发（未覆盖订阅类）」
  - 开发任务拆解 v1 WX-03：「GET / PUT /v1/notification-prefs」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.19 通知策略、WA-05、§10.21；规划/01_需求规划.md F-MSG-01～04；规划/04_数据模型与契约.md §6.4；开发任务拆解_v1_2026-09-29.md WX-03、WT-08
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 例（10 AC-S3-01）：20:15 确认 → 站内信立即写入，推送 20:15 立即发出（push_digest 1 条、item 1 条）。
- 例：20:15 已推送 1 条，20:18、20:22 又各触发 1 条 → 20:25 合并为 1 条摘要「2 个关注的商品已达到目标价」，当日计 2 条。
- 例（10 AC-S3-18）：23:00 触发 3 条 → 3 条站内信即时写入、0 条推送；次日 08:00 复核 3 条中 2 条仍满足 → 1 条摘要推送，计次日推送 1 条；第 3 条的 push notification suppressed(stale_alert_suppressed)。
- 例：00:30 产生的事件在当天 08:00 推送；21:59:59 产生的即时推送；22:00:00 产生的进入免打扰。
- 例：某用户当日已推送 5 条订阅类，14:00 再触发 → push suppressed(daily_push_cap)，只写站内信。
- 例：用户在设置中关闭「订阅」类 → 不推送，站内信仍在（WX-03）。
- 命名映射：PRD v2.1「notification_pref」与开发任务拆解「/v1/notification-prefs」统一为 规划/04 的 `GET/PUT /v1/me/notification-settings`；PRD v2.1 的「D13 频控」与 规划/00 的 D13（首页装修）编号冲突，本规则不沿用 PRD 编号。
- 厂商通道：订阅提醒按各厂商「服务/订阅」类申请，资质与每日条数限制待核实（W0–W2）。
- 默认理由：与营销类免打扰一致；降价信息次日 08:00 仍有效且经复核；首条立即发满足 10 AC-S3-01 的时效。

#### BR-WATCH-16 细则 · 点击提醒后的展示

- 状态：默认假设
- 默认值：落地页用只报价接口，按顺序取行；购买时才转链；不自动取消提醒；摘要点击进我的提醒页
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 返利 App PRD v2.1 WA-01：「用户收到一条提醒，点击后用 scene=watch_alert 的 link_id 实时转链（未定义价格变化时的展示；进入即转链）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.19 WA-01、§10.20 第 7 条；规划/04_数据模型与契约.md §2.2、§6.3、§8.3 availability、§8.4；规划/10 §4.1「点击时涨价、券失效、下架」
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

| 顺序 | 实时结果 | 页面展示 | 购买按钮 |
|---|---|---|---|
| 1 | 实时查询失败 | 「暂时无法获取最新价格；提醒时 ¥38（今天 20:15），价格以下单页为准」 | 可购买，须二次确认 |
| 2 | off_shelf / not_found / in_stock=false | 「商品已下架或无货」 | 隐藏购买；显示「找相似」（Agent 入口） |
| 3 | current > target | 「价格已回升：提醒时 ¥39，现在 ¥45，已高于你的目标价 ¥40」+ 变化原因（券失效 / 价格上涨） | 「按当前价购买」，须二次确认 |
| 4 | coupon_gone 且 current ≤ target | 「券已失效，当前 ¥39.5 仍不高于你的目标价」 | 正常，无需二次确认 |
| 5 | notified &lt; current ≤ target | 「价格有变化：提醒时 ¥38，现在 ¥39.5」 | 正常；/open 返回 price_changed 时按 BR-PRICE-13 确认 |
| 6 | current ≤ notified | 「当前券后价 ¥38 · 取价 今天 08:05」 | 正常 |

金额按 BR-TEXT-10、时间按 BR-TEXT-11 格式化。第 4 行文案用「不高于」而非「低于」，因比较符为 ≤（current = target 时同样命中）。

- 例：提醒 ¥39，点击时实时 ¥45 → 第 3 行；本次首次点击计入误报（BR-WATCH-24）。
- 变化原因判定：coupon_fen 由 >0 变 0 → 券失效；price_fen 上升 → 价格上涨；两者都有则都写。
- 二次确认与 BR-PRICE-13 的衔接：第 1、3 行点购买先由落地页弹确认（文案即该行页面展示），用户确认后调用 /open；/open 返回 price_changed=true 且 new_final_price_fen 等于落地页刚展示的当前价时，客户端不再弹 BR-PRICE-13 弹窗，直接用返回链接外跳；不相等（期间又变价）或第 1 行（落地页无当前价）时按 BR-PRICE-13 再弹 1 次。第 4～6 行不由落地页弹窗，完全按 BR-PRICE-13 处理。复核失败的分支（requote_failed、50303）按 BR-PRICE-13。
- link_id 有效期与订单回流按 BR-ATTR（订单归属主题）。

#### BR-WATCH-17 细则 · 数量上限与可调配置

- 状态：默认假设
- 默认值：每用户 20 个；阈值全部配置化（表中键名与默认值）
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 开发任务拆解 v1 WT-09 / H-25：「watches 接口上限 20 个（D13 频控初值待定）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.19 通用规则；开发任务拆解_v1_2026-09-29.md WT-09；规划/10 §4.1「频率、上限、冷却可配置」
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

| 配置键 | 默认 |
|---|---|
| watch.enabled.&lt;platform> | false |
| watch.max_per_user | 20 |
| watch.price_drop.ttl_days / renew_grace_days / expiry_notice_days | 60 / 30 / 3 |
| watch.expiry_scan_minutes | 5 |
| watch.cooldown_hours | 24 |
| watch.new_low_min_drop_fen / _bp | 100 / 300 |
| watch.confirm_delay_minutes / confirm_min_gap_minutes / confirm_window_hours | 15 / 10 / 6 |
| watch.confirm_retry_minutes | [15, 30, 60] |
| watch.recheck_max_age_minutes / recheck_retry_minutes / recheck_give_up_minutes | 30 / [10, 30] / 120 |
| watch.suspect_drop_bp | 7000 |
| watch.unavailable_after_hours / unavailable_min_failures / unavailable_scan_minutes | 24 / 2 / 15 |
| watch.query_api_kind.&lt;platform> | 见 BR-WATCH-06 初值 |
| watch.pdd.goods_sign_plan | general（搜索/详情通用计划） |
| watch.tier.&lt;platform>.&lt;hot/default/cold>.interval_minutes | 120 / 360 / 1440 |
| watch.tier.hot.min_subscribers / min_changes_7d | 20 / 3 |
| watch.tier.cold.idle_days | 14 |
| watch.min_interval_minutes | 60 |
| watch.promo_mode / promo_speedup | false / 2 |
| watch.quota_share_bp | 500 |
| watch.confirm_card_ttl_minutes | 30 |
| watch.short_title_max_chars | 20 |
| watch.merge_window_minutes | 10 |
| notify.subscription.daily_push_cap | 5 |
| notify.quiet_hours | 22:00-08:00 |
| watch.cancelled_retention_days / expired_retention_days | 7 / 90（待法务） |
| price_snapshot.touch_min_interval_minutes | 10 |
| watch.alert.fetch_fail_rate_bp | 1000（单平台 1 小时） |
| watch.alert.false_alarm_bp / min_samples | 200 / 50 |
| watch.alert.quota_usage_bp | 9000 |

例：用户已有 18 active + 2 paused → 新建被拒；取消 1 个后可建；已有 20 个时续期 expired 提醒也被拒。

#### BR-WATCH-18 细则 · 创建须用户确认（Agent 与商品卡）

- 状态：默认假设
- 默认值：确认卡或设置面板 + 幂等创建；确认卡 30 分钟过期；POST 时重新报价
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 开发任务拆解 v1 WT-10：「cancel_watch：只出确认卡（未写修改与重复点击幂等）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.19 通用规则、WA-04、§10.20 第 11 条；开发任务拆解_v1_2026-09-29.md WT-10
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例（10 AC-S3-27）：用户说「伊利纯牛奶低于 50 提醒我」→ 若上下文无确定商品，Agent 先让用户选商品卡；选定 `tb:123` 后返回确认卡「淘宝 · 伊利纯牛奶 250ml×24 · 券后价 ≤ ¥50 时提醒 · 当前 ¥56.9（今天 14:02）· 约每 6 小时检查 · 站内信+推送 · 有效至 11-28」；此时 watch 表无记录；点确认后创建 1 条 active；连点两次仍 1 条。
- 例：14:20 确认时服务端报价 ¥49 → watch_target_already_met，卡片提示「当前已达到目标价」。
- 边界：用户只说品牌不指定商品 → 不创建 query 型提醒（属 P1-d），提示先选商品。
- 游客、未登录主体与平台开关关闭时 Agent 与商品卡如何处理，见 BR-WATCH-28。

#### BR-WATCH-19 细则 · MVP 预埋范围

- 状态：已确认（负责人 2026-09-30，依据 docs/changes/20260930-拍板第一批.md §2）
- 默认值：MVP 范围变更，需负责人确认：MVP 只预埋价格历史（不含用户标识、只写无用户参数的返回）、scene 枚举、通知分类；不建提醒表
- 决策人：负责人
- 依赖平台能力：联盟价格是否随 relation_id / 渠道 / 地区 / 买家身份变化（09 CAP-TB-13、CAP-JD-13、CAP-PDD-13）
- 取代：
  - 开发任务拆解 v1 WX-02：「MVP 契约预留 watch、tracked_item、tracked_query、watch_event、notification_pref 表结构；create_watch 工具 schema（开关关闭）；watch_confirm 卡片 schema」
  - 返利 App PRD v2.1 §10.21：「工具与表结构：create_watch 等工具 schema 和 watch 相关表写进契约，但默认用开关关闭」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §2 范围表、§10.17、§10.21；开发任务拆解_v1_2026-09-29.md WX-01～WX-03、砍项顺序；规划/09_平台能力验证/3_JD_京东.md CAP-JD-13、4_PDD_拼多多.md CAP-PDD-13；规划/10 §4.1；规划/00 §8
- 需同步修改的规划文档：4 处（计数仅作记录，落点见 README §0.6）

- 为什么只预埋这三项：价格历史事后无法补采；通知分类影响已上线用户的偏好数据与厂商通道申请；scene 枚举进入已发版客户端。其余表是新增表，P1 再建没有迁移成本，且业务规则尚待 S3 验证。
- 例：用户 09-30 查看 `tb:123` 详情返回 4500、10-01 另一次详情返回 4500、10-02 详情返回 3900、10-02 转链返回 3900（转链带 relation_id，09 未证实无关 → 不写）→ price_snapshot 两行：(detail, 4500, first 09-30, last 10-01, count 2)、(detail, 3900, first 10-02, last 10-02, count 1)；同一 source_kind 内才比较是否变化。
- 若 09 证实淘宝转链价与 relation_id 无关，则同例增加 (convert, 3900, first 10-02) 一行，共三行。
- 验收：同一商品同来源价格不变不新增行但 last_observed_at 前移（间隔 ≥10 分钟时）；变化时新增行；表中无用户标识列；压测下详情/转链 P95 与关闭钩子时相比差异 ≤ 5%。

#### BR-WATCH-20 细则 · 任务表模型为候选方案

- 状态：默认假设
- 默认值：方案 A（统一表 + 类型化 condition），S3 只校验 price_drop
- 决策人：代理可自定
- 依赖平台能力：无
- 取代：
  - 返利 App PRD v2.1 §10.20 第 1 条：「watch 表 target_kind（item / query / event / category）统一承载七类任务」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.20 第 1 条；规划/00 §8（重要架构决定写 ADR）

- ADR 模板：背景、选择、影响（迁移、后续类型扩展成本）。
- 例：若选 A，则 condition 对 price_drop 的 JSON Schema 为 {target_price_fen: int ≥1, comparator: 'le'}，其他 type 的 condition 在该 type 进入开发时再定义。

#### BR-WATCH-21 细则 · 有券/到货等提醒（S4）

- 状态：待验证
- 默认值：S4 再立项；PRD v2.1 初值仅作参考；提醒不得预占或发放淘礼金
- 决策人：负责人
- 依赖平台能力：三家联盟接口是否返回券面额/门槛/剩余量、库存/上下架状态（09 链路②⑤）
- 取代：
  - 返利 App PRD v2.1 §10.19：「coupon：从无券变有券或券面额变大，60 天；back_in_stock：重新可购买，30 天（列为 P1-a 同期交付）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.6、§10.19；规划/00_总览与决策.md D7；规划/10 §1 S4；规划/00 §8
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

| 类型 | 用户目标 | 依赖 | 未知项 |
|---|---|---|---|
| coupon | 商品出现券或券面额变大时提醒 | BR-WATCH-05 观测；联盟返回券信息 | 联盟是否稳定返回券面额、门槛、有效期、剩余量；「券变大」用面额还是券后价；券领完如何识别 |
| back_in_stock | 下架/无货商品重新可买时提醒 | in_stock 字段；not_found 错误码 | 三家接口是否返回库存/上下架；下架商品 ID 是否复用；预售算不算可买 |
| 淘礼金提醒（「有新的伊利淘礼金时提醒我」） | 出现符合条件的淘礼金商品时提醒 | D7 我方淘礼金池、素材淘礼金识别 | 属 item 型还是 query 型；是否算营销类 |

初值（PRD v2.1 §10.19，待 S4 确认）：coupon 有效期 60 天、入口为商品卡与 Agent；back_in_stock 有效期 30 天、入口为商品下架/无货时的卡片按钮（S3 期间 BR-WATCH-16 第 2 行不显示该按钮）。两类都按「订阅」类通知，与降价提醒共用 BR-WATCH-15 的每日订阅推送上限。

#### BR-WATCH-22 细则 · 大促/精选/复购/上新路线

- 状态：默认假设
- 默认值：只列目标、依赖与未知项，不开发；硬约束五条：① Agent 不得无用户确认创建任何主动推荐任务；② digest、replenish 须用户逐个确认创建，F-PRIV-04「个性化推荐」开关关闭时不生成新任务并立即停止已有任务；③ digest 每用户最多 3 个、最短间隔 1 天；④ replenish 只用本 App 历史订单；⑤ new_arrival 首次运行只建基线不发提醒。通知分类：精选、上新、复购为营销类，大促为订阅类
- 决策人：负责人
- 依赖平台能力：无
- 取代：无
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.17、§10.19、§10.20 第 8–10 条、§15；规划/01_需求规划.md F-PRIV-04；开发任务拆解_v1_2026-09-29.md WT-15～WT-18

| 类型 | 目标 | 依赖 | 未知项 |
|---|---|---|---|
| promo_calendar | 大促节点前 N 分钟准时提醒，可写系统日历 | 运营录入 promo_event；日历授权 | N 默认值；准时率 100% 的测量口径；PRD v2.1「大促提醒可由用户设为不受免打扰限制」是否采用（与 BR-WATCH-15 免打扰规则的关系） |
| digest | 按用户时间推送保存检索的好价 | tracked_query 规范化与哈希；模板文案 | 是否需算法推荐备案（法务）；是否用模型生成摘要 |
| replenish | 按个人购买间隔提醒复购 | 订单品类数据（同品类 ≥2 单，间隔中位数，到期前 2 天建议） | 品类口径；是否需算法推荐备案 |
| new_arrival | 品牌/关键词出现新商品时提醒 | 联盟「最新」排序检索、query_seen_item、规则过滤 + 批量小模型相关性 | 相关性抽检 ≥90% 的抽样方法；配额成本；所用模型是否在已备案/登记的生成式 AI 服务范围内（法务，06 F 节） |

PRD v2.1 初值（仅参考，立项时定）：digest 90 天可续，new_arrival 90 天，replenish 持续可关，promo_calendar 到事件结束；营销类推送（精选、上新、复购）每人每日 2 条，按 +08:00 自然日计。MVP 已有的营销类只受 F-MSG-04「22:00–08:00 不发」约束，本主题不为 MVP 营销推送增设条数上限。
创建入口（PRD v2.1 §10.19，仅参考）：promo_calendar 为大促日历页与 Agent；digest 为 Agent 与精选设置页；replenish 为订单详情与系统建议卡（需个性化授权）；new_arrival 为 Agent。

#### BR-WATCH-23 细则 · 数据来源、隐私与合规

- 状态：待决策
- 默认值：用户删除 7 天内物理删除或去标识；到期 90 天后删除；关联记录同期删除；注销即暂停、冷静期结束删除
- 决策人：法务
- 依赖平台能力：无
- 取代：无
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.20 第 4、11 条、§15；规划/01_需求规划.md F-PRIV-08、F-ACC-10
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 例：用户 10-01 在「我的提醒」删除提醒 → 立即 cancelled、列表不展示、不再查询；10-08 前物理删除。
- 例：提醒 11-28 到期未续 → 次年 02-26 删除。
- 例：用户注销 → 提交时 paused，冷静期结束同批删除。
- 隐私政策需新增条目：收集的数据（关注的商品、目标价、提醒时间）、用途（价格提醒）、保存期限（删除后 7 天、到期后 90 天，待法务确认）。

#### BR-WATCH-24 细则 · 监控指标与误报率

- 状态：默认假设
- 默认值：误报率按 notification 去重、7 天滚动、按平台、阈值 2%、最小样本 50；样本不足不扩量
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 返利 App PRD v2.1 §10.20 第 12 条：「误报率=点击时实际价格高于提醒价的比例（未定义窗口、分母、样本量）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.20 第 12 条、§14.5、§17；开发任务拆解_v1_2026-09-29.md WT-13
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：某周淘宝提醒 notification 被首次点击 400 条，实时报价成功且有价格 380 条（另 12 条下架、8 条查询失败），其中 6 条当前价高于投递价 → 误报率 6/380 = 1.58%，未超阈值；同一条被点 3 次只算 1 次。
- 抓取失败率告警默认：单平台 1 小时失败率 > 10%（watch.alert.fetch_fail_rate_bp）。
- 数据来源：price_observation（source=click_quote）+ watch_event + notification + push_digest。
- 点击→下单转化（以 notification 为单位去重）：分母 = 7 天滚动窗口内（按首次点击时间）其 scene=watch_alert 的 link_id 至少一次经 /open 成功外跳的 notification 数；分子 = 其中有订单归因到该 link_id 或其经 BR-PRICE-13 派生的 new_link_id、且订单 platform_status ∈ {PAID, RECEIVED, SETTLED}（BR-FUND-01 双状态模型的平台状态，不看 rebate_status；统计时刻取当前值）的 notification 数；DEPOSIT_PAID 与 INVALID 不计；订单归因到哪个 link 按 BR-ATTR。映射说明：若回退到 规划/04 单一 order_status（O1–O12 编号体系），同一口径写作 order_status ∈ {PAID, RECEIVED, CREDITED, SETTLED}，外加联盟状态未失效的 CLAWED_BACK（单状态下 CLAWED_BACK 不区分平台状态，需另查联盟状态），换算按 BR-FUND-01「与单一 order_status 的映射」。按 C-01 默认处理，已由负责人确认 2026-09-30。

#### BR-WATCH-25 细则 · 降价提醒验收用例

- 状态：默认假设
- 默认值：S3 出门条件以 规划/10 §1 S3 为准（§4 用例 AC-S3-01…40 三家各跑一次、按平台独立判定，判定口径见 10 §0.6）；扩大放量另需 7 天有效样本 ≥50 且误报率 &lt;2%（BR-WATCH-24），不属于用例通过条件。旧编号 WA-01…29（= AC-WATCH-01…29）已并入 AC-S3-nn，对应见 10 §5.4；WA-01～06 与 PRD v2.1 同号用例同名，内容以 10 §4 为准
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 返利 App PRD v2.1 §10.19 验收用例：「WA-01～WA-06（未覆盖查询失败、取消、到期、点击价格回升、幂等、上限）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.19 验收用例、§17；规划/10 §1 S3、§4.2
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 用例表已移入 规划/10 §4.2（2026-09-30 合并，WA-01…29 → AC-S3-nn，逐条对应见 10 §4.2「对应」列与 §5.4）；本节不再列用例，修改用例只改 10。
- 验收证据代码与存放路径按 10 §0.4（S3 主要为 price_observation / watch_event / notification / push_digest 记录查询结果）。错误码断言写成「返回该数字码且 data.reason=&lt;reason>」，码值见 13 §13.11。

#### BR-WATCH-26 细则 · S3 范围与后续分期

- 状态：已确认（负责人 2026-09-30，依据 docs/changes/20260930-拍板第一批.md §2）
- 默认值：S3 只做目标价模式；降幅模式、观察最低价标签、有券/到货延到 S4；P1-b/c/d 只列目标。理由：S3 只验证一条确定规则
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 返利 App PRD v2.1 §10.17：「降价提醒、有券提醒、到货提醒同属 P1-a 一次交付」
  - 返利 App PRD v2.1 §10.19 任务类型：「或未设目标时，较上次提醒价下降 ≥5% 且 ≥2 元；或出现自 &lt;开始记录日> 以来观察到的最低价」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.17、§10.19；规划/00_总览与决策.md §4；规划/10 §1；规划/00 §8
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

| 类型 | 阶段 | 本文细化程度 |
|---|---|---|
| price_drop 目标价模式 | P1-a / S3 | 完整规则 BR-WATCH-02～18、24、25、27、28、29 |
| price_drop 无目标价降幅模式、观察到的最低价标签 | S4（按 S3 误报率数据再定） | 只写目标 |
| coupon、back_in_stock、淘礼金提醒 | P1-a 后续 / S4 | BR-WATCH-21 |
| promo_calendar、digest、replenish、new_arrival | P1-b/c/d | BR-WATCH-22 |

- 默认理由：S3 只验证一条确定规则；降幅模式需要额外的基线定义与文案，观察最低价标签涉及价格比较表述合规（BR-WATCH-14），放到 S4 按 S3 误报率数据决定。
- P1-a/b/c/d 分期来自 PRD v2.1（已降为参考），需负责人确认后生效。

#### BR-WATCH-27 细则 · 按平台开关的放量与关停

- 状态：默认假设
- 默认值：watch.enabled.&lt;platform> 独立开关；关停保留 watch、停查询与发送、顺延有效期
- 决策人：负责人
- 依赖平台能力：无
- 取代：无
- 来源：规划/00 D24（按平台开关独立放量）；规划/05 按平台放量
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：京东 10-10 00:00 关停、10-12 00:00 恢复 → 京东 active 提醒 expires_at 顺延 48 小时，10-12 00:00 起各 tracked_item next_fetch_at = now；关停期间 10-10 09:00 待推送的京东事件 suppressed(platform_disabled)，按 BR-WATCH-11 恢复 armed。
- 关停时长记在 watch_platform_switch_log（platform、off_at、on_at），顺延按该记录计算。

#### BR-WATCH-28 细则 · 创建入口与前置条件

- 状态：默认假设
- 默认值：S3 入口只有商品卡类按钮与 Agent；需登录（未绑手机可用、不需实名）；游客在 Agent 中得到登录卡而非确认卡；推送权限不是前提
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 返利 App PRD v2.1 §10.19 任务类型「创建入口」列：「price_drop：商品卡「降价提醒」按钮；对 Agent 说「低于 40 告诉我」（未写身份要求、按钮显示条件、推送权限未开时的处理）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.19 任务类型、通用规则；规划/01 F-MSG-01～04；08 BR-ID-02、BR-ID-10、BR-ID-13、BR-AI（订单类工具主体过滤）；规划/10 §4.1（前置）

| 情形 | 商品卡按钮 | 点击 / 调用结果 |
|---|---|---|
| 已登录，平台开关开，商品可购买，当前券后价 ≥ 2 分 | 显示 | 打开设置面板 |
| 未登录（游客） | 显示 | 拉起登录；pending_action = 打开该商品设置面板；登录成功后打开面板，不自动创建 |
| 基本模式（未同意隐私政策） | 显示 | 按 BR-ID-02 重新展示隐私弹窗 |
| watch.enabled.&lt;platform>=false 或 convert.enabled.&lt;platform>=false | 不显示 | 接口直调返回 30806 watch_platform_disabled（BR-WATCH-27） |
| 下架 / 无货 / price_unavailable / product_key=null | 不显示 | 接口直调：product_key=null 返回参数错误 20001；其余按创建时实时报价（BR-WATCH-07）返回 30805 watch_quote_unavailable 或 30801 watch_target_already_met |
| 未开启系统推送权限 | 显示 | 可创建；「通道」显示「仅站内信（未开启通知）」 |

- 例：游客在 Agent 中说「这个低于 50 提醒我」→ auth_required 卡（reason=login）+ 固定话术 agent.need_login；计配额与 run 结束方式同订单类意图的 auth_required（BR-AI 工具表「订单类工具的主体过滤」）；登录后用户需重新发起，Agent 不自动续做。
- 例：已登录未绑手机用户可创建提醒；提醒不涉及资金，不要求绑手机或实名。
- 身份等级名称、10001 码与 pending_action 结构以 BR-ID-01、BR-ID-02、BR-ID-10 为准，本条只规定提醒功能的最低等级。
- 选择理由：提醒要长期推送到账号、跨设备在「我的提醒」管理，必须归属到 user_id；游客用 device_id 持有提醒会在登录合并、换机时丢失。

#### BR-WATCH-29 细则 · 「我的提醒」页

- 状态：默认假设
- 默认值：两组列表、按创建/到期时间倒序；状态文案按优先级取一；操作按状态矩阵；取消须二次确认
- 决策人：负责人（排序、分页大小、版式代理可自定）
- 依赖平台能力：无
- 取代：
  - 返利 App PRD v2.1 §10.19 通用规则：「「我的提醒」页：列表、暂停、修改目标价、删除；到期前 3 天提示续期（未定义列表范围、状态文案优先级、各状态可用操作、删除与取消的关系）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.19 通用规则；本主题 BR-WATCH-02、07、09、10、16、17、23、27

**状态或价格文案**（自上而下取第一个命中的行）：
| 顺序 | 条件 | 文案 |
|---|---|---|
| 1 | watch.enabled.&lt;platform>=false 或 convert.enabled.&lt;platform>=false | 「该平台提醒暂停服务」（BR-WATCH-27） |
| 2 | expired，now − expires_at ≤ watch.renew_grace_days | 「已过期，可续期」 |
| 3 | expired，超过宽限期 | 「已过期」 |
| 4 | paused | 「已暂停」 |
| 5 | unavailable(item_unresolved) | 「商品信息已变化，请重新选择商品」 |
| 6 | unavailable(fetch_failed) | 「暂时无法获取价格（最近成功 {last_ok_at}）」 |
| 7 | active 且 tracked_item.last_in_stock=false | 「商品已下架或无货」 |
| 8 | active 且 now − tracked_item.last_observed_at > 1.5 × 当前层级间隔 | 「¥{last_final_price} · 更新于 {last_ok_at} · 检查可能延迟」（BR-WATCH-07） |
| 9 | active | 「¥{last_final_price} · 更新于 {last_ok_at}」 |

金额按 BR-TEXT-10，时间按 BR-TEXT-11 列表过去时间规则。第 6、7、9 行即 BR-WATCH-09 页面展示表的各情形，本表规定它们与其他情形同时成立时的取用顺序。

**可用操作**（未列出的操作不显示；平台关闭时以第 1 行为准，覆盖其他行）：
| 顺序 | 条件 | 可用操作 |
|---|---|---|
| 1 | 平台开关关闭，状态非 expired | 暂停（仅 active、unavailable）、取消 |
| 2 | active | 改目标价、暂停、续期、取消 |
| 3 | paused | 恢复、改目标价、续期、取消 |
| 4 | unavailable(fetch_failed) | 改目标价、暂停、续期、取消 |
| 5 | unavailable(item_unresolved) | 重新选择商品、取消 |
| 6 | expired，宽限期内 | 续期、删除 |
| 7 | expired，超过宽限期 | 重新设置、删除 |
| 8 | 平台开关关闭，状态 expired | 删除 |

- 「重新选择商品」：弹确认「将取消本提醒，并按商品名搜索」→ 确认后 DELETE 本条（cancelled）→ 打开搜索页，关键词 = 短标题去掉末尾「…」；用户选定商品后按 BR-WATCH-28 正常新建。
- 「重新设置」：打开该商品设置面板，按 BR-WATCH-02 新建（超过宽限期可新建），旧 expired 记录保留到按 BR-WATCH-23 删除。
- 「删除」与「取消」都是迁移到 cancelled，文案按状态区分（expired 显示「删除」，其余显示「取消」）。
- 「N 天后到期」：N = expires_at 的 +08:00 日期 − 今天（+08:00）的日历日差，1 ≤ N ≤ watch.expiry_notice_days 时显示；N = 0 显示「今天到期」。例：expires_at 11-28 10:00，11-25 显示「3 天后到期」，11-28 09:00 显示「今天到期」，11-28 10:00 后按 BR-WATCH-10 置 expired。
- 例：用户有 20 个进行中提醒 → 页顶「已设 20 / 20」，商品卡设置面板提交返回 watch_limit_exceeded（BR-WATCH-17）；已过期条目不计入 X。
- 例：京东开关关闭时京东 paused 条目只显示「取消」；开关恢复后按正常矩阵显示。

### 9.3 本主题未决问题

1. 比较符最终用 ≤ 还是 &lt;，以及实时价已 ≤ 目标价时是拒绝创建还是允许创建但不立即提醒（BR-WATCH-04，默认 ≤ + 拒绝）
2. S3 范围：是否只做目标价模式，降幅模式与观察最低价标签、有券/到货是否延到 S4，P1-b/c/d 分期是否沿用（BR-WATCH-26）
3. MVP 是否增加价格历史预埋与通知分类（BR-WATCH-19，MVP 范围变更）
4. 订阅类频控初值（5 条/日、首条立即 + 10 分钟合并、[22:00, 08:00) 免打扰）与 F-MSG-04 改动（BR-WATCH-15）；PRD v2.1「D13 频控」需在决策映射表中重新编号
5. 三家联盟券后价是商品级还是 SKU 级、多规格取值；某平台可稳定取 SKU 级价时是否在 S3 启用 sku_key（09 验证）
6. 跨用户共享查价是否成立（价格是否随 relation_id / 地区 / 买家身份变化），不成立的平台 watch.max_per_user 下调到多少（BR-WATCH-08、09 CAP-TB-13/JD-13/PDD-13）
7. 各平台提醒口径接口（watch.query_api_kind）的最终选择，以及它与点击购买时转链接口券后价的一致率；拼多多 goods_sign 计划能否固定为通用计划
8. 三家联盟接口是否返回运费、库存/上下架状态，「商品不存在」与系统错误的错误码能否可靠区分（BR-WATCH-03、09、21）
9. 提醒配额桶比例（默认 5%）与三家日配额、QPS、批量上限；京东、拼多多在 规划/06 G 节尚无对应外部确认项
10. 各安卓厂商与鸿蒙 Push Kit 对「服务/订阅」类消息的资质、每日条数限制，以及是否支持按业务 message_id 去重（W0–W2 核实）
11. 提醒数据保留期（用户删除 7 天、到期 90 天）与删除方式需法务确认；提醒文案的被比较价格表述、观察最低价标签需法务确认；digest、replenish 是否需要算法推荐备案，new_arrival 所用模型是否在已备案服务范围内
12. 创建提醒的最低身份（BR-WATCH-28，默认已登录即可、不要求绑手机与实名）；需在 BR-ID-02 身份能力矩阵补「订阅提醒」行
13. 目标价输入是否放宽为「去末尾 0 后最多两位小数」（如「40.500」）：本文按 BR-PRICE-01 parseYuanToFen 严格口径拒绝；如需放宽，应修改 BR-PRICE-01 而不是在本主题另写解析规则

---
