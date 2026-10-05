# 09 平台能力验证 · 4 附. 拼多多开放平台接入（SDK、授权、签名、官方文档核对）

返回 [README](README.md) · 能力主表见 [4_PDD_拼多多.md](4_PDD_拼多多.md)

2026-10-02 · 来源：负责人登录拼多多开放平台，Claude 主会话在浏览器里只读核对（规划/11 §7.3 第 6 项；V-06 的拼多多部分）。本文登记开放平台接入方式的事实，以及官方接口文档与主表（来自 SDK 注释转述）的差异。**主表中来源为 `OPENPDD(...)` 的事实与本文不一致时，以本文为准**；逐条回写主表前先引用本文。

## 1. 结论

| 问题 | 结论 |
| --- | --- |
| 有哪些官方 SDK | 两种，都在控制台「应用详情 → 开发者工具」：**服务端 SDK**（只有 Java）和**客户端 SDK**（Android、iOS；隐私规则另提到 Web 版）。2026-10-02 控制台未见鸿蒙选项（当前是否支持未核实，2026-10-05 改述），没有 Node / TypeScript 版 |
| 服务端怎么接 | 后端是 NestJS（ADR-0001），不用 Java SDK；按「API 调用详解」自行实现 HTTP 调用与 MD5 签名，放在拼多多 `UnionAdapter`（02 §6）。Java SDK 只作对照 |
| 客户端怎么接 | 客户端 SDK 按"操作系统 + 包名 / Bundle ID + 回调协议"在控制台生成，生成物与我方包签名绑定（§4）。iOS、Android 是否集成、集成后做什么，要拿到 SDK 包内说明才能定；鸿蒙端没有 SDK，继续按转链返回的 schema_url / mobile_url 设计 |
| 我方多多进宝接口要不要用户令牌 | 不要。已核对的 13 个 `pdd.ddk.*` 接口全部标"不需用户授权"、免费，只需 client_id + 签名。OAuth 令牌流程（§3.5）对我方主链路不是必需 |
| 沙箱 | 官方写明"目前只提供正式环境，暂无沙箱环境"。维持用录制回放开发 |
| 对主表的影响 | CAP-PDD-11"未找到唤起 SDK"不成立，已改；CAP-PDD-06"转链无 SKU 参数"不成立，已改；其余差异见 §6，待逐条回写 |

## 2. 核对过的页面

| 短名 | 页面 | 官方更新时间 |
| --- | --- | --- |
| PDD-DOC(SDK) | 基础文档 / 开发文档 / SDK使用指南 | 2022-03-25 |
| PDD-DOC(AUTH) | 基础文档 / 开发文档 / 授权说明 | 2025-12-12 |
| PDD-DOC(API) | 基础文档 / 开发文档 / API调用详解 | 2020-12-24 |
| PDD-DOC(MSG) | 基础文档 / 开发文档 / 消息推送使用文档 | 2026-01-15 |
| PDD-DOC(APP) | 基础文档 / 开发入门 / 应用说明 | 2020-06-02 |
| PDD-DOC(NEW) | 基础文档 / 开发入门 / 新手指南 | 2025-12-12 |
| PDD-DOC(DDK-GUIDE) | 基础文档 / API调用场景 / 多多客使用指南 | 2020-06-30 |
| PDD-DOC(DDK-JOIN) | 开放业务 / 电商业务 / 多多客（入驻指南） | 2022-07-21 |
| PDD-DOC(SDK-PRIV) | 运营规范 / 平台规范 / SDK个人信息保护规则（V1.1） | 2026-03-31 |
| PDD-API(<接口名>) | API文档 / 多多客API：goods.search、goods.detail、goods.promotion.url.generate、goods.zs.unit.url.gen、goods.recommend.get、goods.pid.generate、pid.mediaid.bind、member.authority.query、rp.prom.url.generate、order.list.increment.get、order.list.range.get、order.detail.get、url.short.parse | 2020-11 至 2026-08，各接口不同 |
| PDD-CONSOLE | 控制台 / 应用详情 / 开发者工具（服务端SDK、客户端SDK 两页，只读查看） | — |

