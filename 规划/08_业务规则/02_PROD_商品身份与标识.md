# 08 业务规则 · 2. 商品身份与标识（BR-PROD）

返回 [README](README.md)（使用规则、术语表、规则索引）

## 2. 商品身份与标识（BR-PROD）

本节规定：“同一商品”的判定、product_key 格式/派生/不可变、raw_item_id 与 item_ref 取用、缓存与去重口径。共 11 条（已确认 6、默认假设 1、待决策 1、待验证 3）。

2026-10-03 功能对照补缺第 4 批（docs/changes/20261003-功能对照补缺.md「第 4 批」；「功能对照 G-xx / Q-xx」是该批缺口清单与待确认题的编号）：BR-PROD-10 正文加一句、细则新增「按平台的搜索开关」（功能对照 G-47），状态不变；本批不新增、不作废 BR-PROD 条目。

### 2.1 规则一览

| 编号 | 规则 | 状态 | 影响面 |
| --- | --- | --- | --- |
| BR-PROD-01 | **同一商品的判定**<br>两条商品记录是“同一商品”，当且仅当同时满足：`app_id` 相等；`platform` 相等；两条的 `product_key` 均非 null，且经 `resolveProductKey`（BR-PROD-02）解析后逐字节相等（区分大小写）。不同 app_id 的 product_key 不得相互比较，也不得共用 product_refs、商品缓存、商品池或价格快照。依据有两条：淘宝商品 ID 后半段据公开资料只对单个联盟账号稳定（规划/09 CAP-TB-01，可信度中，待 S0 实测；本条按保守口径先行限制）；规划/04 规定业务唯一键以 app_id 开头。不同平台的商品永远不是同一商品，即使标题、品牌、规格完全相同（跨平台同款见 BR-PROD-09）。购买件数（订单 `quantity`）永远不进入商品身份；规格/SKU 是否进入身份按 BR-PROD-04 执行。天猫商品 platform=`taobao`（BR-PROD-10）。去重、缓存、商品池、link_log、订单关联、Agent 卡片、订阅监控对象中，凡需判断“同一商品”，一律只调用本条的 `isSameProduct`，不得用 `raw_item_id`、标题或图片判断。 | 已确认 | packages/domain isSameProduct；orders.product_key；link_logs.product_key；product_refs 主键 (app_id, product_key)；pool_items 唯一 (app_id, pool_id, product_key)；缓存键 app_id 前缀（BR-PROD-07）；Agent 卡片去重；tracked_item（P1）；客服话术：同一商品；验收 V-PK-1（细则「验收依赖」） |
| BR-PROD-02 | **product_key 格式、校验、别名与不可变**<br>`product_key` = `<key_prefix>:<stable_id>`。key_prefix 取 `platforms` 表的 `key_prefix` 列，现值为：taobao=`tb`、jd=`jd`、pdd=`pdd`、meituan=`mt`、vip=`vip`、douyin=`dy`、kuaishou=`ks`、suning=`sn`；eleme 没有商品形态，key_prefix 为空，不生成 product_key。代码中不写死平台前缀枚举。`stable_id` 由 BR-PROD-03 派生，原样保留大小写，长度 1–124，字符集为可打印 ASCII（0x21–0x7E）去掉 `#`、`/`、`?`；整串长度 ≤128。非 null 的 product_key 一旦写入任何表就不可修改；null 视为未写入，可以回填一次。product_key 不得包含 user_id、推广位、relation_id 等用户或归因信息。客户端、H5、Agent 只能把它当不透明字符串透传，不得解析、拼接，也不得从中推算 raw_item_id；放进 URL 路径时必须 `encodeURIComponent`。所有入口（API 入参、isSameProduct、去重、缓存键、pool_items/tracked_item 写入）都先调用 `resolveProductKey`。`product_key_aliases` 只用于一对一的派生规则变更；粒度变化（如京东从 item 级改为 sku 级）不得用别名映射。 | 已确认 | platforms 字典表 key_prefix 字段；packages/domain validateProductKey / resolveProductKey；所有含 product_key 的表（links、link_logs、orders、pool_items、product_refs、tracked_item、price_snapshot）；GET /v1/products/{product_key}；POST /v1/links/convert；JSBridge trade.openProduct / trade.convertAndOpen；Agent product_card.product_key；product_key_aliases（新增）；错误码 20001、30131 |
| BR-PROD-03 | **各平台 stable_id 派生、稳定性验证与订单派生**<br>`stable_id` 只能由 `packages/domain` 中唯一的纯函数 `deriveProductKey(platform, unionPayload)` 派生；搜索、详情、口令/链接解析、商品池入库、订单同步五个入口调用同一个函数。MVP 只有 taobao、jd、pdd 生成 product_key；其他平台在本条补充派生规则之前，一律抛 `PRODUCT_KEY_UNDERIVABLE`。默认派生规则：淘宝取联盟返回的 item_id 原串按 `-` 分隔后的最后一段（没有 `-` 时取整串）。京东按全平台配置 `product_key.jd.mode` 取值，不按单条响应切换：`sku` 取 skuId；`item` 取 itemId 按 `_` 分隔的第 2 段，加 `i_` 前缀，即 `jd:i_<B段>`。拼多多取 `goods_id`，goods_sign 只作 raw_item_id，不进 key。派生结果为空串，或不满足 BR-PROD-02 的字符集或长度，一律按 `PRODUCT_KEY_UNDERIVABLE` 处理，不截断、不转义。platforms 表为每个平台记录 `key_stability`（unverified / stable_24h / stable_7d / unstable），按本条的验证标准判定；未达到 stable_7d 的平台不得上线订阅提醒和价格历史。验证不通过时，由负责人决定是否启用 BR-PROD-06 兜底键（写 ADR）；批准前该平台继续按默认规则派生。订单入口是否派生由平台级配置 `product_key.order_derivable.<platform>` 决定，默认 false。product_key 为 null 的订单不能使用“同商品”证据；证据等级只由 BR-ATTR 规定，本条不新增证据类型；禁止把“同平台”作为 link_log 回填或订单找回自动匹配的依据。 | 待验证 | packages/domain deriveProductKey；platforms.key_stability（新增）；配置 product_key.jd.mode；配置 product_key.order_derivable.&lt;platform>；catalog 搜索与详情；POST /v1/inputs/parse（规划/04 原写 /v1/clipboard/parse，C-14）；POST /v1/links/convert（传 url）；商品池入库；order-sync 订单入库 orders.product_key；links.product_key / raw_item_id 可空（活动类、PDD 直链降级）；错误码 30131、30132、30143；规划/09 平台能力验证表；fixture：每平台 ≥30 条；验收 V-PK-1、V-PK-2（BR-PROD-01 细则「验收依赖」） |
| BR-PROD-04 | **规格/SKU 与数量粒度**<br>`product_key` 的粒度等于联盟接口可报价、可转链的最小单位：淘宝、拼多多为商品（listing）级；京东在 `product_key.jd.mode=sku` 时为 skuId 级，`item` 模式下的粒度待 S0 确认 itemId 与 skuId 是否一一对应。规格（颜色、尺码、容量、件装）不单独进入 product_key：同一个淘宝或拼多多商品下的不同 SKU 共用一个 product_key，价格采用联盟返回的商品级价格（口径见 BR-PRICE）。商品级价格对应的规格无法确定时，卡片和详情页的价格旁必须显示“规格以下单页为准”；联盟返回价格区间，或确知该价为最低规格价时，显示“¥x 起”。页面、卡片、Agent 都不得声称“某规格的价格”。用户在 spec 或价格条件中指定了规格时，Agent 文字不得出现任何金额（BR-AI-06），也不得说“该规格 ¥x”或“满足 50 元以内”，只能说“你要的规格价格以下单页为准”；金额只在卡片上显示，并带本条的规格限定语（拍板第二批 AI-24 统一）。Agent 卡的逐张核对标记（符合 / 已放宽 / 规格待确认）由服务端代码判定（拍板第二批 AI-04，判定规则见 BR-AI-24），对用户只用“标题显示为 X”“规格待确认”这类说法，不写“符合你的要求”（拍板第二批 JEV-02）；标记不改变本条的价格限定语。规格文本 `spec_text` 只作为检索条件和展示附加信息，不参与去重、商品维度缓存键和归因；作为搜索请求参数时，它进入搜索缓存键（BR-PROD-07）。不同 product_key 之间（包括京东同一商品的不同 sku、同一店铺分别上架的 12 盒装和 24 盒装）不得合并为同一商品，也不得合并比价；MVP 不做任何 SKU 间比价。 | 已确认 | product_key 粒度；search_products.spec 参数；Agent 卡片去重与折叠；Agent 价格话术（文字不出金额）；Agent 卡逐张核对标记（BR-AI-24）；商品卡与详情页价格文案（规格以下单页为准 / ¥x 起）；降价提醒（P1）监控对象与文案；客服话术：价格与所选规格不一致；规划/09 能力验证行 |
| BR-PROD-05 | **raw_item_id 保存、取用与重新解析**<br>`raw_item_id` 等于联盟返回的商品 ID 原串：淘宝为 item_id 原串；京东 sku 模式为 skuId，item 模式为 itemId 全串；拼多多为 goods_sign。按 text 原样保存，不得拼接、截断、推算或跨平台复用。`links`、`link_logs`、`orders` 必须同时保存 product_key 与 raw_item_id（活动类转链两者都为 null，见 BR-PROD-03）。转链、详情、刷新时按以下顺序取原串：① 本次请求携带的卡片 `item_ref`（BR-PROD-11）中的原串，或 `links.raw_item_id`，要求取得时刻距今 ≤1800 秒；② `product_refs` 中 (app_id, product_key) 的原串，要求 `refreshed_at` 距今 ≤1800 秒（已启用兜底键的平台跳过这一步，见 BR-PROD-06）；③ 重新解析。product_refs 只接受 search、detail、parse、pool 四个来源写入；订单同步只写 orders.raw_item_id，不写 product_refs。`refreshed_at` 等于本次联盟响应的接收时刻；写入使用条件更新，较旧的响应不得覆盖较新的记录。重新解析的结果按细则「结果分类」表的三类（下架 / 引用失效 / 暂时失败）处理；任何情况下都不得用过期原串转链。订单的 product_key 派生失败或未开启派生时，product_key=null、raw_item_id 照存，不得丢单。 | 待验证 | product_refs（新增表）；links.raw_item_id；link_logs.raw_item_id；orders.raw_item_id / product_key 可空；POST /v1/links/convert；POST /v1/links/{link_id}/open；product_card.availability（新增 ref_expired）；错误码 30141、30143（新增，只表示商品信息已失效；link_id 无效为 30144，属 BR-AI-11）、50303（open 复核失败且无缓存，BR-PRICE-13）、50401；商品池刷新任务 |
| BR-PROD-06 | **ID 不稳定时的兜底键**<br>默认不启用。只有某平台按 BR-PROD-03 判定为 unstable（或拼多多响应不含 goods_id），且负责人批准并写 ADR 后才启用。兜底键格式为 `<key_prefix>:fp_<hex32>`：对 UTF-8 编码的 `platform\|shop_id\|norm(title)` 计算 SHA-256，取小写十六进制结果的前 32 个字符（128 bit）。`norm` 按顺序执行：① NFKC；② 删除 `【…】` 及其中内容（非贪婪匹配，可以出现多处）；③ 转小写；④ 删除所有属于 Unicode 类别 \\p{P}、\\p{S}、\\p{Z}、\\p{C} 的字符（包括空白、emoji、×、\*、+）。兜底键只在同一个 shop_id 内合并；shop_id 缺失时兜底键为 null，按 BR-PROD-03 的派生失败处理（搜索结果丢弃并计数，订单以 null 入库）。兜底键只用于缓存、会话内去重、商品池和 links/link_logs 记录。它不得作为归因的“同商品”强证据；在归因和订单找回中，最多按“同店铺”证据处理（见 BR-ATTR）。兜底期间，该平台不得上线订阅提醒和价格历史，BR-WATCH 不得另设降级上线路径。兜底期间，转链、详情、刷新只使用卡片 item_ref 或 links.raw_item_id 中的原串（BR-PROD-05 第①步），不得按 product_key 查 product_refs 取原串。原串过期时重新解析；如果同一店铺内有多个 norm 标题相同的候选，则不转链，返回 30143“商品信息已失效，请重新搜索”（与 BR-PROD-05 同码同文案）。启用或停用都须负责人批准并写 ADR；切换时新旧键不做别名映射，旧键保留为只读历史键（BR-PROD-02）。 | 待决策 | deriveProductKey 兜底分支；product_key_aliases（兜底切换不使用）；转链取原串顺序（BR-PROD-05、BR-PROD-11）；价格快照与订阅提醒（P1）；归因证据等级（BR-ATTR）；错误码 30143；ADR |
| BR-PROD-07 | **商品缓存口径**<br>搜索结果和商品详情缓存在服务端，命中条件为 `now − fetched_at ≤ 300 秒`。fetched_at 是收到联盟响应的时刻，存在条目内，毫秒精度，以服务端时钟为准。Redis 物理 TTL 为 3600 秒，只用于清理，不作命中判断。凡是影响联盟返回结果的请求参数，都必须进入搜索缓存键；不影响结果的参数（user_id、device_id、我方游标、会话 ID）不得进入。缓存键不得含推广位、relation_id 或任何归因参数；商品维度只用 product_key，不用 raw_item_id；所有键以 app_id 开头。搜索和详情调用联盟时，统一使用固定的查询专用推广位（新增 pid_scene=`query`，不下发给用户、不用于转链），不带 relation_id。写入缓存前，必须剔除联盟返回的全部链接和口令字段（如 coupon_share_url、click_url、url、\*_tpwd）。缓存只存联盟公共数据（标题、图、店铺、价格、券、佣金比例、fetched_at）；预估返利在读缓存后按当前用户等级实时计算，不得写入缓存。转链结果按 (app_id, user_id, platform, product_key, pid_scene) 隔离缓存，≤900 秒，禁止跨用户复用；只复用联盟返回的推广链接或口令本体，每次 convert/open（包括缓存命中）都新建 links 与 link_logs 行。联盟熔断打开期间，可以返回 age ≤ `search.cache.stale_max_age_s`（默认 300 秒）的条目，并标 `stale=true`；没有符合条件的条目时，搜索返回 50304（新增：&lt;平台>搜索暂不可用；码值以规划/04 §7 为准），不拿商品池冒充搜索结果；详情按 BR-PRICE-11 改读商品池价格并标 stale；首页信息流改读商品池（拍板第二批 TRADE-12）。50301 只表示转链开关关闭（BR-PROD-10）。价格与券以转链或打开时的实时查询为准（BR-PRICE）。跨用户共享搜索、详情缓存的前提是验证通过“结果不随 relation_id 或推广位变化”（规划/09 CAP-TB-03、CAP-TB-13 及京东、拼多多对应项）；验证不成立时，缓存键加入推广位维度，或改为按用户查询。 | 待验证 | Redis 缓存键规范；products_cache（Redis）；GET /v1/products/search 响应 stale、quoted_at；GET /v1/products/{product_key}；POST /v1/links/convert；links.cache_hit、links.expire_at；pid_scene 新增 query；配置 search.cache.stale_max_age_s；配置 search.filter_cfg_version；熔断降级（规划/02 故障表）；错误码 50304（新增，搜索无缓存）；验收 V-PK-1（命中缓存；BR-PROD-01 细则「验收依赖」） |
| BR-PROD-08 | **去重与唯一键口径**<br>所有商品去重的键为 (app_id, platform, resolveProductKey(product_key))。product_key 为 null 的条目不参与去重，也不进入以下集合。① Agent 多平台并发检索合并后，同一个键只保留 1 条；跨平台不去重。同一个键有多条时（如拼多多同一商品的多个券佣计划 goods_sign），保留 final_price_fen 最低的一条，相同取 rebate_max_fen 高的，再相同取排序靠前的；转链用保留那条的 goods_sign（拍板第二批 TRADE-14）。单平台搜索同一页内出现同键多条时按同一规则保留。② 单平台搜索分页时，同一查询会话内已下发过的 product_key 在后续页中剔除。查询会话的定义：同一请求者（已登录用 user_id，未登录用 device_id），在 BR-PROD-07 搜索缓存参数（不含 page_no）完全相同时的连续翻页。请求第 1 页时新建 search_session_id 并写入游标；30 分钟没有请求即过期；筛选或排序一变就开新会话。已下发集合存在 Redis，上限 500 个，超出后不再去重。去重只在读缓存之后、下发之前执行，缓存里保存的是联盟原始页。③ 商品池唯一键为 (app_id, pool_id, product_key)。重复入库时，用本次提交的 sort、start_at、end_at 覆盖原记录，created_at 和创建人不变，并立即触发一次联盟复核：通过则 status=online；不通过则保持或置为 offline，并向运营显示原因。④ P1 订阅监控：tracked_item 唯一 (app_id, platform, product_key)；price_snapshot 以 (app_id, product_key) 为键；query_seen_item 唯一 (query_id, product_key)。⑤ 同一条消息解析出多个链接（≤3 个；第 4 个起不处理，上限由 BR-AI-01 细则 parse_input 行维护）时，同一个键只出 1 张卡。 | 已确认 | catalog 多平台检索合并；搜索游标（search_session_id + page_no）；Redis 会话已下发集合；pool_items 唯一约束与复核；tracked_item / price_snapshot / query_seen_item（P1）；parse_input 多链接出卡；Agent product_list 卡片 |
| BR-PROD-09 | **跨平台同款判定（P1）**<br>MVP 不实现。P1 实现时，跨平台同款只能作为独立关系 `same_item_links(app_id, product_key_a, product_key_b, match_level, basis, created_at)` 保存，不得合并 product_key，也不得共享缓存或价格快照。判定为“同款”必须同时满足四条：品牌归一后相同；核心品名或型号相同；规格归一后单件净含量与每件数量都相等（如 250ml×24 与 24×250ml 相等）；标题不含“同款/平替/适用于/兼容”。只满足品牌与品名、规格不同的，只能标“规格不同”并展示折合单价，不得称“同款”，也不得参与“哪家更便宜”的结论。只有模型打分、没有通过规则的，只能标“相似商品”。 | 已确认 | find_same_item 工具（P1）；same_item_links 表（P1）；Agent 比价话术；截图找同款（P1）；规划/02 模型路由 Plus 档同款打分 |
| BR-PROD-10 | **平台编码、天猫归属与平台开关**<br>商品身份中的 `platform` 取 规划/04 §2.1 的字符串编码（taobao、jd、pdd、meituan、vip、douyin、eleme、kuaishou、suning），不得使用数字编码。天猫商品 platform=`taobao`，用 `shop_type=tmall` 区分，product_key 前缀为 `tb:`；shop_type 的取数为待验证子项（见细则「依赖平台能力」）：商品侧取联盟 user_type（1=天猫），订单侧天猫标识字段待 规划/09 CAP-TB-07（U-43）实测，验证前 orders.shop_type 可空，由商品侧回填；`detail.tmall.com` 等天猫链接的解析结果 platform=taobao。是否生成 product_key，只取决于该平台在 platforms 表中有 key_prefix，且 BR-PROD-03 已给出派生规则，与转链开关无关。能识别域名，但该平台不在 platforms 表中，或其解析与搜索能力都未开启的，解析、详情、搜索返回 30131“暂不支持该平台”，不写 product_refs。`convert.enabled.<platform>=false` 只控制转链：仍生成 product_key，正常展示卡片；`POST /v1/links/convert` 与 `/open` 返回 50301，卡片按钮和文案按 规划/09 中该平台的降级写法处理（如 CAP-TB-06 的“稍后再试”、CAP-TB-07 的“淘宝返利即将开放”）。另有按平台的搜索开关 `search.enabled.<platform>`：只管关键词搜索（搜索 Tab、搜索接口、Agent 的关键词检索），与转链开关相互独立（细则「按平台的搜索开关」，2026-10-03）。 | 已确认 | platforms 字典表；orders.shop_type；product_card.shop_type；parse_input 输出；错误码 30131、50301、50304（data.reason=search_disabled）；配置 convert.enabled.&lt;platform>、search.enabled.&lt;platform>、/v1/config.features.search_status.&lt;platform>；卡片按钮降级文案 |
| BR-PROD-11 | **商品引用令牌 item_ref**<br>服务端在每个下发的商品条目中附带 `item_ref`，包括搜索结果、详情、解析结果、商品池条目和 Agent product_card。item_ref 是服务端加密并签名的不透明串，内容为 app_id、platform、product_key、raw_item_id、fetched_at（联盟响应的接收时刻），不含 user_id。客户端、H5、Agent 只能原样透传，不得解析或自行构造。`POST /v1/links/convert`（按 product_key 调用时）必须携带用户所点卡片的 item_ref。服务端校验签名，且 app_id、product_key 与请求一致后，将其作为 BR-PROD-05 第①步的原串来源。item_ref 缺失、签名无效、无法解密或 app_id 不符时，忽略令牌，按 BR-PROD-05 第②③步继续，不报错；签名有效但 product_key 与请求不一致时返回 20001。`POST /v1/links/{link_id}/open` 以 links.raw_item_id 与 links.raw_fetched_at 作为第①步来源。item_ref 不得用于归因，也不得以明文写入日志。 | 默认假设 | product_card.item_ref（新增）；GET /v1/products/search 与 GET /v1/products/{product_key} 响应条目；POST /v1/inputs/parse 响应（规划/04 原写 /v1/clipboard/parse，C-14）；POST /v1/links/convert 入参 item_ref；links.raw_fetched_at（新增）；JSBridge trade.openProduct / trade.convertAndOpen 参数；Agent product_card；商品池下发接口 |

