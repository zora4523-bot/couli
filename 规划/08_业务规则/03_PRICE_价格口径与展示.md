# 08 业务规则 · 3. 价格口径与展示（BR-PRICE）

返回 [README](README.md)（使用规则、术语表、规则索引）

## 3. 价格口径与展示（BR-PRICE）

本节规定：券前价/券后价/预估返利/预估返后价的计算与展示、取价时间与缓存、点击复核与价格变动、禁用词。共 21 条（已确认 1、默认假设 11、待决策 6、待验证 3）。

### 3.1 规则一览

| 编号 | 规则 | 状态 | 影响面 |
| --- | --- | --- | --- |
| BR-PRICE-01 | **价格三字段定义与计算**<br>商品价格只用三个整数分（int64，_fen）字段表达，全部指「默认 SKU、购买 1 件、联盟接口返回」的价格：price_fen = 券前价（平台当前售价，未扣任何券）；coupon_fen = 本 App 转链后可用的券面额（选券规则见细则），没有可用券时等于 0；final_price_fen = 券后价 = price_fen − coupon_fen，这个恒等式在任何情况下都必须成立。计算只能在服务端 UnionAdapter + packages/domain 完成，禁止浮点，客户端不得重算。元字符串转分只能用 packages/domain.parseYuanToFen()：按字符串做十进制解析，最多两位小数；超过两位小数、非数字、空串、负数一律视为字段缺失，不得四舍五入。final_price_fen 一律自算；平台返回的券后价类字段（如淘宝 final_promotion_price、京东 lowestCouponPrice）只存原始报文，与自算值相差 ≥1 分时记日志 PRICE_CALC_DIFF。某个平台字段只有经 BR-PRICE-02 实测确认口径与本条一致、列入 specs/union/&lt;platform>.md 的「平台券后价白名单」（初始为空）并在规划/09 登记后，才可以以它为准，此时 coupon_fen 记为 price_fen − 该字段值，保持恒等式。price_fen 缺失、coupon_fen ≥ price_fen 或 final_price_fen ≤ 0 时按数据异常处理：记告警 PRICE_ANOMALY，不得把缺失价格当 0 元；检索类场景（搜索、feeds、Agent 检索）该商品不出卡；inputs/parse、rebate_quote 出一张 availability=price_unavailable 的卡，不显示任何金额，文案「暂时查不到该商品价格」，按钮「稍后再试」，不下发 link_id；open 复核时新价格异常，按 BR-PRICE-13 的复核失败分支处理。 | 默认假设 | product_card.price_fen / coupon_fen / final_price_fen；product_card.availability（新增 price_unavailable）；packages/domain.parseYuanToFen()；GET /v1/products/search；GET /v1/products/{product_key}；POST /v1/inputs/parse；Agent product_list / rebate_quote 卡片；price_snapshot 表；UnionAdapter.&lt;platform>；specs/union/&lt;platform>.md 平台券后价白名单；验收：券门槛、多券选择、过期券、金额解析、价格缺失用例 |
| BR-PRICE-02 | **各平台取价字段映射**<br>UnionAdapter 必须按平台把联盟返回映射到 BR-PRICE-01 的三个字段。映射表以 S0 实测的接口样例为准（样例存 specs/union/&lt;platform>.md）。对照通过的条件：用一个无会员身份（非 88VIP、非 PLUS）的测试账号，抽取 ≥20 个商品（有券、无券各 ≥5 个），下单页单件、默认 SKU、不含运费、不勾选平台红包和淘金币等可选优惠时的券后价，与 final_price_fen 全部一致（误差 0 分）；任何一个不一致即判不通过，修正映射后整批重测；证据截图与接口报文存 specs/union/&lt;platform>.md，由负责人签字。对照通过前，该平台的 convert.enabled.&lt;platform> 不得开启。默认映射：淘宝 price_fen 取折扣价 zk_final_price，不取一口价 reserve_price；final_promotion_price 等预估到手价类字段只存原始报文。京东 price_fen 取 priceInfo.price，lowestPrice、lowestCouponPrice 只存原始报文；券从 couponInfo.couponList 按 BR-PRICE-01 的选券规则选取。拼多多 price_fen 取拼单价 min_group_price，不取单买价 min_normal_price，卡片标签按 BR-PRICE-04 显示「拼单」字样。 | 待验证 | UnionAdapter.taobao / jd / pdd；specs/union/&lt;platform>.md；规划/09 平台能力验证表；配置 convert.enabled.&lt;platform>；前端组件 PriceTag（拼单文案）；验收：价格与下单页对照用例 |
| BR-PRICE-03 | **运费与平台外优惠不计入**<br>price_fen、final_price_fen、预估返后价都不得包含运费，也不得包含只在下单页才生效的优惠，包括 88VIP 价、京东 PLUS 价、淘金币抵扣、跨店满减、店铺会员价、平台红包和补贴满减、第三方淘礼金。凡是展示券后价的地方，disclaimer_keys 都必须包含 price_basis，文案为「券后价按单件计算，不含运费及会员价、跨店满减等优惠，以下单页为准」（配置下发，见 BR-PRICE-17）。呈现形式：商品详情页、分享海报、分享中间页常驻显示全文；搜索列表、首页物料流和 Agent 卡片流每屏在列表底部显示一次全文，单张卡只放 i 图标，点击展开全文。联盟返回包邮标识时可以显示「包邮」标签，但不得据此把运费加减进任何价格字段。 | 默认假设 | product_card.disclaimer_keys；商品详情页、搜索卡、Agent 卡、分享海报、分享中间页口径说明；前端组件 DisclaimerFooter / i 图标；订阅提醒（Watch）价格口径；客服话术：「为什么下单价和 App 显示的不一样」；配置：文案键 price_basis |
| BR-PRICE-04 | **券前价与售价标签**<br>price_fen 在所有用户可见处一律标为「券前价」或「券前 ¥x」，不得使用「原价」「划线价」「日常价」等字样，也不得用删除线样式，因为本 App 无法证明该价格就是平台促销前的成交价。coupon_fen > 0 时，主价标「券后 ¥x」（final_price_fen），副行「券前 ¥x · 券 ¥y」（不划线）。coupon_fen = 0 时只显示一个价格，标为「售价 ¥x」，不带「券后」字样，并显示无券状态。拼多多卡片（price_fen 取拼单价，BR-PRICE-02）：有券时主价「拼单券后 ¥x」、副行「拼单券前 ¥x · 券 ¥y」；无券时「拼单价 ¥x」；benefit_tags 不再重复加「拼单价」标签。 | 待决策 | 前端组件 PriceTag；商品详情页、搜索卡、Agent 卡、分享海报；分享文案模板变量；禁用词清单（BR-PRICE-18）；术语表（BR-PRICE-05）；验收：PriceTag 快照测试（有券、无券、拼多多有券无券） |
| BR-PRICE-05 | **价格术语统一**<br>界面、接口文档、客服话术必须使用以下固定术语：券前价 = price_fen（coupon_fen>0 时展示）；售价 = coupon_fen=0 时 final_price_fen 的展示名；券 / 券面额 = coupon_fen；券后价 = coupon_fen>0 时的 final_price_fen；预估返利 = rebate_min_fen–rebate_max_fen，界面短标签只允许「预估返」且后面直接接金额；分享预估赚 = App 内分享面板给分享者看的推广收益估算（BR-PRICE-06）；预估返后价 = est_net_price_fen（BR-PRICE-09），界面短标签「预估返后」；素材参考价 = material.claimed_price_fen（BR-PRICE-10）。拼多多在券前价、券后价、售价前加「拼单」（BR-PRICE-04）。其他简称一律不允许。界面上不得把「到手价」或「接口到手价」用作价格标签，因为 final_price_fen 不含运费和下单页优惠，不等于用户实际付的钱。「返利后到手价透明」只作卖点表述，落到界面上就是预估返后价。 | 默认假设 | 规划/01、03、04 文案；配置中心文案键（F-CFG-06）；客服话术；Agent 系统提示词里的术语表；验收：界面文案检查 |
| BR-PRICE-06 | **预估返利计算口径**<br>本条只管展示对象与 buy_type，计算不在本条维护：报价 = splitCommission(quoteN) 的本人份额，见 BR-CALC-20（N_quote 定义、技术服务费、取较低值、向下取整、规则版本与查看者等级都以 BR-CALC-20 为准）。rebate_min_fen / rebate_max_fen 由 packages/domain.quoteRebate() 按 BR-CALC-20 输出，不得另写估算逻辑。展示对象与 buy_type：搜索卡、详情、inputs/parse、Agent 卡用 buy_type=self，显示「预估返 ¥x」（查看者等级，游客按 BR-CALC-20 的注册默认等级）；buy_type=share 的金额只在 App 内分享面板给分享者本人看（查看者即分享者），文案「分享预估赚 ¥x」，对应推广收益账户（规划/01 J8、F-ORD-04）；分享中间页、海报、分享文案一律不显示任何返利金额，也不显示预估返后价。只展示查看者本人份额。零值展示见 BR-PRICE-08，比价区间见 BR-PRICE-07，金额格式与口径说明文案见 BR-PRICE-17。下单后订单详情只展示基于快照的预估，不与报价比较，页面不得承诺报价金额。 | 待决策 | packages/domain.quoteRebate() / splitCommission()；product_card.rebate_min_fen / rebate_max_fen；App 内分享面板（分享预估赚）；分享中间页、海报、分享文案（不显示返利）；specs/commission-examples.csv 参数化测试；配置：tech_fee_bp[platform]、commission_rules.r_own_bp[platform][level][order_type]（BR-CALC-06；别名 r_self_bp，C-29）、（待决策，BR-CALC-02）reserve_bp；验收：同输入时展示报价 = 入账预估 |
| BR-PRICE-07 | **比价风险与返利区间**<br>MVP 只对 platform=taobao 展示比价区间；拼多多是否存在比价降佣待 CAP-PDD-04（09 附录 A-14），结论为存在时按本条同样规则扩展。有比价预判定权限时，以 link_log.compare_risk 为准；权限存在但结果尚未返回时，先按无权限规则判定，拿到结果后在 open 响应中更新 rebate_\*。无权限时（M-内测默认）按 entry_source 判定：inputs/parse（粘贴链接或口令）、搜索、Agent 卡（含换一批）判为 price_compare_risk；首页物料流、商品池、淘礼金商品池、分享面板与分享中间页判为 normal；商品详情页和由卡片派生的请求继承来源卡片 link 记录的 entry_source，没有来源卡片（直接打开详情）时判为 price_compare_risk；订阅提醒点击继承创建提醒时来源卡的 entry_source，无法确定时判为 price_compare_risk。rebate_basis=normal 时 rebate_min_fen = rebate_max_fen，显示「预估返 ¥x」。rebate_basis=price_compare_risk 时，rebate_max_fen 按正常佣金率计算，rebate_min_fen 按「正常佣金率 × rebate.taobao.compare_rate_ratio_bp / 10000」计算（算法同 BR-CALC-20），显示「预估返 ¥a–¥b」，disclaimer_keys 含 rebate_compare（「以结算为准」）。rebate_min_fen=0 且 rebate_max_fen>0 时仍为 price_compare_risk，显示「预估返 ¥0–¥x」；只有 rebate_max_fen=0 时才判为 no_rebate。不得只显示上限，也不得在区间以外另显示一个「保守值」。下单前比价展示只在本条维护，BR-CALC-16 只管订单侧计算；compare_rate_ratio_bp 占位值不得用于运营素材、客服话术或对外宣传（C-22，默认处理，待负责人确认，财务知悉）。 | 待验证 | product_card.rebate_basis / rebate_min_fen；links.entry_source（新增）；link_log.compare_risk；orders.is_price_compare、commission_rate_min_bp / max_bp；前端组件 RebateTag；配置 rebate.taobao.compare_rate_ratio_bp；disclaimer_keys: rebate_compare；验收：至少 1 笔比价订单三处一致（F-ORD-11）；详情继承来源用例 |
| BR-PRICE-08 | **无返利与淘礼金返利展示**<br>rebate_max_fen = 0 时，rebate_basis 必须为 no_rebate。搜索、首页物料流、Agent 检索结果必须过滤掉 no_rebate 商品（不采用「标无返利放最后」这个选项）；淘礼金商品池里的商品不受这条过滤限制。过滤后不足 page_size 时，最多向上游补拉 1 页补足，仍不足就按实际数量返回；has_more 以上游返回为准；分页游标记录上游页码，不记录过滤后的偏移量。用户主动粘贴或分享的链接和口令（inputs/parse、rebate_quote）即使无返利也照常出卡：显示「暂无返利」，按钮为「去购买（无返利）」。「去购买（无返利）」的目标：转链成功但佣金为 0 时用转链结果；转链失败时，跳到由 product_key 生成、不带任何推广参数的平台商品页；不得原样外跳用户粘贴的链接或口令（可能带其他推广者的推广位），不得把原链接当作返利链接返回；该按钮不显示任何预估返利，也不写 links 报价快照。淘礼金（我方或 A/B 类）商品默认不叠加自购返利（后台可按商品配置），此时 rebate_basis=no_rebate，文案为「淘礼金商品不叠加返利」。淘礼金金额只放在 tlj.amount_fen 字段里（随卡下发 tlj.amount_fen、tlj.remain、tlj_kind，cta 类型为 claim_tlj / claim_tlj_and_buy），不得从 final_price_fen 或 est_net_price_fen 中扣减；淘礼金卡的标签、按钮与说明文案见 BR-TEXT-15。C 类淘礼金卡按普通返利计算，不得打「淘礼金」标签。 | 默认假设 | product_card.rebate_basis / tlj；GET /v1/products/search、feeds 过滤与分页游标；POST /v1/inputs/parse；Agent search_products / get_rebate_quote；前端 RebateTag、CTA 文案键；验收：三态卡片用例、淘礼金卡用例、补拉分页用例、无返利购买不外跳原链接用例 |
| BR-PRICE-09 | **预估返后价**<br>est_net_price_fen = final_price_fen − rebate_min_fen（取区间下限），只在服务端计算，并在 product_card 中下发。只有 rebate_basis ≠ no_rebate 且 rebate_min_fen > 0 时才显示，文案为「预估返后 ¥x」，并且必须同时显示 disclaimer_keys 中的 rebate_estimate（price_compare_risk 时为 rebate_compare），文案键与默认文案见 BR-PRICE-17。分享中间页、海报、分享文案不显示预估返后价（BR-PRICE-06）。预估返后价不得参与价格筛选、排序、降价提醒触发和「价格已变动」判定，这些一律只用 final_price_fen。 | 待决策 | product_card.est_net_price_fen（新增）；前端组件 PriceTag / RebateTag；商品详情页、搜索卡、Agent 卡；disclaimer_keys: rebate_estimate / rebate_compare；验收：返后价计算用例、min=0 不显示用例 |
| BR-PRICE-10 | **素材参考价**<br>material.claimed_price_fen 只取自用户粘贴的素材或文案，属于不可信的对照信息，只能出现在素材场景的 rebate_quote 卡上，作为第二行显示：「素材参考价 ¥x（需 &lt;conditions>，仅供参考，以下单页为准）」，该卡 disclaimer_keys 含 material_ref。它不得写入 final_price_fen 或 est_net_price_fen，不得参与筛选、排序、降价提醒、「价格已变动」判定和分享海报，也不得被模型当作报价复述。解析不出数值、数值 ≤ 0，或 conditions 为空时，不显示这一行。卡片主价仍然是联盟接口的券后价。 | 待决策 | rebate_quote.material.claimed_price_fen / conditions[]；前端 rebate_quote 渲染器；Agent 输出过滤（不复述金额）；disclaimer_keys: material_ref；配置 material_ref.enabled（默认 true，待法务结论）；验收：素材价不写入 final_price_fen |
| BR-PRICE-11 | **取价时间与缓存有效期**<br>quoted_at 等于服务端收到该价格所依据的联盟接口响应的时刻（ISO 8601，+08:00）。命中缓存时必须沿用原 quoted_at，不得改写成当前时间。搜索和详情缓存只存 UnionAdapter 归一化后的价格与券字段（含 quoted_at），缓存键不含用户信息；rebate_\*、est_net_price_fen 和整张卡片每次请求按当前用户与来源重新计算和组装，不得缓存组装好的卡片。有效期：搜索和详情缓存 TTL = 300 秒（search.cache_ttl_sec）；商品池价格每 3600 秒刷新一次（pool.refresh_interval_sec），卡片的 quoted_at 取最近一次成功刷新时间；商品池价格 age > 7200 秒（pool.max_age_sec）时不得展示。联盟超时或限流时，只能返回 age ≤ 300 秒的缓存并标 stale=true；超过 300 秒的缓存不得返回，此时改走商品池降级（结果一律 stale=true），商品池也没有合格数据时提示「××平台暂时查不到」。age 由服务端按响应时刻计算，随卡片下发 age_sec，客户端不用本机时钟判断。客户端展示：详情页显示「取价 HH:mm」（按 +08:00；不是当天则显示 MM-DD HH:mm）；当 age_sec > 300 或 stale=true 时，追加「价格可能已变化，以下单页为准」。 | 默认假设 | product_card.quoted_at / stale / age_sec；搜索与详情缓存（缓存内容与键）；商品池刷新任务；规划/02 §14 降级；商品详情页、卡片的取价时间显示；配置 search.cache_ttl_sec、pool.refresh_interval_sec、pool.max_age_sec；验收：缓存命中不刷新 quoted_at；缓存不串等级；商品池超龄不展示 |
| BR-PRICE-12 | **报价快照、比较基准与 link 归属**<br>每次向客户端渲染一张带价格的卡（含详情页刷新、换一批、open 响应里的新价格），都必须随卡下发一个 link_id，该 link 的报价快照（quoted_final_price_fen、quoted_coupon_fen、quoted_coupon_id、quoted_at）写入后不可修改；价格变化时一律新建 link_id，客户端用新 link_id 替换卡片。同一 user_id（游客用 device_id）、product_key、entry_source 且快照价格相同、未过期的 link 可以复用（代理可自定）。异步预转链拿到的价格只能写入 preconvert_final_price_fen 与 preconvert_at，不得覆盖快照。T1（用户粘贴的链接或口令输入）以及排名第 1 的卡，必须在出卡前同步转链；同步转链返回价格时卡片价格取转链返回价，不返回价格或超时（link.sync_convert_timeout_ms，默认 2000 毫秒，代理设定的初值，S0 按各平台转链实测时延校准；耗时 ≥ 该值即判超时）时取检索价或详情价；其余卡片后台异步预转链。游客下发的 link 行 user_id 为空、不做转链，只保存报价快照。open 时的归属校验按 BR-ATTR-05；为他人 link 新建 link 时比较基准沿用原 link 的 quoted_final_price_fen（G-08，默认处理，待负责人确认）。 | 默认假设 | links 表：quoted_final_price_fen、quoted_coupon_fen、quoted_coupon_id、quoted_at、preconvert_final_price_fen、preconvert_at、entry_source；CardAssembler（link 新建与复用）；配置 link.sync_convert_timeout_ms；POST /v1/links/{link_id}/open（归属校验见 BR-ATTR-05）；规划/02 §9.2；验收：预转链不改写比较基准；旧卡按旧快照比较；A 的 link 由 B 打开时订单归 B |
| BR-PRICE-13 | **点击复核与价格已变动**<br>POST /v1/links/{link_id}/open 必须在外跳前复核价格。old 固定取该 link 的 quoted_final_price_fen（BR-PRICE-12）。new 默认每次实时调用转链或详情接口取得（规划/01 J3、规划/02 §9.2「点击时实时复核」）；是否允许在新鲜度窗口内复用已有取价见 BR-PRICE-20，决策前 link.open.requote_after_sec=0。转链链接缓存 ≤ 900 秒（link.convert_cache_ttl_sec），按 user_id 隔离，不得跨用户复用；价格复核与链接缓存分开计算。diff = \|new − old\|；diff ≥ 100 分，或 diff × 10000 ≥ 500 × old 时 price_changed=true；涨价和降价都触发，全部用整数运算。rebate_max_fen 由 >0 变为 0 时也必须弹窗确认，文案「该商品当前暂无返利，继续购买？」；其他返利变化只静默更新。price_changed=true 时，客户端先弹窗「价格已变动：¥旧 → ¥新，继续购买？」，确认后才外跳；price_changed=false 时直接外跳。new ≠ old 时，open 响应同时返回 new_link_id（快照为 new），客户端无论确认还是取消，都用新价格和 new_link_id 替换卡片；旧 link_id 再次 open 时仍与旧快照比较。同一 link_id 自首次 open 到达服务端起 3000 毫秒内（含）的重复 open 合并为一次复核（按 link_id 单飞锁），返回相同结果；超过 3000 毫秒的 open 重新复核。复核失败但存在该用户 ≤ 900 秒的转链缓存时：用缓存链接外跳，返回 requote_failed=true，客户端提示「暂时无法确认最新价格，以下单页为准」。复核失败且没有缓存，或取价成功但转链失败时：返回 50303（新增：暂时无法确认价格或生成链接），不外跳任何返利链接，主按钮「稍后再试」，次按钮「仍去购买（无返利）」，目标与展示按 BR-PRICE-08。50301 只用于 convert.enabled.&lt;platform> 关闭。 | 默认假设 | POST /v1/links/{link_id}/open 响应：price_changed、old/new_final_price_fen、new_link_id、requote_failed、new_rebate_\*、availability；links 表；错误码 50303（新增）；客户端购买流程弹窗（规划/03 §7.4）；配置 link.price_change.\*、link.open.requote_after_sec、link.convert_cache_ttl_sec；客服话术：「点进去价格变了」；验收：边界值 5%、100 分，涨价与降价用例；返利归零弹窗；3 秒内重复点击只复核一次；复核失败无缓存不外跳 |
| BR-PRICE-14 | **点击时下架或券失效**<br>open 复核发现商品下架时，返回 30141，不外跳；卡片置灰（availability=off_shelf），显示「商品已下架」；Agent 场景追加「换一批」。coupon_gone 只在 open 复核时判定：快照中 quoted_coupon_fen > 0，而复核时原券不可用（平台给券 ID 时按 ID 比对，否则按面额、门槛、结束时间三项比对）。此时商品仍可购买的，返回 200，availability=coupon_gone，new_final_price_fen 按 BR-PRICE-01 用当前可用的券重算（可能有更小的新券，也可能无券），并且不论价差是否达到阈值，都必须弹窗「券已失效：¥旧 → ¥新，继续购买？」；Agent 场景追加「这个券已领完」并提供「换一批」。多种情况同时成立时优先级为 off_shelf > coupon_gone > price_changed；coupon_gone 同时返利归零时，在券失效弹窗里追加「当前暂无返利」。淘礼金卡（cta 为 claim_tlj 或 claim_tlj_and_buy）点击时淘礼金领完，复用 30602（淘礼金已抢光），不外跳；30142 标为废弃，不再返回。检索结果里已下架的商品不出卡；券已过期或领完的商品按 coupon_fen=0 重算后照常出卡（属于「无券有返」，只要仍有返利），只在 has_coupon 等权益筛选时排除。 | 默认假设 | 错误码 30141、30142（废弃）、30602；POST /v1/links/{link_id}/open；product_card.availability；links.quoted_coupon_fen / quoted_coupon_id；客户端购买弹窗、Agent notice 卡；GET /v1/products/search、Agent 检索过滤；验收：下架、券失效（无新券 / 有新券）、淘礼金领完、多情况并存优先级、检索时过期券照常出卡用例 |
| BR-PRICE-15 | **价格筛选与排序口径**<br>price_min_fen / price_max_fen 必须与 final_price_fen 比较，且都含边界（final ≥ min 且 final ≤ max）。服务端校验 0 &lt; 值 ≤ 10,000,000（单位分，即 ¥0.01–¥100000，两端含），且 min ≤ max（相等合法），否则返回参数错误 20001。向上游只透传 price_min_fen 作为券前价下限（券前价 ≥ 券后价，不会漏召回），不透传上限；上限过滤与 sort=final_price_asc 由服务端对本次拉取的结果执行，只保证当页内有序，相同价格按相关性排序。用户说「50 以内」，就换算成 price_max_fen=5000。「再便宜点」：price_max_fen = min(上一轮 price_max_fen, 上一轮已展示卡片的最低 final_price_fen − 1)，并设 sort=final_price_asc；「上一轮已展示卡片」不含被过滤掉的商品；计算结果 &lt; 1 时不再检索，保留原结果集，由服务端固定文案回复「没有找到比当前结果更便宜的商品」。筛选只以检索时刻的联盟价为准；之后价格变化不回溯剔除卡片（由 BR-PRICE-13 在点击时处理）。 | 默认假设 | GET /v1/products/search 参数与校验；Agent search_products 参数；Agent 固定回复文案键；验收 AF-04、「再便宜点」用例、min>max 用例、最低 1 分边界用例 |
| BR-PRICE-16 | **金额唯一来源**<br>价格、券、返利字段（price_fen、coupon_fen、final_price_fen、rebate_\*、est_net_price_fen）必须来自服务端对联盟接口（搜索、详情、转链、口令解析）的返回，或来自其有效期内的缓存或商品池刷新值（BR-PRICE-11），再经 UnionAdapter 和 quoteRebate 计算，由 CardAssembler 或接口下发；不得来自用户粘贴的文本、素材、网页抓取或模型生成。唯一例外是 BR-PRICE-10 的 material.claimed_price_fen：它只作为用户素材的回显，必须带「素材参考价」标签和条件，是否合规以 BR-PRICE-10 的法务结论为准。模型的回复文本里不得出现金额、链接、口令（BR-AI）。每个带金额的卡片或接口对象，都必须带 quoted_at、source 和 disclaimer_keys。source 枚举为 taobao_union、jd_union、pdd_union，与数据来自实时接口、缓存还是商品池无关；是否为缓存降级数据另用 stale 表示。 | 已确认 | CardAssembler；UnionAdapter；Agent 输出过滤；product_card.quoted_at / source / disclaimer_keys / stale；商品池后台（不开放手工改价）；验收：粘贴文案价格不进入价格字段 |
| BR-PRICE-17 | **金额显示格式与口径说明**<br>金额字符串格式只按 BR-TEXT-10（去末尾 0，如 2990 → ¥29.9；区间 en dash；min=max=0 显示「暂无返利」）。客户端只做格式化，不做计算。product_card.disclaimer_keys 为数组，服务端按以下规则下发并排序：凡展示券后价或售价，先放 price_basis（BR-PRICE-03）；rebate_basis=normal 时加 rebate_estimate；rebate_basis=price_compare_risk 时加 rebate_compare（不再加 rebate_estimate）；素材卡最后加 material_ref（BR-PRICE-10）。客户端按数组顺序拼接显示，呈现位置见 BR-PRICE-03。文案由配置中心按 key 下发（F-CFG-06），不得写死在客户端或模板里；默认文案：rebate_estimate「预估返利以平台结算为准，未结算或订单失效时不返」，rebate_compare「以结算为准」。分享海报和分享文案印「券后 ¥x · MM-DD 取价」（x 取生成时刻的 final_price_fen，无券时为「售价 ¥x」），并附 price_basis 文案；不显示任何返利金额（BR-PRICE-06）。 | 默认假设 | product_card.disclaimer_keys（由 disclaimer_key 改为数组）；前端组件 PriceTag / RebateTag（格式化工具）；配置中心文案键 price_basis / rebate_estimate / rebate_compare / material_ref；分享海报模板、分享文案模板（F-SHARE-01/02）；验收：金额格式快照；各场景 disclaimer_keys 组合 |
| BR-PRICE-18 | **价格与返利禁止用语**<br>禁用词的总清单（specs/banned-words.yaml）、匹配方式（字段白名单、NFKC 归一后子串匹配）、适用范围与检查点（CI 扫描、后台保存校验）只由 BR-TEXT-13 维护，本条不另定匹配与扫描规则；Agent 输出过滤见 BR-AI。本条只规定价格与返利类用词必须收录进该清单、以及如何改写：(1) 必须收录：全网最低、历史最低、最便宜、最高返利、稳赚、必返（规划/01 F-PRIV-09 已定）；最低价（BR-TEXT-13 已收录）；返利最高、最高返、原价（待法务确认，确认前默认启用；BR-TEXT-13 尚未收录，由合稿并入；「原价」随 BR-PRICE-04 的法务结论调整）。清单外的「最低」「最高」「新低」单独出现不算命中，是否扩充由法务决定。(2) 卖点表述不用「比价」「全网最低」（「比价」的字段白名单见 BR-TEXT-13）。(3) 用户自己输入的内容（如「返利最高的」）不受限制，但模型回复要改写为「按返利从高到低」；排序选项显示名用「返利从高到低」「券后价从低到高」。 | 待决策 | specs/banned-words.yaml 词条（清单、匹配与扫描规则归 BR-TEXT-13）；后台模板保存校验；Agent 输出过滤词库；分享文案与海报模板；推送模板；客服话术库；验收：禁用词扫描通过 |
| BR-PRICE-19 | **降价提醒监控的价格口径**<br>降价提醒监控 final_price_fen（按 BR-PRICE-01 自算的券后价），细则只在 BR-WATCH-03 维护，本条不另写口径；状态随 BR-WATCH-03。 | 待验证 | 见 BR-WATCH-03 |
| BR-PRICE-20 | **点击复核的价格新鲜度窗口**<br>link.open.requote_after_sec 决定 open 时是否可以不实时取价。默认 0：每次 open 都实时调用转链或详情接口取价（规划/01 J3、F-AGENT-08，规划/02 §9.2）。若负责人确认改为 N > 0（候选 300）：取该 link 的 quoted_at 与 preconvert_at 中较新的一个，其 age ≤ N 时，用对应的价格（preconvert 较新时取 preconvert_final_price_fen，否则取 quoted_final_price_fen）作为 new；否则实时取价。无论取值如何，old 始终取 quoted_final_price_fen，转链链接缓存（≤900 秒，BR-PRICE-13）与价格新鲜度分开计算。 | 待决策 | POST /v1/links/{link_id}/open 取价逻辑；links.preconvert_at；配置 link.open.requote_after_sec；联盟调用量与配额监控；验收：N=0 时每次点击都调用联盟；N>0 时窗口内不调用 |
| BR-PRICE-21 | **查返利三态与带返利跳转**<br>查返利结果只有三态，不另设字段，服务端（接口、埋点、统计、Agent 固定话术）与客户端按同一规则由 coupon_fen 与 rebate_basis 推导：有券有返 = coupon_fen > 0 且 rebate_basis ∈ {normal, price_compare_risk}；无券有返 = coupon_fen = 0 且 rebate_basis ∈ {normal, price_compare_risk}；无返利 = rebate_basis = no_rebate（不论有无券）。price_compare_risk 且 rebate_min_fen = 0 &lt; rebate_max_fen 仍属「有返」（BR-PRICE-07）。availability 为 price_unavailable 或 off_shelf 的卡不属于任何一态，不显示三态标签。凡显示「预估返 ¥x」或「预估返后 ¥x」的购买按钮或卡片，点击后必须经 POST /v1/links/{link_id}/open 由服务端复核并转链，外跳带本 App 推广参数的转链结果（BR-PRICE-12、BR-PRICE-13）；不经转链的跳转（直接唤起平台 App 首页、店铺页，或 BR-PRICE-08 的无推广参数商品页）不得在按钮、卡片或跳转提示中显示任何返利金额，购买按钮文案用「去购买（无返利）」。转链失败或佣金为 0 时一律落到无返利态，按 BR-PRICE-08 处理，不得把用户给的原链接或口令当作返利链接返回。 | 默认假设 | product_card.coupon_fen / rebate_basis / availability（三态推导，不新增字段）；前端组件 RebateTag、CTA 文案键；POST /v1/links/{link_id}/open；Agent rebate_quote 卡；埋点与经营看板的查券三态统计；验收：三态推导用例（含比价风险下限 0）、带返利按钮外跳为转链结果、不经转链的入口不显示返利金额 |

