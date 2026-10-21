# 版本更新：强制更新 ForceUpdate 与首页可选更新提示（App 原生）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- **底稿首页以第 1 批 `Main-v3` 为准**：`MainUpdatePrompt-v2`、`MainUpdatePromptDark` 背后的首页仍含负责人 2026-10-21 已定删除的「确认收货后，返利随联盟月度结算入账」一句与粘贴入口副标题「支持淘宝、京东、拼多多」（第 1 批 v1.1 对抗评审 V1-14）；首页按第 1 批 `Main-v3` / `MainDark` 实现，本规格只管弹窗本身；画板下次改稿时同步
- 路由：`ForceUpdate`（auth none，入口 in_app）；可选更新提示是 `Home` 上的弹窗，不是路由；什么时候出现：冷启动、回前台超过复查间隔、任一接口返回 10405（03 §4.1、F-CFG-03）；去哪：应用商店（【去更新】）、`PrivacyCenter`（强更状态，[app-privacy-center.md](app-privacy-center.md) `PrivacyCenterForceUpdate`）、`DeleteAccount`（受限会话）、`Login`（受限登录，见 §7）
- 需求：01 §4.2 `ForceUpdate` 行；F-CFG-03；规则只引编号：BR-ID-01 细则（商店核对、受限会话）、BR-ID-27 细则、03 §4.1、§4.4（强更状态下的路由与桥调用）、`design/app-icon/README.md`；验收：AC-CFG-03（同号规则）、AC-S1-83、AC-S1-81、AC-S1-154、AC-S1-158、AC-S1-185；任务：APP-02、HM-02
- 可参考的已合并页面：原生三端仓库派发前核对
- 是否资金或归属页面：否

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 首页 · 可选更新提示 | MainUpdatePrompt-v2.dc.html（b4780f118e85） | 本机低于 recommended_version、不低于 min_supported_version | checkAppVersion · 200（update_title、update_notes；稿上为示例）；【暂不更新】的记录方式见 03 §4.1 |
| 强制更新 · 去更新 | ForceUpdate-v2.dc.html（b78478684ed4） | 本机低于 min_supported_version，或 10405 | checkAppVersion（store_url、default_store、stores）；按 BR-ID-01 细则选商店 |
| 强制更新 · 暂时无法更新 | ForceUpdateUnavailable-v2.dc.html（726b568b3a09） | 候选商店的已上架版本都低于目标或都打不开 | 同上；不打开商店、不给下载地址；稿为冷静期内（次要入口「撤销注销」） |
| 深色 | ForceUpdateDark.dc.html（95aa44fd09a7）、MainUpdatePromptDark.dc.html（296ecb161447） | 系统深色 | 同上；可选更新底稿为第 1 批 `MainDark` |

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 强更页 | 正式 App 图标（`design/app-icon` 缩样）+ 标题 + 说明 + 【去更新】 | 版本检查结果 | 全屏拦截，不能返回 |
| 次要入口 | 「隐私政策」+「注销账号」（冷静期内为「撤销注销」） | getDeletion（受限会话） | 完成或返回后回到本页 |
| 暂时无法更新 | 说明 +【重试】 | — | 重试重新核对商店 |
| 可选更新弹窗 | 标题 + 更新说明 +【暂不更新】【去更新】 | update_title、update_notes | 可关闭 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 按钮与次要入口 | BR-TEXT-14 表 C `app_update.go_store`、`.later`、`.retry`、`.privacy_policy`、`.delete_account`、`.cancel_deletion` |
| 暂时无法更新 | 表 C `app_update.unavailable` |
| 强更说明 | 表 A `error.10405` |
| 可选更新的标题与正文 | 取接口 update_title / update_notes；没有时的兜底见 §7 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| checkAppVersion | 冷启动、回前台复查、【重试】 | — |
| getDeletion / getMe（受限会话 deletion_only） | 显示次要入口 | — |

## 5. 权限点与开关

`/v1/config.app_update.recheck_interval_sec`（复查间隔）；强更状态下 Router 只放行从强更页进入的 `PrivacyCenter`、`Agreement`、`Login`、`DeleteAccount`（03 §4.1）。

## 6. 稿上没画、实现要做的

强更检查结果未知时桥调用按三类处理、埋点只入队（03 §4.4）；Android 通用包按安装来源查商店表；读屏焦点锁在强更页。

## 7. 待定与不一致

- 可选更新提示没有 update_title / update_notes 时，08 规定退回 `error.10405`「当前版本过低…」，与可关闭的提示自相矛盾；建议加 `app_update.optional.*` 标题与正文键，待上游（BR-TEXT-14）。
- 强更页次要入口按表 C `app_update.cancel_deletion` 原文「撤销注销」；flow-map §20.3 ③-2 曾统一成「撤回」，需回改（注销页的「撤回注销」不变），待上游（设计文档回写）。
- 强更页进入的受限登录（不显示待绑定码提示条与「登录遇到问题」、登录后不出绑手机与填写邀请码、查不到账号提示 `error.10405.no_account` 并回强更页）本批未画，交付归属登录稿（基稿 `Login-v2` / `LoginCode-v2`），待上游（编排安排）。
- 底稿首页的两处已删文案以第 1 批 `Main-v3` 为准（页首说明），画板随下次改稿同步（微调项）。
