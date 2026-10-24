# 消息模板 messages（管理后台）

- 定稿：负责人 2026-10-24 在对话中「设计稿 没问题」（编排裁定 D10-316 ③「设计先行」）。评审时定下：第 2 条页面名沿用「消息模板」；第 8 条提示语照画板原文；另 12 条照评审页（第 1、3–7、9–14 条，要点见第 7 节开头）。画板与 CT-24t 草稿对不上的四处由编排裁定 D10-337、余下六处细节由 D10-339 定，均以定稿画板为准
- 核对版本：规划提交 ec81e62 加本规格同批的 08 回写（BR-TEXT-20 细则 D10-337 四处与 D10-339 六处、20001 三个 reason）；代码主干 8fd3d4c7b8（rebate-platform 远端 main，2026-10-24 核对：后台资源 `messages` 已在，菜单可见权限还没有 `notify.channels`；CT-24t 契约草稿未合并，按 D10-337、D10-339 修订中）；派发前再核对一次
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（宽 1440），不入公开仓库；完整 sha256 登记在 [design/README.md](../README.md)「后台消息模板页定稿（2026-10-24）」。AdmNotifySmsTestSendNoPhone 定稿后按样例账号权限裁剪侧栏（fe，2026-10-24），正文未改
- 路由：后台资源 `messages`（菜单「运营 / 消息模板」）；页签「消息模板 / 短信 / 发送记录」，本规格管前两个；从哪来：侧栏；去哪：「去「短信」登记 / 处理」切到「短信」页签并定位该编码，未登记验证手机号时去「我的账号」
- 需求：01 F-MSG-05、F-ADM-15；规则只引编号：BR-TEXT-20 细则「短信渠道登记与后台渠道开关」（范围、登记与模板类型、保存校验、「待测试」登记与启用、开关与就绪条件、读写权限、过渡）、BR-TEXT-09 细则（模板表渠道列即默认渠道；频控与免打扰）、BR-TEXT-23 与 BR-TEXT-19 / BR-FUND-24 ⑦（只发站内信的编码）、BR-WATCH-15（订阅类不发短信）、BR-ID-24（站长告警）、BR-ID-05（验证码有效期）、BR-ID-45（验证手机号）、BR-ID-34（后台二次验证）、BR-TEXT-12（资金术语键）、BR-TEXT-13（禁用词）；验收：`docs/changes/20261024-短信模板与通知开关后台编辑.md` §3；任务：05 F1-10k；代码台账 F1-06zv（前端）、CT-24t（契约）、B1-12z（后端）
- 可参考的已合并页面：`apps/admin/src/pages/kill-switches/**`（Switch → 确认 → 动态码 → 写）、`pages/admins/**`（Table）
- 是否资金或归属页面：否（不动余额）；资金类编码的短信登记按资金术语口径评审（BR-TEXT-12）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 模板列表 · 渠道列 | AdmNotifyTemplatesChannels.dc.html（78f79d4aa1ee） | 进入「消息模板」页签 | adminListNotifyChannels · 200 · example |
| 「短信」页签 | AdmNotifyTemplatesSms.dc.html（06484e11e70f） | 点页签，或「去「短信」登记 / 处理」 | 同上，`sms_registrations[]` 展开为 code × variant 行；状态取在用配置与「待测试」登记（字段以 CT-24t 修订为准） |
| 编辑短信 · 变量不一致 | AdmNotifySmsEdit.dc.html（c8049d09635d） | 资金类编码换模板 CODE，预览正文的变量与代码定义不一致 | adminRegisterNotifySms · 20001（`data.fields=[preview_text]`，reason 见第 7 节第 1 条） |
| 编辑短信 · 有效期不一致 | AdmNotifySmsEditCodeMismatch.dc.html（87422f345305） | `SMS_CODE` 正文写的分钟数与 BR-ID-05 不一致（背景列表里 WD_FAILED 行为「测试失败」） | 同上 |
| 测试发送 | AdmNotifySmsTestSend.dc.html（e36dd416c24f） | 有验证手机号时：抽屉【保存】且首次登记或签名、模板 CODE 变了（先弹本窗再一并保存并测试）；列表行点【测试发送 / 重新测试】 | 本地：号码取 adminGetMyPermissions 的 `verify_phone_masked`，样例变量按该变体 `variables` |
| 测试发送 · 未登记验证手机号 | AdmNotifySmsTestSendNoPhone.dc.html（a48954132e55） | ① 抽屉【保存】时 `verify_phone_masked` 为 null：动态码 → 仍存为「待测试」、不发测试短信，再弹本窗；② 页面加载后号码才失效：照常弹测试发送、过动态码，保存响应为「未发送」时结果换成本窗内容；③ 列表行点【测试发送 / 重新测试】而 `verify_phone_masked` 为 null：直接弹本窗 | 保存 · 200，测试状态「未发送：未登记验证手机号」（D10-339 ⑤，形状以 CT-24t 为准）；单独测试时没有号码得 10003 · verify_phone_missing |
| 测试发送 · 已受理 | AdmNotifySmsTestSendOk.dc.html（ac513bb37c1a） | 阿里云受理；新登记可启用 | 保存（或重新测试）· 200；【启用新配置】调启用动作；【稍后再启用】只关弹窗，该行仍为「待测试」、旁注「测试已受理」，之后在该编码的编辑抽屉里启用（D10-339 ①） |
| 测试发送 · 未受理 | AdmNotifySmsTestSendFailed.dc.html（96182b847afd） | 阿里云拒收、出错或超时；新登记标「测试失败」，原配置继续生效 | 50301（拒收或出错）/ 50401（超时或未知） |
| 打开短信 · 二次确认 | AdmNotifySmsEnableConfirm.dc.html（7804fabafdf0） | 给 `sms_billing_confirm` 为真的编码由关到开 | 本地确认后 adminSwitchNotifyChannels（`confirm_sms_billing=true`） |
| 短信「未就绪」 | AdmNotifyTemplatesChannels.dc.html（WD_REJECTED 行） | 未满足 BR-TEXT-20 细则的短信就绪条件（接口就绪标志为假） | 短信关着的：开关置灰，接口拒绝为 20001（`data.fields` 指开关字段）；默认含短信的：显示「开（未就绪）」（D10-339 ⑥） |
| 动态码 | 不另画，用现有 AdmStepUp.dc.html | 画板带盾牌的每个写操作各一次：开关、保存（含同步测试发送）、测试发送 / 重新测试、启用新配置；【放弃新配置】不要动态码（D10-339 ②） | 10003 · data.tier=totp |
| 加载中 / 出错 | 不适用（无画板） | 请求在途；网络 / 5xx / 解析失败 | 本地：Table loading；Result +【重试】 |
| 并发冲突 | 不适用 | 别人先改了同一编码（`row_version` 变了） | 20902（不带 data）：提示后刷新列表 |
| 无权限 | 不适用 | 只读权限而没有 `notify.channels`：能看、写控件不出现；读权限也没有：菜单隐藏 | 10403 · admin_permission_denied |