### 2.2 细则

#### BR-PROD-01 细则 · 同一商品的判定

- 状态：已确认
- 默认值：app_id、platform 相同，且 product_key 非 null、解析别名后相等，即为同一商品；件数不进身份
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - PRD v2.1 §10.7；修订① 3.7：「去重：同一平台同一 item_id 只出一张卡（改为同一 app_id + platform + product_key）」
  - PRD v2.1 §10.20：「tracked_item 以 (platform, item_key) 唯一（item_key 统一改名为 product_key，并加 app_id）」
- 来源：规划/01_需求规划.md E04 F-PROD-06；规划/04_数据模型与契约.md §1 术语表、§2.1、§3 表规范（业务唯一键以 app_id 开头）；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-01；PRD修订_后端功能规划_2026-09-29.md 2.3、10.1 AC-TRADE-004；返利 App PRD（三端原生 + H5 + Agent）.md §10.7、§10.20
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

**判定函数**（放在 `packages/domain`，全系统只此一份）：
```ts
isSameProduct(a, b) =
  a.product_key != null && b.product_key != null &&
  a.app_id === b.app_id && a.platform === b.platform &&
  resolveProductKey(a.product_key) === resolveProductKey(b.product_key)
```

**必备单元测试**
| A | B | 结果 | 原因 |
| --- | --- | --- | --- |
| app1 / taobao / tb:K1（raw=`X-K1`，10:00 搜索） | app1 / taobao / tb:K1（raw=`Y-K1`，10:07 搜索） | true | product_key 相同，原串不同不影响（验收用例 V-PK-1，见下文「验收依赖」） |
| app1 / taobao / tb:K1，买 1 件 | app1 / taobao / tb:K1，买 3 件 | true | 件数不进身份 |
| app1 / taobao / null | app1 / taobao / null | false | null 不与任何记录相同，包括另一条 null |
| app1 / taobao / tb:K1 | app2 / taobao / tb:K1 | false | 不同 app_id 之间不比较 |
| app1 / jd / jd:100012 | app1 / pdd / pdd:123 | false | 跨平台一律不同 |
| app1 / jd / jd:OLD（别名指向 jd:NEW） | app1 / jd / jd:NEW | true | 先按别名解析 |

