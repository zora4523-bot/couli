# 消息模板 messages（管理后台）

- 定稿：负责人 2026-10-24 在对话中「设计稿 没问题」（编排裁定 D10-316 ③「设计先行」）。评审时定下：第 2 条页面名沿用「消息模板」；第 8 条提示语照画板原文；另 12 条照评审页（第 1、3–7、9–14 条，要点见第 7 节开头）
- 核对版本：规划提交 ec81e62；代码主干 8fd3d4c7b8（rebate-platform 远端 main，2026-10-24 核对：后台资源 `messages` 已在，菜单可见权限还没有 `notify.channels`；CT-24t 契约草稿未合并）；派发前再核对一次
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（宽 1440），不入公开仓库；完整 sha256 登记在 [design/README.md](../README.md)「后台消息模板页定稿（2026-10-24）」。AdmNotifySmsTestSendNoPhone 定稿后按样例账号权限裁剪侧栏（fe，2026-10-24），正文未改
- 路由：后台资源 `messages`（菜单「运营 / 消息模板」）；页签「消息模板 / 短信 / 发送记录」，本规格管前两个；从哪来：侧栏；去哪：「去「短信」登记 / 处理」切到「短信」页签并定位该编码，未登记验证手机号时去「我的账号」
- 需求：01 F-MSG-05、F-ADM-15；规则只引编号：BR-TEXT-20 细则「短信渠道登记与后台渠道开关」（范围、登记、保存校验、测试发送、开关、过渡）、BR-TEXT-09 细则（模板表渠道列即默认渠道；频控与免打扰）、BR-TEXT-23 与 BR-TEXT-19 / BR-FUND-24 ⑦（只发站内信的编码）、BR-WATCH-15（订阅类不发短信）、BR-ID-24（站长告警）、BR-ID-05（验证码有效期）、BR-ID-45（验证手机号）、BR-ID-34（后台二次验证）、BR-TEXT-12（资金术语键）、BR-TEXT-13（禁用词）；验收：`docs/changes/20261024-短信模板与通知开关后台编辑.md` §3；任务：05 F1-10k；代码台账 F1-06zv（前端）、CT-24t（契约）、B1-12z（后端）
- 可参考的已合并页面：`apps/admin/src/pages/kill-switches/**`（Switch → 确认 → 动态码 → 写）、`pages/admins/**`（Table）
- 是否资金或归属页面：否（不动余额）；资金类编码的短信登记按资金术语口径评审（BR-TEXT-12）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 模板列表 · 渠道列 | AdmNotifyTemplatesChannels.dc.html（78f79d4aa1ee） | 进入「消息模板」页签 | adminListNotifyChannels · 200 · example |
| 「短信」页签 | AdmNotifyTemplatesSms.dc.html（06484e11e70f） | 点页签，或「去「短信」登记 / 处理」 | 同上，`sms_registrations[]` 展开为 code × variant 行 |
| 编辑短信 · 变量不一致 | AdmNotifySmsEdit.dc.html（c8049d09635d） | 资金类编码换模板 CODE，预览正文的变量与代码定义不一致 | adminRegisterNotifySms · 20001（`data.fields=[preview_text]`，reason 见第 7 节第 3 条） |
| 编辑短信 · 有效期不一致 | AdmNotifySmsEditCodeMismatch.dc.html（87422f345305） | `SMS_CODE` 正文写的分钟数与 BR-ID-05 不一致 | 同上 |
| 测试发送 · 确认 | AdmNotifySmsTestSend.dc.html（e36dd416c24f） | 抽屉【保存】且签名或模板 CODE 变了（或首次登记） | 本地：号码取 adminGetMyPermissions 的 `verify_phone_masked`，样例变量按该变体 `variables` |
| 测试发送 · 未登记验证手机号 | AdmNotifySmsTestSendNoPhone.dc.html（a48954132e55） | `verify_phone_masked` 为 null | 本地预判；直接提交得 10003 · data.reason=verify_phone_missing |
| 测试发送 · 已受理 | AdmNotifySmsTestSendOk.dc.html（ac513bb37c1a） | 阿里云受理，新登记已保存并生效 | adminRegisterNotifySms · 200（`test_send_phone_masked`） |
| 测试发送 · 未受理 | AdmNotifySmsTestSendFailed.dc.html（96182b847afd） | 阿里云拒收、出错或超时；什么都没保存 | 50301 / 50401 |
| 打开短信 · 二次确认 | AdmNotifySmsEnableConfirm.dc.html（7804fabafdf0） | 给 `sms_billing_confirm` 为真的编码由关到开 | 本地确认后 adminSwitchNotifyChannels（`confirm_sms_billing=true`） |
| 动态码 | 不另画，用现有 AdmStepUp.dc.html | 开关一次；保存（含测试发送）一次 | 10003 · data.tier=totp |
| 加载中 / 出错 | 不适用（无画板） | 请求在途；网络 / 5xx / 解析失败 | 本地：Table loading；Result +【重试】 |
| 并发冲突 | 不适用 | 别人先改了同一编码（`row_version` 变了） | 20902（不带 data）：提示后刷新列表 |
| 无权限 | 不适用 | 没有 `notify.channels` | 写控件不出现；10403 · admin_permission_denied |

