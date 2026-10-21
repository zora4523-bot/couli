# 08 业务规则 · 11. 邀请与分销（BR-INV）

返回 [README](README.md)（使用规则、术语表、规则索引）

## 11. 邀请与分销（BR-INV）

本节规定：邀请码、绑定渠道与校验、禁止关系、改上级、计酬层级（直推 + 间推）、直推与间推受益人、等级、下级可见范围、开关与 P1 奖励、P1 会员口径、邀请奖励活动。共 24 条（已确认 13、默认假设 11）。

2026-10-01 晚负责人补充决定（docs/changes/20261001-拍板第二批.md §8）：ADD-06 用户只有一个余额（BR-FUND-13），直推、间推分佣与分享收益都入受益人的同一余额，来源由流水类型区分（BR-INV-12、13、17、19 已改写，状态不变）；ADD-05 间推开关随规则版本发布由超管或有权限账号一人 step-up 完成（BR-CALC-05）；ADD-03 各等级比例开发期用占位值，上线前超管在后台填写。

订单状态统一按 BR-FUND-01 双状态书写（platform_status + rebate_status，C-01 默认处理）。与 规划/04 单一 order_status 的对照：O2「首次入库已归因」≈ rebate_status R2；O11「找回 / 后台改归属」≈ R3；INVALID ≈ rebate_status=VOID；CLAWED_BACK 同名；确认收货 = platform_status 首次到 RECEIVED（或经 P5 补写）。若负责人不采纳双状态，按 BR-FUND-01 的映射表回退。

2026-10-03 功能对照补缺第 1 批（docs/changes/20261003-功能对照补缺.md；「功能对照 G-xx / Q-xx」是该批清单的编号，与 规划/10 §6.1 的 G-xx、规划/06 的 Q-xx 不是同一套）：BR-INV-03 细则补「第三方登录新号的两处提醒」（G-05，按 Q-01 默认 C 写，待负责人确认）；BR-INV-04、BR-INV-07 细则、BR-INV-21 同步指针与两个提醒开关。绑定渠道、先到先得、补填条件与期限都不变，条目状态不变。

2026-10-03 功能对照补缺第 2 批（同一变更记录的「第 2 批」，功能对照 G-09～G-21）：逐条改动在正文或细则里注「2026-10-03」与所按的缺口编号；本批不新增 BR-INV 条目，各条状态不变。

2026-10-03 功能对照补缺第 3 批第 3 轮评审后（同一变更记录 3.11）：BR-INV-06 正文加一句——客户端版本过低时的登录是受限登录，只登录已有账号，不建号、不绑定（BR-ID-01 细则「受限会话」）。绑定规则与条目状态都不变。

2026-10-03 功能对照补缺第 4 批（docs/changes/20261003-功能对照补缺.md「第 4 批」）：BR-INV-04 细则加「邀请码的来源」、BR-INV-20 细则加「不做免填邀请码」（功能对照 Q-16 默认 A）；状态不变。
2026-10-03 功能对照补缺第 5 批（同一变更记录的「第 5 批」，功能对照 G-66～G-96）：BR-INV-04 细则补「扫码填邀请码」并登记为 P1（G-78，正式版第一版不申请相机权限，功能对照 Q-25 默认 A）；BR-INV-16 细则补 P1 好友列表接口改名为 GET /v1/invites/friends（G-67）；BR-INV-18 细则补 P1 专属导师不展示邀请人联系方式（G-66，按功能对照 Q-18 默认 A）。各条状态不变，没有新增或作废条目，绑定渠道与上级可见范围不变。同日按第 1 轮评审的公开表述裁定（变更记录 5.9）：BR-INV-23 正文与细则删去「沿用现有 App 口径」的来源说法，口径与取值不变。

2026-10-04 设计稿第二批拍板（docs/changes/20261004-设计稿第二批拍板.md，负责人 2026-10-04 确认）：BR-INV-18 细则加「邀请页规则摘要明说不发奖励」（§9）。状态不变，没有新增条目。

2026-10-06 待确认事项整批确认（docs/changes/20261006-待确认事项整批确认与交由Jev判断.md，负责人 2026-10-06「全部按建议走吧 不要限制的太死了」）：BR-INV-23 由待决策改为已确认（P1 会员口径按默认，MVP 仍不启用）；有效新人金额门槛仍由财务在 P1 规格给出（§11.3 第 12 项）。

2026-10-06 剩余旧标注处理（docs/changes/20261006-待确认事项整批确认与交由Jev判断.md §14；00 §8 第 ① 类同步，原需负责人确认的默认按 规划/11 §7.1 交 Jev 判断）：BR-INV-04 游客预填邀请码只在本次进程内有效，按默认确认；C-03 码号改注代理自定（00 §9）。状态不变，没有新增条目与错误码。

2026-10-18 登录注册改版（`docs/changes/20261018-登录注册改版.md`，00 §8 第 ② 类，负责人 2026-10-18 对登录注册审稿报告第 6 节「全部按推荐」，按 00 §8 直接回写并注明日期）：邀请码挪到登录后——登录页不再有邀请码输入框；已知邀请码（游客点击确认的剪贴板邀请提示条、用户点开并拉起 App 的邀请链接里的码）随登录请求带上，仍走 register 渠道；本次新建、无上级的账号登录成功后有一页可跳过的「填写邀请码」，走 backfill 渠道；第三方登录新号先整页绑手机再进该页。改动在 BR-INV-03 正文与细则（新增「登录成功后的新号步骤」，「两处提醒」① 由弹窗改为整页）、BR-INV-04 正文 ④ 与细则、BR-INV-06（标题与正文、细则）、BR-INV-07 细则、BR-INV-08 正文的登录方式列举、BR-INV-16 / 18 细则（告知句位置、落地页【在 App 中打开】）、BR-INV-21 正文；BR-INV-04 细则「邀请码的来源」补邀请链接拉起 App 这一来源（审稿报告「邀请链接带来的」）。先到先得、绑定须已绑手机、补填期限（backfill_hours）、有订单不能补填等取值一条不改；没有新增条目、渠道值与错误码，各条状态不变。

2026-10-18 登录 v2 画板定稿前的文案键（`docs/changes/20261018-登录注册改版.md` §10「补充」，00 §8 第 ① 类）：BR-INV-03 细则「第三方登录新号的两处提醒」里购买版绑手机页正文的键名改为 `invite.bind_phone_guide.before_buy_warn`（BR-TEXT-14 表 C 把 `.body` / `.body_before_buy` 按句拆键，文字不变）。规则与状态不变。

2026-10-19 邀请奖励与登录精简（`docs/changes/20261019-邀请奖励与登录精简.md`，00 §8 第 ② 类，负责人 2026-10-19 在对话中确认三项「推荐」选项，按 00 §8 直接回写并注明日期）：① 对被邀请人的告知句从 App 内去掉，只留隐私政策、用户协议与邀请落地页（BR-INV-16 细则告知位置 ④ 删去，BR-INV-18 正文与细则、BR-INV-04 细则同步；上线前法务确认，06 Q-F4）；② 购买不再触发插页：由点击购买触发的登录成功后直接继续购买，不出「绑定手机号」整页与「填写邀请码」页，「首次购买前提示」作废（BR-INV-03 细则改写，开关 invite.before_buy_tip 作废、键保留不用；BR-INV-07、21 同步），填写邀请码页精简；③ 新增 BR-INV-24「邀请奖励活动」（双方各得、可开关、默认关闭），BR-INV-22 标题与正文改为不含邀请奖励，BR-INV-12、20、23 各加一句与 BR-INV-24 的界限。绑定渠道、先到先得、补填期限与条件、并号条件的取值都不变；新增 1 条（默认假设），其余各条状态不变。

2026-10-21 App 内高保真三批定稿回写（docs/changes/20261021-App内高保真定稿回写.md，00 §8 第 ① 类）：BR-INV-18 细则邀请页奖励句改引 `invite.reward.tip_inviter`（第 3 批 W-08，与 BR-INV-24 ⑨、BR-TEXT-14 表 C 一致），BR-INV-24 影响面随之写明两键；BR-INV-06 细则 42901、BR-INV-09 正文 30402、BR-INV-19 正文与 BR-INV-18 细则例 30413 的提示不再复述文案，改引 BR-TEXT-14 表 A（W-09，以表 A 为准）；BR-INV-18、BR-INV-19 细则补「不能邀请时不显示邀请奖励活动卡」（W-17，按定稿画板的保守默认，代理补全）。各条状态不变。

### 11.1 规则一览