**shop_type 不一致**：同一 product_key 两次联盟返回的 shop_type 不同时，以 refreshed_at 较新的一次为准，并记告警；shop_type 不参与身份判定。

**用户话术**：“同一个商品”指同平台、同一个商品链接对应的商品，不承诺同一颜色或尺码。

**解除 app_id 限制**：S0 若证明某平台的 stable_id 与联盟账号无关，由负责人写 ADR 取消该平台的 app_id 限制；在此之前按本条执行。

**验收依赖**：本条定义已确认。本主题引用两条验收用例；V-PK-1、V-PK-2 只是本主题内的简称，正式编号以「归入」列为准（归属见 规划/10 §5.4）。原编号来自参考文档（后端功能规划 10.1 的 AC-TRADE-*；TRADE 不是 规划/01 §6 的 Epic 代码），只作旧编号映射：

| 简称 | 用例（可观察结果） | 原编号 | 归入 |
| --- | --- | --- | --- |
| V-PK-1 | 同一淘宝商品两次搜索拿到不同 raw_item_id，product_key 相同，第二次在 300 秒命中窗口内命中缓存（BR-PROD-07） | AC-TRADE-004 | AC-PROD-06（05 任务，不在 10 首个流程用例内） |
| V-PK-2 | 淘宝订单付款前 15 天内有同 product_key 的 Agent 转链：订单 source_scene=agent，并回填 agent_session_id（证据规则见 BR-ATTR） | AC-TRADE-012 | AC-S1-22（10 §2.6；10 该行对应 AC-ORD-08） |

V-PK-1、V-PK-2 在各平台能否通过，取决于 BR-PROD-03 的 S0 验证结果（V-PK-2 还要求该平台 `product_key.order_derivable.<platform>=true`）；未通过的平台，该验收标为“阻塞：待 BR-PROD-03”，不计为失败。

