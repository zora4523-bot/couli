# 用户详情 · 客服代办：实名更正、编辑会员信息、个人信息副本（管理后台）· 设计规格（定稿）

- 状态：**定稿**（草稿 r2 经独立审查 r2 `review-r2.md` 结论 pass；草稿沿革：编排 D10-490 契约与后端都已完成、只缺规格，r2 按独立审查 r1 `review-r1.md` 回改，逐条处理见 `draft-result.md`）
- 定稿：负责人 2026-10-31 17:47 审阅页整稿「通过」（无备注、未逐条答待定项）；草稿 §7 待定 19 条按默认值处理，取值与方案选择用 TypeSafe Jev 判断后回写（规划/11 §7.3 第 13 项，概率见 §7「定稿决定」），审查 r2 的 S2 / S3 带进本稿（§8、§9）；变更说明 `docs/changes/20261101-后台客服代办三对话框定稿.md`。本次定稿没有改画板；入库时（编排 2026-11-01）按 `couli-runs/design-hifi/project/` 现行文件核对 sha，AdmUserEditConfirm、AdmUserEditConfirmReveal、AdmUserEditPhoneTaken 三张的表内前 12 位原写的是 r1 的值，已更正为现行文件，完整 sha256 登记在 design/README「后台客服代办三对话框定稿」
- 与已定稿规格的关系：补充 `design/specs/admin-user-detail.md`。该规格 §1 最后一行只登记了三张入口画板（AdmUserRealnameFix aa337d48e22b / AdmUserEdit 4fb9af006f38 / AdmUserDataExport a08b538fac72），并写「对话框本身的规格随各自任务」；本稿就是这三个对话框的规格。三张入口画板的 sha256 已登记，本稿**没有改**它们；与契约不一致的地方新增画板取代，见 §7 第 1–3 项（定稿均取 A：入口改指新稿，旧稿留作历史）。
- 核对版本：规划仓库 origin/main 48473e9（r1 写的是 b3ad8ce；r2 按 48473e9 复核所引条目，没有与本稿冲突的变化；规划/01 F-ADM-04；规划/04 §11.2 `user.realname_fix`、`user.phone_change`、`user.data_export`、`pii.reveal_phone`；08 BR-ID-25 细则「实名更正」、BR-ID-44 细则「后台编辑会员信息」（含其照录的 BR-ID-06 细则原段落）、BR-ID-39 细则「后台改昵称」、BR-ID-40 细则、BR-TEXT-12 细则「资金术语键」、BR-TEXT-14、BR-TEXT-25；13 §13.11 30417 / 30419 / 50301 行）；契约 `F1-frontend/work/openapi-main.yaml`（主干 contracts/openapi.yaml 副本，version 0.9.0）；代码主干 rebate-platform origin/main 0809917d3（ops/tasks B1-27a / B1-27b / B1-27c / B1-27i 均 done，本稿五个操作都不在 `planned-main.ts`）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（1440 宽；壳、页面底板取已定稿 AdmUserEdit，抽屉照 AdmUserInvitees，动态码照 AdmStepUp，提交中照 AdmAdminCreateSubmitting）；生成脚本 `F1-spec-drafts/admin-user-assist/gen-user-assist.py`（可重复运行）；样例登记 `design-hifi/sample-data.md` §18（r2 新增样例在 `F1-spec-drafts/admin-user-assist/sample-additions.md`，待合并）
- 路由：后台资源 `users/{id}`（概览页签「客服代办」区的三张卡）；对话框与抽屉不另设路由
- 需求：01 F-ADM-04（客服代办、编辑会员信息、保存确认里的「查看完整号码」）；规则只引编号：BR-ID-25、BR-ID-44、BR-ID-39、BR-ID-40、BR-ID-33（脱敏）、BR-ID-30 ⑨（副本 24 小时过期）
- 是否资金页面：实名更正会让该用户全部收款账号失效（BR-WDR-02），按涉资金评审；另两项否。新文案键的 BR-TEXT-12 归类见 §3 最后一列

## 1. 画板与状态

### 1.1 实名更正（adminCorrectUserRealname）

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 填写 | AdmUserRealnameForm.dc.html（778e7e8bcbdd） | 点「客服代办 · 实名更正」 | 顶部只显示 adminGetUser 能给的用户、绑定手机号、账号状态；**不显示当前姓名、身份证号、实名状态**（后台契约读不到；§7 第 8 项定为请契约线补，补上前按本稿）；姓名、身份证号、原因三项必填 |
| 动态码 | AdmUserRealnameStepUp.dc.html（ea500ef657de） | 点「验证并提交」；或提交返回 10003（`data.tier=totp`） | 本地 + 现有 step-up 接口 |
| 提交中（核验中） | AdmUserRealnameSubmitting.dc.html（e6c2d439fd6b） | 动态码通过、请求在途（要调实名核验服务，可能几秒） | 本地 |
| 成功 | AdmUserRealnameDone.dc.html（fe04146e450a） | 200 | 响应 `masked_name`、`masked_id_no`、`verified_at`；收款账号格标「已失效（实名更正）」（响应语义即全部失效，§7 第 8 项） |
| 校验失败 20001 | AdmUserRealnameInvalid.dc.html（9bdd7098ab24） | 20001 `data.fields=[id_no]`（位数或校验码不对） | 响应 `data.fields` |
| 不受理 30419 | AdmUserRealnameRefused.dc.html（689839066598） | 30419 `data.reason=withdrawal_in_progress`（样例时点 10-06，W…066 未到账） | 响应 `data.reason`（及 `data.stage`） |
| 核验不一致 30406 | AdmUserRealnameMismatch.dc.html（129619bacd34） | 30406 | — |
| 其余返回码（10003、10403、10001、20001 各字段、30419 六个 reason、44001、30407、30405、50401、50301、42901、无响应） | AdmUserRealnameErrors.dc.html（0a7b76e79fd2，状态汇总稿；r1 稿高 2000 时最后一行被截，r2 加高到 2320；50301 行「（含未接入）」随画板删，§9 第 2 条） | 见稿 | 响应 code / data |
| 旧入口稿（已登记，不改） | AdmUserRealnameFix.dc.html（aa337d48e22b） | — | 与契约不一致，被本组取代（§7 第 2 项定 A） |