画板上的签名「凑狸」与 08 BR-TEXT-20 一致；模板 CODE（全零占位）、回执编号、阿里云错误都是样例或占位，手机号只以脱敏样式出现；实现、夹具与文档都不要把这些占位换成真实登记值。

## 2. 组件（03 §9.1 antd）

| 区域 | 组件 | 数据（接口字段） | 交互 |
| --- | --- | --- | --- |
| 页签与筛选 | Tabs；Form inline：Select（分类、渠道、资金术语 / 状态、模板类型）、Input（编码或名称）+【查询】【重置】 | 列表不分页，本地筛选与分页 | 「去「短信」…」切页签、定位并高亮该行 |
| 说明条 | Alert info；「短信」页签另加 warning（资金术语） | 画板文案 | — |
| 模板表 | Table（rowKey=code）：编码 / 名称、分类、资金类、站内信、推送、短信、操作 | `category`、`fund_terms`、`channels`、`default_channels`、`push_switchable`、`sms_switchable`、`sms_fixed`、就绪标志（CT-24t 修订补） | 恒开、只发站内信、不能开短信、订阅类不发短信、只能换模板、未就绪等只按接口字段画，前端不写死编码名单 |
| 推送 / 短信开关 | Switch + 小字默认值 | 同上、`row_version` | 切换 → 动态码 → adminSwitchNotifyChannels；`sms_billing_confirm` 为真且由关到开时先二次确认 Modal；未就绪时短信关着的置灰，默认含短信的显示「开（未就绪）」（D10-339 ⑥，能否关见第 7 节第 8 条）；失败弹回原值 + message，不做乐观更新 |
| 锁定格 | 锁图标 + 文字（不是置灰的开关） | `sms_fixed`；不含 inbox | 无控件 |
| 短信表 | Table（rowKey=code+variant）：编码 · 变体、签名、模板 CODE（有新配置时另列「新配置 …」并标「待测试」或「未启用」）、类型、预览正文（两行截断）、短信渠道、状态、操作 | `sms_registrations[]`：在用配置、「待测试」登记、最近一次测试结果 | 已启用：【编辑】【测试发送】；待测试：【编辑】【测试发送】，有在用配置时另有【放弃新配置】；测试失败：【编辑】【重新测试】【放弃新配置】；未登记：【登记】 |
| 状态列 | Tag：已启用 / 待测试（受理后旁注「测试已受理」）/ 测试失败（小字「保留原配置，原配置继续生效」）/ 未登记；`SMS_CODE` 兜底时「部署配置兜底」，首次登记待测试时两者同时显示 | 同上 | 状态不只靠颜色；不新增状态词（D10-339 ①） |
| 编辑抽屉 | Drawer 640：编码、变体只读；当前生效；资金术语提示；签名、模板 CODE（Input）；模板类型（Radio，锁定值见 BR-TEXT-20 细则「登记」）；预览正文（TextArea）；定义的变量（Tag 只读）；发出效果；错误条与字段下错误 | 在用配置、「待测试」登记与测试结果、`variables`、`fund_terms` | 【取消】【保存】：首次登记或签名、模板 CODE 变了 → 有验证手机号先弹测试发送，没有则动态码后仍存为「待测试」再弹 NoPhone；只改预览正文 → 动态码后直接保存。「待测试」登记已受理时抽屉另给【启用新配置】（动态码；资金类另需 `content.fund_terms`，D10-339 ①③） |
| 测试发送 | Modal 520：测试对象（新配置与当前生效；首次登记不显示当前生效）、发送到（脱敏、不可改）、样例变量、样例短信、频控提醒 | `verify_phone_masked`、`variables` | 【发送测试短信】→ 动态码 → 从抽屉来时保存并同步测试，从列表行来时对已存登记测试；结果换同一弹窗内容；没有验证手机号时按 NoPhone 禁用 |
| 测试结果 | 同一 Modal：已受理（success）/ 未受理（error + 新配置保留为「测试失败」、原配置仍在生效）/ 未发送（换成 NoPhone 内容）；首次登记时这几种和 NoPhone 里提到原配置的半句都不显示（D10-339 ④） | 测试结果 | 已受理：【稍后再启用】【启用新配置】（动态码；资金类编码没有 `content.fund_terms` 时不给）；未受理：【关闭】【修改配置】回抽屉 |
| 二次确认 | Modal 520：默认渠道、按条计费、发送用的签名与 CODE、用户通知开关不影响短信、发送时刻照推送免打扰 | `default_channels`、在用配置 | 【取消】【确认打开】→ 动态码 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 编码中文名 | BR-TEXT-14 `inbox.title.<code>`；没有站内信标题的编码用画板文案，登记 admin.notify_channels.* |
| 分类「服务」「订阅」 | BR-TEXT-09「通知分类」、BR-WATCH-15 |
| 保存被拒的错误条 | BR-TEXT-14 表 B `error.20001.notify_preview_vars_mismatch`、`error.20001.notify_code_ttl_mismatch`；字段下「多了 / 少了哪些变量」由前端按 `variables` 与正文拼画板句式，登记 admin.notify_channels.*；分钟数对照句见第 7 节第 2 条；禁用词沿用 BR-TEXT-13 现有提示 |
| 开关被拒 | BR-TEXT-14 表 B `error.20001.notify_channel_locked`；未就绪被拒照画板「未就绪」与列表刷新 |
| 未登记验证手机号 | 照画板 NoPhone；单独测试时收到 10003 `verify_phone_missing` 也一律弹 NoPhone，表 B 的接口用语不上页面（D10-335 ④ 认可「请先登记验证手机号」这句话术） |
| 测试发送未受理 | 照画板 AdmNotifySmsTestSendFailed，不用表 A 50301 / 50401 的通用句 |
| 说明条、状态、抽屉、弹窗、频控提醒、按条计费 | 08 无键，照画板原文（已定第 8 条），登记 admin.notify_channels.* |
| 出错、无权限、冲突 | BR-TEXT-14（10403.admin_permission_denied、20902、通用网络错误） |

