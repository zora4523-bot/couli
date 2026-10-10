# 后台账号列表 admins（管理后台）

- 核对版本：规划提交 c9a505f；代码主干 6eadf2b（整理 2026-10-10，f1-frontend-6）
- 路由：后台资源 `admins`（菜单「系统 / 后台账号与权限」，resources SUPER_ONLY）；从哪来：侧栏菜单；去哪：本任务无出口（新建、权限设置、停用另立任务）
- 需求：F-ADM 后台账号；任务：F1-06i（05 F1-06）；11 §2.6 试点页（最小骨架，只限超管）
- 可参考的已合并页面：`apps/admin/src/App.tsx`、`layout/**`（F1-06p 后的 antd 外壳）、`pages/login/**`（antd Form 写法）
- 是否资金或归属页面：否

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 正常 | AdmAdmins.dc.html（57a1c1672461） | 超管打开本页 | adminListAdmins · 200 · example |
| 空 | 不适用（无画板） | items 为空 | 同上，列表置空 |
| 加载中 | 不适用（无画板） | 请求在途 | 本地：antd Table loading |
| 出错 | 不适用（无画板） | 网络 / 5xx / 解析失败 | 本地：Result 或 Alert + 【重试】 |
| 无权限 | 不适用（无画板） | 非超管直接访问 | 10403 data.reason=admin_permission_denied；菜单本就隐藏（SUPER_ONLY） |

## 2. 组件

| 区域 | 组件（antd，03 §9.1） | 数据（接口字段） | 交互 |
| --- | --- | --- | --- |
| 标题与说明 | Typography.Title + Alert（info，role=note） | — | — |
| 列表 | Table（rowKey=admin_id） | username、is_super（类型）、permissions.length（权限点，超管显示「全部」）、totp_bound（动态码：已绑定 / 未绑定）、verify_phone_masked（null 显示「未登记」）、status + locked_until（启用 / 已停用 / 已锁定 至 HH:mm）、created_at（日期） | 表头语义由 Table 提供 |
| 分页 | Table pagination（服务端分页，page / page_size ≤ 200） | total | 切页重新请求 |

## 3. 文案键

08 字典没有本页的键：用画板文案，登记 couli-runs/F1-frontend/needs.md（admin.admins.*），放 `texts/admins.ts`。

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| adminListAdmins | 进入本页、切页、点【重试】 | 10001（登录失效，交 auth provider）、10403、20001（page_size） |

## 5. 权限点与开关

只限超管（x-auth: super；资源 SUPER_ONLY）。不演示按权限点裁剪、导出、批量操作（11 §2.6）。

## 6. 稿上没画、实现要做的

加载、空、出错三态；表格横向溢出时 Table scroll；读屏：表格有表头、状态文字不只靠颜色。

## 7. 待定与不一致

- 画板「名称」列、「最近登录（时间 + IP）」列：契约 AdminAccount 没有 display_name / last_login 字段——暂不实现，等契约补字段（转 admin 后端线）。
- 画板筛选条（账号或名称、类型、状态 + 查询 / 重置）：契约 adminListAdmins 没有筛选参数——暂不实现，同上。
- 画板【新建账号】、操作列（权限设置 / 停用 / 启用、超管「不可修改」）：契约写明「Creating, disabling and ticking permission points come with a later task」——本任务不做，另立任务（画板 AdmAdminCreate*、AdmAdminPermissions*、AdmAdminDisable 已有）。