### 1.2 编辑会员信息（adminEditUserProfile）

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 填写（已登记；定稿后随画板换版，§9 第 3 条） | AdmUserEdit.dc.html（4fb9af006f38） | 点「编辑会员信息」 | 当前 phone_masked、nickname |
| 保存确认（改手机号） | AdmUserEditConfirm.dc.html（6ee05f4cf4bc → **6ee05f4cf4bc**） | 填了新手机号后点「保存」（只改昵称也弹确认，内容见 §1.4；§7 第 10 项定 B） | 本次输入（脱敏显示） |
| 保存确认 · 查看完整新号 | AdmUserEditConfirmReveal.dc.html（4487ed34b17b → **4487ed34b17b**） | 确认弹窗里点眼睛 | 只显示本次输入，不读库（BR-ID-44 细则所录 BR-ID-06 细则原段落「保存确认里的查看完整号码」） |
| 保存中 | AdmUserEditSubmitting.dc.html（9363ecb4293f，新增） | 动态码通过、请求在途 | 本地 |
| 成功 | AdmUserEditDone.dc.html（f420e8f34ffc，未改） | 200 | 响应即 adminGetUser 形状 |
| 手机号已被占用 30411 | AdmUserEditPhoneTaken.dc.html（46e632d416f3 → aa27d1cbaa35 → **46e632d416f3**） | 30411 | —；r2 错误条标题改为待登记子键 `error.30411.admin_profile` 的句子（§7 第 18 项） |
| 昵称未通过审核 20001 | AdmUserEditNicknameInvalid.dc.html（ed1c335ba5ea，新增） | 20001 `data.reason=nickname_sensitive`（命中或审核超时）；样例为只改昵称、手机号留空 | 响应 `data.fields` / `data.reason` |
| 其余返回码（含 42901） | AdmUserEditErrors.dc.html（1a1d02a57266，状态汇总稿） | 见稿 | 响应 code / data |

三张未登记的旧稿（Confirm、ConfirmReveal、PhoneTaken）只改了一处：底层表单「手机号」「昵称」去掉必填星号，说明条加「手机号、昵称至少改一项，不改的留空或保持原值。」——契约 `minProperties: 2`（reason + 至少一项），两项各自都不是必填。原文件备份在 `F1-spec-drafts/admin-user-assist/backup/`。PhoneTaken r2 另改了错误条文案（§7 第 18 项），且是手改稿，重跑生成脚本不覆盖。§7 第 11 项定 A：AdmUserEdit 换版，这三张连同 Submitting 的底层表单随画板统一成同一写法（§9 第 3、4 条）。

### 1.3 个人信息副本（adminListUserDataExports / adminCreateUserDataExport / adminDownloadUserDataExport）

底板上「客服代办」区副本卡的按钮文字暂沿用已登记旧稿的「导出个人信息副本」、卡片说明暂沿用「自受理起 15 个工作日内提供」，随 AdmUserDetail 换版改（§7 第 1 项定 A，§9 第 6 条）。

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 请求列表 · 空 | AdmUserDataExportListEmpty.dc.html（129210940f1f） | 点「个人信息副本」卡，用户没有请求 | adminListUserDataExports · total=0 |
| 请求列表 | AdmUserDataExportList.dc.html（1f28fbde5545） | 同上，有请求 | adminListUserDataExports · 每页 20，`created_at` 倒序 |
| 登记 · 填写 | AdmUserDataExportForm.dc.html（b9471c4db3ab） | 抽屉里点「登记副本请求」 | 两项通道情况（必选，无默认）+ 原因 |
| 登记成功（新建 · 企业微信会话） | AdmUserDataExportCreated.dc.html（a3f6db76be7c） | 200 `reused=false`，`delivery=wecom_session` | 响应 + 刷新列表 |
| 登记成功（新建 · 站内信 + 短信提取码） | AdmUserDataExportCreatedInApp.dc.html（dff7123b405f，r2 新增） | 200 `reused=false`，`delivery=in_app_sms`（两项都「能」；样例 …5d03，10-12 09:40 另一分支） | 响应 + 刷新列表；该行操作列一直是「用户在 App 内下载」；…5d01 行「已由 …5d02 重新登记」是错字，应为 …5d03，随画板修正（§9 第 1 条） |
| 请求列表 · 别的账号登记的企业微信请求 | AdmUserDataExportListOther.dc.html（b3def48cce76，r2 新增） | 当前账号不是登记人（样例 …5d02 由客服代办样例账号登记，超管查看） | adminListUserDataExports `requested_by` ≠ 当前账号 → 操作列「仅登记人可下载」 |
| 登记 · 返回原请求 | AdmUserDataExportReused.dc.html（d181c3829898） | 200 `reused=true` | 响应 |
| 登记 · 暂不受理 | AdmUserDataExportUndecided.dc.html（9d4bc54feac7） | 30419 `delivery_undecided`（两项只有一项「能」） | 响应 `data.reason` |
| 下载 · 动态码 | AdmUserDataExportDownloadStepUp.dc.html（849085da5309） | 点行内「下载」（每次都要） | 现有 step-up |
| 下载 · 首次（口令只显示一次） | AdmUserDataExportDownload.dc.html（63f6df7e1625） | 200，`password` 非空 | `url`、`url_expires_at`、`password`、`expires_at` |
| 重新生成 · 确认 | AdmUserDataExportRegenerate.dc.html（455aedcf431f） | 下载对话框里点「重新生成文件与口令」 | 本地；确认后调下载接口 `regenerate: true` |
| 不能下载 30417 | AdmUserDataExportNotDownloadable.dc.html（4c13530aab8c） | 30417 `data.status=expired`（列表过时、副本已过期） | 响应 `data.status` + 刷新列表 |
| 其余返回码与状态（列表加载中 / 加载失败、in_app_sms 登记成功、10403 缺 pii.reveal_phone、20001 各字段、30419 注销、30417 各状态、42901、无响应、以后再下载 `password=null`） | AdmUserDataExportErrors.dc.html（1658b5510ee3，状态汇总稿） | 见稿 | 响应 code / data |
| 旧入口稿（已登记，不改） | AdmUserDataExport.dc.html（a08b538fac72） | — | 与契约不一致，被本组取代（§7 第 3 项定 A） |