## 4. 接口（CT-24t，现为 planned，按 D10-337、D10-339 修订中；operationId 取契约草稿，合并后以 `contracts/` 为准）

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| adminListNotifyChannels（GET /admin/v1/notify-channels） | 进入、写成功后、20902 后、【重试】 | 10001、10403 |
| adminSwitchNotifyChannels（PATCH /admin/v1/notify-channels/{code}） | 推送 / 短信开关；带 `row_version`，需要时带 `confirm_sms_billing` | 10001、10003、10403、20001（`data.fields` 指 push / sms / confirm_sms_billing；未就绪也是 20001）、20902 |
| adminRegisterNotifySms（PUT /admin/v1/notify-channels/{code}/sms?variant=） | 抽屉保存：首次登记或签名、模板 CODE 变了时存为「待测试」登记并同步测试发送；没有验证手机号时仍存、不发，响应带「未发送」测试状态（D10-339 ⑤） | 10001、10003（动态码）、10403（资金类缺 `content.fund_terms`）、20001、20902、50301、50401 |
| 启用新配置、重新测试、放弃新配置 | 结果弹窗或编辑抽屉里【启用新配置】；列表行【测试发送 / 重新测试】【放弃新配置】 | 契约草稿还没有，CT-24t 按 D10-337 ①、D10-339 ①②③⑤ 补（资金类编码启用缺 `content.fund_terms` 为 10403）；单独测试没有验证手机号为 10003 verify_phone_missing，其余码以契约为准 |
| adminGetMyPermissions | 后台外壳已取；本页读 `verify_phone_masked` 决定能否测试发送 | — |