### 3.2 细则

#### BR-PRICE-01 细则 · 价格三字段定义与计算

- 状态：默认假设
- 默认值：券门槛按单件判断；多券取可用的最大面额；券后价一律自算，平台券后价白名单初始为空；价格异常时检索场景不出卡、主动查询出 price_unavailable 卡
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 参考_花卷云功能查漏底稿 §4 统一商品模型：「原价、券额、券后价（未定义门槛与单件口径）」
  - PRD v2.1 §10.7：「product_card v1 价格字段 price_fen、coupon_fen、final_price_fen（未定义原价口径）」
- 来源：规划/04 §8.3；规划/03 §10.2 PriceTag；规划/01 E04 F-PROD-05；PRD v2.1 §10.7；参考_花卷云功能查漏底稿 §4
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**公式**：`final_price_fen = price_fen − coupon_fen`。

**选券**：候选券 = 同时满足 `coupon_start_at ≤ now < coupon_end_at`、`remain > 0`、`price_fen ≥ coupon_threshold_fen` 的券；取 coupon_amount_fen 最大的一张，面额相同取门槛低的；平台标记的 isBest 只作参考；一张都不满足时 coupon_fen=0。

**时间与剩余量**：平台时间带时区的按其时区解析，不带时区的一律按 +08:00；只给日期的结束时间，coupon_end_at 取该日次日 00:00:00+08:00（开区间）；只给日期的开始时间，取当日 00:00:00+08:00。平台不返回剩余量字段时视为 remain>0（点击时由 BR-PRICE-13/14 复核兜底）；返回剩余量为 0 时该券不可用。

