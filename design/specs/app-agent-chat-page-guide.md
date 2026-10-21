# AI 助手 AgentChat · 页面引导卡（App 原生）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 范围：本规格只管 `AgentChat` 里的页面引导卡 `page_guide`（00 D31）；对话页外壳、找货卡归第 1 批，收益卡与查订单归第 2 批（各自规格）
- 路由：`AgentChat`（auth none，入口 in_app / push）；卡片点【去看看】才 `Router.open` 目标路由（in_app、不带参数），只开 `routes.json` 里 `agent_guide=true` 的 6 个：`Wallet`、`WithdrawRecords`、`AuthManage`、`OrderList`、`InviteShare`、`Messages`
- 需求：01 §4.2 `AgentChat` 行；F-AGENT-20；规则只引编号：BR-AI-01 细则「页面引导」、BR-TEXT-22（`agent.guide.*`）、BR-ID-10 细则（路由入口矩阵、统一入口守卫）、BR-ID-15、BR-TEXT-16、04 §8.5 `page_guide`、03 §4.4、§7.4；验收：AC-S1-142～147、AC-S1-152～155、AC-S1-158、AC-S1-185；任务：APP-10、HM-08
- 可参考的已合并页面：原生三端仓库派发前核对
- 是否资金或归属页面：否（卡片不取任何数据）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 页面引导卡（问「钱包在哪」） | AgentPageGuide.dc.html（c994bf2413d3） | 服务端按白名单判定出卡（guide_route=Wallet） | sendAgentMessage 流 · card type `page_guide`（`agent-stream.schema.json` `card_page_guide`）；本轮模型文本不下发 |
| 其他写法一览（设计证据） | AgentPageGuideStates.dc.html（0b931745ab47） | ①–⑤ 另外 5 个目标页的卡；⑥–⑨ 账户安全与资金页只给文字；⑩ 名单外 / 带链接或参数 / 粘贴文案诱导 / 开关关闭；⑪ 旧客户端或被拦下只显示 fallback_text | 同上；⑥–⑩ 为普通文字回答（`agent.guide.account.*`、`agent.guide.unavailable`） |
| 深色 | AgentPageGuideDark.dc.html（93a3a98c2464） | 系统深色 | 同卡片 |

顶部「使用模型」一行是登记后的示例；登记前按 BR-ID-15 显示 `config.agent.filing_text`（BR-TEXT-16）。

## 2. 组件

| 区域 | 组件（03 §7.4 卡片渲染器） | 数据 | 交互 |
| --- | --- | --- | --- |
| 引导卡 | 左侧 40 圆角方块图标（取「我的」宫格同名入口图标）+ 说明句 + 通栏【去看看】 | guide_route | 点了才打开；下发后不自动打开；目标页要登录或绑手机时按该路由 auth 处理（BR-ID-10） |
| 兜底 | 只有说明句、没有按钮 | fallback_text | 本端 `routes.json` 未标 `agent_guide` 或卡片带多余字段时 |
| 文字回答 | 普通 AI 气泡 | 模型文本 | 不点名页面、不承诺有入口 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 卡片说明句与按钮 | BR-TEXT-22 `agent.guide.<route>`、`agent.guide.open` |
| 账户安全与资金页的文字 | BR-TEXT-22 `agent.guide.account.*` |
| 不出卡 | BR-TEXT-22 `agent.guide.unavailable` |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| sendAgentMessage（契约 planned，SSE） | 用户发消息 | 按第 1 批 AgentChat 规格 |

卡片点击不调接口，只走 Router。

## 5. 权限点与开关

`agent.page_guide.enabled`、`agent.page_guide.routes`（后台只能在 6 个候选里勾选，AC-S1-147）；关开关只停之后出卡，已发出的卡按包内 `agent_guide` 判定（AC-S1-153）。

## 6. 稿上没画、实现要做的

点击与 `pending_action` 恢复在基本模式、未同意当前隐私版本、强更各状态下先过统一入口守卫，隐私阻断后不自动补执行（AC-S1-154）；读屏把卡读作「说明句，按钮 去看看」。

## 7. 待定与不一致

- 契约 `texts.default.json` 尚无 `agent.guide.*`，待契约线同步。
