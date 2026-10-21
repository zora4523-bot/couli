# AI 助手 AgentChat · 找货部分（App 原生）

- 核对版本：规划提交 b8b7dac（负责人 2026-10-21 定稿，`docs/changes/20261021-App内高保真第1批定稿.md`）；代码主干 67d7a4df（2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>.dc.html`（PNG 在 `review-shop/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 1 批定稿」
- 路由：`AgentChat`（auth none；参数 `context`；入口 in_app、push）；从哪来：首页【问 AI】、商品详情【问问 AI】、搜索输入页「试试这样搜」、识别结果【让 AI 帮我看看】；去哪：`ProductDetail`、`Search`、`Login` / `BindPhone`（次数用完）
- 范围：本规格只含找货与查返利（01 J3，D2、D16）；订单与收益问答见 [app-agent-chat-orders.md](app-agent-chat-orders.md)（第 2 批），页面引导卡见 [app-agent-chat-page-guide.md](app-agent-chat-page-guide.md)（第 3 批）
- 需求：01 F-AGENT-01～05、F-AGENT-08、F-AGENT-11、F-AGENT-13～15、F-AGENT-17、F-CLIP-04；验收：AC-AGENT-xx（同号规则）；任务：05 APP-10 / HM-08
- 可参考的已合并页面：无（派发前按代码主干核对）
- 是否资金或归属页面：否（卡片购买走 [app-product-buy.md](app-product-buy.md)）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 空态 | Agent-v2.dc.html（ef0d8bd31910） | 新对话首屏 | createAgentSession / getCurrentAgentSession |
| 首次单独同意 | AgentConsent.dc.html（6f38f0bb21e1） | 未做 AI 单独同意（BR-ID-14） | 10004；同意后 recordConsent |
| 生成中 | AgentStreaming-v2.dc.html（fd721027e8b2） | run 进行中 | sendAgentMessage + 流（`agent-stream.schema.json`，fixture normal） |
| 结果完整 | AgentResult-v2.dc.html（e9731f5bb0d0） | run 正常结束 | 同上 |
| 无结果 | AgentNoResult-v2.dc.html（9fbd0ad99262） | 检索为空 | notice `agent.notice.no_result` |
| 模型降级 | AgentDegraded-v2.dc.html（40942d8477ec） | F-AGENT-13 降级 | fixture fallback |
| 部分平台失败 | AgentPartialFail-v2.dc.html（20b3ff61be73） | 某平台工具失败 | fixture tool-failed |
| AI 暂不可用 | AgentUnavailable-v2.dc.html（ac9cf2bb3d2c） | 降级也失败 / 未开放 | 50302、30501 |
| 连接中断 | AgentDisconnected-v2.dc.html（249b22c2109e） | 流断开 | fixture disconnected；本地重连 |
| 次数用完（游客 / 未绑手机） | AgentQuotaGuest-v2.dc.html（974831cedca6）、AgentQuotaPhone-v2.dc.html（ec6fb6d03a85） | 当日配额用完（BR-ID-03、BR-AI-15） | 30502 |
| 举报 / 已提交 | AgentReport-v2.dc.html（da2316cd2ad5）、AgentReported-v2.dc.html（be5efdb9579f） | 点举报 / 提交后 | reportAgentMessage |
| 剪贴板查返利卡 | AgentClipboardCard.dc.html（4092777116fa） | 本页自动识别到商品（03 §4.6「AgentChat 页」） | parseInput · 200（不是 AI 回复） |
| 深色 | AgentResultDark.dc.html（6408def6c888） | 系统深色（00 D35） | 同浅色 |

画板上的商品、价格、返利、对话内容均为样例数据。

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 消息流 | 文本（03 §7.3）、`AiLabel`、notice 卡；同意用 `AgentConsentSheet` | 流事件 | 【停止】调 cancelAgentRun；点赞 / 点踩、举报 |
| 商品卡 | `ProductCard`、`PlatformBadge`（14px）、`MatchBadge`、`RebateTag`、`BuyButton`、`DisclaimerFooter` | 卡片事件 | 卡片 → `ProductDetail`；购买见 app-product-buy；下架卡另给【换一批】 |
| 输入区上方胶囊 | iOS UIPasteControl / 鸿蒙 PasteButton【粘贴】+ 旁边说明；Android 自绘胶囊 | — | 手动粘贴任务，结果出查返利卡 |

## 3. 文案键

胶囊说明：`clipboard.paste_hint.agent`；提示卡：`agent.notice.*`（BR-TEXT-22）；AI 标识：`ai_label`（BR-TEXT-16）；口径：`price_basis`、`price_basis.general`；错误：BR-TEXT-14 表 A 30501、30502、50302。

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| createAgentSession / getCurrentAgentSession / listAgentSessionMessages | 进页、新对话 | 30501、10001、10004、10005、30504 |
| sendAgentMessage | 发送 | 30502、30506、50302、42901、50001、50401 等（契约 x-error-codes） |
| cancelAgentRun | 【停止】 | 30505 |
| setAgentMessageFeedback / reportAgentMessage | 反馈、举报 | 20001、30504 |
| parseInput | 胶囊粘贴、本页自动识别 | 30131、30132 |

## 6. 稿上没画、实现要做的

键盘弹起时输入区上移、消息流可滚动；流式文本的读屏播报节奏按 03 §10.5；Android 胶囊直接写 `clipboard.paste_hint.agent` 的文字。

## 7. 待定与不一致

- 待上游（规划）：03 §7.5 空态胶囊写「粘贴链接查返利」，与 08 `clipboard.paste_hint.agent` 不一致；以 08 为准、画板按 08 画，03 待回写（清单第 6 条）。
- 待上游（契约）：`texts.default.json` 暂无 `clipboard.paste_hint.agent`。同意文本正文仍待法务（BR-ID-14），画板沿用原稿。