#### BR-PROD-02 细则 · product_key 格式、校验、别名与不可变

- 状态：已确认
- 默认值：前缀取自 规划/04 §2.1；长度、字符集、校验顺序、别名解析和 null 回填是本条补充的默认
- 决策人：代理可自定（粒度变化的迁移方案由负责人通过 ADR 决定）
- 依赖平台能力：无
- 取代：无
- 来源：规划/04_数据模型与契约.md §1、§2.1、§7 错误码；规划/01_需求规划.md F-PROD-06；PRD修订_后端功能规划_2026-09-29.md 2.3
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

**校验**（`packages/domain` 的 `validateProductKey`，JS 正则）：
```
^([a-z]{2,3}):([\x21\x22\x24-\x2E\x30-\x3E\x40-\x7E]{1,124})$
```
第 1 组必须等于 platforms 表中某一行的 key_prefix（查表判断，不写死）。

**校验顺序与错误码**（参数错误都放在 `data.fields.product_key`）
| 顺序 | 情形 | 返回 |
| --- | --- | --- |
| ① | 不匹配正则 | 20001 |
| ② | 前缀不在 platforms 表中 | 20001 |
| ③ | 请求另带 platform，且与前缀对应的平台不一致（如 platform=jd、key=`tb:…`） | 20001，不查联盟 |
| ④ | 前缀对应平台的解析与搜索能力都未开启 | 30131（BR-PROD-10） |

单元测试样例：`tb:7Kq9LmN3pQ` 通过；`tb:a/b`、`tb:a?b`、`tb:a#b`、`tb:`、`tb:a b`、`TB:abc`、`xx:abc`（表中没有 xx）均拒绝；`jd:` 加 124 个字符通过，加 125 个拒绝。

**例子**（stable_id 格式为示意，真实格式待 BR-PROD-03 实测）
- 淘宝原串 `AbC12xyz-7Kq9LmN3pQ` → `tb:7Kq9LmN3pQ`
- 京东 sku 模式 skuId `100012043978` → `jd:100012043978`；item 模式 → `jd:i_<B段>`
- 路由：`GET /v1/products/tb%3A7Kq9LmN3pQ`

**别名解析 `resolveProductKey(key)`**
- 沿 `product_key_aliases(old_key, new_key, reason, adr_id, created_at)` 一直跟到终点，最多 5 跳；超过 5 跳或出现环时告警，并按原键处理。
- API 响应一律返回终点键。
- 历史行（orders、links、link_logs）不回填，统计和归因时在读取时解析。
- 可变业务表（product_refs、pool_items、tracked_item、price_snapshot）由迁移任务改写为终点键；唯一键冲突时按 BR-PROD-08 ③ 合并。
- 适用情形：一对一变更，例如联盟升级商品 ID 格式、同时提供新旧 ID 一一对应（示意）。
- 不适用情形：粒度变化，例如一个 itemId 对应多个 skuId。这时旧键保留为只读历史键，新数据用新键；订阅和价格历史须由用户重新创建，或由 ADR 定迁移方案。京东上线时锁定一种粒度（BR-PROD-03 的 `product_key.jd.mode`）。兜底键（BR-PROD-06）启用或停用同样不用别名。

**null 回填**：orders.product_key 为 null 的行允许回填一次（例如 `product_key.order_derivable.<platform>` 后来改为 true）。回填只写 orders.product_key，不改变已有的归因结果和返利金额；未锁定订单是否重新评估证据由 BR-ATTR 决定，默认不重评。活动类转链在 links 中的 null 不回填。

**新增平台**：先在 platforms 表加一行并填 key_prefix，再在 BR-PROD-03 补上派生规则，之后才生成 product_key。

**与 08 §13.2 映射表的分歧（C-13）**：映射表 product_key 行曾提议把前缀改为平台编码（`taobao:` 等）。本条保持短前缀查表（tb、jd、pdd…），不改；映射表该行应改为「保留短前缀，前缀取 platforms.key_prefix」。本条内容未因此变化。按 C-13 默认处理，待负责人确认。

#### BR-PROD-03 细则 · 各平台 stable_id 派生、稳定性验证与订单派生

- 状态：待验证
- 默认值：淘宝取原串最后一段；京东按 product_key.jd.mode 派生（默认 item，即 jd:i_&lt;B段>）；拼多多取 goods_id；订单派生默认关闭；未达 stable_7d 的平台不上线提醒和价格历史
- 决策人：负责人
- 依赖平台能力：淘宝 CAP-TB-01：同一商品在不同时间（24h、7d）、不同接口下，item_id 后半段是否一致。京东 CAP-JD-01：新 App 媒体是否有 sceneId=2（skuId）权限；itemId 的分隔符与 B 段稳定性；itemId 与 skuId 是否一一对应。拼多多 CAP-PDD-01：搜索、详情、解析响应是否返回 goods_id，goods_id 是否稳定。三家：订单接口的商品 ID 能否派生出与搜索相同的 stable_id；更换联盟账号后 stable_id 是否变化
- 取代：
  - 开发任务拆解_v1 §12.1 H-23；PRD v2.1 G19：「淘宝商品 ID 稳定性待实测后定 item_key 规则（并入本条验证标准，item_key 改名为 product_key）」
  - 规划/04 §1；PRD修订_后端功能规划_2026-09-29.md 2.3：「拼多多 product_key = pdd: + goods_sign（改为 goods_id，依据 规划/09 CAP-PDD-01：同一商品有多个 goods_sign）」
  - 规划/09 CAP-TB-01 通过标准：「同一样本 3 次调用 item_id 后半段一致率 100%（改为引用本条验证标准）」
  - 规划/09 CAP-JD-01 通过标准③：「itemId B 段 24 小时内一致（改为引用本条验证标准）」
- 来源：PRD修订_后端功能规划_2026-09-29.md 2.3 product_key 行；开发任务拆解_v1_2026-09-29.md 12.1 H-23；返利 App PRD（三端原生 + H5 + Agent）.md §10.20 第 4 条、G19；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-01、3_JD_京东.md CAP-JD-01、4_PDD_拼多多.md CAP-PDD-01；规划/02_系统架构.md §7 link_log 回填；规划/04_数据模型与契约.md 订单找回 auto_matched、§7 错误码；规划/05_里程碑与任务拆分.md §3.2 B1-07；docs/changes/20261001-拍板第二批.md（TRADE-07、TRADE-08）
- 需同步修改的规划文档：5 处（计数仅作记录，落点见 README §0.6）

**派生表**
| 平台 | raw_item_id（调用联盟用） | stable_id | 依据 | 例（示意） |
| --- | --- | --- | --- | --- |
| taobao | item_id 原串 | 原串按 `-` 分隔的最后一段 | 前半段每次交互都变，后半段对单个账号在一定范围内稳定〔09 CAP-TB-01·中〕 | `AbC12xyz-7Kq9LmN3pQ` → `tb:7Kq9LmN3pQ`；`AbC-` → UNDERIVABLE |
| jd（mode=sku） | skuId | skuId；响应缺 skuId 时 UNDERIVABLE | 需要 sceneId=2 权限〔09 CAP-JD-01·高〕 | `jd:100012043978` |
| jd（mode=item） | itemId 全串（A段_B段） | `i_` + 第 2 段；分隔符待 S0 用样本确认后回填本条 | 非企业认证媒体只能用 itemId，A 段每次请求都变〔09 CAP-JD-01，DDX-231·中〕 | `jd:i_xxxx` |
| pdd | goods_sign | goods_id | 同一商品按券佣计划会有多个 goods_sign，不能作键；订单同时返回 goods_id〔09 CAP-PDD-01，DDX-171·中〕 | `pdd:123456789` |

`product_key.jd.mode` 默认 `item`，不依赖尚未批下的 sceneId=2 权限；S0 后由负责人锁定。从 item 切换到 sku 属于粒度变化，走 ADR（BR-PROD-02），不得原地改写已有键。拼多多的搜索、详情、解析响应如果不含 goods_id，该平台 key_stability 记为 unstable，交负责人按 BR-PROD-06 决定。

**验证标准**（规划/09 CAP-TB-01、CAP-JD-01、CAP-PDD-01 中 product_key 的通过标准统一引用本条）
- 样本：每平台 ≥30 个不同商品，与 parse_input 样本共用（规划/05 B1-07），须包含多规格商品。
- 调用：每个商品至少覆盖 2 种接口（搜索、详情、口令解析、订单中任取），分别在 T0、T0+24h、T0+7d 三个时点调用，每个商品总调用 ≥3 次。
- 判定：T0 与 T0+24h 的全部派生结果 100% 相同 → stable_24h；T0+7d 也 100% 相同 → stable_7d；任一商品出现不一致 → unstable。
- 账号：所有调用都使用该 app_id 在该平台唯一的“派生联盟账号”；更换或增加联盟账号前必须重跑验证，期间 key_stability 回到 unverified。

