# 用户查询 users（管理后台）

- 核对版本：规划提交 408f6d3（负责人 2026-10-18 后台第 1 批定稿「全部按推荐」，`docs/changes/20261018-后台第1批定稿.md`）；代码主干 16b6f5aa（rebate-platform 远端 main，2026-10-18 核对，后端 F1-07a/b 列表与 lookup 已 done；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（PNG 在 `review-admin/png/`），不入公开仓库；完整 sha256 登记在 [design/README.md](../README.md) 第 15 项「管理后台第 1 批」
- 路由：后台资源 `users`（菜单「用户与订单 / 用户查询」）；从哪来：侧栏、工作台、一框搜（多命中）；去哪：用户详情 `users/{id}`、导出记录
- 需求：01 F-ADM-04；验收：AC-ADM-04（同号规则）、10 AC-S2-59（`user.list` / `user.lookup` / `pii.*` 裁剪）、AC-S1-157；任务：05 F1-07（前端）
- 可参考的已合并页面：`apps/admin/src/pages/admins/**`（Table + 分页写法）
- 是否资金或归属页面：否

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 正常 | AdmUsers.dc.html（d4329585aec8） | 持 `user.list` 打开 | adminListUsers · 200 · example |
| 空 | AdmUsersStates.dc.html（480cc63b87da）第一段 | 条件无结果 | 同上，items 置空 |
| 加载中 | 同上第二段 | 请求在途 | 本地：Table loading（骨架） |
| 出错 | 同上第三段 | 网络 / 5xx / 解析失败 | 本地：Result + 【重试】，条件保留 |
| 只有 lookup | 不适用（无画板） | 无 `user.list`、有 `user.lookup` | 列表不可浏览，只能按 UID / 完整手机号 / 订单号查单个（adminLookupUser） |
| 无权限 | 不适用 | 两者都无 | 菜单隐藏；10403 |

画板列表里的 UID、昵称、脱敏手机号、邀请码、余额均为样例数据；风控状态值为样例。

## 2. 组件（03 §9.1 antd）

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 筛选卡 | Form（inline，4 列）：Input（UID、手机号、邀请码）、Select（风控状态、淘宝授权）、RangePicker（注册时间）+【查询】【重置】 | 查询参数同契约 | 查询后显示「已应用」条 |
| 列表 | Table（rowKey=user_id）：UID、昵称、手机号（脱敏）、邀请码、等级、淘宝授权、风控状态（Tag）、可用余额（后台金额格式，BR-TEXT-10）、注册时间、操作【详情】 | items[] 字段 | 【详情】进详情页 |
| 分页 | Table pagination（服务端） | total | 切页请求 |
| 标题行 | 【导出】【导出记录】 | — | 创建导出任务（`export`）；成功用 message 提示并指向导出记录 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 风控状态、授权状态中文名 | BR-TEXT-25 `admin_dict.risk_state.*`、`admin_dict.union_bindings.status.*`（后者契约线补行，补齐前显示编码） |
| 出错、无权限提示 | BR-TEXT-14（10403.admin_permission_denied、通用网络错误） |
| 其余（筛选标签、列头、导出按钮） | 08 无键，用画板文案，登记 admin.users.* |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| adminListUsers | 进入、查询、切页、重试 | 10001、10403、20001 |
| adminLookupUser | 只有 lookup 时按单个标识查 | 同上；无结果返回空 |
| adminCreateExport | 点【导出】 | 10403（无 export） |

## 5. 权限点与开关（04 §11.1）

`user.list`（浏览）、`user.lookup`（逐个查）、`export`（导出；未勾选 `pii.*` 导出脱敏值）。

## 6. 稿上没画、实现要做的

手机号须完整 11 位才提交；表格横向溢出 scroll；读屏：行操作名「详情 U10023」；「已应用」条用 `aria-live=polite`。

## 7. 待定与不一致

- `user.lookup` 是否支持订单号：契约 CT-02j 待核（后台缺口审计 §6 待核 ①）；定前按 04 §11.1 的写法（UID、完整手机号、订单号）做输入校验。