**金额解析**：`"39.9"`→3990；`"39.90"`→3990；`"39.905"`、`""`、`"-1"`、`"abc"`→缺失。JSON 数值型金额先转为最短十进制字符串再走同一解析。平台以分返回的字段直接取整数，单位须在 specs/union/&lt;platform>.md 标注。

**例**
| price_fen | 券 | 门槛 | coupon_fen | final_price_fen |
|---|---|---|---|---|
| 3990 | 10 元 | 39 元 | 1000 | 2990 |
| 3990 | 10 元 | 50 元 | 0（单件没达到门槛） | 3990 |
| 3990 | 10 元，已过期 | — | 0（检索时 availability=ok；只有点击复核时原券失效才是 coupon_gone，见 BR-PRICE-14） | 3990 |
| 3990 | A：10 元门槛 39；B：15 元门槛 50 | — | 1000（B 未达门槛） | 2990 |
| 缺失 | — | — | — | 异常：检索不出卡；粘贴出 price_unavailable 卡 |

- 单件没达到门槛的券：不扣减，不算「有券」（has_coupon 筛选时排除），可以放进 benefit_tags 显示「满 ¥50 减 ¥10」。
- 怎样才算同一商品见 BR-PROD-01；多规格（SKU）取价见 BR-PROD-04：采用联盟返回的商品级价格，规格无法确定时价格旁显示「规格以下单页为准」，联盟返回价格区间或确知为最低规格价时显示「¥x 起」。本主题所说「默认 SKU」即指这个联盟返回的商品级价格；件数不进商品身份，价格一律按购买 1 件。
- 淘礼金金额不计入 coupon_fen，见 BR-PRICE-08。