**功能门槛**
| key_stability | 允许的功能 |
| --- | --- |
| unverified / unstable / stable_24h | 缓存、会话内去重、商品池、links/link_logs 记录 |
| stable_7d | 在上一行基础上，另可开启订单派生（还须通过订单一致性验证）、订阅提醒、价格历史 |

**订单入口**：`product_key.order_derivable.<platform>` 默认 false。只有 key_stability=stable_7d，且 S0 验证订单商品 ID 与搜索派生结果 100% 一致后，负责人才改为 true。为 false 时，该平台订单一律 product_key=null、raw_item_id 照存；为 true 时调用 deriveProductKey，派生失败同样置 null，不丢单。

**派生失败的处理**
| 入口 | 处理 |
| --- | --- |
| 搜索 | 丢弃该条，计数并告警 |
| 解析（`POST /v1/inputs/parse`；规划/04 §6.3 原写 `/v1/clipboard/parse`，读作同一接口，C-14） | 联盟已识别出商品但派生失败 → 30131，文案“暂时无法识别这个商品，试试用商品名搜索”，搜索框预填 title_hint；不写 product_refs。口令本身无法识别时仍按 09 返回 30132。三平台识别不到具体商品时一律报错并给“用商品名搜索”按钮，不自动出候选卡（拍板第二批 TRADE-07）。例外：拼多多合法链接拿不到商品信息、且 pdd.direct_convert.enabled 打开时，出 amount_unknown 卡（BR-PRICE-08，拍板第二批 TRADE-08） |
| `POST /v1/links/convert` 传 url | 与解析相同：返回 30131，不转链，不以 product_key=null 生成 links。唯一例外是 09 CAP-PDD-01 的 zs.unit.url.gen 直链降级（开关 pdd.direct_convert.enabled，默认关；links.product_key=null，不参与去重、缓存和“同商品”证据；卡片按 BR-PRICE-08 显示 amount_unknown，点击经 open 带用户参数转链，拍板第二批 TRADE-08） |
| 详情 `GET /v1/products/{product_key}` | 响应的派生结果（解析别名后）不等于请求键，或无法派生 → 按 BR-PROD-05 结果分类②处理（ref_expired，30143） |
| 商品池 | 拒绝入库，并向运营显示原因（BR-PROD-08） |
| 订单 | product_key=null 入库，不丢单 |

**非商品转链**：美团等活动类转链不是商品，links.product_key 与 raw_item_id 都为 null，link_logs 用活动标识记录（字段名由 规划/04 定）。

**测试**：每平台 ≥30 条真实样本 fixture，断言同一商品在搜索、详情、解析、订单各 fixture 中派生结果相同；用属性测试断言函数确定性（同输入同输出）；边界样例包括淘宝原串以 `-` 结尾、含 `/`、长度为 125。

**接口路径**：本条与 BR-PROD-11 中的输入解析接口统一写作 `POST /v1/inputs/parse`（剪贴板、搜索框、分享扩展、Agent 共用）；规划/04、规划/01 中的 `POST /v1/clipboard/parse` 读作同一接口，改名由 规划/04 同步。按 C-14 默认处理，待代理（决策人为代理可自定）确认。

#### BR-PROD-04 细则 · 规格/SKU 与数量粒度

- 状态：已确认（负责人 2026-09-30，依据 docs/changes/20260930-拍板第一批.md §2）
- 默认值：淘宝、拼多多按商品级；京东 sku 模式按 sku 级；规格只作检索与展示；价格无法对应规格时标“规格以下单页为准”或“¥x 起”；MVP 不合并不同 SKU 比价。理由：联盟接口按商品报价与转链，SKU 级价格未经验证；把规格写进 key 会产生无法从接口复现的键；不标规格限定语有价格表述误导风险
- 决策人：负责人
- 依赖平台能力：淘宝、拼多多联盟接口是否返回 SKU ID 与 SKU 级券后价（拼多多 need_sku_info 为特殊渠道权限，09 CAP-PDD-01）；京东新 App 媒体是否有 skuId 权限；京东 itemId 与 skuId 是否一一对应
- 取代：
  - PRD修订_后端功能规划_2026-09-29.md 2.3：「京东 = jd: + itemId 的 B 段（有 skuId 权限时用 skuId），未说明粒度差异（本条明确：京东 sku 模式为 sku 级，淘宝、拼多多为商品级）」
- 来源：规划/01_需求规划.md J3、F-PROD-06；规划/04_数据模型与契约.md §1；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-01、3_JD_京东.md CAP-JD-01、4_PDD_拼多多.md CAP-PDD-01 降级文案；PRD修订_后端功能规划_2026-09-29.md 2.3；返利 App PRD（三端原生 + H5 + Agent）.md §10.3、§10.11 AF-05；docs/changes/20261001-拍板第二批.md（AI-04、AI-24、JEV-02）
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

**例子**
| 情形 | product_key | 能否视为同一商品 / 展示 |
| --- | --- | --- |
| 淘宝某牛奶商品，SKU 有 12 盒、24 盒 | 同一个 `tb:K1` | 是。价格按商品级，价格旁显示“规格以下单页为准”；确知为最低规格价时显示“¥45 起”；不写“24 盒 ¥49” |
| 同店铺把 12 盒、24 盒分别上架为两个商品 | `tb:K1`、`tb:K2` | 否 |
| 京东同款红色、蓝色，skuId 不同（sku 模式） | `jd:1001`、`jd:1002` | 否。Agent 列表中，如果接口同时返回 itemId/spuid，同组只出相关性最高的 1 张卡（折叠实现由代理自定，不改变去重键） |
| 用户说“伊利 250ml\*24 50 以内”，命中商品的商品级最低券后价为 ¥45（可能是 12 盒规格） | `tb:K1` | spec 只进 `search_products.spec`，无结果时按 BR-AI-08 无结果放宽（先去规格；放宽顺序、次数、放宽说明 notice 与两次放宽后仍无结果的 notice/suggestions 均以 BR-AI-08 为准，本条不另定义；G-19）。卡片显示“券后 ¥45”并带“规格以下单页为准”，核对标记为“规格待确认”；Agent 文字只说“你要的 24 盒规格价格以下单页为准”，不出现金额（BR-AI-06），不得说“24 盒 45 元”或“满足 50 元以内” |

**文案**：文案 key 由 BR-PRICE 统一维护，但不得删除本条要求的规格限定语。与 规划/09 CAP-TB-01、CAP-PDD-01 的降级文案保持一致。

**提醒（P1）的影响**：降价提醒的监控对象为 app_id + platform + product_key，`spec_text` 只作展示。在确认淘宝、拼多多联盟能返回 SKU 级价格之前，提醒文案必须写“按商品页最低价/联盟报价”，不得承诺指定规格的价格（见 BR-PRICE、BR-WATCH）。

**异常**：联盟返回商品级价格区间（min–max）时如何取值由 BR-PRICE 规定，本条只规定按上文显示“¥x 起”。

#### BR-PROD-05 细则 · raw_item_id 保存、取用与重新解析

- 状态：待验证（2026-09-30 由默认假设改：1800 秒有效期与“查询专用推广位取得的原串可用于用户转链”两项都依赖未实测的淘宝能力，按 08 §0.3 不属于默认假设）
- 默认值：raw_item_id 有效期 1800 秒；取原串顺序为 item_ref → product_refs → 重解析；订单不写 product_refs；重解析失败分三类处理，只有联盟明确下架才标 off_shelf
- 决策人：代理可自定
- 依赖平台能力：淘宝加密商品 ID 的实际有效期：实测 >30 分钟可放宽，&lt;30 分钟需缩短。淘宝：用查询专用推广位（不带 relation_id）取得的 raw_item_id，交给带用户 relation_id 的转链时，订单是否正确归属该用户（在 规划/09 CAP-TB-06 实验中增加此项）；不成立时，转链前须用该用户的 relation_id 重新取原串
- 取代：
  - PRD v2.1 §8.2 F-31；修订① 3.2：「平台原始商品 ID 原样保存进 link_log，不作为稳定主键（保留，并扩展到 links、orders、product_refs）」
- 来源：PRD修订_后端功能规划_2026-09-29.md 2.3、第 4 章 product_refs；规划/04_数据模型与契约.md §3.2、§6 product_card、§7 错误码；规划/01_需求规划.md F-LINK-08；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-06、CAP-TB-13；返利 App PRD（三端原生 + H5 + Agent）.md §8.2、§10.2；PRD修订_双品牌与Agent找货_2026-09-29.md 3.2
- 需同步修改的规划文档：7 处（计数仅作记录，落点见 README §0.6）

