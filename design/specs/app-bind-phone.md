# 绑定手机号 BindPhone（App 原生，非登录入口）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`BindPhone`（auth login，入口 in_app，`agent_guide_account: phone`）；本规格只管从功能进入（邀请、Agent 查订单与查收益、补填邀请码、剪贴板邀请码绑定，BR-ID-02 身份矩阵）；登录后新号的整页引导按登录 v2 定稿 `LoginBindPhoneGuide-v2`；验证码页版式同登录 v2 `LoginBindPhoneCode`；去哪：成功后按 BR-ID-10 恢复原动作，补填与剪贴板邀请码入口回 `InviteBackfill`；返回则回来源页、不执行原动作
- 需求：01 §4.2 `BindPhone` 行；F-ACC-11、F-ACC-12；规则只引编号：BR-ID-05、BR-ID-06、BR-ID-10、BR-INV-03 细则、BR-TEXT-14 表 C `invite.bind_phone_guide.*`；验收：AC-ACC-11、AC-ACC-12（同号规则）、AC-S1-59、AC-S1-68、AC-S1-158、AC-S1-185；任务：APP-05、HM-05
- 可参考的已合并页面：登录 v2 的绑手机与验证码组件（原生仓库派发前核对）
- 是否资金或归属页面：是（并号会合并账号）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 填写手机号 | BindPhone-v2.dc.html（4fdff9d70e97） | 从需要手机号的功能进入 | 本地；空输入时【获取验证码】置灰；点后 sendSmsCode（purpose=bind） |
| 6 格验证码 | 不适用（同登录 v2 `LoginBindPhoneCode`） | 发码成功 | 输满自动调 bindPhone |
| 手机号属老账号、引导并入 | BindPhoneMerge-v2.dc.html（d89ad26e1582） | bindPhone · 30411 reason=mergeable（服务端按 BR-ID-06 判定） | 【并入】凭 `merge_ticket` 调 mergeAccount；【取消】回验证码页并清空格子 |
| 深色 | BindPhoneDark.dc.html（80a6aaaf5641） | 系统深色 | 同填写手机号 |
| 验证码错误 / 过期 | 不适用（同登录 v2 `LoginCodeError`） | 20002 / 20003 | 格子清空标红 |
| 号码被拦 | 不适用（无画板，44001 弹窗同 `login.risk_blocked.desc_send` 结构） | 44001 | 见 §7 |

## 2. 组件

| 区域 | 组件（03 §10.2） | 数据 | 交互 |
| --- | --- | --- | --- |
| 标题区 | 标题 + 副标题 + 提示条 | — | 左上返回；没有【暂不绑定】 |
| 手机号输入 | 「+86」次要色前缀 + 输入框 | 用户输入（BR-ID-05 规范化） | 通栏【获取验证码】 |
| 验证码页 | `CodeInput`（6 格，输满自动提交）+ 倒计时 + 求助入口 | — | 规格同登录 v2 r6 |
| 并入弹窗 | 确认框【取消】【并入】 | merge_ticket | 并入后以老账号登录、回来源页 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 标题、副标题、提示条 | BR-TEXT-14 表 C `invite.bind_phone_guide.title` / `.benefit` / `.merge_hint` |
| 倒计时、求助入口 | 表 C `login.code.countdown`、`login.code.help_entry` |
| 并入弹窗正文 | 表 B `error.30411.mergeable` |
| 错误 | 表 A `error.20002`、`.20003`、`.30411`、`.44001`、`.42901` |
| 「已绑定手机号」轻提示、并入弹窗标题与「并入到 / 手机号账号 {phone}」 | 08 无键，用画板文案，待回写 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| sendSmsCode | 【获取验证码】、重新获取 | 20001、44001、44003、42901、10405 |
| bindPhone | 6 格输满 | 20001、20002、20003、30411、44001、10405 |
| mergeAccount（契约 planned） | 并入弹窗【并入】 | 20001、30411、50001、10405 |
| getMe | 成功后 | — |

## 6. 稿上没画、实现要做的

键盘弹起时按钮贴键盘；验证码错误的读屏播报；并入弹窗焦点；`pending_action` 恢复（BR-ID-10）。开关：`invite.bind_phone_guide` 只控制登录后新号的引导，不影响本页（04 §10.1）。样例号码只用脱敏写法 139****0246（`sample-data.md` §12）。

## 7. 待定与不一致

- 首次绑定遇到 44001 的正文：`phone_change.risk_blocked.desc` 的「当前手机号不变」不适用，08 无专用键，待上游（BR-TEXT-14 补键）。
- 登录 v2 稿上 `.merge_hint` 的改写句漏了找回申请与目标账号条件（BR-ID-06），本页用 08 原文；登录稿同步待上游。
- 契约 `texts.default.json` 尚无 `invite.bind_phone_guide.benefit` / `.merge_hint`、`login.code.*`，待契约线同步。