#### BR-PRICE-02 细则 · 各平台取价字段映射

- 状态：待验证
- 默认值：淘宝 zk_final_price；京东 priceInfo.price + 按 BR-PRICE-01 选券；拼多多 min_group_price 并标「拼单」；对照 ≥20 个商品误差 0 分全部一致才算通过
- 决策人：负责人
- 依赖平台能力：淘宝/京东/拼多多：物料搜索、详情、转链、口令解析各接口的价格与券字段实际返回样例；淘宝 final_promotion_price 是否含跨店满减或 88VIP；拼多多拼单价与单买价在下单页的实际差异；京东是否返回 PLUS 价（规划/09 价格口径链路②）
- 取代：无
- 来源：规划/04 §8.3；PRD修订_后端功能规划 §2.2 平台佣金口径差异；规划/01 E04 F-PROD-05「卡片金额与联盟接口一致」
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

| 平台 | price_fen 默认字段 | 只存原始报文 | 券字段 | 待实测点 |
|---|---|---|---|---|
| taobao | zk_final_price | reserve_price、final_promotion_price | coupon_amount、coupon_start_fee、coupon_start_time、coupon_end_time、coupon_remain_count | final_promotion_price 口径；reserve_price 与下单页差异 |
| jd | priceInfo.price | lowestPrice（可能含秒杀、拼购价）、lowestCouponPrice | couponInfo.couponList 中各券 discount、quota、有效期 | PLUS 价是否混进返回；lowestCouponPrice 与自算值是否一致 |
| pdd | min_group_price | min_normal_price | coupon_discount、coupon_min_order_amount、coupon_start_time、coupon_end_time、coupon_remain_quantity | 单买价与拼单价的差；goods_sign 转链后价格是否变化 |

以上字段名都来自公开资料，标「待核实」，以各开放平台当前文档和实测返回为准。

**例**：拼多多返回 min_group_price=1990、min_normal_price=2590、coupon_discount=300、门槛 1000 → price_fen=1990，coupon_fen=300，final_price_fen=1690，卡片主价「拼单券后 ¥16.9」。

**异常**：某个字段缺失 → 按 BR-PRICE-01 的数据异常处理，不猜值。

**对照失败示例**：20 个中 1 个下单页 2890、final 2990 → 不通过，记录原因（如跨店满减被自动勾选或字段映射错误），修正后 20 个重测。

#### BR-PRICE-03 细则 · 运费与平台外优惠不计入

- 状态：默认假设
- 默认值：不含运费、不含下单页优惠；详情与分享常驻全文，列表每屏底部一次 + 单卡 i 图标；不估算运费
- 决策人：负责人
- 依赖平台能力：三平台是否返回包邮 / 运费字段（待实测）
- 取代：
  - PRD v2.1 §10.19 通用规则：「订阅提醒价格口径为联盟券后价，不含 88VIP、跨店满减、淘金币（未说明运费）」
- 来源：PRD v2.1 §10.19；PRD v2.1 §10.6.1 第四步；规划/04 §8.3（未定义运费）；PRD修订_后端功能规划 §2.3 搜索（未定义运费）
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

- **例 1**：券后价 2990，下单页运费 600 → 卡片显示 ¥29.9，口径说明注明不含运费；不做任何提示或校正。
- **例 2**：券后价 2990，88VIP 用户在下单页看到 2690 → 卡片仍显示 ¥29.9；这不算价格变动，不触发 BR-PRICE-13。
- **例 3**：Agent 返回 5 张卡 → 列表底部一行口径说明，每张卡右上角一个 i 图标。
- 包邮标识的字段是否可用，待 BR-PRICE-02 实测；拿不到时不显示「包邮」，也不显示「不包邮」。
- 降价提醒同样用这个口径，见 BR-WATCH-03。

#### BR-PRICE-04 细则 · 券前价与售价标签

