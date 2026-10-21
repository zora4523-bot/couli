# 填写邀请码 InviteBackfill（App 原生）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`InviteBackfill`（只在 App 内打开，BR-ID-10 细则路由入口矩阵）；本规格只管「我的」来源（补填提示条「去填写」）；登录后新号一步（登录来源，带选填说明与【跳过】）按登录 v2 定稿 `LoginInviteFill*`；去哪：成功轻提示后回来源页（「我的」见 [app-me.md](app-me.md) `MeInviteBound`）
- 需求：01 §4.2 `InviteBackfill` 行；F-INV-02、F-INV-11（扫码，本批未画）；规则只引编号：BR-INV-02、BR-INV-03 细则「登录成功后的新号步骤」、BR-INV-04、BR-INV-07、BR-INV-16 细则「告知位置」、BR-ID-16 细则（本页为敏感页面）、00 D36 ③；验收：AC-INV-02（同号规则）、AC-S1-182、AC-S1-158、AC-S1-185；任务：APP-05、APP-17、HM-05、HM-13
- 可参考的已合并页面：原生三端仓库派发前核对（登录 v2 的填写邀请码页同一组件）
- 是否资金或归属页面：是（写邀请关系，影响分佣受益人）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 输入 | InviteBackfill-v2.dc.html（4974164c60d1） | 从「我的」补填提示条进入 | 本地；`InviteLink` 拉起时预填（01 §4.2） |
| 邀请码无效 | InviteBackfillError-v2.dc.html（fb0d4d436218） | 提交返回 30401 | bindInviter · 30401；输入框下就地红字 |
| 其他提交结果一览 | InviteBackfillErrorStates.dc.html（16b7a693347c） | 30403、42901、30408、30404、30402、30409、50001、粘贴未识别 | bindInviter 对应错误码；粘贴未识别为本地（BR-INV-04） |
| 成功 | MeInviteBound.dc.html（d87097d0aaa9，登记在 [app-me.md](app-me.md)） | bindInviter · 200 | 轻提示后回来源页，不出结果页 |
| 深色 | InviteBackfillDark.dc.html（3f320d442449） | 系统深色 | 同输入 |
| 提交中 | 不适用（无画板） | 请求在途 | 本地：【确认绑定】置灰防连点 |

作废不实现：`InviteBackfillDone`、`InviteBackfillBound`、`InviteBackfillExpired`、`InviteBackfillHasOrders`（结果改为就地红字或轻提示，BR-INV-03 细则）。

## 2. 组件

| 区域 | 组件（03 §10.2） | 数据 | 交互 |
| --- | --- | --- | --- |
| 标题 | 单一标题（无顶栏副标题），左上返回 | — | 返回不绑定 |
| 输入框 | 输入框，框内【粘贴】 | 用户输入；规范化按 BR-INV-02 | 粘贴读剪贴板只在用户点击时（BR-ID-16）；识别不到就地提示 |
| 错误行 | 输入框下一行红字 | 错误码 | 修改输入后清除 |
| 主按钮 | 通栏【确认绑定】 | — | 空输入置灰；「我的」来源没有【跳过】与选填说明 |

不显示对被邀请人的告知句、截止时间与规则说明（负责人 2026-10-19，D36）。

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 标题 | BR-TEXT-14 表 C `invite.post_login.title` |
| 成功轻提示 | 表 C `invite.bound_toast` |
| 错误行 | 表 A `error.30401`、`.30402`、`.30403`、`.30404`、`.30408`、`.30409`、`.42901`、`.50001` |
| 输入占位「6 位邀请码」、粘贴未识别 | 08 无键（BR-INV-04 正文有句），用画板文案，待回写 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| bindInviter | 点【确认绑定】 | 10005、30401、30402、30403、30404、30408、30409、42901、10405 |
| getMe | 成功后回来源页重取 | — |

## 6. 稿上没画、实现要做的

键盘弹起时【确认绑定】贴键盘上方；错误行读屏即时播报；扫码填邀请码（F-INV-11）本批未画，随登录线另定；大字号下标题换行。开关：`growth.invite_bind.enabled` 关闭时提交得到 30408；入口显隐取 getMe `invite_backfill`（BR-INV-07）。

## 7. 待定与不一致

- 契约 `routes.json` 尚无 `InviteBackfill`（01 §4.2 有），待上游（契约线）。
- 30401 文案：登录 v2 `LoginInviteFillError` 用了表 A 以外的句子，本页按表 A；两处统一待上游（改表 A 或改登录稿）。
- 42901 / 30402 在 BR-INV-06 细则、BR-INV-09 正文的说法与表 A 不同；本页按表 A，待上游（08 内部同步）。
- 表 C `invite.post_login.optional_hint` 写死天数，按 BR-TEXT-13 应由 `backfill_hours` 渲染（只影响登录来源），待上游。
- 契约 `texts.default.json` 尚无 `invite.post_login.title`、`invite.bound_toast`，待契约线同步。