### 1.4 没有单独画的状态

| 状态 | 处理 |
| --- | --- |
| 冲突 20902 | 三个写接口都没有 compare-and-set 值、也没有 Idempotency-Key（契约 description「No Idempotency-Key (04 §6.6)」），x-error-codes 不含 20902，所以**没有冲突态**；「重复提交 / 无响应」各按接口语义处理，画在三张汇总稿最后一行（§6） |
| 无权限（页面级） | 沿用已定稿 AdmUserDetailNoPerm：缺权限点的卡片按钮隐藏；本稿只画提交后返回 10403 的错误条（汇总稿）。缺 `pii.reveal_phone` 的客服登记企业微信路径没有整页稿（§7 第 13 项定 B，不补画） |
| 动态码（编辑会员信息、重新生成） | 同 AdmUserRealnameStepUp / AdmUserDataExportDownloadStepUp，只换「本次操作」一行 |
| 重新生成后的结果 | 同 AdmUserDataExportDownload（新口令、新链接） |
| 只改昵称的保存 | **也弹保存确认**（§7 第 10 项定 B，与草稿 r2 不同）：同 AdmUserEditConfirm 的 Modal 480（alertdialog），标题「确认保存会员信息？」，手机号行写「不变」、昵称行写「原昵称 → 新昵称」；去掉「手机号是登录凭据 / 退出登录」与「新手机号不发验证码确认」两段，也没有查看完整号码的眼睛；按钮【返回修改】【确认并验证】，确认后动态码再保存；成功提示不提退出登录。未单独画（§9 第 5 条） |
| 站内信 + 短信交付的请求行（已交付） | 同 AdmUserDataExportCreatedInApp 的 …5d03 行，状态换「已交付」、生成 / 过期列填时刻；操作列仍是「用户在 App 内下载」 |
| 以后再下载（`password=null`） | 照 AdmUserDataExportDownload：成功提示换成「已签发新的下载链接」，**口令块换成提示「这次没有新口令；如果没拿到上次的口令，请重新生成」**，其余不变（汇总稿最后一行；§2、§6 同此说法） |
| 副本抽屉加载中 / 列表加载失败 | 汇总稿前两行：加载中表格区 5 行 Skeleton；失败时表格区换成错误结果 +【重试】，10403 换无权限句 |

样例：UID U10023、脱敏手机号、`**凑 / 3****************4` 取自 sample-data §5；更正后的 `张三 / 11010519491231002X` 是契约示例（国家标准里的示例号码）；副本请求 id 是假 UUID 末 4 位（…5d01 / …5d02，取自契约示例）；口令「样例口令-AB12-CD34」、trace 末 6 位 `4f5a6b` 都是样例；时点与分支见 sample-data §18。