**product_refs**（catalog 模块独占；主键 (app_id, product_key)）字段：platform、raw_item_id、canonical_url、title、shop_id、shop_type、source（search / detail / parse / pool）、refreshed_at（+08:00）。canonical_url 可为空，只由 parse 来源写入：服务端从用户输入中抽出商品链接，只保留平台域名和商品 ID 参数，不存用户粘贴的原文、口令全文或分享文案。
写入语句：
```sql
INSERT … ON CONFLICT (app_id, product_key) DO UPDATE SET …
  WHERE product_refs.refreshed_at < EXCLUDED.refreshed_at
```

**重新解析步骤**
1. 有 canonical_url 时，按链接解析。
2. 否则用 `q=title`、按 `shop_id` 过滤，在同平台搜索第 1 页（≤20 条）中找 deriveProductKey 结果等于目标键的条目。
3. 单次超时 3 秒。同一 (app_id, product_key) 只发一次重解析（Redis 锁 10 秒），并发请求等待同一个结果。
4. 成功后写入 product_refs，用新原串转链，links 记录新原串。

**结果分类**
| 类别 | 条件 | convert / open 返回 | 卡片 availability | 文案 | 副作用 |
| --- | --- | --- | --- | --- | --- |
| ① 下架 | 联盟明确返回下架 | 30141 | off_shelf | 商品已下架 | 删除 `product:{app_id}:{product_key}` 缓存；商品池中该 (app_id, product_key) 的全部 pool_items 置 status=offline，并向运营显示原因“联盟返回下架”（规划/01 F-ADM-10 自动失效下架；再次上架走 BR-PROD-08 ③ 复核） |
| ② 引用失效 | 检索不到同键商品，或派生出不同的键 | 30143（新增） | ref_expired（新增） | 商品信息已失效，请重新搜索 | 不删缓存，不触发商品池下架 |
| ③ 暂时失败 | 超时、限流或熔断 | open：按 BR-PRICE-13，有该用户 ≤900 秒转链缓存则用缓存外跳并返回 requote_failed=true，无缓存则返回 50303；convert、详情：50401。均可重试；不使用 50301（只表示 convert.enabled.&lt;platform> 关闭，BR-PROD-10），也不使用 50304（只表示搜索无缓存，BR-PROD-07） | 不变 | open 按 BR-PRICE-13（requote_failed：「暂时无法确认最新价格，以下单页为准」；50303：主按钮「稍后再试」，次按钮「仍去购买（无返利）」）；convert、详情：网络繁忙，请稍后再试 | 无 |

**例子**
- 10:00 搜索得到 raw=`X-K1`（tb:K1），10:20 点击转链；卡片 item_ref 取得时刻为 10:00，间隔 1200 秒 ≤1800，用 `X-K1`。
- 10:00 取得，10:31 转链：item_ref 已过 1860 秒 >1800；product_refs 中有 10:15 其他请求写入的 `Z-K1`，间隔 960 秒，用 `Z-K1`（第②步）。
- 两处都过期 → 重解析得到 `Y-K1`，派生仍为 tb:K1 → 用 `Y-K1`。
- 重解析派生出 tb:K9 → 按②引用失效处理，返回 30143。

**边界**：1800 秒整算未过期（≤），毫秒精度，以服务端时钟为准。原串不设长度上限，日志中截断到 256 字符展示。

**错误码分工**：30143 只表示“商品信息已失效”（ref_expired，客户端动作为重新搜索），BR-PROD-03、BR-PROD-06 同码同文案“商品信息已失效，请重新搜索”；links/open 中 link_id 不存在、不属于当前用户或设备不一致（客户端动作为重新转链）改用 30144，由 BR-AI-11 维护。码值以 规划/04 §7 为准。按 C-03 默认处理，待负责人确认（码号分配代理可自定）。

#### BR-PROD-06 细则 · ID 不稳定时的兜底键

- 状态：待决策
- 默认值：不启用；仅在 S0 验证判定 unstable、负责人写 ADR 批准后，按本条格式启用。理由：指纹键有误合并和改标题断链两种风险，只能作为兜底，且不得支撑提醒、价格历史和“同商品”归因
- 决策人：负责人
- 依赖平台能力：淘宝 CAP-TB-01、京东 CAP-JD-01、拼多多 CAP-PDD-01 的稳定性结果；联盟返回的 shop_id 是否稳定
- 取代：
  - 返利 App PRD（三端原生 + H5 + Agent）.md §10.20 第 4 条：「不稳定时用联盟返回的可稳定标识或“标题+店铺”指纹作兜底键（补全格式、归一化、使用范围与限制）」
  - 规划/09 CAP-PDD-01 不支持时怎么办：「goods_id 不稳定时 product_key 退化为“标题 + 店铺 ID”指纹，只用于短期缓存与去重（改为须负责人 ADR 批准后按本条启用）」
- 来源：返利 App PRD（三端原生 + H5 + Agent）.md §10.20 第 4 条；开发任务拆解_v1_2026-09-29.md 12.1 H-23；规划/09_平台能力验证/4_PDD_拼多多.md CAP-PDD-01
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

**例子**
- 淘宝店铺 `shop_id=58123`，标题 `【官方旗舰】伊利 纯牛奶 250ml*24盒`。第②步删除【】后得 ` 伊利 纯牛奶 250ml*24盒`，第④步删除空白和 `*` 后，norm=`伊利纯牛奶250ml24盒`，key=`tb:fp_3f9a…`（32 个字符）。
- 必备测试：`伊利纯牛奶250ml×24盒` 与 `伊利纯牛奶 250ml*24盒` 得到相同的键；同店 `伊利纯牛奶250ml*12盒` 得到不同的键；shop_id 为空时返回 null。

**已知风险**
| 风险 | 影响 | 处理 |
| --- | --- | --- |
| 同店同标题的不同商品（例如只换了主图的重复铺货）被合并 | 价格、券显示错位；转链可能用错商品 | 转链只用卡片自带原串；重解析出现多个候选时不转链；提醒与价格历史不上线 |
| 商家改标题后产生新键 | 旧键不再更新 | 兜底期内接受这项损失，不做模糊匹配 |

**错误码**：多候选不转链时返回的 30143 与 BR-PROD-05 同义，文案统一为“商品信息已失效，请重新搜索”（原写“商品信息已变化”）；不使用 30144（link_id 无效，BR-AI-11）。按 C-03 默认处理，待负责人确认。

#### BR-PROD-07 细则 · 商品缓存口径

- 状态：待验证
- 默认值：按 fetched_at 判断命中，窗口 300 秒；物理 TTL 3600 秒；熔断期 stale 窗口默认 300 秒；转链缓存 ≤900 秒，按用户隔离，每次都新建 links 行；键组成和剔除链接字段为本条补充。TTL 与键组成已确认，跨用户共享待 09 验证
- 决策人：代理可自定（上调 stale_max_age_s、跨用户共享验证失败后的取舍由负责人决定）
- 依赖平台能力：淘宝 CAP-TB-03、CAP-TB-13 以及京东、拼多多对应项：同一查询的搜索和详情结果（价格、券、佣金）是否随 relation_id 或推广位变化
- 取代：
  - 返利 App PRD（三端原生 + H5 + Agent）.md §6：「搜索、详情服务端缓存 5 分钟；只缓存搜索结果（不含归因）（保留，并补全键组成、命中判断与剔除链接字段）」
  - 规划/02_系统架构.md 故障降级表 搜索行：「返回 5 分钟内缓存并标 stale（改为按 stale_max_age_s 判断，默认 300 秒，并写明无缓存时返回 50301）」
  - 本条原写（2026-09-30）：「没有符合条件的条目时返回 50301」→ 搜索返回新码 50304，不读商品池冒充；50301 只表示转链开关关闭（拍板第二批 TRADE-12）
- 来源：规划/01_需求规划.md F-PROD-07；规划/02_系统架构.md §9 转链时机、故障降级表；规划/04_数据模型与契约.md §2.2 pid_scene、§3.2 links、§5 接口表；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-03、CAP-TB-13；PRD修订_后端功能规划_2026-09-29.md 2.3 F-88；返利 App PRD（三端原生 + H5 + Agent）.md §6、§10.15；docs/changes/20261001-拍板第二批.md（TRADE-12）
- 需同步修改的规划文档：6 处（计数仅作记录，落点见 README §0.6）

