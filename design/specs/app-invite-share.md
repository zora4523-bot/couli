# 邀请好友 InviteShare（App 内 H5）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`InviteShare`（h5 `/invite`，auth phone，入口 in_app / push，`agent_guide`）；从哪来：「我的」宫格、Agent 页面引导卡；去哪：余额流水 `Ledger`、`Help`（邀请规则、邀请奖励活动规则文章）、系统分享 / 保存图片
- 需求：01 §4.2 `InviteShare` 行；F-INV-06、F-INV-12；规则只引编号：BR-INV-16、BR-INV-17、BR-INV-18 细则、BR-INV-19、BR-INV-20、BR-INV-24（⑨ 显示位置、有效期）、00 D9 / D34 ③ / D36；验收：AC-INV-06（同号规则）、AC-S2-112、AC-S1-157、AC-S1-185；任务：F1-05、F1-15
- 可参考的已合并页面：`apps/h5/src/entries/app/pages/help/**`（H5 壳与状态组件）
- 是否资金或归属页面：否（只展示邀请码、链接与直邀人数；奖励发放在服务端）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 可邀请（奖励活动无效） | InviteShare-v2.dc.html（8bcd1fbfb42f） | `can_invite` 为真，`invite.reward_enabled` 为假（含默认） | getMyInvite · 200（invite_code、landing_url、poster_url、direct_count）；getConfig · invite |
| 可邀请（奖励活动有效） | InviteShareReward.dc.html（859b68194f91） | `invite.reward_enabled` 为真 | 同上 + getConfig · invite.reward_amount_fen、eligibility_days |
| 暂不可邀请 | InviteShareUnavailable-v2.dc.html（388fc83a1a31） | `can_invite` 为假 | getMyInvite · 200；不显示奖励活动卡（§7） |
| 邀请海报 | PosterInvite-v2.dc.html（887f00a3eefb） | 点【保存海报】预览 / 保存 | getMyInvite · poster_url（服务端按固定模板出图，TECH-13） |
| 深色 | InviteShareDark.dc.html（8648a72219aa） | 系统深色 | 同可邀请；海报按图片处理不换色 |
| 未成年 | 不适用（无画板；入口在「我的」已隐藏） | 30413 | getMyInvite · 30413 |
| 未绑手机 | 不适用（路由 auth phone 先走 `BindPhone`） | 10005 | getMyInvite · 10005 |
| 加载失败 / 断网 | StateLoadFailed.dc.html（aea7c5d30a24）、StateNetworkError.dc.html（022db8798446） | 请求失败 / 无网络 | 50001；本地 |

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 邀请码卡 | 大号邀请码 +【复制邀请码】【复制邀请链接】【保存海报】 | invite_code、landing_url、poster_url | 复制后轻提示；保存海报走桥的相册权限（BR-ID-13） |
| 人数卡 | 「已邀请好友 n 人」+ 说明（收益在余额流水看） | direct_count | 点说明进 `Ledger`；没有好友列表（`InvitedFriends` 为 P1，BR-INV-16） |
| 邀请奖励活动卡（仅活动有效） | 品牌浅底奖励句 + 活动规则摘要 +「活动规则 ›」 | reward_amount_fen（金额按 BR-TEXT-10） | 进 `HelpArticleInviteReward` 文章（[app-help.md](app-help.md)） |
| 邀请规则卡 | 规则摘要 +「完整规则 ›」 | 文本（§7） | 活动无效时末条为「不发放红包或现金奖励」一句（BR-INV-18 细则） |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 奖励句（邀请人看） | BR-TEXT-14 表 C `invite.reward.tip_inviter` |
| 复制成功 | 表 C `invite.copy_code.done`、`invite.copy_link.done` |
| 错误 | 表 A `error.30413`、`error.10005`、`error.50001` |
| 按钮、标签、人数卡说明、规则摘要四条与活动规则五条、暂不可邀请说明、海报文字 | 08 无键，用画板文案（规则正文待 06 Q-F4，待回写） |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| issueH5Token（经桥 `auth.getH5Token`） | 进页 | 10405 |
| getMyInvite | 进页、重试 | 10005、30413 |
| getConfig（经桥读取） | 进页 | — |

## 6. 稿上没画、实现要做的

保存海报的相册权限说明与被拒处理（BR-ID-13）；复制按钮读屏名带对象；大字号下规则卡换行；海报长按保存与分享面板按端。开关：`/v1/config.invite.reward_enabled`（由 `growth.invite_reward.*` 与预算派生，04 §10.1、BR-INV-24）切换活动卡与「不发放」一句；`growth.invite_bind.enabled` 关闭时绑定返回 30408（影响被邀请人，不改本页）。画板上的昵称、邀请码、人数「3 人」、奖励金额与有效天数均为样例。

## 7. 待定与不一致

- 规则摘要四条与活动规则五条是设计起草，正文待负责人提供（06 Q-F4），待上游。
- BR-INV-18 细则写「显示 invite.reward.tip」，表 C 与 BR-INV-24 ⑨ 是 `invite.reward.tip_inviter`；本页按后者，待上游（08 内部同步）。
- 暂不可邀请时不显示奖励活动卡是保守默认（08 未写），待上游（编排 / Jev）。
- 海报不写任何奖励说法、活动有效与无效同一张（海报无活动状态变量，BR-INV-18 细则），如需改模板待上游。
- 契约 `texts.default.json` 尚无 `invite.copy_code.done`、`invite.copy_link.done`，待契约线同步。
