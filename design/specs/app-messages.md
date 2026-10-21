# 消息中心 Messages（App 内 H5）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`Messages`（h5 `/messages`，auth login，入口 in_app / push，`agent_guide`）；从哪来：「我的」、推送点击回查不到落点或未登录时（BR-ID-10 细则「推送点击的落点」）、Agent 页面引导卡；去哪：消息的 `route`（订单详情、提现记录、余额流水、账号状态、申诉进度、注销页等）
- 需求：01 §4.2 `Messages` 行；F-MSG-02、F-MSG-03；规则只引编号：BR-TEXT-09（交易通知模板）、BR-TEXT-23（账号与风控站内信）、BR-TEXT-05、BR-TEXT-11（时间写法）、BR-ID-10 细则、BR-ID-27 细则（冷静期）、BR-ID-30（留存）；验收：AC-MSG-03（同号规则）、AC-S1-81、AC-S1-157、AC-S1-185；任务：F1-04（H5）、APP-12（入口）
- 可参考的已合并页面：`apps/h5/src/entries/app/pages/notices/**`（列表与时间写法）
- 是否资金或归属页面：否（只读通知，金额只为展示）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 列表（交易通知） | Messages-v2.dc.html（bb6b6607c6fc） | 有消息 | listMessages · 200（items[].code、title、body、created_at、read_at、route） |
| 空态 | MessagesEmpty.dc.html（94d15c9ab971） | 没有消息 | listMessages · 200，items 置空 |
| 注销进度（撤回后） | MessagesDeletion-v2.dc.html（93ba88f2b3b4） | 有 DELETION_PROGRESS 消息 | 同上；模板 BR-TEXT-23 |
| 注销被系统撤销（余额为负） | MessagesDeletionNegative.dc.html（af24fdc4dd84） | 冷静期满时余额为负（BR-ID-27） | 同上；DELETION_PROGRESS cancelled_negative |
| 订单申诉结果 | MessagesOrderAppeal-v2.dc.html（086f4e43a147） | 订单申诉结案 | 同上 |
| 账号与风控（冻结用户 / 解封后） | MessagesRiskFrozen-v2.dc.html（857c88b5655f）、MessagesUnbanned-v2.dc.html（c22ee9eb6ca5） | RISK_STATE_CHANGED；解封时淘宝绑定为 invalid 才带 `{need_reauth}` 一句 | 同上；BR-TEXT-23（unbanned）、BR-ID-20 |
| 其他消息类型一览（设计证据） | MessagesCatalog.dc.html（4c923c97f4e2） | 不是真实页面，按 code 取模板 | 同上；金额与日期只为展示写法 |
| 深色 | MessagesDark.dc.html（a20422604b81） | 系统深色 | 同列表 |
| 加载失败 / 断网 | StateLoadFailed.dc.html（aea7c5d30a24）、StateNetworkError.dc.html（022db8798446） | 请求失败 / 无网络 | 50001；本地 |

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 导航栏 | 标题 +「全部已读」（14px） | unread | 调 markMessagesRead；冷静期内的处理见 §7 |
| 消息行 | 未读点 + 标题 + 正文 + 时间（BR-TEXT-11：今天 / 昨天带时刻，同年更早写月-日） | title、body、created_at、read_at | 有 `route` 才可点，经 `nav.open`；`title_short` 按字素截取 |
| 加载更多 | 列表底 | next_cursor | 游标翻页 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 交易通知正文 | BR-TEXT-09 模板（服务端渲染，`body`） |
| 账号、风控、申诉、注销正文 | BR-TEXT-23 模板（服务端渲染） |
| 加载失败 | 表 C `h5.load_failed` / 表 A `error.50001` |
| 「全部已读」、空态两句、各类消息标题 | 08 无键（消息标题由 04 `inbox_messages.title` 承载），用画板措辞，待回写 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| issueH5Token（经桥） | 进页 | 10405 |
| listMessages（契约 planned） | 进页、翻页、重试 | 10001 |
| getMessage | 推送回查后定位一条 | 30701 |
| markMessagesRead（planned） | 「全部已读」、点开一条 | 20001、10405 |
| getUnreadMessageCount（planned） | 「我的」角标 | — |

## 6. 稿上没画、实现要做的

未读状态读屏播报；时间按设备时区与 BR-TEXT-11 替换样例；点开后未读点消失的焦点处理；长列表虚拟化。开关：无本页开关；推送开关在通知设置（[app-notify-settings.md](app-notify-settings.md)）。画板上的消息时间线按 `couli-runs/design-hifi/sample-data.md` §12；扣回金额写负值（BR-TEXT-02 写法）。

## 7. 待定与不一致

- 冷静期内「全部已读」与记已读会调 `markMessagesRead`，不在 BR-ID-27 冷静期白名单；建议冷静期隐藏「全部已读」、不记已读，或放进白名单，待上游（编排 / Jev）。
- 04：`markMessagesRead` 请求形状（逐条或全部）、`getUnreadMessageCount` 显示位置未定，待上游（契约线）。
- BR-TEXT-23 细则末尾「进度只在注销进度页查询」与 BR-ID-27 细则矛盾；cancelled_negative 模板「后续返利抵扣回正」与 BR-TEXT-01「待抵扣」释义不一致，待上游（08 内部同步）。
- 邀请类消息的跳转：flow-map §23.2.21 写「不跳转」，BR-TEXT-09 为进余额流水；本页按 08，待上游（设计文档回写）。