| 编号 | 规则 | 状态 | 影响面 |
| --- | --- | --- | --- |
| BR-INV-01 | **邀请码生成与格式**<br>每个用户必须在账号创建的同一事务内由服务端生成 1 个邀请码，终身不变。字符集固定为 32 个字符 `23456789ABCDEFGHJKLMNPQRSTUVWXYZ`（去掉 0/O/1/I），长度等于 6，用 CSPRNG 均匀随机生成；(app_id, invite_code) 必须唯一。每个账号最多生成 5 个候选码（含首次）：每个候选码先按敏感词库（场景=invite_code，不区分大小写的子串匹配）过滤，再用 `INSERT … ON CONFLICT (app_id, invite_code) DO NOTHING` 或在 SAVEPOINT 内写入；唯一冲突或命中敏感词各计 1 次。5 个候选全部失败时回滚整个注册事务，注册接口返回 50001 并告警。已注销账号的邀请码不得回收或再分配。新 App 码空间与优券汇独立，不导入、不互认。用户自定义邀请码为 P1。 | 已确认 | users.invite_code（唯一 (app_id, invite_code)）；注册 / 落地页注册事务；敏感词库场景 invite_code；后台用户查询（按邀请码搜索）；错误码 50001；验收用例 AC-INV-01 |
| BR-INV-02 | **邀请码输入校验与错误码**<br>【规范化】服务端对邀请码依次执行：Unicode NFKC 规范化 → 删除全部 Unicode 空白字符（含 \\s、U+3000）及零宽字符 U+200B–U+200D、U+FEFF → 转大写。规范化后为空字符串的：register 渠道视为未携带 invite_code（响应不含 invite_bind），backfill 与 landing 渠道返回 30401。不做 O→0 等纠错映射。<br>【邀请人不可用判定】定义唯一判定函数 `inviter_unavailable(u)` = u.risk_state ∈ {banned, appealing, frozen} OR u 存在 deletion_status ∈ {cooling, processing, done} 的注销单 OR u.phone_hmac IS NULL OR (u.realname_status=verified 且按 BR-INV-19 在判定时刻未满 18 周岁)；以调用时刻的状态为准。绑定校验（30401）、邀请页展示（BR-INV-18）、后台改上级（BR-INV-10）必须调用同一个函数，不得各自实现；快照与入账时直推受益人的有效性不调用本函数，按 BR-CALC-13（BR-INV-13）。<br>【校验顺序】backfill 与 register 渠道固定为：身份级别 phone（10005，仅 backfill）→ 开关 growth.invite_bind.enabled（关则 30408）→ 频控（42901）→ 本人已有上级或已用过自助绑定（30402）→ 补填期限（30404，仅 backfill）→ 补填条件：订单、找回申请或下级（30409，仅 backfill）→ 规范化后格式校验：长度≠6 或含字符集外字符（30401，不查库）→ 邀请人存在且 inviter_unavailable=false（否则 30401）→ 关系冲突（30403，BR-INV-08）。每一步命中即返回，不执行后续步骤。landing 渠道顺序见 BR-INV-05，后台改上级顺序见 BR-INV-10。<br>【文案】邀请人不存在或不可用一律返回 30401，文案统一为“邀请码无效”，不得暴露具体原因。<br>【频控】计数对象 = 三个渠道返回的全部 30401（含格式错误与空码）；计数键 = phone_hmac（三渠道共用），landing 渠道另按 IP 单独计数。当日（+08:00 自然日）同一键累计 30401 ≥5 次后，该键当日后续绑定请求在频控这一步返回 42901，Retry-After = 距次日 00:00 +08:00 的秒数。register 渠道命中时照常建号，invite_bind={failed, 42901}。 | 默认假设 | POST /v1/me/inviter；POST /v1/auth/login/sms（invite_code）；POST /v1/invites/landing-register；inviter_unavailable 公共判定函数（packages/domain）；错误码表 04 §7（30408、30409 由本主题占用，C-03）；客户端 / H5 错误提示文案；客服话术（邀请码无效）；验收用例 AC-INV-\* |
| BR-INV-03 | **绑定渠道与先到先得**<br>MVP 自助绑定渠道只有 3 个，source 取值固定：`landing`（邀请落地页手机号注册，服务端直接绑定，BR-INV-05）、`register`（App 内登录新建账号时随登录请求携带已知邀请码，BR-INV-06；2026-10-18 起登录页不再手填）、`backfill`（“我的”补填与登录后新号的「填写邀请码」页，BR-INV-07）。每个账号自助绑定成功最多 1 次，关系取最先成功的一次，后到的任何渠道都不得覆盖（补填返回 30402，登录携带的 invite_code 被忽略）。绑定写库必须用条件更新 `WHERE parent_id IS NULL AND self_bind_used = false`，并以 Idempotency-Key 去重；成功时同事务写 self_bind_used=true、parent_bind_source、parent_bound_at、relation_change_logs。绑定需要被邀请人为 phone 级别（落地页天然满足）。Agent / AI 工具不得注册任何绑定上级接口（见 BR-AI）。 | 已确认 | users.parent_id、users.self_bind_used、users.parent_bind_source、users.parent_bound_at；relation_change_logs；POST /v1/invites/landing-register、POST /v1/auth/login/sms 与 POST /v1/auth/login/one-tap（2026-10-18）、POST /v1/me/inviter；登录后的「填写邀请码」页（2026-10-18）；Agent 工具注册表 CI 检查；验收用例 AC-INV-\* |
| BR-INV-04 | **剪贴板邀请口令自动识别（MVP）**<br>MVP 必须支持剪贴板邀请口令自动识别，读取方式、读取前提与读取时机只按 BR-ID-16（剪贴板合规规则）执行，本条不放宽：① 前提：本设备已同意当前版本隐私政策（基本模式不读，BR-ID-11），且满足 BR-ID-16 规定的系统权限、用户开关与平台提示方式（三端读取方式只在 BR-ID-16 维护）；② 时机：只在 BR-ID-16 规定的 App 回到前台（含冷启动进入前台）时刻，不在后台读取、不轮询；③ 触发对象：只对「可绑定」的用户触发——未登录（游客）或已登录且 parent_id IS NULL、self_bind_used=false、在补填期限内（/v1/config.invite.backfill_hours）；已有上级、已用过绑定机会、已过期限的用户不识别、不提示；④ 识别后只显示邀请提示条（展示抽取出的邀请码），用户点击确认才进入绑定：已登录走 backfill（POST /v1/me/inviter，BR-INV-07），游客点确认后把邀请码记为「待绑定码」（只存本机、不提交、不需登录），之后进入登录页时显示一条可移除的小字，随下一次登录请求带上、新建账号时走 register（BR-INV-06；2026-10-18 起登录页不再有邀请码输入框，`docs/changes/20261018-登录注册改版.md`）；不得自动提交，关闭提示条即放弃，同一内容 hash 24 小时只提示一次（本条独立的邀请提示去重，自动读取与手动粘贴都适用，不随 BR-ID-16 的商品去重只对自动任务的规定，2026-10-17）；⑤ 只上传抽取出的 6 位邀请码，不上传、不保存剪贴板原文（BR-ID-16）。抽取规则（三端一致，自动识别与输入框“粘贴”按钮共用）：对剪贴板文本做 NFKC 规范化并转大写，用正则 `(?<![0-9A-Z])[2-9A-HJ-NP-Z]{6}(?![0-9A-Z])` 取第一个匹配；没有匹配时不提示（粘贴按钮提示“未识别到邀请码”）。填写邀请码页（「我的」补填与登录后新号的一步，2026-10-18）的“粘贴”按钮保留（用户点击后才读，走 `clipboard.read` L2 手势规则）。服务端仍按 BR-INV-02 校验。App 自己写入剪贴板的邀请码与口令按 BR-ID-16 / 03 的 hash 规则排除，既不被商品识别误判为商品，也不触发邀请提示条；抽取结果等于本人邀请码时不提示。邀请口令与商品链接 / 口令同时出现时商品优先；只有文本含分享域名落地页链接或「邀请码」字样时才出邀请提示条（细则，拍板第二批 OPS-06）。 | 已确认 | 登录页待绑定码提示与填写邀请码页 UI（三端 + H5，2026-10-18）；ClipboardWatcher 邀请口令识别与邀请提示条（三端）；03 §4.6 剪贴板实现；/v1/config.clipboard 本地过滤规则；clipboard.read 桥方法；提示条文案键（BR-TEXT，待登记）；POST /v1/me/inviter、POST /v1/auth/login/sms；隐私政策剪贴板用途；验收用例 |
| BR-INV-05 | **落地页注册绑定**<br>落地页只用两个接口：发码 `POST /v1/landing/sms-codes`（免签名、不要求人机验证，发码限流见 BR-ID-32），注册并绑定 `POST /v1/invites/landing-register`（BR-ID-32 所称 `POST /v1/landing/login` 即本接口，路径按 13 保留规划写法；none 级别，Idempotency-Key 必填）。landing-register 入参 phone、sms_code、invite_code、agreed（协议勾选）、channel（可选渠道码），不收 captcha_token（MVP 不接入人机验证，负责人 2026-10-06）。落地页必须展示《用户协议》《隐私政策》勾选框（默认不勾），未勾选不得提交。校验顺序固定为：agreed=true（否则 10004）→ 开关（30408）→ 频控：同 IP 或同 phone_hmac 当日 30401 ≥5 次（42901）→ 邀请码规范化与格式（30401）→ 邀请人存在且 inviter_unavailable=false（30401）→ 短信验证码校验并核销（20002 / 20003，BR-ID-05）→ 手机号是否已注册（是则 `already_registered`）→ 同 IP 注册上限（BR-ID-32）→ 44001、不建号 → 建号并绑定。邀请码失败时不核销短信验证码；“已注册”判定必须在短信验证码校验通过之后。存在 phone_hmac 相同且注销状态不为 done 的账号（含 cooling、processing）时，不得修改任何关系，返回 `already_registered`；只存在已 done 的注销账号时视为新手机号。新号必须在同一事务内：创建用户（register_method=h5_landing，registered_channel 按 BR-ID-04 取渠道码）、写 parent_id=邀请人、parent_bind_source=landing、parent_bound_at、self_bind_used=true、relation_change_logs 一条、consent_records（agreement 与 privacy 各一条，version=当前版本，channel=h5_landing，accepted=true）。落地页不采集设备 ID，同设备校验延后到首次 App 登录（BR-INV-09）。落地页 `/i/{code}` 对有效码与无效码返回相同页面结构，不显示邀请人昵称或任何个人信息。 | 默认假设 | POST /v1/landing/sms-codes（限流 42901）；POST /v1/invites/landing-register 请求（agreed）与响应（result=already_registered、44001）；配置 landing.ip_register_limit；H5 invite-landing 页面（协议勾选框、统一页面结构）；users.register_method、users.registered_channel、users.phone_hmac 唯一约束；注销留存表（phone_hmac，留存见 BR-ID-30 ⑩）；consent_records（channel=h5_landing）；relation_change_logs；验收用例 AC-INV-02 |
| BR-INV-06 | **登录请求携带邀请码**<br>（2026-10-18 前标题为「注册页填写邀请码」；负责人 2026-10-18 改为登录页不手填，`docs/changes/20261018-登录注册改版.md`）invite_code 只来自已知邀请码（BR-INV-04「待绑定码」）——游客点击确认的剪贴板邀请提示条，或用户点开、直接拉起 App 的邀请链接里带的码（BR-INV-04 细则「邀请链接拉起 App」）；第三方登录接口不收 invite_code（未绑手机不能绑定，BR-INV-03）。POST /v1/auth/login/sms 或一键登录接口 POST /v1/auth/login/one-tap 携带 invite_code 时：若手机号对应账号已存在，必须忽略 invite_code 且不报错；若本次请求新建账号，绑定在建号事务内用 SAVEPOINT 执行，绑定校验失败或写库异常时只回滚到 savepoint，账号照常提交，绑定失败不得阻止注册。响应仅在请求携带规范化后非空的 invite_code 时包含 `invite_bind`：{result: bound \| failed \| ignored_existing_user, code?: 30401 \| 30403 \| 30408 \| 42901 \| 50001}，其中 50001 表示绑定内部错误。failed 时 self_bind_used 保持 false，可在期限内补填。注册页绑定同样执行 BR-INV-08 的同设备校验（设备 ID 取请求签名中的 device_id）。config.invite.required 在 MVP 必须为 false。客户端版本低于最低支持版本时的登录是受限登录（BR-ID-01 细则「受限会话」）：只登录已有账号并按上文忽略 invite_code，不建号、不绑定，手机号尚未注册时返回 10405（2026-10-03 第 3 批第 3 轮评审后补）。 | 默认假设 | POST /v1/auth/login/sms 与 POST /v1/auth/login/one-tap 的请求与响应结构；登录页待绑定码提示、登录后「填写邀请码」页的失败说明（BR-TEXT-14 表 C）；config.invite.required；验收用例 |
| BR-INV-07 | **补填条件与期限**<br>POST /v1/me/inviter（phone 级别 + 请求签名 + Idempotency-Key）仅在同时满足以下条件时绑定成功，按 BR-INV-02 顺序校验：(a) parent_id IS NULL 且 self_bind_used=false，否则 30402；(b) 服务端当前时间 &lt; users.created_at + config.invite.backfill_hours（默认 168 小时，精确到秒，等于边界时刻即拒绝），否则 30404；(c) 本人为归属用户的订单数 = 0（orders.user_id=本人，任何 platform_status / rebate_status，含 rebate_status=VOID 或 CLAWED_BACK，自购与分享单都算），本人没有任何状态的找回申请（claim_status 任意值），且直属下级数 = 0（users.parent_id=本人，任何状态），否则 30409；(d) 通过 BR-INV-02 的邀请人校验与 BR-INV-08。成功只允许 1 次。补填成功前已付款、之后才入库或找回的订单，按 BR-INV-13 的付款时间规则不写直推受益人。 | 已确认 | POST /v1/me/inviter；/v1/config.invite.backfill_hours；“我的”页补填入口显隐；orders、order_claims、users 计数查询；错误码 30404、30409；客服话术（为什么不能补填）；验收用例 AC-INV-\* |
| BR-INV-08 | **禁止绑定的关系**<br>以下情形必须返回 30403（文案“不能绑定该邀请人”）：① 邀请人 = 被邀请人；② 邀请人是被邀请人的任意深度下级（从邀请人沿 parent_id 向上遍历，遇到被邀请人即命中；遍历上限 1000 层，超限按命中处理并告警）；③ 同设备：被邀请人设备集合 = login_logs 中该用户保留期内全部登录成功记录的 device_id_hash（register、backfill 渠道再并入本次请求签名中 device_id 的 hash；后台改上级不并入操作人设备），邀请人设备集合 = login_logs 中该用户保留期内全部登录成功记录的 device_id_hash，两集合交集非空即命中。login_logs 只记录 sms/carrier_one_tap/huawei_one_tap/wechat/apple/huawei 登录成功事件（两个一键登录取值 2026-10-18 加，BR-ID-04），不含 token refresh 与 H5 换 token，留存见 BR-ID-30 ⑥；已注销用户按 F-ACC-10 只保留设备哈希（deleted_identities，留存见 BR-ID-30 ⑩、BR-ID-28），用于本校验。本规则适用于 register、backfill、后台改上级；landing 渠道按 BR-INV-09 事后复核。 | 已确认 | login_logs（新表）、devices；POST /v1/me/inviter、POST /v1/auth/login/sms、后台改上级；risk_hits（记录命中）；隐私政策（登录日志留存期，见 BR-ID-30）；验收用例 |
| BR-INV-09 | **落地页绑定的同设备复核**<br>对 parent_bind_source=landing 且 login_logs 中尚无该用户任何记录的账号，在其首次 App 登录成功（任一登录方式写入第一条 login_logs）的同一事务内执行 BR-INV-08 ③ 校验（被邀请人设备集合 = 本次登录的 device_id_hash）。命中时登录照常成功；parent_id 置 NULL，写 relation_change_logs(source=risk_same_device) 与 risk_hits，self_bind_used 保持 true（不再给自助绑定机会），不通知邀请人也不推送被邀请人；此后 GET /v1/me 的邀请人状态显示“未绑定”，补填返回 30402（文案取 BR-TEXT-14 表 A 30402 行，以表 A 为准；2026-10-21 按 App 内高保真第 3 批定稿 W-09 改为引用，原在此复述了一句与表 A 不同的文案）。未命中则关系保持。首次 App 登录前被邀请人不可能产生订单，因此不影响任何分佣快照。 | 默认假设 | 登录流程（POST /v1/auth/login/\* 成功分支）；users.parent_id；relation_change_logs、risk_hits、login_logs；GET /v1/me 邀请人状态；验收用例 |
| BR-INV-10 | **不可自改绑与后台改上级**<br>用户端不得提供任何改绑或解绑上级的接口。后台改上级（含解绑为无上级）校验顺序固定为：操作人具备“改绑上级”权限且完成二次验证（step-up）并填写原因 → 目标用户直属下级数 = 0、订单数 = 0（任何状态）、无任何状态的找回申请（否则 30409）→ 新上级存在且 inviter_unavailable=false（BR-INV-02，否则 30401；解绑时跳过）→ BR-INV-08 关系冲突（30403；解绑时跳过）。后台改上级不受 BR-INV-07 的 168 小时期限约束，也不受 growth.invite_bind.enabled 约束。成功时同事务将 self_bind_used 置为 true、parent_bind_source=admin、parent_bound_at=操作时间，并写 relation_change_logs(user_id, old_parent_id, new_parent_id, source=admin, operator_id, reason, created_at +08:00)；解绑后用户不再获得自助绑定机会。已生成的分佣快照不得因改绑变化。 | 默认假设 | 后台用户详情“改上级”操作；04 §11 后台角色权限；users.self_bind_used、parent_bind_source、parent_bound_at；relation_change_logs；客服话术（用户要求改上级）；验收用例 |
| BR-INV-11 | **关系存储与注销影响**<br>users.parent_id 是当前上下级关系的唯一权威来源；历史某一时刻的上级（BR-INV-13 按 paid_at 取值）只能由 relation_change_logs 按 created_at 重放得出（某时刻 t 的上级 = created_at ≤ t 的最后一条记录的 new_parent_id，无记录为无上级），因此所有变更必须同事务写 users.parent_id 与 relation_change_logs，source ∈ {landing, register, backfill, admin, risk_same_device, parent_deleted}。M-内测不建、不读闭包表 user_relation_closure（计酬深度最多 2，直推与间推受益人都由 relation_change_logs 按 paid_at 两跳重放得出，BR-INV-12），P1 做关系树视图时再按需建。上级注销到达 done 状态时，其直属下级 parent_id 必须置 NULL（source=parent_deleted），下级不因此获得新的自助绑定机会；注销 cooling/processing 期间关系不变，但按 BR-INV-02 inviter_unavailable=true，其邀请码对新绑定无效；此期间生成的快照中该上级的受益资格按 BR-CALC-13 判定（BR-INV-13）。上级在冷静期撤回注销后，冷静期内已生成的快照不重算。下级注销 done 后其行匿名化，parent_id 保留用于审计，但不计入上级的直邀人数（BR-INV-16）。 | 默认假设 | users.parent_id；relation_change_logs（新表）；user_relation_closure（推迟到 P1）；注销处理任务（04 §4.5）；02 growth 模块表清单 |
| BR-INV-12 | **计酬层级最多两级**<br>每个子订单的分佣受益人最多三类：① 归属用户（自购返利或推广收益，BR-CALC-04、BR-CALC-24）；② 直推上级 = 归属用户在 paid_at 时刻的上级（BR-INV-13），直推分佣入上级的余额（流水 REFERRAL_CREDIT sub_type=DIRECT）；③ 间推上级 = 直推上级在 paid_at 时刻的上级，只在所选规则版本 indirect_enabled=true 时产生，入间推上级的余额（流水 REFERRAL_CREDIT sub_type=INDIRECT，BR-CALC-05）；单一余额，拍板第二批 §8 ADD-06。depth ≥ 3 的祖先不得出现在 commission_splits.beneficiaries，DB 约束与分账纯函数双重保证（断言受益人深度 ≤ 2）；任何层级的份额不得向更上层顺延。间推开关默认关闭，开启、关闭与比例只能按 BR-CALC-05 发布规则版本（按 paid_at 选版本、不回溯）。份额公式、比例、合计上限、取整与尾差只在 BR-CALC-04 / 05 / 06 / 07 维护，本条只约束层级。不得收取任何入门费、会员费或购买门槛，不得以付费、购买或发展人数作为取得上级资格或计酬资格的条件；各级计酬只来自受益订单的真实联盟佣金，不得以下级人数或团队业绩计酬（BR-INV-15、BR-INV-20）。BR-INV-24 的邀请奖励活动不是分佣：每个被邀请人只触发一次、只给邀请人与被邀请人本人、以被邀请人本人订单结算为条件、不随人数累进，不进分佣快照、不计入间推（负责人 2026-10-19；是否构成按人头计酬待法务书面意见，06 Q-F5）。再增加层级须新的负责人决策。 | 已确认 | commission_rules.r_indirect_bp、commission_rule_versions.indirect_enabled（BR-CALC-05）；commission_splits.beneficiaries（role 含 direct / indirect，深度 ≤ 2 断言）；packages/domain 分账纯函数；relation_change_logs 两跳回放；流水 REFERRAL_CREDIT（sub_type DIRECT / INDIRECT）；后台规则配置页（间推开关与比例）；受益人推送（BR-TEXT-09）；验收用例（算例表） |
| BR-INV-13 | **直推与间推受益人判定**<br>快照生成时点按 BR-CALC-10：子订单首次同时满足 platform_status ∈ {PAID, RECEIVED, SETTLED} 且已归因时（rebate_status R2 入库已归因，或 R3 找回 / 后台改归属；单一 order_status 写法下为 O2、O11），platform_status=DEPOSIT_PAID 时不生成；找回或改归属时 rebate_status 已为 VOID / CLAWED_BACK 的不生成（2026-10-18 起只剩后台指派未归因且已 VOID 的订单这一种情形，R3b；找回不受理 VOID，已归属订单不再改给他人，BR-ATTR-20）。直推受益人 = 归属用户在订单 paid_at 时刻的上级（BR-CALC-12；由 relation_change_logs 重放，BR-INV-11），不是快照时刻的 users.parent_id；自购单与分享单都适用（分享单的直推受益人是分享者的上级，不是下单人的上级）。(1) paid_at 时刻归属用户没有上级（含绑定前已付款的订单：paid_at &lt; parent_bound_at，含补填前付款、之后才入库或找回的订单）→ 快照不写直推受益人，该份额归平台（COMMISSION_REVENUE）；(2) 有上级时，上级在快照生成时刻与入账时刻的有效性判定（active / forfeited / held、补入账）只按 BR-CALC-13 执行，本条不另列状态；已实名未满 18 周岁上级的处理按 BR-INV-19、BR-ID-26。`inviter_unavailable`（BR-INV-02）只用于绑定校验、邀请页展示与后台改上级，不用于快照与入账判定。受益人有效性只按 BR-CALC-13（原写「分歧登记 C-30」未在 14 落号，已由拍板第二批 FUND-10、FUND-17 裁决）。间推受益人（所选规则版本 indirect_enabled=true 时）= 直推受益人在 paid_at 时刻的上级（同样由 relation_change_logs 重放）；paid_at 时刻归属用户无上级或直推上级无上级 → 不写间推受益人，份额归平台；间推受益人有效性同样只按 BR-CALC-13；间推受益人与归属用户或直推受益人为同一人（异常数据）→ 份额归平台并告警（BR-CALC-05）。快照后换绑、解绑、升降级、上级撤回注销均不重算该单。任何情况下份额不得向更上层顺延。 | 已确认 | commission_splits 生成逻辑；rebate_status 迁移 R2、R3（BR-FUND-01）；orders.paid_at、users.parent_bound_at、relation_change_logs 按时点查询；流水 REFERRAL_CREDIT；客服话术（为什么没收到邀请分佣）；验收用例（分佣算例） |
| BR-INV-14 | **等级定义与默认等级**<br>user_level 取值只有 L1、L2、L3；新账号注册时等级 = config `level.default`（默认 L1），游客报价按默认等级。等级只作为 commission_rules 的维度（平台 × 等级 × 订单类型）影响比例：r_self 取 commission_rules(platform=订单平台, level=归属用户在 paid_at 时刻的等级, order_type=订单 buy_type) 的 r_self_bp（分享单为对应分享比例；BR-CALC-06 称 r_own_bp）；r_direct 取 commission_rules(platform=订单平台, level=上级在 paid_at 时刻的等级, order_type=订单 buy_type) 的 r_direct_bp；r_indirect（间推开启时）取 commission_rules(platform=订单平台, level=间推受益人在 paid_at 时刻的等级, order_type=订单 buy_type) 的 r_indirect_bp；「paid_at 时刻的等级」= level_change_logs 中 effective_at ≤ paid_at 的最后一条的 after（等号取新等级；注册时同事务写一条 source=register、before=NULL、after=level.default、effective_at=created_at 的记录；仍缺记录时取 L1 并告警，BR-CALC-12）；各受益人等级都写入 beneficiaries.level。规则发布校验：对每个 platform × order_type，max_level(r_self_bp 或分享比例) + max_level(r_direct_bp) + max_level(r_indirect_bp) + 活动加成上限（如有，归 BR-CALC）≤ 合计上限（数值与校验只在 BR-CALC-07 维护），不满足则不能发布；分账纯函数运行时断言各受益份额之和 ≤ B，违反时不写快照并告警。levels 表每级有 status；等级禁用后不得有新升入，已在该等级的用户保持不变。MVP 只允许后台手动调整等级（step-up + 原因），每次变更写 level_change_logs(user_id, before, after, source, operator_id, reason, effective_at, created_at)，MVP 手动调级 effective_at = created_at = 操作提交时刻（+08:00）；用户端等级界面、自动晋升与保级为 P1，MVP 用户端（含「我的」页）不展示等级（拍板第二批 OPS-20）。等级变更只影响 paid_at ≥ effective_at 的订单，已有快照不重算；商品报价（quoteRebate）按当前等级实时计算。 | 已确认 | users.level；levels、level_change_logs（新表，含 effective_at；即 BR-CALC-12 所称 user_level_logs）；commission_rules 发布校验、commission_splits.beneficiaries.level；packages/domain 分账纯函数（份额和断言）；GET /v1/me（等级字段）；后台用户详情调级操作、规则配置页；BR-CALC-06 比例配置；LevelUpgrade 桥调用返回 unsupported（MVP） |
| BR-INV-15 | **等级晋升条件**<br>晋升只看本人推广订单，不得使用下级人数、团队订单或团队业绩。自动晋升（P1 启用，MVP 不运行）：每日 03:00 +08:00 计算，统计窗口 = 前 30 个完整自然日 [D−30 00:00, D 00:00) +08:00；计数对象 = 本人为归属用户的子订单（自购 + 分享），且确认收货时间 received_at 落在窗口内、计算时刻 rebate_status 不是 VOID / CLAWED_BACK（单一 order_status 写法下即不是 INVALID / CLAWED_BACK）、基数 B > 0；计数 ≥ `level.promote.l3_min_orders`（默认 50）升 L3，≥ `level.promote.l2_min_orders`（默认 10）升 L2；只升不降（保级规则 P1）；目标等级已禁用时不升入。 | 已确认 | 等级晋升定时任务（P1）；配置项 level.promote.\*；level_change_logs；等级界面文案（P1）；财务单位经济模型（高等级比例成本） |
| BR-INV-16 | **上级可见的下级信息**<br>MVP：上级只能通过 GET /v1/invites/me 看到直邀人数 direct_count = COUNT(users WHERE parent_id=本人 AND 该用户不存在 deletion_status=done 的注销单)，处于 cooling/processing 的下级、被封禁或冻结的下级仍计入，实时计算；不得返回下级列表。P1 页面 InvitedFriends：下级列表只允许包含下级昵称（经敏感词处理后的当前昵称）与注册日期（YYYY-MM-DD，+08:00），按注册时间倒序分页；不得返回或展示下级的 UID、手机号（含脱敏形式）、微信号/unionid、头像、等级、订单（任何字段）、订单数、GMV、收益、活跃状态。P1 上线前隐私政策须写明“你的昵称和注册日期将向邀请你的用户展示”。从 MVP 起必须告知被邀请人：绑定邀请人后，其订单带来的收益金额和状态变化会通知邀请人，不含商品信息；告知位置为隐私政策、用户协议与邀请落地页（细则「对被邀请人的告知」，2026-10-03；2026-10-19 起 App 内不再显示，上线前法务确认，06 Q-F4）。Agent 与客服不得向上级提供上述禁止信息。后台按角色权限可见（手机号脱敏）。 | 默认假设 | GET /v1/invites/me 响应；P1 InvitedFriends 页面与接口；Agent 工具（不得有查询下级的工具）；客服话术（上级询问下级订单）；隐私政策；验收用例 |
| BR-INV-17 | **邀请分佣流水展示**<br>上级余额流水中的 REFERRAL_CREDIT（直推 sub_type=DIRECT、间推 sub_type=INDIRECT）及受益角色为 referrer 的 CLAWBACK / SETTLE_ADJUST 分录在用户端逐条展示（单一余额，拍板第二批 §8 ADD-06）：类型名称、说明、状态用语与日期格式只按 BR-TEXT-19 字典与 BR-TEXT-01（日期精确到日，不精确到分钟，避免反推好友下单时间；间推名称「好友推广奖励」），金额按 BR-TEXT-10 带符号显示；不可跳转，不得展示下级昵称、层级、商品标题/图片、订单号、订单金额、平台、下单时间。入账前（rebate_status ∈ {ESTIMATED, WAITING}）的直推、间推分佣只以汇总金额计入「预估推广收益」（BR-TEXT-01，状态口径见 BR-FUND-01）。收益看板里的邀请分佣只给本月、上月两个金额合计，不给笔数、不按天拆（BR-FUND-25，2026-10-03）。 | 已确认 | GET /v1/wallet 流水接口字段；dict ledger_type（BR-TEXT-19）；H5 收益明细页；客服话术；验收用例 |
| BR-INV-18 | **邀请页与落地页内容**<br>GET /v1/invites/me（phone 级别，未绑手机返回 10005）：本人为已识别的未满 18 周岁用户（BR-INV-19）时返回 30413（data.reason=self_minor，客户端文案与入口隐藏按 BR-INV-19）；其余情况返回 200：{can_invite: bool, invite_code, landing_url, poster{template_id, background_url, variables}, direct_count}。当 inviter_unavailable(本人)=true（BR-INV-02）且不属于上述未成年情形时，can_invite=false，invite_code、landing_url、poster 均为 null，direct_count 照常返回；客户端 can_invite=false 时显示“暂不可邀请”，不展示原因。landing_url = `{share_domains 当前可用域名}/i/{invite_code}`，可附加渠道码参数，URL 中不得含 UID、手机号、昵称等个人信息。邀请文案模板变量只有 {nickname}、{invite_code}、{download_url}；海报 M-内测为固定模板 + 后台配置背景图，多模板 P1。后台保存邀请文案模板时必须执行 BR-INV-20 禁用词与广告法绝对化用语检查，不通过不能保存；海报背景图上线前需人工审核并留审核记录（审核人、时间、结论）。规则说明页不得出现“最高返利”“稳赚”及 BR-INV-20 禁用词。邀请落地页必须显示对被邀请人的告知句（invite.notice_inviter：订单带来的收益金额和状态会通知邀请人，不含商品信息；BR-INV-16 细则「对被邀请人的告知」，2026-10-03）；2026-10-19 起 App 内的填写邀请码页、剪贴板邀请确认与登录页待绑定码提示不再显示这一句（负责人 2026-10-19，上线前法务确认，06 Q-F4）。邀请奖励活动有效时（BR-INV-24 ⑨），邀请页显示奖励句与活动规则摘要（细则）。「我的」页邀请信息（拍板第二批 OPS-20）：显示本人邀请码（can_invite=false 或 30413 时不显示）；邀请人只显示「已绑定」或「未绑定」，GET /v1/me 只返回绑定状态，不返回、不展示邀请人的昵称、邀请码、头像或 UID；不显示等级（BR-INV-14）。 | 默认假设 | GET /v1/invites/me 响应（can_invite、30413）；InviteShare H5 页（含邀请奖励活动有效时的奖励句，BR-INV-24）；invite-landing H5 页（含对被邀请人的告知句）；App 内填写邀请码页、剪贴板邀请确认与登录页待绑定码提示不显示告知句（2026-10-19）；后台邀请文案模板（禁用词检查）与海报背景配置（审核记录）；config.share_domains；「我的」页邀请区与 GET /v1/me 邀请人状态 |
| BR-INV-19 | **未成年人邀请限制**<br>本条是未成年人邀请与分享侧效果（30401、30413、入口隐藏与提示文案）的唯一维护处。年龄、满 N 周岁时刻、「识别」时点（realname verified 时刻）与推广收益入账、识别前已入账推广收益的处理只在 BR-ID-26 维护；提现限制只在 BR-WDR-06 维护。判定时刻 = 绑定校验、邀请或分享接口请求、快照生成或入账的服务端时刻。已识别且在判定时刻未满 18 周岁的用户：inviter_unavailable=true（BR-INV-02），他人用其邀请码绑定返回 30401「邀请码无效」（不带 reason、不透露邀请人年龄）；本人调用 GET /v1/invites/me（BR-INV-18）、POST /v1/shares 及邀请码生成 / 获取接口返回 30413（data.reason=self_minor），客户端隐藏邀请与分享赚入口并提示 BR-TEXT-14 表 A 30413 行的文案（以表 A 为准；2026-10-21 按 App 内高保真第 3 批定稿 W-09 改为引用，原在此复述了一句与表 A 不同的文案）；作为上级时，快照生成时刻未满 18 周岁则不写直推受益人，份额归平台（BR-INV-13）；已生成的直推快照在入账时刻受益人已被识别为未满 18 周岁的，该份额入账时改归平台（BR-ID-26 (b)）；识别前已入账的 REFERRAL_CREDIT 留在余额中不动、不扣回、不另设冻结，未满 18 周岁期间该用户全部提现合计受 BR-WDR-06 月额度约束，满 18 周岁后不再受限（BR-ID-26 (c)，拍板第二批 FUND-10、§8 ADD-06）。提现限制见 BR-WDR-06。已有的下级关系保留，满 18 周岁时刻之后生成的快照恢复正常。未实名用户无法判断年龄，按成年处理。 | 已确认 | 实名信息（年龄推算，BR-ID-26）；BR-INV-02 inviter_unavailable；commission_splits 生成与入账；未成年提现月额度（BR-WDR-06）；GET /v1/invites/me、POST /v1/shares、邀请码生成 / 获取接口（30413）；错误码 30413（新增）；客户端邀请与分享赚入口隐藏；验收用例（含 2-29 边界、满周岁当日与次日） |
| BR-INV-20 | **分销用语与不做事项**<br>用户端、后台、接口字段、推送与客服话术不得使用“代理、运营商、总代、合伙人、团队业绩、团队奖、分红、下线”等层级或团队计酬用语，等级只称 L1/L2/L3。不得实现：付费升级或付费获得分佣资格、邀请即升级、按发展人数或团队业绩晋升、面向用户的团队业绩/出单/GMV 排行、面向用户的团队收益汇总或按下级层级分列的下级贡献展示；不得收取任何入门费、会员费或购买门槛，不得以发展人数计酬（BR-INV-12）；BR-INV-24 的邀请奖励活动只按其条件每个被邀请人发一次、只给一层，不得改为按邀请人数阶梯、累计、排名或团队发放（2026-10-19）。间推开关开启后，间推份额在余额流水与收益明细中只作为「好友推广奖励」逐笔展示（BR-INV-17，话术按 BR-TEXT 字典），不单列层级、不称「二级」「间推」；「间推」只作内部术语。文案与代码需通过禁用词 CI 检查；后台可配置文案保存时执行同一词库检查（BR-INV-18）。 | 已确认 | 全部 UI 文案与帮助中心；后台菜单命名与可配置文案；CI 禁用词检查；客服话术；规则说明页；余额流水 / 收益明细（间推份额显示） |
| BR-INV-21 | **邀请开关与配置项**<br>紧急开关 growth.invite_bind.enabled（默认 on，10 秒内生效，改动需 step-up 并告警）为 off 时：backfill 返回 30408；register 渠道照常建号但 invite_bind={failed, 30408}；landing-register 返回 30408 且不建号；后台改上级不受影响；已有关系与分佣计算不受影响；关闭期间注册的用户补填期限不顺延。/v1/config.invite 下发 required（MVP 固定 false）与 backfill_hours（默认 168），以及提醒开关 bind_phone_guide（2026-10-18 起管第三方新号登录后的绑手机整页，2026-10-19 起只在非购买触发的登录后出现，BR-INV-03 细则）；原第二个提醒开关 before_buy_tip 2026-10-19 作废（首次购买前提示取消，键保留、不再读取与下发、不复用）。邀请奖励活动的开关、金额与预算（growth.invite_reward.\*）及下发给客户端的 invite.reward_enabled、invite.reward_amount_fen 只在 BR-INV-24 维护。频控配置：invite.fail_limit_per_day=5。等级相关配置：level.default=L1、level.promote.l2_min_orders=10、level.promote.l3_min_orders=50、level.promote.window_days=30。 | 默认假设 | 配置中心 growth.invite_bind.enabled、config.invite、invite.fail_limit_per_day、level.\*；三个绑定接口；落地页暂停态 |
| BR-INV-22 | **新人红包与签到奖励仅P1（邀请奖励见 BR-INV-24）**<br>（2026-10-19 前标题为「邀请奖励仅P1」，正文首句为「MVP（M-内测、M-公开）不得发放任何新人红包、签到奖励或邀请奖励」；负责人 2026-10-19 决定邀请奖励做成可开关的活动，`docs/changes/20261019-邀请奖励与登录精简.md`）MVP（M-内测、M-公开）不得发放任何新人红包或签到奖励；邀请奖励只按 BR-INV-24 发放，不另起一套。P1（W9 起）新人奖励规则（P1 若把邀请奖励并入活动引擎，在 BR-INV-24 上改，不按本条另起）：奖励在被邀请人首单确认收货后才解锁；同设备、同支付宝、同实名各只能领 1 次；设日预算上限，预算扣减与发放同事务原子执行（条件更新 remaining_fen ≥ amount），扣不到即不发、不排队补发；手机号 HMAC 命中未过期注销留存记录（BR-ID-30 ⑩、BR-ID-28）的账号不计为有效新人（F-ACC-10）；同一 device_id 30 天内登录 ≥3 个账号的第 3 个账号起不发奖励（规划/01 E17 风控；08 尚无 BR-RISK 主题）；流水用 REWARD（sub_type=newbie、checkin；邀请奖励 sub_type=invite 见 BR-INV-24），计入 MKT_EXPENSE。“有效新人”口径见 BR-INV-23；奖励金额与预算数值在 P1 规格中定义。 | 默认假设 | 邀请奖励活动（BR-INV-24，2026-10-19 起不在本条）；活动引擎（P1）；预算表 remaining_fen（P1）；注销留存表（phone_hmac，留存见 BR-ID-30 ⑩）；流水 REWARD；风控规则；验收用例（P1） |
| BR-INV-23 | **会员口径仅P1（有效、活跃、新用户、有效新人）**<br>MVP（M-内测、M-公开）不得计算、存储、展示或使用任何会员口径标记，任何 MVP 规则不得以其为条件；首页弹窗等 MVP 人群投放只可使用请求时可直接查询的事实（是否已授权、是否有上级、有无订单），这些不属于会员口径（拍板第二批 OPS-10）。P1 启用时：每个口径只能由 packages/domain 的纯函数计算（输入 = 用户、订单与流水事实、判定时刻；参数全部读配置中心 member.\*，修改写操作日志），后台任务、活动引擎、报表共用该函数，不得在 SQL 或客户端另写一版；每个口径附决策表 fixture，至少 3 条，覆盖边界值（2/3 笔、窗口首尾时刻）。默认口径（取值依据见私有材料）：① 有效用户 = login_logs 中存在首条 App 登录成功记录起永久有效。② 活跃用户：每日 00:10 +08:00 重算；窗口 = [D−member.active_days 00:00, D 00:00) +08:00（默认 30 个完整自然日，D 为重算当日）；计数 = 本人为归属用户的子订单（自购 + 分享）中 paid_at 落在窗口内、且重算时刻 platform_status ∈ {PAID, RECEIVED, SETTLED}、rebate_status ∉ {VOID, CLAWED_BACK} 的笔数；≥ member.active_orders（默认 3）即活跃；不得含邀请人数、下级人数或团队业绩条件（BR-INV-15、BR-INV-20）。③ 新用户 = 本人为归属用户、platform_status 曾到达 PAID 或之后状态的子订单数 = 0；首次跟单即去标，订单之后失效也不恢复。④ 有效新人（P1 新人奖励与「有效邀请」计数共用；BR-INV-24 邀请奖励活动不用本口径，只按其触发时可直接查询的订单事实判定，2026-10-19）= 被邀请人 parent_bind_source ∈ {landing, register, backfill}（后台改上级不计）、已绑手机、首笔 platform_status 到达 RECEIVED 的子订单实付金额（分）≥ member.valid_newcomer_min_paid_fen，且不命中 BR-INV-22 的排除条件；该门槛由财务在 P1 规格给出，给出前有效新人判定不得启用。「首提」「当日入账」「冻结中」属提现主题（BR-WDR-19、BR-WDR-27），本条不定义。 | 已确认 | packages/domain 会员口径纯函数与决策表 fixture（P1）；配置 member.active_days、member.active_orders、member.valid_newcomer_min_paid_fen；每日 00:10 重算任务（P1）；活动引擎与邀请奖励（P1，BR-INV-22）；BR-WDR-19 手续费矩阵活跃度维度（P1）；后台会员查询筛选（P1） |
| BR-INV-24 | **邀请奖励活动（双方各得，可开关）**<br>（负责人 2026-10-19 决定「做，做成可开关的活动」，`docs/changes/20261019-邀请奖励与登录精简.md`）① 开关与资格：活动开关 growth.invite_reward.enabled 默认 off，法务书面意见（06 Q-F5）与奖励所得的税务结论（06 Q-F6）到位后由运营打开（step-up）；「活动有效」= 开关 on 且总预算可用额（总预算 − 已占用 − 已发放）≥ 两方金额之和。被邀请人经 landing、register、backfill 渠道绑定成功时活动有效，才在绑定的同一事务内写一条资格记录（每个被邀请人至多一条），锁定邀请人与当时的每方金额 growth.invite_reward.amount_fen（默认 1000 分），同一事务内按两方金额之和占用总预算（条件更新，可用额不够则不取得资格），并记下绑定请求的客户端 IP（只存 HMAC）；后台改上级（admin）不取得资格；取得资格后关闭开关或改金额都不影响已有资格。② 触发与发放时点：被邀请人本人自购（buy_type=self）子订单中第一笔 rebate_status 迁移到 CREDITED（确认收货后随月结入账，BR-FUND-01、BR-FUND-04）、基数 B > 0 且实付金额 ≥ growth.invite_reward.min_paid_fen（默认 0）的，触发一次（不满足这两项的入账单跳过、不使资格作废）；发放在该迁移提交之后进行，是独立凭证、不随订单迁移（BR-FUND-01）；邀请人与被邀请人各入余额一笔 REWARD（sub_type=invite），金额取资格记录的锁定值；以被邀请人为幂等键，每个被邀请人只触发一次。③ 防刷（发放时判定，命中即不发、不补发，记原因）：双方都不发——两人的设备集合（BR-INV-08 ③ 口径）或被邀请人绑定时的 IP 与邀请人在绑定前 growth.invite_reward.ip_window_hours（默认 24）小时内的登录 IP 相同（login_logs.ip，网关识别出的客户端 IP，口径同 BR-ID-05 细则；IP 只作辅助，主要靠设备判定），或被邀请人手机号 HMAC 命中未过期的注销留存记录（BR-ID-28、BR-ID-06），或发放时被邀请人的上级已不是资格记录里的邀请人（资格作废）；只该方不发、另一方照发——该方被 BR-ID-37 标为同设备多账号、risk_state ∈ {banned, appealing, frozen}、处于注销流程（cooling、processing、done）或为已识别未满 18 周岁（BR-ID-26）。④ 预算：总预算 growth.invite_reward.total_budget_fen 在取得资格时按两方金额之和占用（①），资格作废或某方判为不发时释放对应金额，发放时由占用转为已发放——所以已取得资格的都发得出；每日预算 growth.invite_reward.daily_budget_fen（+08:00 自然日）只计当日实际发放的金额，与发放同事务原子扣减（条件更新，做法同 BR-INV-22），当日不够 → 顺延，次日起按触发先后补发。紧急情况打开暂停发放开关 growth.invite_reward.payout_paused（紧急开关表，默认 off）：暂停期间触发的一律顺延，恢复后补发，不作废。两个预算默认 0（未填），为 0 时不能打开活动开关。⑤ 与分佣的关系：独立于订单分佣——不进 commission_splits、不改基数 B 与任何份额，不按下级人数累进或滚动，不计入间推（邀请人的上级不得任何奖励），不计入等级晋升（BR-INV-12、15、20）。⑥ 扣回：已发放的不追回；触发之后、发放之前（含顺延期间）触发订单被扣回（CLAWED_BACK，含部分退款扣回）或进入维权的，未发放的不再发放，该被邀请人的奖励作废、不再因之后的订单触发（负责人 2026-10-19 给的默认方向，细节为代理补全，待确认）。⑦ 账务：用户侧入单一余额（BR-FUND-13），可提现口径按现有余额与提现规则；平台侧记营销费用科目 MKT_EXPENSE（规划/02 §8.2）；流水类型与凭证约束按 BR-FUND-15、BR-FUND-16，具体分录由资金线在账务模板里补，本条不写分录。⑧ 税务：奖励属于哪类所得、是否需要代扣待确认（06 Q-F6），本条不臆定。⑨ 展示：/v1/config.invite 下发 reward_enabled（= 活动有效）与 reward_amount_fen；为 true 时登录页待绑定码提示旁与邀请落地页 /i/{code}（协议勾选框上方）显示 invite.reward.tip，邀请页显示 invite.reward.tip_inviter（BR-TEXT-14 表 C），邀请页规则摘要换成活动规则（BR-INV-18 细则）；流水名称按 BR-TEXT-19。会员口径（BR-INV-23）不用于本条。 | 默认假设 | 配置 growth.invite_reward.enabled（紧急开关表，默认 off）、growth.invite_reward.amount_fen、daily_budget_fen、total_budget_fen、min_paid_fen、ip_window_hours；紧急开关 growth.invite_reward.payout_paused（默认 off）；/v1/config.invite.reward_enabled、reward_amount_fen；资格与发放记录 invite_rewards（新表）；绑定事务（landing、register、backfill）；订单迁移到 CREDITED 后的发放任务；流水 REWARD（sub_type=invite）与平台科目 MKT_EXPENSE；BR-ID-37 判定；登录页与落地页展示（invite.reward.tip）、邀请页展示（invite.reward.tip_inviter）；后台活动配置与发放记录；06 Q-F5、Q-F6；验收用例 AC-S2-112 |

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
- 码号归属（C-03）：30408、30409 只表示本表含义。BR-ID-25 原用的 30408（今日实名次数用完）改为 30410；BR-ID-26 原用的 30409 拆为：他人用未满 18 周岁用户的码绑定 → 按 inviter_unavailable 返回 30401（不带 reason、不透露年龄），未满 18 周岁本人调用邀请、分享接口 → 30413（data.reason=self_minor）。码号以 规划/04 §7 为准。按 C-03 默认处理，代理自定（00 §9）。