## 2. 组件（03 §9.1 antd）

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 实名更正对话框 | Modal 640：Descriptions（用户、绑定手机号、账号状态；不含当前实名，§7 第 8 项契约补上后再加「当前实名」一行）+ Alert info（两项都填）+ Form（Input 姓名 maxLength 64、Input 身份证号 maxLength 32 等宽字体、TextArea 原因 1–200 带计数）+ Alert warning「提交后」 | adminGetUser | 【取消】【验证并提交（盾牌）】；返回错误时 Alert error 放在 Descriptions 下、字段错误放字段下，输入内容保留 |
| 核验中 | 同一 Modal：输入置灰、关闭与取消禁用、主按钮 loading「核验中…」、`role=status` 提示句 | — | 不可关闭；`aria-busy` |
| 实名更正成功 | 页面顶部 Alert success（`role=status`）+ 基本信息「身份证号」格换新值并加 Tag「刚刚更正」+「收款账号」格加 Tag「已失效（实名更正）」 | 响应三字段 | 【查看操作日志】带 UID 筛选 |
| 编辑会员信息 | 已定稿的 Modal 640（AdmUserEdit）；手机号、昵称都非必填、至少一项；保存确认 Modal 480（alertdialog）每次保存都出现；只改昵称时不含退出登录提示与查看完整号码（§1.4、§7 第 10 项） | phone_masked、nickname | 见 AdmUserEdit* |
| 保存中 | 保存确认弹窗主按钮 loading「保存中…」、返回修改与关闭禁用 | — | 不可关闭 |
| 副本请求抽屉 | Drawer 920：标题「个人信息副本 · {UID}」+ 说明（同一用户最多一条未完成；列表不含链接与口令）+ Alert info（谁能下载）+ Table（rowKey=export_id）：请求（末 4 位 + 「取代 …」）、状态 Tag、交付方式、登记人 + 登记时间、截止、生成 / 过期、操作 + Pagination（每页 20） | adminListUserDataExports | 底部【关闭】【登记副本请求（盾牌）】；行内【下载（盾牌）】只在 `delivery=wecom_session`、`status ∈ ready / delivered`、`expires_at` 未过、`requested_by` = 当前账号、且当前账号有 `pii.reveal_phone` 时显示 |
| 登记对话框 | Modal 640：Descriptions（用户、绑定手机号、账号状态）+ 两个 Radio.Group（能 / 不能，必选、无默认）+ 交付方式规则表（三行，按选择高亮「本次」）+ TextArea 原因 + Alert warning「提交后」 | 两项通道情况 | 【取消】【验证并登记（盾牌）】；只有一项「能」时**不在前端拦**（要让服务端写审计，§7 第 12 项） |
| 下载对话框 | Modal 640：Alert success + Descriptions（交付方式、下载链接有效至、副本过期）+ 只读 Input 口令 +【复制口令】+ Alert warning「发给用户时」 | 下载响应 | 【重新生成文件与口令（盾牌，链接样式）】【关闭】【下载文件】（打开 `url`）；`password=null` 时口令块换成提示「这次没有新口令；如果没拿到上次的口令，请重新生成」 |
| 重新生成确认 | Modal 480（alertdialog） | — | 【取消】【验证并重新生成（盾牌）】 |
| 状态汇总稿 | 不是界面，是给实现与评审的对照表（三张 *Errors） | — | — |

盾牌图标 = 这一步要做动态码二次验证（沿用现有后台稿）。

## 3. 文案键

「BR-TEXT-12 归类」一列按 08 BR-TEXT-12 细则「资金术语键」的认定规则：说到提现、到账、收款账号的归资金术语，拿不准的也按资金术语处理。已在 `specs/fund-term-keys.yaml` 里的照旧；新键待编排补登。