画板上的签名、模板 CODE、回执编号、阿里云错误都是样例或占位，手机号只以脱敏样式出现；实现、夹具与文档都不要照抄成真实值。

## 2. 组件（03 §9.1 antd）

| 区域 | 组件 | 数据（接口字段） | 交互 |
| --- | --- | --- | --- |
| 页签与筛选 | Tabs；Form inline：Select（分类、渠道、资金术语 / 状态、模板类型）、Input（编码或名称）+【查询】【重置】 | 列表不分页，本地筛选与分页 | 「去「短信」…」切页签、定位并高亮该行 |
| 说明条 | Alert info；「短信」页签另加 warning（资金术语） | 画板文案 | — |
| 模板表 | Table（rowKey=code）：编码 / 名称、分类、资金类、站内信、推送、短信、操作 | `category`、`fund_terms`、`channels`、`default_channels`、`push_switchable`、`sms_switchable`、`sms_fixed` | 恒开、只发站内信、不能开短信、订阅类不发短信、只能换模板等只按这些字段画，前端不写死编码名单 |
| 推送 / 短信开关 | Switch + 小字默认值 | 同上、`row_version` | 切换 → 动态码 → adminSwitchNotifyChannels；`sms_billing_confirm` 为真且由关到开时先二次确认 Modal；失败弹回原值 + message，不做乐观更新 |
| 锁定格 | 锁图标 + 文字（不是置灰的开关） | `sms_fixed`；不含 inbox | 无控件 |
| 短信表 | Table（rowKey=code+variant）：编码 · 变体、签名、模板 CODE、类型、预览正文（两行截断）、短信渠道、状态、操作 | `sms_registrations[].variant / variables / registration` | 【编辑】；`registration` 为 null 时【登记】 |
| 编辑抽屉 | Drawer 640：编码、变体只读；当前生效；资金术语提示；签名、模板 CODE（Input）；模板类型（Radio，按已定第 7 条锁定）；预览正文（TextArea）；定义的变量（Tag 只读）；发出效果；错误条与字段下错误 | `registration`、`variables`、`fund_terms` | 【取消】【保存】：签名或模板 CODE 变了 → 测试发送确认；只改类型或正文 → 动态码后直接提交 |
| 测试发送 | Modal 520：测试对象、发送到（脱敏、不可改）、样例变量、样例短信、频控提醒 | `verify_phone_masked`、`variables` | 【发送测试短信】→ 动态码 → adminRegisterNotifySms（`sample` 带样例值）；结果换同一弹窗内容 |
| 测试结果 | 同一 Modal：已受理（success）/ 未受理（error + 原配置仍在生效） | 200 / 50301 / 50401 | 已受理：关闭后刷新列表；未受理：【关闭】【修改配置】回抽屉 |
| 二次确认 | Modal 520：默认渠道、按条计费、发送用的签名与 CODE、用户通知开关不影响短信、发送时刻照推送免打扰 | `default_channels`、`registration` | 【取消】【确认打开】→ 动态码 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 编码中文名 | BR-TEXT-14 `inbox.title.<code>`；没有站内信标题的编码用画板文案，登记 admin.notify_channels.* |
| 分类「服务」「订阅」 | BR-TEXT-09「通知分类」、BR-WATCH-15 |
| 保存被拒的错误条 | BR-TEXT-14 表 B `error.20001.notify_preview_vars_mismatch`、`error.20001.notify_code_ttl_mismatch`；字段下的明细句（多了 / 少了哪些变量、分钟数对照）由前端按 `variables` 与正文拼画板句式，登记 admin.notify_channels.*；禁用词沿用 BR-TEXT-13 现有提示 |
| 开关被拒 | BR-TEXT-14 表 B `error.20001.notify_channel_locked` |
| 未登记验证手机号 | 弹窗内照画板；接口返回时 BR-TEXT-14 表 B `error.10003.verify_phone_missing` |
| 测试发送未受理 | 照画板 AdmNotifySmsTestSendFailed，不用表 A 50301 / 50401 的通用句 |
| 说明条、状态、抽屉、弹窗、频控提醒、按条计费 | 08 无键，照画板原文（已定第 8 条），登记 admin.notify_channels.* |
| 出错、无权限、冲突 | BR-TEXT-14（10403.admin_permission_denied、20902、通用网络错误） |