#### BR-INV-03 细则 · 绑定渠道与先到先得

- 状态：已确认（拍板第二批 OPS-25：维持先到先得；原为待决策，属订单归属口径）
- 默认值：三渠道；将 01 的优先级解释为时间先后、先成功者锁定；失败不消耗机会；理由：落地页在服务端完成绑定，按时间先后不需要跨渠道比较，也不会出现后到渠道改写已有关系
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - PRD修订_后端功能规划 §2.10 绑定上级：「优先级第②项“首次启动识别剪贴板邀请口令”」（2026-09-30 起剪贴板邀请口令自动识别进 MVP，见 BR-INV-04；识别结果经 register / backfill 渠道绑定，不单列渠道与优先级）
- 来源：规划/01 §5 J7、E12 F-INV-02；规划/04 §6.1、§6.4；规划/02 Agent 工具白名单；docs/changes/20261001-拍板第二批.md（OPS-25）；PRD修订_后端功能规划 §2.10
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 将 01 F-INV-02 的“优先级 落地页 > 注册页 > 补填”解释为**时间先后**：落地页注册时已绑定，之后用同一手机号在 App 登录携带 invite_code 会被忽略；注册页绑定成功后补填入口返回 30402。
- 失败的尝试不消耗机会；只有写库成功才置 `self_bind_used=true`。
- 微信 / Apple / 华为登录新建的账号没有邀请码输入框，需先绑手机，再在补填期限内走 backfill（华为账号一键登录取得手机号，按手机号登录处理，不属此列，2026-10-18）。
- 例：用户 U 在 10-01 10:00 经落地页注册（parent=A），10-01 10:05 在 App 用同号登录并带 invite_code=B 的码 → 登录成功，parent 仍为 A，`invite_bind.result=ignored_existing_user`。
- 并发：同一用户两个请求同时补填不同码，只有一条条件更新成功，另一条返回 30402。
- 第三方登录新号并入老账号（拍板第二批 OPS-04，规则见 BR-ID）只允许新号无订单、余额与上下级，合并不产生或改变任何邀请关系，老账号已有的上级与 self_bind_used 照旧。