文档地址形如 `open.pinduoduo.com/application/document/browse?idStr=<id>`，接口文档形如 `open.pinduoduo.com/application/document/api?id=<接口名>`，均须登录。

可信度：均为官方原文。2026-10-02 原文（文字）已存入私有库 `rebate-private/docs-mirror/pdd/`（32 个接口 + 11 篇指南，见该目录 INDEX.md），可按"高"引用；页面中的图片未存。其中 DDK-GUIDE、APP 是 2020 年的旧页，结算日、特权接口等说法可能已变，与新页冲突时以新页为准。

**已补存**：多多客 API 目录其余接口原文已存档（私有库同目录），其中的事实尚未逐条核对进本文。**仍未读**：「开放平台违规处理规则」「开发者入驻协议」；多多进宝站内文档（`jinbao.pinduoduo.com`：goodsSign 使用说明、App 跳转要求、小程序跳转申请）；客户端 SDK 包内说明；控制台「消息订阅」页的主题清单（消息推送文档本身不列主题，多多进宝订单是否有消息仍未知）。

## 3. 服务端接入事实

### 3.1 服务地址〔PDD-DOC(SDK)、PDD-DOC(API)〕

| 用途 | 地址 |
| --- | --- |
| API 网关 | `https://gw-api.pinduoduo.com/api/router`（http 已不允许调用） |
| 文件上传网关 | `https://gw-upload.pinduoduo.com/api/upload` |
| 消息服务（WebSocket） | `wss://message-api.pinduoduo.com` |
| 方舟网关 | `https://ark-api.pinduoduo.com/ark/router`（我方用不到） |

Java SDK 内置备用域名并支持自动 / 手动切换，备用域名的值文档未写（在 SDK 源码里）。

### 3.2 公共参数〔PDD-DOC(API)、PDD-API〕

| 参数 | 必须 | 说明 |
| --- | --- | --- |
| `type` | 是 | 接口名，形如 `pdd.*` |
| `client_id` | 是 | 应用详情里的 client_id |
| `timestamp` | 是 | UNIX 时间，秒；**与拼多多服务器时间相差须在 10 分钟内** |
| `sign` | 是 | 签名，算法见 §3.3 |
| `data_type` | 否 | `JSON`（默认）或 `XML`，大写 |
| `access_token` | 否 | 需用户授权的接口才传 |
| `version` | 否 | 默认 V1，无要求不传 |

业务参数与公共参数平铺在同一层一起提交。

### 3.3 签名算法（MD5）〔PDD-DOC(API)〕

1. 取本次请求的全部参数（公共 + 业务，不含 `sign`），按参数名 ASCII 升序排序。
2. 按"参数名参数值"依次拼接，中间不加任何分隔符。
3. 在拼好的字符串头尾各加一次 client_secret。
4. 取 MD5，转大写，即 `sign`。

官方示例可直接当单元测试用例（client_secret 为示例值 `testSecret`，不是真实密钥）：

```text
参数：access_token=asd78172s8ds9a921j9qqwda12312w1w21211  client_id=1  data_type=XML
      order_status=1  page=1  page_size=10  timestamp=1480411125  type=pdd.order.number.list.get
sign：E4DE3ED21002510DED352819E7AE6775
```

2026-10-02 已在本机按上述四步复算，结果与官方值一致。数组、对象类业务参数（如 `goods_sign_list`、`range_list`）参与签名时怎么序列化，文档没写，以 Java SDK 源码或实测为准。

### 3.4 请求、响应与错误〔PDD-DOC(API)、PDD-API〕

- 方法 `POST`，JSON 请求带 `content-type: application/json`。编码一律 UTF-8；用 URL 参数或表单时参数值要 urlencode。
- **响应外层键名不能由接口名推导**，须按接口文档逐个登记。例：`pdd.ddk.order.list.increment.get` 与 `order.list.range.get` 都是 `order_list_get_response`；`order.detail.get` 是 `order_detail_response`；`member.authority.query` 是 `authority_query_response`；`goods.zs.unit.url.gen` 是 `goods_zs_unit_generate_response`；`rp.prom.url.generate` 是 `rp_promotion_url_generate_response`；`pid.generate` 是 `p_id_generate_response`；`pid.mediaid.bind` 是 `p_id_bind_response`。
- 错误响应外层键为 `error_response`，字段 `error_code`、`error_msg`、`sub_code`、`sub_msg`、`request_id`。