## 5. 权限点与开关（04 §11.2；取值见 BR-TEXT-20 细则，D10-337 ④、D10-339 ②③）

- 读列表：`content.article` 或 `notify.channels` 任一，不要动态码。
- 开关、登记、测试发送、启用新配置：`notify.channels` + 动态码；【放弃新配置】：`notify.channels`，不要动态码。没有 `notify.channels` 时写控件不出现。
- 资金类编码（`fund_terms` 为真）改短信登记、启用新配置另需 `content.fund_terms`，只开关渠道不需要；没有时抽屉只读，抽屉与测试结果弹窗都不给【启用新配置】，用画板上的提示句说明。
- 菜单「消息模板」的可见权限补 `notify.channels`（F1-06zv）。

## 6. 稿上没画、实现要做的

- `SMS_CODE` 的在用配置为空时，「短信」页签该行状态列显示「部署配置兜底」并提示去登记（已定第 9 条；不显示部署配置的值）。
- 预览正文的变量照阿里云原文写 `${name}`（已定第 10 条，推送与站内信仍写 `{name}`）；画板上的 `{code}`、`{amount}` 按此显示。
- 预览正文的字数只提示、不硬校验（BR-TEXT-20 的字数待验证）。
- 【放弃新配置】先 Popconfirm；只删「待测试 / 测试失败」登记，在用配置不动。
- 默认含短信的编码「开（未就绪）」时，前端只照接口字段显示，发送行为在服务端（BR-TEXT-20 细则，D10-339 ⑥）。
- 读屏：开关 `aria-label`「推送 {code}」「短信 {code}」；锁定格读出「恒开，不能关闭，只能换模板」；状态不只靠颜色。

## 7. 待定与不一致

评审已定（照评审页）：短信单独页签；一个编码一个短信开关；ORDER_INVALID、CLAIM_RESULT 可开推送与短信、默认关；状态用词；动态码不做几分钟免验；模板类型锁定；`SMS_CODE` 兜底行；短信变量写 `${name}`；样例账号已补；降价提醒（P1）本期不显示；用新版列表（去掉站内信跳转、启用 / 停用列与【新建模板】）；变体显示名以契约为准。