**第三方登录新号的两处提醒**（2026-10-03，功能对照 G-05；按功能对照 Q-01 默认 C「维持现状，只加提醒」写，负责人 2026-10-06 确认。绑定渠道、先到先得与补填条件都不变；docs/changes/20261003-功能对照补缺.md。2026-10-19 起只剩 ①，且只在非购买触发的登录后出现；② 与「两处不连着出现」作废，见下文「购买触发的登录」，`docs/changes/20261019-邀请奖励与登录精简.md`）：

- 背景：微信 / Apple / 华为登录新建的账号没有邀请码输入框，只能先绑手机再补填（上文）；而未绑手机也能购买（BR-ID-02），一旦有了订单，补填（BR-INV-07 (c)）与并入原账号（BR-ID-06）都不再可行。
- ① 绑手机引导：第三方登录接口返回 `is_new_user=true`（规划/04 §6.1）、且这次登录不是由点击购买触发（不存在待恢复的购买 pending_action，BR-ID-10；2026-10-19 加）时，登录成功后进入一次整页的「绑定手机号」（`BindPhone`，顶部说明用 BR-TEXT-14 invite.bind_phone_guide，右上【跳过】；负责人 2026-10-18 由弹窗改为整页，`docs/changes/20261018-登录注册改版.md`）。说明写两点：绑定手机号的好处（提现、找回账号）；已用手机号注册过的（含在邀请页注册），绑定同一个手机号、符合条件时可并入原账号（BR-ID-06）。绑定成功后接「填写邀请码」页（下文「登录成功后的新号步骤」）。每个账号只在建号的那次登录后出现一次（建号那次登录由购买触发的，之后不再补出）；短信与一键登录的新号已绑手机，不出现。
- ② 首次购买前提示：**作废**（负责人 2026-10-19：购买不再触发插页）。键与记录保留、不复用：开关 `invite.before_buy_tip` 不再读取与下发，tips 键 `inviter_before_buy` 不再写入与读取（规划/04 §3.2、§6.1），文案键 invite.before_buy_tip 保留不用（BR-TEXT-14 表 C）。原写法如下，只作记录：账号仍可补填邀请码（`GET /v1/me` 的 invite_backfill.eligible=true：未绑上级、未用过自助绑定、在补填期限内，没有订单、找回申请与下级，且绑定开关打开；与 BR-INV-07 (a)(b)(c) 同一口径，未绑手机的账号同样计算）且从未展示过本提示时，用户点击购买后、发起 open 之前提示一次（BR-TEXT-14 invite.before_buy_tip）。按钮【先填邀请码】（已绑手机进补填页；未绑手机先进 BindPhone，绑定后进补填页）【继续购买】（继续本次 open）。服务端记已读（tip_key=inviter_before_buy，规划/04 §6.1 的 tips 接口），每个账号一次，换设备不重复。
- 两处不连着出现：**作废**（2026-10-19，由下文「购买触发的登录」取代；购买版文案键 invite.bind_phone_guide.before_buy_warn、invite.post_login.skip_before_buy、invite.post_login.before_buy_hint 保留不用，BR-TEXT-14 表 C）。原写法如下，只作记录：登录是由点击购买触发的（存在待恢复的购买 pending_action，BR-ID-10）时，只出 ①，用带下单提醒的那版（多显示警告条 invite.bind_phone_guide.before_buy_warn，BR-TEXT-14 表 C；2026-10-18 由原 .body_before_buy 拆键，文字不变），同时把 ② 记为已读；用户点【跳过】或完成绑定（及之后的「填写邀请码」页）后继续执行 pending_action。引导停留不算 pending_action 的前置步骤，不重置其计时，超时按 BR-ID-10 丢弃。
- **购买触发的登录**（负责人 2026-10-19「推荐」选项，`docs/changes/20261019-邀请奖励与登录精简.md`）：登录由点击购买触发（存在待恢复的购买 pending_action，BR-ID-10）时，不论是否新号、用哪种方式登录，登录成功后直接按 BR-ID-10 继续执行 pending_action：不出「绑定手机号」整页，不出「填写邀请码」页，也没有任何下单前提示。随登录请求带上的待绑定码照常在建号时绑定（BR-INV-06）：绑定成功照常轻提示 invite.bound_toast，失败只用 invite.auto_bind_failed 轻提示原因、不出页面，之后在期限内仍可在「我的」补填（BR-INV-07）。代价（负责人已知并接受）：第三方登录的新号先下单后，就不能再补填邀请码（BR-INV-07 (c)），也不能并入原手机号账号（BR-ID-06）；这两条规则本身不变。
- 开关：/v1/config.invite.bind_phone_guide（默认 on，BR-INV-21）；关闭后不出（第三方新号登录后直接回来源页），不影响任何绑定规则。原开关 invite.before_buy_tip 2026-10-19 作废。
- 绑手机引导不自动提交任何绑定，不改变「先到先得」「phone 级别才能绑定」「有订单不能补填」。
- 待负责人二选一（功能对照 Q-01 的 A、B，确认前不做）：A 第三方新号建号时就允许填邀请码（放宽「绑定须 phone 级别」）；B 补填期限改从绑定手机时起算。
- 例：用户先在邀请落地页用手机号 P 注册（上级 X），之后在 App 里点微信登录 → 新建账号 U（is_new_user=true）→ 进入绑定手机号页 → 输入 P → 30411（mergeable）→ 确认并入 → 以落地页注册的账号登录，上级仍是 X（BR-ID-06）。
- 例：U 在绑定手机号页点了【跳过】，第二天点【领券购买】→ 直接 open，不出任何提示（2026-10-19 起；原例「弹『下单后将不能再填写邀请码』→【继续购买】」作废）。
- 例（2026-10-19）：游客 G 在详情页点【领券购买】→ 登录页用微信登录、新建账号 → 不出绑定手机号页与填写邀请码页，直接继续本次购买；该单入库后 G 不能再补填邀请码，也不能把这个微信号并入之前用手机号注册的账号。

**登录成功后的新号步骤**（负责人 2026-10-18 对登录注册审稿报告第 6 节第 3 项「按推荐」，`docs/changes/20261018-登录注册改版.md`；只改在哪个页面填写，绑定渠道、先到先得、须已绑手机、补填期限与条件的取值都不变；2026-10-19 起由点击购买触发的登录不走本段，见上文「购买触发的登录」）：

- 出现条件：本次登录响应 `is_new_user=true`、这次登录不是由点击购买触发（2026-10-19 加），且账号仍可补填（`GET /v1/me` 的 invite_backfill.eligible=true，口径见 BR-INV-07 细则：未绑上级、未用过自助绑定、在补填期限内，没有订单、找回申请与下级，且绑定开关打开）。老账号、已有上级或已用过自助绑定的账号永远不出现；每个账号只在建号的那次登录后出现一次，跳过后不再自动出现，之后仍可在「我的」补填（BR-INV-07）。
- 已知邀请码随登录请求绑定成功（`invite_bind.result=bound`，BR-INV-06）：不出页面，轻提示「已绑定邀请人」（BR-TEXT-14 表 C invite.bound_toast）后回来源页。
- 随登录请求绑定失败（`invite_bind.result=failed`）：失败告知与是否出页面分开判断。账号仍可补填（eligible=true，如 30401、30403、42901、50001）→ 进入「填写邀请码」页，顶部说明刚才的邀请码未生效及原因（invite.auto_bind_failed，原因取 BR-INV-02 的码对应文案），用户可改填或跳过，42901 时【确认绑定】按 Retry-After 置灰；账号已不可补填（eligible=false，如绑定开关关闭返回 30408）→ 不出页面，用同一键轻提示原因后回来源页。
- 有手机号的新号（短信、运营商一键、华为账号一键登录）且没有带已知邀请码：进入「填写邀请码」页（标明选填）。
- 第三方登录（微信、Apple、华为普通授权）的新号：先进入上文 ① 的「绑定手机号」整页；绑定成功后（账号仍可补填时）进入「填写邀请码」页（游客时期的待绑定码预填进输入框，由用户点提交，不自动提交，BR-INV-04）；号码属老账号且满足并号条件时按 BR-ID-06 确认并号，以老账号回来源页，不出「填写邀请码」页；跳过绑手机则回来源页（2026-10-19 起不再有首次购买前提示）。
- 「填写邀请码」页是现有补填页加登录来源参数：走 backfill（`POST /v1/me/inviter`，按 BR-INV-02、BR-INV-07 校验），source 记 backfill，不新增渠道值与接口。页面内容（负责人 2026-10-19 精简，「我的」补填入口与登录来源共用）只有：标题、邀请码输入框与【粘贴】（用户点击才读剪贴板，BR-INV-04）、一行选填说明（BR-TEXT-14 表 C invite.post_login.optional_hint，只在登录来源显示）、【跳过】（只在登录来源）与【确认绑定】；不显示对被邀请人的告知句（BR-INV-16 细则）、补填截止时间与规则说明行——规则本身不变（BR-INV-07），截止时刻 `invite_backfill.deadline_at` 仍下发，只供客户端判断入口显隐。成功时轻提示 invite.bound_toast 后回来源页；失败在输入框下方就地显示原因，可改填或跳过；随登录带的码失败时顶部的 invite.auto_bind_failed 说明照旧。
- 登录由点击购买触发时：**作废**（2026-10-19，购买触发的登录不出本页，见上文「购买触发的登录」）；原写法「跳过按钮写『跳过，继续购买』并提示下单后不能再填写（invite.post_login.skip_before_buy、.before_buy_hint），同时把 ② 记为已读」只作记录，两个键保留不用。
- 页面停留不算 pending_action 的前置步骤，不重置其计时，超时按 BR-ID-10 丢弃（同上文 ①）。
- 都不自动提交绑定：只有随登录请求带上的待绑定码（来源只按 BR-INV-04 细则「邀请码的来源」，都是用户主动确认或点开的）会在建号时绑定，其余都要用户在页内点【确认绑定】。
- 例：游客 G 点了剪贴板提示条的【绑定】（待绑定码 K7M2QX），之后点【领券购买】→ 登录页显示待绑定码提示（BR-TEXT-14 login.pending_invite；2026-10-19 起旁边不显示告知句，邀请奖励活动有效时显示 invite.reward.tip）→ 短信登录新建账号 → invite_bind=bound → 轻提示「已绑定邀请人」→ 继续购买。
- 例（2026-10-19）：游客 H 没有待绑定码，点【领券购买】→ 短信登录新建账号 → 不出填写邀请码页，直接继续购买；H 在补填期限内、订单入库前仍可在「我的」补填。
- 例：新号 N 用运营商一键登录，未带邀请码 → 「填写邀请码」页 → 点【跳过】→ 回来源页；第二天在「我的」仍可补填，期限从账号创建时起算（BR-INV-07）。
- 例：老账号 O 重新登录 → 不出页面。

#### BR-INV-04 细则 · 剪贴板邀请口令自动识别（MVP）

- 状态：已确认（负责人 2026-09-30，依据 docs/changes/20260930-拍板第一批.md §3 BR-INV-04：「要自动识别，很重要，需要监听剪贴板；根据规则来，必须要做」；商品优先与触发前提由拍板第二批 OPS-06 确认）
- 默认值：MVP 做自动识别；读取前提、时机与提示方式按 BR-ID-16；只对可绑定用户触发；识别后提示条 + 用户点击确认才绑定，不自动提交；抽取正则与 NFKC 规则不变；与商品口令同时出现时商品优先，触发前提为含落地页链接或「邀请码」字样（拍板第二批 OPS-06）
- 决策人：负责人（剪贴板读取方式的合规口径由 BR-ID-16 维护，决策人法务）
- 依赖平台能力：iOS 开启功能后程序化读取的系统弹窗行为与 UIPasteControl 降级（CAP-X-02，2026-10-17 改版）；华为：返利与口令识别场景能否申请读取剪贴板权限（06 Q-G11，同 BR-ID-16；规划只写「具备资格时」）
- 取代：
  - PRD修订_后端功能规划 §2.10：「② 首次启动识别剪贴板邀请口令（用户点击触发读取）」
  - 本条旧写法（2026-09-30 前）：「剪贴板邀请口令不进MVP：MVP 不得在 App 启动时自动识别剪贴板中的邀请码/邀请口令用于绑定，仅提供用户点击的“粘贴”按钮；理由：落地页已覆盖锁粉，自动读剪贴板有隐私审核风险」
- 来源：PRD修订_后端功能规划 §2.10；规划/03 剪贴板实现要点、§5.3 L2；规划/01 E12 F-INV-02；08 BR-ID-16；docs/changes/20260930-拍板第一批.md §3（BR-INV-04 行）；docs/changes/20261001-拍板第二批.md（OPS-06）