需要专门处理的错误码（各接口文档的公共错误码表）：

| 错误码 | 含义 | 我方处理 |
| --- | --- | --- |
| 20004 | 签名校验失败 | 实现缺陷，告警 |
| 20005 | IP 无权访问，须加入 IP 白名单 | 出口 IP 未登记，见 §5 第 3 项 |
| 20031 | 应用不含此接口的权限包 | 权限未批，按 CAP-PDD-12 降级 |
| 10019 | access_token 已过期 | 只影响需授权接口 |
| 52101、70031 | 接口被限流 / 调用过于频繁 | 退避重试，计入配额治理（02 §6.2） |
| 52102、52103、70033 | 接口降级 / 维护下线 | 熔断，稍后重试 |
| 70032、70034、70035 | 请求被禁止 / 用户或应用存在风险 | 停止调用并通知负责人；70035 文档给出的联系邮箱是多多进宝官方邮箱 |
| 70036 | 应用处于测试状态，调用次数达上限 | 应用未上线前会遇到，见 §5 第 2 项 |
| 50000、50001、50002、52001、52002 | 平台内部错误 | 重试，持续失败告警 |

映射到我方错误码的规则不在本文定（04 管形状）。

### 3.5 限流〔PDD-API、PDD-DOC(DDK-JOIN)〕

| 接口 | 官方"接口总限流频次" |
| --- | --- |
| goods.search、goods.detail、goods.promotion.url.generate | 111500 次 / 10 秒 |
| goods.recommend.get、rp.prom.url.generate | 55750 次 / 50 秒 |
| order.list.increment.get、order.detail.get | 44500 次 / 10 秒 |
| order.list.range.get、goods.zs.unit.url.gen、goods.pid.generate、url.short.parse | 2500 次 / 1 秒 |
| pid.mediaid.bind | 500 次 / 1 秒 |
| member.authority.query | 页面列了两行：600 次 / 1 秒、2500 次 / 1 秒 |

"接口总限流"字面上是该接口全平台的总量，不是分给单个应用的配额；单应用配额看应用信息页的"流量证书"（PDD-DOC(APP)）。入驻指南 FAQ 另写"每条 api 每天调用量 200 万次"（2022）。配额按应用还是按多多进宝账号计，仍待 V-21 书面确认。

### 3.6 授权（OAuth 2.0 授权码）〔PDD-DOC(AUTH)〕

我方已核对的接口都不需要用户授权，本节只在后续用到"需授权"接口或工具商模式时才用得上。

| 项 | 官方说法 |
| --- | --- |
| 多多进宝推手授权页 | `https://jinbao.pinduoduo.com/open.html` |
| 授权页参数 | `response_type=code`、`client_id`、`redirect_uri`（须 urlencode，等于应用登记的回调地址）、`state`（可选）、`view`（可选，`web` / `h5`） |
| code | 有效期 10 分钟 |
| 换令牌 / 刷新 | `pdd.pop.auth.token.create`（参数 `code`）/ `pdd.pop.auth.token.refresh`（参数 `refresh_token`）；**刷新不延长 access_token 有效期** |
| 令牌响应字段 | `access_token`、`refresh_token`、`expires_in`、`expires_at`、`refresh_token_expires_in`、`refresh_token_expires_at`、`owner_id`、`owner_name`、`scope`、`request_id` |
| 重复授权 | 允许但有频率限制；旧的 code、access_token、refresh_token **立即失效** |
| 有效期 | 创建审核通过阶段 24 小时；已上线后三方工具 24 小时、二方系统与新业务应用 1 年；以 `expires_at` 为准 |
| 可授权账号数 | 审核通过阶段 5 个；已上线 25 / 5 / 不限（三方工具 / 二方系统 / 新业务应用）；有限制时须先把账号加入「授权管理」名单 |

官方「授权说明」里刷新令牌的请求示例把 `type` 写了两次，属文档笔误。

