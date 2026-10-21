# 授权管理 AuthManage（App 原生）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`AuthManage`（auth login，入口 in_app / push，不能由深链打开，`agent_guide`）；从哪来：设置「账号与安全」、Agent 页面引导卡；去哪：与购买同一授权流程（`AuthSheet` / 淘宝备案、拼多多备案），授权完回本页刷新、不重放购买；联系客服
- 需求：01 §4.2 `AuthManage` 行；F-LINK-03；规则只引编号：BR-ID-17 细则「授权管理页」、BR-ID-18、BR-ID-19、BR-ID-22、BR-ID-24、BR-TEXT-24、03 §10.2 `PlatformBadge`；验收：AC-S1-102、AC-S1-146、AC-S1-158、AC-S1-185；任务：APP-06、HM-05
- 可参考的已合并页面：原生三端仓库派发前核对
- 是否资金或归属页面：是（授权决定后续订单归属的前提）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 正常 | AuthManage-v2.dc.html（6ec2c5069bca） | 进页 | listUnionBindings · 200（items[].platform、status）；样例为淘宝已授权、拼多多未授权 |
| 淘宝返利被停用 | AuthManageBlocked-v2.dc.html（574ac747fe2d） | 该平台被停用 | listUnionBindings；不给【去授权】，给【联系客服】（表 A 30153） |
| 其他结果一览（设计证据） | AuthManageStates.dc.html（15de53bd2b70） | ① 授权完成回来刷新；② 站长授权暂不可用；③ 30151 | ① listUnionBindings；② getUnionAuthUrl · 30101 / 30102 reason=auth_unavailable（不拉起授权、不外跳）；③ bindUnion · 30151（保持未授权） |
| 深色 | AuthManageDark.dc.html（6d723fa682b2） | 系统深色 | 同正常；平台图标按图片处理 |
| 授权中途取消 | 不适用（无画板） | 用户取消或未完成 | 保持「未授权」，不另提示（BR-ID-18） |
| 加载失败 / 断网 | StateLoadFailed.dc.html（aea7c5d30a24）、StateNetworkError.dc.html（022db8798446） | 请求失败 / 无网络 | 50001；本地 |

## 2. 组件

| 区域 | 组件（03 §10.2） | 数据 | 交互 |
| --- | --- | --- | --- |
| 平台行 | `PlatformBadge`（20px 官方图标，读屏读平台中文名）+ 状态「已授权 / 未授权」+【去授权】 | platform、status | 【去授权】只能由用户点击发起（routes.json 注）；不显示淘宝账号名、昵称、头像 |
| 底部说明 | 一行说明 | — | 不支持自助更换授权的淘宝账号（BR-ID-19） |
| 结果提示 | 轻提示 | 错误码 | 不出购买类按钮 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 标题、状态、按钮 | BR-TEXT-14 表 C `auth_manage.title` / `.status.authorized` / `.status.unauthorized` / `.action.authorize` |
| 底部说明 | 表 C `auth_manage.rebind_note` |
| 被停用 | 表 A `error.30153` |
| 暂不可用 | 表 B `error.30101.auth_unavailable`、`error.30102.auth_unavailable` |
| 绑定冲突 | 表 A `error.30151` |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| listUnionBindings | 进页、授权回来 | 10001 |
| getUnionAuthUrl | 点【去授权】 | 30101、30102、30153、50301 |
| bindUnion | 授权回调后 | 20001、30101、30102、30104、30151、30153、10405 |

## 5. 权限点与开关

平台状态与站长授权按 `/v1/config.features.platform_status` 与 BR-ID-24；京东无需用户授权，不列行（BR-ID-22）。

## 6. 稿上没画、实现要做的

授权回跳（`apps.json` 入站回调）后刷新与焦点；授权状态读屏；从 Agent 卡片打开时先过统一入口守卫（03 §4.4）。

## 7. 待定与不一致

- `30101.auth_unavailable`「淘宝暂时无法下单…」与 30151「…本次购买无法获得返利」都按购买写，用在授权管理页不贴切，建议加授权管理页子键，待上游（BR-TEXT-14）。