- 绑定渠道不新增：自动识别只是把邀请码交给现有渠道，已登录走 backfill、游客走 register，source 仍只取 BR-INV-03 的三个值；先到先得、30402 等语义不变（落地页已绑定的用户按 ③ 不会被提示）。
- 触发对象判定在客户端用 GET /v1/me 的邀请人状态与 /v1/config.invite.backfill_hours 做预判，服务端以 BR-INV-02 / BR-INV-07 校验为准；客户端预判错误时照常返回 30402 / 30404 / 30409，客户端按 BR-TEXT-14 提示。
- 已登录用户的预判可直接取 `GET /v1/me` 的 invite_backfill.eligible（服务端按 BR-INV-07 (a)(b)(c) 算好，BR-INV-07 细则；2026-10-03，功能对照 G-05），不必在客户端重算期限；第三方登录新号的绑手机引导见 BR-INV-03 细则（首次购买前提示 2026-10-19 作废），与本条的提示条互不替代。
- 已登录但未绑手机（member）：点击提示条先引导绑手机（10005），绑定成功后再以同一邀请码调用 backfill；不在未绑手机时静默缓存后自动提交。
- 游客的待绑定码（2026-10-18 前叫「预填的邀请码」；来源是剪贴板提示条或邀请链接，后者见下文「邀请链接拉起 App」）只保存在本机内存 / 本地存储、不上传，用户未提交登录即丢弃；有效期默认本次进程生命周期（已确认：2026-10-06 代理按 规划/11 §7.1 用 Jev 判断，置信度 0.88）。登录页上点「移除」即丢弃；随登录请求提交后不论绑定结果都清除。第三方登录接口不收邀请码：第三方新号绑定手机后，待绑定码预填进「填写邀请码」页，由用户点提交（BR-INV-03 细则「登录成功后的新号步骤」，2026-10-18）。
- 与商品识别的关系（拍板第二批 OPS-06 确认）：同一段剪贴板文本若按 BR-ID-16 的本地过滤规则与 F-CLIP-03 命中商品链接或口令，只弹商品卡（2026-10-17 改版，不再出 clipboard.prompt 提示条），不再出邀请提示条；只有未命中商品规则、且本条抽取正则命中时才出邀请提示条。为降低普通文本误判，默认另加触发前提：文本含分享域名（config.share_domains）的落地页路径 `/i/{code}`，或含「邀请码」字样；该前提作为 /v1/config.clipboard 的可配置规则下发（拍板第二批 OPS-06 确认）。
- iOS 与鸿蒙的限制（2026-10-17 随 BR-ID-16 改版改写）：功能开启且系统允许读取时，三端都在本机对全文抽取，纯邀请码文本（不含链接）也能命中并出邀请提示条；iOS 系统拒绝、鸿蒙不具备资格或未授权时只能经粘贴入口读取，填写邀请码页的「粘贴」按钮兜底。原写法「iOS detectPatterns 只能探测链接……纯邀请码能否自动提示待 CAP-X-02 验证」作废。
- 例：游客从微信复制好友邀请文案「… 邀请码 K7M2QX … https://{share_domain}/i/K7M2QX」，同意隐私政策、开启剪贴板自动识别后回到前台 → iOS 经系统允许读取并在本机抽取 `K7M2QX` → 出邀请提示条 → 用户点提示条确认 → 记为待绑定码（不跳登录）→ 之后用户进入登录页，看到待绑定码提示（login.pending_invite）→ 登录新建账号时随请求按 register 渠道绑定（2026-10-18 改）。
- 例：已登录、无上级、注册第 2 天的用户回到前台（Android 已开自动识别开关）→ 本地抽取 `K7M2QX` → 出邀请提示条 → 用户点「绑定」→ POST /v1/me/inviter → 服务端按 BR-INV-02 / BR-INV-07 校验。
- 例：已有上级的用户复制同样文案回到前台 → 不识别、不提示。
- 例：用户在本 App 邀请页复制自己的邀请文案后切回 → App 自写内容按 hash 排除，不提示。
- 例：用户从微信复制“邀请码 K7M2QX”，在填写邀请码页点“粘贴”→ 抽取 `K7M2QX` 填入 → 用户点提交 → 服务端校验。
- 例：剪贴板为“￥AB12CD￥ 邀请码 K7M2QX”→ 取第一个匹配。`AB12CD` 含 1 不匹配，因此填入 `K7M2QX`。
- 例：剪贴板为商品链接、无 6 位候选 → 粘贴按钮不填入，提示“未识别到邀请码”；自动识别按 BR-ID-16 直接弹商品卡。
- 邀请码的来源（2026-10-03，功能对照 G-39；「不做免填邀请码」按功能对照 Q-16 默认 A 写，负责人 2026-10-06 确认）：填进 App 内邀请码输入框、或交给绑定接口的邀请码，只能来自用户自己提供的内容——用户点击确认的剪贴板邀请提示条（本条）、用户手动输入或点「粘贴」读到的文本；邀请落地页注册时的邀请码取自用户打开的那条邀请链接本身（BR-INV-05）；用户在已安装本 App 的设备上点开邀请链接、由系统直接拉起 App 时，链接本身带的邀请码同样算用户提供的内容（2026-10-18，负责人按审稿报告「邀请链接带来的码随登录带上」一并批准，见下一项「邀请链接拉起 App」）。不得用设备指纹或浏览器指纹（IP、UA、屏幕、字体、画布等特征的组合）、延迟深链或安装归因 SDK 推断、匹配或预填邀请码，也不因此自动绑定。不做的原因与改选时的条件见 BR-INV-20 细则「不做免填邀请码」。
- 邀请链接拉起 App（2026-10-18，`docs/changes/20261018-登录注册改版.md`；分流方式是代理补全的默认）：
  - 入口：邀请落地页上的【在 App 中打开】（BR-INV-18 细则），经 `l.` 子域的通用链接、App Links 或 App Linking 拉起已安装的 App（做法同分享中间页，规划/02 §3.4、01 F-SHARE-07），路由 `InviteLink` 只带邀请码一个参数（BR-ID-10 细则路由入口矩阵）；链接的具体路径由契约线定。没装 App 时不跳转、不做延迟深链与安装归因（BR-INV-20 不变），用户在落地页注册即走 landing（BR-INV-05）。
  - 照常先过统一入口守卫（BR-ID-10、规划/03 §4.4）：基本模式或未同意当前隐私政策时丢弃，不弹登录；码按本条抽取规则校验格式，不符即丢弃，等于本人邀请码时丢弃。
  - 游客：记为待绑定码（替换之前的待绑定码），打开 `Login` 并显示待绑定码提示，由用户自己登录；随登录请求带上，新建账号时走 register（BR-INV-06），老账号登录照常忽略。
  - 已登录且可补填（invite_backfill.eligible=true）：打开 `InviteBackfill` 并预填，由用户点【确认绑定】走 backfill（BR-INV-07）；已登录但不可补填：打开 `Home`，不提示。
  - 都不自动提交绑定；用户在落地页已看到对被邀请人的告知句（BR-INV-18）；登录页的待绑定码提示旁 2026-10-19 起不再显示告知句（BR-INV-16 细则），邀请奖励活动有效时显示奖励句（BR-INV-24 ⑨）。
- 需同步修改的规划文档（2026-09-30）：规划/01 E12 F-INV-02 补剪贴板邀请口令自动识别（经 register / backfill 渠道）与验收要点；规划/01 E06 F-CLIP-01 / F-CLIP-02 补邀请口令用途与触发前提；规划/03 §4.6 ClipboardWatcher 增加邀请口令识别与邀请提示条；规划/00 §4 范围裁决表「剪贴板」行补邀请口令识别；规划/04 /v1/config.clipboard 增加邀请口令触发规则；08 BR-TEXT-14 字典登记邀请提示条文案键；规划/10 增加邀请口令自动识别用例（三端各一，含已有上级不提示、App 自写不提示）；隐私政策（06 Q-F1）剪贴板用途补「识别邀请码」
- 扫码填邀请码（2026-10-03，功能对照 G-78；登记为 P1：按功能对照 Q-25 默认 A，正式版第一版不申请相机权限，扫码随 P1 的 `media.scan` 与相机权限一起做）：P1 在填写邀请码页的邀请码输入框旁加【扫码】（2026-10-18 起登录页不再有邀请码输入框），用系统扫码能力扫邀请海报上的二维码；在本机只解析分享域名下的邀请落地页路径（`/i/{invite_code}`，BR-INV-18），按本条的抽取规则取出邀请码后只预填进输入框，由用户点提交，不自动绑定；其他内容的二维码不处理、不打开。相机权限按 BR-ID-13 与权限组件申请，立项时加进权限清单与隐私政策收集清单（规划/06 Q-F1）。MVP 期间用户可以用手机自带的相机或微信扫海报二维码进入邀请落地页注册，或在输入框旁点【粘贴】。

#### BR-INV-05 细则 · 落地页注册绑定

- 状态：默认假设
- 默认值：发码限流与同 IP 注册上限取 BR-ID-32（本条只定其在校验顺序中的位置）；已注册（含注销中）手机号不改关系；已 done 注销的手机号视为新号；邀请码无效不建号且不核销短信码；已注册判定在短信码之后；协议勾选必填
- 决策人：代理可自定
- 依赖平台能力：无
- 取代：
  - 本条旧写法：「landing-register 入参带 captcha_token 每次校验；IP 限流阈值见 BR-RISK，超限 42901；registered_channel=invite_landing；consent channel=invite_landing」（与 BR-ID-32 两套接口与阈值，按 BR-ID-32 合并：发码接口、人机验证、IP 注册上限与 consent channel 取 BR-ID-32 / BR-ID-04，绑定语义与校验顺序保留本条）
- 来源：规划/01 §5 J7 步骤 2、E12 F-INV-02、F-ACC-10、F-PRIV-01、F-PRIV-05；规划/04 §3.2 users、consent_records；§6.4；§7 10004、42901；规划/03 H5 landing；PRD修订_后端功能规划 §2.1 注册来源、§2.12 同 IP 注册；08 BR-ID-04、BR-ID-05、BR-ID-32
- 需同步修改的规划文档：2 处（计数仅作记录，落点见 README §0.6）

- 流程：好友微信内打开 `{share_domain}/i/K7M2QX` → 勾选协议 → 输入手机号 → 发码（landing/sms-codes）→ 输入验证码提交（landing-register）→ 注册并绑定 → 引导下载 → App 内同号登录，`GET /v1/me` 可见已有上级（本人只看到“已绑定”，BR-INV-18）。
- 落地页发码限流、同 IP 注册上限的计数口径、窗口边界与例子只在 BR-ID-32 维护，本条不重复；同设备注册上限（BR-ID-05）不适用于落地页（不采集设备，改由 BR-INV-09 首次 App 登录时复核）。
- 例：13800000000 首次注册，邀请人 A 正常 → 创建 U，U.parent_id=A；同一号码再次提交且短信码正确 → `already_registered`，不改 U。
- 例：手机号已注册但邀请码无效 → 30401（邀请码校验在前），短信码不核销，不暴露手机号是否注册。
- 例：该号 2026-06 注销并已 done，2026-10 在落地页注册 → 按新号建号并绑定；新号不能领新人奖励（F-ACC-10，BR-INV-22）。
- 页面提示：already_registered →“该手机号已注册，请打开 App；符合条件可在 App 内补填邀请码”；30408 →“邀请活动暂停，可直接下载 App 注册”，不创建账号；44001 →“注册人数过多，请稍后再试或下载 App 注册”。
- 注销 done 时 users.phone_hmac 移入注销留存表（deleted_identities；留存见 BR-ID-30 ⑩、BR-ID-28，用于防重复领奖），不再占用 users 的唯一约束；该处理归注销主题，此处只写依赖。
- 落地页提交的手机号先按 BR-ID-05 细则「手机号规范化」处理，再发码、判定「已注册」与建号；规范化不通过返回 20001，不发短信（2026-10-03，功能对照 G-19）。

#### BR-INV-06 细则 · 登录请求携带邀请码

- 状态：默认假设
- 默认值：SAVEPOINT 内绑定；绑定失败不阻止注册；老用户忽略邀请码；仅携带非空码时返回 invite_bind
- 决策人：代理可自定
- 依赖平台能力：无
- 取代：无
- 来源：规划/04 §6.1、§7、§10.1；规划/01 E12 F-INV-02
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 客户端对 result=failed 不再弹窗：账号仍可补填时进入登录后的「填写邀请码」页，顶部说明刚才的邀请码未生效及原因（BR-TEXT-14 表 C invite.auto_bind_failed），用户可改填或跳过；不可补填时（如 30408）只轻提示原因后回来源页（BR-INV-03 细则「登录成功后的新号步骤」）；42901 的提示取 BR-TEXT-14 表 A 42901 行（以表 A 为准，2026-10-21 按 App 内高保真第 3 批定稿 W-09 改为引用，原在此复述了一句与表 A 不同的文案）（2026-10-18，BR-INV-03 细则「登录成功后的新号步骤」；原写「弹出“邀请码未生效：{原因}，注册 7 天内可在“我的”补填”」）。
- 取代：本条 2026-10-18 前写法「App 注册页填写邀请码」（登录页的邀请码输入框取消，负责人 2026-10-18）。
- 例：新号注册携带自己同设备另一账号 A 的码 → 账号创建成功，invite_bind={failed, 30403}，self_bind_used 仍为 false，可在期限内用其他人的码补填。
- 例：老用户登录携带任意码 → invite_bind.result=ignored_existing_user。
- 例：invite_code 为全角空格 → 视为未携带，响应无 invite_bind。
- 例：绑定写库时数据库异常 → 回滚到 savepoint，账号创建成功，invite_bind={failed, 50001}，告警。

#### BR-INV-07 细则 · 补填条件与期限

- 状态：已确认（负责人 2026-09-30，依据 docs/changes/20260930-拍板第一批.md §2）
- 默认值：168 小时（不含边界）；无订单（含失效）、无任何找回申请、无下级；成功 1 次；01 的“7 天、无订单、无下级”已定，精确边界与订单/找回口径为代理细化；理由：失效单与找回申请也计入，防止先下单再挑上级
- 负责人备注（2026-09-30，变更记录 §2 注 ²）：「有订单就不能补邀请码」，与条件 (c)（本人为归属用户的订单数 = 0，含已失效订单）一致，规则不变
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
- 登录后新号的「填写邀请码」页（2026-10-18，BR-INV-03 细则「登录成功后的新号步骤」）走本条同一接口与校验，source=backfill；新号刚建、没有订单与下级，天然满足 (a)(b)(c)，本条条件与期限不变。
- `GET /v1/me` 的 invite_backfill{eligible, deadline_at} 由服务端按本条 (a)(b)(c) 计算（未绑手机的账号同样计算，补填前须先绑手机），供客户端决定补填入口与登录后新号的「填写邀请码」页是否出现（BR-INV-03 细则；原「首次购买前提示」2026-10-19 作废）；绑定时的校验仍只以本条为准（2026-10-03，功能对照 G-05）。
- 期限随 `/v1/config.invite.backfill_hours` 下发，客户端据此隐藏补填入口，服务端以自身时钟为准。
- 订单状态按 BR-FUND-01 双状态书写：「任何状态」指任意 platform_status 与任意 rebate_status（单一 order_status 写法下即含 INVALID、CLAWED_BACK）；rebate_status=UNATTRIBUTED 的订单 user_id 为空，不属于本人，不计入。按 C-01 默认处理，已由负责人确认 2026-09-30。

#### BR-INV-08 细则 · 禁止绑定的关系

- 状态：已确认（拍板第二批 OPS-23：维持各自口径，邀请防作弊从严，不与 BR-ID-05 的 30×24 小时统一）
- 默认值：三种情形沿用 01；同设备窗口 = login_logs 留存期（BR-ID-30 ⑥）；只比较登录成功记录
- 决策人：负责人
- 依赖平台能力：无
- 取代：无
- 来源：规划/01 §5 J7 步骤 4、E12 F-INV-03、F-ACC-10、§7.6；规划/04 §3.2（无 login_logs 表）、§7 30403；docs/changes/20261001-拍板第二批.md（OPS-23）；PRD修订_后端功能规划 §2.10
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

- 例：A 与 U 在 60 天前曾在同一台 iPhone（device_id=d1）登录过，U 补填 A 的码 → 30403。
- 例：A 与 U 同设备登录发生在 200 天前（已超出 login_logs 留存期，BR-ID-30 ⑥）→ 不命中。
- 例：后台想把 U 的上级改为 V（V 是 U 的下级）→ 按 BR-INV-10 顺序先因 U 有下级返回 30409；② 的成环检查作为兜底。
- 设备 ID 重置后生成的新 device_id 视为不同设备，重置识别与同设备多账号归 规划/01 E17 风控（08 尚无 BR-RISK 主题）、BR-ID-05 同设备注册上限与 02 设备注册。
- 同设备窗口 = login_logs 留存期（BR-ID-30 ⑥；受最小必要与 01 §7.6 留存约束，不能取“全部历史”）；负责人决定不与 BR-ID-05 同设备注册上限的 30×24 小时口径统一（拍板第二批 OPS-23，11.3 第 9 条）。

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
- 改绑前已付款、之后入库的订单按 BR-INV-13 付款时间规则不写新上级，而是写 paid_at 时刻的上级（原上级；其快照、入账时的有效性按 BR-CALC-13；改绑前无上级则不写）。按 C-06 默认处理，已由负责人确认 2026-09-30。
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

- 闭包表改 P1 的理由：D8 计酬深度最多 2（直推 + 间推；2026-09-30 拍板第一批确认两级，2026-10-01 改为规则版本开关），按 paid_at 两跳重放 relation_change_logs 即可得到直推与间推受益人；补填与后台改绑都要求“无下级”，成环只需沿 parent_id 向上遍历即可判定（BR-INV-08），闭包表只增加维护成本。
- 例：A 于 10-10 申请注销（cooling 至 10-17），10-17 进入 processing，10-20 done → 10-20 起 A 的直属下级 U、V 的 parent_id=NULL；U 在 10-14 付款、10-15 生成快照的订单，快照时 A 处于 cooling，按 BR-CALC-13 记 A 为 active；该单入账时 A 已进入 processing 或 done → forfeited，份额归平台（BR-INV-13）。
- 例：A 在冷静期撤回注销 → 关系全程未变；冷静期内生成的快照已按 BR-CALC-13 记 A 为 active，不重算，入账照常。
- relation_change_logs 同时承担 BR-CALC-12 所称「user_relation_logs（bound_at / unbound_at）」：bound_at = 该条 created_at，unbound_at = 同一用户下一条记录的 created_at；表名统一见 13。按 C-06 默认处理，已由负责人确认 2026-09-30。

