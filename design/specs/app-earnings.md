# 收益看板 Earnings（App 内 H5，M-公开）

- 核对版本：规划提交 32a9765（负责人 2026-10-21 定稿 App 内高保真第 2 批，`docs/changes/20261021-App内高保真第2批定稿.md`）；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-money/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 2 批定稿」
- 路由：`Earnings`（h5，`h5_path` /earnings，auth login，参数可选 `platform`，各端 `since` 尚为 null）；从哪来：钱包、「我的」页入口（开关打开时）；去哪：无（只读）
- 需求：01 F-WDR-14；规则只引编号：BR-FUND-25（口径、期间、没有收益时）、BR-TEXT-01（术语与 `earnings.*` 键）、BR-TEXT-24（平台图标）、BR-INV-16 / BR-INV-17（邀请栏不可反推）；验收：AC-WDR-14（同号）、10 AC-S2-61；任务：05 F1-12（H5）、B2-13（接口）
- 可参考的已合并页面：`apps/h5/src/entries/app/pages/help/**`（H5 三态）、`apps/h5/src/components/platform/PlatformBadge.tsx`
- 是否资金或归属页面：是（只读展示，不参与资金计算）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 全部平台（本月） | Earnings-v2.dc.html（e9ba66bd9739） | 进入页面，不带 platform | getEarningsSummary · 200 · example |
| 按平台筛选 | EarningsPlatform-v2.dc.html（174279b9b2c7） | 选中某平台胶囊（只筛自购、分享两栏） | getEarningsSummary（platform=taobao 等） |
| 没有收益 | EarningsEmpty-v2.dc.html（b89225356690） | 各期间全为 0（不做整页空态，BR-FUND-25 细则「没有收益时」） | 同上，各项为 0 |
| 指标说明 | EarningsMetricNote-v2.dc.html（5485ffd51a49） | 点指标旁问号 | 本地 |
| 深色 | EarningsDark.dc.html（3d17b69efb5a） | 系统深色（00 D35） | 同全部平台 |
| 今日 / 昨日 / 上月、邀请栏关闭、已结算为负 | 不另出（版式同上，README 第 1 节） | 切期间；referral 为 null；credited_fen < 0 | 同上 |
| 看板关闭 | 不适用 | 总开关关闭 | 30701（入口本应已隐藏） |
| 加载、出错 | 不适用（无画板；按 H5 三态） | — | 本地；`h5.load_failed` |

画板上的金额与笔数为样例。

## 2. 组件

| 区域 | 组件 | 数据（接口字段） | 交互 |
| --- | --- | --- | --- |
| 期间切换 | 分段控件 | 期间枚举 | 切换只换显示，不重新算 |
| 平台筛选 | 32 高胶囊 + 16px 官方平台图标（`PlatformBadge` 图标，装饰、读屏读平台中文名） | platform | 重新请求带 platform；邀请栏不受筛选（BR-FUND-25） |
| 自购、分享两栏 | `AmountGrid`（付款笔数、预估、已结算 + 问号） | self / share 下各期间 {paid_count, est_fen, credited_fen} | 问号开说明 `Sheet` |
| 邀请栏 | `AmountGrid`（只有金额） | referral.this_month / last_month {est_fen, credited_fen}；null 时整栏不显示 | 栏内说明 `earnings.referral.note`、`.platform_note`，位置按画板 |
| 统计时点行 | 副文字 | as_of | 没有收益时后接 `earnings.empty_hint` |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 标题、栏名、期间、指标名与说明、邀请栏说明 | `earnings.title`、`earnings.section.*`、`earnings.period.*`、`earnings.metric.*.name` / `.hint`、`earnings.referral.note` / `.platform_note`（BR-TEXT-01） |
| 没有收益 | `earnings.empty_hint` |
| 「统计截至今天 10:00」 | 08 无键（第 7 节）；时间按 BR-TEXT-11 |
| 金额 | BR-TEXT-10（已结算为负带负号） |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| issueH5Token（桥 `auth.getH5Token`） | 进页取令牌 | 10405 |
| getEarningsSummary | 进页、切平台、下拉 | 30701（`earnings.dashboard.enabled` 关闭） |

## 5. 权限点与开关

入口 `features.earnings.dashboard.visible`（由 `earnings.dashboard.enabled` 派生，04 §10.1）；邀请栏 `earnings.dashboard.referral_visible`（关闭时 referral 为 null）。各端 `since` 为 null，W6 随 F1-12 开放。

## 6. 稿上没画、实现要做的

今日 / 昨日 / 上月与邀请栏关闭的显示（版式同已有稿）；已结算为负的写法；胶囊命中区 ≥ 44、筛选项播报选中；大字号与窄屏。

## 7. 待定与不一致

- 待上游（08 BR-TEXT-14 补键）：统计时点行「统计截至今天 10:00」为原稿措辞，无字典键（数值取 as_of）。
- 待上游（契约线）：`earnings.empty_hint` 已在 08，`contracts/texts.default.json` 尚未收录。