- 状态：待决策
- 默认值：有券：券后 + 券前（不划线）；无券：售价；拼多多加「拼单」前缀；理由是法规对「原价」的用法有限制（待法务核实），推广方无法证明原价的真实性
- 决策人：法务
- 依赖平台能力：无
- 取代：
  - 规划/03 §10.2：「PriceTag：券后价（主）+ 原价（划线）+ 券额标签」
  - 规划/01 E04 F-PROD-05：「商品详情展示原价」
- 来源：规划/03 §10.2；规划/01 E04 F-PROD-05；参考_花卷云功能查漏底稿 §4
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- **例**：price_fen=3990、coupon_fen=1000 → 主价「券后 ¥29.9」，副行「券前 ¥39.9 · 券 ¥10」（不划线）。
- **例**：coupon_fen=0 → 只显示「售价 ¥39.9」，不显示券前价，不出现「券后」。
- **例**：拼多多 1990 券 300 → 「拼单券后 ¥16.9」，副行「拼单券前 ¥19.9 · 券 ¥3」；拼多多无券 1990 →「拼单价 ¥19.9」。
- 理由：规范价格比较用语的法规对「原价」有特定含义（具体条款待法务核实）；无券时写「券后」会暗示已用券。推广方只能拿到平台当下的售价，所以用「券前价」「售价」这类中性说法。
- 分享海报、分享文案模板里的变量也不得命名为「原价」。

#### BR-PRICE-05 细则 · 价格术语统一

- 状态：默认假设
- 默认值：统一用「券后价」，无券用「售价」；返利短标签只用「预估返」；界面不用「到手价」
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 规划/01 §5 J1：「商品详情展示「到手价」（F-PROD-05 同处用「券后价」）」
  - 规划/01 §5 J2 步骤 4 / 规划/03 §7.4：「「接口到手价」」
- 来源：规划/00 §2；规划/01 §5 J1/J2；规划/01 E04 F-PROD-05；规划/03 §7.4、§10.2；规划/04 §6.3
- 需同步修改的规划文档：4 处（计数仅作记录，落点见 README §0.6）

| 旧叫法（来源） | 统一为 |
|---|---|
| 到手价（规划/01 J1、规划/04 §6.3、00 §1 表） | 券后价（无券时为售价） |
| 接口到手价（规划/01 J2、规划/03 §7.4、PRD v2.1 §10.6.1） | 券后价（素材卡里写作「券后价 · 联盟接口」） |
| 原价（规划/01 F-PROD-05、规划/03 §10.2） | 券前价 |
| 返利后到手价 / 返后价（00 §2） | 预估返后价 |
| 返 ¥x、约返、可返（各处草稿） | 预估返 ¥x |

代码字段名保持不变（final_price_fen 等）。sort 的枚举值 final_price_asc 保持不变，显示文案为「券后价从低到高」。

#### BR-PRICE-06 细则 · 预估返利计算口径

- 状态：待决策
- 默认值：B = N（不扣 reserve_bp，按规划/01 §3 分账口径；D8 在规划/00 §3.2；B 的定义以 BR-CALC-02 为准）；比例按 platform × level × buy_type；分享口径只在分享面板给分享者本人看，分享中间页、海报、文案不显示返利
- 决策人：负责人
- 依赖平台能力：计算侧依赖（各平台技术服务费率、佣金率字段口径）见 BR-CALC-20；淘宝补贴类佣金是否只在分享场景拿得到（后端规划 §2.2 标为假设，待实测）
- 取代：
  - PRD修订_后端功能规划 §2.6：「B = N − floor(N × reserve_bp / 10000)，buyer = floor(B × r_buyer_bp[level] / 10000)（与规划/01 D8 不一致，改为待决策备选）」
  - PRD修订_后端功能规划 §2.3 返利报价口径：「分享中间页、海报、分享文案用分享口径显示预估返」
- 来源：规划/01 §3 分账口径（D8）；规划/01 §5 J8、F-ORD-04；PRD修订_后端功能规划 §2.3 返利报价口径；PRD修订_后端功能规划 §2.6；PRD修订_后端功能规划 §2.2
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

**计算**：公式、算例与 reserve_bp 备选口径对比只在 BR-CALC-20 细则维护，本条不重复。

**例**（接 BR-CALC-20 细则算例：final_price_fen=2990 → 本人份额 269）：搜索卡显示「预估返 ¥2.69」，disclaimer_keys 含 rebate_estimate（BR-PRICE-17）。

- 报价阶段 order_type 取值：自购场景 buy_type=self；分享面板 buy_type=share。
- 规则版本：取值规则见 BR-CALC-20（报价用当前生效版本）与 BR-CALC-11（入账按付款时点版本）；二者可能不同，展示上由 disclaimer_keys 中的 rebate_estimate 说明「以平台结算为准」（BR-PRICE-17）。
- 比例字段名 r_own_bp / r_direct_bp（r_self / r_self_bp 只作别名）见 BR-CALC-06、C-29。
- 分享中间页的查看者经分享链接下单，佣金归分享者推广收益，查看者没有返利，所以中间页不显示返利。
- 预售订单：下单后的订单预估展示按 BR-FUND-01 的双状态表达，platform_status=DEPOSIT_PAID（rebate_status=ESTIMATED）阶段预估计为 0、不向用户展示金额（BR-FUND-03）；对应规划/04 单一 order_status 的 DEPOSIT_PAID（映射见 BR-FUND-01「与 规划/04 单一 order_status 的映射」）。按 C-01 默认处理，待负责人确认。

#### BR-PRICE-07 细则 · 比价风险与返利区间

- 状态：待验证
- 默认值：有风险展示区间；无预判定权限时粘贴 / 搜索 / Agent / 无来源详情的淘宝卡按风险处理；compare_rate_ratio_bp 占位 5000
- 决策人：负责人
- 依赖平台能力：淘宝 06 Q-G2：「粘贴链接查返利」「Agent 推荐后转链」是否会被判为比价订单，以及比价佣金的折算口径；淘宝比价预判定接口权限（后端规划 V2）及返回时延；优券汇 flow_source=1 历史订单占比与佣金率差（规划/06 Q-D2）；拼多多：是否存在比价降佣及比价单佣金口径（CAP-PDD-04，09 附录 A-14）
- 取代：
  - PRD修订_后端功能规划 §2.3 返利报价口径：「有比价风险的订单按佣金率下限展示，并注明「以结算为准」」
  - 规划/01 E04 F-PROD-05、F-ORD-11：「淘宝有比价降佣风险时按区间或保守值」
  - 规划/06 Q-B1（修订前原文）：「需结合 G1 的联盟答复」（原文旧编号 G1，应为 06 Q-G2）
- 来源：规划/06 Q-B1；规划/01 E04 F-PROD-05、F-ORD-11；规划/04 §1、§2.3、§3.2、§8.3；PRD修订_后端功能规划 §2.3 比价预判定；规划/06 Q-G2、Q-D2
- 需同步修改的规划文档：4 处（计数仅作记录，落点见 README §0.6）

**例**：final_price_fen=2990，正常佣金率 2000bp → rebate_max=269（算法见 BR-CALC-20）；compare_rate_ratio_bp=5000 → 比价佣金率 1000bp → gross=299 → fee=29 → N=270 → B=270 → floor(270×5000/10000)=135 → 显示「预估返 ¥1.35–¥2.69 · 以结算为准」。

**来源判定表（无预判定权限）**
| entry_source | rebate_basis |
|---|---|
| parse（粘贴链接 / 口令）、search、agent（含换一批） | price_compare_risk |
| feed、pool、tlj_pool、share | normal |
| detail | 继承来源卡；无来源卡 → price_compare_risk |
| watch（订阅提醒点击） | 继承创建提醒时来源卡；无法确定 → price_compare_risk |

- entry_source 在登记 link 时写入 links 表，派生请求带 from_link_id 继承。
- 下单后以订单为准：orders.is_price_compare=true 时，订单页按比价佣金显示（BR-CALC-16）。
- 与 BR-CALC-16 的分工（C-22，默认处理，待负责人确认，财务知悉）：本条是下单前比价展示的唯一维护处——搜索卡、详情、inputs/parse、Agent 卡等下单前报价一律按本条展示区间 [按 compare_rate_ratio_bp 折算的下限, 正常佣金率上限]，不另显示保守值，也不改为「不展示金额」；BR-CALC-16 只管订单侧计算（以联盟已降佣的 N 分账、订单三处一致、差额原因 PRICE_COMPARE），不再规定下单前报价展示。
- compare_rate_ratio_bp 的默认值要等 D2（优券汇 flow_source=1 的历史佣金率差）和 06 Q-G2（联盟答复）；数据到位前的 5000 只是占位。
- 占位值在 CAP-TB-04 实测与规划/06 Q-D2 数据到位前，只能在 App 内以「预估返 ¥a–¥b · 以结算为准」展示，不得用于运营素材、客服话术或对外宣传（C-22，默认处理，待负责人确认，财务知悉）。
- 冲突裁决：后端规划写「按佣金率下限展示」，规划/06 Q-B1 写「有风险时展示区间」，规划/01 写「区间或保守值」。按规划/ 优先，采用区间。

#### BR-PRICE-08 细则 · 无返利与淘礼金返利展示

- 状态：默认假设
- 默认值：检索场景过滤无返利商品（规划/01 已定）并最多补拉 1 页；主动粘贴的场景出卡并标「暂无返利」；无返利购买跳无推广参数商品页；淘礼金不从券后价扣减
- 决策人：负责人
- 依赖平台能力：三平台由 product_key 生成无推广参数商品页 URL 的方式（待实测）
- 取代：
  - PRD v2.1 §10.7 过滤：「无佣金商品不展示（或单独标「无返利」，放在最后）」