#### BR-INV-12 细则 · 计酬层级最多两级

- 状态：已确认（两级计酬：负责人 2026-09-30，docs/changes/20260930-拍板第一批.md §3 D8、BR-INV-12 行：「多层计酬（直推 + 间推）在实践中没有问题，不收入门费」；规则版本开关与审批：负责人 2026-10-01，docs/changes/20261001-间推二级奖励.md；间推比例数值见 BR-CALC-05）
- 默认值：无（已确认，按规则执行）；间推开关默认关闭
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 本条旧写法（2026-09-30，「计酬层级只到直推」）：「间推比例必须等于 0：commission_rules 的间推比例字段加数据库 CHECK (= 0)，后台不提供输入项；depth ≥2 的祖先不得出现在 commission_splits.beneficiaries……在取得分销模式书面法律意见（06 Q-F5）且负责人另行决策并发布迁移之前，不得开启间推」
  - PRD v2.1 §2、§15：「计酬不超过两层；MVP 间推默认 0（可配）」
  - 拍板第一批写法（2026-09-30）：「比例后台可配、调整后只对新生成的分佣快照生效」（2026-10-01 改为规则版本开关、按 paid_at 选版本，BR-CALC-05、BR-CALC-11）
- 来源：docs/changes/20261001-间推二级奖励.md；docs/changes/20260930-拍板第一批.md §3（D8、BR-INV-12、BR-CALC-05 行与间推比例行）；docs/changes/20261001-拍板第二批.md（OPS-02）；规划/00 §3.2 D8；规划/01 §3 分账口径、E12 F-INV-04；规划/02 §8.3；规划/06 Q-B1、Q-F5；PRD修订_后端功能规划 §2.10 分佣规则 r_l2 CHECK=0；PRD v2.1 §15；docs/changes/20261001-拍板第二批.md §8 ADD-06

- 例：B=1234 分，r_self=5000、r_direct=1000 → 自购 617、直推 floor(123.4)=123、平台 494。
- 例：C→B→A（C 邀请 B，B 邀请 A），A 自购 B=1234 → 间推关闭：B 得 123，C 得 0 且不出现在快照；间推开启（r_indirect=500）：B 得 123，C 得 61。
- 例：D→C→B→A，A 自购 → D 是 depth 3，任何版本都不进入受益人，也不得承接 B 或 C 失效的份额。
- 例：B 邀请 A，B 没有上级；A 自购（间推开启）→ 受益人为 A、B，间推份额归平台（BR-CALC-05）。
- 间推受益人的取值时点、「paid_at 时无上级的上级」、注销 / 封禁 / 冻结 / 未成年时的处理均按 BR-CALC-05、BR-CALC-13 与直推同口径，本条不另列；直推受益人判定见 BR-INV-13。
- r_direct、r_indirect 的默认值与比例配置归 BR-CALC-05 / 06 维护；间推比例按间推受益人在 paid_at 时刻的等级取值，跨等级合计上限把间推计入（BR-CALC-07、BR-INV-14）。
- 用户端展示与隐私：间推分佣按 BR-INV-17 逐条展示为「好友推广奖励」，不含任何下级或订单信息；间推上级看不到二级下级的任何信息，直邀人数只计直属下级（BR-INV-16）。
- 受益人推送：跟单与收益推送发给该订单全部受益人（归属用户、直推上级、间推上级；C-25，拍板第二批 OPS-02 确认），模板与触发只在 BR-TEXT-09 维护。
- 合规边界：不收入门费、不以发展人数计酬、不使用「下线」「团队业绩」等层级或团队计酬用语（BR-INV-20）是两级计酬成立的前提，任何放宽走 00 §8 变更流程。
- 依据 D8（负责人 2026-09-30 确认两级计酬、2026-10-01 确认开关方案）；06 Q-F5 书面法律意见由负责人跟进，不作技术闸门。拍板第一批列出的同步落点（00、01、02、04、06、13、10）已随 docs/changes/20261001-间推二级奖励.md 同步。

#### BR-INV-13 细则 · 直推与间推受益人判定

- 状态：已确认（负责人 2026-09-30，依据 docs/changes/20260930-拍板第一批.md §2；间推部分按 2026-10-01 规则版本开关）
- 默认值：分享单也给分享者的上级直推分佣（理由：推广收益口径已含直推，与自购单一致）；备选仅自购单给直推；上级按 paid_at 时刻取值（理由：结果可重放，不受入库与找回延迟影响）；绑定前付款时份额归平台；上级有效性只按 BR-CALC-13；负责人 2026-09-30 同意默认（变更记录 §2）；有效性口径由拍板第二批 FUND-10、FUND-17 裁决
- 决策人：负责人
- 依赖平台能力：各平台订单 paid_at 字段准确性（09 订单归属链路，待实测）
- 取代：
  - 本条旧写法：「直推受益人 = 分佣快照生成时刻（订单首次入库 O2，或找回/后台归属 O11）归属用户的 users.parent_id，另排除 paid_at &lt; parent_bound_at」（按 C-06 改为 paid_at 时刻的上级；排除条件保留并并入 (1)）
- 来源：docs/changes/20261001-间推二级奖励.md（间推受益人）；docs/changes/20261001-拍板第二批.md（FUND-10、FUND-17）；规划/01 §3 快照、F-SET-03、§6 未成年规则；规划/02 §8.3；规划/04 §3.2 orders.paid_at、commission_splits、状态机 O2/O11；08 BR-FUND-01、BR-CALC-10、BR-CALC-12
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：A 邀请 U；U 于 10-05 自购，订单 10-05 首次入库，B=1000，r_self=5000、r_direct=1000 → U 500、A 100、平台 400。
- 例：A 在 10-04 被封禁，U 10-05 下单 → 按 BR-CALC-13 快照记 A 为 active；入账时 A 仍为 banned → forfeited，U 500、平台 500。A 若为 frozen → 该份额 held，解冻后在后续月结批次补入账（BR-FUND-01 R5a）；held 满 30 天仍无结论则告警转人工（BR-CALC-13）。
- 例：U 是分享者，外部好友 X 通过 U 的分享链接下单（buy_type=share）→ U 得推广收益，U 的上级 A 得直推分佣，A 的上级（如有）得间推分佣（BR-INV-12、BR-CALC-05）。
- 例：U 10-02 付款，10-03 补填 A，10-04 订单入库 → paid_at &lt; parent_bound_at，不写 A。
- 例（间推开启）：Z 邀请 A、A 邀请 U；U 10-05 自购 → 直推 A、间推 Z；若 A 10-06 才绑定 Z → 间推不写，归平台；Z 已注销 → 按 BR-CALC-13 forfeited，不顺延给 Z 的上级。
- 例：A 10-10 申请注销、10-12 撤回；U 10-11、10-13 入库的订单都写 A（cooling 不算失效，BR-CALC-13）。
- 例：U 的定金单 10-01 付定金（platform_status=DEPOSIT_PAID，不生成快照），10-11 付尾款（→PAID）时生成快照；直推受益人与等级取值时刻见 11.3 第 10 条（默认 deposit_paid_at）。
- 例：U 的订单 10-05 付款、10-06 已失效（rebate_status=VOID），10-08 找回通过 → 只设置 user_id 与 user_basis=claim（BR-FUND-01 R3b），不生成快照，无直推份额。
- paid_at 取联盟订单付款时间，时区 +08:00；各平台 paid_at 是否可靠需在 09 验证（待实测；预售单以 deposit_paid_at 还是尾款时间为准见 11.3 第 10 条）。
- 状态名按 BR-FUND-01 双状态书写（O2 ≈ R2、O11 ≈ R3，映射见本主题开头）。按 C-01 默认处理，已由负责人确认 2026-09-30。
- 快照生成时点按 BR-CALC-10、上级取 paid_at 时刻按 BR-CALC-12，绑定前付款不写的排除条件保留。按 C-06 默认处理，已由负责人确认 2026-09-30。
- 上级有效性改为只引用 BR-CALC-13：原 (2)「快照生成时刻 inviter_unavailable(该上级)=true（含封禁、申诉、冻结、注销 cooling/processing/done、已实名未满 18）→ 不写直推受益人」与 BR-CALC-13（banned/frozen/appealing 快照记 active、入账时判 forfeited 或 held，cooling 不算失效）结论相反，已删去；原写「分歧登记 14 §14.3 C-30」，但 14 §14.3 未落此号；已由拍板第二批 FUND-10（未成年：入账时归平台，识别前已入账的不动）与 FUND-17（冻结：held，满 30 天告警转人工）按 BR-CALC-13 口径裁决，不再另立分歧。

#### BR-INV-14 细则 · 等级定义与默认等级

- 状态：已确认（负责人 2026-09-30，依据 docs/changes/20260930-拍板第一批.md §2）
- 默认值：默认 L1；MVP 仅后台手动调级；r_direct 默认按上级在 paid_at 时刻的等级（理由：与上级自身等级激励一致；取值时刻按 BR-CALC-12），备选按归属用户等级；跨等级最大组合（含间推）发布校验按 BR-CALC-07；负责人 2026-09-30 同意默认（变更记录 §2）
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - PRD v2.1 §2：「P1 等级分佣界面（未说明 MVP 等级如何变化）」
  - 规划/01 §3 分账口径：「r_self + r_direct ≤ 8000（未说明跨等级组合如何校验）」
  - 本条旧写法（2026-09-30 前）：「发布校验 = max_level(r_self_bp 或分享比例) + max_level(r_direct_bp) + 活动加成上限 ≤ 8000」（未含间推）
- 来源：规划/00 §3.2 D8、§4；docs/changes/20261001-间推二级奖励.md（r_indirect 取值与上限）；docs/changes/20260930-拍板第一批.md §3（间推比例行）；docs/changes/20261001-拍板第二批.md（OPS-20）；规划/01 §3、E12 F-INV-05/07；规划/04 §2.5、§3.2；PRD修订_后端功能规划 §2.10 等级
- 需同步修改的规划文档：3 处（计数仅作记录，落点见 README §0.6）

- 例：U 在 10-10 12:00:00 被后台从 L1 调到 L2；paid_at=10-10 11:59:59 的订单即使 10-11 才入库，仍按 L1 比例；paid_at=10-10 12:00:00（等于生效时刻）及以后的按 L2。
- 例：taobao × self 下 r_self 为 L1 5000 / L2 5500 / L3 6000，r_direct 为 L1 1000 / L2 1500 / L3 2500 → 6000 + 2500 = 8500 > 8000，发布被拒（逐行校验会漏掉 L3 自购 + L3 上级的组合）。
- 例：L3 被禁用后，自动晋升任务（P1）最多升到 L2；已是 L3 的用户保持 L3。
- r_direct 按上级等级还是按归属用户等级取值属于金额口径；负责人 2026-09-30 同意默认（按上级在 paid_at 时刻的等级，变更记录 §2）。r_indirect_bp 按间推受益人等级取值（BR-CALC-05、BR-CALC-06）。
- 发布校验原为两项之和，D8 改为两级计酬后把 max_level(r_indirect_bp) 计入（变更记录 §3 间推比例行，BR-CALC-07）；下例为两项时的示意，间推比例非 0 时同理相加。
- 等级取值时刻由「快照时等级」改为「paid_at 时刻等级」（BR-CALC-12），与 BR-INV-13 上级取值时刻一致。按 C-06 默认处理，已由负责人确认 2026-09-30。
- MVP 用户端（含「我的」页）不展示等级（拍板第二批 OPS-20）；04 display 配置中的等级展示项在 MVP 固定为不展示，等级界面仍为 P1。
- 拍板第一批列出的同步落点（01 §3、04 §3.2、01 F-ADM-12、10 跨等级发布校验用例）已随 10-01 间推变更同步（10 AC-S2-37）。

#### BR-INV-15 细则 · 等级晋升条件

- 状态：已确认（负责人 2026-09-30，依据 docs/changes/20260930-拍板第一批.md §2）
- 默认值：L1 默认；近 30 个完整自然日本人子订单（确认收货、未失效、B>0）≥10 → L2、≥50 → L3；只升不降；理由：沿用 06 Q-B1 默认，改用确认收货口径防刷
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 参考_花卷云功能查漏底稿 §17：「拉人头晋升（不做）」
- 来源：规划/06 Q-B1 等级 L1–L3 晋升条件；规划/00 §3.2 D8；规划/01 E12 F-INV-05；PRD修订_后端功能规划 §2.10 等级（自动升级 P1）
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：D=2026-11-01，窗口为 10-02 00:00 至 10-31 23:59:59；该窗口确认收货且未失效的本人子订单 12 笔 → 升 L2；其中 1 笔 11-02 退款扣回不影响已升等级。
- 例：窗口内 60 笔，其中 15 笔 rebate_status=VOID → 有效 45 笔 → L2，不升 L3。
- 状态名按 BR-FUND-01 双状态书写（INVALID ≈ VOID）。按 C-01 默认处理，已由负责人确认 2026-09-30。
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
- 页面名 TeamFans 含“团队”语义，按 BR-INV-20 改为 InvitedFriends；P1 的好友列表接口同样不用团队类叫法，登记为 `GET /v1/invites/friends`（08 §13.9；2026-10-03 由 /v1/team/fans 改名，功能对照 G-67）。
- 下级只看到邀请人状态「已绑定 / 未绑定」，看不到邀请人任何信息（拍板第二批 OPS-20，BR-INV-18）。
- **对被邀请人的告知**（2026-10-03，功能对照 G-16；负责人 2026-10-03 已定跟单通知越快越好、不做日汇总，docs/changes/20261003-拍板第三批.md §1，本段是它的配套）：
  - 事实：被邀请人下单后，邀请人（间推开启时还有邀请人的邀请人）会收到跟单、失效、已结算、扣回四类通知，并在余额流水看到逐笔分佣（BR-TEXT-09、BR-INV-17）。通知与流水只有金额和状态，没有商品、订单号、昵称或手机号；但通知在订单同步后很快发出，邀请人能据此大致知道有好友在什么时候下了单。
  - 告知内容（一句话，文案键 invite.notice_inviter，BR-TEXT-14 表 C）：你订单带来的收益金额和状态会通知邀请你的人，不含商品信息。
  - 告知位置，从 MVP 第一版起：① 隐私政策（向其他用户提供信息的一节）；② 用户协议（即注册协议）的邀请与推广条款；③ 邀请落地页，在协议勾选框上方显示（BR-INV-18）。①② 的文本由法务写入（规划/06 Q-F1、Q-F2）。
  - 原 ④ 删去（负责人 2026-10-19「推荐」选项，`docs/changes/20261019-邀请奖励与登录精简.md`）：原写「④ App 内填写或确认邀请码的地方（填写邀请码页——「我的」补填与登录后新号的一步；剪贴板邀请口令的绑定确认；登录页的待绑定码提示），在输入框或确认按钮旁显示同一句」，2026-10-19 起这几处都不显示告知句，编号 ④ 不复用。由此，在 App 内经剪贴板提示条、填写邀请码页或登录带码完成绑定、没有打开过落地页的用户，只经 ①② 得到告知；这一点由法务在上线前确认是否足够（列入上线检查单，06 Q-F4），法务认为不够时按 00 §8 恢复 ④ 的部分位置（恢复方式见变更记录）。
  - 这是告知，不是另设的同意：不增加勾选框，不影响绑定流程（BR-INV-03、BR-INV-05）。用户不愿意被通知时可以不绑定邀请人；已绑定的关系不能自行解除（BR-INV-10）。
  - 上线后若要扩大通知里的信息范围（例如加入商品或昵称），属于改变本条与 BR-TEXT-09 的已确认范围，须先写影响评估，并按 BR-ID-12 判断是否升隐私政策版本。

#### BR-INV-17 细则 · 邀请分佣流水展示

- 状态：已确认（拍板第二批 OPS-18：名称、说明与日期精度以 BR-TEXT-19 为准，日期只到日）
- 默认值：逐条展示；名称、状态用语与日期格式按 BR-TEXT-19 / BR-TEXT-01（日期到日）；不含任何下级或订单字段
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 本条旧写法：「类型名 REFERRAL_CREDIT=“邀请好友购物分佣”、对应 CLAWBACK=“邀请好友购物分佣扣回”；状态固定“已入账 / 已扣回”；时间 = 分录 created_at 精确到分钟」（与 BR-TEXT-19 冲突，拍板第二批 OPS-18 改为以 BR-TEXT-19 为准）
- 来源：规划/01 §5 J7 步骤 5；规划/04 §2.4 REFERRAL_CREDIT、ledger_entries；docs/changes/20261001-拍板第二批.md（OPS-18）；PRD修订_后端功能规划 §2.10 下级隐私；docs/changes/20261001-拍板第二批.md §8 ADD-06
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- ledger_entries 只插入、没有状态字段，REFERRAL_CREDIT 在入账时才生成，所以“状态”由分录类型推出，不另存。
- 例：U 买了一件 99 元商品，A 的收益明细出现「邀请分佣入账｜邀请好友订单｜+¥1.23｜10-25」（格式按 BR-TEXT-19 例 4），看不到是谁、买了什么、几点下单。
- 扣回按 BR-TEXT-19 的 CLAWBACK 行显示，日期同样只到日，不可跳转；间推（开关开启）显示「好友推广奖励」，其余相同。
- 单条流水金额仍可能让上级推测下级有消费，这是分佣本身不可避免的；如需进一步弱化可改为按日汇总（未采用）。
- 取代本条旧写法「预估中的直推分佣计入“待到账”」：按 README §1.2 与 BR-TEXT-01，入账前的推广收益称「预估推广收益」，订单侧用「入账」、不用「到账」（C-02 负责人 2026-09-30 决定，拍板第二批 OPS-01 确认：结算前叫预估、结算后叫已结算）。

