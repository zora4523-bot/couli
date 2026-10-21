# 账号状态 RiskNotice（App 原生）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`RiskNotice`（auth login，入口 in_app / push）；从哪来：封禁用户任一请求得到 10006、钱包顶部「提现已暂停」提示（冻结）、站内信；去哪：`Appeal`（提交申诉 / 查看进度，[app-appeal.md](app-appeal.md)）、联系客服、`DeleteAccount`（公开版）、退出登录
- 需求：01 §4.2 `RiskNotice` 行；F-RISK-04；规则只引编号：BR-ID-31（细则「封禁期间看提现进度」）、BR-ID-36（细则「维持后再申诉」）、BR-TEXT-23、BR-WDR-25、BR-TEXT-07；验收：AC-RISK-04（同号规则）、AC-S1-60、AC-S1-158、AC-S1-185；任务：APP-12、HM-08
- 可参考的已合并页面：第 2 批钱包冻结态与提现记录（原生仓库派发前核对）
- 是否资金或归属页面：否（只读状态与在途提现进度）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 封禁 | RiskNoticeBanned-v2.dc.html（8c6270eba567） | risk.state=banned | getMe · risk（reason_category）；在途提现行取 listWithdrawals（只显示非终态单，BR-ID-31 细则） |
| 封禁 · 申诉中 | RiskNoticeBannedAppealing-v2.dc.html（1ee8c613ca2b） | 申诉处理中（原处罚为封禁） | getMe · risk；listAppeals |
| 封禁 · 申诉维持后 | RiskNoticeBannedUpheld-v2.dc.html（590aeb864498） | 最近一次申诉被维持 | listAppeals；维持后可马上再申诉 |
| 冻结（有期限） | RiskNoticeFrozen.dc.html（f11e629fb6a9） | risk.state=frozen 且有 frozen_until | getMe · risk（reason_category、frozen_until） |
| 冻结 · 申诉中 | RiskNoticeFrozenAppealing.dc.html（eaea66bca604） | 申诉处理中（原处罚为冻结） | getMe · risk；listAppeals |
| 其他写法一览（设计证据） | RiskNoticeStates.dc.html（97b956d881d0） | ① 冻结不定期（frozen_until 为空）；② 同一处罚第 3 次申诉被维持（不再显示【提交申诉】） | getMe · risk；listAppeals |
| 深色 | RiskNoticeDark.dc.html（fd65380f1a8a） | 系统深色 | 同冻结有期限 |

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 状态卡 | 标题 + 说明 + 原因 / 期限 / 预计恢复 | risk.* | 封禁期限写「不设期限，直到解除」（BR-ID-31 说法）；不显示申诉处理时限（BR-TEXT-23 细则） |
| 在途提现行 | 金额 · 状态 + 副文案 | withdrawals 非终态 | 状态与副文案同提现记录（BR-WDR-25） |
| 申诉区 | 最近一次申诉结果 +【提交申诉】/【查看申诉进度】 | appeals | 次数用尽后不显示提交 |
| 底部出口 | 「联系客服 \| 注销账号 \| 退出登录」 | — | 内测包去掉「注销账号」；退出登录沿用 `settings.logout.*` 确认框 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 状态说明 | BR-TEXT-23 账号与风控模板 |
| 提现状态与副文案 | BR-WDR-25、BR-TEXT-07（同提现记录） |
| 退出登录确认 | BR-TEXT-14 表 C `settings.logout.*` |
| 页面标题与说明句、申诉区各句 | 08 无键，用画板文案，待回写 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getMe | 进页（10006 白名单内） | — |
| listAppeals | 进页（10006 白名单内） | — |
| listWithdrawals（契约 planned） | 封禁时进页 | — |
| logout | 退出登录 | — |

## 6. 稿上没画、实现要做的

冻结期满后回前台刷新状态；读屏顺序按状态、原因、期限、出口；10006 落页的去重（同一时刻只打开一次）。开关：「注销账号」只在公开版（BR-ID-27 细则）。画板上的原因类别、金额与时间为样例（冻结同第 2 批 `WalletRiskFrozen-v2`）。

## 7. 待定与不一致

- `RiskInfo.state=appealing` 时契约没有返回原处罚（prev_risk_state），申诉中的封禁与冻结两种写法无法区分（冻结不定期时 frozen_until 也为空），待上游（契约线 / 04）。
- `BannedUpheld` / 「第 3 次被维持」要按同一处罚统计已申诉次数，契约 listAppeals 未给计数或处罚分组，待上游（契约线）；第 4 次申诉被拒的码与文案未分配（BR-ID-36）。
- 冻结且申诉中到期：08 未写，画板按到期照常恢复、申诉照常结案画，待上游（编排 / Jev）。
- 画板设计说明写在途提现「数据来自 GET /v1/me」，按 BR-ID-31 细则应取 `GET /v1/withdrawals`；契约 listWithdrawals 描述未写 10006 白名单，待契约线核对。
- flow-map §20.3 ②3「处理到终态后这一行显示结果」与 BR-ID-31 细则（只显示未到终态的单）不符，本页按 08，待上游（设计文档回写）。