- 来源：规划/01 §5 J1 步骤 2、J3 步骤 2、E05 F-HOME-03；PRD v2.1 §10.7；PRD修订_后端功能规划 §2.4 无返利态、§2.6 活动单；PRD修订_双品牌与Agent找货 §3.6、§3.6.1；参考_花卷云功能查漏底稿 §5、§16 #25
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

| 场景 | rebate_basis | 展示 | 按钮 |
|---|---|---|---|
| 搜索或 Agent 结果中佣金为 0 | — | 过滤掉，不出卡 | — |
| 粘贴链接，有券、佣金为 0 | no_rebate | 券后 ¥29.9 · 暂无返利 | 去购买（无返利） |
| 粘贴链接，转链失败 | no_rebate | 券后 ¥29.9 · 暂无返利 | 去购买（无返利）→ 无推广参数商品页 |
| 我方淘礼金池，tlj.amount_fen=500，不叠加返利 | no_rebate | 券后 ¥29.9 · 淘礼金商品不叠加返利；淘礼金标签与说明按 BR-TEXT-15 判定 1 | cta=claim_tlj\*，按钮文案按 BR-TEXT-15 判定 1 |
| C 类素材 | normal | 券后 ¥29.9 · 预估返 ¥2.69；淘礼金说明按 BR-TEXT-15（验证前判定 3′，验证后判定 3） | 按 BR-TEXT-15 |

- 我方淘礼金池卡片的标签、按钮与说明文案见 BR-TEXT-15 判定 1；本条只定 tlj 字段（tlj.amount_fen、tlj.remain、tlj_kind）、rebate_basis 与 cta 类型（G-17）。
- **分页例**：page_size=20，上游第 1 页过滤掉 6 个 → 补拉上游第 2 页，过滤后补足 20 个返回，游标记为上游第 3 页；补拉后仍只有 17 个 → 返回 17 个。
- 查券三态（有券有返、无券有返、无返利）与本表一致。
- quoteRebate 结果为 0 但 gross > 0 时（金额太小被 floor 截掉），同样判为 no_rebate。
- 规划/01 J1 授权失败时的【仍去购买（无返利）】与本条目标一致。
- 淘礼金的领取资格、发放规则：淘礼金主题（BR-TLJ）建立前以规划/01 E08 为准，Agent 场景见 BR-AI；我方淘礼金订单的返利计算见 BR-CALC-19。
- 查返利三态的推导与「带返利展示必须经转链」见 BR-PRICE-21。

#### BR-PRICE-09 细则 · 预估返后价

- 状态：待决策
- 默认值：显示，取 rebate_min_fen 计算，尽量避免向用户多承诺；不保证实际返后价；必须附结算说明
- 决策人：负责人 + 法务
- 依赖平台能力：无
- 取代：
  - 规划/00 §2：「「返利后到手价透明」，没有给出公式」
- 来源：规划/00 §2；规划/01 §1 一句话；规划/04 §8.3（缺少这个字段）；PRD评审_v2 §差异化
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- **例**：final_price_fen=2990，rebate 135–269（比价风险）→ est_net_price_fen=2855 →「预估返后 ¥28.55」。
- **例**：rebate_basis=normal，rebate=269 → est_net=2721 →「预估返后 ¥27.21」。
- **例**：price_compare_risk，rebate 0–5 → rebate_min=0 → 不显示这一行。
- **例**：no_rebate → 不显示这一行。
- 用下限的理由：尽量避免向用户多承诺。但实际结算返利仍可能低于下限（比价佣金率低于占位值、订单被其他推广者归属、退款维权、结算规则版本不同），所以不作任何保证。
- 这是规划/00 差异化承诺「返利后到手价透明」在界面上的落地；规划/04 目前没有这个字段。

#### BR-PRICE-10 细则 · 素材参考价

- 状态：待决策
- 状态变更：原为默认假设；本条是否合规属合规定性、决策人为法务，按 README §0.3 改为待决策（2026-09-30 自查）
- 默认值：只在素材卡显示为第二行，并标明来源与条件；理由：用户已看到素材价，完全不显示反而无法解释差价，标明「素材参考价」与条件可避免被当作本 App 报价。法务或联盟不同意时，改为不显示这一行（配置开关 material_ref.enabled，默认 true）
- 决策人：法务
- 依赖平台能力：无
- 取代：无
- 来源：规划/01 §5 J2 步骤 4；规划/01 E02 F-PRIV-08；规划/03 §7.4；规划/04 §8.3；PRD v2.1 §10.2、§10.6.1；PRD修订_双品牌与Agent找货 §3.2、§3.6.1
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- **例**：素材写「券后 28，需 88VIP + 淘金币 + 淘礼金」，联盟接口返回的券后价为 3590 → 第一行「券后 ¥35.9 · 联盟接口」，第二行「素材参考价 ¥28（需 88VIP + 淘金币 + 淘礼金，仅供参考，以下单页为准）」。
- conditions[] 枚举：88vip、taojinbi、taolijin、plus、cross_store 等，用于拼接条件文案。
- 素材金额解析同样用 parseYuanToFen()（BR-PRICE-01），解析失败即不显示。
- 与联盟规范红线「展示价来自联盟接口」（F-PRIV-08）之间存在张力：本条的处理方式是把素材价明确标成用户素材的回显，而不是本 App 的报价。是否合规，待法务或联盟确认。BR-PRICE-16 把本条列为唯一例外。

#### BR-PRICE-11 细则 · 取价时间与缓存有效期

- 状态：默认假设
- 默认值：缓存只存归一化价格；TTL 300 秒；商品池 3600 秒刷新、超过 7200 秒不展示；降级结果一律 stale；age 由服务端下发
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 规划/01 E16 F-ADM-10：「定时刷新价格与券（没有给出频率）」
- 来源：规划/01 E04 F-PROD-07；规划/02 §14；PRD修订_后端功能规划 §2.3 商品池、§7 降级表；规划/04 §8.3；PRD v2.1 §10.13
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- **例**：10:00:00 联盟返回 → quoted_at=2026-09-29T10:00:00+08:00；10:03 缓存命中 → quoted_at 仍为 10:00:00，age_sec=180，不显示提示；10:06 联盟超时、缓存 age 360 秒不可用 → 从商品池降级（池刷新于 09:30，age 2160 秒 ≤ 7200）→ stale=true，显示「取价 09:30 · 价格可能已变化，以下单页为准」。
- **例**：商品池最近成功刷新在 07:30，此刻 10:06（age 9360 秒 > 7200）→ 不展示，提示「淘宝暂时查不到」。
- **例**：同一商品缓存命中，V1 用户与游客看到的券后价相同，返利按各自等级分别计算。
- 边界：age = 300 秒不提示，age > 300 秒提示。
- 转链结果缓存的有效期见 BR-PRICE-13（≤900 秒，按 user_id 隔离）。
- Watch 的观测记录与价格变更历史分开存储，见 BR-WATCH。

#### BR-PRICE-12 细则 · 报价快照、比较基准与 link 归属

- 状态：默认假设
- 默认值：比较基准 = 该 link 快照，快照不可变，价格变化即新建 link_id；open 时的归属校验只在 BR-ATTR-05 维护（G-08，默认处理，待负责人确认），本条只定为他人 link 新建 link 时的比较基准
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 规划/01 §5 J3 步骤 4：「价差比较，未定义比较基准」
- 来源：规划/02 §9.2（禁止跨用户复用）；规划/04 §3.2 links、§6.3；PRD v2.1 §10.5；PRD修订_双品牌与Agent找货 §3.5 第 1 步
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- **例**：卡片下发时 final=2990 → link L1 快照 2990；30 秒后异步预转链返回 3050 → 写入 L1.preconvert_final_price_fen=3050、preconvert_at，快照仍为 2990；用户点击 L1 时以 2990 为 old 比较（BR-PRICE-13）。
- **例**：Agent 会话里卡片 L1 显示 2990；用户进详情，刷新得到 3090 → 详情页用新 link L2（快照 3090）；返回会话点 L1 → 仍以 2990 比较，弹窗「¥29.9 → ¥30.9」与用户所见一致。
- **例**：游客搜索得到 L3（user_id 空）→ 登录后点击 → L3 写 user_id=当前用户（只写一次），按其身份转链（BR-ATTR-05 ②）。
- **例**：用户 A 的 L4（非分享 link）被用户 B 打开 → 新建 L5（user_id=B，比较基准沿用 L4 的 quoted_final_price_fen）并按 B 的身份转链，响应带 new_link_id，订单归属 B，A 的缓存链接不被使用（BR-ATTR-05 ③）。
- 「T1」是修订① 定义的输入类型（链接或口令），不是时间点；规划/02 §9.2 没有定义这个词。

#### BR-PRICE-13 细则 · 点击复核与价格已变动

- 状态：默认假设
- 默认值：≥5% 或 ≥100 分，涨跌都触发；每次 open 实时复核；价格变化即换新 link_id；失败无缓存返回 50303 并给无返利购买次按钮
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - PRD v2.1 §10.5 / 后端功能规划 §2.4 / 修订① §3.5：「价差「超过」5% 或 1 元」
  - 规划/06 Q-B4：「到手价变动 ≥5% 或 ≥¥1（未说明方向与基准）」
  - 规划/04 §7：「50301 = 该平台维护中（复核失败不再复用此码）」
- 来源：规划/01 §5 J1 步骤 2、J3 步骤 4、F-AGENT-08；规划/02 §9.2；规划/04 §7、§8.4；规划/03 §7.4 购买流程；规划/06 Q-B4；PRD v2.1 §10.5；PRD修订_后端功能规划 §2.4；PRD修订_双品牌与Agent找货 §3.5 第 2 步
- 需同步修改的规划文档：4 处（计数仅作记录，落点见 README §0.6）

**判定**：`changed = diff >= 100 || diff*10000 >= 500*old`