#### BR-INV-18 细则 · 邀请页与落地页内容

- 状态：默认假设（「我的」页邀请信息部分已由拍板第二批 OPS-20 确认）
- 默认值：200 + can_invite（本人已识别未满 18 周岁时 30413）；固定模板海报；三变量文案；文案保存时禁用词检查、背景图人工审核
- 决策人：运营
- 依赖平台能力：无
- 取代：无
- 来源：规划/01 §5 J7 步骤 1、E12 F-INV-06；规划/04 §6.4；规划/07 §2 02/03；规划/06 Q-F4；docs/changes/20261001-拍板第二批.md（OPS-20）
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：A 正常 → can_invite=true，landing_url=`https://s.example.cn/i/K7M2QX?ch=poster`（域名为占位，实际取 config.share_domains）。
- 例：A 被封禁 → 10006（BR-ID-31：封禁用户除白名单接口外一律 10006，App 进账号受限页，看不到邀请入口；2026-10-19 对齐，原写「200 {can_invite:false, invite_code:null, …, direct_count:5}」）。
- 例：运营在文案模板中写“全网最高返利”→ 保存被拒，提示命中绝对化用语。
- 例：A 已实名、未满 18 周岁 → 30413（data.reason=self_minor）；A 被封禁 → 10006（BR-ID-31，2026-10-19 对齐，原写「200 且 can_invite=false」）。未成年情形按 BR-INV-19 明示原因（提示取 BR-TEXT-14 表 A 30413 行，2026-10-21 W-09 改为引用），其他不可用情形不展示原因。
- 取代本条旧写法「恒返回 200，未成年本人也只返回 can_invite=false」：与 BR-INV-19 及错误码 30413（self_minor）对齐。
- 分享域名被封时换域名，已发出的旧海报二维码失效由 规划/01 E13 分享的域名切换规则处理（08 尚无 BR-SHARE 主题）。
- 例（「我的」页，拍板第二批 OPS-20）：U 经 A 的码绑定 → U 的「我的」页显示本人邀请码与「邀请人：已绑定」，不显示 A 的昵称或邀请码，也不显示 U 的等级；U 被封禁 → App 进账号受限页，「我的」页与邀请码都看不到（BR-ID-31，2026-10-19 对齐，原写「本人邀请码不显示（同 can_invite=false）」）。
- 对被邀请人的告知句（2026-10-03，功能对照 G-16）：落地页 `/i/{code}` 在协议勾选框上方显示 invite.notice_inviter，有效码与无效码的页面都显示（页面结构保持一致，BR-INV-05）。App 内的填写邀请码页（「我的」补填与登录后新号的一步）、剪贴板邀请口令的绑定确认与登录页待绑定码提示 2026-10-19 起不显示（负责人 2026-10-19，原写「App 内填写邀请码页、剪贴板邀请口令的绑定确认页显示同一句」）。文案经字典下发，可改措辞，不得删去「会通知邀请你的人」这层意思；内容与位置的依据见 BR-INV-16 细则。
- 落地页的【在 App 中打开】（2026-10-18，`docs/changes/20261018-登录注册改版.md`）：落地页在注册表单之外加一个次要按钮（BR-TEXT-14 表 C `invite_landing.open_in_app`），只把本页的邀请码带进已安装的 App（BR-INV-04 细则「邀请链接拉起 App」）；没装 App 时按系统行为留在网页或提示下载，不做延迟深链；有效码与无效码的页面结构仍保持一致（BR-INV-05）。
- P1 的专属导师入口（2026-10-03，功能对照 G-66；按功能对照 Q-18 默认 A，负责人 2026-10-06 确认）：本条「下级看不到邀请人任何信息」同样约束导师入口——导师默认只接平台分配的客服或企业微信联系人，不展示邀请人的微信号、手机号或其他联系方式，也不要求用户填写自己的微信号；要改为展示邀请人信息，须先按 00 §8 修改本条（规划/07 §2「导师微信」行）。
- 邀请页规则摘要明说不发奖励（负责人 2026-10-04 确认，docs/changes/20261004-设计稿第二批拍板.md §9）：`InviteShare` 页的规则摘要写明「现阶段邀请好友不发放红包或现金奖励」（原依据 BR-INV-22：MVP 不发邀请奖励）；P1 启用邀请奖励时随 BR-INV-22 一起改这一句。完整的邀请规则文案仍由负责人提供（06 Q-F4）。2026-10-19 起按邀请奖励活动是否有效分两种（BR-INV-24 ⑨，依据 `/v1/config.invite.reward_enabled`）：无效时（含开关默认 off）照旧显示这一句；有效时不显示这一句，改为显示 `invite.reward.tip_inviter`（邀请人看的奖励句，取值见 BR-TEXT-14 表 C，与 BR-INV-24 ⑨ 一致；2026-10-21 按 App 内高保真第 3 批定稿 W-08 改引，原写 invite.reward.tip——那是登录页与落地页给被邀请人看的句子）与活动规则摘要——至少写明奖励在好友首单确认收货并结算后发放、好友须在绑定后若干天内下单（天数取 `growth.invite_reward.eligibility_days`，BR-INV-24「有效期」，2026-10-20）、每位好友只发一次、同设备或同网络不发、预算用完即止（规则文本由运营起草、法务确认，06 Q-F4；数值由配置变量渲染，BR-TEXT-13）。落地页 `/i/{code}` 在活动有效时同样显示奖励句（BR-INV-24 细则，编排 2026-10-19 审阅改；本句原写「默认不显示」，2026-10-20 同步）。
- 不能邀请时不显示邀请奖励活动卡（2026-10-21 按定稿画板的保守默认（代理补全），App 内高保真第 3 批定稿 W-17，画板 `InviteShareUnavailable-v2`）：GET /v1/invites/me 返回 200 且 can_invite=false 时，邀请页即使在邀请奖励活动有效（`/v1/config.invite.reward_enabled=true`）时也不显示奖励活动卡（invite.reward.tip_inviter 与活动规则摘要）；只改展示，不改 BR-INV-24 的资格与发放。本人 30413 时按 BR-INV-19 细则同样不显示。

#### BR-INV-19 细则 · 未成年人邀请限制

- 状态：已确认（拍板第二批 FUND-10：识别前已入账的推广收益不动；§8 ADD-06：单一余额，未满 18 周岁期间全部提现合计受月额度约束；未成年规则 BR-ID-26 已由负责人 2026-09-30 确认）
- 默认值：已识别未满 18 周岁不可邀请（他人绑定 30401、本人邀请页 30413）、不受益直推与间推分佣；识别后未入账的推广份额归平台；识别前已入账 REFERRAL_CREDIT 留在余额中不动（未满 18 周岁期间全部提现合计受 BR-WDR-06 月额度约束）、满 18 周岁后不再受限；满周岁时刻口径按 BR-ID-26（C-15 默认处理，待法务确认）
- 决策人：负责人（2026-10-01 拍板第二批）；满周岁时刻口径：法务（C-15）
- 依赖平台能力：无
- 取代：
  - 本条旧写法：「当日 ≥ 出生日期加 18 年的同月同日即满 18 周岁；2 月 29 日出生者平年按 3 月 1 日计；邀请页 can_invite=false；已入账 REFERRAL_CREDIT 冻结、由法务决定退回或保留」（年龄口径与已入账处理改为引用 BR-ID-26，避免两处维护；邀请页按 30413 对齐）
  - BR-ID-26 (a) 旧写法：「他人用其邀请码绑定时按 BR-INV-02 的 inviter_unavailable 返回 30401…其本人调用 POST /v1/shares、GET /v1/invites/me 及邀请码生成/获取接口返回新增码 30413…」（内容并入本条，BR-ID-26 (a) 改为引用本条）
  - 本条旧写法：「识别前已入账的 REFERRAL_CREDIT 按 BR-ID-26 (c) 默认冻结至满 18 周岁」（拍板第二批 FUND-10 改为不另设冻结，冻结没有资金落点）
  - 本条 2026-10-01 写法：「留在推广账户不动…未满 18 周岁期间按 BR-WDR-06 不可提现」「PROMO 余额的提现限制见 BR-WDR-06」（单一余额，拍板第二批 §8 ADD-06）
- 来源：规划/01 §6 未成年规则（待法务确认）、F-ACC-08；规划/04 §2.5 realname_status；08 BR-ID-26；docs/changes/20261001-拍板第二批.md（FUND-10）；docs/changes/20261001-拍板第二批.md §8 ADD-06

- 例：A 2008-12-01 出生、已实名；2026-10-10 下级 U 的订单生成快照 → A 未满 18，该单直推份额归平台；按 BR-ID-26 口径 A 于 2026-12-02 00:00 +08:00 满 18 周岁，此后生成的快照 A 正常受益。
- 例：2008-02-29 出生者：按 BR-ID-26 在 2026-03-02 00:00 +08:00 满 18 周岁。
- 例：A 未实名，期间累计直推分佣 300 元（已入账）；10-20 首次提现触发实名，推算 16 岁 → 300 元留在余额中，未满 18 周岁期间连同其他余额每月合计最多提 ¥200（BR-WDR-06），满 18 周岁后不再受限（不扣回、不另设冻结）；未入账的直推份额入账时归平台。
- 例：16 岁已实名用户 U 的邀请码被好友输入 → 30401「邀请码无效」（与邀请人不存在同一文案）；U 本人打开邀请页或点分享赚 → 30413，客户端隐藏邀请与分享赚入口。
- 邀请奖励活动卡（2026-10-21 按定稿画板的保守默认（代理补全），App 内高保真第 3 批定稿 W-17）：本人 30413 时邀请与分享赚入口隐藏，邀请奖励活动卡（invite.reward.tip_inviter 与活动规则摘要，BR-INV-24 ⑨）也不在任何位置显示；不改 BR-INV-24 的资格与发放判定。
- 满周岁时刻按 BR-ID-26（C-15 默认，待法务确认）。
- 错误码：他人绑定由 30409(inviter_minor) 改为 30401（BR-INV-02 inviter_unavailable，不透露年龄）；本人分享、邀请由 30409(self_minor) 改为 30413（30409 由 BR-INV-07 用于「不能补填」）。按 C-03 默认处理，代理自定（00 §9）。
- 实名在首次提现时触发，未实名未成年人在提现前仍可邀请与累计分佣，属已知缺口，由 BR-WDR-06 的未成年提现月额度兜底（识别后全部提现每月合计受限，满 18 周岁后不再受限）。

#### BR-INV-20 细则 · 分销用语与不做事项

- 状态：已确认（D8 两级计酬由负责人 2026-09-30 确认，2026-10-01 确认开关方案与「好友推广奖励」名称；禁止项除「间推收益展示」改为逐笔展示外不变）
- 默认值：无（已确认，按规则执行）
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 本条旧写法（2026-09-30）：不得实现「间推收益展示」（改为按「好友推广奖励」逐笔展示）
  - PRD v2.1 §2 范围表：「P1 团队收益页、排行榜」
- 来源：docs/changes/20261001-间推二级奖励.md；docs/changes/20260930-拍板第一批.md §3（D8 行）；规划/00 §3.2 D8、§4、§5；规划/01 §4 页面清单（TeamFans / RankList）；规划/07 §2 不做清单；PRD v2.1 §15；参考_花卷云功能查漏底稿 §17
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：邀请列表标题用“我邀请的好友”，不用“我的团队”；页面名用 InvitedFriends，不用 TeamFans。
- 例：间推开启后，Z 的余额流水出现一笔「好友推广奖励」+¥0.61，不显示「来自二级好友 U」或层级。
- 这些限制的依据是 D8（负责人 2026-09-30 确认两级计酬、不收入门费；2026-10-01 确认开关方案）；用语禁忌与不做清单是两级计酬的配套约束，不因间推开启而放宽，解除需负责人决策并走 00 §8 变更流程。
- 拍板第一批列出的同步落点（00 §6、07）已随 10-01 间推变更同步。
- 不做免填邀请码（2026-10-03，功能对照 G-39；按功能对照 Q-16 默认 A 写，负责人 2026-10-06 确认）：好友点邀请链接下载安装后「自动带上邀请人」一类功能不做。这类功能要靠设备或浏览器指纹、延迟深链或安装归因 SDK 匹配，属于用推断代替用户自己的选择来建立邀请关系，还要新增供应商并在隐私政策里披露。邀请关系只经 BR-INV-03 的三个渠道建立，邀请码的来源见 BR-INV-04 细则「邀请码的来源」；设备指纹类数据只用于风控（规划/01 F-RISK-06）。负责人改选「P1 再评估」时，P1 只写目标与依赖：新增供应商须负责人定（00 §9）、隐私政策与 SDK 清单披露、只预填不自动绑定、由用户确认后走 register 渠道（BR-INV-06）。

#### BR-INV-21 细则 · 邀请开关与配置项

- 状态：默认假设
- 默认值：growth.invite_bind.enabled=on（生效 ≤10 秒，改动 step-up + 告警）；config.invite.required=false；config.invite.backfill_hours=168；config.invite.bind_phone_guide=on（2026-10-03 新补，BR-INV-03 细则）；config.invite.before_buy_tip 2026-10-19 作废（原默认 on，键保留不读、不复用）；邀请奖励活动的键与默认见 BR-INV-24；invite.fail_limit_per_day=5（按 +08:00 自然日）；level.default=L1；level.promote.l2_min_orders=10；level.promote.l3_min_orders=50；level.promote.window_days=30（P1 才使用）；landing.ip_register_limit=3（由 BR-ID-32 维护，此处只列依赖）
- 决策人：代理可自定
- 依赖平台能力：无
- 取代：无
- 来源：规划/04 §10.1、§10.2；规划/01 E12 F-INV-02
- 需同步修改的规划文档：1 处（计数仅作记录，落点见 README §0.6）

- 例：10-10 20:00 关闭开关，20:05 用户补填 → 30408；10-11 09:00 重新打开后可补填（仍受 168 小时限制）。

#### BR-INV-22 细则 · 新人红包与签到奖励仅P1（邀请奖励见 BR-INV-24）

- 状态：默认假设
- 默认值：MVP 不发新人红包与签到奖励；邀请奖励按 BR-INV-24；P1 首单确认收货后解锁、预算原子扣减、注销留存记录未过期（BR-ID-30 ⑩）时重注册不算有效新人
- 决策人：负责人
- 依赖平台能力：无
- 取代：
  - 参考_花卷云功能查漏底稿 §1、§8：「会员有效/活跃/新会员/有效新人口径（不在 MVP 采用）」
  - 本条 2026-10-19 前写法：标题「邀请奖励仅P1」，正文「MVP（M-内测、M-公开）不得发放任何新人红包、签到奖励或邀请奖励」「P1（W9 起）邀请奖励规则」「流水用 REWARD（sub_type=invite）」（负责人 2026-10-19 决定邀请奖励做成可开关的活动，改由 BR-INV-24 维护，`docs/changes/20261019-邀请奖励与登录精简.md`）
- 来源：规划/00 §3.2 D9、§4；规划/01 E12 F-INV-08、F-ACC-10；规划/04 §2.4；PRD修订_后端功能规划 §0.4 B2、§2.12

- 例：当日预算剩余 5 元，两笔 3 元奖励并发发放 → 只有一笔条件更新成功，另一笔不发。（预算原子扣减的做法被 BR-INV-24 ④ 沿用。）
- 例：用户注销后 100 天用同号重新注册并被邀请 → 不计为有效新人，邀请人不得奖励。
- 花卷云“有效新人 = 绑手机/微信/备案 + 首单或首次收货金额 ≥X”口径已整理为 BR-INV-23 的默认口径（P1，负责人 2026-10-06 确认），不在 MVP 实现。

#### BR-INV-23 细则 · 会员口径仅P1（有效、活跃、新用户、有效新人）

- 状态：已确认（负责人 2026-10-06，按默认，docs/changes/20261006-待确认事项整批确认与交由Jev判断.md）；有效新人金额门槛 member.valid_newcomer_min_paid_fen 仍由财务在 P1 规格给出（§11.3 第 12 项）。原为待决策（口径用于 P1 奖励与手续费，属金额口径；MVP 不用会员口径、首页弹窗只用可直接查询的事实已由拍板第二批 OPS-10 确认）
- 默认值：MVP 不启用；P1 active_days=30、active_orders=3、每日 00:10 +08:00 重算；有效 = 首次 App 登录成功；新用户 = 无 PAID 及以后状态的本人订单；有效新人金额门槛由财务在 P1 规格给出；理由：按 PRD评审_v2 F-73 的建议，口径全部参数化，上线后手续费与奖励口径不突变（对照依据见私有材料）
- 决策人：负责人（金额门槛：财务）
- 依赖平台能力：无（订单状态与 paid_at 的可靠性随 BR-FUND-02 在 规划/09 验证）
- 取代：
  - 参考_花卷云功能查漏底稿 §1 会员状态口径：「活跃 = 近 30 天邀请 5 人、近 30 天有 3 笔有效单，所选条件同时满足」（去掉邀请人数条件，BR-INV-20）
  - 参考_花卷云功能查漏底稿 §1：「有效 = 触发任一选定事件（绑手机 / 下载 / 淘宝备案 / 下单 / 收货 / 提现）后永久有效」（固定为首次 App 登录成功）
  - 参考_花卷云功能查漏底稿 §8 有效新人判定：「条件一绑手机 / 绑微信 / 淘宝备案多选，条件二首单金额或首次收货金额 ≥X，两组任意或同时满足」（固定为已绑手机 + 首次确认收货子订单实付 ≥ 门槛）
- 来源：PRD修订_后端功能规划 §2.6 会员口径；PRD评审_v2 F-73；参考_花卷云功能查漏底稿 §1 会员状态口径、§8 有效新人判定；docs/changes/20261001-拍板第二批.md（OPS-10）