| 位置 | 字典键 | BR-TEXT-12 归类 |
| --- | --- | --- |
| 10403、10001、10003、30405、30406、30407、50401、42901 的主句 | BR-TEXT-14 表 A `error.<code>`、表 B `error.10403.admin_permission_denied`（取原句，不改） | 照字典现有归类（普通） |
| 44001 主句 | BR-TEXT-14 表 A `error.44001`（取原句） | 资金术语（字典已列） |
| 20001 字段错误里已有子键的两句 | BR-TEXT-14 表 B `error.20001.phone_invalid`「请输入 11 位中国大陆手机号」、`error.20001.nickname_sensitive`（取原句，不改；r2 起 AdmUserEditErrors 的 phone_invalid 行改用原句） | 普通 |
| 30411（编辑会员信息，新手机号已属于其他账号） | **不用表 A 原句**（「…可退出后用手机号登录」不适用后台）；待登记场景子键 `error.30411.admin_profile`，画板句「该手机号已被其他账号使用，不能改到本账号」为底稿（§7 第 18 项定 A，待规则回写） | 普通 |
| 50301（实名核验服务出错或不可用） | **不用表 A 50301**（无 reason 时回落「{platform_name}维护中」，不适用）；待登记 `error.50301.realname_vendor`，画板句「实名核验服务暂时不可用，请稍后再试」为底稿（§7 第 19 项定 A，待回写 BR-TEXT-14 表 B 与 13 §13.11） | 普通 |
| 30419 主句「该用户当前不受理这项客服代办」 | BR-TEXT-14 表 A `error.30419`（画板主句即此句，见 §7 第 6 项「这项客服代办」与契约 msg 的差异） | 普通 |
| 30419 各 reason 的说明句（7 个值） | **BR-TEXT-14 表 B `error.30419.<reason>` 未补**；§7 第 6 项定 A：用不带业务名的中性句，以画板句去掉业务名为底稿回写 | `error.30419.withdrawal_in_progress` 资金术语（说的是提现单与到账）；其余 6 个普通 |
| 30417 下载被拒 | BR-TEXT-14 表 B `error.30417.data_copy`（「该个人信息副本当前状态不支持下载，请刷新后查看」） | 照字典 |
| 副本状态名、交付方式名 | **BR-TEXT-25 `admin_dict.personal_data_copy_status.*`、`admin_dict.personal_data_copy_delivery.*` 未登记**；画板叫法：排队中 / 生成中 / 待交付 / 已交付 / 失败 / 已过期 / 已取消；站内信 + 短信提取码 / 企业微信会话（§7 第 7 项定 A，照此回写 BR-TEXT-25） | 普通 |
| 字段错误句（「请填写原因说明（1–200 字）」「身份证号格式不正确：请核对 18 位号码与末位校验码」「请至少修改手机号或昵称中的一项」等） | 08 无键，用画板文案，登记 `admin.user_assist.*` | 普通 |
| 实名更正的「提交后」提示、成功提示（含「收款账号全部失效」「才能提现」）、收款账号格 Tag「已失效（实名更正）」 | 08 无键，用画板文案，登记 `admin.user_assist.realname.after_submit`、`admin.user_assist.realname.done`、`admin.user_assist.realname.payout_invalidated` | **资金术语** |
| 其余对话框标题、说明条、「提交后 / 发给用户时」提示、成功提示、按钮 | 08 无键，用画板文案，登记 `admin.user_assist.realname.*`、`admin.user_assist.profile.*`（已定稿 AdmUserEdit* 的原句一并登记）、`admin.user_assist.data_copy.*` | 普通 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 | 备注 |
| --- | --- | --- | --- |
| adminCorrectUserRealname（POST `/admin/v1/users/{user_id}/realname-correction`） | 实名更正「验证并提交」 | 10001、10003、10403、20001（reason / name / id_no / user_id）、30419（六个 reason）、44001、30407、30405、30406、50401、50301、42901 | 动态码 totp 档；无幂等键：重试 = 新一次提交（再调核验、再写审计）；成功后刷新 adminGetUser |
| adminEditUserProfile（PATCH `/admin/v1/users/{user_id}/profile`） | 编辑会员信息保存 | 10001、10003、10403、20001（phone_invalid / nickname / nickname_sensitive / [phone, nickname] / reason / user_id）、30411、44001、42901 | 动态码 totp 档；只发填了的字段（不与现值比对，§6）；重试安全（结果不变，多一条审计）；响应即用户详情 |
| adminListUserDataExports（GET `/admin/v1/users/{user_id}/data-exports`） | 打开副本抽屉、翻页、登记 / 下载后刷新 | 10001、10403、20001（user_id / page_size）、42901、5XX | 不需动态码；不写审计；加载中与失败见汇总稿前两行 |
| adminCreateUserDataExport（POST 同路径） | 登记「验证并登记」 | 10001、10003、10403（含企业微信路径缺 pii.reveal_phone）、20001（reason / app_login_ok / phone_sms_ok / user_id）、30419（account_deleting + stage=processing、account_deleted、delivery_undecided）、42901 | 动态码 totp 档；无幂等键，重试返回原未完成请求（`reused=true`） |
| adminDownloadUserDataExport（POST `…/data-exports/{export_id}/download`） | 行内「下载」；「重新生成」（`regenerate: true`） | 10001、10003、10403、20001（export_id / user_id）、30417（`data.status`）、42901 | **每次**动态码；只限登记人；`password` 只在首次与重新生成时非空；`url` 有效至 `url_expires_at`（≤ 5 分钟）；响应 `Cache-Control: no-store` |
| adminGetUser | 成功后刷新详情 | 见 admin-user-detail.md | — |

## 5. 权限点与二次验证（04 §11.2）

- `user.realname_fix`（动态码）：实名更正；每次提交（含被拒）写审计。
- `user.phone_change`（动态码）：编辑会员信息，手机号与昵称都归它；保存确认里的「查看完整号码」同此权限，只显示本次输入（BR-ID-44 细则所录 BR-ID-06 细则原段落「保存确认里的查看完整号码」）。
- `user.data_export`：看副本请求列表（不需动态码）；登记（动态码）；下载（动态码，且另要 `pii.reveal_phone`）。
- `pii.reveal_phone`：登记被判为企业微信会话交付时必须持有（否则 10403），下载企业微信路径副本时每次必须持有。
- 下载只限登记人本人，超管也不能下载别人登记的请求（20001 `fields=[export_id]`，与不存在同样回答；AdmUserDataExportListOther）。
- 卡片显示：没有对应权限点的账号不显示该卡的按钮（admin-user-detail §5、AdmUserDetailNoPerm）；副本卡在只有 `user.data_export` 时仍显示（可看列表、可登记站内信路径）。

## 6. 稿上没画、实现要做的