| old | new | diff | 结果 |
|---|---|---|---|
| 2990 | 3090 | 100 | true（≥1 元） |
| 2990 | 3080 | 90 | false（900000 &lt; 1495000），静默更新并返回 new_link_id |
| 1000 | 950 | 50 | true（500000 ≥ 500000，正好 5%） |
| 1000 | 951 | 49 | false |
| 300000 | 300100 | 100 | true（高价商品变动 1 元也会提示） |
| 2990 | 2990，rebate_max 229→0 | 0 | 弹窗「该商品当前暂无返利，继续购买？」 |

- 阈值都做成配置：link.price_change.min_fen=100、link.price_change.ratio_bp=500。
- 响应字段：price_changed、old_final_price_fen、new_final_price_fen、new_link_id、new_rebate_min_fen、new_rebate_max_fen、availability、requote_failed。
- 下架、券失效与本条同时成立时的优先级见 BR-PRICE-14。
- 冲突裁决：PRD 与修订① 写「超过」，规划/04 写「≥」，采用 ≥。后端规划写「缓存 ≤15 分钟内不复核」，规划/01 J3 与规划/02 §9.2 写「实时复核」，默认按规划/ 实时复核，新鲜度窗口单独列为 BR-PRICE-20 待决策。

#### BR-PRICE-14 细则 · 点击时下架或券失效

- 状态：默认假设
- 默认值：券失效不阻断购买，但必须弹窗确认；coupon_gone 只在点击复核时判定；淘礼金领完用 30602，30142 废弃；检索时券过期商品按无券出卡
- 决策人：负责人
- 依赖平台能力：三平台券是否带稳定券 ID（待实测，规划/09）
- 取代：
  - 规划/04 §7：「30142 = 券已失效或领完（没区分是否阻断购买）」
  - 规划/01 §5 J3 步骤 2：「服务端过滤（无佣金、禁售类目、券失效）」
- 来源：规划/04 §7、§8.3；规划/02 §14；规划/01 §5 J3 步骤 2；PRD v2.1 §10.5 点击后的分支、§10.7
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- **例**：卡片 final=2990（券 10 元），点击时券领完、无其他可用券 → new=3990，availability=coupon_gone → 弹窗「券已失效：¥29.9 → ¥39.9」。
- **例**：原 10 元券领完，但有新 5 元券 → new=3490，coupon_gone，弹窗「券已失效：¥29.9 → ¥34.9」。
- **例**：原券领完且商品下架 → 按 off_shelf 返回 30141。
- **例**：淘礼金卡点击时领完 → 30602，按钮置灰，显示「淘礼金已领完」，给普通购买入口（按 BR-PRICE-08 重算返利）。
- **例**：搜索时某商品券已过期、佣金 >0 → 出卡「售价 ¥39.9 · 预估返 ¥x」。
- 规划/01 J3 步骤 2「过滤券失效」按本条理解为「失效券不计入券额」：否则无券商品能出卡、券过期的同一类商品却被过滤，前后不一致。
- 转链熔断或复核失败时的处理见 BR-PRICE-13。
- 错误码：30142 废弃后码值不回收、不复用；BR-TEXT-14 话术表中的 30142 行随之删除；本条所用码号（30141、30602、50303）以规划/04 §7 与第 13 节错误码表为准。按 C-03 默认处理，待负责人确认（码号分配代理可自定）。

#### BR-PRICE-15 细则 · 价格筛选与排序口径

- 状态：默认假设
- 默认值：含边界；上游只透传下限；排序仅当页；「再便宜点」= min(上一轮上限, 上一轮已展示最低价 − 1 分)，&lt; 1 时不检索
- 决策人：代理可自定
- 依赖平台能力：三平台物料搜索的价格区间与排序参数作用于券前价还是券后价（待实测）
- 取代：
  - PRD v2.1 §10.8：「「再便宜点」把 price_max_fen 设为上一轮最低到手价（会把原卡再选进来）」
- 来源：PRD v2.1 §10.8、§10.11 AF-04；PRD修订_双品牌与Agent找货 §3.3；PRD修订_后端功能规划 §2.3 搜索；规划/01 §5 J3；规划/04 §7（20001）

- **例**：「京东 伊利纯牛奶 24 盒 50 以内」→ price_max_fen=5000；final=5000 的卡保留，5001 的不保留（AF-04：所有卡 final ≤ 5000）。
- **例**：上一轮 price_max_fen=5000、已展示最低 final=3990 →「再便宜点」→ price_max_fen=3989，结果中不再出现 3990 这张卡。
- **例**：上一轮已展示最低 final=1 →「再便宜点」→ 结果 0 &lt; 1 → 不检索，固定文案回复。
- **例**：min=5000、max=3000 → 20001。
- 上游是否支持按券前价下限筛选、排序参数作用于哪个价格，待 BR-PRICE-02 实测；不支持时服务端全部自行过滤。
- 固定文案须避开 BR-PRICE-18 禁用词（「最便宜」「最低价」）。
- 预估返后价与素材参考价都不参与筛选和排序（BR-PRICE-09、BR-PRICE-10）。
- 模型负责抽取金额，服务端负责校验（BR-AI-08）。
- 「再便宜点」的上限公式只在本条维护。BR-AI-05 细则写作「上一轮结果集最低 final_price_fen − 1」，未取 min(上一轮 price_max_fen, …)，也未排除被过滤的商品，与本条不一致，未列入 §14.3（见 3.3 第 14 条）；裁决前 Agent 服务端按本条计算上限。BR-AI-08 的「无结果时放宽价格上限」不适用于「再便宜点」（BR-AI-05 细则同样写明不放宽）。

#### BR-PRICE-16 细则 · 金额唯一来源

- 状态：已确认
- 默认值：无（已确认，按规则执行）
- 决策人：负责人
- 依赖平台能力：无
- 取代：无
- 来源：规划/01 E02 F-PRIV-08；规划/01 §5 J3 步骤 2；规划/02 §9.2；PRD v2.1 §10.2、§10.13；PRD修订_后端功能规划 §2.11；PRD修订_双品牌与Agent找货 §3.2
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- **例**：用户粘贴「券后 9.9 速抢」，联盟返回的券后价为 1290 → 卡片显示 ¥12.9；「9.9」只能作为素材参考价（BR-PRICE-10），或者完全不显示。
- **例**：商品池降级返回的京东商品 → source=jd_union，stale=true。
- 模型说「这款才 9.9」→ 输出过滤拦截并改写（BR-AI）。
- 商品池里运营人工录入的价格不得直接展示，必须经联盟刷新后才能展示。

#### BR-PRICE-17 细则 · 金额显示格式与口径说明

- 状态：默认假设
- 默认值：格式引用 BR-TEXT-10（G-01）；disclaimer_keys 为数组、按规则排序下发；海报附 price_basis 且不显示返利
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 规划/04 §8.3：「product_card.disclaimer_key（单值）」
- 来源：规划/03 §10.2；规划/01 F-CFG-06、F-SHARE-01/02、J8；PRD v2.1 §10.13 disclaimer_key；规划/06 Q-F4（法务审阅文案）
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- **例**：rebate_min=135、rebate_max=269 → 「预估返 ¥1.35–¥2.69」，disclaimer_keys=[price_basis, rebate_compare]。
- **例**：min=max=269 → 「预估返 ¥2.69」，disclaimer_keys=[price_basis, rebate_estimate]。
- **例**：no_rebate 粘贴卡 → disclaimer_keys=[price_basis]。
- **例**：素材卡、normal → [price_basis, rebate_estimate, material_ref]。
- 「¥x 起」「规格以下单页为准」何时出现由 BR-PROD-04 决定，其中金额格式按 BR-TEXT-10（例：「券后 ¥29.9 起」）。
- 海报例：09-29 生成，券后 ¥29.9 → 海报上印「券后 ¥29.9 · 09-29 取价」+ price_basis 文案。

#### BR-PRICE-18 细则 · 价格与返利禁止用语

- 状态：待决策
- 状态变更：原为默认假设；新增词是否禁用属合规定性、决策人为法务，按 README §0.3 改为待决策（2026-09-30 自查）
- 默认值：六个已定词 + 最低价 + 三个待法务确认词（返利最高、最高返、原价）默认启用；匹配与扫描规则按 BR-TEXT-13；理由：宁可多拦，误伤只需改写文案，漏拦有广告法风险
- 决策人：法务
- 依赖平台能力：无
- 取代：
  - 规划/01 E02 F-PRIV-09：「禁用词：全网最低、历史最低、最便宜、最高返利、稳赚、必返（缺「最低价」「原价」）」
  - PRD修订_后端功能规划 §2.3：「返利展示文案禁用「最高」「最低价」」
- 来源：规划/01 §1 卖点表述；规划/01 E02 F-PRIV-09；PRD修订_后端功能规划 §2.3 返利报价口径；规划/06 Q-F4
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 一处维护：原稿本条另写了一套匹配方式（大小写与全半角归一）与 CI 扫描范围，与 BR-TEXT-13（NFKC 归一、去空白与标点、字段白名单）重复且不一致；现统一以 BR-TEXT-13 为准（NFKC 归一已覆盖全半角与大小写）。本条只保留价格类词的收录要求与改写方式。
- P1 降价提醒与价格历史组件里「自 &lt;开始记录日> 以来观察到的最低价」命中「最低价」。法务确认前的中性模板以 BR-TEXT-13 细则「降价表述」为准（不出现「最低」二字），提醒措辞见 BR-WATCH-14；「新低」类说法在法务答复前不使用，但不列入 CI 扫描词。
- 已知误伤：「最低价格区间」一类说法会命中「最低价」，文案改写为「价格下限」。
- 「到账」「入账」等资金用词见 BR-TEXT-01 与 README §1.2，不在本条。

#### BR-PRICE-19 细则 · 降价提醒监控的价格口径

