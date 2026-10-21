# 我的 Me（App 原生）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`Me`（Tab「我的」，auth none，入口 in_app / push）；去哪：钱包与提现（第 2 批 [app-wallet.md](app-wallet.md)、[app-withdraw.md](app-withdraw.md)）、订单、`InviteShare`、`InviteBackfill`、`Favorites`、`ShareHub` / `Earnings`（公开版）、`Messages`、`Help`、`Settings`、联系客服（[app-contact-cs.md](app-contact-cs.md)）、`Login`
- 需求：01 §4.1「我的」、§4.2 `Me` 行；F-INV-02、F-INV-06、F-MSG-07、F-WDR-01（余额卡口径）；规则只引编号：BR-TEXT-01、BR-TEXT-10 细则「金额隐藏」、BR-INV-03 细则、BR-INV-07、BR-INV-18、BR-INV-19、BR-WDR-05 细则、BR-ID-02 细则、BR-ID-13 细则；验收：AC-S1-62、AC-S1-105、AC-S1-84、AC-S1-158、AC-S1-185；任务：APP-12、HM-08（深色 DS-02）
- 可参考的已合并页面：原生三端仓库派发前核对
- 是否资金或归属页面：否（只读显示余额摘要；提现在 `Withdraw`，见 [app-withdraw.md](app-withdraw.md)）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 已登录（内测版） | Me.dc.html（63524bac6c77） | 已登录、内测包 | getMe · 200 · example（balance、invite_code、inviter_bound） |
| 已登录（公开版） | MeEarningsEntry.dc.html（8ebac9f53fe2） | 公开版：宫格多「分享赚」「收益看板」 | 同上；宫格显隐见 §5 |
| 游客 | MeGuest.dc.html（5d2e6b070643） | 未登录 | 不调 getMe；只有帮助中心、设置（BR-ID-02 细则） |
| 金额已隐藏 + 通知引导条 | MeHidden.dc.html（689a0823ec00） | 本机偏好隐藏金额；通知权限被拒后（BR-ID-13 细则） | 本地：金额隐藏偏好、系统通知权限状态 |
| 可补填邀请码 | MeInviteBackfill-v2.dc.html（b3f9a0369ed8） | `invite_backfill` 表示仍可补填（BR-INV-07） | getMe · invite_backfill；截止时刻只用于判断提示条显隐，不显示 |
| 补填成功回到本页 | MeInviteBound.dc.html（d87097d0aaa9） | 从 `InviteBackfill` 绑定成功返回 | bindInviter · 200 后重取 getMe；顶部轻提示 |
| 未满 18 周岁 | MeMinor.dc.html（2f8c3f44b8b6） | 不能邀请（BR-INV-19） | getMe · invite_code=null（见 §7） |
| 余额卡【提现】其他状态 | MeStates.dc.html（9d15fd5093b8） | 待抵扣、提现关闭、风控冻结 | getMe · balance、risk；提现关闭的判定同 [app-wallet.md](app-wallet.md)；冻结时【提现】不置灰，点了留在本页轻提示 30303.account_frozen |
| 深色 | MeDark.dc.html（77cd55030482） | 系统深色（00 D35） | 同已登录 |
| 加载失败 / 断网 | StateLoadFailed.dc.html（aea7c5d30a24）、StateNetworkError.dc.html（022db8798446） | getMe 失败 / 无网络 | 50001、5xxxx；本地断网 |

## 2. 组件

| 区域 | 组件（03 §10.2） | 数据 | 交互 |
| --- | --- | --- | --- |
| 身份卡 | 昵称 + 默认头像、我的邀请码（复制）、「邀请人：已绑定 / 未绑定」 | nickname、invite_code、inviter_bound | 复制邀请码轻提示；不显示等级（BR-INV-18） |
| 可提现余额卡 | 狸橙实底主卡 + 【提现】+ 小眼睛 | balance.*（口径 BR-TEXT-01） | 金额隐藏只改本机显示（BR-TEXT-10 细则） |
| 补填提示条 | 提示条 +「去填写」 | invite_backfill | 进 `InviteBackfill`（「我的」来源） |
| 通知引导条 | 提示条 + 去设置 | 系统权限 | 只在被拒后出现（BR-ID-13 细则） |
| 分组宫格 | 订单与钱包 / 推广与邀请 / 更多服务 | — | 按路由跳转；授权状态摘要不放本页（06 第 9 项） |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 通知引导条 | BR-TEXT-14 表 D `perm.push.guide_bar` |
| 小眼睛 | 表 C `amount_mask.show` / `.hide` |
| 补填成功轻提示 | 表 C `invite.bound_toast` |
| 提现置灰说明 | 表 A `error.30302`、`error.30306`；表 B `error.30303.account_frozen` |
| 余额卡标签 | BR-TEXT-01 术语 |
| 游客卡、宫格名、分组名、补填提示条 | 08 无键，用画板文案（待回写，变更记录待回写清单） |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getMe（getConfig 启动时已取：宫格开关、邀请配置） | 进入、回前台、从子页返回 | 10001（会话失效转游客态）、50001 |

## 6. 稿上没画、实现要做的

金额隐藏后读屏播报「金额已隐藏」类提示；轻提示播报顺序；大字号与窄屏下宫格换行；深色下余额卡按令牌不变（review-me README §4 第 23 条）。开关：公开版宫格「分享赚」随分享在公开版显示（TRADE-21）；「收益看板」受 `features.earnings.dashboard.visible`；收藏夹格不做开关隐藏（F-PROD-12）。画板上的昵称、邀请码、金额与「最早预计 10 月结算」均为样例（同第 2 批 Wallet）。

## 7. 待定与不一致

- getMe 只用 `invite_code=null` 表示不能邀请，不区分未成年（`MeMinor`：隐藏邀请码与「推广与邀请」组）与其他暂不可邀请（`InviteShareUnavailable-v2` 仍从宫格进入）；隐藏整组的判定待上游（契约线 / BR-INV-18、BR-INV-19）。
- 01 §4.1「我的」行仍写「淘宝 / 拼多多授权状态」，已被 §4.2 `Me` 行（06 第 9 项）取代，待上游（规划同步）。
- 游客卡、宫格与补填提示条的文案 08 无键，待上游（BR-TEXT-14 补键）；契约 `texts.default.json` 尚无 `invite.bound_toast`，待契约线同步。
