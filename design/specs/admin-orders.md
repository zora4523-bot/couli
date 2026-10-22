# 订单查询 orders（管理后台）

- 核对版本：规划提交 408f6d3（负责人 2026-10-18 后台第 1 批定稿「全部按推荐」，`docs/changes/20261018-后台第1批定稿.md`）；代码主干 16b6f5aa（rebate-platform 远端 main，2026-10-18 核对，无 admin 订单契约，待 CT-24 `orders` 与 F1-07e；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>`（PNG 在 `review-admin/png/`），不入公开仓库；完整 sha256 登记在 [design/README.md](../README.md) 第 15 项「管理后台第 1 批」
- 路由：后台资源 `orders`（菜单「用户与订单 / 订单查询」）；从哪来：侧栏、一框搜、用户详情订单页签；去哪：订单详情 `orders/{id}`、手动同步、同步记录、维权 / 违规导入、导出记录
- 需求：01 F-ADM-05（F-ADM-25 为 P1，不在本页）；验收：AC-ADM-05（同号规则）、10 AC-S2-59、AC-S1-157；任务：05 F1-07e
- 可参考的已合并页面：`apps/admin/src/pages/admins/**`
- 是否资金或归属页面：否（只读列表；归属与资金操作在详情）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 正常 | AdmOrders.dc.html（1c3ac708e1cb） | 持 `order.view` | adminListOrders · 200 · example |
| 空 | AdmOrdersStates.dc.html（73070371e3a0）第一段 | 条件无结果 | 同上，items 置空 |
| 加载中 / 出错 | 同上第二、三段 | 在途 / 失败 | 本地 |
| 宽表横向滚动 | AdmAdaptOrdersWideTable.dc.html（9905d20e0535） | 列放不下 | 本地：Table scroll.x |
| 手动同步 / 同步记录 | AdmOrderSync（f9056167321e）/ AdmOrderSyncRecords（8b00d0ca32cd） | 标题行按钮 | adminCreateOrderSync · 同步记录列表 |
| 维权 / 违规导入 | AdmRightsImport.dc.html（f31ad8e7922d） | 标题行按钮 | adminCreateRightsImport（结果稿 AdmRightsImportResult 随 F-ORD-10 登记） |
| 无权限 | 不适用 | 无 `order.view` | 菜单隐藏；10403 |

画板上的订单号、商品名、UID、金额均为样例数据；平台列只以文字标识来源，无平台商标图形。

## 2. 组件（03 §9.1 antd）

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 标题行 | Title + 【导入维权 / 违规】【同步记录】【手动同步】 | — | 分别打开导入、同步记录、手动同步 |
| 筛选卡 | Form（4 列）：Select（平台、platform_status、rebate_status、订单标记）、Input（订单号、用户）、RangePicker（paid_at） | 查询参数 | 查询 / 重置 |
| 列表 | Table（rowKey=sub_order_id）：订单号、平台、商品、用户、付款时间、付款金额、联盟佣金、平台状态（Tag + 编码）、返利状态（Tag + 编码）、标记（归属已锁定 / 维权中 / 暂停 / 已锁定）、操作【详情】 | items[] | 【详情】进详情 |
| 分页 | Table pagination（服务端） | total | 切页 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 平台状态 / 返利状态 / 标记中文名（双列：中文 + 编码，BR-TEXT-18） | BR-TEXT-25 `admin_dict.platform_status.*`、`admin_dict.rebate_status.*`（契约线补行，补齐前显示编码） |
| 出错、无权限提示 | BR-TEXT-14 |
| 其余（筛选标签、列头、按钮） | 08 无键，用画板文案，登记 admin.orders.* |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| adminListOrders | 进入、查询、切页、重试 | 10001、10403、20001 |
| adminCreateOrderSync | 【手动同步】提交 | 10403、20001、50301（站长授权失效期间，04 §6.6 `order-syncs`，2026-10-22） |
| adminCreateRightsImport | 导入提交 | 10403、20001；渠道单另有 10003（动态码，编排裁定 D10-152） |

## 5. 权限点与开关（04 §11.1 / §11.2）

`order.view`（查询、手动同步）；`order.claim`（维权导入）；渠道单导入另需 `risk.blocklist` 与动态码（编排裁定 D10-152，04 §11.2 `order.claim`、08 BR-ATTR-26 细则「渠道单导入」）；`export`。

## 6. 稿上没画、实现要做的

金额列后台格式（BR-TEXT-10）；订单号等宽字体；读屏：行操作名「详情 TB…」；筛选「已应用」条；导出创建成功用 message 提示并指向导出记录。

## 7. 待定与不一致

- 2026-10-22 摘要同步（`docs/changes/20261022-后台风控联盟订单接口形状.md`）：§4 补手动同步的 50301；画板不变。按编排裁定 D10-152：渠道单导入另需 `risk.blocklist` 与动态码（通用二次验证弹窗承载）；维权单须逐子单列明，只有主订单号的行记逐行失败；可选按 time_basis 的时间窗筛选行，结果多一个「跳过」计数。
- 列表与筛选字段以 CT-24 `orders` 契约为准；F-ADM-25 的平台标签组合、失效原因、店铺筛选不在本期。