**缓存键**
| 类别 | 键 | 命中窗口 | 物理 TTL |
| --- | --- | --- | --- |
| 搜索 | `search:{app_id}:{platform}:{sha1(canonical_json(union_request_params))}:{filter_cfg_version}` | ≤300 s | 3600 s |
| 详情 | `product:{app_id}:{product_key}` | ≤300 s | 3600 s |
| raw 映射 | product_refs（数据库表，不是缓存） | ≤1800 s（BR-PROD-05） | — |
| 转链 | `convert:{app_id}:{user_id}:{platform}:{product_key}:{pid_scene}` | ≤900 s | 900 s |

`union_request_params` 指实际发给联盟的全部业务参数，包括 norm(q)、sort、has_coupon、start_price_fen / end_price_fen、spec、cat、is_tmall、material_id、page_no、page_size 等，按 key 排序后序列化；不含 adzone_id/pid、relation_id、user_id、device_id、search_session_id。`norm(q)` = NFKC、去掉首尾空白、连续空白合并为一个、转小写。`filter_cfg_version` 是搜索过滤配置（最低佣金、禁售类目等）的版本号，配置一变更缓存即自然失效。

**游标**：我方游标只携带 search_session_id 与 page_no（BR-PROD-08）；服务端先换算成联盟的 page_no，再组键查缓存。

**例子**：10:00:00.000 用户 A 搜“纯牛奶”（淘宝、综合排序、无价格区间），结果写入缓存；10:04:59 用户 B 用相同参数搜索，命中；10:05:00.000 仍命中（正好 300 秒）；10:05:00.001 未命中，重查联盟。用户 B 加上“50 元以内”后，end_price_fen=5000 进入键，不会命中 A 的条目。A 等级 V1、B 等级 V3，两人的预估返利各自实时计算。

**熔断降级**
| 情形 | 返回 | App 表现 |
| --- | --- | --- |
| 熔断打开，有 age ≤ stale_max_age_s 的条目 | 结果 + stale=true + quoted_at=fetched_at | 结果顶部显示“价格可能已变化，下单前以平台为准” |
| 熔断打开，没有符合条件的条目 | 搜索：50304（新增）；详情：商品池价格 + stale=true（BR-PRICE-11） | 搜索显示“&lt;平台>搜索暂不可用”（措辞以 BR-TEXT-14 为准），不展示商品池商品冒充搜索结果；Agent 改查其他平台；首页信息流改读商品池（拍板第二批 TRADE-12） |
`stale_max_age_s` 默认 300，负责人可以上调，上限 3600（不得超过物理 TTL）。

**转链缓存**：命中时只复用推广链接或口令本体。新建的 links 行记录本次的 scene、spm、agent_session_id，以及 cache_hit=true；links.expire_at 取缓存条目的原始过期时间，不重新计时。归因细节见 BR-ATTR。

**主动失效**：商品池刷新或转链复核发现商品下架（BR-PROD-05 ①）、券失效或佣金为 0 时，删除 `product:{app_id}:{product_key}`；ref_expired 不删除。

#### BR-PROD-08 细则 · 去重与唯一键口径

- 状态：已确认
- 默认值：按 (app_id, platform, product_key) 去重，null 不参与；同键多条取券后价最低、同价取预估返高的（拍板第二批 TRADE-14）；会话 30 分钟过期、集合上限 500；读缓存之后再去重
- 决策人：代理可自定
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划_2026-09-29.md 2.3：「多平台并发检索合并后去重（原文未写去重口径）」
  - 修订① 3.7；PRD v2.1 §10.7：「同一平台同一 item_id 只出一张卡」
  - PRD v2.1 §10.20：「(platform, item_key)、(query_id, item_key) 唯一」
- 来源：规划/01_需求规划.md J3 第 2 步、F-PROD-06；规划/04_数据模型与契约.md §5 GET /v1/products/search（登录要求 none）；PRD修订_后端功能规划_2026-09-29.md 2.3、第 4 章 pools；PRD修订_双品牌与Agent找货_2026-09-29.md 3.7；返利 App PRD（三端原生 + H5 + Agent）.md §10.2、§10.20；docs/changes/20261001-拍板第二批.md（TRADE-14）
- 需同步修改的规划文档：4 处（计数仅作记录，落点见 README §0.6）

**例子**
- Agent 搜“伊利纯牛奶”，并发查 jd、pdd：jd 返回 [jd:1, jd:2, jd:1]（第 3 条重复），pdd 返回 [pdd:a]。合并后出 3 张卡：jd:1、jd:2、pdd:a。
- 拼多多同一商品 pdd:a 返回两个计划：计划 S1 券后 ¥19.9、预估返 ¥0.8；计划 S2 券后 ¥18.9、预估返 ¥0.5 → 保留 S2（券后价低），卡片与转链都用 S2 的 goods_sign。两计划券后价相同时保留预估返高的。
- 淘宝搜索第 1 页含 tb:K1…K20，第 2 页联盟又返回了 tb:K20：第 2 页剔除 tb:K20。本页条数不足时不补拉（是否补拉由代理自定）。缓存中的第 2 页仍保留 tb:K20。
- 用户粘贴 3 个链接，其中两个都解析为 tb:K1：出 2 张卡。
- 运营把 tb:K1 两次加入池 P：第二次覆盖 sort 和有效期，并触发复核；池内仍只有 1 条。

**会话异常**：游标中的 search_session_id 已过期，或不属于当前请求者时，新建会话，按请求的 page_no 返回，不报错；已下发集合从空开始。

**京东折叠**：同一 itemId/spuid 下多个 sku 的折叠只影响 Agent 展示，不改变去重键（BR-PROD-04）。

**异常**：派生失败（null）的搜索结果直接丢弃并计数（BR-PROD-03）；商品池入库时派生失败则拒绝入库，并提示运营。

#### BR-PROD-09 细则 · 跨平台同款判定（P1）

- 状态：已确认（负责人 2026-09-30，依据 docs/changes/20260930-拍板第一批.md §2）
- 默认值：规则优先，模型结果只能降级为“相似商品”；规格或件数不同不称同款。理由：错误的“同款更便宜”结论直接损害信任，并可能构成误导宣传
- 决策人：负责人
- 依赖平台能力：三家联盟接口是否返回品牌、条码或型号等结构化字段
- 取代：无
- 来源：规划/00_总览与决策.md D2、§P1 范围；规划/01_需求规划.md F-AGENT-18；规划/02_系统架构.md 模型路由；返利 App PRD（三端原生 + H5 + Agent）.md §10.0、§10.17、§10.20 第 8 条
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

**规格归一例子**
| A | B | 结论 |
| --- | --- | --- |
| 伊利纯牛奶 250ml\*24（jd） | 伊利 纯牛奶 24盒×250ml（pdd） | 同款 |
| 伊利纯牛奶 250ml\*24 | 伊利纯牛奶 250ml\*12 | 规格不同；折合单价按每 100ml 计 |
| 伊利纯牛奶 250ml\*24 | 蒙牛纯牛奶 250ml\*24 | 不同款 |

**P1 目标、依赖、未知项**（按 规划/00 §8「只细化近期要开发的内容」只写到这一层）
- 目标：Agent 回答“哪家便宜”时给出同款比价。
- 依赖：品牌词典与规格归一词典（与 `specs/material-slang.csv` 同源维护）、BR-PRICE 口径、模型 Plus 档打分；参与比价的两端平台 key_stability 均须为 stable_7d（BR-PROD-03）。
- 未知项：联盟是否提供条码或型号字段；截图找同款的识别准确率。

#### BR-PROD-10 细则 · 平台编码、天猫归属与平台开关

- 状态：已确认（平台编码、天猫归入 taobao、转链开关部分）；shop_type 取数为待验证子项（2026-09-30 补：订单侧能否识别天猫未实测，登记 15 §15.2）
- 默认值：字符串编码；天猫归入 taobao；生成 product_key 与转链开关解耦；商品侧 shop_type 由联盟 user_type 映射（0→taobao，1→tmall）；orders.shop_type 在 CAP-TB-07 验证前可空，按 orders.product_key 取 product_refs.shop_type 回填，product_key 为 null 时保持 null
- 决策人：负责人
- 依赖平台能力：订单侧天猫标识字段待 规划/09 CAP-TB-07（U-43）；未验证前 orders.shop_type 可空，由商品侧 user_type 回填。商品侧 user_type（0 淘宝、1 天猫）来源为 09 U-43「商品侧 user_type」（可信度中，抓取摘要；09 中见于 CAP-TB-03 物料搜索出参），同样待 S0 录制确认；按平台的搜索开关何时打开取决于该平台 CAP-TB-03、CAP-JD-03、CAP-PDD-03 的结论（细则「按平台的搜索开关」，2026-10-03 功能对照 G-47）
- 取代：
  - PRD修订_后端功能规划_2026-09-29.md 1.5、2.5：「tmall 仅作 sub_platform（改为 shop_type=tmall）」
  - 返利 App PRD（三端原生 + H5 + Agent）.md §6：「平台编码含 taobao_flash（淘宝闪购，原饿了么）（改为 eleme）」
  - 修订①；参考_花卷云功能查漏底稿：「platforms:[1,3,4] 数字编码」
