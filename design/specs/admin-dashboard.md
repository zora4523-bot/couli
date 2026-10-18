# 工作台 dashboard（管理后台）

- 核对版本：规划提交 408f6d3（负责人 2026-10-18 后台第 1 批定稿「全部按推荐」，`docs/changes/20261018-后台第1批定稿.md`）；代码主干 16b6f5aa（rebate-platform 远端 main，2026-10-18 核对；派发前再核对一次，对不上的写进第 7 节）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（PNG 在 `review-admin/png/`），不入公开仓库；完整 sha256 登记在 [design/README.md](../README.md) 第 15 项「管理后台第 1 批」
- 路由：后台资源 `dashboard`（菜单「工作台」，登录后落页）；从哪来：登录完成、侧栏菜单；去哪：每张卡直达对应列表并带筛选参数（提现审核 / 找回审核 / 月结账单 / 对账与差错 / 风控 · 申诉 / AI 助手记录 / 风控 · held 告警 / 联盟账号 / 打款队列 / 平台资金台账 / 紧急开关）
- 需求：01 F-ADM-26；验收：10 AC-S2-110、AC-S1-157（读屏与键盘）；任务：05 F1-14a（契约 CT-24 `dashboard`）
- 可参考的已合并页面：`apps/admin/src/App.tsx`、`layout/**`（antd 外壳）；配置中心页的 Card 写法
- 是否资金或归属页面：否（只读聚合；资金类状态卡受 `fund.view` 控制）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 正常（超管，全部卡） | AdmDashboard.dc.html（3718723d5323） | 持 `dashboard.view` 的账号登录后 | adminGetDashboard · 200 · example |
| 正常（按权限裁剪） | AdmDashboardFinance.dc.html（fc9ce929aa93） | 账号缺某些操作权限点 | 同上，响应里没有对应 `todo[]` 项 / `status` 字段 |
| 待办全为 0 | AdmDashboardStates.dc.html（fc31a2cac3d9）第三段 | 各 `count` 为 0 | 同上，count=0（卡仍显示） |
| 加载中 | 同上第一段 | 请求在途 | 本地：Card 骨架 + `role=status` |
| 出错 | 同上第二段 | 网络 / 5xx / 解析失败 | 本地：Result + 【重试】；不显示旧数据 |
| 无权限 | 不适用（无画板；零权限落 AdmHomeNoPerm.dc.html（57e50047eeae）） | 无 `dashboard.view` | 10403 admin_permission_denied；前端改落第一个有权限的菜单 |
| 1280 窄窗 | AdmAdaptDashboard1280.dc.html（c07d67b2541c） | 视口 ≤ 1280 | 本地 |

画板上的待办数、昨日概览数字、UID 与账号名均为样例数据，不对应真实用户。

## 2. 组件（03 §9.1 antd；布局约定 03 §9.2「工作台与一框搜」）

| 区域 | 组件 | 数据（接口字段） | 交互 |
| --- | --- | --- | --- |
| 标题行 | Typography.Title + 说明 + Button【刷新】 | `yesterday.as_of` | 刷新重新请求 |
| 待办 | Row/Col 4 列 × Card + Statistic（整卡为链接） | `todo[]`：`key`、`count`、`route`；卡标题与副文案按 key 取字典 | 点卡 navigate(route)；无对应项不渲染（不是置灰） |
| 昨日概览 | Card + Statistic ×4 | `yesterday.links`、`orders`、`est_rebate_fen`（后台金额格式，BR-TEXT-10）、`new_users` | 无 |
| 系统状态 | Card + Tag ×3 | `status.payout_queue_paused`、`payout_channel_paused[]`、`balance_w_expired`、`settle_auto_enabled` | 点卡进入打款队列 / 平台资金台账 / 紧急开关 |
| 「未关闭告警」位 | 本期不渲染，栅格位置保留（负责人 2026-10-18 第 1 批定稿 ①） | `open_alerts` 本期接口不返回 | — |
| 说明卡 | Alert（info） | — | — |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 待办卡标题、副文案、状态卡 Tag 中文名 | BR-TEXT-25 `admin_dict.*`（已有的行直接用；缺的行由契约线补，补齐前显示编码） |
| 出错提示 | BR-TEXT-14（10403.admin_permission_denied、通用网络错误） |
| 其余（说明卡、刷新按钮等） | 08 无键，用画板文案，登记 couli-runs/F1-frontend/needs.md（admin.dashboard.*） |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| adminGetDashboard | 进入本页、点【刷新】、每 5 分钟自动（可选） | 10001、10403、5xx |

## 5. 权限点与开关（04 §11.1 / §11.2）

`dashboard.view` 开页；每张待办卡按其权限点（`withdraw.review`、`order.claim`、`settle.bill`、`fund.recon`、`risk.appeal`、`agent.report`、`risk.freeze`、`union.account_auth`）；资金状态卡 `fund.view`。服务端裁剪，前端只按响应渲染。本页不做写操作。

## 6. 稿上没画、实现要做的

卡片等高；数字 ≥ 1,000 千分位；读屏：每张卡一个链接名「待审提现 12，进入提现审核」；窄于 1100 时 2 列；自动刷新不打断焦点。

## 7. 待定与不一致

- 「未关闭告警」卡：告警记录与关闭条件未定（CT-24 随 F1-14a），负责人 2026-10-18 第 1 批定稿按推荐：本期不做、位置保留；接口不返回 `open_alerts`（01 F-ADM-26 已注）。
- 昨日概览取「昨日整日」，与 07 §2 原「今日」不同，按 01 F-ADM-26。
- 无 `dashboard.view` 时「第一个有权限的菜单」的顺序按侧栏顺序，03 §9.2 未明写（实现按侧栏顺序，不停）。
