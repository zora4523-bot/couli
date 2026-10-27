# 通知设置（App 原生，`Settings` 子页）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：无独立路由（`Settings` →「通知」进入，需要登录）；去哪：系统设置（【去设置】）
- 需求：01 §4.2 `Settings` 行；F-MSG-04、F-MSG-07；规则只引编号：BR-ID-13 细则「通知权限的申请时机」、BR-TEXT-14 表 D `perm.push.*`；验收：AC-MSG-04（同号规则）、AC-S1-84、AC-S1-158、AC-S1-185；任务：APP-12、HM-08
- 可参考的已合并页面：原生三端仓库派发前核对
- 是否资金或归属页面：否

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 系统通知已关闭 | NotifySettings.dc.html（078b68c7a982） | 系统权限被拒或关闭 | 本地：系统通知权限；getNotificationSettings · service_push |
| 系统通知已开启 | NotifySettingsOn.dc.html（8fac5337de42） | 系统权限已允许 | 同上；没有权限提示条 |
| iOS 从未申请过 | NotifySettingsNotAsked.dc.html（03b8c6b8eea1） | iOS 权限状态为「未决定」 | 本地；只给中性提示，不给按钮、不在本页申请（首次申请只在待跟单卡，BR-ID-13 细则） |
| 深色 | NotifySettingsDark.dc.html（0a70a74ac8f1） | 系统深色 | 同已关闭 |
| 保存失败 | 不适用（无画板） | update 失败 | 开关回到原值并轻提示 50001 |

## 2. 组件

| 区域 | 组件（03 §10.2） | 数据 | 交互 |
| --- | --- | --- | --- |
| 权限提示条 | 提示条 +【去设置】 | 系统权限状态 | 打开系统设置；回前台重读权限 |
| 开关行 | 只有「服务类推送」一个开关（F-MSG-04） | service_push | 切换即调 updateNotificationSettings |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 已关闭提示条 | BR-TEXT-14 表 D `perm.push.denied_forever` |
| 【去设置】 | 表 D `perm.go_settings` |
| 服务类推送说明句、iOS 未申请时的提示句 | 08 无键，用画板文案，待回写 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getNotificationSettings（契约 planned） | 进页 | 10001 |
| updateNotificationSettings（planned） | 切换开关 | 20001、10405 |

## 5. 权限点与开关

无业务开关；系统通知权限由各端权限组件读取（03 §4.9）。

## 6. 稿上没画、实现要做的

开关读屏状态；从系统设置返回后的刷新；鸿蒙、Android 权限状态映射到三种画法。

权限状态到画法的映射（2026-10-27 编排裁定 D10-374 G-S14）：「系统通知已开启」只用于已允许；`NotifySettingsNotAsked` 只用于 iOS「未决定」；Android（含 13+ 未申请过）与鸿蒙的其余状态（拒绝、未申请、不可用）一律画「系统通知已关闭」（提示条 +【去设置】，只打开系统里本 App 的通知设置，不在本页申请权限，BR-ID-13 细则）。

## 7. 待定与不一致

- BR-ID-13 细则「通知设置页里同样给去系统设置的入口」在 iOS 从未申请过时走不通；本页按「首次申请只在待跟单卡」画中性提示（`NotifySettingsNotAsked`），请在 BR-ID-13 细则补一句，待上游。