- 例：D=2026-11-01，00:10 重算，窗口 = [2026-10-02 00:00, 2026-11-01 00:00) +08:00；U 在窗口内付款 3 笔且均未失效 → 活跃；其中 1 笔 10-25 变为 rebate_status=VOID → 2 笔，不活跃。
- 例：paid_at=2026-10-01T23:59:59+08:00 的订单不在该窗口内；paid_at=2026-10-02T00:00:00+08:00 在窗口内。
- 例：U 首单 10-05 付款（首次 PAID）、10-06 失效 → 10-05 起不再是新用户，失效不恢复。
- 例：门槛取示例值 2000 分；被邀请人 V 首笔确认收货子订单实付 1800 分 → 不是有效新人；实付 2000 分 → 是（等于门槛即满足）。
- MVP 弹窗条件与 P1「新用户」口径的区别（拍板第二批 OPS-10）：MVP 按请求时实时查询的事实判定（如「有无订单」），不计算、不存储任何口径标记；P1 启用口径后由本条纯函数统一计算。01 F-HOME-08 的「新用户」人群按「有无订单」事实改写。
- 本条按 R6 只写到 P1 开工前需要的口径；P1 规格需补齐的未知项见 11.3 第 12 条。

#### BR-INV-24 细则 · 邀请奖励活动（双方各得，可开关）

- 状态：默认假设（负责人 2026-10-19 在对话中确认：做成可开关的活动、默认关闭、法务确认后由运营打开；被邀请人首单确认收货并结算后邀请人与被邀请人各得 10 元、进余额、可提现口径按现有余额规则；同设备、同 IP 不发；设每日与总预算上限；活动打开时登录页邀请码提示与邀请页显示「好友下单后，双方各得 10 元」、金额取配置；扣回默认「已发放的不追回，未发放的不再发放」；2026-10-20 确认资格有效期 30 天、按下单时间算（本条「有效期」）。其余为代理补全的默认，逐项见下文「代理补全的默认」，待确认，06「2026-10-19 邀请奖励活动待确认」）
- 默认值：开关 off；每方 1000 分；每日预算与总预算 0（未填，不能打开开关）；开关为 on 时每方金额须 ≥ 1 分，与预算为 0 同一处保存校验（编排 2026-10-20 D10-94 默认：08 原未禁止金额 0，开关开着会显示「各得 ¥0」；负责人可改）；首单实付下限 0；资格有效期 30 天（`growth.invite_reward.eligibility_days`，按被邀请人子订单的下单时间算，取得资格时随金额一起锁定）；资格在绑定时锁定；触发 = 本人自购子订单第一次到 CREDITED 且 B > 0；已发放不追回
- 决策人：负责人（法务定性 06 Q-F5、税务 06 Q-F6）
- 依赖平台能力：无（触发依赖订单月结入账，BR-FUND-04 与各平台 CAP-*-08 的月结验证）
- 取代：
  - BR-INV-22 2026-10-19 前写法：「MVP（M-内测、M-公开）不得发放任何……邀请奖励」；规划/00 D9「邀请奖励放 P1」（由 00 D36 取代邀请奖励部分）
  - BR-INV-18 细则「邀请页规则摘要明说不发奖励」只在活动无效时显示（本条 ⑨）
- 来源：负责人 2026-10-19 对话（`docs/changes/20261019-邀请奖励与登录精简.md` §1 第 3 项）；BR-INV-08、BR-INV-22（预算原子扣减做法）；BR-ID-06、BR-ID-28（注销留存与换号留存）；BR-ID-37；BR-FUND-01、04、13、15、16；规划/02 §8.2 MKT_EXPENSE
- 需同步修改的规划文档：规划/00 §3.1 D36、§4 增长行、§6；规划/01 F-INV-12、F-ADM-27、§4.2 `Login` / `InviteShare` 行、J7；规划/04 §2.4 `REWARD`、§3.2 `invite_rewards`、§6.6、§10.1 `invite`、§10.2、§11.2；规划/05 CT-25、B1-35、B2-16、F1-15、APP-19、HM-15；规划/06 Q-F4、Q-F5、Q-F6 与「2026-10-19 邀请奖励活动待确认」；规划/07 §2 拉新活动行；规划/10 AC-S2-112；08 BR-TEXT-12、14、19，BR-FUND-01、15，BR-ID-37（已同步 2026-10-19）

**资格记录与状态**（形状见规划/04 §3.2 `invite_rewards`，编码由契约线定）：每个被邀请人至多一条，唯一键为被邀请人；字段含邀请人、每方锁定金额、锁定的有效期天数、取得资格时刻、触发子订单、两方各自的结果（已发 / 不发及原因）。状态：已取得资格（等触发）→ 顺延（已触发，当日预算不够）→ 已处理（两方各自已发或不发）；另有作废（关系已变、触发订单发放前被扣回或进入维权）与已过期（有效期内没有可触发的自购子订单，见「有效期」）两个终态。原「预算用尽」终态自 2026-10-19 总预算改为取得资格时占用后已无路径，2026-10-20 由「已过期」取代。不发与作废都写原因，后台可查，用户端不展示原因。

**有效期**（负责人 2026-10-20 确认：30 天、看下单时间）：只有下单时间在「取得资格时刻起锁定天数内」的本人自购子订单才可触发；该订单在期限之后才月结入账，照发。到期（取得资格时刻 + 锁定天数）后由每日任务判定：期限内没有下过自购子订单，或期限内下的自购子订单都已失效（VOID）或基数 B 为 0 → 资格转「已过期」，释放其总预算占用；期限内的子订单还没有结果（未入账也未失效）的，等这些订单有结果再判。过期后再下的订单不触发；改 `eligibility_days` 只影响之后取得资格的记录。下单时间取联盟订单的创建时间（orders 已归一的下单时间字段）。

**判定顺序**（发放任务在触发订单迁移到 CREDITED 的事务提交后执行，按被邀请人加锁，幂等）：
1. 资格记录存在且为「已取得资格」或「顺延」，否则结束。
2. 被邀请人当前 parent_id 仍是资格记录里的邀请人，否则作废（同设备复核解除、邀请人注销完成等）。
3. 触发订单当前仍为 CREDITED、未被扣回、不在维权中，否则作废（⑥）；触发订单的下单时间不在有效期内的不触发、资格不变（由每日任务按「有效期」判过期）。
4. 双方防刷（③ 前三项）：命中则两方都记「不发」，记原因，状态「已处理」。
5. 单方防刷（③ 后四项）：命中的一方记「不发」，另一方继续。
6. 预算：暂停发放开关 payout_paused 为 on → 顺延；否则本次要发的金额（一方或两方之和）扣当日预算（条件更新），同一事务内把对应的总预算占用转为已发放；判为不发的一方、以及第 2、3 步作废时两方，释放其占用；当日不够 → 顺延，次日 00:00 +08:00 起按触发时刻先后重试，重试仍从第 1 步判起（编排 2026-10-19 审阅改：原写「发放时才扣总预算，不够即预算用尽」）。
7. 写 REWARD 凭证（每方一张，用户侧 sub_type=invite），资格记录写结果，状态「已处理」。

**代理补全的默认**（负责人未逐项说明，按保守口径写，都做成配置或可回退的分支；待确认，见 06「2026-10-19 邀请奖励活动待确认」）：
- 资格在绑定时锁定（含金额），关闭开关只停新增资格、不撤销已有资格，并同时占用总预算（编排 2026-10-19 审阅改：原写只计已发放金额，总预算用尽时已锁定的资格会落空）；要紧急停发，打开 growth.invite_reward.payout_paused（触发的顺延，恢复后补发）。理由：月结入账要等一到两个月，若按发放时的开关判定，绑定时看到的承诺多数会落空。
- 「首单」取被邀请人本人自购子订单里、下单时间在有效期内、第一笔进入 CREDITED 的，而不是第一笔付款的；分享单（buy_type=share）不算；要求基数 B > 0（这单有联盟佣金），另设实付下限 `growth.invite_reward.min_paid_fen`（默认 0，即不设门槛）。
- 只认 landing、register、backfill 三个自助渠道建立的关系；后台改上级（admin）不取得资格。
- 同 IP 只比较被邀请人绑定时的 IP 与邀请人绑定前 ip_window_hours（默认 24）小时内的登录 IP（编排 2026-10-19 审阅改：原写两人留存期内 IP 集合求交集，国内移动网络大量用户共用出口地址，会大面积误伤）。同住家人当天共用 Wi-Fi 仍会被判同 IP，这是已知代价；防刷主要靠设备判定（BR-INV-08）。
- 单方不发的情形（BR-ID-37 同设备多账号、封禁 / 申诉中 / 冻结、注销流程中、已识别未满 18 周岁）另一方照发；已识别未满 18 周岁的被邀请人不发，避免对未成年人做现金激励。
- 每日预算不够时顺延补发，不作废；总预算在取得资格时就占用，已取得资格的都发得出（编排 2026-10-19 审阅改）。活动有效（⑨）用「开关 on 且总预算可用额 ≥ 两方金额之和」判定，可用额不够时展示自动消失、不再新增资格。
- 邀请落地页 /i/{code} 也显示奖励句（编排 2026-10-19 审阅改：被邀请人最先看到的就是落地页；原写落地页默认不显示）。
- 发放不另发推送，只在余额流水出现（名称按 BR-TEXT-19）；用户端不展示「不发」的原因。
- 打开开关的前提除负责人说的法务确认外，另加奖励所得的税务结论（06 Q-F6）：不知道要不要代扣就先发钱，事后补扣做不到。负责人认为税务不必作前提时删去这一条。
- 发放是独立凭证，在触发订单的 CREDITED 迁移提交之后执行，不放进月结批次的同一事务（避免奖励逻辑失败拖住入账）；资金线认为放进同一事务更稳时可改，但不得因奖励失败而阻塞结算。

**账务与税务**：用户侧入 USER_BALANCE 的 available 子户，流水 REWARD、sub_type=invite（规划/04 §2.4），可提现口径与其他余额相同（BR-FUND-13、BR-WDR）；平台侧记营销费用科目 MKT_EXPENSE（规划/02 §8.2）。凭证键、借贷方向与机读模板由资金线按 BR-FUND-15、BR-FUND-16 在 `specs/ledger-templates.csv` 补（规划/05 B2-16），本条不写分录；BR-FUND-23 的 X1 已含 REWARD。奖励属于哪类所得、是否需要代扣、提现时怎样与佣金收入合并或分开计税，待税务意见（06 Q-F6）；结论到位前不得打开开关（与 ① 的法务意见一起列入上线检查单）。

**与分佣和其他规则的界限**：本条奖励不是分佣（BR-INV-12），不进 commission_splits、不影响 BR-CALC 的任何份额与合计上限校验；不计入等级晋升（BR-INV-15 只计本人订单）；用语仍受 BR-INV-20 与 BR-TEXT-13 约束（不得写成按人数阶梯或团队奖励，禁用词按 BR-TEXT-13）；不使用 BR-INV-23 的会员口径（「首单结算」是发放时可直接查询的订单事实，不存任何口径标记）；同设备注册上限与同设备多账号仍按 BR-ID-05、BR-ID-37。

- 例：开关 on、每方 1000 分、总预算 100000 分、当日预算 20000 分。A 邀请 U（10-20 经落地页注册）→ 写资格记录（锁定每方 1000 分，占用总预算 2000 分）。U 10-22 自购 O1（B=320 分，实付 4990 分），11-25 月结入账 O1 → 发放任务：A、U 各 +¥10（REWARD），总预算剩 98000、当日剩 18000。U 之后的订单不再触发。
- 例：同上，但 U 与 A 在 9 月用同一台手机登录过 → O1 入账后两方都不发，记「同设备」，状态已处理；U 之后的订单也不再触发。
- 例：U 与 A 不同设备，U 10-20 在 A 家连同一个 Wi-Fi 注册绑定，A 当天也在家用过这个 IP → 两方都不发（同 IP），释放占用的 2000 分；若只是 A 三个月前用过的运营商共享地址与 U 的相同，不算同 IP。
- 例：A 在 O1 入账时被冻结（risk_state=frozen）→ A 不发，U 照发 1000 分；A 解冻后不补发。
- 例：U 的第一笔订单 O0 已失效（VOID），第二笔 O1 入账 → 以 O1 触发（「首单」按第一笔入账的自购单）。
- 例（有效期，2026-10-20）：U 10-20 绑定取得资格（有效期到 11-19）。U 11-10 下单 O1，12-25 才月结入账 → 照发。若 U 第一次下单是 11-25 的 O2 → 11-20 每日任务判定期限内无自购子订单，资格转「已过期」、释放占用的 2000 分，O2 入账也不触发。若 U 11-10 下的 O1 后来失效、期限内没有别的单 → O1 失效后的那次每日任务判「已过期」。
- 例：O1 入账当天当日预算已用完 → 顺延；次日补发时 O1 已被扣回 → 作废，两方都不发，U 之后的订单也不再触发。
- 例：运营 11-01 关闭开关；10-20 已取得资格的 U 在 11-25 入账 → 照发（资格在绑定时锁定）；11-02 绑定的 V 没有资格。
- 例：A 已拿到 U 的 ¥10，12 月 U 的 O1 售后扣回 → 已发放的不追回，A、U 余额不动。

### 11.3 本主题未决问题

1. 推广自买单（规划/01 E17 风控，08 尚无 BR-RISK 主题：分享单下单人与推广者同设备/同支付宝/同收货手机号）判定作废推广收益时，推广者上级的直推分佣是否同时作废？默认：同时作废（整单视为违规）。需负责人确认。
2. 已解决（2026-09-30）：r_direct 按上级在 paid_at 时刻的等级取值（BR-INV-14 默认，负责人确认，变更记录 §2）；序号保留。
3. 已解决（2026-09-30）：分享单给分享者的上级直推分佣（BR-INV-13 默认，负责人确认，变更记录 §2）；间推同理（BR-CALC-05）；序号保留。
4. risk_state=frozen（仅提现冻结）是否也使邀请人不可用、不受益直推分佣？BR-INV-02 默认纳入；若负责人认为 frozen 只影响提现，从 inviter_unavailable 中去掉 frozen，BR-INV-18 自动同步。直推受益人的 frozen 处理不走 inviter_unavailable，按 BR-CALC-13（held，满 30 天告警转人工，拍板第二批 FUND-17）。
5. 已解决（拍板第二批 OPS-20）：被邀请人只看到「已绑定 / 未绑定」，不显示邀请人昵称、邀请码等任何信息（BR-INV-18）；序号保留。
6. 晋升阈值（L2 ≥10、L3 ≥50）已随 BR-INV-15 由负责人确认（2026-09-30）；各等级 r_self / r_direct / r_indirect 比例开发期用占位值，上线前由超管在后台填写（拍板第二批 §8 ADD-03，取代 FUND-21；06 Q-B1、后端规划 B11），且须满足 BR-CALC-07 跨等级合计上限（含间推）。
7. 已解决（2026-09-30 / 2026-10-01）：计酬两级（直推 + 间推），间推由规则版本开关控制、默认关闭（BR-INV-12、BR-CALC-05）；06 Q-F5 书面法律意见由负责人跟进，不作技术闸门；序号保留。
8. 已解决（拍板第二批 FUND-10、§8 ADD-06）：实名后发现未成年上级时，识别前已入账 REFERRAL_CREDIT 留在余额中不动，未满 18 周岁期间全部提现受月额度约束，满 18 周岁后不再受限（BR-ID-26 (c)、BR-INV-19）；满 18 周岁时刻按 BR-ID-26（C-15 默认处理，待法务确认）；序号保留。
9. 已解决（拍板第二批 OPS-23）：维持各自口径——邀请绑定同设备窗口 = login_logs 留存期（BR-INV-08，从严），BR-ID-05 注册上限仍为 30×24 小时；序号保留。
10. BR-INV-13 付款时间规则依赖各平台 paid_at 准确（待实测）；预售单以定金付款时间（deposit_paid_at）还是尾款时间作为取上级与等级的 paid_at，需在 09 订单归属验证中确认，默认用 deposit_paid_at（更早者），并须与 BR-CALC-12 的 paid_at 取法一致。
11. 04 §3.2 users.status 字段未定义取值；本主题封禁判定只用 risk_state，需账号主题定义 users.status 或删除该字段。
12. BR-INV-23（P1）开工前需定：有效新人实付金额门槛 member.valid_newcomer_min_paid_fen（财务）。另两项随本条 2026-10-06 确认按默认（docs/changes/20261006-待确认事项整批确认与交由Jev判断.md）：有效新人不另加「淘宝备案」「绑微信」条件；活跃窗口按 paid_at 计（与 F-73「PAID 及以上状态」一致）。
13. 落地页接口与阈值已按 BR-ID-32 合并（BR-INV-05）：BR-ID-32 的 `POST /v1/landing/login` 与本主题 `POST /v1/invites/landing-register` 指同一接口，路径统一需在 13 与 BR-ID-32 中同步；consent channel 取 h5_landing。
14. 第三方登录（微信、Apple、华为）新建的账号怎样记上邀请人（功能对照 Q-01，2026-10-03）：当前按默认 C 维持现状，只加两处提醒（BR-INV-03 细则；2026-10-19 起只剩非购买触发登录后的绑手机引导，首次购买前提示作废，负责人接受「先下单的第三方新号不能补填、不能并号」的代价）；A「建号时就让填邀请码」与 B「补填期限从绑定手机时起算」都会改变绑定条件或期限，待负责人选定后再改 BR-INV-03、BR-INV-07。
15. BR-INV-24 邀请奖励活动（2026-10-19）待确认：扣回的细节（触发后、发放前被扣回或维权即作废）；「首单」取第一笔入账的自购单并要求 B > 0、实付下限默认 0；资格在绑定时锁定；同 IP 只比绑定时 IP 与邀请人此前 24 小时登录 IP（编排 2026-10-19 改）；单方不发时另一方照发；总预算在取得资格时占用（编排 2026-10-19 改）；落地页显示奖励句（编排 2026-10-19 定）；法务定性（06 Q-F5）与奖励所得的税务处理（06 Q-F6）——后两项到位前不得打开开关。逐项见 06「2026-10-19 邀请奖励活动待确认」。

---