- 来源：规划/00_总览与决策.md §6；规划/04_数据模型与契约.md §2.1、配置项 convert.enabled.&lt;platform>（返回 50301）；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-06、CAP-TB-07；规划/00 D19、D24；PRD修订_后端功能规划_2026-09-29.md 1.5；参考_花卷云功能查漏底稿_2026-09-29.md 头部改判
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

**名词映射**（其他文档 → 规划）
| 其他文档写法 | 规划写法 |
| --- | --- |
| 后端功能规划 `sub_platform=tmall` | `shop_type=tmall` |
| PRD v2.1 `taobao_flash`（淘宝闪购） | `eleme` |
| 修订① / 花卷云 `platforms:[1,3,4]` | 字符串数组 `["taobao","jd","pdd"]` |

**例子**
| 输入 | 平台状态 | 结果 |
| --- | --- | --- |
| `https://detail.tmall.com/item.htm?id=…` | 淘宝解析已开启 | platform=taobao、shop_type=tmall、product_key=`tb:…` |
| `v.douyin.com/…` | douyin 解析、搜索均未开启 | 30131“暂不支持该平台”，不写 product_refs |
| 淘宝商品链接 | 解析已开启，convert.enabled.taobao=false | 正常出卡、生成 product_key；点击购买返回 50301，按钮显示“稍后再试”；订单同步和商品池不受影响 |

**按平台的搜索开关**（2026-10-03，功能对照 G-47；属实现补充，落实规划/00 §4 搜索行的能力条件，不改变本条已确认的判定）：原来隐藏某个平台的搜索 Tab 要发版，CAP-*-03 不达标的平台「不进搜索 Tab」（规划/00 §4）也没有运行时的落点。

- 开关：服务端紧急开关 `search.enabled.<platform>`（规划/04 §10.2，修改需 step-up、写审计，10 秒内生效）。默认 off：该平台 CAP-*-03 判为支持，或部分支持且降级已实现并验收后（规划/09 README §1.1），由有开关权限的账号打开；某平台搜索出问题时也用它临时关闭。
- 作用范围只有关键词搜索：off 时该平台不出现在搜索页的平台 Tab；`GET /v1/products/search` 对该平台返回 50304，`data.platform` 为该平台、`data.reason=search_disabled`（不新开码：含义同属「该平台搜索不可用」，按 08 §13.11 的分配规则用 data.reason 区分原因，客户端动作按 reason 分支，做法与 50301 区分 maintenance、not_launched 相同）；Agent 的 `search_products` 不对该平台发起检索，多平台检索时跳过它。输入链接或口令直达详情、商品详情、转链、订单都不受影响（输入链接直达本来就不受 CAP-*-03 约束，规划/00 §4）。它与 platforms 表的搜索能力标记是两回事：能力标记表示平台有没有搜索这种形态，没有的按正文返回 30131；本开关只对有这种能力的平台在运行时开关。
- 下发：服务端由开关派生 `/v1/config.features.search_status.<platform>` ∈ {on, off}；搜索页只显示 on 的平台 Tab，默认 Tab（规划/01 F-PROD-01）对应的平台为 off 时取第一个为 on 的平台；三家都为 off 时搜索页只保留「粘贴链接查返利」的入口与说明（文案同 error.50304.search_disabled）。客户端取用顺序同其他配置（当前、上一次成功的版本、包内默认），包内默认为 off。客户端按旧配置仍对已关闭的平台发了搜索请求，收到 50304 search_disabled 时刷新配置、隐藏该 Tab，不显示重试按钮。
- 与转链开关 `convert.enabled.<platform>` 相互独立，四种组合都有定义：都开——照常；可搜不可买（搜索 on、转链 off）——搜索结果照常出卡，购买按钮按 50301 与 `platform_status`（维护中或即将开放，BR-TEXT-14）；可买不可搜（搜索 off、转链 on）——没有该平台的搜索 Tab，粘贴链接照常查返利与购买；都关——两者同时生效。
- Agent：用户只要该平台的商品时，用固定话术 `agent.notice.search_disabled`（BR-TEXT-22）答复，并提示可以发链接查返利；多平台的请求里不提这个平台。
- 例：拼多多 CAP-PDD-03 未通过，`search.enabled.pdd=off`、`convert.enabled.pdd=on` → 搜索页只有淘宝、京东两个 Tab；用户粘贴拼多多链接 → 照常出卡、点购买照常转链；Agent 收到「拼多多上找纸巾」→ 答复拼多多暂不提供搜索、可以发链接查返利，不检索拼多多。

#### BR-PROD-11 细则 · 商品引用令牌 item_ref

- 状态：默认假设
- 默认值：所有商品条目携带加密签名的 item_ref；convert 优先使用其中的原串；缺失时不报错
- 决策人：代理可自定
- 依赖平台能力：无
- 取代：无
- 来源：规划/04_数据模型与契约.md §3.2 links、§5 接口表、§6 product_card；规划/09_平台能力验证/2_TB_淘宝.md CAP-TB-01、CAP-TB-13；本主题评审问题：BR-PROD-05、BR-PROD-06（兜底键误合并、跨用户复用原串）
- 需同步修改的规划文档：4 处（计数仅作记录，落点见 README §0.6）

**为什么需要**
1. BR-PROD-06 兜底键会把同店同标题的不同商品合并到同一个键；用卡片自带的原串，才能保证转链的是用户看到的那个商品。
2. product_refs 会被其他请求覆盖；用卡片自带的原串，转链的是用户看到的那一版商品数据。
3. 减少重解析次数和联盟调用量。

**格式**：由代理自定，例如 AES-GCM 加密 + key_id，长度 ≤512 字符。密钥轮换时，上一把密钥保留 24 小时，只用于解密。令牌本身不设过期时间，原串是否新鲜只看 fetched_at（≤1800 秒，BR-PROD-05）。

**例子**
| 情形 | 结果 |
| --- | --- |
| 卡片 item_ref 的 fetched_at=10:00，10:20 转链 | 使用令牌中的原串 |
| 同一令牌在 10:40 转链 | 超过 1800 秒，走 product_refs 或重解析 |
| 客户端没有带 item_ref（旧版本） | 走 product_refs 或重解析，不报错 |
| 令牌中是 tb:K1，请求的 product_key 是 tb:K2 | 20001 |
| app1 签发的令牌用于 app2 的请求 | 忽略令牌 |

**接口路径**：解析结果携带 item_ref 的接口为 `POST /v1/inputs/parse`（原写 `/v1/clipboard/parse`，同一接口）。按 C-14 默认处理，待代理（决策人为代理可自定）确认。

### 2.3 本主题未决问题

1. 京东粒度：product_key.jd.mode 默认为 item，S0 后由负责人锁定。如果 itemId 与 skuId 一一对应，后续切换为 sku 可以走别名迁移；否则须写 ADR 并定订阅与价格历史的迁移方案（负责人，依赖 CAP-JD-01 的 sceneId=2 权限结果）
2. 淘宝、拼多多能否拿到 SKU 级价格：拿不到时，降价提醒（P1）能否只按商品级价格上线，需与 BR-PRICE / BR-WATCH 负责人一并拍板
3. 拼多多：搜索、详情、解析响应是否返回 goods_id（决定 pdd 能否生成稳定 product_key）；【已定】同一商品有多个 goods_sign 时取券后价最低的计划，同价取预估返高的，展示与转链用同一条（拍板第二批 TRADE-14，BR-PROD-08）
4. 订单派生门槛设为 stable_7d，而归因窗口为付款前 15 天。7 天稳定是否足以支撑“同商品”证据，由 BR-ATTR 决定
5. 联盟加密商品 ID 的实际有效期是否确为 30 分钟量级（BR-PROD-05 的 1800 秒是默认值，待 S0 实测）
6. 查询专用推广位取得的 raw_item_id 用于用户 relation_id 转链后，订单能否正确归属（CAP-TB-06 新增实验）；搜索、详情结果是否随 relation_id 或推广位变化（CAP-TB-03 / CAP-TB-13），决定 BR-PROD-07 能否跨用户共享缓存
7. 若 S0 证明某平台 stable_id 与联盟账号无关，是否通过 ADR 取消 BR-PROD-01 的 app_id 比较限制（负责人）
8. 熔断期间是否要把 search.cache.stale_max_age_s 从 300 秒上调（上限 3600 秒）：需要在可用性与价格准确性之间取舍（负责人）

---