- 状态：待验证（随 BR-WATCH-03）
- 本条只作指针：提醒监控的价格字段、口径、取价接口、例子与验收依据只在 BR-WATCH-03 维护；查询失败与缺失价格见 BR-WATCH-09，触发比较符见 BR-WATCH-04。本主题只负责 final_price_fen 本身的定义与计算（BR-PRICE-01、BR-PRICE-03）。
- 变更记录：原稿本条另写了一套监控口径（状态默认假设）并含「查询失败记 failed、不当 0 元」一句，与 BR-WATCH-03（待验证）、BR-WATCH-09 重复且状态不一致；按 00 变更流程收拢为一处，口径与状态以 BR-WATCH-03 为准，编号保留不复用。原稿的依赖平台能力（链路⑤按商品取价的成本与频率）、取代的 PRD v2.1 §10.19 与例子已并入或已由 BR-WATCH-03、BR-WATCH-07 覆盖。

#### BR-PRICE-20 细则 · 点击复核的价格新鲜度窗口

- 状态：待决策
- 默认值：0 秒（每次 open 实时取价，与规划/01 §5 J3 步骤 4、F-AGENT-08 和规划/02 §9.2「点击时实时复核」一致）；候选 300 秒以节省联盟调用；age = N 时仍在窗口内（≤ N 复用）
- 决策人：负责人
- 依赖平台能力：三平台转链与详情接口的 QPS / 日配额（规划/09，待实测）
- 取代：
  - PRD修订_后端功能规划 §2.4：「优先取 ≤15 分钟缓存转链结果，过期才实时重转并复核」
- 来源：规划/01 §5 J3 步骤 4、F-AGENT-08；规划/02 §9.2；PRD修订_后端功能规划 §2.4
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- **取舍**：N=0 时每次点击一次联盟调用，价格最准；N=300 可减少调用，但 5 分钟内的价格变化在点击时发现不了，只能靠下单页。
- **例（N=300）**：10:00 下发快照 2990；10:01 预转链得 3050（preconvert_at=10:01）；10:03 点击 → 预转链较新且 age 120 秒 → new=3050，diff=60，2%，不弹窗，静默更新并返回 new_link_id。
- **例（N=300）**：10:00 下发快照 2990，无预转链；10:08 点击 → age 480 秒 > 300 → 实时取价。
- **例（N=0）**：任何时刻点击都实时取价。
- 决策依据：联盟接口 QPS 与日调用配额（规划/09），以及 M-内测点击量估算。

#### BR-PRICE-21 细则 · 查返利三态与带返利跳转

- 状态：默认假设
- 默认值：三态由 coupon_fen 与 rebate_basis 推导，不新增字段；显示返利金额的购买入口一律经 open 转链；不经转链的入口不显示返利金额
- 决策人：负责人
- 依赖平台能力：无（无推广参数商品页的生成方式见 BR-PRICE-08，待实测）
- 取代：
  - PRD v2.1「有券有返 / 有返无券 / 无返利」、参考_花卷云功能查漏底稿「有券有佣 / 无券有佣 / 无券无佣」（叫法对照见 08 §13 rebate_basis 行）：统一为本条三态，有券但佣金为 0 也归「无返利」
- 来源：PRD修订_后端功能规划 §2.4 无返利态、§13.2 第 25 条「无返利态；所有带佣金的跳转必须转链」；08 §13 rebate_basis 行「推导规则写入 08」
- 需同步修改的规划文档：规划/04 §8.3 product_card 说明补三态推导（未同步，登记于 README §0.6）

例表参数同 BR-CALC-20 细则算例（price_fen=3990、佣金率 2000bp、技术服务费 1000bp、比例 5000bp，只作示意）：

| coupon_fen | rebate_basis | rebate_min–max（分） | 三态 | 卡片展示 |
|---|---|---|---|---|
| 1000 | normal | 269–269 | 有券有返 | 券后 ¥29.9 · 预估返 ¥2.69 |
| 0 | normal | 359–359 | 无券有返 | 售价 ¥39.9 · 预估返 ¥3.59 |
| 1000 | price_compare_risk | 0–269 | 有券有返 | 券后 ¥29.9 · 预估返 ¥0–¥2.69 |
| 1000 | no_rebate | 0–0 | 无返利 | 券后 ¥29.9 · 暂无返利 |
| 0 | no_rebate | 0–0 | 无返利 | 售价 ¥39.9 · 暂无返利 |

- **例**：Agent 卡「去淘宝购买」显示预估返 ¥2.69 → 点击走 open → 外跳转链结果；open 返回 50303 → 按 BR-PRICE-13 给次按钮「仍去购买（无返利）」，该按钮及其跳转提示不显示预估返。
- **例**：首页「打开淘宝」快捷入口直接唤起淘宝 App 首页，不带跟单参数 → 入口不得显示任何返利金额。
- 统计：经营看板的查券三态分布按本条推导；price_unavailable、off_shelf 单独计数，不并入任何一态。
- 推广参数只能由服务端注入（BR-ATTR-05）；本条只约束「显示返利金额」与「经转链跳转」必须同时成立。

### 3.3 本主题未决问题

1. 比价佣金折算比例 rebate.taobao.compare_rate_ratio_bp 的正式默认值：要等 06 Q-G2（联盟答复）与 06 Q-D2（优券汇 flow_source=1 历史佣金率差），当前 5000 只是占位（BR-PRICE-07）。
2. 拼多多用拼单价（min_group_price）还是单买价，京东是否混入 PLUS 价，淘宝 final_promotion_price 的实际口径，上游价格筛选与排序参数作用于券前价还是券后价：都要等 S0 实测（BR-PRICE-02、BR-PRICE-15）。
3. 预估返利基数 B 是否在 N 之后再扣平台预留 reserve_bp；比例约束取规划/01 的 r_own_bp + r_direct_bp ≤ 8000（规划/01 写作 r_self + r_direct，C-29 统一列名），还是后端规划的 r_buyer + r_l1 + r_l2 ≤ 10000：以 BR-CALC-02（基数 B）、BR-CALC-07（比例合计上限）的决策为准，决策前按规划/01 §3 分账口径（D8 见规划/00 §3.2），BR-CALC-20 随之调整。
4. 各平台技术服务费率 tech_fee_bp[platform] 的取值：待核实（BR-CALC-20）。
5. 点击复核的价格新鲜度窗口 link.open.requote_after_sec 取 0（每次实时，规划/ 口径）还是 300（省联盟调用）：负责人决定（BR-PRICE-20）。
6. 「预估返后 ¥x」把不确定的返利折进价格表述，是否合规：需法务确认（BR-PRICE-09）。
7. 素材参考价与联盟规范「展示价来自联盟接口」（F-PRIV-08）是否冲突：需法务或联盟确认（BR-PRICE-10）。
8. 「原价」「划线价」对推广方的具体法规限制条款，以及无券时用「售价」是否足够：待法务核实（BR-PRICE-04）。
9. 禁用词新增的四个词（最低价、返利最高、最高返、原价）是否确认，其中后三个尚待并入 BR-TEXT-13 清单；P1 降价提醒与价格历史组件的替代说法（法务确认前用 BR-TEXT-13 的中性模板）：法务在 06 Q-F4 审阅时给出（BR-PRICE-18、BR-TEXT-13、BR-WATCH-14）。
10. 价格已变动阈值用「或」时，高价商品变动 1 元也会弹窗（例：¥3000 变 ¥3001）。是否改成「且」或分价格段设阈值？默认沿用规划/ 的「或」，并做成配置（BR-PRICE-13）。
11. 多件、多规格商品按哪一个 SKU 取价：已由 BR-PROD-04 给出（采用联盟返回的商品级价格，规格不确定时显示「规格以下单页为准」，区间或最低规格价显示「¥x 起」），已补进 BR-PRICE-01 细则；BR-PROD-04 本身待决策，京东 item 模式的粒度待 S0 实测。
12. 三平台是否返回包邮 / 运费字段、券是否带稳定券 ID、如何由 product_key 生成无推广参数商品页：待实测（BR-PRICE-03、BR-PRICE-08、BR-PRICE-14）。
13. 错误码变更需负责人确认后改规划/04 §7：新增 50303「暂时无法确认价格或生成链接」，30142 标为废弃、淘礼金领完统一用 30602（BR-PRICE-13、BR-PRICE-14；30142 按 C-03 默认处理）。
14. 与其他主题口径不一致、尚未列入 §14.3 的分歧（待合稿登记并裁决）：
    - 【已由 C-22 处理，默认处理，待负责人确认（财务知悉）】BR-PRICE-07 / BR-PRICE-09 与 BR-CALC-16：取不到比价佣金率时，本主题用占位 compare_rate_ratio_bp 展示区间，BR-CALC-16 不展示金额。处理：下单前比价展示只按 BR-PRICE-07（区间，不另显示保守值，不改为不展示金额）；BR-CALC-16 只保留订单侧计算。
    - 【已由 C-29 处理】BR-PRICE-06 与 BR-CALC-06 / 第 13 节映射表：比例字段名 r_self_bp（映射表「保留规划写法」）与 r_own_bp（BR-CALC-06）。处理：统一为 commission_rules 列名 r_own_bp、r_direct_bp，r_self / r_self_bp 只作别名。
    - BR-PRICE-15 与 BR-AI-05：「再便宜点」上限公式（min(上一轮上限, 已展示最低价 − 1) 还是 结果集最低价 − 1）。
    - 【已消解】BR-PRICE-01 / BR-PRICE-19 与 BR-WATCH-03 细则：平台直接返回的券后价是否可直接取用。BR-WATCH-03 细则已写明一律按 BR-PRICE-01 自算、进白名单前平台券后价字段只存原始报文，两处一致；BR-PRICE-19 已改为指向 BR-WATCH-03 的指针。
    - BR-PRICE-18 与 BR-TEXT-13：禁用词清单与匹配规则两处维护；本条已改为只列价格类词、匹配规则归 BR-TEXT-13，BR-TEXT-13 需补入「返利最高」「最高返」「原价」。

---