- 动态码时机：沿用现有 StepUpModal——点带盾牌的按钮先弹动态码，拿到凭证再提交；凭证失效时服务端回 10003，再弹一次后自动重放同一请求（表单内容不丢）。每次都验，不做同档 5 分钟免验（§7 第 14 项定 A）。
- 实名更正：对话框关闭（含成功）后清空姓名、身份证号输入，不在本地存储或日志里留明文；输入框 `autocomplete="off"`。
- 实名更正成功后：刷新用户详情；身份证号格用响应的脱敏值，收款账号格加「已失效（实名更正）」（本页会话内由前端按成功响应标注；刷新后回到 adminGetUser 能给的内容，契约按 §7 第 8 项补字段后改读新字段）。
- 编辑会员信息：只发填了的字段——手机号框、昵称框留空就不发；填了就照发（昵称去首尾空格后发），不在前端与现值比对，与现值相同由服务端当作没改（审查 r2 S2-2 取 ①，与手机号的处理一致）。两项都留空时前端用「请至少修改手机号或昵称中的一项」拦下（汇总稿 20001 `[phone, nickname]` 行）。
- 编辑会员信息保存确认：每次保存都弹（§7 第 10 项定 B）；改了手机号时按 AdmUserEditConfirm，只改昵称时按 §1.4。
- 编辑会员信息「无改动」的提示：契约 200 不说明有没有改动。**这次提交了手机号就一律提示「会员信息已保存」**（脱敏号前 3 后 4，中间 4 位不同的新号保存前后 `phone_masked` 一样，不能据此判「没改」；而真改了号，该用户所有设备已被退出登录）；只提交了昵称时，比对保存前后的 `nickname`，没变才提示「会员信息没有变化」（汇总稿第 2 行）。§7 第 9 项定 B：契约线在响应里补 `changed_fields` 后改按它提示；**落地前先按本条实现**。
- 副本抽屉：登记 / 下载 / 重新生成成功后刷新列表并高亮相关行；`retry_of` 显示为「取代 …xxxx」；`failure_reason` 原样显示在状态下方（失败行）；`requested_by_name` 为 null 时显示「—」。
- 副本行内操作：站内信 + 短信交付的行写「用户在 App 内下载」；别人登记的企业微信行写「仅登记人可下载」；排队中 / 生成中写「生成后可下载」；失败 / 过期 / 取消写原因或「—」。
- 列表过时：下载前不先刷新；被拒（30417 / 20001 export_id）后自动刷新列表。
- 下载对话框：关闭前若没点过「复制口令」，用 Popconfirm 提醒「口令关闭后不能再查看」；口令不进剪贴板之外的任何地方（不写日志、不写本地存储）。「下载文件」直接打开 `url`；链接过期后再点行内「下载」重新签发（会再要动态码、`password=null`）。
- `password=null`（以后再下载、或首次下载无响应后的下一次）：下载对话框把口令块换成提示「这次没有新口令；如果没拿到上次的口令，请重新生成」（§1.4、§2 同此说法；汇总稿最后一行）。
- 429（`42901`）：按 Retry-After 禁用提交按钮，缺省 5 秒（BR-TEXT-14），三张汇总稿各有一行。
- 副本登记无响应：不自动重试，先刷新列表看有没有刚登记的请求（站内信 + 短信交付的请求可能已交付，重新登记会新建一条并再发一次短信）。
- 读屏：对话框 `role=dialog` / 确认框 `role=alertdialog`，被盖住的底层加 `aria-hidden`；错误条 `role=alert`，成功提示 `role=status`；字段错误用 `aria-invalid` + `aria-describedby`；行内下载按钮名称带请求末 4 位（「下载 …5d02」）。
- 关闭后焦点回到触发按钮（同 admin-user-detail §6）。
- 生成脚本没有跑 `fix-adm-tables.py` / `fix-adm-dialogs.py`（它们会扫全部 Adm 画板，可能改到已登记 sha 的稿）；本组画板已按这两个脚本的写法手写 role 与 aria。

## 7. 定稿决定

负责人 2026-10-31 17:47 在审阅页对本稿选「通过」，无备注、未逐条答待定项。按定稿流程，草稿 r2 §7 的 19 条待定按默认值处理，取值与方案选择用 TypeSafe Jev（`jev-latest`，2026-11-01 判断）判断后回写（规划/11 §7.3 第 13 项）；概率原样记在下表，负责人可随时推翻。各条的背景与选项全文见草稿 r2 §7（`F1-spec-drafts/admin-user-assist/admin-user-assist.md`）与变更说明 `docs/changes/20261101-后台客服代办三对话框定稿.md`。