已定：D10-337 ①–④（以定稿画板为准，取值在 08 BR-TEXT-20 细则）——① 测试发送流程按画板实现（「待测试 / 测试失败」与【稍后再启用】【启用新配置】）；② 短信开关就绪条件，未就绪按画板置灰；③ 测试发送未受理按 50301 / 50401，CT-24t 未提交草稿里改成 20001 / 42901 的那处撤回；④ 列表读权限。

已定：D10-339 ①–⑥（以定稿画板为准、从简，取值在 08 BR-TEXT-20 细则）——① 稍后启用：状态仍是「待测试」、旁注「测试已受理」，在编辑抽屉里启用；② 放弃新配置不要动态码；③ 资金类编码启用另需 `content.fund_terms`；④ 首次登记时提到「原配置」的半句不显示；⑤ 保存时没有验证手机号仍存为「待测试」、不发，10003 `verify_phone_missing` 只用于单独测试发送；⑥ 默认含短信的编码未就绪时显示「开（未就绪）」。第 1、2、4、5、6 节已按此改；第 2、4 节里「CT-24t 修订补」的字段与动作都指这十条。

1. **20001 的 reason**：`notify_channel_locked`、`notify_preview_vars_mismatch`、`notify_code_ttl_mismatch` 已登记在 08（13 §13.11、BR-TEXT-14 表 B，编排裁定 D10-335 ②）；CT-24t 草稿目前只给 `data.fields`，待契约补。补上前两种保存提示用同一字段提示（F1-06zv 台账注释）。给不能发短信的编码登记短信（`data.fields=[code]`）、未就绪时打开短信，是否也带 `notify_channel_locked` 或另给 reason，由契约线定。
2. **有效期对照句**：画板字段下的分钟数对照要知道 BR-ID-05 的有效期，列表接口没给；补字段前只显示错误条那句。
3. **测试结果字段**：D10-337 ① 要求契约给最近一次测试结果与时间；画板已受理态的回执编号、未受理态的阿里云错误码与说明，草稿没有，是否给由契约线定，没给前不显示。
4. **变体显示名与分类**：契约 `variant` 只是编码，没给「默认」「抵扣负余额」等显示名；画板 `SMS_CODE` 分类为「—」、站长告警为「站长告警」，契约 `category` 只有 service / subscription / marketing（草稿示例 `SMS_CODE` 为 service）。两处等契约线定。
5. **画板外的编码**：`DATA_COPY_READY`、`DATA_COPY_CODE` 不在画板列表里，按接口字段照画、不需新稿；模板类型见 BR-TEXT-20 细则「登记」，`DATA_COPY_CODE` 的中文名等编排定。
6. **停用态**：已定第 13 条去掉模板「启用 / 停用」列，01 F-ADM-15 与 05 F1-10k 仍写「停用状态 / 停用态」；本页不画停用，01 / 05 的写法等编排定。
7. **不在本规格**：「消息模板」页签的【编辑】【预览】（站内信与推送措辞）和「发送记录」页签（含 04 `notify_logs` 回执编号列）没有契约，F1-06zv 不做。
8. **「开（未就绪）」能否关**：D10-339 ⑥ 没说默认含短信、尚未就绪的编码能不能在后台把短信关掉，关了再开是否受就绪条件限制；先按普通开关处理（可关，再开时受 D10-337 ② 限制），等编排确认。未就绪时「只记日志」记在哪（如 `notify_logs` 的 `suppressed`，现有 suppress_reason 枚举里没有对应取值）交 CT-24t / B1-12z 定。
9. **首次登记的其余句子**：D10-339 ④ 只点了测试弹窗与 `20001.notify_preview_vars_mismatch`；编辑抽屉底部「保存后新配置为「待测试」，原配置继续生效…」和列表「测试失败」小字「保留原配置，原配置继续生效」在首次登记时同样不成立，先照 ④ 的做法不显示提到原配置的半句，等编排确认。
10. **资源名**：前端草稿写 `notify-templates`，代码主干与 F1-06zv 是 `messages`，本规格以代码为准。