### 3.7 消息推送〔PDD-DOC(MSG)〕

- 只有 Java SDK 能收消息（WebSocket 长连接）；须同时满足：应用已订阅消息、用户已授权应用、应用已调 `pdd.pmc.user.permit` 为该用户开通。
- 消息未消费保留 7 天；失败重试间隔 10 分钟 ×3、1 小时 ×3、12 小时……至多 14 次；官方建议收到消息后隔 10 分钟再调接口取详情。
- 多多进宝订单是否有可订阅的消息主题，文档没写，要在控制台「消息订阅」页看。在确认之前，订单同步仍按轮询设计（CAP-PDD-07）；即使有，也需要一个 Java 接收进程或自行实现其 WebSocket 协议，属新增组件，须另行评估。

### 3.8 Java SDK 默认行为（供自实现对照）〔PDD-DOC(SDK)〕

运行环境 Java SE/EE 1.7 及以上，不支持 Android；HTTP 客户端线程安全、应复用；超时默认值也是上限：连接 5000 ms、读 5000 ms、取连接 1000 ms；连接池总 50、每路由 20。SDK 在控制台「服务端SDK」页下载，只包含该应用已有权限包的接口。

## 4. 客户端 SDK〔PDD-CONSOLE、PDD-DOC(SDK-PRIV)〕

| 项 | 事实 |
| --- | --- |
| 入口 | 控制台 → 应用详情 → 开发者工具 → 客户端SDK → 生成客户端SDK |
| 可选系统 | Android、iOS。没有鸿蒙 |
| Android 要提交 | 上传不大于 200MB 的 .apk；SDK 会校验包内加密的 keystore 与运行中 App 的 keystore 是否一致，不一致则初始化失败 |
| iOS 要提交 | 应用 Bundle ID；SDK 校验安全图片里加密的 client_id 与 App 内"唤端链接"所填 client_id 是否一致，不一致报错 |
| 回调协议 | 一个或多个自定义 scheme（表单填 `<scheme>://`） |
| 生成物 | 平台按上传的包 / Bundle ID 生成"安全图片"并打进 SDK 包，每条记录对应一个"系统 + 包名 + 回调协议" |
| 隐私规则 | 《拼多多开放平台SDK个人信息保护规则》V1.1 覆盖安卓版、iOS 版、Web 版 |
| SDK 收集的信息 | 设备标识符（IDFA、Android ID、OAID、IDFV、MAC 地址）与设备参数、**移动应用列表**、集成方 App 包名与版本、IP、WiFi、运营商、访问时间、商品链接信息、渠道信息 |
| 对开发者的要求 | 集成前告知用户并取得同意，同意前不得收集；隐私政策须披露；须提供查阅、删除、撤回同意等途径；须保持 SDK 为最新版 |

由此得出：

- 生成物与签名绑定：Android 要用**正式签名**的 apk 生成，debug 与 release 签名不同就要各生成一份；iOS 每个 Bundle ID 一份。换签名或换包名都要重新生成。
- 控制台当前的应用属于优券汇，已有的 3 条客户端 SDK 记录都是优券汇的包。凑狸新建应用后（§5 第 1 项），客户端 SDK 在新应用下用凑狸自己的包名 / Bundle ID 生成。
- SDK 提供哪些方法（从"唤端链接""回调协议"看，应是唤起拼多多 App 并回跳）、最低系统版本、包体积，这几页都没写，要看 SDK 包内说明。在拿到之前，不能把"集成客户端 SDK 能改善归因 / 唤起"写成事实（CAP-PDD-11）。
- 入驻指南要求：第三方 App 必须把已安装拼多多 App 的用户自动跳转到官方 App，详细做法指向多多进宝官网文档（未读）。
- 回调协议的登记位置（2026-10-03，功能对照 G-30）：现阶段不集成客户端 SDK（规划/03 §3.5）。日后决定集成时，在控制台登记的回调协议（自定义 scheme）要同时登记进 `contracts/apps.json` 的入站回调类，由生成器写入三端工程，并在探测 App 上做真机回跳验证（规划/03 §4.5）；用凑狸自己的包名与 Bundle ID 生成，不沿用其他应用的记录。