| 编号 | 问题 | 采用项 | 结论（白话） | Jev 概率 | 要另开的任务 |
| --- | --- | --- | --- | --- | --- |
| 1 | 「个人信息副本」卡点开后是什么 | A | 点卡片按钮打开请求抽屉（列表 + 登记 + 下载），按钮改叫「个人信息副本」，卡片说明改成「首次登记日之后第 15 个工作日内提供（登记当天不计）」 | A 0.83、B 0.16 | 规格回写：`admin-user-detail.md` §1 末行副本入口改指 AdmUserDataExportList；卡片文字随 AdmUserDetail 换版（§9） |
| 2 | 旧稿 AdmUserRealnameFix 与契约对不上 | A | 入口改指 AdmUserRealnameForm，旧稿留作历史、不动 | A 0.82、B 0.23 | 规格回写：`admin-user-detail.md` §1 末行改指；design/README 标「被 AdmUserRealname* 取代」 |
| 3 | 旧稿 AdmUserDataExport 与契约对不上 | A | 入口改走请求抽屉、登记用 AdmUserDataExportForm，旧稿留作历史、不动 | A 0.71、B 0.26 | 同第 2 项 |
| 4 | 身份证号格式要不要页面先查 | A | 页面只拦没填；位数与校验码由服务端判，填错也留审计 | A 0.80、B 0.33 | 无 |
| 5 | 只更正一项时另一项怎么填 | A | 按用户在企业微信提供的证件原样填两项；不加「查看完整身份证号」，接口不改 | A 0.73、B 0.19、C 0.26 | 无 |
| 6 | 30419「不受理」各原因的说明句 | A | 用不带业务名的中性句，业务名由对话框标题说明；以画板句去掉业务名为底稿登记，`stage` 叫法（冷静期 / 处理中）一并登记 | A 0.73、B 0.47 | 规则回写：BR-TEXT-14 表 B `error.30419.<reason>` 7 个子键 + `stage` 叫法 |
| 7 | 副本状态与交付方式的叫法 | A | 照稿登记：排队中 / 生成中 / 待交付 / 已交付 / 失败 / 已过期 / 已取消；站内信 + 短信提取码 / 企业微信会话 | A 0.78、B 0.22 | 规则回写：BR-TEXT-25 `admin_dict.personal_data_copy_status.*`、`admin_dict.personal_data_copy_delivery.*` |
| 8 | 后台要不要能看到用户当前实名、实名状态和收款账号状态 | A | 请契约线给 adminGetUser 补脱敏实名（`masked_name`、`masked_id_no`）、`realname_status` 与收款账号状态；补上后对话框加「当前实名」一行、详情页三格有数据源。**补上之前实现不得依赖这些字段**，对话框按现稿只显示用户、绑定手机号、账号状态。两项概率接近（A 0.54、B 0.51）；**编排 2026-11-01 确认 A（D10-517）**：负责人 10-18 定稿的 admin-user-detail.md「基本信息」本来就有实名、身份证脱敏、收款账号三格，只是契约没给字段，不扩大个人信息展示范围；脱敏格式照 BR-ID-33，全量仍只走 reveal | A 0.54、B 0.51 | 契约：adminGetUser 补上述字段（编排已确认，派 identity 线 CT-26k） |
| 9 | 编辑会员信息保存后提示「已保存」还是「没有变化」 | B | 请契约线在 adminEditUserProfile 的 200 响应里加 `changed_fields`，页面照它提示。**落地前先按 A**：提交了手机号一律提示「会员信息已保存」；只提交昵称时比对保存前后 `nickname`，没变才提示「会员信息没有变化」（§6） | A 0.53、B 0.61、C 0.12 | 契约：adminEditUserProfile 响应补 `changed_fields` |
| 10 | 只改昵称要不要弹保存确认 | **B（与草稿建议 A 不同，以 Jev 为准）** | 只改昵称也弹保存确认，动态码在确认之后；只改昵称的确认框不含退出登录提示，也没有查看完整号码（§1.4、§2、§6） | A 0.49、B 0.68 | 无契约；画板补一张或按 §1.4 文字实现（§9） |
| 11 | 已登记 AdmUserEdit 把手机号、昵称都标必填 | A | AdmUserEdit 换版：去必填星号、手机号默认空、占位「不改手机号就留空」；Confirm / ConfirmReveal / PhoneTaken / Submitting 四张底层表单统一同一写法，重新登记 sha | A 0.72、B 0.18 | 画板修正（§9）+ design/README 重登 sha |
| 12 | 登记副本时只有一项「能」页面拦不拦 | A | 不拦，交服务端返回 30419 并写审计；判为企业微信路径而缺 `pii.reveal_phone` 时也不拦，规则表里提示 | A 0.79、B 0.22 | 无 |
| 13 | 要不要补画「有 user.data_export、没有 pii.reveal_phone」的整页稿 | B | 不补画，只保留汇总稿里的 10403 行；样例账号 cs.assist01 照 `sample-additions.md` 合并 | A 0.35、B 0.78 | 无 |
| 14 | 登记、每次下载、重新生成都要动态码，要不要 5 分钟免再输 | A | 每次都验（稿上画法）。08 §14.7「同档 5 分钟免验」这条全局规则日后若另定，按其变更说明改本页 | A 0.75、B 0.20 | 无 |
| 15 | 截止时刻的工作日口径 | 确认 | 截止时刻由服务端按 BR-ID-27 的工作日口径给 `due_at`，页面不算；样例按含调休算为 10-29 24:00，若口径不计调休，只把样例改成 10-30 24:00 | —（只需确认） | 无（样例如要改随画板，§9） |
| 16 | AdmUserRealnameRefused 放在哪个时点 | A | 保留 10-06（该用户当时有一笔未到账提现），不另造用户数据 | A 0.63、B 0.58 | 无 |
| 17 | 各种失败情况用对照表还是逐个画 | A | 保留三张 *Errors 对照表，不逐码补画 | A 0.78、B 0.26 | 无 |
| 18 | 编辑会员信息里「手机号已被占用」的提示句 | A | 新增场景子键 `error.30411.admin_profile`，以「该手机号已被其他账号使用，不能改到本账号」为底稿 | A 0.78、B 0.20 | 规则回写：BR-TEXT-14 表 B 新增 `error.30411.admin_profile` |
| 19 | 实名核验服务出错时用哪个错误码、提示什么 | A | 保持契约 50301；新增 `error.50301.realname_vendor`「实名核验服务暂时不可用，请稍后再试」；13 §13.11 把 50301 的含义扩到「外部服务不可用」（实名核验、短信供应商等）；App 自助实名 `app-real-name.md` 一并改指新子键 | A 0.60、B 0.11 | 规则回写：BR-TEXT-14 表 B 新增子键 + 13 §13.11 50301 含义；`app-real-name.md` 改指 |

补充说明：