## 4. 接口（CT-24t，现为 planned；operationId 取契约草稿，合并后以 `contracts/` 为准）

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| adminListNotifyChannels（GET /admin/v1/notify-channels） | 进入、写成功后、20902 后、【重试】 | 10001、10403 |
| adminSwitchNotifyChannels（PATCH /admin/v1/notify-channels/{code}） | 推送 / 短信开关；带 `row_version`，需要时带 `confirm_sms_billing` | 10001、10003、10403、20001（`data.fields` 指 push / sms / confirm_sms_billing）、20902、42901 |
| adminRegisterNotifySms（PUT /admin/v1/notify-channels/{code}/sms?variant=） | 抽屉保存；签名或模板 CODE 变了时同步测试发送，受理才保存 | 10001、10003（含 verify_phone_missing）、10403（资金类缺 `content.fund_terms`）、20001、20902、42901、50301、50401 |
| adminGetMyPermissions | 后台外壳已取；本页读 `verify_phone_masked` 决定能否测试发送 | — |

## 5. 权限点与开关（04 §11.2）

- `notify.channels`（动态码）：读本页列表（契约 GET 也要它），开关推送与短信，登记与更换短信（含测试发送）。没有时写控件不出现。
- 资金类编码（`fund_terms` 为真）改短信登记另需 `content.fund_terms`，只开关渠道不需要；没有时抽屉只读，用画板上的提示句说明。
- 菜单「消息模板」的可见权限补 `notify.channels`（F1-06zv）。

## 6. 稿上没画、实现要做的

- `SMS_CODE` 的 `registration` 为 null 时，「短信」页签该行显示「部署配置兜底」并提示去登记（已定第 9 条；不显示部署配置的值）。
- 预览正文的变量照阿里云原文写 `${name}`（已定第 10 条，推送与站内信仍写 `{name}`）；画板上的 `{code}`、`{amount}` 按此显示。
- 预览正文的字数只提示、不硬校验（BR-TEXT-20 的字数待验证）。
- 读屏：开关 `aria-label`「推送 {code}」「短信 {code}」；锁定格读出「恒开，不能关闭，只能换模板」；状态不只靠颜色。