## 5. 准备不足与遗漏（按紧迫程度）

| # | 问题 | 依据 | 需要谁做什么 |
| --- | --- | --- | --- |
| 1 | **凑狸新建独立的开放平台应用（负责人 2026-10-02 确认）。** 不复用优券汇的应用。仍未解决：client_id 要到多多进宝官网与推手账号绑定，官方 FAQ 写"暂不支持解绑"；一个多多进宝账号能否同时绑定优券汇与凑狸两个 client_id，文档没写 | PDD-CONSOLE；DDK-GUIDE FAQ Q1、Q3；DDK-JOIN 入驻流程 | 负责人新建"多多客联盟"应用（材料见第 2 项）。绑定前先向多多进宝确认多绑规则（并入 06 Q-G7 / CAP-PDD-12）：不能多绑时，要么另开多多进宝账号（主表 CAP-PDD-05 的待决策项），要么回到复用，届时再定 |
| 2 | **新建应用的材料与上线审核。** 应用类型选"多多客联盟"，须上传 PRD、MRD 两份 PDF；审核通过后处于测试状态，调用次数受限（错误码 70036），长期不提交上线会被驳回并停用接口 | DDK-JOIN FAQ 1.1；PDD-DOC(NEW)；PDD-API 错误码 | 若新建：负责人准备两份 PDF 并提交；探测脚本与联调量要控制在测试限额内，功能完成后尽快提交上线 |
| 3 | **IP 白名单。** 控制台有「安全中心 → IP白名单」，错误码 20005 即 IP 未加白 | PDD-CONSOLE 菜单；PDD-API 错误码 | 后端与探测环境须有固定出口 IP 并登记；02 部署章节目前没有这项要求，需补 |
| 4 | **客户端 SDK 未纳入三端规划。** 03 与 CAP-PDD-11 此前按"无 SDK"设计；隐私政策的第三方 SDK 清单、同意前不初始化、应用列表权限说明都没有拼多多这一项 | §4 | 先拿到 SDK 包内说明再决定是否集成；若集成，iOS、Android 两端与隐私政策（BR-ID 合规条目）都要补，鸿蒙端无 SDK。2026-10-03（功能对照 G-10）：实验登记在主表 CAP-PDD-11 步骤 4、CAP-PDD-12 步骤 3；集成时必须满足的约束写在 03 §3.5「拼多多客户端 SDK」；是否集成由负责人定（功能对照 Q-06，默认先实验、不集成） |
| 5 | **应用命名与推广用语限制。** 应用与产品命名不得与"拼多多""多多进宝""多多客"有 2 个字及以上重复；宣传不得出现官方认证 / 背书类表述，不得使用"用户返现"等误导性词汇；不得诱导用户不参与官方活动；只能在备案通过的推广资源内推广 | DDK-JOIN FAQ 2、3 | "凑狸"命名不冲突。"返现"已在 BR-TEXT-13 禁用词内；拼多多相关页面与商店描述上线前按这几条再过一遍 |
| 6 | **违规后果是关接口。** 发现违规可直接关闭该账户 API 权限；pid 被判"站内导流"时该 pid 全部订单不结算并置为已处罚 | DDK-JOIN FAQ 3.5；DDK-GUIDE 1.4.1 | 与优券汇共用多多进宝账号时，一方违规两个 App 同时受影响，与 README §0.2 硬规则 5 同一风险 |
| 7 | **分销模式限制。** 官方写"小程序不允许通过多级分销、网赚、诱导分享等模式推广" | DDK-JOIN FAQ 3.4 | 条文只点名小程序。我方有间推奖励（BR-CALC-05，默认关闭）；是否适用于 App 待向多多进宝确认，确认前不在拼多多订单上开启间推属保守做法，是否这样处理由负责人定 **负责人 2026-10-02 定：拼多多订单先不开间推，后台开关保留，多多进宝书面确认 App 可用后再开（§7A）** |
| 8 | **补贴金额不得展示给下级。** 订单与商品里的 `subsidy_duo_amount_ten_million`、`subsidy_duo_amount_level` 官方注明"不允许直接给下级代理展示" | PDD-API(order.*、goods.*) | 这两个字段不得进入用户可见的返利金额或明细；是否计入可分配基数是资金口径，待负责人定（并入 CAP-PDD-04 / 08） **负责人 2026-10-02 定：补贴不计入可分配基数，归平台，用户端不展示（§7A）** |
| 9 | **原文存档（2026-10-02 已完成文字部分）。** 存于私有库 `rebate-private/docs-mirror/pdd/`，图片未存 | README §0.5 | 需要图片证据时再截图补存 |