- 第 8 项：选 A 只表示「请契约线补」，不是本页现在就能用；在契约补上并重新核对之前，§1.1、§2、§6 一律按「后台读不到当前实名」实现。实名更正成功后，本页会话内身份证号格用响应的 `masked_id_no`、收款账号格由前端按成功响应语义（全部失效）标「已失效（实名更正）」；刷新页面后这两格回到 adminGetUser 能给的内容，契约补上后改读新字段。
- 第 9 项：`changed_fields` 的形状（字段名、取值）由契约线定，前端不自拟；契约合并后再把 §6 的判断换成按它提示。
- 第 10 项：草稿 r2 建议 A（只改昵称不弹），Jev 判断取 B，本稿以 Jev 为准，§1.4、§2、§6 已同步改。
- 第 16 项：A、B 概率也接近（0.63 / 0.58），但只影响样例时点，不涉及规则或个人信息，按默认 A。
- 第 19 项：50301 的「未接入也回 50301」是 App 自助实名 submitRealname 的口径，adminCorrectUserRealname 契约只写了核验服务超时或出错回 50401 / 50301；后台是否也有「未接入」情况以契约为准，汇总稿那三个字随画板删（§9）。

## 8. 独立审查 r2 遗留的处理

审查 r2（`review-r2.md`）结论 pass：S0 / S1 都为 0，S2 2 条、S3 4 条。逐条处理如下。

| 编号 | 问题 | 处理 |
| --- | --- | --- |
| S2-1 | AdmUserDataExportCreatedInApp 的 …5d01 行写「已由 …5d02 重新登记」，与本分支（登记的是 …5d03）矛盾 | 画板错字，**定稿时随画板修正**（§9 第 1 条）；修正后 §1.3 这张稿的 sha 随之更新 |
| S2-2 | 「200（无改动）」行按 §6「昵称相同就不发」走不到，两处规则打架 | 采用审查建议 ①：§6 删掉「昵称去首尾空格后与现值相同就不发」，改为填了就照发、交服务端判；汇总稿「200（无改动）」行保留，不用改稿 |
| S3-1 | `sample-additions.md` ④ 的合并说明括号自相矛盾 | 不属规格与画板；合并样例时按文末「合并方式说明」操作，括号那句删掉（§9 第 8 条） |
| S3-2 | 画板张数写成 32 | 规格改为 31 张（Realname 9、Edit 8、DataExport 14），见文末校验行；`draft-result.md` 是过程记录，不再改 |
| S3-3 | §1.2 末段「只改了一处」说法过时 | §1.2 末段已补「PhoneTaken r2 另改错误条文案，且为手改稿、重跑生成脚本不覆盖」 |
| S3-4 | RealnameErrors 50301 行「（含未接入）」没有契约依据 | 画板文字，**随画板删**（§9 第 2 条）；规格 §7 补充说明已注明这是 App 端口径 |

## 9. 定稿后随画板修正

以下只记录、本稿没有改画板文件；画板由编排另行安排修改，改完重算 sha 并在 design/README 登记。修正前实现以本规格文字为准。

1. **AdmUserDataExportCreatedInApp**（dff7123b405f）：…5d01 行操作列「未交付即过期；已由 …5d02 重新登记」改为「…已由 …5d03 重新登记」（审查 r2 S2-1；改生成脚本里这张稿的替代 id 参数）。
2. **AdmUserRealnameErrors**（0a7b76e79fd2）：50301 行「实名核验服务出错或不可用（含未接入）」删去「（含未接入）」（审查 r2 S3-4）。
3. **AdmUserEdit**（已登记 4fb9af006f38）换版：去掉手机号、昵称的必填星号，手机号默认空、占位「不改手机号就留空」，说明条「手机号、昵称至少改一项，不改的留空或保持原值」，与 AdmUserEditNicknameInvalid 同写法；重新登记 sha（§7 第 11 项）。
4. **AdmUserEditConfirm / AdmUserEditConfirmReveal / AdmUserEditPhoneTaken / AdmUserEditSubmitting** 四张的底层表单统一成第 3 条的写法；这四张演示改手机号，可保留预填新号 `13900005678`，昵称框改为空（占位「不改昵称就留空」）（§7 第 11 项）。
5. **只改昵称的保存确认**（§7 第 10 项定 B）：可新增一张（建议名 AdmUserEditConfirmNickname），内容按 §1.4；不补画则按 §1.4 文字实现。
6. **AdmUserDetail 换版**（已登记底板）：「客服代办」区副本卡按钮改「个人信息副本」、卡片说明改「首次登记日之后第 15 个工作日内提供（登记当天不计）」（§7 第 1 项）；本组 31 张画板的底板沿用旧卡片文字，随 AdmUserDetail 换版一起改。
7. 待契约补字段后（§7 第 8 项）：AdmUserRealnameForm / StepUp / Submitting / Invalid / Refused / Mismatch 六张顶部 Descriptions 加「当前实名」一行；契约未补前不改。
8. 样例：`sample-additions.md` 合并进 `design-hifi/sample-data.md` §18 时删掉 ④ 那句自相矛盾的括号（审查 r2 S3-1）；若 BR-ID-27 不计调休，副本截止样例 10-29 24:00 改为 10-30 24:00（§7 第 15 项）；`draft-result.md` 注明 PhoneTaken 是手改稿、重跑生成脚本不覆盖（审查 r2 S3-3）。

校验（r2）：`cd design-hifi/project && python3 ../verify-admin.py`（脚本在 design-hifi/ 下；314 张 Adm 画板全部 OK，本组 31 张在内：Realname 9、Edit 8、DataExport 14；草稿写的 32 张有误，审查 r2 S3-2；审查 r2 复跑时全库 332 张 Adm 画板都 OK）；`cd design-hifi && python3 check-samples.py --rules` 0 条提示（r2 新样例尚未合并进 sample-data.md，见 `sample-additions.md`；合并前后都不会触发规则）。