## 7. 待定与不一致

评审已定（照评审页）：短信单独页签；一个编码一个短信开关；ORDER_INVALID、CLAIM_RESULT 可开推送与短信、默认关；状态用词；动态码保存一次（同步测试发送）、开关一次；模板类型锁定；`SMS_CODE` 兜底行；短信变量写 `${name}`；样例账号已补；降价提醒（P1）本期不显示；用新版列表（去掉站内信跳转、启用 / 停用列与【新建模板】）；变体显示名以契约为准。

1. **三步合一与画板**：已定第 6 条与 CT-24t 是保存时同步测试发送、受理才保存，没有「待测试 / 测试失败」的新配置，也没有单独的启用步骤。画板上的「待测试」「测试失败」状态，【测试发送 / 重新测试】【放弃新配置】【稍后再启用】【启用新配置】，以及说新配置已保存待测试或保留为测试失败、要用户再点启用的句子（AdmNotifySmsEdit / CodeMismatch 底部、TestSendNoPhone、TestSendOk、TestSendFailed）不实现；状态列先只出现「已启用 / 未登记」。替代句与是否显示最近一次失败记录等编排定，只暂停这几处。
2. **短信「未就绪」**：已定第 3 条要求一个编码所有变体都登记后才能打开短信；CT-24t 草稿写打开短信不要求有登记（未登记的不发），列表也没有就绪字段。WD_REJECTED 的「未就绪」置灰等契约对齐后再做。
3. **20001 的 reason**：`notify_channel_locked`、`notify_preview_vars_mismatch`、`notify_code_ttl_mismatch` 已登记在 08（13 §13.11、BR-TEXT-14 表 B，编排裁定 D10-335 ②）；CT-24t 草稿目前只给 `data.fields`，待契约补。补上前两种保存提示用同一字段提示（F1-06zv 台账注释）。给不能发短信的编码登记短信（`data.fields=[code]`）是否也带 `notify_channel_locked`，由契约线定。
4. **有效期对照句**：画板字段下的分钟数对照要知道 BR-ID-05 的有效期，列表接口没给；补字段前只显示错误条那句。
5. **测试结果字段**：画板已受理态的受理时刻与回执编号、未受理态的阿里云错误码与说明，契约响应都没有（200 只有 `test_send_phone_masked`，50301 / 50401 不带阿里云原因）；补字段前这几处不显示。
6. **变体显示名与分类**：契约 `variant` 只是编码，没给「默认」「抵扣负余额」等显示名；画板 `SMS_CODE` 分类为「—」、站长告警为「站长告警」，契约 `category` 只有 service / subscription / marketing（草稿示例 `SMS_CODE` 为 service）。两处等契约线定。
7. **画板外的编码**：`DATA_COPY_READY`、`DATA_COPY_CODE`（BR-TEXT-23 细则，后者短信只能换模板不能关）不在画板列表里，按接口字段照画、不需新稿；`DATA_COPY_CODE` 的中文名与模板类型（已定第 7 条只说了 `SMS_CODE` 与其余服务类）等编排定。
8. **读权限**：契约 GET 也要 `notify.channels`，只有 `content.article` / `content.fund_terms` 的账号进「消息模板」页签读不到列表；画板「无权限时写控件不出现」的前提是能读。是否放宽读权限等编排 / 契约定。
9. **停用态**：已定第 13 条去掉模板「启用 / 停用」列，01 F-ADM-15 与 05 F1-10k 仍写「停用状态 / 停用态」；本页不画停用，01 / 05 的写法等编排定。
10. **不在本规格**：「消息模板」页签的【编辑】【预览】（站内信与推送措辞）和「发送记录」页签（含 04 `notify_logs` 回执编号列）没有契约，F1-06zv 不做。
11. **资源名**：前端草稿写 `notify-templates`，代码主干与 F1-06zv 是 `messages`，本规格以代码为准。