## 6. 官方接口文档与主表的差异

下列各项已按官方文档核对，主表对应行待回写（除标"已改"的）。

**CAP-PDD-01 商品识别**

- goods.search 的 `keyword` 支持 goods_id、拼多多 App 商详链接、进宝长链 / 短链：与主表一致。
- **goods.search、goods.detail 的出参里没有 goods_id**，只有 goods_sign；goods_id 只在订单接口返回。主表通过标准写的"商品详情和订单出参里 goods_id 仍稳定返回"对商品接口不成立，product_key 不能指望从商品接口拿 goods_id（附录 A-11 的退路提前成为主路径，待 BR-PROD 评估）。
- 新接口 `pdd.ddk.url.short.parse`：把进宝短链解析成长链，只支持 goods.promotion.url.generate 生成的短链。可用于识别他人分享的进宝短链。

**CAP-PDD-02 价格**

- 官方 FAQ 给出口径：min_group_price 是现价，现价减 coupon_discount 是券后价。候选公式有了官方依据，仍须按 BR-PRICE-02 实测。
- goods.detail 的 `need_sku_info`（特殊渠道权限）返回 `sku_list`：每个规格有 `jinbao_goods_price`（进宝算价结果，分）、`min_group_price`、`coupon_amount`、`is_onsale`（上下架）、`sku_id_code`、`spec_list`、是否百补消费券。拿到该权限即可得到规格级价格与上下架状态。
- 新增券与补贴字段：`platform_discount_list`（进宝平台券：千万神券、限时秒杀、超红大额券、爆品加补）、店铺券 `mall_coupon_*`、店铺收藏券 `clt_cpn_*`、`subsidy_list`、`subsidy_goods_type`。券后价公式是否要计入平台券，待实测。
- `activity_type` 含 25 定金预售（goods.search 出参），可作预售标识的候选（BR-PRICE-22）。`service_tags` 含 1 全场包邮；仍没有运费金额与库存字段。
- `goods_labels` 含 1 App 专享。

**CAP-PDD-03 搜索**

- `range_id` 官方枚举：0 最小成团价、1 券后价、2 佣金比例、3 优惠券价格、4 广告创建时间、5 销量、6 佣金金额、7–9 店铺描述 / 物流 / 服务分、10–12 三项分击败同行百分比、13 商品分、17 优惠券 / 最小团购价、18 过去两小时 pv、19 过去两小时销量。主表"range_id 枚举含义 SDK 未给"可关闭，实验改为抽样验证。
- `sort_type` 完整枚举 0–20、27–32；`activity_tags` 另有 31 品牌黑标、10564 / 10584 精选爆品；新增 `block_cat_packages`（含 3 医疗器械、4 处方药、5 非处方药等屏蔽包）、`risk_params`、`goods_img_type`。
- `pid`、`custom_parameters` 在搜索与详情里都是非必填。"未备案报 60001"官方文档未提，仍待实测。

**CAP-PDD-04 佣金**

- 订单 `promotion_amount` 官方注明"包含软件服务费"；另有 `duo_id_service_fee`（软件服务费，分）。可分配基数是否要扣软件服务费，是资金口径，待负责人定后写入 BR-CALC。 **负责人 2026-10-02 定：按实际到账算，即先扣软件服务费再分（§7A）。**
- 订单新增 `bandan_risk_consult`（代购订单预判：-1 未出结果、0 否、1 是，以最终审核为准）、`cps_level`、`platform_discount`（订单使用的平台券金额）、`no_subsidy_reason`、`red_packet_type`。
- 商品 `plan_type`：1 全店、2 单品、3 定向、4 招商、5 分销推广。
- "自购 75%"在已读页面里没有出现，仍无官方依据。

