# 启动与隐私首启弹窗 Launch（App 原生）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`Launch`（auth none，入口 in_app）；什么时候出现：首次启动、隐私政策版本升级后的下一次冷启动、基本模式点【开启完整功能】；去哪：同意 → 首页；仍不同意 → `BasicMode`（[app-basic-mode.md](app-basic-mode.md)）；书名号链接 → `Agreement`（包内副本）
- 需求：01 §4.2 `Launch` 行；F-PRIV-01、F-PRIV-02、F-PRIV-03、F-PRIV-05；规则只引编号：BR-ID-09、BR-ID-11、BR-ID-12、BR-TEXT-14 表 D `privacy.*`、00 D34（号码认证 SDK）；验收：AC-PRIV-01…03（同号规则）、AC-S1-85、AC-S1-158、AC-S1-185；任务：APP-02、HM-02
- 可参考的已合并页面：原生三端仓库派发前核对
- 是否资金或归属页面：否（合规闸门：同意前只取配置与协议文本、不初始化 SDK）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 首启隐私弹窗 | LaunchPrivacy-v2.dc.html（a9508e0b1833） | 本机没有同意当前隐私版本 | 包内默认文案与版本；同意前只允许请求协议文本与 `/v1/config`（BR-ID-11） |
| 不同意后的二次说明 | LaunchSecondNotice-v2.dc.html（5e9c81225429，画的是 Android / 鸿蒙） | 点【不同意】（三端都出一次，BR-ID-11） | 本地；iOS 没有【退出 App】 |
| 深色 | LaunchPrivacyDark.dc.html（601ee4066aaf） | 系统深色 | 同首启弹窗 |
| 同意后 | 不适用（无画板） | 点【同意】 | 本地记录同意 → registerDevice → recordConsent（type=privacy，BR-ID-12：设备注册后补报） |

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 弹窗 | 不可关闭的模态（不响应返回键，APP-02） | — | 只有两个按钮 |
| 摘要 | 分条摘要 + 4 个书名号链接（命中区 44） | 包内文本 | 链接打开 `Agreement` 对应类型 |
| 按钮 | 【同意】【不同意】；二次说明【同意】【仍不同意】，Android / 鸿蒙另有【退出 App】 | — | 按钮含义按 BR-ID-11，不随文案改 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 首启标题与摘要 | BR-TEXT-14 表 D `privacy.first_launch.title` / `.summary`（全文由法务提供） |
| 二次说明 | 表 D `privacy.second_notice.body` |
| 按钮 | 表 D `privacy.btn.agree` / `.disagree` / `.still_disagree` / `.exit_app` |
| 二次说明标题 | 08 无键（建议 `privacy.second_notice.title`），待回写 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| registerDevice | 同意之后 | 20001 |
| recordConsent | 设备注册成功后补报 | 20001、10401、10402、10405 |

同意前只允许 getConfig 与协议文本（getAgreements / getAgreementVersion），不初始化 SDK、不生成设备 ID（BR-ID-11）。

## 5. 权限点与开关

无；隐私版本取包内默认，联网后按 `/v1/config.legal.privacy.version` / `min_version` 判断是否重新同意（BR-ID-12）。

## 6. 稿上没画、实现要做的

弹窗焦点锁定与读屏顺序（标题 → 摘要 → 链接 → 按钮）；大字号下摘要区滚动、按钮常驻；链接打开协议后返回仍在弹窗。

## 7. 待定与不一致

- 首启弹窗标题与摘要是占位措辞，正文由法务提供（06 Q-F14），待上游。
- 两份清单的正式名称（首启弹窗用《第三方共享清单》，与隐私中心一致）待法务定稿统一，待上游。
- 契约 `texts.default.json` 尚无 `privacy.first_launch.*`、`privacy.second_notice.body`，待契约线同步。