**CAP-PDD-05 归因与备案**

- `custom_parameters` 官方描述：最长 64 字节；uid 必填、每个用户对应一个标识；sid 非必填；可加其他自定义 key。与主表一致。备案按什么键匹配，文档仍未写。
- `rp.prom.url.generate` 的 `channel_type=10` 生成绑定备案链接，属于标准"多多客权限包"；只有 channel_type=0（红包）注明需申请推广权限。`p_id_list` 最长 1，活动页生链要求传入授权备案信息。2020 年指南说该接口整体是特权接口，与现行接口文档不一致，以接口文档为准，仍须实测。
- `member.authority.query`：pid、custom_parameters 均非必填，返回 `bind` 1 / 0。
- `pid.mediaid.bind`：`media_id` + `pid_list`（一次最多 1000 个）。`pid.generate`：一次 1–100 个，可直接带 `media_id`，返回 `remain_pid_count`。每个账号 pid 上限 10 万个，可联系客服增加。
- 归属规则（2020 指南，红包与单品推广）：结算给用户购买前**最后点击**的领券页对应的推手 pid。这是"最后点击"的首个官方依据，点击有效期仍没有来源。

**CAP-PDD-06 转链**

- **可以带规格**（已改主表）：`goods_gen_url_param_list` 内的 `sku_id_list` / `sku_id_code_list`（须有 sku 权限，否则不生效）会生成拼接规格的链接，点击后商详自动选中该规格。`sku_id_code` 来自 goods.detail 的 sku_list 或 order.detail.get。
- 新增入参：`generate_weixin_code`、`generate_we_app_long_link`、`generate_share_image`（仅单个商品）、`generate_mall_collect_coupon`、`url_type`（1 百补相似品列表）、`special_params`。官方现行入参里没有 `generate_qq_app`。微信 ShortLink 每个渠道每天数量有限。
- 出参含义（官方）：`mobile_url` 微信内进领券页后拉起小程序、浏览器内直接拉起 App、未安装时落地页点领券进登录页；`url` 浏览器内优先拉起微信小程序；`schema_url` 已安装时唤起 App，需客户端支持 schema 协议。App 内外跳应优先 schema_url / mobile_url，不用 `url`。
- `search_id` 建议填写，来源含 goods.recommend.get、goods.search。
- zs.unit.url.gen 同时属于"多多客权限包"与"多多客工具权限包"；出参没有 schema_url。

**CAP-PDD-07 订单**

- increment.get 的时间窗 ≤24 小时、近 90 天、page 1–10000、page_size 10–100（建议 40–50）、必须倒序翻页、`return_count=false`：与主表一致。range.get 按支付时间、`last_order_id` 迭代、page_size 建议 300：一致。
- **`return_status`、`sku_id_code`、`url_last_generate_time`、`point_time`、`cps_sign` 只出现在 order.detail.get 的出参里**，两个列表接口的出参没有。售后状态要靠逐单调详情接口补，或由 order_status 变化推断；主表把 return_status 当作列表字段的写法需改，PDD-07 / 08 实验要按此设计。
- 推广位字段名不统一：列表接口是 `p_id`，详情接口是 `pid`。
- 列表与详情都有 `order_id`（订单 ID）与 `order_sn`（推广订单编号）两个字段；哪个对应买家端可见订单号，待实测（F-ORD-09 找回）。
- order_status 现行枚举 0、1、2、3、4、5、10，与主表一致。2020 指南另提"未支付""非多多进宝商品（无佣金订单）"两种，现行枚举里没有。

**CAP-PDD-08 结算**

- 2020 指南：确认收货 15 天后未发生售后 → 审核成功；发生售后 → 审核失败；**每月 20 号结算当月 15 号及以前审核通过的订单**。这是结算周期的首个官方说法（主表原写"无来源"），因是 2020 年旧页，仍须按 08b 实测核对。
- `no_subsidy_reason` 的示例含"订单超过 2 个月未审核成功"。

**CAP-PDD-10 推荐**

- channel_type、limit、offset、list_id 与主表一致；`goods_sign_list` 在相似推荐场景只取第一位；channel_type=4 注明与进宝网站精选一致。

**CAP-PDD-11 唤起**

- 存在官方客户端 SDK（Android、iOS），见 §4；主表"按无 SDK 设计"已改为"待取得 SDK 说明后评估"。鸿蒙：2026-10-02 控制台未见鸿蒙选项，当前是否支持未核实（2026-10-05 改述，目录缺席不足以证明不支持）。

**CAP-PDD-12 凭据与配额**

- 应用类型：多多进宝推手角色（企业或个人）下创建"多多客联盟"应用；接口文档的权限包一栏另列有"多多客"应用类型。
- 我方接口不需要用户令牌；令牌有效期只在用到需授权接口时才相关（§3.6）。
- 沙箱：官方明确没有。限流与日上限见 §3.5。timestamp 容差 10 分钟，服务器须校时。

## 7. 我方接入步骤

**人（V-05，凭据不进代理会话，README §0.2 硬规则 4）**

1. 为凑狸新建"多多客联盟"应用并提交材料（§5 第 1、2 项；负责人 2026-10-02 确认新建）。
2. 在多多进宝官网绑定 client_id（不可解绑，先确认多绑规则）。
3. 登记出口 IP 白名单；在应用信息页截图"流量证书"与权限包列表。
4. 在多多进宝为凑狸建 App 媒体，记下 media_id，供建 pid 时绑定（CAP-PDD-05 步骤 1）。
5. 在「服务端SDK」页下载 Java SDK 备查；若要评估客户端 SDK，用凑狸的包名 / Bundle ID 生成并取出包内说明。下载的 SDK 包放仓库根目录的 `_vendor-sdk/`（已在 `.gitignore` 排除），不提交；client_secret 只放 KMS（02 §12.6）。
6. 把 §2 各页原文存入私有存储的 `evidence/sources/pdd/`。

**代理（rebate-platform 仓库建好后）**

1. 在拼多多 `UnionAdapter` 内实现签名函数，用 §3.3 的官方示例作单元测试。
2. 实现统一请求函数：补公共参数 → 签名 → POST JSON 到 API 网关 → 按 §3.4 的键名表解包、按错误码表分类；网关地址读 `config/union-endpoints.yaml`（real / replay / mock）；超时取 02 §6.2 的值。
3. 订单同步按 §6 CAP-PDD-07：列表接口增量拉取，售后状态用 order.detail.get 逐单补。
4. 探测脚本 `tools/probe/pdd/*` 复用同一签名模块（V-08）。`pdd12_token.ts` 降为可选：主链路接口不需要令牌。

## 7A. 负责人拍板（2026-10-02）

| 事项 | 决定 | 写回 |
| --- | --- | --- |
| 软件服务费 | 返利按实际到账金额算：可分配基数 = 佣金 − 软件服务费（`duo_id_service_fee`），与淘宝扣技术服务费同一口径 | BR-CALC（拼多多基数），CAP-PDD-04 |
| 官方渠道补贴（`subsidy_duo_amount_ten_million`、`subsidy_duo_amount_level`） | 不计入可分配基数，归平台；任何用户端页面与明细不展示 | BR-CALC，CAP-PDD-04 / 08 |
| 间推（好友推广奖励）在拼多多订单上 | 先不开；后台开关保留，多多进宝书面确认 App 适用后再开 | BR-CALC-05，CAP-PDD-05 |

## 8. 仍未知

- 一个多多进宝账号能否绑定多个 client_id；凑狸新应用与优券汇（花卷云）现有授权是否互相影响。
- 配额按应用还是按多多进宝账号计；测试状态的调用上限是多少。
- 客户端 SDK 的功能、接口、最低系统版本与体积；SDK 在端上取得的风控标识的用途，它与接口入参 `risk_params` 的对应关系，以及不传时对搜索、转链、代购预判与佣金的影响（CAP-PDD-11 步骤 4、CAP-PDD-12 步骤 3，2026-10-03）。
- 备案匹配键、点击有效期、自购计佣比例（CAP-PDD-04 / 05 的原有未知项，官方文档没有回答）。
- 多多进宝订单是否有消息推送主题。
- 数组 / 对象参数的签名序列化方式。
